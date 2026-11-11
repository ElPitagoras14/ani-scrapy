# Contributing to ani-scrapy

Thank you for your interest in contributing to ani-scrapy!

## Development Setup

Clone the repository and install dependencies with uv:

```bash
git clone https://github.com/ElPitagoras14/ani-scrapy.git
cd ani-scrapy
uv sync
playwright install chromium
git config core.hooksPath .githooks
```

The `commit-msg` hook in `.githooks/` strips `Co-Authored-By` trailers that mention Claude or Anthropic; human co-authors are kept.

## Tests

```bash
uv run pytest
```

The default run uses HTML fixtures and mocked HTTP: it needs no network and no browser. CI runs it on Python 3.11 and 3.14.

Fixtures are snapshots, so they keep passing when a site changes. Live tests check each supported provider (JKAnime, AnimeAV1) against its real site:

```bash
uv run pytest -m live
```

Run them locally, never in CI: they need Playwright Chromium and hit third-party sites. A failing live test means the site changed: fix the provider and refresh its fixtures from the current page.

## Running Benchmarks

To measure performance across providers:

```bash
uv run python examples/07_benchmark.py
```

## Code Style

The project uses:

- **Ruff** for linting and formatting
- **Type hints** (Python 3.11+)

```bash
uv run ruff check src tests
uv run ruff format --check src tests
```

## Git Conventions

Follow the conventions defined in [CLAUDE.md](./CLAUDE.md).

## Project Structure

| Path                                      | Description                          |
|-------------------------------------------|--------------------------------------|
| `src/ani_scrapy/core/`                    | Core functionality (HTTP, browser, exceptions, schemas) |
| `src/ani_scrapy/core/base.py`             | Base scraper class                   |
| `src/ani_scrapy/core/browser.py`         | Playwright browser management        |
| `src/ani_scrapy/core/http.py`             | HTTP I/O                             |
| `src/ani_scrapy/core/exceptions.py`       | Custom exceptions hierarchy          |
| `src/ani_scrapy/core/schemas.py`         | Data schemas (dataclasses)       |
| `src/ani_scrapy/core/log.py`              | Logging utilities                    |
| `src/ani_scrapy/core/constants/`          | Site constants and configuration     |
| `src/ani_scrapy/providers/<site>/`        | Provider-specific implementation     |
| `src/ani_scrapy/providers/<site>/parser.py` | Site HTML parsing                 |
| `src/ani_scrapy/providers/<site>/scraper.py` | Network/browser coordination     |
| `src/ani_scrapy/providers/<site>/constants.py` | Site URLs and configuration    |
| `src/ani_scrapy/cli/`                     | CLI commands                         |
| `tests/fixtures/html/`                    | HTML test fixtures                   |

## Adding a New Scraper

1. Create `src/ani_scrapy/providers/<site>/` with `constants.py`, `parser.py` and `scraper.py`
2. Expose public imports in `src/ani_scrapy/__init__.py`
3. Add fixtures under `tests/fixtures/html/`
4. Add unit tests for the parser and the scraper
5. Add a live test module under `tests/integration/`

### Design Rules

- Keep parsing inside the parser
- Keep network/browser coordination inside scrapers
- All scrapers use async/await patterns

## Testing Philosophy

- Prefer HTML fixtures with pytest
- No real network access in the default run or in CI; live tests are opt-in (`-m live`)

## Python Support

The minimum supported version is the oldest Python that still receives security fixes (currently 3.11). Raising it is a minor release listed under breaking changes in the changelog.

## Releasing

1. `uv run pytest -m live` passes.
2. Bump `version` in `pyproject.toml` and add the `## X.Y.Z` entry to `CHANGELOG.md` in the same PR.
3. Merging to `main` publishes: CI runs, then the package is uploaded to PyPI and the tag and GitHub release are created.

## Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Push to your fork
6. Open a Pull Request against `main`

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
