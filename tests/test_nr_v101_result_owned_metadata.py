"""An extracted result's outcome DEFINITION and TIMEPOINT bind to the sentence (or table cell) that owns THAT result
(lane NR, V1.0.1; corticosteroids-cap-mortality review).

(a) CAPE COD (PMID 36942789): the admitted deaths are 'By day 28, death had occurred in 25 of 400 ...', but the row's
    follow-up was served as 14 days, read from the TREATMENT sentence '... followed by tapering for a total of 8 or 14
    days) or to receive placebo' -- the Farzaneh class, in a phrasing the dosing check missed ('tapering').
(b) Torres (PMID 25688779): the admitted 6 vs 9 are IN-HOSPITAL deaths ('In-hospital mortality did not differ ... (6
    patients [10%] ... vs 9 patients [15%] ...)'), a secondary outcome, but the row's endpoint definition was the PRIMARY
    treatment-failure composite paragraph, and its follow-up was the review's own timepoint.
Rule: the owning span is read first; a primary-endpoint paragraph defines a row only when that row's own span is the
primary result; a window elsewhere in the text binds only if it is a trial-wide follow-up statement, never a regimen.
"""
from __future__ import annotations

import pytest

from harness import compat_check, eligibility_chain, window_evidence

CAPE_ABS = ("Patients were randomly assigned to receive either intravenous hydrocortisone (200 mg daily for either 4 or 7 "
            "days as determined by clinical improvement, followed by tapering for a total of 8 or 14 days) or to receive "
            "placebo. The primary outcome was death at 28 days.")
CAPE_SRC = ("abstract arm-level counts (percentage-corroborated): By day 28, death had occurred in 25 of 400 patients "
            "(6.2%; 95% confidence interval [CI], 3.9 to 8.6) in the hydrocortisone group and in 47 of 395 patients (11.9%)")
TORRES_ABS = ("Patients received methylprednisolone or placebo (n = 59) for 5 days started within 36 hours of hospital "
              "admission. MAIN OUTCOMES AND MEASURES: The primary outcome was treatment failure (composite outcome of early "
              "treatment failure defined as clinical deterioration, and late treatment failure defined as radiographic "
              "progression). In-hospital mortality was a secondary outcome.")
TORRES_SRC = ("abstract arm-level counts (percentage-corroborated): In-hospital mortality did not differ between the 2 groups "
              "(6 patients [10%] in the methylprednisolone group vs 9 patients [15%] in the placebo group; P = .37)")
MORT = {"name": "All-cause mortality", "timepoint": "30-day or in-hospital"}


def test_cape_cod_follow_up_is_the_result_spans_day_28_not_the_regimen():
    fu = compat_check._derive_follow_up(MORT, {"source": CAPE_SRC}, {"abstract": CAPE_ABS}, None)
    assert fu["value"] == "28 days" and fu["source"] == "result span", fu


def test_a_tapering_regimen_is_a_dosing_duration():
    i = CAPE_ABS.index("14 days")
    assert window_evidence.duration_role(CAPE_ABS, i, i + len("14 days")) == "DOSING"


def test_torres_follow_up_is_in_hospital_from_its_own_span():
    fu = compat_check._derive_follow_up(MORT, {"source": TORRES_SRC}, {"abstract": TORRES_ABS}, None)
    assert fu["value"] == "in-hospital" and fu["source"] == "result span", fu


def test_torres_is_not_defined_by_the_primary_composite_paragraph():
    ep = compat_check._derive_endpoint(MORT, {"source": TORRES_SRC}, {"abstract": TORRES_ABS}, None)
    assert "treatment failure" not in (ep["value"] or "").lower(), ep
    assert ep["source"] != "committed source text" or "in-hospital mortality" in ep["value"].lower(), ep


# ---- controls ---------------------------------------------------------------------------------------------------------
def test_a_primary_result_keeps_its_primary_definition():
    abs_ = ("The primary outcome was a composite of death from cardiovascular causes, nonfatal myocardial infarction, or "
            "nonfatal stroke. The primary outcome occurred in 108 patients (6.6%) in the semaglutide group and 146 (8.9%).")
    src = "abstract arm-level counts (percentage-corroborated): The primary outcome occurred in 108 patients (6.6%) in the semaglutide group"
    ep = compat_check._derive_endpoint({"name": "3-point MACE"}, {"source": src}, {"abstract": abs_}, None)
    assert "composite of death from cardiovascular causes" in ep["value"], ep


def test_a_trial_wide_follow_up_statement_still_binds_when_the_result_states_no_window():
    abs_ = "During a median follow-up of 5.3 years, major cardiovascular events occurred in 386 participants."
    src = "abstract source-reported HR: major cardiovascular events (hazard ratio, 0.92; 95% CI, 0.80 to 1.06)"
    fu = compat_check._derive_follow_up({"name": "MACE"}, {"source": src}, {"abstract": abs_}, None)
    assert fu["value"] == "5.3 years", fu


def test_admission_reader_binds_the_result_span_first():
    text = eligibility_chain._record_text({"abstract": TORRES_ABS}, {"source": TORRES_SRC})
    assert eligibility_chain._follow_up_value("999", text, TORRES_SRC)[0] == "in-hospital"
    text = eligibility_chain._record_text({"abstract": CAPE_ABS}, {"source": CAPE_SRC})
    assert eligibility_chain._follow_up_value("999", text, CAPE_SRC)[0] == "28 days"


# ---- FREEDOM (denosumab review): secondary estimates reused the PRIMARY endpoint's definition -------------------------
FREEDOM_ABS = ("METHODS: We enrolled 7868 women between the ages of 60 and 90 years who had a bone mineral density T score of "
               "less than -2.5. The primary end point was new vertebral fracture. Secondary end points included nonvertebral "
               "and hip fractures. RESULTS: As compared with placebo, denosumab reduced the risk of new radiographic vertebral "
               "fracture, with a cumulative incidence of 2.3% in the denosumab group, versus 7.2% in the placebo group (risk "
               "ratio, 0.32; 95% CI, 0.26 to 0.41). Denosumab also reduced the risk of nonvertebral fracture, with a "
               "cumulative incidence of 6.5% in the denosumab group, versus 8.0% in the placebo group (hazard ratio, 0.80; "
               "95% CI, 0.67 to 0.95). Denosumab reduced the risk of hip fracture, with a cumulative incidence of 0.7% in "
               "the denosumab group, versus 1.2% in the placebo group (hazard ratio, 0.60; 95% CI, 0.37 to 0.97).")
_S = lambda k: "abstract effect+CI: " + next(s for s in FREEDOM_ABS.split(". ") if k in s)  # noqa: E731


@pytest.mark.parametrize("name,key", [("Nonvertebral fracture", "nonvertebral fracture, with"),
                                      ("Hip fracture", "hip fracture, with")])
def test_freedom_secondary_estimates_do_not_reuse_the_primary_definition(name, key):
    ep = compat_check._derive_endpoint({"name": name}, {"source": _S(key)}, {"abstract": FREEDOM_ABS}, None)
    assert "vertebral fracture" not in (ep["value"] or "").lower().replace("nonvertebral", ""), ep


def test_freedom_primary_estimate_keeps_its_own_definition():
    ep = compat_check._derive_endpoint({"name": "New vertebral fracture"}, {"source": _S("radiographic vertebral")},
                                       {"abstract": FREEDOM_ABS}, None)
    assert "primary end point was new vertebral fracture" in ep["value"], ep


def test_an_adjustment_model_is_never_borrowed_from_another_estimate():
    from harness import adjustment
    primary = {"source": _S("radiographic vertebral"), "adjustment_axis": {"status": "ADJUSTED", "source": "abstract",
               "span": "risk ratio", "start": _S("radiographic vertebral").find("risk ratio"),
               "end": _S("radiographic vertebral").find("risk ratio") + len("risk ratio")}}
    secondary = {"source": _S("hip fracture, with")}
    assert adjustment.axis_for_trial(primary)["status"] == "ADJUSTED"
    assert adjustment.axis_for_trial(secondary) == {"status": "UNRESOLVED"}   # its own cell states no model


@pytest.mark.parametrize("text,role", [
    # probiotics-aad-prevention, found while reading the combined rebuild: regimens served as 14-day windows
    ("302 hospitalized patients receiving antibiotics were randomized to receive Lactobacillus GG, 20 x 10(9) CFU/d, "
     "or placebo for 14 days", "DOSING"),
    ("214 patients who had begun receiving antibiotics were randomized to receive Lactobacillus (Lacidofil cap) or "
     "placebo for 14 days", "DOSING"),
    ("Patients recorded bowel frequency and stool consistency daily for 14 days", "ASCERTAINMENT"),
])
def test_probiotic_regimens_are_dosing_and_diaries_are_ascertainment(text, role):
    i = text.index("14 days")
    assert window_evidence.duration_role(text, i, i + len("14 days")) == role


def test_a_regimen_first_does_not_hide_the_real_window():
    txt = ("214 patients were randomized to receive Lactobacillus or placebo for 14 days. Patients recorded bowel frequency "
           "daily for 14 days. The primary outcome was the proportion of patients who developed AAD within 14 days of "
           "enrollment.")
    fu = compat_check._derive_follow_up({"name": "AAD"}, {"source": ""}, {"abstract": txt}, None)
    m = next(x for x in window_evidence.DURATION.finditer(txt)
             if window_evidence.duration_role(txt, x.start(), x.end()) != "DOSING")
    assert fu["value"] == "14 days" and m.start() > txt.index("placebo for 14 days") + 5, fu   # not the regimen


# ---- corpus radius of the NR-C04 window fixes (lane NR): two regressions caught and planted ---------------------------
PEARL = ("The percentage of children with AAD was significantly lower in the L. reuteri group compared to the placebo group "
         "at 14 days (7.9% vs. 16.7%; RR: 0.47, 95%CI 0.30-0.7; p < 0.001); at 21 days (8.8% vs. 17.9%; RR: 0.49, 95%CI "
         "0.32-0.74; p < 0.001); and at 56 days (9.1% vs. 19.6%; RR: 0.46, 95%CI 0.30-0.69; p < 0.001).")


def test_an_enumerated_timepoint_owns_the_estimate_attached_to_it():
    # PEARL 40488914: RR 0.46 is the 56-day result; 'earliest window wins' gave it 14 days
    assert window_evidence.result_window(PEARL, [0.46])[0] == "56 days"
    assert window_evidence.result_window(PEARL, [0.47])[0] == "14 days"


def test_without_an_attached_group_the_governing_window_still_wins():
    s = "At 90 days, mortality among patients discharged by day 28 was 12.0% vs 15.0% (RR 0.80)."
    assert window_evidence.result_window(s, [0.80])[0] == "90 days"
    assert window_evidence.result_window(PEARL)[0] == "14 days"      # no estimate: unchanged rule


def test_an_absent_row_with_no_result_owns_no_result_span():
    # GLAGOV 27846344, MACE not reported: its `source` is the IVUS primary sentence; 'to week 78' is not a MACE window
    row = {"state": "outcome_not_reported", "reason_code": "outcome_not_reported",
           "source": "GLAGOV (PMID 27846344) abstract: The primary efficacy measure was the nominal change in percent "
                     "atheroma volume (PAV) from baseline to week 78, measured by serial IVUS imaging."}
    assert compat_check._window_span(row, "Major adverse cardiovascular events") == ""
    fu = compat_check._derive_follow_up({"name": "Major adverse cardiovascular events"}, row, {"abstract": ""}, None)
    assert fu["value"] is None, fu
    refused = dict(row, refused_effect={"effect": 0.46, "ci_low": 0.3, "ci_high": 0.69, "scale": "RR"})
    assert compat_check._window_span(refused, "Major adverse cardiovascular events") != ""   # a refused result owns it


def test_an_absent_rows_trial_wide_source_still_gives_its_window():
    # CORP 21873705: an absent row's source that states the trial's follow-up keeps it (radius round 2)
    row = {"state": "outcome_not_reported", "source": "CORP (PMID 21873705) abstract: Patients were followed for 18 months."}
    fu = compat_check._derive_follow_up({"name": "Treatment discontinuation"}, row, {"abstract": ""}, None)
    assert fu["value"] == "18 months", fu


def test_a_decimal_follow_up_is_read_whole():
    fu = compat_check._derive_follow_up({"name": "Diabetic ketoacidosis"}, {"source": ""},
                                        {"abstract": "During a median of 2.0 years of follow-up, events occurred."}, None)
    assert fu["value"] == "2.0 years", fu


# ---- NOAC-AF review: the analysis set binds to the SELECTED analysis's own sentence -------------------------------------
ROCKET_TEXT = ("A total of 14,264 patients with nonvalvular atrial fibrillation who were at increased risk for stroke were "
               "randomly assigned to receive either rivaroxaban (at a daily dose of 20 mg) or dose-adjusted warfarin. The "
               "per-protocol, as-treated primary analysis was designed to determine whether rivaroxaban was noninferior to "
               "warfarin for the primary end point of stroke or systemic embolism. In the primary analysis, the primary end "
               "point occurred in 188 patients in the rivaroxaban group (1.7% per year) and in 241 in the warfarin group (2.2% "
               "per year) (hazard ratio in the rivaroxaban group, 0.79; 95% confidence interval [CI], 0.66 to 0.96; P<0.001 for "
               "noninferiority). In the intention-to-treat analysis, the primary end point occurred in 269 patients in the "
               "rivaroxaban group (2.1% per year) and in 306 patients in the warfarin group (2.4% per year) (hazard ratio, 0.88; "
               "95% CI, 0.74 to 1.03; P<0.001 for noninferiority; P=0.12 for superiority).")


def _rocket(effect, source):
    return {"label": "21830957", "id": "PMID 21830957", "effect": effect, "source": source, "study_effect": {}}


def test_rocket_itt_estimate_carries_itt_not_the_per_protocol_sentence():
    itt = _rocket(0.88, "abstract effect+CI (HR): In the intention-to-treat analysis, the primary end point occurred in 269 "
                        "patients in the rivaroxaban group (2.1% per year) and in 306 patients in the warfarin group (2.4% per "
                        "year) (hazard ratio, 0.88; 95% CI, 0.74 to 1.03; P<0.001 for noninferiority; P=0.12 for superiority).")
    assert compat_check._derive_analysis_set(itt, {"abstract": ROCKET_TEXT}, None)["value"] == "intention-to-treat"


def test_the_per_protocol_estimate_still_carries_per_protocol():
    pp = _rocket(0.79, "In the primary analysis, the primary end point occurred in 188 patients in the rivaroxaban group and "
                       "in 241 in the warfarin group (hazard ratio in the rivaroxaban group, 0.79; 95% CI, 0.66 to 0.96).")
    assert compat_check._derive_analysis_set(pp, {"abstract": ROCKET_TEXT}, None)["value"] == "per-protocol"


def test_an_analysis_statement_reporting_another_estimate_never_labels_this_row():
    row = _rocket(0.88, "")          # no owning sentence: only the text, whose per-protocol statement reports 0.79
    assert compat_check._derive_analysis_set(row, {"abstract": ROCKET_TEXT}, None)["value"] == "intention-to-treat"


def test_a_population_statement_is_not_attached_to_the_next_sentences_estimate():
    # EMPACTA (33332779): the mITT population sentence stands on its own; the next sentence's estimate is not its
    text = ("RESULTS: A total of 389 patients underwent randomization, and the modified intention-to-treat population "
            "included 249 patients in the tocilizumab group and 128 patients in the placebo group. The cumulative "
            "percentage of patients who had received mechanical ventilation or who had died by day 28 was 12.0% and 19.3% "
            "(hazard ratio, 0.56; 95% CI, 0.33 to 0.97).")
    row = {"label": "33332779", "id": "PMID 33332779", "effect": 0.73, "source": "", "study_effect": {}}
    assert compat_check._derive_analysis_set(row, {"abstract": text}, None)["value"] == "modified intention-to-treat"
