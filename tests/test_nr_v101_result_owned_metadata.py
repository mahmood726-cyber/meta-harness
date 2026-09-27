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
