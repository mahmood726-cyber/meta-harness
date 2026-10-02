"""A bare endpoint LABEL must not decide which endpoint a harvested effect is about.

The defect, from the served corpus. The spironolactone all-cause-mortality outcome declares
"primary outcome" / "primary endpoint" / "primary end point" among its keywords. Those are endpoint
LABELS, not the outcome's own words. J-EMPHASIS (PMID 28824029) reports

    "The primary endpoint occurred in 29.7% ... [hazard ratio=0.85 (95% CI: 0.53-1.36)]"

and its primary endpoint is "a composite of death from cardiovascular causes or hospitalization for
HF". The label keyword harvested that sentence as an all-cause-mortality effect candidate; the
source-hierarchy selector then preferred it over the trial's own mortality counts (17/111 vs 10/110,
already extracted and bound to the held abstract) because a published effect of the declared
estimand CLASS outranks a reconstruction. Endpoint identity was never consulted. The served pool
carried a CV-death/HHF composite as all-cause mortality.

Why the obvious fix is wrong. Dropping label keywords outright breaks the 22 declared outcomes that
ARE the trial's primary composite: PMID 30418475's only MACE candidate is harvested through exactly
that label, and its served 1.02 would vanish. So the rule is conditional -- a label may scope a
harvest only when the label's own definition span in the SAME held text is the declared outcome.

Each case below is a different required answer, which is the point: a change that makes them all
refuse, or all pass, is wrong no matter which one it was written for.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import source_hierarchy as sh  # noqa: E402


def _cfg(slug):
    with open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8") as fh:
        return json.load(fh)


def _abstracts(slug):
    with open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8") as fh:
        return {str(r.get("id")): (r.get("abstract") or "") for r in json.load(fh)["records"]}


def _spec(slug):
    cfg = _cfg(slug)
    po = cfg["primary_outcome"]
    return {"name": po["name"], "keywords": list(po["keywords"]), "estimand": po.get("estimand")}


def _harvest(slug, pmid):
    """The effect candidates the harvester surfaces for this trial under the declared outcome."""
    spec = _spec(slug)
    abstract = _abstracts(slug)[pmid]
    return list(sh.effect_candidates_for_outcome(spec, abstract))


def _effects(cands):
    return sorted(round(float(c["effect"]), 4) for c in cands if c.get("effect") is not None)


# --- the defect -------------------------------------------------------------------------------

def test_composite_named_only_by_label_is_not_harvested_for_a_component_outcome():
    """J-EMPHASIS: 'The primary endpoint occurred in...' resolves to a CV-death/HHF composite.

    The declared outcome is all-cause mortality. The composite HR 0.85 must not be offered as a
    candidate for it -- if it is, the selector will prefer it over the trial's own mortality counts,
    which is what the served release did.
    """
    got = _effects(_harvest("spironolactone-hfref-mortality", "28824029"))
    assert 0.85 not in got, (
        "the CV-death/HHF composite HR 0.85 is still harvested as an all-cause-mortality candidate; "
        f"candidates: {got}"
    )
    assert got == [], f"no effect+CI for all-cause mortality is reported in this abstract; got {got}"


def test_emphasis_hf_keeps_its_own_mortality_effect():
    """EMPHASIS-HF: '...died (hazard ratio, 0.76; 95% CI, 0.62 to 0.93)' names death itself.

    The sentence does not rely on a label, so it survives. Its served number must not move.
    """
    got = _effects(_harvest("spironolactone-hfref-mortality", "21073363"))
    assert 0.76 in got, f"the trial's own all-cause mortality HR 0.76 was dropped; candidates: {got}"


def test_emphasis_hf_composite_harvested_by_label_is_dropped():
    """The same trial ALSO reports its primary composite HR 0.63 (0.54-0.74), harvested by the label.

    It never displaced the served row only because that row was already a reported effect, so the
    displacement rule did not fire -- the same defect, unfired. It must not be a candidate either.
    """
    got = _effects(_harvest("spironolactone-hfref-mortality", "21073363"))
    assert 0.63 not in got, f"the primary-composite HR 0.63 is still a mortality candidate: {got}"


# --- the control: the label is doing correct work here and must keep working ---------------------

def test_label_still_scopes_a_harvest_when_it_resolves_to_the_declared_outcome():
    """PMID 30418475's ONLY candidate is harvested through 'primary endpoint'.

    There the declared outcome IS the trial's primary composite, so the label resolves to the thing
    being pooled. Losing this candidate would remove a correct served effect. A fix that refuses
    this case is a fix that deleted the keyword rather than understanding it.
    """
    got = _effects(_harvest("dpp4-mace-t2d", "30418475"))
    assert got, "the declared 3-point MACE outcome lost its only harvested candidate"


def test_rales_is_untouched():
    """RALES reports 'relative risk of death, 0.70' and is harvested by content words, not a label."""
    got = _effects(_harvest("spironolactone-hfref-mortality", "10471456"))
    assert 0.85 not in got and 0.63 not in got


@pytest.mark.parametrize("slug,pmid", [
    ("glp1-ra-mace-t2d", "31185157"),
    ("glp1-ra-mace-t2d", "27633186"),
    ("glp1-ra-mace-t2d", "27295427"),
    ("glp1-ra-mace-t2d", "34215025"),
])
def test_composite_outcomes_keep_every_candidate_they_had(slug, pmid):
    """No MACE trial may lose a candidate: these were measured unchanged with and without labels."""
    assert _harvest(slug, pmid), f"{slug}/{pmid} lost all candidates"
