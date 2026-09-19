"""Harm-outcome recovery audit.

This module does not extract or pool new numbers. It reads the same committed
sources and the same outcome objects the efficacy path uses, then labels harm
rows with the explicit HM absence ontology and marks incomplete harm panels.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from . import absence, extract, lexicon

NOT_RETRIEVED = "NOT_RETRIEVED"
RETRIEVED_OUTCOME_NOT_REPORTED = "RETRIEVED_OUTCOME_NOT_REPORTED"
RETRIEVED_INCOMPATIBLE_STRUCTURE = "RETRIEVED_INCOMPATIBLE_STRUCTURE"
RETRIEVED_REFUSED_WITH_REASON = "RETRIEVED_REFUSED_WITH_REASON"
KNOWN_REPORTED_NOT_YET_EXTRACTED = "KNOWN_REPORTED_NOT_YET_EXTRACTED"

_REPORTED_STATES = {
    RETRIEVED_INCOMPATIBLE_STRUCTURE,
    RETRIEVED_REFUSED_WITH_REASON,
    KNOWN_REPORTED_NOT_YET_EXTRACTED,
}

INCOMPLETE_MESSAGE = "HARMS EXTRACTION INCOMPLETE — no class-level quantitative safety conclusion issued"


def reporting_ledger(outcome):
    """Keep every reporting row, including typed refusals; typed refusals resolve debt, but cannot support synthesis."""
    rows = {}
    for item in (outcome.get("result") or {}).get("harm_reporting_trials") or []:
        rows[_id_key(item.get("id") or item.get("label"))] = dict(item)
    for trial in outcome.get("trials") or []:
        key = _id_key(trial.get("id") or trial.get("label"))
        span = trial.get("source_span") or trial.get("verbatim_span") or trial.get("source")
        rows[key] = dict(rows.get(key, {}), id=key, label=trial.get("label"),
                         state="EXTRACTED" if span else "UNRESOLVED", span=span,
                         extracted=bool(span))
    for trial in outcome.get("declared_absent_trials") or []:
        key = _id_key(trial.get("id") or trial.get("label"))
        code = trial.get("reason_code") or trial.get("state")
        if (trial.get("harm_source_reported") or key in rows
                or ("harm_source_reported" not in trial
                    and (code in _INCOMPATIBLE_CODES or code == absence.REFUSED_ON_EVIDENCE))):
            rows[key] = dict(rows.get(key, {}), id=key, label=trial.get("label"),
                             state=trial.get("harm_absence_state") or code or "UNRESOLVED", extracted=False,
                             reason_code=code,
                             reason=trial.get("reason") or "Extraction unresolved",
                             span=trial.get("source_span") or trial.get("verbatim_span")
                             or trial.get("harm_source_span"))
    return list(rows.values())


def synthesis_incomplete(outcome):
    if outcome.get("kind") != "harm":
        return False
    result = outcome.get("result") or {}
    return bool(result.get("harms_incomplete") or result.get("state") == "HARMS_INCOMPLETE"
                or any(r.get("state") != "EXTRACTED" or not r.get("span")
                       for r in reporting_ledger(outcome)))


def _ladder(pid, rec_by_id, fulltext_by_pmid, trial=None):
    # Only name checks actually performed here. Held text is not proof that all rungs were searched.
    ladder = [
        {"rung": "abstract", "state": "CHECKED" if (rec_by_id.get(pid) or {}).get("abstract") else "NOT_CHECKED"},
        {"rung": "held full text", "state": "CHECKED" if (fulltext_by_pmid or {}).get(pid) else "NOT_CHECKED"},
        {"rung": "supplement / registry results / regulatory source", "state": "NOT_CHECKED_BY_HARMS_AUDIT",
         "obligation": "Locate outcome-specific evidence or record a source-backed refusal; no completed search inferred."},
    ]
    trial = trial or {}
    document = trial.get("document_ref")
    if document:
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        path = (root / document).resolve()
        span = trial.get("source_span") or trial.get("verbatim_span") or ""
        checked = False
        if span and path.is_relative_to(root) and path.is_file():
            checked = " ".join(span.split()) in " ".join(path.read_text(encoding="utf-8").split())
        ladder.append({"rung": "located adjudication source: " + document,
                       "state": "CHECKED_LOCATED_SPAN" if checked else "SPAN_NOT_VERIFIED",
                       "obligation": "Typed refusal resolves the extraction obligation; other routes remain unverified."})
    return ladder

_INCOMPATIBLE_CODES = {
    absence.EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH,
    absence.COUNTS_PRESENT_NOT_CORROBORATED,
    absence.MULTI_ARM_UNRESOLVED,
    absence.TIMEPOINT_MISMATCH,
    absence.POPULATION_MISMATCH,
}

_REFUSAL_CODES = {
    absence.REFUSED_ON_EVIDENCE,
    absence.SIGNAL_SPURIOUS,
}

_EFFECT_OR_COMPARISON = re.compile(
    r"\b(?:RR|OR|HR|IRR|relative risk|risk ratio|hazard ratio|odds ratio|rate ratio)\b"
    r"[^.;]{0,90}?\d+(?:\.\d+)?"
    r"|(?:\d+(?:\.\d+)?\s*%\s*(?:per year)?[^.;]{0,80}?"
    r"(?:vs\.?|versus|compared with|as compared with|and in|in the placebo|in the warfarin)"
    r"[^.;]{0,80}?\d+(?:\.\d+)?\s*%)"
    r"|(?:\d+\s*(?:/|of)\s*\d+[^.;]{0,90}?"
    r"(?:vs\.?|versus|compared with|as compared with|and in)"
    r"[^.;]{0,90}?\d+\s*(?:/|of)\s*\d+)",
    re.I,
)


def _terms(spec: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for value in list(spec.get("keywords") or []) + [spec.get("name")]:
        if not value:
            continue
        folded = lexicon.fold(str(value)).replace("-", " ")
        folded = re.sub(r"[^a-z0-9 ]+", " ", folded)
        folded = re.sub(r"\s+", " ", folded).strip()
        if len(folded) >= 3:
            out.append(folded)
    more = set()
    for term in out:
        if "bleed" in term:
            more.update({"bleeding", "major bleeding", "hemorrhage", "haemorrhage"})
        if "atrial fibrillation" in term:
            more.update({"atrial fibrillation", "atrial flutter"})
        if "gastro" in term:
            more.update({"gastrointestinal", "diarrhea", "diarrhoea", "nausea", "vomiting"})
        if "discontinu" in term or "withdraw" in term:
            more.update({"discontinuation", "discontinued", "withdrawal", "withdrew"})
        if "ketoacidosis" in term:
            more.add("ketoacidosis")
        if "amputation" in term:
            more.add("amputation")
        if "adverse event" in term:
            more.update({"adverse event", "adverse events", "side effect", "side effects"})
    out.extend(sorted(more))
    return sorted(set(out), key=len, reverse=True)


def _matches(sentence: str, terms: list[str]) -> bool:
    sf = lexicon.fold(sentence).replace("-", " ")
    return any(t in sf for t in terms)


def reporting_signal(text: str | None, spec: dict[str, Any]) -> dict[str, Any] | None:
    """Return a conservative source-reporting signal for a harm outcome, if one is visible."""
    if not text:
        return None
    terms = _terms(spec)
    if not terms:
        return None
    for sent in extract._sentences(extract._norm(text)):
        name = str(spec.get("name") or "").lower()
        folded = lexicon.fold(sent).lower()
        if "gastro" in name and not any(t in folded for t in ("gastrointestinal", "nausea", "vomiting", "diarrh")):
            continue
        if "discontinu" in name and not (any(t in folded for t in ("discontinu", "withdraw")) and any(t in folded for t in ("adverse", "side effect", "toxicity"))):
            continue
        if not _matches(sent, terms):
            continue
        compact = re.sub(r"\s+", " ", sent).strip()
        if _EFFECT_OR_COMPARISON.search(compact):
            return {"reported": True, "kind": "numeric_signal", "span": compact[:300]}
        # Even non-numeric harm reporting is not outcome absence. It remains extraction debt.
        return {"reported": True, "kind": "term_signal", "span": compact[:300]}
    return None


def _id_key(value: Any) -> str:
    return str(value or "").replace("PMID ", "").strip()


def _source_text(row_id: str, rec_by_id: dict[str, dict[str, Any]],
                 fulltext_by_pmid: dict[str, str] | None) -> str:
    rec = rec_by_id.get(row_id) or {}
    parts = [rec.get("abstract") or ""]
    if fulltext_by_pmid and row_id in fulltext_by_pmid:
        parts.append(fulltext_by_pmid[row_id] or "")
    return "\n".join(p for p in parts if p)


def _hm_state_for_absent(row: dict[str, Any], spec: dict[str, Any],
                         rec_by_id: dict[str, dict[str, Any]],
                         fulltext_by_pmid: dict[str, str] | None) -> dict[str, Any]:
    code = row.get("reason_code") or row.get("state")
    pid = _id_key(row.get("id") or row.get("label"))
    text = _source_text(pid, rec_by_id, fulltext_by_pmid)
    sig = reporting_signal(text, spec)
    if code == absence.SOURCE_NOT_RETRIEVED or not (rec_by_id.get(pid) or {}).get("abstract"):
        state = NOT_RETRIEVED
    elif sig and code in (absence.OUTCOME_NOT_IN_SOURCE, "NO_OUTCOME_DATA_IN_SOURCE", None, ""):
        state = KNOWN_REPORTED_NOT_YET_EXTRACTED
    elif code in (absence.EXTRACTION_NOT_PERFORMED, absence.COUNTS_PRESENT_NOT_CORROBORATED):
        state = KNOWN_REPORTED_NOT_YET_EXTRACTED
    elif code in _INCOMPATIBLE_CODES:
        state = RETRIEVED_INCOMPATIBLE_STRUCTURE
    elif code in _REFUSAL_CODES or row.get("absent_kind") == "refused_on_evidence":
        state = RETRIEVED_REFUSED_WITH_REASON
    else:
        state = RETRIEVED_OUTCOME_NOT_REPORTED
    out = {"harm_absence_state": state}
    if sig:
        out["harm_source_reported"] = code != absence.SIGNAL_SPURIOUS
        out["harm_source_span"] = sig["span"]
        out["harm_source_signal"] = sig["kind"]
    else:
        out["harm_source_reported"] = code != absence.SIGNAL_SPURIOUS and state in _REPORTED_STATES
    return out


def _zero_cell(t: dict[str, Any]) -> bool:
    if not all(t.get(k) is not None for k in ("ai", "ci", "n1i", "n2i")):
        return False
    return min(t["ai"], t["ci"], t["n1i"] - t["ai"], t["n2i"] - t["ci"]) == 0


def annotate_outcome(outcome: dict[str, Any], spec: dict[str, Any], included: list[dict[str, Any]],
                     rec_by_id: dict[str, dict[str, Any]],
                     fulltext_by_pmid: dict[str, str] | None = None) -> dict[str, Any]:
    if outcome.get("kind") != "harm":
        return outcome
    pooled = {_id_key(t.get("id") or t.get("label")) for t in outcome.get("trials") or []}
    reporting = []
    unresolved = []
    states = {}
    for t in outcome.get("trials") or []:
        key = _id_key(t.get("id") or t.get("label"))
        states[key] = "EXTRACTED"
        t["harm_absence_state"] = "EXTRACTED"
        t["harm_source_reported"] = True
        reporting.append({"id": key, "label": t.get("label"), "state": "EXTRACTED", "extracted": True})
        if _zero_cell(t):
            t["continuity_correction"] = (
                "0.5 continuity correction applied by synth.Study.yi_vi because this study has at least "
                "one zero cell; correction is per-study and disclosed here."
            )
    for row in outcome.get("declared_absent_trials") or []:
        ann = _hm_state_for_absent(row, spec, rec_by_id, fulltext_by_pmid)
        row.update(ann)
        key = _id_key(row.get("id") or row.get("label"))
        states[key] = ann["harm_absence_state"]
        if ann["harm_absence_state"] in _REPORTED_STATES and ann["harm_source_reported"]:
            item = {
                "id": key,
                "label": row.get("label"),
                "state": ann["harm_absence_state"],
                "span": row.get("harm_source_span") or row.get("source_span") or row.get("verbatim_span"),
            }
            reporting.append(item)
            if ann["harm_absence_state"] == KNOWN_REPORTED_NOT_YET_EXTRACTED:
                unresolved.append(item)
    for d in included:
        key = _id_key(d.get("id"))
        if key in pooled or key in states:
            continue
        sig = reporting_signal(_source_text(key, rec_by_id, fulltext_by_pmid), spec)
        if sig:
            unresolved.append({"id": key, "label": key, "state": KNOWN_REPORTED_NOT_YET_EXTRACTED,
                               "span": sig["span"]})
            reporting.append(unresolved[-1])
    result = outcome.setdefault("result", {})
    result["harm_reporting_trials"] = reporting
    reporting = reporting_ledger(outcome)
    by_id = {_id_key(t.get("id") or t.get("label")): t
             for t in (outcome.get("trials") or []) + (outcome.get("declared_absent_trials") or [])}
    for item in reporting:
        item["source_ladder"] = _ladder(item["id"], rec_by_id, fulltext_by_pmid, by_id.get(item["id"]))
    result["harm_reporting_trials_n"] = len(reporting)
    result["harm_extracted_trials_n"] = len(outcome.get("trials") or [])
    result["harm_registered_trials_n"] = len(included)
    if reporting:
        result["harm_reporting_trials"] = reporting
    if unresolved:
        names = [str(x.get("label") or x.get("id")) for x in unresolved]
        result["harms_incomplete"] = True
        result["known_reported_not_yet_extracted"] = unresolved
        result["reason"] = (
            "HARMS_INCOMPLETE -- "
            f"{len(unresolved)} known reported outcome(s) unresolved ({', '.join(names[:8])}) "
            f"among {len(reporting)} source-reporting trial(s); extracted k="
            f"{len(outcome.get('trials') or [])}. The page must not render this as harm absence."
        )
    elif not outcome.get("trials") and result.get("present") is False:
        states_present = {row.get("harm_absence_state") for row in outcome.get("declared_absent_trials") or []}
        if states_present and states_present <= {RETRIEVED_OUTCOME_NOT_REPORTED}:
            result["harm_absence_certified"] = True
        elif states_present:
            result["reason"] = (
                "No harm value is poolable, but the registered trials are not all certified "
                f"{RETRIEVED_OUTCOME_NOT_REPORTED}; states=" + ", ".join(sorted(s for s in states_present if s))
            )
    if synthesis_incomplete(outcome):
        result["harms_synthesis_suppressed"] = True
        from . import claim
        result["claim"] = claim.derive(result)
    return outcome


def annotate_review(review: dict[str, Any], specs_by_name: dict[str, dict[str, Any]],
                    included: list[dict[str, Any]], rec_by_id: dict[str, dict[str, Any]],
                    fulltext_by_pmid: dict[str, str] | None = None) -> dict[str, Any]:
    harms = [o for o in review.get("outcomes") or [] if o.get("kind") == "harm"]
    for outcome in harms:
        spec = specs_by_name.get(outcome.get("name")) or {"name": outcome.get("name"), "keywords": []}
        annotate_outcome(outcome, spec, included, rec_by_id, fulltext_by_pmid)
    if not harms:
        common = {"name": "registered harms", "keywords": [
            "major bleeding", "bleeding", "adverse event", "adverse events", "ketoacidosis",
            "amputation", "atrial fibrillation", "gastrointestinal", "discontinuation",
        ]}
        hits = []
        for d in included:
            key = _id_key(d.get("id"))
            sig = reporting_signal(_source_text(key, rec_by_id, fulltext_by_pmid), common)
            if sig:
                hits.append({"id": key, "label": key, "span": sig["span"]})
        if hits:
            review["harms_registry_state"] = {
                "state": KNOWN_REPORTED_NOT_YET_EXTRACTED,
                "reason": (
                    "HARMS_INCOMPLETE -- no harm outcome is registered in this topic object, "
                    f"but {len(hits)} included trial source(s) contain harm reporting. Register harm "
                    "outcomes or explicitly certify source non-reporting before rendering 'no harms recorded'."
                ),
                "known_reported_not_yet_extracted": hits,
            }
    return review


def sweep_topic(review: dict[str, Any]) -> dict[str, Any]:
    harms = [o for o in review.get("outcomes") or [] if o.get("kind") == "harm"]
    rows = []
    incomplete = 0
    known_debt = 0
    for o in harms:
        res = o.get("result") or {}
        if synthesis_incomplete(o):
            incomplete += 1
        known_debt += len(res.get("known_reported_not_yet_extracted") or [])
        for t in o.get("trials") or []:
            rows.append({"outcome": o.get("name"), "trial": t.get("label"), "id": t.get("id"),
                         "source_has_harm": True, "extracted": True, "state": "EXTRACTED"})
        for a in o.get("declared_absent_trials") or []:
            rows.append({"outcome": o.get("name"), "trial": a.get("label"), "id": a.get("id"),
                         "source_has_harm": bool(a.get("harm_source_reported")),
                         "extracted": False,
                         "state": a.get("harm_absence_state") or a.get("state"),
                         "span": a.get("harm_source_span")})
    return {
        "slug": review.get("slug"),
        "harm_outcomes": len(harms),
        "harm_outcomes_incomplete": incomplete,
        "known_reported_not_yet_extracted_trials": known_debt,
        "rows": rows,
    }


def write_sweep(reviews_root: str, out_path: str) -> dict[str, Any]:
    topics = []
    for name in sorted(os.listdir(reviews_root)):
        rp = os.path.join(reviews_root, name, "review.json")
        if not os.path.exists(rp):
            continue
        with open(rp, encoding="utf-8") as f:
            topics.append(sweep_topic(json.load(f)))
    n_outcomes = sum(t["harm_outcomes"] for t in topics)
    n_incomplete = sum(t["harm_outcomes_incomplete"] for t in topics)
    n_debt = sum(t["known_reported_not_yet_extracted_trials"] for t in topics)
    out = {
        "denominator": "all docs/reviews/* review.json harm outcomes after HM annotation",
        "topics": topics,
        "n_harm_outcomes_rendered_k_lt_reporting_trials": n_incomplete,
        "n_harm_outcomes_suppressed": n_incomplete,
        "n_pages_with_suppressed_harm_outcomes": sum(t["harm_outcomes_incomplete"] > 0 for t in topics),
        "N_harm_outcomes": n_outcomes,
        "n_trials_with_KNOWN_REPORTED_NOT_YET_EXTRACTED": n_debt,
        "N_topics": len(topics),
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return out
