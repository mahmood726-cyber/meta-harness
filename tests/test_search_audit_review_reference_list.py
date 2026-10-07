"""Plants (search+screen audit, 2026-10-05): REVIEW_REFERENCE_LIST is a STANDING identification source for every topic.

Before: only the comparator's PubMed elink reference list ran by default (COMPARATOR_REFERENCES); Europe PMC's reference
list, forward citation of the comparator and other metas' reference lists ran only under the opt-in cite_chase (2 pages),
which no G1 topic set. All four tests fail on the old code (review_reference_list_sources / _epmc_linked_result absent)."""
from __future__ import annotations

from harness import fetch


def _kinds(cfg):
    return [k for k, *_ in fetch.review_reference_list_sources(cfg)]


def test_every_topic_with_a_comparator_gets_backward_and_forward_citation_by_default():
    assert _kinds({"comparator_pmid": "36050741"}) == ["COMPARATOR_REFERENCE_LIST", "EPMC_FORWARD_CITATION"]
    assert _kinds({}) == []                                         # no comparator: nothing to chase


def test_other_open_metas_add_backward_lists_at_most_two_never_the_comparator():
    k = _kinds({"comparator_pmid": "1", "reference_list_metas": ["1", "2", "3", "4"]})
    assert k == ["COMPARATOR_REFERENCE_LIST", "EPMC_FORWARD_CITATION", "EPMC_BACKWARD_CITATION",
                 "PUBMED_ELINK_BACKWARD_CITATION", "EPMC_BACKWARD_CITATION", "PUBMED_ELINK_BACKWARD_CITATION"]
    q = [q for _, q, *_ in fetch.review_reference_list_sources({"comparator_pmid": "1", "reference_list_metas": ["1", "2", "3"]})]
    assert not any(x.startswith("1 references (PubMed") for x in q) and any(x.startswith("3 references") for x in q)


def test_it_is_switched_off_only_explicitly():
    assert _kinds({"comparator_pmid": "1", "review_reference_list": False}) == []
    assert _kinds({"comparator_pmid": "1", "review_reference_list": None}) != []


def test_a_list_shorter_than_its_hitcount_is_recorded_and_only_pubmed_items_flow(monkeypatch):
    def get_json(url, params=None, **kw):
        return {"hitCount": 5, "referenceList": {"reference": [{"source": "MED", "id": "11"}, {"source": "PMC", "id": "x"},
                                                              {"source": "MED", "id": "12"}]}}
    monkeypatch.setattr(fetch.http, "get_json", get_json)
    monkeypatch.setattr(fetch.time, "sleep", lambda s: None)
    r = fetch._epmc_linked_result("1", "references")
    assert r["ids"] == ["11", "12"] and r["funnel"]["hits"] == 5 and r["funnel"]["fetched"] == 3
    assert r["funnel"]["cap"] == {"kind": "hard_hits_cap", "n": 3, "remainder": 2}
