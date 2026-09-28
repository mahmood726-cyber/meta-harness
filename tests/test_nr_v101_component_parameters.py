"""Thresholds are TYPED PARAMETERS of an endpoint component, never string suffixes (lane NR, V1.0.1; finerenone review,
hash 00a2b7e4...).

The canonical check said HETEROGENEOUS for FIDELIO vs FIGARO (SUSTAINED_40_EGFR_DECLINE vs SUSTAINED_EGFR_DECLINE), yet
both define the component as a sustained decrease of at least 40% in the eGFR: one reader kept '40%' in the component
string, the other dropped it, and the check compared strings. Now: eGFR_decline{threshold_pct: 40|57, sustained: true};
a qualifier lost from one string is read from that trial's own definition sentence; a parameter one side does not state is
disclosed as unresolved, never a difference; 40 vs 57 is a real difference and still fires."""
from __future__ import annotations

import copy

import pytest

from harness import compat_direction, component_identity as ci, endpoint_canonical as ec

FIDELIO = {"label": "33264825", "id": "PMID 33264825",
           "components": ["kidney failure", "sustained >=40% eGFR decline", "renal death"],
           "endpoint_definition_span": "The primary composite outcome, assessed in a time-to-event analysis, was kidney "
                                       "failure, a sustained decrease of at least 40% in the eGFR from baseline, or death "
                                       "from renal causes."}
FIGARO = {"label": "34449181", "id": "PMID 34449181",
          "components": ["kidney failure", "renal death", "sustained egfr decline"],
          "endpoint_definition_span": "The first secondary outcome was a composite of kidney failure, a sustained decrease "
                                      "from baseline of at least 40% in the eGFR, or death from renal causes."}
OUTCOME = {"name": "Kidney composite outcome", "estimand": "HR", "result": {"k": 2, "estimate": 0.84},
           "trials": [FIDELIO, FIGARO]}


def _canon(o):
    return ec.endpoint_canonical(o, "finerenone-ckd-t2d-renal")


def test_a_lost_qualifier_is_not_a_heterogeneity():
    out = _canon(OUTCOME)
    assert out["status"] == "HOMOGENEOUS", out
    assert out["component_sets"][0]["component_parameters"]["EGFR_DECLINE"] == {"threshold_pct": 40, "threshold_op": "ge",
                                                                                "sustained": True}
    assert not any("40" in c for c in out["components"])                   # the threshold is never a name suffix


def test_a_real_40_vs_57_difference_fires():
    o = copy.deepcopy(OUTCOME)
    o["trials"][1]["components"] = ["kidney failure", "sustained >=57% eGFR decline", "renal death"]
    o["trials"][1]["endpoint_definition_span"] = ("The composite was kidney failure, a sustained decrease of at least 57% "
                                                  "in the eGFR, or death from renal causes.")
    assert _canon(o)["status"] == "HETEROGENEOUS"


def test_an_unstated_threshold_is_unresolved_not_different():
    o = copy.deepcopy(OUTCOME)
    o["trials"][1]["endpoint_definition_span"] = "The composite was kidney failure, eGFR decline or renal death."
    out = _canon(o)
    assert out["status"] == "HOMOGENEOUS"
    assert {u["parameter"] for u in out["unresolved_component_parameters"]} >= {"threshold_pct"}


def test_typed_identity_reads_phrases_and_registered_codes_alike():
    want = {"name": "EGFR_DECLINE", "params": {"threshold_pct": 40, "threshold_op": "ge", "sustained": True}}
    assert ci.identity("sustained >=40% eGFR decline") == want
    assert ci.identity("SUSTAINED_EGFR_DECLINE_GE_40_PERCENT") == want
    assert ci.identity("sustained egfr decline", FIGARO["endpoint_definition_span"]) == want
    assert ci.identity("sustained decline in eGFR of at least 57%")["params"]["threshold_pct"] == 57
    assert ci.identity("eGFR <15 ml/min") == {"name": "EGFR_BELOW", "params": {"threshold_ml_min": 15}}
    assert ci.compare([ci.identity("sustained >=40% eGFR decline")],
                      [ci.identity("sustained >=57% eGFR decline")])["same"] is False


def test_the_direction_audit_compares_typed_components_too():
    o = copy.deepcopy(OUTCOME)
    o["trials"][0]["components"] = ["KIDNEY_FAILURE", "SUSTAINED_EGFR_DECLINE_GE_40_PERCENT", "RENAL_DEATH"]
    und = compat_direction._underlying(o, {"slug": "plant-no-facts"}, "endpoint_definition")
    assert und["matched"] is True and und.get("typed_match") is True, und
    o["trials"][1]["endpoint_definition_span"] = "The composite was kidney failure, a sustained 57% eGFR decline or renal death."
    o["trials"][1]["components"] = ["kidney failure", "sustained >=57% eGFR decline", "renal death"]
    assert compat_direction._underlying(o, {"slug": "plant-no-facts"}, "endpoint_definition")["matched"] is False


# ---- NR-C16 (Codex): a threshold is read only where it is ATTACHED to the eGFR decline; operator, sustained and its
#      duration, and a kidney-failure definition are parameters; the typed comparison decides both ways ----------------
C16_CANONICAL = [
 [
  2,
  {
   "name": "Kidney outcome",
   "result": {
    "k": 2
   },
   "trials": [
    {
     "label": "A",
     "components": [
      "eGFR decline"
     ],
     "endpoint_definition_span": "The outcome was a 30% reduction in UACR or a sustained eGFR decline of at least 40%."
    },
    {
     "label": "B",
     "components": [
      "sustained 50% eGFR decline"
     ]
    }
   ]
  },
  "HETEROGENEOUS"
 ],
 [
  3,
  {
   "name": "Kidney outcome",
   "result": {
    "k": 2
   },
   "trials": [
    {
     "label": "A",
     "components": [
      "eGFR decline"
     ],
     "endpoint_definition_span": "In 40% of patients, a sustained eGFR decline of at least 50% occurred."
    },
    {
     "label": "B",
     "components": [
      "sustained 40% eGFR decline"
     ]
    }
   ]
  },
  "HETEROGENEOUS"
 ],
 [
  5,
  {
   "name": "Kidney outcome",
   "result": {
    "k": 2
   },
   "trials": [
    {
     "label": "A",
     "components": [
      "sustained eGFR decline"
     ],
     "endpoint_definition_span": "The endpoint was a sustained eGFR decline from the baseline value obtained at the randomization visit of at least 40%."
    },
    {
     "label": "B",
     "components": [
      "sustained 50% eGFR decline"
     ]
    }
   ]
  },
  "HETEROGENEOUS"
 ],
 [
  6,
  {
   "name": "Kidney outcome",
   "result": {
    "k": 2
   },
   "trials": [
    {
     "label": "A",
     "components": [
      "40% decline in eGFR sustained for at least 4 weeks"
     ]
    },
    {
     "label": "B",
     "components": [
      "40% decline in eGFR sustained for at least 12 weeks"
     ]
    }
   ]
  },
  "HETEROGENEOUS"
 ],
 [
  7,
  {
   "name": "Kidney outcome",
   "result": {
    "k": 2
   },
   "trials": [
    {
     "label": "A",
     "components": [
      "kidney failure defined as eGFR <15 ml/min/1.73 m2 or maintenance dialysis"
     ]
    },
    {
     "label": "B",
     "components": [
      "kidney failure defined as eGFR <15 ml/min/1.73 m2"
     ]
    }
   ]
  },
  "HETEROGENEOUS"
 ],
 [
  8,
  {
   "name": "Kidney outcome",
   "result": {
    "k": 2
   },
   "trials": [
    {
     "label": "A",
     "components": [
      "sustained 40% decline in eGFR"
     ]
    },
    {
     "label": "B",
     "components": [
      "40% decline in eGFR, not sustained"
     ]
    }
   ]
  },
  "HETEROGENEOUS"
 ],
 [
  9,
  {
   "name": "Kidney outcome",
   "result": {
    "k": 2
   },
   "trials": [
    {
     "label": "A",
     "components": [
      "sustained eGFR decline of at least 40%"
     ]
    },
    {
     "label": "B",
     "components": [
      "sustained eGFR decline of at least 50 per cent"
     ]
    }
   ]
  },
  "HETEROGENEOUS"
 ],
 [
  10,
  {
   "name": "Kidney outcome",
   "result": {
    "k": 2
   },
   "trials": [
    {
     "label": "A",
     "components": [
      "sustained eGFR decline of at least 40%"
     ]
    },
    {
     "label": "B",
     "components": [
      "sustained eGFR decline of at least fifty percent"
     ]
    }
   ]
  },
  "HETEROGENEOUS"
 ],
 [
  11,
  {
   "name": "Kidney outcome",
   "result": {
    "k": 2
   },
   "trials": [
    {
     "label": "A",
     "components": [
      "eGFR decline"
     ],
     "endpoint_definition_span": "The outcome was a 30% reduction in UACR or a sustained eGFR decline of at least forty percent."
    },
    {
     "label": "B",
     "components": [
      "sustained 40% eGFR decline"
     ]
    }
   ]
  },
  "HOMOGENEOUS"
 ],
 [
  12,
  {
   "name": "Kidney outcome",
   "result": {
    "k": 2
   },
   "trials": [
    {
     "label": "A",
     "components": [
      "eGFR decline"
     ],
     "endpoint_definition_span": "In 40% of patients, a sustained eGFR decline of at least fifty percent occurred."
    },
    {
     "label": "B",
     "components": [
      "sustained 50% eGFR decline"
     ]
    }
   ]
  },
  "HOMOGENEOUS"
 ],
 [
  13,
  {
   "name": "Kidney outcome",
   "result": {
    "k": 2
   },
   "trials": [
    {
     "label": "A",
     "components": [
      "sustained eGFR decline >40%"
     ]
    },
    {
     "label": "B",
     "components": [
      "sustained eGFR decline >=40%"
     ]
    }
   ]
  },
  "HETEROGENEOUS"
 ]
]
C16_DIRECTION = [
 [
  1,
  {
   "name": "Kidney outcome",
   "trials": [
    {
     "label": "A",
     "components": [
      "sustained eGFR decline"
     ],
     "endpoint_definition_span": "The endpoint was a sustained decline in eGFR of at least 40%."
    },
    {
     "label": "B",
     "components": [
      "sustained eGFR decline"
     ],
     "endpoint_definition_span": "The endpoint was a sustained decline in eGFR of at least 50%."
    }
   ]
  },
  False
 ],
 [
  4,
  {
   "name": "Kidney outcome",
   "trials": [
    {
     "label": "A",
     "components": [
      "eGFR <15 ml/min/1.73 m2"
     ]
    },
    {
     "label": "B",
     "components": [
      "eGFR below 15 ml/min/1.73 m2"
     ]
    }
   ]
  },
  True
 ]
]


@pytest.mark.parametrize("case,o,expected", C16_CANONICAL)
def test_c16_canonical_status(case, o, expected):
    assert ec.endpoint_canonical(o, "plant")["status"] == expected, case


@pytest.mark.parametrize("case,outcome,expected", C16_DIRECTION)
def test_c16_direction_audit(case, outcome, expected):
    assert compat_direction._underlying(outcome, {"slug": "plant-no-facts"}, "endpoint_definition")["matched"] is expected, case
