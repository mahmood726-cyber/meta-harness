"""Deterministic comparator SELECTION from a pre-registered rule (registry/comparator_selection/<slug>.rule.json).

A candidate is eligible only when EVERY criterion is PASS (an UNCLEAR or FAIL fails it). Eligible candidates are ordered
by the rule's tie-breaks, in order, each descending. The rule's commit SHA is recorded with the pick. Nothing about our
own pool is read.

    python scripts/g1_comparator_select.py SLUG   -> prints the pick; writes <slug>.selection.json beside the rule
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEL = os.path.join(ROOT, "registry", "comparator_selection")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def eligible(rule, cand):
    ids = [c["id"] for c in rule["criteria"]]
    verdicts = {c["id"]: (cand.get("criteria") or {}).get(c["id"], {}).get("verdict") for c in rule["criteria"]}
    return all(verdicts.get(i) == "PASS" for i in ids), verdicts


def order_key(rule, cand):
    tb = cand.get("tie_breaks") or {}
    return tuple(-(tb.get(t["id"]) if isinstance(tb.get(t["id"]), (int, float)) else float("-inf"))
                 for t in rule["tie_breaks"])


def select(rule, cands):
    ok = [c for c in cands if eligible(rule, c)[0]]
    if not ok:
        return None, []
    ranked = sorted(ok, key=lambda c: order_key(rule, c))
    return ranked[0], ranked


def rule_sha(slug):
    p = os.path.relpath(os.path.join(SEL, f"{slug}.rule.json"), ROOT)
    r = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%H", "--", p], capture_output=True, text=True)
    return r.stdout.strip() or None


def main(argv):
    slug = argv[0]
    rule = _j(os.path.join(SEL, f"{slug}.rule.json"))
    cands = _j(os.path.join(SEL, f"{slug}.candidates.json"))["candidates"]
    pick, ranked = select(rule, cands)
    out = {"slug": slug, "rule": f"registry/comparator_selection/{slug}.rule.json", "rule_commit": rule_sha(slug),
           "n_candidates": len(cands), "n_eligible": len(ranked),
           "pick": ({k: pick.get(k) for k in ("pmid", "pmcid", "title", "year")} if pick else None),
           "ranking": [{"pmid": c.get("pmid"), "tie_breaks": c.get("tie_breaks")} for c in ranked],
           "per_candidate": [{"pmid": c.get("pmid"), "eligible": eligible(rule, c)[0],
                              "verdicts": eligible(rule, c)[1]} for c in cands],
           "result": "PICKED" if pick else rule["if_none_pass"].split(":")[0]}
    p = os.path.join(SEL, f"{slug}.selection.json")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("rule_commit", "n_candidates", "n_eligible", "pick", "result")}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
