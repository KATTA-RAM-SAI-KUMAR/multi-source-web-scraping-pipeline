import csv
import json
import logging
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
CSV_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary_report.json"
LOG_PATH = LOG_DIR / "scraper.log"

FIELDNAMES = [
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "tags",
    "description",
    "scraped_at",
]


def configure_logging() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()

    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root.addHandler(file_handler)
    root.addHandler(console_handler)


def add_timestamp(records: list[dict]) -> list[dict]:
    timestamp = datetime.now(timezone.utc).isoformat()
    for record in records:
        record["scraped_at"] = timestamp
    return records


def process_source(source_name: str, raw_records: list[dict], stats: dict) -> list[dict]:
    stats["collected_per_source"][source_name] = len(raw_records)
    cleaned: list[dict] = []
    rejection_reasons = Counter()
    rejected_records = 0

    for raw in raw_records:
        record = clean_record(raw)
        problems = validate_record(record)
        if problems:
            rejected_records += 1
            for reason in problems:
                rejection_reasons[reason] += 1
            logging.warning(
                "Rejected %s record: %s | reasons=%s",
                source_name,
                record.get("name_or_title"),
                ",".join(problems),
            )
            continue
        cleaned.append(record)

    stats["cleaned_per_source"][source_name] = len(cleaned)
    stats["rejected_per_source"][source_name] = rejected_records
    stats["rejected_by_reason_per_source"][source_name] = dict(rejection_reasons)
    return cleaned


def write_csv(records: list[dict]) -> None:
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)


def write_summary(stats: dict) -> None:
    with SUMMARY_PATH.open("w", encoding="utf-8") as handle:
        json.dump(stats, handle, indent=4, ensure_ascii=False)


def run() -> None:
    configure_logging()
    start = time.perf_counter()
    start_time = datetime.now(timezone.utc)
    logging.info("Starting scraping assignment pipeline")

    stats = {
        "start_time_utc": start_time.isoformat(),
        "end_time_utc": None,
        "duration_seconds": None,
        "collected_per_source": {},
        "cleaned_per_source": {},
        "rejected_per_source": {},
        "rejected_by_reason_per_source": {},
        "duplicates_detected_per_source": {},
        "duplicates_detected": 0,
        "final_record_count": 0,
        "source_failures": {},
    }

    all_cleaned: list[dict] = []
    scrapers = [
        ("Books to Scrape", BooksScraper()),
        ("Quotes to Scrape", QuotesScraper()),
    ]

    for source_name, scraper in scrapers:
        try:
            raw_records = add_timestamp(scraper.scrape())
            if scraper.failed_requests:
                stats["source_failures"][source_name] = {
                    "failed_requests": scraper.failed_requests,
                    "message": "Scraping stopped at the first failed page after retries.",
                }
            cleaned = process_source(source_name, raw_records, stats)
            all_cleaned.extend(cleaned)
        except Exception as exc:
            logging.exception("Unexpected failure in %s", source_name)
            stats["source_failures"][source_name] = str(exc)
            stats["collected_per_source"].setdefault(source_name, 0)
            stats["cleaned_per_source"].setdefault(source_name, 0)
            stats["rejected_per_source"].setdefault(source_name, 0)
            stats["rejected_by_reason_per_source"].setdefault(source_name, {})

    unique_records, duplicate_records = find_duplicates(all_cleaned)

    # Attribute duplicates to their source for a useful summary.
    duplicate_counts = Counter(rec.get("source") for rec in duplicate_records)
    stats["duplicates_detected_per_source"] = dict(duplicate_counts)
    stats["duplicates_detected"] = len(duplicate_records)
    stats["final_record_count"] = len(unique_records)

    write_csv(unique_records)

    end_time = datetime.now(timezone.utc)
    stats["end_time_utc"] = end_time.isoformat()
    stats["duration_seconds"] = round(time.perf_counter() - start, 3)
    write_summary(stats)

    logging.info("Final records: %d", len(unique_records))
    logging.info("CSV written to %s", CSV_PATH)
    logging.info("Summary written to %s", SUMMARY_PATH)
    logging.info("Pipeline finished in %.3f seconds", stats["duration_seconds"])


if __name__ == "__main__":
    run()
