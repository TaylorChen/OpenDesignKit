# Contributing to OpenDesignKit

Thanks for your interest! Quick ground rules:

## Setup

```bash
git clone https://github.com/TaylorChen/OpenDesignKit.git
cd OpenDesignKit
# no dependencies to install — the toolchain is pure Python 3 stdlib
python3 tools/validator.py check examples/demo-slides
```

## Before you open a PR

1. Run the validator over everything you touched:

   ```bash
   python3 tools/validator.py check examples/demo-slides
   python3 tools/validator.py check examples/demo-design
   python3 tools/validator.py check examples/demo-design-system
   ```

   All three must pass with **0 errors** (warnings need a sentence of justification in the PR description).

2. If you changed `tools/templates/support.js`, copy it to `examples/demo-design/support.js`
   (the template is the single source of truth) and smoke-test a board in your browser.

3. Keep commits focused; the repo is small, squash nit fixes.

## Licensing (important)

- `tools/`, `examples/`, and docs are **MIT** (see [LICENSE](LICENSE)).
- `skills/` is adapted from BaoCut and remains under the **BaoCut Community License**
  (see [NOTICE.md](NOTICE.md) and [licenses/baocut-community-license.txt](licenses/baocut-community-license.txt)).
  By contributing to `skills/` you agree your changes are distributed under that license for
  the noncommercial community grant; MIT cannot be applied to that directory.

## Reporting issues

Include: OS, browser (for render issues), the exact CLI command, and the smallest
deck/canvas/system that reproduces the problem.
