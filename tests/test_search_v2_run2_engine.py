"""Run-2 engine additions: labelled snapshot generations, the split recorded from the registry (lane S3 hard-coded
DEVELOPMENT into every snapshot), and the PubMed elink reference-list adapter beside the Europe PMC one."""
import json

import pytest

from harness import acquisition as acq
from harness import http, search_v2


def test_split_of_reads_the_sealed_split_not_a_constant():
    assert search_v2.split_of("pcsk9-mace") == "MEASUREMENT"
    assert search_v2.split_of("probiotics-aad-prevention") == "DEVELOPMENT"
    assert search_v2.split_of("not-a-topic") == "UNSPLIT"


def test_snapshot_generation_name_sits_beside_the_first_and_sorts_after_it(tmp_path, monkeypatch):
    monkeypatch.setattr(search_v2, "ROOT", str(tmp_path))
    first = search_v2._snapshot_dir("plant", "2026-09-15")
    second = search_v2._snapshot_dir("plant", "2026-09-15", "2026-09-15r2-search_v2")
    assert first != second and first.endswith("2026-09-15-search_v2") and second.endswith("2026-09-15r2-search_v2")
    for d in (first, second):
        (tmp_path / "cache" / "plant" / "snapshots").mkdir(parents=True, exist_ok=True)
        __import__("os").makedirs(d, exist_ok=True)
    assert search_v2._latest_snapshot("plant").endswith("2026-09-15r2-search_v2")
    with pytest.raises(ValueError):
        search_v2.refresh_topic("plant", "2026-09-15", snapshot_name="2026-09-15r2")


def test_pubmed_elink_refs_adapter_parses_linksets_and_reports_state(monkeypatch):
    calls = []

    def fake_get_json(url, params=None, **kw):
        calls.append((url, params))
        return {"linksets": [{"linksetdbs": [{"linkname": "pubmed_pubmed_refs", "links": [11, "22", "x"]}]}]}

    monkeypatch.setattr(http, "get_json", fake_get_json)
    monkeypatch.setattr(search_v2, "_pubmed_efetch", lambda pmids: [{"id": p, "pmid": p, "title": f"t{p}"} for p in pmids])
    monkeypatch.setattr(search_v2.time, "sleep", lambda s: None)
    records, meta = search_v2._pubmed_elink_refs_records("28456509")
    assert [r["pmid"] for r in records] == ["11", "22"]
    assert meta["state"] == "RAN_OK" and meta["funnel"]["hits"] == 2 and meta["funnel"]["cap"]["kind"] == "none"
    assert calls[0][1]["linkname"] == "pubmed_pubmed_refs" and calls[0][1]["id"] == "28456509"
    # a malformed payload is an error (RAN_ERROR in the ledger), never an empty success
    monkeypatch.setattr(http, "get_json", lambda url, params=None, **kw: {"esearchresult": {}})
    with pytest.raises(ValueError):
        search_v2._pubmed_elink_refs_records("28456509")


def test_new_source_kinds_are_ledger_vocabulary():
    assert "PUBMED_ELINK_BACKWARD_CITATION" in acq.SOURCE_KINDS
    assert "COMPARATOR_REFERENCE_LIST_PUBMED" in acq.SOURCE_KINDS
