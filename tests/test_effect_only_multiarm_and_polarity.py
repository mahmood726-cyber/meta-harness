"""Synthetic boundary plants plus source-backed pinned-corpus measurements."""
from collections import defaultdict
from copy import deepcopy

import pytest

from harness import effect_identity as ei
from evidence.fixtures import build_effect_identity_fixture as builder


def arms():
    # Synthetic, not research results: one randomisation, two doses, one placebo.
    common = dict(trial_family_id="synthetic-program", trial_id="synthetic-trial",
                  control_arm_id="placebo", outcome="Mortality", timepoint="day 28",
                  population="cohort A", effect=0.8, ci_low=0.6, ci_high=1.1,
                  scale="HR", source="hazard ratio 0.8; 95% CI 0.6 to 1.1")
    return [dict(common, id="synthetic-trial#low", dose="low"),
            dict(common, id="synthetic-trial#high", dose="high", effect=0.7)]


@pytest.mark.parametrize("rule", [None, "COMBINE_ARMS", "SPLIT_CONTROL", "UNKNOWN"])
def test_effect_only_shared_control_is_held_even_with_count_rule(rule):
    rows = arms()
    before = deepcopy(rows)
    assert ei.multi_arm_groups(rows) == [rows]
    out, held = ei.apply_multi_arm_rule(rows, {"multi_arm_rule": rule})
    assert out == [] and len(held) == 1
    assert held[0]["state"] == "MULTI_ARM_SHARED_CONTROL_UNDECLARED"
    assert "require complete count-only inputs" in held[0]["reason"]
    assert [r["effect"] for r in held[0]["multi_arm"]["arms"]] == [0.8, 0.7]
    assert rows == before


def test_same_concrete_report_arm_suffixes_do_not_need_count_fields():
    rows = arms()
    for row in rows:
        del row["control_arm_id"]
        del row["trial_id"]
    assert ei.multi_arm_groups(rows) == [rows]


@pytest.mark.parametrize("field,value", [
    ("outcome", "Hospitalisation"), ("endpoint_definition", "different endpoint"),
    ("timepoint", "day 90"), ("follow_up_window", "one year"),
    ("population", "cohort B"), ("analysis_population", "different cohort"),
    ("trial_id", "another-trial-in-the-program"), ("control_arm_id", "active-control"),
])
@pytest.mark.parametrize("counts", [False, True])
def test_same_program_does_not_join_different_comparison_scopes(field, value, counts):
    rows = arms()
    if counts:
        for row in rows:
            row.pop("effect")
            row.update(ai=10, n1i=100, ci=20, n2i=100)
    rows[1][field] = value
    assert ei.multi_arm_groups(rows) == []
    assert ei.apply_multi_arm_rule(rows, {}) == (rows, [])


def test_separate_trials_without_explicit_control_and_duplicate_comparison_are_not_arms():
    rows = arms()
    for row in rows:
        row.pop("control_arm_id")
    rows[1]["trial_id"] = "separate-trial"
    assert ei.multi_arm_groups(rows) == []
    assert ei.multi_arm_groups([rows[0], deepcopy(rows[0])]) == []
    assert ei.multi_arm_groups([dict(effect=0.8), dict(effect=0.7)]) == []


def test_declared_single_arm_selection_applies_to_effects_without_covariance():
    rows = arms()
    out, held = ei.apply_multi_arm_rule(rows, {
        "multi_arm_rule": "SELECT_ARM", "multi_arm_selected_id": rows[1]["id"]})
    assert not held and len(out) == 1
    assert out[0]["effect"] == 0.7 and out[0]["multi_arm"]["applied"] == "SELECT_ARM"
    assert len(out[0]["multi_arm"]["arms"]) == 2
    out, held = ei.apply_multi_arm_rule(rows, {
        "multi_arm_rule": "SELECT_ARM", "multi_arm_selected_id": "missing"})
    assert not out and held


def test_published_effect_with_counts_cannot_be_resolved_by_splitting_unused_counts():
    rows = arms()
    for row in rows:
        row.update(ai=10, n1i=100, ci=20, n2i=100)
    assert ei.apply_multi_arm_rule(rows, {"multi_arm_rule": "SPLIT_CONTROL"})[0] == []


@pytest.mark.parametrize("rule", ["COMBINE_ARMS", "SPLIT_CONTROL"])
def test_explicit_control_identity_with_inconsistent_counts_stays_held(rule):
    rows = arms()
    for row in rows:
        row.pop("effect")
        row.update(ai=10, n1i=100, ci=20, n2i=100)
    rows[1]["ci"] = 21
    out, held = ei.apply_multi_arm_rule(rows, {"multi_arm_rule": rule})
    assert not out and "inconsistent counts" in held[0]["reason"]


def test_count_rows_from_separate_reports_are_not_joined_by_equal_counts():
    rows = arms()
    for i, row in enumerate(rows):
        row.pop("effect")
        row.pop("trial_id")
        row.pop("control_arm_id")
        row.update(id=f"separate-report-{i}", ai=10, n1i=100, ci=20, n2i=100)
    assert ei.multi_arm_groups(rows) == []


SURVIVAL = "The hazard ratio for survival was 0.8 (95% CI, 0.6 to 1.1)."


def test_same_estimate_survival_sentence_fires_and_keeps_evidence():
    row = arms()[0]
    assert ei.polarity_check(row, "Mortality", {})["state"] == "NOT_STATED"
    check = ei.polarity_check(row, "Mortality", {}, SURVIVAL)
    assert check["state"] == "EVENT_POLARITY_MISMATCH"
    assert check["resolution"] == "HOLD"
    assert check["sentences"] == [SURVIVAL] and check["read_from"] == "held abstract"
    normal = ei.polarity_check(row, "Mortality", {
        "polarity_normalisation": {"reciprocal_for_benefit_event": True}}, SURVIVAL)
    assert normal["state"] == "NORMALISED"
    assert normal["normalised"] == {"effect": 1.25, "ci_low": 0.9091, "ci_high": 1.6667}


@pytest.mark.parametrize("sentence", [
    SURVIVAL.replace("0.8", "0.9"), SURVIVAL.replace("0.6", "0.5"),
    SURVIVAL.replace("1.1", "1.2"), SURVIVAL.replace("hazard ratio", "odds ratio"),
    "Survival improved. The hazard ratio was 0.8 (95% CI, 0.6 to 1.1).",
    "The hazard ratio for survival was 0.8.",
])
def test_different_or_incomplete_estimate_or_adjacent_sentence_cannot_supply_polarity(sentence):
    assert ei.polarity_check(arms()[0], "Mortality", {}, sentence)["state"] == "NOT_STATED"


def test_fallback_does_not_override_quotation_or_choose_between_conflicting_matches():
    row = arms()[0]
    death = "The hazard ratio for death was 0.8 (95% CI, 0.6 to 1.1)."
    assert ei.polarity_check(dict(row, source=death), "Mortality", {}, SURVIVAL)["state"] == "CONSISTENT"
    assert ei.polarity_check(row, "Mortality", {}, death + " " + SURVIVAL)["state"] == "NOT_STATED"
    assert ei.polarity_check(row, "Mortality", {}, death)["state"] == "CONSISTENT"


def test_pinned_measurements_and_each_original_unknown_row():
    slugs, blobs, paths = builder.pinned_inputs()
    groups = []
    unknown = {}
    all_rows = []
    for slug in slugs:
        records = {str(r["id"]): r for r in blobs[paths[slug]]["records"]} if paths[slug] else {}
        for outcome in blobs[f"docs/reviews/{slug}/review.json"]["outcomes"]:
            rows = outcome.get("trials", [])
            all_rows.extend(rows)
            for field in ("trial_family_id", "family_id", "trial_id"):
                families = defaultdict(list)
                for row in rows:
                    assert row.get(field), (slug, row.get("id"), field)
                    families[row[field].split("#")[0]].append(row)
                groups.extend(g for g in families.values() if len(g) >= 2)
            assert ei.multi_arm_groups(rows) == []
            for row in rows:
                old = ei.polarity_check(row, outcome["name"], {})
                if old and old["state"] == "NOT_STATED":
                    abstract = records.get(row["id"].replace("PMID ", ""), {}).get("abstract")
                    check = ei.polarity_check(row, outcome["name"], {}, abstract)
                    unknown[row["id"]] = check["event_modelled"]
                    sentences = ei.matching_effect_sentences(row, abstract)
                    if row["id"] == "NCT02468232":
                        assert not abstract and not sentences
                    else:
                        assert len(sentences) == 1
                        assert sentences[0] in abstract
                        assert ei.event_modelled(sentences[0]) == check["event_modelled"]
    assert not groups and len(all_rows) == 127
    assert sum(t.get("effect") is not None for t in all_rows) == 86
    assert unknown == {
        "PMID 19966341": "NOT_STATED", "PMID 22449293": "NOT_STATED",
        "PMID 21128814": "NOT_STATED", "PMID 23991658": "NOT_STATED",
        "PMID 23808982": "NOT_STATED", "NCT02468232": "NOT_STATED",
        "PMID 32865377": "DEATH", "PMID 28824029": "NOT_STATED",
    }


def test_two_effect_only_dose_arms_under_one_id_are_held_not_deduplicated():
    """Verifier-added plant: same id, no dose field, DIFFERENT estimates = two comparisons sharing one control."""
    from harness import effect_identity as ei
    a = {"id": "PMID 1", "label": "T", "effect": 0.80, "ci_low": 0.70, "ci_high": 0.92, "scale": "HR"}
    b = {"id": "PMID 1", "label": "T", "effect": 0.74, "ci_low": 0.64, "ci_high": 0.86, "scale": "HR"}
    pool, held = ei.apply_multi_arm_rule([a, b], {})
    assert pool == [] and held and held[0]["state"] == "MULTI_ARM_SHARED_CONTROL_UNDECLARED"
    same = dict(a)
    pool, held = ei.apply_multi_arm_rule([a, same], {})      # an identical copy is one comparison, not two arms
    assert held == [] and len(pool) == 2
