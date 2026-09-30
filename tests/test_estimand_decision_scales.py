"""estimand_decision must always resolve to a real pooling scale, and must never cross the odds boundary.

REVIEW2 R2: a literal compound estimand ('RR/HR') used verbatim as the target reached the pool as an unsupported scale
and silently removed GRADE's imprecision downgrade for spironolactone, with no numeric change to flag it.
"""
from harness.source_hierarchy import estimand_decision

HR = {"effect": 0.8, "scale": "HR"}
RR = {"effect": 0.8, "scale": "RR"}
OR = {"effect": 0.8, "scale": "OR"}
REAL = {"RR", "HR", "OR", "MD", "SMD"}


def test_compound_estimand_resolves_to_a_real_scale():
    assert estimand_decision({"estimand": "RR/HR"}, [HR, RR])["target_scale"] == "HR"
    assert estimand_decision({"estimand": "RR/HR"}, [RR])["target_scale"] == "RR"
    assert estimand_decision({"estimand": "RR/HR"}, [])["target_scale"] == "RR"


def test_within_family_typing_is_the_pre_existing_one():
    # RR target with a published HR types the outcome time-to-first-event, as before the odds-boundary change.
    assert estimand_decision({"estimand": "RR"}, [HR])["target_scale"] == "HR"
    assert estimand_decision({"estimand": "HR"}, [RR])["target_scale"] == "HR"


def test_odds_target_is_immutable():
    # The removed branch re-targeted an OR protocol to HR/RR when only HR/RR were published: never again.
    for cands in ([HR], [RR], [HR, RR], []):
        d = estimand_decision({"estimand": "OR"}, cands)
        assert d["target_scale"] == "OR" and d["decision"] == "odds"
    # And a risk/rate target is never re-targeted to OR by an OR-only candidate set.
    assert estimand_decision({"estimand": "RR"}, [OR])["target_scale"] == "RR"


def test_every_decision_is_a_supported_scale():
    for est in ("RR", "HR", "OR", "RR/HR", "MD", "SMD", "hazard ratio"):
        for cands in ([], [HR], [RR], [OR], [HR, RR, OR]):
            assert estimand_decision({"estimand": est}, cands)["target_scale"] in REAL, (est, cands)
