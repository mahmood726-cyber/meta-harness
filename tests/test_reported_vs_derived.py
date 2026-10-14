"""Plants (A7, external audit r30-C; r1 CORP): a SOURCE-REPORTED effect and the effect DERIVED from the same source's
arm counts that disagree beyond rounding are a TYPED state, SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE: both values
are kept, each with its span, and neither is pooled until a person adjudicates. Never a silent pick of the counts,
never 'not in source'. The PICU pilot (39935568) prints 30% v 55.5% of 10 v 9 (3/10 v 5/9 = RR 0.54) and RR 0.59
(0.21-1.6); these constructed abstracts reproduce that disagreement."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import absence, extract  # noqa: E402

I, C, KW = ["LGG", "probiotic"], ["placebo"], ["antibiotic-associated diarr"]
COUNTS = ("Antibiotic-associated diarrhea occurred in 3/10 (30%) patients given LGG and 5/9 (55.6%) given "
          "placebo")
STATE = "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE"


def _x(abstract):
    return extract.extract_trial(abstract, KW, I, C, estimand="RR")


def test_PLANT_picu_reported_rr_and_count_derived_rr_disagree_is_a_typed_state():
    out = _x(COUNTS + " (relative risk 0.59, 95% CI 0.21-1.60).")
    assert out.get("absent") is True and out.get("state") == STATE, out
    rep, der = out["reported"], out["count_derived"]
    assert (rep["scale"], rep["effect"], rep["ci_low"], rep["ci_high"]) == ("RR", 0.59, 0.21, 1.6)
    assert (der["ai"], der["n1i"], der["ci"], der["n2i"]) == (3, 10, 5, 9)
    assert abs(der["effect"] - 0.54) < 1e-9 and der["scale"] == "RR"
    assert "0.59" in rep["span"] and "3/10" in der["span"]
    assert "ai" not in out and "effect" not in out          # neither value is offered for pooling


def test_the_reported_effect_in_another_sentence_is_compared_too():
    out = _x(COUNTS + ". The risk of antibiotic-associated diarrhea was lower with LGG (RR 0.59, 95% CI 0.21-1.60).")
    assert out.get("state") == STATE, out
    assert "RR 0.59" in out["reported"]["span"] and "3/10" in out["count_derived"]["span"]


import pytest  # noqa: E402


@pytest.mark.xfail(strict=True, reason="A7 part 2 (named limit): extract_effect does not read 'relative risk of X was "
                                       "N (95% CI a-b)' (PICU prints 'The RR ratio for AAD when using LGG was 0.59 "
                                       "(95% CI, 0.21-1.6)'), so there is no reported value to compare")
def test_LIMIT_a_relative_risk_of_x_was_n_sentence_is_read():
    out = _x(COUNTS + ". The relative risk of antibiotic-associated diarrhea was 0.59 (95% CI 0.21-1.60).")
    assert out.get("state") == STATE, out


def test_agreement_within_rounding_still_pools_the_counts():
    out = _x(COUNTS + " (relative risk 0.54, 95% CI 0.17-1.66).")
    assert (out.get("ai"), out.get("n1i"), out.get("ci"), out.get("n2i")) == (3, 10, 5, 9), out
    # 0.54 printed to 2 dp; derived 0.5400 -> agrees. One printed decimal is a coarser tolerance: 0.5 agrees with 0.54
    out = _x(COUNTS + " (relative risk 0.5, 95% CI 0.2-1.7).")
    assert out.get("ai") == 3, out


def test_a_gross_mismatch_is_the_same_typed_state_not_an_untyped_string():
    # the existing round-trip refusal (19138244 class) is generalised into the typed state
    out = _x(COUNTS + " (relative risk 0.20, 95% CI 0.05-0.80).")
    assert out.get("state") == STATE, out
    assert out["reported"]["effect"] == 0.2 and out.get("gross") is True
    assert "different outcome" in out["reason"]


def test_an_adjusted_reported_effect_is_a_different_estimand_and_is_not_compared():
    # named limit: an ADJUSTED effect is not expected to equal the crude count-derived one
    out = _x(COUNTS + " (adjusted relative risk 0.59, 95% CI 0.21-1.60).")
    assert out.get("ai") == 3 and out.get("state") != STATE, out


def test_the_classifier_keeps_the_typed_state_with_both_spans():
    out = _x(COUNTS + " (relative risk 0.59, 95% CI 0.21-1.60).")
    row = {"id": "PMID 1", "absent_kind": "machine_absent", "reason": out["reason"], **out}
    ann = absence.classify_reason(KW, COUNTS + " (relative risk 0.59, 95% CI 0.21-1.60).", None,
                                  outcome_name="Antibiotic-associated diarrhoea", declared_estimand="RR",
                                  reason=out["reason"], absent_kind="machine_absent", row=row)
    assert ann["reason_code"] == STATE and ann["state"] == STATE
    assert "0.59" in ann["state_basis"] and "0.54" in ann["state_basis"]
    assert absence.SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE == STATE


def test_every_consumer_knows_the_state():
    from harness import consumer_consistency, page, reason_audit, harms
    assert STATE in consumer_consistency.VALUE_REASON_CODES
    assert STATE in reason_audit._VALUE_PRESENT_CODES
    assert STATE in page._ABSENCE_STATE_LABEL
    assert STATE in harms._INCOMPATIBLE_CODES


# ---- sweep over the served 32 (11 Oct register, A7): false positives and the gross class, plants that failed first ----
def test_a_regression_controlled_or_is_a_different_estimand_not_a_disagreement():
    # probiotics 17604300: 'Logistic regression to control for other factors gave an odds ratio 0.25 (0.07 to 0.85)'
    ab = ("RESULTS: 7/57 (12%) of the probiotic group developed antibiotic-associated diarrhoea compared with 19/56 "
          "(34%) in the placebo group (P=0.007). Logistic regression to control for other factors gave an odds ratio "
          "0.25 (95% confidence interval 0.07 to 0.85) for antibiotic-associated diarrhoea.")
    out = extract.extract_trial(ab, ["antibiotic-associated diarr"], ["probiotic"], ["placebo"], estimand="OR")
    assert out.get("ai") == 7 and out.get("state") != STATE, out


def test_a_rate_ratio_is_not_compared_with_a_count_derived_risk_ratio():
    # RECOVERY tocilizumab 33933206: 'died within 28 days (rate ratio 0.85; 95% CI 0.76-0.94)' v crude 0.882
    ab = ("Overall, 621 (31%) of the 2022 patients allocated tocilizumab and 729 (35%) of the 2094 patients allocated "
          "to usual care died within 28 days (rate ratio 0.85; 95% CI 0.76-0.94; p=0.0028).")
    out = extract.extract_trial(ab, ["died within 28 days", "28-day mortality"], ["tocilizumab"], ["usual care"],
                                estimand="RR")
    assert out.get("ai") == 621 and out.get("state") != STATE, out


def test_the_rounding_class_is_terminal_and_the_gross_class_is_not():
    # gross = the counts belong to a different outcome (spironolactone 28824029: a composite's HR bound to the death
    # counts) -- a lower rung may still supply the outcome's own value; a rounding disagreement on one outcome sentence
    # is the source disagreeing with itself and nothing else may replace it until adjudicated
    rnd = _x(COUNTS + " (relative risk 0.59, 95% CI 0.21-1.60).")
    grs = _x(COUNTS + " (relative risk 0.20, 95% CI 0.05-0.80).")
    assert rnd["terminal"] is True and grs["terminal"] is False


def test_PLANT_corp_relative_risk_049_v_counts_051_is_the_typed_state():
    # colchicine-recurrent-pericarditis 24694983 (CORP; external audit r1): 26/120 v 51/120 = 0.5098, printed RR 0.49
    ab = ("The proportion of patients who had recurrent pericarditis was 26 (21.6%) of 120 in the colchicine group and "
          "51 (42.5%) of 120 in the placebo group (relative risk 0.49; 95% CI 0.24-0.65; p=0.0009; number needed to "
          "treat 5).")
    out = extract.extract_trial(ab, ["recurrent pericarditis"], ["colchicine"], ["placebo"], estimand="RR")
    assert out.get("state") == STATE and out["terminal"] is True, out
    assert out["reported"]["effect"] == 0.49 and (out["count_derived"]["ai"], out["count_derived"]["ci"]) == (26, 51)


# ---- A7 review round 1 (codex a7-r1 mc-028f887d, 2 P1): plants that failed first ----
def test_precision_is_read_from_the_reported_effect_not_an_equal_number_elsewhere():
    s = "At 0.5 years, mortality was 27/100 versus 50/100 (RR 0.50, 95% CI 0.30-0.80)."
    out = extract.reported_vs_count_derived((27, 100, 50, 100), ("RR", 0.50, 0.30, 0.80), s, s)
    assert out and out["state"] == STATE and out["terminal"] is True, out


def test_an_adjusted_estimate_beside_an_unadjusted_one_does_not_exempt_the_unadjusted_one():
    s = "Mortality was 27/100 versus 50/100 (unadjusted RR 0.50, 95% CI 0.30-0.80; adjusted RR 0.54, 95% CI 0.32-0.85)."
    out = extract.reported_vs_count_derived((27, 100, 50, 100), ("RR", 0.50, 0.30, 0.80), s, s)
    assert out and out["state"] == STATE and out["terminal"] is True, out
    # and the adjusted one, when it is the value compared, is still exempt
    assert extract.reported_vs_count_derived((27, 100, 50, 100), ("RR", 0.54, 0.32, 0.85), s, s) is None


def test_an_adjusted_label_before_the_parenthesis_still_exempts_the_value_inside_it():
    # probiotics 7872284 (sweep, after the r1 fix): 'the adjusted relative risk was significantly protective for S.
    # boulardii (RR = 0.29, 95% CI = 0.08, 0.98)' v crude 7/97 v 14/96 = 0.495
    s = ("Using a multivariate model to adjust for two independent risk factors, the adjusted relative risk was "
         "significantly protective for S. boulardii (RR = 0.29, 95% CI = 0.08, 0.98).")
    assert extract.reported_vs_count_derived((7, 97, 14, 96), ("RR", 0.29, 0.08, 0.98), s, s) is None
