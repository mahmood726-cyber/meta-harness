"""V13-01 (signed 9 Oct, 'sign v13'): a printed 'relative risk' that is numerically the relative risk REDUCTION of the
same sentence's own counts is not admitted as the RR. CORP-2 (PMID 24694983) prints "26 (21.6%) of 120 ... 51 (42.5%) of
120 ... (relative risk 0.49; 95% CI 0.24-0.65)"; its counts give RR 0.5098 (0.3421-0.7596) and 1 - RR = 0.49 (0.24-0.66).
The selector used to prefer the printed 0.49 over the reconstruction because both are in the RR class."""
from harness import design_key as dk

COUNTS = {"ai": 26, "n1i": 120, "ci": 51, "n2i": 120, "derivation": "reconstructed_counts", "scale": "RR"}
PRINTED_RRR = {"effect": 0.49, "ci_low": 0.24, "ci_high": 0.65, "scale": "RR", "derivation": "reported"}


def test_PLANT_a_printed_rr_equal_to_the_counts_rrr_is_not_selected():
    chosen = dk.select_estimator_by_source_hierarchy(dict(COUNTS), [dict(PRINTED_RRR)], "RR")
    assert chosen.get("ai") == 26 and chosen.get("effect") is None and chosen["selection_rule"] == "KEEP_RECONSTRUCTION_PRINTED_RR_IS_RRR", chosen
    alt = [a for a in chosen["alternatives"] if a.get("effect") == 0.49]
    assert alt and alt[0].get("not_selected_reason") == "PRINTED_RR_IS_RRR_OF_COUNTS", chosen["alternatives"]


def test_a_printed_rr_consistent_with_its_counts_is_still_preferred():
    ok = dict(PRINTED_RRR, effect=0.51, ci_low=0.34, ci_high=0.76)
    chosen = dk.select_estimator_by_source_hierarchy(dict(COUNTS), [ok], "RR")
    assert chosen.get("effect") == 0.51 and chosen["selection_rule"] == "PUBLISHED_EFFECT_TARGET_CLASS"


def test_near_half_is_ambiguous_and_the_rule_does_not_fire():
    half = dict(COUNTS, ai=60, ci=120, n1i=240, n2i=240)          # RR 0.5 = 1 - RR
    chosen = dk.select_estimator_by_source_hierarchy(half, [dict(PRINTED_RRR, effect=0.5, ci_low=0.38, ci_high=0.66)], "RR")
    assert chosen.get("effect") == 0.5
