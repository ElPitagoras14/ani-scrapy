## 1. HTTP adapter

- [x] 1.1 Write failing tests in `tests/unit/test_core/test_http.py` (with `aioresponses`) for `AsyncHttpAdapter.post_redirect_location`: a `302` returns its `Location`; a `200` without redirect returns `None`; the redirect is not followed (the target URL is never requested); 403/404/503, connection errors and timeouts raise the same exceptions as `get`. Verify they fail.
- [x] 1.2 Implement `post_redirect_location(endpoint, data) -> str | None` in `src/ani_scrapy/core/http.py` with `allow_redirects=False`, sharing the status, timeout and `ClientError` mapping with `_request` instead of duplicating it. Verify the 1.1 tests and the existing adapter tests pass.

## 2. Parser and constants

- [x] 2.1 Write failing tests in `tests/unit/test_animeav1/test_parser.py` for `AnimeAV1Parser.parse_mp4upload_file_id`: `https://www.mp4upload.com/fevqfos5cs7q` and `https://mp4upload.com/fevqfos5cs7q` return `fevqfos5cs7q`; `https://www.mp4upload.com/embed-fevqfos5cs7q.html`, another host and an empty path return `None`. Verify they fail.
- [x] 2.2 Implement `parse_mp4upload_file_id` in `src/ani_scrapy/providers/animeav1/parser.py`; add `MP4UPLOAD_URL` and append `"MP4Upload"` to `SUPPORTED_SERVERS` in `constants.py`. Verify the 2.1 tests pass.

## 3. Scraper

- [x] 3.1 Write failing tests in `tests/unit/test_animeav1/test_scraper.py`, mocking the MP4Upload adapter's `post_redirect_location` with `AsyncMock`: a table link returns the mocked `Location` and the POST carries `op=download2`, `id=<file_id>` and `method_free`; a missing `Location` returns `None`; an embed link returns `None` without calling the adapter; a `ScraperBlockedError` from the adapter propagates; no browser is created (`_get_browser` not called). Verify they fail.
- [x] 3.2 In `src/ani_scrapy/providers/animeav1/scraper.py`, create the MP4Upload `AsyncHttpAdapter` in `__init__`, close it in `aclose`, add the `MP4Upload` branch to `get_file_download_link` and a `_get_mp4upload_download_link` resolver that logs a warning and returns `None` for unparsable URLs or no `Location`, and joins a relative `Location` to `MP4UPLOAD_URL`. Verify the 3.1 tests and the whole unit suite pass.

## 4. Live tests

- [x] 4.1 In `tests/integration/test_animeav1_live.py`, remove the `xfail(strict=True)` marker from `test_get_file_download_link` and add a test that resolves the `MP4Upload` table link of `black-clover` episode 1, asserts an `https://` URL, and requests its first bytes with `Referer: https://www.mp4upload.com/` expecting HTTP 200 or 206. Verify with `uv run pytest -m live tests/integration/test_animeav1_live.py` that every test passes (no XPASS, no xfail).
- [x] 4.2 Run the full `uv run pytest -m live` and verify JKAnime is unaffected.

## 5. Docs and usage skill

- [x] 5.1 Update `docs/01-scrapers.md`: add an MP4Upload row to "Supported Servers" (AnimeAV1 only) and, in the AnimeAV1 notes, state that MP4Upload resolves from table links over HTTP, that iframe links are not resolved, and that downloading the URL needs `Referer: https://www.mp4upload.com/` and should happen right after resolving. Verify by reading the section.
- [x] 5.2 Update `.claude/skills/ani-scrapy/SKILL.md`: MP4Upload in the frontmatter `description`, the supported servers table, a short note with the `Referer` requirement and the table-link-only rule, and the browser-requirements row for `get_file_download_link`. Verify with `rg -n "MP4Upload|Referer" .claude/skills/ani-scrapy/SKILL.md docs/01-scrapers.md`.

## 6. Release prep

- [x] 6.1 Add a `## 0.10.0` entry to `CHANGELOG.md` with an `Added` item for MP4Upload on AnimeAV1 (written from the user's side: AnimeAV1 episodes can be downloaded again through MP4Upload table links, and the download needs the `Referer` header with a short example), referencing issue #30. Verify the entry is on top.
- [x] 6.2 Run `uv run pytest`, `uv run ruff check src tests`, `uv run ruff format --check src tests` and `openspec validate animeav1-mp4upload-v0-10-0 --strict`; verify all pass.
- [x] 6.3 Bump `version` to 0.10.0 in `pyproject.toml`, run `uv lock` and verify `git diff uv.lock` only changes the `ani-scrapy` version line; run `uv build --out-dir <scratchpad>` and verify it succeeds. Commit `pyproject.toml` and `uv.lock` last, only when asked to commit. Do not touch the existing `.gitignore` change or the `.ignore` deletion in the working tree.
