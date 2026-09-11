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
