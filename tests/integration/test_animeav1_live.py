import asyncio
import urllib.request
from collections.abc import Awaitable, Callable
from typing import TypeVar

import pytest

from ani_scrapy import SUPPORTED_SERVERS, AnimeAV1Scraper

pytestmark = pytest.mark.live

ANIME_ID = "naruto"
EPISODE = 1

T = TypeVar("T")


def run(call: Callable[[AnimeAV1Scraper], Awaitable[T]]) -> T:
    async def _run() -> T:
        async with AnimeAV1Scraper() as scraper:
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


def test_get_iframe_download_links() -> None:
    result = run(lambda s: s.get_iframe_download_links(ANIME_ID, EPISODE))

    assert result.episode_number == EPISODE
    assert result.download_links
    assert all(link.server for link in result.download_links)


def test_get_file_download_link() -> None:
    async def resolve(scraper: AnimeAV1Scraper) -> list[str | None]:
        table = await scraper.get_table_download_links(ANIME_ID, EPISODE)
        iframe = await scraper.get_iframe_download_links(ANIME_ID, EPISODE)
        links = [
            lk
            for lk in table.download_links + iframe.download_links
            if lk.server in SUPPORTED_SERVERS["animeav1"]
        ]
        return [await scraper.get_file_download_link(lk) for lk in links]

    urls = run(resolve)

    assert any(url and url.startswith("http") for url in urls)


def test_get_file_download_link_mp4upload() -> None:
    async def resolve(scraper: AnimeAV1Scraper) -> str | None:
        table = await scraper.get_table_download_links("black-clover", 1)
        link = next(lk for lk in table.download_links if lk.server == "MP4Upload")
        return await scraper.get_file_download_link(link)

    url = run(resolve)

    assert url and url.startswith("https://")
    request = urllib.request.Request(
        url,
        headers={"Referer": "https://www.mp4upload.com/", "Range": "bytes=0-15"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        assert response.status in (200, 206)
