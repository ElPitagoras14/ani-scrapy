from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class AnimeType(Enum):
    TV = "TV"
    MOVIE = "Movie"
    OVA = "OVA"
    SPECIAL = "Special"


class RelatedType(Enum):
    PREQUEL = "Prequel"
    SEQUEL = "Sequel"
    PARALLEL_HISTORY = "Parallel History"
    MAIN_HISTORY = "Main History"


@dataclass
class BaseAnimeInfo:
    id: str
    title: str
    type: AnimeType
    poster: str


@dataclass
class SearchAnimeInfo(BaseAnimeInfo):
    pass


@dataclass
class PagedSearchAnimeInfo:
    """Paginated search results.

    ``total_pages`` is ``1`` when the provider either has a single page of
    results or does not expose pagination (e.g. JKAnime). Only AnimeAV1
    currently parses real pagination from the site.
    """

    page: int
    total_pages: int
    animes: list[SearchAnimeInfo]


@dataclass
class RelatedInfo:
    id: str
    title: str
    type: RelatedType


@dataclass
class EpisodeInfo:
    episode_number: int
    anime_id: str
    image_preview: str | None = None


@dataclass
class AnimeInfo(BaseAnimeInfo):
    description: str
    is_finished: bool
    genres: list[str] = field(default_factory=list)
    related_info: list[RelatedInfo] = field(default_factory=list)
    next_episode_date: datetime | None = None
    episodes: list[EpisodeInfo] = field(default_factory=list)


@dataclass
class DownloadLinkInfo:
    server: str
    url: str | None = None


@dataclass
class EpisodeDownloadInfo:
    episode_number: int
    download_links: list[DownloadLinkInfo]
