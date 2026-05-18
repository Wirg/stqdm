# STqdm Changelog

## Unreleased

### Security
- Hardened GitHub Actions permissions for CI and release workflows.
- Tightened the shared `.nox` cache key to avoid reusing incompatible environments.
- Switched CI session caches to branch-scoped restore keys with a `main` fallback and write-back only from push jobs.
- Removed the unused `create_auto_merge_pr` workflow helper.

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
- Expanded the Streamlit demo surface with examples for:
  - main and sidebar placement
  - multiple bars in columns
  - nested bars
  - `stqdm.scope(...)`
  - `bar_format` variants
  - `leave`
  - session-state lock reuse
- Linked the demo app from the main documentation.
