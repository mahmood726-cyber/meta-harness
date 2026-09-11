"""check_controls gate limb: positive controls must screen IN, negative controls must screen OUT,
and every topic must declare >=1 of each. Uses the real balanced-crystalloids config (pos
29485925/35041780, neg 36534387) with controlled screening records in a temp review dir."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.gate import check_controls  # noqa: E402

SLUG = "balanced-crystalloids-vs-saline-mortality"
POS = ["29485925", "35041780"]
NEG = ["36534387"]


def _review_dir(decisions):
    d = tempfile.mkdtemp(prefix="mh-ctrl-")
    recs = [{"id": f"X · {pid}", "decision": dec} for pid, dec in decisions.items()]
    json.dump({"screening": {"records": recs}},
              open(os.path.join(d, "review.json"), "w", encoding="utf-8"))
    return d


def test_controls_pass_when_pos_in_neg_out():
    d = _review_dir({**{p: "include" for p in POS}, **{n: "exclude" for n in NEG}})
    assert check_controls(d, {"slug": SLUG}) == []


def test_positive_control_screened_out_refused():
    d = _review_dir({POS[0]: "exclude", POS[1]: "include", NEG[0]: "exclude"})
    reasons = check_controls(d, {"slug": SLUG})
    assert any("positive control" in r and POS[0] in r for r in reasons)


def test_negative_control_screened_in_refused():
    d = _review_dir({**{p: "include" for p in POS}, NEG[0]: "include"})
    reasons = check_controls(d, {"slug": SLUG})
    assert any("negative control" in r and NEG[0] in r for r in reasons)


def test_missing_slug_refused():
    assert check_controls(tempfile.mkdtemp(), {}) != []
