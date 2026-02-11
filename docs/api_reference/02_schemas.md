# Schemas

All scrapers return dataclasses from `ani_scrapy.core.schemas`.

## Key types

- `SearchAnimeInfo`
- `PagedSearchAnimeInfo`
- `AnimeInfo`
- `EpisodeInfo`
- `DownloadLinkInfo`
- `EpisodeDownloadInfo`

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
number: int
anime_id: str
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

## Enums

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
