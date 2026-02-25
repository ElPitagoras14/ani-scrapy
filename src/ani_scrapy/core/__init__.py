"""Core package."""

from ani_scrapy.core.base import BaseScraper
from ani_scrapy.core.browser import AsyncBrowser
from ani_scrapy.core.http import AsyncHttpAdapter
from ani_scrapy.core.exceptions import (
    ScraperError,
    ScraperBlockedError,
    ScraperTimeoutError,
    ScraperParseError,
)
from ani_scrapy.core.schemas import (
    AnimeInfo,
    EpisodeInfo,
    SearchAnimeInfo,
    EpisodeDownloadInfo,
    DownloadLinkInfo,
    PagedSearchAnimeInfo,
    RelatedInfo,
    _AnimeType,
    _RelatedType,
)

__all__ = [
    "BaseScraper",
    "AsyncBrowser",
    "AsyncHttpAdapter",
    "ScraperError",
    "ScraperBlockedError",
    "ScraperTimeoutError",
    "ScraperParseError",
    "AnimeInfo",
    "EpisodeInfo",
    "SearchAnimeInfo",
    "EpisodeDownloadInfo",
    "DownloadLinkInfo",
    "PagedSearchAnimeInfo",
    "RelatedInfo",
    "_AnimeType",
    "_RelatedType",
]
