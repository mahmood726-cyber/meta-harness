"""PLANT for harness.secondary_meta.gate_table_location: a recorded table-location proposal is admitted only when its
quote is verbatim, holds every number, NAMES the outcome, and is not a composite for a single declared outcome."""
from harness import secondary_meta as sm

TEXT = ("RESULTS In-hospital death occurred in 818 of 7942 patients (10.3%) in the balanced-crystalloids group and 875 "
        "of 7860 patients (11.1%) in the saline group. A major adverse kidney event within 30 days (the composite of "
        "death, new renal-replacement therapy, or persistent renal dysfunction) occurred in 1139 of 7942 patients "
        "(14.3%) in the balanced-crystalloids group and 1211 of 7860 (15.4%) in the saline group.")
KW = ["mortality", "death", "died", "primary outcome"]


def claim(quote, a, n1, c, n2):
    return {"state": "REPORTED", "quote": quote, "measure": None, "point": None, "lower": None, "upper": None,
            "events_t": a, "n_t": n1, "events_c": c, "n_c": n2}


def test_the_outcome_row_is_admitted():
    q = ("In-hospital death occurred in 818 of 7942 patients (10.3%) in the balanced-crystalloids group and 875 of "
         "7860 patients (11.1%) in the saline group.")
    v, why = sm.gate_table_location(claim(q, "818", "7942", "875", "7860"), TEXT, KW, "Mortality", prefer="counts")
    assert why == "ACCEPTED" and (v["events_t"], v["n_t"], v["events_c"], v["n_c"]) == (818, 7942, 875, 7860)


def test_a_composite_is_never_bound_to_a_single_outcome():
    q = ("A major adverse kidney event within 30 days (the composite of death, new renal-replacement therapy, or "
         "persistent renal dysfunction) occurred in 1139 of 7942 patients (14.3%) in the balanced-crystalloids group "
         "and 1211 of 7860 (15.4%) in the saline group.")
    v, why = sm.gate_table_location(claim(q, "1139", "7942", "1211", "7860"), TEXT, KW, "Mortality", prefer="counts")
    assert v is None and why == "COMPOSITE_QUOTED_FOR_SINGLE_OUTCOME"


def test_a_quote_that_does_not_name_the_outcome_is_refused():
    q = "1139 of 7942 patients (14.3%) in the balanced-crystalloids group and 1211 of 7860 (15.4%)"
    v, why = sm.gate_table_location(claim(q, "1139", "7942", "1211", "7860"), TEXT, KW, "Mortality", prefer="counts")
    assert v is None and why == "OUTCOME_NOT_NAMED_IN_QUOTE"


def test_a_quote_not_in_the_text_is_refused():
    v, why = sm.gate_table_location(claim("Death occurred in 10 of 100 and 20 of 100.", "10", "100", "20", "100"),
                                    TEXT, KW, "Mortality", prefer="counts")
    assert v is None and why == "QUOTE_NOT_IN_TEXT"


def _c(quote, **k):
    d = {"state": "REPORTED", "quote": quote, "measure": None, "point": None, "lower": None, "upper": None,
         "events_t": None, "n_t": None, "events_c": None, "n_c": None}
    d.update(k)
    return d


def test_an_inverted_ratio_is_refused():
    # colchicine 34876021: 'Total MACE | 8 (6.7) | 28 (21.7) | 3.52 (1.60-7.74)' -- events favour the drug, the HR is
    # the inverse comparison
    q = "Total MACE | 8 (6.7) | 28 (21.7) | 3.52 (1.60–7.74) | 0.001"
    v, why = sm.gate_table_location(_c(q, measure="HR", point="3.52", lower="1.60", upper="7.74", events_t="8",
                                       events_c="28"), "Results. " + q + " Other.", ["MACE"], "major adverse events")
    assert v is None and why == "RATIO_DIRECTION_CONTRADICTS_ARM_EVENTS"


def test_a_post_hoc_result_is_refused():
    q = ("In a post hoc analysis, the rate of major adverse cardiovascular events was lower with alirocumab than with "
         "placebo (hazard ratio, 0.52; 95% CI, 0.31 to 0.90).")
    v, why = sm.gate_table_location(_c(q, measure="HR", point="0.52", lower="0.31", upper="0.90"), q,
                                    ["major adverse cardiovascular events"], "Major adverse cardiovascular events")
    assert v is None and why == "SUBGROUP_OR_POST_HOC_QUOTED"


# ---- codex review, 3 Oct (each scenario is the reviewer's reproduction, asserting the requirement)

def test_a_minus_sign_must_be_printed():
    t = "Pain mean difference 2.5 (95% CI 1.2 to 3.8)"
    v, why = sm.gate_locator_claim(_c(t, measure="MD", point="-2.5", lower="-3.8", upper="-1.2"), t)
    assert v is None and why == "SIGN_NOT_IN_QUOTE"


def test_decimal_counts_are_refused_not_crashed():
    t = "Death: drug 10.5 of 100.0, placebo 20.0 of 100.0"
    v, why = sm.gate_locator_claim(_c(t, events_t="10.5", n_t="100.0", events_c="20.0", n_c="100.0"), t)
    assert v is None and why == "NON_INTEGER_COUNT"


def test_the_outcome_keyword_must_govern_the_numbers():
    q = "Mortality was similar. Stroke HR 0.80 (95% CI 0.60 to 0.95)"
    v, why = sm.gate_table_location(_c(q, measure="HR", point="0.80", lower="0.60", upper="0.95"), q,
                                    ["mortality"], "Mortality")
    assert v is None and why == "OUTCOME_DOES_NOT_GOVERN_THE_NUMBERS"


def test_a_subgroup_heading_before_the_quote_refuses():
    q = "Mortality HR 0.80 (95% CI 0.60 to 0.95)"
    t = "Subgroup analysis in women only. " + q
    v, why = sm.gate_table_location(_c(q, measure="HR", point="0.80", lower="0.60", upper="0.95"), t,
                                    ["mortality"], "Mortality")
    assert v is None and why == "SUBGROUP_OR_POST_HOC_QUOTED"


def test_arm_counts_follow_their_own_labels():
    q = "Mortality: drug 10 of 100; placebo 20 of 100"
    v, why = sm.gate_table_location(_c(q, events_t="20", n_t="100", events_c="10", n_c="100"), q, ["mortality"],
                                    "Mortality", prefer="counts", interv=["drug"], comp=["placebo"])
    assert v is None and why == "ARM_COUNTS_SWAPPED"
    v, why = sm.gate_table_location(_c(q, events_t="10", n_t="100", events_c="20", n_c="100"), q, ["mortality"],
                                    "Mortality", prefer="counts", interv=["drug"], comp=["placebo"])
    assert why == "ACCEPTED"
    q2 = "Mortality, placebo versus drug: HR 2.0 (95% CI 1.2 to 3.4)"
    v, why = sm.gate_table_location(_c(q2, measure="HR", point="2.0", lower="1.2", upper="3.4"), q2, ["mortality"],
                                    "Mortality", interv=["drug"], comp=["placebo"])
    assert v is None and why == "INVERSE_COMPARISON_QUOTED"
