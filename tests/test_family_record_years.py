"""Plant (5 Oct night, forest lane): a row's author-year joins a trial when the year is one of the trial record's OWN
dates (PubMed print-issue year OR its electronic-publication year). Metcovid (PMID 32785710) is 'Jeronimo 2021' by issue
date, epub 12 Aug 2020; two metas print it 'Jeronimo 2020' with identical counts and were FAMILY_NOT_RESOLVED. No
tolerance is added: any other year, or another surname, still does not join."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import secondary_meta_build as smb  # noqa: E402
from harness import secondary_meta as sm  # noqa: E402

OURS = [{"id": "PMID 32785710", "pmid": "32785710", "nct": "NCT04343729", "label": "Methylprednisolone as Adjunctive "
         "Therapy for Patients Hospitalized With COVID-19", "acronyms": ["MetCOVID"], "author_year": ("jeronimo", "2021"),
         "record_years": ["2020", "2021"]}]


def _row(label):
    return sm.SecondaryRow(meta_pmid="x", meta_doi="", location={}, source_digest="", provenance="T",
                           trial_label=label, measure="OR", outcome_definition="")


def test_epub_year_of_the_same_record_joins():
    fam = smb.family_of_factory(OURS)
    assert fam(_row("Jeronimo 2020 (3)")) == "PMID 32785710"
    assert fam(_row("Jeronimo,2020")) == "PMID 32785710"
    assert fam(_row("Jeronimo 2021")) == "PMID 32785710"


def test_no_tolerance_beyond_the_records_own_dates():
    fam = smb.family_of_factory(OURS)
    assert fam(_row("Jeronimo 2019")) is None
    assert fam(_row("Jeronimo 2022")) is None
    assert fam(_row("Horby 2020")) is None
    no_epub = [dict(OURS[0], record_years=None)]
    assert smb.family_of_factory(no_epub)(_row("Jeronimo 2020 (3)")) is None
