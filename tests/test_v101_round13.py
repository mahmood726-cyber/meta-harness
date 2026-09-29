"""V1.0.1 round 13 (Mahmood 2026-09-29, "use codex. hard"): the registry-match paired plant as harness code, and the
recorded two-reader codex workloads (screening normalisation for the k-gap lane, comparator trial-identity overlap)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
Q = ROOT / "registry" / "model_proposals"


def test_paired_plants_fire_on_the_prefix_record_and_not_on_this_harness():
    pre = json.loads((ROOT / "evidence/v101_integrated/round13_plants/prefix_834c6d83.json").read_text(encoding="utf-8"))
    qs = [k for k in pre if k.startswith("Q")]
    assert len(qs) == 12 and all(pre[k]["fired"] for k in qs)
    assert not any(v["fired"] for k, v in pre.items() if k.startswith("C"))
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "plants_round13.py"), "--harness-root", str(ROOT)],
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    assert not any(v["fired"] for v in json.loads(out).values())


def test_both_directions_are_planted():
    pre = json.loads((ROOT / "evidence/v101_integrated/round13_plants/prefix_834c6d83.json").read_text(encoding="utf-8"))
    reassurance = [k for k in pre if k.startswith("Q") and pre[k]["got"]["matched"]]
    concern = [k for k in pre if k.startswith("Q") and not pre[k]["got"]["matched"]]
    assert len(reassurance) >= 5 and len(concern) >= 5


def test_the_corpus_score_never_creates_a_disagreement():
    d = json.loads((ROOT / "evidence/v101_integrated/round13_codex/d5_remaining.json").read_text(encoding="utf-8"))
    assert d["created"] == [] and d["disagree_before"] == 83 and d["disagree_after"] == len(d["remaining"]) < 30


def test_the_sacubitril_rob_downgrade_is_held_not_removed_unsigned():
    rev = json.loads((ROOT / "docs/reviews/sacubitril-valsartan-hfref/review.json").read_text(encoding="utf-8"))
    rob = rev["grade"]["domains"]["risk_of_bias"]
    assert rob["downgrade"] == 1 and rob["computed_downgrade"] == 0 and rev["grade"]["downgrades"] == 3


@pytest.mark.parametrize("task,n", [("screen_eligibility", 55), ("screen_x1", 28), ("overlap_identity", 93)])
def test_every_workload_has_two_recorded_readers_on_one_frozen_population(task, n):
    pop = json.loads((Q / f"{task}.population.json").read_text(encoding="utf-8"))["items"]
    r1 = json.loads((Q / f"{task}.json").read_text(encoding="utf-8"))["items"]
    r2 = json.loads((Q / f"{task}_reader2.json").read_text(encoding="utf-8"))["items"]
    assert len(pop) == len(r1) == len(r2) == n
    assert {e["item_id"] for e in r1} == {e["item_id"] for e in r2} == {i["item_id"] for i in pop}
    assert all(e.get("status") == "PROPOSED" for e in r1 + r2)          # nothing a model says enters a build


def test_the_kgap_handoff_is_the_two_readings_verbatim():
    h = json.loads((ROOT / "evidence/v101_integrated/round13_codex/screen_eligibility_for_kgap.json").read_text(encoding="utf-8"))
    r1 = {e["item_id"]: e for e in json.loads((Q / "screen_eligibility.json").read_text(encoding="utf-8"))["items"]}
    for row in h["rows"]:
        assert row["reader1"]["verdict"] == (r1[row["item_id"]].get("verification") or {}).get("model_decision")
        assert row["status"].startswith("PROPOSED")
