"""PLANTS for G1 confirm-unverified (scripts/g1_confirm_bind.py + g1_tracker.apply_confirm_bindings). Each negative is a
shape met on the real UNVERIFIED rows (3 Oct): event counts that are not patients (HEART-FID '297 and 332
hospitalizations'), percentages with no counts (Wright 'n=41 ... 12.2% diarrhoea'), a count written as a word
(Cindoruk 'Nine (14.5%)'), and a subgroup span."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / "scripts"))

import g1_confirm_bind as cb  # noqa: E402
import g1_tracker as gt  # noqa: E402

TERMS = ["diarrhoea", "diarrhea"]


def trial(label="Trial A", **cr):
    return {"label": label, "route": "UNVERIFIED", "comparator_row": cr}


def run(monkeypatch, text, x, terms=TERMS):
    monkeypatch.setattr(cb.smb, "primary_sources", lambda slug, p, nct=None: [("text", f"PMID {p} abstract", text)])
    return cb.bind_one("topic", x, ["111"], [], terms)


COUNTS = dict(events_t="4", n_t="41", events_c="5", n_c="45", measure="RR")


def test_counts_printed_as_fractions_bind(monkeypatch):
    b, why = run(monkeypatch, "RESULTS: Acute diarrhoea occurred in 4/41 patients in the experimental group and "
                              "5/45 in the control group.", trial(**COUNTS))
    assert why == "BOUND" and b["tuple_kind"] == "COUNTS" and b["source_kind"] == "TEXT"
    assert b["agreement_with_comparator_row"] == "NOT_INDEPENDENT:SEARCH_KEYED_BY_COMPARATOR_ROW"


def test_event_counts_that_are_not_patient_fractions_do_not_bind(monkeypatch):
    b, _ = run(monkeypatch, "1532 were assigned to drug and 1533 to placebo; a total of 297 and 332 hospitalizations "
                            "for diarrhoea occurred.", trial(events_t="297", n_t="1532", events_c="332", n_c="1533",
                                                             measure="RR"))
    assert b is None


def test_percentages_without_counts_do_not_bind(monkeypatch):
    b, _ = run(monkeypatch, "41 received the active product (12.2% diarrhoea) and 46 received placebo (8.7% "
                            "diarrhoea); mean duration 4 and 5 days.", trial(events_t="5", n_t="41", events_c="4",
                                                                             n_c="46", measure="RR"))
    assert b is None


def test_count_written_as_a_word_does_not_bind(monkeypatch):
    b, _ = run(monkeypatch, "Nine (14.5%) patients of 62 in the treatment group and 19 of 62 in the placebo group "
                            "experienced diarrhoea.", trial(events_t="9", n_t="62", events_c="19", n_c="62",
                                                            measure="RR"))
    assert b is None


def test_subgroup_span_is_refused(monkeypatch):
    b, why = run(monkeypatch, "In the subgroup of women, diarrhoea occurred in 4/41 versus 5/45.", trial(**COUNTS))
    assert b is None and why.startswith("SUBGROUP_OR_POST_HOC_SPAN")


def test_row_with_no_typed_tuple_is_not_searched(monkeypatch):
    b, why = run(monkeypatch, "diarrhoea 4/41 vs 5/45", trial(measure="RR"))
    assert b is None and why == "COMPARATOR_ROW_HAS_NO_TYPED_TUPLE"


# ---- the tracker hook ----------------------------------------------------------------------------------------------

def _bindings(tmp_path, **b):
    p = tmp_path / "bindings.json"
    p.write_text(json.dumps({"bindings": [dict({"slug": "topic", "label": "Trial A", "source_kind": "TEXT",
                                                "source": "PMID 111 abstract", "tuple_kind": "COUNTS",
                                                "values": {"events_t": 4, "n_t": 41, "events_c": 5, "n_c": 45},
                                                "span": "diarrhoea in 4/41 and 5/45", "search_key": "COMPARATOR_ROW"},
                                               **b)]}), encoding="utf-8")
    return str(p)


def _topic(*trials):
    return {"slug": "topic", "trials": list(trials), "open_gaps": [t["label"] for t in trials]}


def test_hook_flips_an_unverified_row_and_marks_agreement_not_independent(tmp_path):
    o = _topic(dict(trial(**COUNTS), g1_countable=False))
    assert gt.apply_confirm_bindings(o, _bindings(tmp_path)) == ["Trial A"]
    x = o["trials"][0]
    assert x["route"] == "PRIMARY" and gt.is_matched(x)
    assert x["agreement_with_comparator_row"] == "NOT_INDEPENDENT:SEARCH_KEYED_BY_COMPARATOR_ROW"
    assert o["k_matched"] == 1 and o["open_gaps"] == []


def test_hook_refuses_a_binding_whose_span_lacks_a_count(tmp_path):
    o = _topic(dict(trial(**COUNTS), g1_countable=False))
    assert gt.apply_confirm_bindings(o, _bindings(tmp_path, span="diarrhoea in 4/41 patients")) == []
    assert o["trials"][0]["route"] == "UNVERIFIED"
    assert o["trials"][0]["confirm_binding"]["why"] == "COUNTS_NOT_IN_SPAN"


def test_hook_never_touches_a_row_that_is_not_unverified(tmp_path):
    o = _topic(dict(trial(**COUNTS), route="PRIMARY", g1_countable=True, agreement_with_comparator_row="AGREE"))
    assert gt.apply_confirm_bindings(o, _bindings(tmp_path)) == []
    assert o["trials"][0]["agreement_with_comparator_row"] == "AGREE"


def test_hook_effect_ci_binding_needs_all_three_numbers(tmp_path):
    o = _topic(dict(trial(effect="0.61", lower="0.45", upper="0.83", measure="RR"), g1_countable=False))
    p = _bindings(tmp_path, tuple_kind="EFFECT_CI", values={"measure": "RR", "effect": "0.61", "lower": "0.45",
                                                              "upper": "0.83"},
                  span="diarrhoea: relative risk 0.61 (95% CI 0.45 to 0.38)")
    assert gt.apply_confirm_bindings(o, p) == []


def test_count_span_holds_both_arms_pairs(monkeypatch):
    pad = "The ovulation rate was the primary outcome of this trial of clomiphene with or without metformin. " * 4
    b, why = run(monkeypatch, pad + "RESULTS: The diarrhoea rate in the M+C/C arm was 34/52 (65.4%) compared to "
                                    "36/55 (65.5%) in the C/C arm.", trial(events_t="34", n_t="52", events_c="36",
                                                                           n_c="55", measure="OR", effect="1.00",
                                                                           lower="0.45", upper="2.21"))
    assert why == "BOUND" and b["tuple_kind"] == "COUNTS"
    assert "34/52" in b["span"] and "36/55" in b["span"]


def test_effect_from_a_subgroup_named_just_before_is_refused(monkeypatch):
    # DECLARE-TIMI 58 (PMID 30882238): the comparator's HR 0.88 (0.66-1.17) is the 'HF without known reduced EF' subgroup
    b, why = run(monkeypatch, "Dapagliflozin reduced hospitalization for heart failure in patients with HFrEF (HR, 0.62 "
                              "[95% CI, 0.45-0.86]) more than in those without HFrEF (HR, 0.88 [95% CI, 0.76-1.02]; P for "
                              "interaction=0.046), in whom the treatment effect of dapagliflozin was similar in those "
                              "with HF without known reduced EF (HR, 0.88 [95% CI, 0.66-1.17]) and those without HF.",
                 trial(effect="0.88", lower="0.66", upper="1.17", measure="HR"),
                 terms=["hospitalization for heart failure", "heart failure"])
    assert b is None and why.startswith("SUBGROUP_OR_POST_HOC_SPAN")


def test_negative_whole_trial_effect_binds(monkeypatch):
    b, why = run(monkeypatch, "A primary end-point event occurred in 406 patients (13.4%) in the lixisenatide group and in "
                              "399 (13.2%) in the placebo group (hazard ratio, 1.02; 95% confidence interval [CI], 0.89 to "
                              "1.17).", trial(effect="1.02", lower="0.89", upper="1.17", measure="HR"),
                 terms=["primary end-point"])
    assert why == "BOUND" and b["tuple_kind"] == "EFFECT_CI"


# ---- structured tables (harness.fulltext renders cells ' | ') -------------------------------------------------------
def _tbl(title, head, *rows):
    return "Body text.\n\n=== TABLES ===\nTABLE " + title + "\n" + head + "\n" + "\n".join(rows) + "\n"


ROWC = dict(events_t="418", n_t="7942", events_c="467", n_c="7860", measure="OR")


def test_table_counts_bind_with_percent_consistent_with_n(monkeypatch):
    t = _tbl("Table 2: Clinical Outcomes.", "Outcome | Balanced (N = 7942) | Saline (N = 7860)",
             "In-hospital diarrhoea death — no. (%) | 418 (5.3) | 467 (5.9)")
    b, why = run(monkeypatch, t, trial(**ROWC))
    assert why == "BOUND" and b["route"] == "PRIMARY_TEXT_TABLE" and b["tuple_kind"] == "COUNTS"
    assert all(str(v) in b["span"] for v in (418, 7942, 467, 7860))


def test_table_percent_inconsistent_with_n_does_not_bind(monkeypatch):
    t = _tbl("Table 2: Outcomes.", "Outcome | Balanced (N = 7942) | Saline (N = 7860)",
             "Diarrhoea — no. (%) | 418 (8.3) | 467 (5.9)")
    assert run(monkeypatch, t, trial(**ROWC))[0] is None


def test_baseline_table_never_binds(monkeypatch):
    t = _tbl("Table 1: Baseline characteristics.", "Characteristic | Balanced (N = 7942) | Saline (N = 7860)",
             "Previous diarrhoea — no. (%) | 418 (5.3) | 467 (5.9)")
    assert run(monkeypatch, t, trial(**ROWC))[0] is None


def test_table_equal_arm_ns_refused(monkeypatch):
    t = _tbl("Table 2: Outcomes.", "Outcome | A (N = 100) | B (N = 100)", "Diarrhoea — no. (%) | 10 (10.0) | 20 (20.0)")
    assert run(monkeypatch, t, trial(events_t="10", n_t="100", events_c="20", n_c="100", measure="RR"))[0] is None


def test_table_subgroup_row_refused(monkeypatch):
    t = _tbl("Table 3: Subgroup analyses.", "Outcome | Balanced (N = 7942) | Saline (N = 7860)",
             "Diarrhoea — no. (%) | 418 (5.3) | 467 (5.9)")
    assert run(monkeypatch, t, trial(**ROWC))[0] is None


def test_table_effect_needs_the_measure_in_the_column_header(monkeypatch):
    ok = _tbl("Table 2: Outcomes.", "Outcome | Drug | Placebo | Odds Ratio (95% CI)",
              "Diarrhoea | 1 | 2 | 0.84 (0.73–0.97)")
    b, why = run(monkeypatch, ok, trial(effect="0.84", lower="0.73", upper="0.97", measure="OR"))
    assert why == "BOUND" and b["tuple_kind"] == "EFFECT_CI"
    bad = _tbl("Table 2: Outcomes.", "Outcome | Drug | Placebo | P value", "Diarrhoea | 1 | 2 | 0.84 (0.73–0.97)")
    assert run(monkeypatch, bad, trial(effect="0.84", lower="0.73", upper="0.97", measure="OR"))[0] is None


# ---- arm orientation -------------------------------------------------------------------------------------------------
def test_text_counts_with_arms_swapped_against_the_comparator_are_refused(monkeypatch):
    # the comparator assigns 7/78 to the TREATMENT arm; the trial prints 7/78 for PLACEBO
    b, why = run(monkeypatch, "RESULTS: diarrhea developed in the placebo group in 9% (7/78) and in the study group "
                              "in 1.4% (1/73).", trial(events_t="7", n_t="78", events_c="1", n_c="73", measure="RR"))
    assert b is None and why == "ARM_COUNTS_SWAPPED"


def test_text_counts_with_consistent_arms_record_it(monkeypatch):
    b, why = run(monkeypatch, "RESULTS: diarrhea developed in the placebo group in 9% (7/78) and in the study group "
                              "in 1.4% (1/73).", trial(events_t="1", n_t="73", events_c="7", n_c="78", measure="RR"))
    assert why == "BOUND" and b["arm_check"] == "CONSISTENT"


def test_table_counts_with_swapped_headers_are_refused(monkeypatch):
    t = _tbl("Table 2: Outcomes.", "Outcome | Placebo (N = 7942) | Treatment group (N = 7860)",
             "Diarrhoea — no. (%) | 418 (5.3) | 467 (5.9)")
    assert run(monkeypatch, t, trial(**ROWC))[0] is None


def test_counts_among_those_who_completed_the_study_are_refused(monkeypatch):
    # Can 2006 (PMID 16572062): 78 + 73 = the 151 who completed, not the randomized
    b, why = run(monkeypatch, "A total of 151 patients completed the study. RESULTS: The antibiotic-associated diarrhea "
                              "development ratio in placebo group was 9% (7/78) and in the study group 1.4% (1/73).",
                 trial(events_t="1", n_t="73", events_c="7", n_c="78", measure="RR"))
    assert b is None and why.startswith("SUBGROUP_OR_POST_HOC_SPAN")
