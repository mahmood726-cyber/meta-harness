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


@pytest.mark.parametrize("target_exists", [False, True])
def test_a4_symlinked_run_record_cannot_pass_retained_archive_census(
    tmp_path: Path, target_exists: bool
) -> None:
    """External or dangling links are neither safe evidence nor silent skips."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(root, batch, _record(root, batch, "run-valid"))
    external = tmp_path / "externally-mutable-run.json"
    if target_exists:
        prospective.write_run_record(
            external, _record(root, batch, "run-external")
        )
    linked = root / "prospective" / batch / "runs" / "linked.json"
    linked.symlink_to(external)
    with pytest.raises(
        prospective.ProspectiveRefusal,
        match="prospective run record is a symlink",
    ):
        prospective.check_batch(root, batch)


def test_a4_symlinked_prospective_parent_cannot_import_external_archive(
    tmp_path: Path,
) -> None:
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    external = tmp_path / "external-archive"
    prospective.write_run_record(
        external / batch / "runs" / "run-valid",
        _record(root, batch, "run-valid"),
    )
    (root / "prospective").symlink_to(external, target_is_directory=True)
    with pytest.raises(
        prospective.ProspectiveRefusal,
        match="prospective batch archive escapes the repository",
    ):
        prospective.load_run_records(root, batch)


def test_a4_regular_archived_nested_and_flat_run_records_remain_valid(
    tmp_path: Path,
) -> None:
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(root, batch, _record(root, batch, "run-nested"))
    prospective.write_run_record(
        root / "prospective" / batch / "runs" / "run-flat.json",
        _record(root, batch, "run-flat"),
    )
    records = prospective.load_run_records(root, batch)
    assert {record["run_id"] for record in records} == {"run-nested", "run-flat"}
    assert prospective.check_batch(root, batch)["ok"] is True


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


@pytest.mark.parametrize(
    ("field", "forged_value", "error"),
    [
        ("architecture_components", {}, "declared architecture components differ"),
        ("mutable_dependencies", [], "declared mutable dependencies differ"),
        ("external_dependency_mutability", False, "declared external dependency mutability differs"),
        ("freeze_claim", prospective.IMMUTABLE_FREEZE_CLAIM, "declared freeze claim contradicts"),
        ("rerun_policy", "No limits on reruns", "declared rerun policy differs"),
    ],
)
def test_declaration_refuses_metadata_forgery_even_with_unchanged_identity(
    tmp_path: Path, field: str, forged_value: object, error: str
) -> None:
    root = _mini_root(tmp_path)
    decl = _declare(root)
    original_identity = decl["architecture_identity"]
    assert prospective.check_declaration_frozen(root, decl) == decl

    forged = dict(decl)
    forged[field] = forged_value
    assert forged["architecture_identity"] == original_identity
    with pytest.raises(prospective.ProspectiveRefusal, match=error):
        prospective.check_declaration_frozen(root, forged)


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


@pytest.mark.parametrize("other_topic", ["topic-plant", "topic-other"])
def test_a4_repeated_run_id_in_distinct_archived_records_is_refused(
    tmp_path: Path, other_topic: str
) -> None:
    """Distinct retained packages cannot both claim the same run identity."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    first = _record(root, batch, "run-shared")
    second = _record(root, batch, "run-shared", topic=other_topic)
    base = root / "prospective" / batch / "runs"
    prospective.write_run_record(base / "package-first", first)
    prospective.write_run_record(base / "package-second", second)

    assert len(prospective.load_run_records(root, batch)) == 2
    with pytest.raises(
        prospective.ProspectiveRefusal, match="duplicate run_id in retained batch records"
    ) as exc_info:
        prospective.check_batch(root, batch)
    assert "run-shared" in str(exc_info.value)


@pytest.mark.parametrize("corrupt_id", [None, "", 7, True, ".", "..", "../run-escape", []])
def test_a4_run_identity_absent_or_invalid_refuses_batch(
    tmp_path: Path, corrupt_id: object
) -> None:
    """A4 must not accept a run that cannot be uniquely and safely cited."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    record = _record(root, batch, "run-valid")
    record["run_id"] = corrupt_id
    prospective.write_run_record(
        root / "prospective" / batch / "runs" / "package-corrupt", record
    )
    with pytest.raises(
        prospective.ProspectiveRefusal, match="missing or invalid run_id"
    ):
        prospective.check_batch(root, batch)


@pytest.mark.parametrize("precreate_runs_dir", [False, True])
def test_a4_empty_retained_run_census_refuses_success(
    tmp_path: Path, precreate_runs_dir: bool
) -> None:
    """A valid freeze declaration without executed runs cannot pass A4."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    if precreate_runs_dir:
        (root / "prospective" / batch / "runs").mkdir(parents=True)
    assert prospective.load_run_records(root, batch) == []
    with pytest.raises(
        prospective.ProspectiveRefusal,
        match="no retained prospective run records",
    ):
        prospective.check_batch(root, batch)


def test_a4_one_retained_completed_run_remains_eligible_for_structural_check(
    tmp_path: Path,
) -> None:
    """The empty-census refusal does not reject nonempty valid run evidence."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(root, batch, _record(root, batch, "run-one"))
    result = prospective.check_batch(root, batch)
    assert result["run_records"] == 1
    assert result["ok"] is True


def test_a4_distinct_valid_run_ids_keep_successful_census(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(root, batch, _record(root, batch, "run-one"))
    _write_batch_record(root, batch, _record(root, batch, "run-two"))
    summary = prospective.check_batch(root, batch)
    assert summary["ok"] is True
    assert summary["run_records"] == 2


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



@pytest.mark.parametrize("finished", [
    "2026-09-14T00:10:59.999Z",
    "2026-09-14T00:11:00Z",
])
def test_a4_completed_run_at_or_below_registered_time_limit_passes(
    tmp_path: Path, finished: str
) -> None:
    """The preregistered ceiling is inclusive; do not refuse a valid run."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(
        root, batch, _record(root, batch, "run-on-time", finished=finished)
    )
    assert prospective.check_batch(root, batch)["ok"] is True


@pytest.mark.parametrize("finished", [
    "2026-09-14T00:11:00.001Z",
    "2026-09-14T00:12:00Z",
])
def test_a4_completed_run_exceeding_registered_time_limit_refuses(
    tmp_path: Path, finished: str
) -> None:
    """A4: changing an over-time run's label to COMPLETED must not pass."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(
        root, batch, _record(root, batch, "run-over-time", finished=finished)
    )
    with pytest.raises(prospective.ProspectiveRefusal) as exc_info:
        prospective.check_batch(root, batch)
    text = str(exc_info.value)
    assert "run-over-time" in text
    assert "exceeds preregistered time_limit_s 60s" in text
    assert "FAILED_TIMEOUT" in text


@pytest.mark.parametrize(("field", "value"), [
    ("started_utc", None),
    ("finished_utc", None),
    ("started_utc", ""),
    ("finished_utc", ""),
    ("started_utc", "OMIT"),
    ("finished_utc", "OMIT"),
])
def test_a4_missing_clock_cannot_bypass_registered_time_limit(
    tmp_path: Path, field: str, value: str | None
) -> None:
    """A null, blank or omitted clock cannot be treated as a timely run."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    record = _record(root, batch, "run-clock-corrupted")
    if value == "OMIT":
        record.pop(field)
    else:
        record[field] = value
    _write_batch_record(root, batch, record)
    with pytest.raises(
        prospective.ProspectiveRefusal,
        match="missing or invalid timestamps prevent time-limit verification"
    ):
        prospective.check_batch(root, batch)


@pytest.mark.parametrize("corrupt_limit", [
    0, -1, None, "60", True, float("nan"), float("inf"), float("-inf")
])
def test_a4_batch_checker_refuses_invalid_declared_time_limit(
    tmp_path: Path, corrupt_limit: object
) -> None:
    """A4 requires an actual finite, positive predeclared number."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    decl = _declare(root, batch)
    decl["time_limit_s"] = corrupt_limit
    prospective.write_declaration(root, decl)
    _write_batch_record(
        root, batch, _record(root, batch, "run-on-time")
    )
    with pytest.raises(
        prospective.ProspectiveRefusal, match="finite positive numeric time_limit_s"
    ):
        prospective.check_batch(root, batch)


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


@pytest.mark.parametrize("tampered_batch", ["batch-other", None, "OMITTED"])
def test_check_batch_refuses_silent_exclusion_of_failed_run(
    tmp_path: Path, tampered_batch: str | None
) -> None:
    """A4: an archived failed run must never vanish from batch accounting."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(root, batch, _record(root, batch, "run-valid"))
    failed = _record(root, batch, "run-failed")
    failed["outcome"] = "FAILED_CRASH"
    _write_batch_record(root, batch, failed)

    # Positive census control: the failed run remains independently discoverable.
    assert len(prospective.load_run_records(root, batch)) == 2
    # A4: structural integrity cannot promote a batch with a failed run to PASS.
    with pytest.raises(prospective.ProspectiveRefusal, match="failed prospective runs"):
        prospective.check_batch(root, batch)

    corrupted = dict(failed)
    if tampered_batch == "OMITTED":
        del corrupted["batch_id"]
    else:
        corrupted["batch_id"] = tampered_batch
    _write_batch_record(root, batch, corrupted)

    # Before the fix, the loader silently dropped this failed record,
    # and check_batch incorrectly returned ok=True with one run.
    with pytest.raises(
        prospective.ProspectiveRefusal, match="run record batch_id mismatch"
    ):
        prospective.check_batch(root, batch)


@pytest.mark.parametrize("invalid_document", [[], None, "not a record"])
def test_check_batch_refuses_non_object_run_record(
    tmp_path: Path, invalid_document: object
) -> None:
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    prospective.write_run_record(
        root / "prospective" / batch / "runs" / "run-corrupted.json",
        invalid_document,
    )
    with pytest.raises(
        prospective.ProspectiveRefusal, match="run record must be a JSON object"
    ):
        prospective.check_batch(root, batch)


@pytest.mark.parametrize("failure", ["FAILED_CRASH", "FAILED_TIMEOUT", "FAILED_INVARIANT"])
def test_a4_failed_run_cannot_yield_successful_batch(
    tmp_path: Path, failure: str
) -> None:
    """A4: every failed run counts against batch success, even with a completed peer."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(root, batch, _record(root, batch, "run-completed"))
    # Baseline positive control: a completed-only structurally valid batch passes.
    assert prospective.check_batch(root, batch)["ok"] is True

    failed = _record(root, batch, "run-failed")
    failed["outcome"] = failure
    _write_batch_record(root, batch, failed)
    archived = prospective.load_run_records(root, batch)
    assert len(archived) == 2
    assert any(record["outcome"] == failure for record in archived)

    with pytest.raises(prospective.ProspectiveRefusal) as exc_info:
        prospective.check_batch(root, batch)
    message = str(exc_info.value)
    assert "batch contains failed prospective runs (1 of 2 retained)" in message
    assert "run-failed" in message
    assert failure in message


def test_a4_successful_rerun_does_not_erase_failed_original(tmp_path: Path) -> None:
    """A permitted rerun is a second record, not a successful replacement."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    original = _record(root, batch, "run-original")
    original["outcome"] = "FAILED_CRASH"
    _write_batch_record(root, batch, original)

    entry = prospective.defect_entry(
        batch, "topic-plant", "run-original", "FAILED_CRASH",
        "runner killed", "plant defect", entry_id="defect-plant",
        declared_utc="2026-09-14T00:19:00Z",
    )
    prospective.append_defect(
        entry, root.parent / "meta-harness-defects" / f"{batch}.jsonl", root=root
    )
    rerun = _record(
        root, batch, "run-rerun",
        started="2026-09-14T00:20:00Z",
        finished="2026-09-14T00:21:00Z",
        rerun_of="run-original",
        justification="rerun because defect-plant documents external failure",
    )
    _write_batch_record(root, batch, rerun)
    assert len(prospective.load_run_records(root, batch)) == 2

    with pytest.raises(
        prospective.ProspectiveRefusal, match="batch contains failed prospective runs"
    ) as exc_info:
        prospective.check_batch(root, batch)
    assert "run-original" in str(exc_info.value)
    assert "FAILED_CRASH" in str(exc_info.value)
