from processing.deduplication import find_duplicates


def test_duplicates_ignore_case_spaces_and_punctuation():
    base = {
        "source": "Books to Scrape",
        "author": None,
        "name_or_title": "Example Book Title",
    }
    records = [
        base,
        {**base, "name_or_title": "  Example Book Title "},
        {**base, "name_or_title": "EXAMPLE BOOK TITLE!!!"},
    ]
    unique, duplicates = find_duplicates(records)
    assert len(unique) == 1
    assert len(duplicates) == 2


def test_quote_duplicate_uses_author_and_first_50_chars():
    records = [
        {"source": "Quotes to Scrape", "author": "Author", "name_or_title": "A quote!"},
        {"source": "Quotes to Scrape", "author": " author ", "name_or_title": "A quote"},
    ]
    unique, duplicates = find_duplicates(records)
    assert len(unique) == 1
    assert len(duplicates) == 1
