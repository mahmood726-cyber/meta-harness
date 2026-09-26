"""The served OUTCOME label is derived from the pooled inputs; PRIMARY / EXPLORATORY tiers (external review of colchicine-postop-af,
2026-09-26). Real served rows at the pinned candidate 3876a62d (immutable; a missing commit is a failure, not a skip)."""
import copy
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import outcome_tiers as ot   # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
POLICY = {"common_outcome_policy": {"follow_up_window": ["in-hospital / until discharge"], "predeclared": True,
                                    "decided_by": "test", "decided_on": "2026-09-26", "rationale": "synthetic control"}}


def _primary(slug):
    p = subprocess.run(["git", "show", f"{PINNED}:docs/reviews/{slug}/review.json"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        pytest.fail(f"{PINNED[:8]} not in history (never a skip)", pytrace=False)
    return next(o for o in json.loads(p.stdout)["outcomes"] if o.get("primary"))


def test_the_served_label_states_one_window_over_three_the_inputs_show():
    o = _primary("colchicine-postop-af")
    assert o["timepoint"] == "in-hospital / index-admission" and o["population"] == "intention-to-treat"
    lab = ot.tiers(o, o["trials"], {})["derived_label"]
    assert lab["follow_up_window"]["state"] == "MIXED"
    assert lab["follow_up_window"]["values"] == ["14 days / postoperative admission", "3 months", "in-hospital / until discharge"]
    assert lab["analysis_set"]["state"] == "NOT_SHOWN" and "not shown for 2 of 3 inputs" in lab["analysis_set"]["label"]
    assert lab["endpoint_definition"]["state"] == "MIXED"                    # >=5 min vs >=30 s vs not stated
    assert lab["matches_inputs"] is False


def test_a_value_copied_from_the_label_never_confirms_it():
    o = _primary("glp1-ra-mace-t2d")
    lab = ot.tiers(o, o["trials"], {})["derived_label"]
    assert lab["follow_up_window"]["state"] == "NOT_SHOWN" and "trial end" not in [lab["follow_up_window"].get("label")]
    copied = [t for t in o["trials"] if (t.get("compat_dimensions") or {}).get("follow_up_window", {}).get("source") == "outcome.timepoint"]
    assert copied and all(not ot.input_dimensions(t)["follow_up_window"]["derived"] for t in copied)


def test_no_policy_means_no_primary_tier_and_an_exploratory_title():
    o = _primary("colchicine-postop-af")
    t = ot.tiers(o, o["trials"], {})
    assert t["primary"]["state"] == "NO_POLICY_DECLARED" and t["primary"]["trials"] == []
    assert t["exploratory"]["trials"] == [x["id"] for x in o["trials"]]     # every eligible input stays, none re-decided
    assert t["exploratory"]["title"].startswith("Exploratory: trial-defined Postoperative atrial fibrillation across windows")
    assert "index-admission" not in t["exploratory"]["title"]               # a copied value never titles


def test_a_predeclared_policy_admits_only_inputs_whose_derived_values_satisfy_it():
    o = _primary("colchicine-postop-af")
    t = ot.tiers(o, o["trials"], POLICY)
    assert t["primary"]["state"] == "POLICY_APPLIED" and t["primary"]["trials"] == ["PMID 32720823"]        # END-AF, until discharge
    assert sorted(e["trial"] for e in t["primary"]["excluded"]) == ["PMID 25172965", "PMID 42132185"]
    assert t["exploratory"]["trials"] == [x["id"] for x in o["trials"]]


def test_a_copied_value_never_satisfies_a_policy():
    o = _primary("glp1-ra-mace-t2d")
    pol = {"common_outcome_policy": {**POLICY["common_outcome_policy"], "follow_up_window": ["trial end"]}}
    t = ot.tiers(o, o["trials"], pol)
    admitted = set(t["primary"]["trials"])
    for tr in o["trials"]:
        if (tr.get("compat_dimensions") or {}).get("follow_up_window", {}).get("source") == "outcome.timepoint":
            assert tr["id"] not in admitted


@pytest.mark.parametrize("bad", [
    {"follow_up_window": ["x"], "decided_by": "a", "decided_on": "d", "rationale": "r"},              # not predeclared
    {"follow_up_window": ["x"], "predeclared": True, "decided_on": "d", "rationale": "r"},             # no decider
    {"predeclared": True, "decided_by": "a", "decided_on": "d", "rationale": "r"},                    # constrains nothing
])
def test_an_incomplete_policy_is_no_policy(bad):
    assert ot.common_policy({"common_outcome_policy": bad}) is None


def test_a_fully_derived_consistent_input_set_matches():
    o = _primary("melatonin-primary-insomnia-sol")
    assert ot.tiers(o, o["trials"], {})["derived_label"]["matches_inputs"] is True
