"""Plants (E1, 11 Oct): coverage is computed from the held bytes, never from a file's presence. Each named case was
held as 'full text' and read as such by the absence classifier and the harms rung ('held full text: CHECKED')."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import source_coverage as sc  # noqa: E402


def _lab(rel):
    return sc.label_document(open(os.path.join(ROOT, rel), "rb").read())


def test_PLANT_pmc_no_download_responses_are_stubs():
    for rel in ("cache/dpp4-mace-t2d/ft_30418475.txt",                 # r6: listed as held by the certificate
                "cache/metformin-pcos-ovulation/ft_16769748.txt",      # r27-03 Moll: 'full text checked'
                "cache/omega3-cardiovascular-events/ft_33190147.txt"):  # r28 STRENGTH
        d = _lab(rel)
        assert (d["label"], d["reason"], d["bundle_coverage"]) == ("STUB", "PMC_NO_DOWNLOAD", None), rel


def test_PLANT_a_portal_page_is_metadata_not_a_comparator_full_text():
    d = _lab("cache/sglt2-ckd-progression/comparator_fulltext.txt")    # r17-03: a Pure repository page + RIS block
    assert d["label"] == "METADATA" and d["reason"] == "PORTAL_PAGE"


def test_a_self_declared_excerpt_keeps_its_own_label():
    d = _lab("cache/spironolactone-hfref-mortality/ft_28824029.txt")
    assert d["label"] == "EXCERPT" and d["reason"] == "SELF_DECLARED:EXCERPT_ONLY"


def test_real_full_texts_stay_full_texts():
    # flattened JATS prose (no line breaks) and a PMC XML with a body
    for rel in ("cache/balanced-crystalloids-vs-saline-mortality/comparator_fulltext.txt",
                "cache/noac-vs-warfarin-af-stroke/comparator_fulltext.txt",
                "cache/corticosteroids-cap-mortality/ft_35723686.txt"):
        assert _lab(rel)["label"] == "FULLTEXT", rel


def test_synthetic_edges():
    assert sc.label_document(b"<?xml version='1.0'?><article><front><abstract>x</abstract></front></article>")["reason"] == "XML_NO_BODY"
    assert sc.label_document(b"")["label"] == "STUB"
    assert sc.label_document(b"<article><front/><body>  </body></article>")["reason"] == "XML_EMPTY_BODY"
    # a short body is still the whole body (a letter to the editor): length is never coverage
    assert sc.label_document(b"<article><front/><body>Dear editor, I read with interest.</body></article>")["label"] == "FULLTEXT"
    short = "Background ... Methods: x. Results: y. Discussion: z."
    assert sc.label_document(short)["label"] == "EXCERPT"            # an abstract's labels are not an article body


def test_absence_needs_a_complete_object():
    assert not sc.absence_licensed(["STUB", "METADATA", "EXCERPT"])
    assert sc.absence_licensed(["STUB", "FULL_ABSTRACT"]) and sc.absence_licensed(["FULLTEXT"])


def test_abstract_label_uses_the_bundle_preservation_record():
    units = [{"index": 0, "label": "BACKGROUND", "text": "A is studied."},
             {"index": 1, "label": "RESULTS", "text": "HHF 20/2092 v 33/2100, HR 0.60 (0.35-1.05)."}]
    assert sc.abstract_label("BACKGROUND: A is studied. RESULTS: HHF 20/2092 v 33/2100, HR 0.60 (0.35-1.05).", units)["label"] == "FULL_ABSTRACT"
    ab = sc.abstract_label("BACKGROUND: A is studied.", units)
    assert ab["label"] == "EXCERPT" and ab["reason"].startswith("UNITS_MISSING:1/2")
    assert sc.abstract_label("x", None)["bundle_coverage"] == "UNKNOWN_COMPLETENESS"


def _acq_case(slug, pmid):
    import glob
    import json
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import build_bundle
    rec = next(r for r in json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))["records"]
               if str(r["id"]) == pmid)
    xml = glob.glob(os.path.join(ROOT, "registry", "source_acquisitions", slug, "pubmed_efetch_*", f"{pmid}.xml"))
    return rec["abstract"], build_bundle.abstract_units(open(sorted(xml)[-1], "rb").read())


def test_PLANT_the_census_abridgements_are_excerpts():
    for slug, pmid in (("dpp4-mace-t2d", "28893244"), ("glp1-ra-mace-t2d", "40162642")):   # OMNeON, SOUL
        held, units = _acq_case(slug, pmid)
        lab = sc.abstract_label(held, units)
        assert lab["label"] == "EXCERPT" and lab["reason"].startswith("UNITS_MISSING:4/4"), (slug, lab["reason"])


def test_unicode_spaces_in_a_pubmed_label_are_whitespace_not_missing_text():
    held, units = _acq_case("spironolactone-hfref-mortality", "28824029")      # 'METHODS\u2004AND\u2004RESULTS'
    assert sc.abstract_label(held, units)["label"] == "FULL_ABSTRACT"


def test_a_revised_pubmed_record_is_a_complete_earlier_version_not_an_abridgement():
    for slug, pmid in (("spironolactone-hfref-mortality", "41955577"), ("semaglutide-obesity-weight", "42610271")):
        held, units = _acq_case(slug, pmid)
        lab = sc.abstract_label(held, units)
        assert lab["label"] == "FULL_ABSTRACT" and lab["version_differs"] is True, (slug, lab)
