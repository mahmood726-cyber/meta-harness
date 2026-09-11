"""EXTRACTION FILL-RATE MATRIX (the "zero silent gaps" measurement).

For every included trial x every protocol outcome, the cell is one of:
  FILLED         — a pooled number with provenance (abstract / ctgov / full-text / aact_verified),
  DECLARED_ABSENT — named in declared_absent_trials with a reason (the source(s) tried and what
                    each returned), which is a RESULT, not a gap,
  SILENT_GAP     — the trial was screened in for the topic but this outcome neither pooled it nor
                    declared it absent — the ONE state that must be zero.

Reports per-topic fill rate (FILLED / cells) and, crucially, the count of SILENT_GAP cells (target 0).
Writes docs/fill_matrix.json. Read-only; regenerable.

  python scripts/fill_matrix.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    base = os.path.join(ROOT, "docs", "reviews")
    out, tot_filled, tot_absent, tot_silent = {}, 0, 0, 0
    for slug in sorted(os.listdir(base)):
        rp = os.path.join(base, slug, "review.json")
        if not os.path.exists(rp):
            continue
        rev = json.load(open(rp, encoding="utf-8"))
        # screened-in trials for this topic (the row universe)
        included = set()
        for d in (rev.get("screening") or {}).get("records", []) or []:
            if d.get("decision") == "include":
                # record id may carry an acronym prefix "ACRONYM · 12345"; take the trailing token
                rid = str(d.get("id", "")).split("·")[-1].strip()
                included.add(rid)
        filled = absent = silent = 0
        per_outcome = {}
        for o in rev.get("outcomes", []):
            pooled = {str(t.get("id", "")).replace("PMID ", "").strip() for t in (o.get("trials") or [])}
            dabs = {str(a.get("id", "")).replace("PMID ", "").strip() for a in (o.get("declared_absent_trials") or [])}
            f = len(pooled)
            a = len(dabs)
            # silent = screened-in trials neither pooled nor declared-absent for this outcome
            accounted = pooled | dabs
            sil = len([r for r in included if r not in accounted]) if included else 0
            filled += f; absent += a; silent += sil
            per_outcome[o.get("name", "?")] = {"filled": f, "declared_absent": a, "silent_gap": sil}
        cells = filled + absent + silent
        out[slug] = {"filled": filled, "declared_absent": absent, "silent_gap": silent,
                     "cells": cells, "fill_rate": round(filled / cells, 3) if cells else None,
                     "accounted_rate": round((filled + absent) / cells, 3) if cells else None,
                     "per_outcome": per_outcome}
        tot_filled += filled; tot_absent += absent; tot_silent += silent
    json.dump(out, open(os.path.join(ROOT, "docs", "fill_matrix.json"), "w", encoding="utf-8",
                        newline=""), indent=1, ensure_ascii=False)
    print(f"{'topic':42} {'filled':6} {'absent':6} {'silent':6} fill_rate accounted")
    for s, v in out.items():
        print(f"{s:42} {v['filled']:<6} {v['declared_absent']:<6} {v['silent_gap']:<6} "
              f"{str(v['fill_rate']):9} {v['accounted_rate']}")
    tot = tot_filled + tot_absent + tot_silent
    print(f"\nTOTAL cells {tot}: filled {tot_filled}, declared-absent {tot_absent}, SILENT_GAP {tot_silent}")
    print(f"accounted (filled+declared) = {round(100*(tot_filled+tot_absent)/tot,1)}%  "
          f"(the 'zero silent gaps' target is SILENT_GAP == 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
