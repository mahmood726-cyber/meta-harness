"""n of N: served X3 "no eligible comparator" exclusions, and which flip when the comparator is read from the ARMS.

usage: python evidence/matched_placebo/measure_x3_comparator.py [<ref>]
N = every served screening decision at <ref> with rule X3 and reason "no eligible comparator". For each, the held record is
re-screened with the CURRENT harness.screen.screen_record (arm-based comparator recognition). A flip is named with the arms read
and the contrast found; the new decision is whatever the full screen now says (a flip past X3 can still stop at a later rule)."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from harness import screen   # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, check=True).stdout


def measure(ref=PINNED):
    slugs = sorted({p.split("/")[2] for p in _git("ls-tree", "-r", "--name-only", ref, "docs/reviews").decode().split()
                    if p.count("/") == 3 and p.endswith("review.json")})
    rows = []
    for slug in slugs:
        rv = json.loads(_git("show", f"{ref}:docs/reviews/{slug}/review.json"))
        topic = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
        recs = {}
        for path in (f"cache/{slug}/records.json", f"docs/cache/{slug}/records.json"):
            try:
                blob = json.loads(_git("show", f"{ref}:{path}"))
            except subprocess.CalledProcessError:
                continue
            for r in (blob.get("records") or []) + (blob.get("ctgov") or []):
                recs[str(r.get("id"))] = r
            break
        for d in (rv.get("screening") or {}).get("records") or []:
            if d.get("rule_id") != "X3" or "no eligible comparator" not in str(d.get("reason") or ""):
                continue
            rid = str(d.get("id")).split(" · ")[-1].replace("PMID ", "")
            rec = recs.get(rid)
            if rec is None:
                rows.append({"slug": slug, "id": d.get("id"), "state": "RECORD_NOT_HELD"})
                continue
            rec = dict(rec)
            rec.setdefault("id_type", "nct" if rid.upper().startswith("NCT") else "pmid")
            abc = screen._arm_based_comparator(rec, topic.get("include") or {})
            new = screen.screen_record(rec, topic.get("include") or {}, set(topic.get("negative_control_pmids") or []))
            rows.append({"slug": slug, "id": d.get("id"), "arm_based_comparator": abc,
                         "new_decision": [new[0], new[1]], "new_reason": new[2][:240],
                         "flips_past_x3": not (new[1] == "X3" and "no eligible comparator" in new[2])})
    flips = [r for r in rows if r.get("flips_past_x3")]
    return {"ref": ref, "x3_no_comparator": len(rows), "flip_past_x3": len(flips),
            "now_include": sum(1 for r in flips if r["new_decision"][0] == "include"), "rows": rows}


if __name__ == "__main__":
    out = measure(*(sys.argv[1:2] or [PINNED]))
    print(json.dumps(out, indent=1, ensure_ascii=False))
