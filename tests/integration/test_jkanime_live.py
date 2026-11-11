import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

import pytest

from ani_scrapy import JKAnimeScraper
from ani_scrapy.providers.jkanime.constants import SUPPORTED_SERVERS

pytestmark = pytest.mark.live

ANIME_ID = "naruto"
EPISODE = 1
FILE_EPISODE = 2

T = TypeVar("T")


def run(call: Callable[[JKAnimeScraper], Awaitable[T]]) -> T:
    async def _run() -> T:
        async with JKAnimeScraper() as scraper:
            return await call(scraper)

    return asyncio.run(_run())


def test_search_anime() -> None:
    result = run(lambda s: s.search_anime("naruto"))

    assert result.animes
    assert all(a.id and a.title for a in result.animes)


def test_get_anime_info() -> None:
    info = run(lambda s: s.get_anime_info(ANIME_ID))

    assert info.title
    assert info.episodes


def test_get_table_download_links() -> None:
    result = run(lambda s: s.get_table_download_links(ANIME_ID, EPISODE))

    assert result.episode_number == EPISODE
    assert result.download_links
    assert all(link.server for link in result.download_links)


@pytest.mark.xfail(
    strict=True,
    reason="JKAnime iframe links come back empty (issue #29)",
)
def test_get_iframe_download_links() -> None:
    result = run(lambda s: s.get_iframe_download_links(ANIME_ID, EPISODE))

    assert result.episode_number == EPISODE
    assert result.download_links
    assert all(link.server for link in result.download_links)


def test_get_file_download_link() -> None:
    async def resolve(scraper: JKAnimeScraper) -> list[str | None]:
        table = await scraper.get_table_download_links(ANIME_ID, FILE_EPISODE)
        links = [lk for lk in table.download_links if lk.server in SUPPORTED_SERVERS]
        return [await scraper.get_file_download_link(lk) for lk in links]

    urls = run(resolve)

    assert any(url and url.startswith("http") for url in urls)
