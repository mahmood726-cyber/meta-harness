"""Counterexamples from the independent cross-vendor review NR-C04 (Codex, logged in the lane's CALL_LOG.jsonl), each
reproduced by the lane on the committed code before it was fixed. The review's inputs are used verbatim."""
from __future__ import annotations

import pytest

from harness import compat_check as cc, target_endpoint as te, window_evidence as we

MORT = {"name": "28-day all-cause mortality", "keywords": ["mortality", "death", "died", "28-day"], "timepoint": "28 days"}
COVID = {"include": {"population_any": ["covid", "sars-cov-2", "coronavirus"],
                     "population_none": ["influenza", "community-acquired pneumonia"]},
         "intervention_terms": ["dexamethasone"]}


def _m(measure, tf=None, pop=None, spec=MORT, topic=COVID):
    o = te.registry_outcome_match(spec, topic, measure, time_frame=tf, population=pop)
    return o["target_endpoint_class"], o["registry_match"]


# ---- registry match -------------------------------------------------------------------------------------------------
def test_c04_2_a_death_or_ventilation_composite_is_not_mortality():
    cls, rm = _m("Death or invasive mechanical ventilation", "28 days")
    assert cls == te.DIFFERENT_OUTCOME and "outcome" in rm["conflicts"], rm


def test_c04_7_an_excluded_population_in_the_title_body_conflicts():
    cls, rm = _m("All-cause mortality in patients with influenza", "28 days")
    assert cls == te.DIFFERENT_OUTCOME and "population" in rm["conflicts"], rm


def test_c04_9_a_comparison_prefix_does_not_bypass_the_population_check():
    cls, rm = _m("Dexamethasone comparison: All-cause mortality", "28 days", pop="Participants with influenza")
    assert cls == te.DIFFERENT_OUTCOME and "population" in rm["conflicts"], rm


def test_c04_13_a_negated_excluded_population_is_not_a_conflict():
    cls, rm = _m("All-cause mortality", "28 days", pop="Patients with COVID-19 without influenza")
    assert "population" not in rm["conflicts"] and cls == te.EXACT_TARGET, rm


def test_c04_10_a_different_time_anchor_conflicts():
    spec = {"name": "28-day all-cause mortality", "keywords": ["mortality", "death"], "timepoint": "28 days after randomization"}
    cls, rm = _m("All-cause mortality", "28 days after hospital discharge", spec=spec, topic={})
    assert cls == te.DIFFERENT_OUTCOME and "timepoint" in rm["conflicts"], rm


def test_c04_15_a_cumulative_window_ending_later_is_not_the_target_timepoint():
    spec = {"name": "28-day all-cause mortality", "keywords": ["mortality", "death"], "timepoint": "28 days"}
    cls, rm = _m("All-cause mortality", "0-90 days", spec=spec, topic={})
    assert cls != te.EXACT_TARGET, rm


# ---- dosing vs ascertainment, and the result's own window ------------------------------------------------------------
@pytest.mark.parametrize("span", ["Patients received study treatment for up to 14 days.",
                                  "Patients received dexamethasone for 14 days after randomization."])
def test_c04_3_4_administration_durations_are_not_follow_up(span):
    assert we.is_follow_up_evidence(span) is False


def test_c04_5_week_n_ordering_is_read():
    r = we.result_window("At week 12, mortality was 10%.")
    assert r and r[0] == "12 weeks", r


def test_c04_14_a_treatment_stop_day_is_not_the_result_window():
    r = we.result_window("Treatment was stopped on day 14; mortality was assessed at 28 days.")
    assert r and r[0] == "28 days", r


def test_c04_16_the_governing_timepoint_wins_over_a_subgroup_cutoff():
    r = we.result_window("At 90 days, mortality among patients discharged from hospital by day 28 was 12%.")
    assert r and r[0] == "90 days", r


# ---- field link ----------------------------------------------------------------------------------------------------
def test_c04_1_a_composite_definition_does_not_define_its_component_row():
    assert cc._defines_this_row("The primary outcome was cardiovascular death, myocardial infarction, or stroke.",
                                "Cardiovascular death occurred in 20 patients.") is False


def test_c04_1_control_the_full_composite_row_is_still_defined():
    assert cc._defines_this_row("The primary outcome was cardiovascular death, myocardial infarction, or stroke.",
                                "Cardiovascular death, myocardial infarction, or stroke occurred in 60 patients.") is True


def test_c04_11_another_outcomes_assessment_time_is_not_this_rows_follow_up():
    fu = cc._derive_follow_up({"name": "All-cause mortality"},
                              {"source": "abstract effect: Mortality was lower with dexamethasone (risk ratio, 0.80; 95% CI, 0.65 to 0.98)."},
                              {"abstract": "Clinical cure was assessed at 14 days. Mortality was lower with dexamethasone."}, None)
    assert fu["value"] is None, fu


# ---- composite accounting -------------------------------------------------------------------------------------------
def test_c04_6_a_title_part_the_vocabulary_does_not_know_still_counts():
    spec = {"name": "Composite of cardiovascular death or all-cause hospitalization", "components": ["cardiovascular death"]}
    assert te.composite_declaration_problem(spec) is not None
    assert te._classify(spec, "Cardiovascular death occurred in 20 patients.")["target_endpoint_class"] == \
        te.COMPOSITE_DECLARATION_INCOMPLETE


# -- controls for #6: the part-accounting rule must not refuse what is accounted for --------------------------------
def test_c04_6_control_hyphenated_part_matches_its_declared_component():
    spec = {"name": "Composite cardiovascular death or heart-failure hospitalization",
            "components": ["cardiovascular death", "heart failure hospitalization"]}
    assert te.composite_declaration_problem(spec) is None


def test_c04_6_control_slash_joins_synonym_labels_not_parts():
    assert te._title_parts("Major vascular events / MACE") == []


def test_c04_6_control_parenthetical_enumeration_is_the_part_list():
    assert te._title_parts("Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death)") == \
        ["DVT", "nonfatal PE", "fatal PE", "VTE-related death"]


def test_c04_6_control_unreadable_title_is_left_to_keyword_family():
    assert te.composite_declaration_problem({"name": "Gynecomastia or breast pain"}) is None


def test_c04_6_unread_part_is_decided_per_row():
    spec = {"name": "Stroke or systemic embolism"}
    assert te._classify(spec, "Stroke or systemic embolism occurred in 1.1% vs 1.6% (HR 0.79).")[
        "target_endpoint_class"] == te.EXACT_TARGET
    assert te._classify(spec, "Stroke occurred in 1.0% vs 1.4% (HR 0.70).")[
        "target_endpoint_class"] == te.COMPOSITE_DECLARATION_INCOMPLETE


# ---- NR-C07 (Codex round 2), the window / field-link cases fixed by the lane ----------------------------------------
def _fu(name, source, abstract):
    return cc._derive_follow_up({"name": name}, {"source": source}, {"abstract": abstract}, None)["value"]


def test_c07_1_a_trial_wide_follow_up_with_any_duration_binds():
    assert _fu("All-cause mortality", "Mortality was 10%.", "All patients were followed for 28 days.") == "28 days"


def test_c07_2_an_adjectival_month_window_is_read():
    assert we.result_window("Mortality during the 6-month follow-up was 10%.")[0] == "6 months"
    assert we.result_window("Among 6-month-old infants, mortality was 2%.") is None     # an age, not a window


def test_c07_3_an_earlier_discharge_does_not_outrank_an_administration_clause():
    t = "After discharge, patients received study medication for 14 days."
    i = t.index("14 days")
    assert we.duration_role(t, i, i + 7) == "DOSING"
    t2 = "Deaths were counted until 28 days after discharge."
    i = t2.index("28 days")
    assert we.duration_role(t2, i, i + 7) == "ASCERTAINMENT"                           # control


def test_c07_8_a_negated_modifier_is_another_outcome():
    assert _fu("Cardiovascular death", "Cardiovascular death occurred in 20 patients.",
               "Non-cardiovascular death was assessed at 14 days.") is None


def test_c07_9_an_outcome_specific_follow_up_visit_is_not_trial_wide():
    assert _fu("All-cause mortality", "Mortality was 10%.",
               "Clinical cure was assessed at the follow-up visit at 14 days.") is None


def test_c07_10_a_window_before_randomization_is_history_not_the_result():
    s = "Among patients hospitalized within 30 days before randomization, mortality at 90 days was 12%."
    assert we.result_window(s)[0] == "90 days"


def test_c07_13_a_primary_component_row_is_not_defined_by_the_composite():
    d = "The primary outcome was cardiovascular death, myocardial infarction, or stroke."
    assert not cc._defines_this_row(d, "The primary outcome component of cardiovascular death occurred in 20.")
    assert cc._defines_this_row(d, "The primary outcome occurred in 9.8% vs 11.2%.")        # control


@pytest.mark.parametrize("abstract,expected", [
    # radius (11560298, 21165295): the head noun or the acronym names the row, not every modifier
    ("Subjects recorded the number of stools daily for 21 days. The primary outcome was the proportion of patients who "
     "developed diarrhea in the first 21 days after enrollment.", "21 days"),
    ("Patients recorded bowel frequency daily for 14 days. The primary outcome was the proportion of patients who "
     "developed AAD within 14 days of enrollment.", "14 days"),
])
def test_c07_radius_the_row_head_noun_or_acronym_names_the_row(abstract, expected):
    assert _fu("Antibiotic-associated diarrhoea", "", abstract) == expected


# ---- NR-C09 (Codex patch for NR-C07 round-2 registry / composite / exclusion cases, verified by the lane) --------------
MORT = {"name": "All-cause mortality", "keywords": ["mortality", "death"], "timepoint": "28 days"}
POP_NONE = {"include": {"population_none": ["influenza", "community-acquired pneumonia"]}}


def _reg(topic, measure, time_frame, population=None):
    kw = {"spec": MORT, "topic": topic, "measure": measure, "time_frame": time_frame}
    if population is not None:
        kw["population"] = population
    r = te.registry_outcome_match(**kw)
    return r["target_endpoint_class"], r["registry_match"]["conflicts"]


@pytest.mark.parametrize("target,stated,expected", [
    ("6 months", "Month 6", "AGREE"),                                   # C07 #4
    ("in-hospital", "28 days after hospital discharge", "CONFLICT"),     # C07 #5
    ("0-90 days", "28 days", "CONFLICT"),                               # C07 #6
    ("in-hospital", "until the date of discharge", "AGREE"),            # control
])
def test_c09_timepoints(target, stated, expected):
    assert te._timepoint_agreement(target, stated) == expected


def test_c09_7_death_and_dependence_is_not_mortality():
    assert _reg({}, "Death and dependence", "28 days") == ("DIFFERENT_OUTCOME", ["outcome"])


def test_c09_11_15_population_negation_scope():
    assert _reg(POP_NONE, "All-cause mortality", "28 days",
                "Patients with neither influenza nor community-acquired pneumonia") == ("EXACT_TARGET", [])
    assert _reg(POP_NONE, "All-cause mortality", "28 days",
                "Patients without diabetes and with influenza") == ("DIFFERENT_OUTCOME", ["population"])


@pytest.mark.parametrize("spec_name,text,expected", [
    ("3-point major adverse cardiovascular events",
     "The primary outcome was 3-point MACE, excluding all patients with prior stroke.", "EXACT_TARGET"),       # #12
    ("Stroke or systemic embolism", "Stroke occurred in 20 patients; systemic embolism was not assessed.",
     "COMPOSITE_DECLARATION_INCOMPLETE"),                                                                    # #14
    ("Cardiovascular death / all-cause hospitalization", "Cardiovascular death occurred in 20 patients.",
     "COMPOSITE_DECLARATION_INCOMPLETE"),                                                                    # #16
    ("Composite of cardiovascular death, myocardial infarction (fatal or nonfatal), or all-cause hospitalization",
     "Cardiovascular death or myocardial infarction, fatal or nonfatal, occurred in 20 patients.",
     "COMPOSITE_DECLARATION_INCOMPLETE"),                                                                    # #17
    ("3-point major adverse cardiovascular events",
     "The primary outcome in patients with diabetes was 3-point MACE excluding nonfatal stroke.",
     "ENDPOINT_COMPONENT_EXCLUDED"),                                                                         # #18
])
def test_c09_composite_and_exclusion(spec_name, text, expected):
    assert te._classify({"name": spec_name}, text)["target_endpoint_class"] == expected


# ---- NR-C14 (Codex round 3 on sentence ownership of a window; fixed structurally by the lane: sentences are RANKED,
#      the clause holding the estimate decides, absent rows judge only their own sentences) ----------------------------
C14 = [
 [
  1,
  {
   "name": "Major bleeding"
  },
  {
   "source": "Clinical cure at 14 days was improved (RR 1.20), whereas major bleeding at 90 days was similar (RR 0.95).",
   "effect": 0.95
  },
  {
   "abstract": ""
  },
  "90 days"
 ],
 [
  2,
  {
   "name": "All-cause mortality"
  },
  {
   "source": "Mortality was lower (RR 0.80).",
   "effect": 0.8
  },
  {
   "abstract": "Follow-up continued for 12 months."
  },
  "12 months"
 ],
 [
  4,
  {
   "name": "Myocardial infarction (MI)"
  },
  {
   "source": "MI was less frequent (RR 0.80).",
   "effect": 0.8
  },
  {
   "abstract": "MACE was assessed at 12 months. MI was assessed at 14 days."
  },
  "14 days"
 ],
 [
  5,
  {
   "name": "Major bleeding"
  },
  {
   "source": "Major bleeding was less frequent (RR 0.80).",
   "effect": 0.8
  },
  {
   "abstract": "Minor bleeding was assessed at 14 days. Major bleeding was assessed at 90 days."
  },
  "90 days"
 ],
 [
  6,
  {
   "name": "Death from any cause"
  },
  {
   "source": "Death from any cause was less frequent (RR 0.80).",
   "effect": 0.8
  },
  {
   "abstract": "Cardiovascular death was assessed at 14 days. Death from any cause was assessed at 90 days."
  },
  "90 days"
 ],
 [
  7,
  {
   "name": "Cardiovascular death"
  },
  {
   "source": "Cardiovascular death was less frequent (RR 0.80).",
   "effect": 0.8
  },
  {
   "abstract": "Death from any cause was assessed at 14 days. Cardiovascular death was assessed at 90 days."
  },
  "90 days"
 ],
 [
  9,
  {
   "name": "All-cause mortality"
  },
  {
   "source": "At 30 days (RR 0.75; 95% CI 0.60-0.90) and at 90 days (RR 0.60; 95% CI 0.45-0.80), mortality was reduced.",
   "effect": 0.6
  },
  {
   "abstract": ""
  },
  "90 days"
 ],
 [
  10,
  {
   "name": "Death"
  },
  {
   "source": "Death from any cause was less frequent (RR 0.80).",
   "effect": 0.8
  },
  {
   "abstract": "Cardiovascular death was assessed at 14 days. Death from any cause was assessed at 90 days."
  },
  "90 days"
 ],
 [
  11,
  {
   "name": "All-cause mortality"
  },
  {
   "source": "Mortality was lower (RR 0.80).",
   "effect": 0.8
  },
  {
   "abstract": "The primary outcome was clinical cure at 14 days. For mortality, patients continued to be followed until month 12."
  },
  "12 months"
 ],
 [
  12,
  {
   "name": "Serious adverse events"
  },
  {
   "source": "The primary efficacy outcome was clinical cure at 14 days. Serious adverse events were monitored through day 90 but were not reported separately.",
   "state": "outcome_not_reported"
  },
  {
   "abstract": ""
  },
  "90 days"
 ],
 [
  13,
  {
   "name": "All-cause mortality"
  },
  {
   "source": "Mortality was lower (RR 0.80).",
   "effect": 0.8
  },
  {
   "abstract": "Follow-up of all patients was performed for 12 months."
  },
  "12 months"
 ],
 [
  14,
  {
   "name": "All-cause mortality"
  },
  {
   "source": "Mortality was lower (RR 0.80).",
   "effect": 0.8
  },
  {
   "abstract": "Patients were followed during 12 months."
  },
  "12 months"
 ]
]


@pytest.mark.parametrize("case,outcome,trial,rec,expected", C14)
def test_c14_the_window_comes_from_the_sentence_that_owns_it(case, outcome, trial, rec, expected):
    assert cc._derive_follow_up(outcome, trial, rec, None)["value"] == expected, case


# the LEGACY eligibility catalogue (harness/eligibility_chain.py::_follow_up_value) reads a fixed list of windows with no
# row gating -- unchanged since HEAD; recorded, not widened in V1.0.1 (handover: replace with the compat derivation)
C14_LEGACY = [
 [
  3,
  "Patients continued to be followed for 12 months. Mortality was lower (RR 0.80).",
  "Mortality was lower (RR 0.80).",
  [
   0.8
  ],
  "12 months"
 ],
 [
  8,
  "The primary outcome was clinical cure at 14 days. Major bleeding was similar between groups (RR 0.95).",
  "Major bleeding was similar between groups (RR 0.95).",
  [
   0.95
  ],
  "not_stated"
 ]
]


@pytest.mark.xfail(strict=True, reason="legacy eligibility catalogue: no row gating, no generic windows (pre-existing at HEAD)")
@pytest.mark.parametrize("case,text,span,estimates,expected", C14_LEGACY)
def test_c14_legacy_eligibility_catalogue(case, text, span, estimates, expected):
    from harness import eligibility_chain
    assert eligibility_chain._follow_up_value("", text, span, estimates)[0] == expected, case
