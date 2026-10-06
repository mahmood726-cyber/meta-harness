"""Plants (6 Oct, forest lane): the third-reader AUDIT of an accepted comparator figure compares an independent codex
reading with the ACCEPTED agreed rows and pooled row by the reader's own agreement rule (printed rounding; counts exact).
It reports; it never changes an acceptance."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_forest_reader as gfr  # noqa: E402

ACC = [{"label": "TRIAL A", "effect": "0.80", "lower": "0.60", "upper": "1.07", "events_t": 10, "n_t": 100,
        "events_c": 12, "n_c": 99},
       {"label": "TRIAL B", "effect": "1.10", "lower": "0.90", "upper": "1.34", "events_t": None, "n_t": None,
        "events_c": None, "n_c": None}]
POOL = {"effect": "0.95", "lower": "0.80", "upper": "1.12"}


def _reading(rows, pooled):
    return {"legible": True, "row_kind": "study", "rows": rows, "pooled": pooled, "measure": "RR"}


def test_identical_reading_audits_clean():
    a = gfr.audit_compare(ACC, POOL, _reading([dict(r) for r in ACC], dict(POOL)))
    assert a["state"] == "AUDIT_AGREES" and a["disagreements"] == [] and a["rows_agreeing"] == 2


def test_a_count_difference_a_missing_row_and_a_pooled_difference_are_findings():
    rows = [dict(ACC[0], events_t=11)]                       # TRIAL A count differs; TRIAL B missing
    a = gfr.audit_compare(ACC, POOL, _reading(rows, dict(POOL, effect="0.97")))
    assert a["state"] == "AUDIT_DISAGREES"
    whys = {d["label"]: d["why"] for d in a["disagreements"]}
    assert "EVENTS_T_DISAGREES" in whys["TRIAL A"] and whys["TRIAL B"] == "ONLY_IN_ACCEPTED"
    assert a["pooled"]["state"] == "POOLED_DISAGREES"


def test_rounding_within_printed_precision_is_agreement():
    rows = [dict(ACC[0], effect="0.8"), dict(ACC[1])]
    assert gfr.audit_compare(ACC, POOL, _reading(rows, dict(POOL)))["state"] == "AUDIT_AGREES"


def test_a_zero_count_agrees_with_zero_whatever_its_json_type():
    # 'str(x or "")' turned the NUMBER 0 into '' (zero is falsy): every zero-event row read as a disagreement
    assert gfr.agree_count(0, "0") == (True, 0)
    assert gfr.agree_count(0, 0) == (True, 0)
    assert gfr.agree_count("0", 0) == (True, 0)
    assert gfr.agree_count(None, None) == (True, None)
    assert gfr.agree_count(0, None)[0] is False


def test_audit_scope_selects_accepted_figures_of_that_section_only():
    o = {"results": {"s1": {"state": "ACCEPTED"}, "s2": {"state": "REFUSED"}},
         "meta_results": {"s1::11": {"state": "ACCEPTED"}, "s1::12::F2": {"state": gfr.SECOND_SOURCE_ONLY},
                          "s1::13": {"state": "REFUSED"}}}
    assert sorted(gfr.audit_targets(o, "comparator")) == ["s1"]
    assert sorted(gfr.audit_targets(o, "meta")) == ["s1::11", "s1::12::F2"]
