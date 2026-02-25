"""Examples package for ani-scrapy library.

This package contains executable examples demonstrating various use cases
of the ani-scrapy library for scraping anime websites.

Usage:
    python examples/01_basic_search.py
    python examples/02_anime_info.py
    ...

All examples use AnimeFLV and JKAnime scrapers with proper logging
configuration.
"""

from ani_scrapy import AnimeFLVScraper, JKAnimeScraper, AsyncBrowser

__all__ = [
    "AnimeFLVScraper",
    "JKAnimeScraper",
    "AsyncBrowser",
]
