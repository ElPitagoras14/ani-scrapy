# Error Handling

ani-scrapy provides a structured exception hierarchy for handling different error scenarios.

## Exception Hierarchy

```
ScraperError (base)
├── ScraperNotFoundError
├── ScraperBlockedError
├── ScraperHTTPError
├── ScraperTimeoutError
└── ScraperParseError
```

All exceptions are direct children of `ScraperError`; none inherits from another. Every exception has an optional `status_code` attribute (`int | None`) with the HTTP status when the error comes from a response, and `None` otherwise.

| Condition                                   | Exception              | `status_code` |
|---------------------------------------------|------------------------|---------------|
| HTTP 404 or 410                             | ScraperNotFoundError   | 404 / 410     |
| HTTP 403 or 429                             | ScraperBlockedError    | 403 / 429     |
| Other HTTP error status (e.g. 500, 503)     | ScraperHTTPError       | the status    |
| Connection failure without a response       | ScraperHTTPError       | `None`        |
| Request timed out                           | ScraperTimeoutError    | `None`        |
| Unexpected HTML or missing data             | ScraperParseError      | `None`        |

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

### ScraperNotFoundError

The anime or episode does not exist (HTTP 404 or 410).

```python
from ani_scrapy import ScraperNotFoundError

try:
    info = await scraper.get_anime_info("anime-id")
except ScraperNotFoundError as e:
    print(f"Not found (HTTP {e.status_code})")
```

**Recommendation:** Do not retry; check the anime id.

### ScraperHTTPError

The site answered with an error status other than not found or blocked (for example 500 or 503), or the connection failed before any response (`status_code` is `None`).

```python
from ani_scrapy import ScraperHTTPError

try:
    info = await scraper.get_anime_info("anime-id")
except ScraperHTTPError as e:
    print(f"HTTP failure (status {e.status_code})")
```

**Recommendation:** Retry later; the site may be down.

### ScraperTimeoutError

Request failed due to timeout. This is typically a transient error. Other HTTP failures are reported as `ScraperHTTPError`.

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

- Site is taking too long to respond
- Request exceeded the configured timeout

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
- AnimeAV1 page without media data (layout change, error page served with HTTP 200 or anti-bot challenge); this raises instead of returning an empty result

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
    AnimeAV1Scraper,
    ScraperBlockedError,
    ScraperError,
    ScraperHTTPError,
    ScraperNotFoundError,
    ScraperParseError,
    ScraperTimeoutError,
)

async def robust_scraping():
    async with AnimeAV1Scraper() as scraper:
        try:
            info = await scraper.get_anime_info("anime-id")
            return info
        except ScraperNotFoundError:
            print("Anime does not exist")
            return None
        except (ScraperTimeoutError, ScraperHTTPError):
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
from ani_scrapy import (
    ScraperBlockedError,
    ScraperHTTPError,
    ScraperTimeoutError,
)

def with_retry(max_retries=3, delay=2):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ScraperTimeoutError, ScraperHTTPError, ScraperBlockedError) as e:
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

## Recoverability

| Exception              | Recoverable |
|------------------------|-------------|
| ScraperNotFoundError   | No          |
| ScraperBlockedError    | Yes         |
| ScraperHTTPError       | Yes*        |
| ScraperTimeoutError    | Yes         |
| ScraperParseError      | No**        |

*Retry only makes sense for 5xx and connection failures.
**ParseError may be recoverable if site structure is updated in the parser.

## Logging Errors

Enable debug logging to troubleshoot errors:

```python
from ani_scrapy import enable_logging

enable_logging(level="DEBUG")

# Now all HTTP requests and responses are logged
```
