"""HTTP adapter using aiohttp."""

import aiohttp
import time
from typing import Dict, Optional
from ani_scrapy.core.base import create_scraper_logger
from ani_scrapy.core.constants.general import CONTEXT_OPTIONS


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
                "Accept-Language": CONTEXT_OPTIONS["extra_http_headers"]["accept-language"],
            }
            self._session = aiohttp.ClientSession(
                timeout=timeout, headers=headers
            )
        return self._session

    async def get(
        self, endpoint: str, params: Optional[Dict] = None, task_id: str = ""
    ) -> str:
        """Async GET request."""
        log = create_scraper_logger(task_id)

        session = await self._get_session()
        url = self.build_url(endpoint)
        log.debug(
            "HTTP GET request | url={url} params={params}",
            url=url,
            params=params,
        )

        start = time.perf_counter()
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                duration_ms = (time.perf_counter() - start) * 1000
                log.debug(
                    "HTTP GET response | url={url} status_code={status_code} duration_ms={duration_ms}",
                    url=url,
                    status_code=response.status,
                    duration_ms=round(duration_ms, 2),
                )
                return await response.text()
        except aiohttp.ClientError as e:
            log.error(
                "HTTP GET failed | url={url} error={error}",
                url=url,
                error=str(e),
            )
            raise ConnectionError(f"HTTP request failed: {e}")

    async def post(
        self, endpoint: str, data: Optional[Dict] = None, task_id: str = ""
    ) -> str:
        """Async POST request."""
        log = create_scraper_logger(task_id)

        session = await self._get_session()
        url = self.build_url(endpoint)

        log.debug(
            "HTTP POST request | url={url} data={data}", url=url, data=data
        )

        start = time.perf_counter()
        try:
            async with session.post(url, data=data) as response:
                response.raise_for_status()
                duration_ms = (time.perf_counter() - start) * 1000
                log.debug(
                    "HTTP POST response | url={url} status_code={status_code} duration_ms={duration_ms}",
                    url=url,
                    status_code=response.status,
                    duration_ms=round(duration_ms, 2),
                )
                return await response.text()
        except aiohttp.ClientError as e:
            log.error(
                "HTTP POST failed | url={url} error={error}",
                url=url,
                error=str(e),
            )
            raise ConnectionError(f"HTTP request failed: {e}")

    async def close(self) -> None:
        """Close aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
