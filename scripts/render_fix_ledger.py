"""Render generated fix-state views from registry/fixes.json.

The registry is the authority. ``docs/fix_ledger.json`` and the first fix-state
line in each evidence README are generated views and must not be hand-edited.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = Path("registry") / "fixes.json"
LEDGER_PATH = Path("docs") / "fix_ledger.json"
README_STATE_RE = re.compile(
    r"^\*\*Fix state \((?:four|five)-state rule\): .*?(?:\*\*.*)?$",
    re.MULTILINE,
)


def _posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def load_store(root: Path = ROOT) -> dict[str, Any]:
    return json.loads((root / REGISTRY_PATH).read_text(encoding="utf-8"))


def _latest_history(entry: dict[str, Any], status: str) -> dict[str, Any] | None:
    for item in reversed(entry.get("history") or []):
        if isinstance(item, dict) and item.get("status") == status:
            return item
    return None


def _entry_evidence(entry: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for item in entry.get("history") or []:
        if not isinstance(item, dict):
            continue
        for path in item.get("evidence") or []:
            if path not in paths:
                paths.append(path)
    return paths


def _verification_evidence_paths(entry: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for verification in entry.get("verifications") or []:
        if not isinstance(verification, dict):
            continue
        for evidence in verification.get("evidence") or []:
            if not isinstance(evidence, dict):
                continue
            path = evidence.get("path")
            if path and path not in paths:
                paths.append(path)
    return paths


def _view_entry(entry: dict[str, Any]) -> dict[str, Any]:
    landed = _latest_history(entry, "LANDED")
    latest = (entry.get("history") or [{}])[-1]
    out: dict[str, Any] = {
        "finding_id": entry["finding_id"],
        "fix_id": entry["fix_id"],
        "kind": entry["kind"],
        "class": entry["title"],
        "fix_state": entry["status"],
        "state": entry["status"],
        "where": (landed or latest).get("commit", ""),
        "evidence_dir": entry.get("evidence_dir", ""),
        "evidence": _entry_evidence(entry),
        "verified_by": entry.get("verified_by"),
        "verifications": entry.get("verifications", []),
        "executable_evidence": entry.get("executable_evidence"),
    }
    if entry.get("verifications"):
        latest_verification = (entry.get("verifications") or [])[-1]
        out["verification"] = {
            "verifier": latest_verification.get("verifier", {}),
            "when": latest_verification.get("when_utc", ""),
            "evidence": _verification_evidence_paths(entry),
            "method": latest_verification.get("method", ""),
        }
    return out


def render_ledger(store: dict[str, Any]) -> dict[str, Any]:
    counts = Counter(entry["status"] for entry in store.get("entries", []))
    kinds = Counter(entry["kind"] for entry in store.get("entries", []))
    return {
        "_doc": "GENERATED VIEW of registry/fixes.json. Do not edit by hand; run scripts/render_fix_ledger.py.",
        "generated_from": _posix(REGISTRY_PATH),
        "schema_version": store.get("schema_version", 2),
        "fixes": [_view_entry(entry) for entry in store.get("entries", [])],
        "summary": {
            "by_status": {status: counts.get(status, 0) for status in store.get("statuses", [])},
            "by_kind": dict(sorted(kinds.items())),
        },
    }


def _readme_line(entry: dict[str, Any]) -> str:
    reason = ""
    latest = (entry.get("history") or [{}])[-1]
    if latest.get("reason"):
        reason = f" - {latest['reason']}"
    elif entry.get("status") in {"INTERNALLY_VERIFIED", "INDEPENDENTLY_VERIFIED"}:
        verifier = entry.get("verified_by") or {}
        evidence = ", ".join(_verification_evidence_paths(entry))
        reason = (
            f" - generated from {entry['fix_id']}; verified by "
            f"{verifier.get('identity')} ({verifier.get('kind')}); evidence: {evidence}"
        )
    else:
        reason = f" - generated from {entry['fix_id']}"
    return f"**Fix state (five-state rule): {entry['status']}**{reason}"


def _readme_owner_entries(store: dict[str, Any]) -> dict[str, dict[str, Any]]:
    owners: dict[str, dict[str, Any]] = {}
    for entry in store.get("entries", []):
        evidence_dir = entry.get("evidence_dir") or ""
        if evidence_dir and evidence_dir not in owners:
            owners[evidence_dir] = entry
    return owners


def render_readme_updates(root: Path, store: dict[str, Any]) -> dict[str, str]:
    updates: dict[str, str] = {}
    for evidence_dir, entry in _readme_owner_entries(store).items():
        readme = root / evidence_dir / "README.md"
        if not readme.is_file():
            continue
        rel = _posix(readme.relative_to(root))
        text = readme.read_text(encoding="utf-8")
        line = _readme_line(entry)
        if README_STATE_RE.search(text):
            new_text = README_STATE_RE.sub(line, text, count=1)
        else:
            lines = text.splitlines()
            insert_at = 1 if lines and lines[0].startswith("# ") else 0
            lines.insert(insert_at, "")
            lines.insert(insert_at + 1, line)
            new_text = "\n".join(lines).rstrip() + "\n"
        updates[rel] = new_text
    return updates


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=1, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def render(root: Path = ROOT, *, check: bool = False) -> list[str]:
    store = load_store(root)
    expected_ledger = render_ledger(store)
    readme_updates = render_readme_updates(root, store)
    stale: list[str] = []

    ledger_path = root / LEDGER_PATH
    if check:
        try:
            current = json.loads(ledger_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            current = None
        if current != expected_ledger:
            stale.append(_posix(LEDGER_PATH))
        for rel, want in readme_updates.items():
            path = root / rel
            if not path.exists() or path.read_text(encoding="utf-8") != want:
                stale.append(rel)
        return stale

    _write_json(ledger_path, expected_ledger)
    for rel, text in readme_updates.items():
        (root / rel).write_text(text, encoding="utf-8", newline="\n")
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    stale = render(ROOT, check=args.check)
    if stale:
        print("fix ledger view STALE: " + ", ".join(stale))
        return 1
    if args.check:
        print("fix ledger view current")
    else:
        print("rendered docs/fix_ledger.json and evidence README fix-state lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
