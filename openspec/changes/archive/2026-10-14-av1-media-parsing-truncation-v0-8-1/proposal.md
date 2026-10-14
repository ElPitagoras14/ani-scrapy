## Why

The AnimeAV1 parser extracts fields from the page's media payload with regular expressions over fixed-size windows, so real animes lose data silently: `one-piece` returns 5 of 29 relations, `naruto-shippuuden` 5 of 14, and `psyren` 5 of 9 genres. The same regexes also cut titles that contain escaped quotes (a title such as `Kashita Maryoku wa "Revo Barai" de Kyousei Choushuu` is returned as `Kashita Maryoku wa \`) and leave line breaks in synopses as the literal characters `\n`. Consumers such as aniseek persist these incomplete or malformed values as valid.

## What Changes

- AnimeAV1 reads the media payload structurally instead of with fixed-size windows, so relations, genres and episodes are returned complete, whatever their number.
- Titles and synopses are decoded correctly: escaped quotes are kept, and `\n` in a synopsis becomes a real line break.
- If the media payload cannot be read, the parser raises `ScraperParseError` (consistent with the missing-media-data error from 0.8.0) instead of returning partial data.
- No API change: the same fields, with the same types, are returned. Version bump to 0.8.1 with a changelog entry.

Out of scope: relation types (a separate, dropped proposal), JKAnime, and the downloads/embeds/schedule parsers in the same file.

## Capabilities

### New Capabilities
- `animeav1-media-parsing`: completeness and correct decoding of the data read from an AnimeAV1 anime page (relations, genres, episodes, title, synopsis), and failure when the data cannot be read.

### Modified Capabilities

(none; there is no existing spec for this behavior)

## Impact

- Code: `providers/animeav1/parser.py` (`_parse_media_script`).
- Docs: `CHANGELOG.md`.
- Tests: new AnimeAV1 parser tests with minimal fixtures; live verification against `one-piece`, `naruto-shippuuden`, `kaijuu-8-gou-2nd-season` and `psyren`.
- Consumers: same API. They will receive more relations and genres for large franchises, corrected titles, and synopses with real line breaks instead of literal `\n`; text that was previously compensating for the literal sequences may need adjusting.
