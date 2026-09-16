import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import armcontrast, rob2, rob_sensitivity  # noqa: E402
from scripts.arm_contrast_build import keywords  # noqa: E402


EXSCEL_PRIMARY = [
    {
        "measure": "Primary Efficacy Outcome MACE Events",
        "description": (
            "The primary efficacy outcome variable is defined as the composite endpoint of "
            "cardiovascular death, nonfatal MI, or nonfatal stroke. The number of participants "
            "who had an event is reported in the results."
        ),
    }
]


def _committed_prefixed_glp1_review():
    raw = subprocess.check_output(
        ["git", "show", "aa8ed28a:docs/reviews/glp1-ra-mace-t2d/review.json"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    return json.loads(raw)


def test_exscel_d5_prefixed_object_fails_rederivation_with_quoted_fields():
    review = _committed_prefixed_glp1_review()
    stored = review["rob2"]["trials"]["28910237"]["domains"]["D5_selective_reporting"]

    rederived = rob2.derive_d5(EXSCEL_PRIMARY, "3-point major adverse cardiovascular events")

    assert stored["level"] == "some concerns"
    assert rederived["level"] == "low"
    comparison = rederived["inputs"]["comparison"]
    assert comparison["method"] == "component_set"
    assert comparison["pooled_components"] == ["CV_DEATH", "NONFATAL_MI", "NONFATAL_STROKE"]
    assert comparison["registered_components"] == ["CV_DEATH", "NONFATAL_MI", "NONFATAL_STROKE"]
    assert "cardiovascular death, nonfatal MI, or nonfatal stroke" in comparison["registered_text"]


def test_d5_true_registered_primary_mismatch_reproduces_some_concerns():
    stored = {"level": "some concerns"}
    rederived = rob2.derive_d5(
        [{"measure": "Hospitalization for heart failure", "description": "Time to first heart failure hospitalization."}],
        "3-point major adverse cardiovascular events",
    )
    assert rederived["level"] == "some concerns"
    assert rederived["level"] == stored["level"]


def test_d5_unknown_registry_field_is_not_assessable():
    rederived = rob2.derive_d5(["UNKNOWN"], "3-point major adverse cardiovascular events")
    assert rederived["level"] == "not_assessable"
    assert rederived["level"] not in {"low", "some concerns"}


def test_exscel_arm_parser_prefixed_class_terms_fail_postfix_agent_alias_confirms():
    index = {"NCT01144338": (set(), {"exenatide once weekly"})}

    pre_status, pre_basis = armcontrast.contrast_status("NCT01144338", ["GLP-1 receptor agonist"], index)
    post_status, post_basis = armcontrast.contrast_status(
        "NCT01144338",
        keywords("glp1-ra-mace-t2d"),
        index,
    )

    assert pre_status == "unverified_granularity"
    assert "not machine-matchable" in pre_basis
    assert post_status == "verified"
    assert "exenatide" in post_basis.lower()
    assert "exenatide once weekly" in post_basis.lower()


def test_rob_sensitivity_joins_on_pmid_when_display_label_differs():
    review = {
        "outcomes": [
            {
                "primary": True,
                "name": "3-point major adverse cardiovascular events",
                "estimand": "HR",
                "trials": [
                    {"id": "PMID 1", "label": "1", "effect": 0.9, "ci_low": 0.8, "ci_high": 1.0, "scale": "HR"},
                    {"id": "PMID 2", "label": "SOUL", "effect": 0.86, "ci_low": 0.77, "ci_high": 0.96, "scale": "HR"},
                ],
            }
        ],
        "rob2": {
            "trials": {
                "1": {"overall": "low (on assessed domains; some domains require human judgement)"},
                "2": {"overall": "low (on assessed domains; some domains require human judgement)"},
            }
        },
    }
    sens = rob_sensitivity.sensitivity(review)
    assert sens["n_rob_rated"] == 2
    assert sens["low_only"]["k"] == 2
