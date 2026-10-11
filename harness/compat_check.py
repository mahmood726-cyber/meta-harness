"""Check asserted compatibility keys against the pooled trial rows.

The older compatibility key was an outcome-level promise. This module derives
the same dimensions from each pooled trial row and its committed source text,
then refuses a uniform assertion when the underlying rows are heterogeneous.
"""
from __future__ import annotations

import collections
import json
import os
import re
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSERTED_NOT_UNDERLYING = "COMPAT_ASSERTED_NOT_UNDERLYING"
UNDERIVABLE = "COMPAT_DIMENSION_UNDERIVABLE"
HETEROGENEOUS = "COMPAT_DIMENSION_HETEROGENEOUS"
HARMS_INCOMPLETE = "HARMS_INCOMPLETE"

_DIM_TO_KEY = {
    "analysis_set": "analysis_set",
    "follow_up_window": "follow_up_window",
    "endpoint": "endpoint",
}
_DIM_TO_DERIVED = {
    "analysis_set": "analysis_set",
    "follow_up_window": "follow_up_window",
    "endpoint": "endpoint_definition",
}

_PROBIOTIC_CLASS = "probiotic preparations"
_OMEGA3_CLASS = "omega-3 fatty acid preparations"


def _pid(value: Any) -> str:
    s = str(value or "").strip()
    for prefix in ("PMID ", "PMID:", "NCT"):
        if s.upper().startswith(prefix):
            s = s[len(prefix):].strip()
    return s


def _rec_map(records: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for rec in (records or {}).get("records", []) or []:
        if rec.get("id") is not None:
            out[str(rec.get("id"))] = rec
        if rec.get("nct"):
            out[str(rec.get("nct")).upper()] = rec
    return out


def _norm_ws(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _short_span(text: str, match: re.Match[str] | None, flank: int = 110) -> str:
    if not text:
        return ""
    if not match:
        return _norm_ws(text[:240])
    return _norm_ws(text[max(0, match.start() - flank):match.end() + flank])


def _search(pattern: str, text: str) -> re.Match[str] | None:
    return re.search(pattern, text or "", re.I | re.S)


def _load_json(*parts: str) -> dict[str, Any]:
    path = os.path.join(ROOT, *parts)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _topic_definition_audit(slug: str | None, review: dict[str, Any]) -> dict[str, dict[str, Any]]:
    own = review.get("definition_audit") or {}
    if own:
        return own
    if not slug:
        return {}
    all_rows = (_load_json("docs", "definition_audit.json").get("by_row") or {})
    prefix = slug + "::"
    return {k: v for k, v in all_rows.items() if str(k).startswith(prefix)}


def _audit_for_trial(audit: dict[str, dict[str, Any]], outcome: str, pid: str) -> dict[str, Any] | None:
    key = f"::{outcome}::{pid}"
    for rid, row in audit.items():
        if str(rid).endswith(key):
            return row
    return None


def _trial_text(trial: dict[str, Any], rec: dict[str, Any] | None, audit_row: dict[str, Any] | None) -> str:
    bits = [
        trial.get("source"),
        ((trial.get("study_effect") or {}).get("source_provenance") or {}).get("span"),
        (rec or {}).get("title"),
        (rec or {}).get("abstract"),
    ]
    if audit_row:
        bits += [audit_row.get("detail"), audit_row.get("resolution")]
    return _norm_ws(" ".join(str(b or "") for b in bits))


def _text_span(source: str, label: str) -> dict[str, str]:
    return {"source": source, "span": label}


def _derived(value: str | None, source: str, span: str | None, trial_reported: bool | None = None) -> dict[str, Any]:
    if trial_reported is None:
        trial_reported = None if value is None else source not in _NOT_TRIAL_REPORTED
    return {"value": value, "source": source, "span": _norm_ws(span or ""), "trial_reported": trial_reported}


# ---------------------------------------------------------------------------------------------------------------------
# OUTCOME BINDING (external audit review 26-A / 12-03 / 04-2, 11 Oct). Every panel field binds to the row's SELECTED
# outcome, in this order:
#   1. an explicit field (trial.timeframe for follow-up; the definition-audit row for the endpoint);
#   2. the ROW'S OWN source span (the sentence the effect was extracted from);
#   3. sentences of the held record that are ABOUT this outcome (its head term and, for multi-word names, half of the rest);
#      for the analysis set, a sentence about another STAGE (extension, re-randomisation, run-in, open-label phase) never
#      counts; a 'primary outcome was X' clause binds only when X is this outcome;
#   4. a trial-level statement (median follow-up; 'analysed by intention to treat') for follow-up / analysis set;
#   5. the protocol's declaration (outcome.timepoint, study_effect.analysis_population, outcome.name), labelled as such
#      (trial_reported False).
# The old rule took the FIRST regex hit over source + span + title + whole abstract: CAPE COD's mortality follow-up was
# its hydrocortisone taper ('14 days'), Torres's 'primary outcome was treatment failure' was attached to its mortality
# and hyperglycaemia rows, and melatonin's analysis set was the extension phase's 'completers'.
# Time phrases are typed: FOLLOW-UP feeds follow_up_window; EXPOSURE (treatment duration), LENGTH OF STAY and SCHEDULE
# have their own fields and never become a follow-up window.
# ---------------------------------------------------------------------------------------------------------------------
SRC_ROW = "row source span"
SRC_OUTCOME_SENTENCE = "outcome-bound sentence of the held record"
SRC_TRIAL_STATEMENT = "trial-level statement in the held record"
SRC_PRIMARY_CLAUSE = "the trial's primary-outcome clause (the row's own span reports the primary outcome)"
SRC_DECLARED = "protocol declaration (study_effect.analysis_population; not trial-reported)"
_NOT_TRIAL_REPORTED = {SRC_DECLARED, "outcome.timepoint", "outcome.name", "underivable"}

_GENERIC_TOKENS = {"all", "cause", "any", "new", "total", "overall", "time", "first", "rate", "risk", "events", "event",
                   "outcome", "outcomes", "the", "of", "or", "and", "to", "in", "a", "an", "with", "for", "by", "on",
                   "from", "at", "per", "trial", "defined", "reported", "composite", "change", "baseline",
                   "effect", "effects"}           # 'adverse effects' must not bind to 'major adverse cardiac events'
_SYNONYMS = {"mortality": ("mortality", "death", "deaths", "died", "dying", "survival"),
             "death": ("death", "deaths", "died", "mortality"),
             "hospitalization": ("hospitalization", "hospitalisation", "hospitalized", "hospitalised", "admission"),
             "hospitalisation": ("hospitalization", "hospitalisation", "hospitalized", "hospitalised", "admission"),
             "mace": ("mace", "major adverse cardiovascular events", "major adverse cardiac events",
                      "major cardiovascular events", "major vascular events")}
_STAGE = re.compile(r"\bextension\b|\bre-?randomi[sz]ed\b|\bre-?randomi[sz]ation\b|\brun-?in\b|\bopen-label (?:phase|period)\b"
                    r"|\bcontinuation (?:phase|period)\b|\blong-term (?:phase|period|follow-up phase)\b|\bwithdrawal phase\b", re.I)


def _fold(s: str) -> str:
    """Lower case; British/American vowel pairs folded identically on both sides (haemo/hemo, oedema/edema)."""
    s = (s or "").lower()
    return s.replace("ae", "e").replace("oe", "e")


_WORDS = re.compile(r"[a-z]+")


def _outcome_tokens(outcome: dict[str, Any]) -> list[str]:
    words = _WORDS.findall(_fold(str(outcome.get("name") or "")))
    toks = [w for w in words if w not in _GENERIC_TOKENS and len(w) >= 3]
    return toks


def _negates(text_f: str, toks: list[str]) -> bool:
    """The text names a NON-qualified form of one of the outcome's words ('nonvertebral', 'non-fatal'): it is about
    another outcome, whatever head term it shares (codex lc-compat-codex-focused:g1#1, g2#1)."""
    # ...only when the plain word is NOT also named: 'fatal or non-fatal stroke' names both (agy r2-g1#2)
    return any(any(p + t in text_f for p in ("non", "non-", "non ")) and not _has_token(text_f, t) for t in toks)


def _has_token(text_f: str, tok: str) -> bool:
    alts = _SYNONYMS.get(tok, (tok,))
    for alt in alts:
        a = _fold(alt)
        # 'progression-free survival' is not MORTALITY (codex g1#2); 'overall survival' is -- but a row whose own word
        # is 'survival' (Progression-free survival) still finds it (agy r2-g1#1)
        if a == "survival" and tok != "survival":
            text_f = text_f.replace("-free survival", " ").replace(" free survival", " ")
        if re.search(rf"(?<!non-)(?<!non )\b{re.escape(a)}(?:s|es)?\b", text_f):
            return True
    return False


def _about_outcome(text: str, toks: list[str]) -> bool:
    """A text is ABOUT the outcome when it carries the head term (the last content word) and, for longer names, at least
    half of the other content words. 'nonvertebral' never satisfies 'vertebral' (the prefix guard and word boundary)."""
    if not toks:
        return False
    acr = "".join(t[0] for t in toks).upper()
    if len(toks) >= 2 and re.search(rf"\b{re.escape(acr)}\b", text or ""):
        return True                       # the outcome's own acronym ('AAD' for antibiotic-associated diarrhoea)
    tf = _fold(text)
    head, rest = toks[-1], toks[:-1]
    if not _has_token(tf, head):
        return False
    need = (len(rest) + 1) // 2
    return sum(1 for t in rest if _has_token(tf, t)) >= need


_SENT_SPLIT = re.compile(r"(?<=[.;!?])\s+(?=[A-Z(\[])")


def _sentences(text: str) -> list[str]:
    return [s for s in _SENT_SPLIT.split(_norm_ws(text)) if s]


def _row_text(trial: dict[str, Any]) -> str:
    return _norm_ws(" ".join(str(b or "") for b in (
        trial.get("source"), ((trial.get("study_effect") or {}).get("source_provenance") or {}).get("span"))))


def _record_text(rec: dict[str, Any] | None) -> str:
    return _norm_ws(" ".join(str(b or "") for b in ((rec or {}).get("title"), (rec or {}).get("abstract"))))


def _outcome_sentences(outcome: dict[str, Any], rec: dict[str, Any] | None, *, skip_stage: bool = False) -> list[str]:
    toks = _outcome_tokens(outcome)
    out = []
    for s in _sentences(_record_text(rec)):
        if skip_stage and _STAGE.search(s):
            continue
        # the trial's own primary-outcome sentence binds to the review's PRIMARY row when it names the head term
        # ('The primary outcome was the proportion of patients who developed diarrhea in the first 21 days')
        if _about_outcome(s, toks) or (outcome.get("primary") and toks and _PRIMARY_SENTENCE.search(s)
                                       and _primary_fallback_binds(s, toks)):
            out.append(s)
    return out


def _primary_fallback_binds(s: str, toks: list[str]) -> bool:
    """The primary-outcome sentence binds the review's primary row on the head term -- read in the primary CLAUSE's own
    head when the sentence has one, so a separately named 'nonvertebral fractures were secondary' does not veto 'the
    primary outcome was vertebral fracture' (codex lc-compat-r2-codex:g1#1)."""
    m = _PRIMARY_CLAUSE.search(s)
    # the clause to its first ';' -- not to its first comma: '...the 6-month incidence of recurrent symptomatic, ...
    # venous thromboembolism and related deaths' keeps its own words
    scope = _fold(m.group(1).split(";", 1)[0] if m else s)
    return _has_token(scope, toks[-1]) and not _negates(scope, toks)


_PRIMARY_SENTENCE = re.compile(r"\bprimary (?:efficacy )?(?:outcome|end ?point|measure)", re.I)


# --- time phrases ------------------------------------------------------------------------------------------------
_UNIT = r"(day|week|month|year)s?"
# a number: decimals with '.' or the Lancet middle dot ('1·5 years' was read as '5 years'); never the tail of '34.2±13.7'
_NUM = r"(?<![\d.·±])(\d+(?:[.·]\d+)?)"


def _q(n: str, unit: str) -> str:
    n = n.replace("·", ".")
    return f"{n} {unit.lower()}" + ("" if n in ("1", "1.0") else "s")


_TP_ABX30 = re.compile(r"\bduring\s+and\s+up\s+to\s+30\s+days\s+after\b|\bAbx\+30d\b", re.I)
_TP_PLUS2W = re.compile(r"\bduring\s+or\s+up\s+to\s+2\s+weeks\s+after\b|\bup to\s+2\s+weeks\s+after\b", re.I)
_TP_FU_STATED = re.compile(r"\b(?:median|mean)\s+(?:duration\s+of\s+(?:the\s+)?)?follow[-\s]?up\s+(?:of|was|period\s+(?:of|was))\s+"
                           r"(?:approximately\s+)?" + _NUM + r"\s+" + _UNIT, re.I)
_TP_FOLLOWED_FOR = re.compile(r"\bfollowed(?:\s+up)?\s+for\s+(?:a\s+(?:median|mean)\s+of\s+)?" + _NUM + r"\s+" + _UNIT, re.I)
_TP_OVER_MEDIAN = re.compile(r"\b(?:over|during)\s+a\s+(?:median|mean)\s+(?:follow[-\s]?up\s+)?of\s+" + _NUM + r"\s+" + _UNIT, re.I)
_TP_SUPPLEMENTATION = re.compile(r"\bmedian duration of supplementation was\s+" + _NUM + r"\s+years\b", re.I)
_TP_BY_DAY = re.compile(r"\b(?:by|at|on|through|until|to)\s+(day|week|month|year)\s+(\d+(?:[.·]\d+)?)\b", re.I)
_TP_WITHIN = re.compile(r"\bwithin\s+" + _NUM + r"\s+" + _UNIT, re.I)
_TP_N_OR_M = re.compile(r"\b(\d+)\s+or\s+(\d+)[-\s]" + _UNIT + r"\b", re.I)
_TP_NUM_UNIT = re.compile(_NUM + r"[-\s]" + _UNIT + r"\b", re.I)
_TIME_PHRASES = [            # earlier patterns are more specific: they claim their span first
    (_TP_ABX30, lambda m: "during treatment plus 30 days"),
    (_TP_PLUS2W, lambda m: "during treatment plus 2 weeks"),
    (_TP_FU_STATED, lambda m: _q(m.group(1), m.group(2))),
    (_TP_FOLLOWED_FOR, lambda m: _q(m.group(1), m.group(2))),
    (_TP_OVER_MEDIAN, lambda m: _q(m.group(1), m.group(2))),
    (_TP_SUPPLEMENTATION, lambda m: _q(m.group(1), "year")),
    (_TP_BY_DAY, lambda m: _q(m.group(2), m.group(1))),
    (_TP_WITHIN, lambda m: "within " + _q(m.group(1), m.group(2))),
    (_TP_N_OR_M, lambda m: f"{m.group(1)} or " + _q(m.group(2), m.group(3))),
    (_TP_NUM_UNIT, lambda m: _q(m.group(1), m.group(2))),
]
# the explicit follow-up statements a trial makes about ITSELF (used when no sentence binds to the outcome)
_TRIAL_FOLLOW_UP = re.compile(r"\b(?:median|mean)\s+(?:duration\s+of\s+(?:the\s+)?)?follow[-\s]?up\b|\bfollowed(?:\s+up)?\s+for\b"
                              r"|\b(?:over|during)\s+a\s+(?:median|mean)\b|\bmedian duration of supplementation\b", re.I)
_AGE = re.compile(r"\bage[ds]?\b[^.;]{0,25}$|\bmean age\b[^.;]{0,25}$", re.I)
_AFTER_AGE = re.compile(r"\A[^.;]{0,12}\b(?:of age|old)\b", re.I)
_DISPERSION_END = re.compile(r"(?:±|\+/-|\bSD\b|\bIQR\b)\s*$")
_LOS = re.compile(r"\blength of (?:hospital |icu |intensive care )?stay\b|\bhospital stay\b|\bLOS\b|\bdays? in (?:the )?hospital\b", re.I)
_SCHEDULE = re.compile(r"\bevery\s+\d+|\b(?:once|twice|three times)\s+(?:a\s+|per\s+)?(?:day|daily|week|weekly|month)\b|\bq\d+[hdw]?\b", re.I)
_EVERY_END = re.compile(r"\bevery\s*$", re.I)
_FU_LEAD = re.compile(r"\b(?:median|mean)\s+(?:duration\s+of\s+)?follow[-\s]?up\b|\bfollowed(?:\s+up)?\s+for\b"
                      r"|\b(?:by|at|on|through|until)\s+$", re.I)
_FU_PHRASE_START = re.compile(r"\A\s*(?:by|at|on|through|until|within|during|up to|Abx\+)", re.I)
_CLAUSE_SPLIT = re.compile(r"[,;:]")
_EXPOSURE = re.compile(r"\btaper\w*|\btreat(?:ed|ment)\b|\btherapy\b|\badminister\w*|\breceiv\w*|\binfusion\b|\bcourse\b|\bdos(?:e|es|ing)\b"
                       r"|\bsupplementation\b|\bdaily\b|\bfor a total of\b|\bsubcutaneous\w*|\boral\w*|\bintravenous\w*|\bassigned to\b", re.I)
_FOLLOW = re.compile(r"\bfollow[-\s]?up\b|\bfollowed\b|\bdeath\b|\bdied\b|\bmortality\b|\boccurred\b|\bincidence\b|\bevents?\b"
                     r"|\bend ?point\b|\boutcome\b|\bsurvival\b|\bassessed\b|\bmeasured\b|\bcumulative\b", re.I)


def time_phrase_kind(sentence: str, phrase: str, start: int | None = None) -> str:
    """'follow_up' | 'exposure' | 'length_of_stay' | 'schedule' | 'age' | 'dispersion' | 'unclassified' for one time
    phrase in its sentence. The 80 characters BEFORE the phrase decide: a treatment verb there makes it a treatment
    duration ('tapering for a total of 8 or 14 days'), an outcome word a follow-up window ('By day 28, death had occurred').
    start: the phrase's own offset in the (whitespace-normalised) sentence -- a phrase that occurs twice is classified
    where it stands, not at its first occurrence (codex lc-compat-codex-focused:g1#5)."""
    s = _norm_ws(sentence)
    i = start if start is not None else s.lower().find(_norm_ws(phrase).lower())
    i = max(i, 0)
    before = s[max(0, i - 80):i]
    near = s[max(0, i - 80):i + len(phrase) + 60]
    clause = _CLAUSE_SPLIT.split(before)[-1]
    if _AGE.search(before) or _AFTER_AGE.search(s[i + len(phrase):]):
        return "age"                      # 'mean age, 70 years' is not a follow-up window
    if _DISPERSION_END.search(before):
        return "dispersion"               # '34.2±13.7 months': 13.7 is an SD
    # a stay in the phrase's OWN clause ('length of hospital stay was 7 days') or right after it ('5 days in hospital');
    # never a stay named elsewhere in the sentence ('Mortality at day 28 and length of stay', codex g1#4 / full g1#3)
    los_after = _LOS.search(phrase + s[i + len(phrase):i + len(phrase) + 30])
    # (a stay named in the phrase's own clause wins outright: 'Length of hospital stay was measured as 7 days', r2-g2#1)
    if (_LOS.search(clause) or (_LOS.search(before) and not _FOLLOW.search(clause))
            or (los_after and los_after.start() < len(phrase))):
        return "length_of_stay"
    if _SCHEDULE.search(phrase) or _EVERY_END.search(before):
        return "schedule"
    if _FU_LEAD.search(before + " ") or _FU_PHRASE_START.search(phrase):
        # 'until' / 'through' END a treatment as readily as a follow-up: 'received treatment until day 7' is a treatment
        # duration (codex g1#3 / full g1#2). 'at / by / to week N' stay assessment time points ('Treatment with FCM
        # prolonged 6MWT at Week 24'); an outcome or follow-up word in the clause keeps any of them a follow-up window
        ends = {(phrase.split() or [""])[0].lower(), (before.split() or [""])[-1].lower()}
        if (ends & {"until", "through"} and _EXPOSURE.search(clause) and not _FOLLOW.search(clause)
                and not _TRIAL_FOLLOW_UP.search(clause + " " + phrase)):
            return "exposure"
        return "follow_up"
    if _EXPOSURE.search(clause):
        return "exposure"
    if _FOLLOW.search(near):
        return "follow_up"
    return "unclassified"


def _phrases(text: str) -> list[tuple[str, str, str, str]]:
    """Every time phrase in text: (normalised value, raw phrase, its sentence, kind), in text order."""
    out = []
    for sent in _sentences(text):
        taken, found = [], []
        for rx, norm in _TIME_PHRASES:            # earlier patterns are more specific: they claim their span first
            for m in rx.finditer(sent):
                if any(not (m.end() <= a or m.start() >= b) for a, b in taken):
                    continue
                taken.append((m.start(), m.end()))
                found.append((m.start(), norm(m), m.group(0)))
        for at, v, raw in sorted(found):
            out.append((v, raw, sent, time_phrase_kind(sent, raw, at)))
    return out


def _first_kind(text: str, kind: str) -> tuple[str, str] | None:
    for v, raw, sent, k in _phrases(text):
        if k == kind:
            return v, sent
    return None


def _derive_time_fields(outcome: dict[str, Any], trial: dict[str, Any], rec: dict[str, Any] | None) -> dict[str, Any]:
    """Exposure (treatment duration), length of stay and dosing schedule: trial-level fields, kept apart from follow-up."""
    out = {}
    text = _row_text(trial) + " " + _record_text(rec)
    phrases = _phrases(text)
    for key, kind in (("exposure_duration", "exposure"), ("length_of_stay", "length_of_stay"), ("schedule", "schedule")):
        vals, spans = [], []
        for v, raw, sent, k in phrases:
            if k == kind and v not in vals:
                vals.append(v)
                if sent not in spans:
                    spans.append(sent)
        out[key] = (_derived("; ".join(vals[:4]), SRC_TRIAL_STATEMENT, " ".join(spans[:2]), True) if vals
                    else _derived(None, "underivable", "", None))
    return out


def _derive_analysis_set(
    trial: dict[str, Any],
    rec: dict[str, Any] | None,
    audit_row: dict[str, Any] | None,
    outcome: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rules = [
        (r"\bmodified[-\s]+intention[-\s]+to[-\s]+treat\b|\bmodified\s+ITT\b|\bmITT\b", "modified intention-to-treat"),
        (r"\b(completers?|completed the trial and were included|efficacy analysis|no efficacy data)\b",
         "completers efficacy set"),
        (r"\bper[-\s]+protocol\b", "per-protocol"),
        (r"\bintention[-\s]+to[-\s]+treat\b|\bITT\b|\banalys(?:is|es) (?:was|were )?based on allocated treatment\b",
         "intention-to-treat"),
    ]

    def first(text):
        for pattern, value in rules:
            m = _search(pattern, text)
            if m:
                return value, m
        return None

    row = _row_text(trial)
    hit = first(row)
    if hit:
        return _derived(hit[0], SRC_ROW, _short_span(row, hit[1]))
    for s in _outcome_sentences(outcome or {}, rec, skip_stage=True):
        hit = first(s)
        if hit:
            return _derived(hit[0], SRC_OUTCOME_SENTENCE, s)
    # a trial-level analysis statement ('analysed according to the intention-to-treat principle'), never from a
    # sentence about another stage
    for s in _sentences(_record_text(rec)):
        if _STAGE.search(s):
            continue
        hit = first(s)
        if hit and _ANALYSIS_WORD.search(s) and not _OUTCOME_NOUN.search(_fold(s)[:hit[1].start()]):
            return _derived(hit[0], SRC_TRIAL_STATEMENT, s)
    existing = ((trial.get("study_effect") or {}).get("analysis_population")
                or (trial.get("compat_dimensions") or {}).get("analysis_set"))
    if isinstance(existing, dict):
        existing = existing.get("value")
    if existing and existing != "UNKNOWN":
        return _derived(str(existing), SRC_DECLARED, str(existing), False)
    return _derived(None, "underivable", "")


def _derive_follow_up(
    outcome: dict[str, Any],
    trial: dict[str, Any],
    rec: dict[str, Any] | None,
    audit_row: dict[str, Any] | None,
) -> dict[str, Any]:
    if trial.get("timeframe"):
        return _derived(str(trial.get("timeframe")), "trial.timeframe", str(trial.get("timeframe")), True)
    hit = _first_kind(_row_text(trial), "follow_up")
    if hit:
        return _derived(hit[0], SRC_ROW, hit[1])
    for s in _outcome_sentences(outcome, rec):
        hit = _first_kind(s, "follow_up")
        if hit:
            return _derived(hit[0], SRC_OUTCOME_SENTENCE, s)
    for v, raw, sent, kind in _phrases(_record_text(rec)):
        # only an explicit statement about the trial's own follow-up ('median follow-up of 2.8 years'), never any time
        # phrase that happens to share a sentence with the word 'follow' (a treatment duration for 3, 6 or 12 months)
        if _TRIAL_FOLLOW_UP.search(raw):
            return _derived(v, SRC_TRIAL_STATEMENT, sent)
    if outcome.get("timepoint"):
        return _derived(str(outcome.get("timepoint")), "outcome.timepoint", str(outcome.get("timepoint")), False)
    return _derived(None, "underivable", "")


_PRIMARY_CLAUSE = re.compile(r"primary (?:efficacy )?(?:measure|outcome|end point|endpoint) was (?:a composite of )?([^.]{8,240})", re.I)
_DEFINITION_RULES = [
    r"AAD\s*=\s*[^:;.]{8,120}",
    r"diarrh?oe?a\s*\([^)]{10,180}\)",
    r"diarrh?oe?a caused by Clostridium difficile or otherwise unexplained diarrh?oe?a",
    r"serious vascular event \([^)]{10,180}\)",
    r"major cardiovascular events, defined as [^.]{20,220}",
    r"major cardiovascular events,? comprised [^.]{20,220}",
]


_HEAD_BREAK = re.compile(r"\(|;|,| defined\b| which\b| that\b| assessed\b| measured\b")
_ANALYSIS_WORD = re.compile(r"\banaly[sz]\w*|\bpopulation\b|\bset\b", re.I)


def _primary_head(clause_tail: str) -> str:
    """The primary outcome itself: the words after 'was' up to its first parenthesis / definition / list break."""
    return _HEAD_BREAK.split(clause_tail, maxsplit=1)[0]


_ROW_REPORTS_PRIMARY = re.compile(r"\bprimary[- ](?:efficacy[- ])?(?:outcome|end ?point|composite)", re.I)
# ...unless the span says the row is NOT the primary ('a secondary outcome, not the primary outcome', codex full g1#5)
_ROW_NOT_PRIMARY = re.compile(r"\bnot (?:the |a )?primary\b|\bsecondary (?:efficacy )?(?:outcome|end ?point)", re.I)
# a sentence whose subject is a NAMED outcome ('Hospitalization was analysed per-protocol') states that outcome's
# analysis, not the trial's (codex full g1#4); matched on vowel-folded lowercase text
_OUTCOME_NOUN = re.compile(r"\b(?:mortality|deaths?|hospitali[sz]ations?|admissions?|strokes?|fractures?|bleeding|hemorrhages?"
                           r"|infarctions?|survival|infections?|diarrhea|relapses?|recurrences?|remission|pain|exacerbations?)\b")


def _endpoint_from(text: str, outcome: dict[str, Any], toks: list[str]) -> tuple[str, str] | None:
    m = _PRIMARY_CLAUSE.search(text)
    if m:
        head = _primary_head(m.group(1))
        # a composite's head is cut at its first comma ('a composite of mortality, myocardial infarction, or stroke'
        # -> 'mortality'): a ONE-word outcome is then a component of the composite, never defined by it (codex g2#2)
        composite = "composite" in m.group(0).lower()
        component = False
        if composite:                     # a composite outcome is matched on its whole component list
            head = m.group(1).split("(", 1)[0]
            # ...and binds only a row that IS a composite: one naming itself so (composite / MACE wording) or whose
            # words reach two or more of the listed components. 'Disabling stroke' is one component of 'death,
            # myocardial infarction, or disabling stroke', never defined by it (codex g2#2, r2-g3#1)
            name_f = _fold(str(outcome.get("name") or ""))
            comps = [c for c in _fold(head).replace(" or ", ",").replace(" and ", ",").split(",") if c.strip()]
            reached = sum(1 for c in comps if any(_has_token(c, t) for t in toks))
            component = not ("composite" in name_f or any(_fold(a) in name_f for a in _SYNONYMS["mace"])
                             or reached >= 2)
        # the clause binds when ITS outcome is this row's outcome; for the review's PRIMARY row the head term suffices
        # -- unless the clause names a non-qualified form of the row's outcome ('nonfatal stroke' for 'Fatal stroke')
        if not component and not _negates(_fold(head), toks) and (
                _about_outcome(head, toks) or (outcome.get("primary") and toks and _has_token(_fold(head), toks[-1]))):
            return _norm_ws(m.group(0)), _short_span(text, m)
    for pattern in _DEFINITION_RULES:
        m = _search(pattern, text)
        # a definition defines THIS row only when it names one of the row's words: 'diarrhoea (three or more loose
        # stools daily)' never defines Mortality (codex full g1#6)
        if m and any(_has_token(_fold(m.group(0)), t) for t in toks):
            return _norm_ws(m.group(0)), _short_span(text, m)
    return None


def _derive_endpoint(
    outcome: dict[str, Any],
    trial: dict[str, Any],
    rec: dict[str, Any] | None,
    audit_row: dict[str, Any] | None,
) -> dict[str, Any]:
    if audit_row and (audit_row.get("detail") or audit_row.get("resolution")):
        label = _norm_ws("; ".join(str(audit_row.get(k) or "") for k in ("detail", "resolution")))
        return _derived(label, "docs/definition_audit.json", label, True)
    toks = _outcome_tokens(outcome)
    row = _row_text(trial)
    hit = _endpoint_from(row, outcome, toks)
    if hit:
        return _derived(hit[0], SRC_ROW, hit[1])
    # the row's OWN span says it reports the trial's primary outcome ('a primary outcome event occurred in 197 of 2152'):
    # then the trial's primary-outcome clause defines this row, whatever the review calls the outcome
    if _ROW_REPORTS_PRIMARY.search(row) and not _ROW_NOT_PRIMARY.search(row):
        rt = _record_text(rec)
        m = _PRIMARY_CLAUSE.search(rt)
        if m:
            return _derived(_norm_ws(m.group(0)), SRC_PRIMARY_CLAUSE, _short_span(rt, m))
    for s in _outcome_sentences(outcome, rec):
        hit = _endpoint_from(s, outcome, toks)
        if hit:
            return _derived(hit[0], SRC_OUTCOME_SENTENCE, s)
    name = outcome.get("name")
    if name:
        return _derived(str(name), "outcome.name", str(name), False)
    return _derived(None, "underivable", "")


def _derive_population_age(trial: dict[str, Any], rec: dict[str, Any] | None) -> dict[str, Any]:
    text = _trial_text(trial, rec, None)
    rules = [
        (r"\bchildren\b|\bchild\b|\baged\s+\d+\s+months?\s+to\s+\d+\s+years?\b|\bpa?ediatric\b",
         "paediatric"),
        (r"\badults?\b|\bpatients aged\s+65\s+years and older\b|\bmen\s+\d+\s+years of age or older\b|\bwomen\s+\d+\s+years of age or older\b|\b60 through 80 years\b",
         "adult"),
    ]
    for pattern, value in rules:
        m = _search(pattern, text)
        if m:
            return _derived(value, "committed source text", _short_span(text, m))
    return _derived("not_stated", "committed source text", "")


def _topic_class(review: dict[str, Any]) -> str | None:
    hay = " ".join([
        str(review.get("slug") or ""),
        str((review.get("protocol_config") or {}).get("intervention_i_line") or ""),
        str((review.get("protocol") or {}).get("text") or ""),
    ]).lower()
    if "probiotic" in hay:
        return _PROBIOTIC_CLASS
    if "omega-3" in hay or "omega 3" in hay or "n-3 fatty" in hay:
        return _OMEGA3_CLASS
    return None


def _derive_intervention(review: dict[str, Any], trial: dict[str, Any], rec: dict[str, Any] | None) -> dict[str, Any]:
    text = _trial_text(trial, rec, None).lower()
    klass = _topic_class(review)
    out: dict[str, Any] = {"intervention_class": klass}
    if klass == _PROBIOTIC_CLASS:
        if "saccharomyces" in text or "boulardii" in text:
            out["intervention_member"] = "Saccharomyces boulardii"
        elif "lactobacillus" in text or "lacticaseibacillus" in text or "limosilactobacillus" in text:
            out["intervention_member"] = "Lactobacillus/Lacticaseibacillus preparation"
        elif "bifidobacter" in text:
            out["intervention_member"] = "Bifidobacterium-containing preparation"
        elif "bacillus" in text:
            out["intervention_member"] = "Bacillus-containing preparation"
        else:
            out["intervention_member"] = "probiotic preparation"
        if "yogurt" in text or "yoghurt" in text or "milk drink" in text or "margarine" in text:
            out["formulation"] = "food/fermented-product preparation"
        elif "multistrain" in text or "multi-strain" in text or "mix" in text:
            out["formulation"] = "multistrain product"
        else:
            out["formulation"] = "capsule/supplement or not stated"
        dose = _search(r"(\d+(?:\.\d+)?\s*(?:x|×)?\s*10\(?\d+\)?\s*(?:CFU|organisms)|\d+\s*mg|\d+\s*billion)", text)
        out["dose"] = _norm_ws(dose.group(1)) if dose else "not_stated"
    elif klass == _OMEGA3_CLASS:
        if "icosapent ethyl" in text or ("eicosapentaenoic" in text and "docosahexaenoic" not in text):
            out["agent"] = "EPA-only"
        elif "epa" in text and "dha" in text:
            out["agent"] = "EPA+DHA"
        elif "ala" in text or "alpha-linolenic" in text:
            out["agent"] = "ALA/dietary fatty acid"
        else:
            out["agent"] = "omega-3 fatty acids"
        if "carboxylic acid" in text or "omega-3 ca" in text:
            out["formulation"] = "carboxylic acid"
        elif "ethyl ester" in text or "ethyl esters" in text or "icosapent ethyl" in text:
            out["formulation"] = "ethyl ester"
        elif "margarine" in text:
            out["formulation"] = "dietary margarine"
        else:
            out["formulation"] = "capsule/supplement or not stated"
        dose = _search(r"(\d+(?:\.\d+)?\s*g(?:/d| per day| daily)?|\d+\s*mg)", text)
        out["dose"] = _norm_ws(dose.group(1)) if dose else "not_stated"
        if "mineral oil" in text:
            out["comparator_oil"] = "mineral oil"
        elif "corn oil" in text:
            out["comparator_oil"] = "corn oil"
        elif "olive oil" in text:
            out["comparator_oil"] = "olive oil"
        elif "placebo margarine" in text:
            out["comparator_oil"] = "placebo margarine"
        else:
            out["comparator_oil"] = "placebo/control oil not stated"
        if "without evidence of atherosclerotic cardiovascular disease" in text or "primary prevention" in text:
            out["population_risk"] = "primary prevention"
        elif "established cardiovascular disease" in text or "previous myocardial infarction" in text or "history of myocardial infarction" in text or "secondary prevention" in text:
            out["population_risk"] = "secondary prevention"
        else:
            out["population_risk"] = "mixed/unclear cardiovascular risk"
        out["population_enrichment"] = "triglyceride-enriched" if "triglyceride" in text or "hypertriglyceridemia" in text else "not_stated"
    return out


def derive_trial_dimensions(
    review: dict[str, Any],
    outcome: dict[str, Any],
    trial: dict[str, Any],
    records: dict[str, Any] | None = None,
    definition_audit: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    recs = _rec_map(records)
    pid = _pid(trial.get("id") or trial.get("label"))
    rec = recs.get(pid) or {}
    audit_row = _audit_for_trial(definition_audit or {}, str(outcome.get("name") or ""), pid)
    dims = {
        "trial_id": pid,
        "trial_label": trial.get("label") or trial.get("id"),
        "analysis_set": _derive_analysis_set(trial, rec, audit_row, outcome),
        "follow_up_window": _derive_follow_up(outcome, trial, rec, audit_row),
        "endpoint_definition": _derive_endpoint(outcome, trial, rec, audit_row),
        "population_age": _derive_population_age(trial, rec),
        "intervention_ontology": _derive_intervention(review, trial, rec),
        **_derive_time_fields(outcome, trial, rec),
    }
    return dims


def _canon(value: Any) -> str:
    s = _norm_ws(value).lower()
    s = s.replace("modified intention-to-treat", "mitt")
    s = s.replace("modified-intention-to-treat", "mitt")
    s = s.replace("intention to treat", "intention-to-treat")
    return s


def _is_unasserted_value(dim: str, value: Any, ck: dict[str, Any]) -> bool:
    matches = ck.get("dimension_matches") or {}
    if matches.get(dim) is False:
        return True
    s = _canon(value)
    return "mixed" in s or "trial-defined" in s or "heterogeneous" in s


def _value_counts(values: list[str]) -> dict[str, int]:
    return dict(collections.Counter(values))


def _violation(outcome: dict[str, Any], dim: str, code: str, asserted: Any,
               per_trial: list[dict[str, Any]], detail: str = "") -> dict[str, Any]:
    return {
        "code": code,
        "outcome": outcome.get("name"),
        "dimension": dim,
        "asserted": asserted,
        "per_trial_values": per_trial,
        "detail": detail,
    }


_TRIAL_DEFINED_WINDOW = re.compile(r"\btrial end\b|\bstudy end\b|\blongest\b|\btrial-reported\b|\btrial-defined\b", re.I)
_DURATION = re.compile(r"\A(\d+(?:\.\d+)?) (day|week|month|year)s?\Z")
_WINDOW_PREFIX = re.compile(r"\A(?:within|by|at|through|until|up to)\s+")
_WEEK_N = re.compile(r"\b(day|week|month|year)\s+(\d+)\b")
_ASSERTED_RANGE = re.compile(r"(\d+)\s*-\s*(\d+)\s*-?\s*(day|week|month|year)s?\b")


def _follow_canon(v: str) -> str:
    """'Week 68' -> '68 weeks'; 'within 28 days' -> '28 days'; '28-day' -> '28 days'; '1 weeks' -> '1 week'."""
    s = _canon(v)
    s = _WEEK_N.sub(lambda m: f"{m.group(2)} {m.group(1)}s", s)
    s = _WINDOW_PREFIX.sub("", s)
    m = _DURATION.match(s.replace("-", " "))
    if m:
        n, u = m.group(1), m.group(2)
        return f"{n} {u}" + ("" if n in ("1", "1.0") else "s")
    return s


def _follow_compatible(asserted: Any, value: str) -> bool:
    """A per-trial follow-up value is COMPATIBLE with the outcome's asserted window when it states the same window
    (wording aside), lies inside an asserted range, is named in the assertion, or -- for a TRIAL-DEFINED window ('trial
    end', 'longest reported follow-up', 'trial-reported') -- is the trial's own reported follow-up duration. Different
    trials having different lengths is what a trial-defined window means; it is not heterogeneity of the window.
    (Outcome binding, 11 Oct: rows now carry each trial's real follow-up instead of echoing the outcome's timepoint, and
    the old exact-string test would have flagged 18 topics on wording alone.)"""
    av, vv = _follow_canon(asserted), _follow_canon(value)
    # named as one of the assertion's own alternatives ('in-hospital' of 'in-hospital / index-admission') -- a whole
    # part, never a substring ('8 days' is not inside '28 days', codex g3#1)
    if vv == av or (vv and vv in {_follow_canon(p) for p in av.replace(";", "/").split("/")}):
        return True
    m = _DURATION.match(vv)
    # ...or a duration the assertion itself names, as whole words ('trial end / mean follow-up 39.8 months',
    # '12 months or longest reported trial follow-up'); '28 days' never names '8 days'
    words = av.replace("/", " ").replace(",", " ").split()
    if m and vv in {_follow_canon(f"{a} {b}") for a, b in zip(words, words[1:])}:
        return True
    r = _ASSERTED_RANGE.search(av)
    if m and r and m.group(2) == r.group(3) and float(r.group(1)) <= float(m.group(1)) <= float(r.group(2)):
        return True
    # a trial-defined window CAPPED by a fixed one ('28 days or trial end, whichever is earlier', codex g3#2) is not
    # open to any duration; '12 months or longest reported trial follow-up' is (r2-g4#1)
    capped = any(w in av for w in ("whichever", "earlier", "shorter", "first of"))
    if _TRIAL_DEFINED_WINDOW.search(av) and not capped and (
            m or _TRIAL_DEFINED_WINDOW.search(vv) or vv in {"study end", "trial end"}):
        return True
    return False


def _is_mismatch(dim: str, asserted: Any, values: list[str]) -> bool:
    vals = [_canon(v) for v in values if v]
    if not vals:
        return False
    if dim == "follow_up_window":
        # a FIXED asserted window flags every trial whose window differs from it (so differing trials always flag); a
        # TRIAL-DEFINED one accepts each trial's own reported duration (see _follow_compatible)
        return any(not _follow_compatible(asserted, v) for v in vals)
    if len(set(vals)) > 1:
        return True
    av = _canon(asserted)
    if dim == "analysis_set":
        if av in {"intention-to-treat", "itt"}:
            return any(v not in {"intention-to-treat", "itt"} for v in vals)
        return any(v != av for v in vals)
    if dim == "endpoint":
        if av in {"single endpoint", "composite"}:
            return len(set(vals)) > 1 or any(v != av for v in vals)
        return any(v != av for v in vals)
    return any(v != av for v in vals)


def check(
    review: dict[str, Any],
    records: dict[str, Any] | None = None,
    definition_audit: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Return compatibility-underlying violations for a review object."""
    slug = review.get("slug")
    definition_audit = definition_audit or _topic_definition_audit(str(slug) if slug else None, review)
    violations: list[dict[str, Any]] = []
    for outcome in review.get("outcomes", []) or []:
        ck = outcome.get("compat_key") or {}
        if not ck:
            continue
        derived_rows = [
            derive_trial_dimensions(review, outcome, trial, records, definition_audit)
            for trial in (outcome.get("trials") or [])
        ]
        for dim, key_name in _DIM_TO_KEY.items():
            asserted = ck.get(key_name)
            if asserted in (None, "") or _is_unasserted_value(dim, asserted, ck):
                continue
            if dim == "endpoint":
                endpoint = ck.get("endpoint_canonical") or outcome.get("endpoint_canonical") or {}
                if endpoint.get("status") == "HOMOGENEOUS" and asserted == endpoint.get("label"):
                    continue
            derived_key = _DIM_TO_DERIVED[dim]
            per_trial = []
            underivable = []
            values = []
            for row in derived_rows:
                cell = row.get(derived_key) or {}
                value = cell.get("value")
                item = {
                    "trial_id": row.get("trial_id"),
                    "trial_label": row.get("trial_label"),
                    "value": value,
                    "source": cell.get("source"),
                    "span": cell.get("span"),
                }
                per_trial.append(item)
                if value in (None, ""):
                    underivable.append(item)
                else:
                    values.append(str(value))
            if underivable:
                violations.append(_violation(
                    outcome, dim, UNDERIVABLE, asserted, underivable,
                    "per-trial value could not be derived from the row or committed source",
                ))
                continue
            if _is_mismatch(dim, asserted, values):
                violations.append(_violation(
                    outcome, dim, ASSERTED_NOT_UNDERLYING, asserted, per_trial,
                    "outcome-level key asserts a uniform value but pooled trial rows differ",
                ))
    return violations


def _summarize_analysis(values: list[str]) -> str:
    counts = _value_counts(values)
    parts = []
    labels = [
        ("intention-to-treat", "ITT"),
        ("modified intention-to-treat", "mITT"),
        ("completers efficacy set", "completers"),
        ("per-protocol", "per-protocol"),
    ]
    for raw, lab in labels:
        if counts.get(raw):
            parts.append(f"{lab} x{counts[raw]}")
    for raw, n in counts.items():
        if raw not in {r for r, _ in labels}:
            parts.append(f"{raw} x{n}")
    return "mixed (" + ", ".join(parts) + ")" if parts else "mixed"


def _summarize_follow(values: list[str]) -> str:
    nums = []
    for v in values:
        for n in re.findall(r"\b(\d+)\s+days?\b", v):
            nums.append(int(n))
    if nums:
        return f"trial-defined ({min(nums)}-{max(nums)} d; per trial listed)"
    return "trial-defined (per trial listed)"


def _summarize_endpoint(outcome: dict[str, Any]) -> str:
    name = str(outcome.get("name") or "endpoint")
    if "antibiotic-associated" in name.lower():
        return "trial-defined antibiotic-associated diarrhoea (definitions listed per trial)"
    return f"trial-defined {name} (definitions listed per trial)"


def _fix_compat_key(outcome: dict[str, Any], violations: list[dict[str, Any]]) -> None:
    ck = outcome.get("compat_key")
    if not isinstance(ck, dict):
        return
    by_dim = {v["dimension"]: v for v in violations if v.get("code") == ASSERTED_NOT_UNDERLYING}
    if not by_dim:
        return
    dim_matches = dict(ck.get("dimension_matches") or {})
    per_trial_table: dict[str, list[dict[str, Any]]] = {}
    for dim, viol in by_dim.items():
        vals = [str(x.get("value")) for x in viol.get("per_trial_values") or [] if x.get("value")]
        if dim == "analysis_set":
            ck["analysis_set"] = _summarize_analysis(vals)
        elif dim == "follow_up_window":
            ck["follow_up_window"] = _summarize_follow(vals)
        elif dim == "endpoint":
            endpoint = ck.get("endpoint_canonical") or outcome.get("endpoint_canonical") or {}
            if endpoint.get("status") == "HOMOGENEOUS" and endpoint.get("label"):
                ck["endpoint"] = endpoint["label"]
                dim_matches[dim] = True
                continue
            ck["endpoint"] = _summarize_endpoint(outcome)
        dim_matches[dim] = False
        per_trial_table[dim] = viol.get("per_trial_values") or []
    ck["dimension_matches"] = dim_matches
    ck["underlying_checked"] = True
    if per_trial_table:
        ck["limitation_code"] = HETEROGENEOUS
        outcome["compat_underlying"] = {
            "status": HETEROGENEOUS,
            "dimensions": sorted(per_trial_table),
            "per_trial": per_trial_table,
        }


def _attach_trial_dimensions(
    review: dict[str, Any],
    records: dict[str, Any] | None,
    definition_audit: dict[str, dict[str, Any]],
) -> None:
    for outcome in review.get("outcomes", []) or []:
        for trial in outcome.get("trials") or []:
            dims = derive_trial_dimensions(review, outcome, trial, records, definition_audit)
            trial["analysis_set"] = (dims["analysis_set"] or {}).get("value")
            trial["follow_up_window"] = (dims["follow_up_window"] or {}).get("value")
            trial["endpoint_definition"] = (dims["endpoint_definition"] or {}).get("value")
            trial["population_age"] = (dims["population_age"] or {}).get("value")
            trial["intervention_ontology"] = dims["intervention_ontology"]
            trial["compat_dimensions"] = dims


def _source_for_pid(slug: str, pid: str, rec: dict[str, Any]) -> str:
    bits = [rec.get("title"), rec.get("abstract")]
    ft_path = os.path.join(ROOT, "cache", slug, f"ft_{pid}.txt")
    try:
        with open(ft_path, encoding="utf-8") as f:
            bits.append(f.read())
    except OSError:
        pass
    return _norm_ws(" ".join(str(b or "") for b in bits))


def _harm_terms(name: str) -> list[str]:
    n = name.lower()
    if "atrial" in n:
        return ["atrial fibrillation", "atrial flutter"]
    if "bleed" in n or "hemorrhage" in n or "haemorrhage" in n:
        return ["serious bleeding", "major bleeding", "bleeding events", "bleeding event", "bleeding"]
    return [n]


def _apply_harms_incomplete(review: dict[str, Any], records: dict[str, Any] | None) -> None:
    slug = str(review.get("slug") or "")
    if not slug:
        return
    recs = _rec_map(records)
    primary = next((o for o in review.get("outcomes", []) or [] if o.get("primary")), None)
    primary_ids = [_pid(t.get("id") or t.get("label")) for t in (primary or {}).get("trials", []) or []]
    for outcome in review.get("outcomes", []) or []:
        if outcome.get("kind") != "harm":
            continue
        terms = _harm_terms(str(outcome.get("name") or ""))
        pooled_ids = {_pid(t.get("id") or t.get("label")) for t in outcome.get("trials", []) or []}
        refused_ids = {_pid(t.get("id") or t.get("label")) for t in outcome.get("declared_absent_trials", []) or []
                       if t.get("state") == "REFUSED_ON_EVIDENCE"}
        # Canonical typed incompatibility and spurious-signal decisions resolve
        # extraction debt too, but only with a validated held-source citation.
        from .verified_inputs import validate_referenced_span
        for row in outcome.get("declared_absent_trials", []) or []:
            if row.get("typed_refusal"):
                validate_referenced_span(row)
                refused_ids.add(_pid(row.get("id") or row.get("label")))
        known = []
        for pid in primary_ids:
            rec = recs.get(pid) or {}
            text = _source_for_pid(slug, pid, rec).lower()
            hits = [term for term in terms if term in text]
            if hits:
                m = _search("|".join(re.escape(t) for t in hits), text)
                known.append({
                    "trial_id": pid,
                    "trial_label": (rec.get("acronym") or pid),
                    "terms": hits,
                    "span": _short_span(text, m),
                })
        unresolved = [x for x in known if x["trial_id"] not in pooled_ids and x["trial_id"] not in refused_ids]
        if unresolved and len(pooled_ids) < len(known):
            outcome["harms_incomplete"] = {
                "state": HARMS_INCOMPLETE,
                "n_reporting_pool_trials": len(known),
                "n_pooled": len(pooled_ids),
                "unresolved": unresolved,
            }
            outcome["result"] = {
                "present": False,
                "state": HARMS_INCOMPLETE,
                "n_reporting_pool_trials": len(known),
                "n_pooled": len(pooled_ids),
                "known_eligible_outcome_reports_unresolved": unresolved,
                "reason": (f"{HARMS_INCOMPLETE}: {len(unresolved)} known eligible outcome report(s) "
                           f"from primary-pool trials are unresolved; an isolated k={len(pooled_ids)} "
                           "harm estimate is suppressed until those rows are extracted or typed-refused."),
            }
            outcome.pop("compat_key", None)


def _comparator_age_scope(review: dict[str, Any], records: dict[str, Any] | None) -> None:
    comp = review.get("comparator")
    if not isinstance(comp, dict):
        return
    scope = comp.setdefault("scope", {})
    klass = _topic_class(review)
    if klass:
        scope["topic_is_class"] = True
        scope["topic_intervention_level"] = "intervention_class"
        scope["topic_intervention_class"] = klass
    text = " ".join([str(comp.get("name") or ""), str(comp.get("journal") or "")]).lower()
    comp_pmid = str(comp.get("pmid") or "")
    rec = _rec_map(records).get(comp_pmid) or {}
    comp_text = (text + " " + str(rec.get("title") or "") + " " + str(rec.get("abstract") or "")).lower()
    if "probiotic" in comp_text or "omega-3" in comp_text or "omega 3" in comp_text or "fatty acid" in comp_text:
        scope["comparator_is_class"] = True
        scope["comparator_intervention_level"] = "intervention_class"
    primary = next((o for o in review.get("outcomes", []) or [] if o.get("primary")), None)
    ages = []
    for trial in (primary or {}).get("trials", []) or []:
        age = trial.get("population_age") or ((trial.get("compat_dimensions") or {}).get("population_age") or {}).get("value")
        if age:
            ages.append({"trial_id": _pid(trial.get("id") or trial.get("label")), "age": age})
    adult_only_comp = bool(re.search(r"(?<!children and )(?<!children or )(?<!paediatric and )(?<!pediatric and )\badults?\b(?! and children| or children)|\badult population\b", comp_text))
    paed = [x for x in ages if x.get("age") == "paediatric"]
    if adult_only_comp and paed:
        scope["population_match"] = False
        scope["population_match_basis"] = {
            "comparator": "adult-only comparator",
            "pool_has_paediatric_trials": paed,
        }
        scope["scope_valid"] = False
        scope["note"] = ("adult-only comparator vs a pool containing paediatric trials; population scope "
                         "does not match even though the broad topic label is similar")
    if scope.get("topic_is_class") and scope.get("comparator_is_class"):
        scope["intervention_level_match"] = True


def enrich(
    review: dict[str, Any],
    records: dict[str, Any] | None = None,
    definition_audit: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Attach per-trial dimensions and soften heterogeneous key assertions."""
    slug = review.get("slug")
    definition_audit = definition_audit or _topic_definition_audit(str(slug) if slug else None, review)
    _attach_trial_dimensions(review, records, definition_audit)
    before = check(review, records, definition_audit)
    for outcome in review.get("outcomes", []) or []:
        ovs = [v for v in before if v.get("outcome") == outcome.get("name")]
        _fix_compat_key(outcome, ovs)
    _apply_harms_incomplete(review, records)
    _comparator_age_scope(review, records)
    after = check(review, records, definition_audit)
    review["compat_underlying"] = {
        "checked": True,
        "n_pre_fix_asserted_not_underlying": sum(1 for v in before if v.get("code") == ASSERTED_NOT_UNDERLYING),
        "n_post_fix_asserted_not_underlying": sum(1 for v in after if v.get("code") == ASSERTED_NOT_UNDERLYING),
        "pre_fix_violations": before,
        "post_fix_violations": after,
    }
    return review


def page_gate_violations(review: dict[str, Any], records: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [v for v in check(review, records) if v.get("code") == ASSERTED_NOT_UNDERLYING]
