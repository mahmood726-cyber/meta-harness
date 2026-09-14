"""Render the generated fix-state ledger from registry/fixes.json.

The registry is the authority. ``docs/fix_ledger.json`` is a generated view
and must not be hand-edited. Evidence README caption lines are rewritten by
``scripts/rewrite_fixstate_lines.py``.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import fixstate  # noqa: E402


REGISTRY_PATH = Path("registry") / "fixes.json"
LEDGER_PATH = Path("docs") / "fix_ledger.json"


def _posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def load_store(root: Path = ROOT) -> dict[str, Any]:
    return json.loads((root / REGISTRY_PATH).read_text(encoding="utf-8"))


def _event_evidence(entry: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for item in entry.get("events") or []:
        if not isinstance(item, dict):
            continue
        for path in item.get("evidence") or []:
            if path not in paths:
                paths.append(path)
    return paths


def _verification_evidence(entry: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for verification in entry.get("verifications") or []:
        if not isinstance(verification, dict):
            continue
        for evidence in verification.get("evidence") or []:
            if not isinstance(evidence, dict):
                continue
            label = evidence.get("path") or evidence.get("url") or evidence.get("external_record")
            if label and label not in paths:
                paths.append(str(label))
    return paths


def _latest_landed_commit(entry: dict[str, Any]) -> str:
    for event in reversed(entry.get("events") or []):
        if isinstance(event, dict) and event.get("implementation") == "LANDED":
            return str(event.get("commit") or "")
    return ""


def _state_text(entry: dict[str, Any], root: Path) -> str:
    fresh, _ = fixstate.freshness(entry, root)
    return f"{entry['implementation']} / {entry['verification']} / {entry['scope']} / {fresh}"


def _view_entry(entry: dict[str, Any], root: Path) -> dict[str, Any]:
    fresh, moved = fixstate.freshness(entry, root)
    evidence = _event_evidence(entry)
    verification_evidence = _verification_evidence(entry)
    for item in verification_evidence:
        if item not in evidence:
            evidence.append(item)
    out: dict[str, Any] = {
        "finding_id": entry["finding_id"],
        "fix_id": entry["fix_id"],
        "kind": entry["kind"],
        "class": entry["title"],
        "implementation": entry["implementation"],
        "verification": entry["verification"],
        "scope": entry["scope"],
        "freshness": fresh,
        "stale_dependencies": moved,
        "fix_state": _state_text(entry, root),
        "state": _state_text(entry, root),
        "where": _latest_landed_commit(entry),
        "evidence_dir": entry.get("evidence_dir", ""),
        "evidence": evidence,
        "verified_by": entry.get("verified_by"),
        "verifications": entry.get("verifications", []),
        "executable_evidence": entry.get("executable_evidence"),
        "seal": entry.get("seal"),
    }
    if entry.get("note"):
        out["note"] = entry["note"]
    if entry.get("verifications"):
        latest = (entry.get("verifications") or [])[-1]
        out["verification_record"] = {
            "verifier": latest.get("verifier", {}),
            "when": latest.get("when_utc", ""),
            "evidence": verification_evidence,
            "method": latest.get("method", ""),
        }
    return out


def render_ledger(store: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    store_entries = store.get("entries", [])
    by_impl = Counter(entry["implementation"] for entry in store_entries)
    by_verification = Counter(entry["verification"] for entry in store_entries)
    by_scope = Counter(entry["scope"] for entry in store_entries)
    by_kind = Counter(entry["kind"] for entry in store_entries)
    by_freshness = Counter(fixstate.freshness_state(entry, root) for entry in store_entries)
    return {
        "_doc": "GENERATED VIEW of registry/fixes.json. Do not edit by hand; run scripts/render_fix_ledger.py.",
        "generated_from": _posix(REGISTRY_PATH),
        "schema_version": store.get("schema_version", fixstate.SCHEMA_VERSION),
        "fixes": [_view_entry(entry, root) for entry in store_entries],
        "summary": {
            "by_implementation": {
                value: by_impl.get(value, 0)
                for value in store.get("implementations", list(fixstate.CONTROL_IMPLEMENTATIONS))
            },
            "by_verification": {
                value: by_verification.get(value, 0)
                for value in store.get("verification_levels", list(fixstate.VERIFICATIONS))
            },
            "by_scope": {
                value: by_scope.get(value, 0)
                for value in store.get("scopes", list(fixstate.SCOPES))
            },
            "by_freshness": {
                value: by_freshness.get(value, 0)
                for value in store.get("freshness", list(fixstate.FRESHNESS))
            },
            "by_kind": dict(sorted(by_kind.items())),
        },
    }


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=1, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def render(root: Path = ROOT, *, check: bool = False) -> list[str]:
    store = load_store(root)
    expected = render_ledger(store, root=root)
    ledger_path = root / LEDGER_PATH
    if check:
        try:
            current = json.loads(ledger_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            current = None
        return [] if current == expected else [_posix(LEDGER_PATH)]
    _write_json(ledger_path, expected)
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
        print("rendered docs/fix_ledger.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
