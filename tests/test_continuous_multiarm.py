"""Regression test for the continuous verified_arms path with multi-arm combination (esketamine
TRANSFORM-1 cold-audit completion): a mean/SD/n override must pool as a mean-difference, and the
combined-dose-arm-vs-shared-placebo values must survive the MD estimand guard."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_esketamine_transform1_combined_arm_pooled():
    """The continuous multi-arm path: a mean/SD/n override pools as a mean difference, and TRANSFORM-1's combined-dose
    arm is in exactly one named state -- POOLED as continuous MD, or SET ASIDE with its candidate mean/SD tuple visible
    and a named reason. (Until 2026-09-20 this asserted k == 4 and 'CI now excludes 0'; the served interval now includes
    zero and that change carries a notice in docs/result_changes.json -- a test must protect the path, not the number.)"""
    r = json.load(open(os.path.join(ROOT, "docs", "reviews", "esketamine-trd-madrs", "review.json"), encoding="utf-8"))
    prim = next(o for o in r["outcomes"] if o.get("primary"))
    assert prim["result"]["scale"] == "MD" and prim["result"]["k"] == len(prim["trials"]) >= 1
    for t in prim["trials"]:
        assert t.get("mean1") is not None and t.get("sd1") is not None, f"{t.get('label')} pooled but not continuous"
    t1 = next((t for t in prim["trials"] if str(t.get("label")) == "TRANSFORM-1"), None)
    if t1 is None:
        a = next((x for x in prim.get("declared_absent_trials") or [] if "NCT02417064" in str(x.get("id")) or str(x.get("label")) == "TRANSFORM-1"), None)
        assert a is not None, "TRANSFORM-1 neither pooled nor set aside"
        assert a.get("reason_code") or a.get("state"), a
        assert (a.get("candidate_tuple") or {}).get("mean1") is not None, "the set-aside record must show the candidate mean/SD"


def test_esketamine_wrong_route_excluded():
    r = json.load(open(os.path.join(ROOT, "docs", "reviews", "esketamine-trd-madrs", "review.json"), encoding="utf-8"))
    inc = {str(x.get("id")) for x in r.get("screening", {}).get("records", []) if str(x.get("decision")) == "include"}
    for wrong in ("38523183", "42462931", "NCT03965858", "NCT01640080"):  # oral, oral, inhaled DPI, IV
        assert wrong not in inc, f"{wrong} is a wrong-route esketamine record and must be excluded"
