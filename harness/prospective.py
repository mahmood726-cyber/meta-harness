"""Prospective validation declarations, run records, and defect ledgers."""
from __future__ import annotations

import datetime as _dt
import json
import math
import os
import re
from pathlib import Path
from typing import Any

from . import architecture_identity
from .canonical import canonical_json


DECLARATION_VERSION = 1
RUN_RECORD_VERSION = 1
DEFECT_ENTRY_VERSION = 1
RUN_OUTCOMES = (
    "COMPLETED",
    "FAILED_CRASH",
    "FAILED_TIMEOUT",
    "FAILED_INVARIANT",
)
SPEC_REL = Path("docs") / "PROSPECTIVE_VALIDATION_SPEC.md"
DEFECT_ENV = "PROSPECTIVE_DEFECT_LEDGER"
DEFAULT_DEFECT_DIR = "meta-harness-defects"
SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
REPO_ROOT = Path(__file__).resolve().parents[1]
MUTABLE_FREEZE_CLAIM = "frozen local architecture with mutable external model dependency"
IMMUTABLE_FREEZE_CLAIM = "fully frozen computational system"


class ProspectiveRefusal(ValueError):
    """Raised when a prospective-validation invariant refuses an artefact."""


def _root_path(root: str | os.PathLike[str]) -> Path:
    return Path(root).resolve()


def _utc_now() -> str:
    return (
        _dt.datetime.now(_dt.UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _parse_utc(value: str) -> _dt.datetime:
    if not isinstance(value, str):
        raise ProspectiveRefusal(f"UTC timestamp must be a string: {value!r}")
    text = value.replace("Z", "+00:00")
    try:
        parsed = _dt.datetime.fromisoformat(text)
    except ValueError as exc:
        raise ProspectiveRefusal(f"UTC timestamp is not ISO-8601: {value!r}") from exc
    if parsed.tzinfo is None:
        raise ProspectiveRefusal(f"UTC timestamp lacks a timezone: {value!r}")
    return parsed.astimezone(_dt.UTC)


def _require_safe_name(value: str, label: str) -> str:
    text = str(value)
    if not SAFE_NAME_RE.fullmatch(text):
        raise ProspectiveRefusal(f"{label} is not a safe path component: {value!r}")
    return text


def _require_digest(value: str, label: str) -> str:
    text = str(value)
    if not re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", text):
        raise ProspectiveRefusal(f"{label} must be a 40- or 64-hex digest")
    return text.lower()


def _json_list(values: list[str] | tuple[str, ...], label: str) -> list[str]:
    if not isinstance(values, (list, tuple)):
        raise ProspectiveRefusal(f"{label} must be a list")
    out = [str(v) for v in values]
    if any(not v for v in out):
        raise ProspectiveRefusal(f"{label} contains an empty value")
    return out


def rerun_policy_text(root: str | os.PathLike[str]) -> str:
    """Return the A4 numbered rerun policy exactly as stored in the spec."""

    spec = _root_path(root) / SPEC_REL
    try:
        lines = spec.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
    except OSError as exc:
        raise ProspectiveRefusal(f"{SPEC_REL.as_posix()} unreadable: {exc}") from exc

    in_a4 = False
    collecting = False
    out: list[str] = []
    for line in lines:
        if line.startswith("### A4. "):
            in_a4 = True
            continue
        if in_a4 and line.startswith("### "):
            break
        if not in_a4:
            continue
        if re.match(r"^1\. ", line):
            collecting = True
        if collecting and line.startswith("Status:"):
            break
        if collecting:
            out.append(line)
    while out and not out[-1]:
        out.pop()
    if not out or not any(line.startswith("5. ") for line in out):
        raise ProspectiveRefusal("A4 rerun policy items 1-5 were not found")
    return "\n".join(out)


def external_dependency_mutability(root: str | os.PathLike[str]) -> bool:
    """Return whether any architecture-bound external dependency remains mutable."""

    repo = _root_path(root)
    if architecture_identity.mutable_dependencies(repo):
        return True
    stages = architecture_identity.components(repo).get("model_stages", {}).get("stages", [])
    return any(not ((stage.get("snapshot_pinning") or {}).get("pinned")) for stage in stages)


def freeze_claim(root: str | os.PathLike[str]) -> str:
    """Return the honest freeze claim for the current architecture."""

    return MUTABLE_FREEZE_CLAIM if external_dependency_mutability(root) else IMMUTABLE_FREEZE_CLAIM


def batch_declaration(
    root: str | os.PathLike[str],
    batch_id: str,
    time_limit_s: int | float,
    invariants: list[str] | tuple[str, ...],
    custodian_commitment_sha: str,
    universe_ref: dict[str, Any] | str,
    *,
    declared_utc: str | None = None,
) -> dict[str, Any]:
    """Build the prospective-batch declaration object."""

    repo = _root_path(root)
    batch = _require_safe_name(batch_id, "batch_id")
    try:
        limit = float(time_limit_s)
    except (TypeError, ValueError) as exc:
        raise ProspectiveRefusal("time_limit_s must be numeric") from exc
    if not math.isfinite(limit):
        raise ProspectiveRefusal("time_limit_s must be finite")
    if limit <= 0:
        raise ProspectiveRefusal("time_limit_s must be positive")
    if isinstance(time_limit_s, int):
        limit_value: int | float = int(time_limit_s)
    else:
        limit_value = limit

    components = architecture_identity.components(repo)
    mutable = external_dependency_mutability(repo)
    return {
        "schema_version": DECLARATION_VERSION,
        "batch_id": batch,
        "declared_utc": declared_utc or _utc_now(),
        "architecture_identity": architecture_identity.identity_from_components(components),
        "architecture_components": components,
        "mutable_dependencies": architecture_identity.mutable_dependencies(repo),
        "external_dependency_mutability": mutable,
        "freeze_claim": MUTABLE_FREEZE_CLAIM if mutable else IMMUTABLE_FREEZE_CLAIM,
        "rerun_policy": rerun_policy_text(repo),
        "time_limit_s": limit_value,
        "invariants": _json_list(invariants, "invariants"),
        "custodian_commitment_sha": _require_digest(
            custodian_commitment_sha, "custodian_commitment_sha"
        ),
        "universe_ref": universe_ref,
    }


def declaration_path(root: str | os.PathLike[str], batch_id: str) -> Path:
    batch = _require_safe_name(batch_id, "batch_id")
    return _root_path(root) / "prospective" / batch / "declaration.json"


def write_declaration(root: str | os.PathLike[str], decl: dict[str, Any]) -> Path:
    batch = _require_safe_name(decl.get("batch_id"), "batch_id")
    path = declaration_path(root, batch)
    prospective_dir = _root_path(root) / "prospective"
    # Refuse path aliases (including "." and "..") and symlinked ancestors.
    # Exclusive creation below protects the leaf, not its parent directory.
    # This is a local preflight safeguard, not independent/race-free custody.
    if batch in {".", ".."} or prospective_dir.is_symlink() or path.parent.is_symlink():
        raise ProspectiveRefusal("unsafe prospective declaration directory")
    path.parent.mkdir(parents=True, exist_ok=True)
    if prospective_dir.is_symlink() or path.parent.is_symlink():
        raise ProspectiveRefusal("unsafe prospective declaration directory")
    # A second write must never silently revise a prospective declaration
    # after the custodian's commitment or after any study results are visible.
    # Exclusive creation also refuses pre-existing symlinks and concurrent
    # writers, rather than checking exists() before a truncating write.
    # Validate serialization before creating the write-once destination: an
    # unsupported value must not strand an empty/partial frozen declaration.
    try:
        payload = json.dumps(
            decl, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False
        ) + "\n"
    except ValueError as exc:
        raise ProspectiveRefusal("declaration contains a non-finite JSON number") from exc
    try:
        with path.open("x", encoding="utf-8", newline="\n") as fh:
            fh.write(payload)
    except FileExistsError as exc:
        raise ProspectiveRefusal(
            f"declaration already exists for batch {batch!r}; "
            "no in-place revision is permitted"
        ) from exc
    return path


def _parse_strict_prospective_json(text: str, label: str) -> Any:
    """Reject ambiguous or non-finite JSON in frozen prospective evidence.

    Both declarations and run records must use the same decoding rules:
    standard json.loads silently keeps the last duplicate member, potentially
    replacing a recorded FAILED outcome with a later COMPLETED outcome.
    """
    def unique_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ProspectiveRefusal(f"{label} contains duplicate JSON member {key!r}")
            result[key] = value
        return result

    def reject_nonfinite(token: str) -> Any:
        raise ProspectiveRefusal(f"{label} contains non-finite JSON number {token!r}")

    def strict_float(token: str) -> float:
        value = float(token)
        if not math.isfinite(value):
            raise ProspectiveRefusal(f"{label} contains non-finite JSON number")
        return value

    return json.loads(
        text,
        object_pairs_hook=unique_members,
        parse_constant=reject_nonfinite,
        parse_float=strict_float,
    )


def _load_strict_prospective_json(path: Path, label: str) -> Any:
    """Apply strict prospective parsing to a UTF-8 file without losing provenance."""
    return _parse_strict_prospective_json(path.read_text(encoding="utf-8"), label)


def load_declaration(root: str | os.PathLike[str], batch_id: str) -> dict[str, Any]:
    batch = _require_safe_name(batch_id, "batch_id")
    path = declaration_path(root, batch)

    try:
        declaration = _load_strict_prospective_json(path, "declaration")
    except OSError as exc:
        raise ProspectiveRefusal(f"declaration missing for batch {batch!r}") from exc
    except ProspectiveRefusal:
        raise
    except ValueError as exc:
        raise ProspectiveRefusal(f"declaration is not valid JSON: {path}") from exc

    # A declaration's identity must agree with the directory from which it is
    # loaded. A copied or relabelled batch must not pass with zero run records.
    if not isinstance(declaration, dict) or declaration.get("batch_id") != batch:
        raise ProspectiveRefusal(
            f"declaration batch_id does not match requested batch {batch!r}"
        )
    return declaration


def check_declaration_frozen(
    root: str | os.PathLike[str], decl: dict[str, Any]
) -> dict[str, Any]:
    """Verify declaration metadata against the actual architecture and A4 policy.

    The architecture digest alone does not authenticate parallel fields such
    as model mutability, the component inventory, or the rerun policy.
    This is a local consistency check, not externally witnessed registration.
    """
    if (
        not isinstance(decl, dict)
        or type(decl.get("schema_version")) is not int
        or decl["schema_version"] != DECLARATION_VERSION
    ):
        raise ProspectiveRefusal("prospective declaration has an unsupported schema_version")

    observed_components = architecture_identity.components(root)
    observed = architecture_identity.identity_from_components(observed_components)
    expected = decl.get("architecture_identity")
    if observed != expected:
        raise ProspectiveRefusal(
            "architecture identity mismatch: "
            f"expected {expected}, observed {observed}"
        )
    if decl.get("architecture_components") != observed_components:
        raise ProspectiveRefusal("architecture component manifest mismatch")

    observed_dependencies = architecture_identity.mutable_dependencies(root)
    if (
        type(decl.get("mutable_dependencies")) is not list
        or decl["mutable_dependencies"] != observed_dependencies
    ):
        raise ProspectiveRefusal("mutable dependency ledger mismatch")

    observed_mutable = external_dependency_mutability(root)
    if (
        type(decl.get("external_dependency_mutability")) is not bool
        or decl["external_dependency_mutability"] != observed_mutable
    ):
        raise ProspectiveRefusal("external dependency mutability mismatch")

    observed_claim = MUTABLE_FREEZE_CLAIM if observed_mutable else IMMUTABLE_FREEZE_CLAIM
    if decl.get("freeze_claim") != observed_claim:
        raise ProspectiveRefusal("freeze claim mismatches observed dependency mutability")

    if decl.get("rerun_policy") != rerun_policy_text(root):
        raise ProspectiveRefusal("declared rerun policy differs from preregistered protocol")
    return decl


def _run_id(
    batch_id: str,
    topic_identifier: str,
    started_utc: str,
    outcome: str,
) -> str:
    raw = canonical_json(
        {
            "batch_id": batch_id,
            "topic_identifier": topic_identifier,
            "started_utc": started_utc,
            "outcome": outcome,
        }
    )
    import hashlib

    return "run-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def run_record(
    root: str | os.PathLike[str],
    batch_id: str,
    topic_identifier: str,
    started_utc: str,
    finished_utc: str,
    outcome: str,
    artefact_paths: list[str] | tuple[str, ...],
    *,
    run_id: str | None = None,
    rerun_of: str | None = None,
    rerun_justification: str | None = None,
) -> dict[str, Any]:
    """Build one prospective topic-run record."""

    batch = _require_safe_name(batch_id, "batch_id")
    topic = str(topic_identifier)
    if not topic:
        raise ProspectiveRefusal("topic_identifier is required")
    if outcome not in RUN_OUTCOMES:
        raise ProspectiveRefusal(f"unknown run outcome: {outcome!r}")
    started = _parse_utc(started_utc)
    finished = _parse_utc(finished_utc)
    if finished < started:
        raise ProspectiveRefusal("finished_utc precedes started_utc")
    rid = run_id or _run_id(batch, topic, started_utc, outcome)
    _require_safe_name(rid, "run_id")
    if rerun_of is not None and not str(rerun_justification or "").strip():
        raise ProspectiveRefusal("rerun_justification is required when rerun_of is set")
    mutable = external_dependency_mutability(root)
    return {
        "schema_version": RUN_RECORD_VERSION,
        "run_id": rid,
        "batch_id": batch,
        "topic_identifier": topic,
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "architecture_identity": architecture_identity.identity(root),
        "external_dependency_mutability": mutable,
        "freeze_claim": MUTABLE_FREEZE_CLAIM if mutable else IMMUTABLE_FREEZE_CLAIM,
        "outcome": outcome,
        "artefact_paths": _json_list(artefact_paths, "artefact_paths"),
        "rerun_of": None if rerun_of is None else str(rerun_of),
        "rerun_justification": None
        if rerun_justification is None
        else str(rerun_justification),
    }


def write_run_record(path_or_dir: str | os.PathLike[str], record: dict[str, Any]) -> Path:
    path = Path(path_or_dir)
    if path.suffix.lower() != ".json":
        path = path / "run_record.json"
    # A failed, timed-out or surprising prospective run must retain its first
    # record. Rewriting the same path could erase it from the batch history.
    # Pre-serialize so malformed input cannot strand an empty sealed record.
    payload = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as fh:
            fh.write(payload)
    except FileExistsError as exc:
        raise ProspectiveRefusal(
            f"run record already exists at {path}; retain the original and use a distinct run_id"
        ) from exc
    return path


def defect_entry(
    batch_id: str,
    topic_identifier: str,
    failed_run_id: str,
    failure_class: str,
    attribution: str,
    detail: str,
    *,
    entry_id: str | None = None,
    declared_utc: str | None = None,
) -> dict[str, Any]:
    """Build one defect-ledger entry."""

    batch = _require_safe_name(batch_id, "batch_id")
    declared = declared_utc or _utc_now()
    _parse_utc(declared)
    seed = canonical_json(
        {
            "batch_id": batch,
            "topic_identifier": str(topic_identifier),
            "failed_run_id": str(failed_run_id),
            "failure_class": str(failure_class),
            "declared_utc": declared,
        }
    )
    if entry_id is None:
        import hashlib

        entry_id = "defect-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    _require_safe_name(entry_id, "entry_id")
    return {
        "schema_version": DEFECT_ENTRY_VERSION,
        "id": entry_id,
        "batch_id": batch,
        "topic_identifier": str(topic_identifier),
        "failed_run_id": str(failed_run_id),
        "failure_class": str(failure_class),
        "attribution": str(attribution),
        "declared_utc": declared,
        "detail": str(detail),
    }


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def defect_ledger_path(
    root: str | os.PathLike[str],
    batch_id: str,
    ledger_path: str | os.PathLike[str] | None = None,
) -> Path:
    repo = _root_path(root)
    batch = _require_safe_name(batch_id, "batch_id")
    raw = ledger_path or os.environ.get(DEFECT_ENV)
    if raw is None:
        path = repo.parent / DEFAULT_DEFECT_DIR / f"{batch}.jsonl"
    else:
        path = Path(raw)
        if not path.is_absolute():
            path = repo / path
    path = path.resolve()
    if _inside(path, repo):
        raise ProspectiveRefusal(
            "defect ledger path is inside the repository tree; "
            "prospective defects must be recorded outside it"
        )
    return path


def append_defect(
    entry: dict[str, Any],
    ledger_path: str | os.PathLike[str] | None = None,
    *,
    root: str | os.PathLike[str] | None = None,
) -> Path:
    repo = _root_path(root or REPO_ROOT)
    batch = _require_safe_name(entry.get("batch_id"), "batch_id")
    if entry.get("schema_version") != DEFECT_ENTRY_VERSION:
        raise ProspectiveRefusal("defect entry has an unsupported schema_version")
    if not entry.get("id"):
        raise ProspectiveRefusal("defect entry missing id")
    _parse_utc(str(entry.get("declared_utc")))
    path = defect_ledger_path(repo, batch, ledger_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(canonical_json(entry) + "\n")
    return path


def load_defects(root: str | os.PathLike[str], batch_id: str) -> list[dict[str, Any]]:
    try:
        path = defect_ledger_path(root, batch_id)
    except ProspectiveRefusal:
        raise
    if not path.exists():
        return []
    entries = []
    seen_defect_ids: set[str] = set()
    with path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                # Ledger lines authorize reruns and need the same unambiguous
                # JSON rules as frozen declarations and retained run records.
                entry = _parse_strict_prospective_json(
                    text, f"defect ledger line {line_no}"
                )
            except ProspectiveRefusal:
                raise
            except ValueError as exc:
                raise ProspectiveRefusal(
                    f"defect ledger line {line_no} is not valid JSON"
                ) from exc
            if entry.get("batch_id") == batch_id:
                # A rerun cites a defect by id. Ambiguous duplicate ids would
                # silently overwrite earlier evidence in check_batch's lookup;
                # refuse even identical repeats rather than choosing one.
                if entry.get("id"):
                    defect_id = str(entry["id"])
                    if defect_id in seen_defect_ids:
                        raise ProspectiveRefusal(
                            f"duplicate defect id in batch {batch_id!r}: "
                            f"{defect_id!r} (line {line_no})"
                        )
                    seen_defect_ids.add(defect_id)
                entries.append(entry)
    return entries


def _run_record_paths(root: Path, batch_id: str) -> list[Path]:
    base = root / "prospective" / batch_id
    if not base.exists():
        return []
    paths: set[Path] = set()
    for pattern in ("runs/*.json", "runs/**/run_record.json", "**/run_record.json"):
        paths.update(p.resolve() for p in base.glob(pattern) if p.is_file())
    return sorted(paths)


def load_run_records(root: str | os.PathLike[str], batch_id: str) -> list[dict[str, Any]]:
    repo = _root_path(root)
    batch = _require_safe_name(batch_id, "batch_id")
    records = []
    for path in _run_record_paths(repo, batch):
        try:
            record = _load_strict_prospective_json(path, "run record")
        except ProspectiveRefusal:
            raise
        except (OSError, UnicodeError, ValueError) as exc:
            raise ProspectiveRefusal(f"run record is not valid JSON: {path}") from exc
        # Never silently hide an off-batch run from the denominator. A record
        # stored under this batch but claiming another batch must fail closed.
        if not isinstance(record, dict) or record.get("batch_id") != batch:
            raise ProspectiveRefusal(
                f"run record batch_id does not match requested batch {batch!r}: {path}"
            )
        records.append(record)
    return records


def _validate_record_shape(record: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    # A versionless or incorrectly versioned record is not a valid retained
    # prospective run. Compare exact types: bool True must not masquerade as v1.
    if type(record.get("schema_version")) is not int or record["schema_version"] != RUN_RECORD_VERSION:
        reasons.append(f"run {record.get('run_id')}: unsupported schema_version")
    required = {
        "run_id",
        "batch_id",
        "topic_identifier",
        "started_utc",
        "finished_utc",
        "architecture_identity",
        "external_dependency_mutability",
        "freeze_claim",
        "outcome",
        "artefact_paths",
        "rerun_of",
        "rerun_justification",
    }
    missing = sorted(required - set(record))
    if missing:
        reasons.append("run record missing fields: " + ", ".join(missing))
    if record.get("outcome") not in RUN_OUTCOMES:
        reasons.append(f"run {record.get('run_id')}: invalid outcome {record.get('outcome')!r}")
    if not isinstance(record.get("artefact_paths"), list):
        reasons.append(f"run {record.get('run_id')}: artefact_paths is not a list")
    if not isinstance(record.get("external_dependency_mutability"), bool):
        reasons.append(f"run {record.get('run_id')}: external_dependency_mutability is not a boolean")
    expected_claims = {MUTABLE_FREEZE_CLAIM, IMMUTABLE_FREEZE_CLAIM}
    if record.get("freeze_claim") not in expected_claims:
        reasons.append(f"run {record.get('run_id')}: invalid freeze_claim")
    try:
        if record.get("started_utc") and record.get("finished_utc"):
            started = _parse_utc(record["started_utc"])
            finished = _parse_utc(record["finished_utc"])
            if finished < started:
                reasons.append(f"run {record.get('run_id')}: finished before started")
    except ProspectiveRefusal as exc:
        reasons.append(f"run {record.get('run_id')}: {exc}")
    return reasons


def check_batch(root: str | os.PathLike[str], batch_id: str) -> dict[str, Any]:
    """Validate a batch declaration and all run records discoverable under it."""

    repo = _root_path(root)
    batch = _require_safe_name(batch_id, "batch_id")
    reasons: list[str] = []
    decl = load_declaration(repo, batch)
    try:
        check_declaration_frozen(repo, decl)
    except ProspectiveRefusal as exc:
        reasons.append(str(exc))

    # A locally labelled prospective record cannot predate the stored freeze.
    # This checks internal chronology only: a developer-supplied timestamp is
    # not an independently witnessed registration or immutable custody proof.
    try:
        declared_at = _parse_utc(decl.get("declared_utc"))
    except ProspectiveRefusal as exc:
        reasons.append(f"invalid declaration timestamp: {exc}")
        declared_at = None

    records = load_run_records(repo, batch)
    if declared_at is not None:
        for record in records:
            try:
                if _parse_utc(record.get("started_utc")) < declared_at:
                    reasons.append(
                        f"run {record.get('run_id')}: started before prospective declaration"
                    )
            except ProspectiveRefusal:
                # The record-shape check below reports invalid run timestamps.
                pass
    # A declaration alone is not an executed validation batch. Without this
    # refusal, check_batch returned ok=True for a zero-run denominator.
    if not records:
        reasons.append("batch has no retained prospective run records; cannot pass an empty batch")
    seen_run_ids: set[str] = set()
    for record in records:
        reasons.extend(_validate_record_shape(record))
        # Duplicate identifiers would silently collapse in the by_run lookup
        # below. Keep both observed files visible and refuse ambiguous
        # prospective run histories rather than allowing a misleading PASS.
        run_id = record.get("run_id")
        if isinstance(run_id, str) and run_id:
            if run_id in seen_run_ids:
                reasons.append(f"duplicate run_id in batch: {run_id!r}")
            seen_run_ids.add(run_id)

    # A4's predeclared run limit is part of the frozen batch contract. A run
    # that exceeds it cannot be reported as COMPLETED. These are self-reported
    # timestamps, not independently witnessed execution or source custody.
    limit_raw = decl.get("time_limit_s")
    limit_seconds: float | None = None
    if type(limit_raw) not in (int, float):
        reasons.append("declaration time_limit_s must be a positive finite number")
    else:
        try:
            limit_seconds = float(limit_raw)
        except OverflowError:
            limit_seconds = None
        if limit_seconds is None or not math.isfinite(limit_seconds) or limit_seconds <= 0:
            reasons.append("declaration time_limit_s must be a positive finite number")
            limit_seconds = None

    if limit_seconds is not None:
        for record in records:
            try:
                elapsed = (
                    _parse_utc(record.get("finished_utc"))
                    - _parse_utc(record.get("started_utc"))
                ).total_seconds()
            except ProspectiveRefusal:
                # Invalid timestamps are handled by the run shape checker.
                continue
            if elapsed > limit_seconds and record.get("outcome") == "COMPLETED":
                reasons.append(
                    f"run {record.get('run_id')}: COMPLETED after predeclared "
                    f"time_limit_s ({elapsed:g}s > {limit_seconds:g}s)"
                )

    identities = {
        record.get("architecture_identity")
        for record in records
        if record.get("architecture_identity")
    }
    if len(identities) > 1:
        reasons.append("batch contains run records with two architecture identities")
    declared_identity = decl.get("architecture_identity")
    for record in records:
        if record.get("architecture_identity") != declared_identity:
            reasons.append(
                f"run {record.get('run_id')}: architecture identity differs from declaration"
            )
        if record.get("external_dependency_mutability") != decl.get("external_dependency_mutability"):
            reasons.append(
                f"run {record.get('run_id')}: external_dependency_mutability differs from declaration"
            )
        if record.get("freeze_claim") != decl.get("freeze_claim"):
            reasons.append(f"run {record.get('run_id')}: freeze_claim differs from declaration")

    by_run = {record.get("run_id"): record for record in records if record.get("run_id")}
    reruns_by_topic: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        if record.get("rerun_of") is not None:
            reruns_by_topic.setdefault(str(record.get("topic_identifier")), []).append(record)

    for topic, reruns in reruns_by_topic.items():
        if len(reruns) > 1:
            reasons.append(f"topic {topic!r} has more than one rerun")

    defects = load_defects(repo, batch)
    defects_by_id = {str(entry.get("id")): entry for entry in defects if entry.get("id")}
    for record in records:
        original_id = record.get("rerun_of")
        if original_id is None:
            continue
        original = by_run.get(original_id)
        if original is None:
            reasons.append(
                f"run {record.get('run_id')}: rerun_of names a missing original"
            )
        elif original.get("topic_identifier") != record.get("topic_identifier"):
            reasons.append(
                f"run {record.get('run_id')}: original topic does not match rerun topic"
            )
        elif original.get("outcome") not in ("FAILED_CRASH", "FAILED_TIMEOUT"):
            # A4 requires an external infrastructure incident. A recorded
            # FAILED_INVARIANT is a retained scientific/control failure, not
            # a result to rescue with a post-hoc defect assertion.
            reasons.append(
                f"run {record.get('run_id')}: original run is not a recorded failure "
                "eligible for an infrastructure rerun"
            )
        # A retry cannot precede completion of the original attempt. Without
        # this ordering check, an overlapping retry could be counted as a
        # post-failure A4 rerun even while the original was still running.
        # These locally reported times are not independently witnessed.
        if original is not None:
            try:
                original_finished = _parse_utc(original.get("finished_utc"))
                rerun_started = _parse_utc(record.get("started_utc"))
            except ProspectiveRefusal:
                # The run-shape checker reports malformed timestamps.
                pass
            else:
                if rerun_started < original_finished:
                    reasons.append(
                        f"run {record.get('run_id')}: rerun started before original finished"
                    )
        justification = str(record.get("rerun_justification") or "")
        cited = [
            defect
            for defect_id, defect in defects_by_id.items()
            if (
                defect_id
                and defect_id in justification
                and defect.get("failed_run_id") == original_id
                and defect.get("topic_identifier") == record.get("topic_identifier")
            )
        ]
        if not cited:
            reasons.append(
                f"run {record.get('run_id')}: rerun lacks a prior defect-ledger entry "
                "bound to original run/topic"
            )
            continue
        # The ledger must agree with the retained original outcome. Otherwise
        # a timeout allegation could authorise retry of an invariant failure
        # or a crash by changing only the defect's self-reported class.
        if original is not None:
            cited = [
                defect for defect in cited
                if defect.get("failure_class") == original.get("outcome")
            ]
            if not cited:
                reasons.append(
                    f"run {record.get('run_id')}: cited defect failure_class "
                    "does not match original outcome"
                )
                continue
        try:
            rerun_started = _parse_utc(record["started_utc"])
            prior = [
                defect
                for defect in cited
                if _parse_utc(str(defect.get("declared_utc"))) < rerun_started
            ]
        except ProspectiveRefusal as exc:
            reasons.append(f"run {record.get('run_id')}: {exc}")
            continue
        if not prior:
            reasons.append(
                f"run {record.get('run_id')}: cited defect was not declared before rerun start"
            )

    if reasons:
        raise ProspectiveRefusal("PROSPECTIVE BATCH REFUSED:\n  - " + "\n  - ".join(reasons))
    return {
        "batch_id": batch,
        "run_records": len(records),
        "defect_entries": len(defects),
        "architecture_identity": declared_identity,
        "external_dependency_mutability": decl.get("external_dependency_mutability"),
        "freeze_claim": decl.get("freeze_claim"),
        "ok": True,
    }
