"""The error library must not overclaim: every entry that claims a GATE_LIMB must name a gate function
that actually exists, and the coverage math must be self-consistent. This guards against the library
drifting into a marketing list of checks the harness does not really enforce."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import error_library as EL  # noqa: E402
from harness import gate  # noqa: E402


def test_summary_counts_add_up():
    s = EL.summary()
    assert s["total"] == len(EL.LIBRARY)
    assert s["total"] == s.get("GATE_LIMB", 0) + s.get("RENDERED", 0) + s.get("REGRESSION_TEST", 0) + s.get("NOT_CHECKED", 0)


def test_every_gate_limb_entry_names_a_real_gate_function():
    """A GATE_LIMB claim is only honest if the gate module actually has the check. Parse the mechanism
    text for gate.check_* references and require each to exist."""
    import re
    missing = []
    for _id, _label, kind, _univ, mech, _ev in EL.LIBRARY:
        if kind != EL.GATE_LIMB:
            continue
        refs = re.findall(r"check_[a-z0-9_]+", mech)
        assert refs, f"{_id}: GATE_LIMB entry names no check_* function"
        for r in refs:
            if not hasattr(gate, r):
                missing.append(f"{_id}:{r}")
    assert not missing, f"GATE_LIMB entries reference non-existent gate functions: {missing}"


def test_not_checked_entries_are_excluded_from_coverage():
    review = {"outcomes": [{"primary": True, "trials": [{"id": "PMID 1", "source": "x"}]}]}
    n_active, n_checkable, ids = EL.coverage(review, {})
    nc_ids = {i for i, _l, _n in EL.not_checked()}
    assert nc_ids and not (set(ids) & nc_ids), "a NOT_CHECKED id must never count as coverage"
    assert n_checkable == len([e for e in EL.LIBRARY if e[2] != EL.NOT_CHECKED])
    assert 0 < n_active <= n_checkable


def test_pooled_verified_limb_refuses_an_unverified_number():
    """The ME-17 gate limb (check_pooled_verified) must REFUSE a page pooling a not-yet-verified number
    and PASS one where all pooled numbers are verified. This limb is new, so a planted not-yet trial
    that refuses here would have PASSED before it existed — it fires on the defect it guards."""
    import json as _json, os as _os, tempfile
    d = tempfile.mkdtemp(prefix="mh-verif-")
    # a pooled trial that was NOT located in source
    rev_bad = {"outcomes": [{"name": "Primary", "primary": True, "result": {"k": 1},
                             "trials": [{"id": "PMID 1", "verified": "not-yet"}]}]}
    _json.dump(rev_bad, open(_os.path.join(d, "review.json"), "w", encoding="utf-8"))
    reasons = gate.check_pooled_verified(d)
    assert reasons and "not verified" in reasons[0]
    # all-verified passes
    rev_ok = {"outcomes": [{"name": "Primary", "primary": True, "result": {"k": 1},
                            "trials": [{"id": "PMID 1", "verified": "verified"}]}]}
    _json.dump(rev_ok, open(_os.path.join(d, "review.json"), "w", encoding="utf-8"))
    assert gate.check_pooled_verified(d) == []


def test_pivotal_limb_active_only_when_pivotals_declared():
    review = {"outcomes": [{"primary": True, "trials": [{"id": "PMID 1", "source": "x"}]}]}
    _, _, without = EL.coverage(review, {})
    _, _, withp = EL.coverage(review, {"pivotal_trials": ["12345"]})
    assert "ME-06" not in without and "ME-06" in withp


def test_no_double_counted_trial_limb_refuses_a_repeated_trial():
    """ME-25: a trial pooled twice within one outcome (shared-control double-count) must REFUSE; a
    normal pool (distinct ids) passes. This limb is new, so the planted duplicate refuses where it
    would have passed before it existed."""
    import json as _json, os as _os, tempfile
    d = tempfile.mkdtemp(prefix="mh-dc-")
    dup = {"outcomes": [{"name": "Primary", "primary": True, "result": {"k": 2},
                         "trials": [{"id": "PMID 1", "verified": "verified"},
                                    {"id": "PMID 1", "verified": "verified"}]}]}
    _json.dump(dup, open(_os.path.join(d, "review.json"), "w", encoding="utf-8"))
    r = gate.check_no_double_counted_trial(d)
    assert r and "more than once" in r[0]
    ok = {"outcomes": [{"name": "Primary", "primary": True, "result": {"k": 2},
                        "trials": [{"id": "PMID 1"}, {"id": "PMID 2"}]}]}
    _json.dump(ok, open(_os.path.join(d, "review.json"), "w", encoding="utf-8"))
    assert gate.check_no_double_counted_trial(d) == []
