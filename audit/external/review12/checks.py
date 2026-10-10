#!/usr/bin/env python3
"""Topic 12 independent numerical and isolated-code checks (standard library).

This is NOT a repository replay or certificate verifier. The contrast check
executes transcribed excerpts of pinned functions with narrowly scoped fixture
adapters; see README.md. No network or repository changes are performed.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import NormalDist
from types import SimpleNamespace

PIN = "0730234d0b4f"
REVIEW_SHA256 = "17d2b1984f234c37805170333b7ed3b86fb98f19fd0129276877657d0dd71bd8"
PASSAGE = "ClinicalTrials.gov results (structured, continuous): outcome 'The Change From Baseline in Subjective Sleep Latency.' mean -19.1 (SD 47.3, n=137) [Circadin] vs -1.7 (SD 47.8, n=144) [Placebo] minutes — population: Pre-planned analysis on ITT population age 65-80"
EXPECTED_PASSAGE_SHA256 = "5810bccfc56f71a4e5404b862ba2ffea65d04d83af5e4f688ab3890615c1b2db"

# Literal regex from pinned harness/armcontrast.py.
_PLACEBO = re.compile(r"placebo|\bsham\b|matching|standard care|usual care|no treatment|control arm", re.I)

# Fixture adapters, NOT imported repository modules. Inputs below contain only
# plain ASCII labels, so lower-casing supplies the folding needed for this test.
lexicon = SimpleNamespace(fold=lambda text: str(text).lower())
armcontrast = SimpleNamespace(_PLACEBO=_PLACEBO)

def _nct_id(rec):
    """Fixture-only identifier adapter: no identifier-resolution test is claimed."""
    return rec["id"]

# Transcribed executable body from harness/screen.py at PIN.
def _record_arm_interventions_background_only(rec, keywords) -> tuple[bool, str]:
    interventions = [str(x or "") for x in (rec.get("interventions") or []) if str(x or "").strip()]
    if len(interventions) < 2:
        return False, ""
    folded = [lexicon.fold(x).lower() for x in interventions]
    kws = [lexicon.fold(k).lower().strip() for k in (keywords or []) if str(k or "").strip()]
    if not kws:
        return False, ""
    def has_interest(s):
        return any(k and k in s for k in kws)
    active = [s for s in folded if not armcontrast._PLACEBO.fullmatch(s.strip())]
    if len(active) < 2 or not all(has_interest(s) for s in active):
        return False, ""
    return True, "; ".join(interventions)

# Transcribed executable body from harness/screen.py at PIN. In the test, the
# structural arm adapter returns False to isolate and test this branch's flow.
def _background_only_randomised_contrast(rec, keywords, arm_index) -> tuple[bool, str]:
    nct = _nct_id(rec)
    if nct:
        status = armcontrast.background_only_inclusion(nct, keywords, arm_index)
        if status is True:
            _st, basis = armcontrast.contrast_status(nct, keywords, arm_index)
            return True, basis
    bg, basis = _record_arm_interventions_background_only(rec, keywords)
    if bg:
        return True, ("the intervention of interest appears in every structured CT.gov arm entry; "
                      "the randomised difference is another intervention: " + basis)
    return False, ""

def main() -> dict:
    mu_t, sd_t, n_t = -19.1, 47.3, 137
    mu_c, sd_c, n_c = -1.7, 47.8, 144
    effect = mu_t - mu_c
    se = math.sqrt(sd_t**2/n_t + sd_c**2/n_c)
    z = NormalDist().inv_cdf(0.975)
    ci = [effect-z*se, effect+z*se]
    digest = hashlib.sha256(PASSAGE.encode("utf-8")).hexdigest()
    assert digest == EXPECTED_PASSAGE_SHA256
    assert math.isclose(effect, -17.4, abs_tol=1e-12)
    assert [round(x, 2) for x in ci] == [-28.52, -6.28]

    labels = ["placebo Circadin", "Circadin"]
    record = {"id": "NCT00816673", "interventions": labels}
    keywords = ["melatonin", "prolonged-release melatonin", "controlled-release melatonin", "circadin"]
    fallback = _record_arm_interventions_background_only(record, keywords)
    assert fallback[0] is True  # reproduces the erroneous background-only decision
    control = _record_arm_interventions_background_only(
        {"id": "FIXTURE_CONTROL", "interventions": ["placebo", "Circadin"]}, keywords)
    assert control[0] is False

    armcontrast.background_only_inclusion = lambda *args: False
    combined = _background_only_randomised_contrast(record, keywords, {})
    assert combined[0] is True  # a negative structural result does not stop fallback

    result = {
        "reference": PIN,
        "review_sha256_declared_not_independently_recomputed": REVIEW_SHA256,
        "scope": "independent arithmetic and isolated transcribed-function test; no full repository replay",
        "arithmetic": {
            "mean_difference_minutes": effect, "standard_error_minutes": se,
            "normal_critical_value": z, "ci95_minutes": ci,
            "rounded_display_matches": True,
            "population": "age 65-80 subgroup", "timepoint": "3 weeks",
            "estimand": "unadjusted between-arm difference in mean change",
        },
        "passage": {"text": PASSAGE, "sha256": digest, "matches_pinned_digest": True},
        "contrast_fixture": {
            "interventions": labels,
            "placebo_fullmatch": bool(_PLACEBO.fullmatch("placebo circadin")),
            "placebo_search": bool(_PLACEBO.search("placebo circadin")),
            "fallback_background_only": fallback[0], "basis": fallback[1],
            "plain_placebo_control_background_only": control[0],
            "fixture_structural_result": False,
            "combined_result_after_structural_false": combined[0],
            "dependency_adapters": ["ASCII lower-case fold", "literal NCT id", "structural result fixed False"],
        },
        "not_checked": ["canonical review hash", "HTML byte hash", "certificate release hash",
                        "full offline replay", "production end-to-end screening/build",
                        "complete trial census", "current live registry response bodies"],
    }
    Path(__file__).with_name("results.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result

if __name__ == "__main__":
    main()
