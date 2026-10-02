"""Constructed defects are synthetic PLANTS, not trial results."""
import ast
import json
from pathlib import Path

import pytest

from harness import component_typing, endpoint_policy
from scripts import hope3_policy_options as lane


@pytest.mark.parametrize("item", ["NCT00468923", "HOPE-3 (>=70)", "PMID 28385949",
                                      {"id": "other", "family": "hope 3"}])
def test_pool_refused_before_computation(item):
    with pytest.raises(lane.DecisionRequired, match="DECISION_REQUIRED_BEFORE_INTERVAL"):
        lane.pool(["20404379", item])


def test_negative_guard_and_no_synthesis_even_without_hope():
    assert lane.require_no_hope(["20404379", "42670961"]) is None
    with pytest.raises(ValueError, match="POOLING_DISABLED"):
        lane.pool(["20404379"])


def test_script_has_no_synthesis_or_network_path():
    tree = ast.parse(Path(lane.__file__).read_text(encoding="utf-8"))
    imports = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    assert not any(any(x in name for x in ("synth", "pipeline", "requests", "urllib", "scipy", "subprocess")) for name in imports)
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    assert isinstance(functions["pool"].body[-1], ast.Raise)
    assert all(not isinstance(n, ast.Return) for n in ast.walk(functions["pool"]))


@pytest.mark.parametrize("name", ["HOPE-3", "JUPITER", "STAREE", "PREVENTABLE", "ALLHAT-LLT"])
def test_no_components_from_trial_name(name):
    assert lane.typed_definition(name)["state"] == "NOT_DERIVED"
    assert lane.typed_definition(name)["components"] == []


def test_definition_negative_plant():
    text = "The primary endpoint was a composite of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke."
    typed = lane.typed_definition(text)
    assert typed["state"] == "HELD"
    assert set(typed["components"]) == lane.THREE
    assert typed["quote"] == text


def test_relay_never_becomes_held_even_if_text_looks_like_definition():
    relay = {"component_set": ["cardiovascular death", "nonfatal myocardial infarction", "nonfatal stroke"],
             "component_basis": "RELAYED: synthetic plant"}
    typed = lane.typed_definition("The primary endpoint was a composite of cardiovascular death, myocardial infarction or stroke.", relayed=relay)
    assert typed["state"] == "RELAYED"
    assert typed["poolable"] is False
    row = {"id": "NCT00468923", "definition": typed}
    assert all(not lane.admission(row, i).startswith("YES") for i in range(3))


def test_untyped_component_is_not_silently_dropped():
    typed = lane.typed_definition("The primary endpoint was a composite of cardiovascular death, myocardial infarction, stroke, or arterial revascularization.")
    assert typed["untyped"] == ["or arterial revascularization"]
    assert typed["poolable"] is False


@pytest.mark.parametrize("text", [
    "The primary endpoint was a composite of cardiovascular death, myocardial infarction or stroke.",
    "MI, stroke or any death 10 versus 20 events.",
    "Cardiovascular death, myocardial infarction, stroke or revascularization: hazard ratio 0.8.",
    "The primary endpoint was a composite of cardiovascular death, myocardial infarction or stroke. Cardiovascular death: hazard ratio 0.8.",
    "MACE: hazard ratio 0.8.",
])
def test_design_marginals_and_unbound_effects_are_not_three_point_results(text):
    assert lane.three_point_result(text)["state"] == "NOT_HELD"


def test_explicit_three_point_result_negative_plant():
    text = "Cardiovascular death, nonfatal myocardial infarction or nonfatal stroke: hazard ratio 0.8."
    assert lane.three_point_result(text) == {"state": "HELD", "quote": text}


def test_held_corpus_and_history_do_not_leak_pooled_numbers():
    data = lane.build()
    assert [r["id"] for r in data["rows"]] == list(lane.IDS)
    assert all(r["three_point"]["state"] == "NOT_HELD" for r in data["rows"])
    assert data["rows"][0]["excluded_spans"]
    assert data["rows"][1]["registered_three_point"]
    assert data["rows"][4]["definition"]["hasResults"] is False
    assert data["rows"][2]["definition"]["state"] == "RELAYED"
    assert data["rows"][2]["sources"]
    pending = lane.read_json(lane.ROOT / "docs/endpoint_policies.json")["topics"][lane.SLUG]["Major vascular events"]["pending"][0]
    assert data["history"] == pending["diagnostic_already_seen"]["note"]
    output = json.dumps(data) + lane.render(data)
    for key, value in pending["diagnostic_already_seen"].items():
        if key != "note":
            for number in value if isinstance(value, list) else [value]:
                assert str(number) not in output
    for row in data["rows"]:
        for source in row["sources"] + row["excluded_spans"]:
            assert (lane.ROOT / source["path"]).is_file()
            if source["quote"] and source["field"] == "text":
                assert source["quote"] in (lane.ROOT / source["path"]).read_text(encoding="utf-8")


def test_census_all_topics_and_named_denominators():
    output = lane.census()
    assert output["topic_scope"]["N"] == len(list((lane.ROOT / "topics").glob("*.json")))
    for rule in output["rules"].values():
        assert rule["n"] == len(rule["items"])
        assert rule["N"] == len(lane.IDS)


def test_base_behaviour_without_computing_interval():
    # The base annotator returns normally; it catches this only in problems().
    review = {"outcomes": [{"name": "Major vascular events", "trials": [{"id": "NCT00468923"}]}]}
    assert endpoint_policy.attach(review, lane.SLUG, {}, root=str(lane.ROOT)) is None
    assert endpoint_policy.problems(review)[0]["kind"] == "ENDPOINT_POLICY_VIOLATION"
    assert component_typing.derive("HOPE-3") is None
    with pytest.raises(lane.DecisionRequired):
        lane.require_no_hope(review["outcomes"][0]["trials"])
