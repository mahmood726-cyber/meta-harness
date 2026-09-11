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
