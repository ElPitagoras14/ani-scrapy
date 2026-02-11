# Adding Scrapers

## Checklist

1. Add site constants in `src/ani_scrapy/core/constants/<site>.py`.
2. Create a parser in `src/ani_scrapy/<site>/parser.py`.
3. Add scraper in `src/ani_scrapy/<site>/scraper.py`.
4. Expose public imports in `src/ani_scrapy/__init__.py`.
5. Add fixtures under `tests/fixtures/html/`.
6. Add unit tests for the parser.
7. Add integration tests using pytest fixtures.

## Design Rules

- Keep parsing inside the parser.
- Keep network/browser coordination inside scrapers.
- All scrapers use async/await patterns.
