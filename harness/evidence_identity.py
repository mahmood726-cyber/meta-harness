"""Typed identity for every number the refusal auditor may cite (V1.0.1; external review of balanced-crystalloids, commit 6260e70c).

The auditor used to mark a refusal false when ANY sentence mentioned the outcome and held ANY number: crossover/exposure counts
disproved a mortality refusal, a composite disproved a component refusal, a raw count disproved a design refusal. A number is now
evidence against a refusal only through a typed identity that matches the refused claim on EVERY field:

  trial, comparison, outcome, part (COMPONENT | COMPOSITE), timepoint, population, effect measure, adjusted + model, role
  (OUTCOME_COUNT | EXPOSURE_COUNT | DENOMINATOR | BASELINE | EFFECT_ESTIMATE | UNDECIDED)

Deterministic regex / table extraction decides. Where it cannot decide a number's ROLE (exposure vs outcome) the role stays
UNDECIDED: this module is in the certificate's code closure, and no pinned producer reads a model proposal (the reproducible-AI
contract). A reviewer holding recorded proposals as review material may pass them to resolve_role explicitly; the produced identity
then says so (basis RECORDED_PROPOSAL, record_id). Nothing in this module names a trial or a topic.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ROLES = ("OUTCOME_COUNT", "EXPOSURE_COUNT", "DENOMINATOR", "BASELINE", "EFFECT_ESTIMATE", "UNDECIDED")

# EXPOSURE is a real exposure/crossover cue. A bare "received" is NOT one: "patients who received the 5-mg dose" names the ARM.
_EXPOSURE = re.compile(r"\bunassigned\b|\bcross(?:ed)?[- ]?over\b|\bexposure\b|\bexposed\b|\bvolume of\b|\bnon-?study\b"
                       r"|\breceived any\b|\bopen-label\b(?=[^.;]{0,40}\b(?:use|treatment|therapy)\b)", re.I)
# Read clinical predicates as well as event nouns so explicitly reported patient outcomes keep their role.
_OUTCOME = re.compile(r"\bdied\b|\bdeaths?\b|\bmortality\b|\bdeveloped\b|\boccurred\b|\bevents?\b|\bwas used in\b|\brequired\b"
                      r"|\bunderwent\b|\bnew renal[- ]replacement\b|\bhad (?:an? )?(?:[\w-]+ ){0,4}(?:event|injury|failure)\b"
                      r"|\b(?:was|were) (?:performed|observed|reported|diagnosed|recorded)\b|\bexperienced\b"
                      r"|\b(?:had|needed)\b[^.;]{0,60}\b(?:infections?|episodes?|insulin)\b|\bwere hospitalized\b"
                      r"|\b(?:the )?(?:rate|incidence|occurrence|cumulative incidence) of\b", re.I)
_DENOMINATOR = re.compile(r"\b(?:randomi[sz]ed|assigned|allocated|enrolled|included)\b", re.I)
_BASELINE = re.compile(r"\bat baseline\b|\bbaseline (?:characteristics|value|level)\b|\bat (?:enrollment|randomi[sz]ation)\b", re.I)
_COMPOSITE = re.compile(r"\b(?:death|died|mortality)\s+or\s+(?!placebo\b)[a-z]|\b[a-z]+\s+or\s+(?:had\s+)?(?:died|death)\b|\bcomposite\b|\bmajor adverse (?:kidney|cardiovascular|cardiac|limb) events?\b|\bMAKE\d*\b|\bMACE\b", re.I)
_SUBGROUP = re.compile(r"\bamong (?:survivors|patients (?:who|with|without|not)[^.;,)]{0,60})|\bsubgroup\b|\bper[- ]protocol\b"
                       r"|\bas[- ]treated\b|\bin patients who\b", re.I)
_ADJUSTED = re.compile(r"\badjusted\b", re.I)
_MODEL = re.compile(r"[^.;]*(?:mixed[- ]effects?|random effects?|generali[sz]ed (?:linear|estimating)|\bGEE\b|cluster[- ]adjusted"
                    r"|proportional[- ]odds|Cox (?:proportional|regression|model)|logistic regression)[^.;]*", re.I)
_CLUSTER_MODEL = re.compile(r"random effects?|mixed[- ]effects?|generali[sz]ed estimating|\bGEE\b|cluster", re.I)
# spelled-out names match in any case ("Adjusted Odds Ratio" in a table header); abbreviations only in capitals, so the word "or"
# is never an odds ratio
_MEASURE = (("OR", re.compile(r"(?i:\bodds ratio\b)|\bOR\b")), ("HR", re.compile(r"(?i:\bhazard ratio\b)|\bHR\b")),
            ("RR", re.compile(r"(?i:\b(?:relative risk|risk ratio|rate ratio)\b)|\bRR\b")),
            ("RD", re.compile(r"(?i:\b(?:risk|absolute) difference\b)")))
# The left guard prevents a decimal's fractional digits being read as an integer.
_TIME_NUMBER = r"(?<![\w.])\d+(?:\.\d+)?"
_TIME_UNIT = r"(?:days?|months?|hours?|years?)"
_FOLLOWUP_DURATION = (r"\b(?:(?:median|mean)\s+of\s+|"
                      r"(?:(?:median|mean)\s+)?follow[- ]up\s+(?:duration\s+)?(?:(?:of|was)\s+)?)"
                      + _TIME_NUMBER + r"\s+" + _TIME_UNIT + r"\b")
_AGE_BEFORE = re.compile(r"\b(?:age[ds]?|aged|years? of age)\b[^.;,)]{0,20}$", re.I)
_AGE_AFTER = re.compile(r"^\s*(?:old|of age)\b", re.I)


def _is_age(text: str, start: int, end: int) -> bool:
    """A years value governed by age wording ('median age 68 years', 'aged 70 years', '68 years old') is an age."""
    return bool(_AGE_BEFORE.search(text[max(0, start - 30):start]) or _AGE_AFTER.search(text[end:end + 12]))


_TIMEPOINT = re.compile(
    r"(?P<followup>" + _FOLLOWUP_DURATION + r")"
    r"|\b(?:within|before|at|by|through|after|up to|until)\s+(?P<days>" + _TIME_NUMBER + r")\s+days?\b"
    r"|(?P<day_label>" + _TIME_NUMBER + r")[- ]day\b|\bday\s+(?P<day>" + _TIME_NUMBER + r")\b"
    r"|\b(?P<hospital>in[- ]hospital|in the hospital|before (?:hospital|ICU) discharge|hospital discharge|ICU discharge)\b"
    r"|(?P<months>" + _TIME_NUMBER + r")\s+months?\b"
    r"|(?P<duration>" + _TIME_NUMBER + r")(?:\s+|-)?(?P<unit>hours?|years?)\b", re.I)
_EFFECT_CELL = re.compile(r"^\s*([−-]?\d+(?:\.\d+)?)\s*\(\s*([−-]?\d+(?:\.\d+)?)\s*(?:to|-|–|,)\s*([−-]?\d+(?:\.\d+)?)\s*\)\s*$")
# a risk difference is an effect measure too: without it, '60-day mortality (16% vs. 18%; absolute risk difference − 2%, 95% CI
# − 8 to 5%)' was typed by whatever ratio came LATER in the paragraph (ESCAPe: typed 'OR'). Signs are kept (− is U+2212).
# Read CI/Cl labels, optional [CI], and signed or hyphen-separated bounds as one reported effect.
_EFFECT_IN_TEXT = re.compile(r"\b(odds ratio|hazard ratio|relative risk|risk ratio|rate ratio|(?:absolute )?risk difference|OR|HR|RR|RD)"
                             r"\b[^0-9−-]{0,30}([−-]?\s?\d+(?:\.\d+)?)\s*%?\s*[\(\[;,]?\s*(?:\d{2}\s*%\s*(?:CI|Cl|confidence interval)(?:\s*\[CI\])?\s*[,:=]?\s*)?"
                             r"[\(\[]?\s*([−-]?\s?\d+(?:\.\d+)?)\s*%?\s*(?:to|,|[-–](?=\s*[−-]?\d))\s*([−-]?\s?\d+(?:\.\d+)?)", re.I)

# Read a stated one-sided bound separately: its missing opposite limit must stay unknown.
_ONE_SIDED = re.compile(
    r"\b(odds ratio|hazard ratio|relative risk|risk ratio|OR|HR|RR)\b\s*[,=:]?\s*(\d+(?:\.\d+)?)"
    r"\s*[;,]\s*(upper|lower)\s+(?:bound(?:ary)?|limit)\s+of\s+(?:the\s+)?"
    r"one[- ]sided\s+(repeated\s+)?(?:\d{2}%\s+)?confidence interval\s*[,=:]?\s*(\d+(?:\.\d+)?)", re.I)


def _effects(text: str) -> list[dict[str, Any]]:
    out = []
    for m in _EFFECT_IN_TEXT.finditer(text):
        out.append({"start": m.start(), "end": m.end(), "effect_measure": measure_of(m.group(1)),
                    "estimate": _num(m.group(2)), "ci": [_num(m.group(3)), _num(m.group(4))]})
    for m in _ONE_SIDED.finditer(text):
        out.append({"start": m.start(), "end": m.end(), "effect_measure": measure_of(m.group(1)),
                    "estimate": _num(m.group(2)), "ci": None,
                    "confidence_bound": {"side": m.group(3).lower(), "value": _num(m.group(5)),
                                         "one_sided": True, "repeated": bool(m.group(4))}})
    return sorted(out, key=lambda e: e["start"])


def _num(s: str) -> float:
    return float(re.sub(r"\s+", "", s.replace("−", "-")))
_TAG = re.compile(r"<[^>]+>")


def _text(fragment: str) -> str:
    return " ".join(html.unescape(_TAG.sub(" ", fragment)).split())


def measure_of(text: str) -> str | None:
    for name, rx in _MEASURE:
        if rx.search(text or ""):
            return name
    return None


_LEADING_TIME = re.compile(
    r"^\s*(?:(?:over|during|after)\s+(?:a\s+)?" + _FOLLOWUP_DURATION + r"|"
    r"(?:at|by|through|within|after|up to|until)\s+(?:day\s+" + _TIME_NUMBER + r"|"
    + _TIME_NUMBER + r"\s+(?:days?|weeks?|months?|hours?|years?)|"
    r"(?:the )?end of (?:the )?(?:study|follow-up|treatment)))\s*,", re.I)


def leading_timepoint(sentence: str) -> str | None:
    """The timepoint of a sentence-LEADING adverbial ('At day 28, ...'), which governs every clause of the sentence; None otherwise."""
    m = _LEADING_TIME.match(sentence or "")
    return timepoint_of(m.group(0)) if m else None


def timepoint_of(text: str) -> str | None:
    """EVERY time qualifier the span states, in order ('in-hospital; 30 days' for 'In-hospital death before 30 days') -- the
    actual timepoint is kept whole, never cut to its first qualifier."""
    parts = []
    for m in _TIMEPOINT.finditer(text or ""):
        if m["duration"] and m["unit"].lower().startswith("year") and _is_age(text or "", m.start(), m.end()):
            continue                                  # 'median age 68 years' is an age, never a timepoint
        days = m["days"] or m["day_label"] or m["day"]
        if m["followup"]:
            duration = re.search(r"(" + _TIME_NUMBER + r")\s+(" + _TIME_UNIT + r")\b", m["followup"], re.I)
            tp = f"follow-up: {duration[1]} {duration[2].lower().rstrip('s')}s"
        elif days:
            tp = f"{days} days"
        elif m["hospital"]:
            tp = "in-hospital" if "hospital" in m["hospital"].lower() and "icu" not in m["hospital"].lower() else m["hospital"].lower()
        elif m["months"]:
            tp = f"{m['months']} months"
        else:
            tp = f"{m['duration']} {m['unit'].lower().rstrip('s')}s"
        if tp not in parts:
            parts.append(tp)
    return "; ".join(parts) or None


def part_of(text: str) -> str:
    return "COMPOSITE" if _COMPOSITE.search(text or "") else "COMPONENT"


# Endpoint rank is part of its identity: a secondary definition cannot name a primary result.
# Outcome / end point / endpoint are spelling variants; an outcome event is the same endpoint.
_ENDPOINT_SUBJECT = re.compile(
    r"^\s*(?:the|a|an)\s+(?P<rank>primary|key\s+secondary|secondary)\s+"
    r"(?:outcome|end[- ]?point)\b(?:\s+event\b)?", re.I)
_ENDPOINT_FOLLOWUP = re.compile(
    r"^\s*over\s+(?:a\s+)?median\s+(?:follow-up\s+)?of\s+\d+(?:\.\d+)?\s+"
    r"(?:days?|weeks?|months?|years?)\s*,\s*", re.I)
_ENDPOINT_HEADING = re.compile(r"^\s*(?:methods|results|findings|outcomes)\s*:\s*", re.I)


def _endpoint_subject(label: str) -> re.Match | None:
    text = _ENDPOINT_HEADING.sub("", label or "")
    text = _ENDPOINT_FOLLOWUP.sub("", text)
    text = _LEADING_TIME.sub("", text)
    return _ENDPOINT_SUBJECT.match(text)


def endpoint_reference(label: str) -> str | None:
    """Only a named endpoint serving as the clause's subject, never a mention in another result."""
    match = _endpoint_subject(label)
    return " ".join(match["rank"].lower().split()) if match else None


def endpoint_definitions(sentences: list[str]) -> dict[str, str]:
    """Unambiguous explicit definitions from ONE source. No retained state or cross-source lookup.

    Keep the whole definition sentence (including composite components) as provenance. Multiple
    distinct definitions of one rank fail closed rather than choosing one trial or endpoint.
    """
    found: dict[str, set[str]] = {}
    for sentence in sentences:
        subject = _endpoint_subject(sentence)
        if not subject:
            continue
        predicate = subject.string[subject.end():]
        definition = re.match(r"\s+(?:was|is)\s+(?:defined\s+as\s+)?(.+)", predicate, re.I)
        if not definition or result_clauses(sentence) or _effects(sentence):
            continue
        body = definition[1]
        if (not re.match(r"[a-z]", body, re.I)
                or re.match(r"(?:not|lower|higher|similar|reported|observed|recorded|reduced|increased|"
                            r"assessed|evaluated|measured|analysed|analyzed|prespecified|adjudicated|"
                            r"more|less|met|reached|achieved|\w+ly)\b", body, re.I)):
            continue
        rank = " ".join(subject["rank"].lower().split())
        found.setdefault(rank, set()).add(sentence)
    return {rank: next(iter(definitions)) for rank, definitions in found.items() if len(definitions) == 1}


def population_of(text: str) -> str:
    m = _SUBGROUP.search(text or "")
    return m.group(0).strip() if m else "AS_REPORTED_UNQUALIFIED"


def lexical_role(text: str) -> str:
    """The deterministic role, from cues alone. UNDECIDED when the cues conflict or are absent."""
    if _EFFECT_IN_TEXT.search(text or "") or _ONE_SIDED.search(text or ""):
        return "EFFECT_ESTIMATE"
    exposure, outcome = bool(_EXPOSURE.search(text or "")), bool(_OUTCOME.search(text or ""))
    if exposure and not outcome:
        return "EXPOSURE_COUNT"
    if outcome and not exposure:
        return "OUTCOME_COUNT"
    if exposure and outcome:
        return "UNDECIDED"
    if _BASELINE.search(text or ""):
        return "BASELINE"
    if _DENOMINATOR.search(text or ""):
        return "DENOMINATOR"
    return "UNDECIDED"


def role_supported(role: str, text: str) -> bool:
    """The deterministic check any role -- including a recorded model proposal -- must pass: the span carries that role's cue."""
    return {"OUTCOME_COUNT": bool(_OUTCOME.search(text or "")), "EXPOSURE_COUNT": bool(_EXPOSURE.search(text or "")),
            "DENOMINATOR": bool(_DENOMINATOR.search(text or "")), "BASELINE": bool(_BASELINE.search(text or "")),
            "EFFECT_ESTIMATE": bool(_EFFECT_IN_TEXT.search(text or "") or _ONE_SIDED.search(text or ""))}.get(role, False)


def proposal_supported(role: str, quote: str, text: str) -> bool:
    """The deterministic check a RECORDED model proposal must pass (the regex already failed to decide this span, so the check is on
    the proposal's own verbatim quote, not on the cue list that failed): the quote is in the span, carries one of its numbers, and
    fits the role -- an outcome count quotes no exposure cue; an exposure count quotes an exposure word; a denominator quotes an
    allocation word; a baseline quotes 'baseline'; an effect estimate quotes a ratio with its interval."""
    q, span = " ".join((quote or "").split()), " ".join((text or "").split())
    if not q or q not in span or not re.search(r"\d", q):
        return False
    return {"OUTCOME_COUNT": not _EXPOSURE.search(q),
            "EXPOSURE_COUNT": bool(_EXPOSURE.search(q) or re.search(r"\b(?:received|given|administered|treated with)\b", q, re.I)),
            "DENOMINATOR": bool(_DENOMINATOR.search(q)), "BASELINE": bool(re.search(r"\bbaseline\b", q, re.I)),
            "EFFECT_ESTIMATE": bool(_EFFECT_IN_TEXT.search(q))}.get(role, False)


def span_key(text: str) -> str:
    return hashlib.sha256(" ".join((text or "").split()).encode("utf-8")).hexdigest()


def resolve_role(text: str, proposals: dict[str, Any] | None = None) -> tuple[str, str, str | None]:
    """(role, basis, record_id). A recorded proposal is used only for an UNDECIDED span, and only if it passes role_supported."""
    role = lexical_role(text)
    if role != "UNDECIDED":
        return role, "REGEX", None
    prop = (proposals or {}).get(span_key(text))                 # never read from a store here: only what a caller passes
    if (isinstance(prop, dict) and prop.get("role") in ROLES and prop["role"] != "UNDECIDED"
            and proposal_supported(prop["role"], prop.get("quote") or "", text)):
        return prop["role"], "RECORDED_PROPOSAL", prop.get("record_id")
    return "UNDECIDED", ("RECORDED_PROPOSAL_REFUSED" if prop else "REGEX"), (prop or {}).get("record_id") if isinstance(prop, dict) else None


def from_sentence(sentence: str, trial: str, source_id: str, proposals: dict[str, Any] | None = None,
                  context_timepoint: str | None = None) -> dict[str, Any]:
    role, basis, record_id = resolve_role(sentence, proposals)
    effects = _effects(sentence or "")
    eff = effects[0] if effects else None
    if eff:
        role, basis = "EFFECT_ESTIMATE", "REGEX"
    model = _MODEL.search(sentence or "")
    return {"trial": trial, "source_id": source_id, "span": " ".join(sentence.split())[:320], "kind": "SENTENCE",
            "role": role, "role_basis": basis, "role_record_id": record_id,
            "part": part_of(sentence), "timepoint": timepoint_of(sentence) or context_timepoint, "population": population_of(sentence),
            "effect_measure": eff["effect_measure"] if eff else ("COUNTS" if role == "OUTCOME_COUNT" else None),
            "estimate": eff["estimate"] if eff else None, "ci": eff["ci"] if eff else None,
            **({"confidence_bound": eff["confidence_bound"]} if eff and "confidence_bound" in eff else {}),
            "adjusted": bool(_ADJUSTED.search(sentence or "")), "model": model.group(0).strip()[:240] if model else None,
            "unit": unit_of(sentence), "analysis_set": analysis_set_of(sentence),
            "attribution": attribution_of(sentence), "window": window_of(sentence),
            "comparison": "TWO_ARMS_NAMED" if (re.search(r"\b(?:vs\.?|versus|compared with|compared to|respectively)\b", sentence or "", re.I)
                                               or len(re.findall(r"\b(?:group|arm)s?\b", sentence or "", re.I)) >= 2)
            else "UNSTATED"}


def from_registry_measure(measure: dict[str, Any], trial: str, source_id: str) -> list[dict[str, Any]]:
    """Type one held CT.gov outcome table without computing or pooling any value.

    Each category/analysis is a separate candidate. Only the measure's endpoint
    fields name it; intervention descriptions cannot supply endpoint identity.
    The caller applies the ordinary naming, mismatch and refusal-scope checks.
    """
    def objects(value):
        return [v for v in value if isinstance(v, dict)] if isinstance(value, list) else []

    def text(value):
        return str(value) if value is not None else ""

    def integer(value):
        return bool(re.fullmatch(r"\d+", text(value)))

    title = text(measure.get("title"))
    description = text(measure.get("description"))
    endpoint = " ".join(filter(None, (title, description)))
    population = text(measure.get("populationDescription"))
    timeframe = text(measure.get("timeFrame"))
    # A structured duration needs no prose preposition. Feed that explicit field
    # to the existing timepoint parser without changing its matching policy.
    duration = re.fullmatch(_TIME_NUMBER + r"\s+" + _TIME_UNIT, timeframe, re.I)
    timepoint = timepoint_of("at " + timeframe if duration else timeframe) or timeframe or None
    groups = objects(measure.get("groups"))
    group_ids = [g.get("id") for g in groups]
    named_groups = (bool(groups) and all(g.get("id") and g.get("title") for g in groups)
                    and len(set(group_ids)) == len(groups))
    group_map = {g.get("id"): g for g in groups}
    param = measure.get("paramType")
    unit = text(measure.get("unitOfMeasure"))

    def base(label):
        ident = from_sentence(label, trial, source_id, {})
        ident.update(kind="REGISTRY_RESULT", label=label, role_basis="REGISTRY_FIELDS",
                     timepoint=timepoint, population=population_of(label + " " + population),
                     analysis_set=analysis_set_of(label + " " + population),
                     effect_measure=param, role="UNDECIDED", unit=unit_of(unit),
                     estimate=None, ci=None, adjusted=False, model=None,
                     comparison="UNSTATED", registry_time_frame=timeframe,
                     registry_population=population, registry_parameter=param, registry_unit=unit)
        return ident

    def comparison(ids):
        if not named_groups or len(ids) != len(set(ids)) or any(g not in group_map for g in ids):
            return "UNSTATED"
        return "TWO_ARMS_NAMED" if len(ids) == 2 else "MULTI_ARM_UNRESOLVED"

    out = []
    for cls in objects(measure.get("classes")):
        for cat in objects(cls.get("categories")):
            values = objects(cat.get("measurements"))
            if not values:
                continue
            label = " ".join(filter(None, (endpoint, text(cls.get("title")), text(cat.get("title")))))
            ident = base(label)
            # Use the closest explicitly provided denominator table. Never borrow
            # an enrolment total or a denominator from another outcome/category.
            denoms = cat.get("denoms", cls.get("denoms", measure.get("denoms")))
            participant_denoms = [d for d in objects(denoms)
                                  if text(d.get("units")).lower() in {"participants", "patients", "subjects"}]
            counts = objects(participant_denoms[0].get("counts")) if len(participant_denoms) == 1 else []
            denominators = {d.get("groupId"): d.get("value") for d in counts}
            ids = [v.get("groupId") for v in values]
            complete = (len(counts) == len(denominators) and all(
                integer(v.get("value")) and integer(denominators.get(v.get("groupId")))
                and 0 <= int(v["value"]) <= int(denominators[v["groupId"]])
                and int(denominators[v["groupId"]]) > 0 for v in values))
            # An explicit event/cycle unit conflicts with participant counts; do
            # not erase it simply because paramType says COUNT_OF_PARTICIPANTS.
            count_unit = unit_of(label + " " + unit)
            if param == "COUNT_OF_PARTICIPANTS" and complete:
                ident.update(role="OUTCOME_COUNT", effect_measure="COUNTS",
                             unit=count_unit if count_unit in {"EVENTS", "PATIENT_YEARS", "CYCLES"}
                             else "PATIENTS_WITH_EVENT")
            arms = [{"arm": group_map.get(v.get("groupId"), {}).get("title"),
                     "group_id": v.get("groupId"), "events": v.get("value"),
                     "n": denominators.get(v.get("groupId"))} for v in values]
            ident.update(arms=arms, comparison=comparison(ids) if set(ids) == set(group_ids) else "UNSTATED")
            ident["span"] = (f"{label} | timeFrame: {timeframe} | population: {population} | "
                             f"{param}; {unit} | " + " | ".join(
                                 f"{a['arm']} [{a['group_id']}]: {a['events']}/{a['n']}"
                                 if ident["effect_measure"] == "COUNTS" else
                                 f"{a['arm']} [{a['group_id']}]: {a['events']} (analysed n={a['n']})" for a in arms))
            out.append(ident)
    # Keep reported effect estimates separate from arm counts. No effect or CI is
    # calculated from counts, percentages, p-values, dispersion or other analyses.
    effect_types = {"Risk Ratio": "RR", "Relative Risk": "RR", "Odds Ratio": "OR",
                    "Hazard Ratio": "HR", "Risk Difference": "RD",
                    "Mean Difference (Final Values)": "MD", "Mean Difference (Net)": "MD"}
    for analysis in objects(measure.get("analyses")):
        if analysis.get("paramValue") is None:
            continue
        ident = base(endpoint)
        reported_type = analysis.get("paramType")
        ci = [analysis.get("ciLowerLimit"), analysis.get("ciUpperLimit")]
        ident.update(effect_measure=effect_types.get(reported_type, reported_type),
                     estimate=analysis["paramValue"], ci=ci if all(v is not None for v in ci) else None,
                     comparison=comparison(analysis.get("groupIds") or []))
        if reported_type in effect_types and ident["ci"] is not None:
            ident["role"] = "EFFECT_ESTIMATE"
        if analysis.get("ciNumSides") != "TWO_SIDED":
            ident["confidence_bound"] = analysis.get("ciNumSides") or "UNSTATED"
        model_text = " ".join(text(analysis.get(k)) for k in
                              ("statisticalMethod", "statisticalComment", "estimateComment", "paramType"))
        model = _MODEL.search(model_text)
        ident.update(adjusted=bool(_ADJUSTED.search(model_text)), model=model.group(0) if model else None)
        ident["span"] = (f"{endpoint} | timeFrame: {timeframe} | population: {population} | analysis: "
                         + json.dumps(analysis, ensure_ascii=False, sort_keys=True))
        out.append(ident)
    return out


def _table_rows(wrap: str) -> list[tuple[list[str], list[str], str]]:
    # Read the complete header grid (including empty cells and spans) so each body column keeps its own header.
    cell_rx = re.compile(r"<t([dh])\b([^>]*?)(?:/\s*>|>(.*?)</t\1\s*>)", re.S | re.I)
    rows, occupied, headers = [], {}, []
    thead = re.search(r"<thead\b[^>]*>(.*?)</thead>", wrap, re.S | re.I)
    body_started = False
    for ri, tr in enumerate(re.finditer(r"<tr\b[^>]*>(.*?)</tr>", wrap, re.S | re.I)):
        cells = list(cell_rx.finditer(tr.group(1)))
        if not cells:
            continue
        is_header = bool(thead and thead.start() <= tr.start() < thead.end()) or (
            not thead and not body_started and all(c.group(1).lower() == "h" for c in cells))
        body_started |= not is_header
        grid = {col: value for (row, col), value in occupied.items() if row == ri}
        col = 0
        for cell in cells:
            while col in grid:
                col += 1
            spans = []
            for attr in ("rowspan", "colspan"):
                m = re.search(r"\b" + attr + r"\s*=\s*['\"]?(\d+)", cell.group(2), re.I)
                spans.append(int(m.group(1)) if m else 1)
            if any(n < 1 or n > 1000 for n in spans):
                return []  # malformed or unbounded geometry cannot establish column identity
            value = _text(cell.group(3) or "")
            for r in range(ri, ri + spans[0]):
                for c in range(col, col + spans[1]):
                    if (r, c) in occupied:
                        return []
                    occupied[r, c] = value
                    if r == ri:
                        grid[c] = value
            col += spans[1]
        expanded = [grid.get(c, "") for c in range(max(grid, default=-1) + 1)]
        if is_header:
            headers.append(expanded)
        else:
            rows.append(expanded)
    width = max((len(r) for r in rows), default=0)
    header_width = max((len(h) for h in headers), default=0)
    if header_width == width - 1:
        headers = [[""] + h for h in headers]
    header = [" | ".join(dict.fromkeys(h[c] for h in headers if c < len(h) and h[c])) for c in range(width)]
    result, section = [], ""
    for cells in rows:
        nonempty = list(dict.fromkeys(c for c in cells if c))
        if len(nonempty) == 1:
            section = nonempty[0]
            continue
        result.append((header, cells, section))
    return result


def from_tables(raw: str, trial: str, source_id: str) -> list[dict[str, Any]]:
    """One identity per table row that carries an effect estimate (and one per row of arm counts), with the table's model footnote,
    the row's own timepoint and part, and the section it sits under."""
    out = []
    for wrap in re.findall(r"<table-wrap.*?</table-wrap>", raw or "", re.S) or re.findall(r"<table.*?</table>", raw or "", re.S):
        feet = " ".join(_text(f) for f in re.findall(r"<table-wrap-foot>(.*?)</table-wrap-foot>", wrap, re.S)) or \
            " ".join(_text(f) for f in re.findall(r"<fn[^>]*>(.*?)</fn>", wrap, re.S))
        model = _MODEL.search(feet)
        composite_defined = {m.group(1).strip().lower() for m in re.finditer(r"(?:^|\W)(?:A|An|The)\s+([^.]{3,80}?)\s+is the composite of", feet)}
        count_by_row = {(r["section"], r["label"]): r for r in count_rows(wrap, trial, source_id)}
        for header, cells, section in _table_rows(wrap):
            label = cells[0]
            full_label = f"{section} :: {label}" if section else label
            is_component = bool(re.search(r"\bcomponents? of\b", section, re.I))
            part = "COMPONENT" if is_component else (
                "COMPOSITE" if (_COMPOSITE.search(label) or any(d and d in label.lower() for d in composite_defined)) else "COMPONENT")
            for i, cell in enumerate(cells[1:], start=1):
                m = _EFFECT_CELL.match(cell)
                col = header[i] if i < len(header) else ""
                if not m or not measure_of(col):
                    continue
                out.append({"trial": trial, "source_id": source_id, "span": f"{full_label} | {cell} [{col}]", "kind": "TABLE_ROW",
                            "role": "EFFECT_ESTIMATE", "role_basis": "TABLE", "role_record_id": None, "part": part,
                            "timepoint": timepoint_of(label) or timepoint_of(section), "population": population_of(label),
                            "effect_measure": measure_of(col), "estimate": _num(m.group(1)),
                            "ci": [_num(m.group(2)), _num(m.group(3))], "adjusted": bool(_ADJUSTED.search(col)),
                            # Read adjacent arm counts only from this exact row; header totals remain n_group, never n.
                            "arms": count_by_row.get((section, label), {}).get("arms"),
                            "unit": count_by_row.get((section, label), {}).get("unit"),
                            "model": model.group(0).strip()[:240] if model else None,
                            "comparison": count_by_row.get((section, label), {}).get("comparison", "UNSTATED"),
                            "label": label, "section": section})
    return out


# a COUNT cell says it is one: 'n/N', 'n/N (x%)' or 'n (x%)' -- a bare number may be a percentage or a p-value
_COUNT_CELL = re.compile(r"^\s*(\d[\d,]*)\s*(?:/\s*(\d[\d,]*)\s*(?:\(\s*\d+(?:\.\d+)?\s*%?\s*\))?|\(\s*\d+(?:\.\d+)?\s*%?\s*\))\s*$")
_ANY_EVENT = re.compile(r"^\s*(?:any|all|overall|total)\b.*\b(?:adverse|event|effect)", re.I)
_NOT_AN_ARM = re.compile(r"\bp\b|p[- ]?value|\btotal\b|\ball patients\b|difference|ratio|\bCI\b|\bRR\b|\bOR\b|\bHR\b", re.I)
_PERCENT_ROW = re.compile(r"%\s*$|,\s*%|\(%\)\s*$|percent", re.I)
# a residual qualifier must PRECEDE a category noun: 'other serious adverse events', 'other causes' -- never 'the other group'
_RESIDUAL = re.compile(r"\b(?:other|remaining|additional)\s+(?:[\w-]+\s+){0,2}?(?:adverse|serious|events?|effects?|complications?"
                       r"|infections?|causes?|reactions?)\b|\bexcluding\b|\bexcept\b|\bnot otherwise\b", re.I)
_RESTRICTING = re.compile(r"\bnon[- ]?serious\b|\bserious\b|\bsevere\b|\bgrade\s*(?:≥|>=|3|4)|\b(?:drug|treatment|study[- ]drug)[- ]related\b|\bfatal\b"
                          r"|(?<!non-)(?<!non )\bmajor\b|\blife[- ]threatening\b"
                          r"|\bstages?\s*(?:≥|>=|>)?\s*(?:[23]|II|III)\b", re.I)


_BASELINE_TABLE = re.compile(r"\bbaseline\b|\bcharacteristics?\b|\bdemographic", re.I)
_COUNT_LABEL = re.compile(r"\bno\.|\bnumber\b|\bn\s*/\s*N\b|\bn\s*\(\s*%\s*\)", re.I)
_GROUP_N = re.compile(r"\bn\s*[=:]\s*(\d[\d,]*)", re.I)


_CELL_N_PCT = re.compile(r"^\s*(\d[\d,]*)\s*\(\s*(\d+(?:\.\d+)?)\s*%?\s*\)\s*$")


def _unit_from_percent_of_arm(cells: list[str], header: list[str]) -> str | None:
    """PATIENTS_WITH_EVENT when every arm cell's percentage is its count over the arm's header N (95.2 = 100*120/126): a share of
    the arm's PATIENTS. None when any arm lacks the N or the percentage does not reproduce."""
    seen = 0
    for i, c in enumerate(cells[1:], start=1):
        m = _CELL_N_PCT.match(c or "")
        n_arm = _group_n(header[i]) if i < len(header) else None
        if not m or not n_arm:
            continue
        if abs(100 * int(m.group(1).replace(",", "")) / n_arm - float(m.group(2))) > 0.06:
            return None
        seen += 1
    return "PATIENTS_WITH_EVENT" if seen >= 2 else None


def _group_n(header: str) -> int | None:
    m = _GROUP_N.search(header or "")
    return int(m.group(1).replace(",", "")) if m else None


_COL_EVENTS = re.compile(r"^\s*(?:E|events?|no\.?\s*of\s*events|episodes?)\s*$", re.I)
_COL_RATE = re.compile(r"^\s*(?:R|rate|events?\s*per\s*100\b.*|per\s*100\s*(?:PYE|PYO|patient[- ]years?).*|(?:PYE|PYO)\b.*)\s*$", re.I)
_COL_PATIENTS = re.compile(r"^\s*(?:n\s*\(\s*%\s*\)|n|%|no\.?\s*\(\s*%\s*\)|patients?(?:,\s*n\s*\(%\))?|participants?)\s*$", re.I)


def _expand_cells(tr: str) -> list[tuple[str, int, int]]:
    """(text, colspan, rowspan) per cell."""
    out = []
    for attrs, body in re.findall(r"<t[dh]([^>]*)>(.*?)</t[dh]>", tr, re.S):
        cs = re.search(r'colspan="?(\d+)', attrs)
        rs = re.search(r'rowspan="?(\d+)', attrs)
        out.append((_text(body), int(cs.group(1)) if cs else 1, int(rs.group(1)) if rs else 1))
    return out


def _column_unit_rows(wrap: str, trial: str, source_id: str, caption: str) -> list[dict[str, Any]] | None:
    """None unless the table's header gives columns of >=2 different units (patients / events / rate); then one identity per unit
    per body row, pairing the arms' cells of that unit."""
    trs = re.findall(r"<tr[^>]*>(.*?)</tr>", wrap, re.S)
    head = [tr for tr in trs if "<th" in tr]
    if not head:
        return None
    grid: list[list[str]] = []
    carry: dict[int, tuple[str, int]] = {}             # column -> (text, rows still to fill) from rowspan
    for tr in head:
        row, col, cells = [], 0, _expand_cells(tr)
        i = 0
        while i < len(cells) or col in carry:
            if col in carry:
                txt, left = carry.pop(col)
                row.append(txt)
                if left > 1:
                    carry[col] = (txt, left - 1)
                col += 1
                continue
            txt, cs, rs = cells[i]
            i += 1
            for _ in range(cs):
                row.append(txt)
                if rs > 1:
                    carry[col] = (txt, rs - 1)
                col += 1
        grid.append(row)
    width = max(len(r) for r in grid)
    arm_of = [grid[0][c] if c < len(grid[0]) else "" for c in range(width)]
    sub_of = [grid[-1][c] if c < len(grid[-1]) else "" for c in range(width)]
    unit_of_col = []
    for c in range(width):
        sub = sub_of[c] if len(grid) > 1 else ""
        unit_of_col.append("EVENTS" if _COL_EVENTS.match(sub) else "RATE" if _COL_RATE.match(sub) else
                           "PATIENTS" if (_COL_PATIENTS.match(sub) or (len(grid) > 1 and sub == "")) else None)
    if len({u for u in unit_of_col[1:] if u}) < 2:
        return None
    out = []
    for tr in trs:
        if "<th" in tr:
            continue
        cells = [t for t, cs, _ in _expand_cells(tr) for _ in range(cs)]
        if len(cells) < 3 or not cells[0]:
            continue
        for unit in ("PATIENTS", "EVENTS", "RATE"):
            arms = []
            for c in range(1, min(width, len(cells))):
                if unit_of_col[c] != unit or _NOT_AN_ARM.search(arm_of[c] or ""):
                    continue
                v = cells[c]
                if unit == "RATE":
                    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*$", v)
                    val = {"rate": float(m.group(1))} if m else None
                else:
                    m = re.match(r"^\s*(\d[\d,]*)\s*(?:\(\s*\d+(?:\.\d+)?\s*%?\s*\))?\s*$", v)
                    val = {"events": int(m.group(1).replace(",", ""))} if m else None
                if val:
                    arms.append({"arm": arm_of[c], "n": None, "n_group": _group_n(arm_of[c]), **val})
            if len(arms) < 2:
                continue
            u = {"PATIENTS": "PATIENTS_WITH_EVENT", "EVENTS": "EVENTS", "RATE": "PATIENT_YEARS"}[unit]
            out.append({"trial": trial, "source_id": source_id, "kind": "TABLE_COLUMN_UNIT_ROW", "label": cells[0], "section": "",
                        "span": f"{cells[0]} [{unit}] | " + " | ".join(f"{a['arm']}: {a.get('events', a.get('rate'))}" for a in arms[:2]),
                        "role": "BASELINE" if _BASELINE_TABLE.search(caption) else "OUTCOME_COUNT", "role_basis": "TABLE",
                        "role_record_id": None, "any_event_row": bool(_ANY_EVENT.search(cells[0])),
                        "arms": arms[:2], "definition": "AS_LABELLED", "unit": u,
                        "analysis_set": analysis_set_of(caption), "attribution": attribution_of(cells[0]),
                        "window": window_of(caption + " " + cells[0]), "part": part_of(cells[0]), "timepoint": timepoint_of(cells[0]),
                        "population": population_of(cells[0]), "effect_measure": "RATE" if unit == "RATE" else "COUNTS",
                        "estimate": None, "ci": None, "adjusted": False, "model": None, "comparison": "TWO_ARMS_NAMED"})
    return out


def count_rows(raw: str, trial: str, source_id: str) -> list[dict[str, Any]]:
    """Every table row that gives a COUNT of affected individuals per arm ('26/180 (14.4)' or '26 (14.4)'), one identity per labelled
    row. Rows are never combined here: a count belongs to the one label it is printed under."""
    out = []
    for wrap in re.findall(r"<table-wrap.*?</table-wrap>", raw or "", re.S) or re.findall(r"<table.*?</table>", raw or "", re.S):
        caption = _text(" ".join(re.findall(r"<(?:label|caption|title)[^>]*>(.*?)</(?:label|caption|title)>", wrap, re.S)))
        column_rows = _column_unit_rows(wrap, trial, source_id, caption)
        if column_rows is not None:                  # a multi-unit table (n (%) | E | R per arm): read column by column
            out.extend(column_rows)
            continue
        for header, cells, section in _table_rows(wrap):
            # Explicit count/percent cells supported by arm totals outrank a shorthand percent-only row label.
            if (_PERCENT_ROW.search(cells[0]) and not _COUNT_LABEL.search(cells[0])
                    and not _unit_from_percent_of_arm(cells, header)):
                continue                                      # a row of percentages is not a row of counts ('no./total no. (%)' is)
            arms = [(header[i] if i < len(header) else f"col{i}", _COUNT_CELL.match(c)) for i, c in enumerate(cells[1:], start=1)]
            counts = [(h, int(m.group(1).replace(",", "")), int(m.group(2).replace(",", "")) if m.group(2) else None)
                      for h, m in arms if m and h and not _NOT_AN_ARM.search(h)
                      and not h.startswith("col")]
            if len(counts) < 2:
                continue
            groups = {h: _group_n(h) for h, _, _ in counts}
            out.append({"trial": trial, "source_id": source_id, "kind": "TABLE_COUNT_ROW", "label": cells[0], "section": section,
                        "span": f"{cells[0]} | " + " | ".join(f"{header[i]}: {c}" for i, c in enumerate(cells[1:], 1)),
                        "role": "BASELINE" if _BASELINE_TABLE.search(caption + " " + " ".join(header[:1])) else "OUTCOME_COUNT",
                        "role_basis": "TABLE", "role_record_id": None,
                        "any_event_row": bool(_ANY_EVENT.search(cells[0])),
                        # the unit a table row counts: its own label, else its section, else the arm headers ('n (%)')
                        "unit": (unit_of(cells[0]) or unit_of(section) or unit_of(" ".join(header))
                                 or _unit_from_percent_of_arm(cells, header)),
                        "analysis_set": analysis_set_of(caption + " " + " ".join(header)),
                        "attribution": attribution_of(cells[0]), "window": window_of(caption + " " + cells[0] + " " + section),
                        # n = the row's own denominator (outcome ascertained); n_group = the arm header's size (analysis group)
                        "arms": [{"arm": h, "events": e, "n": n, "n_group": groups[h]} for h, e, n in counts],
                        "definition": "AS_LABELLED",
                        "part": part_of(cells[0]), "timepoint": timepoint_of(cells[0]) or timepoint_of(section),
                        "population": population_of(cells[0]), "effect_measure": "COUNTS", "estimate": None, "ci": None,
                        "adjusted": False, "model": None, "comparison": "TWO_ARMS_NAMED" if len(counts) == 2 else "MULTI_ARM_UNRESOLVED"})
    return out


def names_the_outcome(label: str, outcome_name: str) -> bool:
    """A table row stands for an outcome only if it is named by the outcome's OWN name (not merely by a symptom keyword), and adds
    no restricting qualifier the outcome lacks ('serious ...' is a subset of 'adverse events ...')."""
    low = (label or "").lower()
    if not any(_names_alternative(low, alt) for alt in re.split(r"\s*/\s*", (outcome_name or "").lower()) if alt.strip()):
        return False
    return not (_RESTRICTING.search(label or "") and not _RESTRICTING.search(outcome_name or ""))


_AGGREGATE_CATEGORY = re.compile(r"\badverse (?:events?|effects?|reactions?)\b", re.I)
_REPORTING_QUALIFIERS = ("serious", "severe", "overall", "total", "emergent", "treatment")
_NOT_A_HEAD = ("adverse", "effects", "events", "outcome", "leading", "hours", "weeks", "months", "years", "days")


_HEAD_SYNONYMS = {"mortality": r"\bmortalit|\bdied\b|\bdeaths?\b|\bdead\b", "death": r"\bdeaths?\b|\bdied\b|\bmortalit|\bdead\b"}


def _head_present(word: str, low: str) -> bool:
    """A content word is present by its own stem, or -- for the death family only -- by a synonym ('died by day 28')."""
    return word[:6] in low or bool(word in _HEAD_SYNONYMS and re.search(_HEAD_SYNONYMS[word], low))


def _names_alternative(low: str, alt: str) -> bool:
    """One alternative of an outcome name ('muscle symptoms' / 'myopathy') is named when the label carries its HEAD NOUN (the last
    content word: 'death' in 'non-cardiovascular death', 'injury' in 'acute kidney injury') and at least half of its words; a
    'non-X' in the name must appear as 'non-X' ('cardiovascular' alone never names 'non-cardiovascular death')."""
    head = [w for w in re.findall(r"[a-z]{5,}", alt) if w not in _NOT_A_HEAD]
    if head and _AGGREGATE_CATEGORY.search(alt) and not [w for w in head if w not in _REPORTING_QUALIFIERS]:
        # an aggregate category ('serious adverse events'): only an AE-total phrase names it -- a component class ('serious
        # infections', 'neutropenia') is a subset, never the aggregate
        if re.search(r"\bSAEs?\b", low, re.I) and set(head) <= {"serious"}:
            return True                              # the abbreviation carries its own qualifier ('SAEs were reported ...')
        return bool(re.search(r"\badverse (?:events?|effects?|reactions?)\b|\bTEAEs?\b|\bAEs\b", low, re.I)) and \
            all(w[:6] in low for w in head)
    if not head:                                     # a generic outcome ('Any adverse events') is named by the generic phrase itself
        return bool(re.search(r"\badverse (?:events?|effects?|reactions?)\b|\bside effects?\b|\bteaes?\b", low))
    if not _head_present(head[-1], low) or sum(1 for w in head if _head_present(w, low)) * 2 < len(head):
        return False
    for neg in re.findall(r"\bnon[- ]?([a-z]{4,})", alt):
        if not re.search(r"\bnon[- ]?" + re.escape(neg[:6]), low):
            return False
    return True


def bind_labelled_count_row(raw: str, trial: str, source_id: str, outcome_terms: list[str], matches_term,
                            outcome_name: str = "") -> dict[str, Any]:
    """Bind a (specific) outcome to exactly ONE labelled count row of the same source's tables -- the recovery step after a number
    is rejected as the wrong endpoint. Refuses rather than guesses:
      - an 'any adverse event' row never stands for a specific endpoint;
      - two or more rows matching the outcome -> AMBIGUOUS (no pick);
      - symptom rows are NEVER summed into the outcome: without the table stating that the affected patients are distinct,
        a sum can count one patient twice. So no matching row -> NOT_FOUND, even when component symptoms are present."""
    rows = count_rows(raw, trial, source_id)
    hits = [r for r in rows if not r["any_event_row"] and matches_term(r["label"], outcome_terms)]
    # a row named by the outcome's OWN name ('gastrointestinal ...') outranks rows matched only through a symptom keyword
    # ('diarrh'): a symptom is a component of the outcome, not the outcome
    head = [w for w in re.findall(r"[a-z]{5,}", (outcome_name or "").lower()) if w not in ("adverse", "effects", "events", "outcome")]
    named = [r for r in hits if head and any(w[:6] in r["label"].lower() for w in head)]
    if len(named) == 1:
        return {"state": "BOUND", "row": named[0]}
    if len(hits) == 1:
        return {"state": "BOUND", "row": hits[0]}
    if len(hits) > 1:
        return {"state": "AMBIGUOUS", "rows": [h["label"] for h in hits]}
    return {"state": "NOT_FOUND", "why": "no row labelled with this outcome; symptom rows are not summed (patients not shown distinct)",
            "rows_seen": [r["label"] for r in rows]}


def claim_of(outcome: dict[str, Any], row: dict[str, Any], terms_text: str) -> dict[str, Any]:
    """The refused claim, typed on the same fields."""
    design = row.get("design") if isinstance(row.get("design"), dict) else {}
    reason = str(row.get("reason") or "")
    return {"trial": str(row.get("id") or row.get("label")), "outcome": outcome.get("name"),
            # the outcome's timepoint field, else the one its own NAME states ('Secondary infections by 28 days')
            "part": part_of(f"{outcome.get('name')} {terms_text}"),
            "timepoint": outcome.get("timepoint") or timepoint_of(outcome.get("name") or ""),
            "population": outcome.get("population"), "effect_measure": outcome.get("estimand"),
            "design_refusal": bool(design and design.get("adjustment_status") not in (None, "ADJUSTED", "RESOLVED")
                                   or "design_adjusted_effect" in reason or "design=" in reason),
            "design": design.get("design"),
            # the refusal is ABOUT the counting unit ('events, rather than unique patients'): only unit evidence can disprove it
            "unit_refusal": bool(_UNIT_REFUSAL.search(reason)),
            "population_refusal": bool(_POPULATION_REFUSAL.search(reason))
                                  or str(row.get("reason_code") or row.get("state") or "").upper() == "POPULATION_MISMATCH",
            "unit_target": "CYCLES" if _UNIT_CYCLES.search(outcome.get("name") or "") else "PARTICIPANTS",
            "attribution": attribution_of(outcome.get("name") or ""), "window": window_of(outcome.get("name") or "")}


_DEFERS_TO_TRIAL = re.compile(r"\btrial[- ](?:reported|defined|specific)\b|\bas reported\b|\bper trial\b"
                              r"|\b(?:windows?|timing|timepoints?)\s+var(?:y|ies)\s+(?:by|across|between)\s+trials?\b", re.I)
_TERMINAL_TIME = re.compile(r"\b(?:trial|study) end\b|\bend of (?:the )?(?:study|trial|follow[- ]up)\b"
                            r"|\blongest\b(?:\s+[a-z-]+){0,4}\s+follow[- ]up\b", re.I)


def _timepoint_in(claim_tp: str | None, got: str | None) -> bool:
    if not claim_tp or _DEFERS_TO_TRIAL.search(claim_tp):
        return True                                                   # the claim does not constrain the timepoint
    if not got:
        return False                                                  # constrained, but the evidence's timepoint is unknown
    tp = claim_tp.lower()
    rng = re.search(r"(" + _TIME_NUMBER + r")\s*[-–]\s*(" + _TIME_NUMBER + r")\s*(" + _TIME_UNIT + r")\b", tp)
    one = re.search(r"(" + _TIME_NUMBER + r")\s*[- ]?(" + _TIME_UNIT + r")\b", tp)
    for q in got.split("; "):                                         # every qualifier the evidence states must fit the claim
        if q.startswith("follow-up: "):
            # A stated whole-follow-up duration meets a terminal claim, never a fixed assessment.
            ok = bool(_TERMINAL_TIME.search(tp)) and not (one or rng) and bool(
                re.fullmatch(r"follow-up: " + _TIME_NUMBER + r" " + _TIME_UNIT, q))
        elif q == "in-hospital":
            ok = "hospital" in tp
        else:
            m = re.fullmatch(r"(" + _TIME_NUMBER + r") (days|months|hours|years)", q)
            if not m:
                return False
            target = rng or one
            if not target:
                return False
            unit = target[3 if rng else 2].rstrip("s")
            value = Decimal(m[1])
            if m[2].rstrip("s") != unit:
                if m[2] == "months" and unit == "day":
                    value *= 30                                      # retain the existing month-to-day convention
                else:
                    return False                                    # no assumed year length or hour rounding
            ok = (Decimal(rng[1]) <= value <= Decimal(rng[2])) if rng else value == Decimal(one[1])
        if not ok:
            return False
    return True


def mismatches(identity: dict[str, Any], claim: dict[str, Any], outcome_named: bool) -> list[str]:
    """Every field on which this evidence fails to be evidence ABOUT the refused claim. Empty only on a full match."""
    bad = []
    if identity["role"] not in ("OUTCOME_COUNT", "EFFECT_ESTIMATE"):
        bad.append(f"role:{identity['role']}")
    if not outcome_named:
        bad.append("outcome")
    if identity["part"] != claim["part"]:
        bad.append(f"part:{identity['part']}!={claim['part']}")
    unit = identity.get("unit")
    if claim.get("unit_target") == "CYCLES" and unit != "CYCLES":
        bad.append(f"unit:{unit or 'UNSTATED'}!=CYCLES")               # a per-cycle target needs cycle counts
    elif claim.get("unit_target") == "PARTICIPANTS" and unit == "CYCLES":
        bad.append("unit:CYCLES!=PARTICIPANTS")                         # cycle counts are never independent participants
    if identity.get("effect_measure") == "COUNTS" and claim.get("effect_measure") in ("RR", "OR", "RD", None):
        if unit in ("EVENTS", "PATIENT_YEARS"):
            bad.append(f"unit:{unit}")                               # a patient-level ratio cannot be built from event counts
        elif unit is None and claim.get("unit_refusal"):
            bad.append("unit:UNSTATED")                               # a refusal ABOUT the unit needs source evidence of the unit
    if identity.get("definition") not in (None, "AS_NAMED", "AS_LABELLED"):
        bad.append(f"definition:{identity['definition']}")            # 'other serious AEs' is not 'serious AEs'; never summed up to it
    if identity.get("attribution") and claim.get("attribution") and identity["attribution"] != claim["attribution"]:
        bad.append(f"attribution:{identity['attribution']}!={claim['attribution']}")   # 'related' never stands for 'any', nor the reverse
    if claim.get("window") and identity.get("window") and identity["window"] != claim["window"]:
        bad.append(f"window:{identity['window']}!={claim['window']}")
    if claim.get("population_refusal") and identity.get("analysis_set") != "RANDOMIZED":
        bad.append(f"population:{identity.get('analysis_set') or 'ANALYSIS_SET_UNSTATED'}")   # needs evidence of the required set
    if not _timepoint_in(claim.get("timepoint"), identity.get("timepoint")):
        bad.append(f"timepoint:{identity.get('timepoint')}")
    pop = str(claim.get("population") or "").lower()
    if identity["population"] != "AS_REPORTED_UNQUALIFIED" and (not pop or pop not in identity["population"].lower()):
        bad.append(f"population:{identity['population']}")
    want = claim.get("effect_measure")
    got = identity.get("effect_measure")
    if want and got not in (want, "COUNTS" if want in ("RR", "OR", "RD") else None) and got not in (claim.get("permitted_measures") or ()):
        bad.append(f"effect_measure:{got}!={want}")
    if identity.get("comparison") != "TWO_ARMS_NAMED":
        bad.append("comparison")
    if claim.get("design_refusal"):
        if identity["role"] != "EFFECT_ESTIMATE" or not identity.get("adjusted") or not _CLUSTER_MODEL.search(identity.get("model") or ""):
            bad.append("design_variance: no design-adjusted estimate with a model that accounts for the design")
    return bad


# ------------------------------------------------------------------ per-result clauses
# A sentence can carry several results under different labels ('secondary infections 33 vs 43, insulin 47 vs 42, and other serious
# adverse events 5 vs 9'; 'mortality was 6/16 vs 2/14; and serious adverse reactions 1/16 vs 0/14'). Each two-arm result is bound to
# the label of ITS OWN clause; two values pair only if they are the same kind of number, joined by an arm connector, with no clause
# boundary between them (else they are two outcomes, not two arms). Results are never combined across clauses.
# Read spelled integers only in numeric result positions; ordinary endpoint words are never rewritten.
_SMALL_NUMBERS = dict(zip("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(), range(20)))
_TENS = dict(zip("twenty thirty forty fifty sixty seventy eighty ninety".split(), range(20, 100, 10)))
_NUMBER = r"(?:\d[\d,]*|(?:" + "|".join(_TENS) + r")(?:[- ](?:" + "|".join(list(_SMALL_NUMBERS)[1:10]) + r"))?|" + "|".join(_SMALL_NUMBERS) + r"|none)"
_PEOPLE = r"(?:patients?|participants?|subjects?|persons?|people)"
_RESULT_TOKENS = (("of", re.compile(r"\b(" + _NUMBER + r")\s*(?:of|/|out of)\s*(\d[\d,]*)(?:\s*" + _PEOPLE + r")?(?:\s*\(\s*\d+(?:\.\d+)?\s*%\s*\))?", re.I)),
                  ("cnt", re.compile(r"\b(" + _NUMBER + r")\s*(?:" + _PEOPLE + r"\s*(?:assigned to [^;,.()]{1,60})?)?\(\s*(\d+(?:\.\d+)?)\s*%\s*\)", re.I)),
                  ("pct", re.compile(r"(\d+(?:\.\d+)?)\s*%(?!\s*(?:CI|Cl|confidence|credible))")),
                  ("plain", re.compile(r"\b(" + _NUMBER + r")\s+(?:" + _PEOPLE + r"|events?|deaths?|episodes?)\b", re.I)),
                  ("plain", re.compile(r"\b(none)\s+in\s+(?:the\s+)?[^;,.()]{1,60}\b(?:group|arm)\b", re.I)))
_RATE_PAIR = re.compile(r"(\d+(?:\.\d+)?)\s*(?:vs\.?|versus|and)\s*(\d+(?:\.\d+)?)\s*(?:events?\s+)?per\s+(\d[\d,]*)\s+((?:patient|person|participant)[- ]years?)", re.I)
_ARM_CONNECTOR = re.compile(r"compared with|in compare with|versus|\bvs\b\.?|\band\b|\bwhile\b|\bwhereas\b|\bthan\b", re.I)
CLAUSE_BOUNDARY = re.compile(r"[;:]|,\s+and\b|,\s+but\b")


def _int(s: str) -> int:
    if s.lower() == "none":
        return 0
    if re.fullmatch(r"\d[\d,]*", s):
        return int(s.replace(",", ""))
    return sum((_SMALL_NUMBERS | _TENS)[word] for word in re.split(r"[- ]", s.lower()))


def _result_tokens(sentence: str) -> list[dict[str, Any]]:
    # Reserve rates and effect intervals before count scanning; their integers and percentages are not patient counts.
    toks = []
    taken = [(e["start"], e["end"]) for e in _effects(sentence)] + [m.span() for m in _RATE_PAIR.finditer(sentence)]
    for kind, rx in _RESULT_TOKENS:
        for m in rx.finditer(sentence):
            if m.start() and sentence[m.start() - 1] in ".−-":
                continue  # an integer suffix of a decimal or signed quantity is not a count
            if any(m.start() < e and s < m.end() for s, e in taken):
                continue
            taken.append(m.span())
            if kind == "of":
                arm = {"events": _int(m.group(1)), "n": _int(m.group(2))}
                if arm["events"] > arm["n"]:
                    continue
            elif kind == "cnt":
                arm = {"events": _int(m.group(1)), "n": None, "pct": float(m.group(2))}
            elif kind == "pct":
                arm = {"pct": float(m.group(1))}
            else:
                arm = {"events": _int(m.group(1)), "n": None}
            toks.append({"kind": kind, "arm": arm, "start": m.start(), "end": m.end()})
    # Read bare integer contrasts only under an outcome-count cue; decimal, percentage, dose and rate values are excluded.
    for m in re.finditer(r"(?<![\w.,])(" + _NUMBER + r")\s+(?:versus|vs\.?)\s+(" + _NUMBER + r")(?![\w.%]|\s*(?:%|per\b|mg\b|days?\b|years?\b))", sentence, re.I):
        if any(m.start() < e and s < m.end() for s, e in taken):
            continue
        head = re.split(r"[;:]", sentence[:m.start()])[-1]
        if not _OUTCOME.search(head):
            continue
        for j in (1, 2):
            toks.append({"kind": "plain", "arm": {"events": _int(m.group(j)), "n": None},
                         "start": m.start(j), "end": m.end(j)})
    toks.sort(key=lambda t: t["start"])
    # A percentage following an explicit patient predicate qualifies that count, including a spelled count versus none.
    merged = []
    for token in toks:
        if (merged and merged[-1]["kind"] == "plain" and token["kind"] == "pct"
                and re.search(r"\b(?:had|experienced|developed)\b", sentence[merged[-1]["end"]:token["start"]], re.I)
                and not _ARM_CONNECTOR.search(sentence[merged[-1]["end"]:token["start"]])
                and not CLAUSE_BOUNDARY.search(sentence[merged[-1]["end"]:token["start"]])):
            merged[-1]["arm"]["pct"] = token["arm"]["pct"]
            merged[-1]["end"] = token["end"]
        else:
            merged.append(token)
    return merged


# a section heading glued onto the next sentence: a short heading (1-4 words, no verb, no digits) directly followed by a
# capitalised sentence start. Only headings of this closed list are stripped, so ordinary sentence starts are never cut.
_GLUED_HEADING = re.compile(r"^\s*(?:safety(?: outcomes?)?|adverse events?|adverse effects?|harms?|tolerability|primary outcomes?|"
                            r"secondary outcomes?|results|outcomes?|efficacy)\s+(?=[A-Z][a-z])", re.I)


def strip_glued_heading(sentence: str) -> str:
    """'Adverse events Mild abdominal discomfort was reported ...' -> 'Mild abdominal discomfort was reported ...'."""
    m = _GLUED_HEADING.match(sentence or "")
    return sentence[m.end():] if m else sentence


def result_clauses(sentence: str) -> list[dict[str, Any]]:
    """Every two-arm result a sentence states, each with its OWN label (its clause before it, its span, its tail to the next
    boundary or result) and the raw tail an effect + CI may sit in."""
    toks, pairs, i = _result_tokens(sentence), [], 0
    # Preserve an explicitly ordered multi-arm list as one unresolved comparison; never silently select two arms.
    for start in range(len(toks)):
        run = [toks[start]]
        for token in toks[start + 1:]:
            if token["kind"] != run[0]["kind"] or not re.fullmatch(r"\s*,\s*(?:and\s+)?", sentence[run[-1]["end"]:token["start"]]):
                break
            run.append(token)
        if len(run) >= 3 and re.search(r"\brespectively\b", sentence, re.I):
            return [{"kind": run[0]["kind"], "arms": [t["arm"] for t in run], "label": sentence,
                     "span": sentence[run[0]["start"]:run[-1]["end"]], "raw_tail": "", "effects": [],
                     "comparison": "MULTI_ARM_UNRESOLVED"}]
    # A shared value is duplicated only with an explicit distributive group phrase, never for a pooled total.
    shared = set()
    for t in toks:
        tail = sentence[t["end"]:]
        m = re.match(r"\s*(?:of\s+(?:the\s+)?)?(?:" + _PEOPLE + r"\s+)?in\s+(?:each|both)\s+(?:groups?|arms?)\b", tail, re.I)
        if m:
            b = dict(t, end=t["end"] + m.end(), arm=dict(t["arm"]))
            pairs.append((t, b))
            shared.add(t["start"])
    while i + 1 < len(toks):
        a, b = toks[i], toks[i + 1]
        between = sentence[a["end"]:b["start"]]
        if (a["start"] not in shared and b["start"] not in shared
                and (a["kind"] == b["kind"] or {a["kind"], b["kind"]} <= {"cnt", "plain"})
                and len(between) <= 200 and _ARM_CONNECTOR.search(between)
                and not CLAUSE_BOUNDARY.search(between) and not re.search(r"\d", between)):
            pairs.append((a, b))
            i += 2
        else:
            i += 1
    pairs.sort(key=lambda p: p[0]["start"])
    out = []
    for k, (a, b) in enumerate(pairs):
        head = sentence[(pairs[k - 1][1]["end"] if k else 0):a["start"]]
        cuts = list(CLAUSE_BOUNDARY.finditer(head))
        head = head[cuts[-1].end():] if cuts else head
        if k and not cuts and "," in head:
            head = head.rsplit(",", 1)[-1]  # a new numeric predicate after a comma cannot inherit the previous endpoint
        if k and pairs[k - 1][0]["start"] in shared:
            head = re.sub(r"^\s*and\s+", "", head, flags=re.I)
        raw_tail = sentence[b["end"]:(pairs[k + 1][0]["start"] if k + 1 < len(pairs) else len(sentence))]
        stop = CLAUSE_BOUNDARY.search(raw_tail)
        tail = raw_tail[:stop.start()] if stop else raw_tail
        if a["start"] in shared and k + 1 < len(pairs):
            tail = ""  # the next coordinated shared-value predicate belongs to its own result
        # Rates in parentheses describe the same endpoint but have a different unit and representation.
        rates = list(_RATE_PAIR.finditer(raw_tail))
        if rates:
            tail = tail[:max(0, raw_tail.rfind("(", 0, rates[0].start()))]
        effects = []
        cursor = 0
        for eff in _effects(raw_tail):
            bridge = raw_tail[cursor:eff["start"]]
            if not effects:
                # Skip arm suffixes before an opening parenthesis, but never an intervening endpoint after a semicolon.
                if ";" in bridge:
                    bridge = bridge[bridge.find(";") + 1:]
                elif "(" in bridge:
                    bridge = bridge[bridge.find("(") + 1:]
            bridge = _RATE_PAIR.sub("", bridge)
            bridge = re.sub(r"\b(?:incidence|unadjusted|adjusted|marginal|conditional|and)\b", "", bridge, flags=re.I)
            if re.search(r"[a-zA-Z]", bridge):
                break  # another endpoint's clause intervenes: its effect cannot close this result
            effects.append(eff)
            cursor = eff["end"]
        if effects:
            tail = tail[:effects[0]["start"]]
        out.append({"kind": a["kind"], "arms": [a["arm"], b["arm"]], "span": sentence[a["start"]:b["end"]], "raw_tail": raw_tail,
                    "effects": effects, "shared": a["start"] in shared,
                    "label": re.sub(r"\s+", " ", f"{head}{sentence[a['start']:b['end']]}{tail}").strip()})
        for rate in rates:
            out.append({"kind": "rate", "arms": [{"rate": float(rate.group(j)), "per": _int(rate.group(3))} for j in (1, 2)],
                        "span": rate.group(0), "label": head + rate.group(0), "raw_tail": "", "effects": []})
    if not pairs:
        for rate in _RATE_PAIR.finditer(sentence):
            out.append({"kind": "rate", "arms": [{"rate": float(rate.group(j)), "per": _int(rate.group(3))} for j in (1, 2)],
                        "span": rate.group(0), "label": sentence[:rate.end()], "raw_tail": "", "effects": []})
    return out


# ------------------------------------------------------------------ counting unit
# What a count COUNTS is read from the words next to the numbers, never assumed: 'N (x%) patients' / 'N of M participants' / a header
# 'n (%)' or 'no. of patients' count PATIENTS_WITH_EVENT; 'N events' / 'episodes' count EVENTS; 'per 100 patient-years' is a rate.
_UNIT_PY = re.compile(r"\b(?:patient|person|participant)[- ]years?\b|\bper\s+1,?000\s+(?:patient|person)|\bper\s+100\s+(?:patient|person)", re.I)
_NUM = _NUMBER + r"\s*(?:\(\s*[\d.]+\s*%?\s*\)\s*)?"
_UNIT_EVENTS = re.compile(r"\b" + _NUM + r"(?:events?|episodes?|occurrences?)\b|\b(?:number|total) of (?:events|episodes)\b|\bepisodes?\b", re.I)
_UNIT_PATIENTS = re.compile(r"\b" + _NUM + r"(?:of\s+(?:the\s+)?\d[\d,]*\s+)?" + _PEOPLE + r"\b"
                            r"|\b(?:patients|participants|subjects)\s+(?:with|who)\b|\bno\.\s*(?:of\s+)?(?:patients|participants)\b"
                            r"|\bn\s*\(\s*%\s*\)|\bin\s+\d[\d,]*\s+(?:patients|participants)\b"
                            r"|\b\d+(?:\.\d+)?\s*%\s+of\s+(?:the\s+)?(?:patients|participants)\b", re.I)
# Read an explicit patient subject with its clinical predicate, including intervening arm names.
_PATIENT_SUBJECT = re.compile(r"\b" + _PEOPLE + r"\b[^.;]{0,180}\b(?:had|experienced|developed|needed|were hospitalized|died)\b", re.I)
_UNIT_REFUSAL = re.compile(r"\bunique (?:patients|participants)\b|\bdeduplicat\w*|\bparticipant numerator\b|\bepisodes?\b"
                           r"|\bevents?,? (?:rather than|not) (?:unique )?(?:patients|participants)\b|\bpatient[- ]years\b", re.I)


_UNIT_CYCLES = re.compile(r"\b(?:ovulatory |treatment |menstrual |stimulation )?cycles?\b(?!\s+of\s+(?:treatment|therapy))"
                          r"|\bper[- ]cycle\b|\bno\.?\s*of\s*cycles\b", re.I)
_UNIT_PEOPLE = re.compile(r"\b(?:women|men|mothers|girls|boys|infants|neonates|children)\b", re.I)


def unit_of(text: str) -> str | None:
    """... plus CYCLES when the counted thing is a cycle ('ovulatory cycles', 'no. of cycles'); women/men are participants."""
    t = text or ""
    if _UNIT_CYCLES.search(t) and not _UNIT_PEOPLE.search(t):
        return "CYCLES"
    if _UNIT_PEOPLE.search(t) and not _UNIT_CYCLES.search(t):
        return "PATIENTS_WITH_EVENT"
    return _unit_of_counts(t)


def _unit_of_counts(text: str) -> str | None:
    """PATIENTS_WITH_EVENT, EVENTS, PATIENT_YEARS, or None when the text does not state what its numbers count."""
    t = text or ""
    if _UNIT_PY.search(t):
        return "PATIENT_YEARS"
    ev, pt = _UNIT_EVENTS.search(t), (_UNIT_PATIENTS.search(t) or _PATIENT_SUBJECT.search(t))
    if ev and pt:                                    # 'adverse EVENTS occurred in 2697 (77.2%) PATIENTS': the unit is what the NUMBER is of
        ev_num = re.search(r"\d[\d,]*\s*(?:\(\s*[\d.]+\s*%?\s*\)\s*)?(?:events?|episodes?)\b", t, re.I)
        return "EVENTS" if ev_num and not re.search(r"\d[\d,]*\s*(?:\(\s*[\d.]+\s*%?\s*\)\s*)?(?:patients|participants)\b", t, re.I) else "PATIENTS_WITH_EVENT"
    if pt:
        return "PATIENTS_WITH_EVENT"
    if ev:
        return "EVENTS"
    return None


_NONSERIOUS = re.compile(r"\bnon[- ]?serious\b", re.I)
_DISCONTINUATION = re.compile(r"\bdiscontinu\w*|\bwithdr[ae]w\w*\s+(?:from|owing|due|because)|\bstopped (?:study |the )?(?:drug|treatment)\b", re.I)


_POPULATION_REFUSAL = re.compile(r"\bsafety population\b|\btreated (?:safety )?population\b|\btreatment received\b|\bas[- ]treated\b"
                                 r"|\bper[- ]protocol\b|\brandomi[sz]ed (?:groups?|population|arms?)\b.{0,40}\brequired\b"
                                 r"|\brather than the randomi[sz]ed\b|\bintention[- ]to[- ]treat\b.{0,40}\brequired\b|\banalysis set\b", re.I)
_SET_RANDOMIZED = re.compile(r"\bintention[- ]to[- ]treat\b|\bITT\b|\ball (?:patients who (?:were|underwent) )?randomi[sz]ed\b"
                             r"|\brandomi[sz]ed (?:population|groups?|patients)\b", re.I)
_SET_SAFETY = re.compile(r"\bsafety (?:population|analysis set)\b|\bas[- ]treated\b|\breceived at least one dose\b|\btreated patients\b"
                         r"|\baccording to (?:the )?treatment received\b|\bper[- ]protocol\b", re.I)


def analysis_set_of(text: str) -> str | None:
    """RANDOMIZED / SAFETY_OR_AS_TREATED as the text STATES it; None when it does not say which set its numbers are from."""
    if _SET_SAFETY.search(text or ""):
        return "SAFETY_OR_AS_TREATED"
    if _SET_RANDOMIZED.search(text or ""):
        return "RANDOMIZED"
    return None


_ATTR_DISC = re.compile(r"\bleading to (?:the )?(?:permanent |study[- ]drug |treatment |trial[- ]regimen )?discontinuation\b"
                        r"|\bled to (?:the )?(?:permanent )?discontinuation\b|\bresulting in discontinuation\b"
                        r"|\b[a-z]+[- ]related (?:treatment |study[- ]drug |permanent )?discontinuation\b"
                        r"|\bdiscontinu\w*(?:\s+[\w-]+){0,4}?\s+(?:due to|because of|owing to)\b", re.I)   # 'discontinued treatment owing to ...'
_ATTR_RELATED = re.compile(r"\brelated to (?:the )?(?:trial|study|investigational)?\s*(?:regimen|drug|treatment|medication|product)\b"
                           r"|\b(?:drug|treatment|study[- ]drug|regimen|trial[- ]regimen)[- ]related\b|\bcausally related\b"
                           r"|\bconsidered (?:by the investigators? )?(?:to be )?related\b|\badverse (?:drug )?reactions?\b", re.I)
_ATTR_SERIOUS = re.compile(r"(?<!non-)(?<!non )\bserious\b", re.I)
_WINDOW_TE = re.compile(r"\btreatment[- ]emergent\b|\bduring (?:the )?(?:double-blind )?treatment(?: period)?\b|\bon[- ]treatment\b", re.I)
_WINDOW_OTHER = re.compile(r"\bpost[- ]treatment\b|\bafter (?:the end of )?treatment\b|\bfollow[- ]up period\b", re.I)
_CONSEQUENCE = re.compile(r"\b(?:leading to|resulting in|requiring|that led to|causing)\s+(?:hospitali[sz]ation|death|dialysis|"
                          r"emergency|intensive care)", re.I)


# an organ/system or symptom-class word directly qualifying 'adverse event(s)' ('gastrointestinal adverse events', 'GI AEs',
# 'cardiac adverse events'); reporting words (any, all, total, serious, treatment-emergent) are attribution/scope, not subcategory
_AE_SUBCATEGORY = re.compile(r"\b(gastro-?intestinal|GI|cardiac|cardiovascular|renal|kidney|hepatic|liver|neurologic\w*|psychiatric|"
                             r"respiratory|skin|dermatologic\w*|musculoskeletal|infectious|metabolic|ocular|eye|injection[- ]site)\s+"
                             r"(?:adverse (?:events?|effects?|reactions?)|AEs?)\b", re.I)
_GENERIC_AE_NAME = re.compile(r"\badverse (?:events?|effects?|reactions?)\b|\bAEs?\b", re.I)


def attribution_of(text: str) -> str:
    """Which reporting category a safety count belongs to; INVESTIGATOR_REPORTED_ANY when the text adds no qualifier."""
    t = text or ""
    if _ATTR_DISC.search(t):
        return "LEADING_TO_DISCONTINUATION"
    if _ATTR_RELATED.search(t):
        return "TREATMENT_RELATED"
    if _ATTR_SERIOUS.search(t):
        return "SERIOUS"
    return "INVESTIGATOR_REPORTED_ANY"


def window_of(text: str) -> str | None:
    if _WINDOW_OTHER.search(text or ""):
        return "POST_TREATMENT"
    return "TREATMENT_EMERGENT" if _WINDOW_TE.search(text or "") else None


def definition_of(label: str, outcome_name: str) -> str:
    """AS_NAMED, or why this label is a different category than the outcome: RESIDUAL ('other serious adverse events') or RESTRICTED
    ('serious ...' where the outcome is not)."""
    if _RESIDUAL.search(label or "") and not _RESIDUAL.search(outcome_name or ""):
        return "RESIDUAL"
    sub = _AE_SUBCATEGORY.search(label or "")
    if sub and _GENERIC_AE_NAME.search(outcome_name or "") and sub.group(1).lower()[:5] not in (outcome_name or "").lower():
        return "RESTRICTED"                          # 'GI adverse events leading to discontinuation' is a subset of all AE discontinuations
    want = _AE_SUBCATEGORY.search(outcome_name or "")
    if want and _GENERIC_AE_NAME.search(label or "") and want.group(1).lower()[:5] not in (label or "").lower():
        return "BROADER"                             # and the all-cause row is never the GI-specific outcome (a superset, not it)
    if _CONSEQUENCE.search(label or "") and not _CONSEQUENCE.search(outcome_name or ""):
        return "RESTRICTED"                          # 'no hyperkalaemia leading to hospitalisation or death' is not 'no hyperkalaemia'
    if _NONSERIOUS.search(label or "") and not _NONSERIOUS.search(outcome_name or ""):
        return "RESTRICTED"                          # the complement of 'serious', never the serious (or any) total
    if _DISCONTINUATION.search(label or "") and not _DISCONTINUATION.search(outcome_name or ""):
        return "RESTRICTED"                          # 'discontinued treatment owing to GI events' is a discontinuation outcome
    # Read an explicit cause of discontinuation as a subset, never as the all-cause discontinuation total.
    cause = r"\b(?:necessitated|due to|owing to|because of)\b"
    if _DISCONTINUATION.search(label or "") and re.search(cause, label or "", re.I) and not re.search(cause, outcome_name or "", re.I):
        return "RESTRICTED"
    if _RESTRICTING.search(label or "") and not _RESTRICTING.search(outcome_name or ""):
        return "RESTRICTED"
    if re.search(r"\bnon[- ]?major\b", label or "", re.I) and not re.search(r"\bnon[- ]?major\b", outcome_name or "", re.I):
        return "RESTRICTED"                          # 'clinically relevant non-major bleeding' is the complement of major, never it
    return "AS_NAMED"
