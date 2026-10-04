"""RESULT_AGREES is never a bare NOT_YET: g1_status names WHY it is unmet (g1_tracker.result_blocker); a comparator whose
own abstract STATES its pooled trial count that equals our matched set compares whole pools even with named non-trial
differences (doac-vte: '6 phase 3 trials'); and a stated count above the enumerated N is a typed finding (dpp4: a trial missing from ours; iv-iron: the comparator's own count is wrong)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402


def _o(**kw):
    base = {"trials": [], "named_differences": [], "N_comparator_trials": 6, "N_eligible": 6, "k_matched": 6,
            "open_gaps": [], "comparator_pmid": "0", "same_trials": {"state": "FEWER_THAN_2_SHARED_TRIALS", "k": 0},
            "ours": {"k": 6, "estimate": 0.909, "ci_low": 0.748, "ci_high": 1.105, "scale": "HR"},
            "comparator": {"estimate": 0.90, "ci_low": 0.77, "ci_high": 1.06, "scale": "RR"}}
    base.update(kw)
    return base


def test_the_stated_count_is_read_from_the_comparators_own_abstract():
    k, span = gt.comparator_stated_k("24963045")                     # doac-vte comparator
    assert k == 6 and span["text"] == "6 phase 3 trials"
    assert gt.comparator_stated_k("no-such-comparator") == (None, None)


def test_whole_pools_compare_when_the_stated_count_equals_our_matched_set():
    o = _o(N_comparator_trials=7, named_differences=[{"trial": "a pooled bleeding analysis"}], comparator_pmid="24963045")
    wp = gt.whole_pool_comparison(o)
    # our HR vs their RR is a NAMED measure difference (acq/k-gap class): never converted, it passes only on the same
    # conclusion about the null -- both include 1 here
    assert wp["state"] == "MEASURE_DIFFERENCE" and wp["basis"].startswith("COMPARATOR_STATES_ITS_POOL_K")
    assert wp["verdict"]["verdict"] == "MEASURE_DIFFERENCE_SAME_CONCLUSION"
    # negative: the comparator excludes the null, ours does not -> a different conclusion, typed as the blocker
    diff = gt.whole_pool_comparison(dict(o, comparator={"estimate": 0.80, "ci_low": 0.70, "ci_high": 0.92, "scale": "RR"}))
    assert diff["verdict"]["verdict"] == "DIFFERENT_CONCLUSION"
    assert gt.result_blocker(dict(o, same_trials=diff))["code"] == "MEASURE_DIFFERS_DIFFERENT_CONCLUSION"
    # controls: an open gap, or a stated count that differs from ours, never compares whole pools
    assert gt.whole_pool_comparison(dict(o, open_gaps=["X"])) is None
    assert gt.whole_pool_comparison(dict(o, k_matched=5, N_eligible=5)) is None
    # same measure -> a real verdict
    same = dict(o, comparator={"estimate": 0.90, "ci_low": 0.77, "ci_high": 1.06, "scale": "HR"})
    assert gt.whole_pool_comparison(same)["verdict"]["verdict"] == "AGREE"


def test_every_unmet_result_names_its_blocker():
    rb = gt.result_blocker(_o(comparator={"estimate": None}))
    assert rb["code"] == "COMPARATOR_PRINTS_NO_RESULT_FOR_OUTCOME"
    assert gt.result_blocker(_o(same_trials={"state": "MIXED_MEASURES", "measures": ["HR", "RR"], "k": 4}))["code"] == \
        "MEASURE_DIFFERS_PER_TRIAL"
    assert gt.result_blocker(_o(same_trials={"state": "WHOLE_POOL_MEASURE_DIFFERS", "ours": "HR", "theirs": "RR"}))["code"] == \
        "MEASURE_DIFFERS_WHOLE_POOL"
    tr = [{"label": "Imazio [18]", "route": "PRIMARY", "in_our_pool": True, "g1_countable": True,
           "disagreement_side": "SECONDARY_WRONG (primary numbers are in the primary's own span)",
           "agreement_with_comparator_row": "DISAGREE:x"}]
    rb = gt.result_blocker(_o(trials=tr, same_trials={"state": "POOLED", "verdict": {"verdict": "DIFFERENT_CONCLUSION"}}))
    assert rb["code"] == "RESULT_DIFFERS:DIFFERENT_CONCLUSION" and rb["comparator_rows_contradicted_by_primary"] == ["Imazio [18]"]
