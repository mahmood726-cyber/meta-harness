"""Consolidation of the g1 lanes (2026-10-04): two semantic conflicts between branches that each passed on its own.

1. g1/forest-reader 99e1c0a8 ingested accepted dual-read figure rows into the secondary registry -- including the
   COMPARATOR's own rows, which then met the admission meant for OTHER metas (outcome vocabulary, estimand, family
   join) and replaced acq/k-gap's comparator-row path: 27 COMPARATOR_SOURCED rows lost (pcsk9 9, probiotics 7, ...).
2. A cross-check BLOCK was never refereed by the trial's own report, so a second meta's dual-read row (PIONEER 6 upper
   1.11 vs 1.10) erased the comparator row's MISMATCH side and glp1 lost G1_MATCHED on DIVERGENCES_NAMED.
Both plants read the committed, regenerated outputs and failed on the first regeneration of the merged code."""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _j(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return json.load(fh)


def test_PLANT_the_comparators_dual_read_is_never_ingested_as_secondary_evidence():
    bad = []
    for p in glob.glob(os.path.join(ROOT, "registry", "secondary_meta", "*.json")):
        d = _j(p)
        m = (d.get("metas") or {}).get(d.get("comparator_pmid")) or {}
        if m.get("provenance") == "MODEL_PROPOSAL_DUAL" and m.get("is_comparator"):
            bad.append(os.path.basename(p))
    assert bad == [], bad
    pc = _j("outputs", "k_gap", "g1", "pcsk9-mace.json")
    assert pc["k_comparator_sourced"] >= 9, pc["k_comparator_sourced"]


def test_PLANT_a_cross_check_block_is_refereed_by_the_trials_own_report():
    g = _j("outputs", "k_gap", "g1", "glp1-ra-mace-t2d.json")
    x = next(t for t in g["trials"] if t["label"] == "PIONEER 6")
    assert str(x.get("disagreement_side") or "").startswith("SECONDARY_WRONG"), x.get("disagreement_side")
    assert g["g1_status"]["state"] == "G1_MATCHED", g["g1_status"]
