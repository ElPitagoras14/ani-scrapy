from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


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


@dataclass
class BaseAnimeInfo:
    id: str
    title: str
    type: _AnimeType
    poster: str


@dataclass
class SearchAnimeInfo(BaseAnimeInfo):
    pass


@dataclass
class PagedSearchAnimeInfo:
    page: int
    total_pages: int
    animes: list[SearchAnimeInfo]


@dataclass
class RelatedInfo:
    id: str
    title: str
    type: _RelatedType


@dataclass
class EpisodeInfo:
    number: int
    anime_id: str
    image_preview: str | None = None


@dataclass
class AnimeInfo(BaseAnimeInfo):
    description: str
    is_finished: bool
    genres: list[str] = field(default_factory=list)
    related_info: list[RelatedInfo] = field(default_factory=list)
    next_episode_date: datetime | None = None
    episodes: list[EpisodeInfo | None] = field(default_factory=list)


@dataclass
class DownloadLinkInfo:
    server: str
    url: str | None = None


@dataclass
class EpisodeDownloadInfo:
    episode_number: int
    download_links: list[DownloadLinkInfo]
