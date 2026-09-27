"""PROVENANCE TIERS for arm-level counts found by the acquisition cascade (scripts/acquisition_cascade.py).

A count is PRIMARY when it comes from the trial's own report or registry results, SECONDARY_SOURCE when it is read
from a citing paper (a meta-analysis or review), recorded with the citing paper, its table and row. Primary outranks
secondary. A secondary count may corroborate, and may be SERVED only with a visible "secondary-source" label, never as
if it were the primary table. Two accepted witnesses that disagree (secondary vs secondary, or secondary vs primary)
raise SOURCE_EFFECT_CONFLICT.

Acceptance is deterministic, never a match on numbers alone:
  * the witness's row label / sentence must match the target endpoint (row_label_must_match) and must NOT match the
    endpoint it is easily confused with (row_label_must_not_match: ICAP's 'incessant or recurrent' composite);
  * an arm-level witness carries two counts on the trial's arm denominators;
  * a percentage-only witness can corroborate, never supply counts -- and one whose value equals the NOT-THIS row
    (16.7% = ICAP's composite 20/120, printed under 'Recurrence %') is refused as a mislabelled row.
"""
from __future__ import annotations

import re
from typing import Any

PRIMARY, SECONDARY_SOURCE = "PRIMARY", "SECONDARY_SOURCE"
SOURCE_EFFECT_CONFLICT = "SOURCE_EFFECT_CONFLICT"
_OF = re.compile(r"(?<![\d.])(\d{1,4})\s*\(\s*(\d{1,3}(?:[.·]\d+)?)\s*%\s*\)\s*of\s*(\d{1,4})(?![\d.])")
_SLASH = re.compile(r"(?<![\d.])(\d{1,4})\s*/\s*(\d{1,4})(?![\d.])")
_PCT = re.compile(r"(?<![\d.])(\d{1,3}(?:[.·]\d+)?)\s*%")


def _num(x):
    return float(str(x).replace("·", "."))


def count_pairs(text: str) -> list[tuple[int, int]]:
    """(events, denominator) pairs stated in a row or sentence: 'n (x%) of N' (percentage-corroborated) or 'n/N'."""
    out = []
    for m in _OF.finditer(text or ""):
        n, p, d = int(m.group(1)), _num(m.group(2)), int(m.group(3))
        if d and abs(100 * n / d - p) <= 1.0:          # the percentage must corroborate the count
            out.append((n, d))
    if not out:
        out = [(int(a), int(b)) for a, b in _SLASH.findall(text or "") if int(b) >= int(a) and int(b) >= 10]
    return out


def _label_ok(text, target):
    t = (text or "").lower()
    ok = re.search(target.get("row_label_must_match") or ".", t)
    bad = target.get("row_label_must_not_match") and re.search(target["row_label_must_not_match"], t)
    return bool(ok) and not bad


def _witness_text(c):
    # a table row's endpoint is often named only in its column heading ('Recurrence %'), so the heading is label text
    if c.get("where") == "table":
        return " | ".join((c.get("row") or []) + (c.get("column_headings") or []))
    return c.get("sentence") or ""


def evaluate(trial: dict[str, Any], target: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Tier, witnesses, refusals and conflicts for ONE trial x endpoint target."""
    arms = set(trial.get("arm_sizes") or [])
    accepted, pct_only, refused, not_this = [], [], [], []
    for c in (x for x in candidates if x.get("trial") == trial["trial"]):
        text = _witness_text(c)
        where = ({"table": c.get("table"), "caption": c.get("caption"), "column_headings": c.get("column_headings"),
                  "row": c.get("row")} if c.get("where") == "table" else {"sentence": (c.get("sentence") or "")[:400]})
        base = {"tier": c.get("tier"), "document": c.get("document"), "document_sha256": c.get("document_sha256"),
                "citing_pmid": c.get("citing_pmid"), **where}
        pairs = [p for p in count_pairs(text) if not arms or p[1] in arms]
        if target.get("row_label_must_not_match") and re.search(target["row_label_must_not_match"], text.lower()):
            if len(pairs) >= 2:
                not_this.append({**base, "counts": pairs[:2]})
            refused.append({**base, "reason": f"row names the excluded endpoint /{target['row_label_must_not_match']}/"})
            continue
        if not _label_ok(text, target):
            refused.append({**base, "reason": f"row label does not name the target endpoint /{target.get('row_label_must_match')}/"})
            continue
        if len(pairs) >= 2 and pairs[0][1] == pairs[1][1]:
            accepted.append({**base, "counts": [list(pairs[0]), list(pairs[1])]})
        else:
            pcts = [_num(p) for p in _PCT.findall(text)]
            cells = [x for x in (c.get("row") or []) if re.fullmatch(r"\d{1,3}(?:[.·]\d+)?", x or "")]
            if not pcts and c.get("where") == "table" and any("%" in h for h in (c.get("column_headings") or [])):
                pcts = [_num(x) for x in cells if 0 < _num(x) <= 100 and _num(x) not in arms]
            if pcts:
                pct_only.append({**base, "percents": pcts})
            else:
                refused.append({**base, "reason": "no arm-level count pair on the trial's arm denominators"})
    # a percentage-only witness that equals the NOT-THIS row's percentage is a mislabelled row, not a corroboration
    # ... from a witnessed not-this row, or from the target's declared not-this counts ('20/120 vs 45/120')
    declared = count_pairs(target.get("not_this") or "")
    nt_pcts = {round(100 * n / d, 1) for w in not_this for n, d in w["counts"]} | {round(100 * n / d, 1) for n, d in declared}
    corroborating = []
    for w in pct_only:
        if any(round(p, 1) in nt_pcts for p in w["percents"]):
            refused.append({**w, "reason": f"its value {w['percents']} equals the excluded endpoint's percentage "
                                           f"{sorted(nt_pcts)} (the row is mislabelled)"})
        else:
            corroborating.append(w)
    primaries = [w for w in accepted if w["tier"] == PRIMARY]
    secondaries = [w for w in accepted if w["tier"] == SECONDARY_SOURCE]
    distinct = {tuple(map(tuple, w["counts"])) for w in accepted}
    conflict = SOURCE_EFFECT_CONFLICT if len(distinct) > 1 else None
    status = ("FOUND_PRIMARY" if primaries else "FOUND_SECONDARY_ONLY" if secondaries else "NOT_FOUND")
    served = primaries[0] if primaries else (secondaries[0] if secondaries else None)
    return {"trial": trial["trial"], "outcome": target["outcome"], "status": status, "conflict": conflict,
            "served_tier": served["tier"] if served else None,
            "served_counts": served["counts"] if served else None,
            "serve_label": ("secondary-source" if served and served["tier"] == SECONDARY_SOURCE else None),
            "primary_witnesses": primaries, "secondary_witnesses": secondaries,
            "percent_corroboration": corroborating, "not_this_row": not_this, "refused": refused}


def serving_problems(review: dict[str, Any], html: str) -> list[str]:
    """A served row whose counts are SECONDARY_SOURCE must name its citing witness and carry the visible label on the
    page, next to the row; a row claiming PRIMARY while its only witness is secondary is refused outright."""
    out = []
    for o in review.get("outcomes") or []:
        for t in o.get("trials") or []:
            tier = t.get("provenance_tier")
            if tier is None:
                continue
            sw = t.get("secondary_witness") or {}
            if tier == SECONDARY_SOURCE:
                if not (sw.get("document") and sw.get("document_sha256")):
                    out.append(f"L1: {t.get('id')} ({o.get('name')}) is SECONDARY_SOURCE with no citing document+sha256")
                i = html.find(str(t.get("id")))
                if i < 0 or "data-provenance-tier='SECONDARY_SOURCE'" not in html[i:i + 6000]:
                    out.append(f"L1: {t.get('id')} ({o.get('name')}) serves secondary-source counts without the visible "
                               "'secondary-source' label on the page")
            elif tier == PRIMARY:
                if sw and not t.get("primary_witness"):
                    out.append(f"L1: {t.get('id')} ({o.get('name')}) is labelled PRIMARY but its only witness is secondary")
            else:
                out.append(f"L1: {t.get('id')} ({o.get('name')}) has unknown provenance_tier {tier!r}")
    return out
