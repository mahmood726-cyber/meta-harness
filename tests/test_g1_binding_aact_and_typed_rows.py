"""PLANTS: (1) own-tuple EFFECT_CI from the trial's own posted results (scripts/g1_binding_aact.py) -- the outcome is
chosen by the topic's gates, a 4-point composite / per-protocol / one-sided CI are refused, ambiguity refuses;
(2) typed comparator rows (g1_tracker.apply_typed_comparator_rows) -- digest + spans re-checked, comparator side only;
(3) the confirm hook takes an own-tuple EFFECT_CI as our value only when effect and both bounds are verbatim."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))

import g1_binding_aact as ba  # noqa: E402

TOPIC = "3-point major adverse cardiovascular events"
KW = ["major adverse cardiovascular events", "MACE", "primary outcome", "hazard ratio"]


def _reg(outcomes, analyses):
    return {"outcomes": {o["id"]: o for o in outcomes}, "analyses": analyses}


def test_aact_binder_takes_the_itt_3_point_outcome_only():
    reg = _reg([{"id": "1", "title": "First Confirmed CV Event of MACE Plus (Including Hospitalization for Unstable Angina)"},
                {"id": "2", "title": "First Confirmed CV Event of MACE (Per Protocol Population)"},
                {"id": "3", "title": "First Confirmed CV Event of MACE (Intent to Treat Population)"}],
               [{"outcome_id": k, "param_type": "Hazard Ratio (HR)", "param_value": v, "ci_lower": "0.89", "ci_upper": "1.1",
                 "analysis_id": "a" + k} for k, v in (("1", "0.98"), ("2", "0.99"), ("3", "0.99"))])
    desc = {"1": "CV composite endpoint of MACE plus hospitalization for unstable angina",   # the real TECOS wording
            "2": "CV-related death, nonfatal MI, or nonfatal stroke", "3": "CV-related death, nonfatal MI, or nonfatal stroke"}
    ok, ref = ba.candidates(reg, desc, TOPIC, KW, "HR")
    assert [c["outcome_id"] for c in ok] == ["3"]
    assert {r["gate"] for r in ref} == {"A2_ESTIMAND", "A4_POPULATION"}


def test_aact_binder_refuses_a_one_sided_ci_and_generic_titles():
    reg = _reg([{"id": "1", "title": "Primary Major Adverse Cardiac Events (MACE)"}, {"id": "2", "title": "Primary Outcome"}],
               [{"outcome_id": "1", "param_type": "Hazard Ratio (HR)", "param_value": "0.962", "ci_lower": "", "ci_upper": "1.16"},
                {"outcome_id": "2", "param_type": "Hazard Ratio (HR)", "param_value": "0.9", "ci_lower": "0.8", "ci_upper": "1.0"}])
    ok, ref = ba.candidates(reg, {"1": "CV death, nonfatal MI, nonfatal stroke"}, TOPIC, KW, "HR")
    assert ok == [] and ref[0]["gate"] == "A3_ANALYSIS"            # 'Primary Outcome' never matched: generic keyword


def test_typed_comparator_rows_only_set_the_comparator_side(tmp_path, monkeypatch):
    import g1_tracker as gt
    rows = json.load(open(os.path.join(ROOT, "registry", "comparator_rows", "denosumab-vertebral-fracture.json"), encoding="utf-8"))
    assert gt.typed_comparator_rows("denosumab-vertebral-fracture", "32492050")
    assert gt.typed_comparator_rows("denosumab-vertebral-fracture", "36852077") is None       # another comparator
    bad = dict(rows, rows=[dict(rows["rows"][0], span=rows["rows"][0]["span"].replace("164", "999"))] + rows["rows"][1:])
    (tmp_path / "denosumab-vertebral-fracture.json").write_text(json.dumps(bad), encoding="utf-8")
    monkeypatch.setattr(gt, "TYPED_COMPARATOR_ROWS", str(tmp_path / "{slug}.json"))
    assert gt.typed_comparator_rows("denosumab-vertebral-fracture", "32492050") is None       # a span not in its source
    monkeypatch.undo()
    o = {"slug": "denosumab-vertebral-fracture", "comparator_pmid": "32492050", "same_trials": {},
         "trials": [{"label": "Cummings 2009 (FREEDOM)", "in_our_pool": True, "route": "PRIMARY", "g1_countable": True,
                     "our_value": {"measure": "RR", "effect": "0.32", "lower": "0.26", "upper": "0.41"}},
                    {"label": "Bone 2008", "in_our_pool": False, "route": "NO_ROW"}]}
    st = gt.apply_typed_comparator_rows(o)
    assert st["state"] == "ONE_SHARED_TRIAL" and st["verdict"]["verdict"] == "AGREE"
    assert o["trials"][1]["comparator_row"]["events_t"] == 0 and not o["trials"][1].get("our_value")   # never ours


def test_confirm_hook_takes_an_own_tuple_effect_ci(tmp_path):
    import g1_tracker as gt
    o = {"slug": "dpp4-mace-t2d", "trials": [{"label": "TECOS", "route": "NO_ROW", "comparator_row": None}]}
    b = {"slug": "dpp4-mace-t2d", "label": "TECOS", "own_tuple": True, "tuple_kind": "EFFECT_CI", "source_kind": "AACT",
         "source": "AACT x", "values": {"measure": "HR", "effect": "0.99", "lower": "0.89", "upper": "1.1"},
         "span": "MACE (Intent to Treat) | CV death, nonfatal MI, nonfatal stroke | Hazard Ratio (HR) 0.99 [0.89, 1.1]"}
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"bindings": [b]}), encoding="utf-8")
    assert gt.apply_confirm_bindings(o, str(p)) == ["TECOS"]
    x = o["trials"][0]
    assert x["route"] == "PRIMARY" and x["our_value"]["effect"] == "0.99" and x["our_value"]["lower"] == "0.89"
    o2 = {"slug": "dpp4-mace-t2d", "trials": [{"label": "TECOS", "route": "NO_ROW", "comparator_row": None}]}
    p.write_text(json.dumps({"bindings": [dict(b, span=b["span"].replace("0.89", "0.88"))]}), encoding="utf-8")
    assert gt.apply_confirm_bindings(o2, str(p)) == []            # a bound not verbatim in the span: not admitted


def test_a2b_refuses_an_extra_component_even_without_the_word_composite():
    reg = _reg([{"id": "1", "title": "MACE Plus (Including Hospitalization for Unstable Angina)"}],
               [{"outcome_id": "1", "param_type": "Hazard Ratio (HR)", "param_value": "0.98", "ci_lower": "0.88", "ci_upper": "1.09"}])
    ok, ref = ba.candidates(reg, {"1": "Time to first event"}, TOPIC, KW, "HR")
    assert ok == [] and ref[0]["gate"] == "A2_ESTIMAND" and "A2b" in ref[0]["why"]


# ---- the EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH false-positive class (TECOS, dpp4-mace-t2d) -------------------------
TECOS_3PT = ("Percentage of Participants With First Confirmed CV Event of MACE (Intent to Treat Population) | CV composite "
             "endpoint of MACE which includes CV-related death, nonfatal MI, or nonfatal stroke. | Hazard Ratio (HR) 0.99 [0.89, 1.1]")
TECOS_4PT = ("Percentage of Participants With First Confirmed CV Event of Major Adverse Cardiovascular Event (MACE) Plus (Intent "
             "to Treat Population) | Primary composite CV endpoint of MACE plus which includes CV-related death, nonfatal MI, "
             "nonfatal stroke, or unstable angina requiring hospitalization. | Hazard Ratio (HR) 0.98 [0.89, 1.08]")


def _tecos_o():
    return {"slug": "dpp4-mace-t2d", "trials": [{"label": "TECOS", "route": "NO_ROW", "comparator_row": None,
                                                 "absent_code": "EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH",
                                                 "our_refusal": "declared absent (estimand mismatch): TECOS's primary is a FOUR-point composite"}]}


def _bind(o, tmp_path, span, effect, lower, upper, own=True):
    import g1_tracker as gt
    b = {"slug": "dpp4-mace-t2d", "label": "TECOS", "own_tuple": own, "tuple_kind": "EFFECT_CI", "source_kind": "AACT",
         "source": "AACT NCT00790205", "values": {"measure": "HR", "effect": effect, "lower": lower, "upper": upper}, "span": span}
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"bindings": [b]}), encoding="utf-8")
    return gt.apply_confirm_bindings(o, str(p))


def test_tecos_registered_3_point_tuple_is_not_vetoed_by_the_4_point_refusal(tmp_path):
    o = _tecos_o()
    assert _bind(o, tmp_path, TECOS_3PT, "0.99", "0.89", "1.1") == ["TECOS"]
    x = o["trials"][0]
    assert x["route"] == "PRIMARY" and x["our_value"]["effect"] == "0.99" and x["estimand_refusal_superseded"]


def test_a_true_4_point_mace_tuple_is_still_refused(tmp_path):
    o = _tecos_o()
    assert _bind(o, tmp_path, TECOS_4PT, "0.98", "0.89", "1.08") == []
    assert o["trials"][0]["confirm_binding"]["why"] == "TYPED_REFUSAL:EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH"


def test_the_veto_is_lifted_only_for_own_tuples_and_only_on_3_point_mace_topics(tmp_path):
    import g1_tracker as gt
    o = _tecos_o()
    assert _bind(o, tmp_path, TECOS_3PT, "0.99", "0.89", "1.1", own=False) == []          # comparator-keyed: never lifted
    assert gt.own_tuple_establishes_estimand("dpp4-mace-t2d", TECOS_3PT)
    assert not gt.own_tuple_establishes_estimand("dpp4-mace-t2d", "MACE | CV death or stroke | HR 1.0 [0.9, 1.1]")  # no MI
    assert not gt.own_tuple_establishes_estimand("esketamine-trd-madrs", TECOS_3PT)        # not a 3-point MACE topic
