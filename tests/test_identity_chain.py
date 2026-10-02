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
              "1|NCT01589367|15155550|BACKGROUND|Baillargeon JP, et al. Metformin therapy in PCOS. Fertil Steril. "
              "2004 Oct;82(4):893-902.\n"
              "2|NCT00068861|17287476|RESULT|Legro RS, et al. Clomiphene, metformin, or both for infertility. "
              "N Engl J Med. 2007 Feb 8;356(6):551-66.\n",
              studies="NCT01589367|INTERVENTIONAL||Letrozole plus metformin|x\nNCT00068861|INTERVENTIONAL||PPCOS|x\n",
              interventions="1|NCT01589367|DRUG|metformin|\n2|NCT00068861|DRUG|metformin|\n")
    r = ic.resolve([("metformin-pcos-ovulation", "Baillargeon 2004", ["metformin"]),
                    ("metformin-pcos-ovulation", "Legro 2007", ["metformin"])], d)
    assert r[("metformin-pcos-ovulation", "Baillargeon 2004")]["state"] == "NOT_FOUND"
    assert r[("metformin-pcos-ovulation", "Legro 2007")]["nct"] == "NCT00068861"


def test_author_year_reads_the_publication_year_not_a_year_in_the_title(tmp_path):
    d = _snap(tmp_path, "1|NCT9|111|RESULT|Smith J. Metformin in 2007 patients. Journal. 2015 May;10(1):1-9.\n",
              studies="NCT9|INTERVENTIONAL||Metformin trial|x\n", interventions="1|NCT9|DRUG|metformin|\n")
    r = ic.resolve([("t", "Smith 2007", ["metformin"])], d)
    assert r[("t", "Smith 2007")]["state"] == "NOT_FOUND"
    assert ic.resolve([("t", "Smith 2015", ["metformin"])], d)[("t", "Smith 2015")]["nct"] == "NCT9"


def test_an_acronym_and_an_author_year_that_disagree_are_ambiguous(tmp_path):
    d = _snap(tmp_path, "1|NCT1|111|RESULT|Smith J. A trial. J Med. 2007 Jan;1:1.\n",
              studies="NCT1|INTERVENTIONAL||Metformin A|x\nNCT2|INTERVENTIONAL|SMART|Metformin B|x\n",
              interventions="1|NCT1|DRUG|metformin|\n2|NCT2|DRUG|metformin|\n")
    r = ic.resolve([("t", "Smith 2007 (SMART)", ["metformin"])], d)[("t", "Smith 2007 (SMART)")]
    assert r["state"] == "AMBIGUOUS" and r["basis"] == "ACRONYM_VS_AUTHOR_YEAR_CONFLICT"
