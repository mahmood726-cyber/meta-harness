"""Run the meta-analysis error library against every live review and report coverage:
how many documented mistakes each review is screened against, and how many remain unchecked.

    python scripts/error_coverage.py            # writes docs/error_coverage.json, prints summary

The claim "this review is screened against N of M documented meta-analysis errors" is a claim no
published meta-analysis makes, and it is exactly measurable here because each library entry names an
enforced mechanism (a gate limb / regression test / rendered disclosure). NOT_CHECKED entries are the
work queue and are reported as the gap, never counted as coverage.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import error_library as EL  # noqa: E402


def main():
    reviews_dir = os.path.join(ROOT, "docs", "reviews")
    rows = []
    for slug in sorted(os.listdir(reviews_dir)):
        rp = os.path.join(reviews_dir, slug, "review.json")
        cp = os.path.join(ROOT, "topics", slug + ".json")
        if not os.path.exists(rp):
            continue
        review = json.load(open(rp, encoding="utf-8"))
        config = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}
        n_active, n_checkable, ids = EL.coverage(review, config)
        rows.append({"slug": slug, "screened_against": n_active,
                     "checkable_total": n_checkable, "active_ids": ids})
    summ = EL.summary()
    out = {
        "library_size": summ["total"],
        "by_kind": {k: v for k, v in summ.items() if k != "total"},
        "not_checked": [{"id": i, "label": l, "note": n} for i, l, n in EL.not_checked()],
        "per_review": rows,
        "min_screened": min((r["screened_against"] for r in rows), default=0),
        "max_screened": max((r["screened_against"] for r in rows), default=0),
    }
    with open(os.path.join(ROOT, "docs", "error_coverage.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Error library: {summ['total']} documented meta-analysis mistakes")
    print(f"  by kind: {out['by_kind']}")
    print(f"  checkable (enforced mechanism): {rows[0]['checkable_total'] if rows else 0}")
    print(f"  NOT yet checked (work queue): {len(out['not_checked'])}")
    for nc in out["not_checked"]:
        print(f"    - {nc['id']} {nc['label']}")
    print(f"  every live review is screened against {out['min_screened']}"
          + (f"-{out['max_screened']}" if out['max_screened'] != out['min_screened'] else "")
          + f" of {rows[0]['checkable_total'] if rows else 0} checkable documented errors "
          f"(across {len(rows)} reviews)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
