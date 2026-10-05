"""PLANTS for scripts/g1_binding_secondary.py (SECONDARY_SINGLE from a meta's open supplementary table) and its tracker
hook (g1_tracker.apply_secondary_bindings). Row shapes are the real ones of PMID 42402602's eTable 4."""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / "scripts"))

import g1_binding_secondary as gs  # noqa: E402

MORT = "All causes mortality (short term)"
EX = {"outcome_rows": [["Blum 2015", "Prednisone", MORT, "16", "392", "13", "393"],
                       ["Mikami 2007", "Prednisone", MORT, "1", "16", "0", "15"],
                       ["Snijders 2010", "Prednisone", MORT, "1", "61", "1", "59"],
                       ["Snijders* 2010", "Prednisone", MORT, "5", "48", "5", "45"],
                       ["Meijvis 2011", "Dexamethasone", MORT, "9", "151", "11", "153"],
                       ["Confalonieri 2005", "Hydrocortisone", MORT, "0", "23", "7", "22"]],
      "all_binary_rows": [["Blum 2015", "Prednisone", "Hyperglycemia", "3", "392", "4", "393"],
                          ["Mikami 2007", "Prednisone", "Secondary infections", "0", "15", "0", "16"],
                          ["Confalonieri 2005", "Hydrocortisone", "Hyperglycemia", "1", "23", "1", "23"]],
      "dose": {}, "horizon": {"blum 2015": {"horizon": "30-day all-cause mortality", "data_source": "Trial report"},
                              "mikami 2007": {"horizon": "In-hospital mortality", "data_source": "Trial report"},
                              "meijvis 2011": {"horizon": "30-day all-cause mortality",
                                               "data_source": "Secondary source (Pitre 2025)"},
                              "confalonieri 2005": {"horizon": "30-day all-cause mortality", "data_source": "Trial report"}}}
EX["all_binary_rows"] = EX["outcome_rows"] + EX["all_binary_rows"]
TP = r"30-day|in-hospital"


def test_admits_a_consistent_row():
    v, why = gs.admit("blum 2015", EX, TP)
    assert why is None and v == {"events_t": 16, "n_t": 392, "events_c": 13, "n_c": 393}


def test_refusals_are_named():
    assert gs.admit("mikami 2007", EX, TP)[1]["why"] == "ARM_N_SWAPPED_WITHIN_SOURCE"
    assert gs.admit("snijders 2010", EX, TP)[1]["why"] == "SUBGROUP_SPLIT_ROWS"
    assert gs.admit("meijvis 2011", EX, TP)[1]["why"] == "SECONDARY_OF_SECONDARY"
    assert gs.admit("confalonieri 2005", EX, TP)[1]["why"] == "ARM_N_INCONSISTENT_WITHIN_SOURCE"
    assert gs.admit("wagner 1956", EX, TP)[1]["why"] == "NO_ROW_IN_SOURCE"


def test_correction_rules_single_zero_and_double_zero():
    lr, v = gs.log_rr(0, 23, 7, 22)               # single zero: +0.5 to every cell
    assert math.isclose(lr, math.log((0.5 / 24) / (7.5 / 23)))
    assert gs.log_rr(0, 15, 0, 16) is None        # double zero: excluded


def test_control_reproduces_and_refuses_a_planted_mismatch():
    ex = {"outcome_rows": [["A 2001", "x", MORT, "10", "100", "20", "100"], ["B 2002", "x", MORT, "5", "50", "5", "50"]],
          "dose": {"a 2001": 10.0, "b 2002": 5.0}}
    pooled, _ = gs.node_pool(ex["outcome_rows"], ex["dose"], 7.5)
    hi = [f"{v:.2f}" for v in pooled["higher"]["rr"]]
    lo = [f"{v:.2f}" for v in pooled["lower"]["rr"]]
    ok = gs.positive_control(ex, {"higher": tuple(hi), "lower": tuple(lo)}, 7.5, "0")
    assert ok["reproduced"]
    bad = gs.positive_control(ex, {"higher": ("0.40", hi[1], hi[2]), "lower": tuple(lo)}, 7.5, "0")
    assert not bad["reproduced"]
    assert not gs.positive_control(ex, {"higher": tuple(hi)}, 7.5, "0.02")["reproduced"]   # tau^2 > 0: not rebuilt


def _tracker(route="NO_ROW"):
    return {"slug": "t", "comparator_pmid": "999", "trials": [
        {"label": "Blum", "route": route, "comparator_row": {}, "blocker": "X"},
        {"label": "Other", "route": "PRIMARY", "g1_countable": True, "in_our_pool": True}]}


def _sec(meta="42402602", reproduced=True):
    return {"slug": "t", "meta_pmid": meta, "meta_doi": "10.1/x", "supplement_sha256": "ab" * 32,
            "positive_control": {"reproduced": reproduced},
            "bindings": [{"label": "Blum", "admitted": True, "source_row_key": "blum 2015",
                          "values": {"events_t": 16, "n_t": 392, "events_c": 13, "n_c": 393}}]}


def _apply(o, s, tmp_path):
    import g1_tracker as gt
    p = tmp_path / "s.json"
    p.write_text(json.dumps(s), encoding="utf-8")
    return gt.apply_secondary_bindings(o, str(p))


def test_hook_binds_no_row_as_secondary_single(tmp_path):
    o = _tracker()
    assert _apply(o, _sec(), tmp_path) == ["Blum"]
    x = o["trials"][0]
    assert x["route"] == "SECONDARY_SINGLE" and x["g1_countable"] and o["k_matched"] == 2
    assert x["agreement_with_comparator_row"] == "NOT_COMPARABLE:NO_COMPARATOR_ROW"


def test_hook_refuses_the_comparator_itself_and_an_unreproduced_meta(tmp_path):
    assert _apply(_tracker(), _sec(meta="999"), tmp_path) == []          # anti-circularity
    assert _apply(_tracker(), _sec(reproduced=False), tmp_path) == []
    assert _apply(_tracker(route="PRIMARY"), _sec(), tmp_path) == []      # never overrides a held route
