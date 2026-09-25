"""Typed values returned by harness/extract.py (R1 of the regex layer).

Each is a NamedTuple: it IS a tuple -- equal to the bare tuple it replaces, unpacks the same, serialises to the same
JSON -- so no caller changes, while every field is named where the value is made. The field order is the order the
bare tuple had; a test pins it (tests/test_extract_values.py).
"""
from __future__ import annotations

from typing import NamedTuple


class ArmHit(NamedTuple):
    """One arm's event count read from a sentence: where it was read, the count, and its denominator."""
    pos: int
    events: int
    n: int


class ArmCounts(NamedTuple):
    """Two arms' counts, INTERVENTION first: ai events of n1i, ci events of n2i."""
    ai: int
    n1i: int
    ci: int
    n2i: int


class Effect(NamedTuple):
    """A reported relative effect: its scale (RR / OR / HR / IRR), point estimate and confidence limits."""
    scale: str
    point: float
    lo: float
    hi: float


class MeanSDHit(NamedTuple):
    pos: int
    mean: float
    sd: float


class ContinuousArms(NamedTuple):
    """Mean, SD and N per arm, INTERVENTION first."""
    m1: float
    s1: float
    n1: int
    m2: float
    s2: float
    n2: int


class RateHit(NamedTuple):
    pos: int
    events: int
    person_time: float


class RateArms(NamedTuple):
    """Events and person-time per arm, INTERVENTION first."""
    e1: int
    t1: float
    e2: int
    t2: float
