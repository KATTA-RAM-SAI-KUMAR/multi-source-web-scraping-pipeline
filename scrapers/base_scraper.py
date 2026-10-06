import logging
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)


class BaseScraper:
    """Shared HTTP behavior for all source scrapers."""

    def __init__(self, delay: float = 0.5, timeout: int = 10) -> None:
        self.delay = delay
        self.timeout = timeout
        self.failed_requests: list[str] = []
        self.session = self.create_session()

    @staticmethod
    def create_session() -> requests.Session:
        session = requests.Session()
        session.headers.update(
            {"User-Agent": "ScrapingAssignment/1.0 (learning project)"}
        )
        retries = Retry(
            total=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def fetch(self, url: str) -> Optional[requests.Response]:
        """Fetch a URL safely; return None after retries fail."""
        try:
            logger.info("Request: %s", url)
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response
        except requests.RequestException as exc:
            self.failed_requests.append(url)
            logger.error("Failed to fetch %s: %s", url, exc)
            return None
        finally:
            time.sleep(self.delay)
