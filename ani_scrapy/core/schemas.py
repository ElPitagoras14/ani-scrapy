from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
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
    animes: List[SearchAnimeInfo]


@dataclass
class RelatedInfo:
    id: str
    title: str
    type: _RelatedType


@dataclass
class EpisodeInfo:
    number: int
    anime_id: str
    image_preview: Optional[str] = None


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


@dataclass
class DownloadLinkInfo:
    server: str
    url: Optional[str] = None


@dataclass
class EpisodeDownloadInfo:
    episode_number: int
    download_links: List[DownloadLinkInfo]
