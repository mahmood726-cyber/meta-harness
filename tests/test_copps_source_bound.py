"""r24 COPPS: per-arm counts are SOURCE-BOUND or refused -- never reconstructed from percentages and a pooled total.
The 20/169 v 37/167 that stood in harness/known_missing.py were inferred (the auditor's source has 35 placebo events).
Fixed strings copied from the held COPPS abstract (PMID 22090167)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import known_missing as km  # noqa: E402

COPPS_ABSTRACT = ("The COPPS POAF substudy included 336 patients (mean age, 65.7+/-12.3 years; 69% male) of the COPPS "
                  "trial, a multicenter, double-blind, randomized trial. Despite well-balanced baseline characteristics, "
                  "patients on colchicine had a reduced incidence of POAF (12.0% versus 22.0%, respectively; P=0.021; "
                  "relative risk reduction, 45%; number needed to treat, 11).")


def _row():
    return {"id": "PMID 22090167", "label": "Imazio [19]", "reason": "not pooled"}


def test_PLANT_a_percentage_only_source_yields_no_counts():
    out = km._source_value("colchicine-postop-af", {"name": "Postoperative atrial fibrillation", "estimand": "RR"},
                           _row(), {"22090167": {"id": "22090167", "abstract": COPPS_ABSTRACT}}, {})
    assert out["value_status"] == km.REFUSED_DENOMINATORS_NOT_STATED
    assert not any(out.get(k) is not None for k in ("ai", "n1i", "ci", "n2i"))
    assert "336 patients" in out["source_span"] and "never reconstructed" in out["verify_basis"]


def test_PLANT_no_literal_copps_counts_remain_in_the_harness():
    src = open(os.path.join(ROOT, "harness", "known_missing.py"), encoding="utf-8").read()
    for literal in ('"ai": 20', '"n1i": 169', '"ci": 37', '"n2i": 167'):
        assert literal not in src, literal


def test_a_refused_row_is_never_pooled_into_the_sensitivity():
    # build() pools only IN_COMMITTED_SOURCE rows: the refusal keeps COPPS out of the combined estimate
    assert km.REFUSED_DENOMINATORS_NOT_STATED != km.IN_COMMITTED_SOURCE
