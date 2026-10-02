"""TWO INDEPENDENT PRIMARY SOURCES for one trial's typed tuple, by regex (no model): the posted CT.gov analysis (AACT
snapshot, bound to its arms through outcome_analysis_groups) and a regulator's document (a held, hashed text).

A SPEC names the sources and the arms -- never a number. Every number is read:
  registry   kgap.aact_adapter.registry_for(nct): the analysis on an outcome whose title matches `outcome_re`, whose
             param_type names the measure, and whose two result groups are titled `arm_t` and `arm_c`
  regulator  the held text's table `table`: the arm columns in header order, then the row 'Hazard ratio vs. <arm_c>
             (95% CI)' -- one 'est (lo, hi)' per non-comparator column, in that order
Verdict (the NOAC lane's two-source rule, outputs/g1_noac/DISPATCH_TO_KGAP.md section 2):
  TWO_SOURCE_VERIFIED  same trial, outcome, measure and CI level; equal estimate and CI at printed precision; no axis
                       (population, timepoint) STATED differently -- an axis one source does not state is listed in
                       silent_axes, never assumed to agree
  CONFLICT / INCOMPARABLE / NOT_FOUND otherwise

    python scripts/g1_two_primary.py   -> outputs/k_gap/two_primary/<slug>.json
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import secondary_meta as sm  # noqa: E402
from kgap import aact_adapter  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap", "two_primary")
SPECS = [
    {"slug": "noac-vs-warfarin-af-stroke", "trial": "RE-LY", "nct": "NCT00262600", "measure": "HR",
     "outcome_re": r"stroke/SEE?\b(?!/)|stroke or systemic embolism", "arm_t": r"150\s*mg", "arm_c": r"warfarin",
     "regulator": {"what": "FDA PRADAXA label, NDA 022512, October 2010 (US government work, public domain)",
                   "git": "origin/evid/v1.0.1-acquisition-cascade",
                   "path": "evidence/acquisition_cascade/held/RE-LY-regulatory/fda_label_2010-10.txt",
                   "sha256": "53d25c29cc7dcf90a18f05188cf5fd3e38efd13740c5b29d20e16d48a7289197",
                   "table": "Table 4"}},
]
_TRIPLE = re.compile(r"(\d+(?:\.\d+)?)\s*\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*\)")


def held_text(reg):
    b = subprocess.run(["git", "show", f"{reg['git']}:{reg['path']}"], cwd=ROOT, capture_output=True,
                       stdin=subprocess.DEVNULL).stdout
    got = hashlib.sha256(b).hexdigest()
    if got != reg["sha256"]:
        raise RuntimeError(f"held text {reg['path']} sha256 {got[:12]} != pinned {reg['sha256'][:12]} (fail closed)")
    return b.decode("utf-8", "replace")


def regulator_tuple(text, table, arm_t, arm_c):
    """(est, lo, hi, evidence) for arm_t vs arm_c from `table`'s 'Hazard ratio vs. <arm_c> (95% CI)' row, binding each
    triple to its column by the header's arm order. None when the table, the header or the row is not found."""
    # the table's own TITLE line (start of a line), not an in-text reference ('see Table 4 and Figure 1')
    m = re.search(rf"(?m)^\s*{re.escape(table)}\b(.*?)(?=\n\s*(?:Table|Figure)\s+\d)", text, re.S)
    if not m:
        return None
    blk = m.group(1)
    head = blk.split("Patients randomized")[0]
    cols = [x.group(0) for x in re.finditer(rf"\d+\s*mg|{arm_c}", head, re.I)]
    row = re.search(rf"Hazard ratio vs\.?\s*{arm_c}\s*\(95% CI\)\s*(.+)", blk, re.I)
    rnd = re.search(r"Patients randomized\s+([\d\s]+)", blk)
    if not cols or not row:
        return None
    non_c = [c for c in cols if not re.fullmatch(arm_c, c, re.I)]
    trip = _TRIPLE.findall(row.group(1))
    idx = next((i for i, c in enumerate(non_c) if re.search(arm_t, c, re.I)), None)
    if idx is None or idx >= len(trip):
        return None
    e, lo, hi = trip[idx]
    return e, lo, hi, {"columns": cols, "row": row.group(0).strip()[:160],
                       "population": ("ALL_RANDOMIZED (table row 'Patients randomized " +
                                      " ".join(rnd.group(1).split()) + "')") if rnd else None}


def registry_tuple(nct, outcome_re, measure, arm_t, arm_c):
    aact_adapter.ensure([nct])
    reg = aact_adapter.registry_for(nct)
    if not reg:
        return None
    want = {"HR": r"hazard|cox"}.get(measure, measure)
    titles = reg["group_titles"]
    for a in reg["analyses"]:
        o = reg["outcomes"].get(a["outcome_id"]) or {}
        if not re.search(outcome_re, o.get("title") or "", re.I) or not re.search(want, a.get("param_type") or "", re.I):
            continue
        gt = [titles.get(g, "") for g in a.get("groups") or []]
        if len(gt) == 2 and any(re.search(arm_t, x, re.I) for x in gt) and any(re.search(arm_c, x, re.I) for x in gt):
            return (a["param_value"], a["ci_lower"], a["ci_upper"],
                    {"analysis_id": a.get("analysis_id"), "groups": gt, "outcome": o.get("title"),
                     "time_frame": o.get("time_frame"), "population": o.get("population"),
                     "population_class": sm.population_class(o.get("population")), "snapshot": reg["_snapshot"]})
    return None


def verify(spec):
    r = registry_tuple(spec["nct"], spec["outcome_re"], spec["measure"], spec["arm_t"], spec["arm_c"])
    g = regulator_tuple(held_text(spec["regulator"]), spec["regulator"]["table"], spec["arm_t"], spec["arm_c"])
    out = {"slug": spec["slug"], "trial": spec["trial"], "nct": spec["nct"], "measure": spec["measure"],
           "registry": r and {"effect": r[0], "lower": r[1], "upper": r[2], **r[3]},
           "regulator": g and {"effect": g[0], "lower": g[1], "upper": g[2], **g[3],
                               "source": {k: spec["regulator"][k] for k in ("what", "git", "path", "sha256", "table")}}}
    if not r or not g:
        out["state"] = "NOT_FOUND"
        return out
    same = all(sm._eq_printed(a, b) for a, b in zip(r[:3], g[:3]))
    silent = [ax for ax, have in (("timepoint", (bool(r[3].get("time_frame")), False)),) if have[0] != have[1]]
    pop_r = r[3].get("population_class")
    pop_g = "ITT" if (g[3].get("population") or "").startswith("ALL_RANDOMIZED") else "NOT_STATED"
    if "NOT_STATED" not in (pop_r, pop_g) and pop_r != pop_g:
        out.update(state="INCOMPARABLE", reasons=[f"POPULATION_{pop_r}_VS_{pop_g}"])
    else:
        out.update(state="TWO_SOURCE_VERIFIED" if same else "CONFLICT", silent_axes=silent,
                   population={"registry": pop_r, "regulator": pop_g})
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    by = {}
    for sp in SPECS:
        by.setdefault(sp["slug"], []).append(verify(sp))
    for slug, rows in by.items():
        with open(os.path.join(OUT, f"{slug}.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"slug": slug, "rows": rows}, fh, indent=1, ensure_ascii=False)
        for r in rows:
            print(slug, r["trial"], r["state"], (r.get("registry") or {}).get("effect"), (r.get("registry") or {}).get("lower"),
                  (r.get("registry") or {}).get("upper"), "|", (r.get("regulator") or {}).get("effect"),
                  (r.get("regulator") or {}).get("lower"), (r.get("regulator") or {}).get("upper"))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
