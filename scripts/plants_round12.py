"""Plant for round 12 (G1, NOAC review): 'Stroke or systemic embolism' names two components; the lexicon read it as
{stroke}, so a stroke-only measure matched the composite EXACT. FIRED on the pre-fix harness, not on the fix; the
control (a measure naming both stays EXACT) must hold on both.

  python scripts/plants_round12.py --harness-root <dir containing harness/> [--out <json>]
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

SPEC = {"name": "Stroke or systemic embolism"}
STROKE_ONLY = "Number of Participants With Stroke"
BOTH = "The primary outcome was ischemic or hemorrhagic stroke or systemic embolism."
# RE-LY's registered composite abbreviates systemic embolic event as SEE; a first cut of the fix read it as stroke only
# and RE-LY's extractable registry composite was lost (caught by the offline family check, before commit)
RELY = "Yearly Event Rate for Composite Endpoint of Stroke/SEE"


def run(harness_root: Path) -> dict:
    sys.path.insert(0, str(harness_root))
    for m in [k for k in sys.modules if k == "harness" or k.startswith("harness.")]:
        del sys.modules[m]
    te = importlib.import_module("harness.target_endpoint")
    comps = te.canonical_components(SPEC)
    c = te._classify(SPEC, STROKE_ONLY)
    return {"Q1_stroke_or_SE_read_as_stroke_only": {
                "fired": comps == ["stroke"] or c["target_endpoint_class"] == te.EXACT_TARGET,
                "got": {"components": comps, "stroke_only_measure": c["target_endpoint_class"]}},
            "C1_measure_naming_both_stays_exact": {
                "fired": te._classify(SPEC, BOTH)["target_endpoint_class"] != te.EXACT_TARGET,
                "got": te._classify(SPEC, BOTH)["target_endpoint_class"]},
            "C2_RELY_stroke_SEE_abbreviation_stays_exact": {
                "fired": te._classify(SPEC, RELY)["target_endpoint_class"] != te.EXACT_TARGET,
                "got": te._classify(SPEC, RELY)["target_endpoint_class"]},
            "C3_see_as_an_English_word_is_not_embolism": {
                "fired": "systemic embolism" in te._components_from_text("stroke rates (see table 2) were lower"),
                "got": sorted(te._components_from_text("stroke rates (see table 2) were lower"))}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness-root", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    s = json.dumps(run(Path(a.harness_root)), indent=1)
    print(s)
    if a.out:
        Path(a.out).write_text(s + "\n", encoding="utf-8", newline="\n")
