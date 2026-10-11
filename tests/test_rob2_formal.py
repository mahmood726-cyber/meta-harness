"""Plants for the formal RoB 2 algorithms (robgrade/rob2_formal.py): each branch of each domain on constructed answers
whose judgement the RoB 2 guidance fixes, and the rules that keep a missing answer from reading as a favourable one."""
import pytest

from robgrade import rob2_formal as rf

S = "a" * 64


def A(v):
    return rf.answer(v, how="plant", span="span" if v in ("Y", "PY", "PN", "N") else None,
                     source_sha256=S if v in ("Y", "PY", "PN", "N") else None)


def ans(**kw):
    return {k.replace("_", "."): A(v) for k, v in kw.items()}


@pytest.mark.parametrize("kw,want", [
    (dict(q1_1="Y", q1_2="Y", q1_3="N"), rf.LOW),
    (dict(q1_1="NI", q1_2="PY", q1_3="NI"), rf.LOW),
    (dict(q1_1="Y", q1_2="N", q1_3="N"), rf.HIGH),
    (dict(q1_1="Y", q1_2="NI", q1_3="N"), rf.SOME),
    (dict(q1_1="Y", q1_2="NI", q1_3="Y"), rf.HIGH),
    (dict(q1_1="Y", q1_2="Y", q1_3="PY"), rf.SOME),
    (dict(q1_1="PN", q1_2="Y", q1_3="N"), rf.SOME),
])
def test_d1_branches(kw, want):
    a = {k[1:].replace("_", "."): A(v) for k, v in kw.items()}
    assert rf.judge_d1(a)[0] == want


def test_d2_blinded_itt_is_low_open_label_without_information_is_some_concerns():
    blinded = {"2.1": A("N"), "2.2": A("N"), "2.6": A("Y")}
    assert rf.judge_d2(blinded)[0] == rf.LOW
    open_label = {"2.1": A("Y"), "2.2": A("Y"), "2.3": A("NI"), "2.6": A("Y")}
    assert rf.judge_d2(open_label)[0] == rf.SOME
    unbalanced = {"2.1": A("Y"), "2.2": A("Y"), "2.3": A("Y"), "2.4": A("Y"), "2.5": A("N"), "2.6": A("Y")}
    assert rf.judge_d2(unbalanced)[0] == rf.HIGH
    per_protocol_impact = {"2.1": A("N"), "2.2": A("N"), "2.6": A("N"), "2.7": A("Y")}
    assert rf.judge_d2(per_protocol_impact)[0] == rf.HIGH


def test_d3_branches():
    assert rf.judge_d3({"3.1": A("Y")})[0] == rf.LOW
    assert rf.judge_d3({"3.1": A("N"), "3.2": A("Y")})[0] == rf.LOW
    assert rf.judge_d3({"3.1": A("N"), "3.2": A("N"), "3.3": A("N")})[0] == rf.LOW
    assert rf.judge_d3({"3.1": A("N"), "3.2": A("N"), "3.3": A("Y"), "3.4": A("N")})[0] == rf.SOME
    assert rf.judge_d3({"3.1": A("N"), "3.2": A("N"), "3.3": A("Y"), "3.4": A("PY")})[0] == rf.HIGH


def test_d4_branches():
    assert rf.judge_d4({"4.1": A("N"), "4.2": A("N"), "4.3": A("N")})[0] == rf.LOW
    assert rf.judge_d4({"4.1": A("Y")})[0] == rf.HIGH
    assert rf.judge_d4({"4.1": A("N"), "4.2": A("NI"), "4.3": A("N")})[0] == rf.SOME
    assert rf.judge_d4({"4.1": A("N"), "4.2": A("N"), "4.3": A("Y"), "4.4": A("N")})[0] == rf.LOW
    assert rf.judge_d4({"4.1": A("N"), "4.2": A("N"), "4.3": A("Y"), "4.4": A("Y"), "4.5": A("N")})[0] == rf.SOME
    assert rf.judge_d4({"4.1": A("N"), "4.2": A("N"), "4.3": A("Y"), "4.4": A("Y"), "4.5": A("Y")})[0] == rf.HIGH


def test_d5_branches():
    assert rf.judge_d5({"5.1": A("Y"), "5.2": A("N"), "5.3": A("N")})[0] == rf.LOW
    assert rf.judge_d5({"5.1": A("Y"), "5.2": A("Y"), "5.3": A("N")})[0] == rf.HIGH
    assert rf.judge_d5({"5.1": A("NI"), "5.2": A("N"), "5.3": A("N")})[0] == rf.SOME
    assert rf.judge_d5({"5.1": A("Y"), "5.2": A("NI"), "5.3": A("N")})[0] == rf.SOME


def test_PLANT_an_unanswered_question_is_no_information_never_favourable():
    # D1 with only 1.1 answered: 1.2 missing must read NI -> SOME_CONCERNS, never LOW
    assert rf.judge_d1({"1.1": A("Y")})[0] == rf.SOME
    # D5 with nothing answered is not LOW
    assert rf.judge_d5({})[0] == rf.SOME


def test_PLANT_a_yes_or_no_answer_without_a_source_span_is_refused():
    with pytest.raises(ValueError):
        rf.answer("Y", how="model", span=None, source_sha256=None)
    with pytest.raises(ValueError):
        rf.answer("PN", how="regex", span="text", source_sha256=None)
    assert rf.answer("NI", how="model")["answer"] == "NI"


def test_overall_and_insufficient_domain():
    low = {d: rf.LOW for d in rf.DOMAINS}
    assert rf.overall(low)["judgement"] == rf.LOW
    assert rf.overall(dict(low, D3=rf.HIGH))["judgement"] == rf.HIGH
    three = dict(low, D1=rf.SOME, D3=rf.SOME, D5=rf.SOME)
    o = rf.overall(three)
    assert o["judgement"] == rf.SOME and o["flags"] == ["MULTIPLE_SOME_CONCERNS_FOR_REVIEW"]
    # PLANT: a domain without open source makes the overall NOT_ESTABLISHED, not the worst of the others
    o = rf.overall(dict(low, D2=rf.INSUFFICIENT))
    assert o["judgement"] == "NOT_ESTABLISHED" and o["missing_domains"] == ["D2"]


def test_assessment_object_is_hashed_and_complete():
    obj = rf.assessment("PMID 1", "MACE", {"1.1": A("Y"), "1.2": A("Y"), "1.3": A("N")}, insufficient_domains=("D4",))
    assert set(obj["domains"]) == set(rf.DOMAINS)
    assert obj["domains"]["D1"]["judgement"] == rf.LOW
    assert obj["domains"]["D4"]["judgement"] == rf.INSUFFICIENT
    assert obj["overall"]["judgement"] == "NOT_ESTABLISHED"
    assert len(obj["sha256"]) == 64
