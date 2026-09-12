"""The hand-verified endpoint-correction override (verified_effects entry flagged override:true) must
BEAT the abstract for that trial+outcome, while an UNFLAGGED verified_effects entry stays a pure fallback.
This is the ORIGIN (PMID 22686415) fix: the abstract's 'primary outcome' is death from cardiovascular
causes (HR 0.98) but our outcome is major vascular events (HR 1.01). Uses ORIGIN's REAL cached abstract so
the test exercises the actual mis-selection the override corrects."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import pipeline  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CFG = json.load(open(os.path.join(ROOT, "topics", "omega3-cardiovascular-events.json"), encoding="utf-8"))
_RECS = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "cache", "omega3-cardiovascular-events",
         "records.json"), encoding="utf-8")).get("records", [])}
_SPEC = _CFG["primary_outcome"]
_INC = [{"id": "22686415", "id_type": "pmid", "label": "ORIGIN"}]
_INTERV = _CFG.get("intervention_terms", ["n-3", "fatty acid"])
_COMP = _CFG.get("comparator_terms", ["placebo", "control"])


def _origin_effect(verified_effects):
    o = pipeline._build_outcome(_SPEC, "efficacy", _INC, _RECS, _INTERV, _COMP,
                                verified_effects=verified_effects)
    t = [x for x in o["trials"] if x["id"] == "PMID 22686415"]
    return t[0].get("effect") if t else None


def test_without_override_abstract_selects_the_wrong_endpoint():
    # The real bug: no override -> the generic 'primary outcome' anchor grabs ORIGIN's CV-death primary 0.98.
    assert _origin_effect(None) == 0.98


def test_override_corrects_to_major_vascular_events():
    ve = {"22686415": {"outcome": _SPEC["name"], "override": True, "effect": 1.01, "ci_low": 0.93,
                       "ci_high": 1.1, "scale": "HR", "provenance": "fulltext_verified",
                       "source": "ORIGIN abstract: ... major vascular events ... hazard ratio, 1.01 ..."}}
    assert _origin_effect(ve) == 1.01


def test_unflagged_verified_effect_does_not_override():
    ve = {"22686415": {"outcome": _SPEC["name"], "effect": 1.01, "scale": "HR"}}  # no override flag
    assert _origin_effect(ve) == 0.98, "an UNFLAGGED verified_effect must not override the abstract"
