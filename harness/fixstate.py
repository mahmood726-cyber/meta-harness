"""Orthogonal fix-state discipline for the machine-readable claim store.

Auditor correction, recorded as the controlling model: independence and
generalisation are different dimensions. A single ordinal ladder made the
representation stronger than the property, for example by making
``GENERALIZED`` read as if it implied ``INDEPENDENTLY_VERIFIED`` when a
generalisation was only internal. The registry therefore stores four
orthogonal fields instead: implementation, verification, scope, and computed
freshness. A claim reads, for example, LANDED / INDEPENDENT / INSTANCE /
CURRENT or LANDED / INTERNAL / CORPUS / CURRENT; none implies another.

Freshness is structural. It is recomputed from sealed dependencies at check
time and is never a history entry someone writes. The old ``--refresh-stale``
fallback went away for exactly that reason.
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

from harness import gitblob
from harness.target import TargetUnresolvable, describe_target, refusal as target_refusal


REGISTRY_PATH = Path("registry") / "fixes.json"
LEDGER_PATH = Path("docs") / "fix_ledger.json"
SCHEMA_VERSION = 3

IMPLEMENTATIONS = ("REPORTED", "LANDED")
CONTROL_IMPLEMENTATIONS = ("SPECIFIED", "REPORTED", "LANDED")
VERIFICATIONS = ("NONE", "INTERNAL", "INDEPENDENT")
SCOPES = ("INSTANCE", "REGRESSION_SET", "CORPUS", "HELD_OUT")
FRESHNESS = ("CURRENT", "STALE")
VERIFIER_KINDS = ("author", "internal_agent", "external_auditor")
KINDS = ("fix", "control", "result")

OLD_REFUSED_VALUES = {
    "INTERNALLY_VERIFIED",
    "INDEPENDENTLY_VERIFIED",
    "GENERALIZED",
    "VERIFIED",
}
OLD_REFUSED_KEYS = {"status", "statuses", "fix_state"}

REQUIRED_ENTRY_KEYS = {
    "finding_id",
    "fix_id",
    "title",
    "kind",
    "implementation",
    "verification",
    "scope",
    "author",
    "opened_utc",
    "evidence_dir",
    "events",
    "verified_by",
    "verifications",
    "authored_against",
    "generalized_on",
    "executable_evidence",
    "seal",
}
OPTIONAL_ENTRY_KEYS = {"note"}
REQUIRED_EVENT_KEYS = {
    "implementation",
    "verification",
    "scope",
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
    "scope_paths",
    "when_utc",
    "commit",
}
REQUIRED_VERIFIER_KEYS = {"identity", "kind"}
REQUIRED_SEAL_KEYS = {"sealed_utc", "commit", "dependencies", "configuration"}

SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

V2_TO_V3 = {
    "SPECIFIED": ("SPECIFIED", "NONE", "INSTANCE"),
    "REPORTED": ("REPORTED", "NONE", "INSTANCE"),
    "LANDED": ("LANDED", "NONE", "INSTANCE"),
    "INTERNALLY_VERIFIED": ("LANDED", "INTERNAL", "INSTANCE"),
    "INDEPENDENTLY_VERIFIED": ("LANDED", "INDEPENDENT", "INSTANCE"),
    "GENERALIZED": ("LANDED", "INTERNAL", "CORPUS"),
}

DEFAULT_CLAIM_MODULES = {
    "gate": ["harness/gate.py", "scripts/verify_all.py"],
    "grade": ["harness/grade.py"],
    "search": ["harness/acquisition.py", "harness/fetch.py"],
    "retrieval": ["harness/acquisition.py", "harness/fetch.py"],
    "architecture": ["harness/architecture_identity.py"],
    "artifact": ["scripts/production_record.py"],
    "ledger": ["harness/acquisition.py"],
    "ratchet": ["harness/honest_ratchet.py"],
    "compatibility": ["harness/compat.py"],
    "arm": ["harness/armcontrast.py"],
    "protocol": ["harness/protocol_compiler.py"],
    "invalidation": ["harness/invalidation.py"],
    "canonical": ["harness/claim.py"],
    "unit": ["harness/unit_of_analysis.py"],
}


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
    # The identity git would store (clean filter applied), never a sha1 of the raw worktree bytes:
    # 85 tracked files are CRLF on a Windows worktree and LF in the index, so raw-byte hashing made a
    # seal read CURRENT locally and STALE on CI (harness/gitblob.py).
    return gitblob.blob_sha(root, _posix(relpath))


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


def _scope_blob_shas(root: Path, scope: list[str]) -> dict[str, str | None]:
    records: dict[str, str | None] = {}
    for raw in scope:
        rel = _posix(str(raw))
        if not _path_is_repo_relative(rel):
            records[rel] = None
            continue
        path = root / rel
        if path.is_file():
            records[rel] = None  # filled by the batched call below
        elif path.is_dir():
            for child in sorted(p for p in path.rglob("*") if p.is_file()):
                records[_posix(child.relative_to(root))] = None
        else:
            records[rel] = None
    wanted = [rel for rel in records if (root / rel).is_file()]
    if wanted:
        records.update(gitblob.blob_shas(root, wanted))
    return records


def _verification_candidates(entry: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    return [
        item
        for item in (entry.get("verifications") or [])
        if isinstance(item, dict)
        and isinstance(item.get("verifier"), dict)
        and item["verifier"].get("kind") == kind
    ]


def _evidence_source_keys(obj: dict[str, Any]) -> list[str]:
    return [key for key in ("path", "url", "external_record") if obj.get(key)]


def _evidence_is_external(obj: dict[str, Any]) -> bool:
    return bool(obj.get("url") or obj.get("external_record"))


def _seal_dependencies(entry: dict[str, Any]) -> dict[str, str]:
    seal = entry.get("seal") if isinstance(entry.get("seal"), dict) else {}
    deps = seal.get("dependencies") if isinstance(seal, dict) else {}
    return deps if isinstance(deps, dict) else {}


def freshness(entry: dict[str, Any], root: str | os.PathLike[str]) -> tuple[str, list[str]]:
    """Return (CURRENT|STALE, moved_paths) from the entry's sealed dependencies."""

    repo = _root_path(root)
    moved: list[str] = []
    for raw, recorded in sorted(_seal_dependencies(entry).items()):
        rel = _posix(str(raw))
        if _is_generated_view(rel):
            # The evidence README carries the generated fix-state caption line and the index/twin
            # pages are rendered from it; sealing them makes every caption rewrite invalidate the
            # seal that the caption reports -- a seal must bind evidence, never its own rendering.
            continue
        current = _git_blob_sha(repo, rel) if _path_is_repo_relative(rel) else None
        if current != recorded:
            moved.append(rel)
    return ("STALE", moved) if moved else ("CURRENT", [])


def _is_generated_view(rel: str) -> bool:
    if not rel.startswith("docs/evidence/"):
        return False
    name = rel.rsplit("/", 1)[-1]
    return name in ("README.md", "README.md.html", "index.html") or name.endswith(".txt.html") or name.endswith(".json.html") or name.endswith(".md.html")


def freshness_state(entry: dict[str, Any], root: str | os.PathLike[str]) -> str:
    return freshness(entry, root)[0]


def _recursive_old_word_reasons(obj: Any, label: str, *, fix_kind: str | None = None) -> list[str]:
    reasons: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in OLD_REFUSED_KEYS:
                reasons.append(f"{label}: refused old authority key {key!r}")
            reasons.extend(_recursive_old_word_reasons(value, f"{label}.{key}", fix_kind=fix_kind))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            reasons.extend(_recursive_old_word_reasons(value, f"{label}[{idx}]", fix_kind=fix_kind))
    elif isinstance(obj, str):
        if obj in OLD_REFUSED_VALUES:
            reasons.append(f"{label}: refused old ladder word {obj!r}")
        if fix_kind != "control" and obj == "SPECIFIED":
            reasons.append(f"{label}: SPECIFIED is allowed only for controls")
        if re.search(r"\bstatus\b", obj):
            reasons.append(f"{label}: refused stored status wording")
    return reasons


def _validate_verifier_obj(verifier: Any, label: str, *, allow_null: bool) -> list[str]:
    if not isinstance(verifier, dict):
        return [f"{label}: verifier must be an object"]
    missing = sorted(REQUIRED_VERIFIER_KEYS - set(verifier))
    extra = sorted(set(verifier) - REQUIRED_VERIFIER_KEYS)
    reasons: list[str] = []
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
    reasons: list[str] = []
    source_keys = _evidence_source_keys(obj)
    if len(source_keys) != 1:
        reasons.append(f"{label}: evidence item must have exactly one of path, url, external_record")
    extra = sorted(set(obj) - {"path", "url", "external_record", "sha256", "commit", "signature"})
    if extra:
        reasons.append(f"{label}: evidence item unexpected keys: {', '.join(extra)}")

    if obj.get("path"):
        path = obj.get("path")
        if not isinstance(path, str) or not _path_is_repo_relative(path):
            reasons.append(f"{label}: evidence.path must be a repo-relative path")
        else:
            rel = _posix(path)
            full = root / rel
            if not full.is_file():
                reasons.append(f"{label}: evidence path missing in working tree: {rel}")
            elif obj.get("sha256"):
                observed = _sha256_file(full)
                sha = str(obj.get("sha256")).lower()
                if not SHA256_RE.fullmatch(sha):
                    reasons.append(f"{label}: evidence.sha256 must be 64 lowercase hex")
                elif observed != sha:
                    reasons.append(f"{label}: evidence sha256 mismatch for {rel}")
    for key in ("url", "external_record"):
        if key in obj and (not isinstance(obj.get(key), str) or not obj.get(key)):
            reasons.append(f"{label}: evidence.{key} must be a non-empty string")
    if "commit" in obj and (not isinstance(obj.get("commit"), str) or not obj.get("commit")):
        reasons.append(f"{label}: evidence.commit must be a non-empty string when present")
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
    else:
        for eidx, evidence_obj in enumerate(evidence):
            reasons.extend(_validate_evidence_object(root, evidence_obj, f"{vlabel}.evidence[{eidx}]"))
    for key in ("architecture_identity", "method", "when_utc"):
        if not isinstance(obj.get(key), str) or not obj.get(key):
            reasons.append(f"{vlabel}.{key} must be a non-empty string")
    commit = obj.get("commit")
    if commit and (not isinstance(commit, str) or not _commit_exists(root, commit)):
        reasons.append(f"{vlabel}.commit does not exist: {commit!r}")
    scope_paths = obj.get("scope_paths")
    if not isinstance(scope_paths, list) or not scope_paths:
        reasons.append(f"{vlabel}.scope_paths must be a non-empty list")
    else:
        for raw in scope_paths:
            if not _path_is_repo_relative(str(raw)):
                reasons.append(f"{vlabel}.scope_paths path must be repo-relative: {raw!r}")
    return reasons


def _validate_seal(root: Path, entry: dict[str, Any], label: str) -> list[str]:
    seal = entry.get("seal")
    if not isinstance(seal, dict):
        return [f"{label}: seal must be an object"]
    reasons: list[str] = []
    missing = sorted(REQUIRED_SEAL_KEYS - set(seal))
    extra = sorted(set(seal) - REQUIRED_SEAL_KEYS)
    if missing:
        reasons.append(f"{label}: seal missing keys: {', '.join(missing)}")
    if extra:
        reasons.append(f"{label}: seal unexpected keys: {', '.join(extra)}")
    if not isinstance(seal.get("sealed_utc"), str) or not seal.get("sealed_utc"):
        reasons.append(f"{label}: seal.sealed_utc must be a non-empty string")
    commit = seal.get("commit")
    if commit and (not isinstance(commit, str) or not _commit_exists(root, commit)):
        reasons.append(f"{label}: seal.commit does not exist: {commit!r}")
    deps = seal.get("dependencies")
    config = seal.get("configuration")
    if not isinstance(deps, dict):
        reasons.append(f"{label}: seal.dependencies must be an object")
        deps = {}
    if not isinstance(config, dict):
        reasons.append(f"{label}: seal.configuration must be an object")
        config = {}
    for raw, blob in (deps or {}).items():
        rel = _posix(str(raw))
        if not _path_is_repo_relative(rel):
            reasons.append(f"{label}: seal dependency path must be repo-relative: {raw!r}")
        if not isinstance(blob, str) or not SHA1_RE.fullmatch(blob):
            reasons.append(f"{label}: seal dependency {raw!r} must be a git blob sha")
    if entry.get("verification") != "NONE" and not deps and not config:
        reasons.append(f"{label}: verification {entry.get('verification')} needs a non-empty seal")
    return reasons


def _validate_event(obj: Any, idx: int, label: str) -> list[str]:
    elabel = f"{label}: events[{idx}]"
    if not isinstance(obj, dict):
        return [f"{elabel} must be an object"]
    reasons: list[str] = []
    missing = sorted(REQUIRED_EVENT_KEYS - set(obj))
    extra = sorted(set(obj) - REQUIRED_EVENT_KEYS)
    if missing:
        reasons.append(f"{elabel} missing keys: {', '.join(missing)}")
    if extra:
        reasons.append(f"{elabel} unexpected keys: {', '.join(extra)}")
    if obj.get("implementation") not in CONTROL_IMPLEMENTATIONS:
        reasons.append(f"{elabel}.implementation has invalid value {obj.get('implementation')!r}")
    if obj.get("verification") not in VERIFICATIONS:
        reasons.append(f"{elabel}.verification has invalid value {obj.get('verification')!r}")
    if obj.get("scope") not in SCOPES:
        reasons.append(f"{elabel}.scope has invalid value {obj.get('scope')!r}")
    if not isinstance(obj.get("evidence"), list):
        reasons.append(f"{elabel}.evidence must be a list")
    for key in ("when_utc", "by", "reason"):
        if key != "reason" and (not isinstance(obj.get(key), str) or not obj.get(key)):
            reasons.append(f"{elabel}.{key} must be a non-empty string")
        elif key == "reason" and not isinstance(obj.get(key), str):
            reasons.append(f"{elabel}.{key} must be a string")
    if "commit" in obj and not isinstance(obj.get("commit"), str):
        reasons.append(f"{elabel}.commit must be a string")
    return reasons


def _validate_executable_evidence_shape(entry: dict[str, Any], label: str) -> list[str]:
    evidence = entry.get("executable_evidence")
    if evidence is None:
        return []
    if not isinstance(evidence, dict):
        return [f"{label}: executable_evidence must be an object or null"]
    reasons: list[str] = []
    command = evidence.get("command")
    expected = evidence.get("expected_substring")
    if not isinstance(command, str) or not command.strip():
        reasons.append(f"{label}: executable_evidence.command must be a non-empty string")
    if not isinstance(expected, str) or not expected:
        reasons.append(f"{label}: executable_evidence.expected_substring must be a non-empty string")
    return reasons


def _validate_broader_scope(entry: dict[str, Any], label: str) -> list[str]:
    if entry.get("scope") not in {"CORPUS", "REGRESSION_SET", "HELD_OUT"}:
        return []
    evidence = entry.get("executable_evidence")
    if not isinstance(evidence, dict):
        return [f"{label}: scope {entry.get('scope')} needs executable_evidence naming the demonstrated topic list"]
    basis = " ".join(str(evidence.get(key, "")) for key in ("scope_basis", "topic_list", "heldout_register"))
    basis_lower = basis.lower()
    if entry.get("scope") == "HELD_OUT":
        if "held" not in basis_lower and "registry/heldout_sealed.json" not in basis_lower:
            return [f"{label}: HELD_OUT scope must name the sealed held-out register"]
    elif "named" not in basis_lower and "32 of 32" not in basis_lower:
        return [f"{label}: {entry.get('scope')} scope must name the demonstrated topic list"]
    return []


def _validate_claim_verification(root: Path, entry: dict[str, Any], label: str) -> list[str]:
    verification = entry.get("verification")
    verified_by = entry.get("verified_by")
    reasons: list[str] = []
    if verification == "NONE":
        if isinstance(verified_by, dict) and (
            verified_by.get("identity") is not None or verified_by.get("kind") is not None
        ):
            reasons.append(f"{label}: verification NONE must use verified_by identity=null, kind=null")
        return reasons

    if entry.get("implementation") != "LANDED":
        reasons.append(f"{label}: verification {verification} requires implementation LANDED")

    if verification == "INTERNAL":
        candidates = _verification_candidates(entry, "internal_agent")
        if not candidates:
            reasons.append(f"{label}: verification INTERNAL needs an internal_agent verification")
            return reasons
        if all((c.get("verifier") or {}).get("identity") == entry.get("author") for c in candidates):
            reasons.append(f"{label}: verification INTERNAL verifier must differ from author")
        if isinstance(verified_by, dict) and verified_by.get("kind") != "internal_agent":
            reasons.append(f"{label}: verified_by.kind must be internal_agent")
    elif verification == "INDEPENDENT":
        candidates = _verification_candidates(entry, "external_auditor")
        if not candidates:
            reasons.append(f"{label}: verification INDEPENDENT needs an external_auditor verification")
            return reasons
        if isinstance(verified_by, dict) and verified_by.get("kind") != "external_auditor":
            reasons.append(f"{label}: verified_by.kind must be external_auditor")
        if not any(
            any(_evidence_is_external(ev) for ev in c.get("evidence", []) if isinstance(ev, dict))
            for c in candidates
        ):
            reasons.append(f"{label}: verification INDEPENDENT needs external evidence outside this repository")
    return reasons


def validate_store(root: str | os.PathLike[str], store: dict[str, Any]) -> list[str]:
    """Validate the v3 object store without comparing it to a previous tree."""

    repo = _root_path(root)
    reasons: list[str] = []
    if store.get("schema_version") != SCHEMA_VERSION:
        reasons.append(f"registry/fixes.json schema_version must be {SCHEMA_VERSION}")
    if store.get("implementations") != list(CONTROL_IMPLEMENTATIONS):
        reasons.append(f"registry/fixes.json implementations must be {list(CONTROL_IMPLEMENTATIONS)!r}")
    if store.get("verification_levels") != list(VERIFICATIONS):
        reasons.append(f"registry/fixes.json verification_levels must be {list(VERIFICATIONS)!r}")
    if store.get("scopes") != list(SCOPES):
        reasons.append(f"registry/fixes.json scopes must be {list(SCOPES)!r}")
    if "statuses" in store:
        reasons.append("registry/fixes.json must not store v2 statuses")

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
        reasons.extend(_recursive_old_word_reasons(entry, label, fix_kind=str(entry.get("kind"))))

        missing = sorted(REQUIRED_ENTRY_KEYS - set(entry))
        if missing:
            reasons.append(f"{label}: missing keys: {', '.join(missing)}")
        extra = sorted(set(entry) - REQUIRED_ENTRY_KEYS - OPTIONAL_ENTRY_KEYS)
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
        implementation = entry.get("implementation")
        verification = entry.get("verification")
        scope = entry.get("scope")
        if kind not in KINDS:
            reasons.append(f"{label}: kind must be one of {', '.join(KINDS)}")
        if kind == "control":
            if implementation not in CONTROL_IMPLEMENTATIONS:
                reasons.append(f"{label}: invalid implementation {implementation!r}")
        elif implementation not in IMPLEMENTATIONS:
            reasons.append(f"{label}: implementation must be REPORTED or LANDED")
        if implementation == "SPECIFIED" and kind != "control":
            reasons.append(f"{label}: SPECIFIED is allowed only for controls")
        if verification not in VERIFICATIONS:
            reasons.append(f"{label}: verification must be one of {', '.join(VERIFICATIONS)}")
        if scope not in SCOPES:
            reasons.append(f"{label}: scope must be one of {', '.join(SCOPES)}")

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

        reasons.extend(_validate_verifier_obj(entry.get("verified_by"), f"{label}: verified_by", allow_null=True))
        reasons.extend(_validate_executable_evidence_shape(entry, label))
        reasons.extend(_validate_broader_scope(entry, label))
        reasons.extend(_validate_seal(repo, entry, label))

        events = entry.get("events")
        if not isinstance(events, list):
            reasons.append(f"{label}: events must be a list")
        else:
            for eidx, event in enumerate(events):
                reasons.extend(_validate_event(event, eidx, label))

        verifications = entry.get("verifications")
        if not isinstance(verifications, list):
            reasons.append(f"{label}: verifications must be a list")
        else:
            for vidx, verification_obj in enumerate(verifications):
                reasons.extend(_validate_verification(repo, entry, verification_obj, vidx, label))
        reasons.extend(_validate_claim_verification(repo, entry, label))
    return reasons


def _event_key(event: dict[str, Any]) -> str:
    return json.dumps(event, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _new_events(old_entry: dict[str, Any], new_entry: dict[str, Any]) -> list[dict[str, Any]]:
    old_keys = Counter(_event_key(item) for item in (old_entry.get("events") or []) if isinstance(item, dict))
    out: list[dict[str, Any]] = []
    for item in new_entry.get("events") or []:
        if not isinstance(item, dict):
            continue
        key = _event_key(item)
        if old_keys[key]:
            old_keys[key] -= 1
        else:
            out.append(item)
    return out


def _transition_reasons(root: Path, old_entry: dict[str, Any], new_entry: dict[str, Any]) -> list[str]:
    label = str(new_entry.get("fix_id") or new_entry.get("finding_id"))
    changed = [
        key
        for key in ("implementation", "verification", "scope")
        if old_entry.get(key) != new_entry.get(key)
    ]
    if not changed:
        return []
    events = _new_events(old_entry, new_entry)
    if not events:
        return [f"{label}: {', '.join(changed)} changed without a matching new event"]
    latest = events[-1]
    reasons: list[str] = []
    for key in changed:
        if latest.get(key) != new_entry.get(key):
            reasons.append(f"{label}: transition event does not record new {key}")
    if new_entry.get("implementation") == "LANDED":
        commit = latest.get("commit")
        if not _commit_exists(root, str(commit)):
            reasons.append(f"{label}: LANDED transition needs an existing commit")
    if new_entry.get("verification") != "NONE" and not str(latest.get("reason") or "").strip():
        reasons.append(f"{label}: verification transition needs a reason")
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
    """Validate v3 field edits from the baseline tree to the working tree."""

    repo = _root_path(root)
    ref = _baseline_ref(repo)
    if ref is None:
        return []
    old_store = _load_store_from_tree(repo, ref)
    if old_store is None or old_store.get("schema_version") != store.get("schema_version"):
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
        reasons.extend(_transition_reasons(repo, old_entry, entry))
    return reasons


def _expected_views(root: Path) -> tuple[dict[str, Any], dict[str, str]]:
    from scripts import render_fix_ledger
    from scripts import rewrite_fixstate_lines

    store = load(root)
    return render_fix_ledger.render_ledger(store, root=root), rewrite_fixstate_lines.render_readme_updates(root, store)


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
            reasons.append(f"{rel} fix-state line is stale; run python scripts/rewrite_fixstate_lines.py")
    return reasons


def check(root: str | os.PathLike[str]) -> tuple[bool, list[str]]:
    """Validate the object store, generated views, and v3 field transitions."""

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


def _sanitize_v2_reason(text: Any) -> str:
    out = "" if text is None else str(text)
    replacements = {
        "INTERNALLY_VERIFIED": "INTERNAL",
        "INDEPENDENTLY_VERIFIED": "INDEPENDENT",
        "GENERALIZED": "CORPUS-scoped",
        "VERIFIED": "verified",
        "status": "field",
    }
    for old, new in replacements.items():
        out = out.replace(old, new)
    return out


def _v2_to_fields(value: str, kind: str, entry: dict[str, Any]) -> tuple[str, str, str]:
    if value == "GENERALIZED":
        verification = "INDEPENDENT" if _verification_candidates(entry, "external_auditor") else "INTERNAL"
        return "LANDED", verification, "CORPUS"
    implementation, verification, scope = V2_TO_V3[value]
    if implementation == "SPECIFIED" and kind != "control":
        implementation = "REPORTED"
    if value == "LANDED" and verification == "NONE" and _fell_back_from_verified(entry):
        # v2 demoted a verified claim to LANDED procedurally ("assurance stale: <path> changed") and
        # dropped its verifier. In v3 freshness is computed from the seal, so the honest encoding is
        # the verification it actually had (INTERNAL, or INDEPENDENT if an external auditor is
        # recorded) with a STALE freshness -- not NONE, which would hide both the verification and
        # the staleness the auditor asked to see.
        verification = "INDEPENDENT" if _verification_candidates(entry, "external_auditor") else "INTERNAL"
    return implementation, verification, scope


def _fell_back_from_verified(entry: dict[str, Any]) -> bool:
    """True when a v2 entry is LANDED only because an 'assurance stale' fallback demoted it from a
    verified status, and it still carries a verification object from a non-author verifier."""
    history = [item for item in (entry.get("history") or []) if isinstance(item, dict)]
    if not any(str(item.get("reason") or "").startswith("assurance stale:") for item in history):
        return False
    if not any(item.get("status") in ("INTERNALLY_VERIFIED", "INDEPENDENTLY_VERIFIED", "GENERALIZED") for item in history):
        return False
    return bool(_verification_candidates(entry, "internal_agent") or _verification_candidates(entry, "external_auditor"))


def _convert_v2_event(item: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any] | None:
    reason = str(item.get("reason") or "")
    if reason.startswith("assurance stale:"):
        return None
    old = item.get("status")
    if old not in V2_TO_V3:
        old = "REPORTED"
    implementation, verification, scope = _v2_to_fields(str(old), str(entry.get("kind")), entry)
    return {
        "implementation": implementation,
        "verification": verification,
        "scope": scope,
        "when_utc": str(item.get("when_utc") or _utc_now()),
        "by": _sanitize_v2_reason(item.get("by") or "unknown"),
        "commit": str(item.get("commit") or ""),
        "evidence": [str(path) for path in (item.get("evidence") or [])],
        "reason": _sanitize_v2_reason(reason),
    }


def _convert_v2_verification(obj: dict[str, Any]) -> dict[str, Any]:
    method = _sanitize_v2_reason(obj.get("method") or "migration from v2 ladder")
    if method == "migration from legacy verified history; architecture identity recorded at migration":
        method = "migration from v2 ladder; architecture identity recorded at migration"
    return {
        "claim_id": obj.get("claim_id"),
        "verifier": obj.get("verifier"),
        "evidence": obj.get("evidence") or [],
        "architecture_identity": obj.get("architecture_identity") or "unknown-v2-migration",
        "method": method,
        "scope_paths": [_posix(path) for path in (obj.get("scope") or [])],
        "when_utc": obj.get("when_utc") or _utc_now(),
        "commit": obj.get("commit") or "",
    }


def _seal_from_v2(root: Path, entry: dict[str, Any], now: str, head: str) -> dict[str, Any]:
    dependencies: dict[str, str] = {}
    for verification in entry.get("verifications") or []:
        if not isinstance(verification, dict):
            continue
        recorded = verification.get("scope_blob_shas")
        if isinstance(recorded, dict) and recorded:
            for raw, blob in recorded.items():
                rel = _posix(str(raw))
                if isinstance(blob, str) and SHA1_RE.fullmatch(blob):
                    dependencies[rel] = blob
            if dependencies:
                break
    if not dependencies:
        evidence_dir = entry.get("evidence_dir")
        if isinstance(evidence_dir, str) and evidence_dir:
            dependencies.update(
                {
                    rel: blob
                    for rel, blob in _scope_blob_shas(root, [evidence_dir]).items()
                    if isinstance(blob, str)
                }
            )
    if not dependencies:
        text = " ".join(str(entry.get(key, "")) for key in ("fix_id", "title", "evidence_dir")).lower()
        candidates: list[str] = []
        for token, paths in DEFAULT_CLAIM_MODULES.items():
            if token in text:
                candidates.extend(paths)
        command = (entry.get("executable_evidence") or {}).get("command") if isinstance(entry.get("executable_evidence"), dict) else ""
        for rel in re.findall(r"(?:harness|scripts|tests)/[A-Za-z0-9_./-]+\.py", str(command).replace("\\", "/")):
            candidates.append(rel)
        if "harness.architecture_identity" in str(command):
            candidates.append("harness/architecture_identity.py")
        if "tests/test_acquisition.py" in str(command):
            candidates.append("tests/test_acquisition.py")
        if "tests/test_prospective.py" in str(command):
            candidates.append("tests/test_prospective.py")
        for rel, blob in _scope_blob_shas(root, sorted(set(candidates))).items():
            if isinstance(blob, str):
                dependencies[rel] = blob
    latest_commit = ""
    for item in reversed(entry.get("history") or []):
        if isinstance(item, dict) and item.get("commit"):
            latest_commit = str(item.get("commit"))
            break
    return {
        "sealed_utc": now,
        "commit": latest_commit or head,
        "dependencies": dict(sorted(dependencies.items())),
        "configuration": {"schema": "fixes-v3"},
    }


def migrate_v2_to_v3(root: str | os.PathLike[str]) -> dict[str, Any]:
    """Rewrite ``registry/fixes.json`` from schema v2 to schema v3."""

    repo = _root_path(root)
    store = load(repo)
    version = store.get("schema_version")
    if version == SCHEMA_VERSION:
        raise RuntimeError("registry/fixes.json is already schema v3")
    if version != 2:
        raise RuntimeError(f"cannot migrate schema_version {version!r}; expected 2")
    now = _utc_now()
    head = _head_commit(repo)
    new_entries: list[dict[str, Any]] = []
    for entry in entries(store):
        old = entry.get("status")
        if old not in V2_TO_V3:
            raise RuntimeError(f"{entry.get('fix_id')}: unsupported v2 status {old!r}")
        implementation, verification, scope = _v2_to_fields(str(old), str(entry.get("kind")), entry)
        verified_by = {"identity": None, "kind": None}
        if verification != "NONE":
            verified_by = entry.get("verified_by") or verified_by
            if not (isinstance(verified_by, dict) and verified_by.get("kind")):
                # the v2 fallback nulled verified_by; recover it from the verification object
                kind = "external_auditor" if verification == "INDEPENDENT" else "internal_agent"
                cands = _verification_candidates(entry, kind)
                if cands:
                    verified_by = dict(cands[-1]["verifier"])
        events = [
            converted
            for item in (entry.get("history") or [])
            if isinstance(item, dict)
            for converted in [_convert_v2_event(item, entry)]
            if converted is not None
        ]
        if not events:
            events = [
                {
                    "implementation": implementation,
                    "verification": verification,
                    "scope": scope,
                    "when_utc": now,
                    "by": "harness.fixstate --migrate-v2-to-v3",
                    "commit": head if implementation == "LANDED" else "",
                    "evidence": [],
                    "reason": "schema v3 migration",
                }
            ]
        new_entries.append(
            {
                "finding_id": entry.get("finding_id"),
                "fix_id": entry.get("fix_id"),
                "title": entry.get("title"),
                "kind": entry.get("kind"),
                "implementation": implementation,
                "verification": verification,
                "scope": scope,
                "author": entry.get("author"),
                "opened_utc": entry.get("opened_utc"),
                "evidence_dir": entry.get("evidence_dir", ""),
                "events": events,
                "verified_by": verified_by,
                "verifications": [
                    _convert_v2_verification(item)
                    for item in (entry.get("verifications") or [])
                    if isinstance(item, dict)
                ],
                "authored_against": entry.get("authored_against") or [],
                "generalized_on": entry.get("generalized_on") or [],
                "executable_evidence": entry.get("executable_evidence"),
                "seal": _seal_from_v2(repo, entry, now, head),
            }
        )
    new_store = {
        "schema_version": SCHEMA_VERSION,
        "implementations": list(CONTROL_IMPLEMENTATIONS),
        "verification_levels": list(VERIFICATIONS),
        "scopes": list(SCOPES),
        "freshness": list(FRESHNESS),
        "entries": new_entries,
    }
    _write_json(repo / REGISTRY_PATH, new_store)
    return new_store


def _summary_line(store: dict[str, Any], root: Path) -> str:
    by_impl = Counter(entry.get("implementation") for entry in entries(store))
    by_verification = Counter(entry.get("verification") for entry in entries(store))
    by_scope = Counter(entry.get("scope") for entry in entries(store))
    by_freshness = Counter(freshness_state(entry, root) for entry in entries(store))
    return (
        "implementations "
        + ", ".join(f"{value}={by_impl.get(value, 0)}" for value in CONTROL_IMPLEMENTATIONS)
        + "; verifications "
        + ", ".join(f"{value}={by_verification.get(value, 0)}" for value in VERIFICATIONS)
        + "; scopes "
        + ", ".join(f"{value}={by_scope.get(value, 0)}" for value in SCOPES)
        + "; freshness "
        + ", ".join(f"{value}={by_freshness.get(value, 0)}" for value in FRESHNESS)
    )


def _raw_bytes_blob_sha(path: Path) -> str | None:
    """The pre-2026-09-14 identity: sha1 over "blob <len>\\0<raw worktree bytes>" -- CRLF-dependent."""
    if not path.is_file():
        return None
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def rehash_seals(root: str | os.PathLike[str]) -> tuple[int, list[str]]:
    """Convert seal dependencies recorded with the raw-byte sha1 into git-normalised blob ids.

    Only a dependency whose recorded value equals the raw-byte sha1 of the CURRENT file is converted
    (the bytes are unchanged; only the hashing method moves). Anything else is left as recorded and
    reported -- this is a conversion of identity method, never a re-seal of changed content.
    """
    repo = _root_path(root)
    store = load(repo)
    changed = 0
    refused: list[str] = []
    for entry in entries(store):
        deps = _seal_dependencies(entry)
        if not deps:
            continue
        rels = [_posix(str(raw)) for raw in deps]
        normalised = gitblob.blob_shas(repo, [rel for rel in rels if _path_is_repo_relative(rel)])
        for rel, recorded in list(deps.items()):
            rel = _posix(str(rel))
            if not _path_is_repo_relative(rel):
                continue
            new = normalised.get(rel)
            if new is None or new == recorded:
                continue
            if _raw_bytes_blob_sha(repo / rel) == recorded:
                deps[rel] = new
                changed += 1
            else:
                refused.append(f"{_entry_label(entry, 0)}: {rel} recorded {recorded[:12]} is neither the raw-byte nor the normalised identity of the current file; left as recorded (STALE)")
        entry["seal"]["dependencies"] = dict(sorted(deps.items()))
    _write_json(repo / REGISTRY_PATH, store)
    return changed, refused


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m harness.fixstate")
    parser.add_argument("--migrate-v2-to-v3", action="store_true", help="rewrite registry/fixes.json to schema v3")
    parser.add_argument("--rehash-seals", action="store_true",
                        help="convert seals recorded as raw-byte sha1 to git-normalised blob ids where the bytes are unchanged")
    args = parser.parse_args(argv)
    root = _root_path(os.getcwd())
    if args.rehash_seals:
        changed, refused = rehash_seals(root)
        print(f"FIX-STATE: reseal converted={changed} refused={len(refused)}")
        for item in refused:
            print("  - " + item)
        return 0 if not refused else 1
    if args.migrate_v2_to_v3:
        try:
            store = migrate_v2_to_v3(root)
        except RuntimeError as exc:
            print(f"FIX-STATE: migration REFUSED - {exc}")
            return 1
        print(f"FIX-STATE: migrated registry={_posix(REGISTRY_PATH)} entries={len(entries(store))}")
        print("FIX-STATE: " + _summary_line(store, root))
        return 0
    target_line = describe_check_target(root)
    print(target_line)
    if target_line.startswith("TARGET fixstate: COULD-NOT-EXECUTE"):
        print("FIX-STATE: COULD-NOT-EXECUTE")
        return 1
    ok, reasons = check(root)
    if ok:
        store = load(root)
        print(f"FIX-STATE: registry={_posix(REGISTRY_PATH)} entries={len(entries(store))}")
        print("FIX-STATE: " + _summary_line(store, root))
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
