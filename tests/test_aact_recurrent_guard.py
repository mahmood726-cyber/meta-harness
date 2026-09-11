"""Guard: AACT recurrent-event outcomes must not be poolable as binomials (the HEART-FID trap —
AACT tags 'Number of Hospitalizations' as COUNT_OF_PARTICIPANTS but they are events, not patients)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.aact import is_recurrent_event_title  # noqa: E402


def test_recurrent_event_titles_flagged():
    for t in ["Number of Hospitalizations for Heart Failure",
              "Total Heart Failure Hospitalizations",
              "Annualized rate of exacerbations",
              "Number of COPD exacerbations"]:
        assert is_recurrent_event_title(t), t


def test_binomial_participant_titles_not_flagged():
    for t in ["30-day In-hospital Mortality",
              "Number of Participants With at Least One Heart Failure Hospitalization",
              "All-cause mortality",
              "Participants who died"]:
        assert not is_recurrent_event_title(t), t
