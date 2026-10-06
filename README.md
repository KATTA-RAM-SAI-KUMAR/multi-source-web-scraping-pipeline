# Multi-Source Web Scraping & Data Consolidation

## Overview

This project implements the assignment as a small ETL pipeline:

`Scrape -> Clean -> Validate -> Deduplicate -> Consolidate -> Save`

It collects public data from **Books to Scrape** and **Quotes to Scrape**, converts both sources into a common schema, validates the records, removes duplicates, and produces a CSV, JSON summary, and execution log.

The assignment explicitly asks for multi-page scraping, a common data model, cleaning, validation, duplicate detection, error handling, logging, documentation, and reproducible setup.

## Sources and selectors

### Books to Scrape
- Start URL: `https://books.toscrape.com/`
- Record: `article.product_pod`
- Title/link: `h3 > a` (`title` attribute contains the full title)
- Price: `p.price_color`
- Rating: `p.star-rating` class list
- Pagination: `li.next > a`

### Quotes to Scrape
- Start URL: `https://quotes.toscrape.com/`
- Record: `div.quote`
- Quote: `span.text`
- Author: `small.author`
- Tags: `a.tag`
- Author link: `a[href^="/author/"]`
- Pagination: `li.next > a`

The assignment requires separate source-specific scraper modules and automatic pagination rather than manually listing page URLs.

## Data model

| Column | Books | Quotes |
|---|---|---|
| source | Books to Scrape | Quotes to Scrape |
| source_url | Book detail URL | Page URL where quote appeared |
| name_or_title | Book title | Quote text |
| category | Empty | Empty |
| price | Numeric price | Empty |
| rating | 1–5 integer | Empty |
| author | Empty | Author name |
| tags | Empty | Sorted lowercase `tag1;tag2` |
| description | Empty | Empty |
| scraped_at | UTC timestamp | UTC timestamp |

No values are invented for fields that are not collected. This follows the assignment's requirement to use null/empty values when a field does not apply.

### Known limitation

The listing page does not expose the book category or description directly. This implementation intentionally leaves those fields empty instead of adding approximately 1,000 extra detail-page requests. This is a documented trade-off: correctness and reasonable runtime are preferred over guessing or unnecessarily increasing traffic.

## Project structure

```text
scraping_assignment/
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py
│   ├── books_scraper.py
│   └── quotes_scraper.py
├── processing/
│   ├── __init__.py
│   ├── cleaning.py
│   ├── validation.py
│   └── deduplication.py
├── tests/
│   ├── test_cleaning.py
│   ├── test_validation.py
│   └── test_deduplication.py
├── output/
├── logs/
├── main.py
├── streamlit_app.py
├── requirements.txt
├── README.md
└── AI_USAGE.md
```

This mirrors the recommended separation of scrapers, processing, tests, outputs, logs, and the main entry point.

## Setup

Recommended Python: **3.10–3.12**, matching the assignment's stated environment.

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Windows CMD

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run

From the project root:

```bash
python main.py
```

The program creates:

- `output/final_dataset.csv`
- `output/summary_report.json`
- `logs/scraper.log`

The assignment requires the CSV and summary report and also asks for sample execution logs in the deliverables.

## Pagination

Pagination is dynamic. Each scraper starts at the source home page, parses the current page, finds `li.next > a`, converts the relative URL with `urljoin`, and continues until no next link exists. There is no hard-coded page count.

## HTTP reliability

`BaseScraper` provides:

- `requests.Session`
- custom User-Agent
- 10-second request timeout
- retries for HTTP 429, 500, 502, 503, and 504
- exponential backoff through `urllib3 Retry`
- a 0.5-second delay between requests
- logging of failed requests

This directly addresses the assignment's connection failures, HTTP errors, timeouts, missing elements, unexpected formats, and page-failure requirements.

## Cleaning

Cleaning is isolated from scraping:

- `clean_text`: whitespace and non-breaking-space cleanup
- `strip_quotes`: removes surrounding quote characters
- `clean_price`: converts currency text such as `£51.77` to `51.77`
- `clean_rating`: converts word ratings such as `Three` to `3`
- `clean_tags`: lowercases, sorts, de-duplicates, and joins tags with `;`
- `normalize_url`: accepts only complete HTTP/HTTPS URLs

The assignment explicitly asks for reusable transformation functions and separation from scraping logic.

## Validation

A record is rejected if:

- its source is not recognized;
- its main name/title is missing;
- its URL is not HTTP/HTTPS;
- its price, when present, is not a non-negative number;
- its rating, when present, is not an integer from 1 to 5.

Validation returns reason codes rather than a simple boolean, allowing the JSON report to explain rejected data. The assignment requires validation before final output and measurable rejection information.

## Deduplication

Duplicates are removed rather than flagged.

- Books fingerprint: `source + normalized title`
- Quotes fingerprint: `source + author + first 50 characters of quote`

Normalization lowercases text, removes punctuation, and collapses whitespace before SHA-256 hashing. This means casing, extra spaces, and punctuation differences do not create false unique records.

A unit test deliberately creates duplicate books and quotes to prove the logic works even when the live sources contain no duplicates.

## Summary metrics

`summary_report.json` includes:

- raw records collected per source
- cleaned records per source
- rejected records per source
- rejection counts by reason
- duplicate counts per source and overall
- final record count
- UTC start/end times
- duration in seconds
- source failures, if any

The assignment expects these metrics and requires the final count to be verifiable against the CSV.

## Testing

Run:

```bash
pytest -q
```

The tests do not require internet access. They cover cleaning, validation, and duplicate detection, matching the assignment's testing expectations.

## Assumptions

1. The two practice sites remain publicly accessible.
2. Their documented HTML selectors remain compatible.
3. A quote's `source_url` is the page where the quote appeared, not the author page.
4. Empty fields mean the source does not provide that value in the selected scrape path.
5. Duplicates are removed, and the first occurrence is retained.

## Production improvements

If this became a recurring production job, the next upgrades would be checkpoint/resume, configurable settings, persistent storage, data-quality monitoring, stronger schema validation, and a more explicit rate-limit policy. These align with the assignment's optional bonus features.

## AI usage

See `AI_USAGE.md`. The assignment explicitly permits AI assistance but requires the candidate to review, test, correct, and understand the final implementation.

## Optional live demo

`streamlit_app.py` provides a lightweight presentation layer for the same pipeline. It reads the generated CSV and summary report, shows key metrics and a preview, and can trigger the scraper for a fresh run. The CLI remains the primary assignment entry point: `python main.py`.

For a public demo, deploy `streamlit_app.py` from the GitHub repository using Streamlit Community Cloud.
