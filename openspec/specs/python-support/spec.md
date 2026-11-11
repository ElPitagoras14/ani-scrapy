# python-support Specification

## Purpose
Defines which Python versions the package can be installed on and is tested against, and when the minimum supported version is raised.

## Requirements

### Requirement: Minimum Python version
The package SHALL declare Python 3.11 as its minimum supported version, so installers refuse to install it on older interpreters.

#### Scenario: Install on a supported interpreter
- **WHEN** a user installs the package on Python 3.11 or newer
- **THEN** the installation succeeds

#### Scenario: Install on Python 3.10
- **WHEN** a user installs the latest version on Python 3.10
- **THEN** the installer does not select this version and resolves to the latest 0.8.x release instead

### Requirement: Tested versions
Every change SHALL be tested on the oldest supported Python version and on the newest stable Python version the dependencies support.

#### Scenario: Both ends of the range
- **WHEN** a pull request is opened or updated
- **THEN** the test suite runs on Python 3.11 and on the newest supported stable Python, and both must pass

### Requirement: Minimum version policy
The minimum supported version SHALL be the oldest Python version that still receives security fixes. Raising it SHALL be released as a minor version and listed as a breaking change in the changelog.

#### Scenario: A Python version reaches end of life
- **WHEN** the current minimum Python version reaches end of life
- **THEN** the next minor release raises the minimum and its changelog entry lists the change under breaking changes
