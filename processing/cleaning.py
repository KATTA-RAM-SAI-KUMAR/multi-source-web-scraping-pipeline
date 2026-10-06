import re
from urllib.parse import urlparse

RATING_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def clean_text(value):
    if value is None:
        return None
    text = " ".join(str(value).replace("\xa0", " ").split())
    return text or None


def strip_quotes(value):
    text = clean_text(value)
    if not text:
        return None
    return text.strip("\"'“”‘’") or None


def clean_price(raw):
    if raw is None:
        return None
    match = re.search(r"\d+(?:\.\d+)?", str(raw).replace(",", ""))
    return float(match.group()) if match else None


def clean_rating(raw):
    for word in (str(raw or "").lower().split()):
        if word in RATING_MAP:
            return RATING_MAP[word]
    return None


def clean_tags(tags):
    if not tags:
        return None
    cleaned = sorted({clean_text(tag).lower() for tag in tags if clean_text(tag)})
    return ";".join(cleaned) if cleaned else None


def normalize_url(value):
    value = clean_text(value)
    if not value:
        return None
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return value
    return None


def clean_record(raw: dict) -> dict:
    return {
        "source": clean_text(raw.get("source")),
        "source_url": normalize_url(raw.get("source_url")),
        "name_or_title": strip_quotes(raw.get("name_or_title")),
        "category": clean_text(raw.get("category")),
        "price": clean_price(raw.get("price_raw")),
        "rating": clean_rating(raw.get("rating_raw")),
        "author": clean_text(raw.get("author")),
        "tags": clean_tags(raw.get("tags")),
        "description": clean_text(raw.get("description")),
        "scraped_at": clean_text(raw.get("scraped_at")),
    }
