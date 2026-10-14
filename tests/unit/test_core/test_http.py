from __future__ import annotations

import asyncio

import aiohttp
import pytest
from aioresponses import aioresponses

from ani_scrapy.core.exceptions import (
    ScraperBlockedError,
    ScraperHTTPError,
    ScraperNotFoundError,
    ScraperTimeoutError,
)
from ani_scrapy.core.http import AsyncHttpAdapter

BASE_URL = "https://example.test"
URL = f"{BASE_URL}/media/slug"


def _get(adapter: AsyncHttpAdapter) -> str:
    async def run() -> str:
        try:
            return await adapter.get("media/slug")
        finally:
            await adapter.close()

    return asyncio.run(run())


@pytest.fixture
def adapter() -> AsyncHttpAdapter:
    return AsyncHttpAdapter(base_url=BASE_URL)


def test_success_returns_text(adapter: AsyncHttpAdapter) -> None:
    with aioresponses() as mocked:
        mocked.get(URL, status=200, body="ok")
        assert _get(adapter) == "ok"


@pytest.mark.parametrize("status", [404, 410])
def test_not_found(adapter: AsyncHttpAdapter, status: int) -> None:
    with aioresponses() as mocked:
        mocked.get(URL, status=status)
        with pytest.raises(ScraperNotFoundError) as info:
            _get(adapter)
    assert info.value.status_code == status


@pytest.mark.parametrize("status", [403, 429])
def test_blocked(adapter: AsyncHttpAdapter, status: int) -> None:
    with aioresponses() as mocked:
        mocked.get(URL, status=status)
        with pytest.raises(ScraperBlockedError) as info:
            _get(adapter)
    assert info.value.status_code == status


@pytest.mark.parametrize("status", [400, 500, 503])
def test_other_error_status_is_http_error(
    adapter: AsyncHttpAdapter, status: int
) -> None:
    with aioresponses() as mocked:
        mocked.get(URL, status=status)
        with pytest.raises(ScraperHTTPError) as info:
            _get(adapter)
    assert info.value.status_code == status
    assert not isinstance(info.value, ScraperTimeoutError)


def test_connection_error_is_http_error_without_status(
    adapter: AsyncHttpAdapter,
) -> None:
    with aioresponses() as mocked:
        mocked.get(URL, exception=aiohttp.ClientConnectionError("down"))
        with pytest.raises(ScraperHTTPError) as info:
            _get(adapter)
    assert info.value.status_code is None
    assert isinstance(info.value.__cause__, aiohttp.ClientConnectionError)


def test_timeout_is_timeout_error(adapter: AsyncHttpAdapter) -> None:
    with aioresponses() as mocked:
        mocked.get(URL, exception=asyncio.TimeoutError())
        with pytest.raises(ScraperTimeoutError):
            _get(adapter)
