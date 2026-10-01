"""V1.0.1 (external review of balanced-crystalloids, review hash db66dd50..., commit 6260e70c; Mahmood: "fix in reproducible harness
(regex and reproducible AI)"). The REFUSAL AUDITOR accepted wrong evidence:
  - SMART's mortality refusal was audited REASON_FALSE_VALUE_HELD on "426 ... and 343 patients ... received any volume of unassigned
    crystalloid" -- crossover/EXPOSURE counts, not deaths;
  - SMART's AKI and RRT (component) refusals were "disproved" with the MAKE30 COMPOSITE;
  - SPLIT's design refusals (cluster-crossover, missing design-adjusted effect) were "disproved" because a raw count exists.
The fix: every number the auditor cites is a TYPED identity (trial, comparison, outcome, component vs composite, timepoint,
population, effect measure, adjusted + model, role), and a refusal is marked false only on a match on ALL of them -- plus, for a
design refusal, a design-appropriate model. Harness-level only: nothing here names a trial in the code under test.
These plants call the real auditor on the real held sources, exactly as harness/pipeline.py does; they fired pre-fix."""
import json
from pathlib import Path

import pytest

from harness import reason_audit

ROOT = Path(__file__).resolve().parents[1]
SLUG = "balanced-crystalloids-vs-saline-mortality"
SMART, SPLIT = "29485925", "26444692"


@pytest.fixture(scope="module")
def page():
    review = json.loads((ROOT / "docs" / "reviews" / SLUG / "review.json").read_text(encoding="utf-8"))
    records = json.loads((ROOT / "cache" / SLUG / "records.json").read_text(encoding="utf-8"))
    topic = json.loads((ROOT / "topics" / f"{SLUG}.json").read_text(encoding="utf-8"))
    from harness import pipeline                                  # the specs exactly as harness/pipeline.py builds them
    specs = {sp.get("name"): sp for sp, _ in pipeline._outcome_specs(topic)}
    return review, reason_audit.sources_by_trial(SLUG, records, ROOT), specs


def _audit(page, outcome_name, trial):
    review, sources, specs = page
    outcome = next(o for o in review["outcomes"] if o["name"] == outcome_name)
    row = next(d for d in outcome["declared_absent_trials"] if str(d.get("id") or d.get("label")).endswith(trial))
    return reason_audit.audit_reason_row(outcome, row, sources.get(trial, []), specs.get(outcome_name) or {})


def test_exposure_counts_do_not_disprove_a_mortality_refusal(page):
    a = _audit(page, "Mortality", SMART)
    assert a["verdict"] != reason_audit.REASON_FALSE_VALUE_HELD, a
    assert "426" not in (a.get("source_span") or ""), a


def test_the_make30_composite_does_not_disprove_a_component_refusal(page):
    # the composite may never be the disproving evidence; a disproof, if any, must be a COMPONENT identity -- SMART's RRT refusal
    # ("no percentage-corroborated arm counts ... found") IS disproved, correctly, by "189 patients (2.5%) ... and 220 patients
    # (2.9%) ... received new renal-replacement therapy", a component count matching every field
    for outcome in ("Acute kidney injury", "New renal-replacement therapy"):
        a = _audit(page, outcome, SMART)
        assert "major adverse kidney event" not in (a.get("source_span") or "").lower(), (outcome, a)
        if a["verdict"] == reason_audit.REASON_FALSE_VALUE_HELD:
            ident = a["evidence_identity"]
            assert ident["part"] == "COMPONENT" and not ident["mismatch"], (outcome, ident)
        make = [c for c in a.get("candidates", []) if "major adverse kidney event" in c["span"].lower()]
        assert all(any(m.startswith("part:COMPOSITE") for m in c["mismatch"]) for c in make), (outcome, make)


def test_a_raw_count_does_not_disprove_a_design_refusal(page):
    # SPLIT is cluster-crossover; the refusal names the missing design-adjusted effect. A count is not a design-adjusted effect.
    for outcome in ("Mortality", "Acute kidney injury", "New renal-replacement therapy"):
        a = _audit(page, outcome, SPLIT)
        assert a["verdict"] != reason_audit.REASON_FALSE_VALUE_HELD, (outcome, a)


def test_smart_table2_adjusted_or_is_a_typed_candidate_not_a_pooled_value(page):
    a = _audit(page, "Mortality", SMART)
    cands = [c for c in a.get("candidates", []) if c.get("role") == "EFFECT_ESTIMATE"]
    hit = next((c for c in cands if c.get("estimate") == 0.90 and c.get("ci") == [0.80, 1.01]), None)
    assert hit, a.get("candidates")
    assert hit["adjusted"] is True and "random effect" in (hit.get("model") or "").lower() and "icu" in hit["model"].lower()
    assert "30" in (hit.get("timepoint") or "") and hit["part"] == "COMPONENT" and hit["effect_measure"] == "OR"
    assert "effect_measure:OR!=RR" in hit["mismatch"]   # OR is not the outcome's RR estimand: recognised, NOT auto-pooled
    assert a["verdict"] != reason_audit.REASON_FALSE_VALUE_HELD


def test_smart_table2_rrt_and_aki_rows_are_typed_with_model_and_timepoint(page):
    got = {}
    for outcome in ("New renal-replacement therapy", "Acute kidney injury"):
        a = _audit(page, outcome, SMART)
        got[outcome] = [(c.get("estimate"), c.get("ci")) for c in a.get("candidates", []) if c.get("role") == "EFFECT_ESTIMATE"
                        and c.get("adjusted") and c.get("part") == "COMPONENT"]
    assert (0.84, [0.68, 1.02]) in got["New renal-replacement therapy"], got
    assert (0.91, [0.82, 1.01]) in got["Acute kidney injury"], got
