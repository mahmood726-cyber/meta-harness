"""Replay only the pinned label fixture; never build reviews or access the network."""
import importlib.util
import json
from pathlib import Path
import subprocess
from collections import Counter

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "evidence/fixtures/build_derived_label_fixture.py"
spec = importlib.util.spec_from_file_location("derived_label_fixture", BUILDER)
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


@pytest.fixture(scope="module")
def replay():
    try:
        fixture.git("cat-file", "-e", fixture.PIN + "^{commit}")
    except (subprocess.CalledProcessError, OSError) as exc:
        pytest.fail(f"Required pinned commit {fixture.PIN} unavailable: {exc}")
    return fixture.build()


def test_pinned_corpus_and_report_equal_recomputation(replay):
    folder = BUILDER.parent
    expected = json.loads((folder / "derived_label_corpus.json").read_text(encoding="utf-8"))
    assert replay == expected
    assert fixture.report(replay) == (folder / "DERIVED_LABEL_FIXTURE.md").read_text(encoding="utf-8")


def test_controls_have_independent_expected_values_and_both_polarities(replay):
    groups = {}
    for control in replay["controls"]:
        assert control["name"].startswith("__control_")
        assert control["actual"] == control["expected"], control["name"]
        groups.setdefault(control["rule"], []).append(control["positive"])
    assert len(groups) == 19
    assert all(sorted(polarities) == [False, True] for polarities in groups.values())
    assert not any("__control_" in r["name"] for r in replay["records"])


def test_complete_membership_and_denominators(replay):
    assert len(replay["served_reviews"]) == 32
    # Enumerate review outcomes independently of the builder's aggregation.
    expected = []
    for slug in replay["served_reviews"]:
        review = json.loads(fixture.git("show", f"{fixture.PIN}:docs/reviews/{slug}/review.json"))
        expected.extend((slug, i, o["name"], len(o.get("trials") or [])) for i, o in enumerate(review["outcomes"]))
    assert [(r["slug"], r["outcome_index"], r["outcome"], r["trial_count"]) for r in replay["records"]] == expected
    counts = Counter(r["kind"] for r in replay["records"])
    for key, total in replay["totals"].items():
        kind, rule = key.split(".", 1)
        rows = [r for r in replay["records"] if r["kind"] == kind]
        assert total["of"] == (sum(r["trial_count"] for r in rows) if rule == "population_literal" else counts[kind])
        assert 0 <= total["fires"] <= total["of"]
        assert replay["denominators"][key]
    missing = {(x["name"], x["rule"]) for x in replay["unevaluable"]}
    for r in replay["records"]:
        if not r["trial_count"]:
            assert r["derived_label"] is None and r["tiers"] is None
            assert (r["name"], "derived_label") in missing
            assert r["pool_measure_decision"]["code"] == "POOL_MEASURE_UNIDENTIFIED"
        if r["composite_compatibility"] is None:
            assert (r["name"], "composite_compatibility") in missing
    assert all(x["name"] and x["reason"] for x in replay["unevaluable"])


def test_population_literal_precedes_dimension_derivation(replay):
    seen = 0
    for r in replay["records"]:
        for t in r["trials"]:
            if t["population_literal"]:
                dimension = r["tiers"]["per_input"][t["id"]]["analysis_set"]
                assert dimension["derived"] is True
                assert dimension["value"] == t["population_literal"]["population"]
                assert dimension["source"] == "held abstract population statement"
                seen += 1
    assert seen > 0


def test_measure_edge_controls():
    em = fixture.em
    assert em.input_label({"e1i": 0}, "OR") == "IRR"
    assert em.input_label({"mean1": 0}, "RR") == "MD"
    assert em.input_label({"ai": 0}, "RR") == "RR"
    assert em.pool_measure_decision([None, "HR"], ["UNSTATED"] * 2, None)["code"] == "POOL_MEASURE_UNIDENTIFIED"
    policy = {"allow": ["HR", "RR"], "basis": "protocol"}
    decision = em.pool_measure_decision(["HR", "RR", "HR"], ["UNSTATED"] * 3, policy)
    assert decision["label"] == "mixed ratio (HR+RR, approximation per protocol)"
    assert decision["sensitivity_restricted_to"] == "HR"
    assert em.pool_measure_decision(["HR", "RR"], ["UNSTATED"] * 2, policy)["sensitivity_restricted_to"] is None
    assert em.pool_measure_decision(["HR", "OR"], ["UNSTATED"] * 2, policy)["state"] == "REFUSED"
