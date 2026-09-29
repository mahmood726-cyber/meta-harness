"""V1.0.1 round 11 (G1): the conditions the dapagliflozin / empagliflozin HFpEF withdrawals (2026-09-19) named before a
corrected estimate may be served -- a composite read in full, registry analyses chosen by identity, a subpopulation
never the randomised result, an interval level never assumed -- as harness code, with plants (scripts/plants_round11.py)
and the withdrawal's own history pinned so the fix cannot restate it."""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from harness import target_endpoint as te

ROOT = Path(__file__).resolve().parents[1]
WITHDRAWN = {"dapagliflozin-hfpef-hosp": ("PMID 36027570", (0.88, 0.74, 1.05), (0.82, 0.73, 0.92)),
             "empagliflozin-hfpef-hosp": ("PMID 34449189", (0.91, 0.76, 1.09), (0.79, 0.69, 0.90))}


def _spec(slug):
    t = json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))
    return dict(t.get("primary_outcome") or t["outcomes"][0])


def test_plants_fire_on_the_prefix_record_and_not_on_this_harness():
    pre = json.loads((ROOT / "evidence/v101_integrated/round11_plants/prefix_41239b94.json").read_text(encoding="utf-8"))
    assert all(v["fired"] for k, v in pre.items() if k.startswith("Q")) and not any(
        v["fired"] for k, v in pre.items() if k.startswith("C"))
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "plants_round11.py"), "--harness-root", str(ROOT)],
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    assert not any(v["fired"] for v in json.loads(out).values())


def test_worsening_heart_failure_is_a_component_of_the_composite():
    assert te.canonical_components(_spec("dapagliflozin-hfpef-hosp")) == ["cardiovascular death", "worsening heart failure"]
    spec = _spec("dapagliflozin-hfpef-hosp")
    # CV death alone is missing a component: never the composite
    assert te._classify(spec, "Subjects Included in the Endpoint of Cardiovascular Death")["target_endpoint_class"] != te.EXACT_TARGET
    # HF hospitalisation (EMPEROR-Preserved) or hospitalisation + urgent visit (DELIVER) both meet 'worsening HF'
    for text in ("CV death or hospitalisation for heart failure",
                 "CV Death, Hospitalization Due to Heart Failure or Urgent Visit Due to Heart Failure"):
        assert te._classify(spec, text)["target_endpoint_class"] == te.EXACT_TARGET, text


def test_a_non_95_interval_is_never_read_as_95():
    a = {"paramType": "Hazard Ratio (HR)", "paramValue": "0.79", "ciPctValue": "95.03", "ciNumSides": "TWO_SIDED",
         "ciLowerLimit": "0.69", "ciUpperLimit": "0.90"}
    assert te._one_analysis(a) is None
    assert te._one_analysis(dict(a, ciPctValue="95"))["ci_level"] == 95.0
    assert te._one_analysis({k: v for k, v in a.items() if k != "ciPctValue"}) is None      # not stated: not assumed


@pytest.mark.parametrize("slug", sorted(WITHDRAWN))
def test_withdrawn_history_is_pinned_and_the_corrected_selection_is_disclosed_not_served(slug):
    rid, published, corrected = WITHDRAWN[slug]
    spec = _spec(slug)
    pub = next(s for s in spec["withdrawn"]["statements"] if s.startswith("What was published"))
    assert tuple(map(float, re.search(r"HR (\d\.\d+) \(95% CI (\d\.\d+) to (\d\.\d+)\)", pub).groups())) == published
    rev = json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))
    out = rev["outcomes"][0]
    assert out["trials"] == []                                                     # still withdrawn: nothing pooled
    row = next(a for a in out["declared_absent_trials"] if a.get("absent_kind") == "result_withdrawn")
    w = row["withdrawn_effect"]
    assert row["id"] == rid and (w["effect"], w["ci_low"], w["ci_high"]) == published
    now = row["selection_now"]
    assert (now["effect"], now["ci_low"], now["ci_high"]) == corrected and now["target_endpoint_class"] == te.EXACT_TARGET
