# Testing

## Philosophy

- Prefer HTML fixtures with pytest.
- Avoid real network access in CI.

## Mock Adapters

No mock adapters exist in this project. Tests use pytest fixtures for deterministic behavior.

## Adding Fixtures

Place HTML samples in `tests/fixtures/html/`.

## Running Tests

```bash
pytest tests/
```
