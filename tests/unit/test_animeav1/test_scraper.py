from __future__ import annotations

import asyncio
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from ani_scrapy.core.exceptions import ScraperHTTPError, ScraperParseError
from ani_scrapy.providers.animeav1 import scraper as scraper_module
from ani_scrapy.providers.animeav1.scraper import AnimeAV1Scraper

NO_MEDIA_HTML = "<html><body><h1>Error</h1></body></html>"
SCHEDULE = {"some-anime": datetime(2026, 10, 20)}


def _patch_clock(monkeypatch: pytest.MonkeyPatch, clock) -> None:
    monkeypatch.setattr(
        scraper_module, "time", SimpleNamespace(monotonic=lambda: next(clock))
    )


def _make_scraper(ttl: float | None = None) -> AnimeAV1Scraper:
    scraper = AnimeAV1Scraper(schedule_cache_ttl=ttl)
    scraper.http.get = AsyncMock(return_value="<html></html>")
    scraper.parser.parse_schedule = lambda html: SCHEDULE
    return scraper


def test_get_anime_info_propagates_parse_error() -> None:
    scraper = _make_scraper()
    scraper.http.get = AsyncMock(return_value=NO_MEDIA_HTML)

    with pytest.raises(ScraperParseError) as info:
        asyncio.run(scraper.get_anime_info("missing-anime"))

    assert "missing-anime" in str(info.value)


def test_get_new_episodes_propagates_parse_error() -> None:
    scraper = _make_scraper()
    scraper.http.get = AsyncMock(return_value=NO_MEDIA_HTML)

    with pytest.raises(ScraperParseError):
        asyncio.run(scraper.get_new_episodes("missing-anime", 0))


def test_schedule_cache_never_expires_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scraper = _make_scraper()
    clock = iter([0.0, 10_000_000.0, 20_000_000.0])
    _patch_clock(monkeypatch, clock)

    async def run() -> None:
        await scraper._get_schedule()
        await scraper._get_schedule()

    asyncio.run(run())

    assert scraper.http.get.await_count == 1


def test_schedule_cache_is_reused_before_ttl(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scraper = _make_scraper(ttl=60)
    clock = iter([100.0, 130.0])
    _patch_clock(monkeypatch, clock)

    async def run() -> None:
        await scraper._get_schedule()
        await scraper._get_schedule()

    asyncio.run(run())

    assert scraper.http.get.await_count == 1


def test_schedule_cache_is_refetched_after_ttl(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scraper = _make_scraper(ttl=60)
    clock = iter([100.0, 161.0, 161.0])
    _patch_clock(monkeypatch, clock)

    async def run() -> None:
        await scraper._get_schedule()
        await scraper._get_schedule()

    asyncio.run(run())

    assert scraper.http.get.await_count == 2


def test_failed_refresh_returns_empty_schedule(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scraper = _make_scraper(ttl=60)
    clock = iter([100.0, 200.0])
    _patch_clock(monkeypatch, clock)

    async def run() -> dict:
        await scraper._get_schedule()
        scraper.http.get = AsyncMock(side_effect=ScraperHTTPError("down"))
        return await scraper._get_schedule()

    assert asyncio.run(run()) == {}
