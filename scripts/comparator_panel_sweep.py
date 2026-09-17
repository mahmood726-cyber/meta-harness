"""Offline corpus measurement; the base is explicit and the live pool is authoritative."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import comparator_panel as cp

BASE = "3cf73885ffc83f6fcc4db273c6510a5416cdcde0"


def build():
    rows = []
    for path in sorted((ROOT / "docs/reviews").glob("*/review.json")):
        r = json.loads(path.read_text(encoding="utf-8"))
        panel = r.get("comparator_panel", [])
        hp = path.with_name("index.html")
        before = subprocess.check_output(["git", "show", f"{BASE}:{hp.relative_to(ROOT).as_posix()}"], cwd=ROOT).decode("utf-8")
        after = hp.read_text(encoding="utf-8")
        rows.append({"slug": path.parent.name, "comparators": len(panel),
                     "held": sum(c["held"] for c in panel),
                     "enumerated": sum(bool(c.get("trial_set")) for c in panel),
                     "jaccard_gt_0_5": sum(any((o["jaccard"] or 0) > .5 for o in cp.overlaps(c, r)) for c in panel if c.get("trial_set")),
                     "forbidden_before": bool(cp.forbidden_claims(before)),
                     "forbidden_after": bool(cp.forbidden_claims(after, panel)),
                     "gate_reasons": cp.gate_reasons(r, after)})
    return {"measurement": "MEASURED", "base": BASE, "pages": len(rows),
            "comparators": sum(r["comparators"] for r in rows), "held": sum(r["held"] for r in rows),
            "enumerated": sum(r["enumerated"] for r in rows),
            "jaccard_gt_0_5": sum(r["jaccard_gt_0_5"] for r in rows),
            "pages_forbidden_before": sum(r["forbidden_before"] for r in rows),
            "pages_forbidden_after": sum(r["forbidden_after"] for r in rows),
            "phrase_count_definition": "Literal prohibited stems in visible page text, excluding only the mandated adjudicated sentence. Includes legacy negative statements; not all literal matches assert independence.",
            "rows": rows}


if __name__ == "__main__":
    result = build()
    (ROOT / "docs/comparator_panel_sweep.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))
