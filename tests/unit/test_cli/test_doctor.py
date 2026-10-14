from __future__ import annotations

from typer.testing import CliRunner

from ani_scrapy.cli.doctor import AniScrapyDoctor
from ani_scrapy.cli.main import app


def test_connectivity_sites_exclude_animeflv() -> None:
    assert set(AniScrapyDoctor.CONNECTIVITY_SITES) == {"jkanime.net", "animeav1.com"}


def test_doctor_help_works() -> None:
    result = CliRunner().invoke(app, ["doctor", "--help"])

    assert result.exit_code == 0
