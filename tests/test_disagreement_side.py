"""A per-trial DISAGREE takes the side the trial's OWN held text supports (g1_tracker.disagreement_side), so
DIVERGENCES_NAMED is met by evidence: probiotics' Pozzoni (report '16/106' S. boulardii, '13/98' placebo; the comparator
printed 13/106 vs 16/98 -- arms swapped) and Song (the report states 'AAD-1' 4/103 vs 8/111, its primary, and 'AAD-2'
9/103 vs 16/111, what the comparator pooled)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402

POZ = "AAD developed in 13.3% (13/98) of the patients receiving placebo and in 15.1% (16/106) of those receiving S. boulardii"
SONG = ("AAD-1 developed in 4 (3.9%) of 103 patients in the Lactobacillus group and in 8 (7.2%) of 111 patients in the "
        "placebo group. AAD-2 developed in 9 (8.7%) of 103 patients in the Lactobacillus group and in 16 (14.4%) of 111")


def _c(a, n1, b, n2):
    return {"events_t": a, "n_t": n1, "events_c": b, "n_c": n2}


def test_swapped_arms_are_named_from_the_trials_own_text():
    s = gt.disagreement_side(None, _c(13, 106, 16, 98), POZ)
    assert s.startswith("COMPARATOR_ARMS_SWAPPED") and "16/106" in s and "13/98" in s


def test_two_stated_definitions_are_named_as_such_and_neither_side_wrong():
    s = gt.disagreement_side(_c(4, 103, 8, 111), _c(9, 103, 16, 111), SONG)
    assert s.startswith("BOTH_STATED_DIFFERENT_DEFINITIONS")


def test_a_comparator_count_absent_from_the_report_is_named():
    text = SONG.split(" AAD-2")[0]
    s = gt.disagreement_side(_c(4, 103, 8, 111), _c(9, 103, 16, 111), text)
    assert s.startswith("COMPARATOR_ROW_NOT_IN_TRIAL_REPORT")


def test_nothing_is_claimed_without_evidence():
    assert gt.disagreement_side(_c(4, 103, 8, 111), _c(9, 103, 16, 111), "no numbers here") is None
    assert gt.disagreement_side(None, _c(9, 103, 16, 111), "") is None
    assert gt.count_stated("3.9% of 103", 9, 103) is None                 # '9' inside '3.9' is not a count
