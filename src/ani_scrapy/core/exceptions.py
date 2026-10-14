class ScraperError(Exception):
    """Base exception for all scraping-related errors.

    Args:
        message: Human-readable description.
        status_code: HTTP status code when the error comes from a response.
    """

    def __init__(self, message: str = "", *, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class ScraperNotFoundError(ScraperError):
    """The requested resource does not exist (HTTP 404/410)."""


class ScraperHTTPError(ScraperError):
    """HTTP error response (5xx, other 4xx) or connection failure."""


class ScraperTimeoutError(ScraperError):
    """Failed to fetch due to a timeout."""


class ScraperParseError(ScraperError):
    """Invalid HTML or unexpected structure."""


class ScraperBlockedError(ScraperError):
    """The site blocked the IP (bot detection)."""
