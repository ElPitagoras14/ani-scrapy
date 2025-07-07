from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class _AnimeType(Enum):
    TV = "TV"
    MOVIE = "Movie"
    OVA = "OVA"
    SPECIAL = "Special"


class _AnimeFormat(Enum):
    DUB = "Dub"
    SUB = "Sub"


class _RelatedType(Enum):
    PREQUEL = "Prequel"
    SEQUEL = "Sequel"
    PARALLEL_HISTORY = "Parallel History"
    MAIN_HISTORY = "Main History"


@dataclass
class SearchAnimeInfo:
    id: str
    title: str
    type: _AnimeType
    poster: str


@dataclass
class PagedSearchAnimeInfo:
    page: int
    total_pages: int
    animes: List[SearchAnimeInfo]


@dataclass
class RelatedInfo:
    id: str
    title: str
    type: str


@dataclass
class EpisodeInfo:
    id: str
    anime: str
    image_preview: Optional[str] = None


@dataclass
class AnimeInfo:
    id: str
    title: str
    poster: str
    synopsis: str
    rating: str
    is_finished: bool
    type: _AnimeType
    other_titles: Optional[List[str]] = field(default_factory=list)
    genres: Optional[List[str]] = field(default_factory=list)
    related_info: Optional[List[RelatedInfo]] = field(default_factory=list)
    next_episode_date: Optional[datetime] = None
    episodes: List[EpisodeInfo] = field(default_factory=list)


@dataclass
class DownloadLinkInfo:
    server: str
    format: _AnimeFormat
    url: Optional[str] = None


@dataclass
class BulkDownloadLinkInfo:
    episode_id: int
    download_links: List[DownloadLinkInfo]
