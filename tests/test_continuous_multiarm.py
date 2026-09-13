"""Regression test for the continuous verified_arms path with multi-arm combination (esketamine
TRANSFORM-1 cold-audit completion): a mean/SD/n override must pool as a mean-difference, and the
combined-dose-arm-vs-shared-placebo values must survive the MD estimand guard."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_esketamine_transform1_combined_arm_pooled():
    r = json.load(open(os.path.join(ROOT, "docs", "reviews", "esketamine-trd-madrs", "review.json"), encoding="utf-8"))
    prim = next(o for o in r["outcomes"] if o.get("primary"))
    labels = [str(t.get("label")) for t in prim["trials"]]
    assert "TRANSFORM-1" in labels, "TRANSFORM-1 combined-dose arm not pooled"
    t1 = next(t for t in prim["trials"] if str(t.get("label")) == "TRANSFORM-1")
    assert t1.get("mean1") is not None and t1.get("sd1") is not None, "TRANSFORM-1 not continuous"
    assert prim["result"]["scale"] == "MD" and prim["result"]["k"] == 4
    # conclusion change: CI now excludes 0 (a modest but real benefit)
    assert prim["result"]["ci_high"] < 0, "esketamine CI should exclude 0 after TRANSFORM-1"


def test_esketamine_wrong_route_excluded():
    r = json.load(open(os.path.join(ROOT, "docs", "reviews", "esketamine-trd-madrs", "review.json"), encoding="utf-8"))
    inc = {str(x.get("id")) for x in r.get("screening", {}).get("records", []) if str(x.get("decision")) == "include"}
    for wrong in ("38523183", "42462931", "NCT03965858", "NCT01640080"):  # oral, oral, inhaled DPI, IV
        assert wrong not in inc, f"{wrong} is a wrong-route esketamine record and must be excluded"
