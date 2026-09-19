"""Registration must retain disjoint gates and refuse ambiguous collisions."""
import json
import pytest
from harness import gate_scorecard as scorecard


def test_production_registration_merges_gate_ids(tmp_path):
    target = tmp_path / scorecard.REGISTRY_PATH
    target.parent.mkdir(parents=True)
    a = {"schema_version": 2, "gates": [{"gate_id": "plant-a", "events": []}]}
    b = {"schema_version": 2, "gates": [{"gate_id": "plant-b", "events": []}]}
    target.write_text(json.dumps(a), encoding="utf-8")
    scorecard.register_gates(tmp_path, b)
    assert {g["gate_id"] for g in json.loads(target.read_text())["gates"]} == {"plant-a", "plant-b"}
    scorecard.register_gates(tmp_path, b)
    assert len(json.loads(target.read_text())["gates"]) == 2


def test_registration_conflict_preserves_original_bytes(tmp_path):
    target = tmp_path / scorecard.REGISTRY_PATH
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps({"gates": [{"gate_id": "plant-a", "events": []}]}))
    before = target.read_bytes()
    with pytest.raises(ValueError, match="conflict"):
        scorecard.register_gates(tmp_path, {"gates": [{"gate_id": "plant-a", "events": [{"event_id": "different"}]}]})
    assert target.read_bytes() == before
