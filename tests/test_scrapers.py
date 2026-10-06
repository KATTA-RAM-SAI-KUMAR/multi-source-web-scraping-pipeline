from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper


BOOK_HTML = '''
<html><body>
<article class="product_pod">
  <h3><a href="catalogue/example_1/index.html" title="Example Book">Example...</a></h3>
  <p class="price_color">£51.77</p>
  <p class="star-rating Three"><i></i></p>
  <p class="instock availability">In stock</p>
</article>
<ul><li class="next"><a href="page-2.html">next</a></li></ul>
</body></html>
'''


QUOTE_HTML = '''
<html><body>
<div class="quote">
  <span class="text">“A useful quote.”</span>
  <small class="author">Jane Doe</small>
  <a class="tag">Life</a><a class="tag">Books</a>
  <a href="/author/jane-doe">about</a>
</div>
<ul><li class="next"><a href="page/2/">next</a></li></ul>
</body></html>
'''


def test_book_parser_and_next_link():
    scraper = BooksScraper()
    records = scraper.parse_page(BOOK_HTML, "https://books.toscrape.com/")
    assert len(records) == 1
    assert records[0]["name_or_title"] == "Example Book"
    assert records[0]["price_raw"] == "£51.77"
    assert "Three" in records[0]["rating_raw"]


def test_quote_parser_and_fields():
    scraper = QuotesScraper()
    records = scraper.parse_page(QUOTE_HTML, "https://quotes.toscrape.com/")
    assert len(records) == 1
    assert records[0]["name_or_title"] == "“A useful quote.”"
    assert records[0]["author"] == "Jane Doe"
    assert records[0]["tags"] == ["Life", "Books"]
