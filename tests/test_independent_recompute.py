"""audit/independent_recompute.py is a SECOND implementation: it must never import the harness, it must agree with every
served pooled outcome, and it must be able to disagree (a served number that drifts is refused)."""
import ast
import copy
import importlib.util
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "audit", "independent_recompute.py")
_spec = importlib.util.spec_from_file_location("irc", PATH)
irc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(irc)


def test_it_never_imports_the_harness():
    tree = ast.parse(open(PATH, encoding="utf-8").read())
    mods = [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    mods += [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert not any(m == "harness" or m.startswith("harness.") or "synth" in m for m in mods), mods


def test_every_served_pooled_outcome_agrees():
    rows = irc.run()
    assert rows and all(r["state"] == "AGREE" for r in rows), [r for r in rows if r["state"] != "AGREE"]


def test_PLANT_a_served_estimate_that_drifts_disagrees():
    r = json.load(open(os.path.join(ROOT, "docs", "reviews", "doac-vte-recurrence", "review.json"), encoding="utf-8"))
    o = copy.deepcopy(next(x for x in r["outcomes"] if x.get("primary")))
    assert irc.recompute_outcome(o)["state"] == "AGREE"
    o["result"]["estimate"] = round(o["result"]["estimate"] + 0.001, 4)
    assert irc.recompute_outcome(o)["state"] == "DISAGREE"


def test_PLANT_a_k1_counts_row_is_recomputed_on_its_own_measure():
    o = {"method": "Single included trial that reported this outcome - the estimate is that trial's own effect; ...",
         "result": {"estimate": 0.8596, "ci_low": 0.7606, "ci_high": 0.9716, "scale": "OR"},
         "trials": [{"ai": 482, "n1i": 2104, "ci": 1110, "n2i": 4321}]}
    assert irc.recompute_outcome(o)["state"] == "AGREE"
    o["result"]["scale"] = "RR"      # the same counts read as a risk ratio is a different number: must disagree
    assert irc.recompute_outcome(o)["state"] == "DISAGREE"


def test_PLANT_a_non_finite_input_never_certifies_a_served_number():
    """codex ext-audit-r1 P0: abs(NaN - served) > TOL is False, so NaN agreed with anything."""
    o = {"method": "Single included trial that reported this outcome - the estimate is that trial's own effect",
         "trials": [{"effect": float("nan"), "ci_low": 0.5, "ci_high": 2}],
         "result": {"scale": "RR", "estimate": 999, "ci_low": 0.5, "ci_high": 2}}
    assert irc.recompute_outcome(o)["state"] != "AGREE"


def test_PLANT_an_unsupported_measure_is_not_read_as_a_ratio():
    """codex ext-audit-r1 P0: a risk difference was exponentiated as if it were a log RR."""
    row = {"ai": 20, "n1i": 100, "ci": 10, "n2i": 100}
    o = {"method": "Paule-Mandel HKSJ", "trials": [dict(row), dict(row)], "result": {"scale": "RD", "estimate": 2}}
    assert irc.recompute_outcome(o)["state"] == "NOT_RECOMPUTABLE"


def test_PLANT_not_recomputable_fails_the_gate(monkeypatch):
    """codex ext-audit-r1 P1: an incomplete verification must not exit 0."""
    o = {"method": "Paule-Mandel HKSJ", "trials": [], "result": {"scale": "RR", "estimate": 999}}
    monkeypatch.setattr(irc, "run", lambda root=None: [dict(slug="s", outcome="o", **irc.recompute_outcome(o))])
    assert irc.main([]) == 1


def test_PLANT_codex_r2_measure_mismatch_smd_and_partial_ci_never_agree():
    """codex ext-audit-r2: an OR row under an RR outcome; SMD read as a raw MD; a k=2 interval with one bound served."""
    row = {"ai": 20, "n1i": 100, "ci": 10, "n2i": 100, "measure": "OR"}
    assert irc.recompute_outcome({"method": "Paule-Mandel HKSJ", "trials": [row, row],
                                  "result": {"scale": "RR", "estimate": 2.25}})["state"] != "AGREE"
    md = {"mean1": 2, "mean2": 0, "sd1": 10, "sd2": 10, "nc1": 100, "nc2": 100}
    assert irc.recompute_outcome({"method": "Paule-Mandel HKSJ", "trials": [md, md],
                                  "result": {"scale": "SMD", "estimate": 2.0}})["state"] != "AGREE"
    eff = {"effect": 1.0, "ci_low": 0.5, "ci_high": 2.0}
    assert irc.recompute_outcome({"method": "Paule-Mandel HKSJ", "trials": [eff, eff],
                                  "result": {"scale": "RR", "estimate": 1.0, "ci_low": 999.0, "ci_high": None}})["state"] == "DISAGREE"


def test_PLANT_codex_r3_tuple_kind_impossible_counts_reversed_ci_and_large_units():
    """codex ext-audit-r3: an arm-means row under a ratio outcome; events > arm size; reversed CI bounds; PM on large-unit MDs."""
    md = {"mean1": 1, "mean2": 0, "sd1": 1, "sd2": 1, "nc1": 10, "nc2": 10}
    assert irc.recompute_outcome({"method": "Paule-Mandel HKSJ", "trials": [md, md],
                                  "result": {"scale": "RR", "estimate": 2.7183}})["state"] != "AGREE"
    bad = {"ai": 12, "n1i": 10, "ci": 1, "n2i": 10}
    assert irc.recompute_outcome({"method": "Paule-Mandel HKSJ", "trials": [bad, bad],
                                  "result": {"scale": "RR", "estimate": 12}})["state"] != "AGREE"
    rev = {"effect": 1, "ci_low": 2, "ci_high": 0.5}
    assert irc.recompute_outcome({"method": "Single included trial own effect", "trials": [rev],
                                  "result": {"scale": "RR", "estimate": 1, "ci_low": 2, "ci_high": 0.5}})["state"] != "AGREE"
    assert abs(irc.paule_mandel([-20000, 20000], [1, 1]) - 799999999) < 1.0


def test_PLANT_codex_r4_rate_as_or_hidden_bad_effect_negative_time_and_incomplete_tuple():
    """codex ext-audit-r4: a rate tuple under an OR outcome; a reversed reported CI beside valid counts; negative person-time;
    an incomplete 2x2 (which used to raise and abort the whole run)."""
    rate = {"measure": "OR", "e1i": 20, "t1i": 100, "e2i": 10, "t2i": 100}
    assert irc.recompute_outcome({"method": "Paule-Mandel HKSJ", "trials": [rate, rate],
                                  "result": {"scale": "OR", "estimate": 2}})["state"] != "AGREE"
    both = {"ai": 10, "n1i": 100, "ci": 20, "n2i": 100, "effect": 5, "ci_low": 10, "ci_high": 1}
    assert irc.recompute_outcome({"method": "Single included trial own effect", "trials": [both],
                                  "result": {"scale": "RR", "estimate": 5, "ci_low": 10, "ci_high": 1}})["state"] != "AGREE"
    neg = {"e1i": 20, "t1i": -100, "e2i": 10, "t2i": -100}
    assert irc.recompute_outcome({"method": "Paule-Mandel HKSJ", "trials": [neg, neg],
                                  "result": {"scale": "IRR", "estimate": 2}})["state"] != "AGREE"
    part = {"ai": 1, "n1i": 10, "ci": 1}
    assert irc.recompute_outcome({"method": "Single included trial own effect", "trials": [part],
                                  "result": {"scale": "RR", "estimate": 1, "ci_low": 0.1, "ci_high": 10}})["state"] == "NOT_RECOMPUTABLE"


def test_PLANT_codex_r5_conflicting_labels_fractional_counts_and_k1_overflow():
    row = {"measure": "RR", "scale": "MD", "effect": 2, "ci_low": 1, "ci_high": 3}
    assert irc.recompute_outcome({"method": "Paule-Mandel HKSJ", "trials": [row, row],
                                  "result": {"scale": "RR", "estimate": 7.3891}})["state"] != "AGREE"
    frac = {"ai": 12.5, "n1i": 100, "ci": 25, "n2i": 100}
    assert irc.recompute_outcome({"method": "Paule-Mandel HKSJ", "trials": [frac, frac],
                                  "result": {"scale": "RR", "estimate": 0.5}})["state"] != "AGREE"
    big = {"effect": 1e200, "ci_low": 1e-200, "ci_high": 1e201}
    r = irc.recompute_outcome({"method": "Single included trial own effect", "trials": [big],
                               "result": {"scale": "RR", "estimate": 1e200, "ci_low": 1e-200, "ci_high": 1e201}})
    assert r["state"] == "AGREE", r


def test_PLANT_codex_r6_fractional_rate_events_zero_sd_arm_and_unused_k2_interval():
    r = irc.recompute_outcome({"method": "Paule-Mandel HKSJ",
                               "trials": [{"e1i": 12.5, "t1i": 100, "e2i": 25, "t2i": 100}, {"e1i": 10, "t1i": 100, "e2i": 20, "t2i": 100}],
                               "result": {"scale": "IRR", "estimate": 0.5}})
    assert r["state"] == "NOT_RECOMPUTABLE"
    assert irc.study_y_v({"mean1": 1, "sd1": 0, "nc1": 10, "mean2": 2, "sd2": 1, "nc2": 10}, "MD") == (-1.0, 0.1)
    r = irc.recompute_outcome({"method": "Paule-Mandel HKSJ",
                               "trials": [{"effect": 1e-100, "ci_low": 5e-101, "ci_high": 2e-100},
                                          {"effect": 1e100, "ci_low": 5e99, "ci_high": 2e100}],
                               "result": {"scale": "RR", "estimate": 1.0}})
    assert r["state"] == "AGREE", r
