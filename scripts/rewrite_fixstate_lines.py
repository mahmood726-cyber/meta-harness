"""Rewrite evidence README fix-state caption lines from registry/fixes.json."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import fixstate  # noqa: E402


README_STATE_RE = re.compile(
    r"^\*\*Fix state \((?:four|five|orthogonal)(?:-state)?(?: fields)? rule\): .*?(?:\*\*.*)?$",
    re.MULTILINE,
)


def _posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def _verification_evidence(entry: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for verification in entry.get("verifications") or []:
        if not isinstance(verification, dict):
            continue
        for evidence in verification.get("evidence") or []:
            if not isinstance(evidence, dict):
                continue
            label = evidence.get("path") or evidence.get("url") or evidence.get("external_record")
            if label and label not in labels:
                labels.append(str(label))
    return labels


def _state_text(entry: dict[str, Any], root: Path) -> tuple[str, list[str]]:
    fresh, moved = fixstate.freshness(entry, root)
    return f"{entry['implementation']} / {entry['verification']} / {entry['scope']} / {fresh}", moved


def _readme_line(root: Path, entry: dict[str, Any]) -> str:
    state, moved = _state_text(entry, root)
    suffix = f" - generated from {entry['fix_id']}"
    if entry.get("verification") != "NONE":
        verifier = entry.get("verified_by") or {}
        suffix += f"; verified by {verifier.get('identity')} ({verifier.get('kind')})"
        evidence = ", ".join(_verification_evidence(entry))
        if evidence:
            suffix += f"; evidence: {evidence}"
    if moved:
        shown = ", ".join(moved[:3])
        if len(moved) > 3:
            shown += f", +{len(moved) - 3} more"
        suffix += f"; stale dependencies: {shown}"
    return f"**Fix state (orthogonal fields rule): {state}**{suffix}"


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
        line = _readme_line(root, entry)
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


def rewrite(root: Path = ROOT, *, check: bool = False) -> list[str]:
    store = fixstate.load(root)
    updates = render_readme_updates(root, store)
    stale: list[str] = []
    for rel, want in updates.items():
        path = root / rel
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if check:
            if current != want:
                stale.append(rel)
        else:
            path.write_text(want, encoding="utf-8", newline="\n")
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    stale = rewrite(ROOT, check=args.check)
    if stale:
        print("fix-state README lines STALE: " + ", ".join(stale))
        return 1
    if args.check:
        print("fix-state README lines current")
    else:
        print("rewrote evidence README fix-state lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
