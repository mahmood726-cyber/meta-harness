"""k-gap identification step (scripts/g1_identify.py): source-linked, deterministic, never adopting a candidate."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_identify as gi  # noqa: E402

XML = """<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>111</PMID><Article>
<ArticleTitle>A randomised trial of drug A</ArticleTitle>
<Abstract><AbstractText>We randomised 200 adults.</AbstractText></Abstract>
<DataBankList><DataBank><DataBankName>ClinicalTrials.gov</DataBankName><AccessionNumberList>
<AccessionNumber>NCT01234567</AccessionNumber></AccessionNumberList></DataBank></DataBankList></Article>
<OtherID Source="NLM">ISRCTN12345678</OtherID></MedlineCitation></PubmedArticle></PubmedArticleSet>"""


def test_PLANT_pubmed_title_is_read_and_registry_ids_come_from_databank_and_otherid(monkeypatch):
    # 13 Oct: `find(...) or Element` treated a childless <ArticleTitle> as FALSE, so every title came back empty
    from harness import http
    monkeypatch.setattr(http, "get_text", lambda *a, **k: XML)
    r = gi.pubmed_records(["111"])["111"]
    assert r["title"] == "A randomised trial of drug A"
    assert r["registry_ids"] == ["ISRCTN12345678", "NCT01234567"]


def test_PLANT_two_own_registrations_are_ambiguous_never_adopted(monkeypatch):
    # 13 Oct: ticagrelor '6 [25]' -- its PMID is the RESULT reference of TWO studies; both were adopted
    from kgap import aact_adapter, identity_chain as ic
    monkeypatch.setattr(gi, "pubmed_records", lambda p: {"7": {"title": "", "registry_ids": []}})
    monkeypatch.setattr(aact_adapter, "snapshot_dir", lambda: "x")
    monkeypatch.setattr(ic, "pmid_to_ncts", lambda p, s: {"7": {"NCT00000001": "RESULT", "NCT00000002": "RESULT"}})
    monkeypatch.setattr(gi, "ctgov_by_reference", lambda p: ([], [], "sha", 200))
    monkeypatch.setattr(gi, "fulltext_registrations", lambda s, l: ([], None))
    monkeypatch.setattr(gi, "candidates", lambda t, l: [])
    res = gi.identify([{"slug": "t", "label": "6 [25]", "pmid": "7", "active": False, "why": "NO_REGISTRATION_STATED"}])
    assert res[0]["identified"] == [] and res[0]["ambiguous"].startswith("MULTIPLE_OWN_REGISTRATIONS")


def test_a_candidate_is_recorded_never_adopted(monkeypatch):
    from kgap import aact_adapter, identity_chain as ic
    monkeypatch.setattr(gi, "pubmed_records", lambda p: {"8": {"title": "Melatonin in insomnia", "registry_ids": []}})
    monkeypatch.setattr(aact_adapter, "snapshot_dir", lambda: "x")
    monkeypatch.setattr(ic, "pmid_to_ncts", lambda p, s: {})
    monkeypatch.setattr(gi, "ctgov_by_reference", lambda p: ([], [], "sha", 200))
    monkeypatch.setattr(gi, "fulltext_registrations", lambda s, l: ([], None))
    monkeypatch.setattr(gi, "candidates", lambda t, l: [{"route": "TITLE_WORDS", "hits": [("NCT09999999", "x")]}])
    res = gi.identify([{"slug": "t", "label": "James 1990", "pmid": "8", "active": True, "why": "NO_REGISTRATION_STATED"}])
    assert res[0]["identified"] == [] and res[0]["candidates"][0]["hits"]
