"""PLANTS (5 Oct): (1) a trial that a binding hook matched AFTER topic() built the same-trials pairs joins the RESULT
comparison (esketamine TRANSFORM-1 was silently left out); a comparator-keyed confirm binding never joins (it agrees by
construction); (2) a comparator row printing ONE bound only is not a DISAGREE (point compared, interval not), and it is
set aside BY NAME from both pools, never silently."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))

import g1_tracker as gt  # noqa: E402


def _row(label, side, **kw):
    return gt.sm.SecondaryRow(meta_pmid=side, meta_doi="", location={}, source_digest="", provenance=side, trial_label=label,
                              measure=kw.pop("measure", "MD"), outcome_definition="", **kw)


def _arms(mt, mc):
    return {"measure": "MD", "effect": None, "lower": None, "upper": None, "events_t": None, "events_c": None,
            "mean_t": mt, "sd_t": "14", "n_t": 200, "mean_c": mc, "sd_c": "15", "n_c": 100}


def test_a_binding_flipped_trial_joins_the_result_comparison():
    p0 = (gt.as_row(_arms("-19", "-14.6"), "T2"), _row("Popova", "COMPARATOR", effect="-4.40", lower="-7.94", upper="-0.86"))
    o = {"trials": [
        {"label": "T1", "route": "PRIMARY", "g1_countable": True, "in_our_pool": True, "our_value": _arms("-18.9", "-14.8"),
         "reclassified_by": "g1/confirm-unverified primary binding (own tuple)",
         "comparator_row": {"measure": "MD", "effect": "-4.10", "lower": "-6.23", "upper": "-1.97"}},
        {"label": "Tk", "route": "PRIMARY", "g1_countable": True, "in_our_pool": True, "our_value": _arms("-10", "-9"),
         "reclassified_by": "g1/confirm-unverified primary binding",          # comparator-keyed: never compared
         "comparator_row": {"measure": "MD", "effect": "-1.00", "lower": "-3.00", "upper": "1.00"}},
        {"label": "T2", "route": "PRIMARY", "g1_countable": True, "in_our_pool": True, "our_value": {"measure": "MD", "n_t": 1},
         "comparator_row": {"measure": "MD", "effect": "-4.40", "lower": "-7.94", "upper": "-0.86"}}],
        "same_trials": {"state": "ONE_SHARED_TRIAL", "method_basis": "PM"}}
    assert gt.refresh_same_trials_after_bindings(o, [p0], "PM", "37377288") == ["T1"]
    st = o["same_trials"]
    assert st["state"] == "POOLED" and st["k"] == 2 and st["recomputed_after_bindings"] == ["T1"]
    assert gt.refresh_same_trials_after_bindings({"trials": [], "same_trials_per_trial": {}}, [p0], "PM", "x") == []


def test_one_sided_comparator_row_is_not_a_disagreement_and_is_named_not_pooled():
    theirs = _row("EXAMINE", "COMPARATOR", measure="HR", effect="0.96", lower=None, upper="1.16")
    ours = {"measure": "HR", "effect": "0.96", "lower": "0.8209", "upper": "1.1227", "events_t": None}
    assert gt.agreement(ours, theirs) == "AGREE_ON_POINT:COMPARATOR_ONE_SIDED_BOUND"
    assert gt.agreement(dict(ours, effect="0.90"), theirs).startswith("DISAGREE_ON_POINT")
    two = [(gt.as_row(dict(ours, effect=e, lower=lo, upper=hi), lab, "HR"),
            _row(lab, "COMPARATOR", measure="HR", effect=e, lower=lo, upper=hi))
           for lab, e, lo, hi in (("SAVOR", "1.00", "0.89", "1.12"), ("TECOS", "0.99", "0.89", "1.10"))]
    st = gt.same_trials_compare(two + [(gt.as_row(ours, "EXAMINE", "HR"), theirs)], "PM")
    assert st["state"] == "POOLED" and st["k"] == 2 and st["comparator_one_sided_not_pooled"] == ["EXAMINE"]
    assert st["verdict"]["verdict"] == "AGREE"
    # without the fix the one-sided row made the THEIRS side unpoolable and the whole comparison returned no verdict
    assert gt.same_trials_core(two + [(gt.as_row(ours, "EXAMINE", "HR"), theirs)], "PM")["state"] == "THEIRS_ROW_NOT_POOLABLE"
