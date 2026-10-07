"""Plant: a served-pool refresh notice never enters a trial the served-pool register cannot admit. EXAMINE (dpp4 MACE)
is tracker-verified from the FDA label's 98% CI re-expressed at 95% (0.8209 to 1.1227); no held span prints those
numbers, so scripts/build_served_pool_additions.pipeline_row refuses the row and a signed notice naming it could never
be applied (the same never-matching class as V6-03/V6-04). The generator now excludes it with the register's reason."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_served_pool_notices as g  # noqa: E402


def _dpp4():
    return json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", "dpp4-mace-t2d.json"), encoding="utf-8"))


def test_examine_is_excluded_with_the_registers_reason():
    # TECOS is served since V6-01 (lifted 7 Oct); EXAMINE, re-expressed from a 98% CI, is the only remaining candidate and
    # is excluded -- so no notice is derived for dpp4 MACE at all
    n, exc = g.topic_notice(_dpp4())
    assert n is None
    why = [e["why"] for e in exc if e["trial"] == "EXAMINE"]
    assert why and "NOT_ADMISSIBLE_BY_REGISTER" in why[0] and "no verbatim span carries the effect and CI" in why[0]


def test_served_mace_equals_the_signed_v6_01_after():
    r = json.load(open(os.path.join(ROOT, "docs", "reviews", "dpp4-mace-t2d", "review.json"), encoding="utf-8"))
    m = next(o for o in r["outcomes"] if o["name"].startswith("3-point"))
    assert {k: m["result"][k] for k in ("k", "estimate", "ci_low", "ci_high")} ==         {"k": 4, "estimate": 1.0007, "ci_low": 0.8998, "ci_high": 1.1129}


def test_the_decision_is_recorded_and_examine_stays_out_of_the_served_pool():
    """D7 (Mahmood 7 Oct, 'agree'): re-expressed CIs are for MATCHING only, never a served pool."""
    d = json.load(open(os.path.join(ROOT, "registry", "g1_decisions.json"), encoding="utf-8"))
    dec = next(x for x in d["decisions"] if x["id"] == "D7-REEXPRESSED-CI-MATCHING-ONLY")
    assert dec["ratified"]["by"] == "Mahmood" and dec["ratified"]["quote"] == "agree"
    r = json.load(open(os.path.join(ROOT, "docs", "reviews", "dpp4-mace-t2d", "review.json"), encoding="utf-8"))
    mace = next(o for o in r["outcomes"] if o["name"].startswith("3-point"))
    assert "PMID 23992602" not in [str(t.get("id")) for t in mace.get("trials") or []]
