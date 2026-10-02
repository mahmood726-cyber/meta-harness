"""PLANTS for READERS_DIFFER adjudication (scripts/g1_forest_adjudicate.py) and its use by the lane importer
(scripts/g1_import_lanes.apply_resolutions). Offline: readings are constructed."""
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_forest_adjudicate as adj  # noqa: E402
import g1_import_lanes as gil  # noqa: E402

CASE = copy.deepcopy(adj.CASES[0])


def reading(log_hr="-0.2877", se="0.073", mark="†", weight="39.2%", upper="0.87"):
    return {"found": True, "label": "EMPEROR-Reduced", "footnote_mark": mark, "log_hr": log_hr, "se": se,
            "weight_pct": weight, "hr": "0.75", "lower": "0.65", "upper": upper, "notes": ""}


def test_arithmetic_resolves_when_the_printed_SE_is_unambiguous():
    c = dict(CASE, undisputed={"effect": "0.75", "lower": "0.65"})
    v = adj.decide(c, reading(se="0.0730"), reading(se="0.0730"))        # 4 dp: upper 0.8653 +/- tiny -> 0.87 only
    assert v["state"] == "RESOLVED" and v["resolved"] == {"upper": "0.87"}
    assert v["agrees_with"] == {"reader1": CASE["earlier"]["reader1"]["record_id"]}


def test_PLANT_ambiguous_at_printed_rounding_is_refused_not_guessed():
    v = adj.decide(CASE, reading(), reading())                           # SE 0.073 (3 dp) admits 0.86 and 0.87
    assert v["state"] == "REFUSED" and v["problems"] == ["UPPER_AMBIGUOUS_AT_PRINTED_ROUNDING:['0.86', '0.87']"]


def test_PLANT_readers_disagreeing_on_SE_or_the_wrong_row_are_refused():
    assert adj.decide(CASE, reading(), reading(se="0.081"))["problems"] == ["SE_DISAGREES_OR_NOT_NUMERIC"]
    v = adj.decide(CASE, reading(log_hr="-0.3567", se="0.0700"), reading(log_hr="-0.3567", se="0.0700"))
    assert v["state"] == "REFUSED" and any(p.startswith("COMPUTED_EFFECT") for p in v["problems"])   # HR 0.70: not it


def _res(a, b):
    return {CASE["case"]: dict(adj.decide(CASE, a, b), case=CASE, records={"codex": "mc-x", "agy": "mc-y"}),
            "probe": {"state": "REFUSED", "case": "probe"}}


def test_identity_resolution_sets_aside_the_reader_whose_mark_and_weight_contradict_the_row():
    res = adj.identity_resolution(_res(reading(), reading()))
    r = res[CASE["case"]]
    assert r["state"] == "RESOLVED_BY_ROW_IDENTITY" and r["resolved"] == {"upper": "0.87"}
    assert list(r["wrong_row_readers"]) == ["reader2"] and list(r["agrees_with"]) == ["reader1"]


def test_PLANT_identity_never_overrides_the_arithmetic():
    """New readers agreeing on a value the row's own log[HR]/SE cannot give are refused, identity or not."""
    res = adj.identity_resolution(_res(reading(upper="0.89"), reading(upper="0.89")))
    assert res[CASE["case"]]["state"] == "REFUSED"


def test_PLANT_new_readers_who_disagree_on_identity_resolve_nothing():
    res = adj.identity_resolution(_res(reading(), reading(mark="‡", weight="30.7%")))
    assert res[CASE["case"]]["state"] == "REFUSED"


def test_importer_applies_a_resolution_and_names_a_rounding_boundary(tmp_path):
    res = adj.identity_resolution(_res(reading(), reading()))
    p = tmp_path / "res.json"
    p.write_text(json.dumps({"resolutions": res}), encoding="utf-8")
    lane = {"trials": [{"label": "EMPEROR‐Reduced (n = 3730)", "in_our_pool": True,
                        "agreement_with_comparator_row": "READERS_DIFFER:result=DISAGREE/result_reader2=AGREE",
                        "comparator_row": None,
                        "our_value": {"measure": "HR", "effect": "0.75", "lower": "0.65", "upper": "0.86",
                                      "events_t": None, "n_t": None, "events_c": None, "n_c": None}}]}
    untouched = copy.deepcopy(lane)
    o = gil.apply_resolutions("sglt2-hfref-hosp-cvdeath", lane, path=str(p))
    x = o["trials"][0]
    assert x["agreement_with_comparator_row"] == "DISAGREE" and x["comparator_row"]["upper"] == "0.87"
    assert x["disagreement_side"].startswith("ROUNDING_BOUNDARY") and o["per_trial_agreement"] == {"DISAGREE": 1}
    # control: another topic's lane row is never touched
    o2 = gil.apply_resolutions("other-topic", untouched, path=str(p))
    assert o2["trials"][0]["agreement_with_comparator_row"].startswith("READERS_DIFFER")
