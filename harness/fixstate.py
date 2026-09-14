"""Fix-state discipline for the machine-readable fix object store."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REGISTRY_PATH = Path("registry") / "fixes.json"
LEDGER_PATH = Path("docs") / "fix_ledger.json"
STATUSES = ("SPECIFIED", "REPORTED", "LANDED", "VERIFIED", "GENERALIZED")
FIX_STATUSES = ("REPORTED", "LANDED", "VERIFIED", "GENERALIZED")
KINDS = ("fix", "control")
FORWARD_TRANSITIONS = {
    ("SPECIFIED", "LANDED"),
    ("REPORTED", "LANDED"),
    ("LANDED", "VERIFIED"),
    ("VERIFIED", "GENERALIZED"),
}
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


def _root_path(root: str | os.PathLike[str]) -> Path:
    return Path(root).resolve()


def _posix(path: str | os.PathLike[str]) -> str:
    clean = os.fspath(path).replace("\\", "/")
    while clean.startswith("./"):
        clean = clean[2:]
    return clean


def _display_path(path: Path) -> str:
    return _posix(path)


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


def _commit_exists(root: Path, commit: str) -> bool:
    if not isinstance(commit, str) or not commit.strip():
        return False
    proc = _run_git(root, ["cat-file", "-e", f"{commit}^{{commit}}"], check=False)
    return proc.returncode == 0


def _first_parent(root: Path, commit: str) -> str | None:
    proc = _run_git(root, ["rev-list", "--parents", "-n", "1", commit], check=False)
    if proc.returncode != 0:
        return None
    parts = proc.stdout.split()
    return parts[1] if len(parts) > 1 else None


def _path_is_repo_relative(path: str) -> bool:
    if not isinstance(path, str) or not path or os.path.isabs(path):
        return False
    parts = [part for part in _posix(path).split("/") if part]
    return bool(parts) and ".." not in parts


def _path_exists_in_tree(root: Path, treeish: str, path: str) -> bool:
    proc = _run_git(root, ["cat-file", "-e", f"{treeish}:{_posix(path)}"], check=False)
    return proc.returncode == 0


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


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


def _history_entries_for(entry: dict[str, Any], status: str) -> list[dict[str, Any]]:
    return [
        item
        for item in (entry.get("history") or [])
        if isinstance(item, dict) and item.get("status") == status
    ]


def _has_history_status(entry: dict[str, Any], status: str) -> bool:
    return _latest_history(entry, status) is not None


def _is_at_least(status: str, threshold: str) -> bool:
    order = {value: idx for idx, value in enumerate(STATUSES)}
    return order[status] >= order[threshold]


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


def _validate_verified_current(root: Path, entry: dict[str, Any], history: dict[str, Any], label: str) -> list[str]:
    reasons: list[str] = []
    if history.get("by") == entry.get("author"):
        reasons.append(f"{label}: VERIFIED by must differ from author")
    evidence = history.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        reasons.append(f"{label}: VERIFIED history needs evidence paths")
        return reasons
    for raw_path in evidence:
        path = str(raw_path)
        if not _path_is_repo_relative(path):
            reasons.append(f"{label}: evidence path must be repo-relative: {raw_path!r}")
            continue
        if not (root / path).exists():
            reasons.append(f"{label}: evidence path missing in working tree: {_posix(path)}")
    commit = history.get("commit")
    if commit and not _commit_exists(root, commit):
        reasons.append(f"{label}: VERIFIED history commit does not exist: {commit!r}")
    return reasons


def _validate_verified_transition(root: Path, entry: dict[str, Any], history: dict[str, Any], label: str) -> list[str]:
    reasons = _validate_verified_current(root, entry, history, label)
    commit = history.get("commit")
    if not isinstance(commit, str) or not commit.strip() or not _commit_exists(root, commit):
        reasons.append(f"{label}: VERIFIED transition commit must exist")
        return reasons
    parent = _first_parent(root, commit)
    if parent is None:
        reasons.append(f"{label}: VERIFIED transition commit has no parent")
        return reasons
    for raw_path in history.get("evidence") or []:
        path = str(raw_path)
        if _path_is_repo_relative(path) and not _path_exists_in_tree(root, parent, path):
            reasons.append(
                f"{label}: VERIFIED evidence did not exist in parent tree {parent[:12]}: {_posix(path)}"
            )
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
        if status not in STATUSES:
            reasons.append(f"{label}: history[{hidx}] has invalid status {status!r}")
        evidence = item.get("evidence")
        if not isinstance(evidence, list):
            reasons.append(f"{label}: history[{hidx}].evidence must be a list")
    return reasons


def validate_store(root: str | os.PathLike[str], store: dict[str, Any]) -> list[str]:
    """Validate the current object store without comparing it to a previous tree."""

    repo = _root_path(root)
    reasons: list[str] = []
    if store.get("schema_version") != 1:
        reasons.append("registry/fixes.json schema_version must be 1")
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
        if _is_at_least(status, "VERIFIED"):
            verified = _latest_history(entry, "VERIFIED")
            if verified is None:
                reasons.append(f"{label}: {status} status needs VERIFIED history")
            else:
                reasons.extend(_validate_verified_current(repo, entry, verified, label))
        if status == "GENERALIZED":
            if not _has_history_status(entry, "GENERALIZED"):
                reasons.append(f"{label}: GENERALIZED status needs GENERALIZED history")
            reasons.extend(_validate_generalized(entry, label))
    return reasons


def _transition_allowed(old_status: str, new_status: str) -> bool:
    if new_status == "REPORTED":
        return True
    return (old_status, new_status) in FORWARD_TRANSITIONS


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
    if not _transition_allowed(old_status, new_status):
        reasons.append(f"{label}: invalid status transition {old_status}->{new_status}")
        return reasons
    candidates = [
        item for item in _new_history_entries(old_entry, new_entry)
        if item.get("status") == new_status
    ]
    if not candidates:
        return [f"{label}: status changed {old_status}->{new_status} without matching new history entry"]
    history = candidates[-1]
    if new_status == "REPORTED":
        if not str(history.get("reason") or "").strip():
            reasons.append(f"{label}: downgrade to REPORTED needs a reason")
        return reasons
    if new_status == "LANDED":
        reasons.extend(_validate_landed(root, new_entry, history, label))
    elif new_status == "VERIFIED":
        reasons.extend(_validate_verified_transition(root, new_entry, history, label))
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
    try:
        store = load(repo)
    except Exception as exc:
        return False, [f"fix object store could not be loaded: {exc}"]

    reasons: list[str] = []
    reasons.extend(validate_store(repo, store))
    reasons.extend(check_generated_views(repo))
    reasons.extend(check_transitions(repo, store))
    return not reasons, reasons


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m harness.fixstate")
    parser.parse_args(argv)
    root = _root_path(os.getcwd())
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
