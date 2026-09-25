"""R1: harness/extract.py returns typed values (harness/extract_values.py) that are indistinguishable from the bare
tuples they replaced wherever a caller could look -- equality, unpacking, JSON -- and named where they are made."""
from __future__ import annotations

import json

from harness import extract
from harness.extract_values import ArmCounts, ContinuousArms, Effect, RateArms


def test_field_order_is_the_old_tuple_order():
    assert ArmCounts._fields == ("ai", "n1i", "ci", "n2i")
    assert Effect._fields == ("scale", "point", "lo", "hi")
    assert ContinuousArms._fields == ("m1", "s1", "n1", "m2", "s2", "n2")
    assert RateArms._fields == ("e1", "t1", "e2", "t2")


def test_a_typed_value_is_the_bare_tuple_to_every_caller():
    v = ArmCounts(12, 200, 20, 201)
    assert v == (12, 200, 20, 201) and isinstance(v, tuple)
    ai, n1i, ci, n2i = v
    assert (ai, ci) == (12, 20)
    assert json.dumps(v) == json.dumps((12, 200, 20, 201))
    assert json.dumps({"e": Effect("HR", 0.8, 0.7, 0.9)}) == json.dumps({"e": ("HR", 0.8, 0.7, 0.9)})


def test_the_extractors_return_typed_values():
    s = "Death occurred in 12 (6.0%) of 200 patients in the colchicine group and 20 (10.0%) of 201 in the placebo group."
    got = extract.extract_arm_counts(s, ["colchicine"], ["placebo"])
    assert isinstance(got, ArmCounts) and got == (12, 200, 20, 201)
    m = extract._EFFECT.search("hazard ratio 0.80 (95% CI 0.70 to 0.90)")
    eff = extract._effect_from_match(m) if m else None
    assert isinstance(eff, Effect) and eff.scale == "HR" and eff.point == 0.8
