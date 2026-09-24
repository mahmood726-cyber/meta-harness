"""Render queued model proposals for the reviewer, and record the reviewer's countersignature on the exact bytes rendered.

  render <task> <out.html> [--only-individual|--only-batchable]
        one page: every proposal block exactly as reproducible_ai.model_source.render_proposal_block renders it, each with its
        sha256 (what a signature names), the verifier's verdict and the rule/model agreement. Items that cannot be
        signed (verifier refused, record does not replay, no claim) are listed with the reason, never hidden.
  sign   <task> <item_id> --by NAME --basis TEXT [--batch BATCH_ID] [--when UTC]
        writes reviewer_countersignature {state, by, when_utc, rendered_sha256, how_it_reached_the_reviewer[, batch_id]}
        onto that queue entry. A proposal where rule and model disagree (or the model cannot tell) refuses --batch.
  sign-batch <task> --by NAME --basis TEXT --batch BATCH_ID
        signs every entry that (a) passes the verifier, (b) replays, and (c) AGREES with the rule -- nothing else.

This tool is for the REVIEWER to run. A signature the system applies to its own proposals is a password, not a
check. The signature discipline is harness.result_changes.signature_problem, reused unchanged. There is no state for
'agreed in advance', no timeout and no default.
"""
from __future__ import annotations

import argparse
import datetime
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import result_changes
from reproducible_ai import model_source as ms  # noqa: E402

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("_mh_pilot", ROOT / "scripts" / "model_source_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)


def _qpath(task):
    return ROOT / ms.PROPOSAL_DIR / f"{task}.json"


def _rec(e):
    p = ROOT / ms.RECORD_DIR / f"{e['record_id']}.json"
    return ms.load_record(p) if p.exists() else {}


def render(a):
    doc, rows = pilot.gated(a.task)
    parts, n_sig, n_not = [], 0, 0
    for e, status, problems in rows:
        if "claim" not in e:
            parts.append(f"<p class='muted'><code>{html.escape(e['item_id'])}</code>: {html.escape(str(e.get('state')))} (no proposal)</p>")
            n_not += 1
            continue
        indiv = ms.needs_individual_signature(e["verification"])
        if (a.only_individual and not indiv) or (a.only_batchable and indiv):
            continue
        rec = _rec(e)
        block = ms.render_proposal_block(e, rec)
        sha = result_changes.rendered_sha256(block)
        # the signable problems exclude only the countersignature itself (that is what the reviewer is being asked for)
        other = [p for p in (problems or []) if not p.startswith("COUNTERSIGNATURE")]
        head = (f"<p><b>{html.escape(e['item_id'])}</b> &mdash; block sha256 <code>{sha}</code> &mdash; "
                + ("<b>cannot be signed</b>: " + html.escape("; ".join(other)) if other else
                   ("INDIVIDUAL signature required" if indiv else "may be batch-signed")) + f" &mdash; now {status}</p>")
        parts.append(head + block)
        n_sig += 0 if other else 1
    page = ("<!doctype html><meta charset='utf-8'><title>Model proposals: " + html.escape(a.task) + "</title>"
            "<style>body{font:14px/1.45 system-ui;max-width:70em;margin:2em auto;padding:0 1em}th{text-align:left;"
            "vertical-align:top;padding-right:1em;white-space:nowrap}td{font-family:ui-monospace,monospace;font-size:12px}"
            ".model-proposal{border:1px solid #999;padding:.5em;margin:0 0 1.5em}.muted{color:#666}</style>"
            f"<h1>Model proposals &mdash; {html.escape(a.task)}</h1><p>N = {doc['N']} ({html.escape(doc['N_name'])}). "
            f"{n_sig} signable here, {n_not} with no proposal. Every block is PROPOSED model output; nothing is admitted "
            "by signing it in this landing. A signature names the sha256 printed above its block and nothing else.</p>"
            + "".join(parts))
    Path(a.out).write_text(page, encoding="utf-8")
    print(f"rendered {a.out}: {n_sig} signable, {n_not} without a proposal, N = {doc['N']}")


def _sign_one(doc_items, e, a, batch):
    rec = _rec(e)
    held = {i["item_id"]: i for i in pilot.pilot_items(a.task)}.get(e["item_id"], {}).get("held_text")
    if held is None:
        return f"refused: held text for {e['item_id']} is gone"
    other = [p for p in ms.gate_problems(e, rec, held) if not p.startswith("COUNTERSIGNATURE")]
    if other:
        return "refused: " + "; ".join(other)
    if batch and ms.needs_individual_signature(e["verification"]):
        return f"refused: rule and model do not agree ({e['verification'].get('agreement')}); a batch signature does not cover it"
    block = ms.render_proposal_block(e, rec)
    sig = {"state": "BATCH_SEEN_AND_SIGNED" if batch else "SEEN_AND_SIGNED", "by": a.by,
           "when_utc": a.when or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "rendered_sha256": result_changes.rendered_sha256(block), "how_it_reached_the_reviewer": a.basis.strip()}
    if batch:
        sig["batch_id"] = batch
    e["reviewer_countersignature"] = sig
    return None


def _write(doc, task):
    _qpath(task).write_bytes((json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii"))


def sign(a):
    if not a.basis.strip():
        sys.exit("refused: --basis is empty; a signature whose basis is not recorded is an override wearing a signature")
    doc = json.loads(_qpath(a.task).read_text(encoding="utf-8"))
    hits = [e for e in doc["items"] if e["item_id"] == a.item_id and "claim" in e]
    if len(hits) != 1:
        sys.exit(f"{len(hits)} proposals match {a.item_id!r}; name one")
    why = _sign_one(doc["items"], hits[0], a, a.batch)
    if why:
        sys.exit(why)
    _write(doc, a.task)
    print(f"signed {a.item_id}: {hits[0]['reviewer_countersignature']['state']} by {a.by}")


def sign_batch(a):
    if not a.basis.strip():
        sys.exit("refused: --basis is empty")
    doc = json.loads(_qpath(a.task).read_text(encoding="utf-8"))
    done, skipped = 0, 0
    for e in doc["items"]:
        if "claim" not in e or (e.get("reviewer_countersignature") or {}).get("state") != "OPEN":
            continue
        if _sign_one(doc["items"], e, a, a.batch):
            skipped += 1
        else:
            done += 1
    _write(doc, a.task)
    print(f"batch {a.batch}: signed {done}; left OPEN {skipped} (disagreement, cannot tell, or not signable)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render"); r.add_argument("task"); r.add_argument("out")
    r.add_argument("--only-individual", action="store_true"); r.add_argument("--only-batchable", action="store_true")
    r.set_defaults(fn=render)
    s = sub.add_parser("sign"); s.add_argument("task"); s.add_argument("item_id")
    s.add_argument("--by", required=True); s.add_argument("--basis", required=True)
    s.add_argument("--batch"); s.add_argument("--when"); s.set_defaults(fn=sign)
    b = sub.add_parser("sign-batch"); b.add_argument("task")
    b.add_argument("--by", required=True); b.add_argument("--basis", required=True)
    b.add_argument("--batch", required=True); b.add_argument("--when"); b.set_defaults(fn=sign_batch)
    a = ap.parse_args(argv)
    a.fn(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
