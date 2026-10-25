"""Offline A4 regression: producer retains actual raw-response files in its run census.

All payloads in this module are deliberately synthetic; this does not exercise
live study discovery, independent adjudication or any external model provider.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from harness import prospective
from scripts import run_prospective_topic as runner


SPEC = Path(__file__).resolve().parents[1] / "docs" / "PROSPECTIVE_VALIDATION_SPEC.md"


def _mini_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "PROSPECTIVE_VALIDATION_SPEC.md").write_text(
        SPEC.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (root / "requirements.txt").write_text("", encoding="utf-8")
    declaration = prospective.batch_declaration(
        root,
        "batch-raw",
        60,
        ["census"],
        "a" * 64,
        {"definition": "synthetic offline topic universe", "digest": "b" * 64},
        declared_utc="2026-09-14T00:00:00Z",
    )
    prospective.write_declaration(root, declaration)
    return root


@pytest.mark.parametrize(
    "removed",
    ["cache/topic/raw/response-1.bin", "cache/topic/raw/empty-body.bin",
     "cache/topic/raw/INDEX.json", "cache/topic/records.json"],
)
def test_prospective_run_inventory_refuses_missing_raw_response_after_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, removed: str
) -> None:
    """An after-run deletion must not disappear silently from A4's census."""
    root = _mini_root(tmp_path)
    monkeypatch.setattr(runner, "ROOT", root)
    config_path = tmp_path / "topic.json"
    config_path.write_text(
        json.dumps({"slug": "topic", "topic_identifier": "synthetic-topic"}),
        encoding="utf-8",
    )
    output_dir = root / "prospective" / "batch-raw" / "runs" / "run-slot"

    def synthetic_refresh(config: dict, now_day: str, *, root: str) -> str:
        snapshot = Path(root) / "cache" / config["slug"]
        raw = snapshot / "raw"
        raw.mkdir(parents=True)
        bodies = [("response-1.bin", b"synthetic API response"),
                  ("empty-body.bin", b"")]
        entries = []
        for name, payload in bodies:
            (raw / name).write_bytes(payload)
            entries.append({
                "path": f"raw/{name}",
                "file_sha256": hashlib.sha256(payload).hexdigest(),
            })
        raw_index = runner._write_json(raw / "INDEX.json", entries)
        runner._write_json(
            snapshot / runner.acquisition.LEDGER_FILENAME,
            {"snapshot": {
                "mode": "REFRESH",
                "raw_calls": len(entries),
                "raw_index_sha256": hashlib.sha256(raw_index.read_bytes()).hexdigest(),
            }},
        )
        runner._write_json(snapshot / "records.json", {"synthetic": True})
        return str(snapshot)

    def synthetic_review(config, records, out_dir, now_utc, from_cache, ledger):
        return [runner._write_json(
            out_dir / "review" / "manifest.json", {"synthetic": True}
        )]

    monkeypatch.setattr(runner.acquisition, "refresh", synthetic_refresh)
    monkeypatch.setattr(runner, "_package_review", synthetic_review)
    monkeypatch.setattr(runner, "_invariant_failures", lambda *args: [])
    result = runner.run_topic("batch-raw", str(config_path), str(output_dir))
    assert result["outcome"] == "COMPLETED"

    record = json.loads((output_dir / "run_record.json").read_text(encoding="utf-8"))
    assert "cache/topic/raw/response-1.bin" in record["artefact_paths"]
    assert "cache/topic/raw/empty-body.bin" in record["artefact_paths"]
    assert "cache/topic/raw/INDEX.json" in record["artefact_paths"]
    assert "cache/topic/records.json" in record["artefact_paths"]
    assert f"cache/topic/{runner.acquisition.LEDGER_FILENAME}" in record["artefact_paths"]
    assert prospective.check_batch(root, "batch-raw")["ok"] is True

    (output_dir / removed).unlink()
    with pytest.raises(
        prospective.ProspectiveRefusal, match="retained artefact is missing"
    ):
        prospective.check_batch(root, "batch-raw")
