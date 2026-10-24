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



# CROSS-EXCH-007: study IDs alone do not protect against duplicate reports of
# the same trial. This v0.1 handoff has no multi-arm reconciliation model.
def test_distinct_study_ids_with_same_trial_id_refuse_pooling():
    item = exchange()
    second = copy.deepcopy(item["rows"][0])
    second["study_id"] = "SYNTHETIC-SECOND-REPORT"
    assert second["trial_id"] == item["rows"][0]["trial_id"]
    item["rows"].append(second)
    with pytest.raises(ValueError, match="duplicate trial_id"):
        validate_exchange(item, ROOT)


@pytest.mark.parametrize("trial_id", ["", "   ", None, 123])
def test_missing_or_untyped_trial_identity_refuses(trial_id):
    item = exchange()
    item["rows"][0]["trial_id"] = trial_id
    with pytest.raises(ValueError, match="trial_id missing or empty"):
        validate_exchange(item, ROOT)


# CROSS-EXCH-008: identifiers must be canonical at the handoff boundary.
# Without this, "TRIAL-X" and " TRIAL-X " are treated as different trials.
@pytest.mark.parametrize("field", ["study_id", "trial_id"])
@pytest.mark.parametrize("padding", [" ", "\t", "\n", "\u00a0"])
def test_boundary_whitespace_in_identifiers_refuses(field, padding):
    item = exchange()
    item["rows"][0][field] = padding + item["rows"][0][field]
    with pytest.raises(ValueError, match=f"{field} has noncanonical"):
        validate_exchange(item, ROOT)
    item["rows"][0][field] = item["rows"][0][field].strip() + padding
    with pytest.raises(ValueError, match=f"{field} has noncanonical"):
        validate_exchange(item, ROOT)


def test_padded_trial_alias_cannot_evade_duplicate_trial_refusal():
    item = exchange()
    second = copy.deepcopy(item["rows"][0])
    second["study_id"] = "SYNTHETIC-REPORT-TWO"
    second["trial_id"] = " " + item["rows"][0]["trial_id"] + " "
    item["rows"].append(second)
    with pytest.raises(ValueError, match="trial_id has noncanonical"):
        validate_exchange(item, ROOT)


def test_valid_identifier_with_internal_space_is_unchanged():
    item = exchange()
    item["rows"][0]["trial_id"] = "SYNTHETIC TRIAL 001"
    validate_exchange(item, ROOT)


def test_manifest_is_pinned_and_internal_cases_not_claimed_passed():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    validate_manifest(obj, path.parent)
    assert all(c["status"] == "NOT_RUN" for c in obj["cases"])
    assert all(c["status"] == "NOT_RUN" for c in obj["coverage"])


def test_no_bare_pass_status_without_evidence():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj["cases"][0]["status"] = "PASS"
    with pytest.raises(ValueError, match="PASS without matching, complete run evidence"):
        validate_manifest(obj, path.parent)


def test_manifest_digest_tamper_refuses():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj["cases"][0]["input_sha256"] = "1" * 64
    with pytest.raises(ValueError, match="benchmark input SHA-256 mismatch"):
        validate_manifest(obj, path.parent)


def test_fake_empty_pass_record_refuses():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj["cases"][0]["status"] = "PASS"
    obj["cases"][0]["run_evidence"] = {}
    with pytest.raises(ValueError, match="PASS without matching, complete run evidence"):
        validate_manifest(obj, path.parent)


def test_missing_source_span_refuses():
    item = exchange()
    del item["rows"][0]["source_span"]
    with pytest.raises(ValueError, match="source_span missing"):
        validate_exchange(item, ROOT)


def test_unsupported_case_input_type_refuses():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj["cases"][0]["input_type"] = "REAL_CLINICAL_DATA"
    with pytest.raises(ValueError, match="only synthetic test fixtures"):
        validate_manifest(obj, path.parent)


def test_fake_external_coverage_pass_refuses():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj["coverage"][0]["status"] = "PASS"
    with pytest.raises(ValueError, match="coverage requires actual external evidence"):
        validate_manifest(obj, path.parent)


# CROSS-EXCH-006: verify source locator against the archived text, not
# merely that the quote appears somewhere in the source.
@pytest.mark.parametrize("locator", ["line 1", "lines 1-1", "line 3", "lines 2-3"])
def test_forged_text_locator_refuses(locator):
    item = exchange()
    item["rows"][0]["source_span"]["locator"] = locator
    with pytest.raises(ValueError, match="source_span"):
        validate_exchange(item, ROOT)


@pytest.mark.parametrize("locator", [
    "page 2", "paragraph 1", "line 0", "line 02", "lines 2-1",
    "line 2\\n", "lines 2-9999999999", "line -2",
])
def test_unsupported_or_ambiguous_text_locator_refuses(locator):
    item = exchange()
    item["rows"][0]["source_span"]["locator"] = locator
    with pytest.raises(ValueError, match="source_span locator"):
        validate_exchange(item, ROOT)


def test_correct_line_range_accepts_synthetic_fixture_only():
    item = exchange()
    item["rows"][0]["source_span"]["locator"] = "lines 1-2"
    validate_exchange(item, ROOT)


def test_multiline_passage_cannot_claim_only_last_line():
    item = exchange()
    span = item["rows"][0]["source_span"]
    span["verbatim"] = SYNTHETIC.read_text(encoding="utf-8").strip()
    span["locator"] = "line 2"
    with pytest.raises(ValueError, match="passage absent at cited source lines"):
        validate_exchange(item, ROOT)
    span["locator"] = "lines 1-2"
    validate_exchange(item, ROOT)
