"""The domain algorithms against the RoB 2 FULL GUIDANCE mapping tables (Higgins et al., RoB 2 guidance, 22 Aug 2019:
Table 4 (D1), Table 6 (D2), Table 10 (D3), Table 12 (D4), Table 14 (D5)). Written failing-first after the recorded
codex/agy review of the NI policy (outputs/robgrade/ni_policy_review/). Every row is a table row; a row the reviewers
claimed and the table contradicts is pinned too, so a later "fix" in that direction fails."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from robgrade import rob2_formal as rf  # noqa: E402


def j(dom, **kw):
    return rf.JUDGE[dom]({q.replace("_", "."): {"answer": v} for q, v in kw.items()})[0]


# ---- defects found by the review (codex), confirmed by the tables
def test_PLANT_d2_2_4_ni_with_unbalanced_deviations_is_high():          # Table 6 part 1, last row
    assert j("D2", **{"2_1": "Y", "2_2": "Y", "2_3": "Y", "2_4": "NI", "2_5": "N", "2_6": "Y", "2_7": "NA"}) == "HIGH"


def test_PLANT_d2_2_7_ni_after_inappropriate_analysis_is_high():          # Table 6 part 2: N/PN/NI + Y/PY/NI -> High
    assert j("D2", **{"2_1": "N", "2_2": "N", "2_3": "NA", "2_4": "NA", "2_5": "NA", "2_6": "N", "2_7": "NI"}) == "HIGH"


def test_PLANT_d4_4_1_ni_is_grouped_with_no():                            # Table 12 rows 1-4: 4.1 N/PN/NI
    assert j("D4", **{"4_1": "NI", "4_2": "N", "4_3": "N", "4_4": "NA", "4_5": "NA"}) == "LOW"
    assert j("D4", **{"4_1": "NI", "4_2": "N", "4_3": "Y", "4_4": "N", "4_5": "NA"}) == "LOW"


# ---- rows the review claimed otherwise, pinned to the table
def test_d1_not_random_but_concealed_is_some_concerns():                 # Table 3 'Some concerns' (i.1)+(i.2.1)
    assert j("D1", **{"1_1": "N", "1_2": "Y", "1_3": "N"}) == "SOME_CONCERNS"


def test_d2_deviations_not_affecting_outcome_is_some_concerns():          # Table 6: 2.3 Y/PY, 2.4 N/PN -> Some
    assert j("D2", **{"2_1": "Y", "2_2": "Y", "2_3": "Y", "2_4": "N", "2_5": "NA", "2_6": "Y", "2_7": "NA"}) == "SOME_CONCERNS"


def test_d2_2_7_no_is_some_concerns():                                    # Table 6 part 2: N/PN/NI + N/PN -> Some
    assert j("D2", **{"2_1": "N", "2_2": "N", "2_6": "N", "2_7": "N"}) == "SOME_CONCERNS"


def test_d3_3_4_ni_is_high():                                             # Table 10 last row: 3.4 Y/PY/NI -> High
    assert j("D3", **{"3_1": "N", "3_2": "N", "3_3": "Y", "3_4": "NI"}) == "HIGH"


def test_d4_4_5_ni_is_high():                                             # Table 12 row 4: 4.5 Y/PY/NI -> High
    assert j("D4", **{"4_1": "N", "4_2": "N", "4_3": "NI", "4_4": "NI", "4_5": "NI"}) == "HIGH"


def test_d4_4_2_ni_rows_are_some_concerns():                              # Table 12 rows 5-7
    assert j("D4", **{"4_1": "N", "4_2": "NI", "4_3": "N"}) == "SOME_CONCERNS"
    assert j("D4", **{"4_1": "NI", "4_2": "NI", "4_3": "Y", "4_4": "N"}) == "SOME_CONCERNS"


# ---- applicability (Table 1 / Tables 6, 10, 12): a skipped question is NA, never NI
def test_PLANT_applicable_questions_follow_the_branches():
    ap = lambda dom, **kw: rf.applicable(dom, {q.replace("_", "."): {"answer": v} for q, v in kw.items()})
    assert ap("D3", **{"3_1": "Y"}) == ["3.1"]
    assert ap("D3", **{"3_1": "NI", "3_2": "N", "3_3": "NI"}) == ["3.1", "3.2", "3.3", "3.4"]
    assert ap("D2", **{"2_1": "N", "2_2": "N", "2_6": "Y"}) == ["2.1", "2.2", "2.6"]
    assert ap("D2", **{"2_1": "Y", "2_3": "NI", "2_6": "N"}) == ["2.1", "2.2", "2.3", "2.6", "2.7"]   # 2.3 NI -> 2.4 NA
    assert ap("D2", **{"2_1": "Y", "2_3": "Y", "2_4": "NI", "2_6": "Y"}) == ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6"]
    assert ap("D4", **{"4_1": "N", "4_2": "N", "4_3": "N"}) == ["4.1", "4.2", "4.3"]


def test_PLANT_a_skipped_question_is_never_an_ni_question():
    lab = rf.ni_label("D3", {"3.1": {"answer": "Y"}})
    assert lab["ni_questions"] == [] and lab["ni_driven"] is False


# ---- overall: 'some concerns for MULTIPLE domains' (Table 3 of the BMJ paper) is >= 2
def test_PLANT_two_some_concerns_domains_are_flagged_for_review():
    o = rf.overall({"D1": "SOME_CONCERNS", "D2": "SOME_CONCERNS", "D3": "LOW", "D4": "LOW", "D5": "LOW"})
    assert o["judgement"] == "SOME_CONCERNS" and o["flags"] == ["MULTIPLE_SOME_CONCERNS_FOR_REVIEW"]


def test_PLANT_assessment_marks_a_skipped_unanswered_question_na_not_ni():
    a = lambda v, q: rf.answer(v, how="test", span=f"s {q}", source_sha256="0" * 64)
    o = rf.assessment("PMID 1", "o", {"3.1": a("Y", "3.1"), "2.1": a("N", "2.1"), "2.2": a("N", "2.2"), "2.6": a("Y", "2.6")})
    d3, d2 = o["domains"]["D3"], o["domains"]["D2"]
    assert [d3["answers"][q]["answer"] for q in ("3.2", "3.3", "3.4")] == ["NA", "NA", "NA"]
    assert [d2["answers"][q]["answer"] for q in ("2.3", "2.4", "2.5", "2.7")] == ["NA", "NA", "NA", "NA"]
    assert d3["judgement"] == "LOW" and d2["judgement"] == "LOW"
    assert o["domains"]["D5"]["answers"]["5.1"]["answer"] == "NI"        # asked and unanswered stays NI


def test_PLANT_na_for_skipped_questions_is_judgement_neutral_exhaustively():
    import itertools
    for dom, qs in rf.DOMAINS.items():
        for combo in itertools.product(("Y", "N", "NI"), repeat=len(qs)):
            ans = {q: {"answer": v} for q, v in zip(qs, combo)}
            asked = rf.applicable(dom, ans)
            skipped = {q: ({"answer": "NA"} if q not in asked else a) for q, a in ans.items()}
            assert rf.JUDGE[dom](ans)[0] == rf.JUDGE[dom](skipped)[0], (dom, combo)


def test_PLANT_ni_driven_never_claims_a_lower_judgement_than_resolution_gives_exhaustively():
    import itertools
    for dom, qs in rf.DOMAINS.items():
        for combo in itertools.product(("Y", "N", "NI"), repeat=len(qs)):
            lab = rf.ni_label(dom, {q: {"answer": v} for q, v in zip(qs, combo)})
            assert rf.ORDER[lab["if_ni_resolved_favourably"]] <= rf.ORDER[lab["judgement"]], (dom, combo)
            assert lab["ni_driven"] == (lab["if_ni_resolved_favourably"] != lab["judgement"])
            assert not lab["ni_driven"] or lab["ni_questions"], (dom, combo)       # driven => some asked NI


# ---- round 2 (codex): the response vocabulary at every entry, not only for default-filled answers
def _ra(v, how="reader"):
    return rf.answer(v, how=how, span="s", source_sha256="0" * 64) if v in ("Y", "PY", "PN", "N") else rf.answer(v, how=how)


def test_PLANT_unanswered_asked_3_2_is_stored_as_no_evidence():
    o = rf.assessment("PMID 1", "o", {"3.1": _ra("N"), "3.3": _ra("N")})
    a = o["domains"]["D3"]["answers"]["3.2"]
    assert a["answer"] == "N" and "no evidence" in a["how"]


def test_PLANT_a_reader_ni_on_a_skipped_question_is_na():
    o = rf.assessment("PMID 1", "o", {"3.1": _ra("Y"), "3.3": _ra("NI")})
    assert o["domains"]["D3"]["answers"]["3.3"]["answer"] == "NA"


def test_PLANT_na_on_an_always_asked_question_is_no_information():
    assert j("D1", **{"1_1": "Y", "1_2": "NA", "1_3": "N"}) == "SOME_CONCERNS"        # 1.2 is always asked
    o = rf.assessment("PMID 1", "o", {"1.1": _ra("Y"), "1.2": _ra("NA"), "1.3": _ra("N")})
    assert o["domains"]["D1"]["answers"]["1.2"]["answer"] == "NI" and o["domains"]["D1"]["judgement"] == "SOME_CONCERNS"


def test_PLANT_normalize_answers_is_judgement_neutral_on_admissible_answers_exhaustively():
    # admissible = NA only where the branching skips the question; an NA to an ASKED question is a correction (round 3),
    # tested on its own above, and may raise severity
    import itertools
    for dom, qs in rf.DOMAINS.items():
        for combo in itertools.product(("Y", "N", "NI", "NA"), repeat=len(qs)):
            ans = {q: {"answer": v, "how": "x"} for q, v in zip(qs, combo)}
            if any(v == "NA" and q in rf.applicable(dom, ans) for q, v in zip(qs, combo)):
                continue
            assert rf.JUDGE[dom](ans)[0] == rf.JUDGE[dom](rf.normalize_answers(dom, ans))[0], (dom, combo)


# ---- round 3
def test_d1_not_random_with_imbalance_is_some_concerns_by_default():   # Table 4 row "N/PN/NI Y/PY Y/PY": Some concerns
    assert j("D1", **{"1_1": "N", "1_2": "Y", "1_3": "Y"}) == "SOME_CONCERNS"        # High only as an author's override


def test_PLANT_na_on_an_asked_conditional_question_is_no_information():
    # codex round 3: 2.7 is asked after 2.6 N/PN/NI; NA there is not a valid answer (Table 6 part 2: 2.7 NI -> High)
    o = rf.assessment("PMID 1", "o", {"2.1": _ra("N"), "2.2": _ra("N"), "2.6": _ra("N"), "2.7": _ra("NA")})
    d2 = o["domains"]["D2"]
    assert d2["answers"]["2.7"]["answer"] == "NI" and d2["judgement"] == "HIGH"
    assert d2["ni"]["ni_driven"] is True and d2["ni"]["if_ni_resolved_favourably"] == "SOME_CONCERNS"
    lab = rf.ni_label("D2", {"2.1": {"answer": "N"}, "2.2": {"answer": "N"}, "2.6": {"answer": "N"}, "2.7": {"answer": "NA"}})
    assert lab["judgement"] == "HIGH"                                      # the label sees the same correction


def test_PLANT_overall_ni_is_none_when_a_domain_is_missing():
    assert rf.overall_ni({}) is None


# ---- round 4 (codex): normalisation is a fixpoint
def test_PLANT_normalisation_reaches_a_fixpoint():
    o = rf.assessment("PMID 1", "o", {"2.1": _ra("Y"), "2.2": _ra("Y"), "2.3": _ra("Y"), "2.4": _ra("NA"), "2.5": _ra("NI"),
                                       "2.6": _ra("Y"), "2.7": _ra("NA")})
    d2 = o["domains"]["D2"]
    assert (d2["answers"]["2.4"]["answer"], d2["answers"]["2.5"]["answer"]) == ("NI", "NI")
    assert d2["judgement"] == "HIGH" and d2["ni"]["if_ni_resolved_favourably"] == "SOME_CONCERNS"


def test_PLANT_normalisation_is_idempotent_exhaustively():
    import itertools
    for dom, qs in rf.DOMAINS.items():
        for combo in itertools.product(("Y", "N", "NI", "NA"), repeat=len(qs)):
            once = rf.normalize_answers(dom, {q: {"answer": v, "how": "x"} for q, v in zip(qs, combo)})
            twice = rf.normalize_answers(dom, once)
            assert {q: a["answer"] for q, a in once.items()} == {q: a["answer"] for q, a in twice.items()}, (dom, combo)


# ---- round 5 (codex): every entry point judges and labels the SAME normalised answers
def test_PLANT_domain_object_normalises_before_judging():
    o = rf.domain_object("D2", {"2.1": {"answer": "N"}, "2.2": {"answer": "N"}, "2.6": {"answer": "N"}, "2.7": {"answer": "NA"}})
    assert o["answers"]["2.7"]["answer"] == "NI" and o["judgement"] == "HIGH"
    assert o["ni"]["ni_driven"] is True and o["ni"]["if_ni_resolved_favourably"] == "SOME_CONCERNS"
