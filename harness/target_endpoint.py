"""Target-endpoint selection for pooled trial rows.

The selector separates endpoint identity from numeric extraction: enumerate
held-source candidates, classify each against the registered target endpoint,
then choose the best candidate by endpoint match before source rank.  A disclosed
near-match is poolable only when no exact target exists in held source bytes.
"""
from __future__ import annotations

import re
from typing import Any

from . import extract, hand_binding
from .ctgov_results import _classify_arms, _num, _registry_measure_type

# ONE exclusion semantics for producer and verifier. The verifier (scripts/verify_bundle.py) must import nothing from this
# repository (tests/test_bundle_verifier.py), so the relation functions live there and the producer imports them; the
# certificate's import closure (harness/code_closure.py follows scripts/) then pins the verifier's bytes for every topic.
from scripts import verify_bundle as _relations  # noqa: E402

EXACT_TARGET = "EXACT_TARGET"
NEAR_MATCH = "NEAR_MATCH"
DIFFERENT_OUTCOME = "DIFFERENT_OUTCOME"
EXACT_TARGET_IN_SOURCE_NOT_HELD = "EXACT_TARGET_IN_SOURCE_NOT_HELD"
ENDPOINT_UNBOUND = "ENDPOINT_UNBOUND"
# the bound endpoint EXCLUDES a target component ('nonfatal stroke was excluded from the primary outcome'): refused
ENDPOINT_COMPONENT_EXCLUDED = "ENDPOINT_COMPONENT_EXCLUDED"
# the bound result counts a different EVENT PROCESS from the target: total (first and recurrent) events against a
# first-event target, or event counts against patients-with-an-event (EMPEROR-Preserved: 407 vs 541 total HHF, HR 0.73,
# is not the time-to-first composite, HR 0.79): refused
EVENT_PROCESS_MISMATCH = "EVENT_PROCESS_MISMATCH"

# ---- EVENT PROCESS: part of endpoint identity ------------------------------------------------------------------------
# {FIRST_EVENT, TOTAL_EVENTS} x {PATIENTS_WITH_EVENT, EVENT_COUNT}. Read only from EXPLICIT evidence; a span that says
# neither leaves the dimension undecided (no refusal). 'Recurrent VTE' is a disease, not a total-event count.
FIRST_EVENT, TOTAL_EVENTS = "FIRST_EVENT", "TOTAL_EVENTS"
PATIENTS_WITH_EVENT, EVENT_COUNT = "PATIENTS_WITH_EVENT", "EVENT_COUNT"
_TOTAL_EVENTS = re.compile(
    r"\bfirst\s+and\s+(?:subsequent|recurrent|repeat(?:ed)?)\b|"
    r"\btotal\s+(?:number\s+of\s+)?(?:[a-z-]+\s+){0,4}?(?:hospitali[sz]ations|admissions|events|episodes|exacerbations)\b|"
    r"\b(?:recurrent|repeat(?:ed)?)\s+(?:(?:heart\s+failure|hf)\s+)?(?:hospitali[sz]ations|admissions|events)\b|"
    r"\bincluding\s+(?:all\s+)?(?:recurrences|recurrent\s+(?:events|hospitali[sz]ations))\b|"
    r"\brecurrent[\s-]+event\s+(?:model|analysis|analyses|method)\b|\bjoint\s+frailty\b|\bnegative\s+binomial\b|"
    r"\blin[\s-]+wei\b|\bandersen[\s-]+gill\b|\bevent\s+rate\s+ratio\b|\brate\s+of\s+(?:total|recurrent)\b|"
    r"\bannuali[sz]ed\s+(?:event\s+)?rate\b|"
    # the recurrent-event rate models themselves (SGLT2-HFrEF review: DAPA-HF's 'LWYY proportional rates model', 'semiparametric
    # proportional-rates model'); and the registry's own event-count label ('Events Included in ...', beside 'Subjects
    # Included in ...' for the first-event measure)
    r"\blwyy\b|\bproportional[\s-]+rates?\b|\bghosh[\s-]+lin\b|\bmean\s+(?:cumulative\s+)?frequency\b|"
    r"\bevents\s+included\s+in\b", re.I)
_COX = re.compile(r"\bcox\b|\bproportional[\s-]+hazards?\b", re.I)
_RECURRENT_METHOD = re.compile(r"joint\s+frailty|negative\s+binomial|lin[\s-]+wei|andersen[\s-]+gill|recurrent[\s-]+event\s+"
                               r"(?:model|analysis|analyses|method)|lwyy|proportional[\s-]+rates?|ghosh[\s-]+lin", re.I)
# a total-event phrase that is NEGATED is a first-event statement ('recurrent events were not included')
_TOTAL_NEGATED_AFTER = re.compile(r"\s*(?:were|was)\s+(?:not\s+(?:included|counted|analy[sz]ed)|excluded)\b", re.I)
_TOTAL_NEGATED_BEFORE = re.compile(r"\b(?:excluding|without|not\s+including|other\s+than)\s+$", re.I)
_FIRST_EVENT = re.compile(r"\bfirst\s+(?:occurrence|event|episode|hospitali[sz]ation|admission|exacerbation)\b|"
                          r"\btime\s+to\s+(?:the\s+)?first\b|\bpatients\s+with\s+(?:at\s+least\s+one|>=\s*1|≥\s*1|an?|one\s+or\s+"
                          r"more)\s+(?:event|hospitali[sz]ation|admission|exacerbation)s?\b", re.I)
# an explicit count of PATIENTS WITH the event -- not a denominator ('assessed in 5988 patients', 'in 1000 patients')
_PATIENT_COUNTS = re.compile(r"\b\d[\d,]*\s+(?:of|/)\s*\d[\d,]*\s+(?:patients|participants|subjects)\b|"
                             r"\b\d[\d,]*\s+(?:patients|participants|subjects)\s*\(\s*\d|"
                             r"\b(?:occurred|developed|experienced|had|reported)\s+(?:in\s+)?\d[\d,]*\s+(?:patients|participants|subjects)\b|"
                             r"\bnumber\s+of\s+patients\s+with\b", re.I)


def event_process(text: str | None) -> dict[str, Any]:
    """{'process': FIRST_EVENT | TOTAL_EVENTS | None, 'count_unit': PATIENTS_WITH_EVENT | EVENT_COUNT | None,
    'evidence': [...]} for a result span, from EXPLICIT statements only. The count unit follows the process (a first-event
    count is a count of patients; a total-event count is a count of events); with no stated process only an explicit
    patients-with-the-event statement decides it. A bare 'N events' decides nothing -- tables report first-event analyses
    as 'No. of events'. Both processes stated -> undecided (never a refusal by default)."""
    s = text or ""
    allm = list(_TOTAL_EVENTS.finditer(s))
    tot = [m for m in allm
           if not _TOTAL_NEGATED_AFTER.match(s, m.end()) and not _TOTAL_NEGATED_BEFORE.search(s[:m.start()])]
    negated = [m for m in allm if m.span() not in {t.span() for t in tot}]
    # the ESTIMATE's own analysis method outranks a descriptive count: a Cox model is a time-to-FIRST-event analysis, so
    # 'Exposure-adjusted incident rate ... n = total number of events' describing a registry measure whose analysis is
    # 'Hazard Ratio ... Regression, Cox' is a first-event HR (PARALLEL-HF NCT02468232, lane NR rebuild diff); only a
    # recurrent-event METHOD (joint frailty, negative binomial, Lin-Wei, Andersen-Gill, a recurrent-event model) makes
    # a hazard ratio a total-event result
    if _COX.search(s) and not any(_RECURRENT_METHOD.search(m.group(0)) for m in tot):
        tot = []
    rest = s
    for m in list(tot) + negated:
        rest = rest[:m.start()] + " " * (m.end() - m.start()) + rest[m.end():]
    first = [m.group(0) for m in _FIRST_EVENT.finditer(rest)]
    if negated and not tot:
        first.append(negated[0].group(0) + " (negated)")
    process = TOTAL_EVENTS if tot and not first else FIRST_EVENT if first and not tot else None
    pt = [m.group(0) for m in _PATIENT_COUNTS.finditer(rest)]
    unit = {TOTAL_EVENTS: EVENT_COUNT, FIRST_EVENT: PATIENTS_WITH_EVENT}.get(process) or \
        (PATIENTS_WITH_EVENT if pt and not tot else None)
    return {"process": process, "count_unit": unit, "evidence": [m.group(0) for m in tot] + first + pt}


def target_event_process(spec: dict[str, Any]) -> dict[str, Any]:
    """The target's event process: declared (`event_process`, `count_unit`), else read from the outcome name ('total',
    'first and recurrent', 'recurrent hospitalizations'), else from the estimand -- a rate ratio counts total events;
    HR / RR / OR count patients with a first event."""
    proc = spec.get("event_process")
    if not proc:
        name = str(spec.get("name") or "")
        est = str(spec.get("estimand") or "").upper()
        if _TOTAL_EVENTS.search(name) or est in ("IRR", "RATE_RATIO", "RATE_RATIO_RECURRENT"):
            proc = TOTAL_EVENTS
        elif est in ("HR", "RR", "OR", "") or _FIRST_EVENT.search(name):
            proc = FIRST_EVENT
    unit = spec.get("count_unit") or {FIRST_EVENT: PATIENTS_WITH_EVENT, TOTAL_EVENTS: EVENT_COUNT}.get(proc)
    return {"process": proc, "count_unit": unit}


def event_process_problem(spec: dict[str, Any], text: str | None) -> dict[str, Any] | None:
    """None when the result's stated event process and count unit agree with the target's (or are unstated); else the
    two readings. Continuous outcomes have no event process."""
    if str(spec.get("estimand") or "").upper() in ("MD", "SMD"):
        return None
    ep, tp = event_process(text), target_event_process(spec)
    bad = [d for d in ("process", "count_unit") if ep[d] and tp[d] and ep[d] != tp[d]]
    return {"result": ep, "target": tp, "dimensions": bad} if bad else None

# Endpoint-span binding (external review of served glp1 edaf5f6b, defect 1 -- wrong-endpoint
# acceptance).  Before this, an abstract candidate was classified against the WHOLE abstract and that
# classification was attached to a number read from ONE sentence: an abstract that defines the primary
# outcome as 3-point MACE, reports no composite result, and reports CV death alone as HR 0.50 was
# certified as the 3-point MACE effect (EXACT_TARGET, components CV death/MI/stroke, verified).  Every
# effect is now bound to its own RESULT span (the sentence the number was read from) and to the
# DEFINITION span that sentence refers to (its own enumerated components, or the unique primary-outcome
# / named-composite definition sentence it names).  The class is computed from the definition span
# only.  A result span that cannot be bound is ENDPOINT_UNBOUND and never admissible.
BINDING_SELF = "result_span_enumerates_components"
BINDING_DEFINITION = "named_endpoint_resolved_to_definition_span"
BINDING_REGISTRY = "registry_outcome_measure"
BINDING_NONE = "unbound"

_NAMED_COMPOSITE_RX = re.compile(
    # "primary-outcome event" (SOUL, NEJM house style) names the primary outcome as much as "primary outcome";
    # "primary efficacy measure" (STRENGTH) names one as much as "primary end point" (ws/STRENGTHFIX)
    r"\b(?:co-?primary|primary|(?:key |first |second |main )?secondary)[\s-]+(?:[a-z][a-z-]*\s+){0,3}?"
    r"(?:outcome|end[\s-]?point|measure|variable)s?\b|\bmace\b|major adverse cardiovascular event|major cardiovascular event"
    r"|\bcomposite (?:outcome|end[\s-]?point)\b|\bprimary composite\b"
    r"|\b(?:major|serious) (?:adverse )?vascular events?\b",
    re.I,
)
_QUALIFIER_RX = re.compile(
    r"\b(?:(?P<sec>(?:key |first |second |main )?secondary)|(?P<pri>co-?primary|primary|second primary|first primary))[\s-]+"
    r"(?:[a-z][a-z-]*\s+){0,3}?(?:outcome|end[\s-]?point|measure|variable)s?\b", re.I)
_MACE_RX = re.compile(r"\bmace\b|major adverse cardiovascular|major cardiovascular|(?:major|serious) (?:adverse )?vascular event", re.I)
# Endpoint REFERENCE identity (audit 2026-09-20): which defined endpoint a sentence is about is settled by the
# ordinal / timepoint / population it names, before any component comparison.
_ORDINAL_WORDS = {"first": 1, "second": 2, "third": 3, "fourth": 4}
_ORDINAL_RX = re.compile(r"\b(first|second|third|fourth)\s+(?:co-?primary|primary|(?:key |main )?secondary)\b", re.I)
_TIMEPOINT_RX = re.compile(
    r"\b(?:within|at|over|through|by|during|after|to)\s+(?:the\s+first\s+)?(\d+)\s*(days?|weeks?|months?|years?)\b"
    r"|\b(\d+)-(day|week|month|year)\b|\bat\s+(week|month|day|year)\s+(\d+)\b", re.I)
_POPULATION_RX = re.compile(
    r"\b(?:in|among)\s+(?:the\s+)?((?:all\s+)?randomi[sz]ed\s+(?:participants|patients)"
    r"|(?:participants|patients|those)\s+(?:aged|older than|younger than|with|without)\s+[a-z0-9][a-z0-9 ]{1,40}?)"
    r"(?=[,.;:]|\s+(?:was|were|had|the|there)\b)", re.I)


def _reference_of(text: str) -> dict[str, Any]:
    """The endpoint reference a sentence carries: ordinal, qualifier, timepoint, population (None when absent)."""
    tl = _fold(text)
    o = _ORDINAL_RX.search(tl)
    q = _QUALIFIER_RX.search(tl)
    qualifier = "secondary" if (q and q.group("sec")) else ("primary" if q else None)
    t = _TIMEPOINT_RX.search(tl)
    timepoint = None
    if t:
        if t.group(1):
            timepoint = f"{t.group(1)} {t.group(2).rstrip('s')}"
        elif t.group(3):
            timepoint = f"{t.group(3)} {t.group(4)}"
        else:
            timepoint = f"{t.group(6)} {t.group(5)}"
    pop = _POPULATION_RX.search(tl)
    population = re.sub(r"\s+", " ", pop.group(1)).strip() if pop else None
    return {"ordinal": _ORDINAL_WORDS[o.group(1).lower()] if o else None, "qualifier": qualifier,
            "timepoint": timepoint, "population": population}


def _names_phrase(text: str, phrase: str) -> bool:
    """`phrase` occurs in `text` as a whole phrase: not inside a longer word or number ('3-point mace' is not named by
    '13-point mace'). Plain string search -- no pattern is built from the text."""
    i = text.find(phrase)
    while i >= 0:
        before = text[i - 1] if i else " "
        after = text[i + len(phrase)] if i + len(phrase) < len(text) else " "
        if not (before.isalnum() or before in "-_") and not (after.isalnum() or after in "-_"):
            return True
        i = text.find(phrase, i + 1)
    return False


def _resolve_reference(rs: str, pool: list[dict[str, Any]]) -> dict[str, Any]:
    """Select the definition the result REFERS to. Returns {selected, record, how} where record carries
    definition_candidates / endpoint_reference / selected_definition / unresolved_alternatives."""
    ref = _reference_of(rs)
    cands = []
    seen = set()
    for d in pool:
        key = re.sub(r"\W+", " ", (d.get("segment") or d["span"]).lower()).strip()
        if key in seen:
            continue            # an identical repeated definition is a harmless duplicate, not a second endpoint
        seen.add(key)
        cands.append(d)
    record = {"definition_candidates": [{"span": d["span"], "label": d.get("label"),
                                         "components": sorted(d["components"]),
                                         "ordinal": d.get("ordinal"), "timepoint": d.get("timepoint"),
                                         "population": d.get("population")} for d in cands],
              "endpoint_reference": ref, "selected_definition": None, "unresolved_alternatives": []}
    how = []
    narrowed = list(cands)
    rl = (rs or "").lower()
    labelled = [d for d in narrowed if d.get("label") and _names_phrase(rl, d["label"])]
    if labelled:
        narrowed, how = labelled, how + ["label"]
    if len(narrowed) > 1 and ref["ordinal"]:
        explicit = [d for d in narrowed if d.get("ordinal") == ref["ordinal"]]
        if explicit:
            narrowed, how = explicit, how + ["ordinal"]
        elif not any(d.get("ordinal") for d in narrowed):
            narrowed = [narrowed[ref["ordinal"] - 1]] if ref["ordinal"] <= len(narrowed) else []
            how.append("ordinal (positional: no definition carries an ordinal)")
        else:
            narrowed = []       # definitions carry ordinals and none is the one named
    if len(narrowed) > 1 and ref["timepoint"]:
        m = [d for d in narrowed if d.get("timepoint") == ref["timepoint"]]
        if m:
            narrowed, how = m, how + ["timepoint"]
    if len(narrowed) > 1 and ref["population"]:
        m = [d for d in narrowed if d.get("population") and (d["population"] == ref["population"]
                                                              or d["population"] in ref["population"]
                                                              or ref["population"] in d["population"])]
        if m:
            narrowed, how = m, how + ["population"]
    if len(narrowed) > 1:
        # compatibility: two candidates are one endpoint unless BOTH state an attribute with different values
        def _conflict(x, y):
            return any(x.get(k) is not None and y.get(k) is not None and x.get(k) != y.get(k)
                       for k in ("ordinal", "timepoint", "population"))
        conflicting = any(_conflict(narrowed[i], narrowed[j])
                          for i in range(len(narrowed)) for j in range(i + 1, len(narrowed)))
        if not conflicting:
            # prefer the candidate whose stated attributes match the result's reference, else the first definition
            def _matches(d):
                return sum(1 for k in ("timepoint", "population") if ref.get(k) and d.get(k) == ref[k])
            best = max(narrowed, key=_matches)
            narrowed, how = [best], how + ["every candidate states a compatible endpoint identity"]
    if len(narrowed) == 1:
        record["selected_definition"] = narrowed[0]["span"]
        return {"selected": narrowed[0], "record": record, "how": how}
    record["unresolved_alternatives"] = [d["span"] for d in (narrowed or cands)]
    return {"selected": None, "record": record, "how": how}

PUBLISHED_TARGET_EFFECT = "published_target_effect"
REGISTRY_PUBLISHED_EFFECT = "registry_published_effect"
RECONSTRUCTION = "reconstruction"

SOURCE_RANK = {
    PUBLISHED_TARGET_EFFECT: 300,
    REGISTRY_PUBLISHED_EFFECT: 200,
    RECONSTRUCTION: 100,
}


def protocol_rule_object() -> dict[str, Any]:
    return {
        "summary": (
            "Target endpoint selector: EXACT_TARGET beats NEAR_MATCH; a near-match may be pooled "
            "only when no exact target is held. Within the same endpoint class, source-reported "
            "target-estimand effects beat registry effect estimates, which beat crude reconstructions. "
            "For multiple registered primaries in the same outcome family, choose the prespecified "
            "primary whose component set is closest to the canonical review definition; ties use "
            "registration order and alternatives render as sensitivity rows. Rule applied after "
            "results were already known in this lane, so the timing is disclosed."
        ),
        "results_known_at_rule_time": True,
    }


def _fold(text: str | None) -> str:
    s = str(text or "").lower()
    replacements = {
        "hospitalisation": "hospitalization",
        "hospitalisations": "hospitalizations",
        "cardiovascular": "cardiovascular",
        "cv ": "cardiovascular ",
        "hhf": "heart failure hospitalization",
        "e-gfr": "egfr",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    # the adverse-event families abbreviated, as safety tables label them (esketamine Table 4: 'TEAEs | 120 (95.2)')
    s = re.sub(r"\bteaes?\b", "treatment-emergent adverse events", s)
    s = re.sub(r"\bsaes?\b", "serious adverse events", s)
    s = re.sub(r"\baes?\b", "adverse events", s)
    return re.sub(r"\s+", " ", s)


def _ws_lower(text: str | None) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().lower()


def endpoint_relations(text: str | None, context: str | None = None,
                       expand_named_composites: bool = True) -> dict[str, Any]:
    """The endpoint a span defines, as typed relations: INCLUDES(x) and EXCLUDES(x).

    EXCLUDES comes from exclusion SCOPES in the span ('excluding X', 'other than X', 'X' in '(excluding X)' when it is not a
    qualifier of the component before it) and exclusion STATEMENTS in the span or its document `context` ('X was excluded
    from the primary outcome', 'neither X nor Y contributed', a footnote after the result). A POPULATION exclusion
    ('patients with prior stroke were excluded from enrolment', 'patients without prior stroke') excludes nothing.
    INCLUDES is read from the span with every excluded scope and statement cut out, so mentioning what is excluded never
    includes it; a component that is also explicitly excluded is excluded. The relation functions are the verifier's
    (scripts/verify_bundle.py split_exclusions / analysis_exclusions), called with this producer's vocabulary."""
    low = _ws_lower(text)
    namer = lambda t: sorted(_mentions_from_text(t, expand_named_composites=False))  # noqa: E731
    inc_text, exc_text = _relations.split_exclusions(low, namer=namer)
    stmt_text, stmts = _relations.analysis_exclusions(low)
    ctx_text, ctx_stmts = _relations.analysis_exclusions(_ws_lower(context)) if context else ("", [])
    for st in stmts:                                  # the statement's subject is in the span: cut it before reading INCLUDES
        inc_text = inc_text.replace(st.lower(), " ")
    excludes = (_mentions_from_text(exc_text, expand_named_composites=False)
                | _mentions_from_text(stmt_text, expand_named_composites=False)
                | _mentions_from_text(ctx_text, expand_named_composites=False))
    includes = _mentions_from_text(inc_text, expand_named_composites=expand_named_composites) - excludes
    return {"includes": includes, "excludes": excludes,
            "exclusion_statements": stmts + [s for s in ctx_stmts if s not in stmts]}


def neighbourhood(document: str | None, span: str | None, radius: int = 400) -> str | None:
    """The document text around a located span (the verifier's document_neighbourhood): where a footnote or the next
    sentence states an exclusion the span itself does not carry."""
    if not document or not span:
        return None
    return _relations.document_neighbourhood(span, document, radius)


def _components_from_text(text: str | None, expand_named_composites: bool = True) -> set[str]:
    """The components a span INCLUDES: positive relations only (endpoint_relations). A component the span excludes, or
    names only inside an exclusion, is not in the set."""
    return endpoint_relations(text, expand_named_composites=expand_named_composites)["includes"]


def _mentions_from_text(text: str | None, expand_named_composites: bool = True) -> set[str]:
    """Every component WORD a span mentions, with no polarity (the vocabulary; read only through endpoint_relations,
    which cuts the exclusions first).  With expand_named_composites (default, definition spans) a bare
    'MACE' / '3-point MACE' with no enumerated components expands to the canonical 3-point set; a
    RESULT span is read with expansion OFF so that 'MACE occurred in ... (HR ...)' resolves to the
    abstract's definition sentence instead of asserting a component set the sentence never states."""
    s = _fold(text)
    comps: set[str] = set()
    if ("coronary heart disease death" in s or "death from coronary heart disease" in s
            or re.search(r"\bchd\b.{0,30}death|death.{0,30}\bchd\b", s)):
        comps.add("coronary heart disease death")
    # 'non-cardiovascular death' / 'death from non-cardiovascular causes' is NOT cardiovascular death
    # (colchicine-secondary-cv-prevention's 'Non-cardiovascular death' outcome was read as CV death)
    s_cv = re.sub(r"\bnon-?\s?cardiovascular\b", "noncv", s)
    if ("cardiovascular death" in s_cv or "death from cardiovascular" in s_cv
            or "cardiovascular causes" in s_cv
            or re.search(r"cardiovascular(?:(?!\b(?:or|and)\b|[,;]).){0,30}death|death(?:(?!\b(?:or|and)\b|[,;]).){0,30}cardiovascular", s_cv)
            or re.search(r"\bcv\b.*death|death.*\bcv\b", s_cv)
            # 'death from vascular causes' / 'vascular death' is the PLATO / PHILO / ASCEND / ORIGIN
            # phrasing of cardiovascular death (not 'cerebrovascular')
            or re.search(r"(?<!cerebro)(?<!cardio)(?<!non-)(?<!non)\bvascular death|(?<!non-)death from vascular causes", s)):
        comps.add("cardiovascular death")
    if "transient ischemic attack" in s or "transient ischaemic attack" in s or re.search(r"\btia\b", s):
        comps.add("transient ischemic attack")
    if (("heart failure" in s and "hospitalization" in s)
            or "hospitalizations due to heart failure" in s
            or re.search(r"\bhospitali[sz]ed for heart failure\b", s)
            # 'hospitalized HF' / 'HF hospitalisation' (CANVAS HF paper: 'hospitalized HF alone (HR, 0.67 ...)')
            or (re.search(r"\bhf\b", s) and re.search(r"hospitali[sz]", s))):
        comps.add("heart failure hospitalization")
    # 'fatal or hospitalized HF' / 'death from heart failure' is a heart-failure death component, not HHF alone
    if re.search(r"(?<!non-)(?<!non)\bfatal\b.{0,25}\b(?:hf|heart failure)\b|death from heart failure|heart failure death", s):
        comps.add("heart failure death")
    if "urgent visit" in s and ("heart failure" in s or re.search(r"\bhf\b", s)):
        comps.add("urgent heart failure visit")
    if (
        "recurrent" in s
        and ("hospitalization" in s or "event" in s)
        and (
            "rate of recurrent" in s
            or "recurrent event rate" in s
            or "total recurrent" in s
            or "first and recurrent" in s
            # a registry measure declared as a recurrent-event analysis (AFFIRM-AHF: "HF hospitalisations
            # ... analysed as recurrent event") is a recurrent-event estimand, not a first-event count
            or re.search(r"analy[sz]ed as (?:a )?recurrent event|recurrent[- ]event analysis", s)
        )
    ):
        comps.add("recurrent events")
    if "myocardial infarction" in s or re.search(r"\bmi\b", s):
        comps.add("myocardial infarction")
    if "stroke" in s:
        comps.add("stroke")
    if "unstable angina" in s:
        comps.add("unstable angina")
    # both spellings alike: the British 'revascularisation' was read, the American 'revascularization' only after 'coronary'
    # (VESALIUS-CV's 4-point MACE, '... or ischemia-driven arterial revascularization', lost its fourth component)
    if "coronary revascularization" in s or "revascularisation" in s or "revascularization" in s:
        comps.add("coronary revascularization")
    if "kidney failure" in s:
        comps.add("kidney failure")
    if "kidney composite" in s or "renal composite" in s or "composite kidney outcome" in s:
        comps.update({"kidney failure", "sustained egfr decline", "renal death"})
    if "egfr" in s and any(w in s for w in ("decline", "decrease", "reduction")):
        comps.add("sustained egfr decline")
    if "renal death" in s or "death from renal" in s:
        comps.add("renal death")
    if expand_named_composites and ("mace" in s or "major adverse cardiovascular" in s or "major cardiovascular" in s):
        if not comps or "3-point" in s or "three-point" in s:
            comps.update({"cardiovascular death", "myocardial infarction", "stroke"})
        if "4-point" in s or "four-point" in s:
            comps.add("unstable angina")
    return comps


def _result_sentence(abstract: str, source: str | None) -> str | None:
    """Recover the full result sentence from an extractor `source` string ('<label>: <sentence[:200]>')."""
    if not source or ": " not in source:
        return None
    frag = source.split(": ", 1)[1].strip()
    if not frag:
        return None
    norm = extract._norm(abstract or "")
    sents = [x.strip() for x in extract._sentences(norm)]
    for x in sents:
        if x.startswith(frag[:120]) or frag[:120] in x:
            return x
    # the extractor truncates at 200 chars; try the longest prefix that still locates one sentence
    for n in (160, 120, 80, 50):
        hits = [x for x in sents if frag[:n] in x]
        if len(hits) == 1:
            return hits[0]
    return None


# A DEFINITION-BEARING sentence defines an endpoint ('The two primary end points were a composite of ...', '... defined
# as ...'); a BACKGROUND or introduction sentence merely mentions one ('The effect of evolocumab on the risk of MACE among
# patients without a previous myocardial infarction or stroke is unknown') -- its population qualifier is not a component
# list (VESALIUS-CV, PCSK9 review f7132bc2: the background sentence was bound as the definition and HR 0.75 refused)
_DEFINING = re.compile(
    r"\bcomposite\s+(?:(?:outcome|end[\s-]?point)\s+)?(?:of|including|comprising)\b|\bdefined\s+(?:as|by)\b|"
    r"\bconsist(?:ed|ing|s)?\s+of\b|\bcompris(?:ed|ing|es)\b|"
    # 'the primary end point of stroke or systemic embolism', 'primary outcome of the first occurrence of ...'
    r"\b(?:end[\s-]?points?|outcomes?)\s+(?:of|was|were)\s+(?:the\s+)?(?:first\s+)?(?:occurrence\s+of\s+)?"
    r"(?!unknown|unclear|uncertain|not\b|lower|higher|reduced|increased|similar|significant|consistent)|"
    # 'All-cause death was the primary end point'
    r"\b(?:was|were)\s+the\s+(?:co-?)?(?:primary|secondary|main|key)\s+(?:[a-z-]+\s+){0,2}?(?:end[\s-]?points?|outcomes?)\b|"
    # 'The key secondary composite outcome, also assessed in a time-to-event analysis, was death from ...'
    r"\b(?:end[\s-]?points?|outcomes?|measures?|variables?|mace)\b[^.;]{0,80}?\b(?:was|were|is|are|included|includes)\s*:?\s+"
    r"(?!unknown|unclear|uncertain|not\b|lower|higher|reduced|increased|similar|significant|consistent|also\s+not)|"
    # a named endpoint with its own bracketed enumeration: 'first MACE (cardiovascular mortality, nonfatal MI, or stroke)',
    # 'the primary endpoint [first HF hospitalization or cardiovascular death]'
    r"\b(?:mace|end[\s-]?point|outcome)\s*[(\[](?:[^()\[\]]*,)*[^()\[\]]*\b(?:or|and)\b[^()\[\]]*[)\]]|"
    # '(MACE: ischaemic stroke, myocardial infarction, ...)'
    r"\(\s*mace\s*:\s*[^()]*,", re.I)
# background / introduction / conclusion text MENTIONS an endpoint; it does not define it
_BACKGROUND = re.compile(
    r"\b(?:is|are|remains?|was|were)\s+(?:still\s+)?(?:unknown|unclear|uncertain|not\s+known|incompletely\s+characteri[sz]ed)\b|"
    r"\bha(?:s|ve)\s+been\s+shown\b|\breduces?\s+the\s+risk\s+of\b(?![^.;]*\bwas\b)|"
    r"^\s*(?:background|introduction|conclusions?(?:\s+and\s+relevance)?|interpretation)\s*:", re.I)
# 'a composite of death from coronary heart disease, myocardial infarction, or ischemic stroke (3-point MACE)'
_LABELLED_COMPOSITE = re.compile(r"\bcomposite\s+of\s+(?P<body>[^()]+?)\s*\((?P<label>[^()]{2,40})\)", re.I)


def _labelled_definitions(x: str) -> list[tuple[str, str, set[str]]]:
    """[(label, segment, components)] for a sentence defining SEVERAL labelled composites; a later composite that names an
    earlier label ('a composite of 3-point MACE or ischemia-driven arterial revascularization (4-point MACE)') includes it."""
    out: list[tuple[str, str, set[str]]] = []
    known: dict[str, set[str]] = {}
    for m in _LABELLED_COMPOSITE.finditer(x):
        label = re.sub(r"\s+", " ", m.group("label")).strip().lower()
        body = m.group("body")
        comps = set(_components_from_text(body, expand_named_composites=False))
        for prior, pc in known.items():
            if prior in body.lower():
                comps |= pc
        known[label] = comps
        out.append((label, m.group(0), comps))
    return out if len(out) >= 2 else []


def _definition_sentences(abstract: str) -> list[dict[str, Any]]:
    """Sentences that DEFINE a named endpoint (anchor + definition cue) and enumerate its components."""
    out = []
    norm = extract._norm(abstract or "")
    for x in extract._sentences(norm):
        xl = x.lower()
        if not _NAMED_COMPOSITE_RX.search(xl):
            continue
        if not extract._DEF_CUE.search(xl):
            continue
        if not _DEFINING.search(x) or _BACKGROUND.search(x):
            continue                # a background / introduction sentence never defines the endpoint
        # a RESULT sentence (carries an effect+CI or arm counts) is never a definition span, even when
        # it mentions a component in passing ("... a primary outcome event occurred in 458 of 3686 ...
        # (hazard ratio 0.87 ...), with ... hospitalization for heart failure")
        if extract.extract_effect(x) or _EFFECT_RE.search(x) or re.search(r"\d+ of \d+", xl):
            continue
        q = _QUALIFIER_RX.search(xl)
        ref = _reference_of(x)
        labelled = _labelled_definitions(x)
        if labelled:
            # one definition per labelled composite, each with its OWN components (VESALIUS-CV: 3-point MACE = CHD death,
            # MI, ischemic stroke; 4-point MACE = 3-point MACE + ischemia-driven revascularization)
            for label, seg, comps in labelled:
                if not comps:
                    continue
                out.append({"span": x.strip(), "segment": seg, "label": label, "components": comps, "excluded": set(),
                            "ordinal": ref["ordinal"], "timepoint": ref["timepoint"], "population": ref["population"],
                            "primary": bool(q and q.group("pri")) or bool(extract._ANCHOR_RX.search(xl)),
                            "secondary": bool(q and q.group("sec")), "mace": bool(_MACE_RX.search(seg + " " + label))})
            continue
        rel = endpoint_relations(x, context=neighbourhood(abstract, x), expand_named_composites=True)
        comps = rel["includes"]
        if not comps:
            continue
        out.append({
            "span": x.strip(),
            "components": comps,
            "excluded": rel["excludes"],
            "ordinal": ref["ordinal"], "timepoint": ref["timepoint"], "population": ref["population"],
            "primary": bool(q and q.group("pri")) or bool(extract._ANCHOR_RX.search(xl)) or bool(re.search(r"\bprimary (?:[a-z-]+ ){0,3}?(?:measure|variable)s?\b", xl)),
            "secondary": bool(q and q.group("sec")),
            "mace": bool(_MACE_RX.search(xl)),
        })
    return out


def bind_result_span(abstract: str, result_span: str | None) -> dict[str, Any]:
    """_bind_result_span, plus the typed EXCLUDES of the bound endpoint: every component the result span or the definition
    span excludes, in themselves or in their document neighbourhood (endpoint_relations). `components` is already the
    positive-only INCLUDES set; `excluded_components` is what _classify refuses on when it names a target component."""
    b = _bind_result_span(abstract, result_span)
    exc: set[str] = set()
    if b["binding"] != BINDING_NONE:
        for span in {b.get("endpoint_result_span"), b.get("endpoint_definition_span")} - {None}:
            exc |= endpoint_relations(span, context=neighbourhood(abstract, span))["excludes"]
    b["excluded_components"] = exc
    return b


def _bind_result_span(abstract: str, result_span: str | None) -> dict[str, Any]:
    """Bind one result span to its endpoint-definition span.

    Returns {"binding", "endpoint_result_span", "endpoint_definition_span", "components", "binding_reason"}.
    BINDING_SELF: the result sentence enumerates >=2 components (it is its own definition), or names
    exactly one component and no endpoint (a component-only result binds to itself).
    BINDING_DEFINITION: the result sentence names an endpoint (primary outcome / MACE / composite)
    and the held abstract holds exactly one distinct component set defining that endpoint.
    BINDING_NONE otherwise (no result span; a named endpoint with no or several definitions)."""
    if not result_span:
        return {"binding": BINDING_NONE, "endpoint_result_span": None,
                "endpoint_definition_span": None, "components": set(),
                "binding_reason": "no result span"}
    rs = result_span.strip()
    own = _components_from_text(rs, expand_named_composites=False)
    names_endpoint = bool(_NAMED_COMPOSITE_RX.search(rs.lower()))
    if own:
        # the result sentence states its own component set (one component = a component-only result;
        # "the second primary outcome (total heart failure hospitalizations) occurred ..." = that
        # component): the sentence is its own definition span
        return {"binding": BINDING_SELF, "endpoint_result_span": rs,
                "endpoint_definition_span": rs, "components": own,
                "binding_reason": "result sentence names its own component set: " + ", ".join(sorted(own))}
    if names_endpoint:
        defs = _definition_sentences(abstract)
        rl = rs.lower()
        wants_mace = bool(_MACE_RX.search(rl))
        q = _QUALIFIER_RX.search(rl)
        wants_secondary = bool(q and q.group("sec"))
        wants_primary = (not wants_secondary) and (bool(extract._ANCHOR_RX.search(rl)) or "primary composite" in rl)
        pool = defs
        if wants_mace:
            pool = [d for d in defs if d["mace"]]
        elif wants_secondary:
            pool = [d for d in defs if d["secondary"]]
        elif wants_primary:
            pool = [d for d in defs if d["primary"] and not d["secondary"]]
        if not pool and (wants_mace or wants_secondary or wants_primary):
            # the result names a specific endpoint and the held text defines no such endpoint: UNBOUND. The
            # earlier fallback to ALL definitions bound STRENGTH's "primary end point" result to a CONCLUSIONS
            # sentence naming MACE (served 237e9094 as EXACT 3-point while the abstract's primary measure is a
            # 5-point composite) and ORIGIN's "major vascular events" result to the CV-death primary.
            return {"binding": BINDING_NONE, "endpoint_result_span": rs,
                    "endpoint_definition_span": None, "components": set(),
                    "binding_reason": "named endpoint has no definition span in the held text"}
        if not pool:
            return {"binding": BINDING_NONE, "endpoint_result_span": rs,
                    "endpoint_definition_span": None, "components": set(),
                    "binding_reason": ("result sentence names an endpoint but the held text holds no "
                                       "definition span enumerating its components")}
        # RESOLVE THE REFERENCE FIRST, THEN COMPARE COMPONENTS (audit 2026-09-20): which defined endpoint does the
        # result refer to? Two definitions with identical event names can be different endpoints (30 days vs 36
        # months; all randomised vs >= 65 years); the ordinal / timepoint / population the result names decides,
        # never the sentence order, and an unresolved reference is an explicit ambiguity, never 'the first one'.
        res = _resolve_reference(rs, pool)
        rec = res["record"]
        if res["selected"] is not None:
            d = res["selected"]
            n = len(rec["definition_candidates"])
            by = (" by " + " + ".join(res["how"])) if res["how"] else ""
            return {"binding": BINDING_DEFINITION, "endpoint_result_span": rs,
                    "endpoint_definition_span": d.get("segment") or d["span"], "components": set(d["components"]),
                    "binding_reason": (f"result sentence names an endpoint; {n} candidate definition"
                                       f"{'s' if n != 1 else ''} in the held text; selected{by}"),
                    **rec}
        n = len(rec["unresolved_alternatives"])
        return {"binding": BINDING_NONE, "endpoint_result_span": rs,
                "endpoint_definition_span": None, "components": set(),
                "binding_reason": (f"result sentence names an endpoint but the held text holds {n} candidate "
                                   "definitions and the result's reference does not resolve which one "
                                   "(ambiguity abstains; the candidates are listed)"),
                **rec}
    return {"binding": BINDING_NONE, "endpoint_result_span": rs,
            "endpoint_definition_span": None, "components": set(),
            "binding_reason": "result sentence names neither components nor an endpoint"}


def _unbound_classification(binding: dict[str, Any]) -> dict[str, Any]:
    return {
        "target_endpoint_class": ENDPOINT_UNBOUND,
        "target_components": [],
        "extra_components": [],
        "missing_components": [],
        "component_distance": 999,
        "endpoint_binding": binding.get("binding", BINDING_NONE),
        "endpoint_result_span": binding.get("endpoint_result_span"),
        "endpoint_definition_span": binding.get("endpoint_definition_span"),
        "endpoint_binding_reason": binding.get("binding_reason"),
        **{k: binding[k] for k in ("definition_candidates", "endpoint_reference", "unresolved_alternatives") if k in binding},
    }


def classify_bound(spec: dict[str, Any], abstract: str, source: str | None) -> dict[str, Any]:
    """Classify ONE extracted row against the target from its own bound definition span."""
    binding = bind_result_span(abstract, _result_sentence(abstract, source))
    if binding["binding"] == BINDING_NONE:
        return _unbound_classification(binding)
    cls = _classify(spec, binding["endpoint_definition_span"], components=binding["components"],
                    excluded=binding.get("excluded_components"), result_span=binding.get("endpoint_result_span"))
    cls.update({
        "endpoint_binding": binding["binding"],
        "endpoint_result_span": binding["endpoint_result_span"],
        "endpoint_definition_span": binding["endpoint_definition_span"],
        "endpoint_binding_reason": binding["binding_reason"],
    })
    return cls


def _num_forms(value) -> set[str]:
    f = float(value)
    return {f"{f:g}", f"{f:.1f}", f"{f:.2f}", f"{f:.3f}"}


def locate_verified_result_sentence(abstract: str, row: dict[str, Any]) -> str | None:
    """The ONE abstract sentence that carries a hand-verified row's own effect and both CI bounds.

    A verified row's `source` is a hand-written description ("SOUL (...) abstract: primary MACE (...) 579/4825
    vs 668/4825, hazard ratio, 0.86; ...") that the sentence locator cannot find verbatim; the row is nevertheless
    a claim about held text, so it is located by its NUMBERS: exactly one sentence must carry the estimate and both
    bounds inside an effect+CI pattern. None when no sentence or several do (never a guess)."""
    if row.get("effect") is None or row.get("ci_low") is None or row.get("ci_high") is None:
        return None
    want = (_num_forms(row["effect"]), _num_forms(row["ci_low"]), _num_forms(row["ci_high"]))
    hits = []
    for sent in extract._sentences(extract._norm(abstract or "")):
        for m in _EFFECT_RE.finditer(sent):
            if m.group(2) in want[0] and m.group(3) in want[1] and m.group(4) in want[2]:
                hits.append(sent.strip())
                break
    return hits[0] if len(hits) == 1 else None


def bind_verified_row(spec: dict[str, Any], abstract: str, row: dict[str, Any]) -> dict[str, Any]:
    """Bring a hand-verified row inside the endpoint-binding safeguard.

    The served glp1 page pooled SOUL as `UNBOUND_LEGACY` while marked verified, with `provenance:
    fulltext_verified` although the cited passage was the abstract (Mahmood's review of 98726cc1, item 2). The
    row's own numbers locate its result sentence in the held abstract; the sentence binds to its definition span
    and is classified like every other route. Returns the classification (ENDPOINT_UNBOUND with a reason when the
    numbers are not in the abstract -- a genuinely full-text-only verification) plus `passage_location`:
    'abstract' or 'not_in_abstract'."""
    sentence = locate_verified_result_sentence(abstract, row)
    if not sentence:
        out = _unbound_classification({"binding": BINDING_NONE, "endpoint_result_span": None,
                                       "endpoint_definition_span": None, "components": set(),
                                       "binding_reason": "verified numbers not located in the held abstract"})
        out["passage_location"] = "not_in_abstract"
        return out
    binding = bind_result_span(abstract, sentence)
    if binding["binding"] == BINDING_NONE:
        out = _unbound_classification(binding)
        out["passage_location"] = "abstract"
        return out
    cls = _classify(spec, binding["endpoint_definition_span"], components=binding["components"],
                    excluded=binding.get("excluded_components"), result_span=binding.get("endpoint_result_span"))
    cls.update({
        "endpoint_binding": binding["binding"],
        "endpoint_result_span": binding["endpoint_result_span"],
        "endpoint_definition_span": binding["endpoint_definition_span"],
        "endpoint_binding_reason": binding["binding_reason"],
        "passage_location": "abstract",
    })
    return cls


def near_match_declared(spec: dict[str, Any]) -> bool:
    """A near match (a SUPERSET composite) is admissible only under an explicit declaration on the
    outcome: `allow_near_match: true`, or `component_compat_key: true` (the protocol pools each trial's
    own composite definition and discloses the component sets as a compatibility dimension, e.g. the
    pcsk9 protocol's 'MACE, as defined by each trial').  glp1-ra-mace-t2d declares neither."""
    return bool(spec.get("allow_near_match") or spec.get("component_compat_key"))


def _class_verdict(spec: dict[str, Any], cls: str | None, extra, missing, name: str, binding_reason=None) -> dict[str, Any]:
    if cls == EXACT_TARGET:
        return {"admissible": True, "verdict": "EXACT_TARGET"}
    if cls == NEAR_MATCH:
        extra = list(extra or [])
        missing = list(missing or [])
        if near_match_declared(spec) and not missing:
            return {"admissible": True, "verdict": "NEAR_MATCH_DECLARED",
                    "reason": ("near match (superset composite) admitted by the outcome's explicit declaration "
                               "(allow_near_match / component_compat_key); extra components: " + ", ".join(extra))}
        if missing:
            return {"admissible": False, "verdict": "RESULT_INCOMPATIBLE",
                    "reason": (f"the bound endpoint span lacks component(s) of the declared composite "
                               f"({', '.join(missing)}): a component or subset result is not the composite "
                               f"'{name}'; refused rather than pooled under the composite label")}
        return {"admissible": False, "verdict": "RESULT_INCOMPATIBLE",
                "reason": (f"the bound endpoint span adds component(s) to the declared composite "
                           f"({', '.join(extra)}): a different composite is not '{name}' and this outcome "
                           f"declares no near-match permission (allow_near_match / component_compat_key); "
                           f"refused rather than pooled under the declared label")}
    if cls == DIFFERENT_OUTCOME:
        return {"admissible": False, "verdict": "RESULT_INCOMPATIBLE",
                "reason": f"the bound endpoint span defines a different outcome from '{name}'"}
    if cls == COMPOSITE_DECLARATION_INCOMPLETE:
        return {"admissible": False, "verdict": COMPOSITE_DECLARATION_INCOMPLETE,
                "reason": (composite_declaration_problem(spec) or "composite declaration incomplete") +
                          " -- a component result cannot be told from the composite until the composite is declared"}
    if cls == ENDPOINT_COMPONENT_EXCLUDED:
        return {"admissible": False, "verdict": ENDPOINT_COMPONENT_EXCLUDED,
                "reason": (f"the bound endpoint EXCLUDES a component of '{name}' (an exclusion scope or statement in the "
                           "definition, the result span or their document neighbourhood); mentioning what is excluded "
                           "does not include it -- refused rather than pooled under the composite label")}
    if cls == EVENT_PROCESS_MISMATCH:
        return {"admissible": False, "verdict": EVENT_PROCESS_MISMATCH,
                "reason": (f"the bound result counts a different event process from '{name}' (first event vs total / "
                           "recurrent events, or patients with an event vs event counts); a total-event ratio is not a "
                           "first-event result -- refused rather than pooled under the target label")}
    if cls == ENDPOINT_UNBOUND:
        return {"admissible": False, "verdict": "ENDPOINT_UNBOUND",
                "reason": ("the extracted number could not be bound to an endpoint-definition span in the held "
                           "text (" + str(binding_reason or "no binding") + "); a number without a bound "
                           "endpoint is not evidence for '" + name + "'")}
    return {"admissible": None, "verdict": "UNCLASSIFIED"}


def admissibility(spec: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    """The ONE mandatory admissibility verdict every extraction route must pass before a row is pooled.

    EXACT_TARGET -> admissible.  NEAR_MATCH -> admissible only under the outcome's explicit declaration
    (`near_match_declared`) AND with no MISSING component (a superset composite may be disclosed; a
    component or subset is never the composite).  DIFFERENT_OUTCOME / ENDPOINT_UNBOUND -> refused.
    Rows with no class (routes that never classified: hand-verified, registry fallback, full text,
    dose rule) keep the conservative composite-mismatch check and carry `endpoint_binding:
    unbound_legacy` so a reader can see that no span binding exists (the pre-existing state, now
    labelled; binding those rows to held bytes is the FACT-object landing, not this one)."""
    cls = row.get("target_endpoint_class")
    name = spec.get("name", "")
    # Arithmetic impossibility needs no document: a point estimate outside its own interval is not a result
    # (M2: 0.68 (0.77-0.96) was pooled with  on the served release).
    if all(row.get(k) is not None for k in ("effect", "ci_low", "ci_high")):
        try:
            _e, _lo, _hi = float(row["effect"]), float(row["ci_low"]), float(row["ci_high"])
        except (TypeError, ValueError):
            _e = _lo = _hi = None
        if _e is not None and not (min(_lo, _hi) <= _e <= max(_lo, _hi)):
            return {"admissible": False, "verdict": "RESULT_INCOMPATIBLE",
                    "reason": f"point estimate {_e:g} lies outside its own interval ({_lo:g}-{_hi:g}); not a result"}
    # A HAND ROW is bound by the hand binder whatever an earlier route wrote in its class field: the abstract
    # route matches digits and resolves the endpoint, it does not check the declared scale / CI level /
    # direction / analysis set, so returning on its class let SOUL pool as an OR (M2 W1b, both trees).
    if cls in (EXACT_TARGET, NEAR_MATCH, DIFFERENT_OUTCOME, ENDPOINT_UNBOUND, ENDPOINT_COMPONENT_EXCLUDED,
               COMPOSITE_DECLARATION_INCOMPLETE, EVENT_PROCESS_MISMATCH) and not hand_binding.is_hand_row(row):
        return _class_verdict(spec, cls,
                              row.get("target_endpoint_extra_components") or row.get("extra_components"),
                              row.get("target_endpoint_missing_components") or row.get("missing_components"),
                              name, row.get("endpoint_binding_reason"))
    # HAND-EXTRACTED ROW (verified_effects / verified_arms, any override route): bound to the HELD BYTES its
    # document_ref names, or ABSTAIN. Never the  string, never UNBOUND_LEGACY (M2, 2026-09-20: a gate
    # whose failure mode is "admit" rewards exactly the input it exists to stop -- a wrong tuple broke the abstract
    # binding and the row was admitted because it no longer matched).
    if hand_binding.is_hand_row(row):
        bound = hand_binding.bind_hand_row(spec, row)
        row.update(bound)
        if bound.get("direction_conflict"):
            return {"admissible": False, "verdict": "RESULT_INCOMPATIBLE", "reason": bound["direction_conflict"]}
        if bound["target_endpoint_class"] == ENDPOINT_UNBOUND:
            return {"admissible": False, "verdict": ENDPOINT_UNBOUND, "abstain": True,
                    "candidate_locations": bound.get("candidate_locations") or [],
                    "reason": ("the hand-extracted number is not bound to an endpoint in the held document ("
                               + str(bound.get("endpoint_binding_reason")) + "); the candidate extraction is set aside "
                               "for review -- the trial stays eligible evidence awaiting adjudication")}
        return _class_verdict(spec, bound["target_endpoint_class"], bound.get("extra_components"),
                              bound.get("missing_components"), name, bound.get("endpoint_binding_reason"))
    # A route that never classified (hand-verified effect/arms, override, dose rule, registry or
    # full-text fallback): its `source` is a hand-written DESCRIPTION, not a definition span, and
    # classifying prose that explains an override (ORIGIN: "...the abstract's stated PRIMARY outcome is
    # death from cardiovascular causes...") as if it enumerated the endpoint would repeat the defect
    # in the other direction. Such rows keep the conservative composite-mismatch check (an explicit
    # 3-point label against an explicit extra-component keyword in a composite clause) and are
    # LABELLED unbound_legacy on the page; binding them to held bytes is the FACT-object landing.
    mm = extract.composite_component_mismatch(name, row.get("source") or "")
    if mm:
        return {"admissible": False, "verdict": "RESULT_INCOMPATIBLE", "reason": mm}
    return {"admissible": True, "verdict": "UNBOUND_LEGACY", "endpoint_binding": "unbound_legacy"}


def admit_rows(spec: dict[str, Any], trials: list[dict[str, Any]]):
    """Apply `admissibility` to every pooled row (after EVERY route); return (kept, refused)."""
    kept, refused = [], []
    for t in trials:
        v = admissibility(spec, t)
        t["endpoint_admissibility"] = v["verdict"]
        if v.get("endpoint_binding") and not t.get("endpoint_binding"):
            t["endpoint_binding"] = v["endpoint_binding"]
        if v.get("endpoint_definition_span") and not t.get("endpoint_definition_span"):
            t["endpoint_definition_span"] = v["endpoint_definition_span"]
        if v["admissible"]:
            kept.append(t)
            continue
        if v.get("abstain"):
            # ABSTAIN: not pooled, not refused on evidence -- the candidate extraction is set aside and the trial
            # stays visible as eligible evidence awaiting adjudication (existing states: machine_absent /
            # EXTRACTION_DEBT / ENDPOINT_UNBOUND; no new vocabulary).
            refused.append({
                "label": t.get("label"), "id": t.get("id"), "absent_kind": "machine_absent",
                "state": "EXTRACTION_DEBT", "reason_code": ENDPOINT_UNBOUND,
                "endpoint_admissibility": ENDPOINT_UNBOUND, "hand_binding_state": t.get("hand_binding_state"),
                "endpoint_binding": t.get("endpoint_binding"), "endpoint_binding_reason": t.get("endpoint_binding_reason"),
                "endpoint_result_span": t.get("endpoint_result_span"), "held_document": t.get("held_document"),
                "candidate_locations": v.get("candidate_locations") or [],
                "candidate_tuple": {k: t.get(k) for k in ("effect", "ci_low", "ci_high", "scale", "ai", "n1i", "ci", "n2i",
                                                          "mean1", "sd1", "nc1", "mean2", "sd2", "nc2")
                                    if t.get(k) is not None},
                "refused_effect": {k: t.get(k) for k in ("effect", "ci_low", "ci_high", "scale", "ai", "n1i", "ci", "n2i",
                                                         "mean1", "sd1", "nc1", "mean2", "sd2", "nc2")
                                   if t.get(k) is not None},
                "source": t.get("source", ""), "provenance": t.get("provenance"),
                "reason": v["reason"],
                "recovery": "a reviewer binds the tuple to one span of the held document (or records a typed refusal "
                            "with the span) -- recorded, source-linked, under the same numeric and freshness checks",
            })
            continue
        refused.append({
            "label": t.get("label"), "id": t.get("id"), "absent_kind": "refused_on_evidence",
            "state": "REFUSED_ON_EVIDENCE", "reason_code": v["verdict"],
            "endpoint_admissibility": v["verdict"],
            "endpoint_binding": t.get("endpoint_binding"),
            "endpoint_result_span": t.get("endpoint_result_span"),
            "endpoint_definition_span": t.get("endpoint_definition_span"),
            "target_endpoint_class": t.get("target_endpoint_class"),
            "refused_effect": {k: t.get(k) for k in ("effect", "ci_low", "ci_high", "scale", "ai", "n1i", "ci", "n2i")
                               if t.get(k) is not None},
            "source": t.get("source", ""), "provenance": t.get("provenance"),
            "reason": v["reason"],
        })
    return kept, refused


def canonical_components(spec: dict[str, Any]) -> list[str]:
    if str(spec.get("name") or "").strip().lower().startswith("trial-defined"):
        # the outcome is declared as EACH TRIAL'S OWN composite (e.g. sglt2-ckd-progression's
        # 'Trial-defined primary cardiorenal composite'): there is no canonical component set to
        # match against, so classification falls back to the outcome-family keyword match.
        return []
    explicit = spec.get("components") or spec.get("canonical_components")
    if explicit:
        # each DECLARED component survives: read item by item, the literal item when the vocabulary does not know its
        # phrasing ('urgent heart failure visit' vanished when the joined list was read and something else matched)
        out: set[str] = set()
        for x in explicit:
            out |= _components_from_text(str(x)) or {str(x)}
        return sorted(out)
    return sorted(_components_from_text(spec.get("name")))


def optional_components(spec: dict[str, Any]) -> set[str]:
    """Components the protocol makes part of the composite only 'as defined by the trial' (declared
    `optional_components`, with its basis): a result that includes one is not a superset, a result without one is not
    missing anything. Every REQUIRED component still has to be there."""
    out: set[str] = set()
    for x in spec.get("optional_components") or []:
        out |= _components_from_text(str(x)) or {str(x)}
    return out - set(canonical_components(spec))


# ---- the composite's declaration must account for its title ---------------------------------------------------------
COMPOSITE_DECLARATION_INCOMPLETE = "COMPOSITE_DECLARATION_INCOMPLETE"
# title vocabulary ONLY (not the general reader, where trials define these differently): what a composite TITLE names
_WORSENING_HF = re.compile(r"\bworsening\s+(?:heart\s+failure|hf)\b", re.I)   # named: a stable regex-inventory key
_TITLE_TERMS = ((_WORSENING_HF, {"heart failure hospitalization", "urgent heart failure visit"}),)


def title_components(name: str | None) -> set[str]:
    comps = set(_mentions_from_text(name))
    for rx, add in _TITLE_TERMS:
        if rx.search(name or ""):
            comps |= add
    return comps


def composite_declaration_problem(spec: dict[str, Any], text: str | None = None) -> str | None:
    """None when the outcome's canonical components (declared, or read from its title) account for every component its
    TITLE names; else why not. DELIVER: 'Composite cardiovascular death or worsening heart failure' declared no
    components, so the canonical set was the vocabulary's reading of the title -- {cardiovascular death} -- and a
    cardiovascular-death-only result matched the composite exactly (HR 0.88 served for 0.82). A composite that cannot
    say what it contains cannot be matched: its rows are refused until it is declared."""
    name = str(spec.get("name") or "")
    if name.strip().lower().startswith("trial-defined"):
        return None
    title = title_components(name)
    if len(title) < 2 and not extract.declared_is_composite(name) and not _title_parts(name):
        return None
    canon = set(canonical_components(spec))
    missing = sorted(title - canon - optional_components(spec))
    if missing:
        return (f"{COMPOSITE_DECLARATION_INCOMPLETE}: the title '{name}' names {sorted(title)} but the "
                f"{'declared' if spec.get('components') or spec.get('canonical_components') else 'title-derived'} "
                f"components are {sorted(canon)} (missing {missing}); declare the composite's components")
    # every top-level PART of the title must be accounted for, including a part the vocabulary cannot read ('...
    # cardiovascular death or all-cause hospitalization' with only cardiovascular death declared; NR-C04 #6): an unknown
    # part is not an absent part. Such a part is accounted for by a declared component, or -- for ONE row -- by that row's
    # own text naming it ('stroke or systemic embolism ... HR 0.79' is the composite; 'stroke ... HR 0.70' is not).
    # Only when the vocabulary reads SOME part: that partial reading is what lets a component row match the composite
    # exactly. A title it cannot read at all ('Gynecomastia or breast pain') is matched by keyword family, not components.
    if not canon:
        return None
    declared = [_part_words(str(c)) for c in list(spec.get("components") or spec.get("canonical_components") or [])
                + list(spec.get("optional_components") or [])]
    optional = [_part_words(str(c)) for c in spec.get("optional_components") or []]
    row = _part_words(text) if text is not None else None
    unassessed = [
        _part_words(m.group(1))
        for m in re.finditer(
            r"([^.;,]+?)\s+(?:was|were|is|are)\s+not\s+(?:assessed|reported|measured|evaluated|collected)\b",
            text or "", re.I)
    ]
    unread = []
    for part in _title_parts(name):
        words = _part_words(part) - _PART_STOP
        if words and any(words <= subject for subject in unassessed) and not any(words <= o for o in optional):
            return f"{COMPOSITE_DECLARATION_INCOMPLETE}: the row does not assess/report '{part.strip()}'"
        pc = title_components(_unhyphen(part))
        if pc and pc <= canon | optional_components(spec):
            continue
        words = _part_words(part) - _PART_STOP
        if not words or any(words <= d for d in declared) or (row is not None and _row_names_part(words, text or "")):
            continue
        unread.append(part.strip())
    if unread:
        return (f"{COMPOSITE_DECLARATION_INCOMPLETE}: the title '{name}' has part(s) {unread} that no declared component "
                f"{'or the row itself ' if text is not None else ''}accounts for (components {sorted(canon)}); declare "
                f"the composite's components")
    return None


_PART_STOP = {"the", "composite", "any", "first", "occurrence", "time", "rate", "incidence", "total", "combined", "endpoint",
              "outcome", "event", "events", "from", "for", "with"}


def _unhyphen(s: str | None) -> str:
    return re.sub(r"(?<=[A-Za-z])-(?=[A-Za-z])", " ", s or "")


def _part_words(s: str | None) -> set[str]:
    return set(re.findall(r"[a-z][a-z0-9]{2,}", extract.lexicon.fold(_unhyphen(s))))


def _row_names_part(words: set[str], text: str) -> bool:
    """The row's own text names a title part: every part word by its stem ('embolism' ~ 'embolic'), or the part's
    abbreviation as the text writes it ('systemic embolism' -> 'SE' / 'SEE', systemic embolic event: 'Stroke/SEE'; lane
    NR rebuild diff -- 55 NOAC registry measures were refused for writing the part as its abbreviation)."""
    row = _part_words(text)
    if all(any(r.startswith(w[:6]) for r in row) for w in words):
        return True
    ordered = [w for w in re.findall(r"[a-z][a-z0-9]{2,}", extract.lexicon.fold(" ".join(sorted(words))))]
    initials = "".join(w[0] for w in ordered)
    if len(words) >= 2:
        acro = [a.lower() for a in re.findall(r"\b[A-Z]{2,5}\b", text or "")]
        for a in acro:
            # the part's initials in either order, optionally followed by 'e' (event): SE / SEE
            one_less = a[:-1] if a.endswith("e") else a
            if sorted(one_less) == sorted(initials) or sorted(a) == sorted(initials):
                return True
    return False


def _title_parts(name: str) -> list[str]:
    """Top-level parts of a composite title, after dropping a leading 'composite (of)'. Parts are split on ',', ' or ',
    ' and '. A parenthetical that ENUMERATES (two or more parts, '/' allowed inside it) is the part list and its head is
    the umbrella label ('Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death)'). A top-level '/'
    joins synonymous labels only when both sides name the same endpoint."""
    s = re.sub(r"^\s*(?:a\s+|the\s+)?composite(?:\s+(?:end\s*point|endpoint|outcome))?(?:\s+of)?\s*[:,]?\s*", "",
               name or "", flags=re.I)
    def split(t: str, rx: str) -> list[str]:
        return [p for p in re.split(rx, t, flags=re.I) if p.strip()]
    top = r"\s*,\s*(?:or\s+|and\s+)?|\s+or\s+|\s+and\s+"
    def readable(part: str) -> bool:
        return bool(title_components(part) or re.search(
            r"\b(?:hospitali[sz]ation|embolism|DVT|PE|VTE|death|mortality)\b", part, re.I))
    for inner in re.findall(r"\(([^()]*)\)", s):
        parts = split(inner, top + r"|\s*/\s*")
        outer = re.sub(r"\([^()]*\)", " ", s)
        if (len(parts) >= 2 and all(readable(p) for p in parts)
                and len(split(outer, top + r"|\s*/\s*")) == 1):
            return parts
    s = re.sub(r"\([^()]*\)", " ", s)
    slash = split(s, r"\s*/\s*")
    if len(slash) >= 2 and all(readable(p) for p in slash):
        meanings = [title_components(p) for p in slash]
        if not (meanings[0] and all(c == meanings[0] for c in meanings)):
            top += r"|\s*/\s*"
    parts = split(s, top)
    return parts if len(parts) >= 2 else []


# ---- a REGISTRY outcome is the target only when population, comparison, outcome AND timepoint agree ------------------
_MORTALITY = re.compile(r"\b(?:mortality|death|deaths|died|dying|dead|fatal|surviv\w*)\b", re.I)
_NOT_DEATH = re.compile(r"\bdischarge[ds]?\s+alive\b|\balive\s+(?:and\s+)?(?:out\s+of|discharged)|\btime\s+to\s+discharge\b|"
                        r"\bdays\s+alive\b", re.I)
_GENERIC_PREFIX = re.compile(r"\b(?:co-?primary|primary|secondary|key|main|outcome|outcomes|end\s*points?|endpoint|"
                             r"analysis|efficacy|safety|part|stage|phase|measure|[ivx]+|[a-z])\b", re.I)
_COMPARISON_PREFIX = re.compile(r"\b(?:comparison|arm|versus|vs\.?|randomi[sz]ation)\b", re.I)
_UNIT_DAYS = {"day": 1, "week": 7, "month": 30.4, "year": 365.25}
_WINDOW = re.compile(r"(\d+(?:\.\d+)?)\s*(?:-|to|–)\s*(\d+(?:\.\d+)?)[\s-]*(day|week|month|year)s?\b"
                     r"|\bday[\s-]+(\d+)\b|\bweek[\s-]+(\d+)\b"
                     r"|(\d+(?:\.\d+)?)[\s-]*(day|week|month|year)s?\b", re.I)
_OPEN_ENDED = re.compile(r"\b(?:trial\s+end|study\s+end|end\s+of\s+(?:treatment|study|trial)|longest|trial[\s-]reported|"
                         r"symptom\s+resolution)\b", re.I)
_IN_HOSPITAL = re.compile(r"\bin[\s-]hospital\b|\bhospital\s+discharge\b|\b(?:until|to|at)\s+(?:the\s+)?(?:date\s+of\s+)?"
                          r"(?:hospital\s+)?discharge\b|\bduring\s+hospitali[sz]ation\b", re.I)


def _windows(text: str | None) -> tuple[list[tuple[float, float]], bool]:
    """([(lo_days, hi_days), ...], in_hospital) stated by a timepoint text."""
    out = []
    text = re.sub(r"\b(day|week|month|year)s?[\s-]+(\d+(?:\.\d+)?)\b",
                  r"\2 \1", text or "", flags=re.I)
    for m in _WINDOW.finditer(text):
        if m.group(1):
            f = _UNIT_DAYS[m.group(3).lower()]
            out.append((float(m.group(1)) * f, float(m.group(2)) * f))
        elif m.group(4):
            out.append((float(m.group(4)),) * 2)
        elif m.group(5):
            out.append((float(m.group(5)) * 7,) * 2)
        else:
            v = float(m.group(6)) * _UNIT_DAYS[m.group(7).lower()]
            out.append((v, v))
    return out, bool(_IN_HOSPITAL.search(text)) and "discharge" not in _anchors(text)


def _timepoint_agreement(target: str | None, stated: str | None) -> str:
    """AGREE / CONFLICT / UNCONFIRMED / NOT_DEMANDED. Numeric window ends must agree (the 28-vs-30-day
    convention is the same window: +/-10%); an open-ended target ('trial end / longest follow-up') demands nothing."""
    tw, th = _windows(target)
    if not tw and not th or (_OPEN_ENDED.search(target or "") and not tw):
        return "NOT_DEMANDED"
    sw, sh = _windows(stated)
    if not sw and not sh:
        return "UNCONFIRMED"
    ta, sa = _anchors(target), _anchors(stated)
    if ta and sa and not (ta & sa):
        # both state what the clock starts from and they differ: 28 days after DISCHARGE is not 28 days after
        # RANDOMIZATION (NR-C04 #10)
        return "CONFLICT"
    if (th and "discharge" in sa) or (sh and "discharge" in ta):
        return "CONFLICT"
    if th and sh:
        return "AGREE"
    if not tw or not sw:
        # an in-hospital window against a numeric one (or the reverse) cannot be compared: not a conflict, not agreement
        return "UNCONFIRMED"
    for lo, hi in tw:
        for slo, shi in sw:
            # the stated window must END where the target's does (28-vs-30-day convention: +/-10%); a cumulative window that
            # merely CONTAINS day 28 ('0-90 days') is not mortality at day 28 (NR-C04 #15)
            # A target RANGE that starts above zero ('28-90 day or in-hospital') is the set of ACCEPTABLE timepoints: any
            # stated end inside it agrees (28-day mortality for balanced-crystalloids; lane NR rebuild diff), while a range
            # from zero ('0-90 days') is one cumulative window and must end where it ends (NR-C07 #6)
            if (lo > 0 and lo * 0.9 <= shi <= hi * 1.1) or hi * 0.9 <= shi <= hi * 1.1:
                return "AGREE"
    return "CONFLICT"


_ANCHOR_RX = re.compile(r"\b(?:after|following|from|since)\s+(?:the\s+)?(?:date\s+of\s+)?(?:hospital\s+)?(randomi[sz]ation|discharge|"
                        r"surgery|operation|enrol\w*|admission|delivery|birth|diagnosis|index\s+event)\b|"
                        r"\bpost[\s-]?(discharge|randomi[sz]ation|operative|surgery)\b", re.I)


def _anchors(text: str | None) -> set[str]:
    out = set()
    for m in _ANCHOR_RX.finditer(text or ""):
        a = (m.group(1) or m.group(2) or "").lower()
        a = ("randomization" if a.startswith("randomi") else "enrolment" if a.startswith("enrol") else
             "surgery" if a in ("operation", "operative") else a)
        out.add(a)
    return out


# a population the topic EXCLUDES, named positively in a measure: in its label, in AACT's population field, or in a
# population phrase of its body ('... in patients with influenza'); a negated mention ('without influenza') is not one
_POP_PHRASE = re.compile(r"\b(?:in|among|for)\s+(?:patients?|participants?|subjects?|adults?|children|people|those|"
                         r"individuals?|women|men)\s+(?:with|who\s+have|hospitali[sz]ed\s+(?:with|for))\s+([^,;:()]{1,60})", re.I)
_NEGATED_BEFORE = re.compile(r"\b(?:without|excluding|excluded|no|non|not|neither|nor|other\s+than|except)\b[\s\w-]*$", re.I)


def _names_excluded_population(text: str, pop_none: list[str]) -> list[str]:
    hits = []
    for p in pop_none:
        for m in re.finditer(rf"\b{re.escape(p)}\b", text or "", re.I):
            phrase = re.split(r"[,;:.()]|\b(?:and\s+with|but)\b", (text or "")[:m.start()], flags=re.I)[-1]
            if not _NEGATED_BEFORE.search(phrase):
                hits.append(p)
                break
    return hits


_DEATH_OR = re.compile(r"\s+(?:or|and/or)\s+|\s*/\s*", re.I)
_TIME_OR_STOP = re.compile(r"\b(?:\d+|days?|weeks?|months?|years?|at|by|within|after|before|from|to|the|of|in|on|a|an|"
                           r"any|all|cause|causes|randomi[sz]ation|time|first|number|participants?|patients?|with|rate)\b", re.I)


def _death_composite(measure: str) -> bool:
    """'Death or invasive mechanical ventilation' is not all-cause mortality (NR-C04 #2): a part joined by 'or' that is an
    EVENT other than death makes the measure a composite."""
    core = re.sub(r"\([^)]*\)", " ", measure or "")
    parts = [p for p in _DEATH_OR.split(re.sub(r"\s+and\s+", " or ", core, flags=re.I)) if p.strip()]
    if len(parts) < 2:
        return False
    # a SETTING or a QUALIFIER of mortality is not a second event: 'ICU and hospital mortality', 'Cardiac and non-cardiac
    # mortality' are mortality measures, not death composites (lane NR rebuild diff: the 'and' rule of NR-C09 read them so)
    return any(not _MORTALITY.search(p)
               and re.search(r"[a-z]{3,}", _MORT_QUALIFIER.sub(" ", _TIME_OR_STOP.sub(" ", p.lower())))
               for p in parts)


_MORT_QUALIFIER = re.compile(r"\b(?:icu|intensive\s+care|hospital|in-hospital|ward|cardiac|non-?cardiac|cardiovascular|"
                             r"non-?cardiovascular|vascular|non-?vascular|sudden|overall|crude|total|clinical|outcomes?|"
                             r"endpoints?|all-cause|during|stay|and|or)\b", re.I)


def registry_outcome_match(spec: dict[str, Any], topic: dict[str, Any] | None, measure: str | None,
                           time_frame: str | None = None, population: str | None = None,
                           result_span: str | None = None) -> dict[str, Any]:
    """Classify a REGISTRY outcome (AACT design_outcomes / results title) against the target. EXACT_TARGET requires
    agreement on disease POPULATION, intervention COMPARISON, OUTCOME and TIMEPOINT; a shared platform identifier or a
    broad outcome category is never enough (RECOVERY NCT04381936: 'Influenza co-primary outcome: Time to discharge alive
    from hospital' was EXACT_TARGET for 28-day COVID-19 mortality). A conflicting dimension -> DIFFERENT_OUTCOME; a
    dimension the row cannot confirm -> NEAR_MATCH (never admitted as the target without a declaration)."""
    topic = topic or {}
    base = _classify(spec, measure, result_span=result_span)
    measure = str(measure or "")
    head, sep, body = measure.partition(":")
    label = head if sep and len(head) <= 80 else ""
    conflicts, unconfirmed, agrees, evidence = [], [], [], {}
    inc = topic.get("include") or {}
    pop_none = [p.lower() for p in (inc.get("population_none") or [])]
    pop_any = [p.lower() for p in list(inc.get("population_any") or []) + list(inc.get("population_any_extra") or [])]
    interv = [t.lower() for t in (topic.get("intervention_terms") or [])]
    # comparison: a label naming a comparison must name OUR intervention
    if label and _COMPARISON_PREFIX.search(label):
        evidence["comparison"] = label
        (agrees if any(t in label.lower() for t in interv) else conflicts).append("comparison")
    # population -- checked whatever the label is (a comparison prefix must not bypass it; NR-C04 #9). A conflict needs a
    # POSITIVE statement of a population the topic EXCLUDES (population_none: the COVID topics exclude influenza and
    # community-acquired pneumonia): in the label, in AACT's population field, or in a population phrase of the title body
    # ('All-cause mortality in patients with influenza'; NR-C04 #7). 'without influenza' is not one (NR-C04 #13). A title
    # prefix is not a disease stratum by itself ('Panel A and B:'), and AACT's population field otherwise describes the
    # ANALYSIS set, not the disease.
    lab = label.lower()
    body_pops = " ; ".join(m.group(0) for m in _POP_PHRASE.finditer(body if label else measure))
    hit = sorted(set(_names_excluded_population(lab, pop_none) + _names_excluded_population(population or "", pop_none)
                     + _names_excluded_population(body_pops, pop_none)))
    if hit:
        evidence["population"] = {"label": label or None, "aact_population": population, "excluded_population": hit}
        conflicts.append("population")
    elif label and not _COMPARISON_PREFIX.search(label) and any(p in lab for p in pop_any):
        evidence["population"] = {"label": label}
        agrees.append("population")
    # outcome: a MORTALITY target is matched only by a death outcome, never by 'discharge alive'. The target is a mortality
    # outcome by its NAME, and only when it is not a composite: MACE keywords mention death, and 'Major Adverse
    # Cardiovascular Events' is not a death outcome (read from the keywords, it failed every MACE registry measure).
    tname = str(spec.get("name") or "")
    if (_MORTALITY.search(tname) and not extract.declared_is_composite(tname)
            and len(title_components(tname) - {"cardiovascular death", "coronary heart disease death"}) == 0):
        evidence["outcome"] = body or measure
        if _NOT_DEATH.search(measure) or not _MORTALITY.search(measure) or _death_composite(body or measure):
            conflicts.append("outcome")
        else:
            agrees.append("outcome")
    # timepoint
    t = _timepoint_agreement(spec.get("timepoint"), " ".join(x for x in (measure, time_frame or "") if x))
    evidence["timepoint"] = {"target": spec.get("timepoint"), "time_frame": time_frame, "state": t}
    if t == "CONFLICT":
        conflicts.append("timepoint")
    elif t == "UNCONFIRMED":
        unconfirmed.append("timepoint")
    elif t == "AGREE":
        agrees.append("timepoint")
    cls = base["target_endpoint_class"]
    if cls == EXACT_TARGET and conflicts:
        cls = DIFFERENT_OUTCOME
    elif cls == EXACT_TARGET and unconfirmed:
        cls = NEAR_MATCH
    return {**base, "target_endpoint_class": cls,
            "registry_match": {"agrees": agrees, "conflicts": conflicts, "unconfirmed": unconfirmed,
                               "evidence": evidence, "base_class": base["target_endpoint_class"]}}


def _keyword_family_match(spec: dict[str, Any], text: str | None) -> bool:
    s = _fold(text)
    for kw in spec.get("keywords") or []:
        k = _fold(kw)
        if len(k) > 3 and k in s:
            return True
    canon = set(canonical_components(spec))
    return bool(canon and (canon & _components_from_text(text)))


def _classify(spec: dict[str, Any], text: str | None, components: set[str] | None = None,
              excluded: set[str] | None = None, result_span: str | None = None) -> dict[str, Any]:
    """Classify an endpoint against the target from its typed relations. `components` (INCLUDES) and `excluded`
    (EXCLUDES) come from the caller's binding when it has one; the relations of `text` itself are always added. A target
    component the endpoint EXCLUDES is ENDPOINT_COMPONENT_EXCLUDED -- never EXACT, whatever else the span names."""
    decl = composite_declaration_problem(spec, text)
    if decl:
        # the composite cannot say what it contains: nothing can be matched to it (fail closed until declared)
        return {"target_endpoint_class": COMPOSITE_DECLARATION_INCOMPLETE, "target_components": [],
                "extra_components": [], "missing_components": [], "component_distance": 999,
                "declaration_problem": decl}
    # the event process is read from the definition AND the row's own result span: the ESTIMATE's analysis method lives
    # in the result ('Hazard Ratio 1.0881 ... Regression, Cox'), a descriptive count in the definition ('n = Total number
    # of events'); read apart, the definition alone refused PARALLEL-HF's Cox HR as a total-event result
    evp = event_process_problem(spec, " ".join(x for x in (text, result_span) if x))
    if evp:
        # total (first and recurrent) events are not a first-event result, and event counts are not patients with an
        # event -- whatever components the span names (EMPEROR-Preserved: total HHF HR 0.73 vs the composite HR 0.79)
        return {"target_endpoint_class": EVENT_PROCESS_MISMATCH, "target_components": [], "extra_components": [],
                "missing_components": [], "component_distance": 999, "event_process": evp["result"],
                "target_event_process": evp["target"], "event_process_dimensions": evp["dimensions"]}
    canon = set(canonical_components(spec))
    rel = endpoint_relations(text)
    exc = set(excluded or ()) | rel["excludes"]
    cand = set(components or rel["includes"]) - exc
    if canon and (exc & canon):
        return {
            "target_endpoint_class": ENDPOINT_COMPONENT_EXCLUDED,
            "target_components": sorted(cand),
            "excluded_components": sorted(exc),
            "excluded_target_components": sorted(exc & canon),
            "exclusion_statements": rel["exclusion_statements"] or None,
            "extra_components": sorted(cand - canon),
            "missing_components": sorted(canon - cand),
            "component_distance": 999,
        }
    extra_rel = {"excluded_components": sorted(exc)} if exc else {}
    if not canon:
        cls = EXACT_TARGET if _keyword_family_match(spec, text) else DIFFERENT_OUTCOME
        return {
            "target_endpoint_class": cls,
            "target_components": sorted(cand),
            "extra_components": [],
            "missing_components": [],
            "component_distance": 0 if cls == EXACT_TARGET else 999,
            **extra_rel,
        }
    cand_for_match = set(cand)
    judgments = []
    if "cardiovascular death" in canon and "coronary heart disease death" in cand:
        cand_for_match.add("cardiovascular death")
        judgments.append({"target": "cardiovascular death", "trial": "coronary heart disease death",
                          "judgment": "CHD death accepted for the target's CV death (a narrower cause-specific death)"})
    if "stroke" in canon and "stroke" in cand and re.search(r"\b(?:ischa?emic|non-?ha?emorrhagic)\s+stroke", text or "", re.I) \
            and not re.search(r"(?<!ischemic )(?<!ischaemic )\b(?:any|all|fatal or nonfatal|nonfatal)?\s*stroke\b(?!\s*\()",
                              re.sub(r"\b(?:ischa?emic|non-?ha?emorrhagic)\s+stroke", " ", text or "", flags=re.I), re.I):
        judgments.append({"target": "stroke", "trial": "ischemic stroke",
                          "judgment": "ischemic stroke accepted for the target's stroke (all types)"})
    extra = sorted(
        c for c in (cand - canon - optional_components(spec))
        if not (c == "coronary heart disease death" and "cardiovascular death" in canon)
    )
    missing = sorted(canon - cand_for_match)
    if not extra and not missing:
        cls = EXACT_TARGET
    elif cand and (not missing or not extra):
        cls = NEAR_MATCH
    else:
        cls = DIFFERENT_OUTCOME
    if judgments:
        basis = ("the outcome's declared component compatibility (component_compat_key / allow_near_match)"
                 if near_match_declared(spec) else "the harness's standing CHD-death / CV-death equivalence")
        for j in judgments:
            j["basis"] = basis
        extra_rel = dict(extra_rel, compatibility_judgments=judgments)
    return {
        "target_endpoint_class": cls,
        "target_components": sorted(cand),
        "extra_components": extra,
        "missing_components": missing,
        "component_distance": len(extra) + len(missing),
        **extra_rel,
    }


def _effect_analysis(om: dict[str, Any]) -> dict[str, Any] | None:
    for a in om.get("analyses") or []:
        ptype = _fold(a.get("paramType"))
        scale = None
        if "hazard ratio" in ptype or re.search(r"\bhr\b", ptype):
            scale = "HR"
        elif "risk ratio" in ptype or re.search(r"\brr\b", ptype):
            scale = "RR"
        elif "odds ratio" in ptype or re.search(r"\bor\b", ptype):
            scale = "OR"
        if not scale:
            continue
        effect = _num(a.get("paramValue"))
        lo = _num(a.get("ciLowerLimit"))
        hi = _num(a.get("ciUpperLimit"))
        if effect is not None and lo is not None and hi is not None:
            # the registry's OWN rendering of this analysis, verbatim strings: this is the result span the
            # displayed number must be found in (a registry row's result span was the measure TITLE, which
            # carries no number -- REDUCE-IT on the served omega3 page at 237e9094, independent read)
            group = str(a.get("groupDescription") or "").strip()
            pct = str(a.get("ciPctValue") or "95").strip()
            analysis_span = (
                (f"{group}: " if group else "")
                + f"{a.get('paramType')} {a.get('paramValue')} ({pct}% CI {a.get('ciLowerLimit')} to "
                + f"{a.get('ciUpperLimit')}; {a.get('statisticalMethod') or 'method not stated'})"
            )
            return {
                "effect": effect,
                "ci_low": lo,
                "ci_high": hi,
                "scale": scale,
                "ci_pct": _num(pct),
                "analysis_method": a.get("statisticalMethod"),
                "analysis_param_type": a.get("paramType"),
                "analysis_span": analysis_span,
            }
    return None


_EFFECT_RE = re.compile(
    r"\b(hazard ratio|risk ratio|relative risk|odds ratio|hr|rr|or)\b"
    r"(?:\s+for\b[^,;()]*)?\s*[:,]?\s*"
    r"(\d+(?:\.\d+)?)\s*[,;]?\s*"
    r"95%\s*(?:confidence interval\s*)?(?:\[[A-Za-z]+\]\s*)?[:,]?\s*"
    r"(\d+(?:\.\d+)?)\s*(?:to|-|–)\s*(\d+(?:\.\d+)?)",
    re.I,
)


def _published_effect_from_abstract(
    spec: dict[str, Any],
    abstract: str,
    interv: list[str],
    comp: list[str],
) -> dict[str, Any] | None:
    """Parse source-reported effect+CI phrases the legacy extractor misses."""
    try:
        sents = extract._outcome_sentences(abstract, extract._effective_kws(abstract, spec.get("keywords") or []))
    except AttributeError:
        sents = re.split(r"(?<=[.?!])\s+", abstract or "")
    for s in sents:
        if not _keyword_family_match(spec, s):
            continue
        m = _EFFECT_RE.search(s)
        if not m:
            continue
        lab = m.group(1).lower()
        if lab in ("hazard ratio", "hr"):
            scale = "HR"
        elif lab in ("odds ratio", "or"):
            scale = "OR"
        else:
            scale = "RR"
        return {
            "effect": float(m.group(2)),
            "ci_low": float(m.group(3)),
            "ci_high": float(m.group(4)),
            "scale": scale,
            "source": "abstract source-reported effect (target endpoint): " + s.strip()[:220],
        }
    return None


def _counts_from_om(om: dict[str, Any], interv: list[str], comp: list[str]) -> dict[str, Any] | None:
    groups = om.get("groups") or []
    if len(groups) < 2:
        return None
    interv_gid, comp_gid = _classify_arms(groups, [_fold(x) for x in interv], [_fold(x) for x in comp])
    if not (interv_gid and comp_gid):
        return None
    classes = om.get("classes") or []
    if not (classes and classes[0].get("categories")):
        return None
    measurements = classes[0]["categories"][0].get("measurements") or []
    values = {m.get("groupId"): _num(m.get("value")) for m in measurements}
    denoms = {}
    for d in om.get("denoms") or []:
        for c in d.get("counts") or []:
            denoms[c.get("groupId")] = _num(c.get("value"))
    ai, n1i = values.get(interv_gid), denoms.get(interv_gid)
    ci, n2i = values.get(comp_gid), denoms.get(comp_gid)
    if None in (ai, n1i, ci, n2i):
        return None
    if not (0 <= ai <= n1i and 0 <= ci <= n2i and n1i > 0 and n2i > 0):
        return None
    gi = next((g.get("title") for g in groups if g.get("id") == interv_gid), "")
    gc = next((g.get("title") for g in groups if g.get("id") == comp_gid), "")
    return {
        "ai": int(ai),
        "n1i": int(n1i),
        "ci": int(ci),
        "n2i": int(n2i),
        "intervention_arm": gi,
        "comparator_arm": gc,
    }


def _candidate_from_abstract(
    ex: dict[str, Any],
    *,
    spec: dict[str, Any],
    abstract: str,
    source_kind: str,
    source_rank_kind: str,
    source_order: int,
) -> dict[str, Any] | None:
    if not ex or ex.get("absent"):
        return None
    if not (ex.get("effect") is not None or ex.get("ai") is not None):
        return None
    c = {
        "candidate_id": f"abstract:{source_kind}:{source_order}",
        "source_type": "abstract",
        "source_kind": source_kind,
        "source_rank_kind": source_rank_kind,
        "source_rank": SOURCE_RANK[source_rank_kind],
        "source_order": source_order,
        "source": ex.get("source"),
        "classification_text": abstract,
        "provenance": "abstract",
    }
    for k in ("effect", "ci_low", "ci_high", "scale", "ai", "n1i", "ci", "n2i"):
        if ex.get(k) is not None:
            c[k] = ex[k]
    c.update(classify_bound(spec, abstract, ex.get("source")))
    return c


def _ctgov_candidates(
    outcome_measures: list[dict[str, Any]] | None,
    spec: dict[str, Any],
    interv: list[str],
    comp: list[str],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for order, om in enumerate(outcome_measures or []):
        title = om.get("title") or ""
        desc = om.get("description") or ""
        text = " ".join(str(x or "") for x in (title, desc))
        if not _keyword_family_match(spec, text):
            continue
        counts = _counts_from_om(om, interv, comp)
        analysis = _effect_analysis(om)
        if not counts and not analysis:
            continue
        denom_units = "; ".join(d.get("units", "") for d in om.get("denoms", []) if d.get("units"))
        measure_type = _registry_measure_type(
            om,
            ((om.get("classes") or [{}])[0] or {}).get("title"),
            ((((om.get("classes") or [{}])[0] or {}).get("categories") or [{}])[0] or {}).get("measurements") or [],
            denom_units,
        )
        base = {
            "candidate_id": f"ctgov:{order}",
            "source_type": "ctgov_results",
            "registry_title": title,
            "registry_type": om.get("type"),
            "registry_param_type": om.get("paramType"),
            "registry_measure_type": measure_type,
            "registry_timeframe": om.get("timeFrame") or om.get("time_frame"),
            "source_order": order,
            "classification_text": text,
            "provenance": "ctgov_results",
        }
        # a registry measure is the target only when population, comparison, outcome AND timepoint agree
        base.update(registry_outcome_match(spec, {"intervention_terms": list(interv or [])}, text,
                                           time_frame=om.get("timeFrame") or om.get("time_frame"),
                                           population=om.get("populationDescription"),
                                           result_span=analysis["analysis_span"] if analysis else None))
        base.update({"endpoint_binding": BINDING_REGISTRY,
                     "endpoint_definition_span": text.strip(),
                     "endpoint_result_span": f"ClinicalTrials.gov outcome measure #{order}: {title}".strip(),
                     "endpoint_binding_reason": ("registry outcome measure title/description is the definition "
                                                 "span of its own result")})
        if analysis:
            c = dict(base)
            c.update(analysis)
            # the result span is the registry analysis itself (verbatim), not the measure title
            c["endpoint_result_span"] = f"{base['endpoint_result_span']} -- analysis: {analysis['analysis_span']}"
            c["source_kind"] = REGISTRY_PUBLISHED_EFFECT
            c["source_rank_kind"] = REGISTRY_PUBLISHED_EFFECT
            c["source_rank"] = SOURCE_RANK[REGISTRY_PUBLISHED_EFFECT]
            if counts and measure_type == "COUNT_OF_PARTICIPANTS":
                c["endpoint_counts"] = {k: counts[k] for k in ("ai", "n1i", "ci", "n2i")}
                count_txt = (
                    f"; endpoint counts {counts['ai']}/{counts['n1i']} ({counts['intervention_arm']}) "
                    f"vs {counts['ci']}/{counts['n2i']} ({counts['comparator_arm']})"
                )
            else:
                count_txt = ""
            c["source"] = (
                f"ClinicalTrials.gov results (structured target endpoint): outcome '{title[:100]}' "
                f"{c['scale']} {c['effect']:g} (95% CI {c['ci_low']:g} to {c['ci_high']:g})"
                f"{count_txt}"
            )
            out.append(c)
        if counts and measure_type == "COUNT_OF_PARTICIPANTS":
            c = dict(base)
            c.update({k: counts[k] for k in ("ai", "n1i", "ci", "n2i")})
            # a reconstruction's result span carries the registry counts it is derived from, verbatim
            c["endpoint_result_span"] = (
                f"{base['endpoint_result_span']} -- counts: {counts['ai']}/{counts['n1i']} ({counts['intervention_arm']}) "
                f"vs {counts['ci']}/{counts['n2i']} ({counts['comparator_arm']})"
            )
            c["source_kind"] = RECONSTRUCTION
            c["source_rank_kind"] = RECONSTRUCTION
            c["source_rank"] = SOURCE_RANK[RECONSTRUCTION]
            c["source"] = (
                f"ClinicalTrials.gov results (structured target endpoint): outcome '{title[:100]}' "
                f"COUNT_OF_PARTICIPANTS {counts['ai']}/{counts['n1i']} ({counts['intervention_arm']}) "
                f"vs {counts['ci']}/{counts['n2i']} ({counts['comparator_arm']})"
            )
            out.append(c)
    return out


def enumerate_candidates(
    spec: dict[str, Any],
    abstract: str | None,
    outcome_measures: list[dict[str, Any]] | None,
    interv: list[str],
    comp: list[str],
) -> list[dict[str, Any]]:
    abstract = abstract or ""
    dc = extract.declared_is_composite(spec.get("name", ""))
    candidates: list[dict[str, Any]] = []
    hr_ex = extract.extract_trial(abstract, spec.get("keywords") or [], interv, comp,
                                  declared_composite=dc, estimand="HR")
    parsed_effect = _published_effect_from_abstract(spec, abstract, interv, comp)
    if parsed_effect and (not hr_ex or hr_ex.get("effect") is None):
        hr_ex = parsed_effect
    c = _candidate_from_abstract(
        hr_ex,
        spec=spec,
        abstract=abstract,
        source_kind=PUBLISHED_TARGET_EFFECT,
        source_rank_kind=PUBLISHED_TARGET_EFFECT,
        source_order=0,
    )
    if c and c.get("effect") is not None:
        candidates.append(c)
    default_ex = extract.extract_trial(abstract, spec.get("keywords") or [], interv, comp,
                                       declared_composite=dc, estimand=spec.get("estimand"))
    rank = PUBLISHED_TARGET_EFFECT if default_ex.get("effect") is not None else RECONSTRUCTION
    c = _candidate_from_abstract(
        default_ex,
        spec=spec,
        abstract=abstract,
        source_kind=rank,
        source_rank_kind=rank,
        source_order=1,
    )
    if c:
        candidates.append(c)
    candidates.extend(_ctgov_candidates(outcome_measures, spec, interv, comp))

    deduped: list[dict[str, Any]] = []
    seen = set()
    for c in candidates:
        key = (
            c.get("source_type"), c.get("source_kind"), c.get("effect"), c.get("ci_low"),
            c.get("ci_high"), c.get("ai"), c.get("n1i"), c.get("ci"), c.get("n2i"),
            c.get("registry_title"),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)
    return deduped


def _selection_key(c: dict[str, Any]) -> tuple[int, int, int, int]:
    cls_score = 2 if c.get("target_endpoint_class") == EXACT_TARGET else 1
    return (
        cls_score,
        int(c.get("source_rank") or 0),
        -int(c.get("component_distance") or 0),
        -int(c.get("source_order") or 0),
    )


def _near_reason(c: dict[str, Any]) -> str:
    bits = []
    if c.get("extra_components"):
        bits.append("extra components: " + ", ".join(c["extra_components"]))
    if c.get("missing_components"):
        bits.append("missing components: " + ", ".join(c["missing_components"]))
    return "; ".join(bits) or "component set differs from the registered target"


def _public_candidate(c: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "candidate_id", "source_type", "source_kind", "registry_title", "registry_type",
        "target_endpoint_class", "extra_components", "missing_components", "source_rank_kind",
        "endpoint_binding", "endpoint_binding_reason",
    )
    return {k: c.get(k) for k in keys if c.get(k) not in (None, [], "")}


def row_from_candidate(c: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {
        "source": c.get("source"),
        "provenance": c.get("provenance"),
        "target_endpoint_class": c.get("target_endpoint_class"),
        "target_endpoint_source_rank": c.get("source_rank_kind"),
        "target_endpoint_components": c.get("target_components") or [],
        "components": c.get("target_components") or [],
        "target_endpoint_extra_components": c.get("extra_components") or [],
        "target_endpoint_missing_components": c.get("missing_components") or [],
        "results_known_at_rule_time": True,
        "endpoint_binding": c.get("endpoint_binding") or BINDING_NONE,
        "endpoint_result_span": c.get("endpoint_result_span"),
        "endpoint_definition_span": c.get("endpoint_definition_span"),
    }
    if c.get("endpoint_binding_reason"):
        row["endpoint_binding_reason"] = c["endpoint_binding_reason"]
    if c.get("compatibility_judgments"):
        row["endpoint_compatibility_judgments"] = c["compatibility_judgments"]
    if c.get("target_endpoint_class") == NEAR_MATCH:
        row["near_match_reason"] = _near_reason(c)
    if c.get("effect") is not None:
        row.update({"effect": c.get("effect"), "ci_low": c.get("ci_low"),
                    "ci_high": c.get("ci_high"), "scale": c.get("scale")})
    else:
        row.update({"ai": c.get("ai"), "n1i": c.get("n1i"), "ci": c.get("ci"), "n2i": c.get("n2i")})
    if c.get("endpoint_counts"):
        row["endpoint_counts"] = dict(c["endpoint_counts"])
    for k in ("registry_title", "registry_type", "registry_measure_type", "registry_timeframe"):
        if c.get(k) is not None:
            row[k] = c[k]
    return row


def select_target_endpoint(
    spec: dict[str, Any],
    abstract: str | None,
    outcome_measures: list[dict[str, Any]] | None,
    interv: list[str],
    comp: list[str],
) -> dict[str, Any]:
    if not canonical_components(spec):
        return {"selected": None, "candidates": [], "exact_target_in_held_source": False}
    candidates = enumerate_candidates(spec, abstract, outcome_measures, interv, comp)
    exact = [c for c in candidates if c.get("target_endpoint_class") == EXACT_TARGET]
    near = [c for c in candidates if c.get("target_endpoint_class") == NEAR_MATCH]
    # ADMISSIBILITY: exact targets only. A near match is eligible solely under the outcome's explicit
    # `allow_near_match` declaration and only when nothing is MISSING (a superset may be disclosed; a
    # component/subset is never the composite). `exact or near` admitted a 4-point MACE under a 3-point
    # label with no composite-mismatch refusal (external review, defect 1).
    near_ok = [c for c in near if near_match_declared(spec) and not c.get("missing_components")]
    eligible = exact or near_ok
    if not eligible:
        with_number = [c for c in candidates if c.get("effect") is not None or c.get("ai") is not None]
        refusal = None
        if with_number:
            best = sorted(with_number, key=_selection_key, reverse=True)[0]
            verdict = admissibility(spec, row_from_candidate(best))
            refusal = {**_public_candidate(best),
                       "endpoint_result_span": best.get("endpoint_result_span"),
                       "endpoint_definition_span": best.get("endpoint_definition_span"),
                       "refused_effect": {k: best.get(k) for k in ("effect", "ci_low", "ci_high", "scale", "ai", "n1i", "ci", "n2i")
                                          if best.get(k) is not None},
                       "source": best.get("source"),
                       "reason_code": verdict["verdict"], "reason": verdict.get("reason", "")}
        return {"selected": None, "candidates": [_public_candidate(c) for c in candidates],
                "exact_target_in_held_source": False, "refusal": refusal}
    selected = sorted(eligible, key=_selection_key, reverse=True)[0]
    row = row_from_candidate(selected)
    alternatives = [
        _public_candidate(c) for c in (exact + near)
        if c.get("candidate_id") != selected.get("candidate_id")
    ]
    if alternatives:
        row["target_endpoint_alternatives"] = alternatives[:6]
    primary_family = [
        c for c in eligible
        if c.get("source_type") == "ctgov_results" and str(c.get("registry_type") or "").upper() == "PRIMARY"
    ]
    if len(primary_family) > 1:
        row["registered_primary_selection_rule"] = {
            "n_registered_primaries_in_family": len(primary_family),
            "rule": "closest component set to canonical target; ties use registration order",
            "alternatives": [_public_candidate(c) for c in primary_family],
            "results_known_at_rule_time": True,
        }
    return {
        "selected": row,
        "candidates": [_public_candidate(c) for c in candidates],
        "exact_target_in_held_source": bool(exact),
        "selected_candidate": _public_candidate(selected),
        "near_match_while_exact_exists": bool(exact and selected.get("target_endpoint_class") == NEAR_MATCH),
    }
