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


def test_PLANT_codex_r11_1_the_refusal_follows_the_text_not_the_record_id():
    stated = ("200 patients were randomized: 100 to colchicine and 100 to placebo. Postoperative atrial fibrillation "
              "occurred in 10 colchicine patients and 20 placebo patients.")
    out = km._source_value("colchicine-postop-af", {"name": "Postoperative atrial fibrillation", "estimand": "RR"},
                           _row(), {"22090167": {"id": "22090167", "abstract": stated}}, {})
    assert out["value_status"] != km.REFUSED_DENOMINATORS_NOT_STATED
    assert out["missing_class"] != "SOURCE_ABSENT"
    # and the same percentage-only shape refuses under ANY record id
    other = km._source_value("colchicine-postop-af", {"name": "Postoperative atrial fibrillation", "estimand": "RR"},
                             {"id": "PMID 1", "label": "x", "reason": "not pooled"},
                             {"1": {"id": "1", "abstract": COPPS_ABSTRACT}}, {})
    assert other["value_status"] == km.REFUSED_DENOMINATORS_NOT_STATED


def test_PLANT_per_arm_counts_written_as_n_patients_pct_are_not_percent_only():
    # ICAP (23992557) held abstract shape: per-arm event counts ARE stated
    icap = ("The primary outcome occurred in 20 patients (16.7%) in the colchicine group and 45 patients (37.5%) in the "
            "placebo group. Colchicine reduced the rate of symptom persistence at 72 hours (19.2% vs. 40.0%, P=0.001).")
    assert not km._percent_only(icap)
    assert km._percent_only(COPPS_ABSTRACT)


def test_PLANT_codex_r12_1_unspaced_slash_counts_are_per_arm_numbers():
    assert not km._percent_only("Deaths were 20/100 versus 30/100 (20% versus 30%).")


def test_PLANT_codex_r12_2_an_unrelated_n_of_n_does_not_suppress_the_refusal():
    assert km._percent_only("Of 200 participants, 5 of 10 centres were rural. Deaths were 20% versus 30%; arm "
                            "denominators were not reported.")
    assert not km._percent_only("Deaths occurred in 20 of 100 patients versus 30 of 100 (20% versus 30%).")
