"""Plant: a comparator screen read newest-first may stop early, but the pick stands only when no unread candidate could
outrank it -- every unread candidate strictly older (T2) and the pick at the best T1. Otherwise INCOMPLETE_READ refuses;
an unread candidate is never counted as a failed one."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_comparator_select as cs  # noqa: E402

RULE = {"criteria": [{"id": "C1"}], "tie_breaks": [{"id": "T1_ESTIMAND_MATCH"}, {"id": "T2_MOST_RECENT"},
                                                   {"id": "T3_LARGEST_K"}]}


def c(pmid, t1, t2, ok=True, read=True):
    return {"pmid": pmid, "criteria": {"C1": {"verdict": "PASS" if ok else "UNCLEAR"}},
            "tie_breaks": {"T1_ESTIMAND_MATCH": t1, "T2_MOST_RECENT": t2, "T3_LARGEST_K": 5},
            **({} if read else {"read": "NOT_READ_EARLY_STOP"})}


def test_complete_read_needs_no_check():
    pick, _ = cs.select(RULE, [c("1", 1, 202401)])
    assert cs.unread_problem(RULE, [c("1", 1, 202401)], pick) is None


def test_unread_strictly_older_than_a_T1_pick_is_fine():
    cands = [c("1", 1, 202401), c("2", 1, 202312, ok=False, read=False)]
    pick, _ = cs.select(RULE, cands)
    assert pick["pmid"] == "1" and cs.unread_problem(RULE, cands, pick) is None


def test_PLANT_unread_same_month_or_newer_refuses():
    cands = [c("1", 1, 202401), c("2", 1, 202401, ok=False, read=False)]      # same month: T3 could still decide
    assert "INCOMPLETE_READ" in cs.unread_problem(RULE, cands, cs.select(RULE, cands)[0])


def test_PLANT_a_pick_without_the_best_T1_refuses_while_anything_is_unread():
    cands = [c("1", 0, 202401), c("2", 1, 201001, ok=False, read=False)]      # an older T1=1 candidate would win
    assert "INCOMPLETE_READ" in cs.unread_problem(RULE, cands, cs.select(RULE, cands)[0])


def test_PLANT_no_pick_with_unread_candidates_is_incomplete_not_none_achievable():
    cands = [c("1", 1, 202401, ok=False), c("2", 1, 202001, ok=False, read=False)]
    assert cs.select(RULE, cands)[0] is None
    assert "INCOMPLETE_READ" in cs.unread_problem(RULE, cands, None)


def test_read_limit_reads_r0_first_then_the_newest(monkeypatch):
    import g1_swap as g
    monkeypatch.setattr(g, "protocol", lambda s: {"current_comparator": "CUR"})
    pub = {"CUR": "2015 Jan", "A": "2024 Mar", "B": "2023 Dec", "C": "2025 Jan"}
    items = [{"slug": "t", "pmid": p, "key": f"swapscreen::t::{p}"} for p in pub]
    cands_all = {"t": ({p: {"pubdate": d} for p, d in pub.items()}, 4)}
    keep, unread = g.read_limit(items, cands_all, "r0")
    assert [i["pmid"] for i in keep] == ["CUR"] and unread == {"swapscreen::t::A", "swapscreen::t::B", "swapscreen::t::C"}
    keep, unread = g.read_limit(items, cands_all, "2")
    assert [i["pmid"] for i in keep] == ["CUR", "C", "A"] and unread == {"swapscreen::t::B"}
    keep, unread = g.read_limit(items, cands_all, None)
    assert len(keep) == 4 and unread == set()
