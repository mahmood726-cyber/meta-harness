"""A REGISTRY outcome is EXACT_TARGET only when it agrees with the target on disease POPULATION, intervention COMPARISON,
OUTCOME and TIMEPOINT (lane NR, V1.0.1; COVID-corticosteroids review). RECOVERY (NCT04381936) is a platform trial: its
registry lists 'Influenza co-primary outcome: Time to discharge alive from hospital' and 'Community-acquired pneumonia:
All-cause mortality ...', and every one was labelled EXACT_TARGET for '28-day COVID-19 mortality' because the target has no
canonical components and the classifier fell back to a keyword-family match. A shared platform identifier or a broad
outcome category is never enough. Conflicts -> DIFFERENT_OUTCOME; a dimension the row cannot confirm -> NEAR_MATCH.
"""
from __future__ import annotations

import pytest

from harness import target_endpoint as te

SPEC = {"name": "28-day all-cause mortality", "keywords": ["mortality", "death", "died", "28-day"], "timepoint": "28 days"}
TOPIC = {"slug": "corticosteroids-covid19-mortality",
         "include": {"population_any": ["covid", "sars-cov-2", "coronavirus"],
                     "population_none": ["influenza", "community-acquired pneumonia"]},   # as the topic config states
         "intervention_terms": ["dexamethasone", "hydrocortisone", "methylprednisolone", "corticosteroid"]}


def _m(measure, time_frame=None, population=None):
    return te.registry_outcome_match(SPEC, TOPIC, measure, time_frame=time_frame, population=population)


def test_influenza_discharge_alive_fails_a_covid_mortality_match():
    out = _m("Influenza co-primary outcome: Time to discharge alive from hospital", "Within the first 28-days")
    assert out["target_endpoint_class"] == te.DIFFERENT_OUTCOME, out
    assert {"population", "outcome"} <= set(out["registry_match"]["conflicts"])


def test_another_disease_populations_mortality_is_not_the_target():
    out = _m("Community-acquired pneumonia: All-cause mortality (with subsidiary analyses of cause of death)",
             "Within 28 days after randomisation")
    assert out["target_endpoint_class"] == te.DIFFERENT_OUTCOME and out["registry_match"]["conflicts"] == ["population"], out


def test_a_different_timepoint_conflicts():
    out = _m("All-cause mortality", "At 6 months after randomisation")
    assert out["target_endpoint_class"] == te.DIFFERENT_OUTCOME and "timepoint" in out["registry_match"]["conflicts"], out


def test_an_unstated_timepoint_is_unconfirmed_not_exact():
    out = _m("All-cause mortality", None)
    assert out["target_endpoint_class"] == te.NEAR_MATCH and out["registry_match"]["unconfirmed"] == ["timepoint"], out


def test_a_different_intervention_comparison_conflicts():
    out = _m("Tocilizumab comparison: All-cause mortality", "Within 28 days after randomisation")
    assert out["target_endpoint_class"] == te.DIFFERENT_OUTCOME and "comparison" in out["registry_match"]["conflicts"], out


# ---- controls: agreement on every dimension stays EXACT ---------------------------------------------------------------
@pytest.mark.parametrize("measure,tf", [
    ("All-cause mortality", "Within 28 days after randomisation"),
    ("COVID-19 co-primary outcome: All-cause mortality", "28 days"),
    ("Mortality at 28 days", None),                              # the measure itself states the timepoint
    ("Dexamethasone comparison: All-cause mortality", "Day 28"),
])
def test_agreement_on_every_dimension_stays_exact(measure, tf):
    out = _m(measure, tf)
    assert out["target_endpoint_class"] == te.EXACT_TARGET, out


def test_a_target_with_no_declared_timepoint_does_not_demand_one():
    spec = {k: v for k, v in SPEC.items() if k != "timepoint"}
    assert te.registry_outcome_match(spec, TOPIC, "All-cause mortality")["target_endpoint_class"] == te.EXACT_TARGET


def test_an_analysis_population_description_is_not_a_disease_population():
    # AACT's `population` column describes the ANALYSIS set ('Intent-to-treat population: all randomised participants');
    # it never names the topic's disease, so it must not conflict (the first full rebuild dropped genuine matches this way)
    out = _m("All-cause mortality", "Within 28 days after randomisation",
             population="Intention-to-treat population: all randomised participants")
    assert out["target_endpoint_class"] == te.EXACT_TARGET, out
    out = _m("All-cause mortality", "Within 28 days after randomisation", population="Participants with influenza")
    assert out["target_endpoint_class"] == te.DIFFERENT_OUTCOME and out["registry_match"]["conflicts"] == ["population"], out


@pytest.mark.parametrize("measure,tf,dim", [
    ("All-cause mortality at day 90", None, "timepoint"),
    ("All-cause mortality at 1 year after randomisation", None, "timepoint"),
    ("Intensive Care Unit Free Days to Day 28", None, "outcome"),
])
def test_genuine_downgrades_stay_downgraded(measure, tf, dim):
    out = _m(measure, tf)
    assert out["target_endpoint_class"] == te.DIFFERENT_OUTCOME and dim in out["registry_match"]["conflicts"], out


def test_a_composite_target_is_not_a_mortality_target():
    # MACE keywords mention death; that must not make 'Major Adverse Cardiovascular Events' fail a 'death' outcome test
    spec = {"name": "Major adverse cardiovascular events", "keywords": ["major adverse cardiovascular events",
            "cardiovascular death", "mace"], "components": ["cardiovascular death", "myocardial infarction", "stroke"]}
    out = te.registry_outcome_match(spec, {}, "Major Adverse Cardiovascular Events", time_frame="Up to 9 months")
    assert "outcome" not in out["registry_match"]["conflicts"], out


def test_an_in_hospital_target_against_a_numeric_window_is_unconfirmed_not_a_conflict():
    spec = {"name": "Postoperative atrial fibrillation", "keywords": ["atrial fibrillation"],
            "timepoint": "in-hospital / index-admission"}
    out = te.registry_outcome_match(spec, {}, "Atrial fibrillation",
                                    time_frame="Through study completion, an average of 1 week")
    assert out["registry_match"]["conflicts"] == [] and out["registry_match"]["unconfirmed"] == ["timepoint"], out
    assert out["target_endpoint_class"] == te.NEAR_MATCH


@pytest.mark.parametrize("measure", [
    "Panel A and B: Percentage of Participants With Response Based on MADRS Total Score",
    "Composite Outcome: Number of Participants with Major Bleeding and Recurrent VTE",
    "Change in Body Composition: Body Weight",
])
def test_a_title_prefix_that_names_no_excluded_population_is_not_a_population_conflict(measure):
    out = te.registry_outcome_match({"name": "some outcome"}, TOPIC, measure)
    assert "population" not in out["registry_match"]["conflicts"], out


def test_until_the_date_of_discharge_is_an_in_hospital_window():
    spec = {"name": "Postoperative atrial fibrillation", "keywords": ["atrial fibrillation"],
            "timepoint": "in-hospital / index-admission"}
    out = te.registry_outcome_match(spec, {}, "The Number of Participants With Atrial Fibrillation",
                                    time_frame="From date of randomization until the date of discharge, assessed up to 30 days")
    assert out["target_endpoint_class"] == te.EXACT_TARGET, out


# ---- lane NR rebuild diff: two regressions of the V1.0.1 registry fixes, planted ----------------------------------------
def test_a_target_range_above_zero_accepts_any_timepoint_inside_it():
    # balanced-crystalloids: '28-90 day or in-hospital' is the set of acceptable timepoints, not a window ending at 90
    assert te._timepoint_agreement("28-90 day or in-hospital", "28 days") == "AGREE"
    assert te._timepoint_agreement("28-90 day or in-hospital", "Day 28") == "AGREE"
    assert te._timepoint_agreement("0-90 days", "28 days") == "CONFLICT"          # a cumulative window still conflicts
    assert te._timepoint_agreement("28 days", "0-90 days") == "CONFLICT"


def test_a_title_part_written_as_its_abbreviation_is_named():
    spec = {"name": "Stroke or systemic embolism"}
    assert te._classify(spec, "Yearly Event Rate for Composite Endpoint of Stroke/SEE")["target_endpoint_class"] == \
        te.EXACT_TARGET
    assert te._classify(spec, "Stroke or systemic embolic event occurred in 1.1%")["target_endpoint_class"] == \
        te.EXACT_TARGET
    assert te._classify(spec, "Stroke occurred in 1.0% (HR 0.70)")["target_endpoint_class"] == \
        te.COMPOSITE_DECLARATION_INCOMPLETE                                          # still refused: stroke alone


@pytest.mark.parametrize("measure,composite", [
    # a setting or qualifier of mortality is not a second event (lane NR rebuild diff)
    ("ICU, hospital and 28 day all-cause mortality", False),
    ("ICU and Hospital Mortality", False),
    ("Clinical outcomes - Cardiac and non-cardiac mortality", False),
    # a second EVENT still makes a death composite (NR-C04 #2, NR-C07 #7)
    ("30-day all-cause sepsis or all-cause mortality", True),
    ("Death and dependence", True),
    ("Death or invasive mechanical ventilation", True),
])
def test_a_mortality_qualifier_is_not_a_second_event(measure, composite):
    assert te._death_composite(measure) is composite
