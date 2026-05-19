"""HTTP adapter using aiohttp."""

import asyncio
import time

import aiohttp

from ani_scrapy.core.constants.general import CONTEXT_OPTIONS
from ani_scrapy.core.exceptions import ScraperBlockedError, ScraperTimeoutError
from ani_scrapy.core.log import logger


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

    async def _request(self, method: str, endpoint: str, **kwargs) -> str:
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
                if response.status in (403, 429):
                    raise ScraperBlockedError(
                        f"Blocked by site (HTTP {response.status}): {url}"
                    )
                response.raise_for_status()
                duration_ms = (time.perf_counter() - start) * 1000
                logger.debug(
                    "HTTP {method} response | url={url} status_code={status_code} duration_ms={duration_ms}",
                    method=method,
                    url=url,
                    status_code=response.status,
                    duration_ms=round(duration_ms, 2),
                )
                return await response.text()
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
            raise ScraperTimeoutError(f"HTTP request failed: {e}") from e

    async def get(self, endpoint: str, params: dict | None = None) -> str:
        """Async GET request."""
        return await self._request("GET", endpoint, params=params)

    async def post(self, endpoint: str, data: dict | None = None) -> str:
        """Async POST request."""
        return await self._request("POST", endpoint, data=data)

    async def close(self) -> None:
        """Close aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
