import json
import aiohttp
import asyncio
from typing import List, Optional
from bs4 import BeautifulSoup, Tag
from datetime import datetime
from loguru import logger
from anime_scraper.base import BaseAnimeScraper
from anime_scraper.browser_manager import BrowserManager

from anime_scraper.utils import (
    clean_related_type,
    clean_text,
)
from anime_scraper.tab_link import get_stape_link
from anime_scraper.schemas import (
    _AnimeFormat,
    _AnimeType,
    _RelatedType,
    AnimeInfo,
    BulkDownloadLinkInfo,
    DownloadLinkInfo,
    PagedSearchAnimeInfo,
    RelatedInfo,
    SearchAnimeInfo,
    EpisodeInfo,
)
from anime_scraper.exceptions import (
    ScraperBlockedError,
    ScraperParseError,
    ScraperTimeoutError,
)
from anime_scraper.scrapers.animeflv.tab_link import (
    get_yourupload_link_wrapper,
    get_sw_link_wrapper,
)
from anime_scraper.scrapers.animeflv.utils import (
    close_not_allowed_popups,
    get_order_idx,
)
from anime_scraper.scrapers.animeflv.constants import (
    BASE_URL,
    SEARCH_URL,
    ANIME_VIDEO_URL,
    ANIME_URL,
    BASE_EPISODE_IMG_URL,
)

related_type_map = {
    "Precuela": _RelatedType.PREQUEL,
    "Sequel": _RelatedType.SEQUEL,
    "Historia Paralela": _RelatedType.PARALLEL_HISTORY,
    "Historia Principal": _RelatedType.MAIN_HISTORY,
}

anime_type_map = {
    "Anime": _AnimeType.TV,
    "Pelicula": _AnimeType.MOVIE,
    "OVA": _AnimeType.OVA,
    "Especial": _AnimeType.SPECIAL,
}

format_map = {
    "DUB": _AnimeFormat.SUB,
    "SUB": _AnimeFormat.SUB,
}

get_tab_download_link = {
    "SW": get_sw_link_wrapper,
    "YourUpload": get_yourupload_link_wrapper,
}


class AnimeFLVScraper(BaseAnimeScraper):
    def _parse_anime_info(self, element: Tag) -> SearchAnimeInfo:
        try:
            anime_id = element.find("a", href=True)["href"].split("/")[-1]
            type_ = element.find("span", class_="Type").text
            title = element.find("h3").text
            poster = element.find("img")["src"]

            logger.debug(f"Found anime '{title}' with id '{anime_id}'")

            return SearchAnimeInfo(
                id=anime_id,
                title=title,
                poster=poster,
                type=anime_type_map.get(type_, _AnimeType.TV),
            )
        except Exception as e:
            raise ScraperParseError(e)

    async def search_anime_async(
        self,
        query: str = None,
        page: int = 1,
    ) -> List[PagedSearchAnimeInfo]:
        if not isinstance(page, int):
            raise TypeError("The variable 'page' must be of type 'int'")
        if page < 1:
            raise ValueError("The variable 'page' must be greater than 0")

        if query is None:
            raise ValueError("The variable 'query' must be provided")
        if len(query) < 3:
            raise ValueError(
                "The variable 'query' must be at least 3 characters"
            )

        context_logger = logger.bind(query=query, page=page)
        context_logger.info("Searching for anime")

        params = {"q": query, "page": page}

        async with aiohttp.ClientSession() as session:
            async with session.get(SEARCH_URL, params=params) as response:
                if response.status == 403:
                    raise ScraperBlockedError(
                        f"Request failed with status code {response.status}"
                    )
                if response.status == 500:
                    raise ScraperTimeoutError(
                        f"Request failed with status code {response.status}"
                    )

                html_text = await response.text()
                soup = BeautifulSoup(html_text, "lxml")
                elements = soup.select(
                    "div.Container ul.ListAnimes li article"
                )

                logger.info(f"Found {len(elements)} animes")

                animes_info = [
                    self._parse_anime_info(element) for element in elements
                ]
                pagination_links = soup.select("div.NvCnAnm li a")
                total_pages = 1
                if len(pagination_links) > 1:
                    total_pages = int(pagination_links[-2].text)

                return PagedSearchAnimeInfo(
                    page=page,
                    total_pages=total_pages,
                    animes=animes_info,
                )

    async def get_anime_info_async(self, anime_id: str = None) -> AnimeInfo:
        if not isinstance(anime_id, str):
            raise TypeError("The variable 'anime_id' must be of type 'str'")

        logger.info(f"Getting anime info for anime with id '{anime_id}'")

        url = f"{ANIME_URL}/{anime_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 403:
                    raise ScraperBlockedError(
                        f"Request failed with status code {response.status}"
                    )
                if response.status == 500:
                    raise ScraperTimeoutError(
                        f"Request failed with status code {response.status}"
                    )

                html_text = await response.text()
                soup = BeautifulSoup(html_text, "lxml")

                title = soup.select_one("h1.Title").text
                poster = soup.select_one("figure img")["src"]
                synopsis = soup.select_one("div.Description p").text
                genres_list = soup.select("nav.Nvgnrs a")
                other_titles_list = soup.select("div.Ficha span.TxtAlt")

                related_info_list = soup.select("ul.ListAnmRel li a")
                related_info = [
                    RelatedInfo(
                        id=related_info["href"].split("/")[-1],
                        title=related_info.text,
                        type=related_type_map.get(
                            clean_related_type(related_info.next_sibling),
                            _RelatedType.PARALLEL_HISTORY,
                        ),
                    )
                    for related_info in related_info_list
                ]

                type_ = soup.select_one("div.Ficha span.Type").text

                info_ids = []
                episodes_data = []
                episodes = []
                for script in soup.find_all("script"):
                    contents = str(script)

                    if "var anime_info = [" in contents:
                        anime_info = contents.split("var anime_info = ")[
                            1
                        ].split(";")[0]
                        info_ids = json.loads(anime_info)

                    if "var episodes = [" in contents:
                        data = contents.split("var episodes = ")[1].split(";")[
                            0
                        ]
                        episodes_data.extend(json.loads(data))

                anime_thumb_id = info_ids[0]

                for episode, _ in reversed(episodes_data):
                    image_prev = (
                        f"{BASE_EPISODE_IMG_URL}/{anime_thumb_id}/{episode}"
                        + "/th_3.jpg"
                    )
                    episodes.append(
                        EpisodeInfo(
                            id=episode,
                            anime=anime_id,
                            image_preview=image_prev,
                        )
                    )

                rating = soup.select_one("div.Ficha span.vtprmd").text
                is_finished = (
                    soup.select_one("aside.SidebarA span.fa-tv").text
                    == "Finalizado"
                )
                next_episode_date = None
                if len(info_ids) > 3:
                    next_episode_date = info_ids[3]

                return AnimeInfo(
                    id=anime_id,
                    title=title,
                    poster=f"{BASE_URL}{poster}",
                    synopsis=clean_text(synopsis) if synopsis else None,
                    rating=rating,
                    is_finished=is_finished,
                    type=anime_type_map.get(type_, _AnimeType.TV),
                    other_titles=[title.text for title in other_titles_list],
                    genres=[genre.text for genre in genres_list],
                    related_info=related_info,
                    episodes=episodes,
                    next_episode_date=(
                        datetime.fromisoformat(next_episode_date)
                        if next_episode_date
                        else None
                    ),
                )

    async def get_static_download_links_async(
        self,
        anime_id: str = None,
        episode_id: int = None,
    ) -> List[DownloadLinkInfo]:
        if not isinstance(anime_id, str):
            raise TypeError("The variable 'anime_id' must be of type 'str'")
        if not isinstance(episode_id, int):
            raise TypeError("The variable 'episode_id' must be of type 'int'")
        if episode_id < 0:
            raise ValueError(
                "The variable 'episode_id' must be greater than or equal to 0"
            )

        logger.info(
            f"Getting dynamic download links for anime with id '{anime_id}' "
            + f"and episode id '{episode_id}'"
        )

        url = f"{ANIME_VIDEO_URL}/{anime_id}-{episode_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 403:
                    raise ScraperBlockedError(
                        f"Request failed with status code {response.status}"
                    )
                if response.status == 500:
                    raise ScraperTimeoutError(
                        f"Request failed with status code {response.status}"
                    )

                html_text = await response.text()
                soup = BeautifulSoup(html_text, "lxml")

                rows_list = soup.select("div.WdgtCn table tbody tr")
                rows = []
                for row in rows_list:
                    cells = row.select("td")
                    logger.debug(
                        f"Found download link for server '{cells[0].text}'"
                    )

                    rows.append(
                        DownloadLinkInfo(
                            server=cells[0].text,
                            format=format_map.get(
                                cells[2].text, _AnimeFormat.SUB
                            ),
                            url=cells[3].select_one("a")["href"],
                        )
                    )

            return rows

    async def get_dynamic_download_links_async(
        self,
        anime_id: str,
        episode_id: int,
        link_limit: int = None,
        browser: BrowserManager = None,
    ) -> List[DownloadLinkInfo]:
        url = f"{ANIME_VIDEO_URL}/{anime_id}-{episode_id}"

        logger.info(
            f"Getting dynamic download links for anime with id '{anime_id}' "
            + f"and episode id '{episode_id}'"
        )

        external_browser = browser is not None
        if not external_browser:
            browser = await BrowserManager().__aenter__()

        page = await browser.new_page()
        page.on("popup", close_not_allowed_popups)

        search_page = await browser.new_page()
        search_page.on("popup", close_not_allowed_popups)

        await page.goto(url)

        rows_list = await page.query_selector_all("div.WdgtCn table tbody tr")
        stape_url = None
        for row in rows_list:
            cells = await row.query_selector_all("td")
            server = await cells[0].inner_text()
            if server == "Stape":
                logger.debug("Found stape link")
                raw_stape_url = await cells[3].query_selector("a")
                stape_url = await raw_stape_url.get_attribute("href")
                break

        server_urls = await page.query_selector_all("div.CpCnA ul.CapiTnv li")
        server_names = [
            await server_url.get_attribute("title")
            for server_url in server_urls
        ]

        cnt_valid = 0
        download_links = []

        if stape_url:
            try:
                download_link = await get_stape_link(search_page, stape_url)

                if not download_link:
                    download_links.append(
                        DownloadLinkInfo(
                            server="Stape",
                            format=_AnimeFormat.SUB,
                            url=None,
                        )
                    )
                else:
                    download_links.append(
                        DownloadLinkInfo(
                            server="Stape",
                            format=_AnimeFormat.SUB,
                            url=download_link,
                        )
                    )
                    cnt_valid += 1
            except TimeoutError as e:
                logger.debug("Timeout getting stape download link")
                raise ScraperTimeoutError(e)
            except Exception:
                logger.exception("Error getting stape download link")

        if link_limit is not None and cnt_valid >= link_limit:
            await page.close()
            await search_page.close()
            if not external_browser:
                await browser.__aexit__(None, None, None)
            return download_links

        order_idx = get_order_idx(server_names)

        for idx in order_idx:
            if link_limit is not None and cnt_valid >= link_limit:
                await page.close()
                await search_page.close()
                if not external_browser:
                    await browser.__aexit__(None, None, None)
                return download_links

            name = server_names[idx]

            if name not in get_tab_download_link:
                continue

            url = await server_urls[idx].click()

            try:
                get_fn = get_tab_download_link[name]
                download_link = await get_fn(page, search_page)

                if download_link is None:
                    download_links.append(
                        DownloadLinkInfo(
                            server=name,
                            format=_AnimeFormat.SUB,
                            url=None,
                        )
                    )
                    continue

                download_links.append(
                    DownloadLinkInfo(
                        server=name,
                        format=_AnimeFormat.SUB,
                        url=download_link,
                    )
                )
                cnt_valid += 1

            except TimeoutError as e:
                logger.debug("Timeout getting download link")
                download_links.append(
                    DownloadLinkInfo(
                        server=name,
                        format=_AnimeFormat.SUB,
                        url=None,
                    )
                )
                raise ScraperTimeoutError(e)
            except Exception:
                logger.exception("Error getting download link")
                download_links.append(
                    DownloadLinkInfo(
                        server=name,
                        format=_AnimeFormat.SUB,
                        url=None,
                    )
                )

        await page.close()
        await search_page.close()

        if not external_browser:
            await browser.__aexit__(None, None, None)

        return download_links

    async def _download_episode_with_semaphore(
        self,
        anime_id: str,
        episode_id: int,
        link_limit: Optional[int],
        browser_manager: BrowserManager,
        semaphore: asyncio.Semaphore,
    ) -> List[DownloadLinkInfo]:
        async with semaphore:
            return await self.get_dynamic_download_links_async(
                anime_id, episode_id, link_limit, browser_manager
            )

    async def get_bulk_dynamic_download_links_async(
        self,
        anime_id: str,
        episode_ids: List[int],
        link_limit: int = None,
        max_concurrent: int = 3,
    ) -> List[BulkDownloadLinkInfo]:
        semaphore = asyncio.Semaphore(max_concurrent)

        async with BrowserManager() as browser:
            tasks = [
                self._download_episode_with_semaphore(
                    anime_id, ep_id, link_limit, browser, semaphore
                )
                for ep_id in episode_ids
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

        episode_results = {}
        for ep_id, result in zip(episode_ids, results):
            if isinstance(result, Exception):
                episode_results[ep_id] = []
                print(f"Error en episodio {ep_id}: {result}")
            else:
                episode_results[ep_id] = result

        return episode_results
