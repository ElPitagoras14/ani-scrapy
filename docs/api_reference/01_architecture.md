# Architecture

## Goals

- Async-first design with no code duplication.
- Keep scraping coordination small and focused.
- Centralize parsing logic in reusable parsers.

## Modules

- `ani_scrapy.core.http`: HTTP adapters + mocks.
- `ani_scrapy.<site>.parser`: site parsers (e.g. `AnimeFLVParser`, `JKAnimeParser`).
- `ani_scrapy.<site>`: scrapers that coordinate I/O + browser usage.

## Data flow

```
Scraper -> HTTP Adapter -> HTML -> Parser -> Schemas
             |-> Browser (automatic)
```

## Core Classes

### BaseScraper

Abstract base class for anime scrapers.

**Constructor:**
- `__init__(log_file: str | None = None, level: str = "INFO", headless: bool = True, executable_path: str = "") -> None`

**Methods:**

- `search_anime(query: str, page: int = 1, task_id: str | None = None) -> PagedSearchAnimeInfo`
- `get_anime_info(anime_id: str, include_episodes: bool = True, task_id: str | None = None) -> AnimeInfo`
- `get_new_episodes(anime_id: str, last_episode_number: int, task_id: str | None = None) -> list[EpisodeInfo]`
- `get_table_download_links(anime_id: str, episode_number: int, task_id: str | None = None) -> EpisodeDownloadInfo`
- `get_iframe_download_links(anime_id: str, episode_number: int, task_id: str | None = None) -> EpisodeDownloadInfo`
- `get_file_download_link(download_info: DownloadLinkInfo, task_id: str | None = None) -> str | None`

### Task ID

All scraper methods accept an optional `task_id` parameter for log correlation.

**Characteristics:**
- **Optional**: If not provided, a random 12-character ID is automatically generated
- **Customizable**: You can pass any string identifier (e.g., your job ID, user ID, or meaningful name)
- **Use Case**: Correlate logs across multiple operations or scrapers

**Example:**
```python
# Auto-generated task_id (default behavior)
results = await scraper.search_anime(query="naruto")  # task_id="Ab3xK9mNp2Qr"

# Custom task_id (recommended for production)
results = await scraper.search_anime(query="naruto", task_id="batch-job-12345")
```

## Import Paths

```python
from ani_scrapy import AnimeFLVScraper, JKAnimeScraper, AsyncBrowser
```
