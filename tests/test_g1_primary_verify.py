"""Plants for g1_primary_verify's report choice (5 Oct): a PMID listed for trials of DIFFERENT registrations is a pooled
or shared report, never one trial's own; several candidate reports settle only when every verified one agrees."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_primary_verify as pv  # noqa: E402


def test_shared_pmid_across_registrations_is_not_a_trials_own_report():
    ts = [{"label": "A", "ncts": ["NCT1"], "pmids": ["own_a", "pooled"]},
          {"label": "B", "ncts": ["NCT2"], "pmids": ["own_b", "pooled"]},
          {"label": "C", "ncts": ["NCT3"], "pmids": ["pooled"]}]
    own = pv.own_pmids(ts)
    assert own == [["own_a"], ["own_b"], []]


def test_same_registration_sharing_is_kept_for_the_claimed_by_two_refusal():
    ts = [{"label": "X-1", "ncts": ["NCT9"], "pmids": ["r"]}, {"label": "X-ICU", "ncts": ["NCT9"], "pmids": ["r"]}]
    assert pv.own_pmids(ts) == [["r"], ["r"]]


def _v(et, nt, ec, nc):
    return {"state": "PRIMARY_VERIFIED", "value": {"events_t": et, "n_t": nt, "events_c": ec, "n_c": nc}}


def test_candidates_settle_only_when_every_verified_report_agrees():
    agree = pv.settle([_v(1, 10, 2, 10), {"state": "NO_PRIMARY_VALUE:LOCATOR_NOT_REPORTED"}, _v(1, 10, 2, 10)])
    assert agree["state"] == "PRIMARY_VERIFIED" and agree["settled_by"] == "VERIFIED_REPORTS_AGREE_2"
    dis = pv.settle([_v(1, 10, 2, 10), _v(3, 10, 2, 10)])
    assert dis["state"] == "REPORTS_DISAGREE"
    none = pv.settle([{"state": "TIMEPOINT_NOT_IN_SPAN"}, {"state": "NO_PRIMARY_VALUE:X"}])
    assert none["state"].startswith("NO_REPORT_VERIFIED")


def test_a_value_without_both_arms_counts_is_not_primary_verified_for_a_counts_topic():
    assert pv.counts_state({"effect": "0.3", "measure": "WEIGHTED DIFFERENCE"}) == "VERIFIED_NO_COUNTS"
    assert pv.counts_state({"events_t": 26, "n_t": 249, "events_c": 11, "n_c": None}) == "VERIFIED_NO_COUNTS"
    assert pv.counts_state({"events_t": 26, "n_t": 249, "events_c": 11, "n_c": 128}) == "PRIMARY_VERIFIED"


def test_acronym_route_only_when_pmids_and_nct_give_nothing_and_never_a_review(monkeypatch):
    hits = {"NCT": [], "ACR": [("111", "COVINTOC: tocilizumab in severe COVID-19, an open-label RCT"),
                                  ("222", "Tocilizumab in COVID-19: a systematic review and meta-analysis incl. COVINTOC")]}
    monkeypatch.setattr(pv, "nct_hits", lambda nct, run: hits["NCT"])
    monkeypatch.setattr(pv, "acronym_hits", lambda acr, run: hits["ACR"])
    t = {"label": "COVINTOC", "ncts": [], "pmids": [], "acronyms": ["COVINTOC"]}
    pm, basis = pv.choose_report("tocilizumab-covid19-mortality", t, True, {}, {})
    assert pm == "111" and basis == "EPMC_ACRONYM_TITLE_NAMES_INTERVENTION"
    t2 = {"label": "X", "ncts": [], "pmids": [], "acronyms": ["COVINTOC"]}
    hits["ACR"] = [("333", "COVINTOC results"), ("222", "Tocilizumab: a systematic review")]
    assert pv.choose_report("tocilizumab-covid19-mortality", t2, True, {}, {})[0] is None
