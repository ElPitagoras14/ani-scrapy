"""JKAnime parsing logic."""

from datetime import datetime
from bs4 import BeautifulSoup
from typing import List

from ani_scrapy.core.schemas import (
    SearchAnimeInfo,
    AnimeInfo,
    EpisodeInfo,
    _AnimeType,
)
from ani_scrapy.jkanime.constants import ANIME_TYPE_MAP
from ani_scrapy.core.constants.general import MONTH_MAP


class JKAnimeParser:
    """Parsing logic for JKAnime."""

    @staticmethod
    def parse_search_results(html: str) -> List[SearchAnimeInfo]:
        """Parse search results from HTML."""
        soup = BeautifulSoup(html, "lxml")
        results = []

        elements = soup.select("div.row.page_directorio > div")

        for element in elements:
            try:
                link_element = element.select_one("a[href]")
                if not link_element:
                    continue

                href = str(link_element.get("href", ""))
                if not href:
                    continue

                anime_id = href.split("/")[-2] if href else ""

                title_element = element.select_one("h5 > a")
                title = title_element.text.strip() if title_element else ""

                poster_element = element.select_one("a > div")
                poster = (
                    str(poster_element.get("data-setbg", "")).strip()
                    if poster_element
                    else ""
                )

                type_element = element.select_one("li.anime")
                type_text = (
                    type_element.text.strip() if type_element else "Anime"
                )
                anime_type = JKAnimeParser._map_anime_type(type_text)

                if anime_id and title:
                    results.append(
                        SearchAnimeInfo(
                            id=anime_id,
                            title=title,
                            type=anime_type,
                            poster=poster,
                        )
                    )

            except Exception:
                continue

        return results

    @staticmethod
    def parse_anime_info(html: str, anime_id: str) -> AnimeInfo:
        """Parse detailed anime information from HTML."""
        soup = BeautifulSoup(html, "lxml")

        side_anime_info = soup.select_one("div.col-lg-2.picd")
        if not side_anime_info:
            raise ValueError("Could not find anime info container")

        poster_element = side_anime_info.find("img")
        poster = (
            str(poster_element.get("src", "")).strip()
            if poster_element
            else ""
        )

        info_container = side_anime_info.select_one("div.card-bod")
        list_info = info_container.find_all("li") if info_container else []

        anime_type = _AnimeType.TV
        if list_info:
            type_text = list_info[0].text.strip()
            anime_type = JKAnimeParser._map_anime_type(type_text)

        genres = []
        if len(list_info) > 1:
            genre_elements = list_info[1].find_all("a")
            genres = [
                genre.text.strip() for genre in genre_elements if genre.text
            ]

        is_finished = False
        parsed_date = None

        for l_info in list_info:
            div = l_info.find("div")
            if div:
                div_text = div.text.strip()
                if div_text == "Concluido":
                    is_finished = True
                    break
                if div_text == "En emision":
                    is_finished = False
                    break

            span = l_info.find("span")
            if span and "Emitido:" in span.text:
                try:
                    _, date = l_info.text.split(":")
                    date = date.strip()
                    parts = date.split()
                    year = parts[-1]
                    month = MONTH_MAP.get(parts[-3], "01")
                    day = parts[-5]
                    parsed_date = datetime.strptime(
                        f"{year}-{month}-{day}", "%Y-%m-%d"
                    )
                except (ValueError, IndexError):
                    pass

        main_anime_info = soup.select_one("div.anime_info")
        title = ""
        synopsis = ""

        if main_anime_info:
            title_element = main_anime_info.find("h3")
            title = title_element.text.strip() if title_element else ""

            synopsis_element = main_anime_info.select_one("p.scroll")
            synopsis = (
                synopsis_element.text.strip() if synopsis_element else ""
            )

        raw_next_episode_date = soup.select("div#proxep")
        if raw_next_episode_date and len(raw_next_episode_date) == 2:
            try:
                next_episode_date = raw_next_episode_date[-1].text.strip()
                current_year = datetime.now().year
                parts = next_episode_date.split(" ")
                day = parts[-3]
                month = MONTH_MAP.get(parts[-1], "01")
                parsed_date = datetime.strptime(
                    f"{current_year}-{month}-{day}", "%Y-%m-%d"
                )
            except (ValueError, IndexError):
                pass

        episodes: list[EpisodeInfo | None] = []

        return AnimeInfo(
            id=anime_id,
            title=title,
            type=anime_type,
            poster=poster,
            synopsis=synopsis,
            rating=None,
            other_titles=[],
            genres=genres,
            related_info=[],
            episodes=list(episodes),
            next_episode_date=parsed_date,
            is_finished=is_finished,
        )

    @staticmethod
    def parse_episode_page(html: str, anime_id: str) -> List[EpisodeInfo]:
        """Parse episode page HTML and extract episodes."""
        soup = BeautifulSoup(html, "lxml")
        episodes = []

        episodes_container = soup.select_one("div#episodes-content")
        if not episodes_container:
            return episodes

        for episode in episodes_container.select("div.epcontent"):
            try:
                link_element = episode.select_one("a")
                if not link_element:
                    continue

                href = link_element.get("href", "")
                if not href:
                    continue

                number = int(href.split("/")[-2])

                img_element = episode.select_one("a > div")
                image_preview = (
                    str(img_element.get("data-setbg", "")) if img_element else None
                )

                episodes.append(
                    EpisodeInfo(
                        number=number,
                        anime_id=anime_id,
                        image_preview=image_preview,
                    )
                )
            except (ValueError, IndexError, TypeError):
                continue

        return episodes

    @staticmethod
    def _map_anime_type(site_type: str) -> _AnimeType:
        """Map site-specific anime types to shared enum."""
        return ANIME_TYPE_MAP.get(site_type, _AnimeType.TV)

    @staticmethod
    def parse_table_download_links(
        html: str, episode_number: int
    ) -> List[dict]:
        """Parse table download links."""
        soup = BeautifulSoup(html, "lxml")
        download_container = soup.select_one("div.download.mt-2")

        if not download_container:
            return []

        download_links = download_container.select("tr")[1:]
        all_download_links = []

        for download_link in download_links:
            try:
                cells = download_link.select("td")
                if len(cells) >= 2:
                    server = cells[0].text.strip()
                    link_element = download_link.find("a")
                    url = (
                        str(link_element.get("href", "")).strip()
                        if link_element
                        else ""
                    )

                    if server and url:
                        all_download_links.append(
                            {"server": server, "url": url}
                        )
            except Exception:
                continue

        return all_download_links
