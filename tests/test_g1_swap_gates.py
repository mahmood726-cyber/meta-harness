"""Plants (codex binding-v8-fe3ed2a7, reproduced on the binding branch): the swap gates validated a pooled estimate /
bound by SUBSTRING ('0.8' inside '0.85'), never checked k against the quote (999 vs '12 trials'), and accepted an
all-whitespace quote (it folds to '', contained in every text)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_swap as sw  # noqa: E402

Q = "RR 0.85 (95% CI 0.70-1.03); 12 trials."


def _p(**kw):
    p = {"measure": "RR", "estimate": "0.85", "lower": "0.70", "upper": "1.03", "k": 12, "quote": Q}
    p.update(kw)
    return p


def test_a_substring_value_is_refused():
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p(estimate="0.8", upper="1.0")}, Q)
    assert pooled is None and k is None


def test_an_unprinted_k_is_refused():
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p(k=999)}, Q)
    assert pooled is None and k is None


def test_the_printed_claim_stands():
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p()}, Q)
    assert pooled is not None and k == 12


def test_a_whitespace_quote_supports_nothing():
    out, _, _ = sw.gate_screen({"criteria": {"C2": {"verdict": "PASS", "quote": "   "}}, "pooled": {}}, Q)
    assert out["C2"]["verdict"] == "UNCLEAR"
