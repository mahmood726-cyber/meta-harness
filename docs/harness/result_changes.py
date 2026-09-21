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


def notice_for(notices: list[dict[str, Any]], slug: str, outcome: str, before: dict[str, Any] | None,
               after: dict[str, Any] | None, left: list[str], entered: list[str]) -> dict[str, Any] | None:
    """The one notice that names this change EXACTLY (both results, every row that moved), or None."""
    for n in notices:
        if any(k not in n for k in REQUIRED):
            continue
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
