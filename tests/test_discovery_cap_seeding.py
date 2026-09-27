"""V1.1 discovery, corticosteroids-cap-mortality: is comparator-reference seeding safe to re-enable?

The protocol disabled seeding because "the fixed NCT deduplication rule can let later secondary/subgroup reports
replace the original trial report". These plants use the REAL CAPE COD record (PMID 36942789, NCT02517489) and a
synthetic same-NCT report, and compare the production dedup (harness.pipeline._dedup) with V1.1 family linking
(evidence/discovery/glp1-ra-mace-t2d/screen.py trials()). The seeding run itself is
evidence/discovery/corticosteroids-cap-mortality/seeding_test.py (results under run/)."""
import copy
import importlib.util
import json
import os

from harness import pipeline

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAP = "corticosteroids-cap-mortality"
spec = importlib.util.spec_from_file_location("disc_screen", os.path.join(ROOT, "evidence", "discovery", "glp1-ra-mace-t2d", "screen.py"))
disc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(disc)


def _capecod():
    b = json.load(open(os.path.join(ROOT, "cache", CAP, "records.json"), encoding="utf-8"))
    return next(r for r in b["records"] if str(r["id"]) == "36942789")


def _synthetic(year, title):
    r = copy.deepcopy(_capecod())
    r.update(id="99000001", year=str(year), title=title, doi="10.0000/synthetic")
    return r


def _pub(r):
    return {"id": str(r["id"]), "databank_ncts": [r["nct"]], "abstract_ncts": [], "nct": r["nct"]}


def _survivors(recs):
    return {str(r["id"]) for r in pipeline._dedup({"records": recs, "ctgov": []})}


def _family(recs, pid):
    tr, _, _ = disc.trials([_pub(r) for r in recs], [{"id": "NCT02517489", "reference_pmids": [], "reference_types": {}}], [])
    return next(set(t["members"]) for t in tr if f"PMID:{pid}" in t["members"])


def test_PLANT_a_later_subgroup_report_no_longer_replaces_the_primary_under_the_current_dedup():
    sub = _synthetic(2025, "Hydrocortisone in severe community-acquired pneumonia: a prespecified subgroup analysis.")
    assert _survivors([_capecod(), sub]) == {"36942789"}          # earliest-year tie-break: the primary survives


def test_PLANT_an_earlier_same_NCT_RCT_report_DOES_displace_the_primary_under_the_NCT_dedup_but_not_under_families():
    early = _synthetic(2021, "Hydrocortisone in severe community-acquired pneumonia: pilot randomised phase.")
    assert _survivors([_capecod(), early]) == {"99000001"}        # the residual defect of one-record-per-NCT
    fam = _family([_capecod(), early], "36942789")
    assert {"PMID:36942789", "PMID:99000001", "NCT:NCT02517489"} <= fam   # family linking keeps both; nothing replaced


def test_the_seeding_run_moved_no_watched_report():
    res = json.load(open(os.path.join(ROOT, "evidence", "discovery", CAP, "run", "SEEDING_RESULT_crossref.json"), encoding="utf-8"))
    assert res["seeded_pmids"] == 30 and res["new_records"] == 21
    assert res["A_production_dedup"]["displaced"] == [] and res["B_family_linking"]["moved"] == []
    prod = json.load(open(os.path.join(ROOT, "evidence", "discovery", CAP, "run", "seed_refs.json"), encoding="utf-8"))
    assert prod["pmids"] == []                                   # PubMed holds no reference links for 38128217
