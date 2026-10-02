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


# ---- permanent gate over the committed table: a row's label acronym must not contradict its registration's own name --
def _n(x):
    import re
    return re.sub(r"[^A-Z0-9]", "", (x or "").upper())


def label_registration_contradictions(trials):
    """Rows whose short label names an acronym that neither prefixes / is prefixed by the resolved registration's AACT
    acronym nor appears in its titles ('STEP 1 29' resolved to SELECT). Prefix, not equality: a citation number is
    glued onto the label ('WOMAN-210' = WOMAN-2 + ref 10). Title-style labels (> 6 words) are not acronym claims."""
    import re
    bad = []
    for r in trials:
        if not r.get("ncts") or len((r.get("label") or "").split()) > 6:
            continue
        acrs = [_n(re.sub(r"\bNCT\d{8}\b", "", a)) for a in k_gap.identity_tokens(r["label"])["acronyms"]]
        acrs = [a for a in acrs if len(a) >= 4]
        for nct in r["ncts"]:
            st = (r.get("study") or {}).get(nct) or {}
            reg = _n(st.get("acronym"))
            if not acrs or not reg:
                continue
            titles = _n(st.get("brief_title")) + "|" + _n(st.get("official_title"))
            if not any(a.startswith(reg) or reg.startswith(a) or a in titles for a in acrs):
                bad.append((r["slug"], r["label"], nct, st.get("acronym")))
    return bad


def test_gate_flags_the_planted_step1_select_row():
    planted = [{"slug": "x", "label": "STEP 1 29", "ncts": ["NCT03574597"],
                "study": {"NCT03574597": {"acronym": "SELECT", "brief_title": "Semaglutide Effects on Heart Disease"}}}]
    assert label_registration_contradictions(planted) == [("x", "STEP 1 29", "NCT03574597", "SELECT")]


def test_negative_gate_passes_glued_citation_numbers():
    ok = [{"slug": "x", "label": "WOMAN-210", "ncts": ["NCT03475342"], "study": {"NCT03475342": {"acronym": "WOMAN-2"}}},
          {"slug": "x", "label": "OSLER-1 NCT01439880", "ncts": ["NCT01439880"], "study": {"NCT01439880": {"acronym": "OSLER"}}}]
    assert label_registration_contradictions(ok) == []


def test_committed_table_has_no_label_registration_contradiction():
    import json
    t = json.loads((ROOT / "outputs" / "k_gap" / "k_gap_table.json").read_text(encoding="utf-8"))
    assert label_registration_contradictions(t["trials"]) == []
