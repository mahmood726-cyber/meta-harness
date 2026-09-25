"""Specifications for the 23 compiled patterns in harness/extract.py.

Each spec says, in plain words, what the pattern is FOR -- the thing a human labeller (or a recorded model call, as a
PROPOSAL) marks in a sentence without ever seeing the regex. `kind`:
  extractor   the pattern captures values; `fields` names each capture group in order. A label is the set of
              instances the sentence STATES, each field quoted verbatim from the sentence.
  classifier  the pattern decides whether a sentence has a property; a label is yes/no plus the quoted words.
`trigger` is a deliberately BROAD regex used only to sample candidate sentences, so that sentences the pattern MISSES
(false negatives) can be found: a candidate is any sentence where the pattern fires OR the trigger fires.
`plants` are hand-written inputs with known answers (R3): `accept` must produce `groups`; `refuse` must not match.
"""
from __future__ import annotations

SPECS = {
    "_ARM": {"kind": "extractor", "fields": ["count", "percent", "denominator"],
             "spec": "an event count for one group written as COUNT (PERCENT%) of DENOMINATOR (or COUNT (PERCENT%)/DENOMINATOR)",
             "trigger": r"\d\s*%", "plants": {"accept": [("12 (6.0%) of 200", ("12", "6.0", "200"))],
                                               "refuse": ["12 (6.0%) patients", "HR 0.80 (95% CI 0.70-0.90)"]}},
    "_ARM2": {"kind": "extractor", "fields": ["count", "denominator", "percent"],
              "spec": "an event count for one group written as COUNT/DENOMINATOR (PERCENT%)",
              "trigger": r"\d\s*/\s*\d", "plants": {"accept": [("25/400 (6.2%)", ("25", "400", "6.2"))],
                                                    "refuse": ["25/400 patients", "a ratio of 1/2 was used"]}},
    "_ARM3": {"kind": "extractor", "fields": ["count", "denominator", "percent"],
              "spec": "an event count for one group written as COUNT of DENOMINATOR [patients] (PERCENT%)",
              "trigger": r"\bof\s+\d", "plants": {"accept": [("25 of 400 patients (6.2%)", ("25", "400", "6.2"))],
                                                  "refuse": ["25 of 400 patients", "one of 400 sites"]}},
    "_ARMP": {"kind": "extractor", "fields": ["count", "percent"],
              "spec": "an event count for one group written as COUNT [patients] (PERCENT%) with the denominator elsewhere",
              "trigger": r"\d\s*%", "plants": {"accept": [("37 patients (18.5%)", ("37", "18.5"))],
                                               "refuse": ["18.5% of patients", "37 patients in total"]}},
    "_ARM4": {"kind": "extractor", "fields": ["percent", "count", "denominator"],
              "spec": "an event proportion for one group written as PERCENT% (COUNT/DENOMINATOR)",
              "trigger": r"%\s*[\(\[]", "plants": {"accept": [("9% (7/78)", ("9", "7", "78"))],
                                                   "refuse": ["9% of 78", "7/78 patients"]}},
    "_DENOM_EACH": {"kind": "extractor", "fields": ["per_arm_n"],
                    "spec": "the number of participants randomly assigned to EACH group (a per-arm sample size stated once for all arms)",
                    "trigger": r"\beach\b", "plants": {"accept": [("100 patients were randomly assigned to each", ("100",))],
                                                       "refuse": ["100 patients were randomly assigned to placebo"]}},
    "_NEQ": {"kind": "extractor", "fields": ["n"],
             "spec": "a sample size written as n = NUMBER",
             "trigger": r"\bn\b", "plants": {"accept": [("placebo (n = 150)", ("150",))],
                                             "refuse": ["n-3 fatty acids", "in 150 patients",
                                                        "P for interaction = 0.92",       # 'n' ends a word
                                                        "trials (n = 2,523 patients)"]}},  # R4: a fragment is refused
    "_EFFECT": {"kind": "extractor", "fields": ["measure", "point", "lower", "upper"],
                "spec": "a relative effect estimate with its confidence interval: the MEASURE name or abbreviation "
                        "(relative risk, risk ratio, rate ratio, odds ratio, hazard ratio, RR, OR, HR, relative risk "
                        "reduction), the POINT estimate, and the LOWER and UPPER interval bounds",
                "trigger": r"\bCI\b|confidence interval", "plants": {
                    "accept": [("hazard ratio, 0.80; 95% CI, 0.70 to 0.91", ("hazard ratio", "0.80", "0.70", "0.91"))],
                    "refuse": ["death or HF hospitalisation (95% CI 0.70-0.90)", "hazard ratio was similar"]}},
    "_K": {"kind": "extractor", "fields": ["k"],
           "spec": "the NUMBER of randomised (controlled) trials a review or analysis included, in digits or words",
           "trigger": r"trials?\b|RCTs?\b", "plants": {"accept": [("12 randomized controlled trials", ("12",))],
                                                       "refuse": ["a randomized controlled trial"]}},
    "_DOSE_ARM": {"kind": "extractor", "fields": ["dose_mg"],
                  "spec": "a drug DOSE in milligrams that defines a treatment group or regimen",
                  "trigger": r"\bmg\b", "plants": {"accept": [("0.5 mg daily", ("0.5",))], "refuse": ["5 mmol/L"]}},
    "_RATE_EVPT": {"kind": "extractor", "fields": ["events", "person_years"],
                   "spec": "an event COUNT together with the PERSON-TIME it accrued over (N events ... M patient-years)",
                   "trigger": r"(?:patient|person)[-\s]?years?", "plants": {
                       "accept": [("120 events during 1500 patient-years", ("120", "1500"))],
                       "refuse": ["120 events in 1500 patients"]}},
    "_RATE_UNIT": {"kind": "extractor", "fields": ["rate", "unit"],
                   "spec": "an event RATE with its time UNIT (% per year, per 100 patient-years, per patient per year)",
                   "trigger": r"\bper\b|%\s*/", "plants": {"accept": [("4.2 per 100 patient-years", ("4.2", "per 100 patient-years"))],
                                                           "refuse": ["4.2% of patients"]}},
    "_MEAN_SD": {"kind": "extractor", "fields": ["mean", "sd_paren", "sd_plusminus"],
                 "spec": "a MEAN with its STANDARD DEVIATION, written X (SD Y) or X ± Y",
                 "trigger": r"\bSD\b|standard deviation|±|\+/-", "plants": {
                     "accept": [("12.4 (SD 3.1)", ("12.4", "3.1", None)), ("12.4 ± 3.1", ("12.4", None, "3.1"))],
                     "refuse": ["12.4 (95% CI 10.1-14.7)"]}},
    "_MED_IQR": {"kind": "extractor", "fields": ["median", "q1", "q3"],
                 "spec": "a MEDIAN with its interquartile range (IQR lower to upper)",
                 "trigger": r"\bIQR\b|interquartile", "plants": {"accept": [("median 7 days (IQR 4-11)", ("7", "4", "11"))],
                                                                  "refuse": ["median 7 days (range 4-11)"]}},
    "_MORT_Y": {"kind": "classifier", "spec": "the sentence uses the word mortality (or mortalities)",
                "trigger": r"mortal", "plants": {"accept": ["all-cause mortality was lower"], "refuse": ["immortal time bias"]}},
    "_MORT_D": {"kind": "classifier", "spec": "the sentence uses the word death or deaths",
                "trigger": r"\bdea|\bdied|\bdie\b", "plants": {"accept": ["12 deaths occurred"], "refuse": ["patients who died"]}},
    "_RECURRENT_PERSONTIME": {"kind": "classifier",
                              "spec": "the outcome is counted as recurrent events or per unit person-time (rates, "
                                      "'N times', totals of events/hospitalisations) rather than once per patient",
                              "trigger": r"recurren|per\b|total|times\b", "plants": {
                                  "accept": ["total number of heart failure hospitalisations"],
                                  "refuse": ["first hospitalisation for heart failure"]}},
    "_ANCHOR_RX": {"kind": "classifier", "spec": "the sentence names THE primary (or co-primary) outcome / end point",
                   "trigger": r"primary|end[\s-]?point|outcome", "plants": {
                       "accept": ["The primary composite outcome was"], "refuse": ["a secondary outcome was"]}},
    "_DEF_CUE": {"kind": "classifier",
                 "spec": "the sentence DEFINES an outcome (what it was / consisted of / a composite of), rather than "
                         "reporting a result",
                 "trigger": r".", "plants": {"accept": ["a composite of death or stroke"], "refuse": ["reduced by 20"]}},
    "_FACTORIAL": {"kind": "classifier", "spec": "the trial has a factorial (e.g. 2x2) design",
                   "trigger": r"factor|\bx\b|×|by", "plants": {"accept": ["a 2 x 2 factorial trial"], "refuse": ["risk factors"]}},
    "_SUBGROUP": {"kind": "classifier",
                  "spec": "the result is from a subgroup, per-protocol, as-treated, post-hoc, sensitivity or "
                          "exploratory analysis rather than the main randomised comparison",
                  "trigger": r"protocol|hoc|subgroup|sensitivity|treated|among|restricted|exploratory|lowest|highest",
                  "plants": {"accept": ["in the per-protocol analysis"], "refuse": ["in the intention-to-treat analysis"]}},
    "_NULL_RESULT": {"kind": "classifier",
                     "spec": "the sentence states there was NO difference between groups (similar / comparable / did "
                             "not differ / no significant difference)",
                     "trigger": r"similar|compar|differ", "plants": {"accept": ["rates were similar between groups"],
                                                                       "refuse": ["rates were lower with colchicine"]}},
    "_COMPOSITE_ENDPOINT": {"kind": "classifier",
                            "spec": "the outcome named is a COMPOSITE of several events (e.g. MACE, 'death or "
                                    "hospitalisation for heart failure')",
                            "trigger": r"composite|MACE|\bor\b", "plants": {
                                "accept": ["death or hospitalization for heart failure"],
                                "refuse": ["all-cause death"]}},
}


# How harness/*.py READS each pattern (tests/test_regex_plants.py re-derives this from the source, so it cannot go stale).
#   standalone     its own match is used directly
#   conjunct:<P>   used only together with pattern P (its standalone precision is not its contract)
#   dead           no reader anywhere in harness/ -- its measurement cannot move a served number; removal is batched
#                  with the R1/R4 change to the pinned file
ROLES = {name: "standalone" for name in SPECS}
ROLES.update({"_DEF_CUE": "conjunct:_ANCHOR_RX", "_ANCHOR_RX": "conjunct:_DEF_CUE",
              "_DOSE_ARM": "dead", "_RATE_UNIT": "dead", "_MORT_Y": "dead", "_MORT_D": "dead"})


# Inline literal sites in harness/extract.py (keyed as regex_layer.inventory names them: file:method:sha256(text)[:10]).
# The test reads each pattern FROM THE SOURCE by AST, so a changed literal gets a new key and fails the ratchet until
# its plants are restated. kind: "search" (accept = must match, with groups when given) or "split" (accept = parts).
INLINE_SPECS = {
    "extract.py:split:328973b9f2": {
        "kind": "split", "what": "_sentences: split after a full stop before a capital or '('",
        "plants": {"accept": [("Mortality fell. The HR was 0.8.", ["Mortality fell.", "The HR was 0.8."]),
                              ("Death 10%. (95% CI 1-2)", ["Death 10%.", "(95% CI 1-2)"])],
                   "refuse": ["HR 0.80 (95% CI 0.70-0.90) was seen", "rate was 1.5 per 100"]}},
    "extract.py:search:159a89219d": {
        "kind": "search", "what": "_kw_only_in_null_result: a digit follows the keyword",
        "plants": {"accept": [(" 12 events", None)], "refuse": [" no events were seen"]}},
    "extract.py:search:159a89219d#2": {
        "kind": "search", "what": "_intervention_dose_specified: the intervention term carries a dose",
        "plants": {"accept": [("colchicine 0.5 mg", None)], "refuse": ["colchicine"]}},
    "extract.py:search:29ab5efb7e": {
        "kind": "search", "what": "composite_component_mismatch: an N-point composite named in the outcome",
        "plants": {"accept": [("3-point mace", ("3",)), ("4 point mace", ("4",))], "refuse": ["major adverse events"]}},
    "extract.py:search:11cffd49d3": {
        "kind": "search", "what": "timepoint_mismatch: the declared timepoint also allows a day/week/month window",
        "plants": {"accept": [("28-90 day or in-hospital", ("day",)), ("30 days", ("day",))],
                   "refuse": ["in-hospital", "index admission"]}},
    "extract.py:search:8747ec2bd9": {
        "kind": "search", "what": "timepoint_mismatch: the source measures the outcome over a follow-up window",
        "plants": {"accept": [("within 30 days after surgery", ("30", "days")),
                              ("during 12 months of follow-up", ("12", "months"))],
                   "refuse": ["during hospitalisation", "at 30 days, mortality was"]}},
    "extract.py:finditer:8af3725e7a": {
        "kind": "search", "what": "composite_heterogeneity: a clause that DEFINES a composite",
        "plants": {"accept": [("the composite of cardiovascular death", None),
                              ("primary outcome was cardiovascular death", None)],
                   "refuse": ["the primary outcome occurred in 10%", "components were analysed"]}},
    "extract.py:split:54f53f5663": {
        "kind": "split", "what": "composite_heterogeneity: end a definition at the first . ; or :",
        "plants": {"accept": [(" death, mi or stroke; secondary: bleeding", [" death, mi or stroke", " secondary", " bleeding"])],
                   "refuse": ["death, mi or stroke"]}},
    "extract.py:finditer:33f2389e47": {
        "kind": "search", "what": "_multi_dose_arms: a dose with an arm/group context",
        "plants": {"accept": [("the 150 mg group", ("150",)), ("300-mg arm", ("300",))],
                   "refuse": ["150 mg daily", "a 150 mg dose. The group"]}},
}


# Site plants for the other files the regex layer owns (regex_layer/OWNERSHIP.md), same format as INLINE_SPECS; a
# named compiled pattern is keyed "<file>:<name>" and read from the module, an inline literal by its inventory key.
from regex_layer.specs_target_endpoint import SITE_SPECS as _TARGET_ENDPOINT  # noqa: E402

INLINE_SPECS.update(_TARGET_ENDPOINT)

from regex_layer.specs_eligibility_compat import SITE_SPECS as _ELIGIBILITY_COMPAT  # noqa: E402

INLINE_SPECS.update(_ELIGIBILITY_COMPAT)

# Sites in files the OTHER lane owns (harness/rob2.py, funding.py, hand_binding.py): planted and measured here, read
# only -- they are not in sites_without_plants.json's owned_files, and a located defect's fix belongs to that lane.
from regex_layer.specs_other_lanes import SITE_SPECS as _OTHER_LANES  # noqa: E402

INLINE_SPECS.update(_OTHER_LANES)

# Second batch of other-lane sites (harness/gate.py, protocol_compiler.py, absence.py, registry_multi.py, pipeline.py):
# read only, same discipline as specs_other_lanes.
from regex_layer.specs_other_lanes_2 import SITE_SPECS as _OTHER_LANES_2  # noqa: E402

INLINE_SPECS.update(_OTHER_LANES_2)
