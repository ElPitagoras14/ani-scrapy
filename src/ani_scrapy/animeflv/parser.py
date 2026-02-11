"""AnimeFLV parsing logic."""

import json
from bs4 import BeautifulSoup
from typing import List

from ani_scrapy.core.schemas import (
    SearchAnimeInfo,
    AnimeInfo,
    EpisodeInfo,
    RelatedInfo,
    _AnimeType,
    _RelatedType,
)
from ani_scrapy.animeflv.constants import BASE_EPISODE_IMG_URL, ANIME_TYPE_MAP, RELATED_TYPE_MAP


class AnimeFLVParser:
    """Parsing logic for AnimeFLV."""

    @staticmethod
    def parse_search_results(html: str) -> List[SearchAnimeInfo]:
        """Parse search results from HTML."""
        soup = BeautifulSoup(html, "lxml")
        results = []

        for article in soup.select("div.Container ul.ListAnimes li article"):
            try:
                link_element = article.select_one("a")
                if not link_element:
                    continue

                href = str(link_element.get("href", ""))
                if not href:
                    continue

                anime_id = href.split("/")[-1] if href else ""

                title_element = article.select_one("h3")
                title = (
                    str(title_element.text.strip())
                    if title_element
                    else ""
                )

                img_element = article.select_one("figure img")
                poster = (
                    str(img_element.get("src", "")).strip()
                    if img_element
                    else ""
                )

                type_element = article.select_one("span.Type")
                type_text = (
                    type_element.text.strip() if type_element else "Anime"
                )
                anime_type = AnimeFLVParser._map_anime_type(type_text)

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
    def parse_anime_info(
        html: str,
        anime_id: str,
        include_episodes: bool = True,
    ) -> AnimeInfo:
        """Parse detailed anime information."""
        soup = BeautifulSoup(html, "lxml")

        title_element = soup.select_one("h1.Title")
        title = title_element.text.strip() if title_element else ""

        poster_element = soup.select_one("figure img")
        poster = (
            str(poster_element.get("src", "")).strip()
            if poster_element
            else ""
        )

        synopsis_element = soup.select_one("div.Description")
        synopsis = synopsis_element.text.strip() if synopsis_element else ""

        type_element = soup.select_one("span.Type")
        type_text = type_element.text.strip() if type_element else "Anime"
        anime_type = AnimeFLVParser._map_anime_type(type_text)

        genres = []
        genre_elements = soup.select("nav.Nvgnrs a")
        for genre_element in genre_elements:
            genre_text = genre_element.text.strip()
            if genre_text:
                genres.append(genre_text)

        other_titles = []
        titles_element = soup.select_one("div.Titles")
        if titles_element:
            for title_element in titles_element.select("span"):
                title_text = title_element.text.strip()
                if title_text:
                    other_titles.append(title_text)

        rating_element = soup.select_one("span.Rating")
        rating = rating_element.text.strip() if rating_element else None

        related_info = []
        related_elements = soup.select("ul.Related li")
        for related_element in related_elements:
            related_link = related_element.select_one("a")
            if related_link:
                related_id = str(related_link.get("href", "")).split("/")[-1]
                related_title = related_link.text.strip()
                related_type_element = related_element.select_one("span.Type")
                related_type_text = (
                    related_type_element.text.strip()
                    if related_type_element
                    else ""
                )

                related_type = AnimeFLVParser._map_related_type(
                    related_type_text
                )

                if related_id and related_title:
                    related_info.append(
                        RelatedInfo(
                            id=related_id,
                            title=related_title,
                            type=related_type,
                        )
                    )

        episodes: list[EpisodeInfo | None] = []
        if include_episodes:
            episodes = AnimeFLVParser._extract_episodes_from_json(
                soup, anime_id
            )

        next_episode_date = None
        date_element = soup.select_one("span.Date")
        if date_element:
            date_text = date_element.text.strip()
            try:
                from datetime import datetime

                next_episode_date = datetime.strptime(date_text, "%d/%m/%Y")
            except ValueError:
                pass

        is_finished_element = soup.select_one("aside.SidebarA span.fa-tv")
        is_finished = (
            is_finished_element.text.strip() == "Finalizado"
            if is_finished_element
            else len(episodes) > 0
        )

        return AnimeInfo(
            id=anime_id,
            title=title,
            type=anime_type,
            poster=poster,
            synopsis=synopsis,
            rating=rating,
            other_titles=other_titles,
            genres=genres,
            related_info=related_info,
            episodes=list(episodes),
            next_episode_date=next_episode_date,
            is_finished=is_finished,
        )

    @staticmethod
    def extract_episode_data(
        html: str,
    ) -> tuple[list[str], list[list[str]]]:
        """Extract episode data from HTML script tags."""
        soup = BeautifulSoup(html, "lxml")
        info_ids = []
        episodes_data = []

        for script in soup.find_all("script"):
            contents = str(script)

            if "var anime_info = [" in contents:
                try:
                    anime_info = contents.split("var anime_info = ")[1].split(";")[
                        0
                    ]
                    info_ids = json.loads(anime_info)
                except (IndexError, json.JSONDecodeError):
                    continue

            if "var episodes = [" in contents:
                try:
                    data = contents.split("var episodes = ")[1].split(";")[0]
                    episodes_data.extend(json.loads(data))
                except (IndexError, json.JSONDecodeError):
                    continue

        return info_ids, episodes_data

    @staticmethod
    def _extract_episodes_from_json(
        soup: BeautifulSoup, anime_id: str
    ) -> list[EpisodeInfo]:
        """Extract episode information from JSON in script tags."""
        info_ids, episodes_data = AnimeFLVParser.extract_episode_data(
            str(soup)
        )

        if not info_ids or not episodes_data:
            return []

        anime_thumb_id = info_ids[0]
        episodes = []

        for episode_number, _ in reversed(episodes_data):
            number = int(episode_number)
            image_preview = (
                f"{BASE_EPISODE_IMG_URL}/{anime_thumb_id}/{number}/th_3.jpg"
            )
            episodes.append(
                EpisodeInfo(
                    number=number,
                    anime_id=anime_id,
                    image_preview=image_preview,
                )
            )

        return episodes

    @staticmethod
    def _extract_episodes(
        soup: BeautifulSoup, anime_id: str
    ) -> List[EpisodeInfo]:
        """Extract episode information."""
        episodes = []
        episode_elements = soup.select("ul.Episodes li")

        for episode_element in episode_elements:
            try:
                number_element = episode_element.select_one("p")
                if number_element:
                    number_text = number_element.text.strip()
                    number = int(number_text) if number_text.isdigit() else 0
                else:
                    continue

                img_element = episode_element.select_one("img")
                preview = (
                    str(img_element.get("src", "")).strip()
                    if img_element
                    else None
                )

                episodes.append(
                    EpisodeInfo(
                        number=number, anime_id=anime_id, image_preview=preview
                    )
                )

            except Exception:
                continue

        return episodes

    @staticmethod
    def _map_anime_type(site_type: str) -> _AnimeType:
        """Map site-specific anime types to shared enum."""
        return ANIME_TYPE_MAP.get(site_type, _AnimeType.TV)

    @staticmethod
    def _map_related_type(site_type: str) -> _RelatedType:
        """Map site-specific related types to shared enum."""
        return RELATED_TYPE_MAP.get(site_type, _RelatedType.PREQUEL)

    @staticmethod
    def parse_table_download_links(
        html: str, episode_number: int
    ) -> list[dict]:
        """Parse table download links from episode page HTML."""
        soup = BeautifulSoup(html, "lxml")
        rows_list = soup.select("table.RTbl.Dwnl tbody tr")
        rows = []

        for row in rows_list:
            cells = row.select("td")
            if len(cells) >= 4:
                rows.append(
                    {
                        "server": cells[0].text,
                        "url": str(cells[3].select_one("a").get("href")) if cells[3].select_one("a") else None,
                    }
                )

        return rows
