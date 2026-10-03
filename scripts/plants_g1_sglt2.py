"""Plants for the sglt2-hfref G1 lane (scripts/g1_sglt2_tracker.py, scripts/g1_sglt2_forest.py). Each guard is shown
to FIRE on a real input with the guard removed, and not as built. Prints JSON."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_sglt2_tracker as t  # noqa: E402
import g1_sglt2_forest as f  # noqa: E402
import k_gap_forest_plot as kfp  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402


def main():
    out = {}
    rows = json.load(open(t.AACT_SOLOIST, encoding="utf-8"))["rows"]
    # S1 identity on two attributes: an acronym-only bind returns the unrelated goitre trials
    built, bad = t.bind_identity("SOLOIST-WHF", 1222, rows), t.bind_identity("SOLOIST-WHF", 1222, rows, acronym_only=True)
    out["S1_identity_two_attributes"] = {"built": built, "guard_removed": bad,
                                         "fired_as_built": built != ["NCT03521934"],
                                         "fires_with_guard_removed": bool(bad) and "NCT03521934" not in bad}
    # S2 a row is admitted only when both gated readers print it identically: EMPEROR-Reduced (0.87 vs 0.86)
    rws, _ = t.comparator_rows()
    er = rws["EMPEROR-REDUCED"]["readings"]
    out["S2_two_reader_admission"] = {"readings": er, "built": t.admit(er), "guard_removed": t.admit(er, require_two=False),
                                      "fired_as_built": t.admit(er) == "ADMITTED_TWO_READERS",
                                      "fires_with_guard_removed": t.admit(er, require_two=False) == "ADMITTED_TWO_READERS"}
    # D3 DEFENCE IN DEPTH (not a plant: removing one layer leaves the other refusing). Attempt 1's reader-1 subtotal
    # 0.74 (0.66-0.81) is refused by the TEXT ANCHOR (the comparator prints 0.68) and, with the anchor replaced by the
    # plot's own subtotal, by RECOMPUTATION (no method pools the rows to a 0.66 lower limit)
    fj = json.load(open(f.OUT, encoding="utf-8"))
    a1 = next(a for a in fj["earlier_attempts"] if a["attempt"] == 1)["run"]["run"]
    resp = json.loads(ms.replay(ms.load_record(os.path.join(kfp.REC_DIR, a1["record_id"] + ".json"))).decode("utf-8"))
    g_built = kfp.gate(resp, f.text_pool(), None)
    plot_only = {"effect": resp["pooled"]["effect"], "lower": resp["pooled"]["lower"], "upper": resp["pooled"]["upper"],
                 "k": None}
    g_removed = kfp.gate(resp, plot_only, None)
    out["D3_misread_subtotal_two_layers"] = {"read_subtotal": resp["pooled"], "built": g_built["problems"],
                                        "guard_removed": g_removed["problems"],
                                        "fired_as_built": g_built["state"] == "PASS",
                                        "refused_by_each_layer_alone": g_built["state"] == g_removed["state"] == "REFUSED"}
    # C1 control: the admitted DAPA-HF row (both readers 0.75 (0.65-0.85)) stays admitted
    out["C1_identical_reads_admitted"] = {"readings": rws["DAPA-HF"]["readings"], "built": t.admit(rws["DAPA-HF"]["readings"]),
                                          "fired_as_built": t.admit(rws["DAPA-HF"]["readings"]) != "ADMITTED_TWO_READERS"}
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
