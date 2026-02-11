# Exceptions

All exceptions inherit from `ScraperError` defined in `ani_scrapy.core.exceptions`.

## Exception Hierarchy

```
ScraperError
├── ScraperBlockedError
├── ScraperTimeoutError
├── ScraperParseError
├── ValueError (Python built-in)
└── TypeError (Python built-in)
```

## Exception Types

### ScraperError

Base exception for all scraping-related errors. All other exceptions inherit from this.

```python
try:
    results = await scraper.search_anime("naruto")
except ScraperError as e:
    print(f"Scraping error: {e}")
```

### ScraperBlockedError

Raised when the scraper is blocked by the server (HTTP 403).

```python
from ani_scrapy.core.exceptions import ScraperBlockedError

try:
    results = await scraper.search_anime("naruto")
except ScraperBlockedError:
    print("Access blocked - try again later or use a different IP")
```

### ScraperTimeoutError

Raised when a request times out or server returns HTTP 500.

```python
from ani_scrapy.core.exceptions import ScraperTimeoutError

try:
    results = await scraper.search_anime("naruto")
except ScraperTimeoutError:
    print("Request timed out - check your connection")
```

### ScraperParseError

Raised when HTML content cannot be parsed correctly.

```python
from ani_scrapy.core.exceptions import ScraperParseError

try:
    info = await scraper.get_anime_info(anime_id="123")
except ScraperParseError:
    print("Failed to parse response - website structure may have changed")
```

### ValueError

Raised for invalid parameters (query length, page numbers, episode IDs).

```python
try:
    results = scraper.search_anime("na")  # min 3 characters
except ValueError as e:
    print(f"Invalid parameter: {e}")
```

### TypeError

Raised for incorrect parameter types.

```python
try:
    info = scraper.get_anime_info(anime_id=123)  # should be str
except TypeError as e:
    print(f"Wrong type: {e}")
```

## Error Handling Example

```python
from ani_scrapy.core.exceptions import (
    ScraperBlockedError,
    ScraperTimeoutError,
    ScraperParseError,
    ScraperError
)

try:
    results = await scraper.search_anime("naruto")
    if results.animes:
        anime_info = await scraper.get_anime_info(results.animes[0].id)
        print(f"Success: {anime_info.title}")
except ScraperBlockedError:
    print("Access blocked - try again later or use a different IP")
except ScraperTimeoutError:
    print("Request timed out - check your connection")
except ScraperParseError:
    print("Failed to parse response - website structure may have changed")
except ScraperError as e:
    print(f"Scraping error occurred: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```
