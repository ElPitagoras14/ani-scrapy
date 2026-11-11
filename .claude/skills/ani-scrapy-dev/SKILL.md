---
name: ani-scrapy-dev
description: Use when modifying the ani-scrapy library itself in this repository - fixing a provider after an anime site changes its HTML or data, adding a new site provider, changing public API, exceptions, CLI or supported servers, or bumping the version for a release.
---

# Developing ani-scrapy

Repo-specific checklists for recurring maintenance. Process (branches, OpenSpec, commits) lives in `CLAUDE.md`; this skill lists what each kind of change must touch so nothing is left behind. When working through OpenSpec, copy the relevant checklists into `tasks.md`. Where `CONTRIBUTING.md` disagrees with this skill, this skill is current.

## Where things live

| Concern | Location |
|---|---|
| Provider code | `src/ani_scrapy/providers/<site>/{__init__,constants,parser,scraper}.py` |
| Base class (6 abstract methods) | `src/ani_scrapy/core/base.py` |
| HTTP + status-to-exception mapping | `src/ani_scrapy/core/http.py` |
| Public exports | `src/ani_scrapy/__init__.py` (`__all__`) |
| Doctor connectivity | `CONNECTIVITY_SITES` in `src/ani_scrapy/cli/doctor.py` |
| HTML fixtures | `tests/fixtures/html/<site>_<page>.html` + fixture in `tests/conftest.py` |
| Usage skill (guidance for users' agents) | `.claude/skills/ani-scrapy/SKILL.md` |

## Fixing a provider after a site change

1. Reproduce live with the reported id; save the current page to `tasks/` (gitignored).
2. Write the failing test first. HTML pages: trimmed copy of the real page as a fixture. Embedded data payloads: inline builders, as in `tests/unit/test_animeav1/test_media_parsing.py`.
3. Fix in `parser.py` (and `constants.py` if URLs or maps changed). Touch `scraper.py` only if the network flow changed.
4. Check sibling parsers that read the same page or payload (e.g. AnimeAV1 schedule and episode pages share the `__sveltekit_` script).
5. Unreadable data raises `ScraperParseError` including the anime id. Never return partial or empty objects.
6. Re-run live: the reported id, a large franchise (`one-piece`) and an airing anime.
7. It ships as a patch release: follow **Releasing**.

## Adding a provider

- Scraper subclasses `BaseScraper` and implements all six abstract methods. If the site lacks a capability, ask the maintainer before raising `NotImplementedError`.
- HTTP through `AsyncHttpAdapter`. Browser only via `self._get_browser()`, only for methods that need JavaScript.
- Export in `src/ani_scrapy/__init__.py`; add to `CONNECTIVITY_SITES` and update `tests/unit/test_cli/test_doctor.py`.
- Tests in `tests/unit/test_<site>/`: parser tests on fixtures, scraper tests mocking `scraper.http.get` with `AsyncMock`. No network.
- Find every place that lists providers and add the new one next to each hit:

  ```bash
  rg -n "JKAnime" README.md docs examples .claude/skills/ani-scrapy
  ```

  This covers README tables and the Diagnostics list, `docs/01-scrapers.md`, examples, and the usage skill (frontmatter `description`, imports, `SUPPORTED_SERVERS` lines, "all 3 scrapers" counts).
- It ships as a minor release: follow **Releasing**.

## Public surface sync

| When this changes | Also update |
|---|---|
| Methods or static/dynamic behavior | README "Method Status Comparison", `docs/01-scrapers.md`, usage skill |
| `SUPPORTED_SERVERS` | `docs/01-scrapers.md` "Supported Servers", usage skill |
| Exceptions | `docs/04-error-handling.md`, usage skill "Error handling" |
| CLI | `docs/03-cli.md`, README "Diagnostics" |
| Anything users can notice | `CHANGELOG.md` |

## Releasing

The version bump goes in the same PR as the change (as in 0.8.0 and 0.8.1).

1. Version: fix = patch; feature or new provider = minor; breaking = minor while on 0.x.
2. `CHANGELOG.md`: new `## X.Y.Z` on top with `Breaking changes` / `Added` / `Changed` / `Deprecated` / `Fixed` as needed. Write from the user's side: what they saw, what they get now, what to change (Before/After code for breaking changes).
3. `version` in `pyproject.toml` is the only version string. Run `uv lock`; `git diff uv.lock` should change only the `ani-scrapy` version line.
4. `uv build --out-dir <scratch dir>` must succeed: CI builds the same way before publishing.
5. Commit `pyproject.toml` and `uv.lock` last.
6. Merging to `main` IS the release: `publish.yml` tags, creates the GitHub release and uploads to PyPI, and runs no tests. Stop before merging unless the maintainer asks. Never tag or publish by hand.
7. Notifying downstream consumers ("orquestador") happens only when the maintainer asks.

## Verify

```bash
uv run --no-sync pytest
uv run --no-sync ruff check src tests
uv run --no-sync ruff format --check src tests
```

`--no-sync` is required: without it uv uninstalls the editable package from `.venv` (the project has no `[build-system]`) and every test fails with `ModuleNotFoundError: ani_scrapy`.

If `ruff format` flags files you touched that were already unformatted, reformat them in a separate `chore(format): ...` commit before your change, so the diff of the change stays readable.

Provider changes also need the live check above; there is no live test suite.

## Common mistakes

- Using AnimeFLV in new examples, docs or features: it is deprecated and broken.
- Forgetting the usage skill: stale guidance makes users' agents write wrong code.
- Pushing a tag manually: `publish.yml` then sees no version change and skips PyPI.
