# OpenDesignKit

> **English** | [中文文档](README.md)

> An industrial-grade design suite for every AI agent — Claude Design / Claude Slides / Claude Design System, decoupled from any proprietary host so that any agent tool (Claude Code, Antigravity CLI, Cursor, Cline, …) can produce top-tier visual designs and presentations.

Adapted from the built-in skills of [JimLiu/baocut](https://github.com/JimLiu/baocut) (commit [`7aa049e8`](https://github.com/JimLiu/baocut/commit/7aa049e8)), then generalized: host-specific dependencies removed, replaced by **plain file formats + optional tool adapters**. Any agent that can read and write local files can use it.

## The three skills

| Skill | Output format | Purpose |
|---|---|---|
| [`open-design`](skills/open-design/SKILL.md) | `canvas.json` + one `.dc.html` per board | UI / web / poster / infographic / prototype mockups, with interactive components (DCLogic state) |
| [`open-slides`](skills/open-slides/SKILL.md) | `deck.json` + one HTML file per slide | Slide decks and talks, rendered by any modern browser |
| [`open-design-system`](skills/open-design-system/SKILL.md) | `design-system.json` + `tokens.json` + brand manual | Brand design systems: color/type/spacing tokens |

Design system tokens are the **single source of truth** → boards and slides **reference** them → everything on disk is **plain files**, no database or remote service required.

## Toolchain (zero dependencies, pure Python 3 stdlib)

```bash
python3 tools/validator.py check examples/demo-slides    # auto-detects format; 0 errors expected
python3 tools/validator.py init-deck my-deck             # scaffold: deck + cover + player
python3 tools/validator.py init-canvas my-canvas         # scaffold: canvas + board + support.js
python3 tools/validator.py init-design-system my-brand   # scaffold: tokens + manual + tokens.css
python3 tools/validator.py build-player my-deck          # (re)build the slide player
python3 tools/validator.py build-tokens my-brand         # compile tokens.json -> tokens.css
```

- **Slide player**: open the generated `player.html` — arrow keys to navigate, `S` speaker notes, `O` overview, `F` fullscreen; speaker notes are extracted and inlined so it works from `file://`.
- **Board preview runtime** (`support.js`, MIT, independent implementation): renders `{{ holes }}`, `sc-for`/`sc-if`, click handlers, DCLogic state, and `dc-import` child boards directly in any browser.
- **Validator**: structure & references, required board elements, disallowed tags, 1920×1080 stage, token naming/value rules, and more. All shipped examples pass with 0 errors / 0 warnings.

## Install into your agent tool

| Host | How |
|---|---|
| **Claude Code** | `cp -r skills/* ~/.claude/skills/` (or per-project `.claude/skills/`) |
| **Antigravity / agy CLI** | `cp -r skills/* ~/.gemini/skills/` |
| **Cursor / Cline / others** | Put the `SKILL.md` content into system prompt or rules; keep `references/` alongside |
| **Any agent** | Prompt: “When asked for visual designs, read `skills/open-design/SKILL.md` and follow it.” |

## License

- `tools/`, `examples/`, docs: **MIT** ([LICENSE](LICENSE))
- `skills/` (adapted from upstream): **BaoCut Community License v1.0** ([licenses/baocut-community-license.txt](licenses/baocut-community-license.txt)) — noncommercial sharing and modification permitted; commercialization requires upstream written consent. See [NOTICE.md](NOTICE.md).

## Credits & provenance

- Upstream: [JimLiu/baocut](https://github.com/JimLiu/baocut) — commit `7aa049e8` introduced the Claude Design (Design Canvas + Design System) and Claude Slides integration
- Context: [@dotey's tweet](https://x.com/dotey/status/2109482425722057154)
- This repository is not affiliated with or endorsed by Anthropic.

Maintained by [TaylorChen](https://github.com/TaylorChen) · See [CHANGELOG](CHANGELOG.md) · Contributions welcome ([CONTRIBUTING](CONTRIBUTING.md))
