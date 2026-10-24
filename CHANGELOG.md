# Changelog

All notable changes to this project are documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/); versioning: semver.

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
