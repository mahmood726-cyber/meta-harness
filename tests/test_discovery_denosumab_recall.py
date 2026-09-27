"""V1.1 discovery recall test case (denosumab-vertebral-fracture): the registered five-term TITLE query misses
BMD-focused trials that report fractures. Held run: evidence/discovery/denosumab-vertebral-fracture/run/."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(ROOT, "evidence", "discovery", "denosumab-vertebral-fracture", "run")


def _fetch():
    return json.load(open(os.path.join(RUN, "recall_fetch.json"), encoding="utf-8"))


def test_the_registered_title_query_misses_the_BMD_titled_trial_and_a_fracture_primary_trial():
    d = _fetch()
    for pmid in ("27189284", "24646104"):          # Koh 2016 (NCT01457950); DIRECT
        assert pmid not in d["registered_pmids"] and pmid in d["broad_pmids"], pmid


def test_Koh_2016_reports_no_fracture_in_its_abstract_so_its_fracture_data_must_come_through_its_registry_record():
    rec = next(r for r in _fetch()["records_broad_only"] if str(r["id"]) == "27189284")
    assert "fractur" not in (rec.get("abstract") or "").lower()
    assert "bone mineral density" in rec["abstract"].lower()


def test_DIRECT_has_vertebral_fracture_as_its_primary_endpoint():
    rec = next(r for r in _fetch()["records_broad_only"] if str(r["id"]) == "24646104")
    assert "primary endpoint was the 24-month incidence of new or worsening vertebral fracture" in rec["abstract"]
