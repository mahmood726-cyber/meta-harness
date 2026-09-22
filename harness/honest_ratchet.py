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
# result-change: a countersigned result-change notice is an honest marker like an absent/banner block -- once on
# the page it cannot vanish without a reviewed replacement acknowledgement (M2, 2026-09-21).
BLOCK_CLASSES = ("absent", "banner", "result-change")
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
    """Return visible absent/banner/result-change blocks with their rendered text digest."""
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


_PARITY_ACK_REQUIRED = ("slug", "old_relation", "new_relation", "left_pool", "entered_pool", "reason", "by", "when_utc")


def _parity_ack_entries(acknowledgements: Any) -> list[dict[str, Any]]:
    if isinstance(acknowledgements, dict):
        raw = acknowledgements.get("parity_acknowledgements", [])
    else:
        raw = []
    return [e for e in raw if isinstance(e, dict)]


def _parity_facts(review_json: Any) -> tuple[str | None, list[str]]:
    """(computed parity relation, primary-outcome pooled trial ids) of one review.json, or (None, [])."""
    if not isinstance(review_json, dict):
        return None, []
    parity = ((review_json.get("reproduction") or {}).get("parity")) or {}
    relation = (parity.get("parity_relation") or {}).get("relation")
    pooled: list[str] = []
    for outcome in review_json.get("outcomes") or []:
        if isinstance(outcome, dict) and outcome.get("primary"):
            pooled = [str(t.get("id")) for t in (outcome.get("trials") or []) if isinstance(t, dict)]
            break
    return (str(relation) if relation else None), sorted(pooled)


def compare_parity(base_review: Any, new_review: Any, acknowledgements: Any, slug: str) -> list[str]:
    """The computed parity relation is a claim about our agreement with an external benchmark. It is
    derived, so it moves whenever the pool moves -- and a silent SUPERSET -> OVERLAPPING would hide a
    degradation against the one external check we have. A changed relation is admitted only under an
    acknowledgement naming the topic, the old and new relation, EVERY trial that left or entered the
    primary pool (exactly), why, and who. A topic with no served relation has nothing to acknowledge."""
    base_rel, base_pool = _parity_facts(base_review)
    new_rel, new_pool = _parity_facts(new_review)
    if base_rel is None or new_rel is None or base_rel == new_rel:
        return []
    left = sorted(set(base_pool) - set(new_pool))
    entered = sorted(set(new_pool) - set(base_pool))
    for e in _parity_ack_entries(acknowledgements):
        if any(not isinstance(e.get(k), (str, list)) or (isinstance(e.get(k), str) and not e[k].strip())
               for k in _PARITY_ACK_REQUIRED):
            continue
        if (e["slug"] == slug and e["old_relation"] == base_rel and e["new_relation"] == new_rel
                and sorted(map(str, e["left_pool"])) == left and sorted(map(str, e["entered_pool"])) == entered):
            return []
    return [
        f"parity relation changed {base_rel} -> {new_rel} for {slug} "
        f"(left the primary pool: {', '.join(left) or 'none'}; entered: {', '.join(entered) or 'none'}) -- "
        "not acknowledged: docs/ratchet_acknowledgements.json parity_acknowledgements needs an entry naming the "
        "slug, old_relation, new_relation, left_pool and entered_pool exactly, reason, by, when_utc"
    ]


_SCREENING_ACK_REQUIRED = ("slug", "record_id", "old_decision", "new_decision", "reason", "by", "when_utc")


def _screening_ack_entries(acknowledgements: Any) -> list[dict[str, Any]]:
    raw = acknowledgements.get("screening_acknowledgements", []) if isinstance(acknowledgements, dict) else []
    return [e for e in raw if isinstance(e, dict)]


def _screening_decisions(review_json: Any) -> dict[str, str]:
    if not isinstance(review_json, dict):
        return {}
    out: dict[str, str] = {}
    for r in ((review_json.get("screening") or {}).get("records") or []):
        if isinstance(r, dict) and r.get("id") is not None:
            out[str(r.get("id")).strip()] = str(r.get("decision") or "")
    return out


def compare_screening(base_review: Any, new_review: Any, acknowledgements: Any, slug: str) -> list[str]:
    """NOT SATISFIABLE BY DROPPING ROWS (enforcement gate, 2026-09-21; lane R finding R1): a trial screened IN on the
    served page that is screened OUT -- or gone from the screening ledger -- on the rebuilt page has left the
    candidate set BEFORE admission, where the admission gate cannot see it (a consistent rebuild after editing the
    topic's executable include list passed the whole gate with no refusal naming the trial). Every such departure is
    admitted only under an acknowledgement naming the slug, the record, the old and new decision, why, and who
    (docs/ratchet_acknowledgements.json screening_acknowledgements). A record that stays screened in, or a new
    record, needs nothing: the ratchet is one-directional -- the candidate set may not get quieter."""
    base, new = _screening_decisions(base_review), _screening_decisions(new_review)
    if not base:
        return []
    acks = [e for e in _screening_ack_entries(acknowledgements)
            if all(isinstance(e.get(k), str) and e[k].strip() for k in _SCREENING_ACK_REQUIRED)]
    out = []
    for rid, old in sorted(base.items()):
        if old != "include":
            continue
        cur = new.get(rid, "ABSENT_FROM_SCREENING")
        if cur == "include":
            continue
        if any(e["slug"] == slug and e["record_id"] == rid and e["old_decision"] == old and e["new_decision"] == cur for e in acks):
            continue
        out.append(
            f"screened-in record {rid} left the candidate set for {slug}: decision {old} -> {cur} -- not acknowledged: "
            "docs/ratchet_acknowledgements.json screening_acknowledgements needs an entry naming slug, record_id, "
            "old_decision, new_decision exactly, reason, by, when_utc (a refused extraction is set aside on the page "
            "with its reason; a trial never leaves the candidate set silently)"
        )
    return out


RESULT_CHANGES_PATH = Path("docs") / "result_changes.json"


def _load_result_change_notices(root: str | os.PathLike[str]) -> list[dict[str, Any]]:
    from harness import result_changes
    return result_changes.load(str(root))


def compare_results(base_review: Any, new_review: Any, notices: Any, slug: str) -> list[str]:
    """A served pooled result that changes -- k, estimate, interval, or the estimate disappearing -- is admitted
    only under a notice naming the outcome, BOTH results exactly, every trial that left or entered the pool, why,
    and who (docs/result_changes.json). A reversal of significance is named in the refusal as the withdrawal of a
    conclusion. A rebuilt page must not quietly re-render with a new number (esketamine, 2026-09-20)."""
    from harness import result_changes
    if not isinstance(base_review, dict) or not isinstance(new_review, dict):
        return []
    rows = notices.get("notices") if isinstance(notices, dict) else (notices if isinstance(notices, list) else [])
    rows = [n for n in (rows or []) if isinstance(n, dict)]
    new_by_name = {o.get("name"): o for o in new_review.get("outcomes") or [] if isinstance(o, dict)}
    out = []
    for o in base_review.get("outcomes") or []:
        if not isinstance(o, dict):
            continue
        name = o.get("name")
        n = new_by_name.get(name)
        if n is None:
            # the outcome itself is gone from the rebuilt review (lane V2 attempt A9-drop-outcome, 2026-09-21: a harm
            # outcome deleted from the topic config took its pooled rows with it and no refusal named them): a served
            # pooled result that DISAPPEARS is a result change -- admitted only under a notice naming the outcome, the
            # before tuple, an empty after, and every row that left
            base_pool = sorted(str(t.get("id")) for t in (o.get("trials") or []) if isinstance(t, dict))
            before = result_changes.result_tuple(o.get("result"))
            if not base_pool and not (before or {}).get("k"):
                continue
            if result_changes.notice_for(rows, slug, name, before, None, base_pool, []):
                continue
            out.append(
                f"outcome removed for {slug} / {name!r}: the served page pooled k {before.get('k')} "
                f"({', '.join(base_pool) or 'no rows'}) and the rebuilt review has no such outcome -- not acknowledged: "
                "docs/result_changes.json needs a notice naming slug, outcome, before, an empty after, every row in left_pool, "
                "reason, by, when_utc (a trial never leaves a served pool by the outcome vanishing)"
            )
            continue
        before, after = result_changes.result_tuple(o.get("result")), result_changes.result_tuple(n.get("result"))
        if result_changes._same(before, after):
            continue
        base_pool = sorted(str(t.get("id")) for t in (o.get("trials") or []) if isinstance(t, dict))
        new_pool = sorted(str(t.get("id")) for t in (n.get("trials") or []) if isinstance(t, dict))
        left = sorted(set(base_pool) - set(new_pool))
        entered = sorted(set(new_pool) - set(base_pool))
        if result_changes.notice_for(rows, slug, name, before, after, left, entered):
            continue
        scale = (o.get("result") or {}).get("scale") or o.get("estimand")
        change = result_changes.conclusion_changed(before, after, scale)
        out.append(
            f"result changed for {slug} / {name}: k {before.get('k')} -> {after.get('k')}, estimate "
            f"{before.get('estimate')} ({before.get('ci_low')} to {before.get('ci_high')}) -> {after.get('estimate')} "
            f"({after.get('ci_low')} to {after.get('ci_high')})"
            + (f"; {change}" if change else "")
            + f" (left the pool: {', '.join(left) or 'none'}; entered: {', '.join(entered) or 'none'}) -- not acknowledged: "
            "docs/result_changes.json needs a notice naming slug, outcome, before, after, left_pool and entered_pool "
            "exactly, reason, by, when_utc"
        )
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


def _base_reviews(root: str | os.PathLike[str], ref: str) -> tuple[list[str] | None, str | None]:
    p = _run(root, ["ls-tree", "-r", "--name-only", ref, "--", "docs/reviews"])
    if p.returncode != 0:
        return None, f"COULD-NOT-EXECUTE: cannot list base reviews at {ref}: {p.stderr.strip() or p.stdout.strip()}"
    out = []
    for line in p.stdout.splitlines():
        path = line.strip().replace("\\", "/")
        parts = path.split("/")
        if len(parts) == 4 and parts[0] == "docs" and parts[1] == "reviews" and parts[3] == "review.json":
            out.append(path)
    return sorted(out), None


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

    # Parity relation ratchet: the served relation in each committed review.json vs the working tree's.
    review_paths, err = _base_reviews(root, ref)
    if err:
        reasons.append(err)
    for rel in review_paths or []:
        base_raw, err = _show(root, ref, rel)
        if err:
            reasons.append(err)
            continue
        new_path = root_path.joinpath(*rel.split("/"))
        try:
            new_raw = new_path.read_text(encoding="utf-8") if new_path.exists() else ""
        except OSError as exc:
            reasons.append(f"COULD-NOT-EXECUTE: cannot read working-tree {rel}: {exc}")
            continue
        try:
            base_json = json.loads(base_raw or "null")
            new_json = json.loads(new_raw or "null")
        except json.JSONDecodeError as exc:
            reasons.append(f"COULD-NOT-EXECUTE: cannot parse {rel}: {exc}")
            continue
        slug = rel.split("/")[2]
        for violation in compare_parity(base_json, new_json, acknowledgements, slug):
            reasons.append(f"{rel}: {violation}")
        for violation in compare_results(base_json, new_json, _load_result_change_notices(root), slug):
            reasons.append(f"{rel}: {violation}")
        for violation in compare_screening(base_json, new_json, acknowledgements, slug):
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
