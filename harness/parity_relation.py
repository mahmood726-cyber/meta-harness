"""Typed trial-set relation for comparator parity rows.

The hand-written parity row may explain a difference, but the status word is a
computed relation. A stale hand status is a build refusal because it lets a page
say "parity" beside incompatible k values.
"""
from __future__ import annotations

import json
import os
import re
from typing import Optional

VOCABULARY = {
    "IDENTICAL_SET",
    "DOMINANT_SUBSET",
    "SUBSET",
    "SUPERSET",
    "OVERLAPPING",
    "DISTINCT",
    "COMPARATOR_INVALID",
    "NOT_ENUMERABLE",
    "PARITY_REFUTED_BY_N",
}

_NOT_VERIFIABLE = "not exactly verifiable"
_PATIENT_PCT = re.compile(r"(?:~|about|approximately)?\s*(\d+(?:\.\d+)?)\s*%")
_RATIO = re.compile(r"\b(\d+)\s*/\s*(\d+)\b")


def _as_int(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _normalise_status(status: Optional[str]) -> Optional[str]:
    if status is None:
        return None
    return str(status).strip().upper().replace("-", "_").replace(" ", "_")


def _first_ratio_denominator(text: str, numerator: Optional[int]) -> Optional[int]:
    for m in _RATIO.finditer(text or ""):
        num, den = int(m.group(1)), int(m.group(2))
        if numerator is None or num == numerator:
            return den
    return None


def _patient_share(text: str):
    text = text or ""
    for m in _PATIENT_PCT.finditer(text):
        window = text[m.start():m.end() + 50].lower()
        if "patient" in window or "event" in window or "carr" in window:
            return {"value": float(m.group(1)), "source": "parity reason text"}
    return None


def _relation_label(relation: str, inferred: bool, dominance=None) -> str:
    labels = {
        "IDENTICAL_SET": "arithmetic agreement -- same trials; overlapping inputs do not constitute an independent evidence set",
        "DOMINANT_SUBSET": "dominant-trial subset -- ours is contained in the comparator",
        "SUBSET": "subset -- ours is contained in the comparator",
        "SUPERSET": "superset -- the comparator trial set is contained in ours",
        "OVERLAPPING": "overlapping -- neither trial set contains the other",
        "DISTINCT": "distinct -- no shared trials",
        "COMPARATOR_INVALID": "comparator invalid -- not an RCT meta / not the same question",
        "NOT_ENUMERABLE": "not enumerable -- comparator trial list and k are not exposed",
        "PARITY_REFUTED_BY_N": "participant-count refutation -- comparator n exceeds the sum of our shared trial n",
    }
    label = labels[relation]
    if relation == "DOMINANT_SUBSET" and dominance:
        val = dominance.get("value")
        src = dominance.get("source")
        label += f"; carries {val:g}% of comparator patients/events (source: {src})"
    return ("INFERRED " + label) if inferred else label


def compute(row: dict, review: Optional[dict] = None) -> dict:
    """Return the typed relation and audit metadata for one parity row.

    `row` is the docs/parity.json snapshot. `review`, when supplied, contributes
    the comparator overlap block already rendered on the page.
    """
    row = row or {}
    comp = (review or {}).get("comparator") or {}
    overlap = comp.get("overlap") or {}
    truth = comp.get("truth") or {}
    nrec = truth.get("participant_reconciliation") or {}
    scope = comp.get("scope") or {}
    reason = row.get("reason") or ""
    hand_status = row.get("status")
    hand_norm = _normalise_status(hand_status)

    # our_k is DERIVED from the live primary pool when the review object is present (integration 2026-09-16):
    # the hand row's count is a snapshot that goes stale the moment a recovery changes k (pcsk9: 2 -> 3 with
    # VESALIUS-CV), and the gate refuses a stored count that disagrees with the pool. The hand value is kept
    # beside it as hand_our_k so the drift is visible, never silently overwritten.
    live_k = None
    for _o in (review or {}).get("outcomes", []) or []:
        if _o.get("primary"):
            live_k = _as_int((_o.get("result") or {}).get("k"))
            break
    hand_our_k = _as_int(row.get("our_k"))
    our_k = live_k if live_k is not None else hand_our_k
    if our_k is None:
        our_k = _as_int(overlap.get("ours_k"))

    comparable_k = _as_int(row.get("comparable_comparator_k"))
    overlap_k = _as_int(overlap.get("theirs_k"))
    ratio_den = _first_ratio_denominator(reason, our_k)
    their_k_source = "comparable_comparator_k"
    their_k = comparable_k
    if ratio_den is not None and (
            their_k is None or (hand_norm == "PARITY_EFFECTIVE" and ratio_den > their_k)):
        their_k = ratio_den
        their_k_source = "parity reason ratio"
    if their_k is None and overlap_k is not None:
        their_k = overlap_k
        their_k_source = "overlap.theirs_k"
    if overlap_k is not None and hand_norm in {"PARITY_EFFECTIVE"} and overlap_k > (their_k or -1):
        their_k = overlap_k
        their_k_source = "overlap.theirs_k"

    if nrec.get("code") == "PARITY_REFUTED_BY_N":
        relation = "PARITY_REFUTED_BY_N"
        label = (
            f"participant-count refutation -- comparator n {nrec.get('theirs_n')} exceeds "
            f"our shared-trial n {nrec.get('ours_n')} by {nrec.get('excess')}; sets differ"
        )
        hand_disagrees = hand_norm in VOCABULARY and hand_norm != relation
        if hand_norm and hand_norm not in VOCABULARY:
            hand_disagrees = True
        return {
            "relation": relation,
            "label": label,
            "inferred": False,
            "our_k": our_k,
            "their_k": their_k,
            "their_k_source": their_k_source if their_k is not None else None,
            "shared_k": None,
            "only_ours_n": len(overlap.get("only_ours") or []),
            "only_theirs_n": len(overlap.get("only_theirs") or []),
            "dominance": None,
            "hand_status": hand_status,
            "hand_status_normalized": hand_norm,
            "hand_status_disagrees": hand_disagrees,
            "participant_reconciliation": nrec,
        }

    shared_raw = overlap.get("shared_k")
    shared_k = _as_int(shared_raw)
    only_ours = [str(x) for x in (overlap.get("only_ours") or [])]
    only_theirs = [str(x) for x in (overlap.get("only_theirs") or [])]
    inferred = bool(isinstance(shared_raw, str) and _NOT_VERIFIABLE in shared_raw.lower())

    invalid_text = " ".join(str(x or "") for x in (hand_status, reason, scope.get("note")))
    invalid_l = invalid_text.lower()
    comparator_valid = not (
        hand_norm == "COMPARATOR_INVALID"
        or (comparable_k == 0 and ("observational" in invalid_l or "not an rct" in invalid_l))
        or scope.get("scope_valid") is False and "not an rct" in invalid_l
    )
    if not comparator_valid:
        relation = "COMPARATOR_INVALID"
        inferred = False
    elif their_k is None:
        relation = "NOT_ENUMERABLE"
        inferred = False
    elif shared_k == 0 and our_k and their_k:
        relation = "DISTINCT"
        inferred = False
    elif shared_k is not None and our_k is not None:
        if shared_k == our_k == their_k and not only_ours and not only_theirs:
            relation = "IDENTICAL_SET"
        elif shared_k == our_k and our_k < their_k:
            relation = "SUBSET"
        elif shared_k == their_k and their_k < our_k:
            relation = "SUPERSET"
        else:
            relation = "OVERLAPPING"
        inferred = False
    elif our_k is None:
        relation = "NOT_ENUMERABLE"
        inferred = False
    elif our_k == their_k:
        relation = "IDENTICAL_SET"
    elif our_k < their_k:
        dominance = _patient_share(reason)
        if dominance:
            relation = "DOMINANT_SUBSET"
        elif only_ours:
            relation = "OVERLAPPING"
        else:
            relation = "SUBSET"
    else:
        relation = "OVERLAPPING" if only_theirs else "SUPERSET"

    dominance = _patient_share(reason) if relation == "DOMINANT_SUBSET" else None
    hand_disagrees = hand_norm in VOCABULARY and hand_norm != relation
    if hand_norm and hand_norm not in VOCABULARY:
        hand_disagrees = True
    _hand_drift = (hand_our_k is not None and live_k is not None and hand_our_k != live_k)
    return {
        "relation": relation,
        "label": _relation_label(relation, inferred, dominance),
        "inferred": inferred,
        "our_k": our_k,
        "hand_our_k": hand_our_k,
        "hand_our_k_stale": _hand_drift,
        "their_k": their_k,
        "their_k_source": their_k_source if their_k is not None else None,
        "shared_k": shared_k,
        "only_ours_n": len(only_ours),
        "only_theirs_n": len(only_theirs),
        "dominance": dominance,
        "hand_status": hand_status,
        "hand_status_normalized": hand_norm,
        "hand_status_disagrees": hand_disagrees,
    }


def enrich(row: dict, review: Optional[dict] = None, strict: bool = True) -> dict:
    out = dict(row or {})
    rel = compute(out, review)
    out["parity_relation"] = rel
    # The rendered/gated our_k is the derived one; the hand snapshot stays visible under its own name.
    if rel.get("our_k") is not None:
        if out.get("our_k") is not None and out.get("our_k") != rel["our_k"]:
            out["hand_our_k"] = out.get("our_k")
            out["hand_our_k_stale"] = True
        out["our_k"] = rel["our_k"]
    if strict and rel["hand_status_disagrees"]:
        raise ValueError(
            "PARITY-RELATION REFUSED: hand status "
            f"{rel.get('hand_status')!r} disagrees with computed relation {rel['relation']} "
            f"for {out.get('slug')}"
        )
    return out


def scope_consistency_errors(row: dict, review: dict) -> list:
    rel = compute(row, review)
    scope = ((review or {}).get("comparator") or {}).get("scope") or {}
    if rel["relation"] == "COMPARATOR_INVALID" and scope.get("scope_valid") is True:
        return [
            "scope_valid=True while parity_relation=COMPARATOR_INVALID; one comparator object must carry one verdict"
        ]
    return []


def load_parity_rows(root: str) -> list:
    path = os.path.join(root, "docs", "parity.json")
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return []


def load_parity_row(root: str, slug: str) -> Optional[dict]:
    for row in load_parity_rows(root):
        if row.get("slug") == slug:
            return row
    return None


def invalid_scope_override(root: str, slug: str) -> Optional[str]:
    row = load_parity_row(root, slug)
    if not row:
        return None
    rel = compute(row)
    if rel["relation"] == "COMPARATOR_INVALID":
        return "comparator invalid -- not an RCT meta / not the same question"
    return None
