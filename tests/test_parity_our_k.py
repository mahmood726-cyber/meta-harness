"""Derived-narrative / stale-panel guard (audit 28): parity.our_k must not EXCEED the primary pooled k
(you cannot pool more than you pooled). A same-scope subset (our_k < k) is allowed; a suppressed primary is
skipped. omega3/colchicine-postop/colchicine-recurrent parity narratives claimed more pooled than the live
pool (naming declared-absent trials as pooled) — this catches that."""
import json
import os
import tempfile

from harness.gate import check_parity_our_k


def _rev(tmp, k, our_k, suppressed=False):
    d = os.path.join(tmp, "rv")
    os.makedirs(d, exist_ok=True)
    res = {"k": k}
    if suppressed:
        res = {"suppressed_incompatible": True, "k": k}
    rev = {"outcomes": [{"primary": True, "result": res}],
           "reproduction": {"parity": {"our_k": our_k}}}
    json.dump(rev, open(os.path.join(d, "review.json"), "w", encoding="utf-8"))
    return d


def test_our_k_exceeding_k_fails():
    with tempfile.TemporaryDirectory() as t:
        assert check_parity_our_k(_rev(t, 7, 8)), "our_k(8) > k(7) must fail (claims more pooled than pooled)"


def test_subset_our_k_below_k_passes():
    with tempfile.TemporaryDirectory() as t:
        assert check_parity_our_k(_rev(t, 4, 2)) == [], "our_k(2) < k(4) is a legitimate same-scope subset"


def test_equal_passes():
    with tempfile.TemporaryDirectory() as t:
        assert check_parity_our_k(_rev(t, 7, 7)) == []


def test_suppressed_skipped():
    with tempfile.TemporaryDirectory() as t:
        assert check_parity_our_k(_rev(t, 2, 5, suppressed=True)) == []
