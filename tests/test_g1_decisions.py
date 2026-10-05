"""Typed G1 decisions (registry/g1_decisions.json), each planted: the test fails without the decision's code.

D1-SWEEP-AACT-PRIMARY  posted AACT results with a recorded registry binding count as PRIMARY on the page (fail-closed)
D2-ONE-TRIAL-SHARE     one comparable trial carries RESULT_AGREES only with >= 50% of the shared participants
D3-COMPARATOR-POOLS-NO-RCT  statins-elderly: not attainable against a comparator that pools no RCTs (span verbatim)"""
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402
import render_g1_tracker as rg  # noqa: E402
from harness import secondary_meta as sm  # noqa: E402

DIGEST = "0c1ca79b89dc92018d4ae698ae5694b1b844f9fb8ec4f1b7b2171ea461b18e1a"


def _deliver():
    return {"label": "DELIVER", "route": "SWEEP_AACT_PRIMARY", "in_our_pool": False,
            "sweep": {"value": {"measure": "HR", "effect": "0.82", "lower": "0.73", "upper": "0.92",
                                "events_t": 512, "n_t": 3131, "events_c": 610, "n_c": 3132},
                      "basis": {"nct": "NCT03619213", "outcome": "Subjects Included in the Composite Endpoint of CV Death",
                                "snapshot": {"id": "AACT 2026-08-30", "digest": DIGEST},
                                "guard": "POSTED_N_EQUALS_RANDOMISED_N (6263); NCT03619213"}}}


def test_D1_posted_results_with_a_recorded_binding_count_as_primary():
    ok, why = rg.counts(_deliver(), set())
    assert ok and "D1-SWEEP-AACT-PRIMARY" in why


def test_D1_PLANT_an_incomplete_binding_is_not_counted():
    for mutate in (lambda t: t["sweep"]["basis"].pop("nct"),
                   lambda t: t["sweep"]["basis"]["snapshot"].update(digest="abc"),
                   lambda t: t["sweep"]["basis"].update(guard="none"),
                   lambda t: t["sweep"]["basis"].update(outcome=""),
                   lambda t: t["sweep"].update(value={"measure": "HR", "effect": "0.82"})):
        t = _deliver()
        mutate(t)
        ok, why = rg.counts(t, set())
        assert not ok and "fail-closed" in why, why


def _row(label, measure, **kw):
    return sm.SecondaryRow(meta_pmid="1", meta_doi="", location={}, source_digest="", provenance="TEST",
                           trial_label=label, measure=measure, outcome_definition="", **kw)


def _comparable(label, et, nt, ec, nc):
    return (_row(label, "RR", events_t=et, n_t=nt, events_c=ec, n_c=nc),
            _row(label, "RR", events_t=et, n_t=nt, events_c=ec, n_c=nc))


def _md(label, hr, lo, hi, rr, rlo, rhi, nt, nc):
    return (_row(label, "HR", effect=hr, lower=lo, upper=hi, n_t=nt, n_c=nc),
            _row(label, "RR", effect=rr, lower=rlo, upper=rhi, n_t=nt, n_c=nc))


def test_D2_PLANT_one_small_trial_cannot_carry_the_topic():
    # sglt2-primary-prevention: Kosiborod (8 events, 320 people) agrees; four large trials are HR-vs-RR differences
    pairs = [_comparable("Kosiborod", 1, 171, 7, 149),
             _md("Zinman", 0.65, 0.50, 0.85, 0.66, 0.51, 0.85, 4687, 2333),
             _md("Radholm", 0.67, 0.52, 0.87, 0.56, 0.42, 0.73, 5795, 4347),
             _md("Cannon", 0.70, 0.54, 0.90, 0.70, 0.54, 0.90, 5499, 2747),
             _md("Wiviott", 0.73, 0.61, 0.88, 0.74, 0.62, 0.88, 8582, 8578)]
    out = gt.same_trials_compare(pairs, "PM")
    assert out["state"] == "ONE_COMPARABLE_TRIAL"
    assert out["verdict"]["verdict"] == "ONE_TRIAL_MINORITY_SHARE"
    assert out["participant_share"]["share"] < 0.5 and not out["participant_share"]["passes"]


def test_D2_a_majority_comparable_trial_still_agrees():
    # spironolactone shape: the comparable trial is the larger share; the other pair a same-conclusion difference
    pairs = [_comparable("EMPHASIS-HF", 171, 1364, 213, 1373),
             _md("RALES", 0.70, 0.60, 0.82, 0.71, 0.61, 0.83, 822, 841)]
    out = gt.same_trials_compare(pairs, "PM")
    assert out["state"] == "ONE_COMPARABLE_TRIAL" and out["verdict"]["verdict"] == "AGREE"
    assert out["participant_share"]["passes"] and out["participant_share"]["share"] > 0.5


def test_D2_PLANT_a_missing_participant_count_fails_closed():
    o, t = _md("X", 0.70, 0.60, 0.82, 0.71, 0.61, 0.83, None, None)
    pairs = [_comparable("A", 171, 1364, 213, 1373), (o, t)]
    out = gt.same_trials_compare(pairs, "PM")
    assert out["verdict"]["verdict"] == "ONE_TRIAL_MINORITY_SHARE" and "fail-closed" in out["participant_share"]["why"]


STATINS = "statins-primary-prevention-elderly"


def test_D3_statins_is_not_attainable_with_the_comparators_own_words():
    d = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", f"{STATINS}.json"), encoding="utf-8"))
    g = gt.g1_status(d)
    assert g["state"] == "COMPARATOR_POOLS_NO_RCT" and g["decision"] == "D3-COMPARATOR-POOLS-NO-RCT"
    assert "observational studies" in g["span"]["text"] and g["flag"].startswith("FOR MAHMOOD")


def test_D3_PLANT_a_span_not_in_its_source_decides_nothing(monkeypatch):
    real = gt.g1_decisions()
    bad = copy.deepcopy(real)
    for x in bad:
        if x["id"] == "D3-COMPARATOR-POOLS-NO-RCT":
            x["topics"][STATINS]["span"]["text"] = "Twelve eligible randomised trials were enrolled."
    monkeypatch.setattr(gt, "g1_decisions", lambda: bad)
    assert gt.comparator_pools_no_rct(STATINS, "39076238") is None
    monkeypatch.setattr(gt, "g1_decisions", lambda: real)
    assert gt.comparator_pools_no_rct(STATINS, "39076238") and gt.comparator_pools_no_rct(STATINS, "1") is None


def test_every_decision_is_recorded_in_the_registry_and_typed():
    ids = [d["id"] for d in gt.g1_decisions()]
    assert ids == ["D1-SWEEP-AACT-PRIMARY", "D2-ONE-TRIAL-SHARE", "D3-COMPARATOR-POOLS-NO-RCT"]
    assert all(d.get("rule") and d.get("decided") and d.get("by") and d.get("applied_in") for d in gt.g1_decisions())


def test_D2_a_trials_stated_randomised_n_is_read_from_its_own_held_abstract():
    S = "spironolactone-hfref-mortality"
    assert gt.stated_randomised_n(S, "21073363") == (2737, {"field": "abstract", "pmid": "21073363",
                                                             "text": "we randomly assigned 2737 patients"})
    assert gt.stated_randomised_n(S, "10471456")[0] == 1663


def test_D2_PLANT_future_negated_or_ambiguous_n_is_never_read(monkeypatch):
    for ab in ("In total, 1060 patients will be randomized within 7 days.",          # future (protocol)
               "Patients were not randomized 400 patients in the registry arm.",     # negated
               "We randomly assigned 500 patients; we enrolled 620 patients.",       # two Ns: no pick
               "We randomly assigned eligible adults to drug or placebo."):         # no N
        monkeypatch.setattr(gt, "held_record", lambda slug, pmid, ab=ab: {"abstract": ab})
        assert gt.stated_randomised_n("x", "1") == (None, None), ab


def test_D2_the_share_uses_the_stated_n_when_rows_carry_no_counts():
    # spironolactone: both rows are HRs without arm counts; the trials' own abstracts state 2737 and 1663
    e = (_row("EMPHASIS-HF", "HR", effect=0.76, lower=0.62, upper=0.93), _row("EMPHASIS-HF", "HR", effect=0.76, lower=0.62, upper=0.93))
    r = (_row("RALES", "HR", effect=0.70, lower=0.60, upper=0.82), _row("RALES", "RR", effect=0.71, lower=0.61, upper=0.83))
    stated = {"EMPHASIS-HF": 2737, "RALES": 1663}
    out = gt.same_trials_compare([e, r], "PM", participants_of=lambda o, t: (stated[o.trial_label], "stated"))
    assert out["state"] == "ONE_COMPARABLE_TRIAL" and out["verdict"]["verdict"] == "AGREE"
    assert round(out["participant_share"]["share"], 3) == round(2737 / 4400, 3)
    assert gt.same_trials_compare([e, r], "PM")["verdict"]["verdict"] == "ONE_TRIAL_MINORITY_SHARE"   # no N: fail-closed
