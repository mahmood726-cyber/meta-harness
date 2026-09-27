"""V1.0.1 funding extraction, from the codex funding-audit lanes (FUND-F1/F2): 12 industry ties the full-text reader
missed, each traced to a root cause. Every plant is SYNTHETIC text shaped like the missed statement, never a corpus page,
so a later edit to a held text cannot retire it.

Root causes: a fixed reach cap (the 5th funding sentence and 4th supply sentence were dropped); a sentence splitter
that broke 'Co. Ltd.' and 'F. Hoffmann'; an industry marker ('Inc\\.' + \\b) that could never match at a name's end;
an author-contribution line ('Obtained funding: S.') read as the funding statement; 'financed by' and
'Funding/Support:' unrecognised; passive supply phrasings ('provided free of charge for this study by'), active
supply with a donor list or a parenthetical ('BASF (fish oil) donated'), and a manufacturer named only by role.
With every sentence read, author disclosures must not become funders.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import funding as f  # noqa: E402
from harness import funding_typed as ft  # noqa: E402


def _b(*sents):
    return ft.build("T", "", "<article><p>" + " ".join(sents) + "</p></article>", [], [])


def _industry(b):
    return {x.get("name") or x.get("supplier") for x in b["funders"] + b["material_support"] if x["class"] == "INDUSTRY"}


@pytest.mark.parametrize("sents,who", [
    (("Funding/Support: The study was financed by CSL Vifor (an unrestricted grant and free provision of study drug).",),
     "CSL Vifor"),
    (("Tocilizumab was provided free of charge for this study by Roche.",), "Roche"),
    (("Roche donated TCZ in unrestricted grant, and the ministry funded the rest.",), "Roche"),
    (("Novo Nordisk A/S provided the investigational drug and placebo.",), "Novo Nordisk A/S"),
    (("AbbVie contributed some supplies of the comparator for use in the trial.",), "AbbVie"),
    (("The study was funded by a grant-in-aid of research from Zeta K+ International Inc.",), None),
    (("FUNDING This study was funded by Schwabe Farma Iberica.",), "Schwabe Farma Iberica"),
    (("Funding This study was funded by Yakult Honsha Co. Ltd.",), "Yakult Honsha Co. Ltd"),
    (("Funding This trial was supported by F. Hoffmann-La Roche Ltd.",), "F. Hoffmann-La Roche Ltd"),
    (("The study products and placebo will be manufactured and supplied by Acmegaia (Lund, Sweden) free of charge.",),
     "Acmegaia"),
    (("LA85 was provided by Wecare Probiotics Co. Ltd. (Jiangsu, China).",), "Wecare Probiotics Co. Ltd."),
])
def test_PLANT_each_missed_phrasing_now_names_industry(sents, who):
    b = _b(*sents)
    assert b["industry_tie"] == ft.PRESENT, b["industry_tie_basis"]
    if who:
        assert who in _industry(b), _industry(b)


def test_PLANT_a_donor_list_is_classified_on_the_whole_subject():
    b = _b("Pharmavite LLC of Northridge, California and Pronova BioPharma of Norway and BASF (fish oil) donated the "
           "study agents and matching placebos.")
    assert b["industry_tie"] == ft.PRESENT and any("Pharmavite LLC" in n for n in _industry(b))


def test_PLANT_an_author_contribution_line_is_not_the_funding_statement():
    st = ft.statement("<p>Obtained funding: Hermine, Mariette. Funding: HABF, BV. Study supervision: Smith.</p>")
    assert st["funding_sentences"] == []


def test_PLANT_reach_is_not_capped():
    noise = [f"Recruitment in region {i} was supported by local staff." for i in range(8)]
    b = _b(*noise, "Funding The trial is sponsored by Boehringer Ingelheim.")
    assert b["industry_tie"] == ft.PRESENT and "Boehringer Ingelheim" in _industry(b)


def test_PLANT_a_section_heading_splits_a_disclosure_from_the_funding_statement():
    st = ft.statement("<p>Conflict of Interest Disclosures: Dr A reported grants and nonfinancial support from Winclove "
                      "B.V. Funding/Support: Both the placebo and the probiotic were manufactured and provided for study "
                      "purposes by Winclove Probiotics B.V.</p>")
    assert any(s.startswith("Funding/Support:") for s in st["funding_sentences"])


@pytest.mark.parametrize("sent", [
    "LKD receives a research grant from Pfizer, Roche, and Boehringer Ingelheim.",
    "OB received grants from AstraZeneca, Bayer and Novartis.",
    "Dr Smith reported personal fees from Bayer outside the submitted work.",
    "Ruschitzka reported travel grants from AstraZeneca.",
    "Heike Doe reports equipment, drugs, or supplies was provided by Roche.",
])
def test_PLANT_author_disclosures_never_become_trial_funders(sent):
    b = _b("Funding: This trial was funded by the National Institute for Health Research.", sent)
    assert b["industry_tie"] != ft.PRESENT, b["industry_tie_basis"]


# ---------------------------------------------------------------- COI-C1 lane (234 candidate sentences labelled)
@pytest.mark.parametrize("sent", [
    "Semler was supported in part by grants from the National Heart, Lung, and Blood Institute (HL087738).",
    "WGH was funded by an MRC Clinician Scientist Award (MR/R007764/1).",
    "JSN and JEP are supported by the Instituto de Salud Carlos III.",
    "Competing interests Stephen Doe has undertaken research supported by Acme Ltd and received funding from Zed Inc.",
])
def test_PLANT_one_authors_support_or_a_disclosure_heading_is_not_trial_funding(sent):
    st = ft.statement("<p>" + sent + "</p>")
    assert st["funding_sentences"] == [] and st["supply_sentences"] == []


def test_PLANT_a_disclosure_heading_splits_from_the_preceding_sentence_without_a_period():
    st = ft.statement("<p>TSC = Trial Steering Committee Competing interests Jane Doe received funding from Acme Ltd.</p>")
    assert st["funding_sentences"] == []


@pytest.mark.parametrize("sent", [
    "Funding was provided by the Department of Veterans Affairs, Cooperative Studies Program.",
    "Additional support was provided by the University of Maryland School of Medicine.",
])
def test_PLANT_provided_by_lead_ins_are_funding_statements(sent):
    assert ft.statement("<p>" + sent + "</p>")["funding_sentences"]


def test_PLANT_writing_support_provided_by_is_not_a_funding_statement():
    assert not ft.statement("<p>Medical writing support was provided by Jane Doe of Apollo.</p>")["funding_sentences"]


def test_PLANT_an_authors_company_role_blocks_ABSENT():
    base = ("Funding: This trial is funded by the National Institute for Health Research Health Technology Assessment "
            "Programme.")
    assert _b(base)["industry_tie"] == ft.ABSENT
    b = _b(base, "Sue Doe is a Director of Acmetech Ltd. UK.")
    assert b["industry_tie"] == ft.NOT_ESTABLISHED and "company role" in b["industry_tie_basis"]


# ---------------------------------------------------------------- FUND-F3 lane (222 rows without full text)
def test_PLANT_a_registry_non_industry_class_is_not_overruled_by_a_bare_company_suffix():
    b = ft.build("T", "", "", [], [{"name": "Tristate Health Inc.", "agency_class": "OTHER", "lead_or_collaborator": "lead"}])
    f0 = b["funders"][0]
    assert f0["class"] == "UNCLASSIFIED" and b["industry_tie"] != ft.PRESENT
    b = ft.build("T", "", "", [], [{"name": "Pfizer Inc.", "agency_class": "OTHER", "lead_or_collaborator": "lead"}])
    assert b["industry_tie"] == ft.PRESENT                       # a named company still decides


def test_PLANT_a_commercially_named_product_is_not_a_tie():
    # buying a branded product is not support; only a named donation/supply/funding is
    b = _b("Patients were given either tablet melatonin 3 mg (Meloset from Aristo pharmaceuticals) or placebo by our "
           "pharmacist.", "Financial support and sponsorship Nil.")
    assert b["industry_tie"] != ft.PRESENT


@pytest.mark.parametrize("name,industry", [
    ("Zeta K+ International Inc.", True), ("Schwabe Farma Iberica", True), ("Winclove Probiotics B.V", True),
    ("Novo Nordisk A/S", True), ("Incheon National University", False), ("Farmacia Hospital Central", False),
])
def test_PLANT_industry_name_markers(name, industry):
    assert bool(f._INDUSTRY.search(name)) is industry


def test_PLANT_company_suffix_and_initial_do_not_end_the_funder_list_but_a_real_sentence_end_does():
    assert f._split_sponsors("This study was funded by Yakult Honsha Co. Ltd. Role of the funder") == ["Yakult Honsha Co. Ltd"]
    assert f._split_sponsors("Funded by F. Hoffmann-La Roche and the Department of Health; ClinicalTrials") == [
        "F. Hoffmann-La Roche", "Department of Health"]
    assert f._split_sponsors("sponsored by Novo Nordisk A/S. 1 INTRODUCTION Because") == ["Novo Nordisk A/S"]
