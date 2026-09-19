from __future__ import annotations

import json
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import gate_scorecard  # noqa: E402


def _copy_file(src_root: Path, dst_root: Path, rel: str) -> None:
    src = src_root / rel
    dst = dst_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _evidence_paths(data: dict) -> set[str]:
    out: set[str] = set()

    def add(raw):
        for value in gate_scorecard._evidence_values(raw):
            if value.startswith("commit:") or value.startswith(gate_scorecard.EXTERNAL_EVIDENCE_PREFIXES):
                continue
            out.add(value)

    for entry in data["gates"]:
        for event in entry.get("events") or []:
            add(event.get("evidence"))
            adjudication = event.get("adjudication")
            if isinstance(adjudication, dict):
                add(adjudication.get("evidence"))
    return out


def _git_fixture(tmp: Path) -> None:
    """The scorecard check must name its target (HEAD); a mini root that is not a git tree is a
    refusal, not a pass. Lane X's tests passed only because its TMP lay inside the clone, so HEAD
    resolved by accident -- make the fixture a real, committed repository instead."""
    env = {"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
           "HOME": str(tmp), "USERPROFILE": str(tmp)}
    import os
    import subprocess
    full_env = {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")}, **env}  # never a hook GIT_DIR
    for cmd in (["git", "init", "-q"], ["git", "add", "-A"], ["git", "commit", "-q", "-m", "fixture"]):
        subprocess.run(cmd, cwd=tmp, check=True, capture_output=True, env=full_env)
def _replace_commit_evidence(tmp: Path, data: dict) -> None:
    def replace_list(values, stamp: str | None, gate_id: str) -> list:
        out = []
        for value in values:
            if isinstance(value, str) and value.startswith("commit:"):
                rel = f"docs/evidence/test-commit-{gate_id.replace('.', '-')}.txt"
                p = tmp / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(str(stamp or "commit evidence") + "\n", encoding="utf-8", newline="\n")
                out.append(rel)
            else:
                out.append(value)
        return out

    for entry in data["gates"]:
        for event in entry.get("events") or []:
            if isinstance(event.get("evidence"), list):
                event["evidence"] = replace_list(event["evidence"], event.get("when_utc"), entry["gate_id"])
            adjudication = event.get("adjudication")
            if isinstance(adjudication, dict) and isinstance(adjudication.get("evidence"), list):
                adjudication["evidence"] = replace_list(
                    adjudication["evidence"],
                    adjudication.get("when_utc") or event.get("when_utc"),
                    entry["gate_id"],
                )


@contextmanager
def _mini_root():
    with tempfile.TemporaryDirectory(prefix="gate-scorecard-test-", ignore_cleanup_errors=True) as raw:
        tmp = Path(raw)
        _populate_mini_root(tmp)
        _git_fixture(tmp)
        yield tmp


def _populate_mini_root(tmp: Path) -> None:
    for rel in (
        "scripts/verify_all.py",
        "scripts/build_evidence_index.py",
        "scripts/production_record.py",
        "harness/gate.py",
        "harness/census.py",
        ".githooks/pre-commit",
        ".githooks/commit-msg",
        "registry/gate_scorecard.json",
    ):
        _copy_file(ROOT, tmp, rel)
    data = json.loads((ROOT / gate_scorecard.REGISTRY_PATH).read_text(encoding="utf-8"))
    for rel in _evidence_paths(data):
        _copy_file(ROOT, tmp, rel)
    _replace_commit_evidence(tmp, data)
    _write(tmp, data)
    gate_scorecard.write_served_view(tmp)


def _load(root: Path) -> dict:
    return json.loads((root / gate_scorecard.REGISTRY_PATH).read_text(encoding="utf-8"))


def _write(root: Path, data: dict) -> None:
    (root / gate_scorecard.REGISTRY_PATH).write_text(
        json.dumps(data, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _first_event(data: dict, *, verdict: str | None = None, kind: str | None = None) -> dict:
    for gate in data["gates"]:
        for event in gate.get("events") or []:
            if verdict is not None and event.get("adjudication", {}).get("verdict") != verdict:
                continue
            if kind is not None and event.get("kind") != kind:
                continue
            return event
    raise AssertionError("matching event not found")


def test_gate_in_code_with_no_entry_refuses():
    with _mini_root() as root:
        data = _load(root)
        data["gates"] = data["gates"][1:]
        _write(root, data)
        gate_scorecard.write_served_view(root)
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("missing entry for enumerated gate" in r for r in reasons)


def test_dangling_evidence_path_refuses():
    with _mini_root() as root:
        data = _load(root)
        event = _first_event(data)
        event["evidence"] = ["docs/evidence/no-such-capture.txt"]
        _write(root, data)
        gate_scorecard.write_served_view(root)
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("cited evidence does not exist" in r for r in reasons)


def test_missing_registry_path_refuses_as_unnamed_target():
    with _mini_root() as root:
        (root / gate_scorecard.REGISTRY_PATH).unlink()
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert reasons == [
            "TARGET gate_scorecard: COULD-NOT-EXECUTE missing required path: registry/gate_scorecard.json"
        ]


def test_event_without_adjudication_object_refuses():
    with _mini_root() as root:
        data = _load(root)
        _first_event(data).pop("adjudication", None)
        _write(root, data)
        gate_scorecard.write_served_view(root)
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("every event needs an adjudication object" in r for r in reasons)


def test_verdict_outside_allowed_refuses():
    with _mini_root() as root:
        data = _load(root)
        _first_event(data)["adjudication"]["verdict"] = "MAYBE"
        _write(root, data)
        gate_scorecard.write_served_view(root)
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("verdict must be one of" in r for r in reasons)


def test_resolved_verdict_without_adjudicator_kind_refuses():
    with _mini_root() as root:
        data = _load(root)
        event = _first_event(data, verdict="TRUE_POSITIVE")
        event["adjudication"]["adjudicated_by"]["kind"] = None
        _write(root, data)
        gate_scorecard.write_served_view(root)
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("TRUE_POSITIVE requires adjudicated_by.kind" in r for r in reasons)


def test_resolved_verdict_without_adjudication_evidence_refuses():
    with _mini_root() as root:
        data = _load(root)
        event = _first_event(data, verdict="TRUE_POSITIVE")
        event["adjudication"]["evidence"] = []
        _write(root, data)
        gate_scorecard.write_served_view(root)
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("TRUE_POSITIVE requires adjudication evidence" in r for r in reasons)


def test_stored_precision_or_coverage_refuses():
    with _mini_root() as root:
        data = _load(root)
        data["gates"][0]["adjudicated_precision"] = 1.0
        _write(root, data)
        gate_scorecard.write_served_view(root)
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("stored precision/coverage numbers are refused" in r for r in reasons)


def test_unresolved_counted_as_tp_refuses():
    with _mini_root() as root:
        data = _load(root)
        event = _first_event(data, verdict="UNRESOLVED")
        event["counts_as"] = "TP"
        _write(root, data)
        gate_scorecard.write_served_view(root)
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("UNRESOLVED events must not be counted into TP or FP" in r for r in reasons)


def test_plant_counted_as_production_refuses():
    with _mini_root() as root:
        data = _load(root)
        event = _first_event(data, kind="PLANT")
        event["counts_as_production"] = True
        _write(root, data)
        gate_scorecard.write_served_view(root)
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("PLANT event must not be counted as PRODUCTION" in r for r in reasons)


def test_renderer_refuses_precision_without_coverage():
    try:
        gate_scorecard.format_computed_metrics({"adjudicated_precision": 1.0})
    except ValueError as exc:
        assert "precision is reported only beside its adjudication coverage" in str(exc)
    else:
        raise AssertionError("renderer accepted precision without coverage")


def test_compute_uses_only_adjudicated_production_refusals():
    gate = {
        "events": [
            {
                "kind": "PRODUCTION",
                "adjudication": {"verdict": "TRUE_POSITIVE", "adjudicated_by": {"kind": "author"}},
            },
            {
                "kind": "PRODUCTION",
                "adjudication": {"verdict": "FALSE_POSITIVE", "adjudicated_by": {"kind": "author"}},
            },
            {"kind": "PRODUCTION", "adjudication": {"verdict": "UNRESOLVED"}},
            {"kind": "PLANT", "adjudication": {"verdict": "TRUE_POSITIVE", "adjudicated_by": {"kind": "internal_agent"}}},
            {"kind": "PRODUCTION", "miss": True, "adjudication": {"verdict": "TRUE_MISS"}},
        ]
    }
    metrics = gate_scorecard.compute(gate)
    assert metrics["true_positive_production_refusals"] == 1
    assert metrics["false_positive_production_refusals"] == 1
    assert metrics["adjudicated_precision"] == 0.5
    assert metrics["adjudication_coverage"] == 2 / 3
    assert metrics["plant_validations"] == 1
    assert metrics["true_misses"] == 1


def test_migration_preserves_unresolved_when_no_adjudicator_and_author_when_named():
    data = {
        "gates": [
            {
                "gate_id": "sample.unadjudicated",
                "where": "sample:gate",
                "what_it_refuses": "sample refusal",
                "true_refusals": [
                    {"what": "refused", "when_utc": "2026-09-14T01:02:03Z", "evidence": ["GATE_GAPS.md"]}
                ],
                "false_refusals": [],
                "known_misses": [],
                "plant_validations": [],
                "unresolved": [],
                "precision_among_adjudicated": {"true": 1, "false": 0, "value": 1.0},
            },
            {
                "gate_id": "sample.adjudicated",
                "where": "sample:gate",
                "what_it_refuses": "sample refusal",
                "true_refusals": [
                    {
                        "what": "refused",
                        "when_utc": "2026-09-14T01:02:04Z",
                        "evidence": ["GATE_GAPS.md"],
                        "adjudicated_by": {"identity": "Integrator", "kind": "author"},
                    }
                ],
                "false_refusals": [],
                "known_misses": [],
                "plant_validations": [{"test": "plant", "evidence": ["tests/test_gate_scorecard.py"]}],
                "unresolved": [],
                "precision_among_adjudicated": {"true": 1, "false": 0, "value": 1.0},
            },
        ]
    }
    migrated, report = gate_scorecard.migrate_data_v1_to_v2(str(ROOT), data)
    entries = {entry["gate_id"]: entry for entry in migrated["gates"]}
    assert entries["sample.unadjudicated"]["events"][0]["adjudication"]["verdict"] == "UNRESOLVED"
    adjudicated_true = next(
        event for event in entries["sample.adjudicated"]["events"] if event["source_list"] == "true_refusals"
    )
    adjudicated_plant = next(
        event for event in entries["sample.adjudicated"]["events"] if event["source_list"] == "plant_validations"
    )
    assert adjudicated_true["adjudication"]["verdict"] == "TRUE_POSITIVE"
    assert adjudicated_true["adjudication"]["adjudicated_by"]["kind"] == "author"
    assert adjudicated_plant["adjudication"]["verdict"] == "TRUE_POSITIVE"
    assert report["lost_apparent_precision_gates"] == ["sample.unadjudicated"]


def test_stale_served_view_refuses():
    with _mini_root() as root:
        (root / gate_scorecard.SERVED_PATH).write_text("{}\n", encoding="utf-8", newline="\n")
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("gate_scorecard.json" in r and "stale" in r for r in reasons)


def test_served_view_and_index_name_unvalidated_not_green():
    from harness import index as index_mod

    phrase = gate_scorecard.UNVALIDATED_SENTENCE
    coverage = gate_scorecard.PRECISION_COVERAGE_SENTENCE
    served = gate_scorecard.served_view(ROOT)
    assert served["unvalidated_sentence"] == phrase
    assert served["summary"]["unvalidated_sentence"] == phrase
    assert coverage in served["precision_coverage_sentence"]
    html = index_mod.build_index(str(ROOT / "docs"))
    assert phrase in html
    assert "adjudicated precision TP/(TP+FP)" in html


def test_real_registry_passes():
    ok, reasons = gate_scorecard.check(ROOT)
    assert ok, "\n".join(reasons)
