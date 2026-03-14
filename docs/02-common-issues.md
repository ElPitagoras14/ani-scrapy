# Common Issues

## Playwright Not Installed

```bash
playwright install chromium
```

## Tests Are Trying to Use Network

Prefer writing tests using `MockHttp` and HTML fixtures in `tests/fixtures/html/`.

## Windows: "unclosed transport" or "I/O operation on closed pipe"

When running on Playwright Windows with Python, you may see warnings like:

```
Exception ignored in: _ProactorBasePipeTransport.__del__
ValueError: I/O operation on closed pipe
```

This is a known issue with Python's ProactorEventLoop and Playwright's subprocess cleanup timing. The script still runs correctly, but these warnings appear on exit.

### Solution

**Use `get_event_loop()`**

```python
import asyncio

async def main():
    async with JKAnimeScraper() as scraper:
        # ... your code

asyncio.get_event_loop().run_until_complete(main())
```

### Notes

- These warnings are **cosmetic only** - the script works correctly
- This issue is specific to Windows; Linux/macOS do not exhibit this behavior
- The library properly closes all resources (browser, context, playwright) via `aclose()`
