"""Defect plants are synthetic; corpus regressions read actual held bytes."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from harness import estmeasure, extract, source_hierarchy, design_key
from harness.measure_identity import (Measure as M, MeasureMapping, check_pool,
    check_target, identity, measure_from_table, measure_of, outcome_identity, select)

ROOT = Path(__file__).resolve().parents[1]


def counts():
    return {"id": "synthetic-counts", "ai": 10, "n1i": 100, "ci": 20, "n2i": 100}


def published(scale="HR", source="hazard ratio"):
    return {"id": "synthetic-published", "scale": scale, "source": source,
            "effect": 0.5, "ci_low": 0.3, "ci_high": 0.8}


def codes(problems):
    return {p["code"] for p in problems}


@pytest.mark.parametrize("words,expected", [
    ("hazard ratio", M.HAZARD_RATIO), ("rate ratio", M.RATE_RATIO),
    ("risk ratio", M.RISK_RATIO), ("relative risk", M.RISK_RATIO),
    ("odds ratio", M.ODDS_RATIO), ("RMST difference", M.RMST_DIFFERENCE),
    ("mean difference", M.MEAN_DIFFERENCE)])
def test_word_identity(words, expected):
    assert measure_of({"source": words}) == expected


def test_rate_mislabel_plant_and_correct_negative():
    row = published("RR", "rate ratio 0.5; 95% CI 0.3-0.8")
    assert estmeasure.classify(row["scale"], row["source"])["canonical_estimand"] == "RISK_RATIO"
    assert measure_of(row) == M.RATE_RATIO
    assert measure_of(published("RR", "risk ratio")) == M.RISK_RATIO
    assert measure_of({"scale": "RR", "row_label": "rate ratio"}) == M.RATE_RATIO
    assert measure_of({"source": "relative risk reduction"}) == M.UNKNOWN


@pytest.mark.parametrize("header", ["HR/OR", "HR or OR"])
def test_table_footnote_plant(header):
    assert estmeasure.classify(header, "hazard ratio")["canonical_estimand"] != "HAZARD_RATIO_FIRST_EVENT"
    assert measure_from_table(header, "hazard ratio", "mortality") == M.HAZARD_RATIO
    assert measure_of({"table_header": header, "footnote": "hazard ratio"}) == M.HAZARD_RATIO
    assert measure_from_table("OR", "", "mortality") == M.ODDS_RATIO
    assert measure_from_table(header, "hazard ratio or odds ratio", "") == M.UNKNOWN


def test_counts_relayed_and_unknown_fail_closed():
    row = counts()
    row["source"] = "hazard ratio"
    assert identity(row)["derivation"] == "RECONSTRUCTED"
    assert measure_of(row) == M.RISK_RATIO
    for bad in ({**row, "n1i": 0}, {**row, "ai": -1}, {**row, "ci": None},
                {**row, "ai": True}, {**row, "ai": float("nan")},
                {**published(), "derivation": "RELAYED"},
                published(source="hazard ratio and odds ratio")):
        assert measure_of(bad) == M.UNKNOWN
        assert "MEASURE_UNKNOWN" in codes(check_pool([bad, published()]))
    assert not check_pool([published(), published()])


def test_mixed_plant():
    rows = [counts(), published()]
    old = estmeasure.pool_compatibility([estmeasure.classify("RR"), estmeasure.classify("HR")])
    assert old["status"] == "compatible_labels"
    assert "MEASURE_MIX_POOLED" in codes(check_pool(rows))
    assert not check_pool([published(), published()])


def test_target_plant_mapping_and_immutable_inputs():
    config = {"primary_outcome": {"name": "mortality", "estimand": "OR"}}
    row = published("RR", "rate ratio")
    outcome = {"name": "mortality", "trials": [row], "result": {"estimate": 0.5, "scale": "RR"}}
    review = {"outcomes": [outcome]}
    saved = deepcopy((review, config))
    assert source_hierarchy.estimand_decision(config["primary_outcome"], [row])["target_scale"] == "RR"
    assert "TARGET_MEASURE_REWRITTEN" in codes(check_target(review, config))
    assert (review, config) == saved
    assert outcome_identity(outcome, config["primary_outcome"]) == {
        "target_measure": "ODDS_RATIO", "served_measure": "RATE_RATIO"}
    outcome["result"]["scale"] = "OR"
    outcome["result"]["measure_mapping"] = {"source": "RATE_RATIO", "target": "ODDS_RATIO"}
    assert "TARGET_MEASURE_REWRITTEN" in codes(check_target(review, config))
    outcome["result"].update(outcome_identity(outcome, config["primary_outcome"]))
    outcome["result"]["measure_mapping"] = MeasureMapping(M.RATE_RATIO, M.ODDS_RATIO, "test-only receipt", "synthetic evidence")
    assert not check_target(review, config)
    outcome["trials"] = [published("OR", "odds ratio")]
    outcome["result"].pop("measure_mapping")
    outcome["result"].update(outcome_identity(outcome, config["primary_outcome"]))
    assert not check_target(review, config)
    outcome["result"].pop("target_measure")
    assert "MEASURE_IDENTITY_FIELDS_MISSING_OR_WRONG" in codes(check_target(review, config))


def test_selection_plant_and_negative():
    row, rr, hr = counts(), published("RR", "risk ratio"), published()
    old = design_key.select_estimator_by_source_hierarchy(row, [rr, hr], "HR")
    assert old["scale"] == "RR"
    result = select([row, rr, hr], [M.HAZARD_RATIO])
    assert result["row"] == hr and result["admissible"]
    unresolved = select([row, rr], [M.HAZARD_RATIO])
    assert unresolved["row"] == row and not unresolved["admissible"]
    assert "MEASURE_MISMATCH_UNRESOLVED" in codes(unresolved["problems"])
    assert select([row], [M.RISK_RATIO])["admissible"]
    assert not select([hr], [M.HAZARD_RATIO, M.RISK_RATIO])["admissible"]
    assert not select([], [M.HAZARD_RATIO])["admissible"]
    assert not select([hr], [M.UNKNOWN])["admissible"]


def load(slug, where):
    return json.loads((ROOT / where.format(slug=slug)).read_text(encoding="utf-8"))


def test_held_recovery_and_philo():
    slug = "tocilizumab-covid19-mortality"
    config = load(slug, "topics/{slug}.json")
    review = load(slug, "docs/reviews/{slug}/review.json")
    records = load(slug, "cache/{slug}/records.json")["records"]
    outcome = next(o for o in review["outcomes"] if o["name"] == config["primary_outcome"]["name"])
    row = outcome["trials"][0]
    record = next(r for r in records if str(r["id"]) == row["id"].removeprefix("PMID "))
    assert "rate ratio" in record["abstract"]
    # Confirm the numerical tuple independently via the held abstract parser.
    effect = extract.extract_effect(extract._norm(record["abstract"]))
    assert effect[1:] == (row["effect"], row["ci_low"], row["ci_high"])
    assert measure_of(row) == M.RATE_RATIO
    assert "TARGET_MEASURE_REWRITTEN" in codes(check_target(review, config))
    slug = "ticagrelor-vs-clopidogrel-acs"
    review = load(slug, "docs/reviews/{slug}/review.json")
    bleeding = next(o for o in review["outcomes"] if o["name"] == "Major bleeding")
    assert "MEASURE_MIX_POOLED" in codes(check_pool(bleeding["trials"]))
    records = load(slug, "cache/{slug}/records.json")["records"]
    hr = next(r for r in bleeding["trials"] if measure_of(r) == M.HAZARD_RATIO)
    record = next(r for r in records if str(r["id"]) == hr["id"].removeprefix("PMID "))
    assert "hazard ratio" in record["abstract"]
    assert extract.extract_effect(extract._norm(record["abstract"]))[1:] == (hr["effect"], hr["ci_low"], hr["ci_high"])


def test_census_all_topics_and_known_defects():
    from scripts.measure_identity_census import census
    result = census(ROOT)
    assert result["coverage"]["topics"] == len(list((ROOT / "topics").glob("*.json")))
    rules = result["rules"]
    for rule in rules.values():
        assert rule["n"] == len(rule["items"]) <= rule["N"]
    assert any(i["topic"] == "tocilizumab-covid19-mortality" for i in rules["span_scale_disagreement"]["items"])
    assert any(i["topic"] == "ticagrelor-vs-clopidogrel-acs" for i in rules["mixed_measure_pools"]["items"])


def test_plato_counts_match_held_registry_groups():
    slug = "ticagrelor-vs-clopidogrel-acs"
    review = load(slug, "docs/reviews/{slug}/review.json")
    held = load(slug, "cache/{slug}/records.json")
    outcome = next(o for o in review["outcomes"] if o["name"] == "Major bleeding")
    row = next(r for r in outcome["trials"] if identity(r)["derivation"] == "RECONSTRUCTED")
    source = next(o for o in held["ctgov_results"][row["family_id"]]
                  if o["title"] == "Participants With Any Major Bleeding Event")
    groups = {g["title"]: g["id"] for g in source["groups"]}
    ns = {c["groupId"]: int(c["value"]) for d in source["denoms"] for c in d["counts"]}
    events = {m["groupId"]: int(m["value"]) for c in source["classes"]
              for cat in c["categories"] for m in cat["measurements"]}
    i, c = groups["TICAGRELOR"], groups["CLOPIDOGREL"]
    assert (row["ai"], row["n1i"], row["ci"], row["n2i"]) == (events[i], ns[i], events[c], ns[c])
    assert not select([row], [M.HAZARD_RATIO])["admissible"]
