"""AnimeAV1 parser."""

import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

from ani_scrapy.core.exceptions import ScraperParseError
from ani_scrapy.core.schemas import (
    SearchAnimeInfo,
    AnimeInfo,
    EpisodeInfo,
    RelatedInfo,
    DownloadLinkInfo,
    AnimeType,
    RelatedType,
)
from ani_scrapy.providers.animeav1.constants import (
    ANIME_TYPE_MAP,
    RELATED_TYPE_MAP,
    ANIME_COVER_URL,
)

STRING_PATTERN = r'"(?:[^"\\]+|\\.)*"'
BRACE_OR_STRING_PATTERN = re.compile(STRING_PATTERN + r"|[{}]")
MEDIA_KEY_PATTERN = re.compile(STRING_PATTERN + r"|([A-Za-z_$][\w$]*)(?=\s*:)")


def _quote_key(match: re.Match) -> str:
    key = match.group(1)
    return f'"{key}"' if key else match.group()


class AnimeAV1Parser:
    """Parser for AnimeAV1."""

    @staticmethod
    def parse_search_results(html: str) -> list[SearchAnimeInfo]:
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
                anime_type = ANIME_TYPE_MAP.get(type_text, AnimeType.TV)

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
    def parse_total_pages(html: str) -> int:
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

    @staticmethod
    def parse_anime_info(
        html: str, anime_id: str, include_episodes: bool = True
    ) -> AnimeInfo:
        """Parse anime info from HTML.

        Raises:
            ScraperParseError: If the page has no media data or it is invalid.
        """
        soup = BeautifulSoup(html, "lxml")

        # Extract media data from script
        try:
            media_data = AnimeAV1Parser._extract_media_data(html)
        except ScraperParseError as e:
            raise ScraperParseError(
                f"Invalid media data for anime '{anime_id}': {e}"
            ) from e
        if not media_data:
            raise ScraperParseError(
                f"No media data found for anime '{anime_id}'; possible layout "
                "change, error page served with HTTP 200 or anti-bot challenge"
            )

        # Extract fields from media data
        title = media_data.get("title", "")
        synopsis = media_data.get("synopsis", "")
        category_name = (media_data.get("category") or {}).get("name", "TV Anime")
        anime_type = ANIME_TYPE_MAP.get(category_name, AnimeType.TV)

        # Poster from HTML
        img = soup.select_one("div.relative img.aspect-poster")
        if img:
            poster = str(img.get("src", "")).strip()
        else:
            # Fallback to CDN URL using ID
            media_id = media_data.get("id", "")
            poster = f"{ANIME_COVER_URL}/covers/{media_id}.jpg"

        # Genres
        genres = [g.get("name", "") for g in media_data.get("genres") or []]

        # Episodes
        episodes: list[EpisodeInfo] = []
        media_id = media_data.get("id", "")
        if include_episodes:
            episodes_data = media_data.get("episodes") or []
            for ep in episodes_data:
                ep_number = ep.get("number", 0)
                image_preview = f"{ANIME_COVER_URL}/covers/{media_id}/{ep_number}.jpg"
                episodes.append(
                    EpisodeInfo(
                        episode_number=ep_number,
                        anime_id=anime_id,
                        image_preview=image_preview,
                    )
                )

        # Related animes
        related: list[RelatedInfo] = []
        relations_data = media_data.get("relations") or []
        for rel in relations_data:
            rel_type = rel.get("type", 1)
            dest = rel.get("destination") or {}
            related.append(
                RelatedInfo(
                    id=dest.get("slug", ""),
                    title=dest.get("title", ""),
                    type=RELATED_TYPE_MAP.get(rel_type, RelatedType.PARALLEL_HISTORY),
                )
            )

        # Is finished - parse from HTML body div
        is_finished = AnimeAV1Parser._parse_finished_status_from_html(html)

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

    @staticmethod
    def _extract_media_data(html: str) -> dict | None:
        """Extract media data from script tag."""
        soup = BeautifulSoup(html, "lxml")

        # Find script with __sveltekit_ and media
        for script in soup.find_all("script"):
            content = str(script)
            if "__sveltekit_" in content and "media:" in content:
                script_content = content[8:-9]  # Remove <script> and </script>
                return AnimeAV1Parser._parse_media_script(script_content)

        return None

    @staticmethod
    def _parse_media_script(script_content: str) -> dict | None:
        """Parse the media object from script content.

        Raises:
            ScraperParseError: If the media object is unterminated or invalid.
        """
        media_pos = script_content.find("media:")
        if media_pos == -1:
            return None

        media_str = AnimeAV1Parser._extract_object(script_content, media_pos + 6)
        if media_str is None:
            raise ScraperParseError("Unterminated media object")

        try:
            return json.loads(MEDIA_KEY_PATTERN.sub(_quote_key, media_str))
        except json.JSONDecodeError as e:
            raise ScraperParseError(f"Invalid media object: {e}") from e

    @staticmethod
    def _extract_object(text: str, start: int) -> str | None:
        """Return the first balanced {...} at or after start, skipping strings."""
        depth = 0
        obj_start = -1
        for match in BRACE_OR_STRING_PATTERN.finditer(text, start):
            token = match.group()
            if token == "{":
                if depth == 0:
                    obj_start = match.start()
                depth += 1
            elif token == "}" and depth > 0:
                depth -= 1
                if depth == 0:
                    return text[obj_start : match.end()]
        return None

    @staticmethod
    def _parse_finished_status_from_html(html: str) -> bool:
        """Parse is_finished from HTML body div."""
        soup = BeautifulSoup(html, "lxml")

        # Find div with status classes
        status_div = soup.select_one("div.flex.flex-wrap.items-center.gap-2.text-sm")
        if not status_div:
            return False

        # Get all span children
        spans = status_div.find_all("span")
        if not spans:
            return False

        # Check last span text
        last_span_text = spans[-1].text.strip()

        if last_span_text == "Finalizado":
            return True
        elif last_span_text == "En emisión":
            return False

        return False

    @staticmethod
    def parse_episode_page(html: str, anime_id: str) -> list[DownloadLinkInfo]:
        """Parse episode page from HTML and extract download links."""
        download_links: list[DownloadLinkInfo] = []

        soup = BeautifulSoup(html, "lxml")

        # Find script with __sveltekit_ and downloads data
        for script in soup.find_all("script"):
            content = str(script)
            if "__sveltekit_" in content and "downloads:" in content:
                script_content = content[8:-9]  # Remove <script> and </script>
                download_links = AnimeAV1Parser._parse_downloads_from_script(script_content)
                break

        return download_links

    @staticmethod
    def parse_episode_embeds(html: str) -> list[DownloadLinkInfo]:
        """Parse episode page from HTML and extract iframe/embed links."""
        embed_links: list[DownloadLinkInfo] = []

        soup = BeautifulSoup(html, "lxml")

        # Find script with __sveltekit_ and embeds data
        for script in soup.find_all("script"):
            content = str(script)
            if "__sveltekit_" in content and "embeds:" in content:
                script_content = content[8:-9]  # Remove <script> and </script>
                embed_links = AnimeAV1Parser._parse_embeds_from_script(script_content)
                break

        return embed_links

    @staticmethod
    def _parse_downloads_from_script(
        script_content: str,
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

    @staticmethod
    def _parse_embeds_from_script(script_content: str) -> list[DownloadLinkInfo]:
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

    @staticmethod
    def parse_schedule(html: str) -> dict[str, datetime]:
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
