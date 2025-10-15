import requests
from datetime import datetime
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from ani_scrapy.sync_api.browser import SyncBrowser
from ani_scrapy.sync_api.scrapers.jkanime.file_link import (
    get_mediafire_file_link,
    get_streamwish_file_link,
)
import cloudscraper
from urllib.parse import quote
from bs4 import BeautifulSoup, Tag
from ani_scrapy.core.exceptions import (
    ScraperBlockedError,
    ScraperParseError,
    ScraperTimeoutError,
)
from ani_scrapy.core.schemas import (
    _AnimeType,
    _RelatedType,
    AnimeInfo,
    DownloadLinkInfo,
    EpisodeDownloadInfo,
    EpisodeInfo,
    PagedSearchAnimeInfo,
    RelatedInfo,
    SearchAnimeInfo,
)
from ani_scrapy.sync_api.base import SyncBaseScraper
from ani_scrapy.core.constants.jkanime import (
    BASE_URL,
    SEARCH_URL,
    anime_type_map,
    related_type_map,
    month_map,
)


get_file_download_link = {
    "Streamwish": get_streamwish_file_link,
    "Mediafire": get_mediafire_file_link,
}


class JKAnimeScraper(SyncBaseScraper):
    """
    Sync scraper for jkanime.net.
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

    def search_anime(self, query: str) -> PagedSearchAnimeInfo:
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

        if not query or len(query) < 3:
            raise ValueError(
                "The variable 'query' must be at least 3 characters"
            )

        self._log(f"Searching for anime with query '{query}'")

        safe_query = quote(query)
        search_anime_url = f"{SEARCH_URL}/{safe_query}"
        self._log(f"Using search url '{search_anime_url}'", "DEBUG")

        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.get(search_anime_url)
        except requests.Timeout as e:
            raise ScraperTimeoutError("Request timed out") from e
        except Exception as e:
            raise ScraperParseError(
                f"Error fetching search results: {e}"
            ) from e

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
        self._log(f"Found {len(elements)} animes")

        animes_info = [self._parse_anime_info(element) for element in elements]

        return PagedSearchAnimeInfo(
            page=1,
            total_pages=1,
            animes=animes_info,
        )

    def get_anime_info(
        self,
        anime_id: str,
        include_episodes: bool = True,
        tab_timeout: int = 200,
        browser: SyncBrowser | None = None,
    ) -> AnimeInfo:
        """
        Get information about an anime.

        Parameters
        ----------
        anime_id : str
            The id of the anime.
        tab_timeout : int, optional
            The timeout for waiting for the tab to load. Defaults to 200.
        browser : SyncBrowser, optional
            The browser to use for scraping. If not provided, a new browser
            will be created.

        Returns
        -------
        AnimeInfo
            Information about the anime.
        """

        url = f"{BASE_URL}/{anime_id}"
        self._log(f"Getting anime info for anime with id '{anime_id}'")

        external_browser = browser is not None
        if not external_browser:
            browser = SyncBrowser().__enter__()

        page = browser.new_page()
        page.goto(url)

        page.wait_for_selector("div.col-lg-2.picd")

        html_text = page.content()
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
        if raw_next_episode_date and len(raw_next_episode_date) == 2:
            next_episode_date = raw_next_episode_date[-1].text
            current_year = datetime.now().year
            parts = next_episode_date.strip().split(" ")
            day = parts[-3]
            month = month_map[parts[-1]]
            parsed_date = datetime.strptime(
                f"{current_year}-{month}-{day}", "%Y-%m-%d"
            ).date()

        select = page.query_selector("div.nice-select.anime__pagination")
        select.wait_for_selector("ul > li", timeout=10000)
        paged_episodes = select.query_selector_all("ul > li")

        all_episodes = []
        if include_episodes:
            for paged_episode in paged_episodes:
                try:
                    with browser.context.expect_page(
                        timeout=10000
                    ) as new_page_info:
                        select.click()
                    new_page = new_page_info.value
                    new_page.wait_for_load_state("domcontentloaded")
                    new_page.close()
                    select.click()
                except PlaywrightTimeoutError:
                    pass

                paged_episode.click()

                page.wait_for_timeout(1000 + tab_timeout)

                html_text = page.content()
                soup = BeautifulSoup(html_text, "lxml")
                episodes_container = soup.select_one("div#episodes-content")
                episodes = episodes_container.select("div.epcontent")
                for episode in episodes:
                    episode_number = episode.select_one("a")["href"].split(
                        "/"
                    )[-2]
                    image_preview = episode.select_one("a > div")["data-setbg"]
                    number = int(episode_number)
                    all_episodes.append(
                        EpisodeInfo(
                            number=number,
                            anime_id=anime_id,
                            image_preview=image_preview,
                        )
                    )

        navbar = page.query_selector("nav.anime-tabs.mb-4")
        options = navbar.query_selector_all("ul > li")

        try:
            with browser.context.expect_page(timeout=10000) as new_page_info:
                options[1].click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("domcontentloaded")
            new_page.close()
            select.click()
        except PlaywrightTimeoutError:
            pass

        html_text = page.content()
        soup = BeautifulSoup(html_text, "lxml")
        other_titles_container = soup.select_one(
            "div.rounded.bg-dark.mt-2.altert.alternativost"
        )
        all_titles = [
            t.next_sibling.text.strip()
            for t in other_titles_container.select("div > b")
        ]

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
                related_title = child_element.get_text(strip=True).split(" (")[
                    0
                ]
                all_related_info.append(
                    RelatedInfo(
                        id=related_id, title=related_title, type=last_type
                    )
                )

        page.close()
        if not external_browser:
            browser.__exit__(None, None, None)

        return AnimeInfo(
            id=anime_id,
            title=title,
            poster=poster,
            synopsis=synopsis,
            type=type_,
            rating=None,
            is_finished=is_finished,
            other_titles=all_titles,
            genres=[g.text for g in genres],
            related_info=all_related_info,
            next_episode_date=parsed_date,
            episodes=all_episodes,
        )

    def get_new_episodes(
        self,
        anime_id: str,
        last_episode_number: int,
        tab_timeout: int = 200,
        browser: SyncBrowser | None = None,
    ) -> list[EpisodeInfo]:
        """
        Get the new episodes for an anime.

        Parameters
        ----------
        anime_id : str
            The id of the anime.
        last_episode_number : int
            The last episode number to get.
        tab_timeout : int, optional
            The timeout for waiting for the tab to load. Defaults to 200.
        browser : SyncBrowser, optional
            The browser to use for scraping. If not provided, a new browser
            will be created.

        Returns
        -------
        list[EpisodeInfo]
            A list of new episode information.
        """

        url = f"{BASE_URL}/{anime_id}"
        self._log(f"Getting new episodes for anime with id '{anime_id}'")

        external_browser = browser is not None
        if not external_browser:
            browser = SyncBrowser().__enter__()

        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")

        select = page.query_selector("div.nice-select.anime__pagination")
        select.wait_for_selector("ul > li", timeout=10000)
        paged_episodes = select.query_selector_all("ul > li")

        all_episodes = []
        finished = False
        for paged_episode in reversed(paged_episodes):

            try:
                with browser.context.expect_page(
                    timeout=10000
                ) as new_page_info:
                    select.click()
                new_page = new_page_info.value
                new_page.wait_for_load_state("domcontentloaded")
                new_page.close()
                select.click()
            except PlaywrightTimeoutError:
                pass

            paged_episode.click()

            page.wait_for_timeout(1000 + tab_timeout)

            html_text = page.content()
            soup = BeautifulSoup(html_text, "lxml")
            episodes_container = soup.select_one("div#episodes-content")
            episodes = episodes_container.select("div.epcontent")
            for episode in reversed(episodes):
                episode_number = episode.select_one("a")["href"].split("/")[-2]
                image_preview = episode.select_one("a > div")["data-setbg"]
                number = int(episode_number)
                if number <= last_episode_number:
                    finished = True
                    break
                all_episodes.append(
                    EpisodeInfo(
                        number=number,
                        anime_id=anime_id,
                        image_preview=image_preview,
                    )
                )

            if finished:
                break

        page.close()
        if not external_browser:
            browser.__exit__(None, None, None)

        return list(reversed(all_episodes))

    def get_table_download_links(
        self,
        anime_id: str,
        episode_number: int,
        browser: SyncBrowser = None,
    ) -> EpisodeDownloadInfo:
        """
        Get the table download links for an episode.

        Parameters
        ----------
        anime_id : str
            The id of the anime.
        episode_number : int
            The id of the episode.
        browser : SyncBrowser, optional
            The browser to use for scraping. If not provided, a new browser
            will be created.

        Returns
        -------
        EpisodeDownloadInfo
            An object containing the episode id and download links.
        """

        if episode_number < 0:
            raise ValueError("The variable 'episode_number' must be >= 0")

        url = f"{BASE_URL}/{anime_id}/{episode_number}"
        self._log(
            f"Getting table download links for anime '{anime_id}' "
            + f"episode {episode_number}"
        )

        external_browser = browser is not None
        if not external_browser:
            browser = SyncBrowser().__enter__()

        page = browser.new_page()
        page.goto(url)

        html_text = page.content()
        soup = BeautifulSoup(html_text, "lxml")

        download_container = soup.select_one("div.download.mt-2")
        download_rows = download_container.select("tr")[1:]  # Skip header row

        all_download_links = []
        for row in download_rows:
            cells = row.select("td")
            server = cells[0].text
            link = cells[3].select_one("a")["href"]
            all_download_links.append(
                DownloadLinkInfo(server=server, url=link)
            )

        page.close()
        if not external_browser:
            browser.__exit__(None, None, None)

        return EpisodeDownloadInfo(
            episode_number=episode_number,
            download_links=all_download_links,
        )

    def get_iframe_download_links(
        self,
        anime_id: str,
        episode_number: int,
        browser: SyncBrowser | None = None,
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
        episode_number : int
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
            If the anime_id or episode_number is not a string or int.
        ValueError
            If the episode_number is less than 0.
        ScraperBlockedError
            If the request is blocked by the server.
        ScraperTimeoutError
            If the request times out.
        ScraperParseError
            If the response from the server cannot be parsed.
        """
        pass

    def get_file_download_link(
        self,
        download_info: DownloadLinkInfo,
        browser: SyncBrowser | None = None,
    ) -> str | None:
        """
        Get the file download link for a download link info object.

        Parameters
        ----------
        download_info : DownloadLinkInfo
            The download link info object.
        browser : SyncBrowser, optional
            The browser to use for scraping. If not provided, a new browser
            will be created.

        Returns
        -------
        str | None
            The file download link.
        """

        server = download_info.server
        url = download_info.url

        self._log(f"Getting file download link for server '{server}'")

        if server not in get_file_download_link:
            self._log(
                f"Server '{server}' not supported for file download", "ERROR"
            )
            return None

        external_browser = browser is not None
        if not external_browser:
            browser = SyncBrowser().__enter__()

        page = browser.new_page()

        try:
            get_file_fn = get_file_download_link[server]
            file_link = get_file_fn(page, url)

            page.close()
            if not external_browser:
                browser.__exit__(None, None, None)

            return file_link

        except TimeoutError as e:
            self._log("Timeout getting file download link", "ERROR")
            raise ScraperTimeoutError(e)
        except Exception as e:
            self._log("Error getting file download link", "ERROR")
            raise e
