"""Write docs/endpoint_canonical_sweep.json from built review objects."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import endpoint_canonical  # noqa: E402


def main() -> int:
    out = endpoint_canonical.sweep(ROOT)
    path = os.path.join(ROOT, "docs", "endpoint_canonical_sweep.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
