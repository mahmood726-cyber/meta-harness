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

from . import absence, evidence_identity, extract

REASON_TRUE = "REASON_TRUE"
REASON_FALSE_VALUE_HELD = "REASON_FALSE_VALUE_HELD"
# V1.0.1: held numbers exist, but none is evidence ABOUT the refused claim on every typed field (role, part, timepoint, population,
# measure, comparison, and a design-appropriate model for a design refusal). The candidates are listed with their mismatches.
REASON_NOT_DISPROVED = "REASON_NOT_DISPROVED"
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
_OWN_NCT = re.compile(r"\bNCT\s*(\d{8})\b", re.I)
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
    results = records.get("ctgov_results", {}) if isinstance(records, dict) else {}
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
                    raw = fp.read_text(encoding="utf-8")
                    rows.append({
                        "source_id": f"fulltext:{key}",
                        "source_kind": "fulltext",
                        "text": _plain(raw),
                        "raw": raw,              # tables keep their rows, headers and model footnotes (evidence_identity)
                    })
                except OSError:
                    pass
        registry_text = _record_text(rec)
        if registry_text and (str(rec.get("id_type") or "").lower() == "nct" or str(key).upper().startswith("NCT")):
            rows.append({"source_id": f"registry:{key}", "source_kind": "registry", "text": registry_text})
        # ONLY PubMed's own DataBank accession ties a registry record to this trial. An NCT merely named in the text may be another
        # trial's (review round 2, G1: 'an earlier unrelated trial was registered as NCT...'): never attach from text.
        match = _OWN_NCT.fullmatch(norm_space(rec.get("nct")) or "")
        nct = f"NCT{match[1]}" if match else None
        measures = results.get(nct, []) if nct and isinstance(results, dict) else []
        if isinstance(measures, list):
            for index, measure in enumerate(measures):
                if not isinstance(measure, dict):
                    continue
                # Canonical JSON is a lossless text rendering: all fields, nested
                # group denominators/values and analyses are copied, never computed.
                rendered = json.dumps(measure, ensure_ascii=False, sort_keys=True, indent=2)
                rows.append({"source_id": f"registry_results:{key}:{nct}:{index}",
                             "source_kind": "registry_results", "nct": nct,
                             "text": rendered, "registry_measure": rendered})
    return out


def _candidate_sentences(text: str, keywords: list[str], outcome_name: str | None) -> list[str]:
    candidates = absence._candidate_sentences(text, keywords, outcome_name)  # audit-only reuse
    if candidates:
        return candidates
    terms = absence._terms(keywords, outcome_name)
    if not terms:
        return []
    return [norm_space(s) for s in extract._sentences(_plain(text)) if absence._matches_term(s, terms)]


def _sentences_about(text: str, keywords: list[str], outcome_name: str | None) -> list[str]:
    """Keyword-selected sentences, plus every sentence one of whose per-result clauses names the outcome by its OWN name
    ('At day 28, ...; mortality was 6/16 vs 2/14' for '28-day all-cause mortality'): a held result must not be missed because its
    sentence lacks a keyword PHRASE. The typed identity then decides whether it is about the claim."""
    picked = list(_candidate_sentences(text, keywords, outcome_name))
    seen = set(picked)
    for s in extract._sentences(_plain(text)):
        s = norm_space(s)
        if s in seen:
            continue
        # Read each numeric result under its own endpoint, even when it will fail the requested outcome or part gate.
        if evidence_identity.result_clauses(s) or evidence_identity._effects(s):
            picked.append(s)
            seen.add(s)
    return picked


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


def typed_candidates(
    outcome: dict[str, Any],
    row: dict[str, Any],
    sources: list[dict[str, str]],
    spec: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Every held number the auditor could cite for this refused row, as a typed identity with its mismatches against the typed
    refused claim (harness.evidence_identity). Sentences first (regex), then table rows (headers + model footnotes). Fewest
    mismatches first; a full match has an empty mismatch list."""
    spec = spec or {}
    keywords = spec.get("keywords") or []
    terms = absence._terms(keywords, outcome.get("name"))
    claim = evidence_identity.claim_of(outcome, row, " ".join(keywords))
    # keywords that say only 'an adverse event happened' never NAME a specific outcome (extract.GENERIC_HARM)
    specific = absence._terms([k for k in keywords if k.lower() not in extract.GENERIC_HARM], outcome.get("name"))
    if evidence_identity._GENERIC_AE_NAME.search(outcome.get("name") or ""):
        specific = []                                 # an aggregate category is named by its own name, never by a component keyword
        terms = []
    claim["permitted_measures"] = list(spec.get("permitted_measures") or [])      # only what the committed spec declares
    trial = canonical_trial_id(row.get("id") or row.get("label"))
    proposals: dict[str, Any] = {}          # no pinned producer reads a model proposal (reproducible-AI contract)
    out: list[dict[str, Any]] = []
    seen = set()

    def type_endpoint(ident: dict[str, Any], label: str, definitions: dict[str, str]) -> bool:
        reference = evidence_identity.endpoint_reference(label)
        resolved = definitions.get(reference) if reference else None
        naming_label = resolved or label
        if resolved:
            ident["endpoint_resolved_from"] = resolved
            ident["part"] = evidence_identity.part_of(resolved)
        ident["definition"] = evidence_identity.definition_of(naming_label, outcome.get("name") or "")
        # Without its own definition a named reference supplies no outcome identity, even if
        # a keyword appears incidentally in an arm name or the remainder of the result clause.
        if reference and not resolved:
            return False
        return (evidence_identity.names_the_outcome(naming_label, outcome.get("name") or "")
                or (bool(specific) and absence._matches_term(naming_label, specific)))

    for src in sources or []:
        sid = src.get("source_id") or "held_source"
        if src.get("source_kind") == "registry_results":
            # Read structured cells as structured cells, not accidental numbers in
            # group descriptions. Use the very same naming and mismatch gates.
            for ident in evidence_identity.from_registry_measure(
                    json.loads(src["registry_measure"]), trial, sid):
                named = type_endpoint(ident, ident["label"], {})
                ident["mismatch"] = evidence_identity.mismatches(ident, claim, outcome_named=named)
                if ident.get("confidence_bound"):
                    ident["mismatch"].append("precision:ONE_SIDED_CI")
                out.append(ident)
            continue
        definitions = evidence_identity.endpoint_definitions(extract._sentences(_plain(src.get("text") or "")))
        for sent in _sentences_about(src.get("text") or "", keywords, outcome.get("name")):
            if (sid, sent) in seen or not (_has_numeric_outcome(sent) or evidence_identity.result_clauses(sent) or evidence_identity._effects(sent)):
                continue
            seen.add((sid, sent))
            sent = evidence_identity.strip_glued_heading(sent)   # a glued section heading never names the result
            clauses = evidence_identity.result_clauses(sent)
            if not clauses:                               # an effect-only sentence: one identity, named and defined like any other
                ident = evidence_identity.from_sentence(sent, trial, sid, proposals)
                parts = evidence_identity.CLAUSE_BOUNDARY.split(sent)
                own = next((p for p in parts if re.search(r"\d", p)), sent)          # the clause that holds the numbers
                named = type_endpoint(ident, own, definitions)
                ident["mismatch"] = evidence_identity.mismatches(ident, claim, outcome_named=named)
                if ident.get("confidence_bound"):
                    ident["mismatch"].append("precision:ONE_SIDED_CI")
                out.append(ident)
                continue
            sent_tp = evidence_identity.leading_timepoint(sent)   # only a leading adverbial governs every clause
            patient_subject = False
            for cl in clauses:                            # one identity per result, typed by its OWN clause; never summed
                label = cl["label"]
                ident = evidence_identity.from_sentence(label, trial, sid, proposals, context_timepoint=sent_tp)
                if ident["role"] == "UNDECIDED":        # recorded role proposals are keyed on the whole sentence
                    whole = evidence_identity.from_sentence(sent, trial, sid, proposals)
                    if whole["role"] != "EFFECT_ESTIMATE":
                        ident.update(role=whole["role"], role_basis=whole["role_basis"], role_record_id=whole["role_record_id"])
                # Read representation independently of role; counts, percentages, rates and closing effects stay separate.
                ident.update(arms=cl["arms"], estimate=None, ci=None,
                             effect_measure={"pct": "PERCENT", "rate": "RATE"}.get(cl["kind"], "COUNTS"))
                if cl["kind"] == "rate":
                    ident["unit"] = "PATIENT_YEARS"
                if cl.get("shared"):
                    ident["comparison"] = "TWO_ARMS_NAMED"
                if cl.get("comparison"):
                    ident["comparison"] = cl["comparison"]
                if (not ident.get("unit") and evidence_identity._PATIENT_SUBJECT.search(sent)
                        and not evidence_identity._UNIT_EVENTS.search(label)):
                    ident["unit"] = "PATIENTS_WITH_EVENT"
                # A coordinated 'had N or more episodes' predicate counts the previously explicit patient subject, not episodes.
                if patient_subject and re.search(r"\bhad\s+(?:\d+|one)\s+or more\s+episodes?\b", label, re.I):
                    ident["unit"] = "PATIENTS_WITH_EVENT"
                patient_subject |= ident.get("unit") == "PATIENTS_WITH_EVENT"
                named = type_endpoint(ident, label, definitions)
                ident["mismatch"] = evidence_identity.mismatches(ident, claim, outcome_named=named)
                out.append(ident)
                for effect in cl.get("effects", []):
                    estimate = {**ident, **{k: v for k, v in effect.items() if k not in ("start", "end")},
                                "role": "EFFECT_ESTIMATE", "role_basis": "REGEX",
                                "span": label + " " + cl["raw_tail"][effect["start"]:effect["end"]]}
                    estimate["mismatch"] = evidence_identity.mismatches(estimate, claim, outcome_named=named)
                    if estimate.get("confidence_bound"):
                        estimate["mismatch"].append("precision:ONE_SIDED_CI")
                    out.append(estimate)
        # labelled COUNT rows of the same source's tables: when a number is rejected as the wrong endpoint (e.g. 'any adverse
        # event' offered for a specific endpoint), the correctly labelled row is searched for HERE, never summed from symptom rows
        for ident in evidence_identity.count_rows(src.get("raw") or "", trial, sid):
            named = evidence_identity.names_the_outcome(ident["label"], outcome.get("name") or "")
            ident["definition"] = evidence_identity.definition_of(ident["label"], outcome.get("name") or "")
            ident["mismatch"] = evidence_identity.mismatches(ident, claim, outcome_named=named)
            out.append(ident)
        for ident in evidence_identity.from_tables(src.get("raw") or "", trial, sid):
            named = (bool(terms) and absence._matches_term(ident.get("label") or "", terms)) if terms else \
                evidence_identity.names_the_outcome(ident.get("label") or "", outcome.get("name") or "")   # aggregate: own name only
            ident["definition"] = evidence_identity.definition_of(ident["label"], outcome.get("name") or "")
            ident["mismatch"] = evidence_identity.mismatches(ident, claim, outcome_named=named)
            out.append(ident)
    if spec.get("target_population") and out:
        from . import held_rows
        for f in held_rows.subpopulation_flags(sources or [], [spec["target_population"]]):
            for c in out:
                c["mismatch"].append(f"population:ELIGIBILITY_ADJUDICATION_REQUIRED({f['subpopulation']} {f['share_percent']:g}%)")
    out.sort(key=lambda c: len(c["mismatch"]))
    return out


_PER_ARM_DENOMINATOR = re.compile(r"\b\d[\d,]*\s*/\s*\d[\d,]*\b|\b\d[\d,]*\s+(?:out\s+)?of\s+(?:the\s+)?\d[\d,]*\b|\(\s*n\s*=\s*\d", re.I)


def _answers_reason(code: str, cand: dict[str, Any], row: dict[str, Any]) -> str | None:
    """None if this full-match candidate answers the refusal's OWN reason; else why it does not (it then never disproves it)."""
    span = norm_space(_plain(cand.get("span") or ""))
    arms = cand.get("arms") or []
    pct_corroborated = len(arms) == 2 and all(a.get("events") is not None and a.get("pct") is not None for a in arms)
    if code == absence.COUNTS_PRESENT_NOT_CORROBORATED and cand.get("role") != "EFFECT_ESTIMATE" \
            and len(_PER_ARM_DENOMINATOR.findall(span)) < 2 and not pct_corroborated:
        return "reason_scope:COUNTS_NOT_CORROBORATED (no per-arm denominators; the refusal already conceded the counts)"
    if code in ("RESULT_INCOMPATIBLE", "ENDPOINT_UNBOUND"):
        stated = norm_space(_plain(row.get("source_span") or row.get("verbatim_span") or ""))
        key = span[:80].rstrip(". ")
        if stated and key and (key in stated or stated[:80].rstrip(". ") in span):
            return f"reason_scope:{code} (the refusal already weighed this span)"
    return None


def _scoped(code: str, cands: list[dict[str, Any]], row: dict[str, Any]) -> list[dict[str, Any]]:
    """Full matches that also answer the refusal's reason; a full match that does not gets the reason as its mismatch."""
    for c in cands:
        if not c["mismatch"]:
            why = _answers_reason(code, c, row)
            if why:
                c["mismatch"] = [why]
    return [c for c in cands if not c["mismatch"]]


def audit_cited_chain(outcome: dict[str, Any], row: dict[str, Any], cited_span: str, spec: dict[str, Any] | None = None) -> dict[str, Any]:
    """Judge the evidence a served verdict CITED, alone: REASON_FALSE_VALUE_HELD only if that span is a full match to the refused claim
    (outcome + timepoint + aggregation level + measure + unit ...); otherwise REASON_NOT_DISPROVED with the fields it fails on. A
    correct route elsewhere is a separate finding (recovery_routes) and never validates this chain."""
    span = (cited_span or "").rstrip().removesuffix("...").rstrip(". ")
    cands = typed_candidates(outcome, row, [{"source_id": "served-citation", "text": span}], spec)
    full = _scoped(absence.normalize_code(row.get("reason_code") or row.get("state") or ""), cands, row)
    if full:
        return {"chain_verdict": REASON_FALSE_VALUE_HELD, "chain_evidence": full[0]["span"], "fails_on": []}
    fails = sorted({m.split(":", 1)[0] for c in cands for m in c["mismatch"]}) if cands else ["no typed result in the cited span"]
    return {"chain_verdict": REASON_NOT_DISPROVED, "chain_evidence": span[:240], "fails_on": fails}


def recovery_routes(outcome: dict[str, Any], row: dict[str, Any], sources: list[dict[str, str]], spec: dict[str, Any] | None = None,
                    cited_span: str | None = None) -> list[dict[str, Any]]:
    """Full matches in held text OTHER than the cited span: extraction leads, reported beside the chain verdict, never merged into it."""
    cited = " ".join((cited_span or "").split())[:80]
    code = absence.normalize_code(row.get("reason_code") or row.get("state") or "")
    return [{"source_id": c["source_id"], "span": c["span"][:240]} for c in _scoped(code, typed_candidates(outcome, row, sources, spec), row)
            if not cited or cited not in " ".join(c["span"].split())]


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
    candidates = typed_candidates(outcome, row, sources, spec)
    matched = _scoped(code, candidates, row)
    candidates.sort(key=lambda c: len(c["mismatch"]))
    if matched:
        best = matched[0]
        return {
            "verdict": REASON_FALSE_VALUE_HELD,
            "detail": f"{REASON_FALSE_VALUE_HELD}({best['source_id']}, \"{best['span']}\")",
            "stated_reason_code": code,
            "source_id": best["source_id"],
            "source_kind": next((s.get("source_kind") for s in sources if s.get("source_id") == best["source_id"]), "held"),
            "source_span": best["span"],
            "source_contains": best["span"],
            "evidence_identity": best,
            "candidates": candidates[:8],
        }
    if candidates:
        return {
            "verdict": REASON_NOT_DISPROVED,
            "detail": "held numbers exist, but none matches the refused claim on every typed field: "
                      + "; ".join(f"{c['span'][:80]} -> {','.join(c['mismatch'])}" for c in candidates[:3]),
            "stated_reason_code": code,
            "candidates": candidates[:8],
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
    verdicts = [REASON_TRUE, REASON_FALSE_VALUE_HELD, REASON_NOT_DISPROVED, REASON_WRONG_KIND, NOT_VERIFIABLE]
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
        # the review's question is the target population an eligibility flag is judged against
        spec = {**(specs_by_name.get(outcome.get("name")) or {}), "target_population": review.get("question")}
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
