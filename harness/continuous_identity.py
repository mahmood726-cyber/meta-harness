"""CONTINUOUS-OUTCOME identity (external review of esketamine-trd-madrs, 2026-09-27, hash f5b8f4cb).

A continuous row is several different numbers that look alike:
  * an ARM mean change with its arm SD and the number OBSERVED at the timepoint (TRANSFORM-2: 101/100), which is not the
    number in the analysis set (FAS 114/109);
  * a RAW difference of those means (-4.4) versus a model-ADJUSTED difference (LS mean, MMRM/ANCOVA: -4.0);
  * the SE OF A DIFFERENCE (TRANSFORM-2's registry analysis: 1.69) versus an arm SD (12.32, 13.88).
An SE is NEVER used as an arm SD. A CI width / (2 z) gives an SE ONLY when the interval is a standard fixed-level two-sided
CI; a stage-weighted / flexible CI (a two-stage adaptive design's median-unbiased estimate with its weighted-combination
interval -- TRANSFORM-3's held abstract, TRANSFORM-1 per the EMA) is refused for that derivation, because its width is not
2 z SE.

COMBINED DOSES: a declared rule combines eligible dose arms into one arm (Cochrane Handbook 6.5.2.10: pooled mean, and an SD
that includes the between-arm spread) against the SHARED comparator counted ONCE. Without a declared rule, a multi-dose trial
stays refused (the multi-arm guard in ctgov_results).

PRIMARY vs SENSITIVITY: the protocol names the primary analysis (here: raw per-arm mean/SD, observed at Day 28) and must name
its missing-data assumption; a model-based analysis of reported adjusted differences is a SENSITIVITY analysis and admits a
trial only when its SE is established (stated, or from a standard CI).
"""
from __future__ import annotations

import json
import math
import re
from statistics import NormalDist
from typing import Any

# --------------------------------------------------------------------------- typed registry measure
_ADJUSTED = re.compile(r"(?i)least\s+squares?|\bLS\s+mean|adjusted\s+mean|model[- ]based|marginal\s+mean")
# A registry "Treatment difference" estimated by a MODEL is a model-based difference (semaglutide-weight review, e209c1d5): STEP 1
# posts paramType "Treatment difference" with statisticalMethod "ANCOVA". Typing it by paramType alone left it DIFFERENCE_NOT_TYPED.
_MODEL_METHOD = re.compile(r"(?i)\bANCOVA\b|analysis\s+of\s+covariance|\bMMRM\b|mixed[- ]effects?\s+model|mixed\s+model|"
                           r"repeated\s+measures?|regression|\bcLDA\b|constrained\s+longitudinal")
# The ESTIMAND an analysis belongs to, read from the analysis's own description fields only -- never from the topic.
_ESTIMANDS = (("TREATMENT_POLICY", re.compile(r"(?i)treatment[- ]policy")),
              ("HYPOTHETICAL", re.compile(r"(?i)\bhypothetical\b|trial[- ]product\s+estimand")),
              ("WHILE_ON_TREATMENT", re.compile(r"(?i)while[- ]on[- ]treatment|on[- ]treatment\s+estimand")))


def estimand_of(analysis: dict[str, Any]) -> str:
    """The estimand a registry analysis names in its own fields (groupDescription / estimationComment / comments); NOT_STATED
    otherwise. Two analyses of one measure on the same arms are two ESTIMANDS (STEP 1: treatment policy and hypothetical), not
    two doses."""
    txt = " ".join(str(analysis.get(k) or "") for k in ("groupDescription", "estimationComment", "nonInferiorityComment",
                                                         "statisticalComment", "otherAnalysisDescription"))
    hits = [name for name, rx in _ESTIMANDS if rx.search(txt)]
    return hits[0] if len(hits) == 1 else ("AMBIGUOUS" if hits else "NOT_STATED")


def _load(v):
    if isinstance(v, str):
        try:
            return json.loads(v)
        except ValueError:
            return None
    return v


def _num(x):
    try:
        return float(str(x).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def dispersion_kind(label: str | None) -> str:
    s = (label or "").lower().replace("_", " ")
    if "standard deviation" in s:
        return "SD"
    if "standard error" in s:
        return "SE"
    if "confidence interval" in s:
        return "CI"
    if "inter-quartile" in s or "interquartile" in s:
        return "IQR"
    if "range" in s:
        return "RANGE"
    return "NOT_STATED"


def typed_measure(om: dict[str, Any]) -> dict[str, Any]:
    """Every number in one registry outcome measure, typed. Nothing is converted here."""
    groups = _load(om.get("groups")) or []
    titles = {g.get("id"): g.get("title") for g in groups}
    denoms = {}
    for d in om.get("denoms") or []:
        for c in d.get("counts") or []:
            denoms[c.get("groupId")] = _num(c.get("value"))
    arms = []
    classes = _load(om.get("classes")) or []
    # the class the numbers are read from may carry its OWN denominators (STEP 1: 1212/577 under a measure-level 1306/655);
    # those are the n observed behind the mean/SD, and the measure-level count is the analysis-set n
    analysis_set_n = dict(denoms)
    if classes and classes[0].get("denoms"):
        denoms = {}  # A missing class arm must not inherit the measure-level FAS.
        for d in classes[0]["denoms"]:
            for c in d.get("counts") or []:
                denoms[c.get("groupId")] = _num(c.get("value"))
    kind = dispersion_kind(om.get("dispersionType"))
    ptype = str(om.get("paramType") or "")
    estimate_kind = "ADJUSTED_ARM_MEAN" if _ADJUSTED.search(ptype + " " + str(om.get("title") or "")) and "MEAN" != ptype.upper() else "RAW_ARM_MEAN"
    if classes and classes[0].get("categories"):
        for m in classes[0]["categories"][0].get("measurements") or []:
            gid = m.get("groupId")
            arms.append({"group": gid, "title": titles.get(gid), "mean_change": _num(m.get("value")),
                         "dispersion": _num(m.get("spread")), "dispersion_kind": kind,
                         "n_observed": (int(denoms[gid]) if denoms.get(gid) is not None and float(denoms[gid]).is_integer()
                                        else denoms.get(gid)),
                         "n_analysis_set": analysis_set_n.get(gid), "estimate_kind": estimate_kind})
    analyses = []
    for a in _load(om.get("analyses")) or []:
        dk = dispersion_kind(a.get("dispersionType"))
        analyses.append({
            "groups": list(a.get("groupIds") or []),
            "estimate_kind": ("ADJUSTED_DIFFERENCE" if (_ADJUSTED.search(str(a.get("paramType") or ""))
                                                         or (_MODEL_METHOD.search(str(a.get("statisticalMethod") or ""))
                                                             and "difference" in str(a.get("paramType") or "").lower()))
                              else "DIFFERENCE_NOT_TYPED"),
            "estimand": estimand_of(a),
            "method": a.get("statisticalMethod"), "value": _num(a.get("paramValue")),
            # an SE here is the SE OF THE DIFFERENCE -- never an arm SD
            "se_of_difference": _num(a.get("dispersionValue")) if dk == "SE" else None,
            "ci": {"level": _num(a.get("ciPctValue")),
                   "sidedness": {"TWO_SIDED": "two-sided", "ONE_SIDED": "one-sided"}.get(str(a.get("ciNumSides") or "").upper(), "not stated"),
                   "low": _num(a.get("ciLowerLimit")), "high": _num(a.get("ciUpperLimit"))},
        })
    return {"title": om.get("title"), "time_frame": om.get("timeFrame"),
            "population": (om.get("populationDescription") or "").strip().strip('"'),
            "param_type": ptype, "arms": arms, "analyses": analyses}


# --------------------------------------------------------------------------- SD / SE discipline
class NotAnArmSD(ValueError):
    """Raised when a dispersion that is not an arm SD is offered as one."""


def arm_sd(value: float | None, kind: str) -> float:
    """The arm SD, or a refusal. An SE (of an arm mean or of a difference), a CI, an IQR or a range is never an arm SD."""
    if kind != "SD":
        raise NotAnArmSD(f"a {kind} is not an arm SD: an SE is never used as an SD, and no conversion is silent")
    if value is None or not value > 0:
        raise NotAnArmSD("arm SD missing or non-positive")
    return float(value)


# --------------------------------------------------------------------------- CI procedure
STANDARD = "STANDARD_FIXED_LEVEL_TWO_SIDED"
FLEXIBLE = "STAGE_WEIGHTED_FLEXIBLE"
NOT_ESTABLISHED = "NOT_ESTABLISHED"

# Procedure words only. "Flexible doses" (TRANSFORM-2's DOSING) is not an interval procedure and never fires.
_FLEXIBLE_CI = re.compile(r"(?i)median[- ]unbiased|weighted\s+combination\s+test|stage[- ]?wise|stage[- ]weighted|"
                          r"two[- ]stage\s+(?:adaptive\s+)?design|adaptive\s+(?:two[- ]stage\s+)?design|"
                          r"group[- ]sequential|repeated\s+confidence|flexible\s+(?:confidence\s+interval|ci)\b")


def ci_procedure(held_texts, ci: dict[str, Any] | None, declared: dict[str, Any] | None = None) -> dict[str, Any]:
    """How the interval was constructed. FLEXIBLE when the trial's held text names a stage-weighted / adaptive / sequential
    procedure, or when the topic DECLARES one with a source; STANDARD only when the level and two-sidedness are stated and
    nothing flexible is found; otherwise NOT_ESTABLISHED."""
    for t in held_texts or []:
        m = _FLEXIBLE_CI.search(t or "")
        if m:
            return {"procedure": FLEXIBLE, "basis": "held text", "evidence": (t or "")[max(0, m.start() - 80):m.end() + 80]}
    if declared and str(declared.get("procedure") or "").upper() == FLEXIBLE:
        return {"procedure": FLEXIBLE, "basis": "declared", "evidence": declared.get("source")}
    ci = ci or {}
    if ci.get("level") and ci.get("sidedness") == "two-sided":
        return {"procedure": STANDARD, "basis": "level and sidedness stated; no flexible procedure in held text"}
    return {"procedure": NOT_ESTABLISHED, "basis": "level or sidedness not stated"}


def se_from_ci(ci: dict[str, Any], procedure: dict[str, Any]) -> float:
    """SE = CI width / (2 z_level), ONLY for a standard fixed-level two-sided CI."""
    if procedure.get("procedure") != STANDARD:
        raise ValueError(f"SE from CI width refused: interval procedure is {procedure.get('procedure')} "
                         f"({procedure.get('basis')}) -- its width is not 2 z SE")
    lo, hi, lvl = ci.get("low"), ci.get("high"), ci.get("level")
    if lo is None or hi is None or not lvl or not hi > lo:
        raise ValueError("SE from CI width refused: incomplete interval")
    z = NormalDist().inv_cdf(0.5 + float(lvl) / 200.0)
    return (hi - lo) / (2 * z)


def difference_se(analysis: dict[str, Any], procedure: dict[str, Any]) -> dict[str, Any]:
    """The SE of an adjusted difference: stated (typed SE_OF_DIFFERENCE) or derived from a standard CI; else refused."""
    if analysis.get("se_of_difference"):
        return {"se": analysis["se_of_difference"], "basis": "stated SE of the difference (registry analysis)"}
    try:
        return {"se": se_from_ci(analysis["ci"], procedure), "basis": "CI width / (2 z) of a standard two-sided CI"}
    except ValueError as e:
        return {"se": None, "refused": str(e)}


# --------------------------------------------------------------------------- combined doses
def combine_arms(arms: list[dict[str, Any]]) -> dict[str, Any]:
    """Cochrane Handbook 6.5.2.10: combine arm (mean, SD, n) into one; the SD includes the between-arm spread."""
    if len(arms) < 2:
        raise ValueError("combining needs at least two arms")
    n = m = None
    for a in arms:
        sd = arm_sd(a.get("sd"), a.get("dispersion_kind", "SD"))
        if n is None:
            n, m, s = a["n"], a["mean"], sd
            continue
        n2, m2, s2 = a["n"], a["mean"], sd
        N = n + n2
        mean = (n * m + n2 * m2) / N
        s = math.sqrt(((n - 1) * s ** 2 + (n2 - 1) * s2 ** 2 + n * n2 / N * (m - m2) ** 2) / (N - 1))
        n, m = N, mean
    return {"mean": m, "sd": s, "n": int(n)}


def combine_rule(spec: dict[str, Any] | None) -> dict[str, Any] | None:
    r = (spec or {}).get("combine_eligible_doses")
    return r if isinstance(r, dict) and r.get("eligible_arm_terms") else None


def combined_contrast(om: dict[str, Any], interv_terms, comp_terms, rule: dict[str, Any]) -> dict[str, Any] | None:
    """Apply a DECLARED combine rule to one registry measure: every intervention arm must be named eligible by the rule
    (never a subset chosen after seeing results), exactly one comparator arm, counted once. None when it does not apply."""
    tm = typed_measure(om)
    iv = [t.lower() for t in interv_terms or []]
    cp = [t.lower() for t in comp_terms or []]
    elig = [t.lower() for t in rule["eligible_arm_terms"]]
    comp = [a for a in tm["arms"] if any(c in (a["title"] or "").lower() for c in cp)]
    exper = [a for a in tm["arms"] if a not in comp and any(i in (a["title"] or "").lower() for i in iv)]
    if len(comp) != 1 or len(exper) < 2 or len(exper) + 1 != len(tm["arms"]):
        return None
    if not all(any(e in (a["title"] or "").lower() for e in elig) for a in exper):
        return None                               # an experimental arm the rule does not name: refuse, never drop it
    parts = [{"mean": a["mean_change"], "sd": a["dispersion"], "dispersion_kind": a["dispersion_kind"], "n": a["n_observed"]}
             for a in exper]
    comb = combine_arms(parts)
    c = comp[0]
    return {"mean1": round(comb["mean"], 4), "sd1": round(comb["sd"], 4), "nc1": comb["n"],
            "mean2": c["mean_change"], "sd2": arm_sd(c["dispersion"], c["dispersion_kind"]), "nc2": int(c["n_observed"]),
            "scale": "MD",
            "multi_arm_combined": {"rule": "COMBINE_ELIGIBLE_DOSES", "basis": rule.get("basis"),
                                   "prespecified_in_trial": bool(rule.get("prespecified_in_trial")),
                                   "arms": [{"title": a["title"], "mean": a["mean_change"], "sd": a["dispersion"],
                                             "n": a["n_observed"]} for a in exper],
                                   "shared_comparator": {"title": c["title"], "counted": "once"},
                                   "measure_title": tm["title"]}}


# --------------------------------------------------------------------------- the analysis plan
def analysis_plan(spec: dict[str, Any] | None) -> dict[str, Any]:
    """The declared PRIMARY analysis and its missing-data assumption, and the declared sensitivity analyses. A primary with
    no stated missing-data assumption is reported as such -- never filled in."""
    plan = (spec or {}).get("analysis_plan") or {}
    prim = dict(plan.get("primary") or {})
    if not prim:
        return {"state": "PRIMARY_ANALYSIS_NOT_DECLARED"}
    state = "DECLARED" if prim.get("missing_data_assumption") else "MISSING_DATA_ASSUMPTION_NOT_DECLARED"
    return {"state": state, "primary": prim, "sensitivity": list(plan.get("sensitivity") or [])}


def model_based_row(om: dict[str, Any], held_texts, declared_procedure: dict[str, Any] | None,
                    exper_title_terms=None, estimand: str | None = None) -> dict[str, Any]:
    """The trial's reported ADJUSTED difference with an established SE, for the model-based sensitivity analysis -- or a
    typed refusal. A multi-dose trial whose adjusted differences are per dose is refused (no combined adjusted difference
    exists; one is never constructed from per-dose model estimates)."""
    tm = typed_measure(om)
    adj = [a for a in tm["analyses"] if a["estimate_kind"] == "ADJUSTED_DIFFERENCE"]
    if not adj:
        return {"state": "NO_ADJUSTED_DIFFERENCE", "measure_title": tm["title"]}
    if estimand:
        # the analysis is selected by the ESTIMAND the plan declares, from the analysis's own label; one that does not name it
        # is not assumed to be it
        named = [a for a in adj if a.get("estimand") == estimand]
        if not named:
            return {"state": "DECLARED_ESTIMAND_NOT_REPORTED", "measure_title": tm["title"], "declared_estimand": estimand,
                    "reported_estimands": sorted({a.get("estimand") for a in adj})}
        adj = named
    elif len({a.get("estimand") for a in adj}) > 1 and len({tuple(a["groups"]) for a in adj}) == 1:
        return {"state": "ESTIMAND_NOT_SELECTED", "measure_title": tm["title"],
                "reported_estimands": sorted({a.get("estimand") for a in adj}),
                "reason": "the registry reports one model-based difference per ESTIMAND on the same arms; the analysis plan must "
                          "declare which estimand is used -- none is picked"}
    if len(adj) > 1 or len(tm["arms"]) > 2:
        return {"state": "PER_DOSE_ADJUSTED_ONLY", "measure_title": tm["title"],
                "reason": "the registry reports one adjusted difference per dose arm; no combined adjusted difference is reported "
                          "and none is constructed from per-dose model estimates"}
    a = adj[0]
    proc = ci_procedure(held_texts, a["ci"], declared_procedure)
    se = difference_se(a, proc)
    if se.get("se") is None:
        return {"state": "SE_NOT_ESTABLISHED", "measure_title": tm["title"], "value": a["value"], "ci": a["ci"],
                "procedure": proc, "reason": se["refused"]}
    return {"state": "ADMITTED", "measure_title": tm["title"], "value": a["value"], "se": round(se["se"], 4),
            "se_basis": se["basis"], "ci": a["ci"], "procedure": proc, "method": a["method"], "estimand": a.get("estimand")}


# --------------------------------------------------------------------------- observed contribution (semaglutide-weight review)
_AVAILABLE = re.compile(r"(?i)(?:participants|subjects|patients)\s+with\s+(?:available|observed|non[- ]missing)\s+data|"
                        r"number\s+analy[sz]ed\s*=\s*[^.;]{0,40}?available\s+data|observed\s+(?:cases|data)\b")
_IMPUTED = re.compile(r"(?i)imputed|imputation|last\s+observation\s+carried|\bLOCF\b|\bBOCF\b|jump[- ]to[- ]reference|"
                      r"retrieved\s+drop[- ]?outs?|multiple\s+imputation")


def observed_contribution(om: dict[str, Any]) -> dict[str, Any]:
    """Whether a registry arm summary's n is the n that CONTRIBUTED observations. OBSERVED when the measure says the analysed
    number is participants with available data; IMPUTED when it names imputation (then the imputation method AND its variance
    must be established before the summary is used as raw mean/SD -- the caller holds the row); NOT_ESTABLISHED otherwise. A
    full-analysis-set heading never establishes observed contribution."""
    txt = " ".join(str(om.get(k) or "") for k in ("populationDescription", "description"))
    if _IMPUTED.search(txt):
        m = _IMPUTED.search(txt)
        return {"state": "IMPUTED", "evidence": txt[max(0, m.start() - 80):m.end() + 80].strip()}
    if _AVAILABLE.search(txt):
        m = _AVAILABLE.search(txt)
        return {"state": "OBSERVED", "evidence": txt[max(0, m.start() - 60):m.end() + 20].strip()}
    return {"state": "NOT_ESTABLISHED", "evidence": None,
            "note": "the measure does not say whether the analysed number is observed or imputed; a full-analysis-set heading "
                    "does not establish it"}


def estimand_label(kind: str, estimand: str | None = None, method: str | None = None) -> str:
    """The estimand LABEL of a served continuous input, derived from the analysis actually used -- never from the topic's
    declared population string. Raw observed per-arm summaries are not a treatment-policy estimate."""
    if kind == "RAW_OBSERVED":
        return ("observed data: raw per-arm mean/SD of participants with a measurement at the timepoint "
                "(no imputation; not a treatment-policy estimate)")
    if kind == "RAW_NOT_ESTABLISHED":
        return ("raw per-arm mean/SD as reported; whether the n is observed or imputed is not established "
                "(not a treatment-policy estimate)")
    if kind == "MODEL_BASED":
        name = {"TREATMENT_POLICY": "treatment-policy estimand", "HYPOTHETICAL": "hypothetical estimand",
                "WHILE_ON_TREATMENT": "while-on-treatment estimand"}.get(estimand or "", "estimand not stated by the source")
        return f"{name}: the trial's model-based difference ({method or 'model not stated'}), as reported"
    return "estimand not established"
