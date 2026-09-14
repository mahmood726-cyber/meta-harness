"""Held-out topic isolation checks for the acquisition engine.

The held-out registry is a reproducibility boundary: designated topics may be
published as the engine's measurement set, but they must not leak into tests,
fixtures, hard-coded engine target lists, or post-enforcement commit messages.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Iterable


REGISTRY_PATH = os.path.join("registry", "heldout.json")
MEASUREMENT_PATH = os.path.join("docs", "search_recall_heldout.json")
COMMIT_MESSAGE_REFUSAL = (
    "held-out topics may not be named in commit messages "
    "(registry/heldout.json); refer to the measurement artefact instead"
)


def _root_path(root) -> str:
    return os.path.abspath(os.fspath(root))


def _posix(path: str) -> str:
    return path.replace("\\", "/")


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
    """Load the held-out registry from registry/heldout.json under root."""
    with open(os.path.join(_root_path(root), REGISTRY_PATH), encoding="utf-8") as f:
        return json.load(f)


def short_form(slug: str) -> str:
    """Return the first two hyphen-separated tokens of a slug."""
    return "-".join(slug.split("-")[:2])


def _needles(slug: str) -> list[str]:
    needles = [slug]
    sf = short_form(slug)
    if sf and sf.lower() != slug.lower():
        needles.append(sf)
    return needles


def _mentions_slug(text: str, slug: str) -> bool:
    lower = text.lower()
    return any(needle.lower() in lower for needle in _needles(slug))


def _matching_slugs(text: str, registry: dict) -> list[str]:
    return [slug for slug in registry.get("slugs", []) if _mentions_slug(text, slug)]


def _allowed_patterns(registry: dict) -> set[str]:
    patterns = set()
    slugs = registry.get("slugs", [])
    for pattern in registry.get("allowed_paths", []):
        if "<slug>" in pattern:
            for slug in slugs:
                patterns.add(pattern.replace("<slug>", slug))
        else:
            patterns.add(pattern)
    patterns.add(REGISTRY_PATH)
    return {_posix(p) for p in patterns}


def _path_matches(path: str, patterns: Iterable[str]) -> bool:
    for pattern in patterns:
        if pattern.endswith("/"):
            if path.startswith(pattern):
                return True
        elif path == pattern:
            return True
    return False


def _is_forbidden_path(path: str, registry: dict) -> bool:
    return any(path.startswith(_posix(prefix)) for prefix in registry.get("forbidden_paths", []))


def _is_binary(blob: bytes) -> bool:
    # NUL is the fail-closed text/binary divider Git itself commonly uses.
    return b"\0" in blob[:8192]


def scan_paths(root, registry: dict) -> list[dict]:
    """Scan tracked forbidden-path files for held-out slug or short-form mentions."""
    root = _root_path(root)
    allowed = _allowed_patterns(registry)
    hits = []
    tracked = _run_git(root, ["ls-files"]).splitlines()
    for raw_path in tracked:
        path = _posix(raw_path)
        if not _is_forbidden_path(path, registry):
            continue
        if _path_matches(path, allowed):
            continue
        abs_path = os.path.join(root, *path.split("/"))
        try:
            blob = open(abs_path, "rb").read()
        except OSError:
            continue
        if _is_binary(blob):
            continue
        text = blob.decode("utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for slug in _matching_slugs(line, registry):
                hits.append({"path": path, "slug": slug, "line_no": line_no, "line": line})
    return hits


def check_message(text: str, registry: dict) -> list[str]:
    """Return held-out slugs named in a commit message."""
    return _matching_slugs(text, registry)


def _excerpt(text: str, slug: str) -> str:
    for line in text.splitlines() or [text]:
        if _mentions_slug(line, slug):
            clean = " ".join(line.strip().split())
            return clean[:200]
    return ""


def scan_commit_messages(root, registry: dict) -> list[dict]:
    """Scan first-parent commit messages after enforced_since for held-out mentions."""
    root = _root_path(root)
    enforced_since = registry.get("enforced_since")
    if enforced_since is None:
        return []
    out = _run_git(
        root,
        ["log", "--first-parent", "--format=%H%x00%B%x00", f"{enforced_since}..HEAD"],
    )
    parts = out.split("\0")
    hits = []
    for i in range(0, len(parts) - 1, 2):
        sha = parts[i].strip()
        message = parts[i + 1].lstrip("\n")
        if not sha:
            continue
        for slug in check_message(message, registry):
            hits.append({"sha": sha, "slug": slug, "excerpt": _excerpt(message, slug)})
    return hits


def _engine_sha(root: str) -> str:
    return _run_git(root, ["hash-object", os.path.join("harness", "acquisition.py")]).strip()


def measurement_current(root, registry: dict) -> tuple[bool, str]:
    """Return whether the published held-out recall artefact matches the engine blob."""
    root = _root_path(root)
    if registry.get("enforced_since") is None:
        return True, "not enforced yet"
    artefact = os.path.join(root, MEASUREMENT_PATH)
    if not os.path.exists(artefact):
        return False, "no published held-out measurement"
    try:
        data = json.load(open(artefact, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return False, f"published held-out measurement unreadable: {exc}"
    current = _engine_sha(root)
    published = data.get("engine_sha")
    if published != current:
        return (
            False,
            "engine changed since the published measurement "
            f"({published} -> {current}); re-measure and publish before landing",
        )
    history = data.get("history")
    if not isinstance(history, list) or not history:
        return False, "published held-out measurement history is empty"
    last = history[-1]
    if not isinstance(last, dict) or last.get("engine_sha") != published:
        return False, "published held-out measurement history does not end at engine_sha"
    return True, "published held-out measurement matches current engine"


def check(root) -> tuple[bool, list[str]]:
    """Run path, commit-message, and measurement checks."""
    root = _root_path(root)
    reasons = []
    try:
        registry = load(root)
    except Exception as exc:
        return False, [f"held-out registry could not be loaded: {exc}"]
    try:
        for hit in scan_paths(root, registry):
            reasons.append(
                f"{hit['path']}:{hit['line_no']}: held-out topic {hit['slug']} "
                f"appears in a forbidden path: {hit['line']}"
            )
    except Exception as exc:
        reasons.append(f"held-out path scan could not run: {exc}")
    try:
        for hit in scan_commit_messages(root, registry):
            reasons.append(
                f"{hit['sha'][:12]}: held-out topic {hit['slug']} "
                f"appears in a commit message: {hit['excerpt']}"
            )
    except Exception as exc:
        reasons.append(f"held-out commit-message scan could not run: {exc}")
    try:
        ok, detail = measurement_current(root, registry)
        if not ok:
            reasons.append(detail)
    except Exception as exc:
        reasons.append(f"held-out measurement check could not run: {exc}")
    return not reasons, reasons


def _message_check(root: str, path: str) -> int:
    registry = load(root)
    if registry.get("enforced_since") is None:
        print("held-out commit-message check: PASS (not enforced yet)")
        return 0
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as exc:
        print(f"held-out commit-message check: REFUSED ({exc})")
        return 1
    bad = check_message(text, registry)
    if bad:
        print(COMMIT_MESSAGE_REFUSAL)
        print("offending held-out slug(s): " + ", ".join(bad))
        return 1
    print("held-out commit-message check: PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m harness.heldout")
    parser.add_argument("--message", help="commit message file to check")
    args = parser.parse_args(argv)
    root = _root_path(os.getcwd())

    if args.message:
        return _message_check(root, args.message)

    try:
        registry = load(root)
        path_hits = scan_paths(root, registry)
        commit_hits = scan_commit_messages(root, registry)
        measurement_ok, measurement_detail = measurement_current(root, registry)
    except Exception as exc:
        print(f"HELD-OUT: REFUSED -- {type(exc).__name__}: {exc}")
        return 1

    print(f"HELD-OUT: registry={REGISTRY_PATH} slugs={len(registry.get('slugs', []))}")
    print(f"HELD-OUT: path scan {'PASS' if not path_hits else 'REFUSED'} ({len(path_hits)} violation(s))")
    if registry.get("enforced_since") is None:
        print("HELD-OUT: commit-message scan PASS (not enforced yet)")
    else:
        print(
            "HELD-OUT: commit-message scan "
            f"{'PASS' if not commit_hits else 'REFUSED'} ({len(commit_hits)} violation(s))"
        )
    print(f"HELD-OUT: measurement {'PASS' if measurement_ok else 'REFUSED'} ({measurement_detail})")

    ok, reasons = check(root)
    if not ok:
        print("HELD-OUT: REFUSED")
        for reason in reasons:
            print(f"  - {reason}")
        return 1
    print("HELD-OUT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
