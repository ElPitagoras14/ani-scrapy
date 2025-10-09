# API Reference

## Table of Contents

- [Core Classes](#core-classes)
- [Data Models](#data-models)
- [AnimeFLVScraper Methods](#animeflvscraper-methods)
- [JKAnimeScraper Methods](#jkanimescraper-methods)
- [Browser Classes](#browser-classes)
- [Exceptions](#exceptions)

## Core Classes

### AsyncBaseScraper

Abstract base class for async anime scrapers.

**Methods:**

- `init(verbose: bool = False, level: str = "INFO") -> None`
- `search_anime(query: str, **kwargs) -> PagedSearchAnimeInfo`
- `get_anime_info(anime_id: str, include_episodes: bool = True, tab_timeout: int = 200, **kwargs) -> AnimeInfo`
- `get_new_episodes(self, anime_id: str, last_episode_number: int, tab_timeout: int = 200, browser: Optional[AsyncBrowser] = None,) -> List[EpisodeInfo]`
- `get_table_download_links(anime_id: str, episode_number: int, **kwargs) -> EpisodeDownloadInfo`
- `get_iframe_download_links(anime_id: str, episode_number: int, browser: Optional[AsyncBrowser] = None) -> EpisodeDownloadInfo`
- `get_file_download_link(download_info: DownloadLinkInfo, browser: Optional[AsyncBrowser] = None) -> str`

### SyncBaseScraper

Abstract base class for sync anime scrapers.

**Methods:**

- `init(verbose: bool = False, level: str = "INFO") -> None`
- `search_anime(query: str, **kwargs) -> PagedSearchAnimeInfo`
- `get_anime_info(anime_id: str, include_episodes: bool = True, tab_timeout: int = 200, **kwargs) -> AnimeInfo`
- `get_new_episodes(self, anime_id: str, last_episode_number: int, tab_timeout: int = 200, browser: Optional[SyncBrowser] = None,) -> List[EpisodeInfo]`
- `get_table_download_links(anime_id: str, episode_number: int, **kwargs) -> EpisodeDownloadInfo`
- `get_iframe_download_links(anime_id: str, episode_number: int, browser: Optional[SyncBrowser] = None) -> EpisodeDownloadInfo`
- `get_file_download_link(download_info: DownloadLinkInfo, browser: Optional[SyncBrowser] = None) -> str`

**Note:** The synchronous scrapers (`AnimeFLVScraperSync`, `JKAnimeScraperSync`) have identical method signatures and parameters as their async counterparts, but without the `async/await` keywords.

## Data Models

### BaseAnimeInfo

```python
class BaseAnimeInfo:
    id: str
    title: str
    type: _AnimeType
    poster: str
```

### SearchAnimeInfo

Extends `BaseAnimeInfo`

### PagedSearchAnimeInfo

```python
page: int
total_pages: int
animes: List[SearchAnimeInfo]
```

### RelatedInfo

```python
id: str
title: str
type: _RelatedType
```

### EpisodeInfo

```python
id: str
anime_id: str
number: int
image_preview: Optional[str] = None
```

### AnimeInfo

Extends `BaseAnimeInfo` with:

```python
synopsis: str
is_finished: bool
rating: Optional[str] = None
other_titles: List[str]
genres: List[str]
related_info: List[RelatedInfo]
next_episode_date: Optional[datetime] = None
episodes: List[Optional[EpisodeInfo]]
```

### DownloadLinkInfo

```python
server: str
url: Optional[str] = None
```

### EpisodeDownloadInfo

```python
episode_number: int
download_links: List[DownloadLinkInfo]
```

### Enums

```python
class _AnimeType(Enum):
    TV = "TV"
    MOVIE = "Movie"
    OVA = "OVA"
    SPECIAL = "Special"

class _RelatedType(Enum):
    PREQUEL = "Prequel"
    SEQUEL = "Sequel"
    PARALLEL_HISTORY = "Parallel History"
    MAIN_HISTORY = "Main History"
```

## AnimeFLVScraper Methods

### search_anime

```python
async def search_anime(query: str, page: int = 1) -> PagedSearchAnimeInfo
# Synchronous equivalent:
def search_anime(query: str, page: int = 1) -> PagedSearchAnimeInfo
```

Searches for anime on AnimeFLV.

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
# Synchronous equivalent:
def get_anime_info(anime_id: str, include_episodes: bool = True) -> AnimeInfo
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
async def get_new_episodes(anime_id: str, last_episode_number: int, tab_timeout: int = 200, browser: Optional[AsyncBrowser] = None) -> List[EpisodeInfo]
# Synchronous equivalent:
def get_new_episodes(anime_id: str, last_episode_number: int, tab_timeout: int = 200, browser: Optional[SyncBrowser] = None) -> List[EpisodeInfo]
```

Fetches newly released episodes for an anime starting from the last known episode.

**Parameters:**

- `anime_id`: Anime identifier.
- `last_episode_number`: Last known episode number (≥0).
- `tab_timeout`: Maximum page/tab loading timeout in milliseconds (default: 200).
- `browser`: Optional browser instance (`AsyncBrowser` for async, `SyncBrowser` for sync).

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
# Synchronous equivalent:
def get_table_download_links(anime_id: str, episode_number: int) -> EpisodeDownloadInfo
```

Gets direct download links from table servers.

**Parameters:**

- `anime_id`: Anime identifier
- `episode_number`: Episode number (≥0)

**Raises:**

- `ValueError` for invalid episode_number
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

### get_iframe_download_links

```python
async def get_iframe_download_links(anime_id: str, episode_number: int, browser: Optional[AsyncBrowser] = None) -> EpisodeDownloadInfo
# Synchronous equivalent:
def get_iframe_download_links(anime_id: str, episode_number: int, browser: Optional[SyncBrowser] = None) -> EpisodeDownloadInfo
```

Gets download links from iframe-embedded content (requires browser).

**Parameters:**

- `anime_id`: Anime identifier
- `episode_number`: Episode number (≥0)
- `browser`: Optional browser instance (AsyncBrowser for async, SyncBrowser for sync)

**Raises:**

- `ValueError` for invalid episode_number
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

### get_file_download_link

```python
async def get_file_download_link(download_info: DownloadLinkInfo, browser: Optional[AsyncBrowser] = None) -> Optional[str]
# Synchronous equivalent:
def get_file_download_link(download_info: DownloadLinkInfo, browser: Optional[SyncBrowser] = None) -> Optional[str]
```

Resolves final download URLs from intermediate links.

**Parameters:**

- `download_info`: Download information object
- `browser`: Optional browser instance (AsyncBrowser for async, SyncBrowser for sync)

**Raises:**

- `TypeError` for invalid download_info
- `ScraperTimeoutError` on timeout

## JKAnimeScraper Methods

### search_anime

```python
async def search_anime(query: str) -> PagedSearchAnimeInfo
# Synchronous equivalent:
def search_anime(query: str) -> PagedSearchAnimeInfo
```

Searches for anime on JKAnime.

**Parameters:**

- `query`: Search term (min 3 characters)

**Raises:**

- `ValueError` for invalid query
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

### get_anime_info

```python
async def get_anime_info(anime_id: str, include_episodes: bool = True, browser: Optional[AsyncBrowser] = None) -> AnimeInfo
# Synchronous equivalent:
def get_anime_info(anime_id: str, include_episodes: bool = True, browser: Optional[SyncBrowser] = None) -> AnimeInfo
```

Gets detailed anime information (requires browser for JKAnime).

**Parameters:**

- `anime_id`: Anime identifier
- `include_episodes`: Include episodes in the returned `AnimeInfo` object (default: True)
- `browser`: Optional browser instance (AsyncBrowser for async, SyncBrowser for sync)

**Raises:**

- `TypeError` for invalid anime_id
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

### get_new_episodes

```python
async def get_new_episodes(anime_id: str, last_episode_number: int, tab_timeout: int = 200, browser: Optional[AsyncBrowser] = None) -> List[EpisodeInfo]
# Synchronous equivalent:
def get_new_episodes(anime_id: str, last_episode_number: int, tab_timeout: int = 200, browser: Optional[SyncBrowser] = None) -> List[EpisodeInfo]
```

Fetches newly released episodes for an anime starting from the last known episode.

**Parameters:**

- `anime_id`: Anime identifier.
- `last_episode_number`: Last known episode number (≥0).
- `tab_timeout`: Maximum page/tab loading timeout in milliseconds (default: 200).
- `browser`: Optional browser instance (`AsyncBrowser` for async, `SyncBrowser` for sync).

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
async def get_table_download_links(anime_id: str, episode_number: int, browser: Optional[AsyncBrowser] = None) -> EpisodeDownloadInfo
# Synchronous equivalent:
def get_table_download_links(anime_id: str, episode_number: int, browser: Optional[SyncBrowser] = None) -> EpisodeDownloadInfo
```

Gets direct download links from table servers.

**Parameters:**

- `anime_id`: Anime identifier
- `episode_number`: Episode number (≥0)
- `browser`: Optional browser instance (AsyncBrowser for async, SyncBrowser for sync)

**Raises:**

- `ValueError` for invalid episode_number
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

### get_iframe_download_links

```python
async def get_iframe_download_links(anime_id: str, episode_number: int, browser: Optional[AsyncBrowser] = None) -> EpisodeDownloadInfo
# Synchronous equivalent:
def get_iframe_download_links(anime_id: str, episode_number: int, browser: Optional[SyncBrowser] = None) -> EpisodeDownloadInfo
```

_Not supported yet for JKAnime_

### get_file_download_link

```python
async def get_file_download_link(download_info: DownloadLinkInfo, browser: Optional[AsyncBrowser] = None) -> str
# Synchronous equivalent:
def get_file_download_link(download_info: DownloadLinkInfo, browser: Optional[SyncBrowser] = None) -> str
```

Resolves final download URLs from intermediate links.

**Parameters:**

- `download_info`: Download information object
- `browser`: Optional browser instance (AsyncBrowser for async, SyncBrowser for sync)

**Raises:**

- `TypeError` for invalid download_info
- `ValueError` for unsupported servers
- `ScraperTimeoutError` on timeout

## Browser Classes

### AsyncBrowser

Asynchronous browser context manager.

**Parameters:**

- `headless`: Run in headless mode (default: True)
- `executable_path`: Custom browser path
- `args`: Additional browser arguments

**Methods:**

- `new_page()`: Creates a new browser page

### SyncBrowser

Synchronous browser context manager.

**Parameters:**

- `headless`: Run in headless mode (default: True)
- `executable_path`: Custom browser path
- `args`: Additional browser arguments

**Methods:**

- `new_page()`: Creates a new browser page

## Exceptions

### ScraperBlockedError

Raised when the scraper is blocked by the server (HTTP 403).

### ScraperTimeoutError

Raised when a request times out or server returns HTTP 500.

### ScraperParseError

Raised when HTML content cannot be parsed correctly.

### ValueError

Raised for invalid parameters (query length, page numbers, episode IDs).

### TypeError

Raised for incorrect parameter types.

## Supported Servers

### AnimeFLV Supported Servers

- **SW** (Streamwish)
- **YourUpload**

### JKAnime Supported Servers

- **Streamwish**
- **Mediafire**
