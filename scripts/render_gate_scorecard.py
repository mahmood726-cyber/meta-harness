"""Render docs/gate_scorecard.json from registry/gate_scorecard.json."""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import gate_scorecard  # noqa: E402


def main() -> int:
    out = gate_scorecard.write_served_view(ROOT)
    print(f"wrote {os.path.relpath(out, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
