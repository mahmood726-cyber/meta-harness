"""The regex extractor's MISATTRIBUTION class, found by the captain's adjudications by quoted span (7 Oct): the hand-entered
value was right and the extractor misread. One plant per class, each on the REAL sentence of the adjudicated case,
plus the guard that keeps the old behaviour where it was right.

  first-HR-in-sentence  doac 19966341 'Any bleeding'          0.82 (major bleeding) -> 0.71 (any bleeding)
  broader outcome       probiotics 15740542 AAD                RR 0.3 (any diarrhoea) -> 4/119 vs 22/127 (AAD)
  total-as-arm          probiotics 39529939 'Any adverse events' 10/564 (the total) never an arm -> 7/285 vs 3/279
  factorial / bare CI   omega3 21115589 (SU.FOL.OM3, 2x2)       refused -> HR 1.08 (0.79-1.47), the omega-3 factor
  number-word counts    probiotics 18026577 AAD                 OR 0.34 -> 7/44 vs 16/45 (counts, RR estimand)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import extract as X  # noqa: E402

DOAC = ("Major bleeding episodes occurred in 20 patients assigned to dabigatran (1.6%) and in 24 patients assigned to "
        "warfarin (1.9%) (hazard ratio with dabigatran, 0.82; 95% CI, 0.45 to 1.48), and episodes of any bleeding were "
        "observed in 205 patients assigned to dabigatran (16.1%) and 277 patients assigned to warfarin (21.9%; hazard "
        "ratio with dabigatran, 0.71; 95% CI, 0.59 to 0.85).")
SBOUL = ("RESULTS: Patients receiving S. boulardii had a lower prevalence of diarrhoea (> or =3 loose or watery stools/day "
         "for > or =48 h occurring during or up to 2 weeks after the antibiotic therapy) than those receiving placebo "
         "[nine of 119 (8%) vs. 29 of 127 (23%), relative risk: 0.3, 95% confidence interval: 0.2-0.7]. S. boulardii also "
         "reduced the risk of antibiotic-associated diarrhoea (diarrhoea caused by Clostridium difficile or otherwise "
         "unexplained diarrhoea) compared with placebo [four of 119 (3.4%) vs. 22 of 127 (17.3%), relative risk: 0.2; 95% "
         "confidence interval: 0.07-0.5].")
SBOUL_KWS = ["antibiotic-associated diarr", "prevalence of diarrhoea"]
AE = ("Of 564 participants included in the safety analysis, only 1.8% (10/564) experienced an AE: 2.5% (7/285) in the "
      "studied probiotic mix and 1.1% (3/279) in the placebo group.")
SUFOLOM3 = ("DESIGN: Double blind, randomised, placebo controlled trial; factorial design. RESULTS: Allocation to B vitamins "
            "lowered plasma homocysteine concentrations by 19% compared with placebo, but had no significant effects on "
            "major vascular events (75 v 82 patients, hazard ratio, 0.90 (95% confidence interval 0.66 to 1.23, P=0.50)). "
            "Allocation to omega 3 fatty acids increased plasma concentrations of omega 3 fatty acids by 37% compared with "
            "placebo, but also had no significant effect on major vascular events (81 v 76 patients, hazard ratio 1.08 "
            "(0.79 to 1.47, P=0.64)).")
LACTO = ("RESULTS: Among 89 randomized patients, antibiotic-associated diarrhea occurred in seven of 44 patients (15.9%) in "
         "the lactobacilli group and in 16 of 45 patients (35.6%) in the placebo group (OR 0.34, 95% CI 0.125-0.944; "
         "P=0.04).")


def test_first_hr_in_sentence_is_read_from_the_outcomes_own_clause():
    r = X.extract_trial(DOAC, ["any bleeding"], ["dabigatran"], ["warfarin"], declared_composite=False, estimand="HR")
    assert (r.get("effect"), r.get("ci_low"), r.get("ci_high")) == (0.71, 0.59, 0.85)
    # the keyword of the FIRST clause still reads the first effect
    r = X.extract_trial(DOAC, ["major bleeding"], ["dabigatran"], ["warfarin"], declared_composite=False, estimand="HR")
    assert r.get("effect") == 0.82


def test_a_shared_trailing_outcome_noun_keeps_the_first_effect():
    # prone 19903918: the keyword follows every effect, so no clause names it -> the old reading stands (0.97)
    s = ("RESULTS: Prone and supine patients had similar 28-day (31.0% vs 32.8%; relative risk [RR], 0.97; 95% confidence "
         "interval [CI], 0.84-1.13; P = .72) and 6-month (47.0% vs 52.3%; RR, 0.90; 95% CI, 0.73-1.11; P = .33) "
         "mortality rates.")
    assert X.extract_effect_for(s, ["mortality"])[1] == 0.97
    assert X.extract_effect_for("hazard ratio 0.5 (95% CI 0.3 to 0.8)", ["x"])[1] == 0.5     # one effect: unchanged


def test_the_broader_outcomes_sentence_yields_to_the_one_that_names_the_outcome():
    r = X.extract_trial(SBOUL, SBOUL_KWS, ["S. boulardii", "Saccharomyces"], ["placebo"], declared_composite=False,
                        estimand="RR", outcome_name="Antibiotic-associated diarrhoea")
    assert (r.get("ai"), r.get("n1i"), r.get("ci"), r.get("n2i")) == (4, 119, 22, 127)
    # without the name the two sentences disagree -> refused (R4), never the first
    r = X.extract_trial(SBOUL, SBOUL_KWS, ["S. boulardii", "Saccharomyces"], ["placebo"], declared_composite=False,
                        estimand="RR")
    assert r.get("absent")


def test_the_named_reading_is_kept_only_when_it_yields_a_value():
    # a name carried only by a sentence with NO numbers never displaces the result sentence
    t = ("BACKGROUND: Antibiotic-associated diarrhoea is common. RESULTS: Diarrhoea developed in 4 of 119 patients "
         "(3.4%) receiving S. boulardii and 22 of 127 patients (17.3%) receiving placebo.")
    r = X.extract_trial(t, ["antibiotic-associated diarr", "diarrhoea developed"], ["S. boulardii"], ["placebo"],
                        declared_composite=False, estimand="RR", outcome_name="Antibiotic-associated diarrhoea")
    assert (r.get("ai"), r.get("ci")) == (4, 22)


def test_a_total_is_never_an_arm():
    assert tuple(X.extract_arm_counts(AE, ["probiotic"], ["placebo"])) == (7, 285, 3, 279)
    # no group is the sum of two others -> nothing is dropped: the reading is exactly the old one (three-group
    # readings are the separate R4 rule's business, unchanged here)
    assert tuple(X.extract_arm_counts("1.8% (10/560) overall: 2.5% (7/285) probiotic and 1.1% (3/279) placebo",
                                      ["probiotic"], ["placebo"])) == (10, 560, 7, 285)


def test_a_factorial_trials_omega3_factor_is_read_from_its_own_unlabelled_ci_sentence():
    r = X.extract_trial(SUFOLOM3, ["major vascular events"], ["omega 3", "omega-3"], ["placebo"], declared_composite=True,
                        estimand="RR")
    assert (r.get("effect"), r.get("ci_low"), r.get("ci_high"), r.get("scale")) == (1.08, 0.79, 1.47, "HR")
    # the co-randomised factor's clause never counts: a merged sentence naming omega-3 but holding the B-vitamin effect
    merged = ("Allocation to B vitamins had no significant effect on major vascular events (28 v 32 patients, hazard "
              "ratio 0.88 (0.53 to 1.46), P=0.61), and allocation to omega 3 fatty acids is reported below")
    assert X.extract_effect_for(merged, ["major vascular events"], require_terms=["omega 3"]) is None


def test_a_number_word_count_is_read_and_the_counts_win_for_a_risk_ratio():
    r = X.extract_trial(LACTO, ["antibiotic-associated diarr"], ["lactobacilli"], ["placebo"], declared_composite=False,
                        estimand="RR")
    assert (r.get("ai"), r.get("n1i"), r.get("ci"), r.get("n2i")) == (7, 44, 16, 45)
    # a compound is not its last word: 'twenty-nine of 127 (23%)' is never 9 of 127
    assert X.extract_arm_counts("twenty-nine of 127 (23%) vs four of 119 (3.4%)", ["x"], ["y"]) is None


def test_a_measure_word_keyword_never_decides_the_clause():
    # CREDENCE 30990260: the HHF keyword list holds 'hazard ratio', which every clause carries
    s = ("The canagliflozin group also had a lower risk of cardiovascular death, myocardial infarction, or stroke (hazard "
         "ratio, 0.80; 95% CI, 0.67 to 0.95; P = 0.01) and hospitalization for heart failure (hazard ratio, 0.61; 95% CI, "
         "0.47 to 0.80; P<0.001).")
    assert X.extract_effect_for(s, ["hospitalization for heart failure", "hazard ratio", "HR"])[1] == 0.61


def test_with_no_outcome_clause_the_one_clause_naming_our_intervention_decides():
    s = ("Fish oil (RR 0.28, 95% CI 0.09 to 0.90), non-steroidal anti-inflammatory drugs (RR 0.37, 95% CI 0.23 to 0.59) "
         "and colchicine (RR 0.37, 95% CI 0.23 to 0.59) may reduce the risk of postoperative atrial fibrillation.")
    assert X.extract_effect_for(s, ["atrial fibrillation"], interv_terms=["colchicine"])[1:] == (0.37, 0.23, 0.59)
    assert X.extract_effect_for(s, ["atrial fibrillation"])[1] == 0.28          # no intervention given: first, as before


def test_a_slash_composite_is_a_composite_and_its_effect_never_binds_a_single_outcome():
    # VERTIS CV (33026243): 'first HHF/CV death' (0.88) bound the 'first HHF' keyword; first HHF alone is 0.70
    t = ("Ertugliflozin did not significantly reduce first HHF/CV death (hazard ratio [HR], 0.88 [95% CI, 0.75-1.03]). "
         "Overall, ertugliflozin reduced risk for first HHF (HR, 0.70 [95% CI, 0.54-0.90]; P=0.006).")
    r = X.extract_trial(t, ["first HHF", "HHF", "hazard ratio", "HR"], ["ertugliflozin"], ["placebo"],
                        declared_composite=False, estimand="HR")
    assert (r.get("effect"), r.get("ci_low"), r.get("ci_high")) == (0.7, 0.54, 0.9)
    assert X._names_composite("first HHF/CV death") and not X._names_composite("47/120 patients died")


def test_a_composite_naming_sentence_yields_only_its_non_composite_outcome_clause():
    # CANVAS (29526832): the sentence names two composites and then HF hospitalisation alone
    s = ("Overall, cardiovascular death or hospitalized HF was reduced in those treated with canagliflozin compared with "
         "placebo (16.3 versus 20.8 per 1000 patient-years; hazard ratio [HR], 0.78; 95% confidence interval [CI], "
         "0.67-0.91), as was fatal or hospitalized HF (HR, 0.70; 95% CI, 0.55-0.89) and hospitalized HF alone (HR, 0.67; "
         "95% CI, 0.52-0.87).")
    r = X.extract_trial(s, ["hospitalized HF alone", "HHF", "hazard ratio", "HR"], ["canagliflozin"], ["placebo"],
                        declared_composite=False, estimand="HR")
    assert (r.get("effect"), r.get("ci_low"), r.get("ci_high")) == (0.67, 0.52, 0.87)
    # a composite sentence whose only outcome-naming clause IS the composite gives nothing (the old skip, kept)
    assert X.extract_effect_for("cardiovascular death or hospitalized HF alone (HR, 0.78; 95% CI, 0.67-0.91)",
                                ["hospitalized HF alone"], single_outcome_clause=True) is None
