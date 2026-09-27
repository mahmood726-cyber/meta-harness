"""Two reviewer fixtures, colchicine-secondary-cv-prevention (V1.0.1). Written BEFORE the fix.

(1) COPS REPORT FAMILY: the 12-month primary report (PMID 32862667) and the 2-year follow-up letter (PMID 34748393,
DOI 10.1161/CIRCULATIONAHA.121.054610) are ONE trial (ACTRN12615000861550). The protocol's timepoint is 'trial end',
so the 2-year report is the timepoint report and the 12-month report a sensitivity candidate; the refusal, judged on
the 12-month abstract, must say so; the two are never two trials.

(2) AKRAMI ANALYSIS POPULATION: 122 randomised / 120 analysed in the colchicine arm, the 2 exclusions 'lost to
follow-up' in the CONSORT diagram but 'drug intolerance' in the text, and the placebo GI '3 (2.5%)' fits 120 not 129.
SOURCE_INTERNALLY_INCONSISTENT scoped to the SAFETY denominator: Akrami's GI row is held out of the pool (it was
pooled, k=1); the efficacy rows are judged on their own grounds.
"""
import copy
import json
import os

import pytest

from harness import claimgraph, fetch, invalidation, pipeline

ROOT = pipeline.ROOT
SLUG = "colchicine-secondary-cv-prevention"
AKRAMI = "PMID 34876021"
GI = "Gastrointestinal adverse effects"


def _rf():
    from harness import report_family
    return report_family


# ---------------------------------------------------------------- (1) COPS report family
def test_follow_up_is_parsed_from_the_witnessed_span():
    rf = _rf()
    assert rf.months_in("Over the 12-month follow-up") == 12
    assert rf.months_in("Two-Year Follow-Up of the Australian COPS Randomized Clinical Trial") == 24


def test_cops_family_selects_the_two_year_report_under_trial_end():
    rf = _rf()
    fam = rf.load(ROOT, SLUG)[0]
    sel = rf.select(rf.verify_family(ROOT, fam), "trial end")
    assert sel["timepoint_report"] == "PMID 34748393"
    roles = {r["report_id"]: r["report_role"] for r in sel["reports"]}
    assert roles == {"PMID 32862667": rf.SENSITIVITY_CANDIDATE, "PMID 34748393": rf.TIMEPOINT_REPORT}


def test_a_declared_follow_up_the_span_does_not_state_fails_closed():
    rf = _rf()
    fam = copy.deepcopy(rf.load(ROOT, SLUG)[0])
    fam["reports"][1]["follow_up_months"] = 36
    with pytest.raises(ValueError, match="witnessed span states 24"):
        rf.verify_family(ROOT, fam)


def test_a_tampered_witness_digest_fails_closed():
    rf = _rf()
    fam = copy.deepcopy(rf.load(ROOT, SLUG)[0])
    fam["reports"][0]["follow_up_witness"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="digest mismatch"):
        rf.verify_family(ROOT, fam)


def _review_with_family():
    rf = _rf()
    rev = {"slug": SLUG, "outcomes": [{"name": "MACE", "primary": True, "timepoint": "trial end", "trials": []}],
           "trial_families": [{"family_id": "ACTRN12615000861550", "reports": []}]}
    rf.attach(rev, ROOT)
    return rev


def test_two_reports_of_one_trial_pooled_as_two_rows_is_a_double_count():
    rf = _rf()
    rev = _review_with_family()
    rev["outcomes"][0]["trials"] = [{"id": "PMID 32862667", "report_role": rf.SENSITIVITY_CANDIDATE},
                                    {"id": "PMID 34748393"}]
    assert any(p["kind"] == "FAMILY_DOUBLE_COUNT" for p in rf.problems(rev))
    assert rev["report_families"][0]["counted_as_trials"] == 1
    assert rev["trial_families"][0]["report_family_selection"]["timepoint_report"] == "PMID 34748393"


def test_a_refusal_judged_on_the_12_month_report_must_name_the_timepoint_report():
    rf = _rf()
    rev = _review_with_family()
    refusal = {"trial": "COPS (PMID 32862667)", "not_pooled_because": "refused on ambiguity"}
    rev["reproduction"] = {"refusals": [refusal]}
    assert any(p["kind"] == "FAMILY_TIMEPOINT_UNLABELLED" for p in rf.problems(rev))
    rev["reproduction"]["refusals"] = rf.annotate_refusals([refusal], rev)
    fam = rev["reproduction"]["refusals"][0]["report_family"]
    assert fam["judged_report_role"] == rf.SENSITIVITY_CANDIDATE and fam["timepoint_report"] == "PMID 34748393"
    assert fam["timepoint_result_state"] == "DISCOVERED_NOT_RETRIEVED"
    assert rf.problems(rev) == []


def test_the_family_problem_kinds_block_the_screening_gate():
    from harness import screening_record
    assert {"FAMILY_DOUBLE_COUNT", "FAMILY_TIMEPOINT_UNLABELLED"} <= set(screening_record.BLOCKING)


# ---------------------------------------------------------------- (2) Akrami, endpoint-scoped
def _akrami_fact():
    return next(f for f in claimgraph.regulatory_facts(ROOT, SLUG) if f["trial"] == "Akrami 2021")


def test_akrami_is_held_internally_inconsistent_for_harms_only():
    f = _akrami_fact()
    assert invalidation.inconsistency_scope(f) == [GI, "Non-cardiovascular death"]
    assert invalidation.missing_state(f, outcome=GI) == invalidation.SOURCE_INTERNALLY_INCONSISTENT
    assert (invalidation.missing_state(f, outcome="Trial-defined major coronary/cardiovascular composite")
            == invalidation.SOURCE_RETRIEVED_NOT_EXTRACTED)
    kinds = {s["kind"] for s in f["spans"]}
    assert {"results_allocated_122_vs_129", "abstract_assigned_120_vs_129", "discussion_two_left_for_intolerance",
            "abstract_gi_15_vs_3"} <= kinds


def test_the_figure_is_a_declared_transcription_not_a_verbatim_span():
    d = _akrami_fact()["decision"]
    ft = d["figure_transcription"]
    assert "MODEL VISUAL TRANSCRIPTION" in ft["method"]
    assert "colchicine_lost_to_follow_up_2" in ft["image_only"]
    assert not any(k.startswith("figure") for k in d["source_conflict"]["spans_preserved"])


def _build(name):
    config = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
    records = fetch.ensure(config, "")
    inp = pipeline.outcome_inputs(SLUG, config, records)
    spec, kind = next((s, k) for s, k in pipeline._outcome_specs(config) if s["name"] == name)
    return pipeline.build_outcome_from_inputs(inp, spec, kind, SLUG)


def test_akrami_gi_row_is_held_out_of_the_pool_with_its_conflict_named():
    out = _build(GI)
    assert AKRAMI not in [t["id"] for t in out["trials"]]
    row = next(a for a in out["declared_absent_trials"] if a["id"] == AKRAMI)
    assert row["reason_code"] == invalidation.SOURCE_INTERNALLY_INCONSISTENT
    assert row["held_out_row"]["ai"] == 15 and row["held_out_row"]["n2i"] == 129
    spans = " ".join(c["span"] for c in row["conflict_locations"])
    assert "122 and 129" in spans and "drug intolerance" in spans


def test_scope_leaves_the_efficacy_pool_untouched():
    out = _build("Trial-defined major coronary/cardiovascular composite")
    assert [t["id"] for t in out["trials"]] == ["PMID 31733140", "PMID 32865380", "PMID 39555823"]
    assert not any(a.get("reason_code") == invalidation.SOURCE_INTERNALLY_INCONSISTENT
                   for a in out["declared_absent_trials"])
