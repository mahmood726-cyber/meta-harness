"""Canonical effect type from the methods, not the label (r13 RE-LY, r20 RALES): a Cox 'relative risk' is an HR. The
source wording stays beside it; the value never changes. Fixed-string fixtures copied from the held FDA labels."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import canonical_effect_type as ce  # noqa: E402
import g1_tracker as gt  # noqa: E402

RALES_LABEL = ("The Randomized Aldactone Evaluation Study (RALES) was a placebo controlled, double-blind study of the effect "
               "of spironolactone on mortality. The primary endpoint for RALES was time to all-cause mortality. RALES was "
               "terminated early. Figure 1. Survival by Treatment Group in RALES Log-rank p: < 0.001. Mortality hazard "
               "ratios for some subgroups are shown in Figure 2.")


def test_PLANT_rales_label_establishes_time_to_event_hr():
    assert ce.label_time_to_event(RALES_LABEL, "RALES")
    # the acronym must be the trial's: another trial's passage establishes nothing for RALES
    assert ce.label_time_to_event(RALES_LABEL.replace("RALES", "EPHESUS"), "RALES") is None


def test_PLANT_time_to_event_needs_hazard_ratios_or_log_rank_too():
    assert ce.label_time_to_event("In RALES the primary endpoint was time to all-cause mortality.", "RALES") is None


def test_PLANT_own_text_cox_needs_cox_and_the_estimate_in_one_sentence():
    assert ce.own_text_cox("Relative risks were estimated with a Cox proportional-hazards model.")
    assert ce.own_text_cox("We used Cox regression for secondary analyses. The relative risk was 0.70.") is None
    assert ce.own_text_cox("relative risk of death, 0.70; 95 percent confidence interval, 0.60 to 0.82") is None


def test_acronym_of():
    assert ce.acronym_of("RALES1999") == "RALES" and ce.acronym_of("RE-LY") == "RE-LY" and ce.acronym_of("10471456") is None


REG = {"spironolactone-hfref-mortality|PMID 10471456": {
    "source_wording": "RR", "canonical": {"state": "ESTABLISHED_HR", "rule": "LABEL_TIME_TO_EVENT", "document": "x",
                                          "span": "RALES was time to all-cause mortality"}}}
RALES = {"measure": "RR", "effect": "0.7", "lower": "0.6", "upper": "0.82", "events_t": None}


def test_PLANT_g1_compares_an_established_cox_relative_risk_as_an_hr_and_keeps_the_wording():
    p = gt.canonical_primary("spironolactone-hfref-mortality", "PMID 10471456", RALES, REG)
    assert p["measure"] == "HR" and p["measure_source_wording"] == "RR" and p["effect"] == "0.7"
    # and the RALES pair is then compared, not a measure difference (comparator HR 0.71 (0.61-0.82))
    theirs = gt.sm.SecondaryRow(meta_pmid="40959489", meta_doi="", location={}, source_digest="", provenance="x",
                                trial_label="RALES", measure="HR", outcome_definition="", effect="0.71", lower="0.61",
                                upper="0.82")
    row, why = gt.on_comparator_measure(gt.as_row(p, "RALES"), theirs)
    assert row is not None and why is None


def test_PLANT_counts_derived_ratios_unrecorded_rows_and_other_wordings_are_never_relabelled():
    assert gt.canonical_primary("spironolactone-hfref-mortality", "PMID 10471456", dict(RALES, events_t=284), REG) \
        ["measure"] == "RR"
    assert gt.canonical_primary("spironolactone-hfref-mortality", "PMID 999", RALES, REG)["measure"] == "RR"
    assert gt.canonical_primary("spironolactone-hfref-mortality", "PMID 10471456", dict(RALES, measure="OR"), REG) \
        ["measure"] == "OR"
    nope = {k: dict(v, canonical={"state": "NOT_ESTABLISHED"}) for k, v in REG.items()}
    assert gt.canonical_primary("spironolactone-hfref-mortality", "PMID 10471456", RALES, nope)["measure"] == "RR"
