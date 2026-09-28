"""V1.1 discovery recall test case (noac-vs-warfarin-af-stroke): J-ROCKET AF (NCT00494871; PMID 22664783), a randomised
rivaroxaban-vs-warfarin AF trial that the registered UID enumeration of four pivotal reports can never retrieve.
Held run: evidence/discovery/noac-vs-warfarin-af-stroke/run/."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(ROOT, "evidence", "discovery", "noac-vs-warfarin-af-stroke", "run")


def _fetch():
    return json.load(open(os.path.join(RUN, "recall_fetch.json"), encoding="utf-8"))


def test_the_registered_uid_queries_miss_j_rocket_af_and_a_concept_query_finds_it():
    d = _fetch()
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    assert reg == {"19717844", "21830957", "21870978", "24251359"}
    for pmid in ("22664783", "23229461"):
        assert pmid not in reg and pmid in d["broad_pmids"], pmid


def test_the_named_records_are_j_rocket_af():
    recs = {str(r["id"]): r for r in _fetch()["named_records"]}
    assert "J-ROCKET AF" in recs["22664783"]["title"] and recs["22664783"]["nct"] == "NCT00494871"
    assert recs["23229461"]["nct"] == "NCT00494871"          # a subanalysis: a report of the SAME trial


def test_the_served_retrieval_ran_only_the_uid_enumeration():
    # the declared registry-first query has no execution record behind the served records; run now it reaches the
    # primary report (not the subanalysis), and the drug-specific CT.gov query ('edoxaban warfarin') does not
    d = _fetch()
    assert {x["kind"] for x in d["served_ledger_sources"]} == {"PUBMED_PMID_ENUMERATION", "LEGACY_UNRECORDED"}
    assert d["seed_comparator_refs"] is False
    assert "22664783" in d["registry_first"]["pmids"] and "23229461" not in d["registry_first"]["pmids"]
    assert "NCT00494871" not in d["ctgov"]["ncts"]
