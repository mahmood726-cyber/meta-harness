"""Rendered honest-state ratchet.

The gate compares visible honest-state markers against a base ref. A page may add warnings, but
once a warning has been served, a template edit must not silently make that page quieter.
"""
from __future__ import annotations

import argparse
import html
import os
import re
import subprocess
from pathlib import Path


MARKERS = {
    "stale": ["STALE — this topic"],
    "claims_checked_zero": ["Claims checked: 0"],
    "never_considered": ["Never considered (a fifth state"],
    "refusal_counterfactual": ["Refusal is reversible and auditable", "If forced it would be"],
    "pinned_identity": ["Pinned audit identity"],
    "retrieval_class": [
        "KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH",
        "TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH",
        "an auditable screening ledger attached to an unauditable retrieval process",
    ],
    "suppressed_pool": ["Pooled result SUPPRESSED"],
    "retraction": ["RETRACT", "retracted", "withdrawn", "superseded"],
    "declared_absent": ["declared absent", "DECLARED_ABSENT"],
    "not_assessed": ["not assessed", "NOT_ASSESSED"],
}


def _run(root: str | os.PathLike[str], args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _rendered_text(src: str) -> str:
    src = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", src, flags=re.IGNORECASE | re.DOTALL)
    src = re.sub(r"<[^>]+>", " ", src)
    return re.sub(r"\s+", " ", html.unescape(src)).strip()


def inventory(src: str) -> dict[str, int]:
    text = _rendered_text(src)
    return {kind: sum(text.count(_rendered_text(phrase)) for phrase in phrases)
            for kind, phrases in MARKERS.items()}


def compare(base_html: str, new_html: str) -> list[str]:
    base = inventory(base_html)
    new = inventory(new_html)
    out = []
    for kind in MARKERS:
        if base[kind] > 0 and new[kind] < base[kind]:
            out.append(f"{kind}: base count {base[kind]}, new count {new[kind]}")
    return out


def _verify_ref(root: str | os.PathLike[str], ref: str) -> str | None:
    p = _run(root, ["rev-parse", "--verify", f"{ref}^{{commit}}"])
    if p.returncode == 0:
        return p.stdout.strip()
    return None


def _resolve_base(root: str | os.PathLike[str], base_ref: str | None) -> tuple[str | None, str | None]:
    explicit = base_ref or os.environ.get("RATCHET_BASE")
    if explicit:
        ref = _verify_ref(root, explicit)
        if ref:
            return ref, None
        return None, f"COULD-NOT-EXECUTE: base ref not resolvable: {explicit}"

    origin = _verify_ref(root, "origin/main")
    head = _verify_ref(root, "HEAD")
    if origin and head and origin != head:
        p = _run(root, ["merge-base", "HEAD", "origin/main"])
        if p.returncode == 0 and p.stdout.strip():
            return p.stdout.strip(), None

    previous = _verify_ref(root, "HEAD~1")
    if previous:
        return previous, None
    return None, "COULD-NOT-EXECUTE: no ratchet base ref resolvable"


def _base_pages(root: str | os.PathLike[str], ref: str) -> tuple[list[str] | None, str | None]:
    p = _run(root, ["ls-tree", "-r", "--name-only", ref, "--", "docs/index.html", "docs/reviews"])
    if p.returncode != 0:
        return None, f"COULD-NOT-EXECUTE: cannot list base pages at {ref}: {p.stderr.strip() or p.stdout.strip()}"
    pages = []
    for line in p.stdout.splitlines():
        path = line.strip().replace("\\", "/")
        if path == "docs/index.html" or (path.startswith("docs/reviews/") and path.endswith("/index.html")):
            pages.append(path)
    return sorted(pages), None


def _show(root: str | os.PathLike[str], ref: str, path: str) -> tuple[str | None, str | None]:
    p = _run(root, ["show", f"{ref}:{path}"])
    if p.returncode != 0:
        return None, f"COULD-NOT-EXECUTE: cannot read {path} at {ref}: {p.stderr.strip() or p.stdout.strip()}"
    return p.stdout, None


def check(root: str | os.PathLike[str], base_ref: str | None = None) -> tuple[bool, list[str]]:
    ref, err = _resolve_base(root, base_ref)
    if err:
        return False, [err]
    pages, err = _base_pages(root, ref)
    if err:
        return False, [err]

    root_path = Path(root)
    reasons = []
    for rel in pages or []:
        base_html, err = _show(root, ref, rel)
        if err:
            reasons.append(err)
            continue
        new_path = root_path.joinpath(*rel.split("/"))
        try:
            new_html = new_path.read_text(encoding="utf-8") if new_path.exists() else ""
        except OSError as exc:
            reasons.append(f"COULD-NOT-EXECUTE: cannot read working-tree {rel}: {exc}")
            continue
        for violation in compare(base_html or "", new_html):
            reasons.append(f"{rel}: {violation}")
    return not reasons, reasons


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", help="base git ref to compare against")
    args = parser.parse_args(argv)
    ok, reasons = check(os.getcwd(), args.base)
    if ok:
        print("honest-state ratchet: PASS")
        return 0
    print("honest-state ratchet: REFUSED")
    for reason in reasons:
        print(reason)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
