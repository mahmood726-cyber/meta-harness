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

EXACT_TARGET = "EXACT_TARGET"
NEAR_MATCH = "NEAR_MATCH"
DIFFERENT_OUTCOME = "DIFFERENT_OUTCOME"
EXACT_TARGET_IN_SOURCE_NOT_HELD = "EXACT_TARGET_IN_SOURCE_NOT_HELD"
ENDPOINT_UNBOUND = "ENDPOINT_UNBOUND"

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


def _resolve_reference(rs: str, pool: list[dict[str, Any]]) -> dict[str, Any]:
    """Select the definition the result REFERS to. Returns {selected, record, how} where record carries
    definition_candidates / endpoint_reference / selected_definition / unresolved_alternatives."""
    ref = _reference_of(rs)
    cands = []
    seen = set()
    for d in pool:
        key = re.sub(r"\W+", " ", d["span"].lower()).strip()
        if key in seen:
            continue            # an identical repeated definition is a harmless duplicate, not a second endpoint
        seen.add(key)
        cands.append(d)
    record = {"definition_candidates": [{"span": d["span"], "components": sorted(d["components"]),
                                         "ordinal": d.get("ordinal"), "timepoint": d.get("timepoint"),
                                         "population": d.get("population")} for d in cands],
              "endpoint_reference": ref, "selected_definition": None, "unresolved_alternatives": []}
    how = []
    narrowed = list(cands)
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


def _components_from_text(text: str | None, expand_named_composites: bool = True) -> set[str]:
    """Components a span NAMES.  With expand_named_composites (default, definition spans) a bare
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
    if "coronary revascularization" in s or "revascularisation" in s:
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
        # a RESULT sentence (carries an effect+CI or arm counts) is never a definition span, even when
        # it mentions a component in passing ("... a primary outcome event occurred in 458 of 3686 ...
        # (hazard ratio 0.87 ...), with ... hospitalization for heart failure")
        if extract.extract_effect(x) or _EFFECT_RE.search(x) or re.search(r"\d+ of \d+", xl):
            continue
        comps = _components_from_text(x, expand_named_composites=True)
        if not comps:
            continue
        q = _QUALIFIER_RX.search(xl)
        ref = _reference_of(x)
        out.append({
            "span": x.strip(),
            "components": comps,
            "ordinal": ref["ordinal"], "timepoint": ref["timepoint"], "population": ref["population"],
            "primary": bool(q and q.group("pri")) or bool(extract._ANCHOR_RX.search(xl)) or bool(re.search(r"\bprimary (?:[a-z-]+ ){0,3}?(?:measure|variable)s?\b", xl)),
            "secondary": bool(q and q.group("sec")),
            "mace": bool(_MACE_RX.search(xl)),
        })
    return out


def bind_result_span(abstract: str, result_span: str | None) -> dict[str, Any]:
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
                    "endpoint_definition_span": d["span"], "components": set(d["components"]),
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
    cls = _classify(spec, binding["endpoint_definition_span"], components=binding["components"])
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
    cls = _classify(spec, binding["endpoint_definition_span"], components=binding["components"])
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
    if cls in (EXACT_TARGET, NEAR_MATCH, DIFFERENT_OUTCOME, ENDPOINT_UNBOUND) and not hand_binding.is_hand_row(row):
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
        return sorted(_components_from_text(" ; ".join(map(str, explicit))) or {str(x) for x in explicit})
    return sorted(_components_from_text(spec.get("name")))


def _keyword_family_match(spec: dict[str, Any], text: str | None) -> bool:
    s = _fold(text)
    for kw in spec.get("keywords") or []:
        k = _fold(kw)
        if len(k) > 3 and k in s:
            return True
    canon = set(canonical_components(spec))
    return bool(canon and (canon & _components_from_text(text)))


def _classify(spec: dict[str, Any], text: str | None, components: set[str] | None = None) -> dict[str, Any]:
    canon = set(canonical_components(spec))
    cand = set(components or _components_from_text(text))
    if not canon:
        cls = EXACT_TARGET if _keyword_family_match(spec, text) else DIFFERENT_OUTCOME
        return {
            "target_endpoint_class": cls,
            "target_components": sorted(cand),
            "extra_components": [],
            "missing_components": [],
            "component_distance": 0 if cls == EXACT_TARGET else 999,
        }
    cand_for_match = set(cand)
    if "cardiovascular death" in canon and "coronary heart disease death" in cand:
        cand_for_match.add("cardiovascular death")
    extra = sorted(
        c for c in (cand - canon)
        if not (c == "coronary heart disease death" and "cardiovascular death" in canon)
    )
    missing = sorted(canon - cand_for_match)
    if not extra and not missing:
        cls = EXACT_TARGET
    elif cand and (not missing or not extra):
        cls = NEAR_MATCH
    else:
        cls = DIFFERENT_OUTCOME
    return {
        "target_endpoint_class": cls,
        "target_components": sorted(cand),
        "extra_components": extra,
        "missing_components": missing,
        "component_distance": len(extra) + len(missing),
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
        base.update(_classify(spec, text))
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
