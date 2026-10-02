"""G1 sglt2-hfref lane: tracker verdict, two-reader comparator rows, two-attribute identity, and the plants."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", "sglt2-hfref-hosp-cvdeath.json"), encoding="utf-8"))
F = json.load(open(os.path.join(ROOT, "g1", "data", "sglt2_hfref_forest.json"), encoding="utf-8"))


def test_both_gated_readers_reproduce_the_comparators_printed_lvef_le40_pool():
    for k in ("result", "result_reader2"):
        g = F[k]["gate"]
        assert F[k]["state"] == "PASS" and g["printed_pool"]["effect"] == "0.74" and g["printed_pool"]["lower"] == "0.68"
        assert g["methods_reproducing"]


def test_every_earlier_attempt_stays_on_record():
    assert [a["attempt"] for a in F["earlier_attempts"]] == [1]
    assert all(a[k]["result"]["state"] == "REFUSED" for a in F["earlier_attempts"] for k in ("run", "run_reader2"))


def test_tracker_verdict_and_named_differences_cite_our_screen():
    # a scope difference is NAMED only when the exclusion audit classifies the excluded record TRUE_SCOPE_DIFFERENCE
    # (scripts/g1_exclusion_audit_tracker.py). SOLOIST-WHF's X3 exclusion MISFIRED (sotagliflozin is an SGLT2 inhibitor
    # under the registered criteria) and its abstract does not state the HFrEF population: an open gap, not a name.
    assert (O["k_matched"], O["N_eligible"], O["N_comparator_trials"]) == (2, 3, 4)
    nd = {d["trial"].split(" ")[0]: d for d in O["named_differences"]}
    assert list(nd) == ["EMPEROR‐Preserved"] and nd["EMPEROR‐Preserved"]["rule_id"] == "X2"
    assert nd["EMPEROR‐Preserved"]["audit"]["class"] == "TRUE_SCOPE_DIFFERENCE"
    assert [g.split(" ")[0] for g in O["open_gaps"]] == ["SOLOIST‐WHF"]
    sol = next(x for x in O["trials"] if x["label"].startswith("SOLOIST"))
    assert sol["blocker"].startswith("INSUFFICIENT_RECORD:RULE_X3_MISFIRED")


def test_same_trials_verdict_holds_under_each_reader():
    st = O["same_trials"]
    assert st["readers_agree_on_verdict"] and st["verdict"]["verdict"] == "AGREE"
    assert {v["verdict"]["verdict"] for v in st["by_reader"].values()} == {"AGREE"}


def test_plants_fire_only_with_their_guard_removed():
    out = json.loads(subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "plants_g1_sglt2.py")],
                                    capture_output=True, text=True, encoding="utf-8", check=True).stdout)
    assert not any(v["fired_as_built"] for v in out.values())
    assert all(v["fires_with_guard_removed"] for v in out.values() if "fires_with_guard_removed" in v)
    assert out["D3_misread_subtotal_two_layers"]["refused_by_each_layer_alone"]
