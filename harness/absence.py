"""Absence-state ontology (external audit): 'declared absent' conflated four epistemically different
things, letting a page say 'no harms recorded' while the abstract reports a harm. Split them, and
reserve the strong claim for the first only:

  NO_OUTCOME_DATA_IN_SOURCE  — the retrieved source genuinely does not report this outcome. The ONLY
                               state that licenses 'declared absent' (a claim about the trial).
  EXTRACTION_NOT_PERFORMED   — the outcome's effect/counts ARE in the retrieved source but were not
                               machine-extracted (a claim about US, not the trial). The false-absence class.
  SOURCE_NOT_RETRIEVED       — only the abstract was retrieved and it does not report this (usually a
                               secondary/harm); the full text was not fetched, so absence in the TRIAL
                               is not established — we cannot distinguish 'not in trial' from 'not in abstract'.
  OUTCOME_NOT_REQUESTED      — the outcome is not on this topic's prespecified list (handled upstream;
                               a declared-absent trial is always about a REQUESTED outcome, so the
                               per-trial classifier returns one of the three above).

`UNASSESSED NEVER COUNTS AS FAVOURABLE`: none of these is evidence of no effect.
"""
import re
from . import estmeasure, extract, lexicon
from .markup import strip_markup

_EFFECT = re.compile(r"\b(?:RR|OR|HR|IRR|rate ratio|risk ratio|hazard ratio|odds ratio|relative risk)\b"
                     r"[^.]{0,40}?\d+\.\d+", re.I)
_ARMS = re.compile(r"\b\d+\s*/\s*\d{2,}\b|\b\d+\s+of\s+\d{2,}\b|"
                   r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten)\s+of\s+\d{2,}\b", re.I)
_COUNT_WITH_PERCENT = re.compile(
    r"\b\d+\s*(?:/|of)\s*\d{2,}\b[^.]{0,40}?\b\d+(?:\.\d+)?\s*%"
    r"|\b\d+(?:\.\d+)?\s*%[^.]{0,40}?\b\d+\s*/\s*\d{2,}\b"
    r"|\b\d+\s+(?:patients?|participants?|subjects?)?\s*[\(\[]\s*\d+(?:\.\d+)?\s*%[\)\]]",
    re.I,
)
_BARE_OUTCOME_COUNTS = re.compile(
    r"\b(?:a\s+)?total\s+of\s+\d+\s+and\s+\d+[^.;]{0,100}hospitali[sz]ations?\s+for\s+heart\s+failure\b",
    re.I,
)
_PRIMARY_RESULT = re.compile(r"\bprimary\s+(?:outcomes?|end\s*points?|endpoints?|events?)\b", re.I)
_GENERIC_ANCHORS = {"primary outcome", "primary endpoint", "primary end point",
                    "primary study outcome", "primary study end point"}
_ESTIMAND_SUFFIX = re.compile(r"\b(?:RR|OR|HR|IRR|MD|SMD|risk ratio|odds ratio|hazard ratio|rate ratio)\b",
                              re.I)

OUTCOME_NOT_IN_SOURCE = "OUTCOME_NOT_IN_SOURCE"
EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH = "EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH"
COUNTS_PRESENT_NOT_CORROBORATED = "COUNTS_PRESENT_NOT_CORROBORATED"
MULTI_ARM_UNRESOLVED = "MULTI_ARM_UNRESOLVED"
TIMEPOINT_MISMATCH = "TIMEPOINT_MISMATCH"
POPULATION_MISMATCH = "POPULATION_MISMATCH"
SOURCE_NOT_RETRIEVED = "SOURCE_NOT_RETRIEVED"
EXTRACTION_NOT_PERFORMED = "EXTRACTION_NOT_PERFORMED"
REFUSED_ON_EVIDENCE = "REFUSED_ON_EVIDENCE"
SIGNAL_SPURIOUS = "SIGNAL_SPURIOUS"
OUTCOME_POST_HOC_NOT_POOLED = "outcome_post_hoc_not_pooled"
OUTCOME_NOT_REPORTED = "outcome_not_reported"
RETRIEVED_INCOMPATIBLE_STRUCTURE = "RETRIEVED_INCOMPATIBLE_STRUCTURE"
RETRIEVED_REFUSED_WITH_REASON = "RETRIEVED_REFUSED_WITH_REASON"
UNIT_MISMATCH_CYCLE_LEVEL = "UNIT_MISMATCH_CYCLE_LEVEL"
ENGINE_CANNOT_CONSUME = "ENGINE_CANNOT_CONSUME"

_CODE_ALIASES = {
    "NO_OUTCOME_DATA_IN_SOURCE": OUTCOME_NOT_IN_SOURCE,
    "EXTRACTION_NOT_PERFORMED": EXTRACTION_NOT_PERFORMED,
    "REFUSED_ON_EVIDENCE": REFUSED_ON_EVIDENCE,
    "ENGINE_CANNOT_CONSUME": ENGINE_CANNOT_CONSUME,
    "SOURCE_NOT_RETRIEVED": SOURCE_NOT_RETRIEVED,
}

_REASON_HINTS = (
    ("multi-arm", MULTI_ARM_UNRESOLVED),
    ("multi arm", MULTI_ARM_UNRESOLVED),
    ("timepoint mismatch", TIMEPOINT_MISMATCH),
    ("population mismatch", POPULATION_MISMATCH),
    ("per-protocol", POPULATION_MISMATCH),
    ("per protocol", POPULATION_MISMATCH),
    ("completers", POPULATION_MISMATCH),
)


def _strip_markup(text):
    """Full texts are committed as raw JATS/HTML; the sentence splitter needs prose, not tags. Strip
    tags ONLY (and collapse whitespace) -- deliberately NOT dropping any region. The safety asymmetry:
    a spurious 'number present' only downgrades the strong DECLARED_ABSENT claim to a self-deprecating
    'extraction gap' (safe), whereas dropping a region that might hold the result (e.g. a JATS <back>
    appendix carrying a supplementary outcome table) could mask a real number and manufacture a false
    absence (dangerous). So we keep everything and only remove markup, which alone kills the tag-attribute
    numbers (id="FN3", DOIs) that caused a footnote to match. The abstract path is plain text (no-op)."""
    if not text or "<" not in text:
        return text
    return re.sub(r"\s+", " ", strip_markup(text))   # V1.1: a literal P<0.001 is text, not a tag


def _outcome_number_present(text, keywords):
    """True iff the OUTCOME's own sentences (selected by its keywords) contain an effect+CI or arm
    counts -- scoped, so a different outcome's number elsewhere in the text does not count."""
    if not text or not keywords:
        return False
    sents = " ".join(extract._outcome_sentences(_strip_markup(text), keywords))
    return bool(_EFFECT.search(sents) or _ARMS.search(sents))


def classify(keywords, abstract, fulltext=None):
    """Return (state, basis). `fulltext` is the committed full text if we hold it (else None)."""
    if _outcome_number_present(abstract, keywords) or (fulltext and _outcome_number_present(fulltext, keywords)):
        return ("EXTRACTION_NOT_PERFORMED",
                "the outcome's effect/counts ARE present in the retrieved source but were not "
                "machine-extracted; this is a limitation of extraction, NOT evidence the trial lacks the outcome")
    if fulltext:
        return ("NO_OUTCOME_DATA_IN_SOURCE",
                "neither the abstract nor the retrieved full text reports this outcome")
    return ("SOURCE_NOT_RETRIEVED",
            "only the abstract was retrieved and it does not report this outcome; the full text was not "
            "fetched, so absence of the outcome in the TRIAL is not established")


def _norm_space(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def _clip(text, limit=200):
    text = _norm_space(text)
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "..."


def _terms(keywords, outcome_name=None):
    out = []
    for k in list(keywords or []) + ([outcome_name] if outcome_name else []):
        if not k:
            continue
        t = _ESTIMAND_SUFFIX.sub(" ", str(k))
        t = t.replace("-", " ")
        t = re.sub(r"[^A-Za-z0-9 ]+", " ", t)
        t = _norm_space(t)
        if not t:
            continue
        if t.lower() in _GENERIC_ANCHORS:
            continue
        out.append(t)
    # Low-risk expansions for the source-audit pass. These do not affect extraction or pooling.
    folded = {lexicon.fold(t).replace("-", " ") for t in out}
    more = set()
    for t in folded:
        if "heart failure" in t and ("hospital" in t or "admission" in t):
            more.update({
                "heart failure hospitalization",
                "heart failure hospitalizations",
                "heart failure hospitalisation",
                "heart failure hospitalisations",
                "hospitalization for heart failure",
                "hospitalizations for heart failure",
                "hospitalisation for heart failure",
                "hospitalisations for heart failure",
                "hospital admissions for heart failure",
                "hf hospitalization",
                "hfh",
            })
        if "major adverse cardiovascular" in t:
            more.add("mace")
    folded.update(lexicon.fold(x).replace("-", " ") for x in more)
    return sorted({t for t in folded if len(t) >= 3}, key=len, reverse=True)


def _matches_term(sentence, terms):
    sf = lexicon.fold(sentence).replace("-", " ")
    return any(t in sf for t in terms)


def _candidate_sentences(text, keywords, outcome_name=None):
    text = _strip_markup(extract._norm(text or ""))
    terms = _terms(keywords, outcome_name)
    if not text or not terms:
        return []
    out = []
    raw = extract._sentences(text)
    primary_anchor = any(_PRIMARY_RESULT.search(s) and _matches_term(s, terms) for s in raw)
    for s in raw:
        if _matches_term(s, terms):
            out.append(_norm_space(s))
        elif primary_anchor and _PRIMARY_RESULT.search(s):
            out.append(_norm_space(s))
    return out


def _effect_class(scale, span):
    label = (scale or "").upper()
    if label == "RR" and getattr(extract, "_RECURRENT_PERSONTIME").search(span or ""):
        return "RATE"
    canon = estmeasure.classify(label, span).get("canonical_estimand")
    return estmeasure.compatibility_class(canon)


def _declared_class(estimand):
    s = (estimand or "RR").upper()
    if s in ("RR", "OR", "HR"):
        return "FIRST_EVENT_RATIO"
    if s in ("IRR", "RATE_RATIO", "RATE_RATIO_RECURRENT"):
        return "RATE"
    if s in ("MD", "SMD"):
        return "CONTINUOUS"
    return "OTHER"


def _effect_candidates(sentences, terms=None):
    primary, fallback = [], []
    for s in sentences:
        ns = extract._norm(s)
        prev_end = 0
        for m in extract._EFFECT.finditer(ns):
            clause = ns[prev_end:m.start()][-260:]
            context = ns[max(0, m.start() - 260):m.end() + 120]
            eff = extract._effect_from_match(m, context)
            prev_end = m.end()
            if not eff:
                continue
            clause_tail = re.split(r"(?<=[.;)])\s+", clause.strip())[-1] if clause.strip() else ""
            span = _clip((clause_tail + " " + ns[m.start():m.end() + 140]).strip())
            klass = _effect_class(eff[0], span)
            cand = {
                "effect": eff[1],
                "ci_low": eff[2],
                "ci_high": eff[3],
                "scale": eff[0],
                "class": klass,
                "span": span,
            }
            if terms and _matches_term(clause, terms):
                primary.append(cand)
            else:
                fallback.append(cand)
    return primary or fallback


def _count_candidates(sentences, terms=None):
    out = []
    for s in sentences:
        for m in _COUNT_WITH_PERCENT.finditer(extract._norm(s)):
            span = s[max(0, m.start() - 80):m.end() + 120]
            if not terms or _matches_term(span, terms):
                out.append(_clip(span))
        for m in _BARE_OUTCOME_COUNTS.finditer(extract._norm(s)):
            span = s[max(0, m.start() - 80):m.end() + 120]
            out.append(_clip(span))
    return out


def _reason_hint_code(reason):
    rl = (reason or "").lower()
    for needle, code in _REASON_HINTS:
        if needle in rl:
            return code
    if "estimand mismatch" in rl:
        return EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH
    return None


def _basis(code, span=None, detail=None):
    if span:
        return f"{code}: source span: \"{_clip(span)}\"" + (f"; {detail}" if detail else "")
    return f"{code}: {detail or 'no source span available'}"


def classify_reason(keywords, abstract, fulltext=None, outcome_name=None, declared_estimand=None,
                    reason=None, absent_kind=None, row=None):
    """Classify a declared-absent/refused row from the committed source.

    This is an audit layer only: it reports what was visible in the cached source and why a row is not
    poolable. It never changes extraction order and never makes a non-pooled value poolable.
    """
    row = row or {}
    # A row `admit_rows` refused or set aside on its endpoint binding keeps the code it was given
    # (RESULT_INCOMPATIBLE / ENDPOINT_UNBOUND): on the served release this layer overwrote a
    # RESULT_INCOMPATIBLE refusal with EXTRACTION_NOT_PERFORMED -- the right reason, mislabelled before
    # publication (M2, 2026-09-20).
    if row.get("endpoint_admissibility") in ("RESULT_INCOMPATIBLE", "ENDPOINT_UNBOUND") and row.get("reason_code"):
        span = row.get("endpoint_result_span") or row.get("source_span") or row.get("source") or ""
        return {"reason_code": row["reason_code"], "state": row.get("state") or REFUSED_ON_EVIDENCE,
                "state_basis": _basis(row["reason_code"], span, reason),
                "source_span": _clip(span), "verbatim_span": _clip(span)}
    # All lane adjudications require a recognized reason and an exact held span.
    code = row.get("refusal_provenance") or row.get("reason_code") or row.get("state")
    span = row.get("source_span") or row.get("verbatim_span")
    allowed = {REFUSED_ON_EVIDENCE, SIGNAL_SPURIOUS, MULTI_ARM_UNRESOLVED,
               TIMEPOINT_MISMATCH, POPULATION_MISMATCH,
               EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH}
    if row.get("typed_refusal") or ((row.get("absent_kind") == "adjudicated_absent" or row.get("source_adjudicated")) and span and code in allowed):
        if code not in allowed or not reason or not span:
            raise ValueError("Typed refusal requires a recognized code, reason and held verbatim span")
        if not any(span in text for text in (abstract or "", fulltext or "")):
            from .verified_inputs import validate_referenced_span
            validate_referenced_span(row)
        return {"reason_code": code, "state": code,
                "state_basis": _basis(code, span, reason),
                "source_span": span, "verbatim_span": span}
    if row.get("state") in (OUTCOME_POST_HOC_NOT_POOLED, OUTCOME_NOT_REPORTED):
        code = row.get("state")
        span = row.get("source_span") or row.get("verbatim_span") or row.get("source") or reason or ""
        return {
            "reason_code": code,
            "state": code,
            "state_basis": _basis(code, span, reason),
            "source_span": _clip(span),
            "verbatim_span": _clip(span),
        }
    if (
        row.get("state") == ENGINE_CANNOT_CONSUME
        or row.get("reason_code") == ENGINE_CANNOT_CONSUME
        or row.get("absent_kind") == "engine_cannot_consume"
    ):
        return {
            "reason_code": ENGINE_CANNOT_CONSUME,
            "state": ENGINE_CANNOT_CONSUME,
            "state_basis": row.get("state_basis") or _basis(
                ENGINE_CANNOT_CONSUME,
                detail="design-adjusted effect or ICC design effect is not held",
            ),
            "source_span": row.get("source_span") or "",
            "verbatim_span": row.get("verbatim_span") or "",
        }
    hint = _reason_hint_code(reason)
    design_span = None
    for b in (((row.get("design") or {}).get("basis")) or []):
        if b.get("span"):
            design_span = b.get("span")
            break
    locate_span = (row.get("locate_judgment") or {}).get("span")
    if not (abstract or "").strip():
        return {
            "reason_code": SOURCE_NOT_RETRIEVED,
            "state": SOURCE_NOT_RETRIEVED,
            "state_basis": _basis(SOURCE_NOT_RETRIEVED, detail="cached abstract text is missing for this record"),
            "source_span": "",
            "verbatim_span": "",
        }

    texts = [("abstract", abstract or "")]
    if fulltext:
        texts.append(("fulltext", fulltext))
    sentences = []
    for src, txt in texts:
        for sent in _candidate_sentences(txt, keywords, outcome_name):
            sentences.append((src, sent))
    sent_texts = [s for _, s in sentences]

    terms = _terms(keywords, outcome_name)
    effects = _effect_candidates(sent_texts, terms)
    declared = _declared_class(declared_estimand)
    if effects:
        eff = effects[0]
        code = (EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH
                if eff["class"] != declared or hint == EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH
                else EXTRACTION_NOT_PERFORMED)
        return {
            "reason_code": code,
            "state": code,
            "state_basis": _basis(
                code,
                eff["span"],
                f"effect={eff['scale']} {eff['effect']} [{eff['ci_low']}, {eff['ci_high']}], "
                f"class={eff['class']}, declared_class={declared}",
            ),
            "source_span": eff["span"],
            "verbatim_span": eff["span"],
            "observed_effect": eff,
            "declared_class": declared,
        }

    counts = _count_candidates(sent_texts, terms)
    if counts:
        span = counts[0]
        return {
            "reason_code": COUNTS_PRESENT_NOT_CORROBORATED,
            "state": COUNTS_PRESENT_NOT_CORROBORATED,
            "state_basis": _basis(COUNTS_PRESENT_NOT_CORROBORATED, span),
            "source_span": span,
            "verbatim_span": span,
            "count_candidates": counts[:5],
        }

    if hint:
        span = locate_span or design_span or (sent_texts[0] if sent_texts else reason)
        return {
            "reason_code": hint,
            "state": hint,
            "state_basis": _basis(hint, span),
            "source_span": _clip(span or ""),
            "verbatim_span": _clip(span or ""),
        }

    if absent_kind == "refused_on_evidence":
        span = locate_span or design_span or (sent_texts[0] if sent_texts else reason)
        return {
            "reason_code": REFUSED_ON_EVIDENCE,
            "state": REFUSED_ON_EVIDENCE,
            "state_basis": _basis(REFUSED_ON_EVIDENCE, span),
            "source_span": _clip(span or ""),
            "verbatim_span": _clip(span or ""),
        }

    if sent_texts:
        span = sent_texts[0]
        return {
            "reason_code": OUTCOME_NOT_IN_SOURCE,
            "state": OUTCOME_NOT_IN_SOURCE,
            "state_basis": _basis(OUTCOME_NOT_IN_SOURCE, span, "outcome sentence has no poolable effect+CI or corroborated arm counts"),
            "source_span": _clip(span),
            "verbatim_span": _clip(span),
        }

    checked = _clip(abstract, 200)
    return {
        "reason_code": OUTCOME_NOT_IN_SOURCE,
        "state": OUTCOME_NOT_IN_SOURCE,
        "state_basis": _basis(OUTCOME_NOT_IN_SOURCE, checked, "no sentence matching the outcome terms was found"),
        "source_span": checked,
        "verbatim_span": checked,
    }


def normalize_code(code):
    return _CODE_ALIASES.get(code or "", code or "")


def stated_code(row):
    return normalize_code(row.get("reason_code") or row.get("state"))


def verdict_for_row(row, actual):
    actual_code = normalize_code((actual or {}).get("reason_code"))
    stated = stated_code(row)
    if not actual_code:
        return "NOT_CHECKABLE"
    if stated:
        return "TRUE" if stated == actual_code else "FALSE"
    reason = (row.get("reason") or "").lower()
    if actual_code == OUTCOME_NOT_IN_SOURCE and (
            "no percentage-corroborated" in reason or "not found in the abstract" in reason):
        return "TRUE"
    if actual_code == SOURCE_NOT_RETRIEVED and "source_not_retrieved" in reason:
        return "TRUE"
    return "NOT_CHECKABLE"
