"""Held-row invariant, typed per-result clauses and the auditor fixes, from two served reviews:
  CAP corticosteroids (review_sha256 d26a4681...) and COVID corticosteroids (review_sha256 58582fa6...).
Controls are PINNED: the reviews are read at the commit that served those hashes (6260e70c), never from the working tree, and the
pre-fix auditor is loaded from git (23642e0d) -- a control anchored to a mutable page retires itself when the page is fixed."""
import importlib.util
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import evidence_identity as ei, held_rows, known_missing, pipeline, reason_audit  # noqa: E402

SERVED = "6260e70c"
PREFIX_AUDITOR = "23642e0d"
CAP, COVID = "corticosteroids-cap-mortality", "corticosteroids-covid19-mortality"
COVID_STEROID_SENTENCE = ("At day 28, the median number of days alive without life support in the hydrocortisone vs placebo group "
                          "were 7 vs 10 (adjusted mean difference: -1.1 days, 95% CI -9.5 to 7.3, P = .79); mortality was 6/16 vs "
                          "2/14; and the number of serious adverse reactions 1/16 vs 0/14.")


def _git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, check=True).stdout


def served(slug):
    return json.loads(_git("show", f"{SERVED}:docs/reviews/{slug}/review.json"))


def ctx(slug):
    topic = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
    specs = {sp.get("name"): sp for sp, _ in pipeline._outcome_specs(topic)}
    recs = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
    return specs, recs, reason_audit.sources_by_trial(slug, recs, ROOT)


@pytest.fixture(scope="module")
def prefix_auditor():
    src = _git("show", f"{PREFIX_AUDITOR}:harness/reason_audit.py").decode("utf-8")
    spec = importlib.util.spec_from_loader("harness._reason_audit_prefix_heldrows", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "harness"
    exec(compile(src, f"{PREFIX_AUDITOR}:harness/reason_audit.py", "exec"), mod.__dict__)
    return mod


def test_served_hashes_are_the_reviews_the_fixtures_name():
    for slug, head in ((CAP, "d26a4681"), (COVID, "58582fa6")):
        cert = json.loads(_git("show", f"{SERVED}:docs/reviews/{slug}/CERTIFICATE.json"))
        assert cert["review_sha256"].startswith(head)


# ---- CAP (1): the held table row, and NOT_IN_COMMITTED_SOURCE refused when it exists -------------------------------------------
def _escape_table_rows():
    raw = open(os.path.join(ROOT, "cache", CAP, "ft_35723686.txt"), encoding="utf-8").read()
    return [r for r in ei.count_rows(raw, "35723686", "fulltext:35723686") if "mortality" in r["label"].lower()]


def test_PLANT_escape_hospital_mortality_row_is_read_from_the_held_table():
    """Pre-fix this row was skipped as a 'percentage row' ('no./total no. (%)'), so absence was stated from the abstract."""
    rows = [r for r in _escape_table_rows() if r["label"].lower().startswith("hospital mortality")]
    assert len(rows) == 1
    assert [(a["events"], a["n"], a["n_group"]) for a in rows[0]["arms"]] == [(34, 291, 297), (28, 281, 287)]
    assert rows[0]["timepoint"] == "in-hospital"                       # from the section header 'In-hospital morbidity and mortality'


def test_PLANT_served_known_missing_says_not_in_committed_source_and_the_invariant_refuses_it():
    rv = served(CAP)
    km = next(r for r in rv["outcomes"][0]["known_missing_sensitivity"]["rows"] if r["trial_key"] == "35723686")
    assert km["value_status"] == "NOT_IN_COMMITTED_SOURCE"            # the defect, as served
    specs, _, srcs = ctx(CAP)
    hit = next(c for c in held_rows.contradictions(CAP, rv, srcs, specs, [rv.get("question") or ""])
               if c["trial"] == "35723686" and c["kind"] == "known_missing")
    assert hit["contradicted"] and hit["held_row"]["source_id"] == "fulltext:35723686"


def test_known_missing_no_longer_emits_not_in_committed_source_for_a_held_row():
    rv = served(CAP)
    specs, recs, srcs = ctx(CAP)
    rec_by_id = {str(r["id"]): r for r in reason_audit.iter_records(recs)}
    row = known_missing._source_value(CAP, rv["outcomes"][0], {"id": "PMID 35723686"}, rec_by_id, recs, srcs, rv)
    assert row["value_status"] == known_missing.HELD_ROW_NOT_EXTRACTED and row["missing_class"] == "EXTRACTION_DEBT"
    assert "ai" not in row                                             # extraction debt is never pooled here


# ---- CAP (2): the auditor's wrong challenge ---------------------------------------------------------------------------------------
def test_PLANT_prefix_auditor_challenged_escape_with_the_60_day_risk_difference(prefix_auditor):
    rv = served(CAP)
    specs, _, srcs = ctx(CAP)
    row = next(a for a in rv["outcomes"][0]["declared_absent_trials"] if "35723686" in a["id"])
    old = prefix_auditor.audit_reason_row(rv["outcomes"][0], row, srcs["35723686"], specs[rv["outcomes"][0]["name"]])
    assert old["verdict"] == "REASON_FALSE_VALUE_HELD" and "60-day" in old["source_span"]


def test_the_60_day_risk_difference_cannot_establish_an_in_hospital_rr():
    rv = served(CAP)
    specs, _, srcs = ctx(CAP)
    row = next(a for a in rv["outcomes"][0]["declared_absent_trials"] if "35723686" in a["id"])
    spec = {**specs[rv["outcomes"][0]["name"]], "target_population": rv.get("question")}   # as annotate_review passes it
    new = reason_audit.audit_reason_row(rv["outcomes"][0], row, srcs["35723686"], spec)
    full = reason_audit.typed_candidates(rv["outcomes"][0], row, srcs["35723686"], spec)   # the whole population, not the capped display
    ard = [c for c in full if c.get("effect_measure") == "RD"]
    assert ard and all("effect_measure:RD!=RR" in c["mismatch"] for c in ard)         # no risk difference establishes an RR
    ard60 = [c for c in ard if c.get("estimate") == -2.0 and c.get("ci") == [-8.0, 5.0]]
    assert ard60 and all("timepoint:60 days" in c["mismatch"] for c in ard60)          # the 60-day RD is also the wrong timepoint
    assert new["verdict"] == "REASON_NOT_DISPROVED"
    # the held in-hospital Table 2 row fits every field EXCEPT population: 34% HCAP is unadjudicated against a CAP question, so it
    # cannot disprove the refusal either (reconciled with the fixture and an independent codex label, both NOT_DISPROVED)
    table = next(c for c in full if c["span"].startswith("Hospital Mortality"))
    assert table["mismatch"] == ["population:ELIGIBILITY_ADJUDICATION_REQUIRED(HCAP 34%)"]


# ---- CAP (3): denominators and eligibility ----------------------------------------------------------------------------------------
def test_counts_use_outcome_ascertained_denominators_and_carry_the_missing():
    row = next(r for r in _escape_table_rows() if r["label"].lower().startswith("hospital mortality"))
    c = held_rows.ascertained_counts(row)
    assert [(a["events"], a["n_ascertained"], a["missing"], a["non_events"]) for a in c["arms"]] == [(34, 291, 6, 257), (28, 281, 6, 253)]
    assert all(a["non_events"] != a["n_group"] - a["events"] for a in c["arms"])      # a missing patient is never a survivor


def test_events_beside_a_group_size_do_not_become_an_ascertained_denominator():
    c = held_rows.ascertained_counts({"arms": [{"events": 14, "n": None, "n_group": 65}, {"events": 6, "n": None, "n_group": 64}]})
    assert all(a["n_ascertained"] is None and a["non_events"] is None for a in c["arms"])


def test_hcap_subpopulation_is_flagged_for_eligibility_adjudication_not_admitted():
    rv = served(CAP)
    _, _, srcs = ctx(CAP)
    flags = held_rows.subpopulation_flags(srcs["35723686"], [rv.get("question") or ""])
    assert [(f["subpopulation"], f["share_percent"], f["flag"]) for f in flags] == [("HCAP", 34.0, "ELIGIBILITY_ADJUDICATION_REQUIRED")]


# ---- COVID (1): multi-outcome sentences and the cross-extraction contradiction ----------------------------------------------------
def test_a_multi_outcome_sentence_splits_into_per_outcome_clauses():
    got = [(c["label"], [a["events"] for a in c["arms"]]) for c in ei.result_clauses(COVID_STEROID_SENTENCE)]
    assert got == [("mortality was 6/16 vs 2/14", [6, 2]), ("and the number of serious adverse reactions 1/16 vs 0/14.", [1, 0])]


def test_PLANT_the_sentence_is_used_for_harms_while_mortality_is_certified_absent():
    rv = served(COVID)
    sae = next(t for t in rv["outcomes"][1]["trials"] if "34138478" in t["id"])
    mort = next(a for a in rv["outcomes"][0]["declared_absent_trials"] if "34138478" in a["id"])
    assert "mortality was 6/16 vs 2/14" in sae["source"] and mort["reason_code"] == "OUTCOME_NOT_IN_SOURCE"   # the defect, as served
    specs, _, _ = ctx(COVID)
    extraction_only = held_rows.review_texts(rv, "34138478")          # ONLY what another extraction in this review quotes
    hits = held_rows.matching_rows(rv["outcomes"][0], "34138478", extraction_only, specs[rv["outcomes"][0]["name"]])
    assert hits and hits[0]["source_id"] == "extraction:Serious adverse events:source"


def test_enforce_refuses_the_absence_and_leaves_the_pool_alone():
    rv = served(COVID)
    specs, _, srcs = ctx(COVID)
    pool_before = json.dumps(rv["outcomes"][0].get("result"), sort_keys=True)
    changed = held_rows.enforce(COVID, rv, srcs, specs)
    row = next(a for a in rv["outcomes"][0]["declared_absent_trials"] if "34138478" in a["id"])
    assert [c["trial"] for c in changed] == ["34138478"] and row["reason_code"] == held_rows.REFUSED_AS
    assert row["absence_refused"]["was"] == "OUTCOME_NOT_IN_SOURCE"
    assert json.dumps(rv["outcomes"][0].get("result"), sort_keys=True) == pool_before


# ---- COVID (2): the auditor never sums, and a residual category is not the target -------------------------------------------------
def _codex(rv):
    return next(a for a in rv["outcomes"][1]["declared_absent_trials"] if "32876695" in a["id"])


def test_PLANT_prefix_auditor_called_codex_false_because_numbers_exist(prefix_auditor):
    rv = served(COVID)
    specs, _, srcs = ctx(COVID)
    old = prefix_auditor.audit_reason_row(rv["outcomes"][1], _codex(rv), srcs["32876695"], specs[rv["outcomes"][1]["name"]])
    assert old["verdict"] == "REASON_FALSE_VALUE_HELD"


def test_codex_other_serious_aes_do_not_disprove_the_refusal_and_nothing_is_summed():
    rv = served(COVID)
    specs, _, srcs = ctx(COVID)
    new = reason_audit.audit_reason_row(rv["outcomes"][1], _codex(rv), srcs["32876695"], specs[rv["outcomes"][1]["name"]])
    full = reason_audit.typed_candidates(rv["outcomes"][1], _codex(rv), srcs["32876695"], specs[rv["outcomes"][1]["name"]])
    assert new["verdict"] == "REASON_NOT_DISPROVED"
    residual = [c for c in full if c.get("definition") == "RESIDUAL"]
    assert residual and all("definition:RESIDUAL" in c["mismatch"] for c in residual)
    sums = {33 + 47 + 5, 43 + 42 + 9, 33 + 5, 43 + 9}
    assert not [c for c in full if c.get("arms") and {a["events"] for a in c["arms"]} & sums]


def test_other_group_is_not_a_residual_category():
    assert ei.definition_of("12 of 100 in the other group had diarrhoea", "Diarrhoea") == "AS_NAMED"
    assert ei.definition_of("other serious adverse events", "Serious adverse events") == "RESIDUAL"
