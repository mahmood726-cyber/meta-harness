"""Four-state fix discipline for commit messages and evidence ledgers."""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys


REGISTRY_PATH = os.path.join("registry", "fixstate.json")
LEDGER_PATH = os.path.join("docs", "fix_ledger.json")
FIX_STATES = ("REPORTED", "LANDED", "VERIFIED", "GENERALIZED")
NON_FIX = "NOT-A-FIX"
TRAILER_RE = re.compile(r"^([A-Za-z0-9-]+):[ \t]*(.*)$")
ASSERTS_FIX_RE = re.compile(
    r"(?i)(\bfix(?:ed|es)?\b|\bcloses\b|\bclose\s+the\b|\bp0\b|\bgate\b|\brefus\w*)"
)
README_STATE_RE = re.compile(
    r"^\*\*Fix state.*:\s*(REPORTED|LANDED|VERIFIED|GENERALIZED)\b",
    re.MULTILINE,
)


def _root_path(root) -> str:
    return os.path.abspath(os.fspath(root))


def _posix(path: str) -> str:
    clean = path.replace("\\", "/")
    while clean.startswith("./"):
        clean = clean[2:]
    return clean


def _rel(root: str, path: str) -> str:
    return _posix(os.path.relpath(path, root))


def _run_git(root: str, args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return proc.stdout


def load(root) -> dict:
    """Load the fix-state registry from registry/fixstate.json under root."""
    with open(os.path.join(_root_path(root), REGISTRY_PATH), encoding="utf-8") as f:
        return json.load(f)


def parse_trailers(message: str) -> dict[str, list[str]]:
    """Parse contiguous git-style ``Key: value`` trailer lines at message end."""
    lines = message.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()

    block: list[tuple[str, str]] = []
    idx = len(lines) - 1
    while idx >= 0:
        match = TRAILER_RE.match(lines[idx])
        if not match:
            break
        block.append((match.group(1), match.group(2).strip()))
        idx -= 1

    trailers: dict[str, list[str]] = {}
    for key, value in reversed(block):
        trailers.setdefault(key, []).append(value)
    return trailers


def _values(trailers: dict[str, list[str]], key: str) -> list[str]:
    values: list[str] = []
    for found, found_values in trailers.items():
        if found.lower() == key.lower():
            values.extend(found_values)
    return values


def _list_items(values: list[str]) -> list[str]:
    items: list[str] = []
    for value in values:
        for item in re.split(r"[,;]", value):
            clean = item.strip()
            if clean:
                items.append(clean)
    return items


def _subject(message: str) -> str:
    for line in message.splitlines():
        if line.strip():
            return line.strip()
    return ""


def _path_is_repo_relative(path: str) -> bool:
    if not path or os.path.isabs(path):
        return False
    parts = [part for part in _posix(path).split("/") if part]
    return ".." not in parts


def _evidence_exists_in_parent(root: str, parent_tree: str, path: str) -> bool:
    spec = f"{parent_tree}:{_posix(path)}"
    proc = subprocess.run(
        ["git", "cat-file", "-e", spec],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode == 0


def _verified_violations(message: str, root=None, parent_tree=None) -> list[str]:
    trailers = parse_trailers(message)
    evidence = _values(trailers, "Fix-Evidence")
    verified_by = [value for value in _values(trailers, "Fix-Verified-By") if value.strip()]
    violations: list[str] = []

    if not evidence:
        violations.append("VERIFIED/GENERALIZED requires at least one Fix-Evidence: <path> trailer")
    if not verified_by:
        violations.append("VERIFIED/GENERALIZED requires non-empty Fix-Verified-By: <text>")

    if not evidence:
        return violations

    if root is None:
        violations.append("VERIFIED/GENERALIZED evidence cannot be checked without a repository root")
        return violations

    root = _root_path(root)
    parent = parent_tree or "HEAD"
    for raw_path in evidence:
        path = raw_path.strip()
        if not _path_is_repo_relative(path):
            violations.append(f"Fix-Evidence path must be repo-relative: {raw_path!r}")
            continue
        if not parent:
            violations.append(f"Fix-Evidence did not exist in a parent tree: {_posix(path)}")
            continue
        if not _evidence_exists_in_parent(root, parent, path):
            violations.append(
                f"Fix-Evidence did not exist in parent tree {parent}: {_posix(path)}"
            )
    return violations


def check_message(message: str, root=None, parent_tree=None) -> list[str]:
    """Return fix-state trailer violations for one commit message."""
    trailers = parse_trailers(message)
    state_values = [value.strip() for value in _values(trailers, "Fix-State")]
    allowed = set(FIX_STATES) | {NON_FIX}
    violations: list[str] = []
    state = state_values[0] if state_values else None

    if len(state_values) != 1:
        violations.append(f"exactly one Fix-State trailer required; found {len(state_values)}")
    elif state not in allowed:
        violations.append(
            "Fix-State must be one of "
            + ", ".join([*FIX_STATES, NON_FIX])
            + f"; got {state!r}"
        )

    if state == NON_FIX and ASSERTS_FIX_RE.search(_subject(message)):
        violations.append("this message asserts a fix; state it")

    if state in {"VERIFIED", "GENERALIZED"}:
        violations.extend(_verified_violations(message, root=root, parent_tree=parent_tree))

    if state == "GENERALIZED":
        authored_against = _list_items(_values(trailers, "Fix-Authored-Against"))
        generalized_on = _list_items(_values(trailers, "Fix-Generalized-On"))
        if not authored_against:
            violations.append("GENERALIZED requires Fix-Authored-Against: <list>")
        if not generalized_on:
            violations.append("GENERALIZED requires Fix-Generalized-On: <list>")
        overlap = sorted({item for item in authored_against} & {item for item in generalized_on})
        if overlap:
            violations.append(
                "GENERALIZED authored-against and generalized-on lists overlap: "
                + ", ".join(overlap)
            )

    return violations


def _first_parent(root: str, sha: str) -> str | None:
    parts = _run_git(root, ["rev-list", "--parents", "-n", "1", sha]).split()
    return parts[1] if len(parts) > 1 else None


def scan_commits(root, registry: dict) -> list[dict]:
    """Scan first-parent commits after registry['enforced_since']."""
    root = _root_path(root)
    enforced_since = registry.get("enforced_since")
    if enforced_since is None:
        return []
    shas = _run_git(
        root,
        ["rev-list", "--first-parent", "--reverse", f"{enforced_since}..HEAD"],
    ).splitlines()
    hits = []
    for sha in shas:
        message = _run_git(root, ["log", "-1", "--format=%B", sha])
        violations = check_message(message, root=root, parent_tree=_first_parent(root, sha))
        if violations:
            hits.append({"sha": sha, "violations": violations})
    return hits


def check_ledgers(root) -> list[str]:
    """Check evidence README state lines and docs/fix_ledger.json fix_state fields."""
    root = _root_path(root)
    reasons: list[str] = []

    for path in sorted(glob.glob(os.path.join(root, "evidence", "*", "README.md"))):
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as exc:
            reasons.append(f"{_rel(root, path)} unreadable: {exc}")
            continue
        if not README_STATE_RE.search(text):
            reasons.append(f"{_rel(root, path)} missing four-state Fix state line")

    ledger_path = os.path.join(root, LEDGER_PATH)
    try:
        ledger = json.load(open(ledger_path, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return reasons + [f"{LEDGER_PATH} unreadable: {exc}"]

    fixes = ledger.get("fixes")
    if not isinstance(fixes, list):
        return reasons + [f"{LEDGER_PATH}['fixes'] must be a list"]
    for idx, entry in enumerate(fixes):
        if not isinstance(entry, dict):
            reasons.append(f"{LEDGER_PATH} fixes[{idx}] must be an object")
            continue
        state = entry.get("fix_state")
        if state not in FIX_STATES:
            label = entry.get("class", "<unknown>")
            reasons.append(f"{LEDGER_PATH} fixes[{idx}] {label!r} missing valid fix_state")
    return reasons


def _registry_violations(registry: dict) -> list[str]:
    reasons: list[str] = []
    if registry.get("version") != 1:
        reasons.append(f"{REGISTRY_PATH} version must be 1")
    if registry.get("states") != list(FIX_STATES):
        reasons.append(f"{REGISTRY_PATH} states must be {list(FIX_STATES)!r}")
    if registry.get("non_fix") != NON_FIX:
        reasons.append(f"{REGISTRY_PATH} non_fix must be {NON_FIX!r}")
    return reasons


def check(root) -> tuple[bool, list[str]]:
    """Run registry, commit-message, and evidence-ledger checks."""
    root = _root_path(root)
    reasons: list[str] = []
    try:
        registry = load(root)
    except Exception as exc:
        return False, [f"fix-state registry could not be loaded: {exc}"]

    reasons.extend(_registry_violations(registry))

    try:
        for reason in check_ledgers(root):
            reasons.append(reason)
    except Exception as exc:
        reasons.append(f"fix-state ledger scan could not run: {exc}")

    try:
        for hit in scan_commits(root, registry):
            for violation in hit["violations"]:
                reasons.append(f"{hit['sha'][:12]}: {violation}")
    except Exception as exc:
        reasons.append(f"fix-state commit-message scan could not run: {exc}")

    return not reasons, reasons


def _message_check(root: str, path: str) -> int:
    try:
        message = open(path, encoding="utf-8").read()
    except OSError as exc:
        print(f"FIX-STATE: REFUSED -- commit message unreadable: {exc}")
        return 1

    violations = check_message(message, root=root, parent_tree="HEAD")
    if violations:
        print("FIX-STATE: REFUSED")
        for violation in violations:
            print(f"  - {violation}")
        return 1
    print("FIX-STATE: PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m harness.fixstate")
    parser.add_argument("--message", help="commit message file to check")
    args = parser.parse_args(argv)
    root = _root_path(os.getcwd())

    if args.message:
        return _message_check(root, args.message)

    try:
        registry = load(root)
        ledger_reasons = check_ledgers(root)
        commit_hits = scan_commits(root, registry)
    except Exception as exc:
        print(f"FIX-STATE: REFUSED -- {type(exc).__name__}: {exc}")
        return 1

    print(f"FIX-STATE: registry={REGISTRY_PATH} states={','.join(FIX_STATES)}")
    print(f"FIX-STATE: ledgers {'PASS' if not ledger_reasons else 'REFUSED'}")
    if registry.get("enforced_since") is None:
        print("FIX-STATE: commit-message scan PASS (not enforced yet)")
    else:
        print(
            "FIX-STATE: commit-message scan "
            f"{'PASS' if not commit_hits else 'REFUSED'} ({len(commit_hits)} violation(s))"
        )

    ok, reasons = check(root)
    if not ok:
        print("FIX-STATE: REFUSED")
        for reason in reasons:
            print(f"  - {reason}")
        return 1
    print("FIX-STATE: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
