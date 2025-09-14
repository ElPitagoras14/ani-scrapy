from datetime import datetime
from bs4 import BeautifulSoup, Tag
from urllib.parse import quote
from curl_cffi import AsyncSession

from ani_scrapy.async_api.base import AsyncBaseScraper
from ani_scrapy.async_api.browser import AsyncBrowser
from ani_scrapy.core.schemas import (
    _AnimeType,
    _RelatedType,
    AnimeInfo,
    EpisodeDownloadInfo,
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
from ani_scrapy.core.constants.jkanime import (
    BASE_URL,
    SEARCH_URL,
    IMPERSONATE,
    related_type_map,
    anime_type_map,
    month_map,
)
from ani_scrapy.async_api.scrapers.jkanime.file_link import (
    get_streamwish_file_link,
    get_mediafire_file_link,
)


get_file_download_link = {
    "Streamwish": get_streamwish_file_link,
    "Mediafire": get_mediafire_file_link,
}


class JKAnimeScraper(AsyncBaseScraper):
    """
    Async scraper for jkanime.net.
    """

    def __init__(self, verbose: bool = False, level: str = "INFO"):
        super().__init__(verbose, level)
        self._log("Initializing JKAnime scraper", "DEBUG")

    def _parse_anime_info(self, element: Tag) -> SearchAnimeInfo:
        try:
            anime_id = element.select_one("a[href]")["href"].split("/")[-2]
            type_ = element.select_one("li.anime").text
            title = element.select_one("h5 > a").text
            poster = element.select_one("a > div")["data-setbg"]

            self._log(f"Found anime '{title}' with id '{anime_id}'", "DEBUG")
            return SearchAnimeInfo(
                id=anime_id,
                title=title,
                poster=poster,
                type=anime_type_map.get(type_, _AnimeType.TV),
            )
        except Exception as e:
            raise ScraperParseError(e)

    async def search_anime(self, query: str) -> PagedSearchAnimeInfo:
        """
        Search for anime by query.

        Parameters
        ----------
        query : str
            The query to search for.

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
        self._log(
            f"Searching for anime with query '{query}'",
        )

        safe_query = quote(query)
        search_anime_url = f"{SEARCH_URL}/{safe_query}"
        self._log(f"Using search url '{search_anime_url}'", "DEBUG")

        async with AsyncSession() as session:
            response = await session.get(
                search_anime_url, impersonate=IMPERSONATE
            )
            if response.status_code == 403:
                raise ScraperBlockedError(
                    f"Request failed with status code {response.status_code}"
                )
            if response.status_code == 500:
                raise ScraperTimeoutError(
                    f"Request failed with status code {response.status_code}"
                )

            html_text = response.text
            soup = BeautifulSoup(html_text, "lxml")
            elements = soup.select("div.row.page_directorio > div")
            self._log(
                f"Found {len(elements)} animes",
            )

            animes_info = [
                self._parse_anime_info(element) for element in elements
            ]
            return PagedSearchAnimeInfo(
                page=1,
                total_pages=1,
                animes=animes_info,
            )

    async def get_anime_info(
        self,
        anime_id: str,
        tab_timeout: int = 200,
        browser: AsyncBrowser = None,
    ) -> AnimeInfo:
        """
        Get information about an anime.

        Parameters
        ----------
        anime_id : str
            The id of the anime to get information about.
        tab_timeout : int, optional
            The timeout for waiting for the tab to load. Defaults to 200.
        browser : AsyncBrowser, optional
            The browser to use for scraping. If not provided, a new browser
            will be created.

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
        url = f"{BASE_URL}/{anime_id}"

        self._log(
            f"Getting anime info for anime with id '{anime_id}'",
        )

        external_browser = browser is not None
        if not external_browser:
            browser = await AsyncBrowser().__aenter__()

        page = await browser.new_page()
        await page.goto(url)

        html_text = await page.content()
        soup = BeautifulSoup(html_text, "lxml")

        side_anime_info = soup.select_one("div.col-lg-2.picd")
        poster = side_anime_info.find("img")["src"]
        info_container = side_anime_info.select_one("div.card-bod")
        list_info = info_container.find_all("li")
        type_ = anime_type_map.get(list_info[0].text, _AnimeType.TV)
        genres = list_info[1].find_all("a")
        is_finished = None
        for l_info in list_info:
            div = l_info.find("div")
            if div:
                if div.text == "Concluido":
                    is_finished = True
                    break
                if div.text == "En emision":
                    is_finished = False
                    break

        main_anime_info = soup.select_one("div.anime_info")
        title = main_anime_info.find("h3").text
        synopsis = main_anime_info.select_one("p.scroll").text

        raw_next_episode_date = soup.select("div#proxep")
        parsed_date = None
        if raw_next_episode_date:
            next_episode_date = raw_next_episode_date[-1].text
            current_year = datetime.now().year
            parts = next_episode_date.strip().split(" ")
            day = parts[-3]
            month = month_map[parts[-1]]
            parsed_date = datetime.strptime(
                f"{current_year}-{month}-{day}", "%Y-%m-%d"
            ).date()

        select = await page.query_selector("div.nice-select.anime__pagination")
        paged_episodes = await select.query_selector_all("ul > li")

        all_episodes = []
        for paged_episode in paged_episodes:
            await select.click()

            await page.wait_for_timeout(1000)

            current_tabs = browser.context.pages

            if len(current_tabs) > 1:
                await current_tabs[-1].close()
                await select.click()

            await paged_episode.click()

            await page.wait_for_timeout(tab_timeout)

            html_text = await page.content()
            soup = BeautifulSoup(html_text, "lxml")
            episodes_container = soup.select_one("div#episodes-content")
            episodes = episodes_container.select("div.epcontent")
            for episode in episodes:
                episode_id = episode.select_one("a")["href"].split("/")[-2]
                image_preview = episode.select_one("a > div")["data-setbg"]
                all_episodes.append(
                    EpisodeInfo(
                        id=episode_id,
                        anime_id=anime_id,
                        image_preview=image_preview,
                    )
                )

        navbar = await page.query_selector("nav.anime-tabs.mb-4")
        options = await navbar.query_selector_all("ul > li")
        await options[1].click()

        html_text = await page.content()
        soup = BeautifulSoup(html_text, "lxml")

        other_titles_container = soup.select_one(
            "div.rounded.bg-dark.mt-2.altert.alternativost"
        )
        all_titles = []
        title_info = other_titles_container.select("div > b")
        for single_title in title_info:
            all_titles.append(single_title.next_sibling.text.strip())

        related_info_container = soup.select_one("div.col.col-lg-6")
        all_related_info = []
        child_elements = related_info_container.find_all(recursive=False)
        last_type = None
        for child_element in child_elements:
            tag = child_element.name.lower()
            if tag == "h5":
                type_text = child_element.get_text(strip=True)
                last_type = related_type_map.get(
                    type_text, _RelatedType.PARALLEL_HISTORY
                )
            elif tag == "a":
                raw_related_id = child_element.get("href")
                related_id = raw_related_id.split("/")[-2]
                raw_related_title = child_element.get_text(strip=True)
                related_title = raw_related_title.split(" (")[0]
                all_related_info.append(
                    RelatedInfo(
                        id=related_id,
                        title=related_title,
                        type=last_type,
                    )
                )

        await page.close()
        if not external_browser:
            await browser.__aexit__(None, None, None)

        return AnimeInfo(
            id=anime_id,
            title=title,
            poster=poster,
            synopsis=synopsis,
            type=type_,
            rating=None,
            is_finished=is_finished,
            other_titles=all_titles,
            genres=[genre.text for genre in genres],
            related_info=all_related_info,
            next_episode_date=parsed_date,
            episodes=all_episodes,
        )

    async def get_table_download_links(
        self, anime_id: str, episode_id: int, browser: AsyncBrowser = None
    ) -> EpisodeDownloadInfo:
        """
        Get the table download links for an episode.

        Parameters
        ----------
        anime_id : str
            The id of the anime.
        episode_id : int
            The id of the episode.
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
        url = f"{BASE_URL}/{anime_id}/{episode_id}"

        self._log(
            f"Getting table download links for anime with id '{anime_id}' "
            + f"and episode id '{episode_id}'",
        )

        external_browser = browser is not None
        if not external_browser:
            browser = await AsyncBrowser(headless=True).__aenter__()

        page = await browser.new_page()
        await page.goto(url)

        html_text = await page.content()
        soup = BeautifulSoup(html_text, "lxml")
        download_container = soup.select_one("div.download.mt-2")
        download_links = download_container.select("tr")[1:]

        all_download_links = []
        for download_link in download_links:
            cells = download_link.select("td")
            server = cells[0].text
            download_link = download_link.find("a")["href"]
            all_download_links.append(
                DownloadLinkInfo(
                    server=server,
                    url=download_link,
                )
            )

        await page.close()

        if not external_browser:
            await browser.__aexit__(None, None, None)

        return EpisodeDownloadInfo(
            episode_id=episode_id,
            download_links=all_download_links,
        )

    async def get_iframe_download_links(
        self,
        anime_id: str,
        episode_id: int,
        browser: AsyncBrowser = None,
    ) -> EpisodeDownloadInfo:
        """
        Note
        ----
        Not supported yet.

        Get the iframe download links for an episode.

        Parameters
        ----------
        anime_id : str
            The id of the anime.
        episode_id : int
            The id of the episode.
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
        pass

    async def get_file_download_link(
        self,
        download_info: DownloadLinkInfo,
        browser: AsyncBrowser = None,
    ) -> str:
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
        str
            The file download link.

        Raises
        ------
        TypeError
            If the download_info is not a DownloadLinkInfo object.
        ValueError
            If the download_info.server is not supported for file download.
        """
        server = download_info.server
        url = download_info.url

        self._log(
            f"Getting file download link for server '{download_info.server}'",
        )

        if server not in get_file_download_link:
            self._log(
                f"Server '{server}' not supported for file download",
                "error",
            )
            return None

        external_browser = browser is not None
        if not external_browser:
            browser = await AsyncBrowser().__aenter__()

        page = await browser.new_page()

        try:
            get_file_fn = get_file_download_link[server]
            file_link = await get_file_fn(page, url)

            await page.close()

            if not external_browser:
                await browser.__aexit__(None, None, None)

            return file_link
        except TimeoutError as e:
            self._log("Timeout getting file download link", "error")
            raise ScraperTimeoutError(e)
        except Exception as e:
            self._log("Error getting file download link", "error")
            raise e
