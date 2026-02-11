from __future__ import annotations

from ani_scrapy.animeflv.parser import AnimeFLVParser
from ani_scrapy.core.schemas import _AnimeType, _RelatedType


def test_parse_search_results(animeflv_search_html: str) -> None:
    results = AnimeFLVParser.parse_search_results(animeflv_search_html)
    assert len(results) == 12
    assert results[0].id == "naruto"
    assert results[0].title == "Naruto"
    assert results[0].type == _AnimeType.TV
    assert "covers/2.jpg" in results[0].poster
    assert results[1].id == "naruto-shippuden-road-to-ninja"
    assert results[1].title == "Naruto Shippuden: Road to Ninja"
    assert results[1].type == _AnimeType.MOVIE
    assert results[2].id == "naruto-shippuden-hd"
    assert results[2].title == "Naruto Shippuden"
    assert results[2].type == _AnimeType.TV
    assert results[3].id == "boruto-naruto-the-movie-naruto-ga-hokage-ni-natta-hi"
    assert results[3].type == _AnimeType.OVA
    assert results[4].id == "naruto-shippuden-blood-prison"
    assert results[4].type == _AnimeType.MOVIE


def test_parse_anime_info(animeflv_anime_html: str) -> None:
    anime = AnimeFLVParser.parse_anime_info(animeflv_anime_html, "one-punch-man-3")
    assert anime.id == "one-punch-man-3"
    assert anime.title == "One Punch Man 3"
    assert anime.type == _AnimeType.TV
    assert anime.genres == ["Acción", "Comedia"]
    assert anime.other_titles == ["ワンパンマン"]
    assert anime.related_info
    assert anime.related_info[0].type == _RelatedType.PREQUEL
    assert anime.episodes
    assert len(anime.episodes) == 3
    assert anime.episodes[0].number == 3
    assert anime.episodes[1].number == 2
    assert anime.episodes[2].number == 1
    assert "screenshots/12345" in anime.episodes[0].image_preview
