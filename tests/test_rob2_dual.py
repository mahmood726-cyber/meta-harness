"""Plants for the recorded dual RoB 2 reading (scripts/rob2_dual.py), offline: quote verification, the D8 prompt gate,
agreement, typed precedence, and INSUFFICIENT_OPEN_SOURCE."""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import rob2_dual as rd  # noqa: E402
from robgrade import rob2_formal as rf  # noqa: E402
from robgrade import rob2_typed as rt  # noqa: E402

ABSTRACT = "In this double-blind trial, 600 patients were randomly assigned. Allocation was by a central web system."
FULL_CLOSED = "Randomisation was computer generated in permuted blocks of four, stratified by centre."


def _item(full_open=False, abstract=ABSTRACT, full=FULL_CLOSED):
    srcs = []
    if abstract:
        srcs.append({"id": "abstract:PMID 9", "kind": "abstract", "pmid": "9", "text": abstract, "sha256": rt.sha(abstract),
                     "open_for_prompt": True, "licence": "PubMed abstract"})
    if full:
        srcs.append({"id": "fulltext:PMID 9", "kind": "fulltext", "pmid": "9", "text": full, "sha256": rt.sha(full),
                     "open_for_prompt": full_open, "licence": "CC" if full_open else "NOT_OPEN"})
    return {"slug": "t", "pmid": "9", "nct": None, "outcome": "MACE", "sources": srcs, "key": "t::9::MACE"}


def _reading(**ans):
    return {"answers": [{"qid": q.lstrip("q").replace("_", "."), "answer": a, "quote": quote, "source_id": sid, "rationale": ""}
                        for q, (a, quote, sid) in ans.items()], "notes": ""}


def test_PLANT_a_quote_not_in_the_named_source_becomes_NI():
    it = _item()
    r = _reading(q1_2=("Y", "Allocation was by a central web system.", "abstract:PMID 9"),
                 q1_1=("Y", "randomisation by computer in blocks of six", "abstract:PMID 9"))
    v = rd.verify_answers(r, it)
    assert v["1.2"]["answer"] == "Y" and v["1.2"]["source_sha256"] == rt.sha(ABSTRACT)
    assert v["1.1"]["answer"] == "NI" and v["1.1"]["dropped"]["why"] == "QUOTE_NOT_FOUND_IN_NAMED_OPEN_SOURCE"


def test_PLANT_a_quote_from_a_closed_full_text_is_not_an_answer():
    it = _item(full_open=False)
    r = _reading(q1_1=("Y", "computer generated in permuted blocks", "fulltext:PMID 9"))
    assert rd.verify_answers(r, it)["1.1"]["answer"] == "NI"


def test_PLANT_D8_a_closed_full_text_never_enters_the_prompt():
    p = rd.prompt_bytes(_item(full_open=False)).decode("utf-8")
    assert FULL_CLOSED not in p and ABSTRACT in p
    p2 = rd.prompt_bytes(_item(full_open=True)).decode("utf-8")
    assert FULL_CLOSED in p2
    bad = _item(full_open=True)
    bad["sources"][1]["licence"] = "NOT_OPEN"                  # marked open but not CC: refused, not sent
    with pytest.raises(rd.D8Refused):
        rd.prompt_bytes(bad)


def test_agreement_takes_the_less_certain_answer_and_detects_disagreement():
    q = "1.2"
    a = {q: {"answer": "Y", "quote": "x", "source_id": "s", "source_sha256": "h"}}
    b = {q: {"answer": "PY", "quote": "y", "source_id": "s", "source_sha256": "h"}}
    agreed, dis = rd.agree(a, b)
    assert agreed[q]["answer"] == "PY" and q not in dis
    agreed, dis = rd.agree(a, {q: {"answer": "PN", "quote": "z", "source_id": "s", "source_sha256": "h"}})
    assert q in dis and q not in agreed
    agreed, dis = rd.agree(a, {})                              # one reader silent on it: NI v Y is a disagreement
    assert q in dis


def test_typed_answers_take_precedence_and_insufficient_open_source():
    it = _item(abstract=None, full_open=False)
    typed, conflicts = rt.typed_answers(it["sources"])
    assert typed["1.1"]["answer"] == "Y" and "D8 allows regex" in typed["1.1"]["note"]
    obj = rd.assemble(it, typed, conflicts, {}, {}, {})
    assert obj["domains"]["D1"]["answers"]["1.1"]["how"] == "typed-regex"
    # D3, D4 have no answer at all and the only full text is closed: INSUFFICIENT_OPEN_SOURCE, overall NOT_ESTABLISHED
    assert obj["domains"]["D3"]["judgement"] == rf.INSUFFICIENT and obj["domains"]["D4"]["judgement"] == rf.INSUFFICIENT
    assert obj["overall"]["judgement"] == "NOT_ESTABLISHED"
    # D1 has a typed answer: it is judged (1.2 NI -> SOME_CONCERNS), not insufficient
    assert obj["domains"]["D1"]["judgement"] == rf.SOME


def test_PLANT_a_span_from_a_non_cc_full_text_is_never_published():
    it = _item(abstract=None, full_open=False)
    typed, conflicts = rt.typed_answers(it["sources"])
    obj = rd.assemble(it, typed, conflicts, {}, {}, {})
    span = obj["domains"]["D1"]["answers"]["1.1"]["span"]
    assert span and span in FULL_CLOSED
    assert rd.redact_closed_spans(obj, it) >= 1
    a = obj["domains"]["D1"]["answers"]["1.1"]
    assert a["span"] is None and a["span_redacted"]["span_sha256"] == rt.sha(span)
    assert FULL_CLOSED[a["span_redacted"]["start"]:a["span_redacted"]["start"] + a["span_redacted"]["length"]] == span
    assert FULL_CLOSED not in json.dumps(obj) and span not in json.dumps(obj)
    # a CC full text's span is kept
    it2 = _item(abstract=None, full_open=True)
    typed2, c2 = rt.typed_answers(it2["sources"])
    obj2 = rd.assemble(it2, typed2, c2, {}, {}, {})
    assert rd.redact_closed_spans(obj2, it2) == 0


def test_without_a_closed_full_text_an_unanswered_domain_is_judged_on_NI():
    it = _item(full=None)
    obj = rd.assemble(it, {}, [], {}, {}, {})
    assert obj["domains"]["D3"]["judgement"] in (rf.SOME, rf.HIGH, rf.LOW)
    assert all(o["judgement"] != rf.INSUFFICIENT for o in obj["domains"].values())
