"""Keyword-brittleness class: the generic 'primary outcome' anchor must be enabled when a
trial's primary IS our outcome (even when phrased differently), and rejected when it is a
different outcome that merely shares generic medical nouns (death/failure/causes).

These are the real sentences that broke the earlier rules:
 - DAPA-HF: our HF composite phrased 'worsening heart failure (...) or cardiovascular death'
   -- no exact keyword substring, must still link on {worsening, heart, cardiovascular}.
 - FIGARO-DKD: CV primary 'death from cardiovascular causes, MI, stroke, HF hospitalisation'
   shares death/causes/failure with a KIDNEY topic but no renal/kidney term -- must be
   rejected so the number is taken from FIGARO's kidney SECONDARY, not its CV primary.
 - COPPS-2: postpericardiotomy syndrome primary must not enable for an atrial-fibrillation topic.
"""
from harness.extract import _effective_kws, GENERIC_ANCHORS

HF_KWS = ["cardiovascular death or hospitalisation for heart failure",
          "worsening heart failure or cardiovascular death",
          "primary outcome", "primary endpoint", "primary end point"]
KIDNEY_KWS = ["kidney composite", "renal composite", "kidney failure",
              "estimated glomerular filtration rate", "death from renal causes",
              "primary outcome", "primary endpoint", "primary end point"]
AF_KWS = ["atrial fibrillation", "postoperative atrial fibrillation",
          "primary outcome", "primary endpoint"]

DAPA_HF = ("The primary outcome was a composite of worsening heart failure "
           "(hospitalization or an urgent visit resulting in intravenous therapy for heart "
           "failure) or cardiovascular death. A primary outcome event occurred in 386 of "
           "2373 patients in the dapagliflozin group and in 502 of 2371 in the placebo group.")
FIGARO = ("The primary outcome, assessed in a time-to-event analysis, was a composite of "
          "death from cardiovascular causes, nonfatal myocardial infarction, nonfatal stroke, "
          "or hospitalization for heart failure. The first secondary outcome was a composite "
          "of kidney failure, a sustained decrease from baseline of at least 40% in the eGFR, "
          "or death from renal causes. A primary outcome event occurred in 458 of 3686 "
          "patients in the finerenone group and in 519 of 3666 in the placebo group.")
COPPS2 = ("The primary outcome was postoperative pericardial or pleural effusion. "
          "The primary endpoint occurred in 45 of 180 patients in the colchicine group.")


def _enabled(abstract, kws):
    return any(k.lower() in GENERIC_ANCHORS for k in _effective_kws(abstract, kws))


def test_dapa_hf_recovers_generic_anchor():
    # our outcome IS DAPA-HF's primary, phrased differently -> anchor enabled
    assert _enabled(DAPA_HF, HF_KWS)


def test_figaro_cv_primary_rejected_for_kidney_topic():
    # FIGARO's CV primary is NOT our kidney outcome -> anchor must stay disabled,
    # so the number is read from the kidney secondary, never the CV primary counts.
    assert not _enabled(FIGARO, KIDNEY_KWS)


def test_figaro_enabled_for_a_cv_topic():
    # sanity: the same abstract SHOULD enable for a genuinely-CV topic
    cv_kws = ["cardiovascular death or myocardial infarction or stroke",
              "primary outcome", "primary endpoint"]
    assert _enabled(FIGARO, cv_kws)


def test_copps2_pericardial_primary_rejected_for_af_topic():
    assert not _enabled(COPPS2, AF_KWS)


def test_no_generic_anchor_returns_disease_only_unchanged():
    disease = ["atrial fibrillation"]
    assert _effective_kws(DAPA_HF, disease) == disease


# --- NEJM "primary COMPOSITE outcome" phrasing: the inserted adjective must not defeat the
#     anchor when the primary IS ours; a narrative RESULT mention in a substudy must NOT enable it.
FIDELIO = ("The primary composite outcome, assessed in a time-to-event analysis, was kidney "
           "failure, a sustained decrease of at least 40% in the eGFR from baseline, or death "
           "from renal causes. During a median follow-up of 2.6 years, a primary outcome event "
           "occurred in 504 of 2833 patients (17.8%) in the finerenone group and 600 of 2841 "
           "patients (21.1%) in the placebo group (hazard ratio, 0.82; 95% CI, 0.73 to 0.93).")
# PLATO diabetes SUBSTUDY: no outcome-definition sentence, only a narrative result mention and
# subgroup HRs. The generic anchor must stay disabled so no subgroup number is pooled.
PLATO_DM_SUBSTUDY = (
    "In the PLATO trial, ticagrelor reduced the primary composite endpoint of cardiovascular "
    "death, myocardial infarction, or stroke compared with clopidogrel. In patients with DM, "
    "the reduction in the primary composite endpoint (HR: 0.88, 95% CI: 0.76-1.03) was "
    "consistent. ticagrelor reduced the primary endpoint in patients with HbA1c above the "
    "median (HR: 0.80, 95% CI: 0.70-0.91).")
ACS_KWS = ["cardiovascular death, myocardial infarction, or stroke", "major adverse cardiovascular",
           "primary outcome", "primary endpoint", "primary end point"]


def test_nejm_primary_composite_outcome_recovers_anchor():
    # "primary composite outcome ... was kidney failure ..." -- composite splits the literal
    # substring, but the relaxed anchor + definition cue + renal keyword must enable it.
    assert _enabled(FIDELIO, KIDNEY_KWS)


def test_fidelio_primary_extracts_kidney_composite_counts():
    fx = _xt(FIDELIO, KIDNEY_KWS, ["finerenone"], ["placebo"], declared_composite=True)
    assert not fx.get("absent"), fx
    assert (fx["ai"], fx["n1i"], fx["ci"], fx["n2i"]) == (504, 2833, 600, 2841), fx


def test_substudy_narrative_mention_does_not_enable_anchor():
    # a RESULT mention ("reduced the primary composite endpoint of ...") is not a DEFINITION
    # sentence; the anchor must stay disabled so a median-split subgroup HR is never pooled.
    assert not _enabled(PLATO_DM_SUBSTUDY, ACS_KWS)
    fx = _xt(PLATO_DM_SUBSTUDY, ACS_KWS, ["ticagrelor"], ["clopidogrel"], declared_composite=True)
    assert fx.get("absent"), fx


# --- component-as-composite class (the dangerous one: a component and the MACE composite can
#     share a point estimate; only endpoint identity separates them). SUSTAIN-6 primary MACE is
#     HR 0.74 (0.58-0.95) / 108 of 1648 vs 146 of 1649; its nonfatal-MI COMPONENT is HR 0.74
#     (0.51-1.08). A 3-point-MACE topic whose keywords INCLUDE the component names must still pool
#     the composite, never the component.
MACE_KWS = ["major adverse cardiovascular events", "MACE", "3-point MACE",
            "cardiovascular death", "nonfatal myocardial infarction", "nonfatal stroke",
            "primary composite outcome", "primary outcome", "primary endpoint", "primary end point"]
SUSTAIN6 = ("The primary composite outcome was the first occurrence of cardiovascular death, "
            "nonfatal myocardial infarction, or nonfatal stroke. The primary outcome occurred in "
            "108 of 1648 patients (6.6%) in the semaglutide group and in 146 of 1649 patients "
            "(8.9%) in the placebo group (hazard ratio, 0.74; 95% confidence interval [CI], 0.58 "
            "to 0.95; P<0.001). Nonfatal myocardial infarction occurred in 2.9% of patients in the "
            "semaglutide group and 3.9% in the placebo group (hazard ratio, 0.74; 95% CI, 0.51 to "
            "1.08). Nonfatal stroke occurred in 1.6% vs 2.7% (hazard ratio, 0.61; 95% CI, 0.38 to 0.99).")


def test_sustain6_pools_primary_mace_not_mi_component():
    fx = _xt(SUSTAIN6, MACE_KWS, ["semaglutide"], ["placebo"], declared_composite=True)
    assert not fx.get("absent"), fx
    # counts path preferred: the primary MACE 2x2, NOT the MI-component effect (CI 0.51-1.08)
    if "ai" in fx and fx["ai"] is not None:
        assert (fx["ai"], fx["n1i"], fx["ci"], fx["n2i"]) == (108, 1648, 146, 1649), fx
    else:
        assert fx.get("ci_low") == 0.58 and fx.get("ci_high") == 0.95, fx
        assert fx.get("ci_low") != 0.51, "pooled the nonfatal-MI component, not the MACE composite"


# --- FIGARO kidney SECONDARY composite IS the correct pool for a kidney-composite topic (its CV
#     primary must be rejected -- covered above -- and its kidney secondary is our target).
# --- generic-harm guard: a SPECIFIC harm outcome must be selected on its discriminating keyword,
#     never on a bare "adverse events occurred in N ..." sentence (that count is ANY-AE). ---
GI_KWS = ["gastrointestinal", "diarrh", "adverse effect", "adverse event", "side effect"]
ANY_AE_KWS = ["adverse event", "adverse events", "side effect", "tolerability", "safety"]
AE_SENTENCE = ("Adverse events occurred in 21 patients (11.7%) in the placebo group vs 36 (20.0%) "
               "in the colchicine group (absolute difference, 8.3%), but discontinuation rates "
               "were similar.")


from harness.extract import _outcome_sentences


def test_generic_ae_sentence_not_selected_for_gastrointestinal_outcome():
    # a SPECIFIC GI outcome has discriminating keywords (gastrointestinal/diarrh); the bare
    # "adverse events occurred ..." sentence has neither, so it must NOT be selected.
    assert _outcome_sentences(AE_SENTENCE, GI_KWS) == []


def test_generic_ae_sentence_still_selected_for_generic_outcome():
    # a genuinely generic "any adverse events" outcome (only generic-harm keywords) SHOULD select it
    assert len(_outcome_sentences(AE_SENTENCE, ANY_AE_KWS)) == 1


def test_figaro_pools_kidney_secondary_not_cv_primary():
    fx = _xt(FIGARO, KIDNEY_KWS, ["finerenone"], ["placebo"], declared_composite=True)
    # FIGARO in test_extract_class's fixture states the CV primary counts (458/3686); those must
    # NOT be pooled for a kidney topic. Either absent or the kidney secondary -- never 458/3686.
    if not fx.get("absent"):
        assert not (fx.get("ai") == 458 and fx.get("n1i") == 3686), \
            "pooled FIGARO's CV primary counts for a kidney-composite topic"


# --- scale-label correctness: the conjunction "or" must not be read as an odds ratio ---
from harness.extract import _EFFECT, _effect_from_match


def _scale(sentence):
    m = _EFFECT.search(sentence)
    return _effect_from_match(m)[0] if m else None


def test_conjunction_or_not_read_as_odds_ratio():
    # "CV death or HHF (RR ...)" must be RR, not OR (the bug that mislabelled a comparator)
    assert _scale("the occurrence of CV death or HHF (RR = 0.83, 95% CI 0.77-0.89)") == "RR"


def test_real_odds_ratio_still_OR():
    assert _scale("summary OR, 0.86 [95% CI, 0.79-0.95]") == "OR"
    assert _scale("pooled odds ratio [OR] 0.77 [95% CI 0.63-0.93]") == "OR"


def test_hazard_ratio_still_HR():
    assert _scale("hazard ratio 0.80; 95% CI 0.73 to 0.87") == "HR"


# --- percentage-first arm counts "P% (N/M)" (recovers trials like PMID 22472744) ---
from harness.extract import extract_arm_counts


def test_percentage_first_arm_counts():
    s = ("AAD developed in 13.3% (13/98) of the patients receiving placebo and in 15.1% "
         "(16/106) of those receiving S. boulardii.")
    arms = extract_arm_counts(s, ["S. boulardii", "probiotic"], ["placebo"])
    assert arms == (16, 106, 13, 98), arms  # (ai,n1i,ci,n2i): interv S.boulardii vs placebo


# --- round-trip validation: refuse when count-derived effect contradicts the reported effect ---
from harness.extract import _roundtrip_ok, extract_trial as _xt


def test_roundtrip_accepts_matching_rr():
    assert _roundtrip_ok(386, 2373, 502, 2371, "RR", 0.77)


def test_roundtrip_refuses_gross_magnitude_mismatch():
    # counts imply ~0.78; a wrong 15-event OM reported as 0.20 must be refused (EMPEROR class)
    assert not _roundtrip_ok(361, 1863, 462, 1867, "RR", 0.20)


def test_roundtrip_refuses_direction_contradiction_for_hr():
    # counts protective (~0.77) but reported HR 1.5 (harm) -> refuse
    assert not _roundtrip_ok(386, 2373, 502, 2371, "HR", 1.5)


def test_roundtrip_allows_hr_same_direction():
    assert _roundtrip_ok(386, 2373, 502, 2371, "HR", 0.80)


def test_extract_trial_refuses_when_counts_contradict_reported_effect():
    # PMID 19138244 shape: counts imply RR 0.46 but the abstract reports RR 1.63 -> refuse
    ab = ("Antibiotic-associated diarrhoea occurred in 6/16 (37%) in the placebo group and "
          "4/23 (17%) patients in the probiotic group (RR 1.63, 95% CI 0.73-3.65).")
    ex = _xt(ab, ["antibiotic-associated diarrhoea", "diarrhoea"], ["probiotic"], ["placebo"])
    assert ex.get("absent") and "round-trip" in ex.get("reason", "")


# --- factorial-design guard: bind OUR factor, never the co-randomised one (SU.FOL.OM3 class) ---
def test_factorial_guard_binds_our_factor_not_the_other():
    ab = ("In a 2x2 factorial trial, patients were allocated to B vitamins or placebo and to n-3 "
          "fatty acids or placebo. Allocation to B vitamins had no effect (hazard ratio 0.90, 95% "
          "CI 0.80-1.10). Major vascular events occurred with n-3 fatty acids at a hazard ratio of "
          "1.08 (95% CI 0.79-1.47).")
    ex = _xt(ab, ["major vascular events"], ["n-3 fatty acids", "n-3"], ["placebo"])
    assert ex.get("effect") == 1.08, ex  # the omega-3 factor, not the B-vitamin 0.90


def test_factorial_guard_refuses_when_our_factor_not_named():
    ab = ("In a 2x2 factorial trial of B vitamins and fish oil, allocation to B vitamins had a "
          "hazard ratio of 0.90 (95% CI 0.80-1.10) for major vascular events.")
    ex = _xt(ab, ["major vascular events"], ["n-3 fatty acids", "omega-3"], ["placebo"])
    assert ex.get("absent") and "factorial" in ex.get("reason", "")


# --- spelled-out CI marker: "95 percent confidence interval" (RALES class) ---
def test_spelled_out_confidence_interval_parses():
    ex = _xt("The relative risk of death was 0.70; 95 percent confidence interval, 0.60 to 0.82.",
             ["death", "mortality"], ["spironolactone"], ["placebo"])
    assert ex.get("effect") == 0.70 and ex.get("ci_low") == 0.60, ex


# --- multi-arm dose guard: refuse dose-ranging trials unless the dose is specified (CANTOS class) ---
def test_multi_arm_dose_guard_refuses_unspecified():
    ab = ("In the 50-mg group the hazard ratio was 0.93 (95% CI 0.80 to 1.07); in the 150-mg "
          "group 0.85 (95% CI 0.74 to 0.98); in the 300-mg group 0.86 (95% CI 0.75 to 0.99).")
    ex = _xt(ab, ["major adverse cardiovascular"], ["canakinumab"], ["placebo"])
    assert ex.get("absent") and "multi-arm" in ex.get("reason", "")


def test_multi_arm_guard_inert_on_single_dose():
    # a single-dose trial must NOT trip the guard
    ab = ("Patients received empagliflozin 10 mg daily or placebo. A primary event occurred in "
          "361 of 1863 (19.4%) vs 462 of 1867 (24.7%).")
    ex = _xt(ab, ["primary"], ["empagliflozin"], ["placebo"])
    assert not (ex.get("absent") and "multi-arm" in (ex.get("reason") or ""))


# --- incidence-rate extraction: explicit events+person-time only; refuse ambiguous rates ---
from harness.extract import extract_rate


def test_extract_rate_explicit_events_person_time():
    s = ("There were 84 events over 570 patient-years in the azithromycin group compared with "
         "129 events over 572 patient-years in the placebo group.")
    r = extract_rate(s, ["azithromycin"], ["placebo"])
    assert r == (84, 570.0, 129, 572.0), r


def test_extract_rate_refuses_rate_without_person_time():
    # Albert-style "1.48 per patient-year" without explicit events+PT must NOT be extracted
    s = ("The frequency of exacerbations was 1.48 per patient-year in the azithromycin group "
         "versus 1.83 per patient-year in the placebo group.")
    assert extract_rate(s, ["azithromycin"], ["placebo"]) is None


# --- continuous extraction: mean+/-SD per arm; refuse without per-arm n or two arms ---
from harness.extract import extract_continuous


def test_extract_continuous_mean_sd():
    s = "Mean cold duration was 4.0 days (SD 1.5) in the zinc group versus 6.0 days (SD 2.0) in the placebo group."
    assert extract_continuous(s, ["zinc"], ["placebo"], {"i": 50, "c": 52}) == (4.0, 1.5, 50, 6.0, 2.0, 52)


def test_extract_continuous_refuses_without_n_or_two_arms():
    s = "Mean cold duration was 4.0 days (SD 1.5) in the zinc group versus 6.0 days (SD 2.0) in the placebo group."
    assert extract_continuous(s, ["zinc"], ["placebo"], None) is None  # no per-arm n
    one = "Mean cold duration was 4.0 days (SD 1.5) in the zinc group."
    assert extract_continuous(one, ["zinc"], ["placebo"], {"i": 50, "c": 52}) is None  # one arm


# --- subgroup guard: refuse subgroup/per-protocol/post-hoc effects; keep the main ITT result ---
def test_subgroup_guard_refuses_subgroup_effect():
    s = ("Hazard ratio for exacerbations was lowest in the HP+/AZ subgroup at 0.61 "
         "(95% CI 0.45 to 0.83).")
    ex = _xt(s, ["exacerbation"], ["azithromycin"], ["placebo"])
    assert ex.get("absent")


def test_subgroup_guard_keeps_main_itt():
    # a main-analysis sentence (no subgroup marker) with a real disease keyword still extracts
    s = ("Recurrent pericarditis occurred in 26 of 120 vs 51 of 120 (relative risk 0.44, "
         "95% CI 0.27 to 0.73).")
    ex = _xt(s, ["recurrent pericarditis", "pericarditis"], ["colchicine"], ["placebo"])
    assert ex.get("ai") == 26 or ex.get("effect") == 0.44, ex


# --- percentage followed by an in-paren CI must still corroborate (NEJM: "N of M (P%; 95% CI ...)") ---
from harness.extract import extract_arm_counts as _eac


def test_percent_with_inparen_ci_still_corroborates():
    s = ("By day 28, death had occurred in 25 of 400 patients (6.2%; 95% CI, 3.9 to 8.6) in the "
         "hydrocortisone group and in 47 of 395 patients (11.9%; 95% CI, 8.7 to 15.1) in the placebo group.")
    arms = _eac(s, ["hydrocortisone"], ["placebo"])
    assert arms == (25, 400, 47, 395), arms
