## Why

`SUPPORTED_SERVERS` is a flat list repeated in each provider's `constants.py`, and consumers import three differently aliased names (`JKANIME_SUPPORTED_SERVERS`, `ANIMEAV1_SUPPORTED_SERVERS`, ...) to see what is supported. A single object keyed by platform shows every supported server at a glance and removes the aliasing.

## What Changes

- **BREAKING**: a single `SUPPORTED_SERVERS` dict replaces the per-provider constants: `{"animeflv": ["SW", "YourUpload"], "jkanime": ["Streamwish", "Mediafire"], "animeav1": ["PDrain", "UPNShare", "MP4Upload"]}`. It lives in `ani_scrapy.core.constants` and is exported from `ani_scrapy`.
- The per-provider `SUPPORTED_SERVERS` in `providers/<site>/constants.py` are removed, with no alias (decided with the maintainer). Imports from those modules stop working.
- The AnimeFLV and JKAnime scrapers validate against their entry in the new dict; behavior is unchanged.
- Live tests, `examples/03_download_links.py`, docs and the usage skill use the new dict. `CHANGELOG.md` gets a `Breaking changes` item with Before/After code, in the same 0.10.0 entry as the MP4Upload change.

Depends on `animeav1-mp4upload-v0-10-0` (not committed or archived yet), which adds `MP4Upload` to the AnimeAV1 list. This change keeps that value and ships in the same 0.10.0 release.

Non-goals: changing which servers are supported; making the values immutable; validating servers inside `AnimeAV1Scraper` (it still dispatches by server name).

## Capabilities

### New Capabilities
- `supported-servers`: the public `SUPPORTED_SERVERS` object that maps each platform to the servers it can resolve.

### Modified Capabilities
None.

## Impact

- Code: new `src/ani_scrapy/core/constants/servers.py`; re-exports in `core/constants/__init__.py` and `ani_scrapy/__init__.py`; removal of the constant from the three `providers/<site>/constants.py`; `animeflv/scraper.py` and `jkanime/scraper.py`.
- Tests: new unit test for the object; `tests/integration/test_{animeav1,jkanime}_live.py`.
- Docs: `examples/03_download_links.py`, `docs/01-scrapers.md`, `.claude/skills/ani-scrapy/SKILL.md`, `CHANGELOG.md`; the `ani-scrapy-dev` skill row for `SUPPORTED_SERVERS` is checked.
- Release: `pyproject.toml` and `uv.lock` stay at 0.10.0 (set by `animeav1-mp4upload-v0-10-0`; this breaking change shares that minor release).
- Consumers that import the per-provider constants must switch to the new dict.
