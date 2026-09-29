"""Mahmood 2026-09-28, 'fix all in harness (regex and reproducible ai)': every statins-older-adults item as a
deterministic extractor, each with a PLANT (these tests fail on the pre-fix harness; `n of N` in the handover)."""
import copy
import json
import os

import pytest

from harness import pipeline

ROOT = pipeline.ROOT
SLUG = "statins-primary-prevention-elderly"


def _cfg():
    return dict(json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8")), slug=SLUG)


def _recs():
    d = json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))
    return d["records"], d.get("ctgov") or []


# ---------------------------------------------------------------- 1. a condition label its criteria only EXCLUDE
def test_plant_condition_label_excluded_by_its_own_criteria_never_vetoes():
    from harness import registry_criteria as rc, screen, trial_family as tf
    reg = tf.load_registry(ROOT, SLUG)
    crit = reg["NCT04262206"]["population"]["criteria"]["value"]
    assert rc.label_only_excluded("dementia", crit)
    rec = next(r for r in _recs()[1] if r["id"] == "NCT04262206")
    inc = dict(_cfg()["include"], _registry_criteria={"NCT04262206": crit})
    d = screen.screen_record(rec, inc, set())
    assert d.decision == "include" and "EXCLUSION criterion" in d.reason
    # negative plant: the SAME label in the INCLUSION section still vetoes
    assert not rc.label_only_excluded("dementia", "Inclusion Criteria:~* Dementia~Exclusion Criteria:~* Dementia with ...")
    assert screen.screen_record(rec, dict(inc, _registry_criteria={"NCT04262206": "Inclusion Criteria:~* Dementia"}),
                                set()).decision == "exclude"


def test_plant_population_from_inclusion_criteria():
    from harness import registry_criteria as rc
    crit = "Inclusion Criteria:~* Community-dwelling adults~* Age ≥75 years~Exclusion Criteria:~* Dementia"
    assert rc.inclusion_matches(["older adults", "75 years"], crit) == "75 years"
    assert rc.inclusion_matches(["heart failure"], crit) is None


# ---------------------------------------------------------------- 2+3. report linkage: parent registration + shared arm Ns
def test_plant_report_linkage_by_parent_acronym_and_shared_arm_sizes():
    from harness import report_linkage as rl
    recs = _recs()[0]
    links = rl.derive(recs, _cfg())
    orkaby = next(x for x in links if x["pmid"] == "30251369")
    assert orkaby["parent_pmid"] == "28531241" and orkaby["trial_family_id"] == "NCT00000542"
    assert [r["rule"] for r in orkaby["derived"]["rules"]] == ["A_PARENT_LINKAGE", "B_SHARED_ARM_SIZES"]
    assert orkaby["derived"]["rules"][1]["shared"] == [1400, 1467]
    # plant: two registered parents naming the acronym -> abstain (never a guess)
    han = next(r for r in recs if r["id"] == "28531241")
    twin = dict(copy.deepcopy(han), id="99999998", nct="NCT99999998")
    assert not any(x["pmid"] == "30251369" for x in rl.derive(recs + [twin], _cfg()))
    # plant: the two rules point at DIFFERENT parents -> abstain
    other = dict(copy.deepcopy(han), id="99999997", nct="NCT99999997", title="Another pravastatin trial",
                 abstract="Pravastatin (n=1,467) vs usual care (n=1,400).")
    han2 = dict(han, abstract=han["abstract"].replace("1467", "1466").replace("1400", "1399"))
    assert not any(x["pmid"] == "30251369" for x in rl.derive([r for r in recs if r["id"] != "28531241"] + [han2, other],
                                                             _cfg()))


# ---------------------------------------------------------------- 4. RMST is never a ratio
def test_plant_rmst_difference_on_a_ratio_scale_is_blocked():
    from harness import measure_guard as mg
    recs = {r["id"]: r for r in _recs()[0]}
    span = recs["30251369"]["abstract"]
    review = {"outcomes": [{"name": "Major vascular events", "trials": [
        {"id": "PMID 30251369", "effect": -33.7, "scale": "HR", "source_span": span}]}]}
    assert [p["kind"] for p in mg.problems(review)] == ["MEASURE_CLASS_MISMATCH"]
    review["outcomes"][0]["trials"][0]["scale"] = "RMST_DIFFERENCE_DAYS"
    assert mg.problems(review) == []


# ---------------------------------------------------------------- 5. subgroup provenance
def test_plant_subgroup_provenance_contradicting_the_topic_annotation():
    from harness import subgroup_provenance as sp
    recs = {r["id"]: r for r in _recs()[0]}
    j = recs["20404379"]
    c = sp.classify(f"{j['title']} {j['abstract']}")
    assert c["state"] == "POST_HOC" and "age cut-point chosen after" in c["spans"]
    review = {"outcomes": [{"name": "Major vascular events", "trials": [{"id": "PMID 20404379"}]}]}
    sp.attach(review, _cfg(), recs)
    assert [p["kind"] for p in sp.problems(review)] == ["SUBGROUP_PROVENANCE_CONFLICT"]
    assert sp.classify("a prespecified subgroup analysis of age")["state"] == "PRESPECIFIED"


# ---------------------------------------------------------------- 6. component-set typing
def test_plant_component_sets_are_derived_and_untyped_items_disclosed():
    from harness import component_typing as ct, endpoint_policy as ep
    recs = {r["id"]: r for r in _recs()[0]}
    j = ct.derive(recs["20404379"]["abstract"])
    assert j["components"] == ["cardiovascular death", "myocardial infarction", "stroke", "unstable angina"]
    assert j["untyped"] == ["arterial revascularization"]                    # disclosed, never silently dropped
    s = ct.derive(recs["42670961"]["abstract"])
    assert "coronary revascularization" in s["components"] and s["untyped"] == []
    # plant: a pooled input with no derivable definition is not admitted
    review = {"outcomes": [{"name": "Major vascular events", "trials": [{"id": "PMID 11111111"}, {"id": "PMID 20404379"}]}]}
    ep.attach(review, SLUG, {"11111111": {"abstract": "Statins reduced events."}, "20404379": recs["20404379"]})
    assert [p["report_id"] for p in ep.problems(review)] == ["11111111"]


def test_negative_plant_an_abbreviation_is_not_a_trial_acronym():
    # a '(LD)' for 'loading dose' once linked a stable-CAD platelet study (26440227) to a STEMI trial (23500251)
    from harness import report_linkage as rl
    slug = "ticagrelor-vs-clopidogrel-acs"
    cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    recs = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))["records"]
    assert not any(x["pmid"] == "26440227" for x in rl.derive(recs, cfg))


def test_negative_plant_a_trial_about_the_label_is_never_exempted():
    # LAmbre (NCT04684212) is an appendage-occlusion DEVICE trial; its criteria also exclude appendage thrombus. The
    # label names what the trial is ABOUT (title: 'Large Appendages'), so the veto stands.
    from harness import screen, trial_family as tf
    slug = "noac-vs-warfarin-af-stroke"
    inc = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))["include"]
    rec = next(x for x in json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))["ctgov"]
               if x["id"] == "NCT04684212")
    crit = tf.load_registry(ROOT, slug)["NCT04684212"]["population"]["criteria"]["value"]
    assert tuple(screen.screen_record(rec, dict(inc, _registry_criteria={"NCT04684212": crit}), set()))[1] == "X2"
