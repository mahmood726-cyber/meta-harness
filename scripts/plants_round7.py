"""Plants for the round-7 harness fixes (V1.0.1, statins-older-adults and MRA reviews): each plant builds the defect's
input and reports FIRED when the harness under test still produces the defect. Run against the PRE-FIX harness (a
sparse worktree of 1801d205) every plant must fire; against HEAD none may.

  python scripts/plants_round7.py --harness-root <dir containing harness/> [--data-root <repo>] [--out <json>]

The data root (held records, registrations) is always this repository; only the CODE under test changes.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path


def run(harness_root: Path, data_root: Path) -> dict:
    sys.path.insert(0, str(harness_root))
    for m in [k for k in sys.modules if k == "harness" or k.startswith("harness.")]:
        del sys.modules[m]
    out = {}

    def have(mod):
        try:
            return importlib.import_module(f"harness.{mod}")
        except ImportError:
            return None

    # P1 CONDITION_AS_OUTCOME, population witness: a registered condition the criteria refuse at entry
    pw = have("population_witness")
    fam = {"population": {"criteria": {"value": "Inclusion Criteria:~* Community-dwelling adults~* Age >=75 years~"
                                                "Exclusion Criteria:~* Dementia (clinically evident or previously diagnosed)"},
                          "conditions": {"value": ["Cognitive Impairment, Mild", "Dementia"]}},
           "reports": [], "source_records": [{"id": "NCT09999991", "title": "Lipid-lowering in Older Adults"}]}
    cfg = {"include": {"population_any": ["75 years", "older adults"], "population_none": ["dementia"]}}
    st = pw.decide(fam, cfg)["state"]
    out["P1_population_witness_reads_a_prevented_condition_as_a_diagnosis"] = {"fired": st != "ESTABLISHED", "got": st}

    # P1b CONDITION_AS_OUTCOME, screening: the served X2 on the same record
    screen, cr = have("screen"), have("condition_role")
    rec = {"id": "NCT09999991", "id_type": "nct", "title": "Lipid-lowering in Older Adults", "acronym": "PLANT",
           "study_type": "INTERVENTIONAL", "allocation": "RANDOMIZED", "masking": "TRIPLE",
           "conditions": ["Cognitive Impairment, Mild", "Dementia"], "interventions": ["Atorvastatin 40 mg", "Placebo"]}
    scfg = json.loads((data_root / "topics" / "statins-primary-prevention-elderly.json").read_text(encoding="utf-8"))
    scfg = dict(scfg, slug="plant-no-protocol")
    scr = screen.run([dict(rec)], scfg)
    if cr is not None:
        cr.apply(scr, [rec], {"NCT09999991": {"population": fam["population"]}}, scfg,
                 lambda r, c: screen.run([r], dict(c, slug="plant-no-protocol"))["decisions"][0])
    d = scr["decisions"][0]
    out["P1b_screening_excludes_on_a_prevented_condition"] = {"fired": d["rule_id"] == "X2", "got": [d["decision"], d["rule_id"]]}

    # P2 record identity: a registry record's id overwritten by an AACT design row
    dk = have("design_key")
    r2 = {"id": "NCT09999991", "id_type": "nct"}
    dk.registry_designs({"ctgov": [r2], "designs": [{"nct_id": "NCT09999991", "id": "227809937"}]})
    out["P2_registry_designs_overwrites_the_record_id"] = {"fired": r2["id"] != "NCT09999991", "got": r2["id"]}

    # P3 identity: two registrations sharing an acronym are two trials
    ident = have("identity")
    u = ident.build_publication_units([{"id": "NCT04906720", "id_type": "nct", "acronym": "PAPERS"},
                                       {"id": "NCT06731595", "id_type": "nct", "acronym": "PAPERS"}])
    fams = {u[k]["trial_family_id"] for k in u}
    out["P3_two_registrations_sharing_an_acronym_become_one_family"] = {"fired": len(fams) != 2, "got": sorted(fams)}

    # P4 parent registration: a report that names itself a secondary analysis of JUPITER stays unregistered
    preg = have("parent_registration")
    slug = "statins-primary-prevention-elderly"
    recs = json.loads((data_root / "cache" / slug / "records.json").read_text(encoding="utf-8"))
    recs = dict(recs, records=[r for r in recs["records"] if str(r.get("id")) == "20404379"])
    linked = [x for x in (preg.propose(data_root, slug, recs) if preg and hasattr(preg, "propose") else [])
              if x["state"] == "LINKED" and x.get("nct") == "NCT00239681"]
    out["P4_secondary_report_not_linked_to_its_parent_registration"] = {"fired": not linked, "got": [x["nct"] for x in linked]}

    # P5 recovery panel: a blank AACT link rendered as "unregistered / pre-registration-era"
    page = have("page")
    html = page._search({"search": {"n_records": 1, "recall": {"known": 2, "recovered": 1, "enumerated": 9,
                                                                "status": "RAN_OK", "missed": ["20404379"],
                                                                "missed_reasons": {"20404379": "no_registry_link"},
                                                                "reachable_ceiling": 1, "no_registry_link": 1}}}, False)
    out["P5_blank_registry_link_called_unregistered"] = {"fired": "pre-registration-era" in html,
                                                         "got": "pre-registration-era" in html}

    # P6 positive control: a PENDING_SOURCE control with an OPEN route recorded, or no recorded request, is accepted
    pc = have("positive_control")
    ctl = {"id": "plant", "state": "PENDING_SOURCE", "pmid": "1", "doi": "10.1/x"}
    acq_open = {"plant": {"attempts": [{"route": "PMC_IDCONV", "state": "IN_PMC"},
                                       {"route": "EUROPE_PMC", "state": "OPEN_FULL_TEXT"},
                                       {"route": "PUBLISHER_DOI", "state": "LANDING_PAGE_READ"}]}}
    probs = (pc.pending_problems(ctl, acq_open) + pc.pending_problems(ctl, {})) if hasattr(pc, "pending_problems") else []
    out["P6_pending_control_without_recorded_acquisition_accepted"] = {"fired": len(probs) < 2, "got": probs}

    # P7 comparator design: a non-randomised comparator with no RCT checkpoint goes unmarked
    fn = getattr(pc, "comparator_design", None)
    got = fn("We included observational studies comparing statin use vs no-statin use.")["state"] if fn else None
    out["P7_non_randomised_comparator_not_typed"] = {"fired": got != "NON_RANDOMISED", "got": got}
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness-root", required=True)
    ap.add_argument("--data-root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--out")
    a = ap.parse_args(argv[1:])
    res = run(Path(a.harness_root).resolve(), Path(a.data_root).resolve())
    for k, v in res.items():
        print(("FIRED    " if v["fired"] else "NOT FIRED"), k, v["got"])
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
