"""Effect-measure type system (TIER-1 #2) + the three-field effect object (audit 18).

A reported effect carries three things, not one:
  * reported_label     — what the paper called it: "RR" / "OR" / "HR" / "rate ratio" / "MD" ...
  * statistical_model  — the model behind it, when the source states one: Cox proportional-hazards ->
                         a relative HAZARD even if the paper writes "relative risk" (RALES); logistic
                         -> odds; person-time/recurrent -> a rate. Absent when the source does not say.
  * canonical_estimand — the type used for POOLING COMPATIBILITY, one of:
        RISK_RATIO · ODDS_RATIO · HAZARD_RATIO_FIRST_EVENT · INCIDENCE_RATE_RATIO ·
        RATE_RATIO_RECURRENT · MEAN_DIFFERENCE · SMD

Pooling compatibility is decided by CLASS, not by label. Two effects are compatible only if they share
event multiplicity and time structure:
  * FIRST_EVENT_RATIO   {RISK_RATIO, HAZARD_RATIO_FIRST_EVENT} — one event per person, a
                        relative effect; mixing HR/RR labels is disclosed as approximate (RALES's
                        Cox "relative risk" + EMPHASIS's "hazard ratio" are both this class).
  * ODDS_RATIO          {ODDS_RATIO} — odds are not risks; OR is compatible only with OR unless an
                        explicit, source-backed conversion is recorded upstream.
  * RATE                {INCIDENCE_RATE_RATIO, RATE_RATIO_RECURRENT} — multiple events / person-time.
  * CONTINUOUS          {MEAN_DIFFERENCE, SMD}
Mixing WITHIN a class is compatible (a label-only mix, disclosed); mixing ACROSS classes is a genuine
INCOMPATIBILITY — a recurrent-event rate ratio pooled with a first-event hazard ratio, or an odds ratio
pooled with a risk/hazard ratio, counts different things and must be flagged, not smoothed into "mixed".

Pure and committed-source-only, so it replays offline and reproduces.
"""
from __future__ import annotations

import re

_CANON = {"RR": "RISK_RATIO", "OR": "ODDS_RATIO", "HR": "HAZARD_RATIO_FIRST_EVENT",
          "IRR": "INCIDENCE_RATE_RATIO", "MD": "MEAN_DIFFERENCE", "SMD": "SMD"}

_CLASS = {
    "RISK_RATIO": "FIRST_EVENT_RATIO", "ODDS_RATIO": "ODDS_RATIO",
    "HAZARD_RATIO_FIRST_EVENT": "FIRST_EVENT_RATIO",
    "INCIDENCE_RATE_RATIO": "RATE", "RATE_RATIO_RECURRENT": "RATE",
    "MEAN_DIFFERENCE": "CONTINUOUS", "SMD": "CONTINUOUS",
}

# STRONG statistical-model cues, matched ONLY in the effect's own tightly-scoped source span (never the
# whole abstract), and recorded as an INFORMATIONAL field. They do NOT reclassify the canonical estimand:
# an over-broad cue (bare "recurrent" catches the OUTCOME NAME "recurrent VTE"; bare "rate"/"total"
# catches unrelated prose) previously mis-upgraded binary risk ratios to rate ratios and falsely flagged
# whole topics incompatible. Compatibility is decided by the reported LABEL's canonical class, which is
# already correct: an IRR-labelled trial is RATE by label, an HR/RR is FIRST_EVENT by label, and an OR is
# odds by label. The Cox distinction (RALES) does not change the class (a Cox "relative risk" is still
# FIRST_EVENT, same class as an "HR"), so it never affects a mixing decision and needs no risky text
# inference.
_COX = re.compile(r"\bcox\b|proportional[- ]hazards? (?:model|regression)", re.I)
_RATE_MODEL = re.compile(r"rate ratio|per (?:100 )?person[- ]?years?|incidence[- ]rate|"
                         r"recurrent[- ]event (?:analysis|method)|lin[- ]wei[- ]yang[- ]ying", re.I)


def classify(reported_scale: str | None, source_text: str = "") -> dict:
    """Return the three-field effect object for one trial's effect. canonical_estimand comes from the
    reported LABEL (never guessed from prose); statistical_model is an INFORMATIONAL note set only when a
    strong model cue sits in the effect's own source span. The model note never changes the canonical
    estimand — compatibility is a class decision and the label already fixes the class."""
    label = (reported_scale or "").strip()
    txt = source_text or ""
    canon = _CANON.get(label.upper(), label.upper() or "UNKNOWN")
    model = None
    if _COX.search(txt):
        model = "cox_proportional_hazards"
    elif _RATE_MODEL.search(txt):
        model = "rate / person-time"
    return {"reported_label": label or None, "statistical_model": model, "canonical_estimand": canon}


def compatibility_class(canonical_estimand: str) -> str:
    return _CLASS.get(canonical_estimand, "OTHER")


def pool_compatibility(effects: list) -> dict:
    """Given the pooled trials' three-field objects, decide the pool's estimand status:
      {status: 'homogeneous'|'compatible_labels'|'incompatible', classes, canonicals, labels}.
    homogeneous       — one canonical estimand.
    compatible_labels — >1 label but ONE compatibility class (poolable; disclosed, not a defect).
    incompatible      — >1 compatibility class (a genuine estimand conflict; must be flagged)."""
    canonicals = sorted({e["canonical_estimand"] for e in effects if e.get("canonical_estimand")})
    labels = sorted({e["reported_label"] for e in effects if e.get("reported_label")})
    classes = sorted({compatibility_class(c) for c in canonicals})
    if len(canonicals) <= 1:
        status = "homogeneous"
    elif len(classes) == 1:
        status = "compatible_labels"
    else:
        status = "incompatible"
    return {"status": status, "classes": classes, "canonicals": canonicals, "labels": labels}


# ---------------------------------------------------------------------------------------------------------------------------
# THE POOL'S MEASURE IS DERIVED FROM ITS ADMITTED INPUTS, NEVER DECLARED (external review of balanced-crystalloids, 2026-09-26:
# the served headline said HR while the 2-trial pool mixed PLUS's reconstructed RR 0.9918 with BaSICS's adjusted HR 0.97 --
# pool_compatibility's FIRST_EVENT_RATIO class let it through, and the label came from the topic's declared estimand).
# pool_compatibility() above stays a DESCRIPTION of the effect classes; pool_measure_decision() is the GATE.

RATIO_LABELS = ("HR", "RR", "OR", "IRR")
# COVARIATE adjustment only: "adjusted hazard/relative risk/odds ratio", "adjust(ed|ing) for", multivariable/multivariate,
# covariate-adjusted. Not "multiplicity-adjusted" (a CI level for two doses) or "dose-adjusted": a hyphen-prefixed
# "-adjusted" names something else being adjusted (NOAC ENGAGE-AF's 97.5% CI was tagged ADJUSTED by the bare word).
_ADJUSTED = re.compile(r"(?<![-\w])adjusted\s+(?:hazard|relative|risk|odds|rate|incidence|HR|RR|OR|IRR)\b"
                       r"|(?<![-\w])adjust(?:ed|ing)?\s+for\b|\bmultivariab?le\b|\bmultivariate\b|\bcovariate[- ]adjusted\b", re.I)
_UNADJUSTED = re.compile(r"\bunadjusted\b|\bcrude\b", re.I)


def input_label(t: dict, count_measure: str) -> str | None:
    """The measure the ENGINE pools for one admitted input: a stated effect's own scale; arm counts -> the ratio the engine
    reconstructs (`count_measure`, RR or OR); events over person-time -> IRR; means -> MD."""
    if t.get("e1i") is not None:
        return "IRR"
    if t.get("mean1") is not None:
        return "MD"
    if t.get("effect") is None and t.get("ai") is not None:
        return count_measure
    return (t.get("scale") or "").upper() or None


def adjustment_of(t: dict) -> str:
    """ADJUSTED / UNADJUSTED / UNSTATED. Reconstructed from counts -> UNADJUSTED. A stated effect is ADJUSTED or UNADJUSTED only
    when its OWN source quotation says so; otherwise UNSTATED (never guessed)."""
    if t.get("effect") is None and (t.get("ai") is not None or t.get("e1i") is not None or t.get("mean1") is not None):
        return "UNADJUSTED"
    src = t.get("source") or ""
    if _UNADJUSTED.search(src):
        return "UNADJUSTED"
    if _ADJUSTED.search(src):
        return "ADJUSTED"
    return "UNSTATED"


def mixture_policy(spec: dict | None) -> dict | None:
    """A PREDECLARED per-outcome policy naming the mixture it allows, or None. Anything short of a complete declaration is no
    policy (fail closed): {"allow": ["HR", "RR"], "predeclared": true, "decided_by": ..., "decided_on": ..., "rationale": ...,
    optional "allow_adjustment_mixture": true}."""
    p = (spec or {}).get("measure_mixture_policy")
    if not isinstance(p, dict) or p.get("predeclared") is not True:
        return None
    allow = sorted({str(x).upper() for x in (p.get("allow") or [])})
    if len(allow) < 2 or not set(allow) <= set(RATIO_LABELS) or not all(p.get(k) for k in ("decided_by", "decided_on", "rationale")):
        return None
    return {**p, "allow": allow}


def mixed_label(labels) -> str:
    return "mixed ratio (" + "+".join(sorted(labels)) + ")"


def pool_measure_decision(labels: list, adjustments: list, policy: dict | None) -> dict:
    """The GATE. One measure -> {state: DERIVED, label}. Several measures -> refused (POOL_MEASURE_MIXED) unless a predeclared
    policy names exactly this set of ratio measures -> {state: MIXED_BY_POLICY, label: 'mixed ratio (HR+RR)', policy}. An input
    whose measure is unknown refuses (POOL_MEASURE_UNIDENTIFIED). ADJUSTED beside UNADJUSTED refuses (POOL_ADJUSTMENT_MIXED)
    unless the policy says allow_adjustment_mixture; the per-group analyses are always reported."""
    got = sorted({x for x in labels if x})
    out = {"input_measures": dict(sorted({x: labels.count(x) for x in set(labels)}.items(), key=lambda kv: str(kv[0]))),
           "adjustment": {a: adjustments.count(a) for a in sorted(set(adjustments))}, "policy": policy}
    if any(x is None for x in labels) or not got:
        return {**out, "state": "REFUSED", "code": "POOL_MEASURE_UNIDENTIFIED", "label": None,
                "reason": "an admitted input carries no identifiable effect measure; the pooled measure cannot be derived"}
    if len(got) == 1:
        dec = {**out, "state": "DERIVED", "label": got[0]}
    elif policy and set(got) == set(policy["allow"]):
        dec = {**out, "state": "MIXED_BY_POLICY", "label": mixed_label(got)}
    else:
        return {**out, "state": "REFUSED", "code": "POOL_MEASURE_MIXED", "label": mixed_label(got),
                "reason": (f"the admitted inputs are {' and '.join(got)} ({out['input_measures']}): different effect measures are not one "
                           "quantity, and a shared label class does not make them one. Refused by default; a predeclared "
                           "per-outcome measure_mixture_policy naming exactly this mixture is the only way to pool them")}
    if "ADJUSTED" in adjustments and "UNADJUSTED" in adjustments and not (policy or {}).get("allow_adjustment_mixture"):
        return {**dec, "state": "REFUSED", "code": "POOL_ADJUSTMENT_MIXED",
                "reason": ("the pool combines covariate-ADJUSTED and UNADJUSTED effects; they are kept as separate analysis groups "
                           "and not combined into one headline without a predeclared policy (allow_adjustment_mixture)")}
    return dec
