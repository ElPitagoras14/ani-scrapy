# Contributing

## Setup

```bash
pip install -e ".[dev]"
pytest tests/
```

## Code Style

- Tests: `pytest tests/`

## Project Conventions

- Parsers live in `src/ani_scrapy/<site>/parser.py`.
- HTTP I/O lives in `src/ani_scrapy/core/http.py`.
- Scrapers (coordination) live in `src/ani_scrapy/<site>/scraper.py`.
- Tests use pytest fixtures (no network).
