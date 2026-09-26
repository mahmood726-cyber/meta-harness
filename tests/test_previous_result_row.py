"""V1.0.1 page requirement (runbook Step 4; Mahmood: "ten trials please with old k on same page"): the primary
result reads k=10 with the previous result (k=8) BESIDE it -- in the result table, not only in the audit notice.

The previous result is read from the result-change notice's `before` object (never typed), renders only when the
notice opts in (`show_previous_result: true`, so no other topic's page moves), and leaves the countersigned notice
block's bytes unchanged (a signature is on those bytes). Written BEFORE the row existed; needs no cache/.
"""
import json
import os
import re
import html

from harness import page

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIMARY = "3-point major adverse cardiovascular events"


def _notice():
    d = json.load(open(os.path.join(ROOT, "docs", "result_changes.json"), encoding="utf-8"))
    return next(n for n in d["notices"] if n["slug"] == "glp1-ra-mace-t2d" and n["outcome"] == PRIMARY)


def _rendered(s):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", s)).split())


def _review(notice):
    return {"slug": "glp1-ra-mace-t2d", "reproduction": {"result_changes": [notice]}}


def test_glp1_notice_opts_in_and_carries_the_served_v1_result():
    n = _notice()
    assert n.get("show_previous_result") is True
    assert (n["before"]["k"], n["before"]["estimate"], n["before"]["ci_low"], n["before"]["ci_high"]) == (8, 0.856, 0.8086, 0.9061)


def test_previous_result_row_reads_the_notice_before_object():
    o = {"name": PRIMARY, "primary": True, "result": {"scale": "HR", "k": 10}}
    row = page._previous_result_row(o, _review(_notice()))
    assert row is not None
    label, value = row
    text = _rendered(label + " " + value)
    assert "Previous result (k=8)" in text
    assert "HR 0.856 (0.809–0.906)" in text          # Mahmood's form, 3 dp, from before{} not typed
    assert text.lower().count("previous result") >= 1


def test_no_row_without_the_opt_in_or_for_a_secondary_outcome():
    n = dict(_notice())
    n.pop("show_previous_result")
    o = {"name": PRIMARY, "primary": True, "result": {"scale": "HR"}}
    assert page._previous_result_row(o, _review(n)) is None
    assert page._previous_result_row(dict(o, primary=False), _review(_notice())) is None
    assert page._previous_result_row(dict(o, name="another outcome"), _review(_notice())) is None


def test_the_countersigned_block_bytes_do_not_depend_on_the_opt_in():
    n = _notice()
    without = {k: v for k, v in n.items() if k != "show_previous_result"}
    assert page.result_change_block(n) == page.result_change_block(without)
