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


def eligible(rule, cand, exception=None):
    """All criteria PASS -- except ONE criterion waived for ONE named candidate by a RATIFIED exception (decided_by,
    quote, date recorded); every other criterion must still PASS. A waiver never applies to any other candidate."""
    ids = [c["id"] for c in rule["criteria"]]
    verdicts = {c["id"]: (cand.get("criteria") or {}).get(c["id"], {}).get("verdict") for c in rule["criteria"]}
    waived = None
    if exception and str(cand.get("pmid")) == str(exception.get("candidate_pmid")) and exception.get("decided_by") \
            and exception.get("quote") and exception.get("date"):
        waived = exception.get("waived_criterion")
    return all(verdicts.get(i) == "PASS" or i == waived for i in ids), verdicts


def order_key(rule, cand):
    tb = cand.get("tie_breaks") or {}
    return tuple(-(tb.get(t["id"]) if isinstance(tb.get(t["id"]), (int, float)) else float("-inf"))
                 for t in rule["tie_breaks"])


def r0(rule, cands):
    """Rule R0 (pre-registered 6 Oct): the CURRENT comparator, assessed like every candidate, is KEPT when it passes every
    criterion and RETIRED (failing criteria + evidence recorded) otherwise. None when the rule has no R0."""
    cur = (rule.get("R0_current_comparator") or {}).get("comparator_pmid")
    if not cur:
        return None
    c = next((x for x in cands if str(x.get("pmid")) == str(cur)), None)
    if c is None:
        return {"comparator_pmid": cur, "verdict": "RETIRE", "failing": [{"criterion": "NOT_ASSESSED", "verdict": None,
                                                                         "evidence": "the current comparator is not in the candidates file"}]}
    ok, verdicts = eligible(rule, c)
    fail = [{"criterion": k, "verdict": v, "evidence": ((c.get("criteria") or {}).get(k) or {}).get("evidence")}
            for k, v in verdicts.items() if v != "PASS"]
    return {"comparator_pmid": cur, "verdict": "KEEP" if ok else "RETIRE", "failing": fail}


def select(rule, cands, exception=None):
    # the comparator being REPLACED (rule.replaces.excluded_from_candidates) is listed but never picked; under R0 the
    # current comparator is the replaced one whenever R0 retires it
    ex = str((rule.get("replaces") or {}).get("comparator_pmid")) if (rule.get("replaces") or {}).get("excluded_from_candidates") else None
    if ex is None and (rule.get("R0_current_comparator") or {}).get("comparator_pmid"):
        ex = str(rule["R0_current_comparator"]["comparator_pmid"])
    ok = [c for c in cands if eligible(rule, c, exception)[0] and str(c.get("pmid")) != ex]
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
    rp = os.path.join(SEL, f"{slug}.ratification.json")
    exc = _j(rp).get("ratified_exception") if os.path.exists(rp) else None
    r0v = r0(rule, cands)
    if r0v and r0v["verdict"] == "KEEP":                 # R0: a current comparator that passes is never swapped
        cur = next(c for c in cands if str(c.get("pmid")) == str(r0v["comparator_pmid"]))
        out = {"slug": slug, "rule": f"registry/comparator_selection/{slug}.rule.json", "rule_commit": rule_sha(slug),
               "n_candidates": len(cands), "R0": r0v, "pick": {k: cur.get(k) for k in ("pmid", "pmcid", "title", "year")},
               "result": "NO_SWAP_CURRENT_COMPARATOR_PASSES", "ranking": [], "per_candidate": []}
        with open(os.path.join(SEL, f"{slug}.selection.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False)
        print(json.dumps({k: out[k] for k in ("rule_commit", "n_candidates", "pick", "result")}, ensure_ascii=False))
        return
    pick0, _ = select(rule, cands)                       # the pre-registered rule alone, always recorded
    pick, ranked = select(rule, cands, exc)
    out = {"slug": slug, "rule": f"registry/comparator_selection/{slug}.rule.json", "rule_commit": rule_sha(slug),
           "n_candidates": len(cands), "n_eligible": len(ranked),
           "pick": ({k: pick.get(k) for k in ("pmid", "pmcid", "title", "year")} if pick else None),
           "ranking": [{"pmid": c.get("pmid"), "tie_breaks": c.get("tie_breaks")} for c in ranked],
           "per_candidate": [{"pmid": c.get("pmid"), "eligible_under_rule": eligible(rule, c)[0],
                              "eligible_with_ratified_exception": eligible(rule, c, exc)[0],
                              "verdicts": eligible(rule, c)[1]} for c in cands],
           "result_under_preregistered_rule": "PICKED" if pick0 else rule["if_none_pass"].split(":")[0],
           "ratified_exception": exc, "R0": r0v,
           # the final winner's label says whether IT needed the exception (codex review merge-08315be6e:g1#6): an
           # exception that changes the winner is PICKED_BY_RATIFIED_EXCEPTION even when another candidate passes
           "result": ("PICKED" if pick and pick0 and str(pick.get("pmid")) == str(pick0.get("pmid"))
                      else "PICKED_BY_RATIFIED_EXCEPTION" if pick else rule["if_none_pass"].split(":")[0])}
    p = os.path.join(SEL, f"{slug}.selection.json")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("rule_commit", "n_candidates", "n_eligible", "pick", "result")}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
