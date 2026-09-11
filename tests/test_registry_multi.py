"""Multi-registry (ISRCTN) adapter: the pure XML parser is offline-testable against a saved
fixture; the union's fail-closed status contract is testable without network."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import registry_first as rf  # noqa: E402

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "isrctn_sample.xml")


def test_parse_isrctn_ids_from_fixture():
    xml = open(FIX, encoding="utf-8").read()
    ids = rf._parse_isrctn_ids(xml)
    assert ids, "parser found no ISRCTN ids in the fixture"
    assert all(i.startswith("ISRCTN") and i[6:].isdigit() and len(i) == 14 for i in ids)
    assert "ISRCTN41823570" in ids  # first trial in the saved colchicine query
    assert len(ids) == len(set(ids))  # deduped


def test_parse_isrctn_ids_empty_and_garbage():
    assert rf._parse_isrctn_ids('<allTrials totalCount="0"></allTrials>') == []
    assert rf._parse_isrctn_ids("not xml at all <<<") == []
    assert rf._parse_isrctn_ids("") == []


def test_normalise_isrctn():
    assert rf._normalise_isrctn("isrctn41823570") == "ISRCTN41823570"
    try:
        rf._normalise_isrctn("NCT01234567")
        assert False, "should reject an NCT id"
    except ValueError:
        pass


def test_union_fail_closed_empties_pmids_on_error(monkeypatch):
    # CT.gov succeeds, ISRCTN raises -> whole run is RAN_ERROR with pmids=[] (partial != complete),
    # but per-registry status still shows ctgov RAN_OK so the flaky source is diagnosable.
    monkeypatch.setattr(rf, "enumerate_nct", lambda c, i: ["NCT00000001"])
    monkeypatch.setattr(rf, "nct_to_pmids", lambda n: ["111"])
    def boom(c, i, limit=100):
        raise RuntimeError("isrctn down")
    monkeypatch.setattr(rf, "enumerate_isrctn", boom)
    res = rf.registry_first_pmids("cond", "intr", include_isrctn=True)
    assert res["status"] == rf.RAN_ERROR
    assert res["pmids"] == []
    assert res["registries"]["ctgov"]["status"] == rf.RAN_OK
    assert res["registries"]["isrctn"]["status"] == rf.RAN_ERROR


def test_union_ok_unions_pmids(monkeypatch):
    monkeypatch.setattr(rf, "enumerate_nct", lambda c, i: ["NCT00000001"])
    monkeypatch.setattr(rf, "nct_to_pmids", lambda n: ["111", "222"])
    monkeypatch.setattr(rf, "enumerate_isrctn", lambda c, i, limit=100: ["ISRCTN41823570"])
    monkeypatch.setattr(rf, "registry_id_to_pmids", lambda r: ["222", "333"])
    res = rf.registry_first_pmids("cond", "intr", include_isrctn=True)
    assert res["status"] == rf.RAN_OK
    assert set(res["pmids"]) == {"111", "222", "333"}  # deduped union


def test_ctgov_only_unchanged_default(monkeypatch):
    monkeypatch.setattr(rf, "enumerate_nct", lambda c, i: ["NCT00000001"])
    monkeypatch.setattr(rf, "nct_to_pmids", lambda n: ["111"])
    res = rf.registry_first_pmids("cond", "intr")  # include_isrctn defaults False
    assert res["status"] == rf.RAN_OK and res["pmids"] == ["111"]
    assert "isrctn" not in res["registries"]
