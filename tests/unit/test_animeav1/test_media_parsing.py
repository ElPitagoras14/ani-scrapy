from __future__ import annotations

import pytest

from ani_scrapy.core.exceptions import ScraperParseError
from ani_scrapy.providers.animeav1.parser import AnimeAV1Parser


def _page(media: str) -> str:
    return (
        "<html><body><script>"
        f"__sveltekit_x.resolve({{ media: {media} }});"
        "</script></body></html>"
    )


def _media(
    title: str = '"Test Anime"',
    synopsis: str = '"A synopsis"',
    genres: str = "[]",
    episodes: str = "[]",
    relations: str = "[]",
) -> str:
    return (
        f'{{ id: 42, title: {title}, synopsis: {synopsis}, slug: "test-anime",'
        f' category: {{ name: "TV Anime" }}, genres: {genres},'
        f" episodes: {episodes}, relations: {relations} }}"
    )


def _relation(index: int, title: str | None = None) -> str:
    title = title or f'"Related Anime Number {index}"'
    return (
        f"{{ type: 1, destination: {{ id: {index}, "
        f'slug: "related-anime-{index}", title: {title} }} }}'
    )


def _parse(media: str, include_episodes: bool = True):
    return AnimeAV1Parser.parse_anime_info(
        _page(media), "test-anime", include_episodes=include_episodes
    )


def test_many_relations_are_all_returned_in_order() -> None:
    relations = ", ".join(_relation(i) for i in range(1, 31))
    assert len(relations) > 800

    info = _parse(_media(relations=f"[{relations}]"))

    assert [r.id for r in info.related_info] == [
        f"related-anime-{i}" for i in range(1, 31)
    ]


def test_many_genres_are_all_returned() -> None:
    names = [f"Genre number {i} with a longer name" for i in range(12)]
    genres = ", ".join(f'{{ id: {i}, name: "{n}" }}' for i, n in enumerate(names))
    assert len(genres) > 300

    info = _parse(_media(genres=f"[{genres}]"))

    assert info.genres == names


def test_very_long_episode_list_is_complete() -> None:
    episodes = ", ".join(
        f'{{ number: {i}, title: "Episode number {i} with a long title" }}'
        for i in range(1, 3001)
    )
    assert len(episodes) > 50000

    info = _parse(_media(episodes=f"[{episodes}]"))

    assert len(info.episodes) == 3000
    assert info.episodes[-1].episode_number == 3000


def test_episodes_not_requested_are_not_returned() -> None:
    info = _parse(_media(episodes="[{ number: 1 }]"), include_episodes=False)

    assert info.episodes == []


def test_escaped_quotes_in_titles_are_decoded() -> None:
    relation = _relation(1, title=r'"Related \"Quoted\" Title"')

    info = _parse(
        _media(title=r'"Kashita \"Revo Barai\" de Choushuu"', relations=f"[{relation}]")
    )

    assert info.title == 'Kashita "Revo Barai" de Choushuu'
    assert info.related_info[0].title == 'Related "Quoted" Title'


def test_escaped_line_breaks_in_synopsis_become_real_line_breaks() -> None:
    info = _parse(_media(synopsis=r'"First paragraph.\n\nSecond paragraph."'))

    assert info.description == "First paragraph.\n\nSecond paragraph."
    assert "\\n" not in info.description


def test_structural_characters_inside_text_do_not_break_parsing() -> None:
    tricky = r'"Braces {a} }{ brackets [x] ] [ commas, colons: and \"quotes\" {"'
    relations = f"[{_relation(1)}, {_relation(2)}]"
    episodes = "[{ number: 1 }, { number: 2 }]"
    genres = '[{ name: "Action" }]'

    info = _parse(
        _media(
            title=tricky,
            synopsis=tricky,
            genres=genres,
            episodes=episodes,
            relations=relations,
        )
    )

    assert info.title == 'Braces {a} }{ brackets [x] ] [ commas, colons: and "quotes" {'
    assert info.genres == ["Action"]
    assert [e.episode_number for e in info.episodes] == [1, 2]
    assert [r.id for r in info.related_info] == ["related-anime-1", "related-anime-2"]


def test_null_collections_are_treated_as_empty() -> None:
    media = (
        '{ id: 42, title: "Test Anime", synopsis: "S", category: null,'
        " genres: null, episodes: null, relations: null }"
    )

    info = _parse(media)

    assert info.genres == []
    assert info.episodes == []
    assert info.related_info == []


@pytest.mark.parametrize(
    "media",
    [
        '{ id: 42, title: "Test Anime", startDate: undefined }',
        '{ id: 42, title: "Test Anime", releaseDate: new Date("2026-01-01") }',
    ],
)
def test_unreadable_media_data_raises_parse_error_with_anime_id(media: str) -> None:
    with pytest.raises(ScraperParseError) as info:
        _parse(media)

    assert "test-anime" in str(info.value)


def test_unterminated_media_object_raises_parse_error_with_anime_id() -> None:
    html = (
        "<html><body><script>"
        '__sveltekit_x.resolve({ media: { id: 42, title: "Test Anime", genres: ['
        "</script></body></html>"
    )

    with pytest.raises(ScraperParseError) as info:
        AnimeAV1Parser.parse_anime_info(html, "test-anime")

    assert "test-anime" in str(info.value)
