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
        if isinstance(raw, str):
            out.add(raw)
        elif isinstance(raw, list):
            out.update(x for x in raw if isinstance(x, str))

    for entry in data["gates"]:
        for key in gate_scorecard.EVENT_LISTS:
            for event in entry.get(key) or []:
                add(event.get("evidence"))
    prior = data.get("prior_precision_measurement")
    if isinstance(prior, dict):
        add(prior.get("evidence"))
    return out


@contextmanager
def _mini_root():
    with tempfile.TemporaryDirectory(prefix="gate-scorecard-test-", ignore_cleanup_errors=True) as raw:
        tmp = Path(raw)
        _populate_mini_root(tmp)
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
    for rel in [p for p in _evidence_paths(data) if not p.startswith("commit:")]:
        _copy_file(ROOT, tmp, rel)
    for entry in data["gates"]:
        for key in gate_scorecard.EVENT_LISTS:
            for event in entry.get(key) or []:
                evidence = event.get("evidence")
                if not isinstance(evidence, list) or not any(str(x).startswith("commit:") for x in evidence):
                    continue
                rel = f"docs/evidence/test-commit-{entry['gate_id'].replace('.', '-')}.txt"
                p = tmp / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(str(event.get("when_utc") or "commit evidence") + "\n", encoding="utf-8", newline="\n")
                event["evidence"] = [rel if str(x).startswith("commit:") else x for x in evidence]
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


def test_gate_in_code_with_no_entry_refuses():
    with _mini_root() as root:
        data = _load(root)
        data["gates"] = data["gates"][1:]
        _write(root, data)
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("missing entry for enumerated gate" in r for r in reasons)


def test_dangling_evidence_path_refuses():
    with _mini_root() as root:
        data = _load(root)
        event = next(e for g in data["gates"] for e in g["true_refusals"] if e.get("evidence"))
        event["evidence"] = ["docs/evidence/no-such-capture.txt"]
        _write(root, data)
        gate_scorecard.write_served_view(root)
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("cited evidence does not exist" in r for r in reasons)


def test_precision_without_both_counts_refuses():
    with _mini_root() as root:
        data = _load(root)
        data["gates"][0]["precision_among_adjudicated"].pop("true", None)
        _write(root, data)
        gate_scorecard.write_served_view(root)
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("precision stated without both true and false counts" in r for r in reasons)


def test_placeholder_timestamp_refuses():
    with _mini_root() as root:
        data = _load(root)
        event = next(e for g in data["gates"] for e in g["true_refusals"] if e.get("evidence"))
        event["when_utc"] = "2026-09-14T00:00:00Z"
        _write(root, data)
        gate_scorecard.write_served_view(root)
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("placeholder timestamp" in r for r in reasons)


def test_test_file_cannot_be_true_production_refusal():
    with _mini_root() as root:
        data = _load(root)
        event = next(e for g in data["gates"] for e in g["true_refusals"] if e.get("evidence"))
        event["evidence"] = ["tests/test_gate.py"]
        _write(root, data)
        gate_scorecard.write_served_view(root)
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("cannot be counted as a true production refusal" in r for r in reasons)


def test_stale_served_view_refuses():
    with _mini_root() as root:
        (root / gate_scorecard.SERVED_PATH).write_text("{}\n", encoding="utf-8", newline="\n")
        ok, reasons = gate_scorecard.check(root)
        assert not ok
        assert any("gate_scorecard.json" in r and "stale" in r for r in reasons)


def test_served_view_and_index_name_unvalidated_not_green():
    from harness import index as index_mod

    phrase = gate_scorecard.UNVALIDATED_SENTENCE
    served = gate_scorecard.served_view(ROOT)
    assert served["unvalidated_sentence"] == phrase
    assert served["summary"]["unvalidated_sentence"] == phrase
    assert phrase in index_mod.build_index(str(ROOT / "docs"))


def test_real_registry_passes():
    ok, reasons = gate_scorecard.check(ROOT)
    assert ok, "\n".join(reasons)
