## Context

See proposal.md for motivation. Current state of `_parse_media_script` in `providers/animeav1/parser.py`:

- It finds the `media:` object by brace counting that ignores string contents, then pulls fields out with regular expressions over fixed windows: genres from 300 characters, relations from 800, episodes from 50 000, the slug from 30. Title uses `title:\s*"([^"]+)"`, which stops at the first escaped quote. Synopsis only unescapes `\"`, not `\n`.
- `parse_anime_info` consumes `id`, `title`, `synopsis`, `category.name`, `genres[].name`, `episodes[].number` and `relations[].type/destination.slug/destination.title`. The returned dict already has that shape.
- Measured against the live site (160 randomly sampled pages, compared with a full parse of the payload as ground truth): relations differ in 3 pages (for example `wonderful-precure` 20 vs 7, `one-piece` 29 vs 5), genres in 7 (`psyren` 9 vs 5), titles in 2 (cut at an escaped quote), synopsis in 72 (literal `\n`), and the extracted `slug` is missing in 93 (it is unused). Episodes matched in all 160; the 50 000 window is not exceeded by `one-piece` (1180 episodes, about 31 000 characters) but would be by a series of roughly 2 000+ episodes.
- The payload is a JavaScript object literal that, in every page checked (310 across two samples), is valid JSON except that keys are unquoted. No other identifiers (`undefined`, `void 0`, `new Date(...)`) appeared.

## Goals / Non-Goals

**Goals:**
- Return complete relations, genres and episodes regardless of size.
- Decode titles and synopses correctly.
- Fail loudly rather than return partial data.

**Non-Goals:**
- No change to the dict shape consumed by `parse_anime_info`, to `AnimeInfo`, or to the public API.
- The downloads, embeds and schedule parsers in the same file also use string-unaware brace counting, but no failure has been observed in them; they stay as they are.
- No new dependency.

## Decisions

### D1 - Parse the whole media object instead of extracting fields with regexes

After locating the `media:` object (with a string-aware brace match), convert it to JSON by quoting the bare keys and parse it with `json.loads`. `_parse_media_script` then returns the resulting dict, which already has the keys `parse_anime_info` reads. The conversion is one small scanner that copies string literals verbatim and quotes identifiers followed by `:`; it handles escaped quotes inside strings by construction.

This removes every fixed window at once, makes titles and synopses come out decoded, and also makes the `slug` correct. It was verified on 310 real pages (two independent samples) with no failures.

Alternative: enlarge the windows (for example 800 to 5 000 for relations). Rejected: any fixed size truncates a long enough franchise, the next field could bleed into the match, and it does nothing for escaped quotes.

Alternative: extract each array by bracket matching and keep a per-entry regex. Rejected: it fixes the truncation but keeps three more fragile regexes and still needs separate unescaping logic for titles and synopses.

Alternative: use a JavaScript engine or a JS-literal library. Rejected: a new dependency for a literal that is JSON apart from its keys.

### D2 - Make the brace match string-aware

The locating step becomes aware of string literals and escapes, so a `{` or `}` inside a synopsis cannot end the object early. This is needed for D1 and is covered by a test with braces, brackets, commas and colons inside text.

### D3 - Unreadable payload raises `ScraperParseError`

If the converted text is not valid JSON (for example a future payload that introduces `undefined` or `new Date(...)`), `_parse_media_script` raises `ScraperParseError`, and `parse_anime_info` re-raises it with the anime id in the message, in line with the missing-media-data error from 0.8.0. There is no fallback to the old regexes, so there is a single code path and no partial results.

Alternative: fall back to the old regex extraction when the parse fails. Rejected: it would silently reintroduce the truncation this change removes.

### D4 - Behavior changes accepted in a patch

Consumers get more relations and genres, corrected titles, and synopses with real line breaks instead of literal `\n`. These are corrections of wrong data with the same API, so this is a patch release; the changelog lists each effect explicitly so a consumer that compensated for literal `\n` can adjust.

## Risks / Trade-offs

- [A future payload uses JS constructs that are not JSON] → the parse fails loudly with `ScraperParseError` and the anime id; live verification and the fixture tests will show it. This is deliberate (D3).
- [Strict parsing turns previously tolerated odd pages into errors] → none seen in 310 real pages.
- [Large payloads are parsed fully, including fields the library does not use] → the largest observed literal is about 31 000 characters; the cost is negligible.
- [Synopsis text changes for roughly half of the animes (literal `\n` becomes a newline)] → intended; documented in the changelog.

## Migration Plan

1. Replace the extraction in `_parse_media_script`, add the string-aware locating step, and wrap the error with the anime id in `parse_anime_info`.
2. Add unit tests with minimal fixtures, then verify live against `one-piece`, `naruto-shippuuden`, `kaijuu-8-gou-2nd-season` and `psyren`.
3. Add the 0.8.1 changelog entry and bump `pyproject.toml` and `uv.lock` in the last commit.
4. Rollback: revert the release; consumers pinned to 0.8.0 keep the old behavior.
