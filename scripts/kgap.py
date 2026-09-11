"""Target metric: our k vs the comparator's k, per live topic, with the shortfall cause named.

Run: python scripts/kgap.py            # all live topics
     python scripts/kgap.py <slug>     # one topic

Shortfall buckets (per primary outcome), all derived from committed artefacts:
  pooled                 : k contributing to the pooled estimate
  found-screened-out     : records the search returned that screening EXCLUDED
  published-unextractable: screened-IN, has an abstract, yet no poolable number extracted
                           (upper bound on extraction defects -- each needs verifying vs source,
                            because a trial reporting a DIFFERENT outcome is correctly absent)
  registry-only          : screened-IN but NCT-only / no abstract = ongoing / no results (correct)
theirs_k is the comparator's k where machine-extractable, else 'NS' (a measurement gap:
the comparator trial-list has not been extracted -- itself a to-do, not a zero).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def diagnose(slug):
    rev = json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))
    cache = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
    recs = {x["id"]: x for x in cache.get("records", [])}
    prim = next((o for o in rev["outcomes"] if o.get("primary")), rev["outcomes"][0])
    ours = (prim.get("result") or {}).get("k") or 0
    theirs = (rev.get("comparator", {}).get("overlap", {}) or {}).get("theirs_k")
    theirs = theirs if isinstance(theirs, int) else None
    pub_unext = reg_only = 0
    for t in prim.get("declared_absent_trials", []) or []:
        pid = str(t.get("id", "")).replace("PMID ", "")
        r = recs.get(pid)
        if r and (r.get("abstract") or "").strip():
            pub_unext += 1
        else:
            reg_only += 1
    screened_out = sum(1 for r in rev.get("screening", {}).get("records", []) if r["decision"] == "exclude")
    return {"slug": slug, "ours_k": ours, "theirs_k": theirs,
            "gap": (theirs - ours) if theirs is not None else None,
            "pooled": len(prim.get("trials") or []),
            "published_unextractable": pub_unext, "registry_only": reg_only,
            "found_screened_out": screened_out}


def main(argv):
    slugs = [argv[1]] if len(argv) > 1 else sorted(os.listdir(os.path.join(ROOT, "docs", "reviews")))
    rows = [diagnose(s) for s in slugs]
    print(f"{'topic':40} {'ours':4} {'theirs':6} {'gap':4} | pooled  pub-unext  reg-only  scr-out")
    so = to = 0
    for r in rows:
        t = str(r["theirs_k"]) if r["theirs_k"] is not None else "NS"
        g = str(r["gap"]) if r["gap"] is not None else "?"
        if r["theirs_k"] is not None:
            so += r["ours_k"]; to += r["theirs_k"]
        print(f"{r['slug']:40} {r['ours_k']:<4} {t:6} {g:4} | {r['pooled']:^6} "
              f"{r['published_unextractable']:^9} {r['registry_only']:^8} {r['found_screened_out']:^7}")
    measurable = [r for r in rows if r["theirs_k"] is not None]
    print(f"\ncomparator-k measurable: {len(measurable)}/{len(rows)}  (NS = comparator trial-list not yet extracted)")
    print(f"where measurable: sum ours={so}  sum theirs={to}")
    print("pub-unext is an UPPER BOUND on extraction defects; verify each vs source before calling it a miss.")


if __name__ == "__main__":
    main(sys.argv)
