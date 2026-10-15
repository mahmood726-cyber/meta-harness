"""Plants for the formal GRADE rules (robgrade/grade_formal.py): each downgrade on constructed inputs whose answer is
fixed, the statistics against independent references, and the rules that keep a missing input from reading as a
favourable one."""
import math
import json
from pathlib import Path

import pytest

from robgrade import grade_formal as gf


def _rob(j):
    return {"overall": {"judgement": j}}


@pytest.mark.parametrize("unknown_se", (0.1, 100.0))
def test_unestablished_positive_weight_keeps_certainty_provisional(unknown_se):
    outcome = {"name": "fixture", "result": {"k": 2, "i2": 0, "scale": "RR",
               "ci_low": 0.8, "ci_high": 0.9}, "compat_key": {"matched": True},
               "trials": [{"id": name, "study_effect": {"standard_error": se}}
                          for name, se in (("A", 0.1), ("B", unknown_se))]}
    g = gf.grade(outcome, {"A": _rob("LOW"), "B": _rob("NOT_ESTABLISHED")},
                 counts=[{"events_t": 800, "n_t": 5000, "events_c": 1000, "n_c": 5000}])
    assert g["domains"]["risk_of_bias"]["state"] == "PARTIAL"
    assert g["certainty"] == "provisional"
    assert g["certainty_from_assessed_domains_only"] == "high"
    if unknown_se == 0.1:
        assert g["domains"]["risk_of_bias"]["inputs"]["weight_share_by_overall"]["NOT_ESTABLISHED"] == 0.5


def test_melatonin_partial_and_unresolved_judgements_remain_provisional():
    root = Path(__file__).resolve().parents[1]
    slug = "melatonin-primary-insomnia-sol"
    review = json.loads((root / "docs/reviews" / slug / "review.json").read_text(encoding="utf-8"))
    outcome = next(o for o in review["outcomes"] if o.get("primary"))
    from scripts.grade_formal_build import rob_for
    rob, _ = rob_for(slug, outcome["name"], [t["id"] for t in outcome["trials"]])
    g = gf.grade(outcome, rob)
    assert g["domains"]["risk_of_bias"]["inputs"]["weight_share_by_overall"]["HIGH"] == 1
    assert g["domains"]["imprecision"]["state"] == "PARTIAL"
    assert {"VERY_SERIOUS_FOR_JUDGEMENT", "OIS_NOT_COMPUTABLE"} <= set(g["judgement_flags"])
    assert g["certainty_from_assessed_domains_only"] == "moderate"
    assert g["certainty"] == "provisional"


def test_single_trial_dimension_conflict_is_labelled_conservative_policy():
    outcome = {"result": {"k": 1}, "trials": [{"id": "fixture"}],
               "compat_key": {"matched": True, "dimension_matches": {"analysis_set": False}}}
    d = gf.grade(outcome, {})["domains"]["indirectness"]
    assert d["flags"] == ["SOFT_HETEROGENEITY_FOR_JUDGEMENT"]
    assert "conservative policy" in d["basis"]
    assert "across trials" not in d["basis"]


@pytest.mark.parametrize("state,flags", [
    ("PARTIAL", []), ("ASSESSED", ["VERY_SERIOUS_FOR_JUDGEMENT"]),
    ("ASSESSED", ["OIS_NOT_COMPUTABLE"]),
    ("ASSESSED", ["SOFT_HETEROGENEITY_FOR_JUDGEMENT"]),
    ("ASSESSED", ["FUTURE_JUDGEMENT_FLAG"]),
])
def test_any_partial_or_unresolved_flag_blocks_certainty(monkeypatch, state, flags):
    outcome = {"result": {"k": 1, "scale": "RR", "ci_low": 0.8, "ci_high": 1.1},
               "compat_key": {"matched": True}}
    assert gf.grade(outcome, {})["certainty"] == "moderate"  # k < 10 alone does not block.
    monkeypatch.setattr(gf, "indirectness", lambda _: gf._dom(0, state, "fixture", {}, flags))
    g = gf.grade(outcome, {})
    assert g["certainty_from_assessed_domains_only"] == "moderate"
    assert g["certainty"] == "provisional"


def test_PLANT_rob_downgrades_when_less_than_half_the_weight_is_low():
    trials = [{"id": "A", "se": 0.1}, {"id": "B", "se": 0.2}]           # A carries 80% of the weight
    assert gf.risk_of_bias(trials, {"A": _rob("LOW"), "B": _rob("HIGH")}, 0)["downgrade"] == 0
    d = gf.risk_of_bias(trials, {"A": _rob("SOME_CONCERNS"), "B": _rob("LOW")}, 0)
    assert d["downgrade"] == 1 and d["inputs"]["weight_share_by_overall"]["SOME_CONCERNS"] == 0.8


def test_PLANT_a_trial_without_formal_rob_is_never_counted_as_low():
    trials = [{"id": "A", "se": 0.1}, {"id": "B", "se": 0.2}]
    d = gf.risk_of_bias(trials, {"A": _rob("LOW")}, 0)                  # B has no object
    assert d["state"] == "NOT_ASSESSABLE" and d["downgrade"] is None
    d = gf.risk_of_bias(trials, {"A": _rob("NOT_ESTABLISHED"), "B": _rob("LOW")}, 0)
    assert d["downgrade"] == 1                                         # 80% of the weight not established -> not low


def test_inconsistency_rules():
    t = [{"effect": 0.6, "ci_low": 0.5, "ci_high": 0.7}, {"effect": 1.5, "ci_low": 1.3, "ci_high": 1.8}]
    r = {"k": 2, "i2": 90, "ci_low": 0.6, "ci_high": 1.4, "pi_low": 0.2, "pi_high": 4}
    assert gf.inconsistency(r, t, "RR")["downgrade"] == 2               # opposite, non-overlapping CIs, I2 >= 75
    t2 = [{"effect": 0.6, "ci_low": 0.4, "ci_high": 0.9}, {"effect": 0.8, "ci_low": 0.6, "ci_high": 1.1}]
    r2 = {"k": 2, "i2": 60, "ci_low": 0.6, "ci_high": 0.9, "pi_low": 0.3, "pi_high": 1.6}
    assert gf.inconsistency(r2, t2, "RR")["downgrade"] == 1             # PI crosses the null, CI does not
    r3 = dict(r2, i2=20)
    assert gf.inconsistency(r3, t2, "RR")["downgrade"] == 0
    assert gf.inconsistency({"k": 1}, t2[:1], "RR")["state"] == "NOT_APPLICABLE"
    assert gf.inconsistency(r2, t2, "RR", stale=True)["state"] == "NOT_ASSESSABLE"


def test_indirectness_rules():
    assert gf.indirectness({"matched": True, "dimension_matches": {"endpoint": True}})["downgrade"] == 0
    d = gf.indirectness({"matched": True, "limitations": [{"code": "POP", "dimension": "population", "hard": True}]})
    assert d["downgrade"] == 1 and "population" in d["basis"]
    d = gf.indirectness({"matched": True, "dimension_matches": {"analysis_set": False}})
    assert d["downgrade"] == 0 and d["flags"] == ["SOFT_HETEROGENEITY_FOR_JUDGEMENT"]
    assert gf.indirectness(None)["state"] == "NOT_ASSESSABLE"


def test_PLANT_imprecision_rules_and_ois():
    assert gf.imprecision({"ci_low": 0.6, "ci_high": 1.4}, "RR")["downgrade"] == 2
    assert gf.imprecision({"ci_low": 0.8, "ci_high": 1.1}, "RR")["downgrade"] == 1
    assert gf.imprecision({"ci_low": -0.5, "ci_high": 0.2}, "MD")["downgrade"] == 1
    d = gf.imprecision({"ci_low": 0.7, "ci_high": 0.9}, "RR")
    assert d["state"] == "PARTIAL" and d["flags"] == ["OIS_NOT_COMPUTABLE"]
    # OIS by hand: p0 0.20, p1 0.15: (1.96+0.8416)^2 * (0.16 + 0.1275) / 0.05^2 = 902.6 -> 903 per arm
    assert gf.ois(0.20) == 1806
    small = [{"events_t": 15, "n_t": 100, "events_c": 20, "n_c": 100}]
    assert gf.imprecision({"ci_low": 0.7, "ci_high": 0.9}, "RR", small)["downgrade"] == 1
    big = [{"events_t": 150, "n_t": 1000, "events_c": 200, "n_c": 1000}]
    assert gf.imprecision({"ci_low": 0.7, "ci_high": 0.9}, "RR", big)["downgrade"] == 0


def test_egger_against_an_independent_fit():
    scipy_stats = pytest.importorskip("scipy.stats")
    trials = [{"effect": e, "se": s} for e, s in [(0.5, 0.30), (0.6, 0.25), (0.7, 0.20), (0.75, 0.15), (0.8, 0.12),
                                                  (0.85, 0.10), (0.9, 0.08), (0.92, 0.06), (0.95, 0.05), (0.97, 0.04),
                                                  (0.4, 0.35), (0.55, 0.28)]]
    e = gf.egger(trials, "RR")
    xs = [1 / t["se"] for t in trials]
    ys = [math.log(t["effect"]) / t["se"] for t in trials]
    res = scipy_stats.linregress(xs, ys)
    assert abs(e["intercept"] - res.intercept) < 1e-3
    assert abs(e["se"] - res.intercept_stderr) < 1e-3
    p_ref = 2 * scipy_stats.t.sf(abs(res.intercept / res.intercept_stderr), len(trials) - 2)
    assert abs(e["p"] - p_ref) < 1e-3


def test_PLANT_publication_bias_below_ten_is_not_assessable_and_never_downgraded():
    d = gf.publication_bias([{"effect": 0.8, "se": 0.1}] * 9, "RR")
    assert d["state"] == "NOT_ASSESSABLE_K_LT_10" and d["downgrade"] == 0


def test_certainty_is_provisional_while_a_domain_is_unassessed():
    outcome = {"name": "x", "result": {"k": 2, "i2": 0, "ci_low": 0.7, "ci_high": 0.9, "scale": "RR", "tau2": 0},
               "trials": [{"id": "A", "effect": 0.8, "ci_low": 0.6, "ci_high": 1.0, "study_effect": {"standard_error": 0.1}},
                          {"id": "B", "effect": 0.8, "ci_low": 0.6, "ci_high": 1.0, "study_effect": {"standard_error": 0.1}}],
               "compat_key": {"matched": True}}
    g = gf.grade(outcome, {"A": _rob("LOW")})                                 # B has no RoB object
    assert g["certainty"] == "provisional" and "risk_of_bias" in g["unassessed_domains"]
    # Arm counts make OIS computable and met, so imprecision is assessed.
    g = gf.grade(outcome, {"A": _rob("LOW"), "B": _rob("LOW")}, counts=[
        {"events_t": 800, "n_t": 5000, "events_c": 1000, "n_c": 5000},
        {"events_t": 800, "n_t": 5000, "events_c": 1000, "n_c": 5000},
    ])
    assert g["certainty"] == "high" and g["unassessed_domains"] == []
