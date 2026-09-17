import functools
import json
import subprocess
from pathlib import Path

from harness import aact, invalidation, pipeline, screen


BASE = "aa8ed28a"
ROOT = Path(__file__).resolve().parents[1]


def _json(path):
    return json.load(open(ROOT / path, encoding="utf-8"))


def _pre_screen(slug):
    cp = subprocess.run(
        ["git", "show", f"{BASE}:docs/reviews/{slug}/review.json"],
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    rows = (json.loads(cp.stdout).get("screening") or {}).get("records") or []
    return {pipeline._clean_record_id(r.get("id")): r for r in rows}


def _config_for_build(slug):
    config = _json(f"topics/{slug}.json")
    if "contrast_evictions" not in config:
        rows = ((_json("docs/contrast_evictions.json").get("topics") or {}).get(slug) or [])
        if rows:
            config = dict(config, contrast_evictions=rows)
    rows = ((_json("docs/study_families.json").get("topics") or {}).get(slug) or [])
    if rows:
        existing = list(config.get("companion_reports") or [])
        have = {str(c.get("pmid")) for c in existing}
        existing += [r for r in rows if str(r.get("pmid")) not in have]
        config = dict(config, companion_reports=existing)
    return config


@functools.lru_cache(maxsize=None)
def _current_screen(slug):
    config = _config_for_build(slug)
    records = _json(f"cache/{slug}/records.json")
    merged = pipeline._dedup(records, config.get("pivotal_trials"))
    rows = screen.run(merged, config)["decisions"]
    return {pipeline._clean_record_id(r.get("id")): r for r in rows}


def test_required_prefixed_plants_transition_on_current_replay():
    old = _pre_screen("sglt2-ckd-progression")
    new = _current_screen("sglt2-ckd-progression")
    assert old["NCT06350123"]["decision"] == "include"
    assert new["NCT06350123"]["decision"] == "exclude"
    assert new["NCT06350123"]["rule_id"] == "X-CONTRAST"
    assert "Balcinrenone" in new["NCT06350123"]["reason"]
    assert "Dapagliflozin" in new["NCT06350123"]["reason"]

    assert old["NCT03190694"]["rule_id"] == "X2"
    assert new["NCT03190694"]["decision"] == "include"

    old = _pre_screen("metformin-pcos-ovulation")
    new = _current_screen("metformin-pcos-ovulation")
    assert old["19552097"]["decision"] == "exclude"
    assert old["19552097"]["rule_id"] == "X2"
    assert new["19552097"]["decision"] == "include"
    assert "polycystic ovary syndrome" in new["19552097"]["span"].lower()
    assert screen._has(
        "metformin and clomiphene citrate in non-obese women with polycystic ovary syndrome",
        ["polycystic ovary syndrome"],
    )

    old = _pre_screen("noac-vs-warfarin-af-stroke")
    new = _current_screen("noac-vs-warfarin-af-stroke")
    assert old["NCT02935855"]["decision"] == "include"
    assert new["NCT02935855"]["decision"] == "exclude"
    assert new["NCT02935855"]["rule_id"] == "X1"
    assert "consecutive patients" in new["NCT02935855"]["reason"]
    assert old["NCT05006287"]["decision"] == "include"
    assert new["NCT05006287"]["decision"] == "exclude"
    assert new["NCT05006287"]["rule_id"] == "X2"
    assert "Cardiac Surgery" in new["NCT05006287"]["span"]


def test_genuine_drug_vs_placebo_record_stays_include():
    row = _current_screen("sglt2-ckd-progression")["NCT07060417"]
    assert row["decision"] == "include"
    assert row["rule_id"] == "INCLUDE"
    assert "placebo" in row["reason"].lower()


def test_completeness_states_gate_eligible_declared_absent():
    records = _json("cache/sglt2-ckd-progression/records.json")
    recs = {r.get("id"): r for r in pipeline._dedup(records)}
    dates = aact.study_dates(["NCT07060417", "NCT03190694"])
    assert pipeline._completeness_for_record(recs["NCT07060417"], dates)["completeness_state"] == "eligible+not_yet_recruiting"
    assert pipeline._completeness_for_record(recs["NCT03190694"], dates)["completeness_state"] == "eligible+completed+results_available"

    core = {
        "screening": {
            "records": [
                {"id": "EMPA-CKD · NCT07060417", "decision": "include", "completeness_state": "eligible+not_yet_recruiting"},
                {"id": "DIAMOND · NCT03190694", "decision": "include", "completeness_state": "eligible+completed+results_available"},
            ]
        },
        "outcomes": [{"trials": []}],
    }
    unpooled = invalidation._eligible_not_pooled(core)
    assert "DIAMOND · NCT03190694" in unpooled
    assert "EMPA-CKD · NCT07060417" not in unpooled
    reasons = invalidation.assess(core, signals={"search_not_executed": None, "known_eligible_missing": []})["reasons"]
    eligible = [r for r in reasons if r["code"] == "eligible_declared_absent"]
    assert eligible and "NCT03190694" in eligible[0]["detail"]
    assert "NCT07060417" not in eligible[0]["detail"]


def test_adjudicator_disagreement_is_consumed_as_typed_pending_state():
    rows = [{"id": "34585011", "decision": "include", "rule_id": "INCLUDE", "reason": "served row"}]
    out = pipeline._apply_adjudicator_flags("probiotics-aad-prevention", rows)
    row = out["records"][0]
    assert row["adjudicator_state"] == "ADJUDICATOR_DISAGREES"
    assert row["adjudicator_recommended_decision"] == "exclude"
    assert out["pending"] == [
        {
            "id": "34585011",
            "served": "include",
            "adjudicator": "exclude",
            "rationale": row["adjudicator_rationale"],
        }
    ]


def test_screening_delta_artifact_records_required_corpus_sweep():
    delta = _json("docs/screening_delta.json")
    assert delta["topics_n"] == 32
    assert delta["summary"]["screening_rows_old"] == 3143
    assert delta["summary"]["decision_changes"] == 49
    changed = {(c["slug"], c["id"], c["old_decision"], c["new_decision"], c["new_rule_id"]) for c in delta["decision_changes"]}
    assert ("sglt2-ckd-progression", "NCT06350123", "include", "exclude", "X-CONTRAST") in changed
    assert ("sglt2-ckd-progression", "NCT03190694", "exclude", "include", "INCLUDE") in changed
    assert ("metformin-pcos-ovulation", "19552097", "exclude", "include", "INCLUDE") in changed
    assert ("noac-vs-warfarin-af-stroke", "NCT02935855", "include", "exclude", "X1") in changed
    assert ("noac-vs-warfarin-af-stroke", "NCT05006287", "include", "exclude", "X2") in changed
