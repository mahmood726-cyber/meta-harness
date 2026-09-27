"""Provenance tiers for counts found by the acquisition cascade (V1.0.1). Written BEFORE harness/provenance_tiers.py.

Fixtures: CORP-2's own abstract (PRIMARY, 26/120 vs 51/120); PMC9531702 Table 1 prints ICAP 'Recurrence %' 16.7, which is
the incessant-or-recurrent COMPOSITE (20/120), not the recurrence row (11/120) -> refused, never a corroboration.
"""
import json
import os

from harness import provenance_tiers as pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = json.load(open(os.path.join(ROOT, "evidence", "acquisition_cascade", "targets.json"), encoding="utf-8"))
T = {t["trial"]: t for t in SPEC["trials"]}
REC = T["ICAP"]["targets"][0]


def _sent(trial, tier, s, doc="d"):
    return {"trial": trial, "tier": tier, "where": "text", "sentence": s, "document": doc, "document_sha256": "x"}


def _row(trial, tier, row, headings, doc="d"):
    return {"trial": trial, "tier": tier, "where": "table", "row": row, "column_headings": headings, "table": "Table 1",
            "document": doc, "document_sha256": "x"}


def test_count_pairs_requires_the_percentage_to_corroborate():
    assert pt.count_pairs("26 (21.6%) of 120 and 51 (42.5%) of 120") == [(26, 120), (51, 120)]
    assert pt.count_pairs("26 (35.0%) of 120") == []            # percentage contradicts the count


def test_corp2_primary_abstract_is_found_primary():
    c = [_sent("CORP-2", pt.PRIMARY, "recurrent pericarditis was 26 (21·6%) of 120 in the colchicine group and "
                                     "51 (42·5%) of 120 in the placebo group (relative risk 0·49;")]
    r = pt.evaluate(T["CORP-2"], T["CORP-2"]["targets"][0], c)
    assert r["status"] == "FOUND_PRIMARY" and r["served_counts"] == [[26, 120], [51, 120]] and r["serve_label"] is None


def test_icap_composite_row_is_refused_and_its_percentage_cannot_corroborate():
    c = [_sent("ICAP", pt.SECONDARY_SOURCE, "incessant or recurrent pericarditis 20/120 vs 45/120", "a"),
         _row("ICAP", pt.SECONDARY_SOURCE, ["ICAP", "2013", "240", "16.7"], ["Trial", "Year", "N", "Recurrence %"], "b")]
    r = pt.evaluate(T["ICAP"], REC, c)
    assert r["status"] == "NOT_FOUND" and r["served_counts"] is None
    assert r["not_this_row"] and r["not_this_row"][0]["counts"] == [(20, 120), (45, 120)]
    assert not r["percent_corroboration"]
    assert any("mislabelled" in x["reason"] for x in r["refused"])


def test_secondary_only_is_served_with_a_visible_label():
    c = [_sent("ICAP", pt.SECONDARY_SOURCE, "recurrent pericarditis 11/120 vs 25/120")]
    r = pt.evaluate(T["ICAP"], REC, c)
    assert r["status"] == "FOUND_SECONDARY_ONLY" and r["serve_label"] == "secondary-source"


def test_primary_outranks_secondary_and_disagreement_raises_conflict():
    c = [_sent("ICAP", pt.SECONDARY_SOURCE, "recurrent pericarditis 12/120 vs 25/120", "meta"),
         _sent("ICAP", pt.PRIMARY, "recurrent pericarditis 11/120 vs 25/120", "nejm")]
    r = pt.evaluate(T["ICAP"], REC, c)
    assert r["served_tier"] == pt.PRIMARY and r["served_counts"] == [[11, 120], [25, 120]]
    assert r["conflict"] == pt.SOURCE_EFFECT_CONFLICT


def test_two_disagreeing_secondaries_raise_conflict():
    c = [_sent("ICAP", pt.SECONDARY_SOURCE, "recurrent pericarditis 11/120 vs 25/120", "m1"),
         _sent("ICAP", pt.SECONDARY_SOURCE, "recurrent pericarditis 11/120 vs 26/120", "m2")]
    assert pt.evaluate(T["ICAP"], REC, c)["conflict"] == pt.SOURCE_EFFECT_CONFLICT


def test_counts_off_the_arm_denominators_are_refused():
    c = [_sent("ICAP", pt.SECONDARY_SOURCE, "recurrent pericarditis 11/100 vs 25/100")]
    assert pt.evaluate(T["ICAP"], REC, c)["status"] == "NOT_FOUND"


def test_the_committed_report_matches_a_fresh_evaluation():
    rep = json.load(open(os.path.join(ROOT, "evidence", "acquisition_cascade", "REPORT.json"), encoding="utf-8"))
    cands = json.load(open(os.path.join(ROOT, "evidence", "acquisition_cascade", "CANDIDATES.json"), encoding="utf-8"))["candidates"]
    fresh = [pt.evaluate(t, tg, cands)["status"] for t in SPEC["trials"] for tg in t["targets"]]
    assert [r["status"] for r in rep["targets"]] == fresh
    assert rep["corp2_0_49"]["audit"]["verdict"] == "MISLABELLED_RRR"


def _rev(tier, **extra):
    return {"outcomes": [{"name": "Recurrent pericarditis", "trials": [{"id": "PMID 23992557", "provenance_tier": tier, **extra}]}]}


SW = {"document": "_secondary/PMCX.xml", "document_sha256": "ab" * 32, "table": "Table 2"}


def test_secondary_source_row_without_the_page_label_is_refused():
    html = "<tr><td>PMID 23992557</td><td>11/120 vs 25/120</td></tr>"
    assert any("without the visible" in p for p in pt.serving_problems(_rev(pt.SECONDARY_SOURCE, secondary_witness=SW), html))


def test_secondary_source_row_with_label_and_witness_passes():
    html = ("<tr><td>PMID 23992557</td><td>11/120 <span class='badge secondary-source' "
            "data-provenance-tier='SECONDARY_SOURCE'>secondary-source</span></td></tr>")
    assert pt.serving_problems(_rev(pt.SECONDARY_SOURCE, secondary_witness=SW), html) == []


def test_secondary_source_row_without_a_hashed_citing_document_is_refused():
    html = "PMID 23992557 data-provenance-tier='SECONDARY_SOURCE'"
    assert any("no citing document" in p for p in pt.serving_problems(_rev(pt.SECONDARY_SOURCE, secondary_witness={}), html))


def test_a_row_passed_off_as_primary_on_a_secondary_witness_is_refused():
    assert any("only witness is secondary" in p for p in pt.serving_problems(_rev(pt.PRIMARY, secondary_witness=SW), ""))


def test_the_page_renders_the_label_for_a_secondary_row():
    from harness import page
    import inspect
    assert "data-provenance-tier='SECONDARY_SOURCE'" in inspect.getsource(page)
