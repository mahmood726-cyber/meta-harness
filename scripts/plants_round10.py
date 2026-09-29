"""Plants for round 10 (G1, GLP-1 CVOT comparator): each builds the defect's input and reports FIRED when the harness
under test still produces the defect. On the pre-fix harness every plant fires; on the fixed one none.

  python scripts/plants_round10.py --harness-root <dir containing harness/> [--data-root <repo>] [--out <json>]
"""
from __future__ import annotations

import argparse
import copy
import importlib
import json
import sys
from pathlib import Path

GLP1 = ["ELIXA", "LEADER", "SUSTAIN-6", "EXSCEL", "HARMONY Outcomes", "REWIND", "PIONEER 6", "AMPLITUDE-O"]


def run(harness_root: Path, data_root: Path) -> dict:
    sys.path.insert(0, str(harness_root))
    for m in [k for k in sys.modules if k == "harness" or k.startswith("harness.")]:
        del sys.modules[m]
    orl = importlib.import_module("harness.overlap_relation")
    out = {}
    slug = "glp1-ra-mace-t2d"
    review = json.loads((data_root / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))
    panel = json.loads((data_root / "cache" / slug / "comparators.json").read_text(encoding="utf-8"))[0]
    # the comparator's own MACE analysis is all eight CVOTs ("Forest plots of meta-analysis of the eight CVOTs with
    # GLP-1RA on MACE"); ELIXA's trial-level endpoint is 4-point MACE and the panel binds the outcome to "3-point MACE"
    r = copy.deepcopy(review)
    r["comparator"]["analysis"] = {"membership": {"endpoint_label": "MACE (Fig. 3)",
                                                  "members": [{"label": n, "panel_row": n} for n in GLP1]}}
    prim = (orl._primary(r) or {}).get("name")
    src, ins, outs = orl._members(r, panel, prim, {}, set())
    got = sorted(m["name"] for m in ins)
    out["Q1_comparator_analysis_membership_emptied_by_a_per_row_endpoint_label"] = {
        "fired": got != sorted(GLP1), "got": {"in": got, "out": sorted(m["name"] for m in outs),
                                               "endpoint_for_outcome": src.get("endpoint_for_outcome")}}
    # negative control: with no analysis membership the per-row endpoint binding still governs (ELIXA out)
    src, ins, outs = orl._members(copy.deepcopy(review), panel, (orl._primary(review) or {}).get("name"), {}, set())
    out["C1_control_panel_endpoint_binding_still_excludes_ELIXA_without_a_membership"] = {
        "fired": sorted(m["name"] for m in outs) != ["ELIXA"], "got": sorted(m["name"] for m in outs)}
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness-root", required=True)
    ap.add_argument("--data-root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--out")
    a = ap.parse_args()
    res = run(Path(a.harness_root), Path(a.data_root))
    s = json.dumps(res, indent=1)
    print(s)
    if a.out:
        Path(a.out).write_text(s + "\n", encoding="utf-8", newline="\n")
