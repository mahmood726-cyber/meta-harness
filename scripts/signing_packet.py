"""Build a signing packet from the OPEN result-change notices, and guard any packet before it is sent.

  build  --title TITLE --out outputs/SIGNING_PACKET_<V>_<date>.md     every OPEN notice, rendered by the page's own
                                                                    renderer, headed by the full rendered_sha256 its
                                                                    signature will name; split BATCHABLE / INDIVIDUAL
                                                                    by result_changes.conclusion_changed (the tool's
                                                                    annotation, never the author's opinion); writes
                                                                    <out>.sha256 beside it
  guard  <packet.md>                                                exit 0 only if every entry passes; exit 1 names
                                                                    every refusal

The guard is the check a packet must pass before it is relayed (it replaces packet_guard.py, cited by main's
65acd80 but never committed). For each entry it requires, against docs/result_changes.json and the served review
objects of THIS tree:
  1. a derived notice for that slug and outcome whose rendered_sha256, recomputed here, equals the hash printed beside
     the block. No such notice -> "NO DERIVED NOTICE" (the MAIN-14 case: v1 presented a hand-built record);
  2. the block's visible text equals the visible text of that rendering, exactly (so the reviewer reads the bytes
     the signature names, not a paraphrase);
  3. the entry sits in the section its own annotation dictates: a withdrawn or changed conclusion is INDIVIDUAL;
  4. the notice is OPEN (a packet never re-presents a signed notice), and no notice appears twice;
  5. <packet>.sha256 matches the packet's bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import html as _html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from harness import page, result_changes  # noqa: E402

ENTRY = re.compile(r"^### (?P<id>\S+) — (?P<slug>[^/\n]+?) / (?P<outcome>.+?)\s*$", re.M)
SHA_LINE = re.compile(r"`rendered_sha256 ([0-9a-f]{64})`")
SECTION = re.compile(r"^## (?P<sec>[AB])\. ", re.M)


def _notices(root: Path) -> list[dict]:
    return json.load(open(root / "docs" / "result_changes.json", encoding="utf-8"))["notices"]


def _scale(root: Path, slug: str, outcome: str):
    p = root / "docs" / "reviews" / slug / "review.json"
    if not p.exists():
        return None
    rev = json.load(open(p, encoding="utf-8"))
    return next(((o.get("result") or {}).get("scale") or o.get("estimand") for o in rev.get("outcomes") or []
                 if o.get("name") == outcome), None)


def annotated(root: Path, n: dict) -> dict:
    item = dict(n)
    item["conclusion_changed"] = result_changes.conclusion_changed(
        n.get("before") or {}, n.get("after") or {}, _scale(root, n["slug"], n["outcome"]))
    return item


def block_and_sha(root: Path, n: dict) -> tuple[str, str, dict]:
    """The hashed block exactly as countersign_result_change.py and the gate compute it."""
    ann = annotated(root, n)
    full = page.result_change_block(ann)
    block = full[:full.rfind("<p class='muted'>Reviewer countersignature")]
    return block, result_changes.rendered_sha256(block), ann


def visible_text(block_html: str) -> str:
    t = re.sub(r"<h4>.*?</h4>", " ", block_html, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return " ".join(_html.unescape(t).split())


def _signed(n: dict) -> bool:
    return ((n.get("reviewer_countersignature") or {}).get("state") or "").upper().endswith("SIGNED")


def build(root: Path, title: str, out: Path, base_note: str) -> str:
    open_notices = [n for n in _notices(root) if not _signed(n)]
    batch, individual = [], []
    for n in open_notices:
        block, sha, ann = block_and_sha(root, n)
        (individual if ann.get("conclusion_changed") else batch).append((n, block, sha, ann))
    lines = [f"# {title}", "",
             "Every block below is the FULL visible text of a result-change notice as the review page renders it, "
             "headed by the full `rendered_sha256` a signature on it will name. Nothing elided. Split by the "
             "harness's own `conclusion_changed` annotation: a changed or withdrawn conclusion takes its own line.",
             "", base_note, ""]
    k = 0

    def entry(n, block, sha, ann, individual_line):
        nonlocal k
        k += 1
        eid = f"V3-{k:02d}"
        lines.extend([f"### {eid} — {n['slug']} / {n['outcome']}", ""])
        if ann.get("conclusion_changed"):
            lines.extend([f"**Cannot be batched:** {ann['conclusion_changed']}", ""])
        lines.extend([f"`rendered_sha256 {sha}`", "", visible_text(block), ""])
        if individual_line:
            lines.extend(["```", f"SIGNED-BY: Mahmood  NOTICE: {eid}  SHA256: {sha}  DATE: ____", "```", ""])
        return eid

    lines.extend([f"## A. BATCHABLE — {len(batch)} decision(s), one signature line → `BATCH_SEEN_AND_SIGNED`", ""])
    ids = [entry(n, b, s, a, False) for n, b, s, a in batch]
    if ids:
        lines.extend(["```", f"SIGNED-BY: Mahmood  BATCH: v3-A  COVERS: {', '.join(ids)}  DATE: ____", "```", ""])
    lines.extend([f"## B. INDIVIDUAL — {len(individual)} decision(s), each its own line → `SEEN_AND_SIGNED`", ""])
    for n, b, s, a in individual:
        entry(n, b, s, a, True)
    text = "\n".join(lines).rstrip() + "\n"
    out.write_bytes(text.encode("utf-8"))
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    Path(str(out) + ".sha256").write_text(f"{digest} *{out.name}\n", encoding="utf-8")
    return digest


def guard(root: Path, packet: Path) -> list[str]:
    raw = packet.read_bytes()
    text = raw.decode("utf-8")
    problems = []
    side = Path(str(packet) + ".sha256")
    if not side.exists():
        problems.append(f"{side.name} missing: a packet without its digest cannot be named in a signature")
    elif side.read_text(encoding="utf-8").split()[0] != hashlib.sha256(raw).hexdigest():
        problems.append(f"{side.name} does not match the packet's bytes")
    notices = _notices(root)
    sections = [(m.start(), m.group("sec")) for m in SECTION.finditer(text)]
    entries = list(ENTRY.finditer(text))
    if not entries:
        problems.append("the packet contains no entries")
    seen = set()
    for i, m in enumerate(entries):
        eid, slug, outcome = m.group("id"), m.group("slug").strip(), m.group("outcome").strip()
        end = min([entries[i + 1].start() if i + 1 < len(entries) else len(text)]
                  + [p for p, _ in sections if p > m.start()])
        body = text[m.end():end]
        sec = next((s for p, s in reversed(sections) if p < m.start()), None)
        sm = SHA_LINE.search(body)
        if not sm:
            problems.append(f"{eid}: no full rendered_sha256 line"); continue
        printed = sm.group(1)
        cands = [n for n in notices if n["slug"] == slug and n["outcome"] == outcome]
        if not cands:
            problems.append(f"{eid} {slug} / {outcome}: NO DERIVED NOTICE in docs/result_changes.json -- nothing to sign")
            continue
        match = None
        for n in cands:
            block, sha, ann = block_and_sha(root, n)
            if sha == printed:
                match = (n, block, ann)
        if match is None:
            problems.append(f"{eid} {slug} / {outcome}: printed rendered_sha256 {printed[:12]} matches no derived "
                            f"notice for this outcome (recomputed: {[block_and_sha(root, n)[1][:12] for n in cands]})")
            continue
        n, block, ann = match
        if _signed(n):
            problems.append(f"{eid}: the notice is already {n['reviewer_countersignature']['state']}; a packet never "
                            "re-presents a signed notice")
        if printed in seen:
            problems.append(f"{eid}: the same notice appears twice")
        seen.add(printed)
        want = visible_text(block)
        if want not in " ".join(body.split()):
            problems.append(f"{eid}: the block text differs from the rendering the signature names")
        if ann.get("conclusion_changed") and sec != "B":
            problems.append(f"{eid}: {ann['conclusion_changed']} -- a changed conclusion must be INDIVIDUAL (section B), "
                            f"not section {sec}")
        if not ann.get("conclusion_changed") and sec != "A":
            problems.append(f"{eid}: no conclusion change, so it belongs in BATCHABLE (section A), not section {sec}")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--title", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--base-note", default="")
    g = sub.add_parser("guard")
    g.add_argument("packet")
    a = ap.parse_args(argv)
    if a.cmd == "build":
        d = build(ROOT, a.title, Path(a.out), a.base_note)
        problems = guard(ROOT, Path(a.out))
        print(f"wrote {a.out}  sha256 {d}")
        for p in problems:
            print("  GUARD REFUSED --", p)
        return 1 if problems else 0
    problems = guard(ROOT, Path(a.packet))
    if problems:
        for p in problems:
            print("GUARD REFUSED --", p)
        return 1
    print(f"GUARD PASS -- {a.packet}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
