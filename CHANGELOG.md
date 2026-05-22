# STqdm Changelog

## Unreleased

### Security
- Hardened GitHub Actions permissions for CI and release workflows.
- Tightened the shared `.nox` cache key to avoid reusing incompatible environments.
- Restored the session-manifest cache in CI with branch-scoped keys and a `main` fallback.
- Removed the unused `create_auto_merge_pr` workflow helper.
- Added private vulnerability reporting instructions in `SECURITY.md`.
- Added scheduled OpenSSF Scorecard coverage for the repository.
- Reworked the release workflow to use `GITHUB_TOKEN` for GitHub release actions and Trusted Publishing for PyPI uploads.

### Added
- Issue #106: more complex examples
- Issue #94: feature: ability to change defaults

### Fixed
- Issue #104: blank line is printed when `backend=False`
- Issue #101: nested loops break
- Issue #98: `last_print_t` reload issue no longer reproduces
- Issue #97: leave option behavior
- Issue #93: `bar_format` rendering

### Documentation
- Added a short maintenance/status note to the README.
- Expanded the Streamlit demo surface with examples for:
  - main and sidebar placement
  - multiple bars in columns
  - nested bars
  - `stqdm.scope(...)`
  - `bar_format` variants
  - `leave`
  - session-state lock reuse
- Linked the demo app from the main documentation.
