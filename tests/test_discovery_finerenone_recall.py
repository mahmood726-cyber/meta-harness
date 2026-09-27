"""V1.1 discovery recall test cases (finerenone-ckd-t2d-renal): FIVE-STAR (PMID 41351003) and CONFIDENCE (PMID 40470996)
are eligible-looking finerenone RCTs that the registered title+year reconstruction queries can never retrieve.
Held run: evidence/discovery/finerenone-ckd-t2d-renal/run/."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(ROOT, "evidence", "discovery", "finerenone-ckd-t2d-renal", "run")


def _fetch():
    return json.load(open(os.path.join(RUN, "recall_fetch.json"), encoding="utf-8"))


def test_the_registered_title_year_queries_miss_FIVE_STAR_and_CONFIDENCE():
    d = _fetch()
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    for pmid in ("41351003", "40470996"):
        assert pmid not in reg and pmid in d["broad_pmids"], pmid


def test_the_named_records_are_the_trials_they_are_named_as():
    recs = {str(r["id"]): r for r in _fetch()["named_records"]}
    assert "(FIVE-STAR)" in recs["41351003"]["title"] and "placebo-controlled" in recs["41351003"]["title"]
    assert recs["40470996"]["title"].startswith("Finerenone with Empagliflozin in Chronic Kidney Disease")


def test_every_registered_query_is_a_title_reconstruction_of_a_known_report():
    # each carries four [Title] terms and a publication year: known-item seeding, which cannot find a later trial
    for q in _fetch()["registered_queries"]:
        assert q.count("[Title]") >= 4 and "[Date - Publication]" in q
