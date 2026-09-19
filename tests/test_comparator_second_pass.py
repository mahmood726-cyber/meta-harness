import json
import os
import subprocess

from harness import comparator_second_pass


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "aa8ed28a"


def _git_json(path):
    data = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)
    return json.loads(data.decode("utf-8"))


def _topic(slug):
    with open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8") as f:
        return json.load(f)


def _records(slug):
    with open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8") as f:
        return json.load(f)


def _comp_rec(slug):
    config = _topic(slug)
    records = _records(slug)
    by_id = {str(r.get("id")): r for r in records.get("records", [])}
    return by_id.get(str(config.get("comparator_pmid")), {})


def _analysis(slug):
    config = _topic(slug)
    records = _records(slug)
    return comparator_second_pass.analyze(slug, config, records, _comp_rec(slug))


def _applied_to_prefix(slug):
    old = _git_json(f"docs/reviews/{slug}/review.json")
    config = _topic(slug)
    records = _records(slug)
    return comparator_second_pass.apply(slug, config, records, _comp_rec(slug), old["comparator"])


def test_PLANT_noac_not_machine_exposed_refused_when_text_enumerates_four_trials():
    old = _git_json("docs/reviews/noac-vs-warfarin-af-stroke/review.json")
    old_shared = old["comparator"]["overlap"]["shared_k"]
    assert "not exactly verifiable" in old_shared

    fixed = _applied_to_prefix("noac-vs-warfarin-af-stroke")
    assert fixed["comparator_trial_set"]["status"] == "MEASURED"
    assert fixed["comparator_trial_set"]["k"] == 4
    # Enumeration proves the comparator set, not its intersection with a current pool.
    assert fixed["overlap"]["shared_k"] == comparator_second_pass.UNMEASURED_CURRENT_POOL
    assert fixed["overlap"]["shared_k"].startswith("not exactly verifiable")
    assert fixed["overlap"]["shared_k_measurement"] == "NOT_MEASURED"
    assert fixed["quantity_match"]["status"] == "SAME_SET_DIFFERENT_QUANTITY"


def test_colchicine_secondary_recency_fires_for_clear_synergy():
    recency = _analysis("colchicine-secondary-cv-prevention")["comparator_recency"]
    assert recency["status"] == "COMPARATOR_PREDATES_POOLED_TRIAL(CLEAR SYNERGY)"


def test_PLANT_zhang_k3_parser_is_refused_by_table_count():
    old = _git_json("docs/reviews/sglt2-primary-prevention-hf/review.json")
    assert old["comparator"]["overlap"]["theirs_k"] == 3

    fixed = _applied_to_prefix("sglt2-primary-prevention-hf")
    assert fixed["comparator_trial_set"]["status"] == "MEASURED"
    assert fixed["overlap"]["theirs_k"] == 8
    assert fixed["overlap"]["shared_k"] == 4
    assert fixed["overlap"]["shared_k_measurement"] == "MEASURED"
    assert fixed["scope"]["scope_valid"] is False
    assert "DAPA-HF" in fixed["scope"]["note"]


def test_metformin_strategy_mismatch_fires_and_uses_add_on_contrast():
    old = _git_json("docs/reviews/metformin-pcos-ovulation/review.json")
    old_ovulation = next(r for r in old["comparator"]["reported"] if r["outcome"] == "Ovulation rate")
    assert old_ovulation["estimate"] == 2.64

    fixed = _applied_to_prefix("metformin-pcos-ovulation")
    assert fixed["treatment_strategy_match"]["status"] == "MISMATCH_CORRECTED"
    ovulation = next(r for r in fixed["reported"] if r["outcome"] == "Ovulation rate")
    assert ovulation["estimate"] == 1.65
    gi = next(r for r in fixed["reported"] if r["outcome"] == "Gastrointestinal adverse events")
    assert gi["estimate"] == 4.26


def test_control_true_no_enumeration_stays_not_exposed():
    fixed = _applied_to_prefix("denosumab-vertebral-fracture")
    assert fixed["comparator_trial_set"]["status"] == "NOT_EXPOSED"
    assert fixed["overlap"]["shared_k"] == comparator_second_pass.NOT_EXPOSED
    assert fixed["overlap"]["shared_k_measurement"] == "MEASURED_ABSENCE"


def test_control_noac_has_no_recency_flag_when_comparator_is_current_for_pool():
    recency = _analysis("noac-vs-warfarin-af-stroke")["comparator_recency"]
    assert recency["status"] == "NO_RECENCY_FLAG"
