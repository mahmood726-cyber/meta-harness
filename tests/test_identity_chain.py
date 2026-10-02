"""PLANTS for kgap/identity_chain.py: the PMID<->NCT<->label chain from an AACT snapshot. Each trap was hit on real data
(3 Oct): a BACKGROUND citation resolved a trial to a LATER registration that merely cites it (CORE 2005 -> NCT04218786;
Baillargeon 2004 -> a 2012 letrozole trial), and a self-naming secondary analysis was taken as the trial's report."""
from kgap import identity_chain as ic


def _snap(tmp_path, refs, studies="", interventions=""):
    d = tmp_path / "snap"
    d.mkdir()
    (d / "study_references.txt").write_text("id|nct_id|pmid|reference_type|citation\n" + refs, encoding="utf-8")
    (d / "studies.txt").write_text("nct_id|study_type|acronym|brief_title|official_title\n" + studies, encoding="utf-8")
    (d / "interventions.txt").write_text("id|nct_id|intervention_type|name|description\n" + interventions,
                                         encoding="utf-8")
    return str(d)


def test_a_background_citation_never_links_a_paper_to_a_study(tmp_path):
    d = _snap(tmp_path, "1|NCT04218786|16186468|BACKGROUND|Imazio M. Colchicine ... 2005.\n"
                        "2|NCT00128427|20805112|RESULT|Imazio M. COPPS ... 2010.\n")
    assert ic.pmid_to_ncts(["16186468", "20805112"], d) == {"20805112": {"NCT00128427": "RESULT"}}


def test_the_report_is_the_earliest_result_reference_not_the_self_naming_one(tmp_path):
    d = _snap(tmp_path, "1|NCT02444988|31454263|RESULT|Brown RM. ... secondary analysis of SMART. 2019.\n"
                        "2|NCT02444988|29485925|RESULT|Semler MW. Balanced Crystalloids versus Saline. 2018.\n"
                        "3|NCT02444988|11111111|BACKGROUND|Old background paper.\n")
    assert ic.result_pmids(["NCT02444988"], d) == {"NCT02444988": ["29485925", "31454263"]}


def test_author_year_uses_only_the_studys_own_publications(tmp_path):
    d = _snap(tmp_path,
              "1|NCT01589367|15155550|BACKGROUND|Baillargeon JP, et al. Metformin therapy in PCOS. 2004.\n"
              "2|NCT00068861|17287476|RESULT|Legro RS, et al. Clomiphene, metformin, or both for infertility. 2007.\n",
              studies="NCT01589367|INTERVENTIONAL||Letrozole plus metformin|x\nNCT00068861|INTERVENTIONAL||PPCOS|x\n",
              interventions="1|NCT01589367|DRUG|metformin|\n2|NCT00068861|DRUG|metformin|\n")
    r = ic.resolve([("metformin-pcos-ovulation", "Baillargeon 2004", ["metformin"]),
                    ("metformin-pcos-ovulation", "Legro 2007", ["metformin"])], d)
    assert r[("metformin-pcos-ovulation", "Baillargeon 2004")]["state"] == "NOT_FOUND"
    assert r[("metformin-pcos-ovulation", "Legro 2007")]["nct"] == "NCT00068861"
