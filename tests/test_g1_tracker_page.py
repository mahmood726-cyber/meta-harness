"""G1 scoreboard (scripts/render_g1_tracker.py): the counting rule, the independent recomputation of the four G1
criteria, and the page's currency.

Rule (2026-10-02): verified = PRIMARY, or TWO_SOURCE with a recorded independent pair that holds no comparator id;
nothing sourced only from the comparator counts. A topic is MATCHED on the page only when the lane's status AND the
recomputation agree. Each plant would pass a renderer that copied the lane's status instead of recomputing it.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("render_g1_tracker", ROOT / "scripts" / "render_g1_tracker.py")
g1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g1)

COMP = "34526024"


def _rec(trials, lane="G1_MATCHED", n_el=None, k=None, verdict="AGREE", named=()):
    n = len(trials)
    return {"schema_version": 1, "slug": "glp1-ra-mace-t2d", "comparator_pmid": COMP, "N_comparator_trials": n,
            "N_eligible": n if n_el is None else n_el, "k_matched": n if k is None else k, "trials": trials,
            "same_trials": {"state": "POOLED", "k": n, "measure": "HR",
                            "ours": {"estimate": 0.85, "ci_low": 0.8, "ci_high": 0.9},
                            "theirs": {"estimate": 0.85, "ci_low": 0.8, "ci_high": 0.9},
                            "verdict": {"verdict": verdict}},
            "named_differences": [{"trial": t, "kind": "X"} for t in named], "comparator_findings": [],
            "g1_status": {"state": lane}}


def _t(label, route="PRIMARY", pooled=True, agree="AGREE", **kw):
    return dict({"label": label, "route": route, "in_our_pool": pooled, "agreement_with_comparator_row": agree}, **kw)


def test_a_fully_verified_agreeing_named_topic_is_matched():
    assert g1.recompute(_rec([_t("A"), _t("B")]))["matched"]


def test_PLANT_a_two_source_pair_containing_the_comparator_does_not_verify():
    r = g1.recompute(_rec([_t("A", "TWO_SOURCE", independent_pair_ids=["PMID 34526024", "1"])]))
    assert not r["criteria"]["MATCHED_ARE_VERIFIED"] and "anti-circularity" in r["rows"][0]["why"]


def test_PLANT_a_two_source_row_with_an_unknown_pair_does_not_verify():
    r = g1.recompute(_rec([_t("A", "TWO_SOURCE")]))
    assert not r["criteria"]["MATCHED_ARE_VERIFIED"] and "fail-closed" in r["rows"][0]["why"]


def test_PLANT_an_unnamed_divergence_fails_divergences_named():
    outside = _t("ELIXA", "UNVERIFIED", pooled=False, agree="NOT_IN_OUR_POOL")
    r = g1.recompute(_rec([_t("A"), outside]))
    assert not r["criteria"]["DIVERGENCES_NAMED"] and r["unnamed"] == ["ELIXA"]
    assert g1.recompute(_rec([_t("A"), outside], named=["ELIXA"]))["criteria"]["DIVERGENCES_NAMED"]


def test_unmatched_eligible_and_disagreeing_result_fail_their_criteria():
    assert not g1.recompute(_rec([_t("A")], n_el=2, k=1))["criteria"]["ALL_ELIGIBLE_MATCHED"]
    assert not g1.recompute(_rec([_t("A")], verdict="DIFFERENT_CONCLUSION"))["criteria"]["RESULT_AGREES"]


def test_PLANT_a_lane_matched_status_the_recomputation_refutes_is_not_counted(tmp_path):
    (tmp_path / g1.SRC).mkdir(parents=True)
    rec = _rec([_t("A", "TWO_SOURCE")])  # the lane says G1_MATCHED; the pair is unknown, so it is not verified
    (tmp_path / g1.SRC / "glp1-ra-mace-t2d.json").write_text(json.dumps(rec), encoding="utf-8")
    page = g1.render(tmp_path)
    assert "G1 MATCHED: 0 of 1 topics" in page and "lane status disagrees" in page


def test_the_committed_page_is_current():
    assert (ROOT / g1.OUT).read_bytes() == g1.render().encode("utf-8")


def test_committed_snapshot_matches_its_declared_tracker_blob():
    src = json.loads((ROOT / g1.SOURCE).read_text(encoding="utf-8"))
    data = (ROOT / "outputs" / "k_gap" / "G1_TRACKER.md").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest() == src["tracker_blob"]
