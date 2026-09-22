"""Consumer-consistency audit for source-visible outcomes and funding.

This module is deliberately downstream of extraction. It can say "the cached
source contains a value and the page must either extract it or type-refuse it",
but it never makes a value poolable and never changes synthesis arithmetic.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from . import absence, funding
from .admission import ADMISSION_SET_ASIDE_STATES

ROOT = Path(__file__).resolve().parents[1]

RETRIEVED_OUTCOME_NOT_REPORTED = "RETRIEVED_OUTCOME_NOT_REPORTED"
KNOWN_REPORTED_NOT_YET_EXTRACTED = "KNOWN_REPORTED_NOT_YET_EXTRACTED"
EXTRACTION_DEBT = "EXTRACTION_DEBT"
REASON_CODE_FALSE = "REASON_CODE_FALSE"
EXTRACTED_RECONSTRUCTION_WHILE_PUBLISHED_EXISTS = "EXTRACTED_RECONSTRUCTION_WHILE_PUBLISHED_EXISTS"

VALUE_REASON_CODES = {
    KNOWN_REPORTED_NOT_YET_EXTRACTED,
    "RETRIEVED_REFUSED_WITH_REASON",
    "RETRIEVED_INCOMPATIBLE_STRUCTURE",
    "UNIT_MISMATCH_CYCLE_LEVEL",
    absence.EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH,
    absence.COUNTS_PRESENT_NOT_CORROBORATED,
    absence.EXTRACTION_NOT_PERFORMED,
    absence.REFUSED_ON_EVIDENCE,
}

FALSE_ABSENCE_CODES = {
    "",
    None,
    absence.OUTCOME_NOT_IN_SOURCE,
    "NO_OUTCOME_DATA_IN_SOURCE",
    absence.SOURCE_NOT_RETRIEVED,
    RETRIEVED_OUTCOME_NOT_REPORTED,
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_records_blob(slug: str) -> dict[str, Any]:
    path = ROOT / "cache" / slug / "records.json"
    if not path.exists():
        return {}
    data = _load_json(path)
    return data if isinstance(data, dict) else {"records": data}


def iter_records(records_blob: dict[str, Any]) -> list[dict[str, Any]]:
    raw = records_blob.get("records") or records_blob.get("pubmed") or records_blob.get("items") or []
    if isinstance(raw, dict):
        raw = list(raw.values())
    ctgov = records_blob.get("ctgov") or []
    if isinstance(ctgov, dict):
        ctgov = list(ctgov.values())
    return [r for r in list(raw or []) + list(ctgov or []) if isinstance(r, dict)]


def records_by_id(records_blob: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for rec in iter_records(records_blob):
        rid = _norm_id(rec.get("id"))
        if rid and rid not in out:
            out[rid] = rec
    return out


def fulltexts_by_id(slug: str, records_blob: dict[str, Any]) -> dict[str, str]:
    out = {str(k): str(v) for k, v in (records_blob.get("fulltext_by_pmid") or {}).items() if v}
    cache_dir = ROOT / "cache" / slug
    if cache_dir.exists():
        for path in cache_dir.glob("ft_*.txt"):
            pid = path.stem.replace("ft_", "", 1)
            try:
                out[pid] = path.read_text(encoding="utf-8")
            except OSError:
                pass
        for path in cache_dir.glob("pmc_*_fulltext.txt"):
            pid = path.stem.replace("pmc_", "", 1).replace("_fulltext", "")
            try:
                out.setdefault(pid, path.read_text(encoding="utf-8"))
            except OSError:
                pass
    return out


def outcome_specs(config: dict[str, Any]) -> list[tuple[dict[str, Any], str]]:
    specs: list[tuple[dict[str, Any], str]] = []
    if config.get("primary_outcome"):
        specs.append((dict(config["primary_outcome"]), "efficacy"))
    for sp in config.get("secondary_outcomes") or []:
        specs.append((dict(sp), sp.get("kind", "secondary")))
    for sp in config.get("harm_outcomes") or []:
        specs.append((dict(sp), "harm"))
    return specs


def _norm_id(value: Any) -> str:
    text = str(value or "").strip()
    if "·" in text:
        text = text.split("·")[-1].strip()
    for prefix in ("PMID ", "PMID:"):
        if text.upper().startswith(prefix):
            text = text[len(prefix):].strip()
    return text


def _clip(text: str, limit: int = 260) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def _row_code(row: dict[str, Any] | None) -> str:
    if not row:
        return ""
    return absence.normalize_code(row.get("reason_code") or row.get("state") or "")


def _terms(spec: dict[str, Any]) -> list[str]:
    return [str(k).lower() for k in spec.get("keywords") or [] if len(str(k)) > 3]


def _title_matches(title: str, spec: dict[str, Any]) -> bool:
    tl = (title or "").lower()
    return any(k in tl for k in _terms(spec))


def _nct_for(trial_id: str, rec: dict[str, Any]) -> str:
    return trial_id if trial_id.upper().startswith("NCT") else str(rec.get("nct") or "").strip()


def _ctgov_continuous_candidate(records_blob: dict[str, Any], spec: dict[str, Any], trial_id: str,
                                rec: dict[str, Any]) -> dict[str, Any] | None:
    nct = _nct_for(trial_id, rec)
    if not nct:
        return None
    measures = (records_blob.get("ctgov_results") or {}).get(nct) or []
    candidates = [
        om for om in measures
        if _title_matches(om.get("title", ""), spec)
        and (om.get("paramType") or "").upper() in {"MEAN", "LEAST_SQUARES_MEAN"}
        and "standard deviation" in (om.get("dispersionType") or "").lower()
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda om: (0 if om.get("type") == "PRIMARY" else 1,
                                    0 if "day 28" in (om.get("timeFrame") or "").lower() else 1))
    om = candidates[0]
    denoms = {}
    for denom in om.get("denoms") or []:
        for count in denom.get("counts") or []:
            denoms[count.get("groupId")] = count.get("value")
    measurements = {}
    for klass in om.get("classes") or []:
        for cat in klass.get("categories") or []:
            for meas in cat.get("measurements") or []:
                measurements[meas.get("groupId")] = meas
            if measurements:
                break
        if measurements:
            break
    parts = []
    for group in om.get("groups") or []:
        gid = group.get("id")
        meas = measurements.get(gid) or {}
        if meas.get("value") is None or meas.get("spread") is None or denoms.get(gid) is None:
            continue
        parts.append(
            f"{group.get('title')}: mean {meas.get('value')} (SD {meas.get('spread')}, n={denoms.get(gid)})"
        )
    if len(parts) < 2:
        return None
    span = f"CT.gov {nct} {om.get('title')}; " + "; ".join(parts)
    abstract = rec.get("abstract") or ""
    phase_refusal = bool(re.search(r"\bphase\s*2|phase\s*ii\b", abstract, re.I))
    return {
        "source_has_value": True,
        "state": "RETRIEVED_REFUSED_WITH_REASON" if phase_refusal else KNOWN_REPORTED_NOT_YET_EXTRACTED,
        "reason_code": "RETRIEVED_REFUSED_WITH_REASON" if phase_refusal else KNOWN_REPORTED_NOT_YET_EXTRACTED,
        "value_kind": "ctgov_mean_sd_n",
        "source": "ctgov_results",
        "source_span": _clip(span, 500),
        "state_basis": ("retrieved CT.gov continuous per-arm mean/SD/n; refused for a source-backed design "
                        "reason, not because the mean/SD/n was absent" if phase_refusal
                        else "retrieved CT.gov continuous per-arm mean/SD/n not consumed by extraction"),
    }


def _cycle_level_candidate(text: str, spec: dict[str, Any]) -> dict[str, Any] | None:
    if "ovulat" not in " ".join(_terms(spec)) and "ovulat" not in (spec.get("name") or "").lower():
        return None
    m = re.search(r"ovulation[^.]{0,180}?\d+(?:\.\d+)?%\s+of\s+the\s+\d+\s+ovulatory\s+cycles[^.]+",
                  text, re.I)
    if not m:
        return None
    span = _clip(m.group(0), 420)
    return {
        "source_has_value": True,
        "state": "UNIT_MISMATCH_CYCLE_LEVEL",
        "reason_code": "UNIT_MISMATCH_CYCLE_LEVEL",
        "value_kind": "cycle_level_rate",
        "source": "abstract",
        "source_span": span,
        "state_basis": "retrieved value is cycle-level/repeated-within-woman and cannot enter a participant-level pool",
    }


def _event_count_candidate(text: str, spec: dict[str, Any]) -> dict[str, Any] | None:
    folded = text.lower()
    if not any(term in folded for term in _terms(spec)):
        return None
    den = re.search(
        r"(?P<n1>\d{2,5})\s+(?:were\s+)?(?:assigned|allocated)[^.]{0,90}?"
        r"(?P<i>colchicine|metformin|intervention|treatment)[^.]{0,160}?"
        r"(?P<n2>\d{2,5})\s+(?:were\s+)?(?:assigned|allocated)[^.]{0,90}?"
        r"(?P<c>placebo|control)",
        text,
        re.I,
    )
    if not den:
        den = re.search(
            r"(?P<n1>\d{2,5})\s+(?:were\s+)?(?:assigned|allocated)\s+to\s+the\s+"
            r"(?P<i>colchicine|metformin|intervention|treatment)[^.]{0,120}?"
            r"(?:and|,)\s+(?P<n2>\d{2,5})\s+to\s+the\s+(?P<c>placebo|control)",
            text,
            re.I,
        )
    evt = re.search(
        r"(?P<a>\d{1,4})\s+events?[^.]{0,80}?"
        r"(?P<i>colchicine|metformin|intervention|treatment)[^.]{0,160}?"
        r"(?:compared with|versus|vs\.?)\s+(?P<b>\d{1,4})\s+events?[^.]{0,80}?"
        r"(?P<c>placebo|control)",
        text,
        re.I,
    )
    if not (den and evt):
        return None
    lo = max(0, den.start() - 80)
    hi = min(len(text), evt.end() + 120)
    span = _clip(text[lo:hi], 520)
    return {
        "source_has_value": True,
        "state": EXTRACTION_DEBT,
        "reason_code": KNOWN_REPORTED_NOT_YET_EXTRACTED,
        "value_kind": "arm_event_counts_with_denominators",
        "source": "abstract",
        "source_span": span,
        "state_basis": (
            f"retrieved counts {evt.group('a')}/{den.group('n1')} vs "
            f"{evt.group('b')}/{den.group('n2')}; displayed as extraction debt, not pooled"
        ),
    }


def outcome_source_candidate(slug: str, records_blob: dict[str, Any], spec: dict[str, Any],
                             trial_id: str) -> dict[str, Any]:
    recs = records_by_id(records_blob)
    fulltexts = fulltexts_by_id(slug, records_blob)
    tid = _norm_id(trial_id)
    rec = recs.get(tid) or {}

    if (spec.get("estimand") or "").upper() == "MD":
        ct = _ctgov_continuous_candidate(records_blob, spec, tid, rec)
        if ct:
            return ct

    abstract = " ".join(x for x in (rec.get("title"), rec.get("abstract")) if x)
    fulltext = fulltexts.get(tid)
    text = " ".join(x for x in (abstract, fulltext) if x)
    if not text.strip():
        return {
            "source_has_value": False,
            "state": absence.SOURCE_NOT_RETRIEVED,
            "reason_code": absence.SOURCE_NOT_RETRIEVED,
            "source_span": "",
            "state_basis": "no cached abstract/full text for this row",
        }

    for detector in (_cycle_level_candidate, _event_count_candidate):
        hit = detector(text, spec)
        if hit:
            return hit

    actual = absence.classify_reason(
        spec.get("keywords") or [],
        abstract,
        fulltext,
        outcome_name=spec.get("name"),
        declared_estimand=spec.get("estimand"),
        row={},
    )
    code = absence.normalize_code(actual.get("reason_code"))
    if code not in {absence.OUTCOME_NOT_IN_SOURCE, absence.SOURCE_NOT_RETRIEVED}:
        return {
            "source_has_value": True,
            "state": code,
            "reason_code": code,
            "value_kind": "text_effect_or_counts",
            "source": "abstract_or_fulltext",
            "source_span": actual.get("source_span") or actual.get("verbatim_span") or "",
            "state_basis": actual.get("state_basis") or "",
        }
    return {
        "source_has_value": False,
        "state": RETRIEVED_OUTCOME_NOT_REPORTED,
        "reason_code": RETRIEVED_OUTCOME_NOT_REPORTED,
        "source_span": actual.get("source_span") or actual.get("verbatim_span") or "",
        "state_basis": actual.get("state_basis") or "retrieved source did not report this registered outcome",
    }


def _rows_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {_norm_id(r.get("id") or r.get("label")): r for r in rows or []}


def _screen_row(review: dict[str, Any], trial_id: str) -> dict[str, Any] | None:
    tid = _norm_id(trial_id)
    for row in (review.get("screening") or {}).get("records") or []:
        if _norm_id(row.get("id")) == tid:
            return row
    return None


def classify_outcome_cell(slug: str, review: dict[str, Any], config: dict[str, Any],
                          records_blob: dict[str, Any], outcome: dict[str, Any],
                          trial_id: str) -> dict[str, Any]:
    specs = {sp.get("name"): sp for sp, _ in outcome_specs(config)}
    spec = specs.get(outcome.get("name"))
    if not spec and outcome.get("primary") and config.get("primary_outcome"):
        spec = config["primary_outcome"]
    spec = spec or {
        "name": outcome.get("name"),
        "keywords": [],
        "estimand": outcome.get("estimand"),
    }
    tid = _norm_id(trial_id)
    pooled = _rows_by_id(outcome.get("trials") or [])
    absent = _rows_by_id(outcome.get("declared_absent_trials") or [])
    row = pooled.get(tid) or absent.get(tid)
    extracted = tid in pooled
    candidate = outcome_source_candidate(slug, records_blob, spec, tid)
    screen = _screen_row(review, tid)
    if screen and screen.get("decision") != "include":
        return {
            "slug": slug,
            "outcome": outcome.get("name"),
            "trial_key": tid,
            "extracted": False,
            "page_state": "SCREEN_EXCLUDED",
            "screening_decision": screen.get("decision"),
            "screening_rule_id": screen.get("rule_id"),
            "source_has_value": bool(candidate.get("source_has_value")),
            "source_state": candidate.get("state"),
            "source_reason_code": candidate.get("reason_code"),
            "source_span": candidate.get("source_span") or "",
            "state_basis": "screen-excluded record is outside included-trial outcome accounting",
            "value_present_not_extracted": False,
            "unaccounted_source_value": False,
            "reason_code_false": False,
            "violation": None,
        }
    stated = _row_code(row)
    source_has_value = bool(candidate.get("source_has_value"))
    source_code = candidate.get("reason_code")
    typed_mismatch = bool(source_has_value and not extracted and stated and source_code and stated != source_code)
    reason_false = bool(source_has_value and not extracted and (stated in FALSE_ABSENCE_CODES or typed_mismatch))
    accounted = extracted or (source_has_value and stated in VALUE_REASON_CODES)
    return {
        "slug": slug,
        "outcome": outcome.get("name"),
        "trial_key": tid,
        "extracted": extracted,
        "page_state": stated,
        "source_has_value": source_has_value,
        "source_state": candidate.get("state"),
        "source_reason_code": candidate.get("reason_code"),
        "source_span": candidate.get("source_span") or "",
        "state_basis": candidate.get("state_basis") or "",
        "value_present_not_extracted": bool(source_has_value and not extracted),
        "unaccounted_source_value": bool(source_has_value and not accounted),
        "reason_code_false": reason_false,
        "violation": REASON_CODE_FALSE if reason_false else None,
    }


def _funding_state(hit: dict[str, Any] | None, source_retrieved: bool) -> str:
    if not hit:
        return "NOT_STATED_IN_RETRIEVED_SOURCE" if source_retrieved else "SOURCE_NOT_RETRIEVED"
    typ = hit.get("type") or ""
    if typ == "mixed":
        return "MIXED"
    if typ.startswith("industry"):
        return "INDUSTRY_SPONSORED"
    if typ.startswith("public") or typ.startswith("non-profit"):
        return "NON_INDUSTRY"
    return "NOT_STATED_IN_RETRIEVED_SOURCE"


KNOWN_FUNDING_STATES = {"INDUSTRY_SPONSORED", "NON_INDUSTRY", "MIXED"}


def funding_candidate(slug: str, records_blob: dict[str, Any], trial_id: str) -> dict[str, Any]:
    tid = _norm_id(trial_id)
    recs = records_by_id(records_blob)
    fulltexts = fulltexts_by_id(slug, records_blob)
    rec = recs.get(tid) or {}
    candidates: list[tuple[str, str]] = []
    if fulltexts.get(tid):
        candidates.append(("full text", fulltexts[tid]))
    if rec.get("abstract") or rec.get("title"):
        candidates.append(("abstract", " ".join(x for x in (rec.get("title"), rec.get("abstract")) if x)))
    nct = _nct_for(tid, rec)
    if nct:
        for r in recs.values():
            rid = _norm_id(r.get("id"))
            if rid == tid:
                continue
            body = " ".join(x for x in (r.get("title"), r.get("abstract")) if x)
            if r.get("nct") == nct or nct in body:
                if fulltexts.get(rid):
                    candidates.append((f"linked full text PMID {rid}", fulltexts[rid]))
                if body:
                    candidates.append((f"linked abstract PMID {rid}", body))
    for source, text in candidates:
        hit = funding.detect(text)
        if hit:
            return {
                "funding_state": _funding_state(hit, True),
                "type": hit.get("type"),
                "span": hit.get("span") or "",
                "source": source,
                "source_retrieved": True,
                "source_has_value": _funding_state(hit, True) in KNOWN_FUNDING_STATES,
            }
    state = _funding_state(None, bool(candidates))
    return {
        "funding_state": state,
        "type": "",
        "span": "",
        "source": candidates[0][0] if candidates else "",
        "source_retrieved": bool(candidates),
        "source_has_value": state in KNOWN_FUNDING_STATES,
    }


def _display_trial_id(trial_id: str) -> str:
    tid = _norm_id(trial_id)
    if tid.upper().startswith("NCT"):
        return tid
    return f"PMID {tid}" if tid else str(trial_id or "")


def _funding_type_from_candidate(cand: dict[str, Any]) -> str:
    state = cand.get("funding_state")
    if state in KNOWN_FUNDING_STATES:
        return cand.get("type") or state.lower()
    if state == "SOURCE_NOT_RETRIEVED":
        return "source not retrieved"
    source = cand.get("source") or ""
    if "full text" in source:
        return "not stated (full text scanned)"
    if source:
        return "not stated (abstract only - full text not retrieved)"
    return "not stated in retrieved source"


def _funding_row_from_candidate(trial_id: str, cand: dict[str, Any]) -> dict[str, Any]:
    row = {
        "id": _display_trial_id(trial_id),
        "type": _funding_type_from_candidate(cand),
        "span": cand.get("span") or "",
        "source": cand.get("source") or "",
        "scanned": cand.get("source") or "",
        "funding_state": cand.get("funding_state"),
    }
    if cand.get("note"):
        row["note"] = cand["note"]
    return row


def classify_funding_cell(slug: str, review: dict[str, Any], records_blob: dict[str, Any],
                          trial_id: str) -> dict[str, Any]:
    tid = _norm_id(trial_id)
    page = next((f for f in review.get("funding") or [] if _norm_id(f.get("id")) == tid), None)
    cand = funding_candidate(slug, records_blob, tid)
    page_type = (page or {}).get("type") or ""
    page_unknown = (
        (not page)
        or page_type.startswith(("not stated", "declared", "stated"))
        or page_type in {"unknown", "", "source not retrieved"}
    )
    source_has_value = cand.get("funding_state") in KNOWN_FUNDING_STATES
    return {
        "slug": slug,
        "trial_key": tid,
        "cell": "funding",
        "page_type": page_type,
        "source_state": cand.get("funding_state"),
        "source_span": cand.get("span") or "",
        "source": cand.get("source") or "",
        "source_has_value": source_has_value,
        "unaccounted_source_value": bool(source_has_value and page_unknown),
        "reason_code_false": bool(source_has_value and page_unknown),
        "violation": REASON_CODE_FALSE if source_has_value and page_unknown else None,
    }


def _effect_source_id(row: dict[str, Any]) -> str:
    source = row.get("source") or ""
    m = re.search(r"PMID\s*(\d{7,9})", source)
    return f"PMID {m.group(1)}" if m else ""


def stamp_identity_fields(review: dict[str, Any]) -> None:
    slug = review.get("slug") or ""
    for outcome in review.get("outcomes") or []:
        oname = outcome.get("name") or "outcome"
        for section in ("trials", "declared_absent_trials"):
            for row in outcome.get(section) or []:
                trial_id = row.get("trial_id") or row.get("id") or row.get("label")
                trial_id = str(trial_id or "").strip()
                effect_source = row.get("effect_source_id") or _effect_source_id(row)
                report_id = effect_source or trial_id
                row.setdefault("trial_id", trial_id)
                row.setdefault("report_id", report_id)
                if effect_source:
                    row.setdefault("effect_source_id", effect_source)
                row.setdefault("outcome_effect_id", f"{slug}::{oname}::{trial_id}::{report_id}")


_PUBLISHED_EFFECT_IN_SOURCE = re.compile(
    r"\b(relative risk|risk ratio|hazard ratio|odds ratio|rate ratio)\b.{0,80}(95%|confidence interval|\bci\b)",
    re.I,
)


def annotate_reconstruction_with_published_effect(review: dict[str, Any]) -> None:
    for outcome in review.get("outcomes") or []:
        for row in outcome.get("trials") or []:
            if row.get("derivation") != "reconstructed":
                continue
            source = row.get("source") or ""
            if not _PUBLISHED_EFFECT_IN_SOURCE.search(source):
                continue
            row["consumer_consistency_state"] = EXTRACTED_RECONSTRUCTION_WHILE_PUBLISHED_EXISTS
            row["source_warning"] = (
                "source span also reports an effect estimate with confidence interval; "
                "row keeps the existing reconstruction and is flagged for human review"
            )


def annotate_review(review: dict[str, Any], slug: str, config: dict[str, Any],
                    records_blob: dict[str, Any]) -> dict[str, Any]:
    stamp_identity_fields(review)
    annotate_reconstruction_with_published_effect(review)
    specs = {sp.get("name"): sp for sp, _ in outcome_specs(config)}
    for outcome in review.get("outcomes") or []:
        spec = specs.get(outcome.get("name"))
        if not spec:
            continue
        for row in outcome.get("declared_absent_trials") or []:
            if row.get("state") in ADMISSION_SET_ASIDE_STATES and isinstance(row.get("admission_verdict"), dict):
                # A row the build set aside on ADMISSION (harness/admission.py, P5, 2026-09-21) keeps its state: its
                # source-visible value was extracted and refused on admission, not left unextracted -- relabelling it
                # KNOWN_REPORTED_NOT_YET_EXTRACTED here stated a wrong reason on esketamine's two rows at the first rebuild.
                continue
            tid = _norm_id(row.get("id") or row.get("label"))
            cand = outcome_source_candidate(slug, records_blob, spec, tid)
            if not cand.get("source_has_value"):
                continue
            current_code = _row_code(row)
            replacement_code = cand.get("reason_code") or KNOWN_REPORTED_NOT_YET_EXTRACTED
            if current_code not in FALSE_ABSENCE_CODES and current_code == replacement_code:
                continue
            if current_code not in FALSE_ABSENCE_CODES and replacement_code not in {
                KNOWN_REPORTED_NOT_YET_EXTRACTED,
                "RETRIEVED_REFUSED_WITH_REASON",
                "UNIT_MISMATCH_CYCLE_LEVEL",
            }:
                continue
            code = replacement_code
            state = cand.get("state") or EXTRACTION_DEBT
            row["reason_code"] = code
            row["state"] = state
            row["source_span"] = cand.get("source_span") or ""
            row["verbatim_span"] = cand.get("source_span") or ""
            row["state_basis"] = cand.get("state_basis") or ""
            row["reason"] = (
                "source-visible value was not pooled; recorded as extraction debt / typed refusal, "
                "not as absence"
            )
            row["extraction_debt"] = {
                "value_kind": cand.get("value_kind"),
                "source": cand.get("source"),
                "source_span": cand.get("source_span"),
            }
    # Refresh funding rows with cached ft_*.txt where available and carry explicit funding states.
    recs = records_by_id(records_blob)
    fulltexts = fulltexts_by_id(slug, records_blob)
    refreshed = funding.scan_pooled({"outcomes": review.get("outcomes") or []}, recs, fulltexts)
    by_id = {_norm_id(f.get("id")): f for f in (review.get("funding") or [])}
    by_id.update({_norm_id(f.get("id")): f for f in refreshed})
    for tid in included_trial_ids(review):
        cand = funding_candidate(slug, records_blob, tid)
        by_id[tid] = _funding_row_from_candidate(tid, cand)
    for tid, row in list(by_id.items()):
        cand = funding_candidate(slug, records_blob, tid)
        if cand.get("source_has_value"):
            row["type"] = cand.get("type") or row.get("type", "")
            row["span"] = cand.get("span") or row.get("span", "")
            row["source"] = cand.get("source") or row.get("source")
            row["scanned"] = cand.get("source") or row.get("scanned")
        row["funding_state"] = cand.get("funding_state")
    if by_id:
        review["funding"] = list(by_id.values())
    return review


def included_trial_ids(review: dict[str, Any]) -> list[str]:
    ids = []
    for row in (review.get("screening") or {}).get("records") or []:
        if row.get("decision") != "include":
            continue
        tid = _norm_id(row.get("id"))
        if tid:
            ids.append(tid)
    return sorted(dict.fromkeys(ids))


def sweep_review(slug: str, review: dict[str, Any], config: dict[str, Any],
                 records_blob: dict[str, Any]) -> dict[str, Any]:
    rows = []
    ids = included_trial_ids(review)
    for outcome in review.get("outcomes") or []:
        for tid in ids:
            rows.append(classify_outcome_cell(slug, review, config, records_blob, outcome, tid))
    for tid in ids:
        rows.append(classify_funding_cell(slug, review, records_blob, tid))
    n_cells = len(rows)
    n_unaccounted = sum(1 for r in rows if r.get("unaccounted_source_value"))
    n_false = sum(1 for r in rows if r.get("reason_code_false"))
    return {
        "slug": slug,
        "n_cells": n_cells,
        "n_source_value_not_accounted": n_unaccounted,
        "n_reason_code_false": n_false,
        "summary": (
            f"{n_unaccounted} outcome/trial-or-funding cells with a value in source but not accounted "
            f"of {n_cells} included-trial registered-outcome/funding cells; "
            f"{n_false} reason codes factually wrong of {n_cells}"
        ),
        "rows": rows,
    }


def load_topic_config(slug: str) -> dict[str, Any]:
    path = ROOT / "topics" / f"{slug}.json"
    return _load_json(path) if path.exists() else {}
