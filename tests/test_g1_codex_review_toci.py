"""Cross-vendor (codex) review of g1/tocilizumab.py (registry/model_proposals/g1_codex_review.json, record
mc-39a3c5d0...): each finding's OWN failing input, asserting the expected behaviour. All reproduced on the code before
the fix (the review's 'actual'); each passes after it."""
import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from g1 import tocilizumab as t  # noqa: E402

K = t._KEY


def _o(title, tf, rows, param="COUNT_OF_PARTICIPANTS", units=None):
    return {"outcomes": {"o": {"nct_id": "NCT04320615", "title": title, "time_frame": tf, "units": units,
                               "analysed": {"Tocilizumab": 100, "Placebo": 100},
                               "measurements": [{"row_id": str(i), "group": g, "classification": cls, "param_type": param,
                                                 "value": v} for i, (g, cls, v) in enumerate(rows)]}}}


def test_1_a_survival_estimate_never_establishes_a_count():
    ex = _o("Kaplan-Meier survival", "Day 28", [("Tocilizumab", "", "90"), ("Placebo", "", "80")], "NUMBER", "percent")
    rows = t.aact_28d("COVACTA", ex)
    assert all("%" in r["derivation"] for r in rows)              # labelled a derivation, never a stated count
    with patch.object(t, "held_texts", return_value=[]), patch.object(t, "vnh_candidates", return_value=[]), patch.object(t, "_META2", {}):
        assert t.assess("COVACTA", ex, metas={})["state"] != t.ESTABLISHED


def test_2_a_mixed_time_frame_is_not_day_28():
    ex = _o("Mortality", "Day 28 through day 60", [("Tocilizumab", "", "10"), ("Placebo", "", "20")])
    assert t.aact_28d("COVACTA", ex) == []


def test_3_alive_and_dead_categories_are_never_summed():
    ex = _o("Survival status", "Day 28", [("Tocilizumab", "Day 28: alive", "90"), ("Tocilizumab", "Day 28: dead", "10"),
                                          ("Placebo", "Day 28: alive", "80"), ("Placebo", "Day 28: dead", "20")])
    assert [tuple(r[k] for k in K) for r in t.aact_28d("COVACTA", ex)] == [(10, 100, 20, 100)]


def test_4_swapped_arms_in_the_text_conflict_with_the_registry():
    c = {"source": "AACT", "deaths_t": 10, "n_t": 100, "deaths_c": 20, "n_c": 100, "denominator_kind": t.RANDOMISED,
         "derivation": "count posted"}
    s = "By day 28, 20 of 100 patients died in the tocilizumab group and 10 of 100 patients died in the placebo group."
    with patch.object(t, "aact_28d", return_value=[c]), patch.object(t, "held_texts", return_value=[("PMID 1", s)]), patch.object(t, "vnh_candidates", return_value=[]), \
            patch.object(t, "_META2", {}):
        r = t.assess("COVACTA", {}, metas={})
    assert (r["state"], r["row"]) == (t.CONFLICT, None)


def test_5_a_stated_other_denominator_refutes_the_location():
    s = "By day 28, 10 (10%) of 101 tocilizumab patients and 20 (20%) of 101 placebo patients died."
    assert t.text_locates_how({"deaths_t": 10, "n_t": 100, "deaths_c": 20, "n_c": 100}, s) is None


def test_6_a_negated_death_word_does_not_make_counts_deaths():
    s = "By day 28, 10 of 100 tocilizumab patients and 20 of 100 placebo patients had fever; no deaths occurred."
    assert t.text_candidates(s) == []
    assert t.text_locates_how({"deaths_t": 10, "n_t": 100, "deaths_c": 20, "n_c": 100}, s) is None


def test_7_a_composite_table_row_is_not_mortality():
    assert t.table_candidates("Tocilizumab (n=100) Placebo (n=100) Ventilation or death at day 28 30 (30) 40 (40)") == []


def test_8_a_safety_captioned_death_row_is_no_efficacy_candidate():
    s = "Table 4 Adverse Events in the Safety Population Tocilizumab (n=100) Placebo (n=100) Death at day 28 10 (10) 20 (20)"
    assert t.table_candidates(s) == []


def test_9_equal_numbers_over_different_denominator_kinds_are_not_agreement():
    c = {"source": "AACT", "deaths_t": 10, "n_t": 100, "deaths_c": 20, "n_c": 100, "denominator_kind": t.ANALYSED,
         "derivation": "count posted"}
    s = "By day 28, 10 of 100 tocilizumab patients and 20 of 100 placebo patients died among all randomised patients."
    with patch.object(t, "aact_28d", return_value=[c]), patch.object(t, "held_texts", return_value=[("PMID 1", s)]), patch.object(t, "vnh_candidates", return_value=[]), \
            patch.object(t, "_META2", {}):
        r = t.assess("COVACTA", {}, metas={})
    assert r["state"] != t.ESTABLISHED
    assert sorted(x["denominator_kind"] for x in r["readings"]) == [t.ANALYSED, t.RANDOMISED]


def test_10_a_papers_stated_registration_beats_frequency():
    s = "Our trial registration is NCT04320615. References to another trial: NCT04381936; NCT04381936."
    with patch.object(t, "_HELD", {"1": s}), patch.object(t.os.path, "isdir", return_value=False):
        got = [(lab, [ref for ref, _ in t.held_texts(lab)]) for lab in ["COVACTA", "RECOVERY"]]
    assert got == [("COVACTA", ["PMID 1"]), ("RECOVERY", [])]


def test_11_an_unidentified_arm_is_no_row_not_a_crash():
    assert t.text_candidates("By day 28, tocilizumab: 10 of 100 patients died, whereas 20 of 100 patients died.") == []


def test_controls_real_statements_still_read():
    assert [tuple(r[k] for k in K) for r in t.table_candidates(
        "Tocilizumab group (n=65) Control group (n=64) ... Mortality up to 28 days 14 (21) 6 (9)")] == [(14, 65, 6, 64)]
    assert [tuple(r[k] for k in K) for r in t.text_candidates(
        "Overall, 621 (31%) of the 2022 patients allocated tocilizumab and 729 (35%) of the 2094 patients allocated to "
        "usual care died within 28 days (rate ratio 0.85; 95% CI 0.76-0.94; p=0.0028).")] == [(621, 2022, 729, 2094)]
    assert t.text_locates_how({"deaths_t": 58, "n_t": 294, "deaths_c": 28, "n_c": 144},
                              "Death was reported by day 28 in 58 patients (19.7%) in the tocilizumab group and in 28 "
                              "(19.4%) in the placebo group.")[1] == "STATED_COUNT"
