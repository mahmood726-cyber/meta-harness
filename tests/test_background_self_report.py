"""A registration with NO RESULT/DERIVED reference keeps the BACKGROUND references whose own PubMed record names its
NCT: DESCARTES (NCT01516879) types all 12 references BACKGROUND, its NEJM report 24678979 among them, so it resolved to
no report and read IDENTIFICATION. Corpus (AACT 2026-08-30): 1 resolved NCT has no RESULT/DERIVED reference."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import k_gap_table as kt  # noqa: E402


def test_only_background_papers_naming_the_nct_are_kept(monkeypatch):
    monkeypatch.setattr(kt, "pubmed_ncts", lambda pmids, offline=False: {
        "24678979": "NCT01516879", "29221604": "", "28249876": "NCT01709500"})
    idx = {"background_pmids": {"NCT01516879": ["24678979", "29221604", "28249876"]}}
    assert kt.background_self_reports("NCT01516879", idx) == {"24678979"}


def test_resolve_unit_uses_it_only_without_typed_references(monkeypatch):
    monkeypatch.setattr(kt, "pubmed_ncts", lambda pmids, offline=False: {p: "NCT01516879" for p in pmids})
    kt._OFFLINE = True
    base = {"pmid_nct": {}, "acr_nct": {}, "acr_title_nct": {}, "agent_nct": {}, "study": {},
            "background_pmids": {"NCT01516879": ["24678979"]}}
    u = {"cited": [], "ncts": ["NCT01516879"], "author": None, "year": None, "acronyms": []}
    r = kt.resolve_unit(u, None, dict(base, nct_pmids={}), None)
    assert r["pmids"] == ["24678979"] and "background_ref_names_its_nct:1" in r["basis"]
    kt.YEARS.setdefault("11111111", 2015)
    r = kt.resolve_unit(u, None, dict(base, nct_pmids={"NCT01516879": ["11111111"]}), None)
    assert r["pmids"] == ["11111111"]          # a typed reference exists: background is not consulted
