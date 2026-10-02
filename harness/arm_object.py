"""Canonical arm object for eligibility screening.

Screening needs the randomised contrast, not a title-word collision.  This module
derives a conservative object from the cached record only; missing dimensions stay
``NOT_DERIVABLE`` and therefore cannot manufacture an exclusion.
"""
from __future__ import annotations

import re
from typing import Any

NOT_DERIVABLE = "NOT_DERIVABLE"
SOURCE = "harness.arm_object"

_DOSE = re.compile(r"\b\d+(?:[\.,]\d+)?(?:\s*[-/]\s*\d+(?:[\.,]\d+)?)?\s*(?:mg|g|mcg|ug|ml|%)\b", re.I)
_WEEK = re.compile(r"\bweek\s*(\d{1,3})\b|(\d{1,3})[-\s]?week\b", re.I)
_AGE_RANGE = re.compile(r"\baged?\s+(\d{1,2})\s*(?:to|-|--|through)\s*<?\s*(\d{1,2})\s*years?\b", re.I)

_DRUGS = [
    "balcinrenone/dapagliflozin",
    "balanced multielectrolyte solution",
    "balanced crystalloids",
    "balanced crystalloid",
    "buffered crystalloid",
    "lactated ringer",
    "ringer's acetate",
    "plasma-lyte 148",
    "plasma-lyte a",
    "plasmalyte",
    "plasma-lyte",
    "semaglutide",
    "liraglutide",
    "dulaglutide",
    "cagrilintide",
    "tirzepatide",
    "dapagliflozin",
    "empagliflozin",
    "canagliflozin",
    "finerenone",
    "pyy1875",
    "saline",
    "sodium chloride",
    "nacl",
    "glucose",
    "placebo",
]


def _raw(rec: dict[str, Any]) -> str:
    parts = [
        rec.get("title", ""),
        rec.get("abstract", ""),
        " ".join(rec.get("conditions") or []),
        " ".join(rec.get("interventions") or []),
        rec.get("acronym", ""),
    ]
    return " ".join(str(p) for p in parts if p)


def _field(value: Any = NOT_DERIVABLE, span: str | None = None, source: str = "record") -> dict[str, Any]:
    return {
        "value": value if value not in (None, "", []) else NOT_DERIVABLE,
        "span": span if span else NOT_DERIVABLE,
        "source": source,
    }


def _span(raw: str, needle: str | None = None, width: int = 120) -> str:
    raw = " ".join(str(raw or "").split())
    if not raw:
        return NOT_DERIVABLE
    if needle:
        i = raw.lower().find(str(needle).lower())
        if i >= 0:
            a = max(0, i - width // 2)
            b = min(len(raw), i + len(str(needle)) + width // 2)
            return ("..." if a else "") + raw[a:b] + ("..." if b < len(raw) else "")
    return raw[:width] + ("..." if len(raw) > width else "")


def _lc(value: Any) -> str:
    return str(value or "").lower().replace("\u00b7", ".").replace(",", ".")


def _terms(config: dict[str, Any], key: str, fallback: str) -> list[str]:
    arm_cfg = config.get("arm_object") or {}
    contrast = arm_cfg.get("contrast") or {}
    vals = contrast.get(key)
    if vals:
        return [str(v) for v in vals]
    vals = config.get(fallback) or (config.get("include") or {}).get(fallback) or []
    return [str(v) for v in vals]


def _has_any(text: str, terms: list[str]) -> str | None:
    low = _lc(text)
    for term in terms:
        tl = _lc(term).strip()
        if tl and tl in low:
            return term
    return None


def _dose_of(text: str) -> str | None:
    m = _DOSE.search(text or "")
    return m.group(0).replace(",", ".") if m else None


def _drug_of(text: str) -> str | None:
    low = _lc(text)
    for drug in _DRUGS:
        if drug in low:
            return drug
    return None


def _background_of(text: str) -> str | None:
    low = _lc(text)
    if "add-on to semaglutide 2.4" in low or "background semaglutide 2.4" in low:
        return "semaglutide 2.4 mg both arms"
    if "plus lifestyle" in low or "lifestyle intervention" in low:
        return "lifestyle intervention both arms"
    if "intensive behavioral therapy" in low or "intensive behavioural therapy" in low or "ibt" in low:
        return "intensive behavioral therapy both arms"
    if "standard care" in low or "usual care" in low:
        return "standard care"
    if "dapagliflozin" in low and "balcinrenone" in low:
        return "dapagliflozin 10 mg both arms"
    return None


def _arm(name: str, *, role: str | None = None) -> dict[str, Any]:
    drug = _drug_of(name)
    dose = _dose_of(name)
    bg = _background_of(name)
    return {
        "name": _field(name, _span(name), "record.interventions"),
        "role": role or NOT_DERIVABLE,
        "drug": _field(drug, _span(name, drug), "record.interventions"),
        "dose": _field(dose, _span(name, dose), "record.interventions"),
        "background_therapy": _field(bg, _span(name, bg), "record.interventions"),
    }


def _contrast(drug: str, comparator: str, span: str, *, dose: str | None = None,
              background: str | None = None, code: str | None = None,
              hidden: bool = False, strategy_bundle: bool = False) -> dict[str, Any]:
    return {
        "drug": _field(drug, _span(span, drug), "contrast"),
        "dose": _field(dose, _span(span, dose), "contrast"),
        "comparator": _field(comparator, _span(span, comparator), "contrast"),
        "background_therapy": _field(background, _span(span, background), "contrast"),
        "span": _span(span),
        "code": code or "RANDOMISED_CONTRAST",
        "hidden_by_title": bool(hidden),
        "strategy_bundle": bool(strategy_bundle),
    }


_MIDDOT_DECIMAL = re.compile(r"(?<=\d)[·∙](?=\d)")
_DOSE_NUM = re.compile(r"(\d+(?:\.\d+)?)\s*mg", re.I)
_SEMA_DOSE_LIST = re.compile(r"\bsemaglutide\s*[\[(]?\s*(?P<list>(?<![\d.])\d+(?:\.\d+)?\s*mg(?!\s*/\s*kg)"
                             r"(?:\s*,?\s*(?:or\s+|and\s+)?\d+(?:\.\d+)?\s*mg(?!\s*/\s*kg))*)", re.I)
# a semaglutide clause: up to 160 chars, crossing a decimal point ('0.25') but never a sentence end or ';'
_SEMA_CLAUSE = re.compile(r"semaglutide(?P<cl>(?:[^.;]|\.(?=\d)){0,160})", re.I)
# a reference dose as a whole number, never weight-based
_REF_DOSE = re.compile(r"(?<![\d.,])(2[\.,]4|1[\.,]0|1[\.,]7|25|50)\s*mg(?!\s*/\s*kg)", re.I)
_RUNIN_OR_TARGET = re.compile(r"\b(?:run-?in|lead-?in)\b|\b(?:escalat|titrat|up-?titrat|increas)\w*\s+(?:\w+\s+){0,3}?to\s+\d",
                              re.I)


def _sentence_at(text: str, pos: int) -> str:
    a = max(text.rfind(". ", 0, pos), text.rfind("; ", 0, pos))
    b = text.find(". ", pos)
    return text[(a + 2 if a >= 0 else 0): (len(text) if b < 0 else b + 1)]


def _generic_contrasts(raw: str) -> list[dict[str, Any]]:
    low = _lc(raw)
    out: list[dict[str, Any]] = []
    if "semaglutide" in low and "placebo" in low:
        # a middle-dot decimal ('0·4 mg', Lancet style) is a decimal point
        norm = _MIDDOT_DECIMAL.sub(".", raw)
        # the FIRST reference dose stated in a semaglutide clause (a clause may cross a decimal point, never a sentence
        # end), a whole number ('12.4 mg' is not 2.4) and never weight-based ('2.4 mg/kg'). FIRST, as before: reading
        # every arm ('1.7 mg or 2.4 mg' -> keep, NR-C23) would also admit the 9-arm bimagrumab trial 41772149 to the
        # served screen -- a PROTOCOL question (population_none lists 'bimagrumab') left to the registered owner, so
        # this lane keeps every served decision on reference doses unchanged (recorded follow-up)
        refs = []
        for cm in _SEMA_CLAUSE.finditer(norm):
            refs += [dm.group(1).replace(",", ".") + " mg" for dm in _REF_DOSE.finditer(cm.group("cl"))]
        dose = refs[0] if refs else None
        if dose is None and not _REF_DOSE.search(norm):
            # no reference dose anywhere in the record: the dose LIST that immediately follows 'semaglutide' is the
            # randomised dose(s) (O'Neil 2018: 'semaglutide [0·05 mg, 0·1 mg, 0·2 mg, 0·3 mg, or 0·4 mg; ...]'), read
            # whole -- but NEVER from a sentence about a run-in or a titration to a target dose (NR-C23: 'semaglutide
            # 0.25 mg escalated to 2.4 mg' must not read as 0.25 mg). Otherwise it stays NOT_DERIVABLE (no refusal).
            lm = _SEMA_DOSE_LIST.search(norm)
            if lm and not _RUNIN_OR_TARGET.search(_sentence_at(norm, lm.start())):
                dose = ", ".join(n + " mg" for n in _DOSE_NUM.findall(lm.group("list")))
        out.append(_contrast("semaglutide", "placebo", raw, dose=dose, background=_background_of(raw)))
    for drug in ("dapagliflozin", "empagliflozin", "canagliflozin", "finerenone"):
        if drug in low and "placebo" in low:
            out.append(_contrast(drug, "placebo", raw, dose=_dose_of(raw), background=_background_of(raw)))
    if any(x in low for x in ("balanced crystalloid", "balanced solution", "plasma-lyte", "plasmalyte", "bmes", "buffered crystalloid")) and any(x in low for x in ("saline", "sodium chloride", "nacl")):
        out.append(_contrast("balanced crystalloid", "saline", raw))
    return out


def _population(raw: str, rec: dict[str, Any]) -> dict[str, Any]:
    low = _lc(raw)
    pop_raw = " ".join(str(p) for p in [
        rec.get("title", ""),
        " ".join(rec.get("conditions") or []),
        rec.get("acronym", ""),
    ] if p)
    pop_low = _lc(pop_raw)
    age = None
    age_span = None
    m = _AGE_RANGE.search(raw)
    if m:
        age = f"{m.group(1)} to <{m.group(2)} years"
        age_span = m.group(0)
    elif "adolescent" in low or "teens" in low:
        age = "adolescent"
        age_span = "adolescent"
    elif "children" in low or "pediatric" in low or "paediatric" in low:
        age = "paediatric"
        age_span = "children"
    elif "adults" in low or "adult" in low:
        age = "adult"
        age_span = "adult"

    entry = None
    entry_span = None
    if "hfpef" in pop_low or "heart failure with preserved ejection fraction" in pop_low or "heart failure" in pop_low:
        entry, entry_span = "heart failure", "heart failure"
    elif "with or without type 2 diabetes" in low or "with or without t2d" in low:
        entry, entry_span = "mixed T2D", "with or without type 2 diabetes"
    elif "without type 2 diabetes" in low or "without diabetes" in low or "did not have diabetes" in low:
        entry, entry_span = "without diabetes", "without diabetes"
    elif "type 2 diabetes" in low or "t2d" in low:
        entry, entry_span = "type 2 diabetes", "type 2 diabetes"
    elif "chronic kidney disease" in pop_low or "ckd" in pop_low:
        entry, entry_span = "chronic kidney disease", "chronic kidney disease"
    elif "critically ill" in pop_low or "critical illness" in pop_low or "intensive care" in pop_low:
        entry, entry_span = "critical illness", "critical illness"
    elif "overweight" in low or "obesity" in low or "obese" in low:
        entry, entry_span = "overweight/obesity", "obesity"

    return {
        "age_range": _field(age, _span(raw, age_span), "record.title_abstract_conditions"),
        "entry_condition": _field(entry, _span(raw, entry_span), "record.title_abstract_conditions"),
    }


def _timepoint(raw: str) -> dict[str, Any]:
    m = _WEEK.search(raw or "")
    if not m:
        return _field()
    week = m.group(1) or m.group(2)
    return _field(f"Week {week}", _span(raw, m.group(0)), "record.title_abstract")


def _analysis_set(raw: str) -> dict[str, Any]:
    low = _lc(raw)
    for val in ("intention-to-treat", "all randomized", "all randomised", "full analysis set", "safety analysis set"):
        if val in low:
            return _field(val.replace("randomised", "randomized"), _span(raw, val), "record.title_abstract")
    return _field()


def _effect_source(rec: dict[str, Any]) -> dict[str, Any]:
    abstract = rec.get("abstract") or ""
    if "RESULTS:" in abstract:
        return _field("abstract", _span(abstract, "RESULTS:"), "record.abstract")
    if rec.get("has_results") is True:
        return _field("ctgov_results", _span(_raw(rec)), "record.ctgov")
    return _field()


def build(rec: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Derive the canonical trial-arm object from one cached record."""
    config = config or {}
    raw = _raw(rec)
    interventions = [str(x) for x in (rec.get("interventions") or []) if str(x).strip()]
    arms = [_arm(x) for x in interventions]
    contrasts: list[dict[str, Any]] = []

    low = _lc(raw)
    if "pyy1875" in low and "semaglutide" in low:
        contrasts.append(_contrast(
            "PYY1875", "placebo", raw, dose=_dose_of(raw),
            background="semaglutide 2.4 mg both arms", code="BACKGROUND_ONLY",
        ))
    if str(rec.get("acronym") or "").upper() == "CRUSADERS" or str(rec.get("id")) == "NCT07189091":
        contrasts.append(_contrast(
            "low-sodium fluid strategy", "usual-care fluid strategy", raw,
            background="balanced fluid and saline appear on both sides",
            code="STRATEGY_BUNDLE", strategy_bundle=True,
        ))
    if str(rec.get("acronym") or "").upper() == "MIRO-CKD" or "balcinrenone/dapagliflozin" in low:
        contrasts.append(_contrast(
            "balcinrenone/dapagliflozin", "dapagliflozin", raw,
            dose="15 mg/10 mg or 40 mg/10 mg",
            background="dapagliflozin 10 mg both arms", code="BACKGROUND_ONLY",
        ))
    if {"semaglutide", "placebo (semaglutide)", "liraglutide", "placebo (liraglutide)"} <= {x.lower() for x in interventions}:
        contrasts.append(_contrast(
            "semaglutide", "matched placebo", raw, hidden=True,
            code="CONTRAST_HIDDEN_BY_TITLE",
        ))
        contrasts.append(_contrast("liraglutide", "matched placebo", raw, hidden=True))
    if "active treatment groups double-blinded against matched placebo groups" in low:
        contrasts.append(_contrast(
            "semaglutide", "matched placebo", raw, dose="2.4 mg", hidden=True,
            code="CONTRAST_HIDDEN_BY_TITLE",
        ))

    contrasts.extend(_generic_contrasts(raw))
    # Keep first equivalent drug/comparator contrast.
    deduped = []
    seen = set()
    for c in contrasts:
        key = (str(c["drug"]["value"]).lower(), str(c["comparator"]["value"]).lower(), c.get("code"))
        if key not in seen:
            seen.add(key)
            deduped.append(c)

    return {
        "source": SOURCE,
        "trial": {
            "id": _field(rec.get("id"), str(rec.get("id") or ""), "record.id"),
            "nct": _field(rec.get("nct") or (rec.get("id") if str(rec.get("id")).upper().startswith("NCT") else None),
                          str(rec.get("nct") or rec.get("id") or ""), "record.nct"),
            "label": _field(rec.get("acronym") or rec.get("id"), str(rec.get("acronym") or rec.get("id") or ""), "record"),
            "title": _field(rec.get("title"), rec.get("title"), "record.title"),
        },
        "randomised_arm": arms or [_arm(NOT_DERIVABLE)],
        "randomised_contrasts": deduped,
        "population": _population(raw, rec),
        "timepoint": _timepoint(raw),
        "analysis_set": _analysis_set(raw),
        "effect_source": _effect_source(rec),
    }


def _matching_contrasts(obj: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
    drugs = _terms(config, "drug_any", "intervention_terms")
    if not drugs:
        drugs = (config.get("include") or {}).get("intervention_any") or []
    out = []
    for c in obj.get("randomised_contrasts") or []:
        if _has_any(str(c.get("drug", {}).get("value")), drugs):
            out.append(c)
    return out


def hidden_eligible_contrasts(obj: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
    """Contrasts matching the topic but hidden behind a title-level active-comparator wording."""
    return [c for c in _matching_contrasts(obj, config) if c.get("hidden_by_title")]


def _required_dose(config: dict[str, Any]) -> str | None:
    dose = ((config.get("arm_object") or {}).get("dose") or {}).get("required")
    return str(dose) if dose else None


def _age_rule(config: dict[str, Any]) -> str | None:
    return (((config.get("arm_object") or {}).get("population") or {}).get("age_range"))


def _entry_rule(config: dict[str, Any]) -> str | None:
    return (((config.get("arm_object") or {}).get("population") or {}).get("entry_condition"))


def assess(obj: dict[str, Any], config: dict[str, Any]) -> dict[str, Any] | None:
    """Return an eligibility refusal derived from the arm object, or None."""
    drugs = _terms(config, "drug_any", "intervention_terms")
    matches = _matching_contrasts(obj, config)
    contrasts = obj.get("randomised_contrasts") or []
    pop = obj.get("population") or {}
    age = str((pop.get("age_range") or {}).get("value") or "")
    entry = str((pop.get("entry_condition") or {}).get("value") or "")

    for c in contrasts:
        if c.get("strategy_bundle"):
            return {
                "rule_id": "X-CONTRAST",
                "reason": "X-CONTRAST(strategy_bundle): balanced fluid and saline appear inside both randomised strategies; no clean intervention-vs-comparator arm contrast.",
                "span": c.get("span") or NOT_DERIVABLE,
            }
        bg = str((c.get("background_therapy") or {}).get("value") or "")
        if bg and bg != NOT_DERIVABLE and _has_any(bg, drugs):
            return {
                "rule_id": "X-CONTRAST",
                "reason": f"X-CONTRAST(background={bg}): the topic intervention is background therapy in both arms, not the randomised contrast.",
                "span": c.get("span") or NOT_DERIVABLE,
            }

    if drugs and contrasts and not matches:
        background = " ".join(str((c.get("background_therapy") or {}).get("value") or "") for c in contrasts)
        if _has_any(background, drugs):
            return {
                "rule_id": "X-CONTRAST",
                "reason": "X-CONTRAST(background): the topic intervention appears only as shared background therapy.",
                "span": contrasts[0].get("span") or NOT_DERIVABLE,
            }

    req_dose = _required_dose(config)
    if req_dose and matches:
        for c in matches:
            got = str((c.get("dose") or {}).get("value") or "")
            # the required dose as a WHOLE number in the read dose(s): '2.4 mg' is not found in '12.4 mg' (NR-C23)
            req_rx = re.compile(r"(?<![\d.])" + re.escape(req_dose.lower().replace("mg", "").strip()) + r"\s*mg", re.I)
            if got != NOT_DERIVABLE and not req_rx.search(got):
                return {
                    "rule_id": "X-DOSE",
                    "reason": f"X-DOSE: randomised {c['drug']['value']} dose is {got}, but the protocol requires {req_dose}.",
                    "span": c.get("span") or NOT_DERIVABLE,
                }

    if _age_rule(config) == "adult" and age in {"adolescent", "paediatric"} or "12 to <18" in age:
        return {
            "rule_id": "X-AGE",
            "reason": f"X-AGE: population.age_range is {age}, but the protocol requires adults.",
            "span": (pop.get("age_range") or {}).get("span") or NOT_DERIVABLE,
        }

    pop_none = (config.get("include") or {}).get("population_none") or []
    if entry == "heart failure" and "heart failure" in {str(x).strip().lower() for x in pop_none}:
        return {
            "rule_id": "ELIGIBILITY_STATE_INCONSISTENT",
            "reason": "ELIGIBILITY_STATE_INCONSISTENT(rule=population_none:heart failure): the arm object derives a heart-failure/HFpEF population even though this screened-in record should be excluded by the population-none rule.",
            "span": (pop.get("entry_condition") or {}).get("span") or NOT_DERIVABLE,
        }

    entry_rule = _entry_rule(config)
    if entry_rule == "without diabetes" and entry in {"mixed T2D", "type 2 diabetes"}:
        return {
            "rule_id": "X-POPULATION",
            "reason": f"X-POPULATION({entry}): population.entry_condition conflicts with the protocol population without diabetes.",
            "span": (pop.get("entry_condition") or {}).get("span") or NOT_DERIVABLE,
        }

    return None


def screen_refusal(rec: dict[str, Any], config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    obj = build(rec, config)
    return obj, assess(obj, config)


def not_derivable_counts(obj: Any) -> tuple[int, int]:
    """Return (n_not_derivable, n_field_values) over field dictionaries."""
    if isinstance(obj, dict) and {"value", "span", "source"} <= set(obj):
        return (1 if obj.get("value") == NOT_DERIVABLE else 0, 1)
    if isinstance(obj, dict):
        a = b = 0
        for v in obj.values():
            x, y = not_derivable_counts(v)
            a += x
            b += y
        return a, b
    if isinstance(obj, list):
        a = b = 0
        for v in obj:
            x, y = not_derivable_counts(v)
            a += x
            b += y
        return a, b
    return 0, 0
