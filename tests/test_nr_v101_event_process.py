"""EVENT PROCESS is part of endpoint identity (lane NR, V1.0.1; empagliflozin-HFpEF review, hash 56710eb5...).

EMPEROR-Preserved (PMID 34449189, NCT03057951) reports four distinct results; the stored candidate attached the TOTAL
(first and recurrent) HHF ratio, 407 vs 541 EVENTS, HR 0.73, to the primary time-to-first composite as FIRST_EVENT_RATIO.
Identity now carries {FIRST_EVENT, TOTAL_EVENTS} x {PATIENTS_WITH_EVENT, EVENT_COUNT}: a total-event result fails both a
first-event and a composite target (EVENT_PROCESS_MISMATCH, refused); the 0.79 composite passes. A span that states
neither leaves the dimension undecided -- never a refusal by default."""
from __future__ import annotations

import pytest

from harness import absence, target_endpoint as te

COMPOSITE = {"name": "Composite of cardiovascular death or hospitalization for heart failure", "estimand": "HR",
             "components": ["cardiovascular death", "heart failure hospitalization"]}
FIRST_HHF = {"name": "First hospitalization for heart failure", "estimand": "HR"}

PRIMARY = ("A primary outcome event occurred in 415 of 2997 patients (13.8%) in the empagliflozin group and in 511 of 2991 "
           "patients (17.1%) in the placebo group (hazard ratio, 0.79; 95.03% confidence interval, 0.69 to 0.90); the "
           "primary outcome was a composite of cardiovascular death or hospitalization for heart failure.")
TOTAL = ("The total number of hospitalizations for heart failure was lower in the empagliflozin group than in the placebo "
         "group (407 with empagliflozin and 541 with placebo; hazard ratio, 0.73; 95% CI, 0.61 to 0.88; P<0.001).")
RECURRENT = ("First and recurrent hospitalizations for heart failure: 407 events with empagliflozin vs 541 events with "
             "placebo (hazard ratio, 0.73; 95.03% CI, 0.61 to 0.88).")
REGISTRY = ("ClinicalTrials.gov outcome measure: Occurrence of adjudicated HHF (first and recurrent) -- analysis: Hazard "
            "Ratio (HR) 0.73 (95.03% CI 0.61 to 0.88; Joint frailty model)")


@pytest.mark.parametrize("span", [TOTAL, RECURRENT, REGISTRY])
def test_a_total_event_result_fails_a_composite_target(span):
    assert te._classify(COMPOSITE, span)["target_endpoint_class"] == te.EVENT_PROCESS_MISMATCH


@pytest.mark.parametrize("span", [TOTAL, RECURRENT, REGISTRY])
def test_a_total_event_result_fails_a_first_event_target(span):
    assert te._classify(FIRST_HHF, span)["target_endpoint_class"] == te.EVENT_PROCESS_MISMATCH


def test_the_primary_composite_passes():
    assert te._classify(COMPOSITE, PRIMARY)["target_endpoint_class"] == te.EXACT_TARGET


def test_the_refusal_is_a_verdict_with_its_own_code():
    v = te._class_verdict(COMPOSITE, te.EVENT_PROCESS_MISMATCH, [], [], COMPOSITE["name"])
    assert v["admissible"] is False and v["verdict"] == te.EVENT_PROCESS_MISMATCH


def test_the_stored_total_event_candidate_is_not_a_first_event_ratio():
    # the absence layer labelled 0.73 FIRST_EVENT_RATIO from its HR label; the span says total events
    assert absence._effect_class("HR", TOTAL) == "RATE"
    assert absence._effect_class("HR", PRIMARY) == "FIRST_EVENT_RATIO"


@pytest.mark.parametrize("text,process,unit", [
    (PRIMARY, None, te.PATIENTS_WITH_EVENT),
    (TOTAL, te.TOTAL_EVENTS, te.EVENT_COUNT),
    ("Time to first hospitalization for heart failure: 259 patients vs 352 patients.", te.FIRST_EVENT,
     te.PATIENTS_WITH_EVENT),
    # controls: a disease named 'recurrent' is not a total-event count; all-cause is not 'all events'
    ("Symptomatic recurrent VTE occurred in 30 of 1279 patients.", None, te.PATIENTS_WITH_EVENT),
    ("All-cause hospitalization occurred in 120 patients.", None, te.PATIENTS_WITH_EVENT),
    ("Mortality was lower with the drug (hazard ratio, 0.80).", None, None),
])
def test_event_process_reading(text, process, unit):
    ep = te.event_process(text)
    assert (ep["process"], ep["count_unit"]) == (process, unit), ep


def test_a_total_event_target_accepts_total_events_and_refuses_first_event_patients():
    spec = {"name": "Total (first and recurrent) hospitalizations for heart failure", "estimand": "RATE_RATIO"}
    assert te.target_event_process(spec) == {"process": te.TOTAL_EVENTS, "count_unit": te.EVENT_COUNT}
    assert te.event_process_problem(spec, RECURRENT) is None
    assert te.event_process_problem(spec, "Time to first hospitalization for heart failure: 259 patients vs 352 "
                                          "patients.") is not None


def test_a_registry_analysis_carries_its_stated_level_as_a_typed_field():
    om = {"analyses": [{"paramType": "Hazard Ratio (HR)", "paramValue": "0.79", "ciPctValue": "95.03",
                        "ciLowerLimit": "0.69", "ciUpperLimit": "0.9", "statisticalMethod": "Regression, Cox"}]}
    a = te._effect_analysis(om)
    assert a["ci_pct"] == 95.03 and "95.03% CI" in a["analysis_span"]


# ---- the stated interval level travels with the analysis (NR-C11, Codex patch verified by the lane) -------------------
import math  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

from harness.synth import Study, pool  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_bundle  # noqa: E402
import verify_bundle  # noqa: E402

CLAUSE = "hazard ratio, 0.79; 95.03% CI, 0.69 to 0.90"


def _se(pct):
    z = verify_bundle.inverse_normal(1 - (1 - pct / 100) / 2)
    return (math.log(0.90) - math.log(0.69)) / (2 * z)


def test_the_se_is_derived_at_the_stated_level():
    se = math.sqrt(Study("EMPEROR-Preserved", effect=0.79, ci_low=0.69, ci_high=0.90, ci_pct=95.03).yi_vi()[1])
    assert math.isclose(se, _se(95.03), rel_tol=1e-9) and not math.isclose(se, _se(95.0), rel_tol=1e-6)


@pytest.mark.parametrize("mod", [verify_bundle, build_bundle])
def test_a_95_03_interval_with_its_own_se_matches_and_a_95_derived_se_does_not(mod):
    assert mod.ci_level_record(CLAUSE, _se(95.03), 0.69, 0.90, 95.03)["level_agreement"] == "MATCH"
    assert mod.ci_level_record(CLAUSE, _se(95.0), 0.69, 0.90, 95.03)["level_agreement"] == "MISMATCH"
    assert mod.ci_level_record(CLAUSE, _se(95.0), 0.69, 0.90)["level_agreement"] == "MISMATCH"   # P12 still refuses


def test_no_level_leaves_pooling_unchanged():
    a = [Study("a", effect=.79, ci_low=.69, ci_high=.90), Study("b", effect=.9, ci_low=.8, ci_high=1.01)]
    b = [Study("a", effect=.79, ci_low=.69, ci_high=.90, ci_pct=95.0), Study("b", effect=.9, ci_low=.8, ci_high=1.01)]
    ra, rb = pool(a, scale="HR"), pool(b, scale="HR")
    assert (ra.estimate, ra.ci_low, ra.ci_high, ra.tau2) == (rb.estimate, rb.ci_low, rb.ci_high, rb.tau2)


# ---- NR-C12 (Codex adversarial round on the event-process rule; all fixed by the lane) --------------------------------
FIRST = {"name": "First hospitalization for heart failure", "estimand": "HR"}
TOTAL_T = {"name": "Total hospitalizations for heart failure", "estimand": "RATE_RATIO"}


@pytest.mark.parametrize("spec,text,expected", [
    # a first-event analysis reported as 'N events' is not an event count (#1)
    (FIRST, "Time to first hospitalization for heart failure: 259 events in the treatment group and 352 events in the "
            "placebo group; HR 0.71.", te.EXACT_TARGET),
    # patients with at least one event are not total events (#2)
    (TOTAL_T, "Hospitalization for heart failure: number of patients with at least one event, 259 versus 352; HR 0.71.",
     te.EVENT_PROCESS_MISMATCH),
    # a denominator is not a count of patients with the event (#3)
    (TOTAL_T, "Total hospitalizations for heart failure were assessed in 5988 patients; rate ratio 0.73.", te.EXACT_TARGET),
    # 'all events were adjudicated' / 'all patients with events' are not total-event statements (#5, #12)
    (FIRST, "Hospitalization for heart failure: patients with at least one event, 259 versus 352; all events were "
            "adjudicated; HR 0.71.", te.EXACT_TARGET),
    (FIRST, "Hospitalization for heart failure occurred in 259 patients; all patients with events were included in the "
            "analysis; HR 0.71.", te.EXACT_TARGET),
    # recurrences included / a recurrent-event model -> total events (#6, #8, #11)
    (FIRST, "Hospitalization for heart failure: No. of events (including recurrences), 407 versus 541; HR 0.73.",
     te.EVENT_PROCESS_MISMATCH),
    (FIRST, "Hospitalization for heart failure was analysed using a recurrent-event model; HR 0.73.",
     te.EVENT_PROCESS_MISMATCH),
    (FIRST, "Hospitalization for heart failure, including all recurrences: 407 versus 541; HR 0.73.",
     te.EVENT_PROCESS_MISMATCH),
    # negated recurrence is a first-event statement (#7)
    (FIRST, "Hospitalization for heart failure occurred in 259 patients; recurrent events were not included; HR 0.71.",
     te.EXACT_TARGET),
    # a recurrent DISEASE is a first recurrence, not a total-event count (#9, #10)
    ({"name": "Recurrent stroke", "estimand": "HR"}, "Recurrent stroke events occurred in 30 patients versus 45 patients; "
                                                     "HR 0.67.", te.EXACT_TARGET),
    ({"name": "Recurrence of atrial fibrillation", "estimand": "HR", "keywords": ["atrial fibrillation"]},
     "Recurrent atrial fibrillation episodes occurred in 30 patients versus 45 patients; HR 0.67.", te.EXACT_TARGET),
    # an annualised exacerbation rate against a rate target (#4)
    ({"name": "Annualised rate of COPD exacerbations", "estimand": "RATE_RATIO", "keywords": ["exacerbations"]},
     "The annualised rate of COPD exacerbations in 1000 patients was 0.8 versus 1.2; rate ratio 0.67.", te.EXACT_TARGET),
    # an optional component that was not assessed does not break the composite (#13)
    ({"name": "Composite of cardiovascular death or heart failure hospitalization or urgent heart failure visit",
      "estimand": "HR", "components": ["cardiovascular death", "heart failure hospitalization"],
      "optional_components": ["urgent heart failure visit"]},
     "The composite comprised cardiovascular death or heart failure hospitalization; urgent heart failure visits were not "
     "assessed; HR 0.79.", te.EXACT_TARGET),
])
def test_c12_event_process_counterexamples(spec, text, expected):
    assert te._classify(spec, text)["target_endpoint_class"] == expected


def test_c12_14_15_the_absence_label_follows_the_event_process():
    assert absence._effect_class("HR", "Hospitalization for heart failure occurred in 259 patients; recurrent events were "
                                       "not included; HR 0.71.") == "FIRST_EVENT_RATIO"
    assert absence._effect_class("HR", "Hospitalization for heart failure was analysed using a recurrent-event model; "
                                       "HR 0.73.") == "RATE"


# ---- the level of a served effect+CI row is typed from the REGISTRY analysis reporting the same tuple (NR-C13) ---------
import json as _json  # noqa: E402

from harness.registry_ci import registry_ci_level  # noqa: E402

_ROOT = Path(__file__).resolve().parents[1]
_RECS = _json.loads((_ROOT / "cache/empagliflozin-hfpef-hosp/records.json").read_text(encoding="utf-8"))
_EMPEROR = next(r for r in _RECS["records"] if str(r.get("id")) == "34449189")
_CT = _RECS.get("ctgov_results")


def test_the_registry_analysis_types_the_level_of_the_served_tuple():
    lv = registry_ci_level(_EMPEROR, "HR", 0.79, 0.69, 0.90, _CT)
    assert lv["ci_pct"] == 95.03 and lv["basis"]["nct_id"] == "NCT03057951"
    assert "95.03% CI 0.69 to 0.90" in lv["basis"]["span"] and "Cox" in lv["basis"]["span"]
    assert registry_ci_level(_EMPEROR, "HR", 0.73, 0.61, 0.88, _CT)["ci_pct"] == 95.03      # the joint-frailty analysis
    for args in (("HR", 0.80, 0.69, 0.90), ("HR", 0.7901, 0.69, 0.90), ("RR", 0.79, 0.69, 0.90)):
        assert registry_ci_level(_EMPEROR, *args, _CT) is None                              # never a near match


@pytest.mark.parametrize("mod", [verify_bundle, build_bundle])
def test_p12_rederives_the_registry_level_and_refuses_what_it_cannot(mod):
    lv = registry_ci_level(_EMPEROR, "HR", 0.79, 0.69, 0.90, _CT)
    kw = dict(ci_pct_basis=lv["basis"], record=_EMPEROR, ctgov_results=_CT, scale="HR", effect=0.79)
    clause = "hazard ratio, 0.79; 95% confidence interval [CI], 0.69 to 0.90"
    ok = mod.ci_level_record(clause, _se(95.03), 0.69, 0.90, 95.03, **kw)
    assert ok["level_agreement"] == "MATCH" and ok["basis"] == "STATED_IN_REGISTRY_ANALYSIS"
    assert ok["clause_ci_pct"] == 95.0 and ok["clause_level_rounded"] is True
    assert mod.ci_level_record(clause, _se(95.0), 0.69, 0.90, 95.03, **kw)["level_agreement"] == "MISMATCH"
    forged = dict(kw, ci_pct_basis=dict(lv["basis"], nct_id="NCT00000000"))
    assert mod.ci_level_record(clause, _se(95.03), 0.69, 0.90, 95.03, **forged)["level_agreement"] == "MISMATCH"
    assert mod.ci_level_record(clause, _se(95.03), 0.69, 0.90, 95.03,
                               **dict(kw, ctgov_results={}))["level_agreement"] == "MISMATCH"   # fail closed


# ---- rebuild diff (lane NR): the estimate's own analysis method outranks a descriptive event count --------------------
PARALLEL_HF = ("ClinicalTrials.gov outcome measure #1: Exposure-adjusted Incident Rate (EAIR) of CEC Confirmed Composite "
               "Endpoints Composite endpoint is defined as either cardiovascular (CV) death or heart failure (HF) "
               "hospitalization. EAIR = n/T where n = Total number of events included in the analysis. -- analysis: For "
               "Primary Composite: Hazard Ratio (HR) 1.0881 (95% CI 0.6501 to 1.8212; Regression, Cox)")


def test_a_cox_hazard_ratio_is_a_first_event_result_whatever_the_measure_describes():
    assert te.event_process(PARALLEL_HF)["process"] != te.TOTAL_EVENTS
    spec = {"name": "Composite cardiovascular death or heart-failure hospitalization", "estimand": "HR",
            "components": ["cardiovascular death", "heart failure hospitalization"]}
    assert te._classify(spec, PARALLEL_HF)["target_endpoint_class"] != te.EVENT_PROCESS_MISMATCH


def test_a_recurrent_event_method_still_makes_it_total():
    assert te.event_process(REGISTRY)["process"] == te.TOTAL_EVENTS                      # joint frailty
    assert te.event_process("Total HHF were analysed by negative binomial regression (Cox regression was used for "
                            "time to death): rate ratio 0.73.")["process"] == te.TOTAL_EVENTS


def test_the_classifier_reads_the_process_from_the_definition_and_its_own_result_span():
    # PARALLEL-HF as served: the registry description says 'n = Total number of events' (definition span); the Cox HR
    # is in the result span. Read apart, the definition refused the row; read together, the Cox method decides.
    definition = ("Exposure-adjusted Incident Rate (EAIR) of CEC Confirmed Composite Endpoints Composite endpoint is defined "
                  "as either cardiovascular (CV) death or heart failure (HF) hospitalization. EAIR = n/T where n = Total "
                  "number of events included in the analysis.")
    result = "For Primary Composite: Hazard Ratio (HR) 1.0881 (95% CI 0.6501 to 1.8212; Regression, Cox)"
    spec = {"name": "Composite cardiovascular death or heart-failure hospitalization", "estimand": "HR",
            "components": ["cardiovascular death", "heart failure hospitalization"]}
    assert te._classify(spec, definition)["target_endpoint_class"] == te.EVENT_PROCESS_MISMATCH   # the served defect
    assert te._classify(spec, definition, result_span=result)["target_endpoint_class"] != te.EVENT_PROCESS_MISMATCH
    rec = te.registry_outcome_match(spec, {}, definition, result_span=result)
    assert rec["target_endpoint_class"] != te.EVENT_PROCESS_MISMATCH


# ---- SGLT2-HFrEF review: DAPA-HF's first-event and total-event results share the SAME estimate (0.75) -------------------
# Component match is not enough: the recurrent-event result (567 vs 742 EVENTS, rate ratio 0.75 (0.65-0.88), LWYY /
# semiparametric proportional-rates model) was labelled EXACT_TARGET beside the first-event HR 0.75 (0.65-0.85) on the
# live page. The event process must match too, and it must not rest on the word 'recurrent' alone.
SGLT2 = _json.loads((Path(__file__).resolve().parents[1] / "topics/sglt2-hfref-hosp-cvdeath.json").read_text(
    encoding="utf-8"))["primary_outcome"]
DAPA_FIRST = ("Subjects Included in the Composite Endpoint of CV Death or Hospitalization Due to Heart Failure.",
              "Hazard Ratio (HR) 0.75 (95% CI 0.65 to 0.85; Regression, Cox)")


def _reg(measure, analysis):
    return te.registry_outcome_match(SGLT2, {}, measure, result_span=analysis)["target_endpoint_class"]


def test_dapa_hf_first_event_result_is_the_target():
    assert _reg(*DAPA_FIRST) == te.EXACT_TARGET


@pytest.mark.parametrize("measure,analysis", [
    # as held in the registry
    ("Events Included in the Composite Endpoint of Recurrent Hospitalizations Due to Heart Failure and CV Death.",
     "Rate Ratio (RR) 0.75 (95% CI 0.65 to 0.88; LWYY proportional rates model)"),
    # the same result without the word 'recurrent': the registry's event-count label and the rate model decide
    ("Events Included in the Composite Endpoint of Hospitalizations Due to Heart Failure and CV Death.",
     "Rate Ratio (RR) 0.75 (95% CI 0.65 to 0.88; LWYY proportional rates model)"),
    ("Composite Endpoint of Hospitalizations Due to Heart Failure and CV Death.",
     "Rate Ratio (RR) 0.75 (95% CI 0.65 to 0.88; semiparametric proportional-rates model)"),
])
def test_dapa_hf_total_event_result_with_the_identical_estimate_is_refused(measure, analysis):
    assert _reg(measure, analysis) == te.EVENT_PROCESS_MISMATCH


def test_dapa_hf_total_event_prose_is_refused():
    prose = ("The total number of hospitalizations for heart failure and cardiovascular deaths was lower with dapagliflozin "
             "(567 vs 742 events; rate ratio, 0.75; 95% CI, 0.65 to 0.88) in a semiparametric proportional-rates model.")
    assert te._classify(SGLT2, prose)["target_endpoint_class"] == te.EVENT_PROCESS_MISMATCH


def test_a_first_occurrence_rate_ratio_is_not_a_total_event_result():
    # ASCEND-style registry rows call a first-occurrence comparison a 'Rate Ratio' (log rank): the parameter name alone
    # never decides the event process
    assert te.event_process("Number of Participants With First Occurrence of Any Serious Vascular Event "
                            "Rate Ratio 0.88 (95% CI 0.79 to 0.97; Log Rank)")["process"] != te.TOTAL_EVENTS
