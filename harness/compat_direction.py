"""Asserted-vs-underlying compatibility direction audit.

The compatibility key states the quantity a pool claims to share. Some defects point in the
opposite direction from ordinary incompatibility checks: a page can either overstate sameness, or
warn that a dimension differs when the source-backed per-trial values are actually the same. This
module records that direction per page and dimension without changing pooling decisions.
"""
from __future__ import annotations

from .topic_registry import topic_id

from collections import Counter
import re
from typing import Any


ASSERTED_HOMOGENEOUS_UNDERLYING_HETEROGENEOUS = (
    "ASSERTED_HOMOGENEOUS_UNDERLYING_HETEROGENEOUS"
)
ASSERTED_HETEROGENEOUS_UNDERLYING_HOMOGENEOUS = (
    "ASSERTED_HETEROGENEOUS_UNDERLYING_HOMOGENEOUS"
)
CONSISTENT = "CONSISTENT"
NOT_DERIVABLE = "NOT_DERIVABLE"

_DIRECTION_VALUES = {
    ASSERTED_HOMOGENEOUS_UNDERLYING_HETEROGENEOUS,
    ASSERTED_HETEROGENEOUS_UNDERLYING_HOMOGENEOUS,
    CONSISTENT,
    NOT_DERIVABLE,
}

_HETERO_RE = re.compile(
    r"\b(differs?|differing|heterogeneous|heterogeneity|vary|varies|varying|mixed|not identical)\b",
    re.I,
)
_ENDPOINT_HETERO_RE = re.compile(
    r"component sets differ|outcome-definition difference|endpoint definitions? differ|"
    r"VTE-related death[^.]+whereas|recurrent-VTE composite[^.]+whereas",
    re.I,
)
_HOMOGENEOUS = "homogeneous"
_HETEROGENEOUS = "heterogeneous"
_NOT_ASSERTED = "not_asserted"

_SOURCE_FACTS: dict[str, dict[str, dict[str, dict[str, str]]]] = {
    (topic_id('fluid_resuscitation')): {
        "35041780": {
            "follow_up_window": {
                "value": "90_DAY_MORTALITY",
                "basis": "trial source span says death within 90 days after randomization",
            }
        },
        "34375394": {
            "follow_up_window": {
                "value": "90_DAY_MORTALITY",
                "basis": "trial source span says by day 90",
            }
        },
    },
    (topic_id('postoperative_af')): {
        "42132185": {
            "endpoint_definition": {
                "value": "POAF_5_MIN",
                "basis": "held endpoint-definition span: 5 minute postoperative atrial fibrillation",
            },
            "follow_up_window": {
                "value": "INDEX_ADMISSION",
                "basis": "held time-window span: index-admission/in-hospital POAF",
            },
            "analysis_set": {
                "value": "AVAILABLE_CASE",
                "basis": "trial source span says 163 analyzed patients",
            },
        },
        "32720823": {
            "endpoint_definition": {
                "value": "POAF_GE_5_MIN",
                "basis": "held endpoint-definition span: at least 5 minute POAF",
            },
            "follow_up_window": {
                "value": "IN_HOSPITAL",
                "basis": "held time-window span: in-hospital monitoring",
            },
            "analysis_set": {
                "value": "INTENTION_TO_TREAT",
                "basis": "held analysis-population span: randomized patients analysed by assignment",
            },
        },
        "25172965": {
            "endpoint_definition": {
                "value": "POAF_GE_30_SEC",
                "basis": "held endpoint-definition span: at least 30 seconds",
            },
            "follow_up_window": {
                "value": "30_DAY",
                "basis": "held time-window span: 30-day postoperative AF",
            },
            "analysis_set": {
                "value": "INTENTION_TO_TREAT",
                "basis": "held analysis-population span: randomized patients",
            },
        },
        "27502857": {
            "endpoint_definition": {
                "value": "POAF_GE_10_MIN",
                "basis": "held endpoint-definition span: at least 10 minute AF",
            },
            "follow_up_window": {
                "value": "IN_HOSPITAL",
                "basis": "held time-window span: in-hospital/index-admission endpoint",
            },
            "analysis_set": {
                "value": "INTENTION_TO_TREAT",
                "basis": "trial source span gives all randomized n=179 vs n=181",
            },
        },
    },
    (topic_id('vte_anticoagulation')): {
        "24344086": {
            "endpoint_definition": {
                "value": "SYMPTOMATIC_RECURRENT_VTE",
                "basis": "trial components include recurrent symptomatic objectively confirmed VTE",
            },
            "analysis_set": {"value": "INTENTION_TO_TREAT", "basis": "protocol population line"},
        },
        "19966341": {
            "endpoint_definition": {
                "value": "SYMPTOMATIC_RECURRENT_VTE",
                "basis": "trial components include recurrent symptomatic objectively confirmed VTE",
            },
            "analysis_set": {"value": "INTENTION_TO_TREAT", "basis": "protocol population line"},
        },
        "22449293": {
            "endpoint_definition": {
                "value": "SYMPTOMATIC_RECURRENT_VTE",
                "basis": "trial components include symptomatic recurrent VTE",
            },
            "analysis_set": {"value": "INTENTION_TO_TREAT", "basis": "protocol population line"},
        },
        "21128814": {
            "endpoint_definition": {
                "value": "SYMPTOMATIC_RECURRENT_VTE",
                "basis": "trial components include recurrent VTE",
            },
            "analysis_set": {"value": "INTENTION_TO_TREAT", "basis": "protocol population line"},
        },
        "23991658": {
            "endpoint_definition": {
                "value": "SYMPTOMATIC_RECURRENT_VTE",
                "basis": "trial components include recurrent symptomatic VTE",
            },
            "analysis_set": {
                "value": "MODIFIED_INTENTION_TO_TREAT",
                "basis": "Hokusai-VTE reports modified intention-to-treat for the primary efficacy outcome",
            },
        },
        "23808982": {
            "endpoint_definition": {
                "value": "SYMPTOMATIC_RECURRENT_VTE",
                "basis": "trial components include recurrent symptomatic VTE",
            },
            "analysis_set": {"value": "INTENTION_TO_TREAT", "basis": "protocol population line"},
        },
    },
    (topic_id('finerenone_renal')): {
        "33264825": {
            "endpoint_definition": {
                "value": "KIDNEY_FAILURE | SUSTAINED_EGFR_DECLINE_GE_40_PERCENT | RENAL_DEATH",
                "basis": "FIDELIO-DKD kidney composite components",
            }
        },
        "34449181": {
            "endpoint_definition": {
                "value": "KIDNEY_FAILURE | SUSTAINED_EGFR_DECLINE_GE_40_PERCENT | RENAL_DEATH",
                "basis": "FIGARO-DKD first secondary kidney composite components",
            }
        },
    },
    (topic_id('af_anticoagulation')): {
        "21830957": {
            "endpoint_definition": {
                "value": "STROKE_OR_SYSTEMIC_EMBOLISM",
                "basis": "primary outcome source span says stroke or systemic embolism",
            }
        },
        "19717844": {
            "endpoint_definition": {
                "value": "STROKE_OR_SYSTEMIC_EMBOLISM",
                "basis": "primary outcome source span says stroke or systemic embolism",
            }
        },
        "24251359": {
            "endpoint_definition": {
                "value": "STROKE_OR_SYSTEMIC_EMBOLISM",
                "basis": "primary outcome source span says stroke or systemic embolism",
            }
        },
        "21870978": {
            "endpoint_definition": {
                "value": "STROKE_OR_SYSTEMIC_EMBOLISM",
                "basis": "primary outcome source span says stroke or systemic embolism",
            }
        },
    },
    (topic_id('obesity_weight')): {
        "33625476": {
            "background_lifestyle_intensity": {
                "value": "INTENSIVE_BEHAVIORAL_THERAPY_30_VISITS_LOW_CALORIE_DIET",
                "basis": "STEP 3 held span: intensive behavioural therapy, 30 visits, low-calorie diet",
            }
        },
        "33567185": {
            "background_lifestyle_intensity": {
                "value": "STANDARD_LIFESTYLE_INTERVENTION_STEP1",
                "basis": "STEP 1 held span: semaglutide or placebo plus lifestyle intervention",
            }
        },
    },
}

_DIMENSION_LABELS = {
    "endpoint_definition": "Endpoint definition",
    "follow_up_window": "Follow-up window",
    "analysis_set": "Analysis set",
    "effect_model_class": "Effect-model class",
    "background_lifestyle_intensity": "Background lifestyle intensity",
}

_FACT_OUTCOME_TERMS = {
    (topic_id('fluid_resuscitation')): ("mortality",),
    (topic_id('postoperative_af')): ("atrial fibrillation",),
    (topic_id('vte_anticoagulation')): ("recurrent",),
    (topic_id('finerenone_renal')): ("kidney",),
    (topic_id('af_anticoagulation')): ("stroke",),
    (topic_id('obesity_weight')): ("body weight",),
}


def direction_values() -> set[str]:
    return set(_DIRECTION_VALUES)


def review_directions(review: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for outcome in review.get("outcomes") or []:
        out = outcome_directions(outcome, review)
        for dim in out.get("dimensions") or []:
            row = dict(dim)
            row["page"] = review.get("slug")
            row["outcome"] = outcome.get("name")
            rows.append(row)
    return rows


def outcome_directions(outcome: dict[str, Any], review: dict[str, Any] | None = None) -> dict[str, Any]:
    review = review or {}
    res = outcome.get("result") or {}
    if res.get("present") is False or res.get("suppressed_incompatible") or not res.get("k"):
        return {"dimensions": []}
    dims = [_dimension_direction(outcome, review, dim) for dim in _candidate_dimensions(outcome, review)]
    return {"dimensions": [d for d in dims if d]}


def _candidate_dimensions(outcome: dict[str, Any], review: dict[str, Any]) -> list[str]:
    slug = _slug(review)
    trials = outcome.get("trials") or []
    dims: list[str] = []
    if (
        _has_fact(slug, outcome, trials, "endpoint_definition")
        or any(t.get("endpoint_definition") or t.get("components") for t in trials)
        or (outcome.get("compat_key") or {}).get("endpoint") == "composite"
        or "composite" in str((outcome.get("result") or {}).get("composite_heterogeneity") or "").lower()
    ):
        dims.append("endpoint_definition")
    if _has_fact(slug, outcome, trials, "follow_up_window") or any(t.get("follow_up_window") for t in trials):
        dims.append("follow_up_window")
    if _has_fact(slug, outcome, trials, "analysis_set") or any(t.get("analysis_set") for t in trials):
        dims.append("analysis_set")
    em = (outcome.get("result") or {}).get("estmeasure") or {}
    if slug == (topic_id('spironolactone_heart_failure')) or any(t.get("effect_model_class") for t in trials):
        dims.append("effect_model_class")
    if _has_fact(slug, outcome, trials, "background_lifestyle_intensity") or any(
        t.get("background_lifestyle_intensity") for t in trials
    ):
        dims.append("background_lifestyle_intensity")
    return dims


def _dimension_direction(outcome: dict[str, Any], review: dict[str, Any], dimension: str) -> dict[str, Any]:
    trials = outcome.get("trials") or []
    underlying = _underlying(outcome, review, dimension)
    key_state = _key_state(outcome, review, dimension)
    warning_state = _warning_state(outcome, review, dimension)
    if not underlying["derivable"]:
        key_direction = NOT_DERIVABLE
    elif warning_state == _HETEROGENEOUS and underlying["matched"]:
        key_direction = ASSERTED_HETEROGENEOUS_UNDERLYING_HOMOGENEOUS
    elif key_state == _HETEROGENEOUS and underlying["matched"]:
        key_direction = ASSERTED_HETEROGENEOUS_UNDERLYING_HOMOGENEOUS
    elif key_state in {_HOMOGENEOUS, _NOT_ASSERTED} and not underlying["matched"]:
        key_direction = ASSERTED_HOMOGENEOUS_UNDERLYING_HETEROGENEOUS
    else:
        key_direction = CONSISTENT
    return {
        "dimension": dimension,
        "label": _DIMENSION_LABELS.get(dimension, dimension),
        "key_direction": key_direction,
        "asserted_key_state": key_state,
        "rendered_warning_state": warning_state,
        "underlying": underlying,
        "n_trials": len(trials),
    }


def _underlying(outcome: dict[str, Any], review: dict[str, Any], dimension: str) -> dict[str, Any]:
    per_trial = []
    missing = []
    vals = []
    for t in outcome.get("trials") or []:
        value, basis = _derive_value(outcome, review, t, dimension)
        label = t.get("label") or t.get("id")
        if value is None:
            missing.append(str(label))
        else:
            vals.append(value)
        per_trial.append({"trial": label, "id": t.get("id"), "value": value, "basis": basis})
    counts = Counter(v for v in vals if v is not None)
    return {
        "derivable": bool(per_trial) and not missing,
        "matched": len(counts) <= 1 if vals else False,
        "values": sorted(counts),
        "missing_trials": missing,
        "per_trial": per_trial,
    }


def _derive_value(
    outcome: dict[str, Any], review: dict[str, Any], trial: dict[str, Any], dimension: str
) -> tuple[str | None, str | None]:
    if dimension == "endpoint_definition":
        fact = _fact(_slug(review), outcome, _trial_id(trial), dimension)
        if fact:
            return fact["value"], fact.get("basis")
        endpoint, basis = _endpoint_definition(outcome, trial)
        if endpoint:
            return endpoint, basis
    explicit = trial.get(dimension)
    if explicit:
        return str(explicit), "trial annotation"
    fact = _fact(_slug(review), outcome, _trial_id(trial), dimension)
    if fact:
        return fact["value"], fact.get("basis")
    if dimension == "follow_up_window":
        return _follow_up_window(trial)
    if dimension == "analysis_set":
        return _analysis_set(trial)
    if dimension == "effect_model_class":
        return _effect_model_class(outcome, trial)
    return None, None


def _endpoint_definition(outcome: dict[str, Any], trial: dict[str, Any]) -> tuple[str | None, str | None]:
    comps = [str(x) for x in (trial.get("components") or []) if x]
    if comps:
        text = " | ".join(comps)
        low = text.lower()
        if "venous thrombo" in low or "vte" in low:
            return "SYMPTOMATIC_RECURRENT_VTE", "canonicalized from trial components"
        if "systemic embol" in low and "stroke" in low:
            return "STROKE_OR_SYSTEMIC_EMBOLISM", "canonicalized from trial components"
        mapped = [_component_code(c) for c in comps]
        return " | ".join(x for x in mapped if x), "canonicalized from trial components"
    name = str(outcome.get("name") or "").lower()
    src = str(trial.get("source") or "").lower()
    if "stroke or systemic embolism" in name or "stroke or systemic embolism" in src:
        return "STROKE_OR_SYSTEMIC_EMBOLISM", "outcome/source span"
    if "mortality" in name or "death" in name:
        return "ALL_CAUSE_MORTALITY", "outcome label"
    return None, None


def _component_code(component: str) -> str:
    c = component.lower()
    if "cardiovascular death" in c:
        return "CV_DEATH"
    if "coronary heart disease" in c:
        return "CHD_DEATH"
    if "myocardial infarction" in c:
        return "MI"
    if "ischemic stroke" in c:
        return "ISCHEMIC_STROKE"
    if "stroke" in c:
        return "STROKE"
    if "unstable angina" in c:
        return "UNSTABLE_ANGINA_HOSPITALIZATION"
    if "revascularization" in c:
        return "CORONARY_REVASCULARIZATION"
    if (
        "50%" in c
        or "doubling" in c
        or "40%" in c
        or "end-stage" in c
        or "renal death" in c
        or "egfr <10" in c
    ):
        return _kidney_component_code(c)
    return re.sub(r"[^A-Z0-9]+", "_", component.upper()).strip("_")


def _kidney_component_code(c: str) -> str:
    if "50%" in c:
        return "SUSTAINED_EGFR_DECLINE_GE_50_PERCENT"
    if "40%" in c:
        return "SUSTAINED_EGFR_DECLINE_GE_40_PERCENT"
    if "doubling" in c:
        return "DOUBLING_SERUM_CREATININE"
    if "end-stage" in c or "kidney failure" in c or "renal-replacement" in c:
        return "KIDNEY_FAILURE"
    if "cardiovascular death" in c:
        return "CV_DEATH"
    if "renal death" in c:
        return "RENAL_DEATH"
    if "egfr <10" in c:
        return "SUSTAINED_EGFR_LT_10"
    return re.sub(r"[^A-Z0-9]+", "_", c.upper()).strip("_")


def _follow_up_window(trial: dict[str, Any]) -> tuple[str | None, str | None]:
    src = str(trial.get("source") or "")
    low = src.lower()
    if "within 90 days" in low or "by day 90" in low or "90 days" in low:
        return "90_DAY_MORTALITY", "source span"
    if "30 days" in low or "30-day" in low:
        return "30_DAY", "source span"
    if "14 days" in low or "14-day" in low:
        return "14_DAY", "source span"
    if "in-hospital" in low or "in hospital" in low:
        return "IN_HOSPITAL", "source span"
    return None, None


def _analysis_set(trial: dict[str, Any]) -> tuple[str | None, str | None]:
    src = str(trial.get("source") or "").lower()
    if "modified intention-to-treat" in src or "modified intention to treat" in src:
        return "MODIFIED_INTENTION_TO_TREAT", "source span"
    if "analyzed patients" in src or "analysed patients" in src:
        return "AVAILABLE_CASE", "source span"
    if "intention-to-treat" in src or "intention to treat" in src or "all randomized" in src:
        return "INTENTION_TO_TREAT", "source span"
    return None, None


def _effect_model_class(outcome: dict[str, Any], trial: dict[str, Any]) -> tuple[str | None, str | None]:
    src = str(trial.get("source") or "")
    low = src.lower()
    if ("cox" in low or "proportional-hazard" in low or "proportional hazard" in low) and (
        "death" in low or "mortality" in str(outcome.get("name") or "").lower()
    ):
        return "TIME_TO_FIRST_DEATH_COX_RATIO", "source span"
    if str(trial.get("scale") or "").upper() == "HR" and (
        "death" in low or "mortality" in str(outcome.get("name") or "").lower()
    ):
        return "TIME_TO_FIRST_DEATH_COX_RATIO", "HR label for death outcome"
    return None, None


def _key_state(outcome: dict[str, Any], review: dict[str, Any], dimension: str) -> str:
    ck = outcome.get("compat_key") or {}
    if dimension in ck and isinstance(ck.get(dimension), dict):
        return _HOMOGENEOUS if ck[dimension].get("matched") else _HETEROGENEOUS
    if dimension == "endpoint_definition" and ck.get("endpoint"):
        return _HOMOGENEOUS
    if dimension == "follow_up_window":
        return _text_state(ck.get("follow_up_window") or outcome.get("timepoint"))
    if dimension == "analysis_set":
        return _text_state(ck.get("analysis_set") or outcome.get("population"))
    if dimension == "effect_model_class":
        labels = ((outcome.get("result") or {}).get("estmeasure") or {}).get("labels") or []
        if len(set(labels)) > 1:
            return _HETEROGENEOUS
        return _HOMOGENEOUS if labels else _NOT_ASSERTED
    if dimension == "background_lifestyle_intensity":
        text = " ".join(
            str(x or "")
            for x in (review.get("question"), review.get("eligibility_summary"), review.get("protocol_text"))
        )
        if "lifestyle intervention" in text.lower():
            return _HOMOGENEOUS
    return _NOT_ASSERTED


def _warning_state(outcome: dict[str, Any], review: dict[str, Any], dimension: str) -> str:
    texts: list[str] = []
    res = outcome.get("result") or {}
    if dimension == "endpoint_definition":
        joined = " ".join([str(res.get("composite_heterogeneity") or ""),
                           str(review.get("comparator_scope_note") or "")])
        return _HETEROGENEOUS if _ENDPOINT_HETERO_RE.search(joined) else _NOT_ASSERTED
    if dimension == "effect_model_class":
        texts.append(str(outcome.get("recovery_disclosure") or ""))
    for lim in (outcome.get("compat_key") or {}).get("limitations") or []:
        if lim.get("dimension") == dimension:
            texts.append(str(lim.get("detail") or ""))
    joined = " ".join(texts)
    return _HETEROGENEOUS if _HETERO_RE.search(joined) else _NOT_ASSERTED


def _text_state(text: Any) -> str:
    s = str(text or "")
    if not s:
        return _NOT_ASSERTED
    low = s.lower()
    if _HETERO_RE.search(s) or " or " in low or "28-90" in low:
        return _HETEROGENEOUS
    return _HOMOGENEOUS


def _slug(review: dict[str, Any]) -> str:
    return str(review.get("slug") or "")


def _trial_id(trial: dict[str, Any]) -> str:
    raw = str(trial.get("id") or trial.get("label") or "")
    raw = raw.replace("PMID", "").replace(":", " ").strip()
    m = re.search(r"\b(\d{6,9})\b", raw)
    return m.group(1) if m else raw


def _fact(slug: str, outcome: dict[str, Any], trial_id: str, dimension: str) -> dict[str, str] | None:
    if not _facts_apply(slug, outcome):
        return None
    return ((_SOURCE_FACTS.get(slug) or {}).get(trial_id) or {}).get(dimension)


def _facts_apply(slug: str, outcome: dict[str, Any]) -> bool:
    terms = _FACT_OUTCOME_TERMS.get(slug)
    if not terms:
        return True
    name = str(outcome.get("name") or "").lower()
    return all(term in name for term in terms)


def _has_fact(slug: str, outcome: dict[str, Any], trials: list[dict[str, Any]], dimension: str) -> bool:
    return any(_fact(slug, outcome, _trial_id(t), dimension) for t in trials)
