## Why

`AnimeAV1Scraper.get_file_download_link` resolves no server today (issue #30): UPNShare times out waiting for a button that no longer exists, PDrain no longer appears, and the table links only offer servers the library does not support (Mega, 1Fichier, MP4Upload, StreamTape). No AnimeAV1 episode can be downloaded through the library. MP4Upload appears in the table links and, checked live on 2026-11-11 with `black-clover` episode 1, resolves to a direct `.mp4` with two plain HTTP requests and no browser.

## What Changes

- `get_file_download_link` resolves AnimeAV1 table links whose server is `MP4Upload` (URL `https://www.mp4upload.com/<file_id>`) to a direct `.mp4` URL, over HTTP only: it submits the site's free-download form and returns the redirect target. The 30-second countdown on the page is client-side only and is not waited for.
- `MP4Upload` is added to AnimeAV1's `SUPPORTED_SERVERS`.
- MP4Upload iframe links (`https://www.mp4upload.com/embed-<file_id>.html`, from `get_iframe_download_links`) are not resolved: they return `None` with a warning. Resolution goes through the table link.
- A file that no longer exists on MP4Upload returns `None` with a warning; HTTP failures raise the usual `ScraperError` subclasses.
- The returned URL only downloads when the request sends `Referer: https://www.mp4upload.com/` (without it the file host answers 403). This is documented for consumers; the return type does not change.
- The live test `test_get_file_download_link` for AnimeAV1 loses its `xfail(strict=True)` marker (it would otherwise fail as XPASS), and a live test resolves the MP4Upload link of `black-clover` episode 1.
- Release 0.10.0 (new supported server).

Non-goals: fixing UPNShare or removing PDrain/UPNShare from `SUPPORTED_SERVERS`; supporting Mega, 1Fichier or StreamTape; using the Playwright DOM bypass from the local notes (not needed, the flow is plain HTTP).

## Capabilities

### New Capabilities
- `animeav1-file-download`: how AnimeAV1 resolves a download link to a direct file URL; this change adds the MP4Upload server.

### Modified Capabilities
None. The new HTTP call follows the existing `scraper-errors` status mapping unchanged.

## Impact

- Code: `src/ani_scrapy/providers/animeav1/{constants,parser,scraper}.py`; `src/ani_scrapy/core/http.py` gains a POST that returns the redirect `Location` instead of following it.
- Tests: unit tests for the new parser helper, the adapter method and the scraper branch; `tests/integration/test_animeav1_live.py`.
- Docs: `docs/01-scrapers.md` (Supported Servers, AnimeAV1 notes), usage skill `.claude/skills/ani-scrapy/SKILL.md` (server table, description, Referer note), `CHANGELOG.md`.
- Release: `pyproject.toml` and `uv.lock` to 0.10.0.
- Consumers that download the returned URL must send the MP4Upload `Referer` header.
