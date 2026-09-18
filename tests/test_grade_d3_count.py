"""`grade.rob_basis` ("D3 unassessed on n of N trial(s)") must count every pooled primary trial. Pre-fix (main 237e9094)
the lookup into rob2.trials used the row LABEL while the map is keyed by identifier, so a trial whose label is an acronym
(glp1 SOUL, PMID 40162642) was found by neither key and counted as NEITHER assessed nor unassessed: the served glp1 page
carried "D3 unassessed on 7 of 8" beside a RoB block saying D3 is not assessed for any trial, and the object holds no D3
for any of the 8. Found by the agy adversarial read of served 98726cc1 (2026-09-18); verified against review.json.
A lookup miss that shrinks a denominator is the same class as the legend count in tests/test_absent_legend_count.py.
"""
import json
import os
import re
import subprocess
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import grade  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX_SHA = "237e90946f5b257265b0a3b1c986a8907d12eded"
_RX = re.compile(r"D3 unassessed on (\d+) of (\d+) trial")


def _review():
    with open(os.path.join(ROOT, "docs", "reviews", "glp1-ra-mace-t2d", "review.json"), encoding="utf-8") as f:
        return json.load(f)


def _counts(rob_basis):
    m = _RX.search(rob_basis or "")
    assert m, rob_basis
    return int(m.group(1)), int(m.group(2))


def _expected(review):
    prim = next(o for o in review["outcomes"] if o.get("primary"))
    rob = (review.get("rob2") or {}).get("trials") or {}
    n_un = 0
    for t in prim["trials"]:
        rec = None
        for key in (str(t.get("id") or "").replace("PMID ", ""), str(t.get("label") or "")):
            if key in rob:
                rec = rob[key]
                break
        lvl = (((rec or {}).get("domains") or {}).get("D3_missing_outcome_data") or {}).get("level")
        if not rec or lvl in (None, "not assessed"):
            n_un += 1
    return n_un, len(prim["trials"])


def test_glp1_has_a_label_keyed_row_not_in_rob2():
    review = _review()
    prim = next(o for o in review["outcomes"] if o.get("primary"))
    rob = review["rob2"]["trials"]
    missed = [t for t in prim["trials"] if str(t.get("label")) not in rob]
    assert missed, "the plant needs a pooled row whose label is not a rob2 key (glp1 SOUL)"


def test_d3_count_covers_every_pooled_trial():
    review = _review()
    g = grade.grade(review, review.get("ghost"))
    got = _counts(g["rob_basis"])
    assert got == _expected(review), (got, _expected(review))
    assert got[0] == got[1] == 8  # every glp1 primary trial lacks a D3 assessment on this review object


def test_PLANT_prefix_grade_dropped_the_label_keyed_trial():
    src = subprocess.run(["git", "show", f"{PREFIX_SHA}:harness/grade.py"], cwd=ROOT, capture_output=True, text=True,
                         encoding="utf-8").stdout
    assert '_rob2_trials.get(str(t.get("label")))' in src, "pre-fix source no longer has the defect line; re-pin the plant"
    mod = types.ModuleType("harness._grade_prefix")
    mod.__file__ = os.path.join(ROOT, "harness", "_grade_prefix.py")
    mod.__package__ = "harness"
    sys.modules["harness._grade_prefix"] = mod
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    review = _review()
    got = _counts(mod.grade(review, review.get("ghost"))["rob_basis"])
    assert got == (7, 8), got            # the defect: SOUL counted as neither
    assert _expected(review) == (8, 8)
