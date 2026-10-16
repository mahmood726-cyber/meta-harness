"""AE discontinuation requires attribution, not merely treatment cessation."""
import pytest

from harness.harms import reporting_signal


SPEC = {"name": "Treatment discontinuation due to adverse events"}


@pytest.mark.parametrize("text, expected", [
    ("Medication was discontinued when pregnancy was confirmed, and subjects were followed until delivery.", False),
    ("Discontinuation due to adverse events occurred in 5 of 100 patients", True),
    ("withdrew because of gastrointestinal side effects", True),
    ("Gastrointestinal side effects were reported.", False),
    ("Medication was discontinued when pregnancy was confirmed; side effects were mild.", False),
    ("Treatment was discontinued due to toxicity.", True),
    ("Patients withdrew because of intolerance.", True),
])
def test_ae_discontinuation_requires_attribution(text, expected):
    assert bool(reporting_signal(text, SPEC)) is expected
