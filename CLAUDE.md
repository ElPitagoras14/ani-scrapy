# ani-scrapy

## Setup

- Use `uv` for packages and `.venv` to run scripts and tests

## Code Style

- No conditional imports; absolute imports for package modules, relative for same directory
- Type hints on function signatures (Python 3.10+); avoid `Any`
- Prefer async/await; provide async context managers when appropriate
- Errors: use the hierarchy `ScraperError` -> `ScraperTimeoutError`, `ScraperParseError`, `ScraperBlockedError`
- Logging: use `loguru.logger`. The library never configures Loguru: never call `logger.remove()` or modify global handlers in library code
- No comments unless explaining complex logic; concise docstrings (parameters and return values) on public functions and classes
- CLI: `typer`, entry point `ani-scrapy` with subcommands (e.g. `ani-scrapy doctor`), `--help` on all commands

## Project Principles

- Simplicity, clarity and maintainability over complexity; no over-engineering or premature abstractions
- Explicit over clever; design for incremental evolution, suited to a solo-maintained project
- Parsing logic lives in parsers, network coordination in scrapers
- Clarify the problem before proposing solutions; offer alternatives with brief trade-offs when a real decision exists
- Suggest design patterns only when they add real value

## Git

- Branches: `<type>/<short-description>` in kebab-case, types `feat|fix|refactor|chore`
- Commits: `<type>(scope): <description>`, lowercase, imperative, max ~72 chars, small but complete; commit `pyproject.toml` last when it changes
- Do NOT commit unless explicitly asked
- Commits must NOT list Claude as co-author (no `Co-Authored-By` trailer)
- PR titles follow the commit format; labels: `feature` (feat), `bug` (fix), `maintenance` (refactor/chore/docs)

## OpenSpec: applying a change

- On `main`: verify `main` is up to date with the remote, create a new branch from it without upstream, and do the work there
- On any other branch: ask whether to (a) create a new branch from `main`, (b) create a new branch from the current one, or (c) work on the current branch
