"""Contracts every pilot task must meet BEFORE a model is called (both found by a live run that failed, 2026-09-24)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("_pilot_c", ROOT / "scripts" / "model_source_pilot.py")
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


def _strict_problems(node, path="schema"):
    """The API's strict output-schema rule: every object sets additionalProperties false and requires every property."""
    out = []
    if isinstance(node, dict):
        if node.get("type") == "object" or "properties" in node:
            if node.get("additionalProperties") is not False:
                out.append(f"{path}: additionalProperties must be false")
            props = set((node.get("properties") or {}).keys())
            if set(node.get("required") or []) != props:
                out.append(f"{path}: required {sorted(node.get('required') or [])} != properties {sorted(props)}")
        for k, v in node.items():
            out += _strict_problems(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += _strict_problems(v, f"{path}[{i}]")
    return out


@pytest.mark.parametrize("task", [t for t in pilot.TASKS if t not in pilot.RETIRED_TASKS])
def test_every_live_task_schema_is_strict(task):
    # plant #21: site_label's schema had an items object without additionalProperties:false -> 113 of 113 calls
    # RAN_ERROR (invalid_json_schema) -- a 100% failure that measured the harness
    assert _strict_problems(pilot._schema(task)) == []


def test_the_strict_checker_can_fail():
    assert _strict_problems({"type": "object", "properties": {"a": {"type": "object"}}, "required": ["a"],
                             "additionalProperties": False})


def test_a_population_with_duplicate_item_ids_is_refused():
    # plant #22: site_label froze N = 825 of which 56 were the same boilerplate protocol line in several files; the
    # queue keyed by item_id collapsed them to 769 and the denominator shrank without a word
    with pytest.raises(SystemExit):
        pilot.check_unique_ids("t", [{"item_id": "a"}, {"item_id": "b"}, {"item_id": "a"}])
    pilot.check_unique_ids("t", [{"item_id": "a"}, {"item_id": "b"}])
