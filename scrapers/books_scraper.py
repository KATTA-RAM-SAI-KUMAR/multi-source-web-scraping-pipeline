import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BOOKS_START_URL = "https://books.toscrape.com/"

# Small worker pool keeps the scraper reasonably polite
# while avoiding a very long sequential runtime.
DETAIL_WORKERS = 5


class BooksScraper(BaseScraper):
    source_name = "Books to Scrape"

    def parse_book_listing(
        self,
        article,
        page_url: str,
    ) -> dict[str, Any]:

        link = article.select_one("h3 > a")
        price = article.select_one(
            "p.price_color"
        )
        rating = article.select_one(
            "p.star-rating"
        )
        availability = article.select_one(
            "p.instock.availability"
        )

        book_url = (
            urljoin(
                page_url,
                link["href"]
            )
            if link and link.get("href")
            else None
        )

        return {
            "source": self.source_name,
            "source_url": book_url,
            "name_or_title": (
                link.get("title")
                if link
                else None
            ),
            "category": None,
            "price_raw": (
                price.get_text(
                    " ",
                    strip=True
                )
                if price
                else None
            ),
            "rating_raw": (
                " ".join(
                    rating.get("class", [])
                )
                if rating
                else None
            ),
            "author": None,
            "tags": None,
            "description": None,
            "availability": (
                availability.get_text(
                    " ",
                    strip=True
                )
                if availability
                else None
            ),
        }

    def fetch_book_details(
        self,
        record: dict[str, Any],
    ) -> dict[str, Any]:

        book_url = record.get(
            "source_url"
        )

        if not book_url:
            return record

        try:
            response = self.fetch(
                book_url
            )

            if response is None:
                return record

            soup = BeautifulSoup(
                response.text,
                "lxml"
            )

            # ---------------------------------
            # CATEGORY
            # ---------------------------------

            breadcrumb_links = soup.select(
                "ul.breadcrumb li a"
            )

            if len(breadcrumb_links) >= 2:
                record["category"] = (
                    breadcrumb_links[-1]
                    .get_text(
                        " ",
                        strip=True
                    )
                )

            # ---------------------------------
            # DESCRIPTION
            # ---------------------------------

            description_heading = (
                soup.select_one(
                    "#product_description"
                )
            )

            if description_heading:
                description = (
                    description_heading
                    .find_next_sibling("p")
                )

                if description:
                    record["description"] = (
                        description.get_text(
                            " ",
                            strip=True
                        )
                    )

        except Exception as exc:
            logger.warning(
                "Could not fetch book details "
                "for %s: %s",
                book_url,
                exc
            )

        return record

    def parse_page(
        self,
        html: str,
        page_url: str,
    ) -> list[dict[str, Any]]:

        soup = BeautifulSoup(
            html,
            "lxml"
        )

        records: list[dict[str, Any]] = []

        for index, article in enumerate(
            soup.select(
                "article.product_pod"
            ),
            start=1,
        ):
            try:
                records.append(
                    self.parse_book_listing(
                        article,
                        page_url
                    )
                )

            except Exception as exc:
                logger.warning(
                    "Skipping book record %d "
                    "on %s: %s",
                    index,
                    page_url,
                    exc
                )

        return records

    def scrape(
        self,
        start_url: str = BOOKS_START_URL,
    ) -> list[dict[str, Any]]:

        url: str | None = start_url
        page = 1
        records: list[dict[str, Any]] = []

        # ---------------------------------
        # STEP 1:
        # Collect all listing-page records
        # ---------------------------------

        while url:

            logger.info(
                "Books page %d: %s",
                page,
                url
            )

            response = self.fetch(url)

            if response is None:
                logger.error(
                    "Stopping Books to Scrape "
                    "after page %d failure",
                    page
                )
                break

            page_records = self.parse_page(
                response.text,
                url
            )

            records.extend(
                page_records
            )

            logger.info(
                "Books page %d parsed: %d records",
                page,
                len(page_records)
            )

            soup = BeautifulSoup(
                response.text,
                "lxml"
            )

            # Dynamic pagination
            next_link = soup.select_one(
                "li.next > a"
            )

            if (
                next_link
                and next_link.get("href")
            ):
                url = urljoin(
                    url,
                    next_link["href"]
                )
            else:
                url = None

            page += 1

        logger.info(
            "Books listing scrape complete: "
            "%d raw records",
            len(records)
        )

        # ---------------------------------
        # STEP 2:
        # Fetch detail pages concurrently
        # ---------------------------------

        logger.info(
            "Fetching details for %d books "
            "using %d workers",
            len(records),
            DETAIL_WORKERS
        )

        detailed_records: list[
            dict[str, Any]
        ] = []

        with ThreadPoolExecutor(
            max_workers=DETAIL_WORKERS
        ) as executor:

            future_to_record = {
                executor.submit(
                    self.fetch_book_details,
                    record
                ): record
                for record in records
            }

            for future in as_completed(
                future_to_record
            ):
                original_record = (
                    future_to_record[future]
                )

                try:
                    detailed_records.append(
                        future.result()
                    )

                except Exception as exc:
                    logger.warning(
                        "Book detail worker failed "
                        "for %s: %s",
                        original_record.get(
                            "source_url"
                        ),
                        exc
                    )

                    # Keep the original record
                    # rather than losing data.
                    detailed_records.append(
                        original_record
                    )

        logger.info(
            "Books scrape complete: %d records",
            len(detailed_records)
        )

        return detailed_records