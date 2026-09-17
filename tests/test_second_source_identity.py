import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.pipeline import _cross_source, build_review_core  # noqa: E402
from harness.registration import protocol_sha  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _git_json(commit, path):
    return json.loads(subprocess.check_output(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    ))


def _load_json(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return json.load(f)


def _core(slug):
    return build_review_core(
        slug,
        _load_json("topics", slug + ".json"),
        _load_json("cache", slug, "records.json"),
        protocol_sha(slug),
    )


def _row(review, label):
    outcome = next(o for o in review["outcomes"] if o.get("name") == "Major adverse cardiovascular events")
    return next(t for t in outcome["trials"] if t.get("label") == label)


def _om(ai, n1, ci, n2, title="All-cause mortality"):
    return {
        "title": title,
        "description": "All-cause mortality.",
        "type": "PRIMARY",
        "paramType": "COUNT_OF_PARTICIPANTS",
        "groups": [{"id": "g1", "title": "Drug"}, {"id": "g2", "title": "Placebo"}],
        "classes": [{"categories": [{"measurements": [
            {"groupId": "g1", "value": str(ai)},
            {"groupId": "g2", "value": str(ci)},
        ]}]}],
        "denoms": [{"units": "Participants", "counts": [
            {"groupId": "g1", "value": str(n1)},
            {"groupId": "g2", "value": str(n2)},
        ]}],
    }


def test_aa8ed28a_served_fourier_and_odyssey_corroboration_has_no_identity_gate():
    review = _git_json("aa8ed28a", "docs/reviews/pcsk9-mace/review.json")
    fourier = _row(review, "28304224")["cross_source"]
    odyssey = _row(review, "30403574")["cross_source"]

    assert fourier["ctgov_rr"] == 0.666
    assert "shown for corroboration only" in fourier["note"]
    assert "identity" not in fourier
    assert odyssey["ctgov_rr"] == 0.818
    assert "shown for corroboration only" in odyssey["note"]
    assert "identity" not in odyssey


def test_ad5e7c66_odyssey_percentage_ratio_was_still_labelled_corroboration():
    review = _git_json("ad5e7c66", "docs/reviews/pcsk9-mace/review.json")
    fourier = _row(review, "28304224")["cross_source"]
    odyssey = _row(review, "30403574")["cross_source"]

    assert fourier["registry_measure_type"] == "KM_ESTIMATE"
    assert fourier["corroborates_endpoint"] is False
    assert "identity" not in fourier
    assert odyssey["registry_measure_type"] == "PERCENTAGE"
    assert odyssey["endpoint_match"] == "SAME_ENDPOINT"
    assert odyssey["corroborates_endpoint"] is True
    assert "identity" not in odyssey


def test_postfix_pcsk9_second_source_rows_are_different_measure_not_corroboration():
    core = _core("pcsk9-mace")
    fourier = _row(core, "28304224")["cross_source"]
    odyssey = _row(core, "30403574")["cross_source"]

    assert fourier["ctgov_rr"] == 0.887
    assert fourier["registry_title"] == "Time to Cardiovascular Death, Myocardial Infarction, or Stroke"
    assert fourier["endpoint_match"] == "SECOND_SOURCE_DIFFERENT_MEASURE"
    assert fourier["identity"]["verdict"] == "SECOND_SOURCE_DIFFERENT_MEASURE"
    assert fourier["identity"]["title_match"] is True
    assert fourier["identity"]["component_match"] is True
    assert fourier["identity"]["measure_type"] == "KM estimate ratio"
    assert fourier["corroborates_endpoint"] is False

    assert odyssey["ctgov_rr"] == 0.856
    assert odyssey["endpoint_match"] == "SECOND_SOURCE_DIFFERENT_MEASURE"
    assert odyssey["identity"]["measure_type"] == "percentage ratio"
    assert odyssey["registry_effect_label"] == "CT.gov percentage ratio"
    assert odyssey["corroborates_endpoint"] is False


def test_served_fourier_0666_is_value_not_reproducible_from_current_cache():
    old = _row(_git_json("aa8ed28a", "docs/reviews/pcsk9-mace/review.json"), "28304224")["cross_source"]
    rebuilt = _row(_core("pcsk9-mace"), "28304224")["cross_source"]

    assert old["ctgov_rr"] == 0.666
    assert "2/13784" in old["ctgov_source"]
    assert rebuilt["ctgov_rr"] == 0.887
    assert rebuilt["registry_intervention_value"] == 1.65
    assert rebuilt["registry_comparator_value"] == 1.86


def test_synthetic_identical_endpoint_allows_corroboration():
    cs = _cross_source(
        {"ai": 80, "n1i": 1000, "ci": 100, "n2i": 1000},
        "NCT1",
        {"NCT1": [_om(80, 1000, 100, 1000)]},
        {"name": "All-cause mortality", "keywords": ["all-cause mortality", "mortality"], "population": "intention-to-treat"},
        ["drug"],
        ["placebo"],
    )
    assert cs["endpoint_match"] == "IDENTICAL_ENDPOINT"
    assert cs["identity"] == {
        "title_match": True,
        "component_match": True,
        "measure_type": "risk ratio from counts",
        "population_match": True,
        "verdict": "IDENTICAL_ENDPOINT",
    }
    assert cs["corroborates_endpoint"] is True
    assert cs["ctgov_rr"] == 0.8
