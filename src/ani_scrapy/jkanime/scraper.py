"""JKAnime scraper."""

import asyncio
import time
from urllib.parse import quote
from typing import Optional
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from ani_scrapy.core.base import BaseScraper, create_scraper_logger, generate_task_id
from ani_scrapy.core.browser import AsyncBrowser
from ani_scrapy.core.http import AsyncHttpAdapter
from ani_scrapy.jkanime.parser import JKAnimeParser
from ani_scrapy.jkanime.constants import (
    BASE_URL,
    SEARCH_ENDPOINT,
    SW_DOWNLOAD_URL,
)
from ani_scrapy.core.constants.general import (
    SW_TIMEOUT,
    MEDIAFIRE_TIMEOUT,
)
from ani_scrapy.core.exceptions import ScraperTimeoutError
from ani_scrapy.core.schemas import (
    AnimeInfo,
    DownloadLinkInfo,
    EpisodeDownloadInfo,
    EpisodeInfo,
    PagedSearchAnimeInfo,
)


class JKAnimeScraper(BaseScraper):
    """JKAnime scraper."""

    def __init__(
        self,
        log_file: Optional[str] = None,
        level: str = "INFO",
        headless: bool = True,
        executable_path: str = "",
    ):
        super().__init__(
            log_file=log_file,
            level=level,
            headless=headless,
            executable_path=executable_path,
        )
        self.http = AsyncHttpAdapter(base_url=BASE_URL)
        self.parser = JKAnimeParser()

        self._file_link_getters = {
            "Streamwish": self._get_streamwish_file_link,
            "Mediafire": self._get_mediafire_file_link,
        }

    async def _safe_click(
        self,
        element,
        page,
        reclick: bool = False,
        timeout: int = 10,
        debug_name: str = "",
    ) -> None:
        """Safely click an element handling popups."""
        ctx = page.context
        log = create_scraper_logger(
            page.task_id if hasattr(page, "task_id") else ""
        )

        popup_task = asyncio.create_task(ctx.wait_for_event("page"))

        start = time.perf_counter()
        await element.click(force=True)
        elapsed = time.perf_counter() - start
        log.debug(
            "[{name}] Clicked | {ms}ms",
            name=debug_name,
            ms=round(elapsed * 1000, 2),
        )

        popup = None
        try:
            popup = await asyncio.wait_for(popup_task, timeout=timeout / 1000)
            await popup.wait_for_load_state("domcontentloaded", timeout=3000)
            await popup.close()
        except (asyncio.TimeoutError, PlaywrightTimeoutError):
            if popup:
                await popup.close()
        finally:
            if reclick:
                await element.click(force=True)

    async def search_anime(
        self, query: str, page: int = 1, task_id: Optional[str] = None
    ) -> PagedSearchAnimeInfo:
        """Search anime."""
        if task_id is None:
            task_id = generate_task_id()

        log = create_scraper_logger(task_id)
        log.info("Searching anime | query={query}", query=query)

        safe_query = quote(query)
        search_anime_url = f"{SEARCH_ENDPOINT}/{safe_query}"
        log.debug("Using search URL | url={url}", url=search_anime_url)

        try:
            html_text = await self.http.get(search_anime_url, task_id=task_id)
        except ConnectionError as e:
            raise ScraperTimeoutError(str(e)) from e

        animes = self.parser.parse_search_results(html_text)

        log.info("Search completed | count={count}", count=len(animes))

        return PagedSearchAnimeInfo(
            page=1,
            total_pages=1,
            animes=animes,
        )

    async def get_anime_info(
        self,
        anime_id: str,
        include_episodes: bool = True,
        task_id: Optional[str] = None,
    ) -> AnimeInfo:
        """Get anime info."""
        if task_id is None:
            task_id = generate_task_id()

        log = create_scraper_logger(task_id)
        log.info("Getting anime info | anime_id={anime_id}", anime_id=anime_id)

        url = f"{BASE_URL}/{anime_id}"

        if include_episodes:
            executable_path = (
                self.executable_path if self.executable_path else None
            )
            async with AsyncBrowser(
                executable_path=executable_path,
                headless=self.headless,
            ) as browser:
                async with await browser.new_page() as page:
                    return await self._get_anime_info_with_episodes(
                        page, url, anime_id, task_id
                    )

        try:
            html_text = await self.http.get(url, task_id=task_id)
        except ConnectionError as e:
            raise ScraperTimeoutError(str(e)) from e

        return self.parser.parse_anime_info(html_text, anime_id)

    async def _get_anime_info_with_episodes(
        self, page, url: str, anime_id: str, task_id: str
    ) -> AnimeInfo:
        """Get anime info with episodes using Playwright."""
        log = create_scraper_logger(task_id)
        log.debug("Fetching anime info page with Playwright")

        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_selector("div.col-lg-2.picd")

        html_text = await page.content()
        anime_info = self.parser.parse_anime_info(html_text, anime_id)

        episodes = await self._extract_all_episodes(page, anime_id, task_id)
        anime_info.episodes = list(episodes)

        log.info("Anime info fetched | episodes={count}", count=len(episodes))
        return anime_info

    async def _extract_all_episodes(
        self, page, anime_id: str, task_id: str
    ) -> list[EpisodeInfo]:
        """Extract all episodes by navigating pages."""
        log = create_scraper_logger(task_id)

        await page.wait_for_selector(
            "div.nice-select.anime__pagination ul > li"
        )
        select = await page.query_selector("div.nice-select.anime__pagination")

        paged_episodes = await select.query_selector_all("ul.list > li")

        log.info(
            "Starting episode extraction | total_pages={total}",
            total=len(paged_episodes),
        )

        all_episodes = []
        idx = 0
        retries = max(int(len(paged_episodes) * 1.5), 5)
        is_retry = False

        while idx < len(paged_episodes):
            if retries <= 0:
                log.warning("Retries exceeded, breaking")
                break

            if is_retry:
                await page.wait_for_selector(
                    "div.nice-select.anime__pagination ul > li"
                )
                select = await page.query_selector(
                    "div.nice-select.anime__pagination"
                )
                paged_episodes = await select.query_selector_all(
                    "ul.list > li"
                )
                is_retry = False

                if idx >= len(paged_episodes):
                    log.warning(
                        "Index out of bounds after retry | idx={idx} | pages={pages}",
                        idx=idx,
                        pages=len(paged_episodes),
                    )
                    break

            paged_episode = paged_episodes[idx]

            log.info(
                "Processing page {idx} of {total}",
                idx=idx + 1,
                total=len(paged_episodes),
            )

            await self._safe_click(
                select,
                page,
                reclick=True,
                timeout=3000,
                debug_name=f"select_reclick_{idx+1}",
            )

            await self._safe_click(
                paged_episode,
                page,
                timeout=2000,
                debug_name=f"page_click_{idx+1}",
            )

            html_text = await page.content()
            new_episodes = self.parser.parse_episode_page(html_text, anime_id)

            log.info(
                "Extracted episodes from page | count={count} | last={last}",
                count=len(new_episodes),
                last=new_episodes[-1].number if new_episodes else None,
            )

            if not new_episodes:
                log.warning("[ITER_{idx}] EMPTY - Continuing", idx=idx + 1)

                retries -= 1
                is_retry = True
                continue

            if idx > 0 and all_episodes:
                last_extracted = all_episodes[-1].number
                last_page_episode = new_episodes[-1].number
                if last_page_episode == last_extracted:
                    log.warning(
                        "[ITER_{idx}] SAME episodes detected - Continuing",
                        idx=idx + 1,
                    )

                    retries -= 1
                    is_retry = True
                    continue

            all_episodes.extend(new_episodes)
            idx += 1

        log.info(
            "All episodes extracted | count={count}", count=len(all_episodes)
        )
        return all_episodes

    async def get_new_episodes(
        self,
        anime_id: str,
        last_episode_number: int,
        task_id: Optional[str] = None,
    ) -> list[EpisodeInfo]:
        """Get new episodes since last_episode_number."""
        if task_id is None:
            task_id = generate_task_id()

        log = create_scraper_logger(task_id)
        log.info(
            "Getting new episodes | anime_id={anime_id} last_episode_number={last_episode_number}",
            anime_id=anime_id,
            last_episode_number=last_episode_number,
        )

        url = f"{BASE_URL}/{anime_id}"

        executable_path = (
            self.executable_path if self.executable_path else None
        )
        async with AsyncBrowser(
            executable_path=executable_path,
            headless=self.headless,
        ) as browser:
            async with await browser.new_page() as page:
                return await self._get_new_episodes_internal(
                    page, url, anime_id, last_episode_number, task_id
                )

    async def _get_new_episodes_internal(
        self,
        page,
        url: str,
        anime_id: str,
        last_episode_number: int,
        task_id: str,
    ) -> list[EpisodeInfo]:
        """Internal method for getting new episodes."""
        log = create_scraper_logger(task_id)

        await page.goto(url)
        await page.wait_for_selector(
            "div.nice-select.anime__pagination ul > li"
        )

        select = await page.query_selector("div.nice-select.anime__pagination")
        paged_episodes = await select.query_selector_all("ul.list > li")

        log.debug(
            "Found {count} episode pages",
            count=len(paged_episodes),
        )

        all_episodes = []
        idx = len(paged_episodes) - 1
        retries = max(int(len(paged_episodes) * 1.5), 5)
        finished = False
        is_retry = False

        log.debug(
            "Starting new episode extraction | start_page={page} | last_episode={last}",
            page=idx + 1,
            last=last_episode_number,
        )

        while idx >= 0:
            if retries <= 0:
                log.warning("Retries exceeded, breaking")
                break

            if is_retry:
                log.debug("Retrying, fetching fresh select elements")
                await page.wait_for_selector(
                    "div.nice-select.anime__pagination ul > li"
                )
                select = await page.query_selector(
                    "div.nice-select.anime__pagination"
                )
                paged_episodes = await select.query_selector_all(
                    "ul.list > li"
                )
                is_retry = False

            log.debug(
                "Processing page {idx} of {total}",
                idx=idx + 1,
                total=len(paged_episodes),
            )

            paged_episode = paged_episodes[idx]
            await self._safe_click(
                select,
                page,
                reclick=True,
                timeout=3000,
            )
            await self._safe_click(
                paged_episode,
                page,
                timeout=2000,
            )

            page_url = page.url
            if page_url != url:
                log.warning(
                    "Page URL changed, retrying | retries_left={retries}",
                    retries=retries,
                )
                await page.close()
                page = await page.context.new_page()
                await page.goto(url)
                retries -= 1
                is_retry = True
                continue

            html_text = await page.content()
            new_episodes = self.parser.parse_episode_page(html_text, anime_id)

            log.debug(
                "Extracted episodes from page | count={count} | last_episode={last}",
                count=len(new_episodes),
                last=new_episodes[-1].number if new_episodes else None,
            )

            if not new_episodes:
                log.warning(
                    "Empty episodes page detected, retrying | retries_left={retries}",
                    retries=retries,
                )
                retries -= 1
                is_retry = True
                continue

            new_episodes_found = 0
            for episode in reversed(new_episodes):
                if episode.number <= last_episode_number:
                    finished = True
                    break
                all_episodes.append(episode)
                new_episodes_found += 1

            log.debug(
                "New episodes on page | count={count} | last_extracted={last}",
                count=new_episodes_found,
                last=all_episodes[-1].number if all_episodes else None,
            )

            if idx > 0 and all_episodes:
                if (
                    new_episodes
                    and new_episodes[-1].number == all_episodes[-1].number
                ):
                    log.warning(
                        "Same paged_episode detected, retrying | retries_left={retries}",
                        retries=retries,
                    )
                    retries -= 1
                    is_retry = True
                    continue

            idx -= 1

            if finished:
                break

        log.info(
            "New episodes fetched | count={count}", count=len(all_episodes)
        )
        return all_episodes

    async def get_table_download_links(
        self,
        anime_id: str,
        episode_number: int,
        task_id: Optional[str] = None,
    ) -> EpisodeDownloadInfo:
        """Get table download links for an episode."""
        if task_id is None:
            task_id = generate_task_id()

        log = create_scraper_logger(task_id)
        log.info(
            "Getting table download links | anime_id={anime_id} episode_number={episode_number}",
            anime_id=anime_id,
            episode_number=episode_number,
        )

        executable_path = (
            self.executable_path if self.executable_path else None
        )
        async with AsyncBrowser(
            executable_path=executable_path,
            headless=self.headless,
        ) as browser:
            async with await browser.new_page() as page:
                return await self._get_table_download_links_internal(
                    page, anime_id, episode_number, task_id
                )

    async def _get_table_download_links_internal(
        self,
        page,
        anime_id: str,
        episode_number: int,
        task_id: str,
    ) -> EpisodeDownloadInfo:
        """Get table download links using page from Playwright."""
        log = create_scraper_logger(task_id)

        url = f"{BASE_URL}/{anime_id}/{episode_number}"
        await page.goto(url)

        html = await page.content()
        download_links_data = self.parser.parse_table_download_links(
            html, episode_number
        )
        all_download_links: list[DownloadLinkInfo] = [
            DownloadLinkInfo(server=link["server"], url=link["url"])
            for link in download_links_data
        ]

        log.info(
            "Table download links fetched | count={count}",
            count=len(all_download_links),
        )
        return EpisodeDownloadInfo(
            episode_number=episode_number,
            download_links=all_download_links,
        )

    async def get_iframe_download_links(
        self,
        anime_id: str,
        episode_number: int,
        task_id: Optional[str] = None,
    ) -> EpisodeDownloadInfo:
        """Get iframe download links for an episode."""
        if task_id is None:
            task_id = generate_task_id()

        log = create_scraper_logger(task_id)
        log.warning("iframe download links not supported for JKAnime")

        return EpisodeDownloadInfo(
            episode_number=episode_number, download_links=[]
        )

    async def get_file_download_link(
        self,
        download_info: DownloadLinkInfo,
        task_id: Optional[str] = None,
    ) -> str | None:
        """Get file download link for a download link info object."""
        if task_id is None:
            task_id = generate_task_id()

        log = create_scraper_logger(task_id)

        if not isinstance(download_info, DownloadLinkInfo):
            raise TypeError("download_info must be a DownloadLinkInfo object")

        server = download_info.server
        url = download_info.url

        if url is None:
            return None

        log.info("Getting file download link | server={server}", server=server)

        if server not in self._file_link_getters:
            log.error(
                "Server not supported for file download | server={server}",
                server=server,
            )
            return None

        executable_path = (
            self.executable_path if self.executable_path else None
        )
        async with AsyncBrowser(
            executable_path=executable_path,
            headless=self.headless,
        ) as browser:
            async with await browser.new_page() as page:
                return await self._file_link_getters[server](
                    page, url, task_id
                )

    async def _get_streamwish_file_link(
        self, page, url: str, task_id: str = ""
    ) -> str | None:
        """Get Streamwish file download link."""
        log = create_scraper_logger(task_id)
        log.debug("Getting Streamwish file link")

        await page.goto(url)
        current_url = page.url
        video_id = current_url.split("/")[-1]

        try_urls = [
            f"{SW_DOWNLOAD_URL}/{video_id}_h",
            f"{SW_DOWNLOAD_URL}/{video_id}_n",
            f"{SW_DOWNLOAD_URL}/{video_id}_l",
        ]

        for try_url in try_urls:
            retries = 3
            for _ in range(retries):
                try:
                    await page.goto(try_url)
                    download_button = await page.wait_for_selector(
                        "form#F1 button", timeout=3000
                    )
                    await download_button.click(delay=1000)

                    try:
                        error_label = await page.wait_for_selector(
                            "div.text-danger.text-center.mb-5",
                            timeout=SW_TIMEOUT,
                        )
                        text_label = await error_label.inner_text()
                        if text_label.strip() == "Downloads disabled 620":
                            continue
                    except PlaywrightTimeoutError:
                        pass

                    download_link = await page.wait_for_selector(
                        "div.text-center a.btn", timeout=SW_TIMEOUT
                    )
                    return await download_link.get_attribute("href")
                except Exception:
                    continue

        return None

    async def _get_mediafire_file_link(
        self, page, url: str, task_id: str = ""
    ) -> str | None:
        """Get Mediafire file download link."""
        log = create_scraper_logger(task_id)
        log.debug("Getting Mediafire file link")

        await page.goto(url)

        try:
            download_button = await page.wait_for_selector(
                "a#downloadButton", timeout=MEDIAFIRE_TIMEOUT
            )
        except PlaywrightTimeoutError:
            return None

        async with page.expect_download() as download_info:
            await download_button.click()

        download = await download_info.value
        real_url = download.url
        await download.cancel()
        return real_url

    async def aclose(self) -> None:
        """Cleanup resources."""
        await self.http.close()
