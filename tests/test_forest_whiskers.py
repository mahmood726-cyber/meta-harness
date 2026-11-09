"""C5 (external audit R8-2): every forest draws a null line, a whisker for every row, and the pooled point even when its
CI is not served. Before the fix, 26 of the 56 served forests had no null line, 25 had rows without a whisker and 13
served a pooled estimate that was not drawn."""
from __future__ import annotations

import json
import math
from pathlib import Path

from harness import manuscript as M
from harness.known_missing import _study_from_trial

ROOT = Path(__file__).resolve().parents[1]


def _o(trials, **res):
    return {"name": "x", "estimand": res.get("scale", "RR"), "trials": trials, "result": dict({"k": len(trials)}, **res)}


def test_PLANT_the_null_line_is_drawn_even_when_every_ci_is_on_one_side():
    o = _o([{"label": "A", "effect": 0.5, "ci_low": 0.4, "ci_high": 0.6, "scale": "RR"},
            {"label": "B", "effect": 0.55, "ci_low": 0.45, "ci_high": 0.7, "scale": "RR"}],
           scale="RR", estimate=0.52, ci_low=0.44, ci_high=0.62)
    assert "stroke-dasharray" in M.forest_for(o)


def test_PLANT_a_counts_only_row_gets_the_pools_own_per_study_ci_marked_as_display_only():
    t = {"label": "C", "ai": 20, "n1i": 100, "ci": 30, "n2i": 100, "scale": "RR"}
    svg = M.forest_for(_o([t, {"label": "D", "effect": 0.8, "ci_low": 0.6, "ci_high": 1.1, "scale": "RR"}],
                          scale="RR", estimate=0.75, ci_low=0.5, ci_high=1.1))
    y, v = _study_from_trial(t, "RR").yi_vi()                     # the variance the pool itself uses
    lo, hi = math.exp(y - 1.959963984540054 * math.sqrt(v)), math.exp(y + 1.959963984540054 * math.sqrt(v))
    assert f"[{M._fmt(lo)}, {M._fmt(hi)}]†" in svg
    assert "not a served number" in svg
    assert svg.count("<line") - 1 == svg.count("<rect")              # every row has a whisker (minus the null line)


def test_PLANT_a_pooled_estimate_without_a_served_ci_is_drawn_and_says_so():
    o = _o([{"label": "A", "effect": 0.8, "ci_low": 0.7, "ci_high": 0.9, "scale": "HR"},
            {"label": "B", "effect": 0.7, "ci_low": 0.6, "ci_high": 0.82, "scale": "HR"}],
           scale="HR", estimate=0.75, ci_low=None, ci_high=None)
    svg = M.forest_for(o)
    assert "<circle" in svg and "(CI not served)" in svg and "its CI is not served" in svg


def test_every_served_forest_has_a_null_line_whiskers_and_its_pooled_point():
    n = 0
    for p in sorted((ROOT / "docs" / "reviews").glob("*/review.json")):
        for o in json.loads(p.read_text(encoding="utf-8"))["outcomes"]:
            res = o.get("result") or {}
            svg = M.forest_for(o) if res.get("k") else ""
            if not svg:
                continue
            n += 1
            assert "stroke-dasharray" in svg, (p.parent.name, o["name"])
            assert svg.count("<line") - 1 >= svg.count("<rect"), (p.parent.name, o["name"])
            if res.get("estimate") is not None:
                assert "<polygon" in svg or "<circle" in svg, (p.parent.name, o["name"])
    assert n == 56, n                                                  # the denominator: every forest drawn today
