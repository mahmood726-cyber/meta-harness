"""Trial-integrity gate: a pooled RETRACTED trial refuses the page; a clean set passes."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.gate import check_retraction  # noqa: E402


def _dir(integrity):
    d = tempfile.mkdtemp(prefix="mh-integ-")
    rev = {"outcomes": [{"primary": True, "trials": [{"id": "PMID 1"}]}], "integrity": integrity}
    json.dump(rev, open(os.path.join(d, "review.json"), "w", encoding="utf-8"))
    return d


def test_retracted_pooled_trial_refuses():
    reasons = check_retraction(_dir({"retracted": ["32450107"], "concern": []}))
    assert reasons and "RETRACTED" in reasons[0] and "32450107" in reasons[0]


def test_clean_passes():
    assert check_retraction(_dir({"retracted": [], "concern": []})) == []


def test_expression_of_concern_does_not_block():
    # concern is surfaced, not blocked
    assert check_retraction(_dir({"retracted": [], "concern": ["12345"]})) == []


def test_no_integrity_block_does_not_refuse():
    d = tempfile.mkdtemp(prefix="mh-integ2-")
    json.dump({"outcomes": []}, open(os.path.join(d, "review.json"), "w", encoding="utf-8"))
    assert check_retraction(d) == []
