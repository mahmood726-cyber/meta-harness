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


# --- ONE target-aware value predicate (reviews 16 + 23): shared by audit_reason_row and unextracted.audit_pair.
# A held sentence is a value FOR THE TARGET only if it names the OUTCOME (never a population / setting word such as
# 'ICU', never a bare 'primary outcome' phrase) and carries a numeric result; a sentence that states a timepoint outside
# the protocol window is an explicit TIMEPOINT MISMATCH, which takes precedence over a generic 'value held'. A candidate
# overturns a refusal only when it overcomes THAT refusal (a value present does not answer an estimand, population,
# multi-arm or engine refusal; only an in-window value answers a timepoint refusal).
TARGET_MATCH = "MATCH"
TARGET_TIMEPOINT_MISMATCH = "TIMEPOINT_MISMATCH"
_ROLE_PHRASE = re.compile(r"^\s*(?:the\s+)?(?:primary|secondary)\s+(?:outcome|end\s*-?\s*point|endpoint)s?\s*$", re.I)
_IDENTITY_STOP = {"with", "from", "after", "during", "rate", "rates", "total", "number", "change", "percent",
                  "percentage", "proportion", "incidence", "occurrence", "event", "events", "patients", "participants",
                  "risk", "adverse", "outcome", "outcomes", "primary", "secondary", "trial", "study"}
_DEATH_WORDS = ("mortality", "death", "deaths", "died", "dead")
# overcome by a value FOR THE TARGET: the refusal claims the value is absent / not reported / not retrieved
_OVERCOMABLE = {absence.OUTCOME_NOT_IN_SOURCE, absence.OUTCOME_NOT_REPORTED, absence.SOURCE_NOT_RETRIEVED,
                "OUTCOME_NOT_REPORTED", "NOT_REPORTED", ""}


def _content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{4,}", (text or "").lower()) if w not in _IDENTITY_STOP}


def identity_terms(keywords: list[str], outcome_name: str | None) -> list[str]:
    """The keywords that name the OUTCOME: they share a content word with its name (death/mortality are one family);
    a population / setting term ('ICU', 'critically ill') or a bare role phrase never does."""
    name = outcome_name or ""
    # the outcome's CORE, before any population clause ('Mortality in critically ill patients' -> 'Mortality'):
    # a keyword sharing only a population word never identifies the outcome (tvp-r1 #5)
    core = re.split(r"\b(?:in|among|amongst|for|of\s+patients|of\s+participants)\b", name, maxsplit=1, flags=re.I)[0]
    nw = _content_words(core) or _content_words(name)
    if nw & set(_DEATH_WORDS):
        nw |= set(_DEATH_WORDS)
    out = [name] if name else []
    for k in keywords or []:
        if not k or _ROLE_PHRASE.match(str(k)):
            continue
        if _content_words(str(k)) & nw or _is_abbreviation_of(str(k), name):
            out.append(str(k))
    return out


def _is_abbreviation_of(k: str, name: str) -> bool:
    """'POAF' of 'Postoperative atrial fibrillation': a short single token whose letters run, in order, through the
    name and start with its first letter, each name word supplying at least one ('ICU' of 'Mortality' does not)."""
    k = k.strip().lower()
    words = re.findall(r"[a-z]+", (name or "").lower())
    if not (2 <= len(k) <= 6) or not k.isalpha() or not words or k[0] != words[0][0]:
        return False
    i = 0
    for w in words:                      # every name word must contribute its first letter, in order
        if i >= len(k) or k[i] != w[0]:
            return False
        i += 1
        while i < len(k) and k[i] in w[1:] and (len(k) - i) > (len(words) - words.index(w) - 1):
            i += 1
    return i == len(k)


_CITATION = re.compile(r"\[\s*\d{1,3}(?:\s*[,–-]\s*\d{1,3})*\s*\]|\bet\s+al\b", re.I)
# a citation reports ANOTHER study only next to a study name: an all-caps acronym or 'trial'/'study' (40825340's table:
# 'SELECT trial (semaglutide 2.4 mg) [ 9 ]'); '... the prespecified definition [9]' cites a definition (tvp-r1 #3)
_OTHER_STUDY_CITATION = re.compile(r"\b(?:[A-Z][A-Z0-9-]{2,}|trial|study)\b[^;\[\]]{0,60}\[\s*\d{1,3}"
                                   r"(?:\s*[,–-]\s*\d{1,3})*\s*\]|\bet\s+al\b")


def _names_target(sentence: str, terms: list[str]) -> bool:
    """absence._matches_term, also across a dropped space ('bodyweight' names 'body weight')."""
    if absence._matches_term(sentence, terms):
        return True
    from . import lexicon
    squashed = lexicon.fold(sentence).replace("-", " ").replace(" ", "")
    return any(" " in t and t.replace(" ", "") in squashed for t in terms)


def target_window_weeks(spec: dict[str, Any] | None) -> tuple[float, float] | None:
    """The protocol timepoint window in weeks: timepoint_weeks +/- timepoint_tolerance_weeks (pipeline's own rule), else
    a stated day range ('28-90 day'), else None (no window: timepoints are not judged)."""
    spec = spec or {}
    tw = spec.get("timepoint_weeks")
    if tw is not None:
        tol = spec.get("timepoint_tolerance_weeks", 8) or 0
        return float(tw) - tol, float(tw) + tol
    m = re.search(r"(\d+)\s*(?:-|to|–)\s*(\d+)\s*-?\s*days?\b", str(spec.get("timepoint") or ""), re.I)
    if m:
        return int(m.group(1)) / 7.0, int(m.group(2)) / 7.0
    return None


def sentence_weeks(sentence: str, near: list[str] | None = None) -> list[float]:
    """The timepoints a sentence states, in weeks ('week 68', '44 weeks', '12.5 weeks', '26 wk', '90 days', '6
    months'). near: identity terms -- when given, a treatment DURATION ('after 4 weeks of treatment', 'for 12 weeks')
    is not the outcome's timepoint, and the timepoint closest to the outcome term is the one returned (tvp-r1 #2)."""
    s = (sentence or "").lower().replace("·", ".")
    hits = []
    for m in re.finditer(r"\bweek\s*(\d+(?:\.\d+)?)\b|(?<![\d.])(\d+(?:\.\d+)?)[\s-]*(weeks?|wks?|days?|months?|years?)\b", s):
        if m.group(1):
            w = float(m.group(1))
        else:
            n, u = float(m.group(2)), m.group(3)
            w = n if u.startswith("w") else n / 7.0 if u.startswith("d") else n * 4.345 if u.startswith("m") else n * 52.18
        before, after = s[max(0, m.start() - 12):m.start()], s[m.end():m.end() + 25]
        duration = bool(re.search(r"\b(?:after|for|over)\s*$", before) and re.search(r"^\s*of\s+(?:treatment|therapy|"
                                                                                 r"intervention|follow)", after)) or \
            bool(re.search(r"\bfor\s*$", before))
        hits.append((m.start(), w, duration))
    if not near:
        return [w for _, w, _ in hits]
    hits = [h for h in hits if not h[2]]
    pos = [m.start() for t in near for m in re.finditer(re.escape(t.lower()), s)]
    if not hits or not pos:
        return [w for _, w, _ in hits]
    best = min(hits, key=lambda h: min(abs(h[0] - p) for p in pos))
    return [best[1]]


def target_value_match(sources: list[dict[str, str]], spec: dict[str, Any] | None,
                       outcome_name: str | None) -> dict[str, str] | None:
    """The BEST held candidate over every source (tvp-r1 #4): a value FOR THE TARGET stated at an in-window timepoint,
    else one with no stated timepoint (state MATCH), else one naming the outcome at an OUT-of-window timepoint (state
    TIMEPOINT_MISMATCH), else None."""
    spec = spec or {}
    ids = identity_terms(spec.get("keywords") or [], outcome_name)
    terms = absence._terms(ids)
    window = target_window_weeks(spec)
    in_window = undated = mismatch = None
    for src in sources or []:
        text = _plain(src.get("text") or "")
        for sent in extract._sentences(text):
            sent = norm_space(sent)
            if not terms or not _names_target(sent, terms) or not _has_numeric_outcome(sent):
                continue
            if len(sent) > 600 or _OTHER_STUDY_CITATION.search(sent):
                # a table chunk, or a citation next to another study's name, reports OTHER studies, never this
                # trial's own result (40825340: another article's summary table, 'SELECT trial ... [ 9 ]')
                continue
            ws = sentence_weeks(sent, near=[t for t in ids if t])
            out = {"source_id": src.get("source_id") or "held_source", "source_kind": src.get("source_kind") or "held",
                   "span": clip(sent)}
            if window and ws and not any(window[0] - 1e-9 <= w <= window[1] + 1e-9 for w in ws):
                mismatch = mismatch or dict(out, state=TARGET_TIMEPOINT_MISMATCH, stated_weeks=ws,
                                            window_weeks=[round(window[0], 2), round(window[1], 2)])
                continue
            value = _normalised_value(sent, text)
            cand = dict(out, state=TARGET_MATCH, at_target_timepoint=bool(window and ws),
                        **({"value_text": value} if value else {}))
            if cand["at_target_timepoint"]:
                in_window = in_window or cand
            else:
                undated = undated or cand
    return in_window or undated or mismatch


def overcomes(code: str, row: dict[str, Any] | None, match: dict[str, Any] | None) -> bool:
    """Does a target match overcome THIS refusal? Only an absence claim is answered by a value; a timepoint refusal
    only by an in-window value; an estimand / population / multi-arm / engine / evidence refusal never by a bare value."""
    if not match or match.get("state") != TARGET_MATCH:
        return False
    reason = ((row or {}).get("reason") or "").lower()
    if code == absence.TIMEPOINT_MISMATCH or "timepoint mismatch" in reason:
        return bool(match.get("at_target_timepoint"))
    if (row or {}).get("absent_kind") == "refused_on_evidence":
        return False
    if code == absence.COUNTS_PRESENT_NOT_CORROBORATED:
        # the refusal says no PERCENTAGE-CORROBORATED arm counts were found: a target sentence printing them answers it
        return bool(_COUNT_WITH_PERCENT.search(extract._norm(match.get("span") or "")))
    return code in _OVERCOMABLE


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
    # ONE target-aware predicate (r16 + r23): a candidate overturns the refusal only if it is a value FOR THE TARGET
    # (outcome identity + timepoint) AND overcomes this specific refusal; otherwise the refusal stands
    found = target_value_match(sources, spec, outcome.get("name"))
    if found and overcomes(code, row, found):
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
    if found:
        return {
            "verdict": REASON_TRUE,
            "detail": (f"held {found['state'].lower().replace('_', ' ')} candidate ({found['source_id']}) does not "
                       f"overcome the stated refusal {code or 'UNSPECIFIED'}: the refusal stands"),
            "stated_reason_code": code,
            "candidate_state": found["state"],
            "source_span": found["span"],
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
