"""AnimeAV1 parser."""

import re
from datetime import datetime
from bs4 import BeautifulSoup

from ani_scrapy.core.schemas import (
    SearchAnimeInfo,
    AnimeInfo,
    EpisodeInfo,
    RelatedInfo,
    DownloadLinkInfo,
    _AnimeType,
    _RelatedType,
)
from ani_scrapy.providers.animeav1.constants import (
    ANIME_TYPE_MAP,
    RELATED_TYPE_MAP,
    ANIME_COVER_URL,
)


class AnimeAV1Parser:
    """Parser for AnimeAV1."""

    def parse_search_results(self, html: str) -> list[SearchAnimeInfo]:
        """Parse search results from HTML."""
        soup = BeautifulSoup(html, "lxml")
        results = []

        for article in soup.select("article.group\\/item"):
            try:
                link_element = article.select_one("a[href^='/media/']")
                if not link_element:
                    continue

                href = str(link_element.get("href", ""))
                if not href:
                    continue

                anime_id = href.split("/media/")[-1]

                title_element = article.select_one("h3")
                title = title_element.text.strip() if title_element else ""

                img_element = article.select_one("figure img")
                poster = str(img_element.get("src", "")).strip() if img_element else ""

                type_element = article.select_one("div.rounded.bg-line")
                type_text = type_element.text.strip() if type_element else "TV Anime"
                anime_type = ANIME_TYPE_MAP.get(type_text, _AnimeType.TV)

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

    def parse_total_pages(self, html: str) -> int:
        """Parse total pages from pagination HTML."""
        soup = BeautifulSoup(html, "lxml")

        pagination_div = soup.select_one(
            "section.col-span-full div.flex.flex-wrap.gap-2"
        )
        if not pagination_div:
            return 1

        pagination = pagination_div.select("a.btn")
        if len(pagination) >= 2:
            penultimate = pagination[-2]
            page_text = penultimate.text.strip()
            if page_text.isdigit():
                return int(page_text)

        return 1

    def parse_anime_info(
        self, html: str, anime_id: str, include_episodes: bool = True
    ) -> AnimeInfo:
        """Parse anime info from HTML."""
        soup = BeautifulSoup(html, "lxml")

        # Extract media data from script
        media_data = self._extract_media_data(html)
        if not media_data:
            return AnimeInfo(
                id=anime_id,
                title="",
                type=_AnimeType.TV,
                poster="",
                description="",
                is_finished=False,
            )

        # Extract fields from media data
        title = media_data.get("title", "")
        synopsis = media_data.get("synopsis", "")
        category_name = media_data.get("category", {}).get("name", "TV Anime")
        anime_type = ANIME_TYPE_MAP.get(category_name, _AnimeType.TV)

        # Poster from HTML
        img = soup.select_one("div.relative img.aspect-poster")
        if img:
            poster = str(img.get("src", "")).strip()
        else:
            # Fallback to CDN URL using ID
            media_id = media_data.get("id", "")
            poster = f"{ANIME_COVER_URL}/covers/{media_id}.jpg"

        # Genres
        genres = [g.get("name", "") for g in media_data.get("genres", [])]

        # Episodes
        episodes: list[EpisodeInfo | None] = []
        media_id = media_data.get("id", "")
        if include_episodes:
            episodes_data = media_data.get("episodes", [])
            for ep in episodes_data:
                ep_number = ep.get("number", 0)
                image_preview = (
                    f"{ANIME_COVER_URL}/covers/{media_id}/{ep_number}.jpg"
                )
                episodes.append(
                    EpisodeInfo(
                        number=ep_number,
                        anime_id=anime_id,
                        image_preview=image_preview,
                    )
                )

        # Related animes
        related: list[RelatedInfo | None] = []
        relations_data = media_data.get("relations", [])
        for rel in relations_data:
            rel_type = rel.get("type", 1)
            dest = rel.get("destination", {})
            related.append(
                RelatedInfo(
                    id=dest.get("slug", ""),
                    title=dest.get("title", ""),
                    type=RELATED_TYPE_MAP.get(rel_type, _RelatedType.PARALLEL_HISTORY),
                )
            )

        # Is finished - check if endDate exists and is not null
        end_date_value = media_data.get("endDate")
        is_finished = end_date_value is not None and end_date_value != ""

        return AnimeInfo(
            id=anime_id,
            title=title,
            type=anime_type,
            poster=poster,
            description=synopsis,
            is_finished=is_finished,
            genres=genres,
            related_info=related,
            episodes=episodes,
        )

    def _extract_media_data(self, html: str) -> dict | None:
        """Extract media data from script tag."""
        soup = BeautifulSoup(html, "lxml")

        # Find script with __sveltekit_ and media
        for script in soup.find_all("script"):
            content = str(script)
            if "__sveltekit_" in content and "media:" in content:
                script_content = content[8:-9]  # Remove <script> and </script>
                return self._parse_media_script(script_content)

        return None

    def _parse_media_script(self, script_content: str) -> dict | None:
        """Parse media data from script content."""
        # Find media: in this script
        media_pos = script_content.find("media:")
        if media_pos == -1:
            return None

        # Find matching braces
        depth = 0
        i = media_pos + 6  # Skip 'media:'
        obj_start = i

        while i < len(script_content):
            if script_content[i] == "{":
                depth += 1
            elif script_content[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1

        media_str = script_content[obj_start : i + 1]

        # Extract basic fields
        result: dict = {}

        # id
        id_match = re.search(r"(?:id|\"id\"):\s*(\d+)", media_str)
        if id_match:
            result["id"] = int(id_match.group(1))

        # title
        title_match = re.search(r'title:\s*"([^"]+)"', media_str)
        if title_match:
            result["title"] = title_match.group(1)

        # slug - find after synopsis
        synopsis_pos = media_str.find("synopsis:")
        if synopsis_pos != -1:
            slug_pos = media_str.find("slug:", synopsis_pos)
            if slug_pos != -1:
                slug_match = re.search(
                    r'slug:\s*"([^"]+)"', media_str[slug_pos : slug_pos + 30]
                )
                if slug_match:
                    result["slug"] = slug_match.group(1)

        # synopsis
        synopsis_match = re.search(r'synopsis:\s*"([^"]*)"', media_str)
        result["synopsis"] = synopsis_match.group(1) if synopsis_match else ""

        # category
        cat_match = re.search(r'category:\s*\{[^}]*name:\s*"([^"]+)"', media_str)
        result["category"] = (
            {"name": cat_match.group(1)} if cat_match else {"name": "TV Anime"}
        )

        # genres
        if "genres:" in media_str:
            genres_start = media_str.find("genres:")
            genres_section = media_str[genres_start : genres_start + 300]
            genres = re.findall(r'name:\s*"([^"]+)"', genres_section)
            result["genres"] = [{"name": g} for g in genres]
        else:
            result["genres"] = []

        # episodes
        if "episodes:" in media_str:
            episodes_start = media_str.find("episodes:")
            episodes_section = media_str[episodes_start : episodes_start + 50000]
            episodes = re.findall(r"number:\s*(\d+)", episodes_section)
            result["episodes"] = [{"number": int(e)} for e in episodes]
        else:
            result["episodes"] = []

        # relations
        if "relations:" in media_str:
            rels_start = media_str.find("relations:")
            rels_section = media_str[rels_start : rels_start + 800]
            rels = re.findall(
                r'type:\s*(\d+).*?slug:\s*"([^"]+)"[^}]*title:\s*"([^"]+)"',
                rels_section,
            )
            result["relations"] = [
                {"type": int(r[0]), "destination": {"slug": r[1], "title": r[2]}}
                for r in rels
            ]
        else:
            result["relations"] = []

        # endDate (for is_finished) - extract actual value
        end_date_match = re.search(r'endDate:\s*"([^"]*)"', media_str)
        result["endDate"] = end_date_match.group(1) if end_date_match else None

        return result

    def parse_episode_page(self, html: str, anime_id: str) -> list[DownloadLinkInfo]:
        """Parse episode page from HTML and extract download links."""
        download_links: list[DownloadLinkInfo] = []

        soup = BeautifulSoup(html, "lxml")

        # Find script with __sveltekit_ and downloads data
        for script in soup.find_all("script"):
            content = str(script)
            if "__sveltekit_" in content and "downloads:" in content:
                script_content = content[8:-9]  # Remove <script> and </script>
                download_links = self._parse_downloads_from_script(script_content)
                break

        return download_links

    def parse_episode_embeds(self, html: str) -> list[DownloadLinkInfo]:
        """Parse episode page from HTML and extract iframe/embed links."""
        embed_links: list[DownloadLinkInfo] = []

        soup = BeautifulSoup(html, "lxml")

        # Find script with __sveltekit_ and embeds data
        for script in soup.find_all("script"):
            content = str(script)
            if "__sveltekit_" in content and "embeds:" in content:
                script_content = content[8:-9]  # Remove <script> and </script>
                embed_links = self._parse_embeds_from_script(script_content)
                break

        return embed_links

    def _parse_downloads_from_script(
        self, script_content: str
    ) -> list[DownloadLinkInfo]:
        """Parse downloads from script content."""
        download_links: list[DownloadLinkInfo] = []

        # Find downloads section
        downloads_pos = script_content.find("downloads:")
        if downloads_pos == -1:
            return download_links

        # Extract downloads section (find matching braces)
        depth = 0
        i = downloads_pos + 10  # Skip "downloads:"
        obj_start = i

        while i < len(script_content):
            if script_content[i] == "{":
                depth += 1
            elif script_content[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1

        downloads_str = script_content[obj_start : i + 1]

        # Look for SUB section
        sub_pos = downloads_str.find("SUB:")
        if sub_pos == -1:
            return download_links

        # Extract SUB section
        sub_depth = 0
        j = sub_pos + 4
        sub_start = j

        while j < len(downloads_str):
            if downloads_str[j] == "[":
                sub_depth += 1
            elif downloads_str[j] == "]":
                sub_depth -= 1
                if sub_depth == 0:
                    break
            j += 1

        sub_str = downloads_str[sub_start : j + 1]

        # Extract server and url pairs
        # Pattern: server: "X", url: "Y"
        server_matches = re.findall(r'server:\s*"([^"]+)",\s*url:\s*"([^"]+)"', sub_str)

        for server, url in server_matches:
            download_links.append(DownloadLinkInfo(server=server, url=url))

        return download_links

    def _parse_embeds_from_script(self, script_content: str) -> list[DownloadLinkInfo]:
        """Parse embeds from script content."""
        embed_links: list[DownloadLinkInfo] = []

        # Find embeds section
        embeds_pos = script_content.find("embeds:")
        if embeds_pos == -1:
            return embed_links

        # Extract embeds section (find matching braces)
        depth = 0
        i = embeds_pos + 7  # Skip "embeds:"
        obj_start = i

        while i < len(script_content):
            if script_content[i] == "{":
                depth += 1
            elif script_content[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1

        embeds_str = script_content[obj_start : i + 1]

        # Look for SUB section
        sub_pos = embeds_str.find("SUB:")
        if sub_pos == -1:
            return embed_links

        # Extract SUB section
        sub_depth = 0
        j = sub_pos + 4
        sub_start = j

        while j < len(embeds_str):
            if embeds_str[j] == "[":
                sub_depth += 1
            elif embeds_str[j] == "]":
                sub_depth -= 1
                if sub_depth == 0:
                    break
            j += 1

        sub_str = embeds_str[sub_start : j + 1]

        # Extract server and url pairs
        server_matches = re.findall(r'server:\s*"([^"]+)",\s*url:\s*"([^"]+)"', sub_str)

        for server, url in server_matches:
            embed_links.append(DownloadLinkInfo(server=server, url=url))

        return embed_links

    def parse_schedule(self, html: str) -> dict[str, datetime]:
        """Parse schedule from /horario page."""
        schedule: dict[str, datetime] = {}

        soup = BeautifulSoup(html, "lxml")

        # Find script with __sveltekit_ and media array
        for script in soup.find_all("script"):
            content = str(script)
            if "__sveltekit_" in content and "media:" in content:
                script_content = content[8:-9]  # Remove <script> and </script>

                # Find the media array (contains schedule data)
                media_pos = script_content.find("media:")
                if media_pos == -1:
                    continue

                # Extract media array
                depth = 0
                i = media_pos + 6  # Skip 'media:'
                obj_start = i

                while i < len(script_content):
                    if script_content[i] == "[":
                        depth += 1
                    elif script_content[i] == "]":
                        depth -= 1
                        if depth == 0:
                            break
                    i += 1

                media_str = script_content[obj_start : i + 1]

                # Extract slug and latestEpisode for each anime
                # Pattern: slug: "...", latestEpisode: { ..., createdAt: "..." }
                item_pattern = (
                    r'slug:\s*"([^"]+)".*?latestEpisode:.*?createdAt:\s*"([^"]+)"'
                )
                matches = re.findall(item_pattern, media_str, re.DOTALL)

                for slug, created_at in matches:
                    try:
                        # Parse the datetime
                        dt = datetime.fromisoformat(created_at.replace("+00:00", ""))
                        schedule[slug] = dt
                    except (ValueError, OSError):
                        continue

                break

        return schedule
