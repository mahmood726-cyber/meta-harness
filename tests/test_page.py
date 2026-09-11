"""The page must RESOLVE the container-vs-contents defects on the page itself:
 1. a k is never shown without the contributing trials named (Overview names them);
 2. the screening 'N included' count is reconciled with the smaller pooled k, visibly;
 3. a k with no enumerable trials (a transcribed comparator) is labelled un-auditable,
    not left looking like an audited count.
"""
from harness.page import render_page


def _review(k, trials, absent, n_screened_extra=0):
    recs = [{"id": t["id"], "id_type": "pmid", "decision": "include",
             "rule_id": "INCLUDE", "reason": "ok"} for t in trials + absent]
    recs += [{"id": f"x{i}", "id_type": "pmid", "decision": "exclude",
              "rule_id": "X1", "reason": "not an RCT"} for i in range(n_screened_extra)]
    return {
        "slug": "t", "title": "T", "question": "Q", "method_declared": "M",
        "screening": {"records": recs},
        "outcomes": [{
            "name": "Primary", "kind": "efficacy", "primary": True, "estimand": "RR",
            "population": "p", "timepoint": "t", "method": "m",
            "result": {"k": k, "estimate": 0.8, "scale": "RR", "ci_low": 0.7, "ci_high": 0.9,
                       "tau2": 0.0},
            "trials": trials, "declared_absent_trials": absent,
        }],
    }


def test_overview_names_the_pooled_trials():
    r = _review(2, [{"label": "RE-LY", "id": "PMID 1", "ai": 1, "n1i": 10, "ci": 2, "n2i": 10},
                    {"label": "ARISTOTLE", "id": "PMID 2", "ai": 1, "n1i": 10, "ci": 2, "n2i": 10}],
                [])
    html = render_page(r)
    assert "RE-LY" in html and "ARISTOTLE" in html
    # the k appears alongside the names, not as a bare number in the overview
    assert "Trials pooled (k)" in html


def test_reconciliation_when_included_exceeds_pooled():
    # 2 pooled + 1 declared-absent = 3 included; the gap must be stated on the page
    r = _review(2, [{"label": "A", "id": "PMID 1", "ai": 1, "n1i": 10, "ci": 2, "n2i": 10},
                    {"label": "B", "id": "PMID 2", "ai": 1, "n1i": 10, "ci": 2, "n2i": 10}],
                [{"label": "C", "id": "PMID 3", "reason": "no poolable value in abstract"}])
    html = render_page(r)
    assert "Screened-in → pooled" in html
    assert "3 trials met P/I/C/design" in html
    assert "the remaining 1" in html
    # and the per-outcome caption ties k to the named trials
    assert "k = 2" in html


def test_bare_k_without_trials_is_labelled_unauditable():
    # a transcribed comparator: k stated, no trials enumerable
    r = {"slug": "c", "title": "C", "question": "Q", "method_declared": "M",
         "outcomes": [{"name": "Primary", "kind": "efficacy", "primary": True, "estimand": "RR",
                       "result": {"k": 16, "estimate": 0.8, "scale": "RR", "ci_low": 0.7, "ci_high": 0.9},
                       "trials": [], "declared_absent_trials": []}]}
    html = render_page(r)
    assert "cannot be audited on this page" in html


def test_all_pooled_equals_screened_states_so():
    r = _review(2, [{"label": "A", "id": "PMID 1", "ai": 1, "n1i": 10, "ci": 2, "n2i": 10},
                    {"label": "B", "id": "PMID 2", "ai": 1, "n1i": 10, "ci": 2, "n2i": 10}],
                [])
    html = render_page(r)
    assert "all 2 screened-in trials reported this outcome" in html
