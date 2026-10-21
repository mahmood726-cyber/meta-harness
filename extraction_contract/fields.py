"""Typed field definitions for every trial-level value the contract admits.

A value is an ITEM: {"field": <name>, "arm": "intervention"|"comparator"|None, "value": <typed>, "passage": {...}}.
Arm-level fields must name an arm; trial-level fields must not. Types are strict: an int field refuses 12.0 and "12";
a bool is never an int (isinstance(True, int) is True in Python -- excluded explicitly).

OUTCOME fields are the ones a pooled estimate is computed from or whose identity decides poolability; they require a
dual independent reading. DESCRIPTIVE fields need a typed value and a passage, not a second reader.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

ARMS = ("intervention", "comparator")
RATIO_SCALES = ("HR", "OR", "RR", "IRR")
DIFFERENCE_SCALES = ("RD", "MD", "SMD")
SCALES = RATIO_SCALES + DIFFERENCE_SCALES
ANALYSIS_SETS = ("ITT", "mITT", "PP", "AS_TREATED")
CI_LEVELS = (0.90, 0.95, 0.99)


@dataclass(frozen=True)
class FieldSpec:
    name: str
    kind: str                 # "int" | "float" | "enum" | "text"
    role: str                 # "OUTCOME" | "DESCRIPTIVE"
    arm_level: bool
    minimum: float | None = None
    exclusive_minimum: bool = False
    choices: tuple = ()
    meaning: str = ""


FIELDS = {f.name: f for f in (
    FieldSpec("trial_id", "text", "DESCRIPTIVE", False, meaning="registry id (NCT/ISRCTN/...) or PMID as printed"),
    FieldSpec("n_randomised", "int", "DESCRIPTIVE", True, 1, meaning="participants randomised to the arm"),
    FieldSpec("events", "int", "OUTCOME", True, 0, meaning="participants with the outcome event in the arm"),
    FieldSpec("total", "int", "OUTCOME", True, 1, meaning="denominator the events are counted over"),
    FieldSpec("n_analysed", "int", "OUTCOME", True, 1, meaning="participants analysed for a continuous outcome"),
    FieldSpec("mean", "float", "OUTCOME", True, meaning="arm mean (or mean change) of the continuous outcome"),
    FieldSpec("sd", "float", "OUTCOME", True, 0, exclusive_minimum=True, meaning="arm standard deviation"),
    FieldSpec("effect_point", "float", "OUTCOME", False, meaning="reported between-arm effect estimate"),
    FieldSpec("effect_ci_low", "float", "OUTCOME", False, meaning="lower confidence limit as printed"),
    FieldSpec("effect_ci_high", "float", "OUTCOME", False, meaning="upper confidence limit as printed"),
    FieldSpec("effect_scale", "enum", "OUTCOME", False, choices=SCALES, meaning="scale of the reported effect"),
    FieldSpec("ci_level", "float", "OUTCOME", False, choices=CI_LEVELS, meaning="confidence level, e.g. 0.95"),
    FieldSpec("outcome_definition", "text", "OUTCOME", False, meaning="the outcome as the trial defines it"),
    FieldSpec("timepoint", "text", "OUTCOME", False, meaning="when the outcome was assessed"),
    FieldSpec("analysis_set", "enum", "OUTCOME", False, choices=ANALYSIS_SETS, meaning="population analysed"),
)}

# What a trial must carry to be poolable under each measure (the served values, after dual resolution).
REQUIRED_BY_MEASURE = {
    "binary": [("events", a) for a in ARMS] + [("total", a) for a in ARMS] + [("outcome_definition", None)],
    "continuous": [(f, a) for f in ("mean", "sd", "n_analysed") for a in ARMS] + [("outcome_definition", None)],
    "ratio": [("effect_point", None), ("effect_ci_low", None), ("effect_ci_high", None), ("effect_scale", None),
              ("ci_level", None), ("outcome_definition", None)],
}


def key(item) -> tuple:
    return (item.get("field"), item.get("arm"))


def type_problems(item) -> list[str]:
    """Problems with ONE item's shape and type (empty list = well-typed)."""
    f, arm, v = item.get("field"), item.get("arm"), item.get("value")
    spec = FIELDS.get(f)
    where = f"{f}" + (f"[{arm}]" if arm else "")
    if spec is None:
        return [f"{where}: unknown field (not in the contract's FIELDS)"]
    out = []
    if spec.arm_level and arm not in ARMS:
        out.append(f"{where}: arm-level field needs arm in {ARMS}")
    if not spec.arm_level and arm is not None:
        out.append(f"{where}: trial-level field must not name an arm")
    if spec.kind == "int":
        if isinstance(v, bool) or not isinstance(v, int):
            out.append(f"{where}: {v!r} is not an int")
            return out
    elif spec.kind == "float":
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            out.append(f"{where}: {v!r} is not a finite number")
            return out
    elif spec.kind in ("enum", "text"):
        if not isinstance(v, str) or not v.strip():
            out.append(f"{where}: {v!r} is not a non-empty string")
            return out
    if spec.choices and v not in spec.choices:
        out.append(f"{where}: {v!r} not in {spec.choices}")
    if spec.minimum is not None and isinstance(v, (int, float)):
        if v < spec.minimum or (spec.exclusive_minimum and v == spec.minimum):
            out.append(f"{where}: {v!r} below its minimum ({'>' if spec.exclusive_minimum else '>='}{spec.minimum})")
    return out


def coherence_problems(values: dict) -> list[str]:
    """Cross-field checks over one trial's resolved values {(field, arm): value}."""
    out = []
    for a in ARMS:
        e, t = values.get(("events", a)), values.get(("total", a))
        if isinstance(e, int) and isinstance(t, int) and e > t:
            out.append(f"events[{a}]={e} exceeds total[{a}]={t}")
        n_r, t2 = values.get(("n_randomised", a)), values.get(("total", a))
        if isinstance(n_r, int) and isinstance(t2, int) and t2 > n_r:
            out.append(f"total[{a}]={t2} exceeds n_randomised[{a}]={n_r} (a denominator larger than the arm)")
    p, lo, hi = values.get(("effect_point", None)), values.get(("effect_ci_low", None)), values.get(("effect_ci_high", None))
    scale = values.get(("effect_scale", None))
    if all(isinstance(x, (int, float)) for x in (p, lo, hi)):
        if not lo <= p <= hi:
            out.append(f"effect CI [{lo}, {hi}] does not bracket the point {p}")
        if scale in RATIO_SCALES and min(p, lo, hi) <= 0:
            out.append(f"{scale} is a ratio scale but a value is <= 0 ({p}, {lo}, {hi})")
    return out
