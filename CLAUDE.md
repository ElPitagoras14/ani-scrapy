# ani-scrapy

## Setup

- Use `uv` for packages and `.venv` to run scripts and tests

## Code Style

- No conditional imports; absolute imports for package modules, relative for same directory
- Type hints on function signatures (Python 3.11+); avoid `Any`
- Prefer async/await; provide async context managers when appropriate
- Errors: use the hierarchy `ScraperError` -> `ScraperNotFoundError`, `ScraperBlockedError`, `ScraperHTTPError`, `ScraperTimeoutError`, `ScraperParseError`
- Logging: use `loguru.logger`. The library never configures Loguru: never call `logger.remove()` or modify global handlers in library code
- No comments unless explaining complex logic; concise docstrings (parameters and return values) on public functions and classes
- CLI: `typer`, entry point `ani-scrapy` with subcommands (e.g. `ani-scrapy doctor`), `--help` on all commands

## Project Principles

- Simplicity, clarity and maintainability over complexity; no over-engineering or premature abstractions
- Explicit over clever; design for incremental evolution, suited to a solo-maintained project
- Parsing logic lives in parsers, network coordination in scrapers
- Clarify the problem before proposing solutions; offer alternatives with brief trade-offs when a real decision exists
- Suggest design patterns only when they add real value
- Docs, skills and `CLAUDE.md` stay concise: say each thing once, in one place, and drop what the reader does not need

## Workflow

- Changes users can notice update `CHANGELOG.md` and bump the version in the same PR
- Public API changes also update the usage skill (`.claude/skills/ani-scrapy/SKILL.md`)
- Merging to `main` publishes to PyPI; never tag or publish by hand
- Provider fixes, new providers and releases: use the `ani-scrapy-dev` skill

## Git

- Branches: `<type>/<short-description>` in kebab-case, types `feat|fix|refactor|chore`
- Commits: `<type>(scope): <description>`, lowercase, imperative, max ~72 chars; as few commits as possible (usually one per change); if there are several, commit `pyproject.toml` last
- Do NOT commit unless explicitly asked
- Commits must NOT list Claude as co-author (no `Co-Authored-By` trailer); `.githooks/commit-msg` strips it as a backstop
- PR titles follow the commit format; labels: `feature` (feat), `bug` (fix), `maintenance` (refactor/chore/docs)

## OpenSpec: applying a change

- On `main`: verify `main` is up to date with the remote, create a new branch from it without upstream, and do the work there
- On any other branch: ask whether to (a) create a new branch from `main`, (b) create a new branch from the current one, or (c) work on the current branch
