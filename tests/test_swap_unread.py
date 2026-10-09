"""scripts/g1_swap_unread.py: the never-read C1-PASS swap candidates (sglt2-ckd 39) get g1_swap's own stage A; the codex
ceiling follows the 8 Oct dispatch, and no call starts below 5 GB free disk."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_swap_unread as U  # noqa: E402


def test_the_codex_ceiling_follows_the_dispatch():
    U._LAST_ERR[0] = 0.0
    assert U.level(ram=8, disk=20, now=10_000) == 8
    assert U.level(ram=4, disk=20, now=10_000) == 5
    assert U.level(ram=8, disk=7, now=10_000) == 5
    assert U.level(ram=8, disk=4.9, now=10_000) == 0               # the stop line: no new call
    U._LAST_ERR[0] = 9_800.0
    assert U.level(ram=8, disk=20, now=10_000) == 2                 # an error in the last 10 minutes
    U._LAST_ERR[0] = 0.0


def test_only_never_read_c1_pass_candidates_with_no_fail_are_taken():
    sel = {"per_candidate": [
        {"pmid": "1", "verdicts": {"C1_OPEN_LICENCE": "PASS", "C2_RCT_ONLY": "UNCLEAR"}},
        {"pmid": "2", "verdicts": {"C1_OPEN_LICENCE": "PASS", "C5_OUTCOME_AND_ESTIMAND": "FAIL"}},
        {"pmid": "3", "verdicts": {"C1_OPEN_LICENCE": "FAIL", "C2_RCT_ONLY": "UNCLEAR"}}]}
    assert [x["pmid"] for x in U.unread(sel)] == ["1"]


def test_a_stage_a_fail_counts_only_with_its_quote_verbatim_in_the_abstract():
    import g1_swap as sw
    text = "SGLT2 inhibitors and serum electrolytes in type 2 diabetes. We pooled observational cohorts."
    claim = {"criteria": {"C2_RCT_ONLY": {"verdict": "FAIL", "quote": "We pooled observational cohorts."},
                          "C3_POPULATION": {"verdict": "FAIL", "quote": "a sentence the abstract never says"},
                          "C4_INTERVENTION_VS_COMPARATOR": {"verdict": "UNCLEAR", "quote": None},
                          "C5_OUTCOME_AND_ESTIMAND": {"verdict": "PASS", "quote": None}}}
    crit, _p, _k = sw.gate_screen(claim, text)
    assert crit["C2_RCT_ONLY"]["verdict"] == "FAIL"
    assert crit["C3_POPULATION"]["verdict"] == "UNCLEAR"            # an unquoted FAIL excludes nothing
    assert crit["C5_OUTCOME_AND_ESTIMAND"]["verdict"] == "UNCLEAR"  # a PASS with no quote counts for nothing
