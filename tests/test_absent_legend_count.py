"""The outcome legend's "only no outcome data in source (n here) is a claim about the trial itself" must count the
rows that carry that TYPED state (absence.OUTCOME_NOT_IN_SOURCE), not only the legacy spelling
NO_OUTCOME_DATA_IN_SOURCE that no row carries any more. Pre-fix (main 237e9094) the number was 0 on every page:
glp1's primary outcome rendered "(0 here)" beside ELIXA's row in exactly that state. Found by the agy adversarial
read of served review 98726cc1 (2026-09-18); verified mechanically against review.json before this test was written.
The plant renders the committed review with the PRE-FIX page.py taken from git, so the test proves the defect fired.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import absence, page  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX_SHA = "237e90946f5b257265b0a3b1c986a8907d12eded"
_LEGEND = re.compile(r"only <em>no outcome data in source</em> \((\d+) here\)")


def _review():
    with open(os.path.join(ROOT, "docs", "reviews", "glp1-ra-mace-t2d", "review.json"), encoding="utf-8") as f:
        return json.load(f)


def _legend_counts(html):
    return [int(x) for x in _LEGEND.findall(html)]


def _expected(review):
    out = []
    for o in review["outcomes"]:
        if o.get("kind") == "harm" or not (o.get("trials") and o.get("declared_absent_trials")):
            continue
        out.append(sum(1 for a in o["declared_absent_trials"]
                       if (a.get("state") or "") in ("NO_OUTCOME_DATA_IN_SOURCE", absence.OUTCOME_NOT_IN_SOURCE)))
    return out


def test_glp1_has_a_row_in_the_typed_state():
    prim = next(o for o in _review()["outcomes"] if o.get("primary"))
    states = [a.get("state") for a in prim["declared_absent_trials"]]
    assert absence.OUTCOME_NOT_IN_SOURCE in states, states  # ELIXA on the committed review


def test_legend_counts_the_typed_state():
    review = _review()
    html = page.render_page(review)
    got = _legend_counts(html)
    exp = _expected(review)
    assert got, "legend sentence not rendered"
    assert got[0] == exp[0] and exp[0] >= 1, (got, exp)


def test_PLANT_prefix_page_rendered_zero():
    """The pre-fix renderer (page.py at 237e9094, read from git, executed in-process) prints 0 for the same review."""
    src = subprocess.run(["git", "show", f"{PREFIX_SHA}:harness/page.py"], cwd=ROOT, capture_output=True, text=True,
                         encoding="utf-8").stdout
    assert 'get("NO_OUTCOME_DATA_IN_SOURCE", 0)' in src, "pre-fix source no longer has the defect line; re-pin the plant"
    spec = importlib.util.spec_from_loader("harness._page_prefix", loader=None)
    mod = types.ModuleType("harness._page_prefix")
    mod.__file__ = os.path.join(ROOT, "harness", "_page_prefix.py")
    mod.__package__ = "harness"
    sys.modules["harness._page_prefix"] = mod
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    review = _review()
    got = _legend_counts(mod.render_page(review))
    assert got and got[0] == 0, got  # the defect: 0 beside a row in the counted state
    assert _expected(review)[0] >= 1
