## 1. Parser

- [x] 1.1 Make the media-object location in `_parse_media_script` string-aware (braces inside strings and escaped quotes do not affect the match). Verify with a test whose title and synopsis contain `{`, `}`, `[`, `]`, `,` and `:`, and whose related entries and episodes after them are still read.
- [x] 1.2 Replace the regex and fixed-window extraction with a conversion of the media object to JSON (quote bare keys, copy strings verbatim) parsed with `json.loads`, returning the resulting dict with the same keys `parse_anime_info` already reads. Verify with the existing AnimeAV1 parser tests passing unchanged.
- [x] 1.3 Raise `ScraperParseError` when the converted payload is not valid JSON, and re-raise it from `parse_anime_info` with the anime id in the message. Verify with a test using a payload with an unsupported construct (for example `undefined`) that expects `ScraperParseError` with the anime id.

## 2. Tests

- [x] 2.1 Add fixtures and tests that reproduce the truncation: more than 800 characters of relations (for example 30 entries, order preserved), 12 genres, and 3000 episodes. Verify the tests fail against the old implementation and pass against the new one.
- [x] 2.2 Add tests for text decoding: a title and a related-anime title with escaped quotes, and a synopsis with `\n` that comes out with real line breaks and no literal backslash-n. Verify they pass.
- [x] 2.3 Verify `include_episodes=False` still returns no episodes, with a parser test.

## 3. Live verification

- [x] 3.1 Run `get_anime_info` against the live site for `one-piece` (expect 29 relations and 1180 episodes), `naruto-shippuuden` (14 relations), `psyren` (9 genres) and `kaijuu-8-gou-2nd-season` (2 relations, 6 genres), using a script outside the repo, and verify the counts match the page payload. Also run `get_anime_info` for the AnimeAV1 anime used before (`neko-to-ryuu`, `shuiro-no-kamen`, `zombie-sagashitemasu`, `ranma-2024-3rd-season`) and verify nothing regresses.

## 4. Release prep

- [x] 4.1 Add a 0.8.1 entry to `CHANGELOG.md` listing: complete relations, genres and episodes; corrected titles; synopses with real line breaks (instead of literal `\n`); and the parse error for unreadable media data. Verify each item is present.
- [x] 4.2 Run the full test suite with `.venv`, `ruff check` and `openspec validate av1-media-parsing-truncation-v0-8-1 --strict`; verify all pass.
- [x] 4.3 Bump `version` to 0.8.1 in `pyproject.toml` and verify `uv lock` is consistent (last commit, only when asked to commit). Publishing and notifying "orquestador" happen only after the user asks for them.
