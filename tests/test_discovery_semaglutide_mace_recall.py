"""V1.1 discovery recall test (semaglutide-obesity-mace): the registered search is PMID/title anchors on SELECT alone
(plus the two reports those anchors happen to return: a letter and a SELECT subanalysis), with seeding off; no other
semaglutide RCT in adults with overweight or obesity without diabetes is reachable. Held run:
evidence/discovery/semaglutide-obesity-mace/run/."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(ROOT, "evidence", "discovery", "semaglutide-obesity-mace", "run")


def _fetch():
    return json.load(open(os.path.join(RUN, "recall_fetch.json"), encoding="utf-8"))


def test_the_registered_anchors_return_only_select_and_its_own_reports():
    d = _fetch()
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    assert reg == {"37952131", "38157134", "38907684"}          # SELECT, a letter on it, a SELECT HbA1c subanalysis
    assert d["seed_comparator_refs"] is False


def test_every_semaglutide_trial_the_comparator_includes_is_missed_by_the_anchors_and_found_by_a_concept_query():
    d = _fetch()
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    for pmid in ("33567185", "33625476", "33755728", "36216945", "35131037", "35015037", "37385278", "38330988"):
        assert pmid not in reg and pmid in d["broad_pmids"], pmid
