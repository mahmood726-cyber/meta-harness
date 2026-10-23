"""Synthetic transport-level fixtures ONLY; never evidence of clinical accuracy."""
import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.exchange_v01 import validate_exchange, validate_manifest  # noqa: E402

SYNTHETIC = ROOT / "benchmarks/cross_repo/v0.1/synthetic-source.txt"
ESTIMAND = {"measure": "RR", "population": "ITT", "outcome": "synthetic event", "timepoint": "12 months"}


def exchange():
    return {
        "schema_version": "0.1.0", "review_id": "SYNTHETIC-REVIEW", "protocol_sha256": "0" * 64,
        "proposed_pool": {"requested": True, "estimand": copy.deepcopy(ESTIMAND)},
        "rows": [{
            "study_id": "SYNTHETIC-STUDY-001", "trial_id": "SYNTHETIC-TRIAL-001", "decision": "ALLOW",
            "estimand": copy.deepcopy(ESTIMAND),
            "source": {"sha256": hashlib.sha256(SYNTHETIC.read_bytes()).hexdigest(),
                       "path": "benchmarks/cross_repo/v0.1/synthetic-source.txt"},
            "source_span": {"locator": "line 2", "verbatim": "Trial SYNTHETIC-001 measured synthetic endpoint at 12 months."}
        }]
    }


def test_transport_accepts_structurally_valid_synthetic_fixture_only():
    validate_exchange(exchange(), ROOT)


@pytest.mark.parametrize("decision", ["REFUSE", "MANUAL_REVIEW", "ADJUST", "ALLOW_WITH_LABEL", None])
def test_no_nonallow_decision_silently_pools(decision):
    item = exchange()
    item["rows"][0]["decision"] = decision
    with pytest.raises(ValueError, match="cannot be pooled|unknown decision"):
        validate_exchange(item, ROOT)


@pytest.mark.parametrize("key,value", [
    ("measure", "OR"), ("population", "PP"), ("outcome", "different endpoint"), ("timepoint", "24 months")
])
def test_incompatible_estimands_refuse(key, value):
    item = exchange()
    item["rows"][0]["estimand"][key] = value
    with pytest.raises(ValueError, match="estimand mismatch"):
        validate_exchange(item, ROOT)


def test_false_source_digest_refuses():
    item = exchange()
    item["rows"][0]["source"]["sha256"] = "1" * 64
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        validate_exchange(item, ROOT)


def test_unmatched_source_quote_refuses():
    item = exchange()
    item["rows"][0]["source_span"]["verbatim"] = "not in source"
    with pytest.raises(ValueError, match="passage absent"):
        validate_exchange(item, ROOT)


def test_path_traversal_refuses():
    item = exchange()
    item["rows"][0]["source"]["path"] = "../../outside.txt"
    with pytest.raises(ValueError, match="inaccessible source"):
        validate_exchange(item, ROOT)


def test_duplicate_study_refuses():
    item = exchange()
    item["rows"].append(copy.deepcopy(item["rows"][0]))
    with pytest.raises(ValueError, match="duplicate study_id"):
        validate_exchange(item, ROOT)


def test_manifest_is_pinned_and_internal_cases_not_claimed_passed():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    validate_manifest(obj, path.parent)
    assert all(c["status"] == "NOT_RUN" for c in obj["cases"])


def test_no_bare_pass_status_without_evidence():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj["cases"][0]["status"] = "PASS"
    with pytest.raises(ValueError, match="PASS without run evidence"):
        validate_manifest(obj, path.parent)


def test_manifest_digest_tamper_refuses():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj["cases"][0]["input_sha256"] = "1" * 64
    with pytest.raises(ValueError, match="benchmark input SHA-256 mismatch"):
        validate_manifest(obj, path.parent)
