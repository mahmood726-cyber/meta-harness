from harness import acquisition as acq
from scripts import write_legacy_ledgers


def test_build_legacy_ledger_marks_all_records_legacy_unrecorded():
    records = {
        "fetched_utc": "2026-01-02",
        "source_status": {"pubmed": "RAN_ERROR"},
        "records": [{"id": "101"}, {"id": "202"}],
    }
    config = {"pubmed_queries": ["101[uid]", "drug[tiab]"]}

    ledger = write_legacy_ledgers.build_legacy_ledger("__legacy__", config, records)

    kinds = [source["kind"] for source in ledger["sources"]]
    assert kinds == ["PUBMED_PMID_ENUMERATION", "PUBMED_LEGACY_QUERY", "LEGACY_UNRECORDED"]
    query_sources = ledger["sources"][:2]
    assert all(source["state"] == "RAN_UNRECORDED" for source in query_sources)  # attempted, yield unrecorded -- never NOT_RUN
    assert all(source["funnel"]["hits"] is None for source in query_sources)
    legacy = ledger["sources"][2]
    assert legacy["source_id"] == "legacy_unrecorded#1"
    assert legacy["funnel"]["hits"] is None
    assert legacy["funnel"]["fetched"] == 2
    assert ledger["records"] == {
        "101": {"found_by": ["legacy_unrecorded#1"]},
        "202": {"found_by": ["legacy_unrecorded#1"]},
    }
    assert ledger["snapshot"]["mode"] == "LEGACY_UNRECORDED"
    assert ledger["snapshot"]["raw_calls"] == 0
    assert acq.validate(ledger, records["records"]) == []


def test_ran_unrecorded_is_legacy_only():
    """A pre-ledger query is RAN_UNRECORDED (attempted, yield unknown) -- never NOT_RUN, which would assert it was not
    attempted; and validate() refuses the state on a live (REFRESH) snapshot so it can only describe the past."""
    acquisition = acq
    _pubmed_status = write_legacy_ledgers._pubmed_status
    assert _pubmed_status({}) == "RAN_UNRECORDED"
    assert _pubmed_status({"source_status": {"pubmed": "RAN_OK"}}) == "RAN_OK"
    led = acquisition.new_ledger("__plant__")
    sid = acquisition.add_source(led, "PUBMED_LEGACY_QUERY", "q", "2026-01-01", "RAN_UNRECORDED", None,
                                 {"hits": None, "fetched": 0, "retained": 0, "cap": {"kind": "none", "n": None, "remainder": None}},
                                 [], True)
    led["snapshot"] = {"records_sha256": "x", "retrieved_utc": "2026-01-01", "mode": "REFRESH", "engine_sha": "e", "raw_calls": 0}
    assert any("legacy-only" in e for e in acquisition.validate(led, []))
    led["snapshot"]["mode"] = "LEGACY_UNRECORDED"
    assert not any("legacy-only" in e for e in acquisition.validate(led, []))
