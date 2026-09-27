"""Pinned census replay and synthetic contracts; no network and no skipped history."""
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evidence.fixtures.build_continuous_fixture import (  # noqa: E402
    PINNED, PinnedDataError, build_fixture, render_report,
)


@pytest.fixture(scope="module")
def corpus():
    try:
        return build_fixture()
    except PinnedDataError as exc:
        pytest.fail(f"Required pinned history {PINNED} unavailable: {exc}", pytrace=False)


def test_fixture_recomputes_exactly(corpus):
    expected = json.loads((ROOT / "evidence/fixtures/continuous_corpus.json").read_text(encoding="utf-8"))
    assert corpus == expected
    assert render_report(corpus) == (ROOT / "evidence/fixtures/CONTINUOUS_FIXTURE.md").read_text(encoding="utf-8")


def test_complete_pinned_membership_and_denominators(corpus):
    assert corpus["review_count"] == 32
    assert len({r["slug"] for r in corpus["review_inventory"]}) == 32
    rows = corpus["rows"]
    assert len({r["key"] for r in rows}) == len(rows)
    for outcome in corpus["outcomes"]:
        selected = [r for r in rows if r["outcome_key"] == outcome["key"]]
        assert len(selected) == len(outcome["included_ids"])
        assert all(r["analysis_plan"] == outcome["analysis_plan"] for r in selected)
    for prop in rows[0]["properties"]:
        assert corpus["totals"][prop] == {
            "fires": sum(r["properties"][prop] is True for r in rows), "of": len(rows)}
        assert corpus["unevaluable"][prop] == [r["key"] for r in rows if r["properties"][prop] is None]
    assert all(not r["key"].startswith("__control_") for r in rows)
    assert all(r["unevaluable_reason"] for r in rows if r["typed_measure"] is None)
    for row in rows:
        if row["typed_measure"]:
            assert row["registry_measure_title"] == row["typed_measure"]["title"]
            assert all({"mean_change", "dispersion_kind", "n_observed", "n_analysis_set"} <= set(a)
                       for a in row["typed_measure"]["arms"])
        assert all(p["basis"] for p in row["ci_procedures"])


def test_se_label_is_refused(corpus):
    assert corpus["controls"]["__control_se_dispersion"]["result"] is None


def test_ci_procedure_controls(corpus):
    controls = corpus["controls"]
    flexible = controls["__control_median_unbiased"]
    standard = controls["__control_flexible_doses"]
    assert flexible["procedure"]["procedure"] == "STAGE_WEIGHTED_FLEXIBLE"
    assert flexible["procedure"]["basis"] == "held text"
    assert flexible["refused"] and flexible["se"] is None
    assert standard["procedure"]["procedure"] == "STANDARD_FIXED_LEVEL_TWO_SIDED"
    assert not standard["refused"]
    assert standard["se"] == pytest.approx(4 / 3.92, rel=0.0001)


def test_three_arms_and_partial_rule(corpus):
    control = corpus["controls"]["__control_three_arms"]
    assert control["without_rule"] is None
    assert control["partial_rule"] is None
    result = control["with_rule"]
    assert (result["mean1"], result["nc1"], result["mean2"], result["nc2"]) == (1.5, 40, 3, 20)
    # Independent pooled-variance calculation includes between-dose spread.
    assert result["sd1"] == pytest.approx(((19 * 4 + 19 * 4 + 10) / 39) ** 0.5, abs=0.00005)
    assert result["nc1"] + result["nc2"] == 60
    assert result["multi_arm_combined"]["shared_comparator"]["counted"] == "once"
    assert len(result["multi_arm_combined"]["arms"]) == 2


def test_class_denominators_win(corpus):
    control = corpus["controls"]["__control_class_denominators"]
    result = control["result"]
    assert (result["nc1"], result["nc2"]) == (11, 12)
    assert result["n_analysis_set"] == {"nc1": 20, "nc2": 20}
    assert [(a["n_observed"], a["n_analysis_set"]) for a in control["typed"]["arms"]] == [(11, 20), (12, 20)]


def test_transform1_continuous_refusal_is_distinct_from_wrapper_fallback(corpus):
    row = next(r for r in corpus["rows"] if r["id"] == "NCT02417064")
    assert row["served_state"] == "ABSENT"
    assert row["continuous_extractor_without_rule"] is None
    assert row["continuous_extractor_with_rule"]["nc1"] == 209
    assert row["continuous_extractor_with_rule"]["nc2"] == 108
    assert row["extractor_without_rule"]["registry_measure_type"] == "PERCENTAGE"
    assert row["extractor_without_rule"]["registry_title"] != row["registry_measure_title"]
    assert row["hand_override_corroborated"] is True
    assert row["properties"]["continuous_extracts_without_rule"] is False
    assert row["properties"]["combine_rule_rescues"] is True


def test_control_an_se_is_refused_by_arm_sd_itself_and_by_the_combine_path():
    """Verifier-added: the SE control above goes through the extractor, which refuses on the dispersion LABEL before arm_sd is
    reached. This one guards arm_sd and the combine path directly (a mutation letting arm_sd accept an SE left the fixture green)."""
    import pytest as _pt
    from harness import continuous_identity as _ci
    with _pt.raises(_ci.NotAnArmSD):
        _ci.arm_sd(1.69, "SE")
    with _pt.raises(_ci.NotAnArmSD):
        _ci.combine_arms([{"mean": -19.0, "sd": 1.3, "dispersion_kind": "SE", "n": 111},
                          {"mean": -18.8, "sd": 1.4, "dispersion_kind": "SE", "n": 98}])
