"""Plants (8 Oct, forest lane): a figure-only comparator pool is recorded only from an ACCEPTED dual read of THIS
comparator whose pool is reproduced and printed nowhere in the text; anything else refuses."""
import copy
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import comparator_figure_result as cfr  # noqa: E402

GOOD = {"results": {"t": {"pmid": "9", "state": "ACCEPTED", "measure": "MD",
                          "pooled_agreed": {"effect": "-3.72", "lower": "-8.45", "upper": "1.01"},
                          "acceptance": {"state": "ACCEPTED", "methods_reproducing": ["DL"],
                                         "pooled_anchor": "PRINTED_IN_FIGURE_ONLY", "recomputed": {}},
                          "readings": {"codex": {"record_id": "mc-a"}, "agy": {"record_id": "mc-b"}},
                          "figure": {"fig_id": "X2", "caption": "SOL"}, "image": {"ref": "i.png", "sha256": "s"}}}}


def test_records_the_agreed_printed_pool():
    e, why = cfr.figure_result("t", GOOD, "9")
    assert why is None and (e["estimate"], e["ci_low"], e["ci_high"], e["scale"]) == (-3.72, -8.45, 1.01, "MD")
    assert e["readings"] == {"codex": "mc-a", "agy": "mc-b"} and e["state"] == "RECORDED"


def _bad(edit):
    g = copy.deepcopy(GOOD)
    edit(g["results"]["t"])
    return cfr.figure_result("t", g, "9")[1]


def test_refuses_every_weaker_case():
    assert cfr.figure_result("t", GOOD, "8")[1].startswith("NO_READ_OF_THIS_COMPARATOR")      # a retired comparator
    assert _bad(lambda r: r.update(state="REFUSED")).startswith("FIGURE_NOT_ACCEPTED")
    assert _bad(lambda r: r["acceptance"].update(methods_reproducing=[])) == "POOL_NOT_REPRODUCED"
    assert _bad(lambda r: r["acceptance"].update(pooled_anchor="PRINTED_IN_META_TEXT: ...")).startswith("POOL_PRINTED")
    assert _bad(lambda r: r["readings"].pop("agy")) == "NOT_TWO_RECORDED_READINGS"
    assert _bad(lambda r: r["pooled_agreed"].update(lower="2")) == "POOLED_ROW_ORDER"
