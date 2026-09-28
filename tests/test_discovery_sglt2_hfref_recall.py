"""V1.1 discovery recall test (sglt2-hfref-hosp-cvdeath): DEFINE-HF (NCT02653482, PMID 31524498) and EMPERIAL-Reduced
(PMID 33351892), randomised placebo-controlled trials of the protocol's drugs in HFrEF, absent from our inventory.
Held run: evidence/discovery/sglt2-hfref-hosp-cvdeath/run/."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(ROOT, "evidence", "discovery", "sglt2-hfref-hosp-cvdeath", "run")


def _fetch():
    return json.load(open(os.path.join(RUN, "recall_fetch.json"), encoding="utf-8"))


def test_the_registered_uid_enumeration_misses_both_and_a_concept_query_finds_both():
    d = _fetch()
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    assert reg == {"31535829", "32865377", "35112512"}
    for pmid in ("31524498", "33351892"):
        assert pmid not in reg and pmid in d["broad_pmids"], pmid


def test_the_declared_registry_queries_reach_define_hf_but_not_emperial_reduced():
    # run now, the registry-first query reaches DEFINE-HF (a registered trial) but not EMPERIAL-Reduced, whose PubMed
    # record carries no registration; the drug-class CT.gov query ('SGLT2 inhibitor') reaches neither
    d = _fetch()
    assert "31524498" in d["registry_first"]["pmids"] and "33351892" not in d["registry_first"]["pmids"]
    assert "NCT02653482" not in d["ctgov"]["ncts"]


def test_define_hf_is_not_typed_rct_by_pubmed_so_an_rct_filter_would_miss_it():
    recs = {str(r["id"]): r for r in _fetch()["named_records"]}
    assert "Randomized Controlled Trial" not in recs["31524498"]["pubtypes"] and recs["31524498"]["nct"] == "NCT02653482"
    assert "Randomized Controlled Trial" in recs["33351892"]["pubtypes"]
