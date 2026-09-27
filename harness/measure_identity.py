"""MEASURE IDENTITY from the statistical MODEL and the outcome process, never from the abbreviation alone
(NOAC-AF review countercheck, 2026-09-27, hash f1867881; retrospective, Dispatch under Mahmood's delegation).

RE-LY (PMID 19717844) publishes "relative risk, 0.66; 95% CI, 0.53 to 0.82" for stroke or systemic embolism. Its held registry
record (NCT00262600, outcome 258397029 "Yearly Event Rate for Composite Endpoint of Stroke/SEE") types both analyses of that
outcome "Cox Proportional Hazard" (0.65 and 0.9 -- the registry's updated analysis), and the abstract reports rates per year. The
number is a hazard ratio in substance; the source's word "relative risk" is kept as a separate field. The "3 HR + 1 RR" mixture
warning on the served page is therefore false. An ordinary count-based RR stays an RR.

CI PROVENANCE: ENGAGE AF-TIMI 48 reports HR 0.87 with a 97.5% CI (0.73 to 1.04). The published level, the published interval, the
transform and its SE are stored; the pooled ~95% interval (0.745 to 1.016, SE 0.078953) is DERIVED and is never presented as a
published 95% CI.
"""
from __future__ import annotations

import gzip
import json
import math
import os
import re
from statistics import NormalDist
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_SOURCE_TERMS = (("hazard ratio", re.compile(r"(?i)\bhazard\s+ratios?\b|(?-i:\bHR\b)")),
                 ("relative risk", re.compile(r"(?i)\brelative\s+risks?\b|(?-i:\bRR\b)")),
                 ("risk ratio", re.compile(r"(?i)\brisk\s+ratios?\b")),
                 ("odds ratio", re.compile(r"(?i)\bodds\s+ratios?\b|(?-i:\bOR\b)")),
                 ("rate ratio", re.compile(r"(?i)\b(?:incidence\s+)?rate\s+ratios?\b|(?-i:\bIRR\b)")))
_MODELS = (("COX", re.compile(r"(?i)\bcox\b|proportional[- ]hazards?")),
           ("POISSON", re.compile(r"(?i)\bpoisson\b|negative\s+binomial")),
           ("LOGISTIC", re.compile(r"(?i)logistic\s+regression")),
           ("LOG_BINOMIAL", re.compile(r"(?i)log[- ]binomial")),
           ("MANTEL_HAENSZEL", re.compile(r"(?i)mantel[- ]haenszel|cochran")))
_MODEL_MEASURE = {"COX": "HAZARD_RATIO", "POISSON": "RATE_RATIO", "LOGISTIC": "ODDS_RATIO", "LOG_BINOMIAL": "RISK_RATIO"}
_TERM_MEASURE = {"hazard ratio": "HAZARD_RATIO", "relative risk": "RISK_RATIO", "risk ratio": "RISK_RATIO",
                 "odds ratio": "ODDS_RATIO", "rate ratio": "RATE_RATIO"}
_SCALE = {"HAZARD_RATIO": "HR", "RISK_RATIO": "RR", "ODDS_RATIO": "OR", "RATE_RATIO": "RATE_RATIO"}
_PER_TIME = re.compile(r"(?i)%\s*per\s+(?:patient-)?year|per\s+100\s+(?:patient|person)[- ]years|\bannuali[sz]ed\s+rate|"
                       r"\byearly\s+event\s+rate|\btime\s+to\s+(?:the\s+)?first")
_ABBREV = {"see": "systemic embolism", "mi": "myocardial infarction", "vte": "venous thromboembolism",
           "hf": "heart failure", "cv": "cardiovascular"}
_STOP = {"or", "and", "of", "the", "a", "an", "to", "for", "with", "by", "in", "composite", "endpoint", "end", "point",
         "outcome", "rate", "yearly", "event", "events", "first", "time", "any"}


def source_term(text: str | None) -> str | None:
    for term, rx in _SOURCE_TERMS:
        if rx.search(text or ""):
            return term
    return None


def _words(text: str) -> set[str]:
    toks = re.split(r"[^a-z0-9]+", (text or "").lower())
    out = []
    for t in toks:
        out.extend(_ABBREV.get(t, t).split())
    return {t for t in out if t and t not in _STOP and len(t) > 1}


def registry_models(slug: str | None) -> dict[str, list[dict[str, Any]]]:
    """{NCT: [{outcome_id, outcome_title, model, param_type, value, analysis_id}]} from the held AACT rows
    (cache/<slug>/family_registry.rows.json.gz): outcome_analyses joined to outcomes."""
    if not slug:
        return {}
    p = os.path.join(ROOT, "cache", slug, "family_registry.rows.json.gz")
    try:
        rows = json.loads(gzip.open(p, "rt", encoding="utf-8").read())
    except (OSError, ValueError):
        return {}
    titles = {(r.get("nct_id"), str((r.get("inline") or {}).get("id"))): (r.get("inline") or {}).get("title")
              for r in rows if r.get("table") == "outcomes"}
    out: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        if r.get("table") != "outcome_analyses":
            continue
        inl = r.get("inline") or {}
        pt = str(inl.get("param_type") or "")
        model = next((m for m, rx in _MODELS if rx.search(pt)), None)
        out.setdefault(str(r.get("nct_id") or "").upper(), []).append(
            {"outcome_id": str(inl.get("outcome_id")), "outcome_title": titles.get((r.get("nct_id"), str(inl.get("outcome_id")))),
             "model": model, "param_type": pt, "value": inl.get("param_value"), "analysis_id": str(inl.get("id"))})
    return out


def classify(row: dict[str, Any], outcome_name: str | None, nct: str | None, reg: dict[str, list[dict[str, Any]]],
             held_text: str | None = None) -> dict[str, Any]:
    """The measure from the MODEL (row text, else the same trial's registry analysis of the same outcome), the outcome process,
    and the source's own term kept separately. With no stated model, the measure is the source term's -- recorded as such."""
    src = str(row.get("source") or "")
    term = source_term(src)
    model, basis = None, None
    for m, rx in _MODELS:
        if rx.search(src):
            model, basis = m, "the row's source text"
            break
    if model is None and nct:
        want = _words(outcome_name or "")
        for a in reg.get(str(nct).upper(), []):
            if a["model"] and want and want <= _words(a.get("outcome_title") or ""):
                model = a["model"]
                basis = (f"registry analysis {a['analysis_id']} of {nct} outcome {a['outcome_id']} "
                         f"'{a['outcome_title']}': {a['param_type']}")
                break
    process = "TIME_TO_EVENT_RATE" if _PER_TIME.search(src + " " + (held_text or "")) else "NOT_STATED"
    if model in _MODEL_MEASURE:
        measure = _MODEL_MEASURE[model]
    else:
        measure = _TERM_MEASURE.get(term or "", None)
    return {"measure": measure, "scale": _SCALE.get(measure) if measure else None, "source_term": term,
            "model": model or "NOT_STATED", "model_basis": basis, "outcome_process": process,
            "rule": "measure from the statistical model and outcome process; the source's wording is kept, never decisive alone"}


# --------------------------------------------------------------------------- CI level provenance
_LEVEL = re.compile(r"(?i)(\d{2}(?:\.\d+)?)\s*%\s*(?:confidence\s+interval|CI)[^0-9]{0,12}(\d+(?:\.\d+)?)\s*(?:to|-|–|,)\s*(\d+(?:\.\d+)?)")


def ci_level_provenance(row: dict[str, Any]) -> dict[str, Any] | None:
    """For a ratio whose source states a CI at a level other than 95%: the published level and interval, the transform, the SE,
    the derived ~95% interval, and whether the served interval is that derived one. None when the source's CI is 95% or absent."""
    m = _LEVEL.search(str(row.get("source") or ""))
    if not m:
        return None
    level, lo, hi = float(m.group(1)), float(m.group(2)), float(m.group(3))
    if abs(level - 95.0) < 1e-9 or not (lo > 0 and hi > lo) or row.get("effect") is None:
        return None
    z = NormalDist().inv_cdf(0.5 + level / 200.0)
    se = (math.log(hi) - math.log(lo)) / (2 * z)
    est = float(row["effect"])
    d_lo, d_hi = math.exp(math.log(est) - 1.959964 * se), math.exp(math.log(est) + 1.959964 * se)
    served = (row.get("ci_low"), row.get("ci_high"))
    if served == (lo, hi):
        state = "PUBLISHED_NON_95_SERVED_AS_IS"
    elif served[0] is not None and abs(served[0] - d_lo) < 5e-4 and abs(served[1] - d_hi) < 5e-4:
        state = "DERIVED_95_FROM_PUBLISHED_LEVEL"
    else:
        state = "SERVED_INTERVAL_UNEXPLAINED"
    return {"published": {"level": level, "ci_low": lo, "ci_high": hi, "span": m.group(0)},
            "transform": (f"SE = (ln {hi} - ln {lo}) / (2 x z_{{{0.5 + level / 200:.4f}}} = {z:.4f}); "
                          f"~95% = exp(ln {est} +/- 1.96 x SE)"),
            "se": round(se, 6), "derived_95": {"ci_low": round(d_lo, 4), "ci_high": round(d_hi, 4)},
            "served": {"ci_low": served[0], "ci_high": served[1]}, "state": state,
            "presentation": f"published {level:g}% CI {lo}-{hi}; the pooled interval is a DERIVED ~95% interval, not a published 95% CI"}
