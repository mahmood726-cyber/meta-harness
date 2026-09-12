"""Complete-evidence-base classification (answers 'is small k our limit or the question's?'). For each
topic with a same-scope comparator, compares our pooled k to the COMPARABLE comparator k (parity.json):
complete = we have >= the same-scope evidence (small k is the literature's limit); gap_small = 1-2 off
(bar-limited, decomposed on the page); gap_large = >=3 off (a genuinely larger literature; reason named)."""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build():
    p = json.load(open(os.path.join(ROOT, "docs", "parity.json"), encoding="utf-8"))
    prow = {r["slug"]: r for r in p if isinstance(r, dict) and r.get("slug")}
    complete, gap_small, gap_large = [], [], []
    for f in sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json"))):
        slug = os.path.basename(os.path.dirname(f))
        r = json.load(open(f, encoding="utf-8"))
        prim = next((o for o in r.get("outcomes", []) if o.get("primary")), None)
        k = (prim or {}).get("result", {}).get("k") if prim else None
        pr = prow.get(slug)
        if not k or not pr:
            continue
        ourk, compk = pr.get("our_k"), pr.get("comparable_comparator_k")
        if ourk is None or compk is None:
            continue
        entry = {"slug": slug, "our_k": ourk, "comparable_comparator_k": compk}
        if ourk >= compk:
            complete.append(entry)
        elif (compk - ourk) >= 3:
            gap_large.append(entry)
        else:
            gap_small.append(entry)
    return {"_doc": "Complete-evidence-base classification vs the comparable same-scope comparator k. "
                    "complete = small k is the LITERATURE'S limit (we have >= the same-scope evidence); "
                    "gap_small = bar-limited (decomposed on the page); gap_large = a genuinely larger "
                    "literature (reason named per topic).",
            "n_complete": len(complete), "n_gap_small": len(gap_small), "n_gap_large": len(gap_large),
            "complete": complete, "gap_small": gap_small, "gap_large": gap_large}


if __name__ == "__main__":
    d = build()
    json.dump(d, open(os.path.join(ROOT, "docs", "evidence_base.json"), "w", encoding="utf-8"), indent=1)
    print(f"complete={d['n_complete']} gap_small={d['n_gap_small']} gap_large={d['n_gap_large']}")
