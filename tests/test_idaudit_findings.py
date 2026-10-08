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
        # the whole short label too: identity_tokens reads 'RE-COVER' as the acronym 'COVER' (it drops 'RE-'), which
        # neither prefixes 'RECOVERI' nor appears in an acronym-free title -- a false contradiction on the V9-03 labels
        if acrs and len(_n(r["label"])) >= 4:
            acrs.append(_n(r["label"]))
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


def test_single_nct_fallback_refuses_a_multi_trial_paper(monkeypatch):
    # no AACT link at all; PUBNCT holds the first DataBank NCT, the full list holds two -> no identity
    monkeypatch.setattr(kt, "PUBNCT", {"28605608": "NCT01032629"})
    monkeypatch.setattr(kt, "DATABANK", {"28605608": {"databank": ["NCT01032629", "NCT01989754"], "abstract": []}})
    r = kt.resolve_unit(unit("CANVAS Program", [{"pmid": "28605608"}]), None, IDX, None)
    assert r["ncts"] == []
    assert "pmid_nct_paper_lists_several:NCT01032629,NCT01989754" in r["basis"]


def test_negative_single_nct_fallback_kept_for_a_single_trial_paper(monkeypatch):
    monkeypatch.setattr(kt, "PUBNCT", {"31707795": "NCT01169259"})
    monkeypatch.setattr(kt, "DATABANK", {"31707795": {"databank": ["NCT01169259"], "abstract": []}})
    r = kt.resolve_unit(unit("Manson 2019 [50]", [{"pmid": "31707795"}]), None, IDX, None)
    assert r["ncts"] == ["NCT01169259"]


# ---- a Cochrane study ID names its PRIMARY report: 'Legro 2007' is Legro RS 2007 (NEJM, NCT00068861), not the first
# citation listed under it (Cataldo 2008, a secondary report with no registration) -- acq/k-gap's identity chain
# resolved this row to the NEJM paper; ours took Cataldo. Found by comparing the two chains at integration.
LEGRO = ("References to studies included in this review "
         "Legro 2007 {published data only} Cataldo N, Barnhart H, Legro R. Extended-release metformin does not reduce "
         "the clomiphene citrate dose required to induce ovulation in polycystic ovary syndrome. Journal of Clinical "
         "Endocrinology and Metabolism 2008;93(8):3147-7. [ DOI ] [ PMC free article ] [ PubMed ] [ Google Scholar ] "
         "Legro RS, Barnhart HX, Schlaff WD. Clomiphene, metformin, or both for infertility in the polycystic ovary "
         "syndrome. New England Journal of Medicine 2007;356:551-66. [original article] [ DOI ] [ PubMed ] "
         "[ Google Scholar ] "
         "Liu 2017 {published data only} Liu C, Feng G, Huang W. Comparison of clomiphene citrate and letrozole for "
         "ovulation induction in women with polycystic ovary syndrome: a prospective randomized trial. Gynecological "
         "Endocrinology 2017;33(11):872-6. [ DOI ] [ PubMed ] [ Google Scholar ] "
         "Additional references")


def test_study_id_takes_the_citation_whose_author_and_year_name_the_study():
    refs = kt.study_id_citations(LEGRO)
    assert (refs["Legro 2007"]["first_author"], refs["Legro 2007"]["year"]) == ("Legro", "2007")
    assert refs["Legro 2007"]["title"].startswith("Clomiphene, metformin, or both")


def test_negative_study_id_with_one_citation_unchanged():
    refs = kt.study_id_citations(LEGRO)
    assert (refs["Liu 2017"]["first_author"], refs["Liu 2017"]["year"]) == ("Liu", "2017")


# ---- a paper listing several registrations is still resolved when the ROW'S OWN LABEL names exactly one of them by
# its AACT acronym. SYNTHETIC acronyms below (ALPHA / BETA-ED); the real SMART case is the negative at the end.
def test_several_listed_resolved_by_the_labels_own_acronym(monkeypatch):
    monkeypatch.setattr(kt, "DATABANK", {"29485925": {"databank": ["NCT02444988", "NCT02547779"], "abstract": []}})
    idx = dict(idx_two_regs("NCT02444988", "NCT02547779", "29485925"),
               study={"NCT02444988": {"acronym": "ALPHA"}, "NCT02547779": {"acronym": "BETA-ED"}})
    r = kt.resolve_unit(unit("Semler (ALPHA trial)", [{"pmid": "29485925"}]), None, idx, None)
    assert r["ncts"] == ["NCT02444988"]
    assert "pmid_nct_paper_lists_several_label_acronym:NCT02444988" in r["basis"]


def test_negative_several_listed_without_a_label_acronym_stays_refused(monkeypatch):
    monkeypatch.setattr(kt, "DATABANK", {"29485925": {"databank": ["NCT02444988", "NCT02547779"], "abstract": []}})
    idx = dict(idx_two_regs("NCT02444988", "NCT02547779", "29485925"),
               study={"NCT02444988": {"acronym": "ALPHA"}, "NCT02547779": {"acronym": "BETA-ED"}})
    r = kt.resolve_unit(unit("Semler [15]", [{"pmid": "29485925"}]), None, idx, None, our_fams={"NCT02547779"})
    assert r["ncts"] == []


def test_chain3_acronym_ref_applies_the_same_paper_registration_rules(monkeypatch):
    # (synthetic) 'Semler (ALPHA trial)' reaches PMID 29485925 through the comparator's reference naming ALPHA (chain 3), not a
    # cited PMID; the PMID -> NCT step there must apply the same full-list + label-acronym rules
    monkeypatch.setattr(kt, "DATABANK", {"29485925": {"databank": ["NCT02444988", "NCT02547779"], "abstract": []}})
    idx = dict(idx_two_regs("NCT02444988", "NCT02547779", "29485925"),
               study={"NCT02444988": {"acronym": "ALPHA"}, "NCT02547779": {"acronym": "BETA-ED"}})
    parsed = {"refs": {"CR15": {"rid": "CR15", "label": "15", "ordinal": 15, "pmid": "29485925", "year": "2018",
                                "first_author": "Semler", "title": "Balanced crystalloids versus saline",
                                "text": "Semler MW. Balanced crystalloids versus saline in critically ill adults "
                                        "(ALPHA). N Engl J Med 2018."}}}
    u = unit("Semler (ALPHA trial)", [])
    u["layout"] = "text"
    r = kt.resolve_unit(u, parsed, idx, None)
    assert r["ncts"] == ["NCT02444988"]
    assert "pmid_nct_paper_lists_several_label_acronym:NCT02444988" in r["basis"]


def test_negative_real_smart_two_registrations_stay_refused(monkeypatch):
    # REAL: SMART is registered twice in AACT (NCT02444988 SMART-MED, NCT02547779 SMART-SURG) and its NEJM record
    # (PMID 29485925) lists both. The label 'SMART' names neither registration's acronym exactly: no single NCT.
    monkeypatch.setattr(kt, "DATABANK", {"29485925": {"databank": ["NCT02444988", "NCT02547779"], "abstract": []}})
    idx = dict(idx_two_regs("NCT02444988", "NCT02547779", "29485925"),
               study={"NCT02444988": {"acronym": "SMART-MED"}, "NCT02547779": {"acronym": "SMART-SURG"}})
    r = kt.resolve_unit(unit("Semler (SMART trial)", [{"pmid": "29485925"}]), None, idx, None)
    assert r["ncts"] == []
    assert "pmid_nct_paper_lists_several:NCT02444988,NCT02547779" in r["basis"]


def test_cache_save_is_atomic_and_keeps_a_concurrent_writers_entries(tmp_path):
    import json as _json
    cp = str(tmp_path / "c.json")
    kt._save_cache(cp, {"a": 1})
    # another process adds 'b' after we loaded our copy; our save must not drop it, and ours wins on a shared key
    _json.dump({"a": 0, "b": 2}, open(cp, "w", encoding="utf-8"))
    kt._save_cache(cp, {"a": 1, "c": 3})
    assert _json.load(open(cp, encoding="utf-8")) == {"a": 1, "b": 2, "c": 3}
    assert not list(tmp_path.glob("*.tmp"))
