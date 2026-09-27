"""A refused pool is never COMPUTED (release-captain finding, 2026-09-25).

The finding: a pooling contract computed the log BEFORE pool_measure_guard could veto it -- the guard's refusal then only discarded a
number that had already been derived from log(HR) mixed with log(RR). pool_guarded() is now the only route to pool() for a verdict.

Two checks, both of which fire on the pre-fix code:
  1. STRUCTURAL: an AST walk of scripts/verify_bundle.py; every call to pool() must sit inside pool_guarded() or
     _plant_expected_pool() (a --corrupt limb's model of a producer). Pre-fix, run() called pool() directly behind an `if`, and a
     pooling contract that calls pool() and consults the guard afterwards is exactly the shape this refuses -- whatever it is named.
  2. RUNTIME: pool() is replaced by a sentinel that raises; every plant whose pool must be refused is then run through the real
     run(). If any path computes a refused pool, the sentinel raises and the test fails; the refusal codes must still be reported."""
import ast
import importlib.util
import os
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFIER = os.path.join(ROOT, "scripts", "verify_bundle.py")
SLUG = "glp1-ra-mace-t2d"
ALLOWED = {"pool_guarded", "_plant_expected_pool"}
PRE_FIX = "d587d9aa75707020271460234f63aa1b93f854d6"      # oc/V1-READY-p10-p11: the guard ran, but pool() was called directly


def direct_pool_calls(src):
    tree = ast.parse(src)
    bad = []

    class V(ast.NodeVisitor):
        def __init__(self):
            self.stack = []

        def visit_FunctionDef(self, node):
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id == "pool" and not (set(self.stack) & ALLOWED):
                bad.append((node.lineno, self.stack[-1] if self.stack else "<module>"))
            self.generic_visit(node)
    V().visit(tree)
    return bad


def test_pool_is_reachable_only_through_the_guard():
    assert direct_pool_calls(open(VERIFIER, encoding="utf-8").read()) == []


def test_the_structural_check_fires_on_the_pre_fix_verifier():
    p = subprocess.run(["git", "show", f"{PRE_FIX}:scripts/verify_bundle.py"], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL)
    if p.returncode != 0:
        pytest.skip(f"{PRE_FIX[:8]} not in this clone's history -- NOT a pass")
    bad = direct_pool_calls(p.stdout.decode("utf-8"))
    assert {fn for _, fn in bad} >= {"run"}, bad          # the verdict path called pool() directly
    # and the shape the release captain found: a contract that pools, THEN asks the guard -- refused whatever it is named
    planted = "def check_pool_contract(inputs, rows, scale):\n    got = pool(inputs)\n    mg = pool_measure_guard(inputs, rows, scale)\n    return None if mg['refused'] else got\n"
    assert direct_pool_calls(planted) == [(2, "check_pool_contract")]


def _load():
    spec = importlib.util.spec_from_file_location("vb_under_test", VERIFIER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("limb", ["estimator_label_rr", "measure_unidentified", "pool_input_reciprocal", "estimator_genuine_rr_permitted",
                                  "estimator_owner_methods"])
def test_a_refused_pool_is_never_computed(limb):
    vb = _load()
    real = vb.pool
    import sys

    def sentinel(inputs):
        if sys._getframe(1).f_code.co_name == "_plant_expected_pool":   # the limb's model of a producer, not a verdict
            return real(inputs)
        raise AssertionError(f"pool() was reached for a pool the guard refuses ({limb})")
    vb.pool = sentinel
    rep = vb.run(vb.Store(os.path.join(ROOT, "docs"), None), SLUG, ("27295427", limb))
    assert rep["pool"]["recomputed"] is None and rep["pool"]["refused_before_logs"], rep["pool"]
    assert rep["pool_measure_guard"]["refused"] is True


def test_the_canonical_pool_is_still_computed_and_reproduced():
    vb = _load()
    rep = vb.run(vb.Store(os.path.join(ROOT, "docs"), None), SLUG, None)
    assert rep["verdict"] == "PASS" and rep["pool"]["reproduced_to_1e-9"] is True and rep["pool"]["refused_before_logs"] is None
