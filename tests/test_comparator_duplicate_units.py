"""One comparator trial listed in two of the comparator's tables counts once (consolidation 2026-10-04).

balanced-crystalloids (comparator N 7 -> 6, acq/k-gap f21c0aa4): 'Semler (SMART trial)' and 'Semler [15]' are both SMART
(PMID 29485925). acq/k-gap removed [15] by a first-accession NCT tie-break (SMART-MED, NCT02444988) whose registry arm
'Physiologically-balanced isotonic crystalloid' then read as OTHER_AGENT -- a false reason. The trial is one trial listed
twice: it counts once, by identity, and is never called another agent."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]


def _u(label, pmids=(), ncts=(), drug="DRUG_MATCH", status="DECLARED_ABSENT", slug="s"):
    return {"slug": slug, "label": label, "pmids": list(pmids), "ncts": list(ncts), "drug": drug, "status": status}


def test_PLANT_smart_listed_in_two_tables_counts_once():
    import k_gap_table as kt
    rows = [_u("Semler (SMART trial)", ["29485925"]), _u("Semler [15]", ["29485925"], drug="AGENT_UNCONFIRMED"),
            _u("Young [10]", ["26444692"])]
    kt.mark_duplicate_units(rows)
    assert [r["status"] for r in rows] == ["DECLARED_ABSENT", "DUPLICATE_UNIT", "DECLARED_ABSENT"]
    assert rows[1]["duplicate_of"] == "Semler (SMART trial)" and rows[1]["drug"] != "OTHER_AGENT"


def test_two_numbered_rows_of_one_registration_are_not_merged():
    import k_gap_table as kt
    rows = [_u("1 [21]", ["19717846"], ["NCT00391872"]), _u("9 [28]", ["19717846"], ["NCT00391872"])]
    kt.mark_duplicate_units(rows)
    assert all(r["status"] == "DECLARED_ABSENT" for r in rows)


def test_the_served_crystalloids_set_counts_smart_once():
    import json
    d = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", "balanced-crystalloids-vs-saline-mortality.json"),
                       encoding="utf-8"))
    labels = [t["label"] for t in d["trials"]]
    assert sum(1 for l in labels if l.startswith("Semler") and ("SMART" in l or "[15]" in l)) == 1
    assert d["N_comparator_trials"] == 6
