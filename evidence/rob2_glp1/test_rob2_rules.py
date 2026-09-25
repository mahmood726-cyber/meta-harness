"""The RoB 2 proposal rules must be able to FAIL. Each plant is paired with a clean case that must pass first."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import build_rob2 as B

W = lambda span, kind="paper": {"ref": "x", "sha256": "0", "span": span, "source_kind": kind}


def test_missing_evidence_is_never_relabelled_a_risk_level():
    assert B.check_domain("T", "D3_missing_outcome_data", {"proposal": "NO_EVIDENCE_HELD"}, []) is None
    for level in ("high", "low", "some_concerns"):
        assert "R2/R3" in B.check_domain("T", "D3_missing_outcome_data", {"proposal": level}, [])


def test_registry_alone_does_not_make_d5_low():
    ok = B.check_domain("T", "D5_selection_of_reported_result", {"proposal": "low"}, [W("SAP v2 finalised before unblinding", "sap")])
    assert ok is None
    assert "R4" in B.check_domain("T", "D5_selection_of_reported_result", {"proposal": "low"}, [W("PRIMARY OUTCOME: MACE", "registry")])
    assert B.check_domain("T", "D5_selection_of_reported_result", {"proposal": "some_concerns"}, [W("PRIMARY OUTCOME: MACE", "registry")]) is None


def test_stopped_treatment_is_not_missing_outcome_data():
    assert B.check_domain("T", "D3_missing_outcome_data", {"proposal": "low"}, [W("Vital status was known for 99.7% of patients.")]) is None
    assert "R5" in B.check_domain("T", "D3_missing_outcome_data", {"proposal": "low"}, [W("Premature discontinuation of the trial drug occurred in 13.6%.")])


def test_status_is_always_a_proposal():
    assert B.STATUS == "PROPOSAL_AWAITING_HUMAN_REVIEW"
    assert "final" not in {l.lower() for l in B.LEVELS}
