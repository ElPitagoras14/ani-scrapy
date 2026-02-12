# Agent Guidelines for ani-scrapy

This document defines how an LLM or coding agent should reason and behave when helping to plan, design, or implement this project. These guidelines apply to all analysis, planning, design, and code-related assistance within this repository.

---

## Role

You act as a software architect and senior developer. Your goal is to help plan, design, and evolve the project in a clear, modern, and pragmatic way. Prioritize long-term maintainability and clarity over short-term speed.

---

## Commands

### Installation

```bash
pip install -e ".[dev]"        # Install with dev dependencies
pip install -e "."              # Install without dev dependencies
pip install -e ".[examples]"   # Install with examples dependencies
```

### Testing

```bash
pytest tests/                              # all tests
pytest tests/unit/test_file.py              # single file
pytest tests/unit/test_file.py::test_func  # single test
pytest tests/ -v                           # verbose output
pytest tests/ -k "test_name"              # run tests matching pattern
```

### Linting and Type Checking

```bash
# Currently, no formal linting configured
# Code style follows Python standard conventions
```

---

## Code Style Guidelines

### Imports

- Group imports in this order: standard library, third-party, local application
- Use absolute imports for package modules
- Sort imports alphabetically within each group

```python
# Correct
import asyncio
from pathlib import Path
from typing import Optional

import aiohttp
from rich import print as rprint

from ani_scrapy.core.base import BaseScraper
```

### Types

- Use type hints for function signatures
- Use `Optional[T]` instead of `T | None`
- Use `List[T]`, `Dict[K, V]` from `typing`
- Avoid `Any` - be specific when possible

```python
async def search_anime(
    self,
    query: str,
    page: int = 1,
    task_id: Optional[str] = None,
) -> PagedSearchAnimeInfo:
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `AnimeFLVScraper`, `ScraperError`)
- **Functions/Variables**: snake_case (e.g., `search_anime`, `get_system_ram`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_FORMAT`, `STATUS_PASS`)
- **Private methods**: prefix with `_` (e.g., `_check_environment`)
- **Task IDs**: use English alphanumeric characters (no accents)

### Async/Await Patterns

- Prefer async/await throughout the codebase
- Provide both sync and async context managers when appropriate
- Use `async def __aenter__` and `async def __aexit__`
- Always handle `aiohttp.ClientSession` properly with async context

```python
async def __aenter__(self) -> "AsyncBrowser":
    return self

async def __aexit__(self, *args) -> None:
    await self.aclose()
```

### Error Handling

- Use custom exception hierarchy: `ScraperError` -> `ScraperTimeoutError`, `ScraperParseError`, `ScraperBlockedError`
- Log errors with `loguru.logger` using `task_id` for correlation
- Use context managers for resource cleanup
- Define exceptions in `src/ani_scrapy/core/exceptions.py`

```python
class ScraperError(Exception):
    """Base exception for all scraping-related errors."""

class ScraperTimeoutError(ScraperError):
    """Failed to fetch due to a timeout."""
```

### Logging

- Use `loguru.logger` throughout
- Create logger with `create_scraper_logger(task_id)` for correlation
- Define default format in `src/ani_scrapy/core/base.py`
- Include `task_id` in all log messages for tracking

```python
from ani_scrapy.core.base import create_scraper_logger

log = create_scraper_logger(task_id)
log.info("Searching anime | query={query}", query=query)
```

### Comments

- Avoid comments unless explaining complex logic
- Use docstrings for public functions and classes
- Keep docstrings concise and focused on parameters and return values
- NO comments in code unless absolutely necessary (per project rules)

### File Structure

```
src/ani_scrapy/
├── __init__.py              # Public exports
├── animeflv/
│   ├── __init__.py
│   ├── scraper.py          # Coordination logic
│   ├── parser.py           # HTML parsing
│   └── constants.py       # Site-specific constants
├── jkanime/
│   ├── __init__.py
│   ├── scraper.py
│   ├── parser.py
│   └── constants.py
├── core/
│   ├── __init__.py
│   ├── base.py             # BaseScraper, logging utilities
│   ├── http.py            # HTTP adapters
│   ├── browser.py         # Playwright browser
│   ├── schemas.py         # Pydantic/data classes
│   ├── exceptions.py      # Exception hierarchy
│   ├── constants/
│   │   ├── __init__.py
│   │   └── general.py      # General constants
└── cli/
    ├── __init__.py
    ├── main.py             # CLI entry point (ani-scrapy doctor)
    └── doctor.py           # Diagnostic tool
```

### CLI Commands

- Use `typer` for CLI commands
- Entry point: `ani-scrapy` with subcommands
- Diagnostic command: `ani-scrapy doctor`
- Include `--help` for all commands
- Use `typer.echo()` for output

```python
@app.command()
def doctor(
    output: str = typer.Option("text", "--output", "-o"),
    timeout: int = typer.Option(5, "--timeout", "-t"),
):
    """Run ani-scrapy doctor diagnostic tool."""
```

---

## Project Principles

- Prioritize simplicity, clarity, and maintainability over complexity
- Avoid over-engineering and premature abstractions
- Design for incremental evolution, not hypothetical scalability
- Prefer explicit, easy-to-understand solutions over clever or implicit ones
- Keep parsing logic in parsers, network coordination in scrapers
- Do not introduce new dependencies without clear justification
- Prefer solutions that fit a small team or solo-maintained project

---

## Planning and Design Behavior

- Clarify the problem before proposing solutions
- Separate responsibilities naturally, without forcing architectural layers
- Propose alternatives when relevant decisions exist
- Briefly explain trade-offs between alternatives
- Do not impose design patterns; suggest them only when they add real value
