"""Assemble the 84 pooled trial-outcome numbers into batches for DUAL INDEPENDENT EXTRACTION: Fable
locates each span independently; deterministic code then parses a number from the model's span and
compares to the served number. Agreement => two independent extractions (the Cochrane/PRISMA dual-
extraction requirement, currently missing). Disagreement => flag for hand review.

Writes scratchpad/dual_batch_<n>.json (a list of {slug,pmid,outcome,abstract,det}) and
scratchpad/dual_index.json (the served numbers to compare against). No model calls here.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "scratchpad")


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    base = os.path.join(ROOT, "docs", "reviews")
    items = []
    for slug in sorted(os.listdir(base)):
        rp = os.path.join(base, slug, "review.json")
        cp = os.path.join(ROOT, "cache", slug, "records.json")
        if not (os.path.exists(rp) and os.path.exists(cp)):
            continue
        recs = {r["id"]: r for r in json.load(open(cp, encoding="utf-8"))["records"]}
        rev = json.load(open(rp, encoding="utf-8"))
        for o in rev.get("outcomes", []):
            for t in o.get("trials", []) or []:
                pid = str(t.get("id", "")).replace("PMID ", "").strip()
                ab = (recs.get(pid) or {}).get("abstract", "")
                if not ab:
                    continue  # aact_verified / no-abstract handled separately
                det = {k: t.get(k) for k in ("ai", "n1i", "ci", "n2i", "e1i", "e2i", "mean1", "mean2",
                                             "effect", "scale") if t.get(k) is not None}
                items.append({"slug": slug, "pmid": pid, "outcome": o.get("name"),
                              "abstract": ab, "det": det, "provenance": t.get("provenance")})
    # batches of ~12
    n = 12
    batches = [items[i:i + n] for i in range(0, len(items), n)]
    for bi, b in enumerate(batches):
        # strip abstracts to a compact file the model reads; keep det out of the model's file
        model_in = [{"key": f"{x['slug']}|{x['pmid']}|{x['outcome']}", "outcome": x["outcome"],
                     "abstract": x["abstract"]} for x in b]
        json.dump(model_in, open(os.path.join(SCRATCH, f"dual_batch_{bi}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    json.dump({f"{x['slug']}|{x['pmid']}|{x['outcome']}": x for x in items},
              open(os.path.join(SCRATCH, "dual_index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"assembled {len(items)} pooled trial-outcome numbers into {len(batches)} batches in {SCRATCH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
