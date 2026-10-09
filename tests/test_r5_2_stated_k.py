"""R5-2: the comparator's own stated trial count (g1_tracker.stated_k_from_text). 'Phase 3' is a phase, never a count:
Makam (29795629) prints 'We used data from Phase 3 randomized trials ...' and was read as k = 3 ('3 randomized trials')."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402


def k(t):
    return gt.stated_k_from_text(t)[0]


def test_PLANT_a_phase_number_is_never_a_trial_count():
    assert k("Methods We used data from Phase 3 randomized trials that compared an FDA-approved DOAC with VKA") is None
    assert k("pooled data from phase III clinical trials") is None


def test_PLANT_studies_and_rcts_are_trials_too():
    assert k("We included five Phase 3 studies enrolling 27,023 patients") == 5
    assert k("Six RCTs were included") == 6


def test_a_plain_stated_count_still_reads():
    assert k("3 randomized trials were pooled") == 3
    assert k("6 phase 3 trials including a total of 27,023 patients") == 6
