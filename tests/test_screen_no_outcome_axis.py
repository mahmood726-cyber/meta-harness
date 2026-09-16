import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import absence  # noqa: E402
from harness.screen import _text, screen_record  # noqa: E402


INC = {
    "population_any": ["heart failure", "reduced ejection fraction"],
    "intervention_any": ["sacubitril"],
    "intervention_in_title": True,
    "comparator_any": ["enalapril"],
    "design_double_blind": True,
}

TARGET_KEYWORDS = [
    "cardiovascular death or heart-failure hospitalization",
    "cardiovascular death or hospitalization for heart failure",
    "death from cardiovascular causes or hospitalization for heart failure",
]


def _eligible_record_without_target_outcome():
    return {
        "id": "999001",
        "id_type": "pmid",
        "pubtypes": ["Randomized Controlled Trial"],
        "title": (
            "Sacubitril versus enalapril in adults with heart failure and "
            "reduced ejection fraction: a randomized trial"
        ),
        "abstract": (
            "Adults with chronic heart failure and reduced ejection fraction were randomly "
            "assigned to sacubitril or enalapril in a double-blind active-controlled trial. "
            "The abstract reports biomarker change and safety follow-up only."
        ),
        "conditions": [],
        "interventions": [],
        "masking": "",
    }


def test_screen_includes_pic_design_trial_even_when_target_outcome_not_reported():
    rec = _eligible_record_without_target_outcome()
    haystack = _text(rec)
    assert not any(k.lower() in haystack for k in TARGET_KEYWORDS)

    decision, rule, reason, span = screen_record(rec, INC, set())
    assert (decision, rule) == ("include", "INCLUDE"), (decision, rule, reason, span)

    state, basis = absence.classify(TARGET_KEYWORDS, rec["abstract"], fulltext=None)
    assert state == "SOURCE_NOT_RETRIEVED", basis
