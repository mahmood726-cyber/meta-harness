"""Verify reviewer countersignatures on the audited result-change notices, from COMMITTED bytes, and never write.

  python scripts/verify_notice_signatures.py [--ref REF] [--base REF] [--json OUT]

REF (default HEAD) is the commit to verify, e.g. origin/sign/mahmood-2026-09-25. BASE (default
origin/nr/notice-anchors) is the commit it was cut from: every file the signing commit changed other than
docs/result_changes.json is reported, since signing writes that file and nothing else.

For each of the audited notices (registry/notice_adjudication.json at REF) the verdict is one of:
  VALID    signed; the signature names this notice's current rendered-block sha256 AND its current judgement_id;
           the gate's own harness.result_changes.signature_problem accepts it; how_it_reached_the_reviewer is
           recorded; and the notice passes scripts/notice_anchor.guard (no DETACHED or STALE anchor).
  STALE    signed, but against a rendered sha256 or a judgement that is not the current one (e.g. a hash from
           before the re-judgement). It must be redone against the current notice; it is never re-pointed.
  REFUSED  signed, but the gate refuses it (signature_problem), or the notice fails the anchor guard.
  MISSING  not signed (OPEN).
REF's ledger and registry are read with `git show` (committed bytes, never the working copy). The pages and code
they are checked against are THIS tree's, so run it in a tree at REF's base: signing writes only the ledger, the
script refuses if REF's ledger differs from this tree's in anything but signatures, and it lists every other file
REF changed.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from harness import result_changes  # noqa: E402
from scripts import countersign_result_change as countersign  # noqa: E402
from scripts import notice_anchor  # noqa: E402

LEDGER = "docs/result_changes.json"
AUDIT = "registry/notice_adjudication.json"


def _show(ref: str, path: str) -> bytes:
    proc = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True)
    if proc.returncode != 0:
        raise SystemExit(f"refused: cannot read {ref}:{path}: {proc.stderr.decode(errors='replace').strip()}")
    return proc.stdout


# main's harness (ed0524d2, RAI-D7/C9) refuses a delegated bulk acceptance dressed as a countersignature; this
# branch's harness predates it, so the verifier applies the same test itself (values copied from main's
# harness/result_changes.py: DELEGATED_STATUS, DELEGATED_BASIS, DELEGATION_FIELDS).
_DELEGATED_STATUS = "DELEGATED_BULK_ACCEPTANCE"
_DELEGATED_BASIS = "Dispatch chat relay; blanket instruction; no item-by-item review"
_DELEGATION_FIELDS = ("status", "authorised_by", "instruction_text", "accepted_decision", "proposal_sha256")


def _delegated(sig: dict) -> str | None:
    if sig.get("state") == _DELEGATED_STATUS or sig.get("status") == _DELEGATED_STATUS:
        return "DELEGATED_IS_NOT_A_SIGNATURE: its state/status is the delegated-acceptance type"
    carried = [f for f in _DELEGATION_FIELDS if f in sig]
    if carried:
        return f"DELEGATED_IS_NOT_A_SIGNATURE: it carries the delegated-acceptance record's fields {carried}"
    if sig.get("how_it_reached_the_reviewer") == _DELEGATED_BASIS:
        return "DELEGATED_IS_NOT_A_SIGNATURE: its basis is the delegated-acceptance basis (no item-by-item review)"
    return None


def verify_ledger(ledger: list[dict], audit: dict) -> list[dict]:
    """The per-notice verdicts for a ledger (list of notices) against an audit registry. Pure: reads no ledger file."""
    rows = []
    for row in audit["notices"]:
        idx = next(i for i, n in enumerate(ledger) if all(n[k] == row[k] for k in ("slug", "outcome", "when_utc")))
        n = ledger[idx]
        sig = n.get("reviewer_countersignature") or {}
        _, block, sha = countersign._block_and_sha(n)
        judgement = notice_anchor.current_judgement(row)
        out = {"audit_id": row["audit_id"], "ledger_index": idx, "slug": n["slug"], "outcome": n["outcome"],
               "current_sha256": sha, "current_judgement": judgement["judgement_id"],
               "state": sig.get("state", "OPEN"), "by": sig.get("by"), "when_utc": sig.get("when_utc"),
               "signed_sha256": sig.get("rendered_sha256"), "signed_judgement": sig.get("judgement_id"),
               "how_it_reached_the_reviewer": sig.get("how_it_reached_the_reviewer")}
        if out["state"] not in result_changes.SIGNED_STATES:
            out["verdict"], out["why"] = "MISSING", "OPEN: not signed"
        elif sig.get("rendered_sha256") != sha or sig.get("judgement_id") != judgement["judgement_id"]:
            out["verdict"] = "STALE"
            out["why"] = (f"signed sha256 {sig.get('rendered_sha256')} / judgement {sig.get('judgement_id')}; "
                          f"current {sha} / {judgement['judgement_id']}")
        else:
            problem = result_changes.signature_problem(countersign._annotated(n), block)
            try:
                notice_anchor.guard(ROOT, row, n, block, sha)
                guard = None
            except notice_anchor.AnchorRefused as error:
                guard = str(error)
            delegated = _delegated(sig)
            if problem or guard or delegated:
                out["verdict"], out["why"] = "REFUSED", problem or guard or delegated
            else:
                out["verdict"], out["why"] = "VALID", ""
        rows.append(out)
    return rows


def verify(ref: str, base: str | None) -> dict:
    ledger = json.loads(_show(ref, LEDGER))["notices"]
    audit = json.loads(_show(ref, AUDIT))
    head_ledger = json.loads(countersign.PATH.read_bytes())["notices"]
    strip = lambda ns: [{k: v for k, v in n.items() if k != "reviewer_countersignature"} for n in ns]  # noqa: E731
    if strip(ledger) != strip(head_ledger):
        raise SystemExit("refused: the ledger at REF differs from this tree's in more than signatures; "
                         "check out REF's base and run again")
    rows = verify_ledger(ledger, audit)
    extra = []
    if base:
        proc = subprocess.run(["git", "diff", "--name-only", f"{base}...{ref}"], cwd=ROOT, capture_output=True,
                              text=True)
        extra = [p for p in proc.stdout.split() if p != LEDGER]
    audited = {r["ledger_index"] for r in rows}
    unaudited = [i for i, n in enumerate(ledger)
                 if (n.get("reviewer_countersignature") or {}) != (head_ledger[i].get("reviewer_countersignature") or {})
                 and i not in audited]
    return {"ref": ref, "rows": rows, "files_changed_besides_ledger": extra,
            "signature_changes_outside_the_audit": unaudited}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--base", default="origin/nr/notice-anchors")
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    result = verify(args.ref, args.base)
    counts = {}
    for r in result["rows"]:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    n = len(result["rows"])
    print(f"{args.ref}: {counts.get('VALID', 0)} of {n} VALID; STALE {counts.get('STALE', 0)}; "
          f"REFUSED {counts.get('REFUSED', 0)}; MISSING {counts.get('MISSING', 0)}")
    for r in result["rows"]:
        if r["verdict"] != "MISSING":
            print(f"  {r['verdict']:7} {r['audit_id']} {r['slug']} / {r['outcome']}: by {r['by']} {r['when_utc']}"
                  + (f" -- {r['why']}" if r["why"] else ""))
    if result["files_changed_besides_ledger"]:
        print("  FILES CHANGED BESIDES THE LEDGER: " + ", ".join(result["files_changed_besides_ledger"]))
    if result["signature_changes_outside_the_audit"]:
        print("  SIGNATURES CHANGED ON NOTICES OUTSIDE THE AUDIT (the 13 signed before 24 Sep): "
              + str(result["signature_changes_outside_the_audit"]))
    if args.json:
        Path(args.json).write_bytes((json.dumps(result, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
