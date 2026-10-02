"""Cross-vendor (codex) review of harness/screen.py (registry/model_proposals/g1_codex_review.json, group
exclusion_audit_and_screen #1-#4): each finding's OWN failing input, asserting the expected behaviour, plus the controls
that keep the fix from overreaching. Each finding fails on the pre-fix screen and passes after it. Corpus effect
(every held record under every topic, both screeners, 16,668 decisions): #1 66 rule-id changes (exclude -> exclude), #2 0,
#3 0, #4 2 (one rule-id change; NCT03516409 'Bio-Kult' leaves -- it was matched only by 'BIO-K' inside 'Bio-Kult')."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import screen as s  # noqa: E402


def test_1_a_registry_record_states_its_allocation():
    assert s._is_rct({"id_type": "nct", "allocation": "NON_RANDOMIZED", "study_type": "INTERVENTIONAL"}) is False
    assert s._is_rct({"id_type": "nct", "allocation": "NA", "study_type": "INTERVENTIONAL"}) is False
    # controls: a randomised registration; an unstated allocation still falls back to the study type
    assert s._is_rct({"id_type": "nct", "allocation": "RANDOMIZED", "study_type": "INTERVENTIONAL"}) is True
    assert s._is_rct({"id_type": "nct", "allocation": "", "study_type": "INTERVENTIONAL"}) is True


def test_2_nonrandomized_is_not_randomized():
    r = {"id_type": "pmid", "title": "A nonrandomized controlled trial", "pubtypes": ["Journal Article"]}
    assert s._is_rct(r) is False
    assert s._body_says_rct({"abstract": "This was a nonrandomized controlled study."}) is False
    assert s._body_says_rct({"abstract": "This was a non-randomised controlled study."}) is False
    # controls
    assert s._is_rct({"id_type": "pmid", "title": "A randomized controlled trial of X", "pubtypes": []}) is True
    assert s._body_says_rct({"abstract": "Patients were randomly assigned to X or placebo."}) is True
    assert s._body_says_rct({"abstract": "In this double-blind trial, patients were randomized 1:1."}) is True


def test_3_unmasked_is_not_masking():
    assert s._double_blind({}, "an open-label, unmasked randomized trial") is False
    # controls
    assert s._double_blind({}, "a double-masked randomized trial") is True
    assert s._double_blind({}, "outcome assessors were masked to allocation") is True


def test_4_one_drug_does_not_satisfy_another():
    assert s._has_intervention("hydroxychloroquine versus placebo", ["chloroquine"]) is None
    assert s._has_intervention("effect of bio-kult infantis", ["BIO-K"]) is None
    # controls: the term itself, its plural, a stem, and the population-descriptor guard still behave
    assert s._has_intervention("chloroquine versus placebo", ["chloroquine"]) == "chloroquine"
    assert s._has_intervention("the effect of probiotics on diarrhoea", ["probiotic"]) == "probiotic"
    assert s._has_intervention("n-3 polyunsaturated fatty acids in heart failure",
                               ["polyunsaturated fatty acid"]) == "polyunsaturated fatty acid"
    assert s._has_intervention("bio-k+ cl1285 versus placebo", ["BIO-K"]) == "BIO-K"
    assert s._has_intervention("antibiotic-associated diarrhoea", ["antibiotic-associated diarr*"]) is not None
    assert s._has_intervention("metformin-resistant pcos", ["metformin"]) is None
