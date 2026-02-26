# ani-scrapy – LLM Integration Guide

## 1. Library Overview

**ani-scrapy** is an async-first Python library for scraping anime websites. It provides a unified interface for extracting anime metadata, episode information, and download links from multiple anime streaming platforms.

### Primary Use Cases

- Building anime download automation tools
- Creating anime metadata aggregators
- Monitoring new episode releases
- Extracting download links from multiple hosting servers

### Supported Platforms

- **AnimeFLV**: Full support (search, info, table downloads, iframe downloads)
- **JKAnime**: Supports search, info, table downloads, file downloads (iframe downloads not supported)

### When to Use This Library

- When you need async/await patterns for concurrent scraping
- When you need unified API across multiple anime sites
- When you need both static (aiohttp) and dynamic (Playwright) content extraction
- When you need structured data with type hints

## 2. Installation

### From PyPI

```bash
pip install ani-scrapy
```

### From GitHub

```bash
pip install git+https://github.com/ElPitagoras14/ani-scrapy.git
```

### Development Installation

```bash
git clone https://github.com/ElPitagoras14/ani-scrapy.git
cd ani-scrapy
pip install -e ".[dev]"
playwright install chromium
```

### Python Version Compatibility

- Python >= 3.10.14 (tested with Python 3.12)

### Browser Requirement

```bash
playwright install chromium
```

**Recommendation**: Use Brave browser for sites with excessive advertising:

- Windows: `C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe`
- Linux: `/usr/bin/brave`
- macOS: `/Applications/Brave Browser.app/Contents/MacOS/Brave Browser`

## 3. Import and Entry Points

### Root Package Import

```python
from ani_scrapy import AnimeFLVScraper, JKAnimeScraper, AsyncBrowser
from ani_scrapy import ScraperError, ScraperBlockedError, ScraperTimeoutError, ScraperParseError
```

### Core Modules

```python
# Base classes and utilities
from ani_scrapy.core import (
    BaseScraper,
    AsyncBrowser,
    AsyncHttpAdapter,
    ScraperError,
    ScraperBlockedError,
    ScraperTimeoutError,
    ScraperParseError,
)

# Data schemas
from ani_scrapy.core import (
    AnimeInfo,
    EpisodeInfo,
    SearchAnimeInfo,
    EpisodeDownloadInfo,
    DownloadLinkInfo,
    PagedSearchAnimeInfo,
    RelatedInfo,
)
```

### CLI Entry Point

```bash
ani-scrapy doctor              # Run diagnostic tool
ani-scrapy doctor --output json  # JSON output for CI/CD
ani-scrapy doctor --timeout 10   # Increase timeout for slow connections
```

## 4. Core Concepts and Mental Model

### Architecture Overview

The library follows a layered architecture:

1. **Base Layer** (`ani_scrapy/core/`):
   - `BaseScraper`: Abstract base class for all scrapers
   - `AsyncHttpAdapter`: HTTP client using aiohttp for static content
   - `AsyncBrowser`: Playwright wrapper for dynamic JavaScript content
   - `schemas`: Pydantic-like dataclasses for data models

2. **Scraper Layer** (`ani_scrapy/animeflv/`, `ani_scrapy/jkanime/`):
   - Platform-specific scraper implementations
   - HTML parsing logic
   - Site-specific constants

3. **CLI Layer** (`ani_scrapy/cli/`):
   - Diagnostic tools
   - Command-line interface

### Context Manager Pattern

All scrapers use async context managers:

```python
# Async context manager (required)
async with AnimeFLVScraper() as scraper:
    results = await scraper.search_anime("naruto")
# Resources are automatically closed here
```

For manual resource management, use `aclose()`:

```python
scraper = AnimeFLVScraper()
try:
    results = await scraper.search_anime("naruto")
finally:
    await scraper.aclose()  # Always close to release resources
```

### Content Extraction Methods

1. **Static (aiohttp + BeautifulSoup)**: For pages with server-rendered HTML
2. **Dynamic (Playwright)**: For JavaScript-rendered content
3. **Mixed**: Automatic fallback between static and dynamic methods

## 5. Public API Reference

### 5.1 Exception Hierarchy

```python
from ani_scrapy.core.exceptions import (
    ScraperError,           # Base exception for all scraping errors
    ScraperTimeoutError,    # Request timeout
    ScraperParseError,      # HTML parsing failure
    ScraperBlockedError,    # Bot detection / IP blocked
)
```

### 5.2 BaseScraper

**Import Path**: `from ani_scrapy.core import BaseScraper`

```python
class BaseScraper(ABC):
    def __init__(
        self,
        headless: bool = True,
        executable_path: str = "",
        external_browser: Optional[AsyncBrowser] = None,
    ) -> None:
        """Initialize the scraper.

        Args:
            headless: Whether to run browser in headless mode. Default: True.
            executable_path: Path to custom browser executable (e.g., Brave).
            external_browser: Inject an existing AsyncBrowser instance.
        """
```

**Methods**:

- `aclose()`: Async resource cleanup (closes HTTP, browser, playwright)
- `start_browser()`: Manually start browser for reuse across operations
- `stop_browser()`: Manually stop the browser
- `_get_browser()`: Get browser instance (internal use)

### 5.3 Logging

Ani-Scrapy uses **Loguru** for all logging but does **not** configure it automatically. You must configure Loguru in your application if you want custom logging behavior.

#### Default Behavior

All scrapers use the global Loguru logger. Without any configuration, logs go to stderr with Loguru's defaults:

```python
from ani_scrapy import AnimeFLVScraper

async with AnimeFLVScraper() as scraper:
    await scraper.search_anime("naruto")
# Logs appear on stderr
```

#### Application-Level Configuration (Recommended)

Configure Loguru once at application startup. All scrapers will inherit this configuration:

```python
from loguru import logger
import sys

logger.configure(
    handlers=[
        {"sink": "app.log", "level": "DEBUG", "enqueue": True},
        {"sink": sys.stderr, "level": "INFO"},
    ]
)

from ani_scrapy import AnimeFLVScraper
# All scrapers now use this configuration
```

### 5.4 AsyncBrowser

**Import Path**: `from ani_scrapy import AsyncBrowser`

```python
class AsyncBrowser:
    """Async browser manager using Playwright with stealth features."""

    def __init__(
        self,
        headless: bool = True,
        executable_path: str | None = None,
        args: list[str] = [],
    ):
        """Initialize the browser.

        Args:
            headless: Run browser in headless mode. Default: True.
            executable_path: Path to custom browser executable.
            args: Additional browser arguments.
        """

    async def __aenter__(self) -> "AsyncBrowser":
        """Start Playwright and launch browser."""

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Clean up browser resources."""

    async def new_page(self):
        """Create a new page in the browser.

        Returns:
            Playwright page object.
        """
```

### 5.5 AsyncHttpAdapter

**Import Path**: `from ani_scrapy.core import AsyncHttpAdapter`

```python
class AsyncHttpAdapter:
    """Async HTTP adapter using aiohttp."""

    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize HTTP adapter.

        Args:
            base_url: Base URL for all requests.
            timeout: Request timeout in seconds. Default: 30.
        """

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
    ) -> str:
        """Perform async GET request.

        Args:
            endpoint: API endpoint (appended to base_url).
            params: Query parameters.

        Returns:
            Response body as string.

        Raises:
            ConnectionError: On network failure.
        """

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
    ) -> str:
        """Perform async POST request.

        Args:
            endpoint: API endpoint.
            data: Form data.

        Returns:
            Response body as string.
        """

    async def close(self) -> None:
        """Close aiohttp session."""
```

### 5.6 Data Schemas

**Import Path**: `from ani_scrapy.core import AnimeInfo, EpisodeInfo, SearchAnimeInfo, etc.`

```python
# Anime type enumeration
class _AnimeType(Enum):
    TV = "TV"
    MOVIE = "Movie"
    OVA = "OVA"
    SPECIAL = "Special"

# Related type enumeration
class _RelatedType(Enum):
    PREQUEL = "Prequel"
    SEQUEL = "Sequel"
    PARALLEL_HISTORY = "Parallel History"
    MAIN_HISTORY = "Main History"

# Search result item
@dataclass
class SearchAnimeInfo(BaseAnimeInfo):
    """Anime info from search results."""
    pass

# Paginated search results
@dataclass
class PagedSearchAnimeInfo:
    page: int
    total_pages: int
    animes: List[SearchAnimeInfo]

# Related anime info
@dataclass
class RelatedInfo:
    id: str
    title: str
    type: _RelatedType

# Episode information
@dataclass
class EpisodeInfo:
    number: int
    anime_id: str
    image_preview: Optional[str] = None

# Full anime information
@dataclass
class AnimeInfo(BaseAnimeInfo):
    synopsis: str
    is_finished: bool
    rating: Optional[str] = None
    other_titles: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    related_info: List[RelatedInfo] = field(default_factory=list)
    next_episode_date: Optional[datetime] = None
    episodes: List[Optional[EpisodeInfo]] = field(default_factory=list)

# Download link from a server
@dataclass
class DownloadLinkInfo:
    server: str
    url: Optional[str] = None

# Episode download information
@dataclass
class EpisodeDownloadInfo:
    episode_number: int
    download_links: List[DownloadLinkInfo]
```

### 5.7 AnimeFLVScraper

**Import Path**: `from ani_scrapy import AnimeFLVScraper`

```python
class AnimeFLVScraper(BaseScraper):
    """Scraper for AnimeFLV website."""

    def __init__(
        self,
        headless: bool = True,
        executable_path: str = "",
    ):
        """Initialize AnimeFLV scraper.

        Args:
            headless: Run browser in headless mode.
            executable_path: Path to custom browser executable.
        """
```

### 5.8 JKAnimeScraper

**Import Path**: `from ani_scrapy import JKAnimeScraper`

```python
class JKAnimeScraper(BaseScraper):
    """Scraper for JKAnime website."""

    def __init__(
        self,
        headless: bool = True,
        executable_path: str = "",
    ):
        """Initialize JKAnime scraper.

        Args:
            headless: Run browser in headless mode.
            executable_path: Path to custom browser executable.
        """
```

## 6. Usage Patterns (LLM-Optimized)

### Minimal Quick Start

```python
import asyncio
from ani_scrapy import AnimeFLVScraper

async def main():
    async with AnimeFLVScraper() as scraper:
        results = await scraper.search_anime(query="naruto")
        print(f"Found {len(results.animes)} results")

        if results.animes:
            info = await scraper.get_anime_info(anime_id=results.animes[0].id)
            print(f"Title: {info.title}")

asyncio.run(main())
```

### Typical Workflow: Search, Get Info, Get Downloads

```python
import asyncio
from ani_scrapy import AnimeFLVScraper

async def main():
    async with AnimeFLVScraper() as scraper:
        # 1. Search for anime
        search_results = await scraper.search_anime(query="one piece")

        if not search_results.animes:
            print("No results found")
            return

        anime = search_results.animes[0]
        print(f"Selected: {anime.title} ({anime.id})")

        # 2. Get detailed info
        info = await scraper.get_anime_info(
            anime_id=anime.id,
            include_episodes=True
        )
        print(f"Episodes: {len(info.episodes)}")
        print(f"Genres: {', '.join(info.genres)}")

        # 3. Get download links for first episode
        if info.episodes:
            first_ep = info.episodes[0]
            if first_ep:
                download_links = await scraper.get_table_download_links(
                    anime_id=anime.id,
                    episode_number=first_ep.number
                )
                for link in download_links.download_links:
                    print(f"Server: {link.server}, URL: {link.url}")

asyncio.run(main())
```

### Concurrent Scraping

```python
import asyncio
from ani_scrapy import AnimeFLVScraper

async def get_anime_info_batch(scraper, anime_ids):
    """Scrape multiple anime IDs concurrently."""
    tasks = [
        scraper.get_anime_info(anime_id)
        for anime_id in anime_ids
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions
    valid_results = [r for r in results if not isinstance(r, Exception)]
    return valid_results

async def main():
    anime_ids = ["naruto", "one-piece", "bleach", "fairy-tail", "hunter-x-hunter"]

    async with AnimeFLVScraper() as scraper:
        results = await get_anime_info_batch(scraper, anime_ids)

        for info in results:
            print(f"{info.title}: {len(info.episodes)} episodes")

asyncio.run(main())
```

### Manual Browser Control

```python
import asyncio
from ani_scrapy import AsyncBrowser

async def main():
    async with AsyncBrowser(headless=True) as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")

        # Your custom Playwright automation here
        title = await page.title()
        print(f"Page title: {title}")

asyncio.run(main())
```

### Browser Usage Patterns

#### Pattern 1: Automatic (Default)

Browser is created automatically when needed and closed after each operation:

```python
async with JKAnimeScraper() as scraper:
    info = await scraper.get_anime_info("anime-id", include_episodes=True)
# Browser automatically closed
```

#### Pattern 2: Manual Start/Stop

Reuse browser for multiple operations to improve performance:

```python
async with JKAnimeScraper() as scraper:
    await scraper.start_browser()  # Start manually
    
    info = await scraper.get_anime_info("anime-id", include_episodes=True)
    links = await scraper.get_table_download_links("anime-id", episode=1)
    final_url = await scraper.get_file_download_link(links.download_links[0])
    
    await scraper.stop_browser()  # Optional - also called on aclose()
```

#### Pattern 3: External Browser Injection

Inject an existing AsyncBrowser instance:

```python
async with AsyncBrowser(headless=True) as browser:
    async with JKAnimeScraper(external_browser=browser) as scraper:
        info = await scraper.get_anime_info("anime-id")
        # Uses the injected browser
```

## 7. Common Task Recipes

### Recipe 1: Configure Logging

```python
from loguru import logger
import sys

# Configure Loguru once at application startup
logger.configure(
    handlers=[
        {"sink": "app.log", "level": "DEBUG", "enqueue": True},
        {"sink": sys.stderr, "level": "INFO"},
    ]
)

# All scrapers will use this configuration automatically
```

### Recipe 2: Error Handling

```python
from ani_scrapy import AnimeFLVScraper
from ani_scrapy.core.exceptions import (
    ScraperError,
    ScraperBlockedError,
    ScraperTimeoutError,
    ScraperParseError,
)

async def main():
    try:
        async with AnimeFLVScraper() as scraper:
            results = await scraper.search_anime("naruto")

    except ScraperBlockedError:
        print("IP blocked - try using a different IP or wait")
    except ScraperTimeoutError:
        print("Request timed out - check connection")
    except ScraperParseError:
        print("Website structure changed - library may need update")
    except ScraperError as e:
        print(f"Scraping error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

### Recipe 3: Get Download Links

```python
from ani_scrapy import JKAnimeScraper

async def main():
    async with JKAnimeScraper() as scraper:
        # Get table download links
        links = await scraper.get_table_download_links(
            anime_id="naruto",
            episode_number=1
        )

        # Get file URL from a link
        for link in links.download_links:
            if link.url:
                file_url = await scraper.get_file_download_link(link)
                print(f"{link.server}: {file_url}")
```

### Recipe 4: Monitor New Episodes

```python
from ani_scrapy import AnimeFLVScraper

LAST_KNOWN_EPISODE = 500  # Track externally

async def main():
    async with AnimeFLVScraper() as scraper:
        new_episodes = await scraper.get_new_episodes(
            anime_id="one-piece",
            last_episode_number=LAST_KNOWN_EPISODE
        )

        if new_episodes:
            print(f"Found {len(new_episodes)} new episodes!")
            for ep in new_episodes:
                print(f"Episode {ep.number}: {ep.image_preview}")
        else:
            print("No new episodes")
```

### Recipe 5: Dual Platform Search

```python
import asyncio
from ani_scrapy import AnimeFLVScraper, JKAnimeScraper

async def search_both_platforms(query):
    async with AnimeFLVScraper() as flv, JKAnimeScraper() as jk:
        flv_results, jk_results = await asyncio.gather(
            flv.search_anime(query),
            jk.search_anime(query)
        )

        print(f"AnimeFLV: {len(flv_results.animes)} results")
        print(f"JKAnime: {len(jk_results.animes)} results")

        return flv_results.animes, jk_results.animes

asyncio.run(search_both_platforms("naruto"))
```

## 8. Best Practices for LLM Code Generation

### Recommended Calling Patterns

1. **Always use async context managers**:

   ```python
   # CORRECT
   async with AnimeFLVScraper() as scraper:
       results = await scraper.search_anime("query")

   # AVOID (will not work properly)
   scraper = AnimeFLVScraper()
   results = await scraper.search_anime("query")
   ```

2. **Handle empty results**:
   ```python
   results = await scraper.search_anime("query")
   if not results.animes:
       print("No results")
       return
   anime = results.animes[0]
   ```

### Common Pitfalls to Avoid

1. **Forgetting to await async methods**:

   ```python
   # WRONG
   results = scraper.search_anime("query")

   # CORRECT
   results = await scraper.search_anime("query")
   ```

2. **Using sync methods instead of async**:
   - All scraper methods are async
   - Must use `await` and `asyncio.run()`

3. **Not handling None values in download links**:

   ```python
   # Some links may have url=None
   if link.url:  # Check before using
       file_url = await scraper.get_file_download_link(link)
   ```

4. **Using page numbers incorrectly**:
   - `search_anime` page must be >= 1
   - `episode_number` must be >= 0

### Idiomatic Usage

```python
# Use dataclass attributes directly
info = await scraper.get_anime_info(anime_id)
print(info.title)           # str
print(info.rating)           # Optional[str] - may be None
print(info.genres)          # List[str]
print(info.episodes)        # List[Optional[EpisodeInfo]]

# EpisodeInfo may be None in the list
for ep in info.episodes:
    if ep:  # Check for None
        print(f"Episode {ep.number}")
```

## 9. Limitations and Constraints

### Known Limitations

1. **JKAnime iframe downloads**: Not supported (method returns empty list)
2. **Pagination**: JKAnime search always returns page 1
3. **Rate limiting**: No built-in rate limiting - implement your own if needed
4. **No caching**: Each request fetches fresh data
5. **Browser dependency**: Some features require Playwright/Chromium

### Assumptions in the Code

1. **Network connectivity**: Assumes reliable internet connection
2. **Website structure**: Parsers rely on specific HTML structure - may break with site updates
3. **Single context manager usage**: Scrapers are designed for single context entry

### Performance Considerations

1. **Concurrent operations**: Use `asyncio.gather()` for batch scraping
2. **Browser resources**: Each `AsyncBrowser` instance launches a Chromium process
3. **Memory**: Episode lists can be large for long-running anime series
4. **Timeout defaults**: 30 seconds for HTTP, configurable timeouts for browser operations

### Edge Cases

1. **Empty search results**: `PagedSearchAnimeInfo.animes` may be empty list
2. **Missing optional fields**: `rating`, `other_titles`, `genres` may be empty
3. **None in episodes list**: Some positions may contain None
4. **Download link unavailable**: `url` field may be None in `DownloadLinkInfo`

### Windows-Specific Issues

On Windows with Python 3.14+, you may see warnings at script exit:

```
Exception ignored in: _ProactorBasePipeTransport.__del__
ValueError: I/O operation on closed pipe
```

This is a known issue with Python's ProactorEventLoop and Playwright's subprocess cleanup timing. The script runs correctly - these are cosmetic warnings.

**Solutions:**

1. Use `asyncio.run()` (recommended):
```python
asyncio.run(main())
```

2. For Python 3.10-3.13, use:
```python
asyncio.get_event_loop().run_until_complete(main())
```

**Notes:**
- These warnings are cosmetic only - the script works correctly
- This only affects Windows; Linux/macOS are unaffected
- The library properly closes all resources (browser, context, playwright) via `aclose()`

## 10. Internal Architecture Summary (For Reasoning)

### Component Interactions

```
User Code
    |
    v
+---------------------+
|  AnimeFLVScraper   |  (or JKAnimeScraper)
|   (BaseScraper)    |
+----------+----------+
           |
    +------+-------+
    |            |
    v            v
+----------+ +----------+
|AsyncHttp | |AsyncBrowser|
|Adapter   | |(Playwright)|
+----------+ +----------+
    |            |
    v            v
+----------+ +----------+
| aiohttp  | | Chromium |
| requests | | browser  |
+----------+ +----------+
```

### Data Flow

1. **Search**: HTTP request -> Parse HTML -> `PagedSearchAnimeInfo`
2. **Anime Info**: HTTP request -> Parse HTML -> `AnimeInfo` (optionally with episodes via Playwright)
3. **Download Links (Static)**: HTTP request -> Parse HTML -> `EpisodeDownloadInfo`
4. **Download Links (Dynamic)**: Playwright page -> Extract iframe URLs -> `EpisodeDownloadInfo`
5. **File URLs**: Playwright page -> Navigate to server -> Extract final download URL

### Key Design Decisions

1. **Async-first**: All I/O operations are async for concurrent performance
2. **Context managers**: Automatic resource cleanup for HTTP sessions and browsers
3. **Task ID logging**: Enables correlation across complex multi-step operations
4. **Separate static/dynamic methods**: Allows choosing appropriate extraction method
5. **Dataclasses**: Type-safe data models with sensible defaults

### Extension Points

To add a new scraper:

1. Create new module in `src/ani_scrapy/<site>/`
2. Inherit from `BaseScraper`
3. Implement required methods (`search_anime`, `get_anime_info`, etc.)
4. Add parser module for site-specific HTML parsing
5. Define site constants (BASE_URL, endpoints, etc.)
6. Export scraper class from `ani_scrapy/__init__.py`
