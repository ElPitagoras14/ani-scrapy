from __future__ import annotations

import pytest

from ani_scrapy.core.exceptions import ScraperParseError
from ani_scrapy.core.schemas import AnimeType
from ani_scrapy.providers.animeav1.parser import AnimeAV1Parser

MEDIA_HTML = """
<html><body>
<script>
  __sveltekit_x.resolve({ media: { id: 42, title: "Test Anime",
    synopsis: "A synopsis", slug: "test-anime",
    category: { name: "TV Anime" },
    genres: [{ name: "Action" }],
    episodes: [{ number: 1 }, { number: 2 }],
    relations: [] } });
</script>
</body></html>
"""

NO_MEDIA_HTML = "<html><body><h1>Error</h1></body></html>"


def test_parse_anime_info_with_media_data() -> None:
    info = AnimeAV1Parser.parse_anime_info(MEDIA_HTML, "test-anime")

    assert info.title == "Test Anime"
    assert info.type == AnimeType.TV
    assert info.genres == ["Action"]
    assert [ep.episode_number for ep in info.episodes] == [1, 2]


def test_parse_anime_info_without_media_data_raises() -> None:
    with pytest.raises(ScraperParseError) as info:
        AnimeAV1Parser.parse_anime_info(NO_MEDIA_HTML, "missing-anime")

    assert "missing-anime" in str(info.value)
