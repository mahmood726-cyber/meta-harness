import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import acquisition as acq  # noqa: E402
from harness import fetch  # noqa: E402


def _record(pid: str) -> dict:
    return {
        "id": str(pid),
        "id_type": "pmid",
        "title": f"Trial {pid}",
        "abstract": "",
        "doi": "",
        "journal": "",
        "nct": "",
        "pubtypes": [],
        "year": "2026",
    }


def _fake_efetch(pmids):
    return [_record(pid) for pid in pmids]


def _empty_epmc(_query, retmax):
    return {
        "ids": [],
        "count": 0,
        "state": "RAN_ZERO",
        "error": None,
        "funnel": {
            "hits": 0,
            "fetched": 0,
            "retained": 0,
            "cap": {"kind": "relevance_top_n", "n": retmax, "remainder": 0},
        },
    }


def _mute_optional_network(monkeypatch):
    monkeypatch.setattr(fetch, "_efetch", _fake_efetch)
    monkeypatch.setattr(fetch, "_pmc_fulltext", lambda *args, **kwargs: "")
    monkeypatch.setattr(fetch, "_ctgov_results", lambda _nct: None)


def test_adapter_exception_is_ran_error_and_drives_europepmc_status(monkeypatch):
    _mute_optional_network(monkeypatch)

    def boom(_query, _retmax):
        raise RuntimeError("epmc exploded")

    monkeypatch.setattr(fetch, "_europepmc_result", boom)
    out = fetch.run({
        "slug": "__plant_acq__",
        "pubmed_queries": ["101[uid]"],
        "seed_comparator_refs": False,
        "_now": "2026-09-14",
    })

    epmc = [s for s in out["retrieval_ledger"]["sources"] if s["kind"] == "EUROPEPMC_QUERY"]
    assert epmc and epmc[0]["state"] == "RAN_ERROR"
    assert epmc[0]["error"]
    assert epmc[0]["state"] not in {"RAN_ZERO", "RAN_OK"}
    assert epmc[0]["funnel"]["fetched"] == 0
    assert out["source_status"]["europepmc"] == "RAN_ERROR"


def test_esearch_all_fetches_full_count_and_hard_cap(monkeypatch):
    def fake_get_json(_url, params):
        count = 764
        retstart = int(params.get("retstart", 0))
        retmax = int(params.get("retmax", 0))
        stop = min(count, retstart + retmax)
        return {"esearchresult": {"count": str(count),
                                  "idlist": [str(i) for i in range(retstart, stop)]}}

    monkeypatch.setattr(acq.http, "get_json", fake_get_json)

    full = acq.esearch_all("plant", page_size=200, sleep=0)
    assert full["state"] == "RAN_OK"
    assert full["count"] == 764
    assert len(full["ids"]) == 764
    assert full["funnel"]["hits"] == 764
    assert full["funnel"]["fetched"] == 764
    assert full["funnel"]["cap"]["kind"] == "none"

    capped = acq.esearch_all("plant", page_size=1000, hard_cap=100, sleep=0)
    assert len(capped["ids"]) == 100
    assert capped["funnel"]["fetched"] == 100
    assert capped["funnel"]["cap"]["kind"] == "hard_hits_cap"
    assert capped["funnel"]["cap"]["remainder"] == 664


def test_fetch_records_have_found_by_and_validate_refuses_bad_ledgers(monkeypatch):
    _mute_optional_network(monkeypatch)
    monkeypatch.setattr(fetch, "_europepmc_result", _empty_epmc)
    out = fetch.run({
        "slug": "__plant_acq__",
        "pubmed_queries": ["1[uid] OR 2[uid]"],
        "extra_pmids": ["3"],
        "positive_control_pmids": ["4"],
        "negative_control_pmids": ["5"],
        "comparator_pmid": "6",
        "seed_comparator_refs": False,
        "_now": "2026-09-14",
    })
    ledger = out["retrieval_ledger"]
    source_ids = {s["source_id"] for s in ledger["sources"]}
    for record in out["records"]:
        found_by = ledger["records"][record["id"]]["found_by"]
        assert found_by
        assert set(found_by) <= source_ids
    assert acq.validate(ledger, out["records"]) == []

    orphan = acq.new_ledger("__plant_acq__")
    acq.add_source(orphan, "EXTRA_PMIDS", "q", "2026-09-14", "RAN_OK", None,
                   {"hits": 1, "fetched": 1, "retained": 1,
                    "cap": {"kind": "none", "n": None, "remainder": None}},
                   ["x"], False)
    assert any("orphan record x" in e for e in acq.validate(orphan, [_record("x")]))

    unknown = acq.new_ledger("__plant_acq__")
    unknown["records"] = {"x": {"found_by": ["missing#1"]}}
    assert any("unknown source_id" in e for e in acq.validate(unknown, []))

    bad_error = acq.new_ledger("__plant_acq__")
    acq.add_source(bad_error, "EUROPEPMC_QUERY", "q", "2026-09-14", "RAN_ERROR", "boom",
                   {"hits": None, "fetched": 1, "retained": 1,
                    "cap": {"kind": "none", "n": None, "remainder": None}},
                   [], True)
    assert any("RAN_ERROR with fetched" in e for e in acq.validate(bad_error, []))

    bad_zero = acq.new_ledger("__plant_acq__")
    acq.add_source(bad_zero, "EUROPEPMC_QUERY", "q", "2026-09-14", "RAN_ZERO", None,
                   {"hits": 1, "fetched": 0, "retained": 0,
                    "cap": {"kind": "none", "n": None, "remainder": None}},
                   [], True)
    assert any("RAN_ZERO with hits" in e for e in acq.validate(bad_zero, []))


def test_uid_query_is_pmid_enumeration_and_not_discovery_capable(monkeypatch):
    assert acq.classify_query("123[uid]") == "PUBMED_PMID_ENUMERATION"
    assert acq.classify_query("randomized[tiab]") == "PUBMED_LEGACY_QUERY"
    _mute_optional_network(monkeypatch)
    monkeypatch.setattr(fetch, "_europepmc_result", _empty_epmc)

    out = fetch.run({
        "slug": "__plant_acq__",
        "pubmed_queries": ["123[uid]"],
        "seed_comparator_refs": False,
        "_now": "2026-09-14",
    })
    src = next(s for s in out["retrieval_ledger"]["sources"] if s["kind"] == "PUBMED_PMID_ENUMERATION")
    assert src["discovery_capable"] is False


def test_refresh_writes_snapshot_pin_load_and_hash_without_touching_pinned(monkeypatch):
    slug = "__plant_acq__"
    tmp_root = tempfile.mkdtemp(prefix="__plant_acq__", dir=os.getcwd())
    try:
        cache_dir = os.path.join(tmp_root, "cache", slug)
        os.makedirs(cache_dir, exist_ok=True)
        pinned = os.path.join(cache_dir, "records.json")
        with open(pinned, "wb") as f:
            f.write(b'{"old":true}')

        def fake_run(config):
            records = [_record("9")]
            ledger = acq.new_ledger(slug)
            sid = acq.add_source(
                ledger,
                "EXTRA_PMIDS",
                "config.extra_pmids",
                config["_now"],
                "RAN_OK",
                None,
                {"hits": 1, "fetched": 1, "retained": 1,
                 "cap": {"kind": "none", "n": None, "remainder": None}},
                ["9"],
                False,
            )
            acq.attach_records(ledger, sid, ["9"])
            acq.finalize(ledger, records, config["_now"], "REFRESH")
            return {"slug": slug, "fetched_utc": config["_now"], "records": records,
                    "retrieval_ledger": ledger}

        monkeypatch.setattr(fetch, "run", fake_run)
        snapshot_dir = acq.refresh({"slug": slug}, "2026-09-14", root=tmp_root)

        with open(pinned, "rb") as f:
            assert f.read() == b'{"old":true}'
        assert os.path.basename(snapshot_dir).startswith("2026-09-14-")
        snap_records_path = os.path.join(snapshot_dir, "records.json")
        with open(snap_records_path, encoding="utf-8") as f:
            snap_records = json.load(f)
        assert "retrieval_ledger" not in snap_records
        assert os.path.exists(os.path.join(snapshot_dir, "retrieval_ledger.json"))

        acq.pin(slug, snapshot_dir, root=tmp_root)
        loaded = acq.load_ledger(slug, root=tmp_root)
        assert loaded["slug"] == slug
        with open(pinned, encoding="utf-8") as f:
            assert json.load(f)["records"][0]["id"] == "9"
        assert acq.records_sha256([_record("9")]) == acq.records_sha256(json.loads(json.dumps([_record("9")])))
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def test_concept_query_matches_search_rebuild_import_parity():
    from scripts import search_rebuild

    cfg = {
        "include": {"population_any": ["type 2 diabetes"]},
        "intervention_terms": ["DPP-4 inhibitor"],
    }
    assert acq.concept_query(cfg) == search_rebuild.build_query(cfg)
