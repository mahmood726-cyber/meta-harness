from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import compat_direction  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "compat_direction_sweep.json")
    args = ap.parse_args(argv)
    rows = []
    for path in sorted((ROOT / "docs" / "reviews").glob("*/review.json")):
        review = json.loads(path.read_text(encoding="utf-8"))
        for row in compat_direction.review_directions(review):
            rows.append(row)

    derivable = [r for r in rows if r["key_direction"] != compat_direction.NOT_DERIVABLE]
    over = [
        r
        for r in derivable
        if r["key_direction"]
        == compat_direction.ASSERTED_HOMOGENEOUS_UNDERLYING_HETEROGENEOUS
    ]
    under = [
        r
        for r in derivable
        if r["key_direction"]
        == compat_direction.ASSERTED_HETEROGENEOUS_UNDERLYING_HOMOGENEOUS
    ]
    not_derivable = [r for r in rows if r["key_direction"] == compat_direction.NOT_DERIVABLE]

    def named(items):
        return [
            {"page": r.get("page"), "outcome": r.get("outcome"), "dimension": r.get("dimension")}
            for r in items
        ]

    summary = {
        "over_claiming": {
            "n": len(over),
            "of_derivable": len(derivable),
            "statement": f"{len(over)} (page, dimension) over-claiming of {len(derivable)} derivable",
            "pages": named(over),
        },
        "under_claiming": {
            "n": len(under),
            "of_derivable": len(derivable),
            "statement": f"{len(under)} (page, dimension) under-claiming of {len(derivable)} derivable",
            "pages": named(under),
        },
        "not_derivable": {
            "n": len(not_derivable),
            "of_total": len(rows),
            "statement": f"{len(not_derivable)} NOT_DERIVABLE of {len(rows)}",
            "pages": named(not_derivable),
        },
    }
    out = {"summary": summary, "rows": rows}
    # Bytes with an explicit "\n": text mode on Windows would write CRLF into the served tree.
    args.out.write_bytes((json.dumps(out, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(summary["over_claiming"]["statement"])
    print(summary["under_claiming"]["statement"])
    print(summary["not_derivable"]["statement"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
