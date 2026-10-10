"""r23-03 / r17 / r13: a harms row carries ITS OWN definition and state, never the efficacy tuple's.

  - PLUS: the new-RRT row carried 'primary outcome was death from any cause within 90 days'.
  - SPLIT: AKI and RRT are REPORTED (RR 1.04, RR 0.96) but were labelled RETRIEVED_OUTCOME_NOT_REPORTED because the
    design refusal code (ENGINE_CANNOT_CONSUME) fell through to the not-reported default; its RRT span was the
    exclusion criterion.
Strings are copied from the held abstracts (cache/balanced-crystalloids-vs-saline-mortality/records.json)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import absence, compat_check, harms  # noqa: E402

PLUS = ("METHODS: In a double-blind, randomized, controlled trial, we assigned critically ill patients to receive BMES "
        "(Plasma-Lyte 148) or saline as fluid therapy in the intensive care unit (ICU) for 90 days. The primary outcome "
        "was death from any cause within 90 days after randomization. Secondary outcomes were receipt of new "
        "renal-replacement therapy and the maximum increase in the creatinine level during ICU stay. RESULTS: ... New "
        "renal-replacement therapy was initiated in 306 of 2403 patients (12.7%) in the BMES group and in 310 of 2394 "
        "patients (12.9%) in the saline group, for a difference of -0.20 percentage points (95% CI, -2.96 to 2.56).")
SPLIT = ("IMPORTANCE: Saline (0.9% sodium chloride) is the most commonly administered intravenous fluid; however, its "
         "use may be associated with acute kidney injury (AKI) and increased mortality. PARTICIPANTS: All patients "
         "admitted to the ICU requiring crystalloid fluid therapy were eligible for inclusion. Patients with "
         "established AKI requiring renal replacement therapy (RRT) were excluded. MAIN OUTCOMES AND MEASURES: The "
         "primary outcome was proportion of patients with AKI (defined as a rise in serum creatinine level of at least "
         "2-fold or a serum creatinine level of >=3.96 mg/dL with an increase of >=0.5 mg/dL); main secondary outcomes "
         "were incidence of RRT use and in-hospital mortality. RESULTS: In the buffered crystalloid group, 102 of 1067 "
         "patients (9.6%) developed AKI within 90 days after enrollment compared with 94 of 1025 patients (9.2%) in the "
         "saline group (absolute difference, 0.4% [95% CI, -2.1% to 2.9%]; relative risk [RR], 1.04 [95% CI, 0.80 to "
         "1.36]; P = .77). In the buffered crystalloid group, RRT was used in 38 of 1152 patients (3.3%) compared with "
         "38 of 1110 patients (3.4%) in the saline group (absolute difference, -0.1% [95% CI, -1.6% to 1.4%]; RR, 0.96 "
         "[95% CI, 0.62 to 1.50]; P = .91).")
AKI = {"name": "Acute kidney injury", "keywords": ["acute kidney injury", "AKI", "kidney injury"], "estimand": "RR"}
RRT = {"name": "New renal-replacement therapy", "estimand": "RR",
       "keywords": ["new renal-replacement therapy", "renal-replacement therapy", "renal replacement therapy", "RRT",
                    "kidney replacement therapy"]}
DESIGN_REFUSAL = ("ENGINE_CANNOT_CONSUME(design=cluster_crossover, missing=design_adjusted_effect|ICC): typed design "
                  "action REFUSE: SPLIT is cluster-crossover")


def _endpoint(outcome, pid, abstract):
    trial = {"id": f"PMID {pid}", "label": pid}
    return compat_check.derive_trial_dimensions({"slug": "x"}, outcome, trial,
                                                {"records": [{"id": pid, "title": "", "abstract": abstract}]},
                                                {})["endpoint_definition"]


def test_PLANT_a_harm_row_never_inherits_the_efficacy_primary_definition():
    got = _endpoint({"name": "New renal-replacement therapy", "kind": "harm"}, "35041780", PLUS)
    assert "death" not in (got["value"] or "").lower(), got
    assert got["value"] == "New renal-replacement therapy"
    assert "does not name this outcome" in got["source"]


def test_the_primary_outcome_still_gets_its_primary_definition():
    got = _endpoint({"name": "All-cause mortality", "primary": True}, "35041780", PLUS)
    assert "death from any cause within 90 days" in got["value"]


def test_a_secondary_outcome_named_by_the_definition_keeps_it():
    got = _endpoint({"name": "Acute kidney injury", "kind": "harm"}, "26444692", SPLIT)
    assert "proportion of patients with AKI" in got["value"]


def _state(spec, code, reason, abstract=SPLIT, pid="26444692"):
    row = {"id": f"PMID {pid}", "label": pid, "reason_code": code, "reason": reason}
    return harms._hm_state_for_absent(row, spec, {pid: {"id": pid, "abstract": abstract}}, {})


def test_PLANT_a_design_refusal_of_a_reported_harm_is_not_not_reported():
    for spec, needle in ((AKI, "102 of 1067"), (RRT, "38 of 1152")):
        got = _state(spec, absence.ENGINE_CANNOT_CONSUME, DESIGN_REFUSAL)
        assert got["harm_absence_state"] == harms.RETRIEVED_REFUSED_WITH_REASON, (spec["name"], got)
        assert got["harm_source_reported"] is True
        # PLANT: the span is the RESULT sentence, not the background sentence or the RRT exclusion criterion
        assert needle in got["harm_source_span"], got["harm_source_span"]
        assert got["harm_source_signal"] == "numeric_signal"


def test_PLANT_an_unrecognised_code_never_certifies_absence():
    got = _state(RRT, "SOME_NEW_CODE", "a reason")
    assert got["harm_absence_state"] != harms.RETRIEVED_OUTCOME_NOT_REPORTED


def test_a_genuine_not_in_source_row_is_still_not_reported():
    got = _state(RRT, absence.OUTCOME_NOT_IN_SOURCE, "not in the abstract",
                 abstract="RESULTS: Mortality was 10% versus 11% in the two groups.", pid="1")
    assert got["harm_absence_state"] == harms.RETRIEVED_OUTCOME_NOT_REPORTED
    assert got["harm_source_reported"] is False


def test_PLANT_the_word_or_is_not_an_odds_ratio():
    sent = ("The primary outcome was AKI (a rise in serum creatinine of at least 2-fold or a serum creatinine level of "
            ">=3.96 mg/dL with an increase of >=0.5 mg/dL).")
    assert harms._EFFECT_OR_COMPARISON.search(sent) is None
    assert harms._EFFECT_OR_COMPARISON.search("AKI occurred more often (OR 1.40, 95% CI 1.1 to 1.8).")


def test_PLANT_a_known_reported_row_stays_extraction_debt_not_a_refusal():
    # LoDoCo2 (32862667) GI events: the row's own code says reported-not-yet-extracted; it must stay unresolved debt
    # (harms_incomplete), never 'not reported' and never a resolved refusal (r13 'reported, extraction unresolved')
    got = _state(AKI, harms.KNOWN_REPORTED_NOT_YET_EXTRACTED, "reported; not yet extracted")
    assert got["harm_absence_state"] == harms.KNOWN_REPORTED_NOT_YET_EXTRACTED


def test_PLANT_codex_harms_r1_1_one_shared_word_is_not_outcome_identity():
    rrt = {"name": "new renal replacement therapy", "primary": False}
    assert not compat_check._names_outcome(
        "major cardiovascular events, defined as cardiovascular death, myocardial infarction, or renal failure", rrt)
    # the whole phrase, all significant words, a keyword phrase or the acronym still establish identity
    assert compat_check._names_outcome("receipt of new renal-replacement therapy", rrt)
    assert compat_check._names_outcome("proportion of patients with AKI (defined as ...)", AKI)
    assert compat_check._names_outcome("time to first hospitalization for heart failure",
                                       {"name": "Hospitalization for heart failure"})


def test_PLANT_codex_harms_r2_negation_and_prefixes_do_not_establish_identity():
    nf = {"name": "Non-fatal myocardial infarction"}
    assert not compat_check._names_outcome("major cardiovascular events, defined as fatal myocardial infarction", nf)
    assert not compat_check._names_outcome("defined as non-fatal myocardial infarction",
                                           {"name": "Fatal myocardial infarction"})
    assert compat_check._names_outcome("composite of nonfatal myocardial infarction or stroke", nf) or \
        compat_check._names_outcome("composite of non-fatal myocardial infarction or stroke", nf)
    assert not compat_check._names_outcome("The primary endpoint was burnout severity at six months", {"name": "Burn"})
    # plurals still match
    assert compat_check._names_outcome("hospitalizations for heart failure", {"name": "Hospitalization for heart failure"})
