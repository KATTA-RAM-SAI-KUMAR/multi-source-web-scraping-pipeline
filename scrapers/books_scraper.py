import logging
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BOOKS_START_URL = "https://books.toscrape.com/"


class BooksScraper(BaseScraper):
    source_name = "Books to Scrape"

    def parse_book(self, article, page_url: str) -> dict[str, Any]:
        link = article.select_one("h3 > a")
        price = article.select_one("p.price_color")
        rating = article.select_one("p.star-rating")
        availability = article.select_one("p.instock.availability")

        return {
            "source": self.source_name,
            "source_url": (
                urljoin(page_url, link["href"])
                if link and link.get("href")
                else None
            ),
            "name_or_title": link.get("title") if link else None,
            "category": None,
            "price_raw": price.get_text(" ", strip=True) if price else None,
            "rating_raw": " ".join(rating.get("class", [])) if rating else None,
            "author": None,
            "tags": None,
            "description": None,
            "availability": (
                availability.get_text(" ", strip=True) if availability else None
            ),
        }

    def parse_page(self, html: str, page_url: str) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "lxml")
        records: list[dict[str, Any]] = []

        for index, article in enumerate(soup.select("article.product_pod"), start=1):
            try:
                records.append(self.parse_book(article, page_url))
            except Exception as exc:  # one malformed record must not stop a page
                logger.warning(
                    "Skipping book record %d on %s: %s", index, page_url, exc
                )

        return records

    def scrape(self, start_url: str = BOOKS_START_URL) -> list[dict[str, Any]]:
        url: str | None = start_url
        page = 1
        records: list[dict[str, Any]] = []

        while url:
            logger.info("Books page %d: %s", page, url)
            response = self.fetch(url)
            if response is None:
                logger.error("Stopping Books to Scrape after page %d failure", page)
                break

            page_records = self.parse_page(response.text, url)
            records.extend(page_records)
            logger.info(
                "Books page %d parsed: %d records", page, len(page_records)
            )

            soup = BeautifulSoup(response.text, "lxml")
            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
            page += 1

        logger.info("Books scrape complete: %d raw records", len(records))
        return records
