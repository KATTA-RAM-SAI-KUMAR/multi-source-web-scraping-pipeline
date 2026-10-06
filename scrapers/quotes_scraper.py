import logging
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

QUOTES_START_URL = "https://quotes.toscrape.com/"


class QuotesScraper(BaseScraper):
    source_name = "Quotes to Scrape"

    def parse_quote(self, quote, page_url: str) -> dict[str, Any]:
        text = quote.select_one("span.text")
        author = quote.select_one("small.author")
        author_link = quote.select_one('a[href^="/author/"]')
        tags = quote.select("a.tag")

        return {
            "source": self.source_name,
            "source_url": page_url,
            "name_or_title": text.get_text(" ", strip=True) if text else None,
            "category": None,
            "price_raw": None,
            "rating_raw": None,
            "author": author.get_text(" ", strip=True) if author else None,
            "tags": [tag.get_text(" ", strip=True) for tag in tags],
            "description": None,
            "author_url": (
                urljoin(page_url, author_link["href"])
                if author_link and author_link.get("href")
                else None
            ),
        }

    def parse_page(self, html: str, page_url: str) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "lxml")
        records: list[dict[str, Any]] = []

        for index, quote in enumerate(soup.select("div.quote"), start=1):
            try:
                records.append(self.parse_quote(quote, page_url))
            except Exception as exc:
                logger.warning(
                    "Skipping quote record %d on %s: %s", index, page_url, exc
                )

        return records

    def scrape(self, start_url: str = QUOTES_START_URL) -> list[dict[str, Any]]:
        url: str | None = start_url
        page = 1
        records: list[dict[str, Any]] = []

        while url:
            logger.info("Quotes page %d: %s", page, url)
            response = self.fetch(url)
            if response is None:
                logger.error("Stopping Quotes to Scrape after page %d failure", page)
                break

            page_records = self.parse_page(response.text, url)
            records.extend(page_records)
            logger.info(
                "Quotes page %d parsed: %d records", page, len(page_records)
            )

            soup = BeautifulSoup(response.text, "lxml")
            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
            page += 1

        logger.info("Quotes scrape complete: %d raw records", len(records))
        return records
