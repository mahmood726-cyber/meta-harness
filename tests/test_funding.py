"""Per-trial funding / COI disclosure (ME-32). Source-anchored classification, verbatim span, and
refuse-on-absence: a trial with no funding statement is reported 'not stated in source', never guessed.
An industry/public marker classifies only when it sits in the FUNDING sentence, so a company named in an
unrelated sentence does not mislabel the trial."""
import os
import sys
import json
import subprocess
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import funding  # noqa: E402
from harness import error_library as EL  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BASE = "ad5e7c66"


def _git_show_json(path):
    raw = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT, text=True, encoding="utf-8")
    return json.loads(raw)


def _cache_records(slug):
    return json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8"))


def _rec_by_id(records):
    return {str(row["id"]): row for row in (records.get("records") or []) + (records.get("ctgov") or [])}


def _rescan(slug, review):
    records = _cache_records(slug)
    return funding.scan_pooled(review, _rec_by_id(records), records.get("fulltext_by_pmid") or {})


def test_industry_funding_detected_from_statement():
    txt = "Background. This is an RCT. Funding: This study was funded by Novo Nordisk. Results were positive."
    d = funding.detect(txt)
    assert d and d["type"] == "industry"
    assert "Novo Nordisk" in d["span"]
    assert d["status"] == "stated_in_held_text"
    assert d["sponsor_class"] == "industry"
    assert "Novo Nordisk" in d["sponsors"]


def test_roles_are_source_backed_not_affiliation_inferred():
    txt = (
        "Funding: Pfizer sponsored, designed and performed the study, collected and analysed "
        "the data, and wrote the first draft. The authors included Pfizer employees."
    )
    d = funding.detect(txt)
    assert d["sponsor_class"] == "industry"
    assert {"design", "conduct", "data_collection", "analysis", "manuscript_writing"}.issubset(set(d["role"]))
    assert d.get("industry_authors_present") is True


def test_public_funding_detected():
    txt = "Methods... The trial was supported by a grant from the National Institutes of Health (NIH)."
    d = funding.detect(txt)
    assert d and d["type"] == "public/non-profit"


def test_mixed_funding():
    txt = "Funded by the Medical Research Council and Pfizer Inc., with additional academic support."
    d = funding.detect(txt)
    assert d and d["type"] == "mixed"


def test_no_statement_returns_none():
    assert funding.detect("A randomized trial of drug X versus placebo in adults. The primary outcome was met.") is None
    assert funding.detect("") is None


def test_registry_sponsor_second_source_recovers_abstract_silence():
    review = {"outcomes": [{"primary": True, "trials": [{"id": "PMID 1", "source": "NCT12345678"}]}]}
    rec = {"1": {"title": "Silent trial", "abstract": "No funding sentence.", "nct": "NCT12345678"}}
    registry = {
        "NCT12345678": {
            "sponsors": [
                {"agency_class": "INDUSTRY", "lead_or_collaborator": "lead", "name": "Boehringer Ingelheim"}
            ],
            "responsible_parties": [{"responsible_party_type": "SPONSOR", "organization": "Boehringer Ingelheim"}],
        }
    }
    out = funding.scan_pooled(review, rec, registry_by_nct=registry)
    assert out[0]["status"] == "stated_in_registry"
    assert out[0]["sponsor_class"] == "industry"
    assert out[0]["source_id"] == "registry:NCT12345678"
    assert "Boehringer Ingelheim" in out[0]["basis_span"]


def test_registry_vs_abstract_disagreement_keeps_both_sources_renderable():
    review = {"outcomes": [{"primary": True, "trials": [{"id": "PMID 1", "label": "T1"}]}]}
    rec = {"1": {"title": "T", "abstract": "Funding: National Institutes of Health.", "nct": "NCT12345678"}}
    registry = {
        "NCT12345678": {
            "sponsors": [
                {"agency_class": "INDUSTRY", "lead_or_collaborator": "lead", "name": "Janssen Research & Development"}
            ],
            "responsible_parties": [],
        }
    }
    row = funding.scan_pooled(review, rec, registry_by_nct=registry)[0]
    assert row["source_disagreement"] is True
    assert row["sponsor_class"] == "mixed"
    assert {src["source_id"] for src in row["sources"]} == {"abstract:PMID 1", "registry:NCT12345678"}


def test_prefix_j_emphasis_unknown_funding_row_is_recovered_from_registry():
    review = _git_show_json("docs/reviews/spironolactone-hfref-mortality/review.json")
    old = next(row for row in review["funding"] if row["id"] == "PMID 28824029")
    assert old["type"].startswith("not stated")
    after = _rescan("spironolactone-hfref-mortality", review)
    recovered = {row["id"]: row for row in funding.unknown_but_recovered(review["funding"], after)}
    assert recovered["PMID 28824029"]["sponsor_class"] == "industry"
    assert recovered["PMID 28824029"]["source_id"] == "registry:NCT01115855"
    assert any("Pfizer" in sponsor or "Viatris" in sponsor for sponsor in recovered["PMID 28824029"]["sponsors"])


def test_prefix_rely_unknown_funding_row_is_recovered_from_registry():
    review = _git_show_json("docs/reviews/noac-vs-warfarin-af-stroke/review.json")
    old = next(row for row in review["funding"] if row["id"] == "PMID 19717844")
    assert old["type"].startswith("not stated")
    after = _rescan("noac-vs-warfarin-af-stroke", review)
    recovered = {row["id"]: row for row in funding.unknown_but_recovered(review["funding"], after)}
    assert recovered["PMID 19717844"]["sponsor_class"] == "industry"
    assert recovered["PMID 19717844"]["source_id"] == "registry:NCT00262600"
    assert "Boehringer Ingelheim" in recovered["PMID 19717844"]["sponsors"]


def test_company_outside_funding_sentence_does_not_classify_as_industry():
    # A company named far from any funding anchor must NOT flip the classification to industry.
    txt = ("Pfizer manufactures the comparator tablet used in routine care. " + ("filler. " * 40)
           + "This work was supported by a grant from the National Institutes of Health.")
    d = funding.detect(txt)
    assert d and d["type"] == "public/non-profit", d


def test_scan_pooled_reports_not_stated_when_silent():
    review = {"outcomes": [{"primary": True, "trials": [{"id": "PMID 1"}, {"id": "PMID 2"}]}]}
    rec = {"1": {"title": "Trial one", "abstract": "supported by AstraZeneca."},
           "2": {"title": "Trial two", "abstract": "no funding statement here at all."}}
    out = funding.scan_pooled(review, rec)
    by = {f["id"]: f for f in out}
    assert by["PMID 1"]["type"] == "industry"
    # abstract-only scan: absence must be labelled as such, not as "independently funded"
    assert by["PMID 2"]["type"].startswith("not stated (abstract only")
    assert by["PMID 2"]["scanned"] == "abstract only"


def test_scan_depth_distinguishes_fulltext_silence_from_abstract_only():
    review = {"outcomes": [{"primary": True, "trials": [{"id": "PMID 5"}]}]}
    rec = {"5": {"title": "T", "abstract": "no funding line"}}
    # full text present and genuinely silent -> "not stated (full text scanned)"
    ft = {"5": "Full text with methods and results but no funding or COI statement anywhere."}
    out = funding.scan_pooled(review, rec, ft)
    assert out[0]["type"] == "not stated (full text scanned)" and out[0]["scanned"] == "full text"
    assert out[0]["status"] == "none_stated_in_held_text"
    assert out[0]["sponsor_class"] == "none_stated_in_held_text"
    # no full text -> abstract-only label
    out2 = funding.scan_pooled(review, rec)
    assert out2[0]["type"].startswith("not stated (abstract only") and out2[0]["scanned"] == "abstract only"


def test_industry_drug_supply_in_investigator_initiated_trial():
    # publicly funded / investigator-initiated but study drug donated by industry: surfaced, not lost
    txt = ("This investigator-initiated trial. The study drug and matching placebo were provided by "
           "Novartis. No other external funding was received.")
    d = funding.detect(txt)
    assert d is not None and "industry" in d["type"]


def test_drug_supply_note_on_publicly_funded_trial():
    txt = "This work was funded by the National Institutes of Health; study drug was supplied by Merck."
    d = funding.detect(txt)
    assert d["type"] == "public/non-profit"
    assert d.get("note") and "industry" in d["note"]


def test_funding_pointer_to_supplement_is_not_silence():
    txt = "Methods... Funding details are provided in the Supplementary Appendix."
    d = funding.detect(txt)
    assert d is not None and "supplement" in d["type"].lower()
    assert d["status"] == "in_source_not_held"


def test_scan_pooled_prefers_full_text():
    review = {"outcomes": [{"primary": True, "trials": [{"id": "PMID 9"}]}]}
    rec = {"9": {"title": "T", "abstract": "no funding line in abstract"}}
    ft = {"9": "Full text ... Funding: supported by a grant from the Wellcome Trust foundation."}
    out = funding.scan_pooled(review, rec, ft)
    assert out[0]["type"] == "public/non-profit" and out[0]["source"] == "full text"


def test_funding_source_anchor_detects_jupiter():
    # "PRIMARY FUNDING SOURCE: AstraZeneca" (JUPITER 20404379) was missed by the old "funding:" anchor
    # (no direct colon after "funding"); the "funding source:" anchor now catches it.
    d = funding.detect("PRIMARY FUNDING SOURCE: AstraZeneca.")
    assert d and d["type"] == "industry"


def test_ag_corporate_suffix_classifies_industry_but_not_bare_ag():
    # "Viollier AG" (a commercial company listed under FUNDING) makes a public+industry trial MIXED...
    d = funding.detect("FUNDING: Swiss National Science Foundation, Viollier AG, Bangerter Stiftung.")
    assert d and d["type"] == "mixed"
    # ...but a lower-case "ag" (e.g. an acronym) must NOT flip a publicly funded trial to industry.
    d2 = funding.detect("This work was supported by a grant from the ag research council at the university.")
    assert d2 and d2["type"] == "public/non-profit"


def test_me32_is_now_rendered_and_no_unchecked_remain():
    entry = next(e for e in EL.LIBRARY if e[0] == "ME-32")
    assert entry[2] == EL.RENDERED
    assert EL.not_checked() == [], f"unexpected NOT_CHECKED entries: {EL.not_checked()}"
    s = EL.summary()
    assert s.get("NOT_CHECKED", 0) == 0


def test_funding_fraction_excludes_unknown_from_denominator():
    """UNKNOWN funding must not be folded into the non-industry denominator (audit 23): the headline
    industry-funded fraction is over trials with KNOWN funding, and unknowns are reported separately."""
    import json
    import glob
    from harness import page
    checked = 0
    for f in glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    "docs", "reviews", "*", "review.json")):
        r = json.load(open(f, encoding="utf-8"))
        fund = r.get("funding") or []
        if not fund:
            continue
        html = page._riskofbias(r, False)
        n_known = sum(1 for x in fund if ((x.get("type") or "").startswith(("industry", "public", "non-profit"))
                                          or x.get("type") == "mixed" or x.get("note")))
        n_unknown = len(fund) - n_known
        if n_unknown:
            checked += 1
            # the page must never present the full pool as the industry denominator when unknowns exist
            assert f"of {len(fund)}</strong> pooled trials are industry" not in html, os.path.basename(os.path.dirname(f))
            assert f"of {n_known} known" in html and f"({n_unknown} unknown)" in html, os.path.basename(os.path.dirname(f))
    assert checked > 0, "no topic with unknown funding found — test would be vacuous"
