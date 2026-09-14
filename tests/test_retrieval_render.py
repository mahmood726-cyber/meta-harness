from copy import deepcopy

from harness.page import render_page


ERROR_PHRASE = "attempted and FAILED — its zero is not observed, not absent"
ZERO_PHRASE = "ran; nothing matched"
REPLAY_SENTENCE = (
    "This page is a REPLAY of that snapshot: re-running from the protocol SHA regenerates "
    "it byte-for-byte. A live re-search is a separate, dated event (see Re-search below if present)."
)


def _core(with_retrieval=True, enumeration_only=False):
    retrieval = {
        "snapshot": {
            "records_sha256": "abcdef1234567890",
            "retrieved_utc": "2026-09-14",
            "mode": "REFRESH",
        },
        "record_cap": {"retrieved": 52, "retained": 40, "n": 40, "remainder": 12},
        "sources": [
            {
                "source_id": "pubmed#1",
                "kind": "PUBMED_CONCEPT_QUERY",
                "query": "condition AND drug <unsafe>",
                "run_utc": "2026-09-14",
                "state": "RAN_ERROR",
                "error": "HTTP 500 from PubMed",
                "discovery_capable": True,
                "funnel": {
                    "hits": None,
                    "fetched": 0,
                    "retained": 0,
                    "cap": {"kind": "hard_hits_cap", "n": 40, "remainder": 664},
                },
                "n_records": 0,
            },
            {
                "source_id": "epmc#1",
                "kind": "EUROPEPMC_QUERY",
                "query": "zero query",
                "run_utc": "2026-09-14",
                "state": "RAN_ZERO",
                "error": None,
                "discovery_capable": True,
                "funnel": {"hits": 0, "fetched": 0, "retained": 0, "cap": {"kind": "none", "n": None, "remainder": None}},
                "n_records": 0,
            },
            {
                "source_id": "pmid_enum#1",
                "kind": "PUBMED_PMID_ENUMERATION",
                "query": "111[uid]",
                "run_utc": "2026-09-14",
                "state": "RAN_OK",
                "error": None,
                "discovery_capable": False,
                "funnel": {"hits": 1, "fetched": 1, "retained": 1, "cap": {"kind": "none", "n": None, "remainder": None}},
                "n_records": 1,
            },
        ],
        "state_counts": {"RAN_OK": 1, "RAN_ZERO": 1, "RAN_ERROR": 1, "NOT_RUN": 0},
        "discovery_capable_sources": 2,
        "enumeration_only": False,
    }
    if enumeration_only:
        retrieval["sources"] = [
            {
                "source_id": "pmid_enum#1",
                "kind": "PUBMED_PMID_ENUMERATION",
                "query": "111[uid]",
                "run_utc": "2026-09-14",
                "state": "RAN_OK",
                "error": None,
                "discovery_capable": False,
                "funnel": {"hits": 1, "fetched": 1, "retained": 1, "cap": {"kind": "none", "n": None, "remainder": None}},
                "n_records": 1,
            }
        ]
        retrieval["state_counts"] = {"RAN_OK": 1, "RAN_ZERO": 0, "RAN_ERROR": 0, "NOT_RUN": 0}
        retrieval["discovery_capable_sources"] = 0
        retrieval["enumeration_only"] = True
    search = {
        "n_records": 2,
        "cache_ref": "cache/__plant_render__/records.json",
        "run_utc": "2026-09-14",
        "databases": ["PubMed"],
        "sources": [],
        "source_status": {},
    }
    if with_retrieval:
        search["retrieval"] = retrieval
    return {
        "slug": "__plant_render__",
        "title": "Synthetic retrieval render",
        "question": "Does retrieval render?",
        "method_declared": "M",
        "search": search,
        "screening": {
            "records": [
                {
                    "id": "ALPHA · 111",
                    "id_type": "pmid",
                    "decision": "include",
                    "rule_id": "INCLUDE",
                    "reason": "eligible",
                    "span": "randomized trial",
                    "found_by": ["pubmed#1", "epmc#1"],
                },
                {
                    "id": "222",
                    "id_type": "pmid",
                    "decision": "exclude",
                    "rule_id": "X1",
                    "reason": "not a trial",
                    "span": "review",
                    "found_by": ["UNRECORDED"],
                },
            ]
        },
        "outcomes": [
            {
                "name": "Primary",
                "kind": "efficacy",
                "primary": True,
                "estimand": "RR",
                "result": {"present": False, "reason": "synthetic no result"},
                "trials": [],
                "declared_absent_trials": [],
            }
        ],
    }


def test_retrieval_snapshot_renders_sha_date_and_replay_sentence():
    html = render_page(_core())
    assert "abcdef12" in html
    assert "2026-09-14" in html
    assert REPLAY_SENTENCE in html
    assert "live search run on that date" in html


def test_ran_error_row_has_error_wording_not_zero_wording():
    html = render_page(_core())
    error_row = next(row for row in html.split("<tr>") if "HTTP 500 from PubMed" in row)
    assert ERROR_PHRASE in error_row
    assert ZERO_PHRASE not in error_row
    assert ERROR_PHRASE != ZERO_PHRASE
    assert ZERO_PHRASE in html


def test_source_and_record_caps_show_remainders():
    html = render_page(_core())
    assert "hard_hits_cap" in html
    assert "remainder=664" in html
    assert "52 records retrieved, 40 retained after the record cap (n=40); 12 not screened" in html


def test_enumeration_only_block_only_for_all_enumeration_sources():
    enum_html = render_page(_core(enumeration_only=True))
    mixed_html = render_page(_core(enumeration_only=False))
    assert "No search was run for this topic: every PubMed source is a PMID enumeration." in enum_html
    assert "No search was run for this topic: every PubMed source is a PMID enumeration." not in mixed_html
    assert "PMID enumeration — not a search; can retrieve only what it was told" in enum_html


def test_found_by_values_render_in_screening_table():
    html = render_page(_core())
    assert "Found by" in html
    assert "pubmed#1, epmc#1" in html
    assert "UNRECORDED" in html


def test_deleting_retrieval_block_suppresses_retrieval_strings():
    core = deepcopy(_core())
    del core["search"]["retrieval"]
    html = render_page(core)
    for absent in [
        "abcdef12",
        REPLAY_SENTENCE,
        "HTTP 500 from PubMed",
        "hard_hits_cap",
        "12 not screened",
        "No search was run for this topic",
        "pubmed#1, epmc#1",
        "UNRECORDED",
    ]:
        assert absent not in html
