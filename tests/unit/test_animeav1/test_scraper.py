from __future__ import annotations

import asyncio
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from ani_scrapy.core.exceptions import (
    ScraperBlockedError,
    ScraperHTTPError,
    ScraperParseError,
)
from ani_scrapy.core.schemas import DownloadLinkInfo
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


MP4UPLOAD_LINK = DownloadLinkInfo(
    server="MP4Upload", url="https://www.mp4upload.com/fevqfos5cs7q"
)
FILE_URL = "https://a4.mp4upload.com:183/d/token/video.mp4"


def _make_mp4upload_scraper(
    location: str | None = FILE_URL,
    error: Exception | None = None,
) -> AnimeAV1Scraper:
    scraper = AnimeAV1Scraper()
    scraper.mp4upload_http.post_redirect_location = AsyncMock(
        return_value=location, side_effect=error
    )
    scraper._get_browser = AsyncMock()
    return scraper


def test_mp4upload_table_link_resolves_to_file_url() -> None:
    scraper = _make_mp4upload_scraper()

    result = asyncio.run(scraper.get_file_download_link(MP4UPLOAD_LINK))

    assert result == FILE_URL
    endpoint, data = scraper.mp4upload_http.post_redirect_location.call_args.args
    assert endpoint == "fevqfos5cs7q"
    assert data["op"] == "download2"
    assert data["id"] == "fevqfos5cs7q"
    assert data["method_free"] == "Free Download"
    scraper._get_browser.assert_not_called()


def test_mp4upload_without_location_returns_none() -> None:
    scraper = _make_mp4upload_scraper(location=None)

    assert asyncio.run(scraper.get_file_download_link(MP4UPLOAD_LINK)) is None


def test_mp4upload_relative_location_is_joined() -> None:
    scraper = _make_mp4upload_scraper(location="/d/token/video.mp4")

    result = asyncio.run(scraper.get_file_download_link(MP4UPLOAD_LINK))

    assert result == "https://www.mp4upload.com/d/token/video.mp4"


def test_mp4upload_embed_link_returns_none_without_request() -> None:
    scraper = _make_mp4upload_scraper()
    embed = DownloadLinkInfo(
        server="MP4Upload",
        url="https://www.mp4upload.com/embed-fevqfos5cs7q.html",
    )

    assert asyncio.run(scraper.get_file_download_link(embed)) is None
    scraper.mp4upload_http.post_redirect_location.assert_not_called()


def test_mp4upload_blocked_error_propagates() -> None:
    scraper = _make_mp4upload_scraper(error=ScraperBlockedError("blocked"))

    with pytest.raises(ScraperBlockedError):
        asyncio.run(scraper.get_file_download_link(MP4UPLOAD_LINK))
