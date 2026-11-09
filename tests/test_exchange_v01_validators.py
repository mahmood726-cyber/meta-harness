"""Synthetic refusal controls for the stacked v0.1 validators.

Fictional run records test local consistency only. They are never saved as
benchmark evidence and no network, clinical source, or VCS command is used.
"""
import copy
import json

import pytest

from test_exchange_v01 import ROOT, SYNTHETIC, exchange
from harness.exchange_v01 import validate_exchange, validate_manifest
from harness.exchange_v01.wire import validate_exchange_json, validate_manifest_json

MANIFEST = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
BOUNDARY_WHITESPACE = [" ", "\t", "\n", "\r", "\u00a0", "\u001c", "\u001f",
                       "\u0085", "\u2028", "\u2029", "\u3000", "\ufeff"]


@pytest.fixture(params=["parsed", "wire"])
def exchange_check(request):
    if request.param == "wire":
        return lambda item: validate_exchange_json(json.dumps(item).encode("utf-8"), ROOT)
    return lambda item: validate_exchange(item, ROOT)


@pytest.fixture(params=["parsed", "wire"])
def manifest_check(request):
    if request.param == "wire":
        return lambda item: validate_manifest_json(json.dumps(item).encode("utf-8"), MANIFEST.parent)
    return lambda item: validate_manifest(item, MANIFEST.parent)


def manifest_fixture():
    """Supply the entire synthetic suite even before its missing rows are ported.

    This keeps missing-check controls independent of the on-disk row additions.
    """
    item = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing = {case["id"] for case in item["cases"]}
    for number in range(1, 16):
        cid = f"CROSS-EXCH-{number:03d}"
        if cid not in existing:
            case = copy.deepcopy(item["cases"][0])
            case.update(id=cid, description="Synthetic registry completeness control")
            item["cases"].append(case)
    return item


def executed_manifest(status="PASS", repository="meta-harness"):
    item = manifest_fixture()
    case = item["cases"][0]
    case.update(status=status, run_evidence={
        "action_run_url": f"https://github.com/mahmood726-cyber/{repository}/actions/runs/123456789",
        "commit_sha": item["repositories"][repository]["commit"],
        "input_sha256": case["input_sha256"],
        "job_name": "synthetic-structure-control-not-a-real-run",
    })
    return item


class TestIdentity:
    @pytest.mark.parametrize("field", ["study_id", "trial_id"])
    @pytest.mark.parametrize("padding", BOUNDARY_WHITESPACE)
    @pytest.mark.parametrize("side", ["leading", "trailing"])
    def test_boundary_whitespace_refuses(self, exchange_check, field, padding, side):
        item = exchange()
        original = item["rows"][0][field]
        item["rows"][0][field] = (padding + original if side == "leading" else original + padding)
        with pytest.raises(ValueError, match=f"{field} has noncanonical"):
            exchange_check(item)

    def test_padded_trial_alias_cannot_bypass_deduplication(self, exchange_check):
        item = exchange()
        second = copy.deepcopy(item["rows"][0])
        second["study_id"] = "SYNTHETIC-REPORT-TWO"
        second["trial_id"] = " " + second["trial_id"] + " "
        item["rows"].append(second)
        before = copy.deepcopy(item)
        with pytest.raises(ValueError, match="trial_id has noncanonical"):
            exchange_check(item)
        assert item == before  # Refusal must not silently normalize provenance.

    @pytest.mark.parametrize("trial", ["", "   ", None, 123])
    def test_existing_missing_or_untyped_trial_refusal(self, exchange_check, trial):
        item = exchange()
        item["rows"][0]["trial_id"] = trial
        with pytest.raises(ValueError, match="trial_id missing or empty"):
            exchange_check(item)

    def test_internal_whitespace_and_single_character_ids_stay_unchanged(self, exchange_check):
        item = exchange()
        item["rows"][0].update(study_id="S", trial_id="SYNTHETIC TRIAL 001")
        before = copy.deepcopy(item)
        exchange_check(item)
        assert item == before


class TestSourceLocator:
    @pytest.mark.parametrize("locator", ["line 1", "lines 1-1", "line 3", "lines 2-3"])
    def test_forged_or_out_of_range_locator_refuses(self, exchange_check, locator):
        item = exchange()
        item["rows"][0]["source_span"]["locator"] = locator
        with pytest.raises(ValueError, match="source_span"):
            exchange_check(item)

    @pytest.mark.parametrize("locator", [
        "page 2", "paragraph 1", "line 0", "line 02", "lines 2-1",
        "line 2\n", "line 2\\n", "lines 2-9999999999", "line -2", " line 2",
    ])
    def test_malformed_or_unsupported_locator_refuses(self, exchange_check, locator):
        item = exchange()
        item["rows"][0]["source_span"]["locator"] = locator
        with pytest.raises(ValueError, match="source_span locator"):
            exchange_check(item)

    def test_multiline_passage_must_fit_entire_claimed_range(self, exchange_check):
        item = exchange()
        span = item["rows"][0]["source_span"]
        span["verbatim"] = SYNTHETIC.read_bytes().decode("utf-8").strip()
        span["locator"] = "line 2"
        with pytest.raises(ValueError, match="passage absent at cited source lines"):
            exchange_check(item)
        span["locator"] = "lines 1-2"
        exchange_check(item)

    @pytest.mark.parametrize("locator", ["line 2", "lines 2-2", "lines 1-2"])
    def test_correct_locator_accepts(self, exchange_check, locator):
        item = exchange()
        item["rows"][0]["source_span"]["locator"] = locator
        exchange_check(item)


class TestExchangeShape:
    @pytest.mark.parametrize("section", ["root", "proposed_pool", "row", "source", "source_span"])
    def test_unversioned_field_refuses(self, exchange_check, section):
        item = exchange()
        row = item["rows"][0]
        target = {"root": item, "proposed_pool": item["proposed_pool"],
                  "row": row, "source": row["source"], "source_span": row["source_span"]}[section]
        target["unversioned_pool_override"] = {"decision": "ALLOW"}
        with pytest.raises(ValueError, match="unsupported field"):
            exchange_check(item)


class TestManifestPins:
    @pytest.mark.parametrize("url", [
        "https://github.com/other-owner/meta-harness/actions/runs/123456789",
        "https://github.com/mahmood726-cyber/unpinned-repo/actions/runs/123456789",
        "https://github.com/mahmood726-cyber/meta-harness/actions/runs/0",
        "https://github.com/mahmood726-cyber/meta-harness/actions/runs/0123",
        "https://github.com/mahmood726-cyber/meta-harness/actions/runs/123?spoof=1",
    ])
    def test_pass_requires_pinned_repository_and_canonical_run_url(self, manifest_check, url):
        item = executed_manifest()
        item["cases"][0]["run_evidence"]["action_run_url"] = url
        with pytest.raises(ValueError, match="not from a pinned repository"):
            manifest_check(item)

    @pytest.mark.parametrize("wrong_pin", ["unrelated", "other-repository"])
    def test_pass_requires_that_repositories_exact_commit(self, manifest_check, wrong_pin):
        item = executed_manifest()
        item["cases"][0]["run_evidence"]["commit_sha"] = (
            "f" * 40 if wrong_pin == "unrelated" else item["repositories"]["e156"]["commit"])
        with pytest.raises(ValueError, match="not the pinned meta-harness commit"):
            manifest_check(item)

    @pytest.mark.parametrize("repository", ["meta-harness", "rapidmeta-kit", "e156-ecosystem-starter", "e156"])
    @pytest.mark.parametrize("status", ["PASS", "FAIL"])
    def test_matching_fictional_record_checks_structure_only(self, manifest_check, repository, status):
        manifest_check(executed_manifest(status, repository))


class TestManifestRegistry:
    @pytest.mark.parametrize("number", [1, 6, 11, 12, 13, 14, 15])
    def test_required_case_cannot_disappear(self, manifest_check, number):
        item = manifest_fixture()
        cid = f"CROSS-EXCH-{number:03d}"
        item["cases"] = [case for case in item["cases"] if case["id"] != cid]
        with pytest.raises(ValueError, match=f"missing required IDs:.*{cid}"):
            manifest_check(item)

    @pytest.mark.parametrize("cid", ["CROSS-R-014", "CROSS-EXCH-000", "CROSS-EXCH-14", "CROSS-EXCH-014\n"])
    def test_cross_lane_or_noncanonical_case_identity_refuses(self, manifest_check, cid):
        item = manifest_fixture()
        item["cases"][-1]["id"] = cid
        with pytest.raises(ValueError, match="unsupported CROSS-EXCH case namespace"):
            manifest_check(item)

    def test_renamed_case_cannot_leave_gap(self, manifest_check):
        item = manifest_fixture()
        item["cases"][-1]["id"] = "CROSS-EXCH-016"
        with pytest.raises(ValueError, match="missing required IDs:.*CROSS-EXCH-015"):
            manifest_check(item)

    def test_future_gap_refuses_even_when_floor_is_complete(self, manifest_check):
        item = manifest_fixture()
        future = copy.deepcopy(item["cases"][-1])
        future["id"] = "CROSS-EXCH-017"
        item["cases"].append(future)
        with pytest.raises(ValueError, match="missing required IDs:.*CROSS-EXCH-016"):
            manifest_check(item)

    def test_contiguous_future_case_and_reordering_accept(self, manifest_check):
        item = manifest_fixture()
        future = copy.deepcopy(item["cases"][-1])
        future["id"] = "CROSS-EXCH-016"
        item["cases"].insert(0, future)
        item["cases"].reverse()
        manifest_check(item)


class TestManifestShape:
    @pytest.mark.parametrize("section", ["root", "repository", "case", "coverage"])
    def test_unversioned_field_refuses(self, manifest_check, section):
        item = manifest_fixture()
        target = {"root": item, "repository": item["repositories"]["rapidmeta-kit"],
                  "case": item["cases"][0], "coverage": item["coverage"][0]}[section]
        target["silent_gate_override"] = {"status": "PASS"}
        with pytest.raises(ValueError, match="unsupported field"):
            manifest_check(item)

    @pytest.mark.parametrize("section,key", [
        ("root", "purpose"), ("repository", "dependency_identity"), ("case", "description"),
    ])
    @pytest.mark.parametrize("value", [None, "", " \t", 12])
    def test_required_provenance_metadata_refuses(self, manifest_check, section, key, value):
        item = manifest_fixture()
        target = {"root": item, "repository": item["repositories"]["rapidmeta-kit"],
                  "case": item["cases"][0]}[section]
        if value is None:
            del target[key]
        else:
            target[key] = value
        with pytest.raises(ValueError, match=f"{key} missing or empty"):
            manifest_check(item)

    @pytest.mark.parametrize("value", [None, 123, int("1" * 40), "F" * 40, "0" * 39, "0" * 41, "0" * 40 + "\n"])
    def test_invalid_declared_lock_blob_refuses(self, manifest_check, value):
        item = manifest_fixture()
        item["repositories"]["meta-harness"]["dependency_lock_git_blob"] = value
        with pytest.raises(ValueError, match="invalid dependency_lock_git_blob"):
            manifest_check(item)

    def test_integer_repository_commit_is_not_a_string_pin(self, manifest_check):
        item = manifest_fixture()
        item["repositories"]["meta-harness"]["commit"] = int("1" * 40)
        with pytest.raises(ValueError, match="exact Git commit pin required"):
            manifest_check(item)

    @pytest.mark.parametrize("entry", [None, [], "not-an-object"])
    def test_nonobject_coverage_refuses_cleanly(self, manifest_check, entry):
        item = manifest_fixture()
        item["coverage"][0] = entry
        with pytest.raises(ValueError, match="coverage"):
            manifest_check(item)

    @pytest.mark.parametrize("field,value", [("id", []), ("id", {}), ("status", []), ("status", {})])
    def test_untyped_coverage_field_refuses_cleanly(self, manifest_check, field, value):
        item = manifest_fixture()
        item["coverage"][0][field] = value
        with pytest.raises(ValueError, match="id missing or empty|coverage"):
            manifest_check(item)

    def test_optional_dependency_lock_can_be_absent(self, manifest_check):
        item = manifest_fixture()
        del item["repositories"]["meta-harness"]["dependency_lock_git_blob"]
        manifest_check(item)


class TestManifestStatus:
    @pytest.mark.parametrize("evidence", [None, {}])
    def test_fail_requires_execution_record(self, manifest_check, evidence):
        item = manifest_fixture()
        item["cases"][0]["status"] = "FAIL"
        if evidence is not None:
            item["cases"][0]["run_evidence"] = evidence
        with pytest.raises(ValueError, match="FAIL without matching, complete run evidence"):
            manifest_check(item)

    @pytest.mark.parametrize("field,value", [
        ("action_run_url", "https://github.com/other-owner/meta-harness/actions/runs/123"),
        ("commit_sha", "f" * 40), ("input_sha256", "f" * 64), ("job_name", ""),
    ])
    def test_fail_reuses_exact_pin_and_complete_evidence_gate(self, manifest_check, field, value):
        item = executed_manifest("FAIL")
        item["cases"][0]["run_evidence"][field] = value
        with pytest.raises(ValueError):
            manifest_check(item)

    @pytest.mark.parametrize("status", ["NOT_RUN", "BLOCKED"])
    @pytest.mark.parametrize("evidence", [None, {}, "complete"])
    def test_nonexecuted_status_forbids_even_empty_evidence(self, manifest_check, status, evidence):
        item = executed_manifest()
        case = item["cases"][0]
        case["status"] = status
        if evidence != "complete":
            case["run_evidence"] = evidence
        with pytest.raises(ValueError, match="run_evidence requires PASS or FAIL"):
            manifest_check(item)

    @pytest.mark.parametrize("status", ["PASS", "FAIL"])
    def test_unversioned_execution_evidence_refuses(self, manifest_check, status):
        item = executed_manifest(status)
        item["cases"][0]["run_evidence"]["fictitious_attestation"] = "yes"
        with pytest.raises(ValueError, match="unsupported field"):
            manifest_check(item)

    @pytest.mark.parametrize("status", [[], {}, 15])
    def test_untyped_status_refuses_cleanly(self, manifest_check, status):
        item = manifest_fixture()
        item["cases"][0]["status"] = status
        with pytest.raises(ValueError, match="unknown status"):
            manifest_check(item)
