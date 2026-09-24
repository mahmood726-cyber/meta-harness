"""Properties of the R2 measurer (regex_layer.measure): it compares VALUES, not typography, and it never turns a
partial number into agreement."""
from __future__ import annotations

from regex_layer import measure


def _claim(*instances):
    return {"states": bool(instances), "quote": None,
            "instances": [{"fields": [{"field": f, "quote": q} for f, q in inst.items()]} for inst in instances]}


def test_a_percent_quoted_with_its_sign_is_the_same_value_the_regex_captures():
    # plant #14 (fired before the fix: every _ARM / _ARM3 / _ARMP instance scored FP + FN, precision 0 of 27)
    s = "Death occurred in 20 (9%) of 220 patients."
    lab = _claim({"count": "20", "percent": "9%", "denominator": "220"})
    assert measure.verify_label(lab, s, "_ARM")["agreement"] == "RULE_MODEL_AGREE"
    m = measure.measure([("_ARM", s, lab)])["_ARM"]
    assert (m["tp"], m["fp"], m["fn"]) == (1, 0, 0)


def test_a_partial_number_is_never_agreement():
    # a thin-space thousands separator: the pattern reads '488' out of '48 488' -- that is a false positive AND a miss
    s = "The event occurred in 48 488 (98.1%) of 49 419 participants."
    lab = _claim({"count": "48 488", "percent": "98.1%", "denominator": "49 419"})
    m = measure.measure([("_ARM", s, lab)])["_ARM"]
    assert m["tp"] == 0 and m["fp"] >= 1 and m["fn"] == 1


def test_a_quote_not_in_the_sentence_is_refused():
    s = "Death occurred in 20 (9%) of 220 patients."
    lab = _claim({"count": "21", "percent": "9%", "denominator": "220"})
    assert measure.verify_label(lab, s, "_ARM")["state"] == "VERIFIER_REFUSED"


def test_a_percent_sign_is_only_stripped_from_a_percent_field():
    assert measure.norm_value("_ARM", "percent", "9 %") == "9"
    assert measure.norm_value("_ARM", "count", "9%") == "9%"


def test_the_queue_verifies_with_the_same_context_it_stores():
    # plant #15 (fired in the wild before the fix: 68 of 68 regex_label proposals VERIFIER_REFUSED 'PATTERN_UNKNOWN: None',
    # because cmd_queue handed reverify {"prior": ...} while storing a context that named the pattern)
    import importlib.util
    from pathlib import Path
    from reproducible_ai import model_source as ms
    spec = importlib.util.spec_from_file_location("_pilot", Path(__file__).resolve().parents[1] / "scripts" / "model_source_pilot.py")
    pilot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pilot)
    s = "Death occurred in 20 (9%) of 220 patients."
    item = {"pattern": "_ARM", "sample": "FIRES", "rule_decision": "regex sample FIRES", "held_text": s}
    ctx = pilot.queue_context(item)
    assert ctx["pattern"] == "_ARM"
    v = ms.reverify({"task": "regex_label", "claim": _claim({"count": "20", "percent": "9%", "denominator": "220"}),
                     "rule_decision": item["rule_decision"], "context": ctx}, s)
    assert v["state"] == "VERIFIER_PASS", v
    src = (Path(__file__).resolve().parents[1] / "scripts" / "model_source_pilot.py").read_text(encoding="utf-8")
    assert '"context": {"prior": i.get("prior")}' not in src, "a verifier call builds its own context again"


def test_a_percent_sign_on_either_side_of_a_rate_and_its_unit_is_the_same_value():
    # plant #17: _RATE_UNIT scored FP+FN when the label put '%' on the rate ('3.64%', 'per year') and the regex put it on
    # the unit ('3.64', '% per year') -- the same statement
    s = "The mortality rate was 4.13% per year in the warfarin group."
    lab = _claim({"rate": "4.13%", "unit": "per year"})
    m = measure.measure([("_RATE_UNIT", s, lab)])["_RATE_UNIT"]
    assert (m["tp"], m["fp"], m["fn"]) == (1, 0, 0), m
    # and a genuinely different unit still disagrees
    lab2 = _claim({"rate": "4.13", "unit": "per 100 patient-years"})
    assert measure.measure([("_RATE_UNIT", s, lab2)])["_RATE_UNIT"]["tp"] == 0


def test_a_percent_unit_on_a_mean_or_sd_is_typography_but_never_on_a_count():
    # plant #18: _MEAN_SD scored '43 +/- 4%' as FP+FN (label sd '4%', regex '4')
    assert measure.norm_value("_MEAN_SD", "sd", "4%") == "4"
    assert measure.norm_value("_MEAN_SD", "mean", "43 %") == "43"
    assert measure.norm_value("_ARMP", "count", "9%") == "9%"      # a count quoted with a % is a different thing
