"""Continuous-outcome rules from the melatonin review (2026-09-27; retrospective, decided by Dispatch under Mahmood's delegation).

(1) population default: for a broad adult question the primary input is the full eligible population; a subgroup (Wade's age
    65-80) is a separate analysis, never pooled as independent. Plant: the served primary IS the 65-80 subgroup (-17.4).
(2) measurement class: PSG, diary and questionnaire are different measurements -- read from the words the source uses for THIS
    number, never from the outcome's name, and never chosen for favourability.
(3) crossover: per-arm mean/SD from a crossover (Almeida Montes: 10 people, 3 periods) are refused as independent arms.
(5) raw vs adjusted kept apart: Wade raw -17.4 vs adjusted -15.6 (-25.3 to -6.0), ANCOVA; the analysis's SD 47 is never an SE.
Sign orientation (4) is on its own branch (oc/cx-contrast-sign). Held bytes at the pinned candidate 3876a62d (never a skip)."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import continuous_identity as ci   # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
SLUG = "melatonin-primary-insomnia-sol"


def _show(path):
    p = subprocess.run(["git", "show", f"{PINNED}:{path}"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        pytest.fail(f"{PINNED[:8]}:{path} not in history (never a skip)", pytrace=False)
    return p.stdout.decode("utf-8")


@pytest.fixture(scope="module")
def held():
    return json.loads(_show(f"cache/{SLUG}/records.json"))


@pytest.fixture(scope="module")
def served_row():
    o = next(x for x in json.loads(_show(f"docs/reviews/{SLUG}/review.json"))["outcomes"] if x.get("primary"))
    return o, o["trials"][0]


@pytest.fixture(scope="module")
def topic():
    return json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))


def _wade_om(held):
    return held["ctgov_results"]["NCT00397189"][0]


# ------------------------------------------------------------------ (1) population default
def test_plant_the_served_primary_is_the_65_80_subgroup(served_row):
    o, t = served_row
    assert (o["result"]["estimate"], o["result"]["k"]) == (-17.4, 1)
    assert "age 65-80" in t["source"] and t["id"] == "PMID 20712869"


def test_the_subgroup_is_recognised_from_the_row_and_from_the_annotation(served_row, topic):
    _, t = served_row
    pc = ci.population_class(t, {})                                             # from the row's own population statement
    assert pc["population"] == "SUBGROUP" and "65-80" in pc["label"]
    assert ci.population_class(t, topic["primary_outcome"])["basis"] == "trial annotation (topic)"
    full = dict(t, source="ClinicalTrials.gov results: mean -6.7 (SD 40, n=354) vs 0.0 (SD 40, n=356) -- population: all randomised adults")
    assert ci.population_class(full, {})["population"] == "FULL_ELIGIBLE"


def test_under_the_full_population_rule_the_subgroup_leaves_the_primary_and_the_full_row_stays(served_row, topic):
    _, t = served_row
    spec = topic["primary_outcome"]
    full = dict(t, id="PMID FULL", source="... population: all randomised adults 18-80 with primary insomnia")
    keep, rec = ci.split_continuous_inputs([dict(t), full], spec, lambda r: [r["source"]], lambda r: None, lambda r: "")
    assert [r["id"] for r in keep] == ["PMID FULL"] and [r["id"] for r in rec["subgroups"]] == ["PMID 20712869"]
    assert "RETROSPECTIVE" in spec["population_default"]["decided"]
    # without the declared rule nothing moves (the rule is a declaration, not a default of the code)
    keep2, rec2 = ci.split_continuous_inputs([dict(t)], {}, lambda r: [r["source"]], lambda r: None, lambda r: "")
    assert len(keep2) == 1 and not rec2["subgroups"]


def test_the_all_adult_values_the_review_cites_are_not_in_the_held_bytes():
    """-6.70 (-13.63 to +0.23), 55-80 -9.90 and PSQI -11.2 are not in any held melatonin file: the primary is therefore NOT HELD,
    never filled from the review's text."""
    blob = _show(f"cache/{SLUG}/records.json") + _show(f"cache/{SLUG}/ft_20712869.txt")
    for v in ("13.63", "-6.70", "-9.90"):
        assert v not in blob


# ------------------------------------------------------------------ (2) measurement class
def test_wades_number_is_the_sleep_diary_read_from_its_registry_analysis(held):
    om = _wade_om(held)
    an = om["analyses"] if isinstance(om["analyses"], list) else json.loads(om["analyses"])
    assert ci.measurement_class([om["title"]])["class"] == "SUBJECTIVE_UNSPECIFIED"     # "Subjective Sleep Latency" alone
    assert ci.measurement_class([om["title"], an[0]["groupDescription"]])["class"] == "DIARY"


@pytest.mark.parametrize("text,cls", [
    ("Latency to Persistent Sleep", "PSG"), ("polysomnographic sleep-onset latency", "PSG"),
    ("PSQI component 2 (sleep latency)", "QUESTIONNAIRE"), ("sleep latency from the sleep diary", "DIARY"),
    ("sleep latency by wrist actigraphy", "ACTIGRAPHY"), ("Sleep onset latency", "NOT_STATED"),
    ("diary and polysomnography", "AMBIGUOUS"),
])
def test_measurement_class_comes_from_the_words_for_this_number(text, cls):
    assert ci.measurement_class([text])["class"] == cls


def test_mixed_classes_without_a_declared_primary_are_all_separate_and_a_declared_class_keeps_only_itself():
    rows = [{"id": "A", "mean1": -6.7, "source": "sleep diary"}, {"id": "B", "mean1": -11.2, "source": "PSQI question 2"}]
    spec = {"measurement_classes": {"separate_by_class": True}}
    keep, rec = ci.split_continuous_inputs([dict(r) for r in rows], spec, lambda r: [r["source"]], lambda r: None, lambda r: "")
    assert keep == [] and rec["state"] == "MEASUREMENT_CLASS_MIXED_PRIMARY_NOT_DECLARED" and set(rec["by_class"]) == {"DIARY", "QUESTIONNAIRE"}
    spec["measurement_classes"]["primary"] = "DIARY"
    keep, rec = ci.split_continuous_inputs([dict(r) for r in rows], spec, lambda r: [r["source"]], lambda r: None, lambda r: "")
    assert [r["id"] for r in keep] == ["A"] and set(rec["by_class"]) == {"QUESTIONNAIRE"}     # never the more favourable -11.2


# ------------------------------------------------------------------ (3) crossover
def test_plant_almeida_montes_is_a_crossover_and_per_arm_means_are_refused(held):
    ab = next(r["abstract"] for r in held["records"] if str(r["id"]) == "12790159")
    arm_row = {"id": "PMID 12790159", "mean1": -10.0, "sd1": 20.0, "nc1": 10, "mean2": -5.0, "sd2": 20.0, "nc2": 10}
    cx = ci.crossover_state(arm_row, None, ab)
    assert cx["state"] == "CROSSOVER_PAIRED_VARIANCE_REQUIRED" and "random order" in cx["basis"] or "crossover" in cx["basis"].lower()
    paired = dict(arm_row, paired_md=-5.0, paired_se=3.1)
    assert ci.crossover_state(paired, None, ab)["state"] == "PAIRED_ADMITTED"
    assert ci.crossover_state(arm_row, {"intervention_model": "PARALLEL"}, "a parallel-group trial") is None


# ------------------------------------------------------------------ (5) raw vs adjusted
def test_wade_adjusted_minus_15_6_is_typed_adjusted_kept_apart_from_raw_and_its_sd_is_never_an_se(held):
    tm = ci.typed_measure(_wade_om(held))
    (an,) = tm["analyses"]
    assert (an["estimate_kind"], an["value"], an["ci"]["low"], an["ci"]["high"]) == ("ADJUSTED_DIFFERENCE", -15.6, -25.3, -6.0)
    assert an["se_of_difference"] is None                               # the analysis's "STANDARD_DEVIATION 47" is not an SE
    raw = tm["arms"][0]["mean_change"] - tm["arms"][1]["mean_change"]
    assert round(raw, 1) == -17.4
    row = ci.model_based_row(_wade_om(held), [], None)
    assert row["state"] == "ADMITTED" and row["value"] == -15.6 and abs(row["se"] - 4.9236) < 1e-3


def test_a_decided_exclusion_is_never_relabelled_extraction_debt():
    from harness import consumer_consistency as cc
    assert {"FULL_POPULATION_INPUT_NOT_HELD", "CROSSOVER_PAIRED_VARIANCE_REQUIRED"} <= cc._DECIDED_EXCLUSIONS
