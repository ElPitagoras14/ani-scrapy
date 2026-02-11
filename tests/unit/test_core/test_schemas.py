from __future__ import annotations

from ani_scrapy.core.schemas import (
    AnimeInfo,
    EpisodeInfo,
    SearchAnimeInfo,
    EpisodeDownloadInfo,
    DownloadLinkInfo,
)


def test_schemas_exist() -> None:
    """Test that core schemas can be imported."""
    assert AnimeInfo
    assert EpisodeInfo
    assert SearchAnimeInfo
    assert EpisodeDownloadInfo
    assert DownloadLinkInfo
