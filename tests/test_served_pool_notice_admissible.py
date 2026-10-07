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
    n, exc = g.topic_notice(_dpp4())
    assert n is not None and n["entered_pool"] == ["PMID 26052984"]
    assert n["after"]["k"] == 4
    why = [e["why"] for e in exc if e["trial"] == "EXAMINE"]
    assert why and "NOT_ADMISSIBLE_BY_REGISTER" in why[0] and "no verbatim span carries the effect and CI" in why[0]


def test_tecos_alone_reproduces_the_signed_v6_01_after():
    n, _ = g.topic_notice(_dpp4())
    assert n["after"] == {"k": 4, "estimate": 1.0007, "ci_low": 0.8998, "ci_high": 1.1129}
