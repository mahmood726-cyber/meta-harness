"""Synthetic transport-level fixtures ONLY; never evidence of clinical accuracy."""
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.exchange_v01 import validate_exchange, validate_exchange_json, validate_manifest  # noqa: E402

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


# CROSS-EXCH-010: parse *wire JSON* before duplicate keys can disappear.
# Python's ordinary json.loads uses the last occurrence, potentially turning
# a raw REFUSE / duplicate trial identity into an apparently valid ALLOW row.
def test_strict_wire_json_accepts_unique_synthetic_fixture():
    validate_exchange_json(json.dumps(exchange()), ROOT)


@pytest.mark.parametrize("key,shadow,accepted", [
    ("schema_version", "future-version", "0.1.0"),
    ("requested", False, True),
    ("trial_id", "SHADOW-TRIAL", "SYNTHETIC-TRIAL-001"),
    ("decision", "REFUSE", "ALLOW"),
    ("measure", "OR", "RR"),
    ("sha256", "1" * 64, hashlib.sha256(SYNTHETIC.read_bytes()).hexdigest()),
])
def test_duplicate_wire_json_member_refuses_even_when_last_value_passes(key, shadow, accepted):
    original = json.dumps(exchange())
    member = f'{json.dumps(key)}: {json.dumps(accepted)}'
    assert member in original
    poisoned = original.replace(member, f'{json.dumps(key)}: {json.dumps(shadow)}, ' + member, 1)
    # This reproduces the old last-key-wins hazard, not a validated evidence row.
    assert json.loads(poisoned) == exchange()
    with pytest.raises(ValueError, match=f"duplicate JSON object member: {key}"):
        validate_exchange_json(poisoned, ROOT)


def test_unicode_escaped_duplicate_member_refuses():
    raw = json.dumps(exchange())
    original = '"decision": "ALLOW"'
    assert original in raw
    poisoned = raw.replace(original, '"\\u0064ecision": "REFUSE", ' + original, 1)
    with pytest.raises(ValueError, match="duplicate JSON object member: decision"):
        validate_exchange_json(poisoned, ROOT)


@pytest.mark.parametrize("invalid", [b"\xff", b"\xef\xbb\xbf{}"])
def test_non_utf8_or_bom_wire_json_refuses(invalid):
    with pytest.raises(ValueError, match="UTF-8"):
        validate_exchange_json(invalid, ROOT)


def test_transport_accepts_structurally_valid_synthetic_fixture_only():
    validate_exchange(exchange(), ROOT)


# CROSS-EXCH-009: the Python importer must enforce the same closed object
# shapes as the versioned JSON Schema (additionalProperties=false). Otherwise
# a second consumer might silently treat an unknown field as a pooling override.
@pytest.mark.parametrize("section", ["root", "proposed_pool", "row", "source", "source_span"])
def test_unversioned_extra_exchange_field_refuses(section):
    item = exchange()
    parts = {
        "root": item,
        "proposed_pool": item["proposed_pool"],
        "row": item["rows"][0],
        "source": item["rows"][0]["source"],
        "source_span": item["rows"][0]["source_span"],
    }
    parts[section]["unversioned_pool_override"] = {"decision": "ALLOW"}
    with pytest.raises(ValueError, match="unsupported field"):
        validate_exchange(item, ROOT)


def test_schema_and_executable_importer_both_require_closed_exchange_objects():
    spec = json.loads((ROOT / "benchmarks/cross_repo/v0.1/exchange.schema.json").read_text(encoding="utf-8"))
    assert spec["additionalProperties"] is False
    assert spec["properties"]["proposed_pool"]["additionalProperties"] is False
    assert spec["$defs"]["row"]["additionalProperties"] is False
    assert spec["$defs"]["estimand"]["additionalProperties"] is False
    assert spec["$defs"]["row"]["properties"]["source"]["additionalProperties"] is False
    assert spec["$defs"]["row"]["properties"]["source_span"]["additionalProperties"] is False



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
@pytest.mark.parametrize("padding", [" ", "\t", "\n", "\u00a0", "\u001c", "\u0085", "\ufeff"])
def test_boundary_whitespace_in_identifiers_refuses(field, padding):
    item = exchange()
    original = item["rows"][0][field]
    item["rows"][0][field] = padding + original
    with pytest.raises(ValueError, match=f"{field} has noncanonical"):
        validate_exchange(item, ROOT)
    item["rows"][0][field] = original + padding
    with pytest.raises(ValueError, match=f"{field} has noncanonical"):
        validate_exchange(item, ROOT)


@pytest.mark.parametrize("field", ["study_id", "trial_id"])
@pytest.mark.parametrize("padding", [" ", "\t", "\n", "\u00a0", "\u001c", "\u0085", "\ufeff"])
def test_schema_and_python_identity_whitespace_policy_agree(field, padding):
    spec = json.loads((ROOT / "benchmarks/cross_repo/v0.1/exchange.schema.json").read_text(encoding="utf-8"))
    pattern = spec["$defs"]["row"]["properties"][field]["pattern"]
    # Built-in Python regex checks schema spelling without adding a dependency;
    # execution under an actual JS/JSON Schema validator is a separate gate.
    assert re.search(pattern, padding + "TRIAL-X") is None
    assert re.search(pattern, "TRIAL-X" + padding) is None
    assert re.search(pattern, "TRIAL X") is not None


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


# CROSS-EXCH-011: synthetic PASS records test *offline provenance consistency*,
# not real Actions execution, successful cross-repo canaries, or clinical accuracy.
# These records exist only inside the test and must never be written to the
# public manifest as benchmark evidence.
def _synthetic_pass_manifest():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    case = obj["cases"][0]
    case["status"] = "PASS"
    case["run_evidence"] = {
        "action_run_url": "https://github.com/mahmood726-cyber/meta-harness/actions/runs/123456789",
        "commit_sha": obj["repositories"]["meta-harness"]["commit"],
        "input_sha256": case["input_sha256"],
        "job_name": "synthetic-provenance-check-not-a-real-job",
    }
    return obj, path.parent


def test_synthetic_pin_matched_pass_record_checks_structure_only():
    manifest, root = _synthetic_pass_manifest()
    validate_manifest(manifest, root)


@pytest.mark.parametrize("wrong_url", [
    "https://github.com/other-owner/meta-harness/actions/runs/123456789",
    "https://github.com/mahmood726-cyber/unpinned-repo/actions/runs/123456789",
    "https://github.com/mahmood726-cyber/meta-harness/actions/runs/0",
    "https://github.com/mahmood726-cyber/meta-harness/actions/runs/123456789?spoof=1",
])
def test_synthetic_pass_cannot_cite_unpinned_workflow_url(wrong_url):
    manifest, root = _synthetic_pass_manifest()
    manifest["cases"][0]["run_evidence"]["action_run_url"] = wrong_url
    with pytest.raises(ValueError, match="not from a pinned repository"):
        validate_manifest(manifest, root)


def test_synthetic_pass_cannot_claim_unpinned_checkout():
    manifest, root = _synthetic_pass_manifest()
    manifest["cases"][0]["run_evidence"]["commit_sha"] = "f" * 40
    with pytest.raises(ValueError, match="not the pinned meta-harness commit"):
        validate_manifest(manifest, root)


def test_synthetic_pass_cannot_reuse_other_repositories_pin():
    manifest, root = _synthetic_pass_manifest()
    manifest["cases"][0]["run_evidence"]["commit_sha"] = manifest["repositories"]["e156"]["commit"]
    with pytest.raises(ValueError, match="not the pinned meta-harness commit"):
        validate_manifest(manifest, root)



# CROSS-EXCH-012: every previously declared transport refusal case must remain
# registered. Missing tests must not become an apparently complete benchmark.
# These are synthetic manifest-structure tests, not executed benchmark PASSes.
@pytest.mark.parametrize("missing_id", [
    "CROSS-EXCH-001", "CROSS-EXCH-006", "CROSS-EXCH-011", "CROSS-EXCH-012",
])
def test_registered_exchange_case_cannot_disappear(missing_id):
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["cases"] = [c for c in manifest["cases"] if c["id"] != missing_id]
    with pytest.raises(ValueError, match=f"missing required IDs:.*{missing_id}"):
        validate_manifest(manifest, path.parent)


def test_cross_lane_case_id_cannot_replace_registered_exchange_case():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["cases"][-1]["id"] = "CROSS-R-012"
    with pytest.raises(ValueError, match="unsupported CROSS-EXCH case namespace"):
        validate_manifest(manifest, path.parent)


def test_renamed_case_cannot_create_gap_in_registration():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["cases"][-1]["id"] = "CROSS-EXCH-014"
    with pytest.raises(ValueError, match="missing required IDs:.*CROSS-EXCH-012"):
        validate_manifest(manifest, path.parent)


def test_contiguous_future_id_and_reordering_are_structurally_allowed():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    future = copy.deepcopy(manifest["cases"][-1])
    future["id"] = "CROSS-EXCH-014"
    future["status"] = "NOT_RUN"
    manifest["cases"].insert(0, future)
    manifest["cases"].reverse()
    validate_manifest(manifest, path.parent)


def test_manifest_schema_declares_transport_namespace_and_13_case_floor():
    schema = json.loads(
        (ROOT / "benchmarks/cross_repo/v0.1/manifest.schema.json").read_text(encoding="utf-8")
    )
    assert schema["properties"]["cases"]["minItems"] == 13
    pat = schema["$defs"]["case"]["properties"]["id"]["pattern"]
    assert re.fullmatch(pat, "CROSS-EXCH-012")
    assert re.fullmatch(pat, "CROSS-R-012") is None
    assert re.fullmatch(pat, "CROSS-EXCH-000") is None


# CROSS-EXCH-013: the executable manifest validator must honor the same
# closed shapes and required provenance declarations as manifest.schema.json.
# All inputs here are local synthetic mutations, not benchmark PASS evidence.
def _manifest_fixture():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    return json.loads(path.read_text(encoding="utf-8")), path.parent


@pytest.mark.parametrize("section", ["root", "repository", "case", "coverage"])
def test_manifest_rejects_unversioned_fields(section):
    manifest, root = _manifest_fixture()
    target = {
        "root": manifest,
        "repository": manifest["repositories"]["rapidmeta-kit"],
        "case": manifest["cases"][0],
        "coverage": manifest["coverage"][0],
    }[section]
    target["silent_gate_override"] = {"status": "PASS"}
    with pytest.raises(ValueError, match="unsupported field"):
        validate_manifest(manifest, root)


@pytest.mark.parametrize("section,key", [
    ("root", "purpose"),
    ("repository", "dependency_identity"),
    ("case", "description"),
])
def test_manifest_rejects_missing_required_metadata(section, key):
    manifest, root = _manifest_fixture()
    target = {
        "root": manifest,
        "repository": manifest["repositories"]["rapidmeta-kit"],
        "case": manifest["cases"][0],
    }[section]
    del target[key]
    with pytest.raises(ValueError, match=f"{key} missing or empty"):
        validate_manifest(manifest, root)


@pytest.mark.parametrize("value", [None, 123, "F" * 40, "0" * 39, "0" * 41])
def test_manifest_rejects_invalid_declared_lock_blob(value):
    manifest, root = _manifest_fixture()
    manifest["repositories"]["meta-harness"]["dependency_lock_git_blob"] = value
    with pytest.raises(ValueError, match="invalid dependency_lock_git_blob"):
        validate_manifest(manifest, root)


def test_manifest_rejects_nonobject_coverage_without_attribute_error():
    manifest, root = _manifest_fixture()
    manifest["coverage"][0] = ["not-a-record"]
    with pytest.raises(ValueError, match="coverage entry must be an object"):
        validate_manifest(manifest, root)


def test_manifest_schema_declares_all_four_closed_shapes_and_13_cases():
    spec = json.loads(
        (ROOT / "benchmarks/cross_repo/v0.1/manifest.schema.json").read_text(encoding="utf-8")
    )
    assert spec["additionalProperties"] is False
    assert spec["$defs"]["repository"]["additionalProperties"] is False
    assert spec["$defs"]["case"]["additionalProperties"] is False
    assert spec["properties"]["coverage"]["items"]["additionalProperties"] is False
    assert spec["properties"]["cases"]["minItems"] == 13


def test_manifest_13th_case_remains_not_run_and_fixture_pinned():
    manifest, root = _manifest_fixture()
    validate_manifest(manifest, root)
    case = next(c for c in manifest["cases"] if c["id"] == "CROSS-EXCH-013")
    assert case["status"] == "NOT_RUN"
    assert case["input_type"] == "SYNTHETIC_FIXTURE_ONLY"
