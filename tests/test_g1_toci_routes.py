"""G1 tocilizumab routes after the 2 Oct (one bound primary that STATES the counts verifies a row) and 3 Oct
(SECONDARY_SINGLE: a non-comparator meta row) decisions, and the shared-registration binding defect (Q16). Each guard is
shown to fire with it removed (or on a constructed input) and not as built."""
import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from g1 import tocilizumab as g  # noqa: E402
import g1_toci_tracker as tr  # noqa: E402

T = {t["label"]: t for t in g.run()["trials"]}


def _m2(meta, label, a, n1, b, n2):
    return {"meta_pmid": meta, "label": label, "binding": "BOUND", "cited_pmid": "1",
            "events_t": a, "total_t": n1, "events_c": b, "total_c": n2}


def test_q16_a_shared_registration_never_binds_a_paper_to_both_populations():
    built = [r for r, _ in g.held_texts("CORIMUNO-TOCI-ICU")]
    assert "PMID 33080017" not in built                                # the TOCI-1 paper ('Moderate or Severe Pneumonia')
    assert not g.meta2_rows().get("CORIMUNO-TOCI-ICU")                 # so no Hermine row reaches the ICU trial
    with patch.object(g, "_SHARED_REG_GUARD", False), patch.object(g, "_HELD", None):
        assert "PMID 33080017" in [r for r, _ in g.held_texts("CORIMUNO-TOCI-ICU")]      # fires with the guard removed
    assert "PMID 33080017" in [r for r, _ in g.held_texts("CORIMUNO-TOCI-1")]            # control: still TOCI-1's


def test_one_bound_primary_that_states_the_counts_is_primary_a_converted_percentage_is_not():
    rec = T["RECOVERY"]
    best = next(x for x in rec["readings"] if x["values"] == {k: rec["row"][k] for k in g._KEY})
    assert rec["state"] == g.ONE_SOURCE and tr._route(rec, best) == "PRIMARY"
    rem = T["REMDACTA"]                                                # AACT percentage converted to counts
    bestr = next(x for x in rem["readings"] if x["values"] == {k: rem["row"][k] for k in g._KEY})
    assert rem["state"] == g.ONE_SOURCE and not bestr.get("counts_stated_by") and tr._route(rem, bestr) == "UNVERIFIED"


def test_secondary_single_is_admitted_only_when_typed_day_28_by_the_trials_own_primary():
    for lab in ("EMPACTA", "CORIMUNO-TOCI-1"):
        ss, why = tr.secondary_single(T[lab])
        assert ss and why is None and ss["row"] == {k: T[lab]["react_row"][k] for k in g._KEY}
    ss, why = tr.secondary_single(T["COVINTOC"])                       # meta window 14-28 days, nothing types the row
    assert ss is None and why.startswith("TIMEPOINT_NOT_TYPED")


def test_secondary_single_refuses_contradicting_metas_and_another_timepoints_count():
    ss, why = tr.secondary_single(T["REMAP-CAP"])
    assert ss is None and "CONTRADICTED" in why and "IN-HOSPITAL" in why
    t = dict(T["EMPACTA"], meta2_rows=[_m2("A", "Salama", 26, 249, 11, 128), _m2("B", "Salama", 26, 249, 12, 128)])
    assert tr.secondary_single(t)[1].startswith("CONTRADICTED")       # constructed: two metas, one count apart


def test_secondary_single_refuses_a_row_that_does_not_reproduce_every_posted_day_28_percentage():
    ss, why = tr.secondary_single(T["BACC-Bay"])                      # placebo 3/81 = 3.7% vs posted 3.8% (KM estimate)
    assert ss is None and "posted 3.8% of 81" in why
    t = dict(T["BACC-Bay"], meta2_rows=[_m2("A", "Stone", 9, 161, 3, 80)])          # constructed control: 3/80 = 3.75%
    with patch.object(tr, "aact_day28_percentages", return_value=[("t", 5.6, 161, "Tocilizumab"), ("c", 3.8, 80, "Placebo")]):
        assert tr.secondary_single(t)[0]


def test_secondary_single_never_reads_a_meta_that_cites_the_comparator():
    m = {"35657993": {"state": "PASS", "independence": {"state": "CITES_COMPARATOR:34228774"}, "admitted_rows": []},
         "36102463": {"state": "PASS", "independence": {"state": "CITES_COMPARATOR:34228774"}, "admitted_rows": []}}
    with patch.object(g.json, "load", side_effect=lambda fh, *a, **k: m if "meta2_forest" in getattr(fh, "name", "")
                      else __import__("json").loads(fh.read())):
        assert g.meta2_rows() == {}


def test_tracker_counts_matched_by_route_and_names_every_gap():
    d = tr.build()
    assert d["k_matched"] == sum(1 for t in d["trials"] if t["route"] in tr.COUNTABLE)
    assert set(d["open_gaps"]) == {t["label"] for t in d["trials"] if t["route"] not in tr.COUNTABLE}
    assert all(t["secondary_single"]["state"] != "REFUSED" or t["secondary_single"]["why"] for t in d["trials"])
