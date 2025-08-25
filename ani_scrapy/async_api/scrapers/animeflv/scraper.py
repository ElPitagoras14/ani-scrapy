import json
import aiohttp
from typing import Optional
from bs4 import BeautifulSoup, Tag
from datetime import datetime
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from ani_scrapy.async_api.base import AsyncBaseScraper
from ani_scrapy.async_api.browser import AsyncBrowser
from ani_scrapy.async_api.scrapers.animeflv.utils import (
    close_not_allowed_popups,
)
from ani_scrapy.core.utils.general import (
    clean_related_type,
    clean_text,
)
from ani_scrapy.core.schemas import (
    _AnimeType,
    _RelatedType,
    EpisodeDownloadInfo,
    AnimeInfo,
    DownloadLinkInfo,
    PagedSearchAnimeInfo,
    RelatedInfo,
    SearchAnimeInfo,
    EpisodeInfo,
)
from ani_scrapy.core.exceptions import (
    ScraperBlockedError,
    ScraperParseError,
    ScraperTimeoutError,
)
from ani_scrapy.async_api.scrapers.animeflv.tab_link import (
    get_yourupload_link,
    get_sw_link,
)
from ani_scrapy.async_api.scrapers.animeflv.file_link import (
    get_sw_file_link,
    get_yourupload_file_link,
)
from ani_scrapy.core.utils.animeflv import get_order_idx
from ani_scrapy.core.constants.animeflv import (
    BASE_URL,
    SEARCH_URL,
    ANIME_VIDEO_URL,
    ANIME_URL,
    BASE_EPISODE_IMG_URL,
    related_type_map,
    anime_type_map,
)


get_tab_download_link = {
    "SW": get_sw_link,
    "YourUpload": get_yourupload_link,
}

get_file_download_link = {
    "SW": get_sw_file_link,
    "YourUpload": get_yourupload_file_link,
}


class AnimeFLVScraper(AsyncBaseScraper):
    """
    Async scraper for animeflv.net.
    """

    def __init__(self, verbose: bool = False, level: str = "INFO"):
        super().__init__(verbose, level)
        self._log("Initializing AnimeFLV scraper", "DEBUG")

    def _parse_anime_info(self, element: Tag) -> SearchAnimeInfo:
        try:
            anime_id = element.select_one("a[href]")["href"].split("/")[-1]
            type_ = element.select_one("span.Type").text
            title = element.select_one("h3").text
            poster = element.select_one("img")["src"]

            self._log(f"Found anime '{title}' with id '{anime_id}'", "DEBUG")

            return SearchAnimeInfo(
                id=anime_id,
                title=title,
                poster=poster,
                type=anime_type_map.get(type_, _AnimeType.TV),
            )
        except Exception as e:
            raise ScraperParseError(e)

    async def search_anime(
        self,
        query: str,
        page: int = 1,
    ) -> PagedSearchAnimeInfo:
        """
        Search for anime by query.

        Parameters
        ----------
        query : str
            The query to search for.
        page : int
            The page number to search for. Defaults to 1.

        Returns
        -------
        PagedSearchAnimeInfo
            An object containing the page number, total pages, and animes found.

        Raises
        ------
        ValueError
            If the query is not provided or is less than 3 characters.
        ScraperBlockedError
            If the request is blocked by the server.
        ScraperTimeoutError
            If the request times out.
        ScraperParseError
            If the response from the server cannot be parsed.
        """
        if page < 1:
            raise ValueError("The variable 'page' must be greater than 0")

        if len(query) < 3:
            raise ValueError(
                "The variable 'query' must be at least 3 characters"
            )

        self._log(f"Searching for anime with query '{query}' and page {page}")

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

                self._log(f"Found {len(elements)} animes")

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

    async def get_anime_info(self, anime_id: str) -> AnimeInfo:
        """
        Get information about an anime.

        Parameters
        ----------
        anime_id : str
            The id of the anime to get information about.

        Returns
        -------
        AnimeInfo
            Information about the anime.

        Raises
        ------
        TypeError
            If the anime_id is not a string.
        ScraperBlockedError
            If the request is blocked by the server.
        ScraperTimeoutError
            If the request times out.
        ScraperParseError
            If the response from the server cannot be parsed.
        """

        self._log(f"Getting anime info for anime with id '{anime_id}'")

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
                            anime_id=anime_id,
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
                        datetime.fromisoformat(next_episode_date).date()
                        if next_episode_date
                        else None
                    ),
                )

    async def get_table_download_links(
        self,
        anime_id: str,
        episode_id: int,
    ) -> EpisodeDownloadInfo:
        """
        Get the table download links for an episode.

        Parameters
        ----------
        anime_id : str
            The id of the anime.
        episode_id : int
            The id of the episode.

        Returns
        -------
        EpisodeDownloadInfo
            An object containing the episode id and download links.

        Raises
        ------
        TypeError
            If the anime_id or episode_id is not a string or int, respectively.
        ValueError
            If the episode_id is less than 0.
        ScraperBlockedError
            If the request is blocked by the server.
        ScraperTimeoutError
            If the request times out.
        ScraperParseError
            If the response from the server cannot be parsed.
        """
        if episode_id < 0:
            raise ValueError(
                "The variable 'episode_id' must be greater than or equal to 0"
            )

        self._log(
            f"Getting table download links for anime with id '{anime_id}' "
            + f"and episode id '{episode_id}'",
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

                rows_list = soup.select("table.RTbl.Dwnl tbody tr")
                rows = []
                for row in rows_list:
                    cells = row.select("td")
                    self._log(
                        f"Found download link for server '{cells[0].text}'",
                        "DEBUG",
                    )

                    rows.append(
                        DownloadLinkInfo(
                            server=cells[0].text,
                            url=cells[3].select_one("a")["href"],
                        )
                    )

            return EpisodeDownloadInfo(
                episode_id=episode_id,
                download_links=rows,
            )

    async def get_iframe_download_links(
        self,
        anime_id: str,
        episode_id: int,
        tab_timeout: int = 200,
        browser: Optional[AsyncBrowser] = None,
    ) -> EpisodeDownloadInfo:
        """
        Get the iframe download links for an episode.

        Parameters
        ----------
        anime_id : str
            The id of the anime.
        episode_id : int
            The id of the episode.
        tab_timeout : int, optional
            The timeout for waiting for the tab to load. Defaults to 200.
        browser : AsyncBrowser, optional
            The browser to use for scraping. If not provided, a new browser
            will be created.

        Returns
        -------
        EpisodeDownloadInfo
            An object containing the episode id and download links.

        Raises
        ------
        TypeError
            If the anime_id or episode_id is not a string or int, respectively.
        ValueError
            If the episode_id is less than 0.
        ScraperBlockedError
            If the request is blocked by the server.
        ScraperTimeoutError
            If the request times out.
        ScraperParseError
            If the response from the server cannot be parsed.
        """
        url = f"{ANIME_VIDEO_URL}/{anime_id}-{episode_id}"

        self._log(
            f"Getting iframe download links for anime with id '{anime_id}' "
            + f"and episode id '{episode_id}'",
        )

        external_browser = browser is not None
        if not external_browser:
            browser = await AsyncBrowser().__aenter__()

        page = await browser.new_page()
        page.on("popup", close_not_allowed_popups)
        await page.goto(url)

        server_urls = await page.query_selector_all("div.CpCnA ul.CapiTnv li")
        server_names = [
            await server_url.get_attribute("title")
            for server_url in server_urls
        ]

        download_links = []

        order_idx = get_order_idx(server_names)
        for idx in order_idx:
            name = server_names[idx]

            if name not in get_tab_download_link:
                continue

            await server_urls[idx].click()
            await page.wait_for_timeout(tab_timeout)
            await server_urls[idx].click()
            try:
                get_fn = get_tab_download_link[name]
                download_link = await get_fn(page)

                if download_link is None:
                    download_links.append(
                        DownloadLinkInfo(
                            server=name,
                            url=None,
                        )
                    )
                    continue

                download_links.append(
                    DownloadLinkInfo(
                        server=name,
                        url=download_link,
                    )
                )

            except TimeoutError as e:
                self._log("Timeout getting download link", "ERROR")
                download_links.append(
                    DownloadLinkInfo(
                        server=name,
                        url=None,
                    )
                )
                raise ScraperTimeoutError(e)
            except Exception as e:
                self._log("Error getting download link", "ERROR")
                download_links.append(
                    DownloadLinkInfo(
                        server=name,
                        url=None,
                    )
                )
                raise e

        await page.close()

        if not external_browser:
            await browser.__aexit__(None, None, None)

        return EpisodeDownloadInfo(
            episode_id=episode_id,
            download_links=download_links,
        )

    async def get_file_download_link(
        self,
        download_info: DownloadLinkInfo,
        browser: Optional[AsyncBrowser] = None,
    ) -> Optional[str]:
        """
        Get the file download link for a download link info object.

        Parameters
        ----------
        download_info : DownloadLinkInfo
            The download link info object.
        browser : AsyncBrowser, optional
            The browser to use for scraping. If not provided, a new browser
            will be created.

        Returns
        -------
        str | None
            The file download link if found, else None.

        Raises
        ------
        TypeError
            If download_info is not a DownloadLinkInfo object.
        ScraperTimeoutError
            If the operation times out.
        """

        if not isinstance(download_info, DownloadLinkInfo):
            raise TypeError("download_info must be a DownloadLinkInfo object")

        server = download_info.server
        url = download_info.url

        self._log(f"Getting file download link for server '{server}'")

        if server not in get_file_download_link:
            self._log(
                f"Server '{server}' not supported for file download",
                "ERROR",
            )
            return None

        external_browser = browser is not None
        if not external_browser:
            browser = await AsyncBrowser().__aenter__()

        page = None
        try:
            page = await browser.new_page()
            page.on("popup", close_not_allowed_popups)

            get_file_fn = get_file_download_link[server]
            file_link = await get_file_fn(page, url)

            return file_link
        except PlaywrightTimeoutError as e:
            self._log("Timeout getting file download link", "ERROR")
            raise ScraperTimeoutError(e)
        except Exception as e:
            self._log(f"Error getting file download link: {e}", "ERROR")
            raise e
        finally:
            if page:
                await page.close()
            if not external_browser and browser:
                await browser.__aexit__(None, None, None)
