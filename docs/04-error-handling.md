# Error Handling

ani-scrapy provides a structured exception hierarchy for handling different error scenarios.

## Exception Hierarchy

```
ScraperError (base)
├── ScraperTimeoutError
├── ScraperParseError
└── ScraperBlockedError
```

## Exception Types

### ScraperError

Base exception for all scraping-related errors. All other exceptions inherit from this class.

```python
from ani_scrapy import ScraperError

try:
    info = await scraper.get_anime_info("anime-id")
except ScraperError as e:
    print(f"Scraping error: {e}")
```

### ScraperTimeoutError

Request failed due to timeout. This is typically a transient error.

```python
from ani_scrapy import ScraperTimeoutError
import asyncio

try:
    info = await scraper.get_anime_info("anime-id")
except ScraperTimeoutError:
    print("Request timed out, retrying...")
    await asyncio.sleep(2)
    info = await scraper.get_anime_info("anime-id")
```

**When it occurs:**

- Network is slow or unreachable
- Site is taking too long to respond
- Browser failed to load page within timeout

**Recommendation:** Implement retry logic with exponential backoff.

### ScraperParseError

HTML structure is invalid or unexpected. This usually indicates the site structure changed.

```python
from ani_scrapy import ScraperParseError

try:
    info = await scraper.get_anime_info("anime-id")
except ScraperParseError as e:
    print(f"Failed to parse response: {e}")
    # Site structure may have changed
```

**When it occurs:**

- Site HTML structure changed
- Required CSS selectors no longer exist
- API response format changed

**Recommendation:** Check if site structure changed and update parser if needed.

### ScraperBlockedError

The site blocked the request (bot detection).

```python
from ani_scrapy import ScraperBlockedError

try:
    info = await scraper.get_anime_info("anime-id")
except ScraperBlockedError:
    print("IP blocked by site")
    # Consider using Brave browser or waiting
```

**When it occurs:**

- Too many requests in short period
- Suspicious request patterns detected
- IP address flagged as bot

**Recommendations:**

- Use Brave browser for better ad-block capabilities
- Add delays between requests
- Rotate IP if consistently blocked

## Handling Strategy

### Try-Except Pattern

```python
import asyncio
from ani_scrapy import (
    AnimeFLVScraper,
    ScraperError,
    ScraperTimeoutError,
    ScraperParseError,
    ScraperBlockedError,
)

async def robust_scraping():
    async with AnimeFLVScraper() as scraper:
        try:
            info = await scraper.get_anime_info("anime-id")
            return info
        except ScraperTimeoutError:
            print("Timeout - will retry")
            await asyncio.sleep(5)
            return await scraper.get_anime_info("anime-id")
        except ScraperParseError as e:
            print(f"Parse error: {e}")
            return None
        except ScraperBlockedError:
            print("Blocked - try using Brave browser")
            return None
        except ScraperError as e:
            print(f"Unexpected error: {e}")
            return None
```

### Retry Decorator

```python
import functools
import asyncio
from ani_scrapy import ScraperTimeoutError, ScraperBlockedError

def with_retry(max_retries=3, delay=2):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ScraperTimeoutError, ScraperBlockedError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))
            raise last_exception
        return wrapper
    return decorator

@with_retry(max_retries=3, delay=2)
async def fetch_with_retry(scraper, anime_id):
    return await scraper.get_anime_info(anime_id)
```

## Error Codes Reference

| Exception              | Code | Recoverable |
|------------------------|------|-------------|
| ScraperTimeoutError    | 1    | Yes         |
| ScraperParseError      | 2    | No*         |
| ScraperBlockedError    | 3    | Yes         |

*ParseError may be recoverable if site structure is updated in the parser.

## Logging Errors

Enable debug logging to troubleshoot errors:

```python
from ani_scrapy import enable_logging

enable_logging(level="DEBUG")

# Now all HTTP requests and responses are logged
```
