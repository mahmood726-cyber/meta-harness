"""Prospective validation declarations, run records, and defect ledgers."""
from __future__ import annotations

import datetime as _dt
import json
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
    if limit <= 0:
        raise ProspectiveRefusal("time_limit_s must be positive")
    if isinstance(time_limit_s, int):
        limit_value: int | float = int(time_limit_s)
    else:
        limit_value = limit

    components = architecture_identity.components(repo)
    return {
        "schema_version": DECLARATION_VERSION,
        "batch_id": batch,
        "declared_utc": declared_utc or _utc_now(),
        "architecture_identity": architecture_identity.identity_from_components(components),
        "architecture_components": components,
        "mutable_dependencies": architecture_identity.mutable_dependencies(repo),
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(decl, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def load_declaration(root: str | os.PathLike[str], batch_id: str) -> dict[str, Any]:
    path = declaration_path(root, batch_id)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ProspectiveRefusal(f"declaration missing for batch {batch_id!r}") from exc
    except ValueError as exc:
        raise ProspectiveRefusal(f"declaration is not valid JSON: {path}") from exc


def check_declaration_frozen(
    root: str | os.PathLike[str], decl: dict[str, Any]
) -> dict[str, Any]:
    observed = architecture_identity.identity(root)
    expected = decl.get("architecture_identity")
    if observed != expected:
        raise ProspectiveRefusal(
            "architecture identity mismatch: "
            f"expected {expected}, observed {observed}"
        )
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
    return {
        "schema_version": RUN_RECORD_VERSION,
        "run_id": rid,
        "batch_id": batch,
        "topic_identifier": topic,
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "architecture_identity": architecture_identity.identity(root),
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
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
    with path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                entry = json.loads(text)
            except ValueError as exc:
                raise ProspectiveRefusal(
                    f"defect ledger line {line_no} is not valid JSON"
                ) from exc
            if entry.get("batch_id") == batch_id:
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
            record = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise ProspectiveRefusal(f"run record is not valid JSON: {path}") from exc
        if record.get("batch_id") == batch:
            records.append(record)
    return records


def _validate_record_shape(record: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    required = {
        "run_id",
        "batch_id",
        "topic_identifier",
        "started_utc",
        "finished_utc",
        "architecture_identity",
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

    records = load_run_records(repo, batch)
    for record in records:
        reasons.extend(_validate_record_shape(record))

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
        justification = str(record.get("rerun_justification") or "")
        cited = [
            defect
            for defect_id, defect in defects_by_id.items()
            if defect_id and defect_id in justification
        ]
        if not cited:
            reasons.append(
                f"run {record.get('run_id')}: rerun lacks a prior defect-ledger entry"
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
        "ok": True,
    }
