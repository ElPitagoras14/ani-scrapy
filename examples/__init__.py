"""Examples package for ani-scrapy library.

This package contains executable examples demonstrating various use cases
of the ani-scrapy library for scraping anime websites.

Usage:
    python examples/01_basic_search.py
    python examples/02_anime_info.py
    ...

All examples use JKAnime and AnimeAV1 scrapers with proper logging
configuration.
"""

from ani_scrapy import AnimeAV1Scraper, JKAnimeScraper, AsyncBrowser

__all__ = [
    "AnimeAV1Scraper",
    "JKAnimeScraper",
    "AsyncBrowser",
]
