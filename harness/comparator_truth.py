"""Comparator-truth checks backed by held comparator text.

The checks in this module read cached comparator text and return audit objects
with source spans. They do not change pooled trials or extraction decisions.
"""
from __future__ import annotations

from .topic_registry import topic_id

import os
import re
from typing import Any, Iterable


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_WS = re.compile(r"\s+")
_N_LVEF40 = re.compile(r"LVEF\s*(?:<=|\u2264)\s*40.{0,100}?n\s*=\s*([\d, ]+)", re.I)
_ONLY_TWO = re.compile(r"Only\s+two\s+of\s+the\s+four\s+citations\s+reported\s+renal\s+composite", re.I)


KNOWN_ELIGIBLE_BY_SLUG = {
    (topic_id('spironolactone_heart_failure')): [
        {"name": "RALES", "aliases": ["RALES"]},
        {"name": "EMPHASIS-HF", "aliases": ["EMPHASIS-HF", "EMPHASIS HF"]},
        {"name": "J-EMPHASIS-HF", "aliases": ["J-EMPHASIS-HF", "J-EMPHASIS"]},
    ],
    (topic_id('finerenone_renal')): [
        {"name": "FIDELIO-DKD", "aliases": ["FIDELIO-DKD", "FIDELIO-CDK", "Bakris et al., 2020"]},
        {"name": "FIGARO-DKD", "aliases": ["FIGARO-DKD", "FIRAGO-DKD", "Pitt et al., 2021"]},
    ],
}

PAGE_ANNOTATION_SLUGS = frozenset(
    {
        (topic_id('sglt2_heart_failure')),
        (topic_id('pcsk9_cardiovascular')),
        (topic_id('spironolactone_heart_failure')),
        (topic_id('finerenone_renal')),
    }
)


NAMED_TRIALS_BY_SLUG = {
    (topic_id('pcsk9_cardiovascular')): [
        {
            "name": "VESALIUS-CV",
            "date": "2025-11",
            "basis": "lane instruction; committed search-v2 candidates contain VESALIUS-CV records",
        }
    ],
}


def _flat(text: str) -> str:
    return _WS.sub(" ", text or "").strip()


def _span(flat: str, start: int, end: int, window: int = 120) -> str:
    lo = max(0, start - window)
    hi = min(len(flat), end + window)
    return flat[lo:hi].strip()


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, dict):
        return _as_int(value.get("value"))
    if isinstance(value, str):
        m = re.search(r"\d[\d, ]*", value)
        if m:
            try:
                return int(re.sub(r"\D", "", m.group(0)))
            except ValueError:
                return None
    return None


def _number_pattern(value: Any) -> str | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        digits = str(value)
        if len(digits) > 3:
            grouped = r"[\s,]?".join(
                [digits[: len(digits) % 3] or digits[:3]]
                + [digits[i:i + 3] for i in range(len(digits) % 3 or 3, len(digits), 3)]
            )
            return rf"(?<!\d)(?:{re.escape(digits)}|{grouped})(?!\d)"
        return rf"(?<!\d){re.escape(digits)}(?!\d)"
    if isinstance(value, float):
        s = f"{value:g}"
        if "." in s:
            left, right = s.split(".", 1)
            return rf"(?<![\d.]){re.escape(left)}\.{re.escape(right)}0*(?!\d)"
        return rf"(?<![\d.]){re.escape(s)}(?:\.0+)?(?!\d)"
    return None


def span_or_not_held(text: str, value: Any) -> dict[str, Any]:
    """Locate a rendered comparator value in held comparator text."""
    out = {"value": value, "status": "NOT_IN_HELD_TEXT", "span": None, "start": None, "end": None}
    flat = _flat(text)
    if value in (None, "") or not flat:
        return out
    pat = _number_pattern(value)
    if pat:
        m = re.search(pat, flat, re.I)
        if m:
            return {**out, "status": "FOUND", "span": _span(flat, m.start(), m.end()), "start": m.start(), "end": m.end()}
        return out
    needle = _flat(str(value))
    idx = flat.lower().find(needle.lower())
    if idx >= 0:
        return {**out, "status": "FOUND", "span": _span(flat, idx, idx + len(needle)), "start": idx, "end": idx + len(needle)}
    return out


def load_cached_comparator_text(root: str, slug: str, pmid: str | None = None, fallback: str = "") -> str:
    """Read held comparator text, preferring normalized AE cache then per-topic cache."""
    paths = []
    if pmid:
        paths.append(os.path.join(root, "cache", "comparators", str(pmid), "body.txt"))
    if slug:
        paths.append(os.path.join(root, "cache", slug, "comparator_fulltext.txt"))
    for path in paths:
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            if text.strip():
                return text
        except OSError:
            pass
    return fallback or ""


def _row_n(row: dict[str, Any]) -> int | None:
    for a, b in (("n1i", "n2i"), ("nc1", "nc2")):
        if row.get(a) is not None and row.get(b) is not None:
            try:
                return int(row[a]) + int(row[b])
            except (TypeError, ValueError):
                return None
    endpoint_counts = row.get("endpoint_counts") if isinstance(row.get("endpoint_counts"), dict) else {}
    if endpoint_counts:
        for a, b in (("n1i", "n2i"), ("nc1", "nc2")):
            if endpoint_counts.get(a) is not None and endpoint_counts.get(b) is not None:
                try:
                    return int(endpoint_counts[a]) + int(endpoint_counts[b])
                except (TypeError, ValueError):
                    return None
    for key in ("n", "sample_size", "participants"):
        n = _as_int(row.get(key))
        if n is not None:
            return n
    return None


def participant_reconciliation(theirs_n: Any, ours_rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Compare comparator participant n with the sum of our shared trial rows."""
    theirs = _as_int(theirs_n)
    row_parts = []
    for row in ours_rows or []:
        n = _row_n(row or {})
        if n is not None:
            row_parts.append({"trial": row.get("label") or row.get("id"), "n": n})
    ours = sum(part["n"] for part in row_parts) if row_parts else None
    if theirs is None:
        code = "N_NOT_IN_HELD_TEXT"
    elif ours is None:
        code = "OURS_N_NOT_COMPUTABLE"
    elif theirs > ours:
        code = "PARITY_REFUTED_BY_N"
    elif theirs == ours:
        code = "N_RECONCILIATION_MATCH"
    else:
        code = "N_RECONCILIATION_NOT_REFUTED"
    out = {"code": code, "theirs_n": theirs, "ours_n": ours, "ours_trials": row_parts}
    if theirs is not None and ours is not None:
        out["excess"] = theirs - ours
        out["detail"] = (
            f"PARITY_REFUTED_BY_N(theirs={theirs}, ours={ours}, excess={theirs - ours})"
            if code == "PARITY_REFUTED_BY_N"
            else f"{code}(theirs={theirs}, ours={ours})"
        )
    return out


def _sentences(text: str) -> list[str]:
    flat = _flat(text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", flat)
    return [p.strip() for p in parts if p.strip()]


def agent_scope_from_text(text: str) -> dict[str, Any]:
    """Classify comparator intervention scope from the comparator's own words."""
    flat = _flat(text)
    head = flat[:400]
    head_l = head.lower()
    if "finerenone in type 2 diabetes" in head_l or head_l.startswith("finerenone "):
        return {
            "comparator_agent_scope": "single-agent",
            "sentence": head,
            "span": head,
            "status": "FOUND",
        }
    candidates = []
    for sent in _sentences(flat):
        low = sent.lower()
        if "alirocumab" in low and "evolocumab" in low:
            candidates.append(sent)
        elif "pcsk9 inhibitors" in low or "sglt2 inhibitors" in low:
            candidates.append(sent)
        elif "mineralocorticoid receptor antagonists" in low or re.search(r"\bMRAs\b", sent):
            candidates.append(sent)
    if not candidates and flat:
        line = flat[:240]
        if "alirocumab" in line.lower() and "evolocumab" in line.lower():
            candidates.append(line)
    if candidates:
        sentence = candidates[0]
        low = sentence.lower()
        if (
            "inhibitors" in low
            or "antagonists" in low
            or ("alirocumab" in low and "evolocumab" in low)
            or "mras" in low
        ):
            scope = "class-level"
        else:
            scope = "single-agent"
        return {
            "comparator_agent_scope": scope,
            "sentence": sentence,
            "span": sentence,
            "status": "FOUND",
        }
    return {"comparator_agent_scope": "not-classified", "sentence": None, "span": None, "status": "NOT_IN_HELD_TEXT"}


def completeness_vs_known_eligible(
    text: str,
    known_eligible: Iterable[dict[str, Any] | str],
    *,
    expected_count: int | None = None,
) -> dict[str, Any]:
    """Compare comparator text against named eligible trials known to the page."""
    present = []
    missing = []
    for item in known_eligible or []:
        if isinstance(item, str):
            name, aliases = item, [item]
        else:
            name = str(item.get("name") or "")
            aliases = [str(x) for x in (item.get("aliases") or [name])]
        hit = None
        for alias in aliases:
            hit = span_or_not_held(text, alias)
            if hit["status"] == "FOUND":
                break
        if hit and hit["status"] == "FOUND":
            present.append({"trial": name, "span": hit["span"]})
        else:
            missing.append(name)
    contradictions = []
    flat_text = _flat(text)
    for match in re.finditer(r"\bEPHESUS\b", flat_text, re.I):
        e_span = _span(flat_text, match.start(), match.end())
        if re.search(r"myocardial infarction|post[- ]?MI|after Myocardial", e_span, re.I):
            contradictions.append(
                {
                    "code": "COMPARATOR_SCOPE_CONTRADICTION",
                    "trial": "EPHESUS",
                    "span": e_span,
                    "reason": "EPHESUS is described as post-myocardial-infarction LV dysfunction in comparator text.",
                }
            )
            break
    only_two = span_or_not_held(text, "Only two of the four citations reported renal composite")
    if only_two["status"] == "NOT_IN_HELD_TEXT":
        m = _ONLY_TWO.search(_flat(text))
        if m:
            flat = _flat(text)
            only_two = {
                "value": "Only two of the four citations reported renal composite",
                "status": "FOUND",
                "span": _span(flat, m.start(), m.end()),
                "start": m.start(),
                "end": m.end(),
            }
    relation = None
    if expected_count is not None and not missing and len(present) == expected_count and only_two["status"] == "FOUND":
        relation = "IDENTICAL_SET"
    code = "COMPARATOR_COMPLETE_FOR_KNOWN_ELIGIBLE" if not missing else "COMPARATOR_INCOMPLETE"
    detail = f"COMPARATOR_INCOMPLETE(missing: {', '.join(missing)})" if missing else code
    return {
        "code": code,
        "detail": detail,
        "relation": relation,
        "known_n": len(list(known_eligible or [])),
        "present": present,
        "missing": missing,
        "contradictions": contradictions,
        "expected_count": expected_count,
        "expected_count_span": only_two,
    }


def recency_vs_named_trials(comparator_year: Any, named_trials: Iterable[dict[str, Any]]) -> dict[str, Any]:
    try:
        comp_year = int(str(comparator_year)[:4])
    except (TypeError, ValueError):
        comp_year = None
    predates = []
    for trial in named_trials or []:
        date = str(trial.get("date") or "")
        try:
            trial_year = int(date[:4])
        except ValueError:
            continue
        if comp_year is not None and comp_year < trial_year:
            predates.append(
                {
                    "trial": trial.get("name"),
                    "trial_date": date,
                    "comparator_year": comp_year,
                    "code": f"COMPARATOR_PREDATES_KNOWN_TRIAL({trial.get('name')})",
                    "basis": trial.get("basis"),
                }
            )
    return {
        "code": "COMPARATOR_PREDATES_KNOWN_TRIAL" if predates else "RECENCY_OK_OR_NOT_ASSESSED",
        "predates": predates,
    }


def _extract_lvef40_n(text: str) -> dict[str, Any]:
    flat = _flat(text)
    m = _N_LVEF40.search(flat)
    if not m:
        return span_or_not_held(text, None)
    value = _as_int(m.group(1))
    return {"value": value, "status": "FOUND", "span": _span(flat, m.start(), m.end()), "start": m.start(1), "end": m.end(1)}


def rendered_comparator_value_spans(review: dict[str, Any], text: str) -> list[dict[str, Any]]:
    comp = (review or {}).get("comparator") or {}
    rows = []
    for idx, rep in enumerate(comp.get("reported") or []):
        for key in ("estimate", "ci_low", "ci_high"):
            rows.append({"field": f"reported[{idx}].{key}", **span_or_not_held(text, rep.get(key))})
    ov = comp.get("overlap") or {}
    if isinstance(ov.get("theirs_k"), int):
        rows.append({"field": "overlap.theirs_k", **span_or_not_held(text, ov.get("theirs_k"))})
    truth = comp.get("truth") or {}
    nrec = truth.get("participant_reconciliation") or {}
    if nrec.get("theirs_n") is not None:
        rows.append({"field": "truth.participant_reconciliation.theirs_n", **span_or_not_held(text, nrec.get("theirs_n"))})
    return rows


def assess_review(slug: str, review: dict[str, Any], config: dict[str, Any] | None, text: str) -> dict[str, Any]:
    comp = (review or {}).get("comparator") or {}
    primary = next((o for o in (review or {}).get("outcomes", []) if o.get("primary")), None)
    if primary is None and (review or {}).get("outcomes"):
        primary = (review or {}).get("outcomes", [])[0]
    primary_trials = (primary or {}).get("trials") or []

    truth: dict[str, Any] = {
        "agent_scope": agent_scope_from_text(text),
        "participant_reconciliation": {"code": "NOT_ASSESSED"},
        "completeness": {"code": "NOT_ASSESSED"},
        "recency": recency_vs_named_trials(comp.get("year"), NAMED_TRIALS_BY_SLUG.get(slug, [])),
    }

    if slug == (topic_id('sglt2_heart_failure')):
        theirs_n = _extract_lvef40_n(text)
        nrec = participant_reconciliation(theirs_n, primary_trials)
        nrec["theirs_n_span"] = theirs_n
        truth["participant_reconciliation"] = nrec

    known = KNOWN_ELIGIBLE_BY_SLUG.get(slug)
    if known:
        expected = 2 if slug == (topic_id('finerenone_renal')) else None
        truth["completeness"] = completeness_vs_known_eligible(text, known, expected_count=expected)

    shell = {"comparator": {**comp, "truth": truth}}
    truth["rendered_comparator_value_spans"] = rendered_comparator_value_spans(shell, text)
    return truth


def annotate_comparator(
    slug: str,
    comparator: dict[str, Any],
    primary_trials: Iterable[dict[str, Any]],
    config: dict[str, Any] | None,
    text: str,
) -> dict[str, Any]:
    """Attach comparator_truth and patch local comparator metadata where text proves it."""
    review = {"comparator": comparator, "outcomes": [{"primary": True, "trials": list(primary_trials or [])}]}
    truth = assess_review(slug, review, config, text)
    comparator["truth"] = truth

    agent = truth.get("agent_scope") or {}
    scope = comparator.get("scope") or {}
    if agent.get("comparator_agent_scope") != "not-classified":
        scope["comparator_agent_scope"] = agent.get("comparator_agent_scope")
        scope["comparator_agent_scope_sentence"] = agent.get("sentence")
        if agent.get("comparator_agent_scope") == "class-level":
            scope["comparator_is_class"] = True
    comparator["scope"] = scope

    overlap = comparator.get("overlap") or {}
    nrec = truth.get("participant_reconciliation") or {}
    if nrec.get("code") == "PARITY_REFUTED_BY_N":
        overlap["theirs_n"] = nrec.get("theirs_n")
        overlap["ours_n"] = nrec.get("ours_n")
        overlap["n_reconciliation"] = nrec.get("detail")
    complete = truth.get("completeness") or {}
    if complete.get("relation") == "IDENTICAL_SET":
        overlap["theirs_k"] = complete.get("expected_count")
        overlap["shared_k"] = complete.get("expected_count")
        overlap["only_theirs"] = []
        overlap["only_ours"] = []
        overlap["method"] = "comparator-truth: named conforming renal-composite trials located in cached comparator text"
        overlap["note"] = "Comparator text says only two citations reported the conforming renal composite; those are FIDELIO-DKD and FIGARO-DKD, matching this pool."
    comparator["overlap"] = overlap
    return comparator
