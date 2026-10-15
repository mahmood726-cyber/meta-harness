"""Plants (external audit review 26-A / 12-03 / 04-2): the compatibility-panel fields of a served row bind to THE ROW'S
SELECTED OUTCOME, not to the first regex hit over the row's source + span + title + whole abstract.

- CAPE COD (cortico-CAP, 36942789), all-cause mortality: the follow-up was '14 days' -- the hydrocortisone TAPER
  ('tapering for a total of 8 or 14 days'). The row's own span says 'By day 28, death had occurred ...'.
- Torres (cortico-CAP, 25688779): 'The primary outcome was treatment failure (...)' was attached to the MORTALITY and the
  HYPERGLYCAEMIA rows. A primary-outcome clause binds only to the row whose outcome IS that primary.
- Melatonin (20712869), sleep-onset latency: the analysis set was 'completers', from the EXTENSION re-randomisation
  sentence; the row's own source says 'Pre-planned analysis on ITT'.
- Denosumab FREEDOM (19671655): 'The primary end point was new vertebral fracture' was attached to the nonvertebral and
  hip rows. The analysis set 'intention-to-treat' is the protocol's declaration, not trial-reported: it must say so.
Each test reads the served review and held records of this tree, and failed on main a8a7c4b6.
"""
from __future__ import annotations

import json
import os

from harness import compat_check as cc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _row(slug, outcome, pid):
    review = json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))
    records = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
    o = next(x for x in review["outcomes"] if x["name"] == outcome)
    t = next(x for x in o["trials"] if str(x.get("id", "")).replace("PMID ", "") == pid)
    return cc.derive_trial_dimensions(review, o, t, records, cc._topic_definition_audit(slug, review))


def test_cape_cod_follow_up_is_the_outcome_window_not_the_treatment_taper():
    d = _row("corticosteroids-cap-mortality", "All-cause mortality", "36942789")
    assert d["follow_up_window"]["value"] == "28 days", d["follow_up_window"]
    assert "14 days" in (d["exposure_duration"]["value"] or ""), d["exposure_duration"]


def test_a_primary_outcome_clause_binds_only_to_the_row_whose_outcome_it_is():
    mort = _row("corticosteroids-cap-mortality", "All-cause mortality", "25688779")
    hyper = _row("corticosteroids-cap-mortality", "Hyperglycaemia", "25688779")
    for d in (mort, hyper):
        assert "treatment failure" not in (d["endpoint_definition"]["value"] or ""), d["endpoint_definition"]


def test_melatonin_analysis_set_is_the_rows_own_itt_not_the_extension_completers():
    d = _row("melatonin-primary-insomnia-sol", "Sleep-onset latency", "20712869")
    assert d["analysis_set"]["value"] == "intention-to-treat", d["analysis_set"]
    assert "completer" not in (d["analysis_set"]["span"] or "").lower()


def test_denosumab_vertebral_primary_clause_stays_on_its_own_row_only():
    vert = _row("denosumab-vertebral-fracture", "New vertebral fracture", "19671655")
    assert "new vertebral fracture" in (vert["endpoint_definition"]["value"] or "").lower()
    for name in ("Nonvertebral fracture", "Hip fracture"):
        d = _row("denosumab-vertebral-fracture", name, "19671655")
        assert "primary end point" not in (d["endpoint_definition"]["value"] or "").lower(), (name, d["endpoint_definition"])


def test_a_protocol_declared_analysis_set_is_labelled_as_declared_not_trial_reported():
    d = _row("denosumab-vertebral-fracture", "New vertebral fracture", "19671655")
    assert d["analysis_set"]["source"] == cc.SRC_DECLARED and d["analysis_set"]["trial_reported"] is False


def test_an_explicit_timeframe_wins_over_prose():
    d = _row("melatonin-primary-insomnia-sol", "Sleep-onset latency", "20712869")
    assert d["follow_up_window"]["value"] == "Baseline and 3 weeks" and d["follow_up_window"]["source"] == "trial.timeframe"


def test_time_phrases_are_typed_by_kind():
    k = cc.time_phrase_kind
    assert k("followed by tapering for a total of 8 or 14 days", "14 days") == "exposure"
    assert k("By day 28, death had occurred in 25 of 400 patients", "day 28") == "follow_up"
    assert k("the median length of hospital stay was 5 days", "5 days") == "length_of_stay"
    assert k("60 mg of denosumab subcutaneously every 6 months for 36 months", "every 6 months") == "schedule"


def test_age_dispersion_and_lancet_decimals_are_not_follow_up_windows():
    k = cc.time_phrase_kind
    assert k("Of the 1105 participants (mean age, 70 years [SD, 12 years]; 33% were women)", "70 years") == "age"
    assert k("The mean duration of exposure was 34.2±13.7 months", "13.7 months") == "dispersion"
    vals = [v for v, raw, s, kind in cc._phrases("During a median follow-up of 5·4 years (IQR 5·1-5·9), the outcome occurred.")]
    assert vals[0] == "5.4 years"


def test_the_outcome_acronym_binds_a_sentence():
    assert cc._about_outcome("AAD occurred in 12% of the placebo group.", cc._outcome_tokens({"name": "Antibiotic-associated diarrhoea"}))


def test_follow_up_comparison_trial_defined_accepts_durations_fixed_window_does_not():
    """A trial-defined window ('trial end') accepts each trial's own reported duration -- that is what it means; a fixed
    window ('28 days') flags a trial with another window, and wording ('within 28 days', 'Day 28') is not a difference."""
    from harness.compat_check import _follow_compatible, _is_mismatch
    assert _follow_compatible("trial end", "2.6 years")
    assert _follow_compatible("trial end / longest randomized follow-up", "40 months")
    assert not _is_mismatch("follow_up_window", "trial end", ["2.6 years", "3.4 years"])
    assert _follow_compatible("28 days", "within 28 days") and _follow_compatible("28 days", "Day 28")
    assert not _follow_compatible("28 days", "90 days")
    assert _is_mismatch("follow_up_window", "28 days", ["28 days", "90 days"])
    assert _follow_compatible("52-104 weeks", "68 weeks") and not _follow_compatible("52-104 weeks", "26 weeks")
    assert not _follow_compatible("in-hospital / index-admission", "14 days")


# --- recorded codex review of this branch (registry/model_proposals/pr_codex_review.json: lc-compat-codex-*) ---------
# each finding's own failing input, reproduced here before the fix
def test_PLANT_codex_focused_g1_1_and_g2_1_a_non_qualified_primary_never_binds_the_qualified_outcome():
    assert cc._outcome_sentences({"name": "Vertebral fractures", "primary": True},
                                 {"abstract": "The primary outcome was nonvertebral fractures."}) == []
    assert cc._endpoint_from("The primary outcome was nonfatal stroke.", {"name": "Fatal stroke", "primary": True},
                             ["fatal", "stroke"]) is None


def test_PLANT_codex_focused_g1_2_event_free_survival_is_not_mortality():
    assert cc._outcome_sentences({"name": "Mortality"}, {"abstract": "Progression-free survival was analysed per-protocol."}) == []
    assert cc._outcome_sentences({"name": "Mortality"}, {"abstract": "Overall survival was 80%."}) != []


def test_PLANT_codex_focused_g1_3_and_full_g1_2_treatment_until_day_n_is_exposure():
    assert cc.time_phrase_kind("Patients received treatment until day 7.", "until day 7") == "exposure"
    assert cc._derive_follow_up({"name": "Mortality"}, {"source": "Patients received treatment until day 14. Mortality was "
                                "assessed at day 28."}, None, None)["value"] == "28 days"
    assert cc.time_phrase_kind("By day 28, death had occurred in 25.", "By day 28") == "follow_up"


def test_PLANT_codex_focused_g1_4_and_full_g1_3_length_of_stay_only_in_its_own_clause():
    assert cc._derive_time_fields({}, {"source": "Mortality at day 28 and length of stay were assessed."}, None)[
        "length_of_stay"]["value"] is None
    assert cc._derive_follow_up({"name": "Mortality"}, {"source": "Mortality was assessed at day 28; length of hospital "
                                "stay was 7 days."}, None, None)["value"] == "28 days"
    assert cc._derive_time_fields({}, {"source": "Mortality was assessed at day 28; length of hospital stay was 7 days."},
                                  None)["length_of_stay"]["value"] == "7 days"
    assert cc._derive_time_fields({}, {"source": "Patients spent 5 days in hospital."}, None)["length_of_stay"]["value"] == "5 days"


def test_PLANT_codex_focused_g1_5_a_repeated_phrase_is_classified_at_its_own_offset():
    kinds = [k for _, _, _, k in cc._phrases("Treatment lasted 7 days, and mortality was assessed at 7 days.")]
    assert kinds == ["exposure", "follow_up"], kinds


def test_PLANT_codex_focused_g2_2_a_composite_primary_does_not_define_its_first_component():
    assert cc._endpoint_from("The primary outcome was a composite of mortality, myocardial infarction, or stroke.",
                             {"name": "Mortality", "primary": True}, ["mortality"]) is None
    assert cc._endpoint_from("The primary outcome was a composite of death, myocardial infarction, or stroke.",
                             {"name": "Composite of death, myocardial infarction or stroke", "primary": True},
                             cc._outcome_tokens({"name": "Composite of death, myocardial infarction or stroke"})) is not None


def test_PLANT_codex_focused_g3_1_and_full_g1_1_8_days_is_not_inside_28_days():
    assert not cc._follow_compatible("28 days", "8 days")
    assert cc._is_mismatch("follow_up_window", "28 days", ["8 days"])
    assert cc._follow_compatible("in-hospital / index-admission", "in-hospital")


def test_PLANT_codex_focused_g3_2_a_capped_trial_end_assertion_is_not_open_ended():
    assert cc._is_mismatch("follow_up_window", "28 days or trial end, whichever is earlier", ["365 days"])


def test_PLANT_codex_full_g1_4_another_outcomes_analysis_statement_is_not_trial_level():
    d = cc._derive_analysis_set({"study_effect": {"analysis_population": "intention-to-treat"}},
                                {"abstract": "Hospitalization was analysed per-protocol."}, None, {"name": "Mortality"})
    assert (d["value"], d["source"], d["trial_reported"]) == ("intention-to-treat", cc.SRC_DECLARED, False), d
    d = cc._derive_analysis_set({}, {"abstract": "Data were analysed according to the intention-to-treat principle."},
                                None, {"name": "Mortality"})
    assert (d["value"], d["source"]) == ("intention-to-treat", cc.SRC_TRIAL_STATEMENT), d


def test_PLANT_codex_full_g1_5_a_row_that_denies_being_primary_does_not_take_the_primary_clause():
    d = cc._derive_endpoint({"name": "Mortality"}, {"source": "Mortality was a secondary outcome, not the primary outcome."},
                            {"abstract": "The primary outcome was treatment failure."}, None)
    assert d["value"] == "Mortality", d


def test_PLANT_codex_full_g1_6_a_co_mentioned_outcomes_definition_is_not_this_rows():
    d = cc._derive_endpoint({"name": "Mortality"}, {"source": "Mortality and diarrhoea (three or more loose stools daily) "
                            "were assessed."}, None, None)
    assert d["value"] == "Mortality", d
    d = cc._derive_endpoint({"name": "Antibiotic-associated diarrhoea"}, {"source": "diarrhoea (three or more loose stools "
                            "daily for 2 days) occurred in 10"}, None, None)
    assert d["value"].startswith("diarrhoea ("), d


def test_PLANT_codex_full_g1_7_a_fractional_time_point_keeps_its_decimal():
    assert cc._derive_follow_up({"name": "Mortality"}, {"source": "Mortality was assessed at month 1.5."}, None,
                                None)["value"] == "1.5 months"


def test_follow_up_a_duration_named_in_the_assertion_is_compatible_even_beside_trial_end():
    # served keys: semaglutide-obesity-mace, ticagrelor-vs-clopidogrel-acs (the g3#2 cap must not flag these)
    assert cc._follow_compatible("trial end / mean follow-up 39.8 months", "39.8 months")
    assert cc._follow_compatible("12 months or longest reported trial follow-up", "12 months")
    assert not cc._follow_compatible("12 months", "2 months")           # whole words: "2 months" is not in "12 months"


# --- recorded review round 2 (lc-compat-r2-codex) -------------------------------------------------------------------
def test_PLANT_codex_r2_g1_1_a_separately_named_non_outcome_does_not_veto_the_primary_clause():
    s = cc._outcome_sentences({"name": "Vertebral fracture", "primary": True},
                              {"abstract": "The primary outcome was new vertebral fracture; nonvertebral fractures were "
                                           "secondary."})
    assert s, s
    assert cc._outcome_sentences({"name": "Vertebral fractures", "primary": True},
                                 {"abstract": "The primary outcome was nonvertebral fractures."}) == []


def test_PLANT_codex_r2_g2_1_a_measured_stay_is_still_a_stay():
    assert cc.time_phrase_kind("Length of hospital stay was measured as 7 days.", "7 days") == "length_of_stay"


def test_PLANT_codex_r2_g3_1_a_multiword_component_is_not_defined_by_its_composite():
    assert cc._endpoint_from("The primary outcome was a composite of death, myocardial infarction, or disabling "
                             "stroke.", {"name": "Disabling stroke", "primary": False}, ["disabling", "stroke"]) is None
    toks = cc._outcome_tokens({"name": "3-point major adverse cardiovascular events"})
    assert cc._endpoint_from("The primary outcome was a composite of death from cardiovascular causes, nonfatal "
                             "myocardial infarction, or nonfatal stroke.",
                             {"name": "3-point major adverse cardiovascular events", "primary": True}, toks) is not None


def test_PLANT_codex_r2_g4_1_an_or_longest_assertion_is_open_a_whichever_earlier_one_is_capped():
    assert cc._follow_compatible("12 months or longest reported trial follow-up", "24 months")
    assert not cc._follow_compatible("28 days or trial end, whichever is earlier", "365 days")


# --- recorded review round 2, second family (lc-compat-r2-agy) -------------------------------------------------------
def test_PLANT_agy_r2_g1_1_a_progression_free_survival_row_still_binds_its_own_word():
    assert cc._has_token("progression-free survival", "survival")
    assert not cc._has_token("progression-free survival", "mortality")


def test_PLANT_agy_r2_g1_2_fatal_or_non_fatal_names_both_and_negates_neither():
    assert not cc._negates("the primary outcome was fatal or non-fatal stroke", ["fatal", "stroke"])
    assert cc._negates("the primary outcome was nonfatal stroke", ["fatal", "stroke"])
