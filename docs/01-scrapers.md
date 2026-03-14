# Scrapers

All scrapers inherit from `BaseScraper` and share the same public API. The implementation may vary per provider, but the method signatures are identical.

## Imports

```python
from ani_scrapy import AnimeFLVScraper, JKAnimeScraper, AnimeAV1Scraper
```

## Public Methods

All scrapers provide the following methods:

### search_anime

```python
async def search_anime(query: str, page: int = 1) -> PagedSearchAnimeInfo
```

Searches for anime on the provider site.

**Parameters:**

- `query`: Search term (min 3 characters)
- `page`: Page number (default: 1)

**Raises:**

- `ValueError` for invalid parameters
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

### get_anime_info

```python
async def get_anime_info(anime_id: str, include_episodes: bool = True) -> AnimeInfo
```

Gets detailed anime information.

**Parameters:**

- `anime_id`: Anime identifier
- `include_episodes`: Include episodes in the returned `AnimeInfo` object (default: True)

**Raises:**

- `TypeError` for invalid anime_id
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

### get_new_episodes

```python
async def get_new_episodes(anime_id: str, last_episode_number: int) -> list[EpisodeInfo]
```

Fetches newly released episodes for an anime starting from the last known episode.

**Parameters:**

- `anime_id`: Anime identifier.
- `last_episode_number`: Last known episode number (>=0).

**Returns:**

- A list of `EpisodeInfo` objects representing the new episodes found.

**Raises:**

- `ValueError` if `last_episode_number` is invalid.
- `TypeError` if `anime_id` is invalid.
- `ScraperBlockedError` if the request is blocked.
- `ScraperTimeoutError` on timeout.
- `ScraperParseError` if parsing the response fails.

### get_table_download_links

```python
async def get_table_download_links(anime_id: str, episode_number: int) -> EpisodeDownloadInfo
```

Gets direct download links from table servers.

**Parameters:**

- `anime_id`: Anime identifier
- `episode_number`: Episode number (>=0)

**Raises:**

- `ValueError` for invalid episode_number
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

### get_iframe_download_links

```python
async def get_iframe_download_links(anime_id: str, episode_number: int) -> EpisodeDownloadInfo
```

Gets download links from iframe-embedded content.

**Parameters:**

- `anime_id`: Anime identifier
- `episode_number`: Episode number (>=0)

**Raises:**

- `ValueError` for invalid episode_number
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

### get_file_download_link

```python
async def get_file_download_link(download_info: DownloadLinkInfo) -> str | None
```

Resolves final download URLs from intermediate links.

**Parameters:**

- `download_info`: Download information object

**Raises:**

- `TypeError` for invalid download_info
- `ScraperTimeoutError` on timeout

## Supported Servers

| Service         | AnimeFLV | JKAnime | AnimeAV1 |
| --------------- | -------- | ------- | -------- |
| Streamwish (SW) | ✅       | ✅      | ❌       |
| YourUpload      | ✅       | ❌      | ❌       |
| Mediafire       | ❌       | ✅      | ❌       |
| Pixeldrain      | ❌       | ❌      | ✅       |
| UPNShare        | ❌       | ❌      | ✅       |

---

## Provider-specific Notes

### AnimeFLV

- All methods work with HTTP-only except `get_iframe_download_links` and `get_file_download_link` which require a browser.

### JKAnime

- `get_anime_info` with `include_episodes=True` requires a browser.
- `get_new_episodes` requires a browser.
- `get_table_download_links` requires a browser.
- `get_iframe_download_links` is not supported (returns empty result).

### AnimeAV1

- All methods work with HTTP-only.
- `get_file_download_link` requires a browser only for UPNShare server.

---

## Resource Management

All scrapers implement the async context manager protocol:

```python
async with AnimeFLVScraper() as scraper:
    # ... use scraper
# Resources are automatically closed here
```

You can also manually close resources using `aclose()`:

```python
scraper = AnimeFLVScraper()
try:
    info = await scraper.get_anime_info("anime-id")
finally:
    await scraper.aclose()  # Always close to release resources
```

The `aclose()` method ensures:

- HTTP session is closed
- Browser (if created) is closed
- Playwright context is properly cleaned up
