"""K MATCHED headline (Mahmood 5 Oct, 'not inferior k-wise'): every eligible comparator trial has a typed row from any
admitted source, comparator-sourced rows included and labelled. It sits BESIDE G1 MATCHED (strict, first line) and never
replaces or feeds it. Plants: a comparator-sourced-only topic is K MATCHED but never G1 MATCHED; one uncovered eligible
trial breaks K MATCHED; a topic with no eligible trial is not K MATCHED."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import render_g1_tracker as rg  # noqa: E402

COMP = "999"


def _t(label, route="UNVERIFIED", covered_by_comparator=False, scope=None):
    t = {"label": label, "route": route, "in_our_pool": route == "PRIMARY", "scope_difference": scope}
    if covered_by_comparator:
        t["coverage"] = "COMPARATOR_SOURCED"
        t["comparator_sourced"] = {"provenance": {"meta_pmid": COMP, "location": {"kind": "figure", "id": "F2"},
                                                  "digest": "d" * 64, "read": "mc-1"}}
    return t


def _rec(trials):
    return {"slug": "x", "comparator_pmid": COMP, "N_comparator_trials": len(trials),
            "N_eligible": sum(1 for t in trials if not t.get("scope_difference")), "k_matched": 0,
            "g1_status": {"state": "NOT_YET"}, "trials": trials, "same_trials": {}}


def test_PLANT_comparator_sourced_rows_make_k_matched_never_g1():
    rec = _rec([_t("A", "PRIMARY"), _t("B", covered_by_comparator=True)])
    k = rg.k_matched(rec)
    assert k["matched"] and k["comparator_sourced"] == 1
    assert not rg.recompute(rec)["matched"]                     # strict G1 untouched


def test_PLANT_one_uncovered_eligible_trial_breaks_k_matched():
    rec = _rec([_t("A", "PRIMARY"), _t("B")])
    assert not rg.k_matched(rec)["matched"] and rg.k_matched(rec)["uncovered"] == ["B"]
    named = _rec([_t("A", "PRIMARY"), _t("B", scope={"kind": "PROTOCOL_SCOPE_DIFFERENCE"})])
    assert rg.k_matched(named)["matched"] and rg.k_matched(named)["eligible"] == 1


def test_no_eligible_trial_is_not_k_matched():
    assert rg.k_matched(_rec([_t("A", scope={"kind": "X"})])) is None


def test_the_page_shows_k_matched_second_beside_the_strict_count():
    page = open(os.path.join(ROOT, "docs", "g1", "index.html"), encoding="utf-8").read()
    i, j = page.index("G1 MATCHED:"), page.index("K MATCHED:")
    assert i < j and "a k-wise count only, not G1 MATCHED" in page
    recs = rg.load()
    assert f"K MATCHED:</strong> {len(rg.k_matched_topics(recs))} of {len(recs)} topics" in page
