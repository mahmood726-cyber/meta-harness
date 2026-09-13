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
  * FIRST_EVENT_RATIO   {RISK_RATIO, ODDS_RATIO, HAZARD_RATIO_FIRST_EVENT} — one event per person, a
                        relative effect; mixing these LABELS is not a real estimand conflict (RALES's
                        Cox "relative risk" + EMPHASIS's "hazard ratio" are both this class).
  * RATE                {INCIDENCE_RATE_RATIO, RATE_RATIO_RECURRENT} — multiple events / person-time.
  * CONTINUOUS          {MEAN_DIFFERENCE, SMD}
Mixing WITHIN a class is compatible (a label-only mix, disclosed); mixing ACROSS classes is a genuine
INCOMPATIBILITY — a recurrent-event rate ratio pooled with a first-event hazard ratio counts different
things (the iv-iron defect, audit 12) and must be flagged, not smoothed into "mixed".

Pure and committed-source-only, so it replays offline and reproduces.
"""
from __future__ import annotations

import re

_CANON = {"RR": "RISK_RATIO", "OR": "ODDS_RATIO", "HR": "HAZARD_RATIO_FIRST_EVENT",
          "IRR": "INCIDENCE_RATE_RATIO", "MD": "MEAN_DIFFERENCE", "SMD": "SMD"}

_CLASS = {
    "RISK_RATIO": "FIRST_EVENT_RATIO", "ODDS_RATIO": "FIRST_EVENT_RATIO",
    "HAZARD_RATIO_FIRST_EVENT": "FIRST_EVENT_RATIO",
    "INCIDENCE_RATE_RATIO": "RATE", "RATE_RATIO_RECURRENT": "RATE",
    "MEAN_DIFFERENCE": "CONTINUOUS", "SMD": "CONTINUOUS",
}

# STRONG statistical-model cues, matched ONLY in the effect's own tightly-scoped source span (never the
# whole abstract), and recorded as an INFORMATIONAL field. They do NOT reclassify the canonical estimand:
# an over-broad cue (bare "recurrent" catches the OUTCOME NAME "recurrent VTE"; bare "rate"/"total"
# catches unrelated prose) previously mis-upgraded binary risk ratios to rate ratios and falsely flagged
# whole topics incompatible. Compatibility is decided by the reported LABEL's canonical class, which is
# already correct: an IRR-labelled trial is RATE by label, an HR/RR/OR is FIRST_EVENT by label. The Cox
# distinction (RALES) does not change the class (a Cox "relative risk" is still FIRST_EVENT, same class as
# an "HR"), so it never affects a mixing decision and needs no risky text inference.
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
