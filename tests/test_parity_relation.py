import json
import os
import subprocess

import pytest

from harness import parity_relation

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BASE = "aa8ed28a"


def _git_json(path):
    data = subprocess.check_output(["git", "show", f"{_BASE}:{path}"], cwd=_ROOT)
    return json.loads(data.decode("utf-8"))


def _prefix_review(slug):
    return _git_json(f"docs/reviews/{slug}/review.json")


def _prefix_parity_row(slug):
    rows = _git_json("docs/parity.json")
    return next(r for r in rows if r["slug"] == slug)


@pytest.mark.parametrize(
    ("slug", "relation"),
    [
        ("pcsk9-mace", "DOMINANT_SUBSET"),
        ("ticagrelor-vs-clopidogrel-acs", "SUPERSET"),
    ],
)
def test_PLANT_prefix_hand_parity_status_refused(slug, relation):
    rel = parity_relation.compute(_prefix_parity_row(slug), _prefix_review(slug))
    assert rel["relation"] == relation
    assert rel["hand_status_disagrees"] is True


def test_PLANT_prefix_invalid_comparator_scope_refused():
    review = _prefix_review("statins-primary-prevention-elderly")
    row = _prefix_parity_row("statins-primary-prevention-elderly")
    assert review["comparator"]["scope"]["scope_valid"] is True
    assert parity_relation.compute(row, review)["relation"] == "COMPARATOR_INVALID"
    assert parity_relation.scope_consistency_errors(row, review)


@pytest.mark.parametrize(
    "slug",
    ["noac-vs-warfarin-af-stroke", "finerenone-ckd-t2d-renal", "sglt2-hfref-hosp-cvdeath"],
)
def test_PLANT_identical_trial_set_is_replication(slug):
    rel = parity_relation.compute(_prefix_parity_row(slug), _prefix_review(slug))
    assert rel["relation"] == "IDENTICAL_SET"
    assert "arithmetic agreement" in rel["label"]


def test_PLANT_prefix_external_agreement_said_agrees_for_same_set():
    old = _git_json("docs/external_agreement.json")
    noac = next(r for r in old["rows"] if r["slug"] == "noac-vs-warfarin-af-stroke")
    assert noac["category"] == "same_estimand_agree"
    assert noac["agree_within_12pct"] is True

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "external_agreement", os.path.join(_ROOT, "scripts", "external_agreement.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fixed = mod._classify("noac", 0.8069, "HR", 0.81, "HR", "stroke",
                          "IDENTICAL_SET",
                          "arithmetic replication -- same trials; agreement is not independent corroboration")
    assert fixed["category"] == "same_estimand_replication"
    assert fixed["agree_within_12pct"] is False
    assert fixed["agreement_basis"] == "arithmetic_replication"


@pytest.mark.parametrize(
    ("row", "review", "relation"),
    [
        ({"our_k": 2, "comparable_comparator_k": 2, "status": "IDENTICAL_SET"}, {}, "IDENTICAL_SET"),
        (
            {"our_k": 2, "comparable_comparator_k": 12, "status": "DOMINANT_SUBSET",
             "reason": "2/12; ours carry ~87% of patients"},
            {},
            "DOMINANT_SUBSET",
        ),
        ({"our_k": 2, "comparable_comparator_k": 5, "status": "SUBSET"}, {}, "SUBSET"),
        ({"our_k": 5, "comparable_comparator_k": 2, "status": "SUPERSET"}, {}, "SUPERSET"),
        (
            {"our_k": 5, "comparable_comparator_k": 7, "status": "OVERLAPPING"},
            {"comparator": {"overlap": {"shared_k": "not exactly verifiable", "only_ours": ["A"]}}},
            "OVERLAPPING",
        ),
        (
            {"our_k": 2, "comparable_comparator_k": 3, "status": "DISTINCT"},
            {"comparator": {"overlap": {"shared_k": 0}}},
            "DISTINCT",
        ),
        (
            {"our_k": 2, "comparable_comparator_k": 0, "status": "COMPARATOR_INVALID",
             "reason": "not an RCT meta"},
            {},
            "COMPARATOR_INVALID",
        ),
        ({"our_k": 1, "comparable_comparator_k": None, "status": "NOT_ENUMERABLE"}, {}, "NOT_ENUMERABLE"),
    ],
)
def test_synthetic_controls_cover_every_relation(row, review, relation):
    rel = parity_relation.compute(row, review)
    assert rel["relation"] == relation
    assert rel["hand_status_disagrees"] is False
