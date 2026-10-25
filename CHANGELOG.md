# Changelog

All notable changes to this project are documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/); versioning: semver.

## [0.1.1] - 2026-10-25

### Added
- **`odk` unified CLI** (pip-installable, `pipx install opendesignkit`): `init deck|canvas|system`, `check [--json]`, `build player|tokens`, `serve`, `export-pdf`
- `odk serve`: local preview server enabling `dc-import` child boards over http
- `odk export-pdf`: per-slide 16:9 PDF export via headless Chrome (`--no-pdf-header-footer`)
- `odk check --json`: machine-readable validation output for agents/CI
- Local quality gate: `.githooks/pre-commit` (validates examples + runs unit tests)
- Community infrastructure: issue/PR templates, CODE_OF_CONDUCT, SECURITY policy
- Unit test suite (`tests/test_core.py`): injection escapes, type detection, token compiler edges

### Fixed
- **Security**: `build-player` inlined JSON is now escaped (`</` → `<\/`, `<!--` → `<\u0021--`); a malicious deck.json can no longer break out of the player's `<script>` block (regression-tested)
- `check --json` output is now pure JSON (validator banners suppressed)

### Changed
- Engine moved from `tools/validator.py` to `odk/core.py`; the old path remains a compatible shim
- Templates canonical location: `odk/templates/` (shipped inside the wheel)

## [0.1.0] - 2026-10-25

First public release.

### Added
- **Three agent skills** (generalized from [JimLiu/baocut@7aa049e8](https://github.com/JimLiu/baocut/commit/7aa049e8), host-specific dependencies removed):
  - `open-design` — canvas.json + interactive `.dc.html` boards (DCLogic state, sc-for/sc-if, dc-import)
  - `open-slides` — deck.json + one HTML per slide, with speaker notes
  - `open-design-system` — tokens.json + brand manual, single source of truth
- **Zero-dependency CLI** (`tools/validator.py`):
  - `check` (auto-detect) / `check-slides` / `check-design` / `check-design-system`
  - scaffolding: `init-deck` / `init-canvas` / `init-design-system`
  - builders: `build-player` (slide player with inlined speaker notes), `build-tokens` (tokens.json → tokens.css)
- **`support.js` preview runtime** — renders `{{ holes }}`, `sc-for`/`sc-if`, event bindings, DCLogic state and `dc-import` child boards in any plain browser; board links navigate natively
- **Examples** for all three formats, all passing validation with 0 errors / 0 warnings
- Dual licensing: MIT (original parts) + BaoCut Community License (derived skills), see [NOTICE.md](NOTICE.md)

[0.1.0]: https://github.com/TaylorChen/OpenDesignKit/releases/tag/v0.1.0
