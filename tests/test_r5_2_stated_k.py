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


def test_PLANT_r1_1_a_screening_count_never_overrides_the_included_count():
    # codex r5-2-stated-k-r1 #1 (P0): '20 studies screened' was read before '4 randomized controlled trials were included'
    assert k("Of 20 studies screened, 4 randomized controlled trials were included.") == 4
    assert k("We identified 312 studies, of which 9 RCTs met the inclusion criteria.") == 9
    assert k("A total of 48 studies were assessed for eligibility") is None


# ---------------------------------------------------------------- captain, codex pr53-cap-r1 #1 (P0) and #2 (P1)
def test_of_n_studies_is_the_funnel_not_the_included_count():
    assert gt.stated_k_from_text("Of 20 studies, 18 were excluded and 2 trials were included.") == (2, "2 trials")


def test_an_exclusion_governs_only_its_own_count():
    assert gt.stated_k_from_text("We included 5 studies and excluded 2 studies.") == (5, "5 studies")


def test_a_total_of_and_analysis_of_stay_counts():
    """Regression found by the captain's sweep of the fix itself: the first 'Of N' rule matched any '... of' before the
    count and dropped two real comparators (36050741 colchicine-postop-af; 40959489 spironolactone, a G1 topic)."""
    assert gt.stated_k_from_text("Results A total of 9 RCTs were included in this meta-analysis, enrolling a total of "
                                 "2031 patients.") == (9, "9 RCTs")
    assert gt.stated_k_from_text("In the analysis of nine RCTs, MRAs were associated with a 23% reduction in CV composite "
                                 "outcomes") == (9, "nine RCTs")


# ---------------------------------------------------------------- captain review round 2 (codex pr53-cap-r2 #1-#3)
def test_a_shared_exclusion_verb_governs_every_coordinated_count():
    assert gt.stated_k_from_text("We excluded 20 studies and 5 RCTs. We included 3 trials.") == (3, "3 trials")


def test_an_explicit_inclusion_outranks_a_screening_word():
    assert gt.stated_k_from_text("We included 5 studies after full-text review.") == (5, "5 studies")


def test_a_hyphenated_phase_is_never_a_count():
    assert gt.stated_k_from_text("Data from phase-3 RCTs were pooled. We included 8 trials.") == (8, "8 trials")
