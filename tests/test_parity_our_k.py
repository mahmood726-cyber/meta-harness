"""Derived-narrative / stale-panel guard (audit 28). TWO assertions:
  (1) parity.our_k EQUALS the primary pooled k (equality, not <=; a same-scope subset is a different quantity
      that belongs in its own field, never smuggled into our_k).
  (2) SET MEMBERSHIP: a trial the parity reason names as EXCLUDED must NOT be in the pool. The serious half of
      the omega3 defect was naming SU.FOL.OM3 (a POOLED trial) as 'excluded' — a count check misses it."""
import json
import os
import tempfile

from harness.gate import check_parity_our_k


def _rev(tmp, k, our_k, reason="", trials=None, suppressed=False):
    d = os.path.join(tmp, "rv")
    os.makedirs(d, exist_ok=True)
    res = {"suppressed_incompatible": True, "k": k} if suppressed else {"k": k}
    prim = {"primary": True, "result": res, "trials": trials or []}
    rev = {"outcomes": [prim], "reproduction": {"parity": {"our_k": our_k, "reason": reason}}}
    json.dump(rev, open(os.path.join(d, "review.json"), "w", encoding="utf-8"))
    return d


def test_our_k_must_equal_k_not_merely_below():
    with tempfile.TemporaryDirectory() as t:
        # a SUBSET (our_k < k) must now FAIL — equality, not <= (the loosened-test correction)
        assert check_parity_our_k(_rev(t, 4, 2)), "our_k(2) != k(4) must fail under equality"
    with tempfile.TemporaryDirectory() as t:
        assert check_parity_our_k(_rev(t, 7, 8)), "our_k(8) != k(7) must fail"
    with tempfile.TemporaryDirectory() as t:
        assert check_parity_our_k(_rev(t, 7, 7)) == [], "our_k == k passes"


def test_named_excluded_trial_in_pool_fires():
    # PLANT (the SU.FOL.OM3 shape): a trial named EXCLUDED while it is pooled.
    trials = [{"id": "PMID 21115589", "label": "SU.FOL.OM3",
               "source": "SU.FOL.OM3 (PMID 21115589) full text: omega-3 arm ..."}]
    reason = "7 POOLED BY US. 1 FACTORIAL we caught and excluded (SU.FOL.OM3, the B-vitamin binding trap)."
    with tempfile.TemporaryDirectory() as t:
        r = check_parity_our_k(_rev(t, 1, 1, reason=reason, trials=trials))
        assert any("EXCLUDED but it IS in the pooled set" in x for x in r), \
            "must fire when a pooled trial is named as excluded"


def test_correctly_excluded_trial_not_in_pool_passes():
    trials = [{"id": "PMID 21115589", "label": "SU.FOL.OM3", "source": "SU.FOL.OM3 (PMID 21115589) ..."}]
    reason = "1 POOLED BY US. DART design-excluded (open-label)."  # DART is not pooled
    with tempfile.TemporaryDirectory() as t:
        assert check_parity_our_k(_rev(t, 1, 1, reason=reason, trials=trials)) == []


def test_outcome_abbreviation_not_treated_as_trial():
    # POAF/AAD are outcome abbreviations in the source, not trial acronyms — must not false-fire.
    trials = [{"id": "PMID 25172965", "label": "COPPS-2", "source": "COPPS-2 (PMID 25172965): POAF occurred in ..."}]
    reason = "3 POOLED BY US. Some records excluded for POAF-definition differences."
    with tempfile.TemporaryDirectory() as t:
        assert check_parity_our_k(_rev(t, 1, 1, reason=reason, trials=trials)) == [], \
            "an outcome abbreviation named after 'excluded' must not be read as a pooled trial"


def test_suppressed_skipped():
    with tempfile.TemporaryDirectory() as t:
        assert check_parity_our_k(_rev(t, 2, 5, suppressed=True)) == []
