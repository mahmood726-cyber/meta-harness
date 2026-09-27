"""Plants from the REV-R1 codex review of the V1.0.1 GLP-1/melatonin modules: 15 findings, each reproduced by Claude
before the fix and pinned here so it cannot return. Every one could have served a FALSE state (or crashed)."""
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import (ascertainment as asc, comparator_display as cd, family_pub_links as fpl,  # noqa: E402
                     outcome_match as om, search_execution as se)

ROOT = Path(__file__).resolve().parents[1]


def _asc_root(tmp_path, pro_q, adj_q, src="2020-01-01", res="2021-01-01"):
    (tmp_path / "cache" / "t").mkdir(parents=True)
    (tmp_path / "cache" / "t" / "d.txt").write_text(f"{pro_q} {adj_q}", encoding="utf-8")
    ev = {"documents": {"d": {"document_ref": "cache/t/d.txt", "earliest_date": src}},
          "families": {"F": {"prospective": {"doc": "d", "quote": pro_q}, "ascertained": {"doc": "d", "quote": adj_q},
                             "results": {"earliest_date": res}}}}
    (tmp_path / "cache" / "t" / "ascertainment_evidence.json").write_text(json.dumps(ev), encoding="utf-8")
    return tmp_path


ADJ = "Cardiovascular events were adjudicated by an independent committee."
PRO = "The primary outcome was 3-point MACE (cardiovascular death, nonfatal myocardial infarction or nonfatal stroke)."


@pytest.mark.parametrize("pro,adj,match", [
    ("3-point MACE was not prospectively specified in the protocol.", ADJ, "negated"),
    (PRO, "Cardiovascular events were not adjudicated by any committee.", "negated"),
    ("Only 4-point MACE was specified in this protocol.", ADJ, "names neither"),
])
def test_PLANT_negated_or_four_point_evidence_refused(tmp_path, pro, adj, match):
    with pytest.raises(asc.EvidenceRefused, match=match):
        asc.load(_asc_root(tmp_path, pro, adj), "t")


def test_PLANT_dates_are_parsed_not_string_compared(tmp_path):
    with pytest.raises(asc.EvidenceRefused, match="not an ISO date"):
        asc.load(_asc_root(tmp_path, PRO, ADJ, src="2020-10-01", res="2020-2-01"), "t")


def test_PLANT_a_pmid_selects_only_the_articles_own_pmid(tmp_path):
    xml = ("<PubmedArticle><MedlineCitation><PMID>111</PMID><Article><Abstract>" + PRO + "</Abstract></Article>"
           "<CommentsCorrectionsList><CommentsCorrections><PMID>222</PMID></CommentsCorrections></CommentsCorrectionsList>"
           "</MedlineCitation></PubmedArticle>")
    (tmp_path / "b.xml").write_text(xml, encoding="utf-8")
    assert PRO in asc._doc_text(tmp_path, {"document_ref": "b.xml", "pmid": "111"})
    with pytest.raises(asc.EvidenceRefused, match="PMID 222 not in"):
        asc._doc_text(tmp_path, {"document_ref": "b.xml", "pmid": "222"})


@pytest.mark.parametrize("link,match", [
    ({"nct": "NCT0", "pmid": "111", "binding_token": "", "record": {"id": "111", "title": "x"}}, "empty or too short"),
    ({"nct": "NCT0", "pmid": "111", "binding_token": "TRIAL-A", "record": {"id": "222", "title": "TRIAL-A"}}, "not the linked one"),
])
def test_PLANT_link_token_and_pmid_are_checked(monkeypatch, link, match):
    monkeypatch.setattr(fpl, "links", lambda root, slug: [link])
    with pytest.raises(fpl.LinkRefused, match=match):
        fpl.merge(".", "s", {"registry": [{"id": "NCT0", "title": "TRIAL-A"}]})


def test_PLANT_a_repeated_or_already_held_link_is_neither_duplicated_nor_unlinked(monkeypatch):
    rec = {"id": "111", "title": "TRIAL-A results"}
    x = {"nct": "NCT0", "pmid": "111", "binding_token": "TRIAL-A", "record": rec}
    monkeypatch.setattr(fpl, "links", lambda root, slug: [x, x])
    out = fpl.merge(".", "s", {"registry": [{"id": "NCT0", "title": "TRIAL-A"}]})
    assert [r["id"] for r in out["records"]] == ["111"]
    monkeypatch.setattr(fpl, "links", lambda root, slug: [x])
    out = fpl.merge(".", "s", {"records": [dict(rec)], "registry": [{"id": "NCT0", "title": "TRIAL-A"}]})
    assert out["records"][0]["family_link"]["nct"] == "NCT0" and out["records"][0]["nct"] == "NCT0"


def test_PLANT_HELD_needs_a_source_and_an_empty_quote_proves_nothing(tmp_path):
    with pytest.raises(om.InputsRefused, match="too-short quote"):
        om.check_source(tmp_path, {"kind": "abstract", "document_ref": "r.json", "record_id": "1", "quote": ""})
    side = {"state": "HELD", "scale": "MD", "effect": 1, "window": {"value": "W", "state": "HELD"}}
    doc = {"comparator_pmid": "1", "outcome": "o", "trials": [{"family_id": "F", "name": "T", "report_pmid": "2",
                                                              "ours": side, "theirs": side}]}
    (tmp_path / "cache" / "s").mkdir(parents=True)
    (tmp_path / "cache" / "s" / "comparator_member_inputs.json").write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(om.InputsRefused, match="HELD with no source"):
        om.load(tmp_path, "s")


def test_PLANT_a_NaN_served_effect_fails_the_cross_check():
    side = {"state": "HELD", "scale": "MD", "effect": 1}
    doc = {"comparator_pmid": "1", "outcome": "o", "trials": [{"family_id": "F", "name": "T", "report_pmid": "2",
                                                              "ours": side, "theirs": side}]}
    review = {"outcomes": [{"primary": True, "trials": [{"label": "2", "effect": float("nan"), "scale": "MD"}]}]}
    with pytest.raises(om.InputsRefused):
        om.compare(doc, review)


def test_PLANT_held_zero_vs_not_held_is_decided_by_the_record(tmp_path):
    (tmp_path / "protocols").mkdir()
    (tmp_path / "protocols" / "s.md").write_text("- **Search.** PubMed and ClinicalTrials.gov via AACT.\n", encoding="utf-8")
    c = tmp_path / "cache" / "s"
    c.mkdir(parents=True)
    (c / "retrieval_ledger.json").write_text(json.dumps({"sources": [
        {"source_id": "q", "kind": "PUBMED_CONCEPT_QUERY", "state": "RAN_ZERO", "record_ids": [], "query": "x", "run_utc": "d"}],
        "records": {}}), encoding="utf-8")
    (c / "family_query.json").write_text(json.dumps({"source_id": "a", "state": "RAN_OK", "query": "y", "run_utc": "d"}),
                                        encoding="utf-8")
    rows = {r["source"]: r for r in se.build(tmp_path, "s", {})["rows"]}
    assert rows["PubMed/MEDLINE"]["state"] == "EXECUTED"                        # a held zero
    assert rows["ClinicalTrials.gov (AACT)"]["state"] == "EXECUTED_IDS_NOT_HELD"  # no record_ids field: not held


@pytest.mark.parametrize("rows", [[], [{"label": "A", "effect": 0, "ci_low": 1, "ci_high": -1, "printed_weight_pct": 100}]])
def test_PLANT_empty_or_reversed_rows_are_refused(rows):
    with pytest.raises(cd.DisplayRefused):
        cd.assess({"rows": rows, "printed_pools": {"Overall": {"effect": 0, "ci_low": -1, "ci_high": 1}},
                   "figure": dict.fromkeys(("label", "document_ref", "sha256", "read_by", "licence"), "t")})


def test_the_real_evidence_files_still_load_under_the_stricter_rules():
    assert asc.load(ROOT, "glp1-ra-mace-t2d") is not None
    assert cd.assess(cd.load(ROOT, "melatonin-primary-insomnia-sol"))["calculation"]["state"] == "CALCULATION_REPRODUCED"
    assert om.load(ROOT, "melatonin-primary-insomnia-sol") and om.load(ROOT, "doac-vte-recurrence")
