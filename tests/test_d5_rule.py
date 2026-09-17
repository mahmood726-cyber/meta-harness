from __future__ import annotations

import json
import os
import subprocess
import sys
from functools import lru_cache

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import rob2  # noqa: E402

BASE_REF = "ad5e7c66"

TARGETS = {
    "sglt2-primary-prevention-hf": ["28605608"],
    "glp1-ra-mace-t2d": ["28910237"],
    "doac-vte-recurrence": ["21128814"],
    "esketamine-trd-madrs": ["37025256", "31109201", "NCT02422186", "NCT02417064"],
    "sglt2-ckd-progression": ["32970396", "30990260", "36331190"],
}


def _git_json(path: str) -> dict:
    raw = subprocess.check_output(
        ["git", "show", f"{BASE_REF}:{path}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    return json.loads(raw)


def _read_json(*parts: str) -> dict:
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def _case_index() -> dict[tuple[str, str], dict]:
    cases = {}
    for slug, pids in TARGETS.items():
        review = _git_json(f"docs/reviews/{slug}/review.json")
        measured = _read_json("cache", slug, "rob2.json")["trials"]
        primary = next(o for o in review.get("outcomes", []) if o.get("primary"))
        trials = {str(t.get("id", "")).replace("PMID ", ""): t for t in primary.get("trials", [])}
        for pid in pids:
            trial = trials[pid]
            stored = review["rob2"]["trials"][pid]["domains"]["D5_selective_reporting"]
            # Re-run the rule from measured registry inputs, not its saved verdict
            # and not an off-tree snapshot. Assertions below remain unchanged.
            inputs = measured[pid]["domains"]["D5_selective_reporting"]["inputs"]
            cases[(slug, pid)] = {
                "pooled": primary["name"], "stored": stored, "trial": trial,
                "primaries": inputs["registered_primary_outcomes"],
                "secondaries": inputs["registered_secondary_outcomes"],
            }
    return cases


def _derive(slug: str, pid: str) -> tuple[dict, dict]:
    case = _case_index()[(slug, pid)]
    d5 = rob2.derive_d5(case["primaries"], case["pooled"], None, case["secondaries"])
    return case["stored"], d5


def _print_case(slug: str, pid: str, stored: dict, post: dict) -> None:
    registered = post["inputs"]["comparison"]["registered_text"]
    registered_ascii = registered.encode("ascii", "backslashreplace").decode("ascii")
    print(f"{slug} {pid}: pre={stored['level']} post={post['level']} registered={registered_ascii}")


def test_d5_named_false_positives_are_no_longer_some_concerns():
    cases = [
        ("glp1-ra-mace-t2d", "28910237", "Primary Efficacy Outcome MACE Events"),
        ("doac-vte-recurrence", "21128814", "Symptomatic Recurrent Venous Thromboembolism"),
        ("sglt2-primary-prevention-hf", "28605608", "Hospitalization for Heart Failure"),
        ("esketamine-trd-madrs", "37025256", "Montgomery Asberg Depression Rating Scale"),
        ("esketamine-trd-madrs", "31109201", "Montgomery-Asberg Depression Rating Scale"),
        ("esketamine-trd-madrs", "NCT02422186", "Montgomery Asberg Depression Rating Scale"),
        ("esketamine-trd-madrs", "NCT02417064", "Montgomery-Asberg Depression Rating Scale"),
    ]
    for slug, pid, registered_fragment in cases:
        stored, post = _derive(slug, pid)
        comparison = post["inputs"]["comparison"]
        _print_case(slug, pid, stored, post)
        assert stored["level"] == "some concerns"
        assert post["level"] == "low"
        assert post["level"] != "some concerns"
        assert registered_fragment.lower() in comparison["registered_text"].lower()


def test_d5_positive_controls_stay_low():
    cases = [
        ("sglt2-ckd-progression", "32970396", "Sustained Decline in eGFR"),
        ("sglt2-ckd-progression", "30990260", "End-stage Kidney Disease"),
        ("sglt2-ckd-progression", "36331190", "Kidney Disease Progression"),
    ]
    for slug, pid, registered_fragment in cases:
        stored, post = _derive(slug, pid)
        comparison = post["inputs"]["comparison"]
        _print_case(slug, pid, stored, post)
        assert stored["level"] == "low"
        assert post["level"] == "low"
        assert comparison["registered_type"] == "primary"
        assert registered_fragment.lower() in comparison["registered_text"].lower()


def test_d5_synthetic_unregistered_and_absent_registry_fail_closed():
    unregistered = rob2.derive_d5(
        [{"measure": "Systolic blood pressure at 12 weeks"}],
        "Change in MADRS",
        None,
        [{"measure": "Clinical Global Impression-Severity"}],
    )
    assert unregistered["level"] == "some concerns"

    absent = rob2.derive_d5([], "Change in MADRS", None, [])
    assert absent["level"] == "not_assessable"

    unknown = rob2.derive_d5(["UNKNOWN"], "Change in MADRS", None, [])
    assert unknown["level"] == "not_assessable"
