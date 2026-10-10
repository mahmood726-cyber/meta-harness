"""ONE target-aware value predicate (reviews 16 + 23), shared by reason_audit.audit_reason_row and
unextracted.audit_pair: a held candidate counts only if it is a value FOR THE TARGET (outcome identity + protocol
timepoint) and it overturns a refusal only if it overcomes THAT refusal. Fixed strings from the held sources the
auditors cite."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import absence, reason_audit as ra, unextracted as ux  # noqa: E402

MORT = {"name": "Mortality", "keywords": ["mortality", "death", "died", "critically ill", "intensive care", "ICU",
                                          "primary outcome", "primary end point", "primary endpoint"],
        "timepoint": "28-90 day or in-hospital"}
SMART_EXPOSURE = ("Only 426 patients (5.4%) in the balanced-crystalloids group and 343 patients (4.4%) in the saline group "
                  "received any volume of unassigned crystalloid as a result of remaining in the ICU from one calendar "
                  "month into the next.")
SPLIT_DEATH = ("Overall, 87 of 1152 patients (7.6%) in the buffered crystalloid group and 95 of 1110 patients (8.6%) in the "
               "saline group died in the hospital.")
WEIGHT = {"name": "Percent change in body weight", "keywords": ["change in body weight (%)", "body weight",
                                                                "primary outcome", "primary endpoint"],
          "timepoint": "Week 68", "timepoint_weeks": 68, "timepoint_tolerance_weeks": 8}
# STEP 11 (40825340), its own abstract, verbatim: a 44-week trial against a week-68 protocol
STEP11_W44 = ("At week 44, mean change in bodyweight was -16·0% (SE 0·7) in the semaglutide 2·4 mg group versus "
              "-3·1% (0·9) in the placebo group (p<0·0001), and a greater proportion of participants reached "
              "bodyweight reductions of ≥5% (96 [96%] vs 12 [25%]; p<0·0001).")
# the cached "full text" of 40825340 was another article's summary table of OTHER trials
OTHER_TABLE = ("Study Study design Study population Primary endpoints Key findings SELECT trial (semaglutide 2.4 mg) "
               "[ 9 ] Randomized, double-blind, placebo-controlled phase 3 trial 17,604 adults; change in body weight "
               "at week 68 was -9.4% vs -0.9%; 10 of 15 (67%) in the semaglutide group and 5 of 15 (33%) in the "
               "placebo group.")


def src(text, sid="abstract:1"):
    return [{"source_id": sid, "source_kind": "abstract", "text": text}]


def test_PLANT_r23_icu_exposure_counts_never_overturn_a_mortality_refusal():
    assert ra.target_value_match(src(SMART_EXPOSURE), MORT, "Mortality") is None
    row = {"reason_code": absence.OUTCOME_NOT_IN_SOURCE, "label": "SMART"}
    a = ra.audit_reason_row({"name": "Mortality"}, row, src(SMART_EXPOSURE), MORT)
    assert a["verdict"] != ra.REASON_FALSE_VALUE_HELD


def test_PLANT_r23_a_target_value_overturns_an_absence_claim_but_not_an_engine_refusal():
    absent = {"reason_code": absence.OUTCOME_NOT_IN_SOURCE}
    assert ra.audit_reason_row({"name": "Mortality"}, absent, src(SPLIT_DEATH), MORT)["verdict"] == \
        ra.REASON_FALSE_VALUE_HELD
    engine = {"reason_code": absence.ENGINE_CANNOT_CONSUME}
    a = ra.audit_reason_row({"name": "Mortality"}, engine, src(SPLIT_DEATH), MORT)
    assert a["verdict"] == ra.REASON_TRUE and "does not overcome" in a["detail"]


def test_PLANT_r16_a_value_only_at_a_non_protocol_timepoint_is_TIMEPOINT_MISMATCH_never_held_not_extracted():
    m = ra.target_value_match(src(STEP11_W44), WEIGHT, WEIGHT["name"])
    assert m["state"] == ra.TARGET_TIMEPOINT_MISMATCH and m["stated_weeks"] == [44.0]
    out = ux.audit_pair({"name": WEIGHT["name"], "trials": []}, "40825340", src(STEP11_W44), WEIGHT, None)
    assert out["status"] == ux.TIMEPOINT_MISMATCH
    # and the same value at week 68 IS held, not extracted
    w68 = STEP11_W44.replace("week 44", "week 68")
    assert ux.audit_pair({"name": WEIGHT["name"], "trials": []}, "x", src(w68), WEIGHT, None)["status"] == \
        ux.HELD_NOT_EXTRACTED


def test_PLANT_an_explicit_timepoint_refusal_takes_precedence_unless_an_in_window_value_overcomes_it():
    row = {"reason_code": absence.TIMEPOINT_MISMATCH, "reason": "timepoint mismatch: week 44"}
    out = ux.audit_pair({"name": WEIGHT["name"], "trials": []}, "x", src(STEP11_W44), WEIGHT, row)
    assert out["status"] == ux.ABSENT_BY_DESIGN
    no_tp = "The mean change in body weight was -9.3% with semaglutide and -2.1% with placebo (difference -7.2)."
    assert ux.audit_pair({"name": WEIGHT["name"], "trials": []}, "x", src(no_tp), WEIGHT, row)["status"] == \
        ux.ABSENT_BY_DESIGN                              # no stated timepoint: cannot overcome a timepoint refusal
    w68 = STEP11_W44.replace("week 44", "week 68")
    assert ux.audit_pair({"name": WEIGHT["name"], "trials": []}, "x", src(w68), WEIGHT, row)["status"] == \
        ux.HELD_NOT_EXTRACTED


def test_identity_terms_drop_population_setting_and_role_words():
    assert ra.identity_terms(MORT["keywords"], "Mortality") == ["Mortality", "mortality", "death", "died"]
    assert "primary outcome" not in ra.identity_terms(WEIGHT["keywords"], WEIGHT["name"])


def test_PLANT_r16_another_articles_table_of_other_trials_is_never_this_trials_value():
    assert ra.target_value_match(src(OTHER_TABLE, "fulltext:40825340"), WEIGHT, WEIGHT["name"]) is None
    m = ra.target_value_match(src(OTHER_TABLE, "fulltext:40825340") + src(STEP11_W44), WEIGHT, WEIGHT["name"])
    assert m["state"] == ra.TARGET_TIMEPOINT_MISMATCH          # the trial's OWN week-44 sentence decides


def test_PLANT_abbreviations_name_the_outcome_and_corroborated_counts_overcome_a_counts_refusal():
    # COCS 36286314 (colchicine-postop-af): 'POAF' names postoperative atrial fibrillation; the refusal said no
    # percentage-corroborated counts were found, and the abstract prints them
    spec = {"name": "Postoperative atrial fibrillation",
            "keywords": ["atrial fibrillation", "poaf", "postoperative af", "primary outcome"]}
    assert "poaf" in ra.identity_terms(spec["keywords"], spec["name"])
    assert not ra._is_abbreviation_of("ICU", "Mortality")
    text = "POAF was observed in 21 (18.6%) patients in the colchicine group and 39 (30.7%) in the placebo group."
    row = {"reason_code": absence.COUNTS_PRESENT_NOT_CORROBORATED}
    assert ra.audit_reason_row({"name": spec["name"]}, row, src(text), spec)["verdict"] == ra.REASON_FALSE_VALUE_HELD
    # without the percentages the counts refusal stands
    bare = "POAF was observed in 21 patients in the colchicine group and 39 in the placebo group (OR 0.52)."
    assert ra.audit_reason_row({"name": spec["name"]}, row, src(bare), spec)["verdict"] != ra.REASON_FALSE_VALUE_HELD
