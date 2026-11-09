"""Synthetic custody regressions; no network, git or scientific validation.

The runner tests isolate the already frozen declaration and record-construction
boundaries. Files, archive verification and retained-inventory checks are real.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from harness import prospective
from scripts import run_prospective_topic as runner


def _dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _snapshot(out):
    snapshot = out / "cache" / "topic" / "snapshots" / "synthetic"
    rows = []
    for name, body in [("one", b"synthetic response"), ("empty", b""), ("binary", b"\x00\xff")]:
        fields = {
            "source_id": "concept#1", "url": "https://example.invalid/query",
            "params": {"q": "synthetic concept"}, "status": 200,
            "fetched_utc": "2026-10-24T00:00:00Z", "adapter": "synthetic",
            "adapter_blob_sha": "a" * 40,
            "body_sha256": hashlib.sha256(body).hexdigest(),
        }
        path = _dump(snapshot / "raw" / "concept" / f"{name}.json", {
            **fields, "body_bytes_b64": base64.b64encode(body).decode("ascii"),
        })
        rows.append({**fields, "path": path.relative_to(snapshot).as_posix(),
                     "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    _dump(snapshot / "raw" / "INDEX.json", rows)
    ledger = {
        "snapshot": {"mode": "REFRESH", "raw_calls": len(rows)},
        "sources": [{"source_id": "concept#1", "kind": "PUBMED_CONCEPT_QUERY",
                     "discovery_capable": True, "query": "synthetic concept",
                     "state": "RAN_OK", "funnel": {"cap": {"kind": "none"}}}],
    }
    _save_ledger(snapshot, ledger)
    _dump(snapshot / "records.json", {"records": []})
    return snapshot, ledger


def _save_ledger(snapshot, ledger):
    ledger["snapshot"]["raw_index_sha256"] = hashlib.sha256(
        (snapshot / "raw" / "INDEX.json").read_bytes()
    ).hexdigest()
    _dump(snapshot / runner.acquisition.LEDGER_FILENAME, ledger)


@pytest.fixture
def synthetic_run(monkeypatch):
    monkeypatch.setattr(prospective, "load_declaration", lambda *_: {"time_limit_s": 60, "invariants": []})
    monkeypatch.setattr(prospective, "check_declaration_frozen", lambda *_: None)

    def record(_root, batch, topic, started, finished, outcome, paths, **_kw):
        return {"run_id": "synthetic-run", "batch_id": batch,
                "topic_identifier": topic, "outcome": outcome, "artefact_paths": paths}

    monkeypatch.setattr(prospective, "run_record", record)
    package = Mock(side_effect=lambda _config, _records, out, *_args, **_kw: [
        _dump(out / "synthetic-result.json", {"fixture": True})
    ])
    monkeypatch.setattr(runner, "_package_review", package)
    return package


def test_config_is_read_once_and_archived_before_parse(tmp_path, monkeypatch, synthetic_run):
    original = b'{"slug":"topic","topic_identifier":"original"}\n'
    replacement = b'{"slug":"changed","topic_identifier":"changed"}\n'
    config = tmp_path / "topic.json"
    config.write_bytes(original)
    actual_open = io.open
    reads = []

    class ChangeAfterRead:
        def __init__(self, handle):
            self.handle = handle

        def __enter__(self):
            self.handle.__enter__()
            return self

        def read(self, *args, **kwargs):
            return self.handle.read(*args, **kwargs)

        def __exit__(self, *args):
            result = self.handle.__exit__(*args)
            config.write_bytes(replacement)
            return result

    def injected_open(path, mode="r", *args, **kwargs):
        handle = actual_open(path, mode, *args, **kwargs)
        if str(path) == str(config) and "r" in mode:
            reads.append(mode)
            return ChangeAfterRead(handle)
        return handle

    monkeypatch.setattr(io, "open", injected_open)
    refresh = Mock(side_effect=RuntimeError("synthetic stop"))
    monkeypatch.setattr(runner.acquisition, "refresh", refresh)
    out = tmp_path / "run"
    result = runner.run_topic("batch", str(config), str(out))
    assert result["outcome"] == "FAILED_CRASH"
    assert len(reads) == 1
    assert refresh.call_args.args[0]["slug"] == "topic"
    assert (out / "topic-config.json").read_bytes() == original
    assert json.loads((out / "run_record.json").read_bytes())["topic_identifier"] == "original"


@pytest.mark.parametrize("raw", [b'{"slug":', b"\xff", b"[]", b'{"slug":"topic","x":NaN}',
                                     b'{"slug":"topic","nested":{"x":1e999}}'])
def test_invalid_config_bytes_are_retained(tmp_path, monkeypatch, synthetic_run, raw):
    config = tmp_path / "topic.json"
    config.write_bytes(raw)
    refresh = Mock(side_effect=AssertionError("invalid input reached acquisition"))
    monkeypatch.setattr(runner.acquisition, "refresh", refresh)
    out = tmp_path / "run"
    result = runner.run_topic("batch", str(config), str(out))
    assert result["outcome"] != "COMPLETED"
    refresh.assert_not_called()
    assert (out / "topic-config.json").read_bytes() == raw
    record = json.loads((out / "run_record.json").read_bytes())
    assert "topic-config.json" in record["artefact_paths"]
    assert "failure.json" in record["artefact_paths"]


@pytest.mark.parametrize("mutate,reason", [
    ("body", "body SHA256 mismatch"), ("metadata", "mismatch: status"),
    ("duplicate_path", "duplicate"), ("duplicate_key", "duplicate"),
    ("nonfinite", "non-finite"), ("escape", "unsafe"),
    ("bad_index_sha", "index SHA256"), ("bad_file_sha", "SHA256"),
])
def test_archive_refuses_rehashed_corruption(tmp_path, monkeypatch, mutate, reason):
    snapshot, ledger = _snapshot(tmp_path / "run")
    index = snapshot / "raw" / "INDEX.json"
    rows = json.loads(index.read_bytes())
    path = snapshot / rows[0]["path"]
    envelope = json.loads(path.read_bytes())
    if mutate == "body":
        envelope["body_bytes_b64"] = base64.b64encode(b"changed").decode("ascii")
        _dump(path, envelope)
    elif mutate == "metadata":
        envelope["status"] = 200.0
        _dump(path, envelope)
    elif mutate == "duplicate_key":
        path.write_bytes(path.read_bytes().replace(b'"status": 200', b'"status": 500, "status": 200'))
    elif mutate == "nonfinite":
        envelope["extra"] = float("nan")
        _dump(path, envelope)
    rows[0]["file_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    if mutate == "duplicate_path":
        rows.append(rows[0])
        ledger["snapshot"]["raw_calls"] += 1
    elif mutate == "escape":
        rows[0]["path"] = "raw/concept/../one.json"
    elif mutate == "bad_file_sha":
        rows[0]["file_sha256"] = "0" * 64
    _dump(index, rows)
    _save_ledger(snapshot, ledger)
    if mutate == "bad_index_sha":
        index.write_bytes(index.read_bytes() + b" ")
    monkeypatch.setattr(runner.acquisition, "refresh", lambda *_a, **_k: str(snapshot))
    with pytest.raises(prospective.ProspectiveRefusal, match=reason):
        runner._load_or_refresh({"slug": "topic"}, tmp_path / "run", "2026-10-24")


@pytest.mark.parametrize("change", ["seeded", "error", "capped", "no_response", "missing_sources"])
def test_concept_gate_stops_review_packaging(tmp_path, monkeypatch, synthetic_run, change):
    config = _dump(tmp_path / "topic.json", {"slug": "topic"})
    captured = []

    def refresh(_config, _day, *, root):
        snapshot, ledger = _snapshot(Path(root))
        source = ledger["sources"][0]
        if change == "seeded": source["kind"] = "PUBMED_PMID_ENUMERATION"
        elif change == "error": source["state"] = "RAN_ERROR"
        elif change == "capped": source["funnel"]["cap"]["kind"] = "hard_hits_cap"
        elif change == "no_response": source["source_id"] = "missing#1"
        elif change == "missing_sources": ledger.pop("sources")
        _save_ledger(snapshot, ledger)
        captured.append(snapshot)
        return str(snapshot)

    monkeypatch.setattr(runner.acquisition, "refresh", refresh)
    out = tmp_path / "run"
    result = runner.run_topic("batch", str(config), str(out))
    assert result["outcome"] == "FAILED_INVARIANT"
    synthetic_run.assert_not_called()
    record = json.loads((out / "run_record.json").read_bytes())
    assert captured[0].relative_to(out).as_posix() in record["artefact_paths"]


def test_corrupt_acquired_snapshot_is_cited_in_failed_record(tmp_path, monkeypatch, synthetic_run):
    config = _dump(tmp_path / "topic.json", {"slug": "topic"})
    captured = []

    def refresh(_config, _day, *, root):
        snapshot, _ = _snapshot(Path(root))
        (snapshot / "raw" / "concept" / "one.json").write_bytes(b"compromised")
        captured.append(snapshot)
        return str(snapshot)

    monkeypatch.setattr(runner.acquisition, "refresh", refresh)
    out = tmp_path / "run"
    result = runner.run_topic("batch", str(config), str(out))
    assert result["outcome"] == "FAILED_INVARIANT"
    synthetic_run.assert_not_called()
    record = json.loads((out / "run_record.json").read_bytes())
    assert captured[0].relative_to(out).as_posix() in record["artefact_paths"]
    assert (captured[0] / "raw" / "concept" / "one.json").read_bytes() == b"compromised"


@pytest.mark.parametrize("removed", ["raw/concept/one.json", "raw/concept/empty.json",
    "raw/concept/binary.json", "raw/INDEX.json", "records.json", runner.acquisition.LEDGER_FILENAME])
def test_each_acquired_file_is_in_retained_inventory(tmp_path, monkeypatch, synthetic_run, removed):
    config = _dump(tmp_path / "topic.json", {"slug": "topic"})
    captured = []

    def refresh(_config, _day, *, root):
        snapshot, _ = _snapshot(Path(root))
        captured.append(snapshot)
        return str(snapshot)

    monkeypatch.setattr(runner.acquisition, "refresh", refresh)
    out = tmp_path / "run"
    result = runner.run_topic("batch", str(config), str(out))
    assert result["outcome"] == "COMPLETED"
    synthetic_run.assert_called_once()
    record_path = out / "run_record.json"
    record = json.loads(record_path.read_bytes())
    snapshot = captured[0]
    retained = (snapshot / removed).relative_to(out).as_posix()
    assert retained in record["artefact_paths"]
    assert len(record["artefact_paths"]) == len(set(record["artefact_paths"]))
    assert prospective._retained_artefact_errors(record_path, record) == []
    (snapshot / removed).unlink()
    assert "retained artefact is missing or unreadable" in prospective._retained_artefact_errors(record_path, record)


@pytest.mark.parametrize("raw", ["null", "[]", "false", "42", '"text"'])
def test_non_object_defect_ledger_is_refused(tmp_path, monkeypatch, raw):
    root = tmp_path / "repo"
    root.mkdir()
    ledger = tmp_path / "defects.jsonl"
    ledger.write_text(raw + "\n", encoding="utf-8")
    monkeypatch.setenv(prospective.DEFECT_ENV, str(ledger))
    with pytest.raises(prospective.ProspectiveRefusal, match="not a JSON object"):
        prospective.load_defects(root, "batch")


@pytest.mark.parametrize("value", [True, False, None, "60", 0, -1, float("nan"), float("inf"), 10**1000])
def test_time_limit_validation_is_shared_and_strict(value):
    with pytest.raises(prospective.ProspectiveRefusal, match="time_limit_s"):
        prospective._require_finite_positive_time_limit(value)


def _batch(tmp_path, monkeypatch):
    """Isolate audit logic after the architecture-freeze boundary."""
    root = tmp_path / "repo"
    monkeypatch.setattr(prospective, "check_declaration_frozen", lambda *_: None)
    _dump(root / "prospective/batch/declaration.json", {
        "batch_id": "batch", "declared_utc": "2026-10-24T00:00:00Z", "time_limit_s": 60,
        "architecture_identity": "a" * 64, "external_dependency_mutability": False,
        "freeze_claim": prospective.IMMUTABLE_FREEZE_CLAIM,
    })
    record = {
        "schema_version": 1, "run_id": "original", "batch_id": "batch", "topic_identifier": "topic",
        "started_utc": "2026-10-24T00:01:00Z", "finished_utc": "2026-10-24T00:01:30Z",
        "architecture_identity": "a" * 64, "external_dependency_mutability": False,
        "freeze_claim": prospective.IMMUTABLE_FREEZE_CLAIM, "outcome": "COMPLETED",
        "artefact_paths": ["synthetic.json"], "rerun_of": None, "rerun_justification": None,
    }
    out = root / "prospective/batch/runs/original"
    _dump(out / "synthetic.json", {"fixture": True})
    _dump(out / "run_record.json", record)
    ledger = tmp_path / "defects.jsonl"
    monkeypatch.setenv(prospective.DEFECT_ENV, str(ledger))
    assert prospective.check_batch(root, "batch")["ok"] is True
    return root, out, record, ledger


@pytest.mark.parametrize("value", [[], {}, False, 42, "", "../original", ".", ".."])
def test_invalid_rerun_identifier_refuses_without_type_error(tmp_path, monkeypatch, value):
    root, out, record, _ = _batch(tmp_path, monkeypatch)
    record["rerun_of"] = value
    _dump(out / "run_record.json", record)
    with pytest.raises(prospective.ProspectiveRefusal, match="invalid rerun_of identifier"):
        prospective.check_batch(root, "batch")


@pytest.mark.parametrize("value", [["original"], {"id": "original"}])
def test_unhashable_run_identifier_refuses_without_type_error(tmp_path, monkeypatch, value):
    root, out, record, _ = _batch(tmp_path, monkeypatch)
    record["run_id"] = value
    _dump(out / "run_record.json", record)
    with pytest.raises(prospective.ProspectiveRefusal, match="run_id"):
        prospective.check_batch(root, "batch")


@pytest.mark.parametrize("value", [None, False, 42, [], {}, "", "bad/id", ".", ".."])
def test_malformed_defect_id_refuses(tmp_path, monkeypatch, value):
    root, _, _, ledger = _batch(tmp_path, monkeypatch)
    ledger.write_text(json.dumps({"id": value, "batch_id": "batch"}) + "\n", encoding="utf-8")
    with pytest.raises(prospective.ProspectiveRefusal, match="invalid.*id"):
        prospective.check_batch(root, "batch")


@pytest.mark.parametrize("attribution,permitted", [
    ("network outage", True), ("external network outage", True),
    (" PROVIDER 5XX ", True), ("runner killed", True),
    ("scientific disagreement", False), (None, False), ({"network outage": True}, False),
    ("", False),
])
def test_only_permitted_external_attributions_authorise_rerun(tmp_path, monkeypatch, attribution, permitted):
    root, out, record, ledger = _batch(tmp_path, monkeypatch)
    record["outcome"] = "FAILED_CRASH"
    _dump(out / "run_record.json", record)
    rerun = {**record, "run_id": "rerun", "outcome": "COMPLETED", "rerun_of": "original",
             "rerun_justification": "defect-1", "started_utc": "2026-10-24T00:03:00Z",
             "finished_utc": "2026-10-24T00:03:30Z"}
    _dump(out.parent / "rerun/synthetic.json", {"fixture": True})
    _dump(out.parent / "rerun/run_record.json", rerun)
    ledger.write_text(json.dumps({
        "id": "defect-1", "batch_id": "batch", "failed_run_id": "original",
        "topic_identifier": "topic", "failure_class": "FAILED_CRASH", "attribution": attribution,
        "declared_utc": "2026-10-24T00:02:00Z",
    }) + "\n", encoding="utf-8")
    with pytest.raises(prospective.ProspectiveRefusal) as caught:
        prospective.check_batch(root, "batch")
    assert "batch contains failed prospective runs" in str(caught.value)
    assert ("permitted A4 external infrastructure attribution" in str(caught.value)) is not permitted


def test_run_must_start_strictly_after_declaration(tmp_path, monkeypatch):
    root, out, record, _ = _batch(tmp_path, monkeypatch)
    record["started_utc"] = "2026-10-24T00:00:00Z"
    record["finished_utc"] = "2026-10-24T00:00:30Z"
    _dump(out / "run_record.json", record)
    with pytest.raises(prospective.ProspectiveRefusal, match="declaration"):
        prospective.check_batch(root, "batch")


def test_dangling_preseeded_cache_is_refused(tmp_path, monkeypatch):
    out = tmp_path / "run"
    out.mkdir()
    try:
        (out / "records.json").symlink_to(tmp_path / "missing.json")
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    refresh = Mock(side_effect=AssertionError("dangling cache reached acquisition"))
    monkeypatch.setattr(runner.acquisition, "refresh", refresh)
    with pytest.raises(prospective.ProspectiveRefusal, match="pre-existing records"):
        runner._load_or_refresh({"slug": "topic"}, out, "2026-10-24")
    refresh.assert_not_called()


@pytest.mark.parametrize("value", [True, False, None, "60", 0, -1, float("nan"), float("inf"), 10**1000])
def test_invalid_ceiling_refused_before_architecture_inventory(tmp_path, monkeypatch, value):
    inventory = Mock(side_effect=AssertionError("invalid ceiling reached architecture inventory"))
    monkeypatch.setattr(prospective.architecture_identity, "components", inventory)
    with pytest.raises(prospective.ProspectiveRefusal, match="time_limit_s"):
        prospective.batch_declaration(tmp_path, "batch", value, ["census"], "a" * 64, {})
    with pytest.raises(prospective.ProspectiveRefusal, match="time_limit_s"):
        prospective.check_declaration_frozen(tmp_path, {"schema_version": 1, "time_limit_s": value})
    inventory.assert_not_called()


def test_real_raw_recorder_receipts_verify_for_binary_and_empty_bodies(tmp_path):
    """Exercise actual recorder I/O with explicitly synthetic adapter provenance."""
    recorder = runner.acquisition.RawRecorder()
    for body in (b"synthetic response", b"", b"\x00\xff"):
        recorder.record(
            "concept#1", "https://example.invalid/query", {"q": "synthetic concept"}, 200, body,
            {"adapter": "synthetic", "adapter_blob_sha": "a" * 40},
        )
    snapshot = tmp_path / "snapshot"
    count, index_sha = recorder.write_snapshot(str(snapshot))
    ledger = {"snapshot": {"mode": "REFRESH", "raw_calls": count, "raw_index_sha256": index_sha}}
    rows = []
    verified = runner._verify_prospective_raw_archive(snapshot, ledger, raw_rows=rows)
    assert count == 3
    assert len(verified) == 4
    assert verified[0] == snapshot / "raw" / "INDEX.json"
    assert [base64.b64decode(json.loads(path.read_bytes())["body_bytes_b64"]) for path in verified[1:]] == [
        b"synthetic response", b"", b"\x00\xff",
    ]
    assert len(rows) == count
