"""Fail-closed tests for preseeded records in a prospective topic run.

All records below are routing-only fixtures. These tests do NOT exercise
network discovery, clinical synthesis, raw API archiving or external review.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness import prospective
from scripts import run_prospective_topic as runner


@pytest.mark.parametrize(
    "relative_path",
    [
        "records.json",
        "cache/topic-fixture/records.json",
    ],
)
def test_prospective_loader_refuses_preseeded_records_without_fetch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, relative_path: str
) -> None:
    out_dir = tmp_path / "package"
    candidate = out_dir / relative_path
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_text('{"synthetic_fixture_only": true}\n', encoding="utf-8")

    def fail_if_called(*_args: object, **_kwargs: object) -> str:
        pytest.fail("acquisition.refresh must not run after seeded-cache refusal")

    monkeypatch.setattr(runner.acquisition, "refresh", fail_if_called)
    with pytest.raises(prospective.ProspectiveRefusal, match="pre-existing cached records"):
        runner._load_or_refresh({"slug": "topic-fixture"}, out_dir, "2026-10-24")


def test_prospective_loader_refuses_dangling_cache_symlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out_dir = tmp_path / "package"
    out_dir.mkdir()
    (out_dir / "records.json").symlink_to(tmp_path / "missing-records.json")

    monkeypatch.setattr(
        runner.acquisition,
        "refresh",
        lambda *_args, **_kwargs: pytest.fail("must refuse dangling cache link"),
    )
    with pytest.raises(prospective.ProspectiveRefusal, match="pre-existing cached records"):
        runner._load_or_refresh({"slug": "topic-fixture"}, out_dir, "2026-10-24")


def test_prospective_loader_calls_refresh_when_no_seeded_records(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out_dir = tmp_path / "package"
    out_dir.mkdir()
    calls: list[tuple[dict[str, str], str, str]] = []

    def synthetic_refresh(config: dict[str, str], day: str, *, root: str) -> str:
        calls.append((config, day, root))
        snapshot = Path(root) / "fresh-snapshot"
        snapshot.mkdir()
        (snapshot / "records.json").write_text(
            json.dumps({"synthetic_fixture_only": True}) + "\n", encoding="utf-8"
        )
        return str(snapshot)

    monkeypatch.setattr(runner.acquisition, "refresh", synthetic_refresh)
    records, snapshot, from_cache = runner._load_or_refresh(
        {"slug": "topic-fixture"}, out_dir, "2026-10-24"
    )

    assert calls == [
        ({"slug": "topic-fixture"}, "2026-10-24", str(out_dir))
    ]
    assert records == {"synthetic_fixture_only": True}
    assert snapshot == (out_dir / "fresh-snapshot").resolve()
    assert from_cache is False
