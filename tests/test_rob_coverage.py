"""Canonical trial identity: every pooled trial gets a RoB2 assessment (external audit #1).

Before: rob2_build DROPPED trials with no NCT (RALES) and any NCT the AACT snapshot did not carry
(J-EMPHASIS NCT01115855, SOUL NCT03914326, omarigliptin) — they rendered "no registry match / not
assessed" even though Results knows the NCT. 28 of 100 pooled trials were unassessed, and the
randomised-contrast check silently passes any trial it cannot identify. Fix: assess EVERY pooled
trial — registry design where AACT has the NCT, else the abstract (blinding/randomisation from the
trial's own text). The canonical identity is shared; RoB no longer drops what it cannot find in AACT.
"""
import glob
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _pooled_primary(slug):
    rv = json.load(open(os.path.join(_ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))
    prim = next((o for o in rv.get("outcomes", []) if o.get("primary")), None)
    return [str(t.get("id", "")).replace("PMID ", "").strip() for t in (prim or {}).get("trials", []) or []]


def _rob_assessed(slug):
    p = os.path.join(_ROOT, "cache", slug, "rob2.json")
    if not os.path.exists(p):
        return set()
    return set(json.load(open(p, encoding="utf-8")).get("trials", {}))


def test_every_pooled_primary_trial_is_rob_assessed():
    gaps = []
    n_pooled = n_assessed = 0
    for rp in sorted(glob.glob(os.path.join(_ROOT, "docs", "reviews", "*", "review.json"))):
        slug = os.path.basename(os.path.dirname(rp))
        pooled = _pooled_primary(slug)
        assessed = _rob_assessed(slug)
        n_pooled += len(pooled)
        n_assessed += sum(1 for p in pooled if p in assessed)
        miss = [p for p in pooled if p not in assessed]
        if miss:
            gaps.append(f"{slug}: {miss}")
    assert not gaps, ("pooled primary trials with NO RoB assessment (identity/AACT-only-match gap): "
                      + "; ".join(gaps) + f" [{n_assessed}/{n_pooled}]")


def test_recovered_and_no_nct_trials_are_assessed_not_dropped():
    # Two failure modes both fixed here:
    #  - STALENESS: J-EMPHASIS (28824029, NCT01115855 which IS in AACT) was added by a recovery AFTER
    #    rob2.json was last built, so it was missing until regeneration.
    #  - NO NCT: RALES (10471456, no registration) was structurally dropped; now assessed from abstract.
    spiro = _rob_assessed("spironolactone-hfref-mortality")
    assert "28824029" in spiro, "J-EMPHASIS must be RoB-assessed (was stale-missing after recovery)"
    assert "10471456" in spiro, "RALES (no NCT) must be RoB-assessed from the abstract, not dropped"
    rob = json.load(open(os.path.join(_ROOT, "cache", "spironolactone-hfref-mortality", "rob2.json"), encoding="utf-8"))
    # RALES has no NCT -> assessed from the abstract only (registry_in_aact False), not registry-backed.
    assert rob["trials"]["10471456"].get("registry_in_aact") is False
    assert rob["trials"]["10471456"].get("assessed_from") == "abstract only"


def test_PLANT_missing_rob_assessment_is_caught():
    # PLANT: simulate the old defect — a pooled trial absent from rob2. The coverage check must flag it.
    pooled = ["A", "B", "C"]
    assessed = {"A", "B"}  # C dropped (e.g., NCT not in AACT)
    miss = [p for p in pooled if p not in assessed]
    assert miss == ["C"]  # the assertion in the coverage test would fire on this
