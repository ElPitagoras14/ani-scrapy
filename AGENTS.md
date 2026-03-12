# Agent Guidelines for ani-scrapy

## Code Style Guidelines

### Package Management

- Use `uv` for package management

### Imports

- Group imports in this order: standard library, third-party, local application
- Use absolute imports for package modules
- Sort imports alphabetically within each group
- Don't use conditional imports

### Types

- Use type hints for function signatures (Python 3.10+)
- Avoid `Any` - be specific when possible

### Naming Conventions

- **Classes**: PascalCase (e.g., `AnimeFLVScraper`, `ScraperError`)
- **Functions/Variables**: snake_case (e.g., `search_anime`, `get_system_ram`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_FORMAT`, `STATUS_PASS`)
- **Private methods**: prefix with `_` (e.g., `_check_environment`)

### Async/Await Patterns

- Prefer async/await throughout the codebase
- Provide async context managers when appropriate

### Error Handling

- Use custom exception hierarchy: `ScraperError` -> `ScraperTimeoutError`, `ScraperParseError`, `ScraperBlockedError`
- Log errors with `loguru.logger`
- Use context managers for resource cleanup

### Logging

- Use `loguru.logger` throughout the codebase
- The library does NOT configure Loguru - users must configure it in their application
- Never call `logger.remove()` or modify global handlers in library code
- For simple scripts, users can configure Loguru before using scrapers

### Comments

- Avoid comments unless explaining complex logic
- Use docstrings for public functions and classes
- Keep docstrings concise and focused on parameters and return values
- NO comments in code unless absolutely necessary (per project rules)

### CLI Commands

- Use `typer` for CLI commands
- Entry point: `ani-scrapy` with subcommands
- Diagnostic command: `ani-scrapy doctor`
- Include `--help` for all commands

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

## Git Conventions

Ignore `tasks` folder in commits

### Branch Naming Convention

Format: `<type>/<short-description>`

Rules:

- use kebab-case
- keep short and descriptive
- prefix with change type

Minimal types:

- `feat` -> new feature
- `fix` -> bug fix
- `refactor` -> code improvement without behavior change
- `chore` -> maintenance, config, dependencies, CI, docs

Git CLI:

```bash
# Create branch
git checkout -b feat/add-user-authentication

# Push branch
git push -u origin feat/add-user-authentication
```

---

### Commit Message Convention

Header format: `<type>(scope): <short description>`

Rules:

- lowercase
- imperative mood
- max ~72 chars
- scope optional
- use body description for longer descriptions

Minimal types:

- `feat` -> new feature
- `fix` -> bug fix
- `refactor` -> code improvement without behavior change
- `chore` -> maintenance, dependencies, CI, docs

Examples:

```
feat(auth): add JWT authentication
```

```
feat(discovery): implement SNMP device discovery

Adds SNMP-based discovery to automatically detect devices
in a network segment.

This allows network engineers to bootstrap inventory faster.
```

Optional body:

```bash
git commit -m "feat(auth): add JWT authentication" -m "Adds JWT middleware and token validation."
```

Git CLI:

```bash
git add .
git commit -m "feat(auth): add JWT authentication"
git push
```

---

### Pull Request Convention

Title format: Same as commit convention

Body: PR description template

Labels: Recommended labels

- `feature` - new features (type: feat)
- `bug` - bug fixes (type: fix)
- `maintenance` - refactor, chore, docs, etc.

GitHub CLI:

```bash
# Create PR
gh pr create --fill --label feature
```
