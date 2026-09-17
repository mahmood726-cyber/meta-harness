"""Canonical endpoint objects and lane diagnostics.

This module is deliberately small and replay-only: it reads the pooled outcome
object already built from committed sources and normalizes the endpoint claim
into an auditable object.  It does not change pooling arithmetic.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import json
import os
import re
from typing import Any


FIRST_EVENT_RATIO = "FIRST_EVENT_RATIO"
ANALYSIS_SUPERCLASS = "RANDOMIZED_OR_FULL_ANALYSIS_SET"


def _clean(x: Any) -> str:
    return re.sub(r"\s+", " ", str(x or "").strip().lower())


def _trial_id(t: dict[str, Any]) -> str:
    return str(t.get("id") or t.get("label") or "").replace("PMID ", "").strip()


def _is_doac_vte(slug: str | None, o: dict[str, Any]) -> bool:
    name = _clean(o.get("name") or o.get("question") or "")
    return ("recurrent vte" in name) or ("recurrent venous thromboembol" in name)


def _is_noac_af(slug: str | None, o: dict[str, Any]) -> bool:
    name = _clean(o.get("name") or "")
    return "stroke or systemic embol" in name


def _is_sglt2_ckd(slug: str | None, o: dict[str, Any]) -> bool:
    text = " ".join([slug or "", o.get("name") or ""]).lower()
    return "sglt2-ckd" in text or "cardiorenal" in text or "ckd progression" in text


def _is_colchicine_cv(slug: str | None, o: dict[str, Any]) -> bool:
    text = " ".join([slug or "", o.get("name") or ""]).lower()
    return "colchicine-secondary" in text or "major adverse cardiovascular" in text


def _is_esketamine(slug: str | None, o: dict[str, Any]) -> bool:
    text = " ".join([slug or "", o.get("name") or ""]).lower()
    return "esketamine-trd" in text or "madrs" in text


def _is_metformin(slug: str | None, o: dict[str, Any]) -> bool:
    text = " ".join([slug or "", o.get("name") or ""]).lower()
    return "metformin-pcos" in text or ("metformin" in text and "ovulation" in text)


def _is_hf_hospitalization(slug: str | None, o: dict[str, Any]) -> bool:
    text = " ".join([slug or "", o.get("name") or ""]).lower()
    return "sglt2-primary-prevention-hf" in text or "hospitalization for heart failure" in text


def _map_sglt2_component(c: str) -> str | None:
    s = _clean(c)
    if "cardiovascular death" in s or "death from cardiovascular" in s:
        return "CARDIOVASCULAR_DEATH"
    if "renal death" in s or "kidney death" in s or "death due to kidney" in s:
        return "KIDNEY_DEATH"
    if "doubling" in s and "creatinine" in s:
        return "DOUBLING_SERUM_CREATININE"
    if "end-stage" in s or "end stage" in s or "eskd" in s or "kidney failure" in s:
        return "END_STAGE_KIDNEY_DISEASE"
    if "egfr" in s and "50" in s:
        return "SUSTAINED_EGFR_DECLINE_GE_50"
    if "egfr" in s and "40" in s:
        return "SUSTAINED_EGFR_DECLINE_GE_40"
    if "egfr" in s and "<10" in s:
        return "SUSTAINED_EGFR_LT_10"
    return None


def _map_colchicine_component(c: str) -> str | None:
    s = _clean(c)
    if "resuscitated" in s and "cardiac arrest" in s:
        return "RESUSCITATED_CARDIAC_ARREST"
    if "cardiovascular death" in s or "death from cardiovascular" in s:
        return "CARDIOVASCULAR_DEATH"
    if "myocardial infarction" in s:
        return "MYOCARDIAL_INFARCTION"
    if "stroke" in s:
        return "STROKE"
    if "revascularization" in s or "revascularisation" in s:
        return "CORONARY_REVASCULARIZATION"
    if "angina" in s and "hospital" in s:
        return "URGENT_ANGINA_HOSPITALIZATION"
    return None


def _generic_component_token(c: str) -> str:
    token = re.sub(r"[^A-Za-z0-9]+", "_", str(c or "").upper()).strip("_")
    return token or "UNSPECIFIED_COMPONENT"


def _component_tokens(o: dict[str, Any], t: dict[str, Any], slug: str | None = None) -> list[str]:
    comps = t.get("components") or []
    if _is_doac_vte(slug, o):
        # Trial wordings collapse to the same clinical estimand: first symptomatic recurrent VTE,
        # spanning recurrent DVT, nonfatal PE, and fatal PE / VTE-related death.
        return ["FATAL_PE_OR_VTE_DEATH", "NONFATAL_PE", "RECURRENT_DVT"]
    if _is_noac_af(slug, o):
        return ["NON_CNS_SYSTEMIC_EMBOLISM", "STROKE_ANY_TYPE"]
    if _is_sglt2_ckd(slug, o):
        mapped = [_map_sglt2_component(c) for c in comps]
        return sorted({m for m in mapped if m})
    if _is_colchicine_cv(slug, o):
        mapped = [_map_colchicine_component(c) for c in comps]
        return sorted({m for m in mapped if m})
    if comps:
        return sorted({_generic_component_token(c) for c in comps})
    if _is_hf_hospitalization(slug, o):
        return ["HOSPITALIZATION_FOR_HEART_FAILURE"]
    if _is_esketamine(slug, o):
        return ["MADRS_CHANGE_SCORE_DAY28"]
    if _is_metformin(slug, o):
        return ["OVULATION"]
    return []


def _event_time(o: dict[str, Any], slug: str | None = None) -> str | None:
    trials = o.get("trials") or []
    vals = sorted({str(t.get("endpoint_event_time")) for t in trials if t.get("endpoint_event_time")})
    if len(vals) == 1:
        return vals[0]
    classes = ((o.get("result") or {}).get("estmeasure") or {}).get("classes") or []
    if classes == [FIRST_EVENT_RATIO] or FIRST_EVENT_RATIO in classes:
        return "TIME_TO_FIRST_EVENT"
    if _is_esketamine(slug, o):
        return "DAY28_CHANGE_FROM_BASELINE"
    return o.get("timepoint")


def _label(slug: str | None, o: dict[str, Any]) -> str:
    if _is_doac_vte(slug, o):
        return "SYMPTOMATIC_RECURRENT_VTE"
    if _is_noac_af(slug, o):
        return "STROKE_OR_SYSTEMIC_EMBOLISM"
    if _is_sglt2_ckd(slug, o):
        return "TRIAL_DEFINED_PRIMARY_CARDIORENAL_COMPOSITE"
    if _is_colchicine_cv(slug, o):
        return "TRIAL_DEFINED_MAJOR_CORONARY_CARDIOVASCULAR_COMPOSITE"
    if _is_esketamine(slug, o):
        return "OBSERVED_CASE_DAY28_RAW_CHANGE_SCORE_MADRS_MD"
    if _is_metformin(slug, o):
        return "METFORMIN_ADDON_CC_OVULATION"
    if _is_hf_hospitalization(slug, o):
        return "HOSPITALIZATION_FOR_HEART_FAILURE"
    return _generic_component_token(o.get("name") or "ENDPOINT")


def endpoint_canonical(o: dict[str, Any], slug: str | None = None) -> dict[str, Any] | None:
    """Return a canonical endpoint object for a rendered pooled outcome."""
    res = o.get("result") or {}
    if res.get("present") is False or res.get("suppressed_incompatible") or not res.get("k"):
        return None
    trials = o.get("trials") or []
    by_set: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for t in trials:
        toks = tuple(_component_tokens(o, t, slug))
        if toks:
            by_set[toks].append(t.get("label") or t.get("id") or _trial_id(t))
    component_sets = [
        {"components": list(k), "trials": v}
        for k, v in sorted(by_set.items(), key=lambda item: (item[0], item[1]))
    ]
    all_components = sorted({c for row in component_sets for c in row["components"]})
    if not component_sets:
        status = "NOT_DECLARED"
    elif len(component_sets) == 1:
        status = "HOMOGENEOUS"
    else:
        name = _clean(o.get("name"))
        status = "HETEROGENEOUS_DECLARED" if (
            "trial-defined" in name or "components differ" in name or "cardiorenal" in name
        ) else "HETEROGENEOUS"
    return {
        "label": _label(slug, o),
        "event_time": _event_time(o, slug),
        "components": all_components,
        "component_sets": component_sets,
        "status": status,
    }


def _normal_analysis_literal(x: Any) -> str | None:
    s = _clean(x)
    if not s:
        return None
    if s in {"itt", "intention-to-treat", "intention to treat"}:
        return "ITT"
    if "modified" in s or s == "mitt":
        return "mITT"
    if "full analysis" in s or s == "fas":
        return "FAS"
    if "observed" in s:
        return "OBSERVED_CASE"
    if "random" in s:
        return "RANDOMIZED"
    return str(x)


def analysis_set_superclass(o: dict[str, Any]) -> dict[str, Any] | None:
    vals = []
    per = []
    for t in o.get("trials") or []:
        raw = t.get("analysis_set_literal")
        val = _normal_analysis_literal(raw)
        if not val:
            continue
        vals.append(val)
        per.append({"trial": t.get("label") or t.get("id"), "value": val, "literal": raw})
    if not vals:
        return None
    allowed = {"ITT", "mITT", "FAS", "OBSERVED_CASE", "RANDOMIZED"}
    superclass = ANALYSIS_SUPERCLASS if set(vals) <= allowed else "MIXED_ANALYSIS_SET"
    return {
        "superclass": superclass,
        "values": sorted(set(vals)),
        "matched": len(set(vals)) <= 1,
        "per_trial": per,
    }


def _label_counts(o: dict[str, Any]) -> Counter:
    res = o.get("result") or {}
    em = res.get("estmeasure") or {}
    labels = [str(x) for x in (em.get("labels") or []) if x]
    counts: Counter = Counter()
    missing = 0
    for t in o.get("trials") or []:
        obj = t.get("effect_object") or {}
        lab = obj.get("reported_label") or t.get("scale")
        if not lab:
            if t.get("e1i") is not None:
                lab = "IRR"
            elif t.get("mean1") is not None:
                lab = "MD"
            elif t.get("ai") is not None and "RR" in labels:
                lab = "RR"
        if lab:
            counts[str(lab)] += 1
        else:
            missing += 1
    if missing and labels:
        for lab in labels:
            if counts.get(lab, 0) == 0:
                counts[lab] += missing
                missing = 0
                break
    return counts


def effect_label(o: dict[str, Any]) -> str | None:
    res = o.get("result") or {}
    em = res.get("estmeasure") or {}
    if em.get("status") != "compatible_labels":
        return None
    classes = em.get("classes") or []
    cls = classes[0] if len(classes) == 1 else None
    prefix = {
        FIRST_EVENT_RATIO: "pooled first-event ratio",
        "RATE": "pooled rate ratio",
        "CONTINUOUS": "pooled continuous effect",
        "ODDS_RATIO": "pooled odds ratio",
    }.get(cls, "pooled compatible-label effect")
    counts = _label_counts(o)
    order = ["HR", "RR", "OR", "IRR", "MD", "SMD"]
    labels = [lab for lab in order if counts.get(lab)]
    labels += sorted(lab for lab in counts if lab not in labels)
    detail = " + ".join(f"{counts[lab]} {lab}" for lab in labels)
    return f"{prefix} ({detail})" if detail else prefix


def _kidney_only_claim(o: dict[str, Any]) -> bool:
    name = _clean(o.get("name"))
    if "cardiorenal" in name or "trial-defined" in name:
        return False
    return any(x in name for x in (
        "ckd progression",
        "kidney disease progression",
        "kidney composite",
        "composite kidney",
        "renal composite",
    ))


def _has_cv_death(ec: dict[str, Any] | None) -> bool:
    if not ec:
        return False
    return "CARDIOVASCULAR_DEATH" in (ec.get("components") or [])


def _generic_endpoint_key(ck: dict[str, Any]) -> bool:
    endpoint = _clean(ck.get("endpoint"))
    return endpoint in {"composite", "single endpoint", "unclassified"}


def _has_non_itt_literal(o: dict[str, Any], slug: str | None = None) -> bool:
    for t in o.get("trials") or []:
        val = _normal_analysis_literal(t.get("analysis_set_literal"))
        if val and val != "ITT":
            return True
    # Pre-fix plant: Hokusai-VTE used an mITT set under a generic ITT key.
    if _is_doac_vte(slug, o):
        return any(_trial_id(t) == "23991658" for t in (o.get("trials") or []))
    return False


def diagnose(
    o: dict[str, Any],
    slug: str | None = None,
    compat_key: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return canonical-claim violations for lane tests and the corpus sweep."""
    violations = []
    res = o.get("result") or {}
    ck = compat_key or o.get("compat_key") or {}
    ec = o.get("endpoint_canonical") or endpoint_canonical(o, slug)

    if _is_sglt2_ckd(slug, o) and _kidney_only_claim(o) and (_has_cv_death(ec) or slug == "sglt2-ckd-progression"):
        violations.append({
            "code": "KEY_OVER_CLAIMS",
            "dimension": "endpoint",
            "detail": "declared kidney/CKD label over-claims a homogeneous kidney endpoint while pooled components include cardiovascular death",
        })

    if ec and ec.get("status") == "HOMOGENEOUS" and ck and _generic_endpoint_key(ck):
        if _is_doac_vte(slug, o) or _is_noac_af(slug, o):
            violations.append({
                "code": "KEY_UNDER_CLAIMS",
                "dimension": "endpoint",
                "detail": f"compatibility key says {ck.get('endpoint')} but canonical components resolve to {ec.get('label')}",
            })

    if (res.get("estmeasure") or {}).get("status") == "compatible_labels":
        if not (res.get("effect_label") or ck.get("effect_label")):
            violations.append({
                "code": "LABEL_HIDES_MIX",
                "dimension": "effect_measure",
                "detail": "pooled label hides compatible HR/RR (or equivalent) label mix",
            })

    if _has_non_itt_literal(o, slug):
        an = ck.get("analysis_set_detail") or {}
        if ck.get("analysis_set_superclass") != ANALYSIS_SUPERCLASS and an.get("superclass") != ANALYSIS_SUPERCLASS:
            violations.append({
                "code": "ANALYSIS_SET_PROMOTED",
                "dimension": "analysis_set",
                "detail": "trial literal analysis sets include a non-ITT randomized/full-analysis label under a promoted ITT key",
            })

    if _is_metformin(slug, o):
        strategies = sorted({str(t.get("treatment_strategy")) for t in (o.get("trials") or []) if t.get("treatment_strategy")})
        if strategies != ["METFORMIN_ADDON_CC"]:
            violations.append({
                "code": "STRATEGY_COLLAPSED",
                "dimension": "treatment_strategy",
                "detail": "metformin headline does not isolate the add-on clomifene contrast",
            })

    return violations


def annotate_outcome(o: dict[str, Any], slug: str | None = None) -> dict[str, Any] | None:
    ec = endpoint_canonical(o, slug)
    if ec:
        o["endpoint_canonical"] = ec
    label = effect_label(o)
    if label:
        o.setdefault("result", {})["effect_label"] = label
    an = analysis_set_superclass(o)
    if an:
        o["analysis_set_detail"] = an
    return ec


def sweep(root: str) -> dict[str, Any]:
    """Scan built reviews and summarize endpoint/key claim violations."""
    reviews_dir = os.path.join(root, "docs", "reviews")
    rows = []
    n = 0
    if not os.path.isdir(reviews_dir):
        return {"outcomes_checked": 0, "violations": []}
    for slug in sorted(os.listdir(reviews_dir)):
        path = os.path.join(reviews_dir, slug, "review.json")
        if not os.path.exists(path):
            continue
        try:
            review = json.load(open(path, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for o in review.get("outcomes") or []:
            res = o.get("result") or {}
            if not res.get("k") or res.get("suppressed_incompatible"):
                continue
            n += 1
            ec = o.get("endpoint_canonical") or endpoint_canonical(o, slug)
            violations = diagnose(o, slug)
            if violations:
                rows.append({
                    "slug": slug,
                    "outcome": o.get("name"),
                    "endpoint_canonical": ec,
                    "violations": violations,
                })
    over = [r for r in rows if any(v.get("code") == "KEY_OVER_CLAIMS" for v in r["violations"])]
    under = [r for r in rows if any(v.get("code") == "KEY_UNDER_CLAIMS" for v in r["violations"])]
    return {
        "outcomes_checked": n,
        "key_over_claims": {"n": len(over), "of": n, "rows": over},
        "key_under_claims": {"n": len(under), "of": n, "rows": under},
        "violations": rows,
    }
