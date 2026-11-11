## 1. Core object

- [x] 1.1 Write a failing test in `tests/unit/test_core/test_servers.py`: `SUPPORTED_SERVERS` is importable from `ani_scrapy` and `ani_scrapy.core.constants`, its keys are exactly `animeflv`, `jkanime`, `animeav1`, and `"MP4Upload"` is in the `animeav1` list. Verify it fails.
- [x] 1.2 Create `src/ani_scrapy/core/constants/servers.py`, re-export it from `core/constants/__init__.py` and `ani_scrapy/__init__.py` (`__all__`). Verify the 1.1 test passes.

## 2. Providers

- [x] 2.1 Remove `SUPPORTED_SERVERS` from the three `providers/<site>/constants.py`; point the AnimeFLV and JKAnime scrapers to `SUPPORTED_SERVERS["animeflv"]` / `["jkanime"]` (validation and log unchanged). Verify with `rg -n "SUPPORTED_SERVERS" src` that no per-provider definition or import remains.
- [x] 2.2 Add scraper tests (mocked, no network) that an unsupported server returns `None` for JKAnime and AnimeFLV, and that `from ani_scrapy.providers.jkanime.constants import SUPPORTED_SERVERS` raises `ImportError`. Verify the unit suite passes.

## 3. Consumers in the repo

- [x] 3.1 Update `tests/integration/test_animeav1_live.py` and `test_jkanime_live.py` to `from ani_scrapy import SUPPORTED_SERVERS` and the platform key. Verify with `uv run pytest -m live`.
- [x] 3.2 Update `examples/03_download_links.py` (drop the aliased imports) and verify with `rg -n "_SUPPORTED_SERVERS|providers\..*constants" examples` that no old import remains.
- [x] 3.3 Update `docs/01-scrapers.md` and `.claude/skills/ani-scrapy/SKILL.md` (imports at line ~38-45, the filter snippets and the "Forgetting to filter" pitfall) to the new dict; check the `ani-scrapy-dev` "Public surface sync" row. Verify with `rg -n "providers\.[a-z0-9]+\.constants" docs .claude README.md`.

## 4. Release prep

- [x] 4.1 Add a `Breaking changes` item with Before/After code (old per-provider import vs `from ani_scrapy import SUPPORTED_SERVERS`) to the `## 0.10.0` entry of `CHANGELOG.md`, shared with the MP4Upload change. Verify the entry has both `Breaking changes` and `Added`.
- [x] 4.2 Run `uv run pytest`, `uv run ruff check src tests`, `uv run ruff format --check src tests` and `openspec validate supported-servers-by-platform --strict`; verify all pass.
- [x] 4.3 Confirm `version` stays 0.10.0 in `pyproject.toml` and `uv.lock` (set by `animeav1-mp4upload-v0-10-0`) and `uv build --out-dir <scratch dir>` succeeds. Commit `pyproject.toml` and `uv.lock` last, only when asked to commit.
