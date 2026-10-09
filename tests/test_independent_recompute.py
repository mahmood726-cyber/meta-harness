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
