# Scrapers

## AnimeFLVScraper

### Imports

```python
from ani_scrapy import AnimeFLVScraper
```

### Methods

#### search_anime

```python
async def search_anime(query: str, page: int = 1, task_id: str | None = None) -> PagedSearchAnimeInfo
```

Searches for anime on AnimeFLV.

**Parameters:**

- `query`: Search term (min 3 characters)
- `page`: Page number (default: 1)
- `task_id`: Optional identifier for log correlation. If not provided, a random ID is generated.

**Raises:**

- `ValueError` for invalid parameters
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

#### get_anime_info

```python
async def get_anime_info(anime_id: str, include_episodes: bool = True, task_id: str | None = None) -> AnimeInfo
```

Gets detailed anime information.

**Parameters:**

- `anime_id`: Anime identifier
- `include_episodes`: Include episodes in the returned `AnimeInfo` object (default: True)
- `task_id`: Optional identifier for log correlation. If not provided, a random ID is generated.

**Raises:**

- `TypeError` for invalid anime_id
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

#### get_new_episodes

```python
async def get_new_episodes(anime_id: str, last_episode_number: int, task_id: str | None = None) -> list[EpisodeInfo]
```

Fetches newly released episodes for an anime starting from the last known episode.

**Parameters:**

- `anime_id`: Anime identifier.
- `last_episode_number`: Last known episode number (≥0).
- `task_id`: Optional identifier for log correlation. If not provided, a random ID is generated.

**Returns:**

- A list of `EpisodeInfo` objects representing the new episodes found.

**Raises:**

- `ValueError` if `last_episode_number` is invalid.
- `TypeError` if `anime_id` is invalid.
- `ScraperBlockedError` if the request is blocked.
- `ScraperTimeoutError` on timeout.
- `ScraperParseError` if parsing the response fails.

#### get_table_download_links

```python
async def get_table_download_links(anime_id: str, episode_number: int, task_id: str | None = None) -> EpisodeDownloadInfo
```

Gets direct download links from table servers.

**Parameters:**

- `anime_id`: Anime identifier
- `episode_number`: Episode number (≥0)
- `task_id`: Optional identifier for log correlation. If not provided, a random ID is generated.

**Raises:**

- `ValueError` for invalid episode_number
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

#### get_iframe_download_links

```python
async def get_iframe_download_links(anime_id: str, episode_number: int, task_id: str | None = None) -> EpisodeDownloadInfo
```

Gets download links from iframe-embedded content (requires browser).

**Parameters:**

- `anime_id`: Anime identifier
- `episode_number`: Episode number (≥0)
- `task_id`: Optional identifier for log correlation. If not provided, a random ID is generated.

**Raises:**

- `ValueError` for invalid episode_number
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

#### get_file_download_link

```python
async def get_file_download_link(download_info: DownloadLinkInfo, task_id: str | None = None) -> str | None
```

Resolves final download URLs from intermediate links.

**Parameters:**

- `download_info`: Download information object
- `task_id`: Optional identifier for log correlation. If not provided, a random ID is generated.

**Raises:**

- `TypeError` for invalid download_info
- `ScraperTimeoutError` on timeout

---

## JKAnimeScraper

### Imports

```python
from ani_scrapy import JKAnimeScraper
```

### Methods

#### search_anime

```python
async def search_anime(query: str, page: int = 1, task_id: str | None = None) -> PagedSearchAnimeInfo
```

Searches for anime on JKAnime.

**Parameters:**

- `query`: Search term (min 3 characters)
- `page`: Page number (default: 1)
- `task_id`: Optional identifier for log correlation. If not provided, a random ID is generated.

**Raises:**

- `ValueError` for invalid query
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

#### get_anime_info

```python
async def get_anime_info(anime_id: str, include_episodes: bool = True, task_id: str | None = None) -> AnimeInfo
```

Gets detailed anime information (requires browser for JKAnime).

**Parameters:**

- `anime_id`: Anime identifier
- `include_episodes`: Include episodes in the returned `AnimeInfo` object (default: True)
- `task_id`: Optional identifier for log correlation. If not provided, a random ID is generated.

**Raises:**

- `TypeError` for invalid anime_id
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

#### get_new_episodes

```python
async def get_new_episodes(anime_id: str, last_episode_number: int, task_id: str | None = None) -> list[EpisodeInfo]
```

Fetches newly released episodes for an anime starting from the last known episode.

**Parameters:**

- `anime_id`: Anime identifier.
- `last_episode_number`: Last known episode number (≥0).
- `task_id`: Optional identifier for log correlation. If not provided, a random ID is generated.

**Returns:**

- A list of `EpisodeInfo` objects representing the new episodes found.

**Raises:**

- `ValueError` if `last_episode_number` is invalid.
- `TypeError` if `anime_id` is invalid.
- `ScraperBlockedError` if the request is blocked.
- `ScraperTimeoutError` on timeout.
- `ScraperParseError` if parsing the response fails.

#### get_table_download_links

```python
async def get_table_download_links(anime_id: str, episode_number: int, task_id: str | None = None) -> EpisodeDownloadInfo
```

Gets direct download links from table servers.

**Parameters:**

- `anime_id`: Anime identifier
- `episode_number`: Episode number (≥0)
- `task_id`: Optional identifier for log correlation. If not provided, a random ID is generated.

**Raises:**

- `ValueError` for invalid episode_number
- `ScraperBlockedError` if request is blocked
- `ScraperTimeoutError` on timeout
- `ScraperParseError` on parsing errors

#### get_iframe_download_links

```python
async def get_iframe_download_links(anime_id: str, episode_number: int, task_id: str | None = None) -> EpisodeDownloadInfo
```

_Not supported yet for JKAnime_

---

#### get_file_download_link

```python
async def get_file_download_link(download_info: DownloadLinkInfo, task_id: str | None = None) -> str | None
```

Resolves final download URLs from intermediate links.

**Parameters:**

- `download_info`: Download information object
- `task_id`: Optional identifier for log correlation. If not provided, a random ID is generated.

**Raises:**

- `TypeError` for invalid download_info
- `ValueError` for unsupported servers
- `ScraperTimeoutError` on timeout

---

## Supported Servers

| Servicio | AnimeFLV | JKAnime |
|----------|----------|---------|
| Streamwish (SW) | ✓ | ✓ |
| YourUpload | ✓ | ✗ |
| Mediafire | ✗ | ✓ |

> **Nota:** Ver [Architecture](../01_architecture.md#task-id) para detalles sobre `task_id`.
