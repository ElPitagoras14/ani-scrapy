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

- `__init__(headless: bool = True, executable_path: str = "") -> None`

**Methods:**

- `search_anime(query: str, page: int = 1) -> PagedSearchAnimeInfo`
- `get_anime_info(anime_id: str, include_episodes: bool = True) -> AnimeInfo`
- `get_new_episodes(anime_id: str, last_episode_number: int) -> list[EpisodeInfo]`
- `get_table_download_links(anime_id: str, episode_number: int) -> EpisodeDownloadInfo`
- `get_iframe_download_links(anime_id: str, episode_number: int) -> EpisodeDownloadInfo`
- `get_file_download_link(download_info: DownloadLinkInfo) -> str | None`

## Import Paths

```python
from ani_scrapy import AnimeFLVScraper, JKAnimeScraper, AsyncBrowser
```
