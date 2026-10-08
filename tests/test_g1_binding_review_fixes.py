"""PLANTS for the captain's codex review of the binding lane (registry/model_proposals/pr_codex_review.json, ranges
merge-08315be6e and merge-bdfb19729): each defect class reproduced on the reviewer's own failing input, then fixed at
its source. Written BEFORE the fixes; each must fail on the unfixed code."""
import hashlib
import json
import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))

import g1_binding_aact as ba  # noqa: E402
import g1_tracker as gt  # noqa: E402


def _r(g, v, **kw):
    return dict({"result_group_id": g, "param_type": "MEAN", "dispersion_type": "Standard Deviation", "param_value": v,
                 "dispersion_value": "1"}, **kw)


TOPIC = {"primary_outcome": {"keywords": ["Score"], "timepoint": "Day 28"}}


# ---- g1#1 subgroup measurement rows are not arms ------------------------------------------------------------------
def test_g1_1_category_rows_of_one_group_are_refused():
    ok, ref = ba.arm_candidates({"o": [_r("t", "1", category="Male"), _r("t", "1", category="Female"), _r("c", "0")]},
                                {"o": {"t": "10", "c": "10"}}, {"t": "DrugX", "c": "Placebo"}, {"o": {"title": "Score Day 28"}},
                                TOPIC, ["DrugX"])
    assert ok == [] and ref[0]["gate"] == "C5_ARMS"


# ---- g1#2 a posted group with a denominator but no measurement --------------------------------------------------
def test_g1_2_a_posted_arm_without_a_measurement_refuses_the_outcome():
    ok, ref = ba.arm_candidates({"o": [_r("t1", "1"), _r("c", "0")]}, {"o": {"t1": "10", "t2": "20", "c": "10"}},
                                {"t1": "DrugX 10 mg", "t2": "DrugX 20 mg", "c": "Placebo"}, {"o": {"title": "Score Day 28"}},
                                TOPIC, ["DrugX"])
    assert ok == [] and ref[0]["gate"] == "C5_ARMS"


# ---- g1#3 imputation stated in the population field --------------------------------------------------------------
def test_g1_3_imputed_population_refused_for_an_observed_case_estimand():
    ok, ref = ba.arm_candidates(
        {"o": [_r("t", "2"), _r("c", "0")]}, {"o": {"t": "10", "c": "10"}}, {"t": "DrugX", "c": "Placebo"},
        {"o": {"title": "Score Day 28", "population": "Intention-to-treat population; missing values imputed using last "
                                                      "observation carried forward (LOCF)."}},
        {"primary_outcome": {"name": "Score, observed-case", "keywords": ["Score"], "timepoint": "Day 28"}}, ["DrugX"])
    assert ok == [] and ref[0]["gate"] == "C3_OBSERVED"


# ---- g1#4 'Placebo for <agent>' is the control -------------------------------------------------------------------
def test_g1_4_placebo_for_the_agent_is_control():
    assert ba.arm_role("Placebo for alogliptin", ["alogliptin"]) == "control"
    assert ba.arm_role("Matching placebo to esketamine", ["esketamine"]) == "control"
    assert ba.arm_role("Intranasal Esketamine plus oral placebo", ["esketamine"]) == "intervention"
    assert ba.arm_role("Oral AD Plus Intranasal Placebo", ["esketamine"]) == "control"


# ---- g1#5 / g2#3 absence of a comparator term is not an active control -------------------------------------------
def test_g1_5_unresolved_scope_is_never_written_as_an_exclusion(tmp_path):
    import g1_binding_enumerate as be
    (tmp_path / "held.txt").write_text("Trial A: DrugX versus unspecified control", encoding="utf-8")
    res = {"slug": "scope-test", "comparator_pmid": "100", "source": "held.txt", "open_question": "Comparator arm unresolved",
           "trials": [{"label": "Trial A", "ref": "1", "pmid": "200", "identity": "CONFIRMED",
                       "span": "Trial A: DrugX versus unspecified control", "arms": [], "scope": "UNCLEAR",
                       "reference": "Trial A report"}]}
    with patch.object(be, "ROOT", str(tmp_path)), patch.object(be, "ENUM_DIR", str(tmp_path)):
        p = be.write_input(res)
    u = json.load(open(p, encoding="utf-8"))["units"][0]
    assert u["scope"] != "OUT_OF_SCOPE" and u["rule_id"] is None


def test_g1_5_enumerator_names_an_active_control_only_when_one_is_printed():
    import g1_binding_enumerate as be
    assert be.arm_scope([{"drug": "Empagliflozin"}, {"drug": "Placebo"}], ["empagliflozin"], ["placebo"]) == "IN_SCOPE"
    assert be.arm_scope([{"drug": "Empagliflozin"}, {"drug": "Glimepiride"}], ["empagliflozin"], ["placebo"]) \
        == "OUT_OF_SCOPE:COMPARATOR_NOT_PLACEBO"
    for other in ([], [{"drug": "NR"}], [{"drug": "control"}], [{"drug": "not reported"}]):
        assert be.arm_scope([{"drug": "Empagliflozin"}] + other, ["empagliflozin"], ["placebo"]) == "UNRESOLVED"


def test_g2_3_tracker_refuses_e2_when_the_span_does_not_name_an_active_control(tmp_path):
    raw = b"Trial A: empagliflozin; comparator not reported."
    (tmp_path / "held.txt").write_bytes(raw)
    x = {"enumeration": {"scope": "OUT_OF_SCOPE", "rule_id": "E2:COMPARATOR_NOT_PLACEBO", "span": raw.decode(),
                         "source": "held.txt", "sha256": hashlib.sha256(raw).hexdigest(), "ref": "1"}}
    with patch.object(gt, "ROOT", str(tmp_path)):
        assert gt.enumeration_scope(x, {"comparator_terms": ["placebo"], "intervention_agents": ["empagliflozin"]}) is None
    raw2 = b"Trial B: empagliflozin 10 mg / glimepiride 4 mg"
    (tmp_path / "held2.txt").write_bytes(raw2)
    x2 = {"enumeration": {"scope": "OUT_OF_SCOPE", "rule_id": "E2:COMPARATOR_NOT_PLACEBO", "span": raw2.decode(),
                          "source": "held2.txt", "sha256": hashlib.sha256(raw2).hexdigest(), "ref": "2",
                          "arms": [{"drug": "empagliflozin"}, {"drug": "glimepiride"}]}}
    with patch.object(gt, "ROOT", str(tmp_path)):
        assert gt.enumeration_scope(x2, {"comparator_terms": ["placebo"], "intervention_agents": ["empagliflozin"]})


# ---- g1#6 the exception's pick is labelled as such -----------------------------------------------------------------
def test_g1_6_a_pick_that_needed_the_exception_is_labelled_so(tmp_path):
    import g1_comparator_select as cs
    files = {"x.rule.json": {"criteria": [{"id": "q"}], "tie_breaks": [{"id": "year"}], "if_none_pass": "STOP:no eligible candidate"},
             "x.candidates.json": {"candidates": [{"pmid": "101", "criteria": {"q": {"verdict": "PASS"}}, "tie_breaks": {"year": 2020}},
                                                  {"pmid": "202", "criteria": {"q": {"verdict": "FAIL"}}, "tie_breaks": {"year": 2021}}]},
             "x.ratification.json": {"ratified_exception": {"candidate_pmid": "202", "waived_criterion": "q", "decided_by": "Reviewer",
                                                            "quote": "Waive q for candidate 202", "date": "2026-10-05"}}}
    for n, d in files.items():
        (tmp_path / n).write_text(json.dumps(d), encoding="utf-8")
    with patch.object(cs, "SEL", str(tmp_path)), patch.object(cs, "rule_sha", lambda s: None):
        cs.main(["x"])
    out = json.load(open(tmp_path / "x.selection.json", encoding="utf-8"))
    if out["pick"]["pmid"] == "202":
        assert out["result"] == "PICKED_BY_RATIFIED_EXCEPTION" and out["result_under_preregistered_rule"] == "PICKED"
    else:
        assert out["result"] == "PICKED"


# ---- g2#1 typed comparator numbers must come from their span -------------------------------------------------------
def test_g2_1_typed_row_numbers_not_in_the_span_are_refused(tmp_path):
    raw = b"Trial A: HR 0.90 (95% CI 0.80-1.01)."
    (tmp_path / "held.txt").write_bytes(raw)
    d = {"comparator_pmid": "123", "source": {"path": "held.txt", "sha256": hashlib.sha256(raw).hexdigest()}, "rows": [
        {"label": "Trial A", "measure": "HR", "effect": "9.0", "lower": "8.0", "upper": "10.1", "span": raw.decode()}]}
    (tmp_path / "demo.json").write_text(json.dumps(d), encoding="utf-8")
    with patch.object(gt, "ROOT", str(tmp_path)), patch.object(gt, "TYPED_COMPARATOR_ROWS", str(tmp_path / "{slug}.json")):
        assert gt.typed_comparator_rows("demo", "123") is None
        good = dict(d, rows=[dict(d["rows"][0], effect="0.90", lower="0.80", upper="1.01")])
        (tmp_path / "demo.json").write_text(json.dumps(good), encoding="utf-8")
        assert gt.typed_comparator_rows("demo", "123")["rows"][0]["effect"] == "0.90"


def test_g2_1_real_typed_rows_still_verify():
    assert gt.typed_comparator_rows("dpp4-mace-t2d", "31462224")
    assert gt.typed_comparator_rows("denosumab-vertebral-fracture", "32492050")


# ---- g2#2 the adopted pooled result must be the one its span prints ------------------------------------------------
def test_g2_2_adoption_numbers_not_in_the_result_span_are_refused(tmp_path):
    raw = b"Two trials: pooled RR 0.90 (95% CI 0.80-1.01), random-effects DL model."
    (tmp_path / "held.txt").write_bytes(raw)

    def adopt(e, lo, hi, measure="RR"):
        a = {"comparator_type": "COMPARATOR_NO_PER_TRIAL_ROWS", "comparator_pmid": "123",
             "pooled_result": {"measure": measure, "estimate": e, "ci_low": lo, "ci_high": hi, "k": 2, "method_for_ours": "DL",
                               "source": {"path": "held.txt", "sha256": hashlib.sha256(raw).hexdigest()},
                               "spans": {"result": raw.decode()}}}
        (tmp_path / "demo.json").write_text(json.dumps(a), encoding="utf-8")
        with patch.object(gt, "ROOT", str(tmp_path)), patch.object(gt, "NO_ROWS_ADOPTION", str(tmp_path / "{slug}.json")):
            return gt.no_rows_adoption("demo", "123")
    assert adopt(9.0, 8.0, 10.1) is None
    assert adopt(0.90, 0.80, 1.01, measure="HR") is None
    assert adopt(0.90, 0.80, 1.01)["pooled_result"]["estimate"] == 0.90


def test_g2_2_real_adoption_still_verifies():
    assert gt.no_rows_adoption("statins-primary-prevention-elderly", "32529863")


# ---- g2#4 an enumerated PMID contradicted by the held reference ----------------------------------------------------
def test_g2_4_enumeration_pmid_contradicted_by_the_held_reference_is_refused(tmp_path):
    import k_gap_table as k
    span = "Smith 2020: empagliflozin versus placebo."
    raw = (span + "\nReference 1: Smith 2020. PMID 11111111.").encode()
    (tmp_path / "held.txt").write_bytes(raw)
    e = {"comparator_pmid": "123", "source": {"path": "held.txt", "sha256": hashlib.sha256(raw).hexdigest()},
         "units": [{"label": "Smith 2020", "span": span, "ref": "1", "pmid": "22222222", "identity": "CONFIRMED", "scope": "IN_SCOPE"}]}
    (tmp_path / "demo.json").write_text(json.dumps(e), encoding="utf-8")
    with patch.object(k, "ROOT", str(tmp_path)), patch.object(k, "ENUM_DIR", str(tmp_path)):
        assert k.enumeration_units("demo", ["empagliflozin"], "123") == []
        e["units"][0]["pmid"] = "11111111"
        (tmp_path / "demo.json").write_text(json.dumps(e), encoding="utf-8")
        assert k.enumeration_units("demo", ["empagliflozin"], "123")[0]["cited"][0]["pmid"] == "11111111"
        e["units"][0]["identity"] = "NOT_LOOKED_UP"
        (tmp_path / "demo.json").write_text(json.dumps(e), encoding="utf-8")
        assert k.enumeration_units("demo", ["empagliflozin"], "123") == []


# ---- bdfb19729 g1#1 _neg with an explicit '+' ---------------------------------------------------------------------
def test_neg_explicit_plus():
    assert gt._neg("+1.7") == "-1.7" and gt._neg("1.7") == "-1.7" and gt._neg("-12.71") == "12.71" and gt._neg("+0.00") == "0.00"


def test_g2_4_a_reference_list_pmid_counts_only_when_printed_in_the_held_source(tmp_path):
    import k_gap_table as k
    span = "Smith 2020: empagliflozin versus placebo."
    for printed, n in (("PMID 33333333", 1), ("no identifier", 0)):
        raw = (span + "\n29. Smith J. Title. 2020. " + printed).encode()
        (tmp_path / "held.txt").write_bytes(raw)
        e = {"comparator_pmid": "123", "source": {"path": "held.txt", "sha256": hashlib.sha256(raw).hexdigest()},
             "units": [{"label": "Smith 2020", "span": span, "ref": "29", "pmid": "33333333",
                        "identity": "COMPARATOR_REFERENCE_LIST_PMID", "scope": "IN_SCOPE"}]}
        (tmp_path / "demo.json").write_text(json.dumps(e), encoding="utf-8")
        with patch.object(k, "ROOT", str(tmp_path)), patch.object(k, "ENUM_DIR", str(tmp_path)):
            assert len(k.enumeration_units("demo", ["empagliflozin"], "123")) == n
