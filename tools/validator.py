#!/usr/bin/env python3
"""Legacy entry point — kept for compatibility with earlier docs & scripts.

Prefer the packaged CLI:

    pipx install opendesignkit
    odk check <dir>

This shim bootstraps the repo root on sys.path, re-exports the engine
(`odk.core`) for `import validator` style usage, and delegates to `odk.cli`.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from odk import core  # noqa: E402,F401,F403

# re-export engine names for `import validator` style consumers
globals().update({k: v for k, v in vars(core).items() if not k.startswith("_")})

from odk.cli import main  # noqa: E402

if __name__ == "__main__":
    main(sys.argv[1:])
