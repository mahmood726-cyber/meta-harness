"""Render GATE_GAPS.md gate rows from registry/gate_gaps.json."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import fixstate  # noqa: E402


REGISTRY_PATH = Path("registry") / "gate_gaps.json"
DOC_PATH = Path("GATE_GAPS.md")
START = "<!-- gate-gaps:generated:start -->"
END = "<!-- gate-gaps:generated:end -->"


def _posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def load(root: Path = ROOT) -> dict[str, Any]:
    return json.loads((root / REGISTRY_PATH).read_text(encoding="utf-8"))


def _freshness(entry: dict[str, Any], root: Path) -> tuple[str, list[str]]:
    return fixstate.freshness(entry, root)


def _row(cells: list[str]) -> str:
    return "| " + " | ".join(cell.replace("\n", " ") for cell in cells) + " |"


def _render_group(group: str, rows: list[dict[str, Any]], root: Path) -> str:
    out = [f"### {group}", ""]
    out.append(_row(["gate", "what it stops", "what it would NOT stop", "freshness", "source"]))
    out.append("|---|---|---|---|---|")
    for entry in rows:
        state, moved = _freshness(entry, root)
        fresh = state if not moved else f"{state}: " + ", ".join(f"`{path}`" for path in moved[:3])
        if len(moved) > 3:
            fresh += f", +{len(moved) - 3} more"
        out.append(
            _row(
                [
                    entry["gate"],
                    entry["stops"],
                    entry["would_not_stop"],
                    fresh,
                    entry.get("source", ""),
                ]
            )
        )
    return "\n".join(out)


def render_region(store: dict[str, Any], root: Path = ROOT) -> str:
    groups: dict[str, list[dict[str, Any]]] = {}
    for entry in store.get("entries", []):
        groups.setdefault(entry["group"], []).append(entry)
    body = [
        "## Gates that exist today, and what each would not stop",
        "",
        START,
        "",
        "The rows below are generated from `registry/gate_gaps.json`; freshness is computed from each row's seal.",
        "",
    ]
    for group, rows in groups.items():
        body.append(_render_group(group, rows, root))
        body.append("")
    body.append(END)
    body.append("")
    return "\n".join(body)


def render_document(text: str, store: dict[str, Any], root: Path = ROOT) -> str:
    region = render_region(store, root)
    if START in text and END in text:
        start = text.index("## Gates that exist today")
        end = text.index(END, start) + len(END)
        return text[:start] + region.rstrip() + text[end:]
    start = text.index("## Gates that exist today")
    end = text.index("\n## Not a gate", start)
    return text[:start] + region.rstrip() + text[end:]


def render(root: Path = ROOT, *, check: bool = False) -> list[str]:
    store = load(root)
    path = root / DOC_PATH
    current = path.read_text(encoding="utf-8")
    expected = render_document(current, store, root)
    if check:
        return [] if current == expected else [_posix(DOC_PATH)]
    path.write_text(expected, encoding="utf-8", newline="\n")
    return []


def check_registry(root: Path = ROOT) -> list[str]:
    store = load(root)
    reasons: list[str] = []
    seen: set[str] = set()
    for idx, entry in enumerate(store.get("entries", [])):
        label = entry.get("gap_id") or f"entries[{idx}]"
        if entry.get("kind") != "gap":
            reasons.append(f"{label}: kind must be gap")
        if entry.get("implementation") != "n/a":
            reasons.append(f"{label}: implementation must be n/a")
        if label in seen:
            reasons.append(f"{label}: duplicate gap_id")
        seen.add(str(label))
        for key in ("group", "gate", "stops", "would_not_stop", "source", "seal"):
            if key not in entry:
                reasons.append(f"{label}: missing {key}")
        seal = entry.get("seal")
        if not isinstance(seal, dict) or not isinstance(seal.get("dependencies"), dict) or not seal["dependencies"]:
            reasons.append(f"{label}: seal.dependencies must be non-empty")
    return reasons


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    reasons = check_registry(ROOT)
    if reasons:
        print("gate gaps registry REFUSED:")
        for reason in reasons:
            print(f"  - {reason}")
        return 1
    stale = render(ROOT, check=args.check)
    if stale:
        print("gate gaps table STALE: " + ", ".join(stale))
        return 1
    if args.check:
        print("gate gaps table current")
    else:
        print("rendered GATE_GAPS.md gate table")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
