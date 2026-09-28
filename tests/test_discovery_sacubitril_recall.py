"""V1.1 discovery recall test case (sacubitril-valsartan-hfref): LIFE (NCT02816736; PMID 34730769), a randomised
sacubitril/valsartan-vs-valsartan trial in advanced HFrEF that the registered PARADIGM-HF-seeded queries and the CT.gov
query never retrieve. Held run: evidence/discovery/sacubitril-valsartan-hfref/run/."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(ROOT, "evidence", "discovery", "sacubitril-valsartan-hfref", "run")


def _fetch():
    return json.load(open(os.path.join(RUN, "recall_fetch.json"), encoding="utf-8"))


def test_the_registered_queries_and_ctgov_miss_life_and_a_concept_query_finds_it():
    d = _fetch()
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    assert not {"34730769", "32641226", "35772853"} & reg
    assert "NCT02816736" not in d["ctgov"]["ncts"]
    assert "34730769" in d["broad_pmids"]


def test_the_named_records_are_reports_of_the_same_trial():
    recs = {str(r["id"]): r for r in _fetch()["named_records"]}
    assert {r["nct"] for r in recs.values()} == {"NCT02816736"}
    assert "Randomized Controlled Trial" in recs["34730769"]["pubtypes"]


def test_a_biomarker_primary_endpoint_is_not_the_absence_of_clinical_events():
    # LIFE's primary endpoint is NT-proBNP; its own report still states a clinical-event composite and harms by arm
    a = {str(r["id"]): r for r in _fetch()["named_records"]}["34730769"]["abstract"]
    assert "N-terminal pro-brain natriuretic peptide (NT-proBNP)" in a
    assert "free from heart failure events" in a
    assert "hyperkalemia in the sacubitril/valsartan arm (28 [17%] vs 15 [9%]" in a
