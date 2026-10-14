from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from ani_scrapy.core.exceptions import (
    ScraperBlockedError,
    ScraperHTTPError,
    ScraperNotFoundError,
)
from ani_scrapy.providers.jkanime.scraper import JKAnimeScraper

URL = "https://jkanime.net/some-anime"


def _make_page(status: int | None) -> AsyncMock:
    page = AsyncMock()
    page.goto.return_value = None if status is None else SimpleNamespace(status=status)
    return page


def _run(scraper: JKAnimeScraper, page: AsyncMock, html: str = "") -> object:
    page.content.return_value = html
    return asyncio.run(scraper._get_anime_info_with_episodes(page, URL, "some-anime"))


@pytest.mark.parametrize(
    ("status", "exc_class"),
    [
        (404, ScraperNotFoundError),
        (410, ScraperNotFoundError),
        (429, ScraperBlockedError),
        (500, ScraperHTTPError),
    ],
)
def test_goto_error_status_is_mapped(status: int, exc_class: type) -> None:
    scraper = JKAnimeScraper()
    page = _make_page(status)

    with pytest.raises(exc_class) as info:
        _run(scraper, page)

    assert info.value.status_code == status
    page.wait_for_selector.assert_not_awaited()


@pytest.mark.parametrize("status", [200, None])
def test_goto_success_or_no_response_continues(
    status: int | None, jkanime_anime_html: str
) -> None:
    scraper = JKAnimeScraper()
    scraper._extract_all_episodes = AsyncMock(return_value=[])
    page = _make_page(status)

    info = _run(scraper, page, jkanime_anime_html)

    assert info.id == "some-anime"
    page.wait_for_selector.assert_awaited_once_with("div.col-lg-2.picd")
