from numbers import Real

VALID_SOURCES = {"Books to Scrape", "Quotes to Scrape"}


def validate_record(rec: dict) -> list[str]:
    problems: list[str] = []

    if rec.get("source") not in VALID_SOURCES:
        problems.append("unknown_source")
    if not rec.get("name_or_title"):
        problems.append("missing_name")
    if not str(rec.get("source_url") or "").startswith(("http://", "https://")):
        problems.append("invalid_url")

    price = rec.get("price")
    if price is not None and (not isinstance(price, Real) or isinstance(price, bool) or price < 0):
        problems.append("invalid_price")

    rating = rec.get("rating")
    if rating is not None and (not isinstance(rating, int) or rating not in {1, 2, 3, 4, 5}):
        problems.append("invalid_rating")

    return problems
