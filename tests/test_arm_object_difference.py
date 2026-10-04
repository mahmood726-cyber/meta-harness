"""A comparator trial whose own record states a different dose AND primary timepoint than the protocol's arm object is
a NAMED scope difference with rule + verbatim span: semaglutide-obesity-weight O'Neil 2018 (30122305), a phase-2
once-daily 0.05-0.4 mg dose-finding trial with its primary at week 52, against a protocol estimand of 2.4 mg weekly at
Week 68 +/- 8. Silence is never a difference; a record stating the required dose is never named."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402

CFG = json.load(open(os.path.join(ROOT, "topics", "semaglutide-obesity-weight.json"), encoding="utf-8"))


def _with_record(monkeypatch, rec):
    monkeypatch.setattr(gt, "held_record", lambda slug, pmid: rec)


def test_oneil_is_named_by_dose_and_timepoint():
    d = gt.arm_object_difference({"in_our_pool": False, "family": "PMID 30122305"}, CFG, "semaglutide-obesity-weight")
    assert d and d["rule_id"] == "ARM_OBJECT" and "2.4 mg" in d["protocol_rule"] and "Week 68" in d["protocol_rule"]
    assert "0·4 mg" in d["span"]["text"] and d["also"][0]["span"]["text"].endswith("at week 52.")
    assert gt.span_is_verbatim("semaglutide-obesity-weight", "30122305", d["span"])


def test_a_record_stating_the_required_dose_is_not_named(monkeypatch):
    _with_record(monkeypatch, {"title": "Once-weekly semaglutide in adults with obesity",
                               "abstract": "Participants received semaglutide 2.4 mg or 1.0 mg once weekly. "
                                           "The primary endpoint was change in body weight at week 68."})
    assert gt.arm_object_difference({"in_our_pool": False, "family": "PMID 1"}, CFG, "x") is None


def test_a_silent_record_is_not_named(monkeypatch):
    _with_record(monkeypatch, {"title": "Semaglutide and weight", "abstract": "We randomised adults to semaglutide or placebo."})
    assert gt.arm_object_difference({"in_our_pool": False, "family": "PMID 1"}, CFG, "x") is None


def test_a_pooled_trial_is_never_named():
    assert gt.arm_object_difference({"in_our_pool": True, "family": "PMID 30122305"}, CFG,
                                    "semaglutide-obesity-weight") is None


def test_an_x_dose_screen_out_is_named_from_the_record_not_the_audit():
    # main 3733b80a: O'Neil SCREENED_OUT by the arm-object stage's X-DOSE read SCREENED_OUT_UNAUDITED:X-DOSE
    x = {"in_our_pool": False, "family": "PMID 30122305", "label": "O'Neil, 2018",
         "seeded_funnel": {"stage": "SCREENED_OUT", "rule_id": "X-DOSE", "pmid": "30122305",
                           "reason": "X-DOSE: randomised semaglutide dose is 0.4 mg, but the protocol requires 2.4 mg."}}
    d = gt.scope_difference(x, CFG, "semaglutide-obesity-weight")
    assert d and d["rule_id"] == "X-DOSE" and d["kind"] == "PROTOCOL_SCOPE_DIFFERENCE" and d["span"]["text"]
