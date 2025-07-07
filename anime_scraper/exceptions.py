class ScraperError(Exception):
    """Base exception for all scraping-related errors."""


class ScraperTimeoutError(ScraperError):
    """Failed to fetch due to a timeout."""


class ScraperParseError(ScraperError):
    """Invalid HTML or unexpected structure."""


class ScraperBlockedError(ScraperError):
    """The site blocked the IP (bot detection)."""
