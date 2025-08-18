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
- `get_anime_info(anime_id: str, **kwargs) -> AnimeInfo`
- `get_table_download_links(anime_id: str, episode_id: int, **kwargs) -> EpisodeDownloadInfo`
- `get_iframe_download_links(anime_id: str, episode_id: int, browser: Optional[AsyncBrowser] = None) -> EpisodeDownloadInfo`
- `get_file_download_link(download_info: DownloadLinkInfo, browser: Optional[AsyncBrowser] = None) -> str`

### SyncBaseScraper
Abstract base class for sync anime scrapers.

**Methods:**
- `init(verbose: bool = False, level: str = "INFO") -> None`
- `search_anime(query: str, **kwargs) -> PagedSearchAnimeInfo`
- `get_anime_info(anime_id: str, **kwargs) -> AnimeInfo`
- `get_table_download_links(anime_id: str, episode_id: int, **kwargs) -> EpisodeDownloadInfo`
- `get_iframe_download_links(anime_id: str, episode_id: int, browser: Optional[SyncBrowser] = None) -> EpisodeDownloadInfo`
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
image_preview: Optional[str]
```

### AnimeInfo
Extends `BaseAnimeInfo` with:
```python
synopsis: str
is_finished: bool
rating: Optional[str]
other_titles: List[str]
genres: List[str]
related_info: List[RelatedInfo]
next_episode_date: Optional[datetime]
episodes: List[EpisodeInfo]
```

### DownloadLinkInfo
```python
server: str
url: Optional[str]
```

### EpisodeDownloadInfo
```python
episode_id: int
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
async def get_anime_info(anime_id: str) -> AnimeInfo
# Synchronous equivalent:
def get_anime_info(anime_id: str) -> AnimeInfo
```
Gets detailed anime information.

**Parameters:**
- `anime_id`: Anime identifier

**Raises:**
- `TypeError` for invalid anime_id
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

### get_table_download_links
```python
async def get_table_download_links(anime_id: str, episode_id: int) -> EpisodeDownloadInfo
# Synchronous equivalent:
def get_table_download_links(anime_id: str, episode_id: int) -> EpisodeDownloadInfo
```
Gets direct download links from table servers.

**Parameters:**
- `anime_id`: Anime identifier
- `episode_id`: Episode number (≥0)

**Raises:**
- `ValueError` for invalid episode_id
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

### get_iframe_download_links
```python
async def get_iframe_download_links(anime_id: str, episode_id: int, browser: Optional[AsyncBrowser] = None) -> EpisodeDownloadInfo
# Synchronous equivalent:
def get_iframe_download_links(anime_id: str, episode_id: int, browser: Optional[SyncBrowser] = None) -> EpisodeDownloadInfo
```
Gets download links from iframe-embedded content (requires browser).

**Parameters:**
- `anime_id`: Anime identifier
- `episode_id`: Episode number (≥0)
- `browser`: Optional browser instance (AsyncBrowser for async, SyncBrowser for sync)

**Raises:**
- `ValueError` for invalid episode_id
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
async def get_anime_info(anime_id: str, browser: Optional[AsyncBrowser] = None) -> AnimeInfo
# Synchronous equivalent:
def get_anime_info(anime_id: str, browser: Optional[SyncBrowser] = None) -> AnimeInfo
```
Gets detailed anime information (requires browser for JKAnime).

**Parameters:**
- `anime_id`: Anime identifier
- `browser`: Optional browser instance (AsyncBrowser for async, SyncBrowser for sync)

**Raises:**
- `TypeError` for invalid anime_id
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

### get_table_download_links
```python
async def get_table_download_links(anime_id: str, episode_id: int, browser: Optional[AsyncBrowser] = None) -> EpisodeDownloadInfo
# Synchronous equivalent:
def get_table_download_links(anime_id: str, episode_id: int, browser: Optional[SyncBrowser] = None) -> EpisodeDownloadInfo
```
Gets direct download links from table servers.

**Parameters:**
- `anime_id`: Anime identifier
- `episode_id`: Episode number (≥0)
- `browser`: Optional browser instance (AsyncBrowser for async, SyncBrowser for sync)

**Raises:**
- `ValueError` for invalid episode_id
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

### get_iframe_download_links
```python
async def get_iframe_download_links(anime_id: str, episode_id: int, browser: Optional[AsyncBrowser] = None) -> EpisodeDownloadInfo
# Synchronous equivalent:
def get_iframe_download_links(anime_id: str, episode_id: int, browser: Optional[SyncBrowser] = None) -> EpisodeDownloadInfo
```
*Not supported yet for JKAnime*

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