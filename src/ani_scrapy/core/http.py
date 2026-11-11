"""HTTP adapter using aiohttp."""

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

import aiohttp

from ani_scrapy.core.constants.general import CONTEXT_OPTIONS
from ani_scrapy.core.exceptions import (
    ScraperBlockedError,
    ScraperHTTPError,
    ScraperNotFoundError,
    ScraperTimeoutError,
)
from ani_scrapy.core.log import logger

NOT_FOUND_STATUSES = (404, 410)
BLOCKED_STATUSES = (403, 429)

T = TypeVar("T")


def raise_for_status_code(status: int, url: str) -> None:
    """Raise the matching scraper exception for an error HTTP status.

    Args:
        status: HTTP status code.
        url: Requested URL, used in the error message.
    """
    if status < 400:
        return
    if status in NOT_FOUND_STATUSES:
        raise ScraperNotFoundError(
            f"Not found (HTTP {status}): {url}", status_code=status
        )
    if status in BLOCKED_STATUSES:
        raise ScraperBlockedError(
            f"Blocked by site (HTTP {status}): {url}", status_code=status
        )
    raise ScraperHTTPError(f"HTTP error {status}: {url}", status_code=status)


class BaseHttpAdapter:
    """Base HTTP adapter."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"


class AsyncHttpAdapter(BaseHttpAdapter):
    """Async HTTP adapter using aiohttp."""

    def __init__(self, base_url: str, timeout: int = 30):
        super().__init__(base_url, timeout)
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazy initialization of aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            headers = {
                "User-Agent": CONTEXT_OPTIONS["user_agent"],
                "Accept": CONTEXT_OPTIONS["extra_http_headers"]["accept"],
                "Accept-Language": CONTEXT_OPTIONS["extra_http_headers"][
                    "accept-language"
                ],
            }
            self._session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return self._session

    async def _request(
        self,
        method: str,
        endpoint: str,
        read: Callable[[aiohttp.ClientResponse], Awaitable[T]],
        **kwargs,
    ) -> T:
        session = await self._get_session()
        url = self.build_url(endpoint)
        logger.debug(
            "HTTP {method} request | url={url} kwargs={kwargs}",
            method=method,
            url=url,
            kwargs=kwargs,
        )

        start = time.perf_counter()
        try:
            async with session.request(method, url, **kwargs) as response:
                raise_for_status_code(response.status, url)
                duration_ms = (time.perf_counter() - start) * 1000
                logger.debug(
                    "HTTP {method} response | url={url} status_code={status_code} duration_ms={duration_ms}",
                    method=method,
                    url=url,
                    status_code=response.status,
                    duration_ms=round(duration_ms, 2),
                )
                return await read(response)
        except asyncio.TimeoutError as e:
            logger.error("HTTP {method} timeout | url={url}", method=method, url=url)
            raise ScraperTimeoutError(f"HTTP request timed out: {url}") from e
        except aiohttp.ClientError as e:
            logger.error(
                "HTTP {method} failed | url={url} error={error}",
                method=method,
                url=url,
                error=str(e),
            )
            raise ScraperHTTPError(
                f"HTTP request failed: {e}",
                status_code=getattr(e, "status", None),
            ) from e

    async def get(self, endpoint: str, params: dict | None = None) -> str:
        """Async GET request."""
        return await self._request("GET", endpoint, lambda r: r.text(), params=params)

    async def post(self, endpoint: str, data: dict | None = None) -> str:
        """Async POST request."""
        return await self._request("POST", endpoint, lambda r: r.text(), data=data)

    async def post_redirect_location(
        self, endpoint: str, data: dict | None = None
    ) -> str | None:
        """Async POST that does not follow redirects.

        Args:
            endpoint: Endpoint relative to the base URL.
            data: Form fields to send.

        Returns:
            The Location header of the redirect response, or None if the
            response is not a redirect.
        """

        async def location(response: aiohttp.ClientResponse) -> str | None:
            if 300 <= response.status < 400:
                return response.headers.get("Location")
            return None

        return await self._request(
            "POST", endpoint, location, data=data, allow_redirects=False
        )

    async def close(self) -> None:
        """Close aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
