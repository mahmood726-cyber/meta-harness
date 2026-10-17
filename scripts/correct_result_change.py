"""Draft direction corrections without rewriting signed records; render drafts for review.

Usage: correct_result_change.py draft SLUG OUTCOME --by NAME --when UTC
       correct_result_change.py render SLUG OUTCOME --out-dir DIRECTORY
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import page, result_changes as rc
from scripts.countersign_result_change import _annotated


def draft(path, slug, outcome, by, when):
    raw = path.read_bytes()
    data = json.loads(raw)
    originals = data["notices"]
    corrections = []
    for n in originals:
        if n["slug"] != slug or n["outcome"] != outcome:
            continue
        if (n.get("reviewer_countersignature") or {}).get("state") not in rc.SIGNED_STATES:
            continue
        ann = _annotated(n)
        if rc.direction_sentence(n["before"], n["after"], ann["scale"]) != "The direction of the estimate is changed.":
            continue
        if "The direction of the estimate is unchanged." not in page.result_change_block(ann):
            continue
        corrections.append(rc.direction_correction(ann, by, when))
    if not corrections:
        raise ValueError("no false signed direction sentences found")
    # Append a separate top-level field. The entire pre-existing JSON payload, including
    # whitespace and original record bytes, remains byte-identical (except the final brace).
    if "corrections" in data:
        if {json.dumps(c["corrects"], sort_keys=True) for c in data["corrections"]} == {
                json.dumps(c["corrects"], sort_keys=True) for c in corrections}:
            return data["corrections"]
        raise ValueError("corrections already exist; refusing to overwrite them")
    end = raw.rfind(b"}")
    appended = (raw[:end].rstrip() + b',\n "corrections": '
                + json.dumps(corrections, indent=1, ensure_ascii=False).encode("utf-8") + b"\n" + raw[end:])
    assert json.loads(appended)["notices"] == originals
    assert appended.startswith(raw[:end].rstrip())
    path.write_bytes(appended)
    return corrections


def render(path, slug, outcome, out_dir):
    data = json.loads(path.read_bytes())
    out_dir.mkdir(parents=True, exist_ok=True)
    for c in data.get("corrections", []):
        ref = c["corrects"]
        if ref["slug"] != slug or ref["outcome"] != outcome:
            continue
        n, = [n for n in data["notices"] if all(n[k] == ref[k] for k in ("slug", "outcome", "when_utc"))]
        block = page.correction_block(c, _annotated(n))
        sha = rc.rendered_sha256(block.split("<p class='muted'>Reviewer countersignature")[0])
        dest = out_dir / ("correction-" + ref["when_utc"][:10] + ".html")
        dest.write_text("<!doctype html><meta charset='utf-8'><title>Correction draft</title>" + block,
                        encoding="utf-8")
        print(f"{dest.name}: rendered_sha256 {sha}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=("draft", "render"))
    ap.add_argument("slug")
    ap.add_argument("outcome")
    ap.add_argument("--by")
    ap.add_argument("--when")
    ap.add_argument("--out-dir", type=Path)
    a = ap.parse_args()
    path = ROOT / rc.PATH
    if a.action == "draft":
        if not a.by or not a.when:
            ap.error("draft requires --by and --when")
        print(f"Drafted {len(draft(path, a.slug, a.outcome, a.by, a.when))} OPEN corrections")
    else:
        if not a.out_dir:
            ap.error("render requires --out-dir")
        render(path, a.slug, a.outcome, a.out_dir)


if __name__ == "__main__":
    main()
