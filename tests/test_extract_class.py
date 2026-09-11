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
