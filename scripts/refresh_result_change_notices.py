"""Refresh docs/result_changes.json from the objects: for every (slug, outcome) whose served result (at the base
commit) differs from the working tree's, a notice with before/after tuples, the rows that left/entered, interval
or pool-refusal notes, and a reason built from the set-aside records (specific reason first, mechanism after, the
surviving sentence last). Existing notices are kept where before/after/left/entered still match; a notice whose
numbers or rows changed is rebuilt and its countersignature reset to OPEN (a signature is on bytes; the bytes
moved). A notice with `reason_locked: true` keeps its hand-written reason. Notices for outcomes that no longer
differ are dropped. Run after every regeneration, before the census is read.

Usage: python scripts/refresh_result_change_notices.py <base_commit> [--by NAME] [--when UTC]
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import result_changes  # noqa: E402

PATH = ROOT / "docs" / "result_changes.json"
MECH = ("Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it "
        "aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong.")
CODE_WORD = {"ENDPOINT_UNBOUND": "set aside", "RESULT_INCOMPATIBLE": "refused", "KNOWN_REPORTED_NOT_YET_EXTRACTED": "set aside"}


def _before(commit, slug):
    p = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:docs/reviews/{slug}/review.json"], capture_output=True)
    return json.loads(p.stdout.decode("utf-8")) if p.returncode == 0 else None


def _after(slug):
    p = ROOT / "docs" / "reviews" / slug / "review.json"
    return json.load(open(p, encoding="utf-8")) if p.exists() else None


def _note(res):
    r = res or {}
    pr = r.get("pool_refused") or {}
    if pr.get("code"):
        return f"pool refused at k = {r.get('k')}, {pr['code']}: {pr.get('detail') or ''}".rstrip(": ")
    if r.get("suppressed_incompatible"):
        return f"pool suppressed: incompatible estimands, {r.get('scale')}"
    c = (r.get("pooled_ci_refused") or {}).get("code")
    return f"refused at k = {r.get('k')}, {c}" if c else None


def _fmt(row):
    """What this row contributes, as a number a reader can check -- never "no effect+CI".

    A reconstructed row carries no `effect`; its estimate lives in `study_effect`, with the arm
    counts beside it. Writing "no effect+CI" would describe the FIELD rather than the contribution
    and would leave a notice about a changed number that never states the new number.
    """
    e, lo, hi = row.get("effect"), row.get("ci_low"), row.get("ci_high")
    if e is not None:
        ci = f" ({lo} to {hi})" if lo is not None and hi is not None else ""
        return f"{row.get('scale') or ''} {e}{ci}".strip()
    se = row.get("study_effect") or {}
    est = se.get("effect_estimate")
    if est is not None:
        counts = ""
        if all(row.get(k) is not None for k in ("ai", "n1i", "ci", "n2i")):
            counts = f", reconstructed from {row['ai']}/{row['n1i']} vs {row['ci']}/{row['n2i']}"
        return f"{se.get('estimand') or row.get('scale') or ''} {est:.4g}{counts}".strip()
    return "no estimate"


def _estimator_substitutions(before_trials, after_trials):
    """Rows that stayed in the pool but whose NUMBER came from somewhere else than before.

    A pooled result can move with no trial leaving and none entering: the same trial contributes a
    different estimate because a different candidate was selected for it. That is what happened to
    spironolactone all-cause mortality -- J-EMPHASIS stopped contributing the CV-death/HHF composite
    HR it had been contributing and started contributing the mortality reconstruction from its own
    held counts, with k unchanged at 3.

    Without this, `_reason` saw an empty `left` list, had nothing specific to say, and emitted the
    shared mechanism sentence alone -- a notice whose stated reason belonged to a different landing
    and did not describe the change it was attached to.
    """
    b = {str(t.get("id")): t for t in before_trials or []}
    a = {str(t.get("id")): t for t in after_trials or []}
    out = []
    for tid in sorted(set(b) & set(a)):
        ob, oa = b[tid], a[tid]
        moved = tuple(ob.get(k) for k in ("effect", "ci_low", "ci_high", "scale")) != \
            tuple(oa.get(k) for k in ("effect", "ci_low", "ci_high", "scale"))
        if not moved:
            continue
        why = ""
        # The row records why a candidate it used to contribute is no longer eligible. Quote it:
        # a notice that reports a number changing without saying why is a changelog, not a notice.
        refusals = [r for r in (oa.get("endpoint_eligibility_refusals") or [])
                    if r not in (ob.get("endpoint_eligibility_refusals") or [])]
        if refusals:
            why = " The previously contributed candidate is no longer eligible: " + " ".join(refusals) + "."
        out.append(
            f"{tid} stayed in the pool but now contributes a different number: {_fmt(ob)} -> "
            f"{_fmt(oa)} (estimator selection {ob.get('selection_rule') or 'unrecorded'} -> "
            f"{oa.get('selection_rule') or 'unrecorded'}; source {ob.get('derivation') or '?'} -> "
            f"{oa.get('derivation') or '?'}).{why}"
        )
    return out


def _reason(left, absent, before_trials=None, after_trials=None):
    parts = []
    for tid in left:
        x = absent.get(tid) or {}
        code = x.get("reason_code") or x.get("state") or "ABSENT"
        why = (x.get("endpoint_binding_reason") or x.get("reason") or "").strip().rstrip(".")
        parts.append(f"{tid} {CODE_WORD.get(code, 'set aside')} ({code}): {why}.")
    parts += _estimator_substitutions(before_trials, after_trials)
    if not parts:
        # No trial left, none entered, and no row's number moved -- the result changed for a reason
        # this script cannot see. Say that, rather than attaching a mechanism sentence that happens
        # to be on hand: an unexplained notice is honest, a misattributed one is not.
        return ("The pooled result changed with no trial leaving or entering the pool and no "
                "individual row's estimate moving; the cause is not derivable from the review "
                "objects and has not been stated.")
    # The shared mechanism sentence belongs only to set-aside rows; it explains why a trial LEFT.
    return " ".join(parts) + ((" " + MECH) if left else "")


def refresh(commit, by, when, allow_signed_drop: bool = False):
    data = json.load(open(PATH, encoding="utf-8")) if PATH.exists() else {"_doc": "", "notices": []}
    old = {(n["slug"], n["outcome"]): n for n in data.get("notices", [])}
    new, kept, rebuilt, added, dropped = [], [], [], [], []
    for slug in sorted(os.listdir(ROOT / "docs" / "reviews")):
        b, a = _before(commit, slug), _after(slug)
        if not b or not a:
            continue
        an = {o["name"]: o for o in a["outcomes"]}
        for o in b["outcomes"]:
            n = an.get(o["name"])
            if n is None:
                continue
            tb, ta = result_changes.result_tuple(o.get("result")), result_changes.result_tuple(n.get("result"))
            if result_changes._same(tb, ta):
                continue
            bp = [t["id"] for t in o.get("trials") or []]
            ap = [t["id"] for t in n.get("trials") or []]
            left, entered = sorted(set(bp) - set(ap)), sorted(set(ap) - set(bp))
            absent = {x["id"]: x for x in n.get("declared_absent_trials") or []}
            key = (slug, o["name"])
            prev = old.get(key)
            same = (prev is not None and result_changes._same(prev.get("before"), tb) and result_changes._same(prev.get("after"), ta)
                    and sorted(map(str, prev.get("left_pool") or [])) == left and sorted(map(str, prev.get("entered_pool") or [])) == entered)
            notice = dict(prev) if prev else {"slug": slug, "outcome": o["name"]}
            notice.update({"before": tb, "after": ta, "left_pool": left, "entered_pool": entered})
            for k, v in (("before_note", _note(o.get("result"))), ("after_note", _note(n.get("result")))):
                if v:
                    notice[k] = v
                else:
                    notice.pop(k, None)
            if not same or not prev.get("reason"):
                if not notice.get("reason_locked"):
                    notice["reason"] = _reason(left, absent, o.get("trials"), n.get("trials"))
                notice["by"] = by
                notice["when_utc"] = when
                notice["reviewer_countersignature"] = {"state": "OPEN", "note": "the reviewer has not yet seen the rendered notice; "
                                                       "sign with scripts/countersign_result_change.py after reading it"}
                (rebuilt if prev else added).append(key)
            else:
                kept.append(key)
            if "reviewer_countersignature" not in notice:
                notice["reviewer_countersignature"] = {"state": "OPEN"}
            new.append(notice)
    for key in old:
        if key not in {(n["slug"], n["outcome"]) for n in new}:
            dropped.append(key)
    # A DROPPED SIGNED NOTICE IS NOT A REFRESH, IT IS A DELETION OF SOMEONE'S SIGNATURE.
    #
    # "Notices for outcomes that no longer differ are dropped" is correct against the base the
    # notices were built for. Against a LATER base it is catastrophic: once a change has landed, the
    # working tree no longer differs from that base, so every notice describing it becomes
    # droppable -- including its countersignature. Run with base=origin/main in a tree at
    # origin/main, this deleted all 13 of Mahmood's countersignatures from 2026-09-29 and printed
    # thirteen cheerful DROPPED lines while doing it (caught by hand, 2026-09-29; the file was
    # restored from git). Nothing in the output looked like a loss.
    #
    # So the refusal is on the SIGNATURE, not on the base: whatever base is passed, a notice a
    # reviewer has signed is not deleted by a tool run. Re-deriving it against the right base is
    # the fix; --drop-signed exists only so that a deliberate removal is a thing someone typed.
    signed_drops = []
    for key in dropped:
        state = ((old[key].get("reviewer_countersignature") or {}).get("state") or "").upper()
        if state.endswith("SIGNED"):
            signed_drops.append((key, state, (old[key].get("reviewer_countersignature") or {}).get("by")))
    if signed_drops and not allow_signed_drop:
        lines = [f"   {k[0]} | {k[1]}  ({state} by {by_who})" for k, state, by_who in signed_drops]
        raise SystemExit(
            f"REFUSED: this run would drop {len(signed_drops)} COUNTERSIGNED notice(s) and nothing "
            f"was written:\n" + "\n".join(lines) +
            f"\n\nA signed notice is only droppable against a base that predates the change it "
            f"describes. Base given: {commit}. Either pass the base those notices were derived "
            f"against, or, if the removal is intended, re-run with --drop-signed."
        )
    data["notices"] = new
    json.dump(data, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    open(PATH, "a", encoding="utf-8").write("\n")
    return kept, rebuilt, added, dropped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("base_commit")
    ap.add_argument("--by", default="Claude Opus 5 (lane m2/bind-hand-rows); reviewer countersignature owed: Mahmood")
    ap.add_argument("--when", default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    ap.add_argument("--drop-signed", action="store_true",
                    help="allow this run to delete notices a reviewer has countersigned "
                         "(refused by default; see the note in refresh())")
    args = ap.parse_args(argv)
    kept, rebuilt, added, dropped = refresh(args.base_commit, args.by, args.when, args.drop_signed)
    print(f"notices kept {len(kept)}, rebuilt {len(rebuilt)}, added {len(added)}, dropped {len(dropped)}")
    for tag, items in (("REBUILT", rebuilt), ("ADDED", added), ("DROPPED", dropped)):
        for k in items:
            print(f"  {tag} {k[0]} | {k[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
