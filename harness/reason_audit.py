"""Reason-code audit over held sources.

This layer measures whether a declared-absent/refused row's reason code is
supported by the sources already cached for the topic. It does not change
extraction, pooling, membership, or the row's stated reason code.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from . import absence, extract

REASON_TRUE = "REASON_TRUE"
REASON_FALSE_VALUE_HELD = "REASON_FALSE_VALUE_HELD"
REASON_WRONG_KIND = "REASON_WRONG_KIND"
NOT_VERIFIABLE = "NOT_VERIFIABLE"

_VALUE_PRESENT_CODES = {
    absence.COUNTS_PRESENT_NOT_CORROBORATED,
    absence.EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH,
    absence.EXTRACTION_NOT_PERFORMED,
    absence.REFUSED_ON_EVIDENCE,
}
_DESIGN_CODES = _VALUE_PRESENT_CODES | {
    absence.MULTI_ARM_UNRESOLVED,
    absence.TIMEPOINT_MISMATCH,
    absence.POPULATION_MISMATCH,
}
_TAG = re.compile(r"<[^>]+>")
_NCT_OR_PMID = re.compile(r"\b(NCT\d{8}|\d{6,9})\b", re.I)
_COUNT_WITH_PERCENT = re.compile(
    r"\b\d[\d,]*\s*(?:patients?|participants?|subjects?|events?|cases?)?\s*[\(\[]\s*"
    r"\d+(?:\.\d+)?\s*%\s*[\)\]]"
    r"|\b\d+(?:\.\d+)?\s*%\s*[\(\[]?\s*\d[\d,]*\s*/\s*\d[\d,]*",
    re.I,
)
_EXPLICIT_FRACTION = re.compile(r"\b\d[\d,]*\s*/\s*\d[\d,]*\b|\b\d[\d,]*\s+of\s+\d[\d,]*\b", re.I)
_TWO_ARM_EVENT_COUNTS = re.compile(
    r"\b\d[\d,]*\s+(?:events?|patients?|participants?|subjects?|cases?)\b"
    r"[^.]{0,180}?\b(?:vs\.?|versus|compared with|compared to)\b"
    r"[^.]{0,180}?\b\d[\d,]*\s+(?:events?|patients?|participants?|subjects?|cases?)\b",
    re.I,
)
_GROUP_WORD = re.compile(
    r"\b(?:placebo|control|controls|usual care|standard care|saline|balanced|colchicine|"
    r"semaglutide|esketamine|finerenone|dapagliflozin|empagliflozin|tocilizumab|"
    r"intervention|treatment|drug|no-colchicine)\b",
    re.I,
)
_ASSIGNED = re.compile(
    r"\b(\d[\d,]*)\s+(?:were\s+)?(?:randomly\s+)?(?:assigned|allocated|randomi[sz]ed)\s+"
    r"to\s+(?:the\s+)?([^.;]+?)(?:group|arm|,|;|\.|\band\b)",
    re.I,
)
_EVENT_IN_GROUP = re.compile(
    r"\b(\d[\d,]*)\s+events?\s+in\s+(?:the\s+)?([^.;]+?)(?:group|arm|,|;|\.|\bcompared\b)",
    re.I,
)


def norm_space(text: Any) -> str:
    return re.sub(r"\s+", " ", "" if text is None else str(text)).strip()


def clip(text: Any, limit: int = 240) -> str:
    text = norm_space(text)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def canonical_trial_id(value: Any) -> str:
    text = norm_space(value)
    if "·" in text:
        text = text.split("·")[-1].strip()
    match = _NCT_OR_PMID.search(text)
    if match:
        return match.group(1).upper() if match.group(1).upper().startswith("NCT") else match.group(1)
    for prefix in ("PMID ", "PMID:", "NCT "):
        if text.upper().startswith(prefix):
            return text[len(prefix):].strip()
    return text


def _plain(text: str) -> str:
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    if "<" in text:
        text = _TAG.sub(" ", text)
    return norm_space(text)


def _record_text(rec: dict[str, Any]) -> str:
    fields: list[str] = []
    for key in (
        "title",
        "brief_title",
        "official_title",
        "acronym",
        "conditions",
        "interventions",
        "outcomes",
        "primary_outcomes",
        "secondary_outcomes",
        "results",
    ):
        val = rec.get(key)
        if val:
            fields.append(json.dumps(val, ensure_ascii=False) if isinstance(val, (dict, list)) else str(val))
    return _plain(" ".join(fields))


def iter_records(records: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(records, list):
        return [r for r in records if isinstance(r, dict)]
    if not isinstance(records, dict):
        return []
    out: list[dict[str, Any]] = []
    for key in ("records", "pubmed", "items", "ctgov"):
        block = records.get(key)
        if isinstance(block, dict):
            out.extend(r for r in block.values() if isinstance(r, dict))
        elif isinstance(block, list):
            out.extend(r for r in block if isinstance(r, dict))
    if not out and records.get("id"):
        out.append(records)
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for rec in out:
        key = str(rec.get("id"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(rec)
    return deduped


def sources_by_trial(
    slug: str,
    records: dict[str, Any] | list[dict[str, Any]],
    root: str | os.PathLike[str] | None = None,
) -> dict[str, list[dict[str, str]]]:
    """Build held source text entries keyed by PMID/NCT/trial id."""
    root_path = Path(root) if root else None
    out: dict[str, list[dict[str, str]]] = {}
    fulltext_by_pmid = records.get("fulltext_by_pmid", {}) if isinstance(records, dict) else {}
    for rec in iter_records(records):
        key = canonical_trial_id(rec.get("id"))
        if not key:
            continue
        rows = out.setdefault(key, [])
        abstract = _plain(rec.get("abstract") or "")
        if abstract:
            rows.append({"source_id": f"abstract:{key}", "source_kind": "abstract", "text": abstract})
        ft = fulltext_by_pmid.get(str(rec.get("id"))) or fulltext_by_pmid.get(key)
        if ft:
            rows.append({"source_id": f"fulltext:{key}", "source_kind": "fulltext", "text": _plain(ft)})
        if root_path and key.isdigit():
            fp = root_path / "cache" / slug / f"ft_{key}.txt"
            if fp.exists():
                try:
                    rows.append({
                        "source_id": f"fulltext:{key}",
                        "source_kind": "fulltext",
                        "text": _plain(fp.read_text(encoding="utf-8")),
                    })
                except OSError:
                    pass
        registry_text = _record_text(rec)
        if registry_text and (str(rec.get("id_type") or "").lower() == "nct" or str(key).upper().startswith("NCT")):
            rows.append({"source_id": f"registry:{key}", "source_kind": "registry", "text": registry_text})
    return out


def _candidate_sentences(text: str, keywords: list[str], outcome_name: str | None) -> list[str]:
    candidates = absence._candidate_sentences(text, keywords, outcome_name)  # audit-only reuse
    if candidates:
        return candidates
    terms = absence._terms(keywords, outcome_name)
    if not terms:
        return []
    return [norm_space(s) for s in extract._sentences(_plain(text)) if absence._matches_term(s, terms)]


def _has_extractable_effect(sentence: str) -> bool:
    return bool(extract._EFFECT.search(extract._norm(sentence)))


def _has_numeric_outcome(sentence: str) -> bool:
    s = extract._norm(sentence)
    if _has_extractable_effect(s):
        return True
    if _COUNT_WITH_PERCENT.search(s) and _GROUP_WORD.search(s):
        return True
    if _TWO_ARM_EVENT_COUNTS.search(s) and _GROUP_WORD.search(s):
        return True
    if _EXPLICIT_FRACTION.search(s) and _GROUP_WORD.search(s):
        return True
    return False


def _assignment_denominators(text: str) -> tuple[int | None, int | None]:
    intervention = control = None
    for m in _ASSIGNED.finditer(text):
        try:
            n = int(m.group(1).replace(",", ""))
        except ValueError:
            continue
        label = m.group(2).lower()
        if any(x in label for x in ("placebo", "control", "saline", "usual care", "standard care", "no-colchicine")):
            control = n
        elif any(x in label for x in ("colchicine", "semaglutide", "balanced", "treatment", "intervention", "drug")):
            intervention = n
    return intervention, control


def _event_counts(sentence: str) -> tuple[int | None, int | None]:
    intervention = control = None
    for m in _EVENT_IN_GROUP.finditer(sentence):
        try:
            n = int(m.group(1).replace(",", ""))
        except ValueError:
            continue
        label = m.group(2).lower()
        if any(x in label for x in ("placebo", "control", "saline", "usual care", "standard care", "no-colchicine")):
            control = n
        elif any(x in label for x in ("colchicine", "semaglutide", "balanced", "treatment", "intervention", "drug")):
            intervention = n
    return intervention, control


def _normalised_value(sentence: str, source_text: str) -> str | None:
    ei, ec = _event_counts(sentence)
    ni, nc = _assignment_denominators(source_text)
    if None not in (ei, ec, ni, nc):
        return f"{ei}/{ni} vs {ec}/{nc}"
    frac = _EXPLICIT_FRACTION.search(sentence)
    if frac:
        return norm_space(frac.group(0))
    return None


def find_value_in_sources(
    sources: list[dict[str, str]],
    keywords: list[str],
    outcome_name: str | None = None,
) -> dict[str, str] | None:
    for src in sources or []:
        text = src.get("text") or ""
        for sent in _candidate_sentences(text, keywords, outcome_name):
            if not _has_numeric_outcome(sent):
                continue
            out = {
                "source_id": src.get("source_id") or "held_source",
                "source_kind": src.get("source_kind") or "held",
                "span": clip(sent),
            }
            value = _normalised_value(sent, text)
            if value:
                out["value_text"] = value
            return out
    return None


def _expects_value(code: str, row: dict[str, Any]) -> bool:
    reason = (row.get("reason") or "").lower()
    return (
        code in _VALUE_PRESENT_CODES
        or row.get("absent_kind") == "refused_on_evidence"
        or "estimand mismatch" in reason
        or "timepoint mismatch" in reason
        or "population mismatch" in reason
        or "refused" in reason
    )


def _source_not_retrieved_wrong(code: str, sources: list[dict[str, str]]) -> bool:
    if code != absence.SOURCE_NOT_RETRIEVED:
        return False
    return any((s.get("source_kind") or "") in {"abstract", "fulltext"} and (s.get("text") or "").strip()
               for s in sources or [])


def audit_reason_row(
    outcome: dict[str, Any],
    row: dict[str, Any],
    sources: list[dict[str, str]],
    spec: dict[str, Any] | None = None,
) -> dict[str, Any]:
    spec = spec or {}
    code = absence.normalize_code(row.get("reason_code") or row.get("state") or "")
    if not sources:
        return {
            "verdict": NOT_VERIFIABLE,
            "detail": "no held source",
            "stated_reason_code": code,
        }
    found = find_value_in_sources(sources, spec.get("keywords") or [], outcome.get("name"))
    if found:
        return {
            "verdict": REASON_FALSE_VALUE_HELD,
            "detail": f"{REASON_FALSE_VALUE_HELD}({found['source_id']}, \"{found['span']}\")",
            "stated_reason_code": code,
            "source_id": found["source_id"],
            "source_kind": found["source_kind"],
            "source_span": found["span"],
            "source_contains": found["span"],
            **({"value_text": found["value_text"]} if found.get("value_text") else {}),
        }
    if _expects_value(code, row) or _source_not_retrieved_wrong(code, sources):
        return {
            "verdict": REASON_WRONG_KIND,
            "detail": "value absent from held source, but the code names a value-present/refusal cause",
            "stated_reason_code": code,
        }
    return {
        "verdict": REASON_TRUE,
        "detail": "value absent from every held source inspected; code is consistent",
        "stated_reason_code": code,
    }


def _summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    verdicts = [REASON_TRUE, REASON_FALSE_VALUE_HELD, REASON_WRONG_KIND, NOT_VERIFIABLE]
    counts = {v: sum(1 for r in rows if r.get("verdict") == v) for v in verdicts}
    by_code: dict[str, dict[str, int]] = {}
    for row in rows:
        code = row.get("stated_reason_code") or "UNSPECIFIED"
        by_code.setdefault(code, {v: 0 for v in verdicts})
        by_code[code][row.get("verdict")] = by_code[code].get(row.get("verdict"), 0) + 1
    return {
        "denominator_source": "declared_absent_trials reason_code/state rows on this page",
        "N": len(rows),
        "counts": counts,
        "n_false_value_held": counts[REASON_FALSE_VALUE_HELD],
        "n_not_verifiable": counts[NOT_VERIFIABLE],
        "by_code_kind": by_code,
    }


def annotate_review(
    slug: str,
    review: dict[str, Any],
    specs_by_name: dict[str, dict[str, Any]],
    source_map: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for outcome in review.get("outcomes") or []:
        spec = specs_by_name.get(outcome.get("name")) or {}
        for row in outcome.get("declared_absent_trials") or []:
            key = canonical_trial_id(row.get("id") or row.get("label"))
            audit = audit_reason_row(outcome, row, source_map.get(key, []), spec)
            row["reason_code_audit"] = audit
            rows.append({
                "slug": slug,
                "outcome": outcome.get("name"),
                "outcome_kind": "primary" if outcome.get("primary") else outcome.get("kind", "secondary"),
                "trial_key": key,
                "label": row.get("label"),
                "id": row.get("id"),
                "stated_reason_code": audit.get("stated_reason_code"),
                **audit,
            })
    review["reason_code_audit"] = {**_summarise(rows), "rows": rows}
    return review["reason_code_audit"]
