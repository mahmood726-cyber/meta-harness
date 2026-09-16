import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import claimgraph  # noqa: E402


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX = "aa8ed28a"


def _git_json(path):
    out = subprocess.check_output(
        ["git", "-C", ROOT, "show", f"{PREFIX}:{path}"],
        text=True,
        encoding="utf-8",
    )
    return json.loads(out)


def _codes(review, registries=None):
    return [v["code"] for v in claimgraph.check(review, registries=registries)]


@pytest.mark.parametrize(
    ("slug", "code"),
    [
        ("colchicine-secondary-cv-prevention", "ROB_JOIN_MISS"),
        ("ticagrelor-vs-clopidogrel-acs", "ROB_JOIN_MISS"),
        ("spironolactone-hfref-mortality", "ROB_JOIN_MISS"),
        ("glp1-ra-mace-t2d", "ROB_JOIN_MISS"),
        ("dpp4-mace-t2d", "PROSE_PREDICATE_FALSE"),
    ],
)
def test_prefixed_named_pages_fire(slug, code):
    review = _git_json(f"docs/reviews/{slug}/review.json")
    assert code in _codes(review)


def test_prefixed_iv_iron_strands_fire():
    review = _git_json("docs/reviews/iv-iron-hfref-hosp/review.json")
    codes = set(_codes(review))
    assert {"STRAND_OUTSIDE_CLAIMS", "MEMBERSHIP_CONFLICT"} <= codes


def test_prefixed_corticosteroids_refusal_fire():
    review = _git_json("docs/reviews/corticosteroids-cap-mortality/review.json")
    refusals = _git_json("docs/refusals.json")
    assert "REFUSED_AND_POOLED" in _codes(review, registries={"refusals": refusals})


def _clean_review():
    return {
        "slug": "clean",
        "outcomes": [{
            "name": "Mortality",
            "primary": True,
            "trials": [
                {"id": "PMID 12345678", "label": "A", "ai": 1, "n1i": 10, "ci": 2, "n2i": 10},
                {"id": "PMID 22345678", "label": "B", "ai": 2, "n1i": 10, "ci": 2, "n2i": 10},
            ],
            "declared_absent_trials": [],
            "result": {"k": 2, "estimate": 0.8, "ci_low": 0.6, "ci_high": 1.1, "scale": "RR"},
        }],
        "rob2": {"trials": {"12345678": {"overall": "low"}, "22345678": {"overall": "low"}}},
        "rob_sensitivity": {"levels": {"12345678": "low", "22345678": "low"}},
    }


def test_synthetic_negative_control_clean_object():
    review = _clean_review()
    claimgraph.stamp_review(review)
    assert claimgraph.check(review) == []


def test_synthetic_positive_rob_join_miss():
    review = _clean_review()
    review["outcomes"][0]["trials"][1]["label"] = "ACRONYM"
    review["rob_sensitivity"]["levels"] = {"12345678": "low", "ACRONYM": None}
    assert "ROB_JOIN_MISS" in _codes(review)


def test_synthetic_positive_stale_dependent():
    review = _clean_review()
    claimgraph.stamp_review(review)
    review["outcomes"][0]["result"]["depends_on"]["input_set_version"] = "old"
    assert "STALE_DEPENDENT" in _codes(review)


def test_synthetic_positive_refused_and_pooled():
    review = _clean_review()
    refusals = {"clean": [{"trial": "A (PMID 12345678)", "verified": "x", "not_pooled_because": "x"}]}
    assert "REFUSED_AND_POOLED" in _codes(review, registries={"refusals": refusals})


def test_synthetic_positive_strand_outside_claims():
    review = _clean_review()
    review["strands"] = {
        "strands": [{
            "strand": "B",
            "name": "rate",
            "members": [{"trial": "A", "pmid": "12345678", "effect": 0.8, "ci_low": 0.6, "ci_high": 1.0}],
            "pool": {"k": 1, "effect": 0.8},
            "k": 1,
        }]
    }
    review["reproduction"] = {"claim_check": {"claims_checked": 0, "scope_counts": {"outcome_result": 0}}}
    assert "STRAND_OUTSIDE_CLAIMS" in _codes(review)


def test_synthetic_positive_prose_predicate_false():
    review = _clean_review()
    review["rob_sensitivity"] = {
        "full": {"k": 2, "estimate": 0.8, "ci_low": 0.6, "ci_high": 1.1, "scale": "RR"},
        "low_only": {"k": 2, "estimate": 0.8, "ci_low": 0.6, "ci_high": 1.1, "scale": "RR"},
        "low_only_informative": False,
        "levels": {"12345678": "low", "22345678": "low"},
    }
    assert "PROSE_PREDICATE_FALSE" in _codes(review)


def test_synthetic_positive_membership_conflict():
    review = _clean_review()
    review["outcomes"][0]["declared_absent_trials"] = [{"id": "PMID 22345678", "label": "B", "reason": "absent"}]
    review["strands"] = {
        "strands": [{
            "strand": "B",
            "name": "rate",
            "members": [{"trial": "B", "pmid": "22345678", "effect": 0.8, "ci_low": 0.6, "ci_high": 1.0}],
            "pool": {"k": 1, "effect": 0.8},
            "k": 1,
        }]
    }
    assert "MEMBERSHIP_CONFLICT" in _codes(review)
