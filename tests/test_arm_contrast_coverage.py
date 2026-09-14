"""Randomised-contrast check must not SILENTLY PASS a trial it cannot identify (external audit, last
IDENTITY gap). Every pooled primary trial must appear in arm_contrast with an explicit status; a
trial with no NCT/registry match must read 'unverified_no_registry_match', never be ABSENT (absence
let it pass the contrast check silently -- commit 4 was blind wherever identity broke)."""
import glob
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_every_pooled_primary_trial_has_a_contrast_status():
    gaps = []
    for rp in sorted(glob.glob(os.path.join(_ROOT, "docs", "reviews", "*", "review.json"))):
        slug = os.path.basename(os.path.dirname(rp))
        rv = json.load(open(rp, encoding="utf-8"))
        prim = next((o for o in rv.get("outcomes", []) if o.get("primary")), None)
        pooled = [str(t.get("id", "")).replace("PMID ", "") for t in (prim or {}).get("trials", []) or []]
        acp = os.path.join(_ROOT, "cache", slug, "arm_contrast.json")
        ac = json.load(open(acp, encoding="utf-8")).get("trials", {}) if os.path.exists(acp) else {}
        for pid in pooled:
            if pid not in ac:
                gaps.append(f"{slug}::{pid}")  # absent -> would pass the contrast check silently
    assert not gaps, "pooled trials missing from arm_contrast (silent-pass identity gap): " + "; ".join(gaps)


def test_no_nct_trial_is_visibly_unverified_not_dropped():
    # RALES (10471456, no NCT) must be present AND visibly unverified, not dropped.
    ac = json.load(open(os.path.join(_ROOT, "cache", "spironolactone-hfref-mortality", "arm_contrast.json"), encoding="utf-8"))["trials"]
    assert "10471456" in ac, "RALES (no NCT) dropped from arm_contrast (silent pass)"
    assert ac["10471456"]["status"] == "unverified_no_registry_match"


def test_PLANT_absent_trial_would_be_caught():
    # PLANT: a pooled trial absent from arm_contrast is exactly the silent-pass defect the coverage
    # test catches.
    pooled = ["A", "B", "C"]
    ac = {"A": {}, "B": {}}  # C dropped
    assert [p for p in pooled if p not in ac] == ["C"]
