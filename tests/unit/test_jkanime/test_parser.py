from __future__ import annotations

from ani_scrapy.jkanime.parser import JKAnimeParser
from ani_scrapy.core.schemas import _AnimeType


def test_parse_search_results(jkanime_search_html: str) -> None:
    results = JKAnimeParser.parse_search_results(jkanime_search_html)
    assert len(results) == 1
    assert results[0].id == "steins-gate"
    assert results[0].title == "Steins;Gate"
    assert results[0].type == _AnimeType.TV


def test_parse_anime_info(jkanime_anime_html: str) -> None:
    anime = JKAnimeParser.parse_anime_info(jkanime_anime_html, "steins-gate")
    assert anime.id == "steins-gate"
    assert anime.title == "Steins;Gate"
    assert anime.type == _AnimeType.TV
    assert anime.genres == ["Ciencia ficción", "Suspenso"]
    assert anime.is_finished is False
