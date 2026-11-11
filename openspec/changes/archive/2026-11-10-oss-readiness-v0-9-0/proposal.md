## Why

The library is published and open source, but nothing checks a change before it reaches PyPI: the only workflow publishes on every version bump without running tests or lint. The project also declares support for Python 3.10, which reached end of life in October 2026. Its README and examples lead with the deprecated, broken AnimeFLV provider and call a method that does not exist, and CONTRIBUTING and the packaging metadata are out of date. For a project maintained by one person, automation that blocks a broken release is worth more than extra community files.

## What Changes

- Add a CI workflow (lint, format check, tests on the oldest and newest supported Python) that runs on pull requests and pushes to `main`. Publishing runs it first and does not publish when it fails.
- Publish to PyPI with Trusted Publishing (OIDC) instead of the `PYPI_API_TOKEN` secret.
- The GitHub release body is the version's section of `CHANGELOG.md`; remove `.github/release.yaml` and auto-generated notes.
- Add Dependabot for GitHub Actions only (monthly, grouped).
- **BREAKING**: require Python >= 3.11 (`requires-python`, `.python-version`, docs, `doctor` docs).
- Declare a `[build-system]` so uv installs the package; drop the `uv run --no-sync` workaround from `CLAUDE.md` and the dev skill.
- Complete `pyproject.toml` metadata: SPDX license, Python version classifiers, development status, `Typing :: Typed`, Changelog/Issues/Documentation URLs; remove the duplicated `rich` from the `examples` extra.
- README: add a Quick Start, CI and Python badges, fix the logging example (nonexistent `scraper.log`), stop using AnimeFLV in examples and the benchmark table, and explain how to install the agent skill.
- Replace AnimeFLV in `examples/` and in the main examples of the usage skill with JKAnime or AnimeAV1. AnimeFLV stays documented as deprecated.
- Fix `CONTRIBUTING.md`: provider paths, nonexistent benchmark script, coverage command without its dependency, "Pydantic" schemas, how fixtures and live tests relate; add the release checklist (including the live run) and the Python support policy.
- Add live provider tests in `tests/integration/`, marked `live` and excluded from the default run and from CI. The maintainer runs them locally before each release and when a site is reported broken; a failing live test is the trigger to refresh the provider's fixtures. Today fixtures only change after a user reports a bug, and stale fixtures keep passing (the AnimeFLV fixtures still pass although the provider is broken).
- Reformat the four files that fail `ruff format --check` (separate commit) so CI starts green.
- `CHANGELOG.md`: versioning policy, a pointer to GitHub Releases for versions before 0.8.0, and the 0.9.0 entry. Bump version to 0.9.0.

## Capabilities

### New Capabilities
- `python-support`: which Python versions the package supports and the policy for raising the minimum.
- `release-pipeline`: checks every change must pass, and how a version bump becomes a tag, a GitHub release and a PyPI upload.

### Modified Capabilities

(none)

## Impact

- CI/CD: new `.github/workflows/ci.yml` and `.github/dependabot.yml`; `.github/workflows/publish.yml` rewritten; `.github/release.yaml` deleted.
- Packaging: `pyproject.toml`, `uv.lock`, `.python-version`.
- Tests: new `tests/integration/` live tests and a `live` marker in `pytest.ini`; the default run excludes them.
- Code: formatting only (`providers/animeav1/parser.py`, `providers/animeav1/scraper.py`, `providers/jkanime/scraper.py`, `cli/doctor.py`); no behavior change in the library.
- Docs: `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/03-cli.md`, `docs/01-scrapers.md`, `examples/`, `.claude/skills/ani-scrapy/SKILL.md`, `.claude/skills/ani-scrapy-dev/SKILL.md`, `CLAUDE.md`.
- External, done by the maintainer: register the trusted publisher on pypi.org before merging, then delete the `PYPI_API_TOKEN` secret.
- Consumers on Python 3.10 stay on 0.8.x.
