## 1. Formatting baseline

- [x] 1.1 Run `ruff format src tests`. Verify `uv run --no-sync ruff format --check src tests` and `uv run --no-sync pytest` pass and the diff contains only formatting.

## 2. Packaging and Python support

- [x] 2.1 In `pyproject.toml`: add `[build-system]` (setuptools>=77), set `requires-python = ">=3.11"`, `license = "MIT"`, `license-files = ["LICENSE"]`, remove the license classifier, add classifiers for Python 3.11–3.14, `Development Status :: 4 - Beta` and `Typing :: Typed`, add `Changelog`, `Issues` and `Documentation` URLs, and reduce the `examples` extra to `tabulate`. Verify `uv build --out-dir <scratch>` succeeds without license warnings and the wheel contains `ani_scrapy/py.typed`.
- [x] 2.2 Set `.python-version` to 3.14, recreate `.venv` with it, and run `uv lock` and `uv sync`. Verify `uv sync --dry-run` no longer wants to uninstall `ani-scrapy`, the installed version reports the current one, and `uv run pytest` passes.
- [x] 2.3 Verify the suite on the minimum version with `uv run --python 3.11 --isolated pytest` (or an equivalent fresh 3.11 environment).
- [x] 2.4 Verify the default suite runs without Playwright browsers and without network: run it in a fresh environment where `playwright install` was not run, with no network access if possible. Fix or mock any test that needs either.
- [x] 2.5 Review `git diff uv.lock`: only the `ani-scrapy` entry and `requires-python` markers change, no dependency upgrades.

## 3. Live tests

- [x] 3.1 In `pytest.ini`, register the `live` marker and add `-m "not live"` to `addopts`. Verify `uv run pytest` collects no live test and `uv run pytest -m live --collect-only` collects only live tests.
- [x] 3.2 Add `tests/integration/test_jkanime_live.py` and `tests/integration/test_animeav1_live.py`, all tests marked `live`. Per provider, on a stable finished anime: `search_anime` returns results, `get_anime_info` returns a title and episodes, `get_table_download_links` and `get_iframe_download_links` for one episode return links. Assert invariants, not exact counts. Verify with `uv run pytest -m live` against the live sites (Playwright Chromium installed).
- [x] 3.3 Mark `test_get_iframe_download_links` in `tests/integration/test_jkanime_live.py` with `pytest.mark.xfail(strict=True, reason=...)` citing issue #29 (JKAnime iframe links empty; deferred, iframe is a last-resort option). Verify `uv run pytest -m live` reports it as xfailed and nothing fails.
- [x] 3.4 Add a live test per provider for `get_file_download_link`, the main download path: from the episode's table links, resolve at least one server in that provider's `SUPPORTED_SERVERS` to a final URL. Verify with `uv run pytest -m live`.

## 4. CI and publishing

- [x] 4.1 Add `.github/workflows/ci.yml` (triggers: `pull_request`, `push` to `main`, `workflow_call`) with a `lint` job (`ruff check`, `ruff format --check`, Python 3.14) and a `test` job (matrix 3.11 and 3.14, `uv sync --locked`, `uv run pytest`). Verify the YAML parses and, once pushed, both jobs pass on the PR and the logs show the live tests deselected.
- [x] 4.2 Rewrite `.github/workflows/publish.yml`: `check-version` (also fails when `CHANGELOG.md` has no `## X.Y.Z` heading) → `ci` (calls `ci.yml`) → `publish` (`uv build`, `uv publish --trusted-publishing always`, `permissions: id-token: write`, no token env vars) → `release` (tag, then GitHub release with `body_path` from the changelog section, no `generate_release_notes`). Verify by reading the job graph: no job creates a tag or uploads before `ci` passes, and the upload precedes the tag.
- [x] 4.3 Verify the changelog extraction locally: run the `awk` command from the workflow for `0.9.0` and `0.8.0` against `CHANGELOG.md` and check each prints exactly that version's section; for a missing version, check the `check-version` step's test exits non-zero.
- [x] 4.4 Delete `.github/release.yaml`. Verify no file references it (`rg -n "release.yaml"` outside `openspec/changes/archive`).
- [x] 4.5 Add `.github/dependabot.yml` for `github-actions` only, monthly, in a single group. Verify the YAML parses.

## 5. README

- [x] 5.1 Add CI and supported-Python badges next to the existing ones and a Quick Start (install, `playwright install chromium`, a search + info example with AnimeAV1). Verify the Quick Start code runs against the live site.
- [x] 5.2 Fix the logging example (no `scraper.log`, no AnimeFLV), switch the Brave example to JKAnime, drop the AnimeFLV benchmark row, and update Requirements to Python >= 3.11. Verify `rg -n "AnimeFLV" README.md` only hits the deprecation notes in the API tables.
- [x] 5.3 Add a "Using with AI agents" section explaining how to copy `.claude/skills/ani-scrapy/` into a project's `.claude/skills/`. Verify the path exists.

## 6. Examples, docs and usage skill

- [x] 6.1 Remove AnimeFLV from `examples/01`, `02`, `03`, `05`, `07`, `examples/__init__.py` and `examples/index.md` (index also says Python >= 3.11). Verify `rg -n "AnimeFLV" examples` returns nothing and `uv run python -m py_compile` succeeds on each example.
- [x] 6.2 `docs/03-cli.md`: "Reports the Python version" instead of "Verifies Python >= 3.10.14", remove the duplicated "Latency" line. `docs/01-scrapers.md`: replace AnimeFLV in import and code examples, keep its provider note as deprecated. Verify with `rg -n "3\.10|AnimeFLV" docs`.
- [x] 6.3 Usage skill `.claude/skills/ani-scrapy/SKILL.md`: Python >= 3.11, main examples (core pattern, Brave, end-to-end, `SUPPORTED_SERVERS` filter) with JKAnime or AnimeAV1, keep the AnimeFLV deprecation notes. Verify every remaining `AnimeFLV` hit is a deprecation note.

## 7. Contributor docs

- [x] 7.1 Rewrite the stale parts of `CONTRIBUTING.md`: provider paths (`providers/<site>/`), benchmark via `examples/07_benchmark.py`, remove the coverage command, schemas are dataclasses, type hints for Python 3.11+, add `ruff format --check`. Add a "Tests" section explaining fixtures vs live tests (`uv run pytest -m live`, run locally, never in CI; a failing live test means refreshing the fixture), a short release checklist (live tests pass, version bump + changelog in the same PR, merge publishes) and the Python support policy. Verify every path and command it mentions exists or runs.
- [x] 7.2 `CLAUDE.md`: remove the `uv run --no-sync` note and change "Python 3.10+" to "Python 3.11+". `.claude/skills/ani-scrapy-dev/SKILL.md`: use plain `uv run` in Verify, remove the `--no-sync` explanation and the "CONTRIBUTING disagrees" sentence; in "Fixing a provider" replace the ad hoc live reproduction with `uv run pytest -m live`; in "Adding a provider" require a live test module; in "Releasing" add "live tests pass" as the first step; replace "there is no live test suite"; remove anything the skill repeats from `CLAUDE.md` or `CONTRIBUTING.md`. Verify `rg -n "no-sync|3\.10|no live test" CLAUDE.md .claude/skills CONTRIBUTING.md` returns nothing.

## 8. Release prep

- [x] 8.1 `CHANGELOG.md`: add a header with the versioning policy and a pointer to GitHub Releases for versions before 0.8.0, and a `## 0.9.0` entry: Breaking changes (Python >= 3.11; 3.10 users stay on 0.8.x), Changed (packaging metadata, typed marker classifier). Verify each item is present and the workflow `awk` extracts it.
- [x] 8.2 Run `uv run pytest`, `uv run pytest -m live`, `uv run ruff check src tests`, `uv run ruff format --check src tests` and `openspec validate oss-readiness-v0-9-0 --strict`; verify all pass.
- [x] 8.3 Bump `version` to 0.9.0 in `pyproject.toml`, run `uv lock`, and verify `git diff uv.lock` only changes the `ani-scrapy` version line (last commit, only when asked to commit).
- [ ] 8.4 Before merging, the maintainer registers the trusted publisher on pypi.org (owner `ElPitagoras14`, repository `ani-scrapy`, workflow `publish.yml`, no environment). After the release run succeeds, the maintainer deletes the `PYPI_API_TOKEN` secret. Merging, publishing and notifying "orquestador" happen only when the user asks.
