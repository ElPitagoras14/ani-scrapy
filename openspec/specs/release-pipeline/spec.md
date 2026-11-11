# release-pipeline Specification

## Purpose
Defines the checks every change must pass and how a version bump on `main` becomes a tag, a GitHub release and a PyPI upload, so a broken build is never published.

## Requirements

### Requirement: Checks on every change
Every pull request and every push to `main` SHALL run lint, a formatting check and the unit test suite, and SHALL report failure when any of them fails.

#### Scenario: Pull request with a failing test
- **WHEN** a pull request contains a change that makes a unit test fail
- **THEN** the checks on the pull request fail

#### Scenario: Unformatted code
- **WHEN** a pull request contains a file that the formatter would change
- **THEN** the checks on the pull request fail

### Requirement: Live provider checks on demand
The test suite SHALL include live tests that exercise each supported, non-deprecated provider against its real site. They SHALL be excluded from the default test run and from CI, and SHALL run only when explicitly selected. A release SHALL NOT be prepared while a live test fails, unless the failure is tracked in an issue and the test is marked as an expected failure that cites it.

#### Scenario: Default run stays offline
- **WHEN** the test suite runs without selecting live tests, locally or in CI
- **THEN** no live test runs and no request reaches a provider's site

#### Scenario: Maintainer runs the live tests
- **WHEN** the maintainer selects the live tests
- **THEN** for each supported provider, search, anime info and download links are checked against the real site

#### Scenario: Site changed
- **WHEN** a live test fails because a provider's site changed
- **THEN** the release is not prepared until the provider is fixed and its fixtures are refreshed from the current site

#### Scenario: Known failure deferred
- **WHEN** a live test fails, the maintainer opens an issue for it and marks the test as an expected failure citing the issue
- **THEN** the live run passes and the release can be prepared; once the provider is fixed and the test passes again, the run fails until the marker is removed

### Requirement: Publish only after checks pass
A push to `main` whose package version differs from the latest tag SHALL create the tag, the GitHub release and the PyPI upload only after the checks pass on that commit.

#### Scenario: Checks fail on a version bump
- **WHEN** a commit that changes the version is pushed to `main` and the checks fail
- **THEN** no tag, GitHub release or PyPI upload is created

#### Scenario: No version change
- **WHEN** a commit that does not change the version is pushed to `main`
- **THEN** nothing is tagged, released or published

### Requirement: Publishing without stored credentials
Uploads to PyPI SHALL authenticate with short-lived credentials issued to the repository's publish workflow, not with a long-lived token stored as a repository secret.

#### Scenario: Release upload
- **WHEN** the publish workflow uploads a new version
- **THEN** it authenticates through Trusted Publishing and no PyPI token secret is read

### Requirement: Release notes from the changelog
The body of the GitHub release for a version SHALL be that version's section of `CHANGELOG.md`.

#### Scenario: Release created
- **WHEN** version `X.Y.Z` is released
- **THEN** the GitHub release body contains the text under `## X.Y.Z` in `CHANGELOG.md`, up to the next version heading

#### Scenario: Missing changelog entry
- **WHEN** the version is bumped but `CHANGELOG.md` has no `## X.Y.Z` section
- **THEN** the publish workflow fails before creating the tag, the release or the upload
