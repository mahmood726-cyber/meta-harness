"""V13-03Q (signed 9 Oct, 'sign v13' / 'yes to all recommended'): eleven outcomes declared RR and served the trials'
published HR are amended to declare HR. The amendment is POST HOC (made after the results were seen) and the page must
say so beside the estimand, keeping the original declaration -- never a silent rewrite of the protocol."""
import json
import os

from harness import page

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = [{"until": "2026-10-09", "declared": "RR", "amended_to": "HR", "post_hoc": True,
         "changed_by": "V13-03Q (A), signed by Mahmood 9 Oct 2026"}]


def test_PLANT_the_estimand_amendment_row_says_post_hoc_and_keeps_the_original():
    o = {"name": "Hip fracture", "estimand": "HR", "estimand_history": HIST}
    txt = page._estimand_amendment_text(o)
    assert txt and "post hoc" in txt.lower() and "RR" in txt and "HR" in txt and "V13-03Q" in txt
    assert page._estimand_amendment_text({"name": "x", "estimand": "HR"}) is None


def test_every_amended_topic_outcome_carries_its_history():
    amended = 0
    for f in sorted(os.listdir(os.path.join(ROOT, "topics"))):
        t = json.load(open(os.path.join(ROOT, "topics", f), encoding="utf-8"))
        for key in ("primary_outcome", "secondary_outcomes", "harm_outcomes"):
            v = t.get(key)
            for o in (v if isinstance(v, list) else [v]):
                if isinstance(o, dict) and o.get("estimand_history"):
                    h = o["estimand_history"][-1]
                    assert h["declared"] != o["estimand"] and h["amended_to"] == o["estimand"] and h["post_hoc"] is True
                    amended += 1
    assert amended == 11, amended
