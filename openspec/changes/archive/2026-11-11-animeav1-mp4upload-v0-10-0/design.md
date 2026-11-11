## Context

See proposal.md for motivation. Requirements are in `specs/animeav1-file-download/spec.md`.

`AnimeAV1Scraper.get_file_download_link` dispatches by `server` to private resolvers (`_get_pdrawin_download_link`, `_get_upnshare_download_link`). The scraper has one `AsyncHttpAdapter` bound to `https://animeav1.com`; the adapter only returns response text, follows redirects (aiohttp default) and resolves endpoints relative to its `base_url`.

MP4Upload was probed live on 2026-11-11 (`black-clover` episode 1, table URL `https://www.mp4upload.com/fevqfos5cs7q`):

- The page is a standard XFileSharing form: `op=download1` → page with a second form `op=download2` → `302 Found` whose `Location` is the file (`https://a4.mp4upload.com:183/d/<token>/897_1_SUB.mp4`).
- A single `POST` with `op=download2&id=<file_id>&method_free=Free Download` to `https://www.mp4upload.com/<file_id>` already returns that `302`, with no cookies, no `Referer`, no prior `download1` and no wait. The countdown in `countdown.js` is client-side only.
- A missing file answers `200` with a "No such file" page and no redirect.
- The file URL answers `403` without a `Referer`, and `200` with `Referer: https://www.mp4upload.com/` (User-Agent does not matter); the first bytes are a valid MP4 (`ftypisom`).

## Goals / Non-Goals

**Goals:**
- Resolve MP4Upload table links over HTTP only, never downloading the file body.
- Keep parsing (file id from URL) in the parser and network flow in the scraper.

**Non-Goals:**
- A general redirect-following or header-returning API for downloads.
- Retrying or falling back between servers inside `get_file_download_link`.

## Decisions

### D1 - One `POST op=download2` instead of the Playwright DOM bypass

The probe shows the server does not enforce the countdown, so the browser flow from `local/mp4upload.md` (load page, edit DOM, click, close ad tabs) only adds Chromium, latency and ad-popup handling. Skipping the `download1` step saves a request; the request still sends the full `download2` field set the form submits (`op`, `id`, `rand=""`, `referer=""`, `method_free="Free Download"`, `method_premium=""`) so it matches what a browser posts. Alternative considered: `GET` the page and parse the hidden fields first. Rejected for now because the fields are constant apart from `id`; if MP4Upload starts requiring them, the live test fails and this becomes the fix.

### D2 - Adapter method that returns the redirect `Location`

`AsyncHttpAdapter` gains `post_redirect_location(endpoint, data) -> str | None`: it posts with `allow_redirects=False`, applies `raise_for_status_code` and the same timeout/`ClientError` mapping as `_request` (shared, not duplicated), and returns the `Location` header of a 3xx response or `None` otherwise. Following the redirect is not an option: it would download the whole video (about 160 MB in the probe). Using `aiohttp` directly in the scraper was rejected because it would bypass the status-to-exception mapping in `scraper-errors`.

### D3 - Second adapter instance for MP4Upload

The scraper creates `AsyncHttpAdapter(base_url=MP4UPLOAD_URL)` alongside the AnimeAV1 one and closes it in `aclose`, so the endpoint is just the file id and `build_url` does not need to handle absolute URLs. `MP4UPLOAD_URL = "https://www.mp4upload.com"` goes in `constants.py`, and `"MP4Upload"` is appended to `SUPPORTED_SERVERS`.

### D4 - File id parsing in the parser, table links only

`AnimeAV1Parser.parse_mp4upload_file_id(url) -> str | None` matches only the table form `https://(www.)mp4upload.com/<alphanumeric id>` and returns `None` for anything else, including `embed-<id>.html`. The scraper logs a warning and returns `None` without any request when it gets `None`. Alternative considered: also map the embed form to its id (one more regex branch), which would make the iframe link resolve too. Not done because the request scopes MP4Upload to the table link; it is a one-line follow-up if wanted.

### D5 - Error behavior

No `Location` (missing file) → `None` plus a warning, matching how unsupported or unresolvable links already return `None`. HTTP errors propagate as `ScraperError` subclasses from the adapter, per `CLAUDE.md` and `scraper-errors`. This differs from the UPNShare resolver, which swallows every exception; that resolver is not touched. A relative `Location` is joined to `MP4UPLOAD_URL` (only absolute ones were observed).

### D6 - `Referer` is documented, not returned

`get_file_download_link` keeps returning `str | None`. Returning headers would change the public API for every provider; downloading inside the library is out of scope. The requirement goes in `docs/01-scrapers.md`, the usage skill and `CHANGELOG.md`, and a live test checks it so the docs cannot drift.

### D7 - Version 0.10.0

A new supported server is a feature (minor per the `ani-scrapy-dev` skill), even though it also addresses issue #30.

## Risks / Trade-offs

- [The file URL carries a token that may expire or be bound to the requesting IP] → Docs say to resolve right before downloading, from the same machine that downloads.
- [The file host uses a non-standard port (`:183`)] → Nothing to do in the library; mentioned in the docs so consumers behind restrictive egress know.
- [MP4Upload adds server-side countdown checks, a captcha or required hidden fields] → The live test for `black-clover` episode 1 fails; D1 names the first fallback (parse the form first).
- [AnimeAV1 removes MP4Upload from an episode] → `get_file_download_link` is only called for links present in the table; the live test would need another episode.
- [`test_get_file_download_link` also tries UPNShare through the browser, which times out] → Unchanged behavior; it returns `None` and the test passes through `any(...)` on the MP4Upload result.

## Migration Plan

Additive. Consumers that filter by `SUPPORTED_SERVERS` start receiving MP4Upload links and must send the `Referer` header when downloading. Rollback is reverting the release; no data or config changes.
