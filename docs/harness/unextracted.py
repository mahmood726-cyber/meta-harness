"""Registered-outcome coverage audit.

For each included trial and each registered outcome on the page, report whether
the outcome is extracted, visibly held but not extracted, absent from held
sources, or absent by an explicit design/refusal rule. This is measurement only.
"""
from __future__ import annotations

from typing import Any

from . import absence
from . import reason_audit

EXTRACTED = "EXTRACTED"
HELD_NOT_EXTRACTED = "HELD_NOT_EXTRACTED"
NOT_IN_HELD_SOURCES = "NOT_IN_HELD_SOURCES"
ABSENT_BY_DESIGN = "ABSENT_BY_DESIGN"

_DESIGN_CODES = {
    absence.EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH,
    absence.MULTI_ARM_UNRESOLVED,
    absence.TIMEPOINT_MISMATCH,
    absence.POPULATION_MISMATCH,
    absence.REFUSED_ON_EVIDENCE,
}


def _outcome_kind(outcome: dict[str, Any]) -> str:
    if outcome.get("primary"):
        return "primary"
    if outcome.get("kind") == "harm":
        return "harm"
    return "secondary"


def _trial_keys(rows: list[dict[str, Any]]) -> set[str]:
    return {reason_audit.canonical_trial_id(t.get("id") or t.get("label")) for t in rows or []}


def _included_trials(review: dict[str, Any]) -> list[dict[str, str]]:
    records = ((review.get("screening") or {}).get("records")) or []
    out = []
    for rec in records:
        if rec.get("decision") != "include":
            continue
        key = reason_audit.canonical_trial_id(rec.get("id"))
        if key:
            out.append({"trial_key": key, "label": rec.get("id")})
    if out:
        return out
    seen: dict[str, str] = {}
    for outcome in review.get("outcomes") or []:
        for row in (outcome.get("trials") or []) + (outcome.get("declared_absent_trials") or []):
            key = reason_audit.canonical_trial_id(row.get("id") or row.get("label"))
            if key:
                seen.setdefault(key, row.get("label") or row.get("id"))
    return [{"trial_key": key, "label": label} for key, label in sorted(seen.items())]


def _declared_absent_by_key(outcome: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out = {}
    for row in outcome.get("declared_absent_trials") or []:
        key = reason_audit.canonical_trial_id(row.get("id") or row.get("label"))
        if key:
            out[key] = row
    return out


def _is_design_absent(row: dict[str, Any] | None) -> bool:
    if not row:
        return False
    code = absence.normalize_code(row.get("reason_code") or row.get("state") or "")
    reason = (row.get("reason") or "").lower()
    return (
        code in _DESIGN_CODES
        or row.get("absent_kind") == "refused_on_evidence"
        or "timepoint mismatch" in reason
        or "population mismatch" in reason
        or "multi-arm" in reason
        or "multi arm" in reason
        or "estimand mismatch" in reason
    )


def audit_pair(
    outcome: dict[str, Any],
    trial_key: str,
    sources: list[dict[str, str]],
    spec: dict[str, Any] | None = None,
    row: dict[str, Any] | None = None,
) -> dict[str, Any]:
    spec = spec or {}
    pooled = _trial_keys(outcome.get("trials") or [])
    if trial_key in pooled:
        return {"status": EXTRACTED}
    found = reason_audit.find_value_in_sources(sources, spec.get("keywords") or [], outcome.get("name"))
    if found:
        return {
            "status": HELD_NOT_EXTRACTED,
            "source_id": found["source_id"],
            "source_kind": found["source_kind"],
            "source_span": found["span"],
            **({"value_text": found["value_text"]} if found.get("value_text") else {}),
        }
    if _is_design_absent(row):
        return {"status": ABSENT_BY_DESIGN, "reason_code": row.get("reason_code") or row.get("state")}
    return {"status": NOT_IN_HELD_SOURCES}


def _summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = [EXTRACTED, HELD_NOT_EXTRACTED, NOT_IN_HELD_SOURCES, ABSENT_BY_DESIGN]
    counts = {s: sum(1 for r in rows if r.get("status") == s) for s in statuses}
    by_kind: dict[str, dict[str, int]] = {}
    for row in rows:
        kind = row.get("outcome_kind") or "secondary"
        by_kind.setdefault(kind, {s: 0 for s in statuses})
        by_kind[kind][row.get("status")] = by_kind[kind].get(row.get("status"), 0) + 1
    return {
        "denominator_source": "included screening records x registered outcomes in this review",
        "N": len(rows),
        "counts": counts,
        "n_held_not_extracted": counts[HELD_NOT_EXTRACTED],
        "by_outcome_kind": by_kind,
    }


def annotate_review(
    slug: str,
    review: dict[str, Any],
    specs_by_name: dict[str, dict[str, Any]],
    source_map: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    included = _included_trials(review)
    for outcome in review.get("outcomes") or []:
        spec = specs_by_name.get(outcome.get("name")) or {}
        absent_by_key = _declared_absent_by_key(outcome)
        kind = _outcome_kind(outcome)
        for trial in included:
            key = trial["trial_key"]
            audit = audit_pair(outcome, key, source_map.get(key, []), spec, absent_by_key.get(key))
            rows.append({
                "slug": slug,
                "trial_key": key,
                "trial_label": trial.get("label"),
                "outcome": outcome.get("name"),
                "outcome_kind": kind,
                **audit,
            })
    review["unextracted_outcome_audit"] = {**_summarise(rows), "rows": rows}
    return review["unextracted_outcome_audit"]
