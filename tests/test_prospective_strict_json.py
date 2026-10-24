"""Prospective records must not silently choose the last duplicate JSON member.

These are isolated synthetic parser regressions, NOT held-out validation or
independent clinical adjudication. They exercise actual repository loaders.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from harness import prospective


BATCH = "batch-a"


def _declaration(tmp_path: Path, raw: str) -> Path:
    path = tmp_path / "root" / "prospective" / BATCH / "declaration.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(raw, encoding="utf-8")
    return path


def _run(tmp_path: Path, raw: str) -> Path:
    path = tmp_path / "root" / "prospective" / BATCH / "runs" / "record.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(raw, encoding="utf-8")
    return path


def _defect(tmp_path: Path, raw: str) -> Path:
    path = tmp_path / "meta-harness-defects" / f"{BATCH}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(raw + "\n", encoding="utf-8")
    return path


@pytest.mark.parametrize(
    "raw,member",
    [
        ('{"batch_id":"batch-a","batch_id":"batch-b"}', "batch_id"),
        ('{"batch_id":"batch-a","invariants":{"census":1,"census":0}}', "census"),
    ],
)
def test_declaration_rejects_ambiguous_raw_members(
    tmp_path: Path, raw: str, member: str
) -> None:
    _declaration(tmp_path, raw)
    with pytest.raises(prospective.ProspectiveRefusal, match=f"duplicate prospective JSON member: '{member}'"):
        prospective.load_declaration(tmp_path / "root", BATCH)


@pytest.mark.parametrize(
    "raw,member",
    [
        ('{"batch_id":"batch-a","outcome":"FAILED_CRASH","outcome":"COMPLETED"}', "outcome"),
        ('{"batch_id":"batch-a","evidence":{"source":"one","source":"two"}}', "source"),
    ],
)
def test_run_records_reject_ambiguous_raw_members(
    tmp_path: Path, raw: str, member: str
) -> None:
    _run(tmp_path, raw)
    with pytest.raises(prospective.ProspectiveRefusal, match=f"duplicate prospective JSON member: '{member}'"):
        prospective.load_run_records(tmp_path / "root", BATCH)


@pytest.mark.parametrize(
    "raw,member",
    [
        ('{"batch_id":"batch-a","batch_id":"batch-b"}', "batch_id"),
        ('{"batch_id":"batch-a","attribution":"network outage","attribution":"surprising result"}', "attribution"),
    ],
)
def test_defect_ledger_rejects_ambiguous_raw_members(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, raw: str, member: str
) -> None:
    monkeypatch.delenv(prospective.DEFECT_ENV, raising=False)
    _defect(tmp_path, raw)
    with pytest.raises(prospective.ProspectiveRefusal, match=f"defect ledger line 1: duplicate prospective JSON member: '{member}'"):
        prospective.load_defects(tmp_path / "root", BATCH)


def test_unambiguous_declaration_still_loads(tmp_path: Path) -> None:
    _declaration(tmp_path, '{"batch_id":"batch-a","invariants":{"census":1}}')
    assert prospective.load_declaration(tmp_path / "root", BATCH)["invariants"] == {"census": 1}


def test_unambiguous_run_still_loads(tmp_path: Path) -> None:
    _run(tmp_path, '{"batch_id":"batch-a","outcome":"FAILED_CRASH"}')
    assert prospective.load_run_records(tmp_path / "root", BATCH)[0]["outcome"] == "FAILED_CRASH"


def test_unambiguous_defect_still_loads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(prospective.DEFECT_ENV, raising=False)
    _defect(tmp_path, '{"batch_id":"batch-a","attribution":"runner killed"}')
    assert prospective.load_defects(tmp_path / "root", BATCH)[0]["attribution"] == "runner killed"
