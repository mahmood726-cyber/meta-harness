"""Result-change notices: a served pooled result that changes is a CLAIM about the previous claim.

A rebuild that moves an outcome's k or estimate -- or removes the estimate entirely -- must not re-render
quietly. docs/result_changes.json holds one notice per (slug, outcome) change: the served result, the new result,
every trial that left or entered the pool, why, who. The page renders the notice beside the outcome; the honest
ratchet (honest_ratchet.compare_results) refuses a landing whose committed review.json result differs from the
served one without an exact notice. A reversal of significance (an interval that now includes the null) is a
withdrawal of a conclusion and the notice says so in its own words (`conclusion_changed`).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join("docs", "result_changes.json")
REQUIRED = ("slug", "outcome", "before", "after", "left_pool", "entered_pool", "reason", "by", "when_utc")
RESULT_KEYS = ("k", "estimate", "ci_low", "ci_high")


def load(root: str | None = None) -> list[dict[str, Any]]:
    p = os.path.join(root or ROOT, PATH)
    if not os.path.exists(p):
        return []
    data = json.load(open(p, encoding="utf-8"))
    rows = data.get("notices") if isinstance(data, dict) else data
    return [r for r in (rows or []) if isinstance(r, dict)]


def result_tuple(result: dict[str, Any] | None) -> dict[str, Any]:
    r = result or {}
    return {k: r.get(k) for k in RESULT_KEYS}


def _same(a: dict[str, Any] | None, b: dict[str, Any] | None) -> bool:
    a, b = a or {}, b or {}
    for k in RESULT_KEYS:
        x, y = a.get(k), b.get(k)
        if x is None or y is None:
            if x is not y:
                return False
            continue
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            if abs(float(x) - float(y)) > 1e-6:
                return False
        elif x != y:
            return False
    return True


def null_value(scale: str | None) -> float:
    return 1.0 if str(scale or "").upper() in ("HR", "RR", "OR", "IRR", "RATE_RATIO") else 0.0


def significance(result: dict[str, Any] | None, scale: str | None) -> str | None:
    """'benefit' / 'harm' / 'includes_null' from an interval, or None when there is no interval."""
    r = result or {}
    lo, hi = r.get("ci_low"), r.get("ci_high")
    if lo is None or hi is None:
        return None
    null = null_value(scale)
    if lo > null or hi < null:
        return "excludes_null"
    return "includes_null"


def conclusion_changed(before: dict[str, Any], after: dict[str, Any], scale: str | None) -> str | None:
    """The derived sentence, or None when the direction is preserved. Losing a served estimate -- k -> 0, or a
    pool refused where one was served -- is a withdrawal; a pooled estimate appearing where none was served is a
    new claim; both take a per-notice signature."""
    b, a = significance(before, scale), significance(after, scale)
    if before.get("estimate") is not None and after.get("estimate") is None:
        return "the outcome no longer has a pooled estimate"
    if before.get("k") and not after.get("k"):
        return "the outcome no longer has a pooled estimate"
    if before.get("estimate") is None and after.get("estimate") is not None:
        return "a pooled estimate is now served where none was served before: a new claim, not a continuation"
    if b == "excludes_null" and a == "includes_null":
        return "the interval now includes the null: the previous conclusion of a difference is withdrawn"
    if b == "includes_null" and a == "excludes_null":
        return "the interval now excludes the null: a difference is now claimed that was not before"
    return None


def not_applied(n: dict[str, Any]) -> bool:
    """A notice kept on the record but never applied: withdrawn by its signer, or superseded by a later notice."""
    return (n.get("withdrawal") or {}).get("state") == "WITHDRAWN_BY_SIGNER" or bool((n.get("superseded_by") or {}).get("notice"))


def _instant(t: Any):
    """A notice's when_utc as an aware datetime (UTC 'Z' or an offset, fractional seconds allowed), or None."""
    import datetime as _dt
    try:
        d = _dt.datetime.fromisoformat(str(t).strip().replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return d if d.tzinfo else None


def reversed_setasides(n: dict[str, Any], notices: list[dict[str, Any]]) -> dict[str, dict[str, Any]] | None:
    """A REINSTATEMENT (V8-06, 7 Oct): every trial this notice enters was SET ASIDE by an earlier signed, applied notice
    for the same outcome ('eligible evidence awaiting adjudication'), and this notice is that adjudication, reversing it by
    name. {trial id: the set-aside notice} when that holds for EVERY entering trial and the reason says it REVERSES the
    set-aside and names each trial; None otherwise. A reinstatement claims nothing about the old number: the set-aside
    already said it was not asserted wrong, and the old pool lacked this trial only because it was set aside."""
    ent = [str(t) for t in n.get("entered_pool") or []]
    reason = str(n.get("reason") or "")
    if not ent or n.get("left_pool") or "REVERSES" not in reason or "set-aside" not in reason:
        return None
    out = {}
    for tid in ent:
        # the trial is NAMED, not merely a substring of another id ('TRIAL-1' inside 'TRIAL-10'; codex v8-apply #2)
        if not re.search(r"(?<![\w-])" + re.escape(tid) + r"(?![\w-])", reason):
            return None
        # the notice being reversed is the LATEST earlier signed, applied notice that MOVED this trial (in or out) for the
        # same outcome -- not any qualifying set-aside in its history (codex v8-apply-r3 #2: set aside, reinstated, then
        # excluded as ineligible must not reinstate again)
        # times are compared as instants, never as strings ('...00Z' sorts after '...00.500Z'; codex v8-apply-r4 #2);
        # a notice whose time cannot be parsed makes the question unanswerable, so it refuses
        t_n = _instant(n.get("when_utc"))
        cands = [p for p in notices if p is not n and p.get("slug") == n.get("slug") and p.get("outcome") == n.get("outcome")
                 and tid in [str(x) for x in (p.get("left_pool") or []) + (p.get("entered_pool") or [])]
                 and not not_applied(p)
                 and (p.get("reviewer_countersignature") or {}).get("state") in ("SEEN_AND_SIGNED", "BATCH_SEEN_AND_SIGNED")]
        if t_n is None or any(_instant(p.get("when_utc")) is None for p in cands):
            return None
        if any(_instant(p.get("when_utc")) >= t_n for p in cands):
            return None        # another signed movement at (or after) this instant: the order is unknown (codex r6 #2)
        moved = [p for p in cands if _instant(p.get("when_utc")) < t_n]
        if not moved:
            return None
        latest = max(_instant(x.get("when_utc")) for x in moved)
        tied = [x for x in moved if _instant(x.get("when_utc")) == latest]
        if len(tied) != 1:
            return None        # two movements at the same instant: the order is unknown, so refuse (codex r5 #1)
        p = tied[0]
        reason_p = str(p.get("reason") or "")
        # ... and it must be a SET-ASIDE of THIS trial: a correction that removed an ineligible trial is not reversible
        # this way (codex v8-signing g1#1). The claim must belong to this trial: a notice that moved several trials and
        # names any of them as ineligible / wrong never reinstates by another trial's set-aside wording (codex r5 #2)
        # STRUCTURE, not wording: the reversed notice must have moved exactly ONE trial -- this one -- so its claim can
        # only be about this trial (codex r5 #2, r6 #1: a reason covering several trials cannot be attributed by text)
        if [str(x) for x in p.get("left_pool") or []] != [tid] or (p.get("entered_pool") or []) \
                or "eligible evidence awaiting adjudication" not in reason_p \
                or "the numbers are not asserted wrong" not in reason_p \
                or "asserted wrong" in reason_p.replace("not asserted wrong", "") \
                or "ineligible" in reason_p.lower() or "correction" in reason_p.lower():
            return None
        out[tid] = p
    return out


def notice_for(notices: list[dict[str, Any]], slug: str, outcome: str, before: dict[str, Any] | None,
               after: dict[str, Any] | None, left: list[str], entered: list[str]) -> dict[str, Any] | None:
    """The one notice that names this change EXACTLY (both results, every row that moved), or None."""
    for n in notices:
        if any(k not in n for k in REQUIRED):
            continue
        if not_applied(n):
            continue        # withdrawn by its signer, or superseded: on the record, never admits a change
        if not all(isinstance(n[k], str) and n[k].strip() for k in ("slug", "outcome", "reason", "by", "when_utc")):
            continue
        if n["slug"] != slug or n["outcome"] != outcome:
            continue
        if not (_same(n["before"], result_tuple(before)) and _same(n["after"], result_tuple(after))):
            continue
        if sorted(map(str, n["left_pool"])) != sorted(left) or sorted(map(str, n["entered_pool"])) != sorted(entered):
            continue
        return n
    return None


# ----------------------------------------------------------------------------- reviewer countersignature
SIGNATURE_STATES = ("OPEN", "SEEN_AND_SIGNED", "BATCH_SEEN_AND_SIGNED")
SIGNED_STATES = ("SEEN_AND_SIGNED", "BATCH_SEEN_AND_SIGNED")

# A DELEGATED BULK ACCEPTANCE is a different TYPE of record from a countersignature: a blanket instruction, recorded as
# such, with no item-by-item review (reproducible_ai/delegated.py writes it and imports this definition). It is never a
# signature, whatever state it is dressed in: the gate refuses it by its type -- its status, the fields only that type
# carries, and the basis it records -- never by matching words a human might also use in an honest relayed signature.
DELEGATED_STATUS = "DELEGATED_BULK_ACCEPTANCE"
DELEGATED_BASIS = "Dispatch chat relay; blanket instruction; no item-by-item review"
DELEGATION_FIELDS = ("status", "authorised_by", "instruction_text", "accepted_decision", "proposal_sha256")


def _delegation_problem(sig: Any, notice: dict[str, Any]) -> str | None:
    """Why a countersignature is in fact a delegated acceptance, or None."""
    if not isinstance(sig, dict):
        return None
    if sig.get("state") == DELEGATED_STATUS or sig.get("status") == DELEGATED_STATUS:
        return "its state/status is the delegated-acceptance type"
    carried = [f for f in DELEGATION_FIELDS if f in sig]
    if carried:
        return f"it carries the delegated-acceptance record's own fields {carried}"
    if sig.get("how_it_reached_the_reviewer") == DELEGATED_BASIS:
        return "its recorded basis is the delegated-acceptance basis (a blanket instruction, no item-by-item review)"
    return None


def rendered_sha256(block_html: str) -> str:
    """The identity of what the reviewer saw: the rendered notice block, whitespace-normalised."""
    return hashlib.sha256(" ".join(block_html.split()).encode("utf-8")).hexdigest()


def signature_problem(notice: dict[str, Any], block_html: str) -> str | None:
    """None when this notice may publish; else why not. A signature is an act on bytes: it must name the sha256
    of the rendered block it was given, the signer, the time, its kind, and how the notice reached the reviewer
    (how_it_reached_the_reviewer: the rendered block itself, or a relay and what the relay conveyed -- a signature
    whose basis is recorded is honest even when the basis is a relay; one that hides the relay is the defect). A conclusion change (withdrawal) accepts
    a per-notice signature only -- never a batch, never 'authorised in principle', which is not a state at all."""
    sig = notice.get("reviewer_countersignature")
    if not isinstance(sig, dict):
        return "reviewer_countersignature missing: the notice has not been put in front of the reviewer"
    why = _delegation_problem(sig, notice)
    if why:
        return (f"DELEGATED_IS_NOT_A_SIGNATURE: {why}. A delegated bulk acceptance is recorded as its own status and "
                "can never publish a notice that needs a human countersignature")
    state = sig.get("state")
    if state not in SIGNATURE_STATES:
        return f"reviewer_countersignature.state {state!r} is not a recognised act (OPEN / SEEN_AND_SIGNED / BATCH_SEEN_AND_SIGNED)"
    if state == "OPEN":
        return "reviewer_countersignature OPEN: the reviewer has not seen the rendered notice"
    for k in ("by", "when_utc", "rendered_sha256", "how_it_reached_the_reviewer"):
        if not isinstance(sig.get(k), str) or not sig[k].strip():
            return (f"reviewer_countersignature.{k} missing" + (": a signature whose basis is not recorded is an override "
                    "wearing a signature -- say whether the reviewer read the rendered block or a relay of it, and what "
                    "the relay conveyed" if k == "how_it_reached_the_reviewer" else ""))
    if sig["rendered_sha256"] != rendered_sha256(block_html):
        return ("reviewer_countersignature names a rendered notice that is not this one (sha256 mismatch): the "
                "reviewer saw different words or numbers")
    if notice.get("conclusion_changed") and state != "SEEN_AND_SIGNED":
        return "a withdrawn conclusion needs a per-notice signature (SEEN_AND_SIGNED); a batch signature does not cover it"
    if state == "BATCH_SEEN_AND_SIGNED" and not str(sig.get("batch_id") or "").strip():
        return "BATCH_SEEN_AND_SIGNED needs a batch_id naming the batch the reviewer saw"
    return None
