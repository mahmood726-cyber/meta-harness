"""Render a result-change notice standalone for the reviewer, and record the reviewer's countersignature on the
exact bytes rendered.

  render  <slug> <outcome-substring> <out.html>        -> one page: the notice block exactly as the review page
                                                          renders it, and its sha256 (what a signature will name)
  sign    <slug> <outcome-substring> --by NAME --basis TEXT [--batch BATCH_ID] [--when UTC]
                                                       -> writes reviewer_countersignature {state, by, when_utc,
                                                          rendered_sha256, how_it_reached_the_reviewer[, batch_id]}
                                                          for that notice (--basis: the rendered block itself, or a
                                                          relay and what the relay conveyed), state
                                                          SEEN_AND_SIGNED (or BATCH_SEEN_AND_SIGNED with --batch);
                                                          a withdrawn conclusion refuses --batch

The signature names sha256 of the rendered block (harness.result_changes.rendered_sha256); the gate recomputes it
from the served review object, so a signature covers the words and numbers the reviewer saw and nothing else.
There is no state for 'agreed in advance'.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import page, result_changes  # noqa: E402

PATH = ROOT / "docs" / "result_changes.json"


def _notice(slug: str, outcome_sub: str):
    data = json.load(open(PATH, encoding="utf-8"))
    hits = [n for n in data["notices"] if n["slug"] == slug and outcome_sub.lower() in n["outcome"].lower()]
    if len(hits) != 1:
        sys.exit(f"{len(hits)} notices match {slug} / {outcome_sub!r}; name one")
    return data, hits[0]


def _annotated(n):
    rev_path = ROOT / "docs" / "reviews" / n["slug"] / "review.json"
    scale = None
    if rev_path.exists():
        rev = json.load(open(rev_path, encoding="utf-8"))
        scale = next(((o.get("result") or {}).get("scale") or o.get("estimand") for o in rev.get("outcomes") or []
                      if o.get("name") == n["outcome"]), None)
    item = dict(n)
    item["conclusion_changed"] = result_changes.conclusion_changed(n.get("before") or {}, n.get("after") or {}, scale)
    return item


def _block_and_sha(n):
    html = page.result_change_block(_annotated(n))
    block = html[:html.rfind("<p class='muted'>Reviewer countersignature")]
    return html, block, result_changes.rendered_sha256(block)


def render(args):
    _, n = _notice(args.slug, args.outcome)
    html, block, sha = _block_and_sha(n)
    doc = ("<!doctype html><meta charset='utf-8'><title>Result-change notice</title>"
           "<style>body{font:15px/1.5 system-ui;max-width:60em;margin:2em auto;padding:0 1em}"
           ".banner{border:2px solid #b00;padding:1em;background:#fff6f6}.muted{color:#555}code{font-size:.9em}</style>"
           f"<p class='muted'>Review <code>{n['slug']}</code> &mdash; the notice exactly as the page renders it. "
           f"Signing names sha256 <code>{sha}</code> of the block below (nothing else).</p>" + html)
    Path(args.out).write_text(doc, encoding="utf-8")
    print(f"rendered {args.out}; block sha256 {sha}")


def sign(args):
    data, n = _notice(args.slug, args.outcome)
    _, block, sha = _block_and_sha(n)
    ann = _annotated(n)
    if args.batch and ann.get("conclusion_changed"):
        sys.exit(f"refused: this notice withdraws a conclusion ({ann['conclusion_changed']}); a batch signature does not cover it")
    sig = {"state": "BATCH_SEEN_AND_SIGNED" if args.batch else "SEEN_AND_SIGNED", "by": args.by,
           "when_utc": args.when or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "rendered_sha256": sha, "how_it_reached_the_reviewer": args.basis.strip()}
    if not sig["how_it_reached_the_reviewer"]:
        sys.exit("refused: --basis is empty; a signature whose basis is not recorded is an override wearing a signature")
    if args.batch:
        sig["batch_id"] = args.batch
    n["reviewer_countersignature"] = sig
    json.dump(data, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    open(PATH, "a", encoding="utf-8").write("\n")
    print(f"signed {n['slug']} / {n['outcome']}: {sig['state']} by {sig['by']} on {sig['when_utc']} over sha256 {sha[:12]}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("slug"); r.add_argument("outcome"); r.add_argument("out")
    r.set_defaults(fn=render)
    g = sub.add_parser("sign")
    g.add_argument("slug"); g.add_argument("outcome"); g.add_argument("--by", required=True)
    g.add_argument("--basis", required=True, help="how the notice reached the reviewer: the rendered block, or a relay and what it conveyed")
    g.add_argument("--batch"); g.add_argument("--when")
    g.set_defaults(fn=sign)
    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
