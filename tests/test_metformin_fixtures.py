"""Metformin-PCOS review fixtures (2026-09-27, hash f1643a71; retrospective, decided by Dispatch under Mahmood's delegation).

(1) arm-based comparator: Legro 2007 (PMID 17287476) was excluded X3 "no eligible comparator" by phrase matching; its arms
    ("clomiphene citrate plus placebo, extended-release metformin plus placebo, or a combination of metformin and clomiphene")
    establish a placebo arm, and the eligible contrast is the CLEAN one (clomiphene held constant).
(2) outcome definition record: "ovulation" HOMOGENEOUS was asserted from one component token; it is derived now.
(3) narrative: an OR is never a probability ratio; an uninformative interval carries no magnitude word.
Held bytes at the pinned candidate 3876a62d (a missing commit fails, never skips)."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import arm_parse, narrative_rules as nr, outcome_definition as od, screen   # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
SLUG = "metformin-pcos-ovulation"


def _show(path):
    p = subprocess.run(["git", "show", f"{PINNED}:{path}"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        pytest.fail(f"{PINNED[:8]}:{path} not in history (never a skip)", pytrace=False)
    return p.stdout.decode("utf-8")


@pytest.fixture(scope="module")
def held():
    return json.loads(_show(f"cache/{SLUG}/records.json"))


def _rec(held, pid):
    r = dict(next(x for x in held["records"] if str(x["id"]) == pid))
    r.setdefault("id_type", "pmid")
    return r


@pytest.fixture(scope="module")
def topic():
    return json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))


# ------------------------------------------------------------------ (1) arm-based comparator
def test_plant_served_legro_is_x3_no_eligible_comparator():
    rv = json.loads(_show(f"docs/reviews/{SLUG}/review.json"))
    d = next(x for x in rv["screening"]["records"] if "17287476" in str(x["id"]))
    assert (d["decision"], d["rule_id"]) == ("exclude", "X3") and "no eligible comparator" in d["reason"]


def test_legros_arms_are_read_and_only_the_clean_contrast_counts(held):
    arms = arm_parse.abstract_arms(_rec(held, "17287476")["abstract"])
    assert arms == ["clomiphene citrate plus placebo", "extended-release metformin plus placebo",
                    "a combination of metformin and clomiphene"]
    cs = {(c["experimental_arm"], c["comparator_arm"]): c for c in arm_parse.ordered_contrasts(arms, ["metformin"])}
    assert cs[(arms[2], arms[0])]["state"] == "CLEAN" and cs[(arms[2], arms[0])]["held_constant"] == ["clomiphene"]
    assert cs[(arms[1], arms[0])]["state"] == "CONFOUNDED"                       # metformin vs clomiphene: not eligible
    abc = arm_parse.arm_based_comparator(arms, ["metformin"])
    assert (abc["experimental_arm"], abc["comparator_arm"]) == (arms[2], arms[0])


def test_the_screen_now_includes_legro_through_its_placebo_arm(held, topic):
    dec = screen.screen_record(_rec(held, "17287476"), topic["include"], set())
    assert (dec[0], dec[1]) == ("include", "INCLUDE") and "clomiphene citrate plus placebo" in dec[2]


def test_a_registry_intervention_list_is_not_a_list_of_arms():
    # NCT02792400 lists seven interventions; pairing them as arms invented "linagliptin vs LY2403021 placebo"
    interventions = ["LY2403021", "LY2403021 placebo", "Standardised liquid meal", "Linagliptin", "Linagliptin placebo",
                     "Empagliflozin", "Empagliflozin placebo"]
    abc = arm_parse.arm_based_comparator(interventions, ["linagliptin"], labels_are_arms=False)
    assert abc["comparator_arm"] == "Linagliptin placebo"                       # the placebo MATCHED to the agent
    no_matched = ["LY2403021", "LY2403021 placebo", "Linagliptin", "Empagliflozin"]
    assert arm_parse.arm_based_comparator(no_matched, ["linagliptin"], labels_are_arms=False) is None
    assert arm_parse.arm_based_comparator(["Saxagliptin", "Placebo"], ["saxagliptin"], labels_are_arms=False)["comparator_arm"] == "Placebo"


def test_corpus_n_of_n_x3_flips_matches_the_recorded_measurement():
    sys.path.insert(0, os.path.join(ROOT, "evidence", "matched_placebo"))
    import measure_x3_comparator as m
    got = m.measure(PINNED)
    assert (got["x3_no_comparator"], got["flip_past_x3"], got["now_include"]) == (175, 5, 4)
    stored = json.load(open(os.path.join(ROOT, "evidence", "matched_placebo", "x3_comparator_3876a62d.json"), encoding="utf-8"))
    assert [r["id"] for r in stored["rows"] if r.get("flips_past_x3")] == [r["id"] for r in got["rows"] if r.get("flips_past_x3")]


# ------------------------------------------------------------------ (2) outcome definition record
def test_plant_the_served_endpoint_label_is_asserted_homogeneous():
    rv = json.loads(_show(f"docs/reviews/{SLUG}/review.json"))
    o = next(x for x in rv["outcomes"] if x.get("primary"))
    assert o["compat_key"]["endpoint_canonical_status"] == "HOMOGENEOUS"


def test_each_trials_definition_is_read_from_its_held_text(held):
    ben = od.definition_record(_rec(held, "19522426")["abstract"])
    assert set(ben["criterion"]["value"]) >= {"FOLLICLE_SIZE", "ESTRADIOL", "ENDOMETRIUM"} and "16 mm" in ben["criterion"]["span"]
    assert ben["observation"]["value"] == od.NOT_STATED                           # "Within 7 months ... recruited" is recruitment
    van = od.definition_record(_rec(held, "11172832")["abstract"])
    assert van["criterion"]["value"] == ("PROGESTERONE",) and van["denominator"]["value"] == "WOMAN"
    assert "six ovulatory cycles, became pregnant" in van["stopping"]["value"]
    moll = od.definition_record(_rec(held, "16769748")["abstract"])
    assert moll["criterion"]["value"] == od.NOT_STATED and moll["stopping"]["value"] == od.NOT_STATED


def test_the_label_is_derived_heterogeneous_here_and_homogeneous_only_when_every_field_agrees(held):
    recs = {p: od.definition_record(_rec(held, p)["abstract"]) for p in ("19522426", "16769748", "11172832")}
    st = od.derive_status(recs)
    assert st["status"] == "DEFINITION_HETEROGENEOUS" and st["fields"]["criterion"]["state"] == "HETEROGENEOUS"
    same = {"a": {f: {"value": "X"} for f in od.FIELDS}, "b": {f: {"value": "X"} for f in od.FIELDS}}
    assert od.derive_status(same)["status"] == "HOMOGENEOUS"
    silent = {"a": {f: {"value": "X"} for f in od.FIELDS}, "b": {f: {"value": od.NOT_STATED} for f in od.FIELDS}}
    assert od.derive_status(silent)["status"] == "DEFINITION_NOT_DERIVABLE"


# ------------------------------------------------------------------ (3) narrative
POOLED_OR = [{"scale": "OR", "ci_low": 0.0922, "ci_high": 46.6008}]


@pytest.mark.parametrize("claim,code", [
    ("With metformin, twice as many women ovulated.", "OR_AS_PROBABILITY_RATIO"),
    ("Ovulation was 2-fold more likely with metformin.", "OR_AS_PROBABILITY_RATIO"),
    ("Metformin produced a substantial improvement in ovulation.", "MAGNITUDE_CLAIM_ON_UNINFORMATIVE_INTERVAL"),
])
def test_plant_an_or_worded_as_a_probability_ratio_or_a_magnitude_claim_is_refused(claim, code):
    bad = nr.check_or_narrative(f"<p>{claim}</p>", [], POOLED_OR)
    assert bad and bad[0]["code"] == code


def test_quotations_endpoint_names_and_informative_intervals_pass(held):
    ben = _rec(held, "19522426")["abstract"]
    quote = "a non-statistically significant (small study population) but important difference (1.66 times)"
    assert nr.check_or_narrative(f"<p>The authors report {quote}.</p>", [ben], POOLED_OR) == []
    assert nr.check_or_narrative("<p>a doubling of the serum creatinine level</p>", [], POOLED_OR) == []
    assert nr.check_or_narrative("<p>a substantial reduction</p>", [], [{"scale": "HR", "ci_low": 0.55, "ci_high": 0.84}]) == []
    assert nr.uninformative_interval(0.0922, 46.6008) and not nr.uninformative_interval(0.55, 0.84)
