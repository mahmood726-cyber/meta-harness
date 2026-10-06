"""RESULT_AGREES as a class (5 Oct): the same-trials comparison runs ON THE COMPARATOR'S MEASURE.
  - our trial row is expressed in the comparator's measure only from verified ARM COUNTS (RR / OR); an HR is never
    converted -- that pair is a typed MEASURE_DIFFERENCE, which passes only on the same conclusion about the null;
  - k = 1: one shared trial is compared directly;
  - whole pools: when the comparator's own text states how many trials it pooled and that k is our matched set
    (doac-vte: '6 phase 3 trials'), our pool vs its printed pool -- on a measure difference, named, same-conclusion."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import secondary_meta as sm  # noqa: E402
import g1_tracker as gt  # noqa: E402


def R(label, measure, effect=None, lower=None, upper=None, counts=None, who="C"):
    a = counts or (None, None, None, None)
    return sm.SecondaryRow(meta_pmid=who, meta_doi="", location={}, source_digest="", provenance="", trial_label=label,
                           measure=measure, outcome_definition="", effect=effect, lower=lower, upper=upper,
                           events_t=a[0], n_t=a[1], events_c=a[2], n_c=a[3])


def test_our_counts_go_to_the_comparators_measure_an_hr_never_does():
    ours = R("K", "RR", counts=(1, 171, 7, 149), who="OURS")
    row, why = gt.on_comparator_measure(ours, R("K", "OR", "0.12", "0.02", "1.0"))
    assert row is not None and row.measure == "OR" and why is None
    row, why = gt.on_comparator_measure(R("W", "HR", "0.73", "0.61", "0.88", who="OURS"), R("W", "RR", "0.74", "0.62", "0.88"))
    assert row is None and why == "MEASURE_DIFFERENCE:HR_VS_RR"


def test_one_shared_trial_is_compared_directly():
    st = gt.same_trials_compare([(R("E", "HR", "0.76", "0.62", "0.93", who="OURS"), R("E", "HR", "0.76", "0.62", "0.93"))], "FE")
    assert st["state"] == "ONE_SHARED_TRIAL" and st["verdict"]["verdict"] == "AGREE"


def test_hr_only_pairs_against_an_rr_comparator_are_a_named_measure_difference_on_the_same_conclusion():
    pairs = [(R("Radholm", "HR", "0.67", "0.52", "0.87", who="OURS"), R("Radholm", "RR", "0.56", "0.42", "0.73")),
             (R("Cannon", "HR", "0.70", "0.54", "0.90", who="OURS"), R("Cannon", "RR", "0.70", "0.54", "0.90"))]
    st = gt.same_trials_compare(pairs, "PM")
    assert st["state"] == "MEASURE_DIFFERENCE" and st["verdict"]["verdict"] == "MEASURE_DIFFERENCE_SAME_CONCLUSION"
    assert all(d["why"] == "MEASURE_DIFFERENCE:HR_VS_RR" for d in st["measure_differences"])
    # a pair whose conclusions about the null differ is never passed as a measure difference
    bad = pairs + [(R("X", "HR", "0.80", "0.70", "0.95", who="OURS"), R("X", "RR", "1.05", "0.90", "1.20"))]
    assert gt.same_trials_compare(bad, "PM")["verdict"]["verdict"] == "DIFFERENT_CONCLUSION"


def test_mixed_comparable_and_measure_difference_pairs():
    pairs = [(R("K", "RR", counts=(1, 171, 7, 149), who="OURS"), R("K", "RR", "0.12", "0.02", "1.00", counts=(1, 171, 7, 149))),
             (R("W", "HR", "0.73", "0.61", "0.88", who="OURS"), R("W", "RR", "0.74", "0.62", "0.88"))]
    st = gt.same_trials_compare(pairs, "PM")
    # the mixed case is typed: one comparable pair, the HR-vs-RR pair a named measure difference. The verdict follows
    # D2-ONE-TRIAL-SHARE (registry/g1_decisions.json): W carries no participant count, so the share cannot be shown and
    # one small comparable trial (K, 320 people) does not carry the topic (fail-closed). Before D2 this asserted AGREE.
    assert st["state"] == "ONE_COMPARABLE_TRIAL" and len(st["measure_differences"]) == 1
    assert st["verdict"]["verdict"] == "ONE_TRIAL_MINORITY_SHARE" and not st["participant_share"]["passes"]


def test_printed_k_and_the_whole_pool_measure_difference():
    assert gt.printed_trial_count("In the last 4 years, 6 phase 3 trials including a total of 27,023 patients ...") == 6
    # the real doac-vte abstract also says 'the phase 3 trials that compared ...': a PHASE number is never a count
    assert gt.printed_trial_count("In the last 4 years, 6 phase 3 trials including a total of 27,023 patients with VTE "
                                  "... We included the phase 3 trials that compared dabigatran ...") == 6
    assert gt.printed_trial_count("Four randomized controlled trials (DAPA HF, ...) were included") == 4
    assert gt.printed_trial_count("We screened 1,203 studies and included 12 trials") is None    # two counts: no pick
    o = {"k_matched": 6, "N_comparator_trials": 7, "named_differences": [{"trial": "x"}], "ours_not_in_comparator": [],
         "same_trials": {"state": "FEWER_THAN_2_SHARED_TRIALS"},
         "ours": {"k": 6, "estimate": 0.9091, "ci_low": 0.7479, "ci_high": 1.105, "scale": "HR"},
         "comparator": {"estimate": 0.9, "ci_low": 0.77, "ci_high": 1.06, "scale": "RR"}}
    wp = gt.whole_pool_comparison(o, printed_k=6)
    assert wp["state"] == "MEASURE_DIFFERENCE" and wp["verdict"]["verdict"] == "MEASURE_DIFFERENCE_SAME_CONCLUSION"
    assert gt.whole_pool_comparison(o, printed_k=7) is None                 # the comparator pooled another set
    assert gt.whole_pool_comparison(o) is None                              # no printed k: unchanged behaviour


def test_result_agrees_never_accepts_a_measure_difference_strict_needs_agree():
    # restated 6 Oct to the dispatcher's decision 1 (made under Mahmood's delegation, "fully matched k and data wise"):
    # a same-conclusion MEASURE_DIFFERENCE is reported beside the status but never passes strict RESULT_AGREES -- the
    # page's own recount already required AGREE; the lane status now does too
    base = {"trials": [], "named_differences": [], "N_comparator_trials": 1, "N_eligible": 1, "k_matched": 1, "open_gaps": []}
    same = dict(base, same_trials={"state": "MEASURE_DIFFERENCE", "verdict": {"verdict": "MEASURE_DIFFERENCE_SAME_CONCLUSION"}})
    diff = dict(base, same_trials={"state": "MEASURE_DIFFERENCE", "verdict": {"verdict": "DIFFERENT_CONCLUSION"}})
    agree = dict(base, same_trials={"state": "POOLED", "verdict": {"verdict": "AGREE"}})
    assert gt.g1_status(same)["criteria"]["RESULT_AGREES"] is False
    assert gt.g1_status(diff)["criteria"]["RESULT_AGREES"] is False
    assert gt.g1_status(agree)["criteria"]["RESULT_AGREES"] is True


def test_our_arm_means_reach_the_same_trials_comparison_as_a_mean_difference():
    # esketamine 5 Oct: our pool holds TRANSFORM-1/-2/-3 as arm means/SDs/Ns; the value object dropped them, so the
    # comparator's per-trial MDs were never compared
    v = gt.our_value_from_row({"id": "PMID 31109201", "mean1": -21.4, "sd1": 12.32, "nc1": 101,
                               "mean2": -17.0, "sd2": 13.88, "nc2": 100})
    assert v["measure"] == "MD" and v["n_t"] == 101
    row = gt.as_row(v, "Trial A")
    assert sm.row_yi_vi(row) is not None and abs(sm.row_yi_vi(row)[0] - (-4.4)) < 1e-9
    pairs = [(row, R("Trial A", "MD", "-4.20", "-6.53", "-1.87")),
             (gt.as_row(gt.our_value_from_row({"id": "x", "mean1": -10.0, "sd1": 12.74, "nc1": 63, "mean2": -6.3,
                                                 "sd2": 8.86, "nc2": 60}), "Trial C"), R("Trial C", "MD", "-2.00", "-4.92", "0.92"))]
    st = gt.same_trials_compare(pairs, "DL")
    assert st["state"] == "POOLED" and st["measure"] == "MD"
