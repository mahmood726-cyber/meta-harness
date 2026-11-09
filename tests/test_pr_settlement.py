"""Current-tree negative cases for the open PRs, using synthetic evidence only.

The architecture inventory is a fixed fixture so these tests need no VCS.
The declaration, batch, ledger, raw parser and filesystem gates remain real.
This is local structural validation, not independent scientific validation.
"""
import copy
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from harness import prospective
from harness.exchange_v01 import validate_exchange
from harness.exchange_v01.wire import main, validate_exchange_json, validate_manifest_json
from harness.provenance.evidence import REQUIRED, sha256, validate_extraction
from scripts import run_prospective_topic as runner
from test_exchange_v01 import ROOT, exchange
from test_exchange_v01_validators import MANIFEST, manifest_fixture
from test_prospective_runner_live_acquisition import _live_snapshot


def _dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture
def batch(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    spec = root / prospective.SPEC_REL
    spec.parent.mkdir(parents=True)
    spec.write_bytes((ROOT / prospective.SPEC_REL).read_bytes())
    inventory = {"model_stages": {"stages": []}, "synthetic": True}
    monkeypatch.setattr(prospective.architecture_identity, "components", lambda *_: inventory)
    monkeypatch.setattr(prospective.architecture_identity, "mutable_dependencies", lambda *_: [])
    ledger = tmp_path / "defects.jsonl"
    monkeypatch.setenv(prospective.DEFECT_ENV, str(ledger))
    declaration = prospective.batch_declaration(
        root, "batch", 60, ["synthetic census"], "a" * 64,
        {"definition": "synthetic universe", "version": "test", "digest": "b" * 64},
        declared_utc="2026-10-24T00:00:00Z",
    )
    prospective.write_declaration(root, declaration)
    record = prospective.run_record(
        root, "batch", "topic", "2026-10-24T00:01:00Z", "2026-10-24T00:01:30Z",
        "COMPLETED", ["synthetic.json"], run_id="original",
    )
    package = root / "prospective/batch/runs/original"
    _dump(package / "synthetic.json", {"synthetic": True})
    prospective.write_run_record(package, record)
    assert prospective.check_batch(root, "batch")["ok"] is True
    return root, declaration, record, package, ledger


def test_pr124_claim_corrections_are_present():
    how = (ROOT / "HOW_IT_WORKS.md").read_text(encoding="utf-8")
    spec = (ROOT / prospective.SPEC_REL).read_text(encoding="utf-8")
    for phrase in (
        "15 verification limbs", "two-limb publication gate", "not evidence of prospective registration",
        "does not regenerate the served bytes", "not an independent estimate",
    ):
        assert phrase in how
    assert "docs/offline/requirements.lock" in spec
    assert "that number is historical" in spec
    assert "there is no\n  lockfile" not in spec


def test_pr125_self_declared_adjudication_already_refuses():
    source = b"synthetic source: HR 0.80"
    record = dict.fromkeys(REQUIRED, "synthetic")
    record.update(document_sha256=sha256(source), verbatim_passage="HR 0.80", status="ADJUDICATED")
    with pytest.raises(ValueError, match="adjudication verifier is not implemented"):
        validate_extraction(record, source)


@pytest.mark.parametrize("relative", ["records.json", "cache/plant/records.json"])
def test_pr125_body_preseeded_replay_refuses(tmp_path, monkeypatch, relative):
    out = tmp_path / "run"
    _dump(out / relative, {"records": []})
    refresh = Mock(side_effect=AssertionError("preseeded evidence reached retrieval"))
    monkeypatch.setattr(runner.acquisition, "refresh", refresh)
    with pytest.raises(prospective.ProspectiveRefusal, match="pre-existing records"):
        runner._load_or_refresh({"slug": "plant"}, out, "2026-10-24")
    refresh.assert_not_called()


@pytest.mark.parametrize("mutation,reason", [
    ("replay", "REFRESH"), ("empty", "no archived raw HTTP calls"),
    ("index", "raw index SHA256 differs"), ("body", "raw response SHA256 differs"),
    ("count", "raw index count differs"), ("missing", "raw response missing"),
])
def test_pr125_body_unauditable_retrieval_refuses(tmp_path, monkeypatch, mutation, reason):
    out = tmp_path / "run"
    snapshot = _live_snapshot(out)
    ledger_path = snapshot / runner.acquisition.LEDGER_FILENAME
    ledger = json.loads(ledger_path.read_bytes())
    if mutation == "replay":
        ledger["snapshot"]["mode"] = "REPLAY"
    elif mutation == "empty":
        ledger["snapshot"]["raw_calls"] = 0
    elif mutation == "count":
        ledger["snapshot"]["raw_calls"] = 2
    elif mutation == "index":
        (snapshot / "raw/INDEX.json").write_bytes(b"[]")
    elif mutation == "body":
        (snapshot / "raw/pubmed/001.json").write_bytes(b"changed")
    elif mutation == "missing":
        (snapshot / "raw/pubmed/001.json").unlink()
    _dump(ledger_path, ledger)
    monkeypatch.setattr(runner.acquisition, "refresh", lambda *_a, **_k: str(snapshot))
    with pytest.raises(prospective.ProspectiveRefusal, match=reason):
        runner._load_or_refresh({"slug": "plant"}, out, "2026-10-24")


def test_pr130_distinct_reports_cannot_duplicate_one_trial():
    item = exchange()
    second = copy.deepcopy(item["rows"][0])
    second["study_id"] = "SYNTHETIC-SECOND-REPORT"
    item["rows"].append(second)
    with pytest.raises(ValueError, match="duplicate trial_id"):
        validate_exchange(item, ROOT)
    second["trial_id"] = "SYNTHETIC-SECOND-TRIAL"
    validate_exchange(item, ROOT)


@pytest.mark.parametrize("escaped", [False, True])
def test_pr136_wire_refusal_cannot_be_shadowed(escaped):
    item = exchange()
    raw = json.dumps(item)
    key = r'"\u0064ecision"' if escaped else '"decision"'
    raw = raw.replace('"decision": "ALLOW"', key + ': "REFUSE", "decision": "ALLOW"', 1)
    assert json.loads(raw) == item
    with pytest.raises(ValueError, match="duplicate JSON object member: decision"):
        validate_exchange_json(raw.encode("utf-8"), ROOT)


@pytest.mark.parametrize("escaped", [False, True])
def test_pr146_manifest_failure_cannot_be_shadowed_in_api_or_cli(tmp_path, capsys, escaped):
    item = manifest_fixture()
    raw = json.dumps(item)
    key = r'"\u0073tatus"' if escaped else '"status"'
    raw = raw.replace('"status": "NOT_RUN"', key + ': "FAIL", "status": "NOT_RUN"', 1)
    assert json.loads(raw) == item
    with pytest.raises(ValueError, match="duplicate JSON object member: status"):
        validate_manifest_json(raw, MANIFEST.parent)
    path = tmp_path / "manifest.json"
    path.write_text(raw, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate JSON object member: status"):
        main([str(path)])
    assert "MANIFEST VERIFIED" not in capsys.readouterr().out


@pytest.mark.parametrize("timestamp", ["2026-10-24T00:01:00Z", "2026-10-24T00:01:01Z", "bad", "", None, "OMITTED"])
def test_pr135_declaration_must_precede_run(batch, timestamp):
    root, declaration, _, _, _ = batch
    if timestamp == "OMITTED":
        declaration.pop("declared_utc")
    else:
        declaration["declared_utc"] = timestamp
    _dump(prospective.declaration_path(root, "batch"), declaration)
    with pytest.raises(prospective.ProspectiveRefusal, match="declaration"):
        prospective.check_batch(root, "batch")


def test_pr135_offset_predeclaration_is_accepted(batch):
    root, declaration, _, _, _ = batch
    declaration["declared_utc"] = "2026-10-24T01:00:00+01:00"
    _dump(prospective.declaration_path(root, "batch"), declaration)
    assert prospective.check_batch(root, "batch")["ok"] is True


@pytest.mark.parametrize("timestamp", [None, "", "bad", "OMITTED"])
def test_pr135_missing_start_cannot_bypass_predeclaration(batch, timestamp):
    root, _, record, package, _ = batch
    if timestamp == "OMITTED":
        record.pop("started_utc")
    else:
        record["started_utc"] = timestamp
    _dump(package / "run_record.json", record)
    with pytest.raises(prospective.ProspectiveRefusal, match="UTC timestamp"):
        prospective.check_batch(root, "batch")


@pytest.mark.parametrize("batch_id", ["other", "", None, "OMITTED", "ARRAY"])
def test_pr137_failed_record_cannot_disappear(batch, batch_id):
    root, _, record, package, _ = batch
    failed = {**record, "run_id": "failed", "topic_identifier": "failed-topic", "outcome": "FAILED_CRASH"}
    if batch_id == "OMITTED":
        failed.pop("batch_id")
    elif batch_id == "ARRAY":
        failed = [failed]
    else:
        failed["batch_id"] = batch_id
    _dump(package.parent / "failed/run_record.json", failed)
    with pytest.raises(prospective.ProspectiveRefusal, match="run record batch_id"):
        prospective.check_batch(root, "batch")


@pytest.mark.parametrize("citation,accepted", [
    ("defect-plant", True), ("linked to (defect-plant) after failure", True),
    ("defect-plant-v2", False), ("prefixdefect-plant", False),
    ("defect-plant.extra", False), ("defect-plant_2", False),
    ("DEFECT-plant", False), ("defect-pla", False),
])
def test_pr143_citation_is_a_complete_identifier_and_original_failure_stays(batch, citation, accepted):
    root, _, record, package, ledger = batch
    record["outcome"] = "FAILED_CRASH"
    _dump(package / "run_record.json", record)
    retry = {**record, "run_id": "retry", "outcome": "COMPLETED", "rerun_of": "original",
             "rerun_justification": citation, "started_utc": "2026-10-24T00:03:00Z",
             "finished_utc": "2026-10-24T00:03:30Z"}
    _dump(package.parent / "retry/synthetic.json", {"synthetic": True})
    _dump(package.parent / "retry/run_record.json", retry)
    defect = prospective.defect_entry(
        "batch", "topic", "original", "FAILED_CRASH", "runner killed", "synthetic incident",
        entry_id="defect-plant", declared_utc="2026-10-24T00:02:00Z",
    )
    prospective.append_defect(defect, ledger, root=root)
    with pytest.raises(prospective.ProspectiveRefusal) as caught:
        prospective.check_batch(root, "batch")
    assert "1 of 2 retained" in str(caught.value)
    assert ("rerun lacks a prior defect-ledger entry" not in str(caught.value)) is accepted


@pytest.mark.parametrize("limit", [float("nan"), float("inf"), -float("inf"), True, False, None, "60", "", 0, -1, [], {}])
def test_pr155_invalid_time_limit_refuses_at_construction_and_freeze(batch, limit):
    root, declaration, _, _, _ = batch
    with pytest.raises(prospective.ProspectiveRefusal, match="time_limit_s"):
        prospective.batch_declaration(root, "other", limit, ["synthetic"], "a" * 64, declaration["universe_ref"])
    declaration["time_limit_s"] = limit
    with pytest.raises(prospective.ProspectiveRefusal, match="time_limit_s"):
        prospective.check_declaration_frozen(root, declaration)


@pytest.mark.parametrize("limit", [float("nan"), float("inf"), -float("inf")])
def test_pr155_nonstandard_json_time_limit_refuses_on_load(batch, limit):
    root, declaration, _, _, _ = batch
    declaration["time_limit_s"] = limit
    _dump(prospective.declaration_path(root, "batch"), declaration)
    with pytest.raises(prospective.ProspectiveRefusal, match="non-finite JSON number"):
        prospective.load_declaration(root, "batch")


@pytest.mark.parametrize("limit", [1, 30.5, 60])
def test_pr155_finite_positive_limits_preserve_representation(batch, limit):
    root, declaration, _, _, _ = batch
    item = prospective.batch_declaration(root, "other", limit, ["synthetic"], "a" * 64, declaration["universe_ref"])
    assert type(item["time_limit_s"]) is type(limit)
    assert prospective.check_declaration_frozen(root, item) == item


@pytest.mark.parametrize("limit,finished,accepted", [
    (60, "2026-10-24T00:02:00Z", True),
    (60, "2026-10-24T00:02:00.001Z", False),
    (60, "2026-10-24T01:02:00+01:00", True),
    (60, "2026-10-24T01:02:01+01:00", False),
    (0.5, "2026-10-24T00:01:00.500Z", True),
    (0.5, "2026-10-24T00:01:00.501Z", False),
])
def test_pr157_completed_deadline_is_enforced(batch, limit, finished, accepted):
    root, declaration, record, package, _ = batch
    declaration["time_limit_s"] = limit
    record["finished_utc"] = finished
    _dump(prospective.declaration_path(root, "batch"), declaration)
    _dump(package / "run_record.json", record)
    if accepted:
        assert prospective.check_batch(root, "batch")["ok"] is True
    else:
        with pytest.raises(prospective.ProspectiveRefusal, match="COMPLETED after predeclared time_limit_s"):
            prospective.check_batch(root, "batch")


@pytest.mark.parametrize("finished", [None, "", "bad", "2026-10-24T00:00:59Z", "OMITTED"])
def test_pr157_uncheckable_finish_refuses(batch, finished):
    root, _, record, package, _ = batch
    if finished == "OMITTED":
        record.pop("finished_utc")
    else:
        record["finished_utc"] = finished
    _dump(package / "run_record.json", record)
    with pytest.raises(prospective.ProspectiveRefusal, match="UTC timestamp|finished before started"):
        prospective.check_batch(root, "batch")


@pytest.mark.parametrize("outcome", ["FAILED_CRASH", "FAILED_TIMEOUT", "FAILED_INVARIANT"])
def test_pr157_failed_overrun_keeps_original_outcome(batch, outcome):
    root, _, record, package, _ = batch
    record.update(outcome=outcome, finished_utc="2026-10-24T00:03:00Z")
    path = package / "run_record.json"
    _dump(path, record)
    before = path.read_bytes()
    with pytest.raises(prospective.ProspectiveRefusal, match="batch contains failed prospective runs") as caught:
        prospective.check_batch(root, "batch")
    assert outcome in str(caught.value)
    assert "COMPLETED after" not in str(caught.value)
    assert path.read_bytes() == before


@pytest.mark.parametrize("policy", ["No limits", "", None, False, [], "OMITTED", "APPEND_SPACE"])
def test_pr159_frozen_rerun_policy_cannot_drift(batch, policy):
    root, declaration, _, _, _ = batch
    if policy == "OMITTED":
        declaration.pop("rerun_policy")
    elif policy == "APPEND_SPACE":
        declaration["rerun_policy"] += " "
    else:
        declaration["rerun_policy"] = policy
    with pytest.raises(prospective.ProspectiveRefusal, match="declared rerun policy differs"):
        prospective.check_declaration_frozen(root, declaration)


@pytest.mark.parametrize("kind", ["declaration", "run", "defect"])
@pytest.mark.parametrize("nested", [False, True])
def test_pr163_duplicate_members_refuse_in_each_evidence_loader(batch, kind, nested):
    root, declaration, record, package, ledger = batch
    if kind == "declaration":
        item, path = declaration, prospective.declaration_path(root, "batch")
        loader = prospective.load_declaration
    elif kind == "run":
        item, path, loader = record, package / "run_record.json", prospective.load_run_records
    else:
        item, path, loader = {"batch_id": "batch", "id": "defect-plant"}, ledger, prospective.load_defects
    raw = json.dumps(item)
    if nested:
        raw = raw[:-1] + ', "evidence": {"attribution":"unknown", "attribution":"runner killed"}}'
    else:
        raw = raw.replace('"batch_id": "batch"', '"batch_id":"other", "batch_id":"batch"', 1)
    path.write_text(raw + "\n", encoding="utf-8")
    with pytest.raises(prospective.ProspectiveRefusal, match="duplicate JSON member"):
        loader(root, "batch")


def test_pr163_unique_members_still_load_at_all_boundaries(batch):
    root, declaration, record, _, ledger = batch
    assert prospective.load_declaration(root, "batch") == declaration
    assert prospective.load_run_records(root, "batch") == [record]
    entry = {"batch_id": "batch", "id": "defect-plant"}
    ledger.write_text(json.dumps(entry) + "\n", encoding="utf-8")
    assert prospective.load_defects(root, "batch") == [entry]
