import hashlib
import re


def _normalize_key(value) -> str:
    value = str(value or "").lower()
    value = re.sub(r"[^\w\s]", "", value)
    return " ".join(value.split())


def make_fingerprint(rec: dict) -> str:
    if rec.get("source") == "Books to Scrape":
        key = f'{rec.get("source")} {rec.get("name_or_title")}'
    else:
        key = (
            f'{rec.get("source")} {rec.get("author")} '
            f'{str(rec.get("name_or_title") or "")[:50]}'
        )
    normalized = _normalize_key(key)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def find_duplicates(records: list[dict]) -> tuple[list[dict], list[dict]]:
    seen: set[str] = set()
    unique: list[dict] = []
    duplicates: list[dict] = []

    for rec in records:
        fingerprint = make_fingerprint(rec)
        if fingerprint in seen:
            duplicates.append(rec)
        else:
            unique.append(rec)
            seen.add(fingerprint)

    return unique, duplicates
