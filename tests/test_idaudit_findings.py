"""Identity audit of the class fix (hand audit of the 60 added/changed identities): a PMID that AACT links to several
registrations must resolve to the registration the PAPER ITSELF names (its full PubMed DataBank list + abstract NCTs),
before any 'one of them is in our family' tiebreak. STEP 1's NEJM paper (PMID 33567185) is listed as a RESULT
reference by both NCT03548935 (STEP 1) and NCT03574597 (SELECT); the tiebreak picked SELECT because SELECT is in the
served family, and report-family consolidation then merged STEP 1 into SELECT. A paper that names SEVERAL of the
candidates (Shah 2020 lists NCT01709981 and NCT02594111) reports several registrations: no tiebreak may pick one."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / "scripts"))

from kgap import k_gap  # noqa: E402
import k_gap_table as kt  # noqa: E402

IDX = {"pmid_nct": {}, "agent_nct": {}, "acr_nct": {}, "acr_title_nct": {}, "nct_pmids": {}, "study": {}}


def unit(label, cited):
    t = k_gap.identity_tokens(label)
    return {"cited": cited, "ncts": [], "author": t["author"], "year": t["year"], "acronyms": t["acronyms"],
            "marker": t["marker"], "label": label, "layout": "row"}


@pytest.fixture(autouse=True)
def clean_state(monkeypatch):
    for name in ("REF_PMID", "PUBNCT", "SELF_REG", "COLLECTIVE", "DATABANK"):
        monkeypatch.setattr(kt, name, {})
    monkeypatch.setattr(kt, "registered_before", lambda n, y, idx: True)


def idx_two_regs(a="NCT03574597", b="NCT03548935", pmid="33567185"):
    return dict(IDX, pmid_nct={pmid: [(a, "RESULT"), (b, "RESULT")]})


def test_paper_own_accession_beats_our_family_tiebreak(monkeypatch):
    monkeypatch.setattr(kt, "DATABANK", {"33567185": {"databank": ["NCT03548935"], "abstract": []}})
    r = kt.resolve_unit(unit("STEP 1 29", [{"pmid": "33567185"}]), None, idx_two_regs(), None,
                        our_fams={"NCT03574597"})
    assert r["ncts"] == ["NCT03548935"]
    assert "pmid_nct_from_pubmed_record_among_aact:NCT03548935" in r["basis"]
    assert not any(b.startswith("pmid_nct_tiebreak_our_family") for b in r["basis"])


def test_paper_listing_several_candidates_refuses_family_tiebreak(monkeypatch):
    monkeypatch.setattr(kt, "DATABANK", {"32295417": {"databank": ["NCT01709981", "NCT02594111"], "abstract": []}})
    r = kt.resolve_unit(unit("Shah et al. (16)", [{"pmid": "32295417"}]), None,
                        idx_two_regs("NCT02594111", "NCT01709981", "32295417"), None, our_fams={"NCT01709981"})
    assert r["ncts"] == []
    assert "pmid_nct_paper_lists_several:NCT01709981,NCT02594111" in r["basis"]


def test_single_nct_cache_is_not_used_as_the_papers_full_list(monkeypatch):
    # pubmed_ncts.json keeps only the FIRST DataBank NCT: it must not decide between candidates
    monkeypatch.setattr(kt, "PUBNCT", {"32295417": "NCT02594111"})
    r = kt.resolve_unit(unit("Shah et al. (16)", [{"pmid": "32295417"}]), None,
                        idx_two_regs("NCT02594111", "NCT01709981", "32295417"), None, our_fams=None)
    assert r["ncts"] == []


def test_negative_our_family_tiebreak_still_used_when_papers_list_not_held():
    r = kt.resolve_unit(unit("STEP 1 29", [{"pmid": "33567185"}]), None, idx_two_regs(), None,
                        our_fams={"NCT03574597"})
    assert r["ncts"] == ["NCT03574597"]


def test_negative_paper_accession_outside_aact_links_does_not_override(monkeypatch):
    # the paper's accession must be one of the registrations AACT links; otherwise it is not a tiebreak between them
    monkeypatch.setattr(kt, "DATABANK", {"33567185": {"databank": ["NCT09999999"], "abstract": []}})
    r = kt.resolve_unit(unit("STEP 1 29", [{"pmid": "33567185"}]), None, idx_two_regs(), None, our_fams=None)
    assert r["ncts"] == []
    assert any(b.startswith("pmid_nct_ambiguous") for b in r["basis"])
