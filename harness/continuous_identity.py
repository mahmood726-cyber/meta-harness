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
_MODEL_METHOD = re.compile(r"(?i)\bANCOVA\b|analysis\s+of\s+covariance|regression|mixed\s+model|\bMMRM\b|repeated\s+measure")
_MODEL_WITH_TERMS = re.compile(r"(?i)model\s+with\s+terms|adjusted\s+for|covariates?\b")


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
            # ADJUSTED when the parameter says so (LS mean) OR the method / description is a covariate model (Wade: ANCOVA,
            # "linear regression model with terms for treatment ... and baseline sleep latency", -15.6 vs raw -17.4)
            "estimate_kind": ("ADJUSTED_DIFFERENCE" if (_ADJUSTED.search(str(a.get("paramType") or ""))
                                                       or _MODEL_METHOD.search(str(a.get("statisticalMethod") or ""))
                                                       or _MODEL_WITH_TERMS.search(str(a.get("groupDescription") or "")))
                              else "DIFFERENCE_NOT_TYPED"),
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
                    exper_title_terms=None) -> dict[str, Any]:
    """The trial's reported ADJUSTED difference with an established SE, for the model-based sensitivity analysis -- or a
    typed refusal. A multi-dose trial whose adjusted differences are per dose is refused (no combined adjusted difference
    exists; one is never constructed from per-dose model estimates)."""
    tm = typed_measure(om)
    adj = [a for a in tm["analyses"] if a["estimate_kind"] == "ADJUSTED_DIFFERENCE"]
    if not adj:
        return {"state": "NO_ADJUSTED_DIFFERENCE", "measure_title": tm["title"]}
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
            "se_basis": se["basis"], "ci": a["ci"], "procedure": proc, "method": a["method"]}


# =========================================================================== melatonin review (2026-09-27, retrospective,
# decided by Dispatch under Mahmood's delegation): population default, measurement class, crossover pairing
# --------------------------------------------------------------------------- (1) population default
_SUBGROUP = re.compile(r"(?i)\bsub-?groups?\b|\blow\s+excretors?\b|\bpre-?planned\s+analysis\s+on\s+[^.;]{0,40}?population\s+aged?(?:\s*\d{2}\s*(?:-|–|to)\s*\d{2})?"
                       r"|\bpopulation\s+(?:aged?\s+)?\d{2}\s*(?:-|–|to)\s*\d{2}\b|\baged?\s+\d{2}\s*(?:-|–|to)\s*\d{2}\b"
                       r"|\b\d{2}\s*(?:-|–|to)\s*\d{2}\s*(?:-\s*)?years?\s+(?:old\s+)?(?:population|subgroup|group)\b")


def population_class(row: dict[str, Any], spec: dict[str, Any] | None) -> dict[str, Any]:
    """FULL_ELIGIBLE unless the row's own source or the topic's annotation says the number is a SUBGROUP (an age band, low
    excretors, a pre-planned subgroup). A subgroup is never the primary input for a broad question and never pooled as
    independent of its own trial's full population."""
    pid = str(row.get("id") or "").replace("PMID ", "")
    ann = ((spec or {}).get("trial_annotations") or {}).get(pid) or {}
    if "subgroup" in str(ann.get("evidence_unit") or "").lower():
        return {"population": "SUBGROUP", "label": ann.get("evidence_unit_detail") or ann.get("evidence_unit"),
                "basis": "trial annotation (topic)"}
    src = str(row.get("source") or "")
    pop = src.split("population:", 1)[1] if "population:" in src else ""
    m = _SUBGROUP.search(pop) or _SUBGROUP.search(str(row.get("population_description") or ""))
    if m:
        return {"population": "SUBGROUP", "label": m.group(0).strip(), "basis": "the row's own population statement"}
    return {"population": "FULL_ELIGIBLE", "basis": "no subgroup statement in the row's source or annotation"}


# --------------------------------------------------------------------------- (2) measurement class
_MEASUREMENT = (("PSG", re.compile(r"(?i)polysomnograph\w*|\bPSG\b|\bEEG\b|electroencephalograph\w*|latency\s+to\s+persistent\s+sleep|\bLPS\b")),
                ("DIARY", re.compile(r"(?i)sleep\s+diar\w*|\bdiar(?:y|ies)\b|sleep\s+logs?\b")),
                ("QUESTIONNAIRE", re.compile(r"(?i)\bPSQI\b|pittsburgh\s+sleep\s+quality|questionnaire|\bLSEQ\b|leeds\s+sleep|"
                                             r"insomnia\s+severity\s+index")),
                ("ACTIGRAPHY", re.compile(r"(?i)actigraph\w*|\bwrist\s+activity")))


def measurement_class(texts) -> dict[str, Any]:
    """PSG / DIARY / QUESTIONNAIRE / ACTIGRAPHY from the words the SOURCE uses for THIS number; AMBIGUOUS when the same text names
    two classes; SUBJECTIVE_UNSPECIFIED for 'subjective' alone (diary or questionnaire); NOT_STATED otherwise. Never inferred
    from the outcome's name."""
    found = {}
    for t in texts or []:
        for cls, rx in _MEASUREMENT:
            m = rx.search(t or "")
            if m:
                found.setdefault(cls, m.group(0))
    if len(found) == 1:
        (cls, words), = found.items()
        return {"class": cls, "words": words}
    if len(found) > 1:
        return {"class": "AMBIGUOUS", "words": found}
    if any(re.search(r"(?i)\bsubjective\b", t or "") for t in texts or []):
        return {"class": "SUBJECTIVE_UNSPECIFIED", "words": "subjective"}
    return {"class": "NOT_STATED", "words": None}


# --------------------------------------------------------------------------- (3) crossover
_CROSSOVER_TEXT = re.compile(r"(?i)\bcross-?over\b|\beach\s+(?:patient|participant|subject)\s+received\s+(?:each|all)\b|"
                             r"\breceived,?\s+in\s+random\s+order\b")


def crossover_state(row: dict[str, Any], registry_row: dict[str, Any] | None, held_text: str | None) -> dict[str, Any] | None:
    """A crossover's arms are periods in the same people. A continuous row given as per-arm mean/SD is two INDEPENDENT arms and
    is refused: the analysis needs the paired (within-person) difference with its own SD or SE. None when not a crossover."""
    model = str((registry_row or {}).get("intervention_model") or "").upper()
    m = _CROSSOVER_TEXT.search(held_text or "")
    if model != "CROSSOVER" and not m:
        return None
    basis = "registry intervention_model CROSSOVER" if model == "CROSSOVER" else f"held text: '{m.group(0)}'"
    if row.get("paired_md") is not None and (row.get("paired_se") is not None or row.get("paired_sd_diff") is not None):
        return {"design": "CROSSOVER", "basis": basis, "state": "PAIRED_ADMITTED"}
    if row.get("mean1") is not None:
        return {"design": "CROSSOVER", "basis": basis, "state": "CROSSOVER_PAIRED_VARIANCE_REQUIRED",
                "reason": ("a crossover's periods are the same people: per-arm means and SDs analysed as independent parallel arms "
                           "give the wrong variance. The paired (within-person) difference with its SD or SE is required")}
    return {"design": "CROSSOVER", "basis": basis, "state": "EFFECT_AS_REPORTED",
            "note": "a reported crossover effect is taken as the trial's paired estimate only if its source says so"}


def split_continuous_inputs(trials: list[dict[str, Any]], spec: dict[str, Any] | None, texts_for, registry_for, held_for):
    """Apply (1)-(3) to an outcome's continuous rows. Returns (primary rows, record). Subgroup rows go to subgroup analyses;
    rows of another measurement class than the declared primary class go to separate per-class analyses (and, when no class is
    declared and classes are mixed, EVERY class is separate and the primary is refused); crossover rows without a paired
    variance are held. texts_for / registry_for / held_for are callables on a row."""
    rule = (spec or {}).get("population_default") or {}
    mrule = (spec or {}).get("measurement_classes") or {}
    rec = {"subgroups": [], "held_crossover": [], "classes": {}, "primary_class": mrule.get("primary"), "state": None}
    keep = []
    for t in trials:
        if t.get("mean1") is None and str(t.get("scale") or "").upper() not in ("MD", "SMD"):
            keep.append(t)
            continue
        cx = crossover_state(t, registry_for(t), held_for(t))
        if cx:
            t["crossover"] = cx
            if cx["state"] == "CROSSOVER_PAIRED_VARIANCE_REQUIRED":
                rec["held_crossover"].append(t)
                continue
        pc = population_class(t, spec)
        t["population_class"] = pc
        mc = measurement_class(texts_for(t))
        t["measurement_class"] = mc
        if str(rule.get("rule") or "").upper() == "FULL_ELIGIBLE" and pc["population"] == "SUBGROUP":
            rec["subgroups"].append(t)
            continue
        keep.append(t)
    if mrule.get("separate_by_class"):
        by = {}
        for t in keep:
            by.setdefault((t.get("measurement_class") or {}).get("class", "NOT_STATED"), []).append(t)
        rec["classes"] = {k: [r.get("id") for r in v] for k, v in by.items()}
        prim = mrule.get("primary")
        if len(by) > 1 and not prim:
            rec["state"] = "MEASUREMENT_CLASS_MIXED_PRIMARY_NOT_DECLARED"
            rec["by_class"] = by
            return [], rec
        if prim:
            rec["by_class"] = {k: v for k, v in by.items() if k != prim}
            return by.get(prim, []), rec
    return keep, rec
