"""D12 COUNTS_FOR_MATCHING (Mahmood, 8 Oct 2026: "approve d12"). A trial's own typed per-arm counts may be used for the
G1 same-trial comparison on the comparator's measure; the served pool keeps its registered estimand; nothing served
changes. The plants: counts used for matching never enter a served pool, never overwrite our_value, and are used only
when they verify against their own source."""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_d12 as D  # noqa: E402
import g1_tracker as gt  # noqa: E402
from harness import secondary_meta as sm  # noqa: E402

# everything that builds, admits or serves a pooled number
SERVING = ["scripts/build_served_pool_additions.py", "scripts/g1_served_pool_notices.py", "scripts/build_topic_recorded.py",
           "scripts/build_topic.py", "scripts/countersign_result_change.py"]


def _serving_sources():
    for dp, _dn, fs in os.walk(os.path.join(ROOT, "harness")):
        for f in fs:
            if f.endswith(".py"):
                yield os.path.join(dp, f)
    for rel in SERVING:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            yield p


def test_PLANT_nothing_that_serves_a_pool_reads_d12_counts():
    bad = []
    for p in _serving_sources():
        src = open(p, encoding="utf-8", errors="replace").read()
        if "g1_d12" in src or "d12_counts_for_matching" in src:
            bad.append(os.path.relpath(p, ROOT))
    assert bad == [], bad


def test_PLANT_the_only_reader_of_d12_is_the_tracker_comparison():
    readers = []
    for f in os.listdir(os.path.join(ROOT, "scripts")):
        if f.endswith(".py") and f != "g1_d12.py":
            if "import g1_d12" in open(os.path.join(ROOT, "scripts", f), encoding="utf-8", errors="replace").read():
                readers.append(f)
    assert readers == ["g1_tracker.py"], readers


def _row(label, measure, **kw):
    return sm.SecondaryRow(meta_pmid="X", meta_doi="", location={}, source_digest="", provenance="P", trial_label=label,
                           measure=measure, outcome_definition="", **kw)


def test_PLANT_d12_replaces_only_the_comparison_pair_never_our_value():
    x = {"label": "T1", "our_value": {"measure": "HR", "effect": "0.80", "lower": "0.70", "upper": "0.90"}}
    before = json.dumps(x, sort_keys=True)
    ours = gt.as_row(x["our_value"], "T1", "OR")
    theirs = _row("T1", "OR", events_t=569, n_t=8803, events_c=701, n_c=8801)
    d12 = {"T1": {"row": {"events_t": 569, "n_t": 8803, "events_c": 701, "n_c": 8801}, "rule": "K1", "basis": "b",
                  "source": "s", "span": "sp"}}
    without = gt.same_trials_compare([(ours, theirs)], "FE")
    withd12 = gt.same_trials_compare([(ours, theirs)], "FE", d12=d12)
    assert without["state"] == "MEASURE_DIFFERENCE" and "d12_counts_for_matching" not in without
    assert withd12["state"] == "ONE_SHARED_TRIAL" and withd12["verdict"]["verdict"] == "AGREE"
    used = withd12["d12_counts_for_matching"][0]
    assert used["served_value_unchanged"] == {"measure": "HR", "effect": "0.80", "lower": "0.70", "upper": "0.90"}
    assert json.dumps(x, sort_keys=True) == before and ours.measure == "HR" and ours.events_t is None
    # never across a non-count comparator measure, and never without a binding
    hr_theirs = _row("T1", "HR", effect="0.8", lower="0.7", upper="0.9")
    assert "d12_counts_for_matching" not in gt.same_trials_compare([(ours, hr_theirs)], "FE", d12=d12)
    assert "d12_counts_for_matching" not in gt.same_trials_compare([(ours, theirs)], "FE", d12={"OTHER": d12["T1"]})


def _k2(**kw):
    b = {"slug": "s", "label": "T", "pmid": "1", "ncts": ["NCT00000001"], "own_tuple": True, "tuple_kind": "COUNTS",
         "rule": "K2", "values": {"events_t": 59, "n_t": 2609, "events_c": 71, "n_c": 2635},
         "second_reader": {"verdict": "CONFIRMED", "record_id": "mc-7948396356bf9b690759ec525d16a1c4"},
         "span": "occurred in 59 of 2609 patients (2.3%) in the apixaban group, as compared with 71 of 2635 (2.7%) in the "
                 "conventional-therapy group"}
    b.update(kw)
    return b


TERMS = (["apixaban", "rivaroxaban", "drug"], ["conventional therapy", "vitamin k antagonist", "placebo"])
HELD = ("RESULTS: The outcome occurred in 59 of 2609 patients (2.3%) in the apixaban group, as compared with 71 of 2635 "
        "(2.7%) in the conventional-therapy group.")


@pytest.fixture(autouse=True)
def _terms(monkeypatch):
    monkeypatch.setattr(D, "arm_terms", lambda slug: TERMS)
    monkeypatch.setattr(D, "_held_nct", lambda slug, pmid: "NCT00000001")


def test_PLANT_a_binding_is_used_only_when_it_verifies(monkeypatch):
    monkeypatch.setattr(D, "_held_abstract", lambda slug, pmid: HELD)
    assert D.verify(_k2())[0]
    assert D.verify(_k2(span="occurred in 59 of 2609 patients (2.3%) in the apixaban group, as compared with 71 of 2636"))[1] \
        == "K2_SPAN_NOT_VERBATIM_IN_HELD_ABSTRACT"
    assert D.verify(_k2(values={"events_t": 58, "n_t": 2609, "events_c": 71, "n_c": 2635}))[1] == \
        "K2_EVENT_COUNTS_NOT_WRITTEN_ONCE_AS_COUNTS_IN_SPAN"
    assert D.verify(_k2(values={"events_t": 59, "n_t": 2609, "events_c": 71, "n_c": 70}))[1] == "IMPOSSIBLE_COUNTS"
    assert D.verify(_k2(own_tuple=False))[1] == "NOT_AN_OWN_COUNTS_TUPLE"
    k1 = _k2(rule="K1", source="AACT AACT 2026-08-30 NCT00000001 outcome 42")
    assert D.verify(k1, aact=None)[1] == "K1_NOT_VERIFIABLE:NO_AACT_SNAPSHOT"
    assert D.verify(dict(k1, source="AACT AACT 2026-08-30 NCT09999999 outcome 42"))[1] == \
        "K1_SOURCE_NOT_AN_AACT_OUTCOME_OF_THIS_TRIAL"


def _snapshot(tmp_path, titles=("Drug", "Placebo")):
    (tmp_path / "outcome_counts.txt").write_text(
        "id|nct_id|outcome_id|result_group_id|ctgov_group_code|scope|units|count\n"
        "1|NCT00000001|42|g0|OG000|Measure|Participants|2609\n2|NCT00000001|42|g1|OG001|Measure|Participants|2635\n",
        encoding="utf-8")
    (tmp_path / "outcome_measurements.txt").write_text(
        "id|nct_id|outcome_id|result_group_id|ctgov_group_code|classification|category|title|units|param_type|param_value\n"
        "1|NCT00000001|42|g0|OG000||||Participants|COUNT_OF_PARTICIPANTS|59\n"
        "2|NCT00000001|42|g1|OG001||||Participants|COUNT_OF_PARTICIPANTS|71\n", encoding="utf-8")
    (tmp_path / "result_groups.txt").write_text(
        "id|nct_id|ctgov_group_code|result_type|title|description|outcome_id\n"
        f"g0|NCT00000001|OG000|Outcome|{titles[0]}||42\ng1|NCT00000001|OG001|Outcome|{titles[1]}||42\n", encoding="utf-8")
    a = D.Aact(str(tmp_path))
    a.load({"42"})
    return a


def test_PLANT_k1_verifies_against_the_aact_rows_and_their_group_titles(tmp_path):
    a = _snapshot(tmp_path)
    k1 = _k2(rule="K1", source="AACT AACT 2026-08-30 NCT00000001 outcome 42",
             span="X | unclassified | Drug: 59 of 2609 participants | Placebo: 71 of 2635 participants")
    assert D.verify(k1, a)[0]
    # the span states the arms the other way round from AACT -> never verifies
    swapped = dict(k1, span="X | unclassified | Placebo: 59 of 2609 participants | Drug: 71 of 2635 participants")
    assert D.verify(swapped, a)[1].startswith("K1_SPAN_DOES_NOT_STATE_AACT_GROUP")
    assert D.verify(dict(k1, values={"events_t": 60, "n_t": 2609, "events_c": 71, "n_c": 2635}), a)[1].startswith(
        "K1_AACT_ROWS_DIFFER")


def test_identity_not_label_joins_a_binding_to_a_trial(tmp_path, monkeypatch):
    monkeypatch.setattr(D, "_held_abstract", lambda slug, pmid: HELD)
    reg = {"bindings": [_k2(label="Some other label")]}
    trials = [{"label": "T 18", "in_our_pool": True, "family": "PMID 1"},
              {"label": "U", "in_our_pool": True, "family": "PMID 2"}]
    ok, refused = D.for_topic("s", trials, snap="", reg=reg)
    assert list(ok) == ["T 18"] and refused == []
    ok, refused = D.for_topic("s", [{"label": "T 18", "in_our_pool": False, "family": "PMID 1"}], snap="", reg=reg)
    assert ok == {} and refused[0]["why"] == "IDENTITY:0_MATCHED_TRIALS"


def test_d12_is_a_recorded_decision_with_mahmoods_words():
    d = next(x for x in gt.g1_decisions() if x["id"] == "D12-COUNTS_FOR_MATCHING")
    assert d["quote"] == "approve d12" and d["served_change"] == "none" and "served pool keeps" in d["rule"]


def test_the_committed_bindings_carry_their_import_provenance():
    r = D.load()
    assert r["decision"] == "D12-COUNTS_FOR_MATCHING" and len(r["imported_from"]["sha256"]) == 64
    assert all(b["own_tuple"] and b["tuple_kind"] == "COUNTS" for b in r["bindings"])


def test_a_missing_bindings_file_is_an_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        D.load(str(tmp_path / "none.json"))


def _held(monkeypatch, text):
    monkeypatch.setattr(D, "_held_abstract", lambda slug, pmid: text)
    return text


def test_PLANT_r1_1_a_percentage_is_never_a_count(monkeypatch):
    t = _held(monkeypatch, "Death occurred in 2% of 59 apixaban patients and 3% of 71 with conventional therapy.")
    b = _k2(span=t, values={"events_t": 2, "n_t": 59, "events_c": 3, "n_c": 71})
    assert D.verify(b)[1] == "K2_EVENT_COUNTS_NOT_WRITTEN_ONCE_AS_COUNTS_IN_SPAN"
    assert D.count_positions("2% of 59 and 59 of 2609 and 2.59 events", 59) == [13]


def test_PLANT_r1_2_counts_assigned_to_the_opposite_arms_never_verify(monkeypatch):
    t = _held(monkeypatch, "occurred in 71 of 2635 patients (2.7%) in the apixaban group, as compared with 59 of 2609 "
                           "(2.3%) in the conventional-therapy group")
    assert D.verify(_k2(span=t))[1] == "K2_COUNTS_NOT_IN_THE_ARMS_ORDER"


def test_PLANT_r1_3_a_count_must_be_tied_to_its_own_denominator(monkeypatch):
    # deaths in a safety population (59 of 2500, 2.4%) beside randomised Ns elsewhere in the text
    t = _held(monkeypatch, "Randomised: 2609 apixaban and 2635 conventional therapy. In the safety population, 59 deaths "
                           "(2.4%) with apixaban and 71 deaths (2.9%) with conventional therapy.")
    b = _k2(span=t, n_source="abstract")
    assert D.verify(b)[1] == "K2_COUNT_NOT_TIED_TO_ITS_DENOMINATOR"


def test_PLANT_r1_4_a_non_count_or_fractional_aact_value_is_never_an_event_count(tmp_path):
    a = _snapshot(tmp_path)
    a._meas = [dict(r, param_type="MEAN", units="kg") for r in a._meas]
    assert a.arms("NCT00000001", "42", None) == {}
    a2 = _snapshot(tmp_path)
    a2._meas = [dict(r, param_value="59.4" if r["param_value"] == "59" else r["param_value"]) for r in a2._meas]
    assert len(a2.arms("NCT00000001", "42", None)) == 1
    assert D._whole("30.0") == 30 and D._whole("30.5") is None and D._whole("x") is None


def test_PLANT_r1_5_k1_needs_the_trials_own_report_to_carry_the_nct(tmp_path, monkeypatch):
    a = _snapshot(tmp_path)
    k1 = _k2(rule="K1", source="AACT AACT 2026-08-30 NCT00000001 outcome 42",
             span="X | unclassified | Drug: 59 of 2609 participants | Placebo: 71 of 2635 participants")
    assert D.verify(k1, a)[0]
    monkeypatch.setattr(D, "_held_nct", lambda slug, pmid: "NCT00000002")
    assert D.verify(k1, a)[1] == "K1_HELD_REPORT_DOES_NOT_CARRY_THIS_NCT"


def test_PLANT_k2_needs_the_independent_second_readers_confirmation(monkeypatch):
    """codex d12-r2 (#2 #4 #6): syntax cannot certify endpoint, population or arm ownership; a K2 span is used only with the
    binding lane's recorded independent reader CONFIRMED, and that record held in evidence/model_calls/audit."""
    _held(monkeypatch, HELD)
    assert D.verify(_k2())[0]
    for sr in ({"verdict": "NOT_COMPARABLE", "record_id": "mc-7948396356bf9b690759ec525d16a1c4"},
               {"verdict": "CONFIRMED", "record_id": "mc-0000000000000000000000000000dead"}, {}):
        assert D.verify(_k2(second_reader=sr))[1].startswith(("K2_NO_INDEPENDENT_CONFIRMATION",
                                                              "K2_SECOND_READER_RECORD_DOES_NOT_STATE_THESE_COUNTS:None")), sr


def test_PLANT_r2_percentage_units_are_never_counts(tmp_path):
    a = _snapshot(tmp_path)
    a._meas = [dict(r, param_type="NUMBER", units="Percentage of participants") for r in a._meas]
    assert a.arms("NCT00000001", "42", None) == {}


def test_PLANT_r2_a_denominator_needs_a_numeric_boundary_and_printed_precision():
    assert D._tied("10 of 100 patients", 0, 10, 100)
    assert not D._tied("10 of 1000 patients", 0, 10, 100)
    # 10.0% printed with one decimal: 10/104 = 9.6% is not 10.0% (integer tolerance would have admitted it)
    assert not D._tied("10 events (10.0%)", 0, 10, 104)
    assert D._tied("10 events (10.0%)", 0, 10, 100) and D._tied("10 events (10%)", 0, 10, 104)


def test_PLANT_r2_k2_joins_by_its_pmid_only(monkeypatch):
    _held(monkeypatch, HELD)
    reg = {"bindings": [_k2()]}
    trials = [{"label": "Other report", "in_our_pool": True, "family": "NCT00000001"}]
    ok, refused = D.for_topic("s", trials, snap="", reg=reg)
    assert ok == {} and refused[0]["why"] == "IDENTITY:0_MATCHED_TRIALS"


def test_PLANT_r3_1_the_record_is_read_not_the_label(monkeypatch):
    _held(monkeypatch, HELD)
    assert D.reader_counts("mc-7948396356bf9b690759ec525d16a1c4") == (59, 2609, 71, 2635)   # AMPLIFY, as recorded
    monkeypatch.setattr(D, "reader_counts", lambda rid: (71, 2635, 59, 2609))            # the record says the reverse
    assert D.verify(_k2())[1].startswith("K2_SECOND_READER_RECORD_DOES_NOT_STATE_THESE_COUNTS")


def test_PLANT_r3_2_slash_rates_are_not_counts(tmp_path):
    a = _snapshot(tmp_path)
    a._meas = [dict(r, param_type="NUMBER", units="participants/100 patient-years") for r in a._meas]
    assert a.arms("NCT00000001", "42", None) == {}


def test_PLANT_r3_3_k1_joins_only_through_its_source_nct():
    k1 = _k2(rule="K1", source="AACT AACT 2026-08-30 NCT00000001 outcome 42", ncts=["NCT00000001", "NCT00000009"],
             pmid="77")
    trials = [{"label": "Another trial", "in_our_pool": True, "family": "NCT00000009"}]
    ok, refused = D.for_topic("s", trials, snap="", reg={"bindings": [k1]})
    assert ok == {} and refused[0]["why"] == "IDENTITY:0_MATCHED_TRIALS"


def test_PLANT_r3_4_equal_counts_in_both_arms_verify(monkeypatch):
    t = _held(monkeypatch, "occurred in 30 of 1274 patients (2.4%) in the apixaban group, as compared with 30 of 1265 "
                           "(2.4%) in the conventional-therapy group")
    monkeypatch.setattr(D, "reader_counts", lambda rid: (30, 1274, 30, 1265))
    assert D.verify(_k2(span=t, values={"events_t": 30, "n_t": 1274, "events_c": 30, "n_c": 1265}))[0]


def test_PLANT_r3_5_non_finite_values_are_not_counts():
    assert D._whole("nan") is None and D._whole("inf") is None and D._whole("-1") is None
