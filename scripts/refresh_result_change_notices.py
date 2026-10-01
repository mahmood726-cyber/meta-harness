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
WRONG_QUANTITY = ("This is not a set-aside: the previously served number was the WRONG QUANTITY for this outcome, and is asserted wrong. The trial stays in the pool and contributes the quantity the outcome declares, read from the same held document.")
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
        # WHY THE SUBSTITUTE AND NOT THE PUBLISHED EFFECT. When a row falls back to a
        # reconstruction, the reader's next question is whether a published effect for this outcome
        # exists. The row already records the answer -- J-EMPHASIS carries
        # PUBLISHED_EFFECT_KNOWN_NOT_IN_COMMITTED_SOURCE: the published ITT mortality HR
        # 1.77 [0.81, 3.87] is KNOWN, cited, and simply not in the held bytes, so the row is not
        # switched until that span is committed. The served page shows this; the NOTICE did not, and
        # the notice is what a reviewer signs. A reviewer asked to countersign a reconstruction
        # without being told a published figure exists is being asked to sign an incomplete account.
        limits = ""
        for lim in (oa.get("source_hierarchy_limitations") or []):
            code, reason = lim.get("code"), (lim.get("reason") or "").strip()
            if code and reason:
                cite = lim.get("citation")
                limits += f" {code}: {reason}" + (f" ({cite})" if cite else "")
        out.append(
            f"{tid} stayed in the pool but now contributes a different number: {_fmt(ob)} -> "
            f"{_fmt(oa)} (estimator selection {ob.get('selection_rule') or 'unrecorded'} -> "
            f"{oa.get('selection_rule') or 'unrecorded'}; source {ob.get('derivation') or '?'} -> "
            f"{oa.get('derivation') or '?'}).{why}{limits}"
        )
    return out


def _entered(entered, after_trials):
    """Say what each ENTERING trial contributes and where the number was read.

    The original refresher had no clause for an entering trial, so a notice whose entered_pool listed one
    still said "no trial leaving or entering the pool" -- a false sentence on a notice a reviewer signs.
    """
    rows = {str(t.get("id")): t for t in after_trials or []}
    out = []
    for tid in entered:
        t = rows.get(str(tid)) or {}
        prov = t.get("provenance") or "unrecorded"
        where = ""
        if str(prov).startswith("pmc_fulltext"):
            where = " from its committed held full text"
        out.append(f"{tid} entered the pool contributing {_fmt(t)} (source {prov}{where}).")
    return out


def _refused_on_evidence(before_absent, after_absent):
    """Trials newly refused on evidence in this change, with the harness's own reason -- the named reasons a
    reviewer needs when a held document is admitted and some of what it yields is not poolable."""
    # Compare the KIND, not the id: a trial already absent for another reason (machine_absent) that is now
    # refused on evidence is a change a reviewer must be told about (probiotics PMID 39497860, 2026-10-01).
    was = {str(x.get("id")) for x in before_absent or [] if x.get("absent_kind") == "refused_on_evidence"}
    out = []
    for x in after_absent or []:
        if x.get("absent_kind") != "refused_on_evidence" or str(x.get("id")) in was:
            continue
        out.append(f"{x.get('id')} refused on evidence: {(x.get('reason') or '').strip().rstrip('.')}.")
    return out


ADDED_EVIDENCE = ("Entering trials are new evidence, not a correction: the previously served number is not asserted "
                  "wrong; it was computed without the held document(s) this topic now admits to pool construction.")


def _reason(left, absent, before_trials=None, after_trials=None, entered=None, before_absent=None,
            after_absent=None):
    parts = []
    for tid in left:
        x = absent.get(tid) or {}
        code = x.get("reason_code") or x.get("state") or "ABSENT"
        why = (x.get("endpoint_binding_reason") or x.get("reason") or "").strip().rstrip(".")
        parts.append(f"{tid} {CODE_WORD.get(code, 'set aside')} ({code}): {why}.")
    entered_parts = _entered(entered or [], after_trials)
    substitutions = _estimator_substitutions(before_trials, after_trials)
    parts += entered_parts + substitutions
    if parts:
        parts += _refused_on_evidence(before_absent, after_absent)
    if not parts:
        # No trial left, none entered, and no row's number moved -- the result changed for a reason
        # this script cannot see. Say that, rather than attaching a mechanism sentence that happens
        # to be on hand: an unexplained notice is honest, a misattributed one is not.
        return ("The pooled result changed with no trial leaving or entering the pool and no "
                "individual row's estimate moving; the cause is not derivable from the review "
                "objects and has not been stated.")
    # The shared mechanism sentence belongs only to set-aside rows; it explains why a trial LEFT.
    # It carries "the numbers are not asserted wrong", which is TRUE of a set-aside (the trial's
    # number could not be bound, so it is not challenged) and FALSE of a substitution (the served
    # number was the wrong quantity). Attaching it to a substitution would put a false sentence on
    # a served page, so a substitution gets the opposite statement, said plainly.
    # Each kind of change carries its own claim, and only its own: a set-aside is not asserted wrong; a
    # substitution IS asserted wrong; an entering trial is new evidence and asserts nothing about the old number.
    claims = []
    if left:
        claims.append(MECH)
    if entered_parts:
        claims.append(ADDED_EVIDENCE)
    if substitutions:
        claims.append(WRONG_QUANTITY)
    return " ".join(parts + claims)


def refresh(commit, by, when, allow_signed_drop: bool = False, prune: bool = False):
    data = json.load(open(PATH, encoding="utf-8")) if PATH.exists() else {"_doc": "", "notices": []}
    olds = list(data.get("notices", []))
    new, kept, rebuilt, added, dropped = [], [], [], [], []
    used = set()            # indices into `olds` that this run has accounted for

    def _signed(nt):
        return ((nt.get("reviewer_countersignature") or {}).get("state") or "").upper().endswith("SIGNED")

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
            # A NOTICE RECORDS ONE CHANGE FROM ONE BASE, AND A SIGNED NOTICE IS NEVER REWRITTEN.
            #
            # Notices used to be keyed one per (slug, outcome). A second change to an outcome whose notice
            # Mahmood had already signed therefore REBUILT that notice and reset its countersignature to OPEN
            # -- deleting a signature by overwriting it rather than dropping it (2026-10-01: omega3 MACE and
            # probiotics AAD, signed 2026-09-29, were both overwritten by the held-full-text enables). So the
            # notice this change updates is the one describing the SAME base (same `before`), and only if it is
            # unsigned. A signed notice for an earlier change is carried untouched and the new change gets a new
            # notice beside it.
            prev_i = next((i for i, nt in enumerate(olds)
                           if i not in used and (nt["slug"], nt["outcome"]) == key and not _signed(nt)
                           and result_changes._same(nt.get("before"), tb)), None)
            same_signed_i = next((i for i, nt in enumerate(olds)
                                  if i not in used and (nt["slug"], nt["outcome"]) == key and _signed(nt)
                                  and result_changes._same(nt.get("before"), tb) and result_changes._same(nt.get("after"), ta)), None)
            if same_signed_i is not None:
                # this exact change is already recorded and signed: carry it, byte for byte
                used.add(same_signed_i)
                new.append(olds[same_signed_i])
                kept.append(key)
                continue
            prev = olds[prev_i] if prev_i is not None else None
            if prev_i is not None:
                used.add(prev_i)
            same = (prev is not None and result_changes._same(prev.get("after"), ta)
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
                    notice["reason"] = _reason(left, absent, o.get("trials"), n.get("trials"), entered,
                                               o.get("declared_absent_trials"), n.get("declared_absent_trials"))
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
    # A NOTICE IS A HISTORICAL RECORD, NOT A DIFF AGAINST TODAY'S BASE.
    #
    # The original rule was "notices for outcomes that no longer differ are dropped". That is only
    # coherent if the whole file is derived against one base for all time. It is not: notices
    # accumulate across landings, each derived against the base current when its change was made.
    # So nothing is dropped automatically: every notice this run did not account for is carried forward
    # untouched, in its original position order. --prune drops UNSIGNED stale notices and names each one;
    # a signed notice additionally needs --drop-signed. The default cannot delete.
    carried = []
    old = {}
    for i, notice in enumerate(olds):
        if i in used:
            continue
        key = (notice["slug"], notice["outcome"])
        if prune and not _signed(notice):
            dropped.append(key)
            old[key] = notice
        else:
            carried.append(key)
            new.append(notice)
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
    return kept, rebuilt, added, dropped, carried


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("base_commit")
    ap.add_argument("--by", default="Claude Opus 5 (lane m2/bind-hand-rows); reviewer countersignature owed: Mahmood")
    ap.add_argument("--when", default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    ap.add_argument("--prune", action="store_true",
                    help="drop UNSIGNED notices whose outcome no longer differs from the base; "
                         "without it nothing is dropped at all")
    ap.add_argument("--drop-signed", action="store_true",
                    help="allow this run to delete notices a reviewer has countersigned "
                         "(refused by default; see the note in refresh())")
    args = ap.parse_args(argv)
    kept, rebuilt, added, dropped, carried = refresh(
        args.base_commit, args.by, args.when, args.drop_signed, args.prune)
    print(f"notices kept {len(kept)}, rebuilt {len(rebuilt)}, added {len(added)}, "
          f"carried forward {len(carried)}, dropped {len(dropped)}")
    for tag, items in (("REBUILT", rebuilt), ("ADDED", added), ("CARRIED", carried), ("DROPPED", dropped)):
        for k in items:
            print(f"  {tag} {k[0]} | {k[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
