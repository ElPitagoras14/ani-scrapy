# Contributing to ani-scrapy

Thank you for your interest in contributing to ani-scrapy!

## Development Setup

Clone the repository and install dependencies with uv:

```bash
git clone https://github.com/ElPitagoras14/ani-scrapy.git
cd ani-scrapy
uv sync
playwright install chromium
```

## Running Tests

Run the unit tests with uv:

```bash
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=src --cov-report=html
```

## Running Benchmarks

To measure performance across providers:

```bash
uv run python scripts/benchmark_providers.py
```

## Code Style

The project uses:

- **Ruff** for linting
- **Type hints** (Python 3.10+)

Run linting:

```bash
uv run ruff check src/
```

## Git Conventions

### Branch Naming

Format: `<type>/<short-description>`

| Type | Description |
| ---- |-------------|
| `feat` | new feature |
| `fix` | bug fix |
| `refactor` | code improvement without behavior change |
| `chore` | maintenance, config, dependencies, CI, docs |

Example:
```bash
git checkout -b feat/add-user-authentication
```

### Commit Message

Format: `<type>(scope): <short description>`

| Type | Description |
| ---- |-------------|
| `feat` | new feature |
| `fix` | bug fix |
| `refactor` | code improvement without behavior change |
| `chore` | maintenance, dependencies, CI, docs |

Examples:
```
feat(auth): add JWT authentication
fix(parser): handle missing episode field
chore(deps): update playwright to latest version
```

## Project Structure

| Path | Description |
|------|-------------|
| `src/ani_scrapy/<site>/parser.py` | Site HTML parsing |
| `src/ani_scrapy/<site>/scraper.py` | Network/browser coordination |
| `src/ani_scrapy/core/http.py` | HTTP I/O |
| `tests/fixtures/html/` | HTML test fixtures |

## Adding a New Scraper

1. Add site constants in `src/ani_scrapy/core/constants/<site>.py`
2. Create parser in `src/ani_scrapy/<site>/parser.py`
3. Add scraper in `src/ani_scrapy/<site>/scraper.py`
4. Expose public imports in `src/ani_scrapy/__init__.py`
5. Add fixtures under `tests/fixtures/html/`
6. Add unit tests for the parser
7. Add integration tests using pytest fixtures

### Design Rules

- Keep parsing inside the parser
- Keep network/browser coordination inside scrapers
- All scrapers use async/await patterns

## Testing Philosophy

- Prefer HTML fixtures with pytest
- Avoid real network access in CI
- Tests use pytest fixtures for deterministic behavior

## Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Push to your fork
6. Open a Pull Request against `main`

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
