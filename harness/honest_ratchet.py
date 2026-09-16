"""Rendered honest-state ratchet.

The gate compares visible honest-state markers against a base ref. A page may add warnings, but
once a warning has been served, a template edit must not silently make that page quieter.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from harness.target import TargetUnresolvable, describe_target, refusal as target_refusal


MARKERS = {
    "stale": ["STALE — this topic"],
    "claims_checked_zero": ["Claims checked: 0"],
    "never_considered": ["Never considered (a fifth state"],
    "refusal_counterfactual": ["Refusal is reversible and auditable", "If forced it would be"],
    "pinned_identity": ["Pinned audit identity"],
    "retrieval_class": [
        "KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH",
        "TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH",
        "HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH",
        "an auditable screening ledger attached to an unauditable retrieval process",
    ],
    "search_provenance": ["Search provenance", "not a completed systematic search"],
    "identifier_scope": ["identifier names", "class-level pool"],
    "suppressed_pool": ["Pooled result SUPPRESSED"],
    "design_refusal": ["Pool changed because a design refusal was added", "pooled variance unsupported"],
    "retraction": ["retract", "retraction", "we retract", "retracted", "withdrawn", "superseded"],
    # The declared-absent state is one honest marker under several spellings: the legacy phrase and the
    # typed absence codes (lane RR, 2026-09-16). A page that renames the state has not lost it.
    "declared_absent": ["declared absent", "DECLARED_ABSENT", "OUTCOME_NOT_IN_SOURCE",
                        "EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH", "COUNTS_PRESENT_NOT_CORROBORATED",
                        "SOURCE_NOT_RETRIEVED", "MULTI_ARM_UNRESOLVED", "TIMEPOINT_MISMATCH",
                        "POPULATION_MISMATCH"],
    "not_assessed": ["not assessed", "NOT_ASSESSED"],
}
ACK_PATH = Path("docs") / "ratchet_acknowledgements.json"
BLOCK_CLASSES = ("absent", "banner")
BLOCK_RATCHET_BASE_REFS = ("b8925e04~1",)
RETRACTION_RE = {
    phrase: re.compile(r"\b" + r"\s+".join(map(re.escape, phrase.split())) + r"\b", re.IGNORECASE)
    for phrase in MARKERS["retraction"]
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


def _count_marker(text: str, kind: str, phrases: list[str]) -> int:
    if kind == "retraction":
        return sum(len(RETRACTION_RE[phrase].findall(text)) for phrase in phrases)
    return sum(text.count(_rendered_text(phrase)) for phrase in phrases)


def inventory(src: str) -> dict[str, int]:
    text = _rendered_text(src)
    return {kind: _count_marker(text, kind, phrases) for kind, phrases in MARKERS.items()}


class _BlockParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.active: list[dict[str, Any]] = []
        self.out: list[dict[str, str]] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style"}:
            self.skip_depth += 1
        for block in self.active:
            if tag == "div":
                block["depth"] += 1
            block["parts"].append(" ")
        cls = _tracked_class(dict(attrs).get("class"))
        if tag == "div" and cls:
            self.active.append({"cls": cls, "depth": 1, "parts": []})

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style"} and self.skip_depth:
            self.skip_depth -= 1
        done = []
        for block in self.active:
            block["parts"].append(" ")
            if tag == "div":
                block["depth"] -= 1
                if block["depth"] == 0:
                    done.append(block)
        for block in done:
            self.active.remove(block)
            text = re.sub(r"\s+", " ", html.unescape("".join(block["parts"]))).strip()
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            self.out.append({"cls": block["cls"], "text": text, "sha256": digest})

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        for block in self.active:
            block["parts"].append(data)


def _tracked_class(raw: str | None) -> str | None:
    if not raw:
        return None
    classes = set(raw.split())
    for cls in BLOCK_CLASSES:
        if cls in classes:
            return cls
    return None


def blocks(src: str) -> list[dict[str, str]]:
    """Return visible absent/banner blocks with their rendered text digest."""
    parser = _BlockParser()
    parser.feed(src)
    parser.close()
    return parser.out


_MARKER_ACK_REQUIRED = ("page", "kind", "base_count", "new_count", "reason", "by", "when_utc")


def _marker_ack_entries(acknowledgements: Any) -> list[dict[str, Any]]:
    if isinstance(acknowledgements, dict):
        raw = acknowledgements.get("marker_acknowledgements", [])
    else:
        raw = []
    return [e for e in raw if isinstance(e, dict)]


def _marker_decrease_acknowledged(acknowledgements: Any, page: str, kind: str, base: int, new: int) -> bool:
    """A marker-count decrease is acceptable only under a signed entry naming the page, the kind and BOTH
    counts exactly. A decrease is a fix only when someone read both pages and said why; a fix that lands
    the counts anywhere else is a different change and is not covered."""
    for e in _marker_ack_entries(acknowledgements):
        if any(not e.get(k) and e.get(k) != 0 for k in _MARKER_ACK_REQUIRED):
            continue
        if e["page"] == page and e["kind"] == kind and e["base_count"] == base and e["new_count"] == new:
            return True
    return False


def compare(base_html: str, new_html: str, acknowledgements: Any = None, page: str | None = None) -> list[str]:
    base = inventory(base_html)
    new = inventory(new_html)
    out = []
    for kind in MARKERS:
        if base[kind] > 0 and new[kind] < base[kind]:
            if page and _marker_decrease_acknowledged(acknowledgements, page, kind, base[kind], new[kind]):
                continue
            out.append(f"{kind}: base count {base[kind]}, new count {new[kind]}")
    return out


def _ack_entries(acknowledgements: Any) -> list[dict[str, Any]]:
    if isinstance(acknowledgements, dict):
        raw = acknowledgements.get("acknowledgements", [])
    else:
        raw = acknowledgements
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def _valid_ack(entry: dict[str, Any], lost: dict[str, str], new_shas: set[str], page: str) -> bool:
    return (
        entry.get("page") == page
        and entry.get("lost_sha256") == lost["sha256"]
        and isinstance(entry.get("lost_text_prefix"), str)
        and bool(entry["lost_text_prefix"])
        and lost["text"].startswith(entry["lost_text_prefix"])
        and entry.get("replaced_by_sha256") in new_shas
        and all(isinstance(entry.get(key), str) and entry.get(key).strip() for key in ("reason", "when_utc", "by"))
    )


def compare_blocks(
    base_blocks: list[dict[str, str]],
    new_blocks: list[dict[str, str]],
    acknowledgements: Any,
    page: str,
) -> list[str]:
    """Refuse absent/banner blocks that vanished without a reviewed replacement acknowledgement."""
    new_shas = {block["sha256"] for block in new_blocks}
    entries = _ack_entries(acknowledgements)
    # A base several commits back can skip intermediate replacements (A -> B acknowledged, B -> C
    # acknowledged, only C on the page). Follow the reviewed chain transitively: a replacement is
    # acceptable if it is on the page or is itself the lost sha of another reviewed acknowledgement
    # for the same page whose chain ends on the page. Every link is still a signed acknowledgement.
    reachable = set(new_shas)
    changed = True
    while changed:
        changed = False
        for entry in entries:
            if entry.get("page") == page and entry.get("replaced_by_sha256") in reachable \
                    and isinstance(entry.get("lost_sha256"), str) and entry["lost_sha256"] not in reachable \
                    and all(isinstance(entry.get(k), str) and entry.get(k).strip() for k in ("reason", "when_utc", "by")):
                reachable.add(entry["lost_sha256"])
                changed = True
    out = []
    for block in base_blocks:
        if block["sha256"] in new_shas:
            continue
        if any(_valid_ack(entry, block, reachable, page) for entry in entries):
            continue
        prefix = block["text"][:120]
        out.append(f"lost {block['cls']} block {block['sha256']}: {prefix}")
    return out


def _load_acknowledgements(root: str | os.PathLike[str]) -> tuple[Any, list[str]]:
    path = Path(root) / ACK_PATH
    if not path.exists():
        return [], []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"COULD-NOT-EXECUTE: cannot read {ACK_PATH.as_posix()}: {exc}"]
    if isinstance(data, dict):
        if not isinstance(data.get("_doc"), str) or not data["_doc"].strip():
            return data, [f"COULD-NOT-EXECUTE: {ACK_PATH.as_posix()} missing _doc"]
        if not isinstance(data.get("acknowledgements"), list):
            return data, [f"COULD-NOT-EXECUTE: {ACK_PATH.as_posix()} acknowledgements must be a list"]
        return data, []
    if isinstance(data, list):
        return data, []
    return [], [f"COULD-NOT-EXECUTE: {ACK_PATH.as_posix()} must be a list or object"]


def _verify_ref(root: str | os.PathLike[str], ref: str) -> str | None:
    p = _run(root, ["rev-parse", "--verify", f"{ref}^{{commit}}"])
    if p.returncode == 0:
        return p.stdout.strip()
    return None


def _resolve_base(root: str | os.PathLike[str], base_ref: str | None) -> tuple[str | None, str | None, str | None]:
    explicit = base_ref or os.environ.get("RATCHET_BASE")
    if explicit:
        ref = _verify_ref(root, explicit)
        if ref:
            source = "--base" if base_ref else "RATCHET_BASE"
            return ref, source, None
        return None, None, f"COULD-NOT-EXECUTE: base ref not resolvable: {explicit}"

    origin = _verify_ref(root, "origin/main")
    head = _verify_ref(root, "HEAD")
    if origin and head and origin != head:
        p = _run(root, ["merge-base", "HEAD", "origin/main"])
        if p.returncode == 0 and p.stdout.strip():
            return p.stdout.strip(), "merge-base origin/main", None

    previous = _verify_ref(root, "HEAD~1")
    if previous:
        return previous, "HEAD~1", None
    return None, None, "COULD-NOT-EXECUTE: no ratchet base ref resolvable"


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


def _block_base_refs(root: str | os.PathLike[str], ref: str) -> list[str]:
    seen = {ref}
    out = [ref]
    for raw_ref in BLOCK_RATCHET_BASE_REFS:
        resolved = _verify_ref(root, raw_ref)
        if resolved and resolved not in seen:
            seen.add(resolved)
            out.append(resolved)
    return out


def describe_check_target(root: str | os.PathLike[str], base_ref: str | None = None) -> str:
    """Describe the ratchet target without running the ratchet comparison."""

    ref, source, err = _resolve_base(root, base_ref)
    if err:
        return target_refusal("honest_ratchet", err.replace("COULD-NOT-EXECUTE: ", ""))
    pages, err = _base_pages(root, ref)
    if err:
        return target_refusal("honest_ratchet", err.replace("COULD-NOT-EXECUTE: ", ""))
    block_refs = _block_base_refs(root, ref)
    paths = list(pages or [])
    paths.append(ACK_PATH.as_posix())
    try:
        line = describe_target(root, refs=(ref,), paths=paths, label="honest_ratchet")
    except TargetUnresolvable as exc:
        return target_refusal("honest_ratchet", str(exc))
    return (
        f"{line} base_resolution={source} pages={len(pages or [])} "
        f"block_floor_refs={','.join(block_refs)}"
    )


def _show(root: str | os.PathLike[str], ref: str, path: str) -> tuple[str | None, str | None]:
    p = _run(root, ["show", f"{ref}:{path}"])
    if p.returncode != 0:
        return None, f"COULD-NOT-EXECUTE: cannot read {path} at {ref}: {p.stderr.strip() or p.stdout.strip()}"
    return p.stdout, None


def check(root: str | os.PathLike[str], base_ref: str | None = None) -> tuple[bool, list[str]]:
    ref, _source, err = _resolve_base(root, base_ref)
    if err:
        return False, [err]
    pages, err = _base_pages(root, ref)
    if err:
        return False, [err]

    root_path = Path(root)
    reasons = []
    acknowledgements, ack_errors = _load_acknowledgements(root_path)
    reasons.extend(ack_errors)
    block_reasons_seen: set[tuple[str, str]] = set()
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
        for violation in compare(base_html or "", new_html, acknowledgements, rel):
            reasons.append(f"{rel}: {violation}")

    for block_ref in _block_base_refs(root, ref):
        block_pages, err = _base_pages(root, block_ref)
        if err:
            reasons.append(err)
            continue
        for rel in block_pages or []:
            if block_ref != ref and rel == "docs/index.html":
                continue
            base_html, err = _show(root, block_ref, rel)
            if err:
                reasons.append(err)
                continue
            new_path = root_path.joinpath(*rel.split("/"))
            try:
                new_html = new_path.read_text(encoding="utf-8") if new_path.exists() else ""
            except OSError as exc:
                reasons.append(f"COULD-NOT-EXECUTE: cannot read working-tree {rel}: {exc}")
                continue
            for violation in compare_blocks(blocks(base_html or ""), blocks(new_html), acknowledgements, rel):
                key = (rel, violation.split(":", 1)[0])
                if key in block_reasons_seen:
                    continue
                block_reasons_seen.add(key)
                reasons.append(f"{rel}: {violation}")
    return not reasons, reasons


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", help="base git ref to compare against")
    args = parser.parse_args(argv)
    target_line = describe_check_target(os.getcwd(), args.base)
    print(target_line)
    if target_line.startswith("TARGET honest_ratchet: COULD-NOT-EXECUTE"):
        print("honest-state ratchet: COULD-NOT-EXECUTE")
        return 1
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
