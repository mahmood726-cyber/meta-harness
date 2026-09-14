"""Fix-state discipline for the machine-readable fix object store.

The v2 ladder is SPECIFIED -> REPORTED -> LANDED ->
INTERNALLY_VERIFIED -> INDEPENDENTLY_VERIFIED -> GENERALIZED.
There is deliberately no bare VERIFIED state. The old state collapsed
"verified by another agent in this development environment" with
"verified by an external auditor against served bytes"; this checker keeps
those claims separate.

This is the same defect family as accepting an assurance claim from the
representation of a property rather than from the property itself: benchmark
leakage, held-out blinding claims, deployment authority claims, and the twelve
phantom fixes all became possible when an assertion about evidence stood in for
the evidence property.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from harness.target import TargetUnresolvable, describe_target, refusal as target_refusal


REGISTRY_PATH = Path("registry") / "fixes.json"
LEDGER_PATH = Path("docs") / "fix_ledger.json"
SCHEMA_VERSION = 2
STATUSES = (
    "SPECIFIED",
    "REPORTED",
    "LANDED",
    "INTERNALLY_VERIFIED",
    "INDEPENDENTLY_VERIFIED",
    "GENERALIZED",
)
FIX_STATUSES = (
    "REPORTED",
    "LANDED",
    "INTERNALLY_VERIFIED",
    "INDEPENDENTLY_VERIFIED",
    "GENERALIZED",
)
VERIFIED_STATUSES = ("INTERNALLY_VERIFIED", "INDEPENDENTLY_VERIFIED")
VERIFIER_KINDS = ("author", "internal_agent", "external_auditor")
KINDS = ("fix", "control")
FORWARD_TRANSITIONS = {
    ("SPECIFIED", "LANDED"),
    ("REPORTED", "LANDED"),
    ("LANDED", "INTERNALLY_VERIFIED"),
    ("INTERNALLY_VERIFIED", "INDEPENDENTLY_VERIFIED"),
    ("INDEPENDENTLY_VERIFIED", "GENERALIZED"),
}
REPORTED_DOWNGRADE_PREFIXES = ("detector proven to miss", "assurance stale")
REQUIRED_ENTRY_KEYS = {
    "finding_id",
    "fix_id",
    "title",
    "kind",
    "status",
    "author",
    "opened_utc",
    "evidence_dir",
    "history",
    "verified_by",
    "verifications",
    "authored_against",
    "generalized_on",
    "executable_evidence",
}
REQUIRED_HISTORY_KEYS = {
    "status",
    "when_utc",
    "by",
    "commit",
    "evidence",
    "reason",
}
REQUIRED_VERIFICATION_KEYS = {
    "claim_id",
    "verifier",
    "evidence",
    "architecture_identity",
    "method",
    "scope",
    "scope_blob_shas",
    "when_utc",
    "commit",
}
REQUIRED_VERIFIER_KEYS = {"identity", "kind"}
REQUIRED_EVIDENCE_KEYS = {"path", "sha256"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _root_path(root: str | os.PathLike[str]) -> Path:
    return Path(root).resolve()


def _posix(path: str | os.PathLike[str]) -> str:
    clean = os.fspath(path).replace("\\", "/")
    while clean.startswith("./"):
        clean = clean[2:]
    return clean


def _display_path(path: Path) -> str:
    return _posix(path)


def _utc_now() -> str:
    return (
        _dt.datetime.now(_dt.UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _run_git(root: Path, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return proc


def _git_stdout(root: Path, args: list[str]) -> str:
    return _run_git(root, args).stdout


def _head_commit(root: Path) -> str:
    proc = _run_git(root, ["rev-parse", "--verify", "HEAD"], check=False)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _commit_exists(root: Path, commit: str) -> bool:
    if not isinstance(commit, str) or not commit.strip():
        return False
    proc = _run_git(root, ["cat-file", "-e", f"{commit}^{{commit}}"], check=False)
    return proc.returncode == 0


def _path_is_repo_relative(path: str) -> bool:
    if not isinstance(path, str) or not path or os.path.isabs(path):
        return False
    parts = [part for part in _posix(path).split("/") if part]
    return bool(parts) and ".." not in parts


def _git_blob_sha(root: Path, relpath: str) -> str | None:
    path = root / relpath
    if not path.is_file():
        return None
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=1, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def load(root: str | os.PathLike[str]) -> dict[str, Any]:
    """Load ``registry/fixes.json`` from ``root``."""

    return _load_json(_root_path(root) / REGISTRY_PATH)


def entries(store: dict[str, Any]) -> list[dict[str, Any]]:
    raw = store.get("entries")
    return raw if isinstance(raw, list) else []


def _entry_label(entry: dict[str, Any], idx: int) -> str:
    return str(entry.get("fix_id") or entry.get("finding_id") or f"entries[{idx}]")


def _history_key(history: dict[str, Any]) -> str:
    return json.dumps(history, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _latest_history(entry: dict[str, Any], status: str) -> dict[str, Any] | None:
    for item in reversed(entry.get("history") or []):
        if isinstance(item, dict) and item.get("status") == status:
            return item
    return None


def _has_history_status(entry: dict[str, Any], status: str) -> bool:
    return _latest_history(entry, status) is not None


def _is_at_least(status: str, threshold: str) -> bool:
    order = {value: idx for idx, value in enumerate(STATUSES)}
    return order[status] >= order[threshold]


def _scope_blob_shas(root: Path, scope: list[str]) -> dict[str, str | None]:
    records: dict[str, str | None] = {}
    for raw in scope:
        rel = _posix(str(raw))
        if not _path_is_repo_relative(rel):
            records[rel] = None
            continue
        path = root / rel
        if path.is_file():
            records[rel] = _git_blob_sha(root, rel)
        elif path.is_dir():
            for child in sorted(p for p in path.rglob("*") if p.is_file()):
                child_rel = _posix(child.relative_to(root))
                records[child_rel] = _git_blob_sha(root, child_rel)
        else:
            records[rel] = None
    return records


def _evidence_is_external(path: str) -> bool:
    text = str(path)
    return (
        text.startswith(("http://", "https://", "urn:", "doi:", "external:", "signed:"))
        or not _path_is_repo_relative(text)
    )


def _validate_executable_evidence(root: Path, entry: dict[str, Any], label: str) -> list[str]:
    evidence = entry.get("executable_evidence")
    if not isinstance(evidence, dict):
        return [f"{label}: control LANDED needs executable_evidence"]
    command = evidence.get("command")
    expected = evidence.get("expected_substring")
    if not isinstance(command, str) or not command.strip():
        return [f"{label}: executable_evidence.command must be a non-empty string"]
    if not isinstance(expected, str) or not expected:
        return [f"{label}: executable_evidence.expected_substring must be a non-empty string"]
    try:
        proc = subprocess.run(
            command,
            cwd=root,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return [f"{label}: executable_evidence timed out after 120 seconds"]
    except OSError as exc:
        return [f"{label}: executable_evidence could not run: {exc}"]
    output = (proc.stdout or "") + (proc.stderr or "")
    reasons: list[str] = []
    if proc.returncode != 0:
        reasons.append(f"{label}: executable_evidence exited {proc.returncode}")
    if expected not in output:
        reasons.append(f"{label}: executable_evidence missing expected substring {expected!r}")
    return reasons


def _validate_landed(root: Path, entry: dict[str, Any], history: dict[str, Any], label: str) -> list[str]:
    commit = history.get("commit")
    if not _commit_exists(root, commit):
        return [f"{label}: LANDED history commit does not exist: {commit!r}"]
    if entry.get("kind") == "control":
        return _validate_executable_evidence(root, entry, label)
    return []


def _validate_verifier_obj(verifier: Any, label: str, *, allow_null: bool) -> list[str]:
    if not isinstance(verifier, dict):
        return [f"{label}: verifier must be an object"]
    missing = sorted(REQUIRED_VERIFIER_KEYS - set(verifier))
    extra = sorted(set(verifier) - REQUIRED_VERIFIER_KEYS)
    reasons = []
    if missing:
        reasons.append(f"{label}: verifier missing keys: {', '.join(missing)}")
    if extra:
        reasons.append(f"{label}: verifier unexpected keys: {', '.join(extra)}")
    identity = verifier.get("identity")
    kind = verifier.get("kind")
    if kind is None:
        if not allow_null or identity is not None:
            reasons.append(f"{label}: null verifier requires identity=null and is allowed only before verification")
        return reasons
    if kind not in VERIFIER_KINDS:
        reasons.append(f"{label}: verifier.kind must be one of {', '.join(VERIFIER_KINDS)} or null")
    if not isinstance(identity, str) or not identity.strip():
        reasons.append(f"{label}: verifier.identity must be a non-empty string")
    return reasons


def _validate_evidence_object(root: Path, obj: Any, label: str) -> list[str]:
    if not isinstance(obj, dict):
        return [f"{label}: evidence item must be an object"]
    missing = sorted(REQUIRED_EVIDENCE_KEYS - set(obj))
    extra = sorted(set(obj) - REQUIRED_EVIDENCE_KEYS)
    reasons: list[str] = []
    if missing:
        reasons.append(f"{label}: evidence item missing keys: {', '.join(missing)}")
    if extra:
        reasons.append(f"{label}: evidence item unexpected keys: {', '.join(extra)}")
    path = obj.get("path")
    sha = obj.get("sha256")
    if not isinstance(path, str) or not path:
        reasons.append(f"{label}: evidence.path must be a non-empty string")
        return reasons
    if not isinstance(sha, str) or not sha:
        reasons.append(f"{label}: evidence.sha256 must be a non-empty string")
    if _path_is_repo_relative(path):
        rel = _posix(path)
        full = root / rel
        if not full.is_file():
            reasons.append(f"{label}: evidence path missing in working tree: {rel}")
        else:
            observed = _sha256_file(full)
            if isinstance(sha, str) and SHA256_RE.fullmatch(sha.lower()) and observed != sha.lower():
                reasons.append(f"{label}: evidence sha256 mismatch for {rel}")
    return reasons


def _validate_verification(root: Path, entry: dict[str, Any], obj: Any, idx: int, label: str) -> list[str]:
    vlabel = f"{label}: verifications[{idx}]"
    if not isinstance(obj, dict):
        return [f"{vlabel} must be an object"]
    reasons: list[str] = []
    missing = sorted(REQUIRED_VERIFICATION_KEYS - set(obj))
    extra = sorted(set(obj) - REQUIRED_VERIFICATION_KEYS)
    if missing:
        reasons.append(f"{vlabel} missing keys: {', '.join(missing)}")
    if extra:
        reasons.append(f"{vlabel} unexpected keys: {', '.join(extra)}")
    if obj.get("claim_id") != entry.get("fix_id"):
        reasons.append(f"{vlabel}.claim_id must equal fix_id")
    reasons.extend(_validate_verifier_obj(obj.get("verifier"), vlabel, allow_null=False))
    evidence = obj.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        reasons.append(f"{vlabel}.evidence must be a non-empty list")
    elif isinstance(evidence, list):
        for eidx, evidence_obj in enumerate(evidence):
            reasons.extend(_validate_evidence_object(root, evidence_obj, f"{vlabel}.evidence[{eidx}]"))
    for key in ("architecture_identity", "method", "when_utc"):
        if not isinstance(obj.get(key), str) or not obj.get(key):
            reasons.append(f"{vlabel}.{key} must be a non-empty string")
    commit = obj.get("commit")
    if commit and (not isinstance(commit, str) or not _commit_exists(root, commit)):
        reasons.append(f"{vlabel}.commit does not exist: {commit!r}")
    scope = obj.get("scope")
    if not isinstance(scope, list) or not scope:
        reasons.append(f"{vlabel}.scope must be a non-empty list")
    else:
        for raw in scope:
            if not _path_is_repo_relative(str(raw)):
                reasons.append(f"{vlabel}.scope path must be repo-relative: {raw!r}")
    scope_blob_shas = obj.get("scope_blob_shas")
    if not isinstance(scope_blob_shas, dict) or not scope_blob_shas:
        reasons.append(f"{vlabel}.scope_blob_shas must be a non-empty object")
    elif isinstance(scope_blob_shas, dict):
        for path, blob in scope_blob_shas.items():
            if not _path_is_repo_relative(str(path)):
                reasons.append(f"{vlabel}.scope_blob_shas path must be repo-relative: {path!r}")
            if blob is not None and (not isinstance(blob, str) or not re.fullmatch(r"[0-9a-f]{40}", blob)):
                reasons.append(f"{vlabel}.scope_blob_shas[{path!r}] must be a git blob sha or null")
    return reasons


def _verification_candidates(entry: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    return [
        item
        for item in (entry.get("verifications") or [])
        if isinstance(item, dict)
        and isinstance(item.get("verifier"), dict)
        and item["verifier"].get("kind") == kind
    ]


def _validate_status_verifications(root: Path, entry: dict[str, Any], label: str) -> list[str]:
    status = entry.get("status")
    reasons: list[str] = []
    verified_by = entry.get("verified_by")
    if status in ("SPECIFIED", "REPORTED", "LANDED"):
        if isinstance(verified_by, dict) and (
            verified_by.get("identity") is not None or verified_by.get("kind") is not None
        ):
            reasons.append(f"{label}: non-verified status must use verified_by identity=null, kind=null")
        return reasons

    if status == "INTERNALLY_VERIFIED":
        candidates = _verification_candidates(entry, "internal_agent")
        if not candidates:
            reasons.append(f"{label}: INTERNALLY_VERIFIED needs an internal_agent verification")
            return reasons
        if all((c.get("verifier") or {}).get("identity") == entry.get("author") for c in candidates):
            reasons.append(f"{label}: INTERNALLY_VERIFIED verifier must differ from author")
        if isinstance(verified_by, dict) and verified_by.get("kind") != "internal_agent":
            reasons.append(f"{label}: verified_by.kind must be internal_agent")
    elif status == "INDEPENDENTLY_VERIFIED":
        candidates = _verification_candidates(entry, "external_auditor")
        if not candidates:
            reasons.append(f"{label}: INDEPENDENTLY_VERIFIED needs an external_auditor verification")
            return reasons
        if isinstance(verified_by, dict) and verified_by.get("kind") != "external_auditor":
            reasons.append(f"{label}: verified_by.kind must be external_auditor")
        if not any(
            any(_evidence_is_external(str(ev.get("path"))) for ev in c.get("evidence", []) if isinstance(ev, dict))
            for c in candidates
        ):
            reasons.append(f"{label}: INDEPENDENTLY_VERIFIED needs external evidence outside this repository")
    elif status == "GENERALIZED":
        if not entry.get("verifications"):
            reasons.append(f"{label}: GENERALIZED needs at least one verification object")
    return reasons


def _validate_generalized(entry: dict[str, Any], label: str) -> list[str]:
    authored = entry.get("authored_against")
    generalized = entry.get("generalized_on")
    reasons: list[str] = []
    if not isinstance(generalized, list) or not generalized:
        reasons.append(f"{label}: GENERALIZED needs generalized_on")
    if not isinstance(authored, list):
        reasons.append(f"{label}: authored_against must be a list")
        authored = []
    if not isinstance(generalized, list):
        generalized = []
    overlap = sorted(set(map(str, authored)) & set(map(str, generalized)))
    if overlap:
        reasons.append(f"{label}: GENERALIZED authored_against overlaps generalized_on: {', '.join(overlap)}")
    return reasons


def _validate_history_shape(entry: dict[str, Any], idx: int) -> list[str]:
    label = _entry_label(entry, idx)
    reasons: list[str] = []
    history = entry.get("history")
    if not isinstance(history, list):
        return [f"{label}: history must be a list"]
    for hidx, item in enumerate(history):
        if not isinstance(item, dict):
            reasons.append(f"{label}: history[{hidx}] must be an object")
            continue
        missing = sorted(REQUIRED_HISTORY_KEYS - set(item))
        if missing:
            reasons.append(f"{label}: history[{hidx}] missing keys: {', '.join(missing)}")
        status = item.get("status")
        if status == "VERIFIED":
            reasons.append(f"{label}: history[{hidx}] uses refused bare VERIFIED state")
        elif status not in STATUSES:
            reasons.append(f"{label}: history[{hidx}] has invalid status {status!r}")
        evidence = item.get("evidence")
        if not isinstance(evidence, list):
            reasons.append(f"{label}: history[{hidx}].evidence must be a list")
    return reasons


def _stale_scope_paths(root: Path, entry: dict[str, Any]) -> list[str]:
    stale: set[str] = set()
    for verification in entry.get("verifications") or []:
        if not isinstance(verification, dict):
            continue
        scope = verification.get("scope")
        recorded = verification.get("scope_blob_shas")
        if not isinstance(scope, list) or not isinstance(recorded, dict):
            continue
        current = _scope_blob_shas(root, [str(item) for item in scope])
        for path, old_blob in recorded.items():
            if current.get(path) != old_blob:
                stale.add(str(path))
        for path, new_blob in current.items():
            if recorded.get(path) != new_blob:
                stale.add(str(path))
    return sorted(stale)


def _validate_staleness(root: Path, entry: dict[str, Any], label: str) -> list[str]:
    if entry.get("status") not in VERIFIED_STATUSES:
        return []
    return [f"{label}: assurance stale: {path} changed" for path in _stale_scope_paths(root, entry)]


def validate_store(root: str | os.PathLike[str], store: dict[str, Any]) -> list[str]:
    """Validate the current object store without comparing it to a previous tree."""

    repo = _root_path(root)
    reasons: list[str] = []
    if store.get("schema_version") != SCHEMA_VERSION:
        reasons.append(f"registry/fixes.json schema_version must be {SCHEMA_VERSION}")
    if store.get("statuses") != list(STATUSES):
        reasons.append(f"registry/fixes.json statuses must be {list(STATUSES)!r}")

    raw_entries = store.get("entries")
    if not isinstance(raw_entries, list):
        return reasons + ["registry/fixes.json entries must be a list"]

    seen_finding: set[str] = set()
    seen_fix: set[str] = set()
    for idx, entry in enumerate(raw_entries):
        if not isinstance(entry, dict):
            reasons.append(f"entries[{idx}] must be an object")
            continue
        label = _entry_label(entry, idx)
        missing = sorted(REQUIRED_ENTRY_KEYS - set(entry))
        if missing:
            reasons.append(f"{label}: missing keys: {', '.join(missing)}")
        extra = sorted(set(entry) - REQUIRED_ENTRY_KEYS)
        if extra:
            reasons.append(f"{label}: unexpected keys: {', '.join(extra)}")

        finding_id = entry.get("finding_id")
        fix_id = entry.get("fix_id")
        if not isinstance(finding_id, str) or not finding_id:
            reasons.append(f"{label}: finding_id must be a non-empty string")
        elif finding_id in seen_finding:
            reasons.append(f"{label}: duplicate finding_id {finding_id}")
        else:
            seen_finding.add(finding_id)
        if not isinstance(fix_id, str) or not fix_id:
            reasons.append(f"{label}: fix_id must be a non-empty string")
        elif fix_id in seen_fix:
            reasons.append(f"{label}: duplicate fix_id {fix_id}")
        else:
            seen_fix.add(fix_id)

        kind = entry.get("kind")
        status = entry.get("status")
        if kind not in KINDS:
            reasons.append(f"{label}: kind must be one of {', '.join(KINDS)}")
        if status == "VERIFIED":
            reasons.append(f"{label}: refused bare VERIFIED status; use INTERNALLY_VERIFIED or INDEPENDENTLY_VERIFIED")
            continue
        if status not in STATUSES:
            reasons.append(f"{label}: invalid status {status!r}")
            continue
        if status == "SPECIFIED" and kind != "control":
            reasons.append(f"{label}: SPECIFIED is allowed only for controls")
        if kind == "fix" and status not in FIX_STATUSES:
            reasons.append(f"{label}: fix entries cannot use status {status}")

        evidence_dir = entry.get("evidence_dir")
        if evidence_dir:
            if not isinstance(evidence_dir, str) or not _path_is_repo_relative(evidence_dir):
                reasons.append(f"{label}: evidence_dir must be repo-relative")
            elif not (repo / evidence_dir).is_dir():
                reasons.append(f"{label}: evidence_dir does not exist: {_posix(evidence_dir)}")
        elif evidence_dir != "":
            reasons.append(f"{label}: evidence_dir must be a string")

        if not isinstance(entry.get("authored_against"), list):
            reasons.append(f"{label}: authored_against must be a list")
        if not isinstance(entry.get("generalized_on"), list):
            reasons.append(f"{label}: generalized_on must be a list")
        if entry.get("executable_evidence") is not None and not isinstance(entry.get("executable_evidence"), dict):
            reasons.append(f"{label}: executable_evidence must be an object or null")

        reasons.extend(_validate_verifier_obj(entry.get("verified_by"), f"{label}: verified_by", allow_null=True))
        verifications = entry.get("verifications")
        if not isinstance(verifications, list):
            reasons.append(f"{label}: verifications must be a list")
        else:
            for vidx, verification in enumerate(verifications):
                reasons.extend(_validate_verification(repo, entry, verification, vidx, label))

        reasons.extend(_validate_history_shape(entry, idx))
        if status == "SPECIFIED":
            if not _has_history_status(entry, "SPECIFIED"):
                reasons.append(f"{label}: SPECIFIED status needs SPECIFIED history")
            continue
        if _is_at_least(status, "LANDED"):
            landed = _latest_history(entry, "LANDED")
            if landed is None:
                reasons.append(f"{label}: {status} status needs LANDED history")
            else:
                reasons.extend(_validate_landed(repo, entry, landed, label))
        if status in VERIFIED_STATUSES:
            if not _has_history_status(entry, status):
                reasons.append(f"{label}: {status} status needs {status} history")
        if status == "GENERALIZED":
            if not _has_history_status(entry, "GENERALIZED"):
                reasons.append(f"{label}: GENERALIZED status needs GENERALIZED history")
            reasons.extend(_validate_generalized(entry, label))
        reasons.extend(_validate_status_verifications(repo, entry, label))
        reasons.extend(_validate_staleness(repo, entry, label))
    return reasons


def _transition_allowed(old_status: str, new_status: str) -> bool:
    return (old_status, new_status) in FORWARD_TRANSITIONS


def _reported_downgrade_allowed(reason: str) -> bool:
    return any(reason.startswith(prefix) for prefix in REPORTED_DOWNGRADE_PREFIXES)


def _new_history_entries(old_entry: dict[str, Any], new_entry: dict[str, Any]) -> list[dict[str, Any]]:
    old_keys = Counter(
        _history_key(item)
        for item in (old_entry.get("history") or [])
        if isinstance(item, dict)
    )
    out: list[dict[str, Any]] = []
    for item in new_entry.get("history") or []:
        if not isinstance(item, dict):
            continue
        key = _history_key(item)
        if old_keys[key]:
            old_keys[key] -= 1
        else:
            out.append(item)
    return out


def _validate_transition(
    root: Path,
    old_entry: dict[str, Any],
    new_entry: dict[str, Any],
) -> list[str]:
    label = str(new_entry.get("fix_id") or new_entry.get("finding_id"))
    old_status = old_entry.get("status")
    new_status = new_entry.get("status")
    if old_status == new_status:
        return []
    reasons: list[str] = []
    if old_status not in STATUSES or new_status not in STATUSES:
        return [f"{label}: cannot compare invalid statuses {old_status!r}->{new_status!r}"]
    candidates = [
        item for item in _new_history_entries(old_entry, new_entry)
        if item.get("status") == new_status
    ]
    if old_status in VERIFIED_STATUSES and new_status == "LANDED":
        if not candidates:
            return [f"{label}: status changed {old_status}->LANDED without matching new history entry"]
        if not all(str(item.get("reason") or "").startswith("assurance stale: ") for item in candidates):
            return [f"{label}: fallback to LANDED from {old_status} needs assurance stale history reason"]
        return reasons
    if not _transition_allowed(old_status, new_status):
        if new_status != "REPORTED":
            reasons.append(f"{label}: invalid status transition {old_status}->{new_status}")
            return reasons
    if not candidates:
        return [f"{label}: status changed {old_status}->{new_status} without matching new history entry"]
    history = candidates[-1]
    if new_status == "REPORTED":
        reason = str(history.get("reason") or "")
        if not reason.strip():
            reasons.append(f"{label}: downgrade to REPORTED needs a reason")
        elif not _reported_downgrade_allowed(reason):
            reasons.append(
                f"{label}: downgrade to REPORTED refused; reason must begin "
                f"{' or '.join(REPORTED_DOWNGRADE_PREFIXES)}"
            )
        return reasons
    if new_status == "LANDED":
        reasons.extend(_validate_landed(root, new_entry, history, label))
    elif new_status in VERIFIED_STATUSES:
        if not str(history.get("reason") or "").strip():
            reasons.append(f"{label}: {new_status} transition needs a reason")
    elif new_status == "GENERALIZED":
        reasons.extend(_validate_generalized(new_entry, label))
    return reasons


def _baseline_ref(root: Path) -> str | None:
    branch = _run_git(root, ["branch", "--show-current"], check=False).stdout.strip()
    if branch and branch != "main":
        proc = _run_git(root, ["merge-base", "HEAD", "origin/main"], check=False)
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    proc = _run_git(root, ["rev-parse", "--verify", "HEAD~1"], check=False)
    if proc.returncode == 0 and proc.stdout.strip():
        return "HEAD~1"
    return None


def describe_check_target(root: str | os.PathLike[str]) -> str:
    """Return the target line for the fix-state object-store check."""

    repo = _root_path(root)
    paths = [
        _posix(REGISTRY_PATH),
        _posix(LEDGER_PATH),
        "scripts/render_fix_ledger.py",
    ]
    for rel in (_posix(REGISTRY_PATH), _posix(LEDGER_PATH)):
        if not (repo / rel).is_file():
            return target_refusal("fixstate", f"missing required path: {rel}")
    ref = _baseline_ref(repo)
    refs = (ref,) if ref else ()
    try:
        return describe_target(repo, refs=refs, paths=paths, label="fixstate")
    except TargetUnresolvable as exc:
        return target_refusal("fixstate", str(exc))


def _load_store_from_tree(root: Path, ref: str) -> dict[str, Any] | None:
    proc = _run_git(root, ["show", f"{ref}:{_posix(REGISTRY_PATH)}"], check=False)
    if proc.returncode != 0:
        return None
    return json.loads(proc.stdout)


def check_transitions(root: str | os.PathLike[str], store: dict[str, Any]) -> list[str]:
    """Validate status edits from the baseline tree to the working tree."""

    repo = _root_path(root)
    ref = _baseline_ref(repo)
    if ref is None:
        return []
    old_store = _load_store_from_tree(repo, ref)
    if old_store is None:
        return []
    if old_store.get("schema_version") != store.get("schema_version"):
        return []
    old_by_fix = {
        entry.get("fix_id"): entry
        for entry in entries(old_store)
        if isinstance(entry, dict) and entry.get("fix_id")
    }
    reasons: list[str] = []
    for entry in entries(store):
        fix_id = entry.get("fix_id")
        old_entry = old_by_fix.get(fix_id)
        if old_entry is None:
            continue
        reasons.extend(_validate_transition(repo, old_entry, entry))
    return reasons


def _expected_views(root: Path) -> tuple[dict[str, Any], dict[str, str]]:
    from scripts import render_fix_ledger

    store = load(root)
    return render_fix_ledger.render_ledger(store), render_fix_ledger.render_readme_updates(root, store)


def check_generated_views(root: str | os.PathLike[str]) -> list[str]:
    """Refuse stale generated views of ``registry/fixes.json``."""

    repo = _root_path(root)
    reasons: list[str] = []
    try:
        expected_ledger, readme_updates = _expected_views(repo)
    except Exception as exc:
        return [f"generated view render failed: {type(exc).__name__}: {exc}"]

    ledger_path = repo / LEDGER_PATH
    try:
        current = _load_json(ledger_path)
    except (OSError, ValueError) as exc:
        return [f"{_display_path(LEDGER_PATH)} unreadable: {exc}"]
    if current != expected_ledger:
        reasons.append(f"{_display_path(LEDGER_PATH)} is stale; run python scripts/render_fix_ledger.py")

    for rel, want in readme_updates.items():
        path = repo / rel
        try:
            got = path.read_text(encoding="utf-8")
        except OSError as exc:
            reasons.append(f"{rel} unreadable: {exc}")
            continue
        if got != want:
            reasons.append(f"{rel} fix-state line is stale; run python scripts/render_fix_ledger.py")
    return reasons


def check(root: str | os.PathLike[str]) -> tuple[bool, list[str]]:
    """Validate the fix object store, generated views, and status transitions."""

    repo = _root_path(root)
    target_line = describe_check_target(repo)
    if target_line.startswith("TARGET fixstate: COULD-NOT-EXECUTE"):
        return False, [target_line]
    try:
        store = load(repo)
    except Exception as exc:
        return False, [f"fix object store could not be loaded: {exc}"]

    reasons: list[str] = []
    reasons.extend(validate_store(repo, store))
    reasons.extend(check_generated_views(repo))
    reasons.extend(check_transitions(repo, store))
    return not reasons, reasons


def refresh_stale(root: str | os.PathLike[str]) -> int:
    """Move stale verified claims back to LANDED and append fallback history."""

    repo = _root_path(root)
    store = load(repo)
    now = _utc_now()
    commit = _head_commit(repo)
    changed = 0
    for entry in entries(store):
        if entry.get("status") not in VERIFIED_STATUSES:
            continue
        stale = _stale_scope_paths(repo, entry)
        if not stale:
            continue
        entry["status"] = "LANDED"
        entry["verified_by"] = {"identity": None, "kind": None}
        for path in stale:
            entry.setdefault("history", []).append(
                {
                    "status": "LANDED",
                    "when_utc": now,
                    "by": "harness.fixstate --refresh-stale",
                    "commit": commit,
                    "evidence": [],
                    "reason": f"assurance stale: {path} changed",
                }
            )
        changed += 1
    if changed:
        _write_json(repo / REGISTRY_PATH, store)
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m harness.fixstate")
    parser.add_argument("--refresh-stale", action="store_true", help="fall stale verified entries back to LANDED")
    args = parser.parse_args(argv)
    root = _root_path(os.getcwd())
    if args.refresh_stale:
        changed = refresh_stale(root)
        suffix = "y" if changed == 1 else "ies"
        print(f"FIX-STATE: refresh-stale fallback entries written for {changed} entr{suffix}")
        return 0
    target_line = describe_check_target(root)
    print(target_line)
    if target_line.startswith("TARGET fixstate: COULD-NOT-EXECUTE"):
        print("FIX-STATE: COULD-NOT-EXECUTE")
        return 1
    ok, reasons = check(root)
    if ok:
        store = load(root)
        counts = Counter(entry["status"] for entry in entries(store))
        print(f"FIX-STATE: registry={_posix(REGISTRY_PATH)} entries={len(entries(store))}")
        print(
            "FIX-STATE: statuses "
            + ", ".join(f"{status}={counts.get(status, 0)}" for status in STATUSES)
        )
        print("FIX-STATE: generated views PASS")
        print("FIX-STATE: transitions PASS")
        print("FIX-STATE: PASS")
        return 0
    print("FIX-STATE: REFUSED")
    for reason in reasons:
        print(f"  - {reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
