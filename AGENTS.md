# Agent Guidelines for ani-scrapy

## Build/Lint/Test Commands
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/

# Run single test file
pytest tests/async_api/animeflv.py
pytest tests/sync_api/animeflv.py

# Run specific test function
pytest tests/async_api/animeflv.py::test_function_name

# Code formatting
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

## Code Style

### Imports & Formatting
- Black/isort for formatting (88 char limit)
- Imports: stdlib → third-party → local (absolute imports)

### Naming
- Classes: PascalCase, Functions/vars: snake_case, Constants: UPPER_SNAKE_CASE
- Private methods: prefix with underscore

### Async/Sync Patterns
- Async API: use aiohttp, Sync API: use requests
- Browser contexts: use context managers, proper cleanup

### Data & Error Handling
- Dataclasses for structures, Enums for fixed values
- Use `ani_scrapy.core.exceptions`, log with loguru
- Type hints required, `Optional[T]` for nullable fields

### Testing
- Mock network requests, use pytest-asyncio for async
- Test both sync and async variants