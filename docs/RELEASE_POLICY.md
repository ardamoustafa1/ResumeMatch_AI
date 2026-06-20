# Release Policy

ResumeMatch AI follows [Semantic Versioning](https://semver.org/).

## Version Format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Incompatible API changes, requiring database migrations that are not backward-compatible, or major UI overhauls.
- **MINOR**: Added functionality in a backwards-compatible manner (e.g., adding a new AI provider, adding a new UI section).
- **PATCH**: Backwards-compatible bug fixes and security patches.

## Release Cadence

- **Minor releases** are typically cut at the end of each month if there are significant new features.
- **Patch releases** are cut on an as-needed basis for critical bug fixes.

## Supported Versions

Only the latest `MAJOR.MINOR` release receives official patch updates. If you are running an older version, please upgrade to the latest release before reporting a bug.

## Deprecation Policy

Features or API endpoints scheduled for removal will be marked as `Deprecated` for at least one full `MINOR` release before being completely removed in the next `MAJOR` release.
