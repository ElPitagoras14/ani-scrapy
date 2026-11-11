## Context

See proposal.md for motivation. Current state:

- `.github/workflows/publish.yml` has three jobs on push to `main`: `check-version` (compares `pyproject.toml` with the latest tag), `release` (creates the tag and a GitHub release with auto-generated notes), and `publish` (`uv build` + `uv publish` with `PYPI_API_TOKEN`). No tests or lint run. The tag is pushed before the upload, so a failed upload leaves a tag that makes the next push skip publishing.
- `.github/release.yaml` groups auto-generated notes by PR label. With one PR per release, every release body is a single line.
- `pyproject.toml` has no `[build-system]`. uv treats the project as not packaged: `uv sync` uninstalls the editable package from `.venv` (which still reports version 0.6.1) and tests fail to import `ani_scrapy`. `CLAUDE.md` and the dev skill work around this with `uv run --no-sync`.
- `license = { text = "MIT" }` plus the `License :: OSI Approved :: MIT License` classifier; recent setuptools rejects that classifier when an SPDX `license` expression is used.
- `ruff check` passes; `ruff format --check` fails on `providers/animeav1/parser.py`, `providers/animeav1/scraper.py`, `providers/jkanime/scraper.py` and `cli/doctor.py`.
- The unit suite (59 tests) mocks HTTP and has run offline; it has never run without Playwright browsers installed.
- AnimeFLV appears in README (logging, Brave, benchmark), in `examples/01`–`03`, `05`, `07`, in `docs/01-scrapers.md`, and in 14 places in the usage skill, several of them as the main example.
- Fixtures in `tests/fixtures/html/` (AnimeFLV and JKAnime, all captured 2026-02-11) and the inline AnimeAV1 builders are snapshots: they never fail when a site changes. The AnimeFLV fixtures still pass although the provider is broken. `tests/integration/` exists with only an empty `__init__.py`; `pytest.ini` registers only an `asyncio` marker.
- `docs/03-cli.md` says `doctor` "verifies Python >= 3.10.14"; `doctor` only reports the version. The "Latency" line is duplicated.

## Goals / Non-Goals

**Goals:**
- A broken change cannot reach PyPI.
- Releasing stays a version bump plus a changelog entry in the same PR.
- A new contributor can follow README and CONTRIBUTING without hitting stale paths or commands.

**Non-Goals:**
- No library behavior change and no adoption of 3.11-only features in the code.
- No scheduled or CI-run live checks (see D11), issue or PR templates, SECURITY.md, code of conduct, docs site or coverage thresholds (out of scope by decision).
- No GitHub repository settings (description, topics); those are not code.
- AnimeFLV is not removed; it stays documented as deprecated.

## Decisions

### D1 - One reusable CI workflow, called by publish

`ci.yml` runs on `pull_request`, on `push` to `main` and on `workflow_call`. Jobs: `lint` (`ruff check`, `ruff format --check`, newest Python) and `test` (matrix 3.11 and 3.14: `uv sync --locked`, `uv run pytest`). `publish.yml` calls it with `uses: ./.github/workflows/ci.yml` and every later job `needs` it.

Alternative: rely on branch protection requiring CI. Rejected: a solo maintainer can push to `main` directly, and protection does not stop a push from triggering publish.
Alternative: copy the test steps into `publish.yml`. Rejected: two definitions of "the checks" drift.

### D2 - Upload before tagging

New job order in `publish.yml`: `check-version` → `ci` → `publish` (build + upload) → `release` (tag + GitHub release). If the upload fails, no tag exists, and the next push or a re-run retries. `check-version` also fails when `CHANGELOG.md` has no `## X.Y.Z` heading for the new version, so a missing entry stops everything before the upload.

Alternative: keep tag-then-publish. Rejected: a failed upload leaves a tag that hides the version from the comparison.

### D3 - Trusted Publishing with `uv publish`

The `publish` job gets `permissions: id-token: write` and runs `uv publish --trusted-publishing always`, which fails instead of silently looking for a token. No GitHub environment: an approval gate adds nothing for one maintainer. The upload stays in a job of `publish.yml` itself, never inside the reusable `ci.yml`: PyPI does not accept a reusable workflow as a trusted publisher. The secret stays in the repository until the first release succeeds, then the maintainer deletes it.

### D4 - Release body from CHANGELOG.md

The `release` job extracts the lines between `## X.Y.Z` and the next `## ` heading with `awk` into a file and passes it as `body_path` to `softprops/action-gh-release`. `generate_release_notes` and `.github/release.yaml` are removed. PR labels remain a convention in `CLAUDE.md` for filtering, not for notes.

### D5 - setuptools as build backend, SPDX license

`[build-system] requires = ["setuptools>=77"]`, `build-backend = "setuptools.build_meta"`. The existing `[tool.setuptools.packages.find]` and `MANIFEST.in` keep working. `license = "MIT"`, `license-files = ["LICENSE"]`, and the license classifier is removed.

Alternative: `uv_build` or hatchling. Rejected: more configuration to change for no gain, and `MANIFEST.in` would need rewriting.

### D6 - Python 3.11 minimum, 3.14 as newest

`requires-python = ">=3.11"`; classifiers for 3.11–3.14; `.python-version` set to 3.14, which is what `publish.yml` builds with and what the local `.venv` is recreated with. 3.14 is the newest version installed locally with known wheels for `lxml` and `aiohttp`; moving to a newer one is a later one-line change in the matrix.

### D7 - Replace AnimeFLV in examples, keep it in reference docs

Examples (README, `examples/`, the usage skill's main examples) use JKAnime or AnimeAV1. AnimeFLV blocks are removed from `examples/` because they fail against the current site. The README API tables and `docs/01-scrapers.md` provider notes keep AnimeFLV marked as deprecated. The benchmark table drops the AnimeFLV row.

### D8 - Agent skill distribution through the README

README gets a short "Using with AI agents" section: copy `.claude/skills/ani-scrapy/` into the consuming project's `.claude/skills/`. The skill is not shipped in the wheel: agents read skills from project or user directories, not from `site-packages`.

### D9 - Changelog stays in its current style

No `[Unreleased]` section, because the version is bumped in the same PR as the change. A header states the versioning policy (0.x: breaking changes bump the minor version) and points to GitHub Releases for versions before 0.8.0. No dates are added, to stay consistent with existing entries.

### D10 - Formatting before the rest

`ruff format src tests` runs first so CI starts green. It goes in the change's single commit (`CLAUDE.md`: as few commits as possible); the reformatted files have no other changes, so they are easy to tell apart in review.

### D11 - Live tests run locally, behind a marker

Live tests live in `tests/integration/`, one module per supported provider (JKAnime, AnimeAV1; not the deprecated AnimeFLV), marked `@pytest.mark.live`. `pytest.ini` registers the marker and adds `-m "not live"` to `addopts`, so the default run and CI skip them; `uv run pytest -m live` selects them (the last `-m` wins). Each test checks invariants, not exact values: search returns results, `get_anime_info` on a stable finished anime returns a title and episodes, table and iframe links are non-empty. They do not compare against fixtures.

They run on the maintainer's machine before each release and when a site is reported broken. A failure is the trigger for the "Fixing a provider" procedure in the dev skill, which refreshes the fixture from the current page. Fixtures are refreshed on evidence of change, not on a schedule. A failure the maintainer chooses to defer gets an issue and `pytest.mark.xfail(strict=True)` citing it: the run stays green, and `strict` turns it red again once the provider works, so the marker is not forgotten. The first case is JKAnime iframe links (#29).

Alternative: a scheduled GitHub Actions canary. Rejected: requests to third-party sites from GitHub's infrastructure raise terms-of-service questions, and datacenter IPs are often blocked, which makes failures noisy.
Alternative: record a capture date per fixture and refresh old ones. Rejected: age does not indicate whether a fixture still matches the site.

## Risks / Trade-offs

- [Live tests are flaky (slow site, temporary block, anime removed)] → Use stable, finished titles and invariants instead of exact counts; a failure is investigated by hand before acting on it.
- [The maintainer forgets to run them] → The step is in the release checklist of the dev skill and CONTRIBUTING, and the release-pipeline spec requires it.

- [Trusted publisher not registered on pypi.org when the PR is merged] → The upload fails and, thanks to D2, nothing is tagged. Register it before merging; if it was missed, register it and re-run the failed jobs.
- [A unit test needs a Playwright browser or network in CI] → Run the suite in a fresh environment without `playwright install` during implementation; fix or mock any test that needs it before relying on CI.
- [`uv lock` with the new `requires-python` changes more than the version line] → Expected once (resolution markers for 3.10 disappear); review the diff for unexpected dependency upgrades.
- [Users on Python 3.10] → Installers skip 0.9.0 because of `requires-python` and keep 0.8.1; the changelog says so.
- [Reformatting adds noise to `git blame`] → Isolated in one commit.

## Migration Plan

1. Before merging: register a trusted publisher on pypi.org for project `ani-scrapy` (owner `ElPitagoras14`, repository `ani-scrapy`, workflow `publish.yml`, no environment).
2. Merge; watch the "Publish to PyPI" run: CI, upload, tag `0.9.0`, release with the changelog section.
3. After a successful upload: delete the `PYPI_API_TOKEN` repository secret.

Rollback: if Trusted Publishing cannot be set up, restore the token environment variables in the `publish` job; the rest of the change is independent of it.
