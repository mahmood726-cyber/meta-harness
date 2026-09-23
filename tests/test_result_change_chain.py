"""Chronology checks are read-only; mutation plants exist only in memory."""
import copy
import json
from pathlib import Path

import pytest

from harness import result_changes

ROOT = Path(__file__).resolve().parents[1]


def test_all_real_outcome_groups_have_exact_chains():
    path = ROOT / "docs" / "result_changes.json"
    initial = path.read_bytes()
    report = result_changes.chain_integrity(json.loads(initial)["notices"])
    assert len(report) == 48  # Denominator: distinct (slug, outcome) groups in the supplied ledger.
    assert all(row["ok"] for row in report), report
    assert sum(len(row["indices"]) > 1 for row in report) == 6
    assert path.read_bytes() == initial


@pytest.fixture
def synthetic_chain():
    base = {"slug": "synthetic-chain", "outcome": "Synthetic outcome",
            "before": {"k": 3, "estimate": 2}, "after": {"k": 2, "estimate": 3},
            "when_utc": "2000-01-01T00:00:00Z"}
    next_notice = dict(base, before=copy.deepcopy(base["after"]), after={"k": 1, "estimate": 4},
                       when_utc="2000-01-02T00:00:00Z")
    return [base, next_notice]


def test_chronology_does_not_depend_on_array_order(synthetic_chain):
    row = result_changes.chain_integrity(list(reversed(synthetic_chain)))[0]
    assert row["ok"] and row["indices"] == [1, 0]


def test_tiny_break_is_not_hidden_by_estimate_tolerance(synthetic_chain):
    synthetic_chain[1]["before"]["estimate"] += 1e-9
    row = result_changes.chain_integrity(synthetic_chain)[0]
    assert not row["ok"] and "1.before != ledger index 0.after" in row["problems"][0]


@pytest.mark.parametrize("when", [None, "invalid", "2000-01-02", "2000-01-01T01:00:00+01:00"])
def test_missing_invalid_naive_or_tied_dates_fail(synthetic_chain, when):
    synthetic_chain[1]["when_utc"] = when
    assert not result_changes.chain_integrity(synthetic_chain)[0]["ok"]


def test_missing_transition_is_not_a_valid_empty_chain(synthetic_chain):
    del synthetic_chain[0]["after"]
    del synthetic_chain[1]["before"]
    assert not result_changes.chain_integrity(synthetic_chain)[0]["ok"]
