"""Synthetic PLANTS only; none of these identities are research output."""
import json
import pytest

from harness.g1_recall import candidate_records, recall_trial, ceiling, metrics, screen
from harness.identity_join import join
from harness.screen import screen_record


def trial(label="NCT00000001", **resolved):
    return dict(label=label, resolved=resolved, resolution="RESOLVED_BY_IDENTIFIER", evidence_kind="PRINTED")


def record(**changes):
    return dict(id="NCT00000001", id_type="nct", nct="NCT00000001", title="Test population trial",
                abstract="randomized placebo trial", allocation="RANDOMIZED", **changes)


def plants():
    records = [record()]
    ambiguous = [dict(id="one", acronym="ABC"), dict(id="two", acronym="ABC")]
    return [(trial(nct="NCT00000001"), records), (trial("NCT00000002", nct="NCT00000002"), records),
            (trial("ABC"), ambiguous)]


def test_required_plants():
    expected = ["RETRIEVED", "NOT_RETRIEVED", "ABSTAIN"]
    base_expected = ["JOINED", "NOT_JOINED", "AMBIGUOUS"]
    for (entry, records), status, before in zip(plants(), expected, base_expected):
        assert join({"label": entry["label"], **entry["resolved"]}, records)["status"] == before
        got = recall_trial(entry, records, {})
        assert got["status"] == status
        if status == "RETRIEVED":
            assert got["screen"]["decision"] == "include"
        if status == "ABSTAIN":
            assert got["reason"] == "REFUSED_AMBIGUOUS_IDENTITY"


@pytest.mark.parametrize("row, candidate, key", [
    (trial("Report", doi="10.1234/test"), {"doi": "10.1234/test"}, "dois"),
    (trial("Report", pmid="12345678"), {"pmid": "12345678"}, "pmids"),
    (trial("ABC"), {"acronym": "ABC"}, "acronyms"),
    (trial("Smith 2020"), {"first_author": "Smith", "year": "2020"}, "author_years"),
])
def test_identity_routes(row, candidate, key):
    rec = {**record(), "nct": "", **candidate}
    assert recall_trial(row, [rec], {})["identity_join"]["key"] == key


def test_stronger_conflict_and_short_alias():
    assert recall_trial(trial("ABC", nct="NCT00000002"), [record(acronym="ABC")], {})["status"] == "NOT_RETRIEVED"
    assert recall_trial(trial("AB"), [record(acronym="AB")], {})["status"] == "NOT_RETRIEVED"


def test_screen_passthrough_exclusion_and_negative_plant():
    rec = record()
    topic = {"include": {"population_any": ["absentword"]}, "negative_control_pmids": ["12345678"]}
    result = screen(rec, topic)
    assert tuple(result.values()) == tuple(screen_record(rec, topic["include"], set(topic["negative_control_pmids"])))
    assert result["rule"] == "X2"
    assert screen(rec, {})["decision"] == "include"


def test_ceiling_refuses_relayed_unknown_and_duplicate():
    row = recall_trial(trial(nct="NCT00000001"), [record()], {})
    assert ceiling(2, [row, row])["k"] == 3
    assert ceiling(2, [{**row, "evidence_kind": "RELAYED"}])["k"] == 2
    assert ceiling(None, [row])["k"] is None
    assert ceiling(2, [row])["k"] == 3


def manifest(tmp_path):
    path = tmp_path / "cache/test/snapshots/run"
    path.mkdir(parents=True)
    rec = record()
    (path / "records.json").write_text(json.dumps({"slug": "test", "records": [rec]}), encoding="utf-8")
    return {"topics": {"test": {"state": "RAN_OK", "snapshot_dir": "cache/test/snapshots/run", "candidate_count": 1}},
            "candidates": {"test": [rec]}}


def test_manifest_binding_and_not_run(tmp_path):
    data = manifest(tmp_path)
    assert candidate_records(tmp_path, data, "test") == [record()]
    data["candidates"]["test"][0]["title"] = "wrong"
    with pytest.raises(ValueError, match="REFUSED_CANDIDATE_SNAPSHOT_MISMATCH"):
        candidate_records(tmp_path, data, "test")
    with pytest.raises(ValueError, match="REFUSED_SEARCH_TOPIC_NOT_RUN"):
        candidate_records(tmp_path, data, "other")


def test_unknown_search_not_counted_as_absence():
    got = metrics([{"item": "x", "status": "UNAVAILABLE"}])
    assert got["NOT_RETRIEVED"]["n"] == 0
    assert got["UNAVAILABLE"]["n"] == 1


@pytest.mark.parametrize("defect, reason", [
    ("state", "REFUSED_SEARCH_STATE"),
    ("path", "REFUSED_SNAPSHOT_PATH"),
    ("schema", "REFUSED_CANDIDATE_SCHEMA"),
])
def test_manifest_fail_closed(tmp_path, defect, reason):
    data = manifest(tmp_path)
    if defect == "state":
        data["topics"]["test"]["state"] = "RAN_ERROR"
    elif defect == "path":
        data["topics"]["test"]["snapshot_dir"] = "../outside"
    else:
        data["candidates"]["test"] = {}
    with pytest.raises(ValueError, match=reason):
        candidate_records(tmp_path, data, "test")


def test_ambiguity_negative_unique_acronym():
    assert recall_trial(trial("ABC"), [record(acronym="ABC")], {})["status"] == "RETRIEVED"


def test_summary_is_not_screen_record():
    rec = record()
    summary = {k: rec[k] for k in ("id", "id_type", "title", "nct")}
    assert screen_record(summary, {}, set())[1] == "X1"
    assert screen(rec, {})["decision"] == "include"
