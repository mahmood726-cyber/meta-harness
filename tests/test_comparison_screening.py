"""Retrospective comparison-level screening plants; synthetic IDs are labelled."""
import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import screen, arm_parse
from evidence.comparison_screening.measure import baseline, served_matches


@pytest.fixture
def held():
    config = json.loads((ROOT / "topics/semaglutide-obesity-weight.json").read_text(encoding="utf-8"))
    data = json.loads((ROOT / "cache/semaglutide-obesity-weight/records.json").read_text(encoding="utf-8"))
    record = next(r for r in data["ctgov"] if r["id"] == "NCT04074161")
    return copy.deepcopy(record), config["include"]


def test_step8_plant_fires_on_read_only_baseline_and_passes(held):
    rec, inc = held
    old, _ = baseline()
    assert old.screen_record(rec, inc, []).rule_id == "X2"
    assert old.screen_record_2(rec, inc) == "exclude"
    result = screen.screen_record(rec, inc, [])
    assert result.decision == "include"
    assert screen.screen_record_2(rec, inc) == "include"
    assert len(result) == 4  # downstream unpacking remains compatible
    c = result.comparison
    assert c["experimental_arm"] == "Semaglutide"
    assert c["comparator_arm"] == "Placebo (semaglutide)"
    assert c["comparator_kind"] == "MATCHED_PLACEBO"
    assert c["other_arms"] == ["Liraglutide", "Placebo (liraglutide)"]
    assert c["pooled_placebo_alternative"]["arms"] == ["Placebo (semaglutide)", "Placebo (liraglutide)"]
    assert c["pooled_placebo_alternative"]["state"] == "NOT_THE_ELIGIBLE_CONTRAST"


@pytest.mark.parametrize("conditions", [["liraglutide-treated obesity"], ["Obesity"]])
def test_no_interest_arm_remains_excluded(held, conditions):
    rec, inc = held
    rec.update(id="SYNTHETIC_NO_INTEREST", conditions=conditions,
               interventions=["Liraglutide", "Placebo (liraglutide)"])
    old, _ = baseline()
    for screener in (old, screen):
        assert screener.screen_record(rec, inc, []).decision == "exclude"
        assert screener.screen_record_2(rec, inc) == "exclude"


def test_real_population_term_still_x2(held):
    rec, inc = held
    rec.update(id="SYNTHETIC_DIABETES", conditions=["Obesity", "type 2 diabetes"])
    old, _ = baseline()
    for screener in (old, screen):
        assert screener.screen_record(rec, inc, []).rule_id == "X2"
        assert screener.screen_record_2(rec, inc) == "exclude"


@pytest.mark.parametrize("mutation", [
    {"interventions": []}, {"allocation": "NON_RANDOMIZED"},
    {"interventions": ["Semaglutide", "Liraglutide", "Placebo (liraglutide)"]},
    {"interventions": ["Semaglutide", "Liraglutide"]},
])
def test_unknown_or_absent_comparison_fails_closed(held, mutation):
    rec, inc = held
    rec.update(mutation, id="SYNTHETIC_UNRESOLVED")
    assert screen.screen_record(rec, inc, []).decision == "exclude"
    assert screen.screen_record_2(rec, inc) == "exclude"


def test_arm_group_titles_and_other_design_gates(held):
    rec, inc = held
    rec["arm_groups"] = [{"title": x} for x in rec.pop("interventions")]
    rec["title"] = "Obesity trial including liraglutide"
    assert screen.screen_record(rec, inc, []).decision == "include"
    inc = {**inc, "design_any": ["crossover"]}
    assert screen.screen_record(rec, inc, []).rule_id == "X-DESIGN"
    # review correction: screener 2 applies the same arm exemption and then its OWN gates; it has no design_any gate for any
    # record and must not call screener 1 (the two would agree by construction on exactly these records). The disagreement
    # with screener 1's X-DESIGN is what dual screening surfaces for adjudication; screener 1 remains the adjudicator.
    assert screen.screen_record_2(rec, inc) == "include"


def test_publication_requires_allocation_sentence(held):
    rec, inc = held
    rec.update(id="SYNTHETIC_PUBLICATION", id_type="pmid", pubtypes=["Randomized Controlled Trial"],
               abstract="Participants were randomly assigned to semaglutide, placebo (semaglutide), liraglutide, or placebo (liraglutide).")
    assert len(arm_parse.allocation_arms(rec)) == 4
    assert screen.screen_record(rec, inc, []).decision == "include"
    assert screen.screen_record_2(rec, inc) == "include"
    rec["abstract"] = "Prior trials compared semaglutide with liraglutide and placebo."
    assert screen.screen_record(rec, inc, []).rule_id == "X2"
    assert screen.screen_record_2(rec, inc) == "exclude"


def test_portable_rule_not_trial_id_or_drug_specific():
    rec = {"id": "SYNTHETIC_GENERIC", "id_type": "nct", "allocation": "RANDOMIZED",
           "title": "Agentalpha versus agentbeta in obesity", "conditions": ["Obesity"],
           "interventions": ["Agentalpha", "Placebo (agentalpha)", "Agentbeta", "Placebo (agentbeta)"]}
    inc = {"population_any": ["obesity"], "population_none": ["agentbeta"],
           "intervention_any": ["agentalpha"], "comparator_any": ["placebo"]}
    c = screen.screen_record(rec, inc, []).comparison
    assert c["comparator_arm"] == "Placebo (agentalpha)"
    assert c["experimental_arm"] == "Agentalpha"


def test_served_prefixed_identifier_is_not_hidden():
    assert served_matches({"id": "STEP 8 ? NCT04074161"}, "NCT04074161")
    assert not served_matches({"id": "NCT040741610"}, "NCT04074161")


def test_comparison_emitted_on_pipeline_decision(held):
    rec, inc = held
    result = screen.run([rec], {"include": inc})
    row = result["decisions"][0]
    assert row["decision"] == "include"
    assert row["comparison"]["comparator_arm"] == "Placebo (semaglutide)"
