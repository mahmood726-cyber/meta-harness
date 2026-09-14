from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness import architecture_identity
from harness import prospective


ROOT = Path(__file__).resolve().parents[1]
COMMITMENT = "a" * 64


def _write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _mini_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    spec = (ROOT / "docs" / "PROSPECTIVE_VALIDATION_SPEC.md").read_text(
        encoding="utf-8"
    )
    _write(root, "docs/PROSPECTIVE_VALIDATION_SPEC.md", spec)
    _write(root, "requirements.txt", "")
    return root


def _declare(root: Path, batch_id: str = "batch-plant") -> dict:
    decl = prospective.batch_declaration(
        root,
        batch_id,
        60,
        ["census", "gate"],
        COMMITMENT,
        {"definition": "plant universe", "version": "v1", "digest": "b" * 64},
        declared_utc="2026-09-14T00:00:00Z",
    )
    prospective.write_declaration(root, decl)
    return decl


def _record(
    root: Path,
    batch_id: str,
    run_id: str,
    topic: str = "topic-plant",
    started: str = "2026-09-14T00:10:00Z",
    finished: str = "2026-09-14T00:11:00Z",
    rerun_of: str | None = None,
    justification: str | None = None,
) -> dict:
    return prospective.run_record(
        root,
        batch_id,
        topic,
        started,
        finished,
        "COMPLETED",
        ["review/index.html", "review/manifest.json"],
        run_id=run_id,
        rerun_of=rerun_of,
        rerun_justification=justification,
    )


def _write_batch_record(root: Path, batch_id: str, record: dict) -> Path:
    return prospective.write_run_record(
        root / "prospective" / batch_id / "runs" / record["run_id"],
        record,
    )


def test_declaration_copies_a4_policy_and_freezes_architecture_identity(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    decl = _declare(root)

    assert decl["rerun_policy"] == prospective.rerun_policy_text(root)
    assert decl["time_limit_s"] == 60
    assert decl["invariants"] == ["census", "gate"]
    assert decl["external_dependency_mutability"] is True
    assert decl["freeze_claim"] == prospective.MUTABLE_FREEZE_CLAIM
    assert prospective.check_declaration_frozen(root, decl) == decl

    _write(root, "harness/plant.py", "PLANT = True\n")
    with pytest.raises(prospective.ProspectiveRefusal, match="architecture identity mismatch"):
        prospective.check_declaration_frozen(root, decl)


def test_append_defect_outside_tree_leaves_architecture_identity_unchanged(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    before = architecture_identity.identity(root)
    entry = prospective.defect_entry(
        "batch-plant",
        "topic-plant",
        "run-original",
        "FAILED_CRASH",
        "runner killed",
        "plant defect",
        entry_id="defect-plant",
        declared_utc="2026-09-14T00:12:00Z",
    )

    path = prospective.append_defect(
        entry,
        root.parent / "meta-harness-defects" / "batch-plant.jsonl",
        root=root,
    )

    assert path.exists()
    assert architecture_identity.identity(root) == before


def test_append_defect_refuses_ledger_inside_repository_tree(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    entry = prospective.defect_entry(
        "batch-plant",
        "topic-plant",
        "run-original",
        "FAILED_CRASH",
        "runner killed",
        "plant defect",
        entry_id="defect-plant",
        declared_utc="2026-09-14T00:12:00Z",
    )

    with pytest.raises(prospective.ProspectiveRefusal, match="inside the repository tree"):
        prospective.append_defect(
            entry,
            root / "prospective" / "batch-plant.jsonl",
            root=root,
        )


def test_check_batch_refuses_two_identities_in_one_batch(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    original = _record(root, batch, "run-original")
    changed = dict(_record(root, batch, "run-changed"))
    changed["architecture_identity"] = "0" * 64
    _write_batch_record(root, batch, original)
    _write_batch_record(root, batch, changed)

    with pytest.raises(prospective.ProspectiveRefusal, match="two architecture identities"):
        prospective.check_batch(root, batch)


def test_check_batch_refuses_rerun_without_prior_defect_entry(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(root, batch, _record(root, batch, "run-original"))
    rerun = _record(
        root,
        batch,
        "run-rerun",
        rerun_of="run-original",
        justification="rerun because defect-plant documents external failure",
    )
    _write_batch_record(root, batch, rerun)

    with pytest.raises(prospective.ProspectiveRefusal, match="prior defect-ledger entry"):
        prospective.check_batch(root, batch)


def test_check_batch_refuses_rerun_when_cited_defect_is_late(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(root, batch, _record(root, batch, "run-original"))
    rerun = _record(
        root,
        batch,
        "run-rerun",
        started="2026-09-14T00:20:00Z",
        finished="2026-09-14T00:21:00Z",
        rerun_of="run-original",
        justification="rerun because defect-plant documents external failure",
    )
    _write_batch_record(root, batch, rerun)
    entry = prospective.defect_entry(
        batch,
        "topic-plant",
        "run-original",
        "FAILED_CRASH",
        "runner killed",
        "plant defect",
        entry_id="defect-plant",
        declared_utc="2026-09-14T00:22:00Z",
    )
    prospective.append_defect(
        entry,
        root.parent / "meta-harness-defects" / f"{batch}.jsonl",
        root=root,
    )

    with pytest.raises(prospective.ProspectiveRefusal, match="not declared before rerun start"):
        prospective.check_batch(root, batch)


def test_check_batch_refuses_more_than_one_rerun_per_topic(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(root, batch, _record(root, batch, "run-original"))
    for idx, minute in enumerate((20, 30), start=1):
        defect_id = f"defect-plant-{idx}"
        entry = prospective.defect_entry(
            batch,
            "topic-plant",
            "run-original",
            "FAILED_CRASH",
            "runner killed",
            "plant defect",
            entry_id=defect_id,
            declared_utc=f"2026-09-14T00:{minute - 1}:00Z",
        )
        prospective.append_defect(
            entry,
            root.parent / "meta-harness-defects" / f"{batch}.jsonl",
            root=root,
        )
        rerun = _record(
            root,
            batch,
            f"run-rerun-{idx}",
            started=f"2026-09-14T00:{minute}:00Z",
            finished=f"2026-09-14T00:{minute + 1}:00Z",
            rerun_of="run-original",
            justification=f"rerun because {defect_id} documents external failure",
        )
        _write_batch_record(root, batch, rerun)

    with pytest.raises(prospective.ProspectiveRefusal, match="more than one rerun"):
        prospective.check_batch(root, batch)


def test_check_batch_refuses_rerun_missing_original(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    entry = prospective.defect_entry(
        batch,
        "topic-plant",
        "run-missing",
        "FAILED_CRASH",
        "runner killed",
        "plant defect",
        entry_id="defect-plant",
        declared_utc="2026-09-14T00:19:00Z",
    )
    prospective.append_defect(
        entry,
        root.parent / "meta-harness-defects" / f"{batch}.jsonl",
        root=root,
    )
    rerun = _record(
        root,
        batch,
        "run-rerun",
        started="2026-09-14T00:20:00Z",
        finished="2026-09-14T00:21:00Z",
        rerun_of="run-missing",
        justification="rerun because defect-plant documents external failure",
    )
    _write_batch_record(root, batch, rerun)

    with pytest.raises(prospective.ProspectiveRefusal, match="missing original"):
        prospective.check_batch(root, batch)


def test_check_batch_accepts_one_rerun_with_prior_defect(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(root, batch, _record(root, batch, "run-original"))
    entry = prospective.defect_entry(
        batch,
        "topic-plant",
        "run-original",
        "FAILED_CRASH",
        "runner killed",
        "plant defect",
        entry_id="defect-plant",
        declared_utc="2026-09-14T00:19:00Z",
    )
    prospective.append_defect(
        entry,
        root.parent / "meta-harness-defects" / f"{batch}.jsonl",
        root=root,
    )
    _write_batch_record(
        root,
        batch,
        _record(
            root,
            batch,
            "run-rerun",
            started="2026-09-14T00:20:00Z",
            finished="2026-09-14T00:21:00Z",
            rerun_of="run-original",
            justification="rerun because defect-plant documents external failure",
        ),
    )

    summary = prospective.check_batch(root, batch)

    assert summary["ok"] is True
    assert summary["run_records"] == 2
    assert summary["defect_entries"] == 1
    assert summary["external_dependency_mutability"] is True
    assert summary["freeze_claim"] == prospective.MUTABLE_FREEZE_CLAIM


def test_freeze_claim_tracks_mutability_both_ways(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _mini_root(tmp_path)

    monkeypatch.setattr(
        prospective.architecture_identity,
        "mutable_dependencies",
        lambda _root: ["model_stages.plant: unpinned"],
    )
    assert prospective.external_dependency_mutability(root) is True
    assert prospective.freeze_claim(root) == prospective.MUTABLE_FREEZE_CLAIM

    monkeypatch.setattr(prospective.architecture_identity, "mutable_dependencies", lambda _root: [])
    monkeypatch.setattr(
        prospective.architecture_identity,
        "components",
        lambda _root: {"model_stages": {"stages": [{"snapshot_pinning": {"pinned": True}}]}},
    )
    monkeypatch.setattr(prospective.architecture_identity, "identity", lambda _root: "c" * 64)
    monkeypatch.setattr(prospective.architecture_identity, "identity_from_components", lambda _components: "d" * 64)

    assert prospective.external_dependency_mutability(root) is False
    assert prospective.freeze_claim(root) == prospective.IMMUTABLE_FREEZE_CLAIM

    decl = prospective.batch_declaration(
        root,
        "batch-frozen",
        60,
        ["census"],
        COMMITMENT,
        {"definition": "plant universe", "version": "v1", "digest": "b" * 64},
        declared_utc="2026-09-14T00:00:00Z",
    )
    record = prospective.run_record(
        root,
        "batch-frozen",
        "topic-plant",
        "2026-09-14T00:10:00Z",
        "2026-09-14T00:11:00Z",
        "COMPLETED",
        ["review/index.html"],
    )

    assert decl["external_dependency_mutability"] is False
    assert decl["freeze_claim"] == prospective.IMMUTABLE_FREEZE_CLAIM
    assert record["external_dependency_mutability"] is False
    assert record["freeze_claim"] == prospective.IMMUTABLE_FREEZE_CLAIM


def test_run_record_refuses_unknown_outcome(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)

    with pytest.raises(prospective.ProspectiveRefusal, match="unknown run outcome"):
        prospective.run_record(
            root,
            "batch-plant",
            "topic-plant",
            "2026-09-14T00:00:00Z",
            "2026-09-14T00:01:00Z",
            "FAILED_SECRETLY",
            [],
        )


def test_prospective_module_has_no_release_timing_state_and_run_record_fields_are_closed(tmp_path: Path) -> None:
    source = (ROOT / "harness" / "prospective.py").read_text(encoding="utf-8").lower()
    for forbidden in ("sleep", "poll", "interval"):
        assert forbidden not in source

    record = _record(_mini_root(tmp_path), "batch-plant", "run-original")
    forbidden_fields = {
        "release_cadence",
        "release_gap",
        "next_release",
        "previous_release",
        "next_expected",
    }
    assert forbidden_fields.isdisjoint(record)


def test_a5_spec_names_inventory_derived_mutable_model_stages() -> None:
    spec = (ROOT / "docs" / "PROSPECTIVE_VALIDATION_SPEC.md").read_text(encoding="utf-8")
    inventory = json.loads((ROOT / "docs" / "model_stage_inventory.json").read_text(encoding="utf-8"))
    stages = inventory["stages"]
    mutable_names = [
        stage["name"]
        for stage in stages
        if not (stage.get("snapshot_pinning") or {}).get("pinned")
    ]

    assert len(stages) == 11
    assert len(mutable_names) == 11
    assert "external_dependency_mutability: true" in spec
    assert "frozen local architecture with mutable external model dependency" in spec
    assert "11 of 11 model-driven stages" in spec
    for name in mutable_names:
        assert f"`{name}`" in spec
