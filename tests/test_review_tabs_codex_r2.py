"""Regressions for the new-tab defects codex round 2 (gpt-6-astra, recorded) found after round 1's fixes; each span-verified
and checked against the committed review before it was accepted. Round-2 findings in legacy tabs, in signed notice text,
and one false finding (recorded-read ids the job had not been given; they are in evidence/model_calls/) are not here."""
from __future__ import annotations

import json
from pathlib import Path

from harness import manuscript, review_tabs as T

ROOT = Path(__file__).resolve().parents[1]


def _r(slug):
    return json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


def test_no_notice_is_not_presented_as_no_change():
    c = T.changes_tab(_r("balanced-crystalloids-vs-saline-mortality"))
    assert "has not changed since first publication" not in c
    assert "not evidence that the result" in c


def test_claim_check_coverage_is_the_recorded_count():
    for slug in ("balanced-crystalloids-vs-saline-mortality", "iv-iron-hfref-hosp"):
        r = _r(slug)
        c = T.conclusions(r)
        assert f"<strong>{r['reproduction']['claim_check']['claims_checked']}</strong>" in c
        assert "No primary-result claim was checked" in c          # outcome_result 0 on both
    assert "No primary-result claim was checked" not in T.conclusions(_r("dpp4-mace-t2d"))


def test_counts_only_row_in_an_hr_pool_is_drawn_and_labelled():
    r = _r("balanced-crystalloids-vs-saline-mortality")
    prim = next(o for o in r["outcomes"] if o.get("primary"))
    svg = manuscript.forest_for(prim)
    assert "35041780 (RR FROM COUNTS)" in svg


def test_notice_ledger_states_the_outcomes_current_state():
    r = _r("omega3-cardiovascular-events")
    c = T.changes_tab(r)
    assert ">applied<" not in c
    af = next(o for o in r["outcomes"] if o["name"] == "Atrial fibrillation")
    assert T.outcome_state(af) in c and T.outcome_state(af).startswith("withheld")


def test_registry_id_is_read_from_the_family_id():
    for slug, nct in (("spironolactone-hfref-mortality", "NCT01115855"), ("ticagrelor-vs-clopidogrel-acs", "NCT01294462")):
        assert f"clinicaltrials.gov/study/{nct}" in T.included_tab(_r(slug))


def test_direction_is_defined_as_claim_py_defines_it():
    c = T.conclusions(_r("metformin-pcos-ovulation"))
    assert "does not reverse for an outcome where higher is better" in c
