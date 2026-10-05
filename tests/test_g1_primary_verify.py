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
