"""The NI policy (outputs/robgrade/NI_POLICY.md; Mahmood 12 Oct, decision (b)). Written BEFORE the implementation and
run failing first. Every expected value is derived by hand from the RoB 2 algorithms (Sterne et al., BMJ 2019;366:l4898,
Table 1 and the web-appendix algorithms; Cochrane Handbook ch. 8, 8.2.3), never from the code under test.

The policy NEVER changes a judgement (the algorithm's proposal stands; Handbook 8.2.3: reasons are needed to depart
from it, and missing information is not such a reason). It LABELS a judgement NI-driven when resolving the domain's
asked NI answers to Table 1's lower-risk response would lower it: a sensitivity of the output to the missing answers,
not a causal attribution (NI_POLICY P5). 3.2 has no NI option in Table 1: no evidence = N, so it is never resolved."""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from robgrade import ni_policy as nip  # noqa: E402
from robgrade import rob2_formal as rf  # noqa: E402


def _ans(**kw):
    return {q.replace("_", "."): {"answer": v} for q, v in kw.items()}


# ---- Table 1 lower-risk responses, transcribed from the BMJ 2019 table (the source of every counterfactual)
def test_favourable_is_table_1():
    y = {"1.1", "1.2", "2.5", "2.6", "3.1", "3.2", "5.1"}
    assert set(rf.FAVOURABLE) == set(rf.QUESTIONS)
    assert {q for q, v in rf.FAVOURABLE.items() if v == "Y"} == y
    assert all(v == "N" for q, v in rf.FAVOURABLE.items() if q not in y)
    assert rf.NI_NOT_AN_OPTION == {"3.2"}


# ---- domain labels (hand-derived)
def test_PLANT_d1_concealment_ni_is_ni_driven():
    lab = rf.ni_label("D1", _ans(**{"1_1": "Y", "1_2": "NI", "1_3": "N"}))
    assert (lab["judgement"], lab["ni_driven"], lab["if_ni_resolved_favourably"]) == ("SOME_CONCERNS", True, "LOW")
    assert lab["decisive_ni_questions"] == ["1.2"]


def test_PLANT_d1_ni_lifts_high_to_some_only():
    lab = rf.ni_label("D1", _ans(**{"1_1": "Y", "1_2": "NI", "1_3": "Y"}))
    assert (lab["judgement"], lab["ni_driven"], lab["if_ni_resolved_favourably"]) == ("HIGH", True, "SOME_CONCERNS")


def test_PLANT_d1_reported_problem_is_not_ni_driven():
    lab = rf.ni_label("D1", _ans(**{"1_1": "Y", "1_2": "N", "1_3": "NI"}))
    assert (lab["judgement"], lab["ni_driven"]) == ("HIGH", False)
    assert lab["ni_questions"] == ["1.3"] and lab["decisive_ni_questions"] == []


def test_PLANT_ni_with_no_evidence_of_a_problem_is_not_ni_driven():
    # Handbook 8.2.3: where a question checks for a problem, NI is no evidence of it (1.3 NI -> LOW already)
    lab = rf.ni_label("D1", _ans(**{"1_1": "Y", "1_2": "Y", "1_3": "NI"}))
    assert (lab["judgement"], lab["ni_driven"]) == ("LOW", False)


def test_PLANT_3_2_is_never_resolved():
    # defensive: an (invalid) 3.2 NI is read as N and never resolved
    lab = rf.ni_label("D3", _ans(**{"3_1": "N", "3_2": "NI", "3_3": "Y", "3_4": "N"}))
    assert (lab["judgement"], lab["ni_driven"]) == ("SOME_CONCERNS", False)
    assert "3.2" not in lab["ni_questions"]


def test_PLANT_d3_all_ni():
    # 3.2 has no NI option (Table 1): its 'no evidence' is N; 3.4 is asked because 3.3 is NI (Table 10)
    lab = rf.ni_label("D3", _ans(**{"3_1": "NI", "3_2": "N", "3_3": "NI", "3_4": "NI"}))
    assert (lab["judgement"], lab["ni_driven"], lab["if_ni_resolved_favourably"]) == ("HIGH", True, "LOW")
    assert lab["decisive_ni_questions"] == ["3.1", "3.3", "3.4"]


def test_PLANT_d4_unknown_assessor_awareness():
    lab = rf.ni_label("D4", _ans(**{"4_1": "N", "4_2": "N", "4_3": "NI", "4_4": "NI", "4_5": "NI"}))
    assert (lab["judgement"], lab["ni_driven"], lab["if_ni_resolved_favourably"]) == ("HIGH", True, "LOW")


def test_PLANT_d5_no_prespecified_plan_reported():
    lab = rf.ni_label("D5", _ans(**{"5_1": "NI", "5_2": "N", "5_3": "N"}))
    assert (lab["judgement"], lab["ni_driven"], lab["if_ni_resolved_favourably"]) == ("SOME_CONCERNS", True, "LOW")
    lab = rf.ni_label("D5", _ans(**{"5_1": "NI", "5_2": "Y", "5_3": "N"}))
    assert (lab["judgement"], lab["ni_driven"]) == ("HIGH", False)


def test_PLANT_d2_unreported_deviations():
    # a valid configuration (guidance Table 6): 2.3 NI makes 2.4 and 2.5 NA (codex review, 12 Oct)
    lab = rf.ni_label("D2", _ans(**{"2_1": "Y", "2_2": "Y", "2_3": "NI", "2_4": "NA", "2_5": "NA", "2_6": "Y", "2_7": "NA"}))
    assert (lab["judgement"], lab["ni_driven"], lab["if_ni_resolved_favourably"]) == ("SOME_CONCERNS", True, "LOW")


def test_PLANT_an_unanswered_question_counts_as_ni():
    lab = rf.ni_label("D5", {"5.2": {"answer": "N"}, "5.3": {"answer": "N"}})
    assert lab["ni_driven"] is True and lab["ni_questions"] == ["5.1"]


# ---- the assessment object: label added, judgement unchanged
def _a(v, q):
    if v == "NI":
        return rf.answer("NI", how="unanswered")
    return rf.answer(v, how="test", span=f"span for {q}", source_sha256="0" * 64)


def _assess(spec, insufficient=()):
    return rf.assessment("PMID 1", "o", {q: _a(v, q) for q, v in spec.items()}, insufficient_domains=insufficient)


ALL_LOW = {"1.1": "Y", "1.2": "Y", "1.3": "N", "2.1": "N", "2.2": "N", "2.6": "Y", "3.1": "Y", "4.1": "N", "4.2": "N",
           "4.3": "N", "5.1": "Y", "5.2": "N", "5.3": "N"}


def test_PLANT_the_policy_never_changes_a_judgement():
    spec = dict(ALL_LOW, **{"1.2": "NI"})
    o = _assess(spec)
    assert o["domains"]["D1"]["judgement"] == rf.judge_d1(o["domains"]["D1"]["answers"])[0] == "SOME_CONCERNS"
    assert o["overall"]["judgement"] == "SOME_CONCERNS"
    assert o["domains"]["D1"]["ni"]["ni_driven"] is True


def test_PLANT_overall_ni_driven_only_when_ni_decides_it():
    o = _assess(dict(ALL_LOW, **{"1.2": "NI"}))
    assert (o["overall"]["ni"]["ni_driven"], o["overall"]["ni"]["if_ni_resolved_favourably"]) == (True, "LOW")
    o = _assess(dict(ALL_LOW, **{"1.2": "NI", "5.2": "Y"}))              # D5 HIGH from a reported selection
    assert (o["overall"]["judgement"], o["overall"]["ni"]["ni_driven"]) == ("HIGH", False)


def test_PLANT_insufficient_open_source_is_not_labelled():
    o = _assess(ALL_LOW, insufficient=("D3",))
    assert o["domains"]["D3"]["ni"] is None and o["overall"]["ni"] is None


# ---- two-way agreement (pre-registered scoring)
def _p(d, ours, theirs, ni):
    return {"domain": d, "ours": ours, "theirs": theirs, "ni_driven": ni}


def test_PLANT_two_way_agreement():
    pairs = [_p("D1", "LOW", "LOW", False), _p("D1", "SOME_CONCERNS", "LOW", True), _p("D1", "HIGH", "HIGH", True),
             _p("D5", "SOME_CONCERNS", "SOME_CONCERNS", False)]
    t = nip.two_way(pairs)
    assert t["all"]["all"] == {"agree": 3, "N": 4}
    assert t["excluding_ni_driven"]["all"] == {"agree": 2, "N": 2}
    assert t["ni_driven_only"]["all"] == {"agree": 1, "N": 2}
    assert t["all"]["D1"] == {"agree": 2, "N": 3} and t["excluding_ni_driven"]["D1"] == {"agree": 1, "N": 1}


def test_PLANT_two_way_fails_closed_on_an_unlabelled_pair():
    with pytest.raises(ValueError):
        nip.two_way([{"domain": "D1", "ours": "LOW", "theirs": "LOW"}])


# ---- the scoring script's refusals (written after scripts/rob2_ni_score.py, so not failing-first: disclosed)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import rob2_ni_score as sc  # noqa: E402


class _R:
    def __init__(self, rc, out=""):
        self.returncode, self.stdout = rc, out


def _git_mock(fail_when):
    """git, as seen by the scorer: 'deadbeef' is the commit that added the policy (the anchor passes), and any other
    call fails exactly when fail_when(args) is true -- so each test exercises ONE guard."""
    def git(*a):
        if a[0] in ("log", "rev-parse"):
            return _R(0, "deadbeef")
        return _R(1 if fail_when(a) else 0)
    return git


def test_PLANT_score_refuses_a_commit_that_is_not_an_ancestor(monkeypatch):
    monkeypatch.setattr(sc, "_git", _git_mock(lambda a: a[0] == "merge-base"))
    with pytest.raises(SystemExit, match="not an ancestor"):
        sc.check_prereg("deadbeef")


def test_PLANT_score_refuses_a_policy_edited_after_preregistration(monkeypatch):
    monkeypatch.setattr(sc, "_git", _git_mock(lambda a: a[0] == "diff" and a[-1] == "robgrade/rob2_formal.py"))
    with pytest.raises(SystemExit, match="rob2_formal.py"):
        sc.check_prereg("deadbeef")


D1_SOME_NI = {"1.1": {"answer": "Y"}, "1.2": {"answer": "NI"}, "1.3": {"answer": "N"}}      # SOME_CONCERNS, NI-driven


def _rebuild_with(monkeypatch, tmp_path, pairs, test=("1",)):
    (tmp_path / "s.json").write_text(json.dumps({"trials": {"1": {"domains": {"D1": {"answers": D1_SOME_NI}}}}}),
                                     encoding="utf-8")
    monkeypatch.setattr(sc.cal, "OURS", str(tmp_path))
    monkeypatch.setattr(sc.cal, "pairs_for", lambda s: (pairs, [], [], "RoB 2"))
    return sc.rebuild(["s"], set(test))


def _pair(**kw):
    return dict({"slug": "s", "pmid": "1", "domain": "D1", "ours": "SOME_CONCERNS", "theirs": "LOW", "ni_driven": True}, **kw)


def test_PLANT_score_accepts_an_authentic_pair(monkeypatch, tmp_path):
    assert len(_rebuild_with(monkeypatch, tmp_path, [_pair()])[0]) == 1


def test_PLANT_score_refuses_an_edited_label_or_judgement(monkeypatch, tmp_path):
    for bad in (_pair(ni_driven=False), _pair(ours="LOW")):
        with pytest.raises(SystemExit, match="recomputed"):
            _rebuild_with(monkeypatch, tmp_path, [bad])


def test_PLANT_score_refuses_a_non_test_trial(monkeypatch, tmp_path):
    with pytest.raises(SystemExit, match="not a TEST trial"):
        _rebuild_with(monkeypatch, tmp_path, [_pair()], test=("2",))


def test_PLANT_score_refuses_a_duplicate_pair(monkeypatch, tmp_path):
    with pytest.raises(SystemExit, match="duplicate"):
        _rebuild_with(monkeypatch, tmp_path, [_pair(), _pair()])


# ---- round 2 (codex)
def test_PLANT_score_refuses_a_slug_given_twice(monkeypatch, tmp_path):
    (tmp_path / "s.json").write_text(json.dumps({"trials": {"1": {"domains": {"D1": {"answers": D1_SOME_NI}}}}}),
                                     encoding="utf-8")
    monkeypatch.setattr(sc.cal, "OURS", str(tmp_path))
    monkeypatch.setattr(sc.cal, "pairs_for", lambda s: ([_pair(slug=s)], [], [], "RoB 2"))
    with pytest.raises(SystemExit, match="duplicate"):
        sc.rebuild(["s", "s"], {"1"})


def test_PLANT_score_refuses_changed_frozen_inputs(monkeypatch):
    monkeypatch.setattr(sc, "_git", _git_mock(lambda a: a[0] == "diff" and a[-1] == "outputs/robgrade/split.json"))
    with pytest.raises(SystemExit, match="split.json"):
        sc.check_prereg("deadbeef")


def test_PLANT_score_refuses_answers_changed_since_preregistration(monkeypatch, tmp_path):
    frozen = {"trials": {"1": {"domains": {"D1": {"answers": D1_SOME_NI, "judgement": "SOME_CONCERNS"}}}}}
    edited = {"trials": {"1": {"domains": {"D1": {"answers": dict(D1_SOME_NI, **{"1.2": {"answer": "Y"}}),
                                                  "judgement": "LOW"}}}}}
    monkeypatch.setattr(sc, "frozen_object", lambda sha, s: frozen)
    with pytest.raises(SystemExit, match="answers differ"):
        sc.check_answers_frozen("deadbeef", "s", edited)
    sc.check_answers_frozen("deadbeef", "s", frozen)


def test_PLANT_v3_comparison_uses_identical_pairs():
    base = [dict(_pair(slug="s", ours="LOW", theirs="LOW")), dict(_pair(slug="t", ours="HIGH", theirs="LOW"))]
    now = [dict(_pair(slug="s", ours="LOW", theirs="LOW"))]
    c = sc.v3_compare(now, base)
    assert c["v3"] == {"agree": 1, "N": 1} and c["v31"] == {"agree": 1, "N": 1} and c["moved"] == []
    assert c["not_in_baseline"] == 0
    c = sc.v3_compare(now + [_pair(slug="u")], base)
    assert c["not_in_baseline"] == 1


def test_PLANT_report_states_that_result_identity_is_unverified():
    assert "result identity" in sc.DISCLOSURE and "PMID" in sc.DISCLOSURE


# ---- round 3
def test_PLANT_score_refuses_a_trial_dropped_since_preregistration(monkeypatch):
    frozen = {"trials": {"1": {"domains": {"D1": {"answers": D1_SOME_NI, "judgement": "SOME_CONCERNS"}}},
                         "2": {"domains": {"D1": {"answers": D1_SOME_NI, "judgement": "SOME_CONCERNS"}}}}}
    now = {"trials": {"1": frozen["trials"]["1"]}}
    monkeypatch.setattr(sc, "frozen_object", lambda sha, s: frozen)
    with pytest.raises(SystemExit, match="trials differ"):
        sc.check_answers_frozen("deadbeef", "s", now)


def test_PLANT_score_refuses_a_domain_made_insufficient_since_preregistration(monkeypatch):
    frozen = {"trials": {"1": {"domains": {"D1": {"answers": D1_SOME_NI, "judgement": "SOME_CONCERNS"}}}}}
    now = {"trials": {"1": {"domains": {"D1": {"answers": D1_SOME_NI, "judgement": "INSUFFICIENT_OPEN_SOURCE"}}}}}
    monkeypatch.setattr(sc, "frozen_object", lambda sha, s: frozen)
    with pytest.raises(SystemExit, match="eligibility"):
        sc.check_answers_frozen("deadbeef", "s", now)


# ---- round 4 (codex)
def test_PLANT_score_refuses_a_malformed_judgement(monkeypatch):
    frozen = {"trials": {"1": {"domains": {"D1": {"answers": D1_SOME_NI, "judgement": "SOME_CONCERNS"}}}}}
    now = {"trials": {"1": {"domains": {"D1": {"answers": D1_SOME_NI, "judgement": "LOW_typo"}}}}}
    monkeypatch.setattr(sc, "frozen_object", lambda sha, s: frozen)
    with pytest.raises(SystemExit, match="recomputed"):
        sc.check_answers_frozen("deadbeef", "s", now)


def test_PLANT_score_takes_no_topic_subset():
    with pytest.raises(SystemExit, match="all four"):
        sc.main(["deadbeef", "probiotics-aad-prevention"])


def test_PLANT_score_anchor_is_the_commit_that_added_the_policy(monkeypatch):
    def git(*a):
        if a[0] == "log":
            return _R(0, "aaaa\n")                                   # the policy file was first added in aaaa
        if a[0] == "rev-parse":
            return _R(0, a[1] + "\n")
        return _R(0)
    monkeypatch.setattr(sc, "_git", git)
    with pytest.raises(SystemExit, match="not the commit that added"):
        sc.check_prereg("bbbb")
    assert sc.check_prereg("aaaa") == "aaaa"
