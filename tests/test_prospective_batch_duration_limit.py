"""A4 regression: a completed prospective run cannot outlive its frozen ceiling.

These are isolated, synthetic batch-record checks, not prospective clinical runs.
"""
from __future__ import annotations

import pytest

from harness import prospective


@pytest.mark.parametrize(
    ("finished_utc", "outcome", "limit_s", "refusal"),
    [
        ("2026-10-24T10:00:59Z", "COMPLETED", 60, None),
        ("2026-10-24T10:01:00Z", "COMPLETED", 60, None),
        ("2026-10-24T10:01:01Z", "COMPLETED", 60, "COMPLETED exceeds preregistered"),
        # Offsets must be compared by instant, not lexicographically.
        ("2026-10-24T11:01:01+01:00", "COMPLETED", 60, "COMPLETED exceeds preregistered"),
        ("2026-10-24T10:00:30Z", "COMPLETED", 29.5, "COMPLETED exceeds preregistered"),
        # Failures remain failures and must not be promoted to completed.
        ("2026-10-24T10:02:00Z", "FAILED_TIMEOUT", 60, None),
        ("2026-10-24T10:02:00Z", "FAILED_CRASH", 60, None),
        (None, "COMPLETED", 60, "invalid start/finish UTC"),
        ("2026-10-24T09:59:59Z", "COMPLETED", 60, "finished before started"),
    ],
)
def test_batch_refuses_success_after_declared_time_limit(
    monkeypatch, tmp_path, finished_utc, outcome, limit_s, refusal
):
    """Exercise check_batch, not a standalone imitation of the duration formula."""
    claim = prospective.MUTABLE_FREEZE_CLAIM
    declaration = {
        "architecture_identity": "a" * 64,
        "external_dependency_mutability": True,
        "freeze_claim": claim,
        "declared_utc": "2026-10-24T09:00:00Z",
        "time_limit_s": limit_s,
    }
    record = {
        "run_id": "run-one",
        "batch_id": "batch-one",
        "topic_identifier": "held-out-01",
        "started_utc": "2026-10-24T10:00:00Z",
        "finished_utc": finished_utc,
        "architecture_identity": declaration["architecture_identity"],
        "external_dependency_mutability": True,
        "freeze_claim": claim,
        "outcome": outcome,
        "artefact_paths": ["review/manifest.json"],
        "rerun_of": None,
        "rerun_justification": None,
    }
    monkeypatch.setattr(prospective, "load_declaration", lambda *_: declaration)
    monkeypatch.setattr(prospective, "check_declaration_frozen", lambda *_: declaration)
    monkeypatch.setattr(prospective, "load_run_records", lambda *_: [record])
    monkeypatch.setattr(prospective, "load_defects", lambda *_: [])

    if refusal:
        with pytest.raises(prospective.ProspectiveRefusal, match=refusal):
            prospective.check_batch(tmp_path, "batch-one")
    else:
        result = prospective.check_batch(tmp_path, "batch-one")
        assert result["ok"] is True
        assert result["run_records"] == 1


def test_time_limit_not_checkable_refuses_completed_batch(monkeypatch, tmp_path):
    """An invalid declaration must fail closed even if another layer is stubbed."""
    declaration = {
        "architecture_identity": "a" * 64,
        "external_dependency_mutability": True,
        "freeze_claim": prospective.MUTABLE_FREEZE_CLAIM,
        "declared_utc": "2026-10-24T09:00:00Z",
        "time_limit_s": float("nan"),
    }
    monkeypatch.setattr(prospective, "load_declaration", lambda *_: declaration)
    monkeypatch.setattr(prospective, "check_declaration_frozen", lambda *_: declaration)
    monkeypatch.setattr(prospective, "load_run_records", lambda *_: [])
    monkeypatch.setattr(prospective, "load_defects", lambda *_: [])
    with pytest.raises(prospective.ProspectiveRefusal, match="time_limit_s invalid"):
        prospective.check_batch(tmp_path, "batch-one")
