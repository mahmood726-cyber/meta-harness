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



def test_misfiled_declaration_cannot_validate_as_a_different_batch(tmp_path: Path) -> None:
    # Synthetic cross-batch substitution: previously check_batch could PASS
    # using the wrong declaration and reporting zero runs.
    root = _mini_root(tmp_path)
    _declare(root, "batch-source")
    source = prospective.declaration_path(root, "batch-source")
    misplaced = prospective.declaration_path(root, "batch-target")
    misplaced.parent.mkdir(parents=True)
    misplaced.write_bytes(source.read_bytes())

    with pytest.raises(prospective.ProspectiveRefusal, match="declaration batch_id does not match"):
        prospective.load_declaration(root, "batch-target")
    with pytest.raises(prospective.ProspectiveRefusal, match="declaration batch_id does not match"):
        prospective.check_batch(root, "batch-target")


def test_misfiled_run_record_cannot_disappear_from_batch_denominator(tmp_path: Path) -> None:
    # A foreign batch_id in this batch directory was previously filtered out,
    # allowing an apparently clean batch with an understated run count.
    root = _mini_root(tmp_path)
    _declare(root, "batch-plant")
    foreign = _record(root, "batch-foreign", "run-foreign")
    _write_batch_record(root, "batch-plant", foreign)

    with pytest.raises(prospective.ProspectiveRefusal, match="run record batch_id does not match"):
        prospective.load_run_records(root, "batch-plant")
    with pytest.raises(prospective.ProspectiveRefusal, match="run record batch_id does not match"):
        prospective.check_batch(root, "batch-plant")



@pytest.mark.parametrize("precreate_runs_dir", [False, True])
def test_a4_empty_retained_run_census_refuses_success(
    tmp_path: Path, precreate_runs_dir: bool
) -> None:
    """An intact freeze declaration is not evidence that a topic was executed."""
    root = _mini_root(tmp_path)
    _declare(root)
    if precreate_runs_dir:
        (root / "prospective" / "batch-plant" / "runs").mkdir(parents=True)
    assert prospective.load_run_records(root, "batch-plant") == []

    with pytest.raises(
        prospective.ProspectiveRefusal, match="no retained prospective run records"
    ):
        prospective.check_batch(root, "batch-plant")


def test_pre_registration_run_cannot_pass_as_prospective(tmp_path: Path) -> None:
    # Synthetic study execution before the declared freeze. Even an otherwise
    # consistent architecture and valid outcome must not be counted as
    # prospective merely because a declaration file exists now.
    root = _mini_root(tmp_path)
    _declare(root)
    earlier = _record(
        root, "batch-plant", "run-earlier",
        started="2026-09-13T23:58:00Z",
        finished="2026-09-13T23:59:00Z",
    )
    _write_batch_record(root, "batch-plant", earlier)

    with pytest.raises(
        prospective.ProspectiveRefusal, match="started before prospective declaration"
    ):
        prospective.check_batch(root, "batch-plant")


def test_missing_or_invalid_registration_time_refuses_batch(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    decl = _declare(root)
    _write_batch_record(root, "batch-plant", _record(root, "batch-plant", "run-normal"))
    decl["declared_utc"] = "not-a-UTC-timestamp"
    prospective.declaration_path(root, "batch-plant").write_text(json.dumps(decl), encoding="utf-8")

    with pytest.raises(prospective.ProspectiveRefusal, match="invalid declaration timestamp"):
        prospective.check_batch(root, "batch-plant")


@pytest.mark.parametrize(
    "field,replacement,reason",
    [
        ("universe_ref", None, "eligibility universe must be"),
        ("universe_ref", "unversioned-pointer", "eligibility universe must be"),
        (
            "universe_ref",
            {"definition": "plant universe", "version": "v1"},
            "eligibility universe digest",
        ),
        (
            "universe_ref",
            {"definition": "plant universe", "digest": "b" * 64},
            "eligibility universe version",
        ),
        (
            "universe_ref",
            {"definition": " ", "version": "v1", "digest": "b" * 64},
            "eligibility universe definition",
        ),
        ("custodian_commitment_sha", None, "custodian_commitment_sha"),
        ("custodian_commitment_sha", "a" * 40, "custodian_commitment_sha"),
    ],
)
def test_a6_missing_or_unbound_eligibility_universe_refuses_batch(
    tmp_path: Path, field: str, replacement: object, reason: str
) -> None:
    """A synthetic completed run is not prospective without an A6 universe binding."""
    root = _mini_root(tmp_path)
    declaration = _declare(root)
    _write_batch_record(root, "batch-plant", _record(root, "batch-plant", "run-one"))
    declaration[field] = replacement
    path = prospective.declaration_path(root, "batch-plant")
    path.write_text(json.dumps(declaration), encoding="utf-8")
    altered_bytes = path.read_bytes()

    with pytest.raises(prospective.ProspectiveRefusal, match=reason):
        prospective.check_batch(root, "batch-plant")
    assert path.read_bytes() == altered_bytes



@pytest.mark.parametrize(
    "forged_invariants",
    [
        None,
        [],
        [" "],
        ["census", ""],
        ["census", "census"],
        ["census", " census "],
        ["census", False],
        "census",
    ],
)
def test_a1_missing_or_ambiguous_preregistered_invariants_refuse_batch(
    tmp_path: Path, forged_invariants: object
) -> None:
    """Synthetic freeze tampering must not produce a batch PASS without rules."""
    root = _mini_root(tmp_path)
    declaration = _declare(root)
    _write_batch_record(root, "batch-plant", _record(root, "batch-plant", "run-one"))
    declaration["invariants"] = forged_invariants
    path = prospective.declaration_path(root, "batch-plant")
    path.write_text(json.dumps(declaration), encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(prospective.ProspectiveRefusal, match="preregistered invariants"):
        prospective.check_batch(root, "batch-plant")
    assert path.read_bytes() == before


def test_a4_completed_run_preserves_structural_check_positive_control(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    _declare(root)
    _write_batch_record(root, "batch-plant", _record(root, "batch-plant", "run-one"))
    summary = prospective.check_batch(root, "batch-plant")
    assert summary["ok"] is True
    assert summary["run_records"] == 1


@pytest.mark.parametrize("first_outcome", ["COMPLETED", "FAILED_CRASH"])
def test_a4_unlabelled_second_attempt_same_topic_must_refuse(
    tmp_path: Path, first_outcome: str
) -> None:
    """A second unlabelled attempt cannot bypass the A4 one-rerun policy."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root)
    first = dict(_record(root, batch, "run-first"), outcome=first_outcome)
    second = _record(
        root, batch, "run-unlabelled-second",
        started="2026-09-14T00:20:00Z",
        finished="2026-09-14T00:21:00Z",
    )
    _write_batch_record(root, batch, first)
    _write_batch_record(root, batch, second)
    # Both records count; a passed first attempt and a failed first attempt
    # are equally unable to authorise an unmarked fresh run.
    assert len(prospective.load_run_records(root, batch)) == 2
    with pytest.raises(
        prospective.ProspectiveRefusal, match="2 unlabelled original attempts"
    ):
        prospective.check_batch(root, batch)


def test_duplicate_run_ids_refuse_batch_instead_of_collapsing_history(tmp_path: Path) -> None:
    # Synthetic failure followed by a success with the SAME identity, stored
    # in two files discoverable by the loader. Previously the by_run mapping
    # silently collapsed them and check_batch returned ok=True.
    root = _mini_root(tmp_path)
    _declare(root)
    failed = _record(root, "batch-plant", "run-collision")
    failed["outcome"] = "FAILED_CRASH"
    completed = dict(failed, outcome="COMPLETED")
    runs = root / "prospective" / "batch-plant" / "runs"
    prospective.write_run_record(runs / "first.json", failed)
    prospective.write_run_record(runs / "second.json", completed)

    loaded = prospective.load_run_records(root, "batch-plant")
    assert [item["outcome"] for item in loaded] == ["FAILED_CRASH", "COMPLETED"]
    with pytest.raises(prospective.ProspectiveRefusal, match="duplicate run_id in batch"):
        prospective.check_batch(root, "batch-plant")




@pytest.mark.parametrize(
    "forgery,reason",
    [
        ("duplicate_timestamp", "duplicate JSON member"),
        ("NaN", "non-finite JSON number"),
        ("1e400", "non-finite JSON number"),
    ],
)
def test_a4_defect_ledger_ambiguous_json_cannot_authorise_rerun(
    tmp_path: Path, forgery: str, reason: str
) -> None:
    """Synthetic ledger poison must REFUSE, never convert a retry into PASS."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root)
    _write_batch_record(
        root, batch, dict(_record(root, batch, "run-original"), outcome="FAILED_CRASH")
    )
    _write_batch_record(
        root,
        batch,
        _record(
            root, batch, "run-rerun",
            started="2026-09-14T00:20:00Z",
            finished="2026-09-14T00:21:00Z",
            rerun_of="run-original",
            justification="rerun because defect-plant documents external failure",
        ),
    )
    entry = prospective.defect_entry(
        batch, "topic-plant", "run-original", "FAILED_CRASH",
        "runner killed", "synthetic event, not independently verified",
        entry_id="defect-plant", declared_utc="2026-09-14T00:19:00Z",
    )
    raw = json.dumps(entry)
    if forgery == "duplicate_timestamp":
        original = '"declared_utc": "2026-09-14T00:19:00Z"'
        assert raw.count(original) == 1
        raw = raw.replace(
            original,
            '"declared_utc": "2026-09-14T00:22:00Z", ' + original,
            1,
        )
        # Standard JSON silently chooses the second timestamp (a false prior).
        assert json.loads(raw)["declared_utc"] == "2026-09-14T00:19:00Z"
    else:
        raw = raw[:-1] + f', "extra": {{"score": {forgery}}}}}'
    ledger = root.parent / "meta-harness-defects" / f"{batch}.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(raw + "\n", encoding="utf-8")
    original_bytes = ledger.read_bytes()

    with pytest.raises(prospective.ProspectiveRefusal, match=reason):
        prospective.load_defects(root, batch)
    with pytest.raises(prospective.ProspectiveRefusal, match=reason):
        prospective.check_batch(root, batch)
    assert ledger.read_bytes() == original_bytes


def test_run_record_duplicate_outcome_cannot_hide_failed_attempt(tmp_path: Path) -> None:
    # A later duplicate JSON member must not replace a recorded failure when
    # the batch validator loads prospective evidence.
    root = _mini_root(tmp_path)
    _declare(root)
    failed = _record(root, "batch-plant", "run-ambiguous")
    failed["outcome"] = "FAILED_CRASH"
    path = _write_batch_record(root, "batch-plant", failed)
    raw = path.read_text(encoding="utf-8")
    original = '"outcome": "FAILED_CRASH"'
    assert raw.count(original) == 1
    raw = raw.replace(original, '"outcome": "FAILED_CRASH", "outcome": "COMPLETED"', 1)
    path.write_text(raw, encoding="utf-8")
    assert json.loads(raw)["outcome"] == "COMPLETED"  # Demonstrates default last-key wins.

    with pytest.raises(prospective.ProspectiveRefusal, match="run record contains duplicate JSON member"):
        prospective.load_run_records(root, "batch-plant")
    with pytest.raises(prospective.ProspectiveRefusal, match="run record contains duplicate JSON member"):
        prospective.check_batch(root, "batch-plant")


@pytest.mark.parametrize("nonfinite", ["NaN", "1e400"])
def test_nonfinite_run_record_metadata_cannot_pass_batch(
    tmp_path: Path, nonfinite: str
) -> None:
    root = _mini_root(tmp_path)
    _declare(root)
    path = _write_batch_record(root, "batch-plant", _record(root, "batch-plant", "run-nonfinite"))
    raw = path.read_text(encoding="utf-8").rstrip()
    assert raw.endswith("}")
    path.write_text(raw[:-1] + f', "extra_metadata": {{"score": {nonfinite}}}}}' + "\n", encoding="utf-8")

    with pytest.raises(prospective.ProspectiveRefusal, match="run record contains non-finite JSON number"):
        prospective.load_run_records(root, "batch-plant")
    with pytest.raises(prospective.ProspectiveRefusal, match="run record contains non-finite JSON number"):
        prospective.check_batch(root, "batch-plant")


def test_declaration_refuses_posthoc_rewrite_and_preserves_first_bytes(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    original = _declare(root)
    path = prospective.declaration_path(root, "batch-plant")
    frozen_bytes = path.read_bytes()

    # Even a locally plausible replacement with a later eligibility rule or
    # time limit must not silently replace the first declaration.
    revised = dict(original, invariants=["posthoc-eligibility"], time_limit_s=3600)
    with pytest.raises(prospective.ProspectiveRefusal, match="declaration already exists"):
        prospective.write_declaration(root, revised)
    with pytest.raises(prospective.ProspectiveRefusal, match="declaration already exists"):
        prospective.write_declaration(root, original)

    assert path.read_bytes() == frozen_bytes
    assert prospective.load_declaration(root, "batch-plant") == original



@pytest.mark.parametrize("limit", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_preregistered_time_limits_are_refused(tmp_path: Path, limit: float) -> None:
    root = _mini_root(tmp_path)
    with pytest.raises(prospective.ProspectiveRefusal, match="time_limit_s must be finite"):
        prospective.batch_declaration(
            root, "batch-invalid-limit", limit, ["census"], COMMITMENT,
            {"definition": "synthetic universe", "digest": "b" * 64},
        )


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_nested_declaration_number_leaves_no_freeze(
    tmp_path: Path, value: float
) -> None:
    root = _mini_root(tmp_path)
    destination = prospective.declaration_path(root, "batch-nonfinite")
    with pytest.raises(prospective.ProspectiveRefusal, match="non-finite JSON number"):
        prospective.write_declaration(root, {
            "batch_id": "batch-nonfinite",
            "universe_ref": {"threshold": value},
        })
    assert not destination.exists()


@pytest.mark.parametrize("number", ["NaN", "Infinity", "-Infinity", "1e400"])
def test_nonfinite_frozen_json_number_refuses_at_load_and_batch_gate(
    tmp_path: Path, number: str
) -> None:
    root = _mini_root(tmp_path)
    path = prospective.declaration_path(root, "batch-nonfinite")
    path.parent.mkdir(parents=True)
    path.write_text(
        '{"batch_id":"batch-nonfinite","universe_ref":{"threshold":'
        + number + '}}', encoding="utf-8"
    )
    with pytest.raises(prospective.ProspectiveRefusal, match="non-finite JSON number"):
        prospective.load_declaration(root, "batch-nonfinite")
    with pytest.raises(prospective.ProspectiveRefusal, match="non-finite JSON number"):
        prospective.check_batch(root, "batch-nonfinite")



def test_declaration_serialization_failure_leaves_no_partial_freeze(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    path = prospective.declaration_path(root, "batch-serialize")

    # An invalid payload must fail before exclusive creation, rather than
    # stranding an empty declaration that cannot subsequently be repaired.
    with pytest.raises(TypeError, match="not JSON serializable"):
        prospective.write_declaration(root, {
            "batch_id": "batch-serialize", "unsupported": object(),
        })
    assert not path.exists()


@pytest.mark.parametrize("payload,member", [
    ('{"batch_id":"batch-plant","batch_id":"posthoc"}', "batch_id"),
    ('{"batch_id":"batch-plant","universe_ref":{"eligibility":"initial",'
     '"eligibility":"posthoc"}}', "eligibility"),
])
def test_duplicate_preregistration_json_members_refuse_at_load_and_batch_gate(
    tmp_path: Path, payload: str, member: str
) -> None:
    # Synthetic hostile declaration: standard json.loads would silently keep
    # the last value, obscuring a competing preregistered eligibility rule.
    root = _mini_root(tmp_path)
    path = prospective.declaration_path(root, "batch-plant")
    path.parent.mkdir(parents=True)
    path.write_text(payload, encoding="utf-8")
    with pytest.raises(prospective.ProspectiveRefusal, match=f"duplicate JSON member '{member}'"):
        prospective.load_declaration(root, "batch-plant")
    with pytest.raises(prospective.ProspectiveRefusal, match=f"duplicate JSON member '{member}'"):
        prospective.check_batch(root, "batch-plant")




def test_declaration_refuses_existing_partial_file_without_replacing_bytes(tmp_path: Path) -> None:
    # Reconciled from the overlapping PR #198: a failed first registration
    # must remain visible for manual review, not silently be overwritten.
    root = _mini_root(tmp_path)
    path = prospective.declaration_path(root, "batch-partial")
    path.parent.mkdir(parents=True)
    path.write_bytes(b"{")
    decl = prospective.batch_declaration(
        root, "batch-partial", 60, ["census"], COMMITMENT,
        {"definition": "synthetic universe", "digest": "b" * 64},
        declared_utc="2026-09-14T00:00:00Z",
    )
    with pytest.raises(prospective.ProspectiveRefusal, match="declaration already exists"):
        prospective.write_declaration(root, decl)
    assert path.read_bytes() == b"{"



def test_declaration_refuses_preexisting_symlink_without_writing_target(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    decl = prospective.batch_declaration(
        root, "batch-linked", 60, ["census"], COMMITMENT,
        {"definition": "synthetic universe", "digest": "b" * 64},
        declared_utc="2026-09-14T00:00:00Z",
    )
    path = prospective.declaration_path(root, "batch-linked")
    path.parent.mkdir(parents=True)
    outside = tmp_path / "untrusted-replacement.json"
    outside.write_text('{"existing": true}', encoding="utf-8")
    before = outside.read_bytes()
    try:
        path.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("filesystem does not permit symlinks")

    with pytest.raises(prospective.ProspectiveRefusal, match="declaration already exists"):
        prospective.write_declaration(root, decl)
    assert path.is_symlink()
    assert outside.read_bytes() == before


@pytest.mark.parametrize("batch_id", [".", ".."])
def test_declaration_refuses_dot_segment_batch_aliases(tmp_path: Path, batch_id: str) -> None:
    root = _mini_root(tmp_path)
    with pytest.raises(prospective.ProspectiveRefusal, match="unsafe prospective declaration directory"):
        prospective.write_declaration(root, {"batch_id": batch_id})
    assert not (root / "declaration.json").exists()
    assert not (root / "prospective" / "declaration.json").exists()


@pytest.mark.parametrize("symlink_parent", ["prospective", "batch"])
def test_declaration_refuses_symlinked_parent_directory(tmp_path: Path, symlink_parent: str) -> None:
    root = _mini_root(tmp_path)
    outside = tmp_path / "external"
    outside.mkdir()
    prospective_dir = root / "prospective"
    if symlink_parent == "prospective":
        link = prospective_dir
    else:
        prospective_dir.mkdir()
        link = prospective_dir / "batch-linked"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("filesystem does not permit directory symlinks")

    # The parent alias must not create an externally located declaration.
    with pytest.raises(prospective.ProspectiveRefusal, match="unsafe prospective declaration directory"):
        prospective.write_declaration(root, {"batch_id": "batch-linked"})
    assert list(outside.iterdir()) == []


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



def test_prospective_run_record_is_write_once_even_if_original_failed(tmp_path: Path) -> None:
    # A rerun cannot silently rewrite the evidence for an earlier FAILED run.
    root = _mini_root(tmp_path)
    _declare(root)
    failed = _record(root, "batch-plant", "run-original")
    failed["outcome"] = "FAILED_CRASH"
    original_path = _write_batch_record(root, "batch-plant", failed)
    original_bytes = original_path.read_bytes()

    corrected = dict(failed, outcome="COMPLETED")
    with pytest.raises(prospective.ProspectiveRefusal, match="run record already exists"):
        _write_batch_record(root, "batch-plant", corrected)
    with pytest.raises(prospective.ProspectiveRefusal, match="run record already exists"):
        _write_batch_record(root, "batch-plant", failed)

    assert original_path.read_bytes() == original_bytes
    assert prospective.load_run_records(root, "batch-plant") == [failed]


def test_partial_prospective_run_record_cannot_be_silently_replaced(tmp_path: Path) -> None:
    # A crash that leaves a partial first write requires manual investigation.
    root = _mini_root(tmp_path)
    record = _record(root, "batch-plant", "run-partial")
    path = root / "prospective" / "batch-plant" / "runs" / "run-partial" / "run_record.json"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"{")
    with pytest.raises(prospective.ProspectiveRefusal, match="run record already exists"):
        prospective.write_run_record(path, record)
    assert path.read_bytes() == b"{"


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
    "field,forged_value,reason",
    [
        ("schema_version", 999, "unsupported schema_version"),
        ("schema_version", True, "unsupported schema_version"),
        ("architecture_components", {}, "architecture component manifest mismatch"),
        ("mutable_dependencies", [], "mutable dependency ledger mismatch"),
        ("external_dependency_mutability", False, "external dependency mutability mismatch"),
        ("external_dependency_mutability", "false", "external dependency mutability mismatch"),
        ("freeze_claim", prospective.IMMUTABLE_FREEZE_CLAIM, "freeze claim mismatches"),
        ("rerun_policy", "reruns without prior defects are permitted", "declared rerun policy differs"),
    ],
)
def test_forged_freeze_metadata_cannot_pass_batch_gate(
    tmp_path: Path, field: str, forged_value: object, reason: str
) -> None:
    # Synthetic direct-file tampering bypasses write_declaration intentionally.
    # A matching architecture digest must not make a dishonest parallel field PASS.
    root = _mini_root(tmp_path)
    original = _declare(root)
    # A nonempty retained-run census is required before structural PASS.
    _write_batch_record(root, "batch-plant", _record(root, "batch-plant", "run-baseline"))
    assert prospective.check_batch(root, "batch-plant")["ok"] is True
    forged = dict(original, **{field: forged_value})
    assert forged["architecture_identity"] == original["architecture_identity"]

    with pytest.raises(prospective.ProspectiveRefusal, match=reason):
        prospective.check_declaration_frozen(root, forged)
    path = prospective.declaration_path(root, "batch-plant")
    path.write_text(json.dumps(forged), encoding="utf-8")
    with pytest.raises(prospective.ProspectiveRefusal, match=reason):
        prospective.check_batch(root, "batch-plant")


@pytest.mark.parametrize(
    "field,reason",
    [
        ("architecture_components", "architecture component manifest mismatch"),
        ("mutable_dependencies", "mutable dependency ledger mismatch"),
        ("external_dependency_mutability", "external dependency mutability mismatch"),
        ("freeze_claim", "freeze claim mismatches"),
        ("rerun_policy", "declared rerun policy differs"),
    ],
)
def test_missing_freeze_metadata_refuses_batch(tmp_path: Path, field: str, reason: str) -> None:
    root = _mini_root(tmp_path)
    forged = _declare(root)
    forged.pop(field)
    path = prospective.declaration_path(root, "batch-plant")
    path.write_text(json.dumps(forged), encoding="utf-8")
    with pytest.raises(prospective.ProspectiveRefusal, match=reason):
        prospective.check_batch(root, "batch-plant")


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
    # Isolate the *late defect* refusal: A4 requires an actual retained
    # infrastructure failure before any defect chronology can be evaluated.
    original = dict(_record(root, batch, "run-original"), outcome="FAILED_CRASH")
    _write_batch_record(root, batch, original)
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



def test_duplicate_defect_ids_cannot_rewrite_rerun_history(tmp_path: Path) -> None:
    # A later ledger line cannot backdate a pre-existing defect id to turn
    # a previously refused rerun into an apparent preregistered exception.
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    original = dict(_record(root, batch, "run-original"), outcome="FAILED_CRASH")
    _write_batch_record(root, batch, original)
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
            justification="rerun because defect-plant documents the failure",
        ),
    )
    late = prospective.defect_entry(
        batch,
        "topic-plant",
        "run-original",
        "FAILED_CRASH",
        "runner killed",
        "synthetic failure",
        entry_id="defect-plant",
        declared_utc="2026-09-14T00:22:00Z",
    )
    ledger = root.parent / "meta-harness-defects" / f"{batch}.jsonl"
    prospective.append_defect(late, ledger, root=root)
    with pytest.raises(prospective.ProspectiveRefusal, match="not declared before rerun start"):
        prospective.check_batch(root, batch)

    # The second line reuses the same identity but claims a prior timestamp.
    prospective.append_defect(
        dict(late, declared_utc="2026-09-14T00:19:00Z"), ledger, root=root
    )
    original_ledger = ledger.read_bytes()
    assert len(original_ledger.splitlines()) == 2
    with pytest.raises(prospective.ProspectiveRefusal, match="duplicate defect id"):
        prospective.check_batch(root, batch)
    assert ledger.read_bytes() == original_ledger



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


@pytest.mark.parametrize(
    "misleading_reference",
    [
        "defect-plant-extra",
        "prefix-defect-plant",
        "defect-plant.more",
    ],
)
def test_a4_defect_id_must_be_cited_as_complete_identifier(
    tmp_path: Path, misleading_reference: str
) -> None:
    """A substring of a different identifier is not a cited A4 defect."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(
        root, batch, dict(_record(root, batch, "run-original"), outcome="FAILED_CRASH")
    )
    prospective.append_defect(
        prospective.defect_entry(
            batch, "topic-plant", "run-original", "FAILED_CRASH",
            "synthetic runner crash", "unverified incident",
            entry_id="defect-plant", declared_utc="2026-09-14T00:19:00Z",
        ),
        root=root,
    )
    _write_batch_record(
        root, batch,
        _record(
            root, batch, "run-rerun",
            started="2026-09-14T00:20:00Z",
            finished="2026-09-14T00:21:00Z",
            rerun_of="run-original",
            justification=f"retry authorised by {misleading_reference}",
        ),
    )
    with pytest.raises(
        prospective.ProspectiveRefusal, match="rerun lacks a prior defect-ledger entry"
    ):
        prospective.check_batch(root, batch)


def test_check_batch_accepts_one_rerun_with_prior_defect(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(
        root, batch,
        dict(_record(root, batch, "run-original"), outcome="FAILED_CRASH"),
    )
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



@pytest.mark.parametrize(
    "defect_topic,defect_run",
    [
        ("topic-other", "run-original"),
        ("topic-plant", "run-other"),
        ("topic-other", "run-other"),
    ],
)
def test_a4_rerun_cannot_cite_unrelated_defect(
    tmp_path: Path, defect_topic: str, defect_run: str
) -> None:
    """Synthetic provenance guard; a different topic/run must not authorise retry."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(
        root, batch,
        dict(_record(root, batch, "run-original"), outcome="FAILED_CRASH"),
    )
    entry = prospective.defect_entry(
        batch, defect_topic, defect_run, "FAILED_CRASH",
        "runner killed", "synthetic infrastructure failure",
        entry_id="defect-unrelated", declared_utc="2026-09-14T00:19:00Z",
    )
    prospective.append_defect(entry, root=root)
    _write_batch_record(
        root, batch,
        _record(
            root, batch, "run-rerun",
            started="2026-09-14T00:20:00Z",
            finished="2026-09-14T00:21:00Z",
            rerun_of="run-original",
            justification="external incident defect-unrelated",
        ),
    )

    with pytest.raises(
        prospective.ProspectiveRefusal, match="bound to original run/topic"
    ):
        prospective.check_batch(root, batch)


def test_a4_completed_original_cannot_be_relabelled_as_failed_for_rerun(
    tmp_path: Path,
) -> None:
    """An ex-post defect assertion cannot alter the archived original outcome."""
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    _write_batch_record(root, batch, _record(root, batch, "run-original"))
    prospective.append_defect(
        prospective.defect_entry(
            batch, "topic-plant", "run-original", "FAILED_CRASH",
            "runner killed", "synthetic alleged incident",
            entry_id="defect-posthoc", declared_utc="2026-09-14T00:19:00Z",
        ),
        root=root,
    )
    _write_batch_record(
        root, batch,
        _record(
            root, batch, "run-rerun",
            started="2026-09-14T00:20:00Z",
            finished="2026-09-14T00:21:00Z",
            rerun_of="run-original",
            justification="external incident defect-posthoc",
        ),
    )
    with pytest.raises(
        prospective.ProspectiveRefusal, match="original run is not a recorded failure"
    ):
        prospective.check_batch(root, batch)


@pytest.mark.parametrize(
    "original_outcome,defect_failure_class,expected_refusal",
    [
        ("FAILED_INVARIANT", "FAILED_INVARIANT", "not a recorded failure eligible"),
        ("FAILED_CRASH", "FAILED_TIMEOUT", "defect failure_class does not match"),
        ("FAILED_TIMEOUT", "FAILED_CRASH", "defect failure_class does not match"),
        ("FAILED_TIMEOUT", "FAILED_TIMEOUT", None),
    ],
)
def test_a4_rerun_requires_infrastructure_eligible_matching_failure(
    tmp_path: Path,
    original_outcome: str,
    defect_failure_class: str,
    expected_refusal: str | None,
) -> None:
    # Synthetic provenance controls only; no independently witnessed incident.
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    original = dict(
        _record(root, batch, "run-original"), outcome=original_outcome
    )
    _write_batch_record(root, batch, original)
    _write_batch_record(
        root,
        batch,
        _record(
            root, batch, "run-rerun",
            started="2026-09-14T00:20:00Z",
            finished="2026-09-14T00:21:00Z",
            rerun_of="run-original",
            justification="external incident defect-classified",
        ),
    )
    prospective.append_defect(
        prospective.defect_entry(
            batch, "topic-plant", "run-original",
            defect_failure_class, "provider error",
            "synthetic unverified incident",
            entry_id="defect-classified",
            declared_utc="2026-09-14T00:19:00Z",
        ),
        root=root,
    )
    if expected_refusal:
        with pytest.raises(prospective.ProspectiveRefusal, match=expected_refusal):
            prospective.check_batch(root, batch)
    else:
        summary = prospective.check_batch(root, batch)
        assert summary["ok"] is True
        assert summary["run_records"] == 2


@pytest.mark.parametrize(
    "original_finished,should_refuse",
    [
        ("2026-09-14T00:21:00Z", True),  # Original still running at retry start.
        ("2026-09-14T00:20:00Z", False),  # Exact handoff boundary is valid.
        ("2026-09-14T00:19:00Z", False),  # Original completed before retry.
    ],
)
def test_a4_rerun_must_follow_original_completion(
    tmp_path: Path, original_finished: str, should_refuse: bool
) -> None:
    # These timestamps and incident descriptions are synthetic developer
    # controls, not witnessed prospective clinical validation.
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    original = dict(
        _record(root, batch, "run-original", finished=original_finished),
        outcome="FAILED_CRASH",
    )
    _write_batch_record(root, batch, original)
    prospective.append_defect(
        prospective.defect_entry(
            batch, "topic-plant", "run-original", "FAILED_CRASH",
            "runner killed", "synthetic unverified infrastructure incident",
            entry_id="defect-order", declared_utc="2026-09-14T00:19:00Z",
        ),
        root=root,
    )
    _write_batch_record(
        root,
        batch,
        _record(
            root, batch, "run-rerun",
            started="2026-09-14T00:20:00Z",
            finished="2026-09-14T00:21:00Z",
            rerun_of="run-original",
            justification="external incident defect-order",
        ),
    )
    if should_refuse:
        with pytest.raises(
            prospective.ProspectiveRefusal,
            match="rerun started before original finished",
        ):
            prospective.check_batch(root, batch)
    else:
        summary = prospective.check_batch(root, batch)
        assert summary["ok"] is True
        assert summary["run_records"] == 2


@pytest.mark.parametrize(
    "timestamp_field,invalid_timestamp",
    [
        ("started_utc", None),
        ("finished_utc", None),
        ("started_utc", ""),
        ("finished_utc", ""),
        ("started_utc", 0),
        ("finished_utc", 0),
    ],
)
def test_a4_completed_run_without_valid_timestamps_cannot_pass(
    tmp_path: Path, timestamp_field: str, invalid_timestamp: object
) -> None:
    # Synthetic engineering regression: a missing recorded time is never
    # independently witnessed chronology and must not produce batch PASS.
    root = _mini_root(tmp_path)
    batch = "batch-plant"
    _declare(root, batch)
    record = _record(root, batch, "run-invalid-timestamp")
    record[timestamp_field] = invalid_timestamp
    _write_batch_record(root, batch, record)

    with pytest.raises(prospective.ProspectiveRefusal, match="UTC timestamp"):
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


@pytest.mark.parametrize(
    "schema_value", ["missing", True, 2, "1", 1.0]
)
def test_a4_run_schema_tampering_cannot_pass_batch(tmp_path: Path, schema_value: object) -> None:
    # Negative synthetic record tampering; this is not a prospective clinical run.
    root = _mini_root(tmp_path)
    _declare(root)
    record = _record(root, "batch-plant", "run-schema")
    if schema_value == "missing":
        record.pop("schema_version")
    else:
        record["schema_version"] = schema_value
    _write_batch_record(root, "batch-plant", record)

    with pytest.raises(prospective.ProspectiveRefusal, match="unsupported schema_version"):
        prospective.check_batch(root, "batch-plant")


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


@pytest.mark.parametrize(
    "finished,outcome,should_refuse",
    [
        ("2026-09-14T00:11:01Z", "COMPLETED", True),
        ("2026-09-14T00:11:00Z", "COMPLETED", False),
        ("2026-09-14T00:11:01Z", "FAILED_TIMEOUT", False),
        ("2026-09-14T00:11:01Z", "FAILED_CRASH", False),
    ],
)
def test_a4_predeclared_time_limit_refuses_completed_overrun(
    tmp_path: Path, finished: str, outcome: str, should_refuse: bool
) -> None:
    # Synthetic time records verify structural refusal only; no witnessed
    # execution or independent clinical outcome is claimed here.
    root = _mini_root(tmp_path)
    _declare(root)
    record = dict(
        _record(root, "batch-plant", "run-timed", finished=finished),
        outcome=outcome,
    )
    _write_batch_record(root, "batch-plant", record)
    if should_refuse:
        with pytest.raises(
            prospective.ProspectiveRefusal,
            match="COMPLETED after predeclared time_limit_s",
        ):
            prospective.check_batch(root, "batch-plant")
    else:
        assert prospective.check_batch(root, "batch-plant")["ok"] is True


@pytest.mark.parametrize("bad_limit", [0, -1, True, "60", None])
def test_a4_tampered_time_limit_cannot_validate_batch(
    tmp_path: Path, bad_limit: object
) -> None:
    root = _mini_root(tmp_path)
    declaration = _declare(root)
    _write_batch_record(root, "batch-plant", _record(root, "batch-plant", "run-timed"))
    declaration["time_limit_s"] = bad_limit
    prospective.declaration_path(root, "batch-plant").write_text(
        json.dumps(declaration), encoding="utf-8"
    )
    with pytest.raises(
        prospective.ProspectiveRefusal, match="time_limit_s must be a positive finite number"
    ):
        prospective.check_batch(root, "batch-plant")


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
