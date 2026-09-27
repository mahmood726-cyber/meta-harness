"""n of N: served X-CONTRAST exclusions that the arm-list fallback made, and why each flips under matched-placebo parsing.

usage: python evidence/matched_placebo/measure.py [<ref>]
N = every screening decision with rule_id X-CONTRAST in every served review at <ref> (default the pinned candidate).
For each whose basis lists the arms ("... another intervention: A; B; C"), the real harness.arm_parse decides whether
the intervention of interest is ACTIVELY in every arm, and names the arm that breaks "every arm":
  MATCHED_PLACEBO     -- "placebo for X", "placebo Circadin", "X placebo": a placebo matched to X read as exposure to X
  VARIES_WITHIN_ARM   -- "fish oil/fish oil placebo": two levels collapsed into one listed arm
  ABSENT              -- a plain "Placebo" arm, dropped before the old "every arm" test
Exclusions made by other routes (curated evictions, AACT arm index, arm-object background rules) are listed, not re-judged."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from harness import arm_parse   # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
MARK = "another intervention: "


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, check=True).stdout


def _decisions(o, out):
    if isinstance(o, dict):
        if "rule_id" in o and "decision" in o:
            out.append(o)
        for v in o.values():
            _decisions(v, out)
    elif isinstance(o, list):
        for v in o:
            _decisions(v, out)
    return out


def measure(ref=PINNED):
    slugs = sorted({p.split("/")[2] for p in _git("ls-tree", "-r", "--name-only", ref, "docs/reviews").decode().split()
                    if p.count("/") == 3 and p.endswith("review.json")})
    rows, seen = [], set()
    for slug in slugs:
        rv = json.loads(_git("show", f"{ref}:docs/reviews/{slug}/review.json"))
        topic = json.loads(_git("show", f"{ref}:topics/{slug}.json"))
        kws = topic.get("intervention_terms") or (topic.get("include") or {}).get("intervention_any") or []
        for d in _decisions(rv, []):
            key = (slug, str(d.get("id")))
            if d.get("rule_id") != "X-CONTRAST" or key in seen:
                continue
            seen.add(key)
            reason = d.get("reason") or ""
            row = {"slug": slug, "id": d.get("id"), "route": "arm-list fallback" if MARK in reason else "other route",
                   "reason": reason}
            if MARK in reason:
                arms = [a.strip() for a in reason.split(MARK, 1)[1].rstrip(". ").split(";") if a.strip()]
                states = {a: arm_parse.exposure(arm_parse.parse_arm(a), kws) for a in arms}
                row.update({"arms": states, "every_arm_active_now": arm_parse.interest_in_every_arm(arms, kws),
                            "broken_by": sorted({s for s in states.values() if s != "ACTIVE"})})
            rows.append(row)
    fallback = [r for r in rows if r["route"] == "arm-list fallback"]
    flips = [r for r in fallback if not r["every_arm_active_now"]]
    by = {k: [f"{r['slug']} {r['id']}" for r in flips if k in r["broken_by"]] for k in ("MATCHED_PLACEBO", "VARIES_WITHIN_ARM", "ABSENT")}
    return {"ref": ref, "x_contrast_exclusions": len(rows), "by_arm_list_fallback": len(fallback),
            "no_longer_every_arm": len(flips), "by_cause": {k: {"n": len(v), "trials": v} for k, v in by.items()}, "rows": rows}


if __name__ == "__main__":
    print(json.dumps(measure(*(sys.argv[1:2] or [PINNED])), indent=1, ensure_ascii=False))
