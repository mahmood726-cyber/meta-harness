"""PLANTS for the ARMS_COMBINED own tuple (scripts/g1_binding_aact.py C1-C6 + g1_tracker.arms_combined_check):
a multi-arm trial's dose arms are COMBINED against the one shared control by the Cochrane Handbook 6.5.2.10 formula,
never picked; the outcome is chosen by the topic (declared day, observed-case), and the tracker re-derives every arm,
role and the combination offline from the committed span."""
import copy
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))

import g1_binding_aact as ba  # noqa: E402

TOPIC = {"primary_outcome": {"name": "Observed-case Day-28 raw change-score MADRS MD", "estimand": "MD",
                             "keywords": ["madrs", "primary outcome"], "timepoint": "Day 28 double-blind induction endpoint"}}
AGENTS = ["esketamine"]
TITLES = {"g1": "Intranasal Esketamine 56 mg Plus Oral Antidepressant", "g2": "Intranasal Esketamine 84 mg Plus Oral AD",
          "g3": "Oral AD Plus Intranasal Placebo"}
OBS = "Change From Baseline in MADRS Total Score up to Day 28 of Double- Blind Induction Phase- MMRM Analysis"
LOCF = "Change From Baseline in MADRS Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- ANCOVA Analysis"


def _m(rows):
    return [{"result_group_id": g, "ctgov_group_code": c, "param_type": "MEAN", "param_value": m,
             "dispersion_type": "Standard Deviation", "dispersion_value": sd} for g, c, m, sd in rows]


MEAS = {"1": _m([("g1", "OG000", "-19.0", "13.86"), ("g2", "OG001", "-18.8", "14.12"), ("g3", "OG002", "-14.8", "15.07")]),
        "2": _m([("g1", "OG000", "-18.3", "14.21"), ("g2", "OG001", "-17.4", "14.25"), ("g3", "OG002", "-14.3", "15.00")])}
COUNTS = {"1": {"g1": "111", "g2": "98", "g3": "108"}, "2": {"g1": "115", "g2": "114", "g3": "113"}}
OUTCOMES = {"1": {"title": OBS, "population": "Full analysis set"}, "2": {"title": LOCF, "population": "Full analysis set"}}


def test_handbook_combination_matches_the_formula():
    n, m, sd = ba.combine_arms([(111, -19.0, 13.86), (98, -18.8, 14.12)])
    N = 209
    M = (111 * -19.0 + 98 * -18.8) / N
    SD = math.sqrt((110 * 13.86 ** 2 + 97 * 14.12 ** 2 + 111 * 98 / N * (19.0 ** 2 + 18.8 ** 2 - 2 * 19.0 * 18.8)) / (N - 1))
    assert n == N and abs(m - M) < 1e-12 and abs(sd - SD) < 1e-12
    assert ba.combine_arms([(10, 1.0, 2.0)]) == (10, 1.0, 2.0)               # one arm: unchanged


def test_the_topic_picks_the_observed_day_28_outcome_and_refuses_the_imputed_endpoint():
    ok, ref = ba.arm_candidates(MEAS, COUNTS, TITLES, OUTCOMES, TOPIC, AGENTS)
    assert [c["outcome_id"] for c in ok] == ["1"]
    assert ref == [{"outcome_id": "2", "title": LOCF, "gate": "C3_OBSERVED", "why": ref[0]["why"]}]
    v = ba.arms_values(ok[0]["arms"])
    assert (v["n_t"], v["mean_t"], v["n_c"], v["mean_c"], v["k_intervention_arms"]) == (209, "-18.9062", 108, "-14.8", 2)


def test_both_dose_arms_are_combined_never_one_picked():
    ok, _ = ba.arm_candidates(MEAS, COUNTS, TITLES, OUTCOMES, TOPIC, AGENTS)
    assert sorted(a["role"] for a in ok[0]["arms"]) == ["control", "intervention", "intervention"]
    assert ba.arms_values(ok[0]["arms"])["combination"] == "Cochrane Handbook 6.5.2.10"


def test_arm_gates_refuse():
    t2 = dict(TITLES, g2="Oral AD Plus Intranasal Placebo B")                  # two control arms
    ok, ref = ba.arm_candidates({"1": MEAS["1"]}, COUNTS, t2, {"1": OUTCOMES["1"]}, TOPIC, AGENTS)
    assert ok == [] and ref[0]["gate"] == "C5_ARMS"
    t3 = dict(TITLES, g2="Ketamine infusion")                                  # an arm that is neither
    ok, ref = ba.arm_candidates({"1": MEAS["1"]}, COUNTS, t3, {"1": OUTCOMES["1"]}, TOPIC, AGENTS)
    assert ok == [] and ref[0]["gate"] == "C5_ARMS"
    nod = {"1": dict(OUTCOMES["1"], title="Change From Baseline in MADRS Total Score at Week 4")}
    ok, ref = ba.arm_candidates({"1": MEAS["1"]}, COUNTS, TITLES, nod, TOPIC, AGENTS)
    assert ok == [] and ref[0]["gate"] == "C2_TIMEPOINT"
    nosd = {"1": [dict(r, dispersion_type="Standard Error") for r in MEAS["1"]]}
    ok, ref = ba.arm_candidates(nosd, COUNTS, TITLES, {"1": OUTCOMES["1"]}, TOPIC, AGENTS)
    assert ok == [] and ref[0]["gate"] == "C5_ARMS"


def _binding():
    ok, _ = ba.arm_candidates(MEAS, COUNTS, TITLES, OUTCOMES, TOPIC, AGENTS)
    arms = ok[0]["arms"]
    return {"slug": "esketamine-trd-madrs", "label": "Fedgchin 2019 (TRANSFORM-1)", "own_tuple": True,
            "tuple_kind": "ARMS_COMBINED", "source_kind": "AACT", "source": "AACT test", "values": ba.arms_values(arms),
            "arms": arms, "span": ba.arms_span(OBS, arms)}


def test_tracker_rederives_the_combination_and_refuses_tampering():
    import g1_tracker as gt
    b = _binding()
    ok, why, ours = gt.arms_combined_check("esketamine-trd-madrs", b)
    assert ok and ours["n_t"] == 209 and ours["mean_c"] == "-14.8" and "6.5.2.10" in why
    bad = copy.deepcopy(b)
    bad["span"] = bad["span"].replace("MEAN -19.0", "MEAN -21.0")             # a number not in the span
    assert gt.arms_combined_check("esketamine-trd-madrs", bad)[1].startswith("ARM_NOT_IN_SPAN")
    bad = copy.deepcopy(b)
    bad["values"] = dict(bad["values"], mean_t="-19.0000", sd_t="13.8600", n_t=111)   # one dose PICKED, not combined
    assert gt.arms_combined_check("esketamine-trd-madrs", bad)[1] == "ARMS_COMBINATION_NOT_REPRODUCED"
    bad = copy.deepcopy(b)
    ctl = next(a for a in bad["arms"] if a["role"] == "control")
    ctl["role"] = "intervention"                                               # control relabelled
    assert gt.arms_combined_check("esketamine-trd-madrs", bad)[1].startswith("ARM_ROLE_NOT_REDERIVED")
    assert gt.arms_combined_check("dpp4-mace-t2d", b)[1] == "ARMS_COMBINED_NOT_AN_MD_TOPIC"


def test_confirm_hook_admits_the_combined_arms_as_our_value(tmp_path):
    import g1_tracker as gt
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"bindings": [_binding()]}), encoding="utf-8")
    o = {"slug": "esketamine-trd-madrs", "trials": [{"label": "Fedgchin 2019 (TRANSFORM-1)", "route": "UNVERIFIED",
                                                    "comparator_row": {"measure": "MD", "effect": "-4.10", "lower": "-6.23",
                                                                       "upper": "-1.97", "n_t": 229, "n_c": 113}}]}
    assert gt.apply_confirm_bindings(o, str(p)) == ["Fedgchin 2019 (TRANSFORM-1)"]
    x = o["trials"][0]
    assert x["route"] == "PRIMARY" and x["our_value"]["mean_t"] == "-18.9062" and x["our_value"]["effect"] is None
    yi, vi = gt.sm.row_yi_vi(gt.as_row(x["our_value"], x["label"]))
    assert abs(yi - (-4.1062)) < 1e-3 and abs(vi - (13.9491 ** 2 / 209 + 15.07 ** 2 / 108)) < 1e-6
