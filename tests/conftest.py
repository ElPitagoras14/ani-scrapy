from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures" / "html"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.fixture
def animeflv_search_html(fixtures_dir: Path) -> str:
    return _read_text(fixtures_dir / "animeflv_search.html")


@pytest.fixture
def animeflv_anime_html(fixtures_dir: Path) -> str:
    return _read_text(fixtures_dir / "animeflv_anime.html")


@pytest.fixture
def jkanime_search_html(fixtures_dir: Path) -> str:
    return _read_text(fixtures_dir / "jkanime_search.html")


@pytest.fixture
def jkanime_anime_html(fixtures_dir: Path) -> str:
    return _read_text(fixtures_dir / "jkanime_anime.html")
