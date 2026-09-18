"""Measure scale/adjustment labels in every rebuilt review against the specified HRM base."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import adjustment

BASE = "3cf73885ffc83f6fcc4db273c6510a5416cdcde0"


def main():
    rows = []
    for path in sorted((ROOT / "docs/reviews").glob("*/review.json")):
        review = json.loads(path.read_text(encoding="utf-8"))
        old = json.loads(subprocess.check_output(["git", "show", f"{BASE}:{path.relative_to(ROOT).as_posix()}"], cwd=ROOT))
        old_rows = {(o["name"], t.get("id")): t for o in old["outcomes"] for t in o.get("trials", [])}
        for outcome in review["outcomes"]:
            for trial in outcome.get("trials", []):
                design = trial.get("design") or {}
                if not str(design.get("estimator_source", "")).startswith("PUBLISHED_"):
                    continue
                before = old_rows.get((outcome["name"], trial.get("id")), {}).get("design", {})
                axis = adjustment.axis_for_trial(trial)
                rows.append({"slug": path.parent.name, "outcome": outcome["name"], "id": trial.get("id"),
                             "old_label": before.get("estimator_source"), "label": design.get("estimator_source"),
                             "adjustment_status": design.get("adjustment_status"),
                             "span_backed": axis["status"] in {"ADJUSTED", "UNADJUSTED"},
                             "axis": axis})
    result = {"base": BASE, "denominator": "published per-outcome trial rows in all docs/reviews/*/review.json",
              "N": len(rows), "n_rows_relabelled_UNRESOLVED": sum(r["old_label"] in {"PUBLISHED_ADJUSTED", "PUBLISHED_UNADJUSTED"}
                  and r["adjustment_status"] == "UNRESOLVED" for r in rows),
              "n_with_span_backed_status": sum(r["span_backed"] for r in rows), "rows": rows}
    (ROOT / "docs/adjustment_label_sweep.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{result['n_rows_relabelled_UNRESOLVED']} rows relabelled UNRESOLVED of {result['N']}; "
          f"{result['n_with_span_backed_status']} with a span-backed status of {result['N']}")


if __name__ == "__main__":
    main()
