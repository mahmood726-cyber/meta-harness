"""Synthetic denominator plants; registry identifiers in these plants are deliberately non-real."""
import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import consumer_consistency, continuous_identity, pipeline, target_endpoint
from harness.ctgov_results import extract_ctgov

SPEC = {"name": "All-cause mortality", "keywords": ["mortality"], "scale": "RR"}


def measure(class_denoms=True):
    def denoms(a, b):
        return [{"units": "Participants", "counts": [
            {"groupId": "a", "value": str(a)}, {"groupId": "b", "value": str(b)}]}]
    klass = {"title": "Observed", "categories": [{"measurements": [
        {"groupId": "a", "value": "10", "spread": "2"},
        {"groupId": "b", "value": "20", "spread": "3"}]}]}
    if class_denoms:
        klass["denoms"] = denoms(80, 70)
    return {"title": "All-cause mortality", "type": "PRIMARY", "paramType": "COUNT_OF_PARTICIPANTS",
            "groups": [{"id": "a", "title": "Drug"}, {"id": "b", "title": "Placebo"}],
            "denoms": denoms(100, 110), "classes": [klass]}


def count_routes(om):
    direct = extract_ctgov([om], ["mortality"], ["drug"], ["placebo"])
    counts = target_endpoint._counts_from_om(om, ["drug"], ["placebo"])
    candidates = target_endpoint._ctgov_candidates([om], SPEC, ["drug"], ["placebo"])
    rows = [target_endpoint.row_from_candidate(c) for c in candidates]
    return [direct, counts, *rows]


@pytest.mark.parametrize("has_class,expected", [(True, (80, 70)), (False, (100, 110))])
def test_count_readers_and_target_rows(has_class, expected):
    om = measure(has_class)
    before = copy.deepcopy(om)
    for row in count_routes(om):
        assert (row["ai"], row["ci"]) == (10, 20)
        assert (row["n1i"], row["n2i"]) == expected
        if has_class:
            assert row["n_analysis_set"] == {"n1i": 100, "n2i": 110}
        else:
            assert "n_analysis_set" not in row
    assert om == before


@pytest.mark.parametrize("has_class,n", [(True, (80, 70)), (False, (100, 110))])
def test_second_source_uses_class_denominators(has_class, n):
    row = pipeline._cross_source({"ai": 10, "n1i": n[0], "ci": 20, "n2i": n[1]},
                                 "synthetic", {"synthetic": [measure(has_class)]},
                                 SPEC, ["drug"], ["placebo"])
    assert row["ctgov_rr"] == round((10 / n[0]) / (20 / n[1]), 3)
    assert f"10/{n[0]}" in row["ctgov_source"] and f"20/{n[1]}" in row["ctgov_source"]
    assert ("n_analysis_set" in row) == has_class


@pytest.mark.parametrize("has_class,n", [(True, (80, 70)), (False, (100, 110))])
def test_harms_pipeline_uses_class_denominators(has_class, n):
    out = pipeline._build_outcome(SPEC, "harm", [{"id": "synthetic", "id_type": "pmid", "label": "plant"}],
        {"synthetic": {"id": "synthetic", "nct": "synthetic-registry", "abstract": ""}},
        ["drug"], ["placebo"], ctgov_results={"synthetic-registry": [measure(has_class)]})
    row, = out["trials"]
    assert (row["n1i"], row["n2i"]) == n
    assert ("n_analysis_set" in row) == has_class


@pytest.mark.parametrize("has_class,n", [(True, (80, 70)), (False, (100, 110))])
def test_continuous_readers_and_consumer_span(has_class, n):
    om = measure(has_class)
    om.update(paramType="MEAN", dispersionType="Standard Deviation")
    row = extract_ctgov([om], ["mortality"], ["drug"], ["placebo"])
    assert (row["nc1"], row["nc2"]) == n
    assert tuple(a["n_observed"] for a in continuous_identity.typed_measure(om)["arms"]) == n
    # Consumer selects the first nonempty class, which need not be class zero.
    om["classes"].insert(0, {"denoms": [{"counts": [{"groupId": "a", "value": "999"}]}]})
    candidate = consumer_consistency._ctgov_continuous_candidate(
        {"ctgov_results": {"synthetic": [om]}}, SPEC, "plant", {"nct": "synthetic"})
    assert f"n={n[0]}" in candidate["source_span"] and f"n={n[1]}" in candidate["source_span"]


def test_partial_class_denominators_do_not_borrow_measure_arm():
    om = measure()
    om["classes"][0]["denoms"][0]["counts"].pop()
    assert extract_ctgov([om], ["mortality"], ["drug"], ["placebo"]) is None
    assert target_endpoint._counts_from_om(om, ["drug"], ["placebo"]) is None
    assert continuous_identity.typed_measure(om)["arms"][1]["n_observed"] is None


def test_counts_are_validated_against_class_n_and_minimum_total():
    om = measure()
    om["classes"][0]["categories"][0]["measurements"][0]["value"] = "90"
    assert extract_ctgov([om], ["mortality"], ["drug"], ["placebo"]) is None
    assert target_endpoint._counts_from_om(om, ["drug"], ["placebo"]) is None
    assert extract_ctgov([measure()], ["mortality"], ["drug"], ["placebo"], min_total=180) is None


def test_reported_effect_retains_class_endpoint_counts():
    om = measure()
    om["analyses"] = [{"paramType": "Risk Ratio", "paramValue": "0.5", "ciLowerLimit": "0.3",
                       "ciUpperLimit": "0.8", "ciPctValue": "95"}]
    candidates = target_endpoint._ctgov_candidates([om], SPEC, ["drug"], ["placebo"])
    row = target_endpoint.row_from_candidate(next(c for c in candidates if c.get("effect")))
    assert row["endpoint_counts"] == {"ai": 10, "n1i": 80, "ci": 20, "n2i": 70}
    assert row["n_analysis_set"] == {"n1i": 100, "n2i": 110}
