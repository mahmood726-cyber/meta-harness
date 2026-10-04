"""shown_pmid must not fall back to a paper its own main-report test rejects: ODYSSEY FH II (NCT01709500) was shown the
2014 'design and rationale of the ODYSSEY FH studies' (24842558) because the JOINT results paper 'ODYSSEY FH I and FH
II: 78 week results' (26330422) links only FH I's NCT in pubmed_ncts.json (one NCT per PMID). Corpus: 1 of 307 changes."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import k_gap_identity_reader2 as r2  # noqa: E402

RCT = ["Journal Article", "Randomized Controlled Trial"]
PT = {"24842558": {"title": "Efficacy and safety of alirocumab ...: design and rationale of the ODYSSEY FH studies.",
                   "pubtypes": RCT},
      "26330422": {"title": "ODYSSEY FH I and FH II: 78 week results with alirocumab treatment in 735 patients",
                   "pubtypes": RCT}}
NC = {"24842558": "NCT01623115", "26330422": "NCT01623115"}


def _with(monkeypatch, pt, nc=NC, store=None):
    monkeypatch.setattr(r2, "_STORE", store or {})
    monkeypatch.setattr(r2, "_PM", (nc, pt))


def test_a_joint_report_beats_a_design_paper(monkeypatch):
    _with(monkeypatch, PT)
    assert r2.shown_pmid({"pmids": ["24842558", "26330422"], "ncts": ["NCT01709500"]}) == "26330422"


def test_an_uncached_first_paper_is_kept(monkeypatch):
    # LONG TERM 25773378 has no cached title: unknown is not 'design paper', the old fallback stands
    _with(monkeypatch, {"28391886": {"title": "Efficacy and safety of alirocumab", "pubtypes": RCT}}, nc={})
    assert r2.shown_pmid({"pmids": ["25773378", "28391886"], "ncts": ["NCT01507831"]}) == "25773378"


def test_a_result_typed_design_paper_yields_to_a_result_typed_report(monkeypatch):
    store = {"24842558": [("NCT01709500", "RESULT")], "26330422": [("NCT01709500", "RESULT")]}
    _with(monkeypatch, PT, store=store)
    assert r2.shown_pmid({"pmids": ["24842558", "26330422"], "ncts": ["NCT01709500"]}) == "26330422"
