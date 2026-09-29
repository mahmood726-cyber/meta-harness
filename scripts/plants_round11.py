"""Plants for round 11 (G1: the conditions the dapagliflozin / empagliflozin HFpEF withdrawals named, 2026-09-19).
Each builds the defect's input from held registry data and reports FIRED when the harness under test still produces
the defect. On the pre-fix harness every plant fires; on the fixed one none. Controls must hold on both.

  python scripts/plants_round11.py --harness-root <dir containing harness/> [--data-root <repo>] [--out <json>]
"""
from __future__ import annotations

import argparse
import copy
import importlib
import json
import sys
from pathlib import Path

WHF = "Composite cardiovascular death or worsening heart failure"


def run(harness_root: Path, data_root: Path) -> dict:
    sys.path.insert(0, str(harness_root))
    for m in [k for k in sys.modules if k == "harness" or k.startswith("harness.")]:
        del sys.modules[m]
    te = importlib.import_module("harness.target_endpoint")
    out = {}

    def spec_of(slug):
        t = json.loads((data_root / "topics" / f"{slug}.json").read_text(encoding="utf-8"))
        s = dict(t.get("primary_outcome") or t["outcomes"][0])
        s.pop("withdrawn", None)          # the plant measures what the SELECTOR would serve
        return s

    def held(slug, nct):
        return json.loads((data_root / "cache" / slug / "records.json").read_text(encoding="utf-8"))["ctgov_results"][nct]

    dapa, empa = spec_of("dapagliflozin-hfpef-hosp"), spec_of("empagliflozin-hfpef-hosp")
    deliver = held("dapagliflozin-hfpef-hosp", "NCT03619213")
    emperor = held("empagliflozin-hfpef-hosp", "NCT03057951")

    # Q1: the composite's target is read as cardiovascular death alone, so a CV-death-only measure is EXACT
    comps = te.canonical_components(dapa)
    pick = te.select_target_endpoint(dapa, "", deliver, ["dapagliflozin"], ["placebo"])["selected"] or {}
    out["Q1_worsening_HF_composite_read_as_CV_death_only"] = {
        "fired": comps == ["cardiovascular death"] or "Cardiovascular Death" == (pick.get("registry_title") or "")[-20:],
        "got": {"components": comps, "selected": pick.get("registry_title"), "effect": pick.get("effect")}}

    # Q2: a registry SUBPOPULATION measure (LVEF <60%, 2200/2172 of 3131/3132) served as the ITT result -- placed first
    comp_spec = dict(dapa, components=["cardiovascular death", "hospitalization for heart failure", "urgent visit for heart failure"])
    subfirst = [copy.deepcopy(deliver[1]), copy.deepcopy(deliver[0])]
    pick = te.select_target_endpoint(comp_spec, "", subfirst, ["dapagliflozin"], ["placebo"])["selected"] or {}
    out["Q2_registry_subpopulation_measure_served_as_ITT"] = {
        "fired": "Subpopulation" in (pick.get("registry_title") or ""),
        "got": {"selected": pick.get("registry_title"), "effect": pick.get("effect")}}

    # Q3: a 95.03% alpha-adjusted interval rendered and pooled as a 95% CI (EMPEROR-Preserved's registered primary)
    emp_spec = dict(empa, components=["cardiovascular death", "heart failure hospitalization"])
    pick = te.select_target_endpoint(emp_spec, "", emperor, ["empagliflozin"], ["placebo"])["selected"] or {}
    out["Q3_non_95_interval_served_as_95"] = {
        "fired": pick.get("effect") == 0.79 and "95% CI" in (pick.get("source") or ""),
        "got": {"effect": pick.get("effect"), "source": pick.get("source")}}

    # Q4: several analyses on one measure chosen by ARRAY ORDER -- PARALLEL-HF's measure with its component analyses
    # moved in front of the composite one
    pspec = json.loads((data_root / "topics" / "sacubitril-valsartan-hfref.json").read_text(encoding="utf-8"))
    pspec = dict(pspec.get("primary_outcome") or pspec["outcomes"][0])
    par = next(om for om in held("sacubitril-valsartan-hfref", "NCT02468232")
               if len(om.get("analyses") or []) == 3 and "1.0881" in json.dumps(om))
    par = copy.deepcopy(par)
    par["analyses"] = par["analyses"][1:] + par["analyses"][:1]
    pick = te.select_target_endpoint(pspec, "", [par], ["sacubitril"], ["enalapril"])["selected"] or {}
    out["Q4_measure_analysis_chosen_by_array_order"] = {
        "fired": pick.get("effect") not in (None, 1.0881) or (pick.get("effect") is None and False),
        "got": {"effect": pick.get("effect"), "n_analyses": len(par["analyses"])}}

    # controls: the served PARALLEL-HF row (composite analysis first) still selects 1.0881; DELIVER's full-population
    # measure alone is still the registry result for an explicit three-component target
    par0 = next(om for om in held("sacubitril-valsartan-hfref", "NCT02468232")
                if len(om.get("analyses") or []) == 3 and "1.0881" in json.dumps(om))
    pick = te.select_target_endpoint(pspec, "", [par0], ["sacubitril"], ["enalapril"])["selected"] or {}
    out["C1_served_PARALLEL_HF_row_unchanged"] = {"fired": pick.get("effect") != 1.0881, "got": pick.get("effect")}
    pick = te.select_target_endpoint(comp_spec, "", [deliver[0]], ["dapagliflozin"], ["placebo"])["selected"] or {}
    out["C2_DELIVER_full_population_measure_still_selected"] = {"fired": pick.get("effect") != 0.82, "got": pick.get("effect")}
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
