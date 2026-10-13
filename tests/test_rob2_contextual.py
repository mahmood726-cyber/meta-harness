"""Contextual 'probably' answers (outputs/robgrade/CONTEXTUAL_POLICY.md; Mahmood 12 Oct, item 3). Written BEFORE
robgrade/contextual.py and run failing first. The rule: only an asked NI question may change, only to PY/PN, only with a
verbatim context quote from an open source, only when both blind readers agree or the adjudicator decides; it is
stored and shown as contextual, never silently; NI stays where there is no context."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from robgrade import contextual as cx  # noqa: E402
from robgrade import rob2_formal as rf  # noqa: E402

SRC = {"id": "abstract:PMID 1", "kind": "abstract", "text": "A multicentre trial coordinated by the national clinical "
       "trials unit, with central web-based randomisation of 4000 patients.", "sha256": "a" * 64, "open_for_prompt": True}
QUOTE = "central web-based randomisation"


def _ans(v, q):
    return rf.answer(v, how="t", span=f"s {q}", source_sha256="0" * 64) if v in ("Y", "PY", "PN", "N") else rf.answer(v, how="t")


def _obj(spec, insufficient=()):
    return rf.assessment("PMID 1", "o", {q: _ans(v, q) for q, v in spec.items()}, insufficient_domains=insufficient)


BASE = {"1.1": "Y", "1.2": "NI", "1.3": "N", "2.1": "N", "2.2": "N", "2.6": "Y", "3.1": "Y", "4.1": "N", "4.2": "N",
        "4.3": "N", "5.1": "NI", "5.2": "N", "5.3": "N"}


# ---- C1: only asked NI questions, never 3.2, never an INSUFFICIENT domain
def test_PLANT_targets_are_the_asked_ni_questions_only():
    assert cx.ni_targets(_obj(BASE)) == ["1.2", "5.1"]


def test_PLANT_targets_never_include_3_2_or_an_insufficient_domain():
    o = _obj(dict(BASE, **{"3.1": "N", "3.3": "NI", "3.4": "NI"}), insufficient=("D5",))
    t = cx.ni_targets(o)
    assert "3.2" not in t and "5.1" not in t and "3.3" in t


# ---- C2/C3: only PY/PN, with a verified verbatim quote from a shown open source
def _reading(*rows):
    return {"answers": [dict(zip(("qid", "answer", "quote", "source_id", "rationale"), r)) for r in rows]}


def test_PLANT_a_verified_contextual_py_is_kept():
    v = cx.verify(_reading(("1.2", "PY", QUOTE, SRC["id"], "central randomisation implies concealment")), [SRC], ["1.2"])
    assert v["1.2"]["answer"] == "PY" and v["1.2"]["quote"] == QUOTE and v["1.2"]["source_sha256"] == SRC["sha256"]


def test_PLANT_y_or_n_is_never_a_contextual_answer():
    v = cx.verify(_reading(("1.2", "Y", QUOTE, SRC["id"], "r")), [SRC], ["1.2"])
    assert v["1.2"]["answer"] == "NI" and v["1.2"]["dropped"]["why"] == "ONLY_PY_PN_MAY_BE_CONTEXTUAL"


def test_PLANT_a_quote_not_in_the_source_is_dropped():
    v = cx.verify(_reading(("1.2", "PY", "sealed opaque envelopes", SRC["id"], "r")), [SRC], ["1.2"])
    assert v["1.2"]["answer"] == "NI" and v["1.2"]["dropped"]["why"] == "QUOTE_NOT_FOUND_IN_NAMED_OPEN_SOURCE"


def test_PLANT_a_closed_source_is_not_a_context():
    closed = dict(SRC, open_for_prompt=False)
    v = cx.verify(_reading(("1.2", "PY", QUOTE, SRC["id"], "r")), [closed], ["1.2"])
    assert v["1.2"]["answer"] == "NI"


def test_PLANT_a_non_target_question_is_ignored():
    v = cx.verify(_reading(("1.1", "PY", QUOTE, SRC["id"], "r")), [SRC], ["1.2"])
    assert "1.1" not in v


# ---- C4: two blind readers agree, or the adjudicator decides
def _v(a, quote=QUOTE):
    return {"answer": a, "quote": quote, "source_id": SRC["id"], "source_sha256": SRC["sha256"], "rationale": "r"} \
        if a in ("PY", "PN") else {"answer": a}


def test_PLANT_agreement_gives_a_contextual_answer():
    c = cx.combine({"1.2": _v("PY")}, {"1.2": _v("PY")}, {})
    assert c["1.2"]["answer"] == "PY" and c["1.2"]["decided_by"] == "both readers"


def test_PLANT_disagreement_without_an_adjudicator_stays_ni():
    assert cx.combine({"1.2": _v("PY")}, {"1.2": _v("NI")}, {})["1.2"]["answer"] == "NI"
    assert cx.combine({"1.2": _v("PY")}, {"1.2": _v("PN")}, {})["1.2"]["answer"] == "NI"


def test_PLANT_the_adjudicator_decides_a_disagreement():
    c = cx.combine({"1.2": _v("PY")}, {"1.2": _v("NI")}, {"1.2": _v("PY")})
    assert c["1.2"]["answer"] == "PY" and c["1.2"]["decided_by"] == "adjudicator"
    assert cx.combine({"1.2": _v("PY")}, {"1.2": _v("NI")}, {"1.2": _v("NI")})["1.2"]["answer"] == "NI"


def test_PLANT_an_adjudicator_cannot_override_agreement():
    c = cx.combine({"1.2": _v("PY")}, {"1.2": _v("PY")}, {"1.2": _v("PN")})
    assert c["1.2"]["answer"] == "PY" and c["1.2"]["decided_by"] == "both readers"


# ---- C1/C5/C6: applied to the object -- only targets change, stored as contextual, re-judged by the same engine
def test_PLANT_apply_changes_only_targets_and_marks_them_contextual():
    o = _obj(BASE)
    new = cx.apply(o, {"1.2": dict(_v("PY"), decided_by="both readers")}, records={"1.2": ["mc-a", "mc-b"]})
    a = new["domains"]["D1"]["answers"]["1.2"]
    assert a["answer"] == "PY" and a["basis"] == "contextual" and a["span"] == QUOTE and a["records"] == ["mc-a", "mc-b"]
    assert new["domains"]["D1"]["judgement"] == "LOW" and new["domains"]["D1"]["ni"]["ni_driven"] is False
    for d in rf.DOMAINS:                                               # every other answer is byte-for-byte the same
        for q, x in o["domains"][d]["answers"].items():
            if q != "1.2":
                assert new["domains"][d]["answers"][q] == x
    assert new["domains"]["D5"]["answers"]["5.1"]["answer"] == "NI"     # no context offered: NI remains


def test_PLANT_apply_refuses_a_non_target_or_a_y_n():
    o = _obj(BASE)
    with pytest.raises(ValueError):
        cx.apply(o, {"1.1": dict(_v("PY"), decided_by="both readers")}, records={})
    with pytest.raises(ValueError):
        cx.apply(o, {"1.2": dict(_v("PY"), answer="Y", decided_by="both readers")}, records={})


# ---- the pre-registered scorer's guards (scripts/rob2_ctx_score.py)
import copy  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import rob2_ctx_score as cs  # noqa: E402

AFTER = "2026-10-12T22:00:00+01:00"


def _docs():
    base = {"trials": {"1": _obj(BASE)}}
    ctx = copy.deepcopy(base)
    ctx["trials"]["1"] = cx.apply(base["trials"]["1"], {"1.2": dict(_v("PY"), decided_by="both readers")},
                                  records={"1.2": ["mc-new"]})
    return base, ctx


def test_PLANT_ctx_score_accepts_a_documented_contextual_change():
    base, ctx = _docs()
    n = cs.check_contextual_doc("s", base, ctx, AFTER, record_time=lambda rid: "2026-10-12T23:00:00+00:00", verify_records=lambda *a, **k: None)
    assert n == {"1.2": 1}


def test_PLANT_ctx_score_refuses_a_record_from_before_the_preregistration():
    base, ctx = _docs()
    with pytest.raises(SystemExit, match="predates"):
        cs.check_contextual_doc("s", base, ctx, AFTER, record_time=lambda rid: "2026-10-12T20:00:00+00:00", verify_records=lambda *a, **k: None)


def test_PLANT_ctx_score_refuses_any_other_change():
    base, ctx = _docs()
    ctx["trials"]["1"]["domains"]["D1"]["answers"]["1.1"]["answer"] = "PY"          # a direct answer edited
    with pytest.raises(SystemExit, match="other than NI"):
        cs.check_contextual_doc("s", base, ctx, AFTER, record_time=lambda rid: "2026-10-12T23:00:00+00:00", verify_records=lambda *a, **k: None)


def test_PLANT_ctx_score_refuses_an_undocumented_contextual_answer():
    base, ctx = _docs()
    del ctx["trials"]["1"]["domains"]["D1"]["answers"]["1.2"]["records"]
    with pytest.raises(SystemExit, match="other than NI"):
        cs.check_contextual_doc("s", base, ctx, AFTER, record_time=lambda rid: "2026-10-12T23:00:00+00:00", verify_records=lambda *a, **k: None)


def test_PLANT_ctx_score_refuses_a_changed_cohort_or_label():
    base, ctx = _docs()
    ctx["trials"]["2"] = ctx["trials"]["1"]
    with pytest.raises(SystemExit, match="trials differ"):
        cs.check_contextual_doc("s", base, ctx, AFTER, record_time=lambda rid: "2026-10-12T23:00:00+00:00", verify_records=lambda *a, **k: None)
    base, ctx = _docs()
    ctx["trials"]["1"]["domains"]["D1"]["judgement"] = "HIGH"
    with pytest.raises(SystemExit, match="recomputed"):
        cs.check_contextual_doc("s", base, ctx, AFTER, record_time=lambda rid: "2026-10-12T23:00:00+00:00", verify_records=lambda *a, **k: None)


def test_PLANT_ctx_score_takes_no_subset():
    with pytest.raises(SystemExit, match="all four"):
        cs.main(["deadbeef", "x"])


def test_PLANT_ctx_score_reads_git_as_utf8(tmp_path, monkeypatch):
    # a REAL git, a non-ASCII committed file: the NI scorer's 12 Oct cp1252 false refusal must not recur here
    repo = tmp_path / "r"
    repo.mkdir()
    (repo / "f.txt").write_text("11\u202f052 caf\u00e9", encoding="utf-8")
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "x"]):
        subprocess.run(["git", "-C", str(repo), "-c", "core.hooksPath=/dev/null", *args], check=True, env=env)
    monkeypatch.setattr(cs, "ROOT", str(repo))
    assert cs._git("show", "HEAD:f.txt").stdout == "11\u202f052 caf\u00e9"


def test_PLANT_quote_normalisation_matches_the_dual_reader():
    # one quote, one verdict: the same NFKC / dash / case / whitespace normalisation as scripts/rob2_dual._norm
    src = dict(SRC, text="Randomisation was done centrally \ufb01rst via a web system \u2013 by the CTU.")
    # the rationale refers to the quoted words (the round-2 rule); this test is about the quote normalisation
    v = cx.verify(_reading(("1.2", "PY", "done centrally first via a web system - by the CTU", SRC["id"],
                            "randomisation done centrally means concealment")), [src], ["1.2"])
    assert v["1.2"]["answer"] == "PY"


def test_PLANT_apply_never_shares_answer_dicts_with_the_baseline():
    o = _obj(BASE)
    new = cx.apply(o, {"1.2": dict(_v("PY"), decided_by="both readers")}, records={"1.2": ["mc-a"]})
    new["domains"]["D1"]["answers"]["1.1"]["answer"] = "PN"
    assert o["domains"]["D1"]["answers"]["1.1"]["answer"] == "Y"


# ================= review round 1 (codex + agy, recorded): failing-first tests =================
def test_PLANT_r1_a_generic_or_empty_rationale_is_not_context():          # codex0
    for why in ("", "Trials usually prespecify analyses", "This is standard practice in such trials",
                "Most trials of this kind are typically concealed"):
        v = cx.verify(_reading(("1.2", "PY", QUOTE, SRC["id"], why)), [SRC], ["1.2"])
        assert v["1.2"]["answer"] == "NI", why


def test_PLANT_r1_a_quote_over_300_characters_is_dropped():               # agy3
    long_src = dict(SRC, text="x " * 10 + "a" * 350)
    v = cx.verify(_reading(("1.2", "PY", "a" * 301, SRC["id"], "the context shows it")), [long_src], ["1.2"])
    assert v["1.2"]["answer"] == "NI"


def test_PLANT_r1_a_target_the_reader_skipped_is_ni():                    # agy7
    assert cx.verify({"answers": []}, [SRC], ["1.2"]) == {"1.2": {"answer": "NI", "rationale": None}}


def test_PLANT_r1_readers_agreeing_on_ni_are_never_overridden():          # agy0
    c = cx.combine({"1.2": _v("NI")}, {"1.2": _v("NI")}, {"1.2": _v("PY")})
    assert c["1.2"]["answer"] == "NI"


def test_PLANT_r1_an_adjudicated_ni_is_recorded_as_the_adjudicators():    # agy5
    c = cx.combine({"1.2": _v("PY")}, {"1.2": _v("PN")}, {"1.2": {"answer": "NI", "rationale": "no context"}})
    assert (c["1.2"]["answer"], c["1.2"]["decided_by"]) == ("NI", "adjudicator")


def test_PLANT_r1_ctx_score_refuses_a_deleted_direct_answer():            # codex2, agy6
    base, ctx = _docs()
    del ctx["trials"]["1"]["domains"]["D1"]["answers"]["1.3"]
    with pytest.raises(SystemExit, match="answers differ|changed"):
        cs.check_contextual_doc("s", base, ctx, AFTER, record_time=lambda rid: "2026-10-12T23:00:00+00:00",
                                verify_records=lambda *a, **k: None)


def test_PLANT_r1_ctx_score_refuses_a_domain_made_insufficient():         # codex3, agy2
    base, ctx = _docs()
    ctx["trials"]["1"]["domains"]["D1"]["judgement"] = rf.INSUFFICIENT
    with pytest.raises(SystemExit, match="INSUFFICIENT|eligibility"):
        cs.check_contextual_doc("s", base, ctx, AFTER, record_time=lambda rid: "2026-10-12T23:00:00+00:00",
                                verify_records=lambda *a, **k: None)


def test_PLANT_r1_ctx_score_refuses_an_edited_overall_or_label():         # codex3
    base, ctx = _docs()
    ctx["trials"]["1"]["overall"]["judgement"] = "HIGH"
    with pytest.raises(SystemExit, match="overall"):
        cs.check_contextual_doc("s", base, ctx, AFTER, record_time=lambda rid: "2026-10-12T23:00:00+00:00",
                                verify_records=lambda *a, **k: None)
    base, ctx = _docs()
    ctx["trials"]["1"]["domains"]["D1"]["ni"]["if_ni_resolved_favourably"] = "HIGH"
    with pytest.raises(SystemExit, match="recomputed"):
        cs.check_contextual_doc("s", base, ctx, AFTER, record_time=lambda rid: "2026-10-12T23:00:00+00:00",
                                verify_records=lambda *a, **k: None)


# ---- codex1 / agy1: a contextual answer is verified against its RECORDS, not just its fields (updated to the
# round-2 contract: replies are re-verified, so the fixtures carry grounded rationales and both readers' contexts)
def test_PLANT_r1_records_verify_an_authentic_contextual_answer():
    recs = {"mc-c": _rec2("codex", "1.2", "PY", QUOTE), "mc-a": _rec2("agy", "1.2", "PY", QUOTE)}
    cs.verify_records("1.2", _stored(), recs.get, trial="1", outcome="o")


def test_PLANT_r1_records_refuse_a_quote_not_in_the_recorded_prompt():
    other = dict(SRC, text="no such context here at all, nothing about it")
    recs = {"mc-c": _rec2("codex", "1.2", "PY", QUOTE, src=other), "mc-a": _rec2("agy", "1.2", "PY", QUOTE, src=other)}
    with pytest.raises(SystemExit, match="does not verify .*QUOTE_NOT_FOUND"):
        cs.verify_records("1.2", _stored(), recs.get, trial="1", outcome="o")


def test_PLANT_r1_records_refuse_a_single_reader():
    recs = {"mc-c": _rec2("codex", "1.2", "PY", QUOTE)}
    with pytest.raises(SystemExit, match="both readers"):
        cs.verify_records("1.2", dict(_stored(), records=["mc-c"]), recs.get, trial="1", outcome="o")


def test_PLANT_r1_records_refuse_a_reply_that_does_not_say_it():
    recs = {"mc-c": _rec2("codex", "1.2", "PY", QUOTE), "mc-a": _rec2("agy", "1.2", "PN", QUOTE)}
    with pytest.raises(SystemExit, match="does not verify as PY"):
        cs.verify_records("1.2", _stored(), recs.get, trial="1", outcome="o")


def test_PLANT_r1_records_refuse_a_source_hash_the_call_was_not_given():
    other = dict(SRC, sha256="b" * 64)                    # the calls were given a different source sha256
    recs = {"mc-c": _rec2("codex", "1.2", "PY", QUOTE, src=other), "mc-a": _rec2("agy", "1.2", "PY", QUOTE, src=other)}
    with pytest.raises(SystemExit, match="sha256"):
        cs.verify_records("1.2", _stored(), recs.get, trial="1", outcome="o")


# ---- codex5: the freeze covers every file the score depends on
def test_PLANT_r1_freeze_covers_the_pipeline():
    for f in ("scripts/rob2_calibrate.py", "scripts/rob2_dual.py", "robgrade/rob2_typed.py", "robgrade/prompt_licence.py",
              "robgrade/rob2_tab.py", "tests/test_rob2_tab.py"):
        assert f in cs.POLICY_FILES, f


# ---- codex4: a recorded reading is used only for the prompt it answered
def test_PLANT_r1_a_stale_record_is_not_replayed(monkeypatch):
    import hashlib
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import rob2_contextual as rc
    p = b"the current prompt"
    # the held record carries the current prompt (round 2: fresh() also reads the record itself)
    monkeypatch.setattr(rc, "record_prompt_sha256", lambda rid: hashlib.sha256(p).hexdigest())
    run = {"state": "RAN_OK", "record_id": "mc-x", "prompt_sha256": hashlib.sha256(b"an older prompt").hexdigest()}
    assert rc.fresh(run, p) is None
    assert rc.fresh(dict(run, prompt_sha256=hashlib.sha256(p).hexdigest()), p) is not None
    assert rc.fresh(dict(run, state="RAN_ERROR", prompt_sha256=hashlib.sha256(p).hexdigest()), p) is None


# ================= review round 2 (codex + agy): failing-first tests =================
GOOD_WHY = "central web-based randomisation means the allocation was concealed"
SRC_B = {"id": "registry:NCT1:description", "kind": "registry_text", "text": "Randomisation by an interactive voice "
         "response system held at the coordinating centre.", "sha256": "b" * 64, "open_for_prompt": True}
QUOTE_B = "interactive voice response system"


def test_PLANT_r2_a_memory_rationale_is_not_context():                      # codex3
    for why in ("I remember that this trial followed its prospectively finalized analysis plan",
                "As is known from the published protocol, the plan was final"):
        assert cx.verify(_reading(("5.1", "PY", QUOTE, SRC["id"], why)), [SRC], ["5.1"])["5.1"]["answer"] == "NI", why


def test_PLANT_r2_a_rationale_must_refer_to_the_quoted_words():            # codex3
    v = cx.verify(_reading(("1.2", "PY", QUOTE, SRC["id"], "the allocation was concealed properly")), [SRC], ["1.2"])
    assert v["1.2"]["answer"] == "NI" and v["1.2"]["dropped"]["why"].startswith("RATIONALE_DOES_NOT_REFER")
    assert cx.verify(_reading(("1.2", "PY", QUOTE, SRC["id"], GOOD_WHY)), [SRC], ["1.2"])["1.2"]["answer"] == "PY"


def test_PLANT_r2_an_abstract_source_keyed_abstract_is_read():              # agy1
    src = {"id": "abstract:PMID 9", "abstract": SRC["text"], "sha256": "a" * 64, "open_for_prompt": True}
    assert cx.verify(_reading(("1.2", "PY", QUOTE, src["id"], GOOD_WHY)), [src], ["1.2"])["1.2"]["answer"] == "PY"


def _vv(src, quote, why=GOOD_WHY, ans="PY"):
    return {"answer": ans, "quote": quote, "source_id": src["id"], "source_sha256": src["sha256"], "rationale": why}


def test_PLANT_r2_agreement_from_two_sources_keeps_both_contexts():         # codex5, agy0, agy5
    c = cx.combine({"1.2": _vv(SRC, QUOTE)}, {"1.2": _vv(SRC_B, QUOTE_B, "an interactive voice response system conceals it")}, {})
    assert c["1.2"]["answer"] == "PY" and [x["source_id"] for x in c["1.2"]["context"]] == [SRC["id"], SRC_B["id"]]
    new = cx.apply(_obj(BASE), c, records={"1.2": ["mc-c", "mc-a"]})
    assert [x["quote"] for x in new["domains"]["D1"]["answers"]["1.2"]["context"]] == [QUOTE, QUOTE_B]


def test_PLANT_r2_an_adjudicated_ni_keeps_its_audit_and_the_ni_answer():    # codex6, agy3
    o = _obj(BASE)
    c = {"1.2": {"answer": "NI", "decided_by": "adjudicator", "rationale": "insufficient context"}}
    new = cx.apply(o, c, records={"1.2": ["mc-c", "mc-a", "mc-j"]})
    assert new["domains"]["D1"]["answers"]["1.2"] == o["domains"]["D1"]["answers"]["1.2"]
    assert new["contextual_audit"]["1.2"] == {"answer": "NI", "decided_by": "adjudicator",
                                              "rationale": "insufficient context", "records": ["mc-c", "mc-a", "mc-j"]}


def test_PLANT_r2_a_contextual_answer_on_a_question_no_longer_asked_is_na():   # agy2, agy4
    o = _obj(dict(BASE, **{"3.1": "NI", "3.3": "NI", "3.4": "NI"}))
    c = {"3.1": dict(_vv(SRC, QUOTE), decided_by="both readers", context=[]),
         "3.3": dict(_vv(SRC, QUOTE), decided_by="both readers", context=[])}
    new = cx.apply(o, c, records={"3.1": ["x"], "3.3": ["x"]})
    a = new["domains"]["D3"]["answers"]
    assert a["3.1"]["answer"] == "PY" and a["3.3"]["answer"] == "NA" and a["3.4"]["answer"] == "NA"


def test_PLANT_r2_ctx_score_accepts_a_branch_closed_by_a_contextual_answer():  # agy2
    base = {"trials": {"1": _obj(dict(BASE, **{"3.1": "NI", "3.3": "NI", "3.4": "NI"}))}}
    ctx = {"trials": {"1": cx.apply(base["trials"]["1"], {"3.1": dict(_vv(SRC, QUOTE), decided_by="both readers",
                                                                       context=[])}, records={"3.1": ["mc-n"]})}}
    n = cs.check_contextual_doc("s", base, ctx, AFTER, record_time=lambda rid: "2026-10-12T23:00:00+00:00",
                                verify_records=lambda *a, **k: None)
    assert n == {"3.1": 1}


def test_PLANT_r2_overall_label_discloses_contextual_answers():             # agy6
    sys.path.insert(0, ROOT)
    from robgrade import rob2_tab as tab
    new = cx.apply(_obj(dict(BASE, **{"5.1": "Y"})), {"1.2": dict(_vv(SRC, QUOTE), decided_by="both readers", context=[])},
                   records={"1.2": ["x"]})
    assert tab.overall_label(new["overall"], new["domains"]) == "Low [contextual answers in: D1]"


# ---- the scorer re-verifies every recorded reply; records are bound to their trial and outcome
def _rec2(who, qid, ans, quote, src=SRC, why=GOOD_WHY, trial="1", outcome="o", readings=None, shown=None):
    """A record as the scorer loads it. Readers carry the REGISTERED reader prompt head; the adjudicator carries the
    registered adjudicator head and the two readings it was shown (round 3)."""
    import rob2_contextual as rc
    shown = shown or [src]                 # every source the prompt showed (both readers see the SAME prompt)
    # the REGISTERED head, built by the pipeline's own prompt_head (round 4: no placeholder question text)
    head = rc.prompt_head(trial, None, outcome, [qid], "adjudicator" if who == "adjudicator" else "reader",
                          readings or {})
    ev = [{"id": x["id"], "kind": "x", ("abstract" if x["id"].startswith("abstract") else "text"): x["text"]} for x in shown]
    prompt = head + rc.EVIDENCE_MARK + json.dumps({"sources": ev})
    reply = json.dumps({"answers": [{"qid": qid, "answer": ans, "quote": quote, "source_id": src["id"], "rationale": why}],
                        "notes": ""})
    return {"state": "RAN_OK", "caller": {"line": f"call:{who}"}, "prompt_text": prompt, "reply": reply,
            "input_digests": [{"ref": x["id"], "sha256": x["sha256"]} for x in shown],
            "request_utc": "2026-10-12T23:00:00+00:00"}


def _readings(r1, r2, qid="1.2"):
    """The two readings exactly as the pipeline shows them to the adjudicator: each reply through contextual.verify."""
    return {qid: {"reader 1": cs._verified(r1, qid), "reader 2": cs._verified(r2, qid)}}


def _stored(answer="PY", note="both readers: x", context=None):
    ctx1 = {"who": "reader 1", "quote": QUOTE, "source_id": SRC["id"], "source_sha256": SRC["sha256"], "rationale": GOOD_WHY}
    return {"answer": answer, "basis": "contextual", "span": QUOTE, "source_ref": SRC["id"], "source_sha256": SRC["sha256"],
            "records": ["mc-c", "mc-a"], "note": note,
            "context": context if context is not None else [ctx1, dict(ctx1, who="reader 2")]}


def test_PLANT_r2_records_bind_trial_and_outcome():                         # codex0
    recs = {"mc-c": _rec2("codex", "1.2", "PY", QUOTE, outcome="pain"), "mc-a": _rec2("agy", "1.2", "PY", QUOTE, outcome="pain")}
    with pytest.raises(SystemExit, match="trial or outcome"):
        cs.verify_records("1.2", _stored(), recs.get, trial="1", outcome="o")


def test_PLANT_r2_records_are_re_verified_empty_quote_refused():            # codex2
    recs = {"mc-c": _rec2("codex", "1.2", "PY", ""), "mc-a": _rec2("agy", "1.2", "PY", "")}
    with pytest.raises(SystemExit, match="does not verify"):
        cs.verify_records("1.2", _stored(), recs.get, trial="1", outcome="o")


def test_PLANT_r2_adjudication_needs_a_real_disagreement():                 # codex1
    r1, r2 = _rec2("codex", "1.2", "NI", ""), _rec2("agy", "1.2", "NI", "")
    recs = {"mc-c": r1, "mc-a": r2, "mc-j": _rec2("adjudicator", "1.2", "PY", QUOTE, readings=_readings(r1, r2))}
    a = dict(_stored(note="adjudicator: x", context=[{"who": "adjudicator", "quote": QUOTE, "source_id": SRC["id"],
                                                     "source_sha256": SRC["sha256"], "rationale": GOOD_WHY}]),
             records=["mc-c", "mc-a", "mc-j"])
    with pytest.raises(SystemExit, match="agreed"):
        cs.verify_records("1.2", a, recs.get, trial="1", outcome="o")


def test_PLANT_r2_an_authentic_adjudication_verifies():                     # agy7
    r1, r2 = _rec2("codex", "1.2", "PY", QUOTE), _rec2("agy", "1.2", "NI", "")
    recs = {"mc-c": r1, "mc-a": r2, "mc-j": _rec2("adjudicator", "1.2", "PY", QUOTE, readings=_readings(r1, r2))}
    a = dict(_stored(note="adjudicator: x", context=[{"who": "adjudicator", "quote": QUOTE, "source_id": SRC["id"],
                                                     "source_sha256": SRC["sha256"], "rationale": GOOD_WHY}]),
             records=["mc-c", "mc-a", "mc-j"])
    cs.verify_records("1.2", a, recs.get, trial="1", outcome="o")


def test_PLANT_r2_two_sources_verify_each_against_its_own():                # codex5, agy0
    both = [SRC, SRC_B]                    # the two readers saw the same prompt, with both sources
    recs = {"mc-c": _rec2("codex", "1.2", "PY", QUOTE, shown=both),
            "mc-a": _rec2("agy", "1.2", "PY", QUOTE_B, src=SRC_B, why="an interactive voice response system conceals it",
                          shown=both)}
    a = _stored(context=[{"who": "reader 1", "quote": QUOTE, "source_id": SRC["id"], "source_sha256": SRC["sha256"],
                          "rationale": GOOD_WHY},
                         {"who": "reader 2", "quote": QUOTE_B, "source_id": SRC_B["id"], "source_sha256": SRC_B["sha256"],
                          "rationale": "an interactive voice response system conceals it"}])
    cs.verify_records("1.2", a, recs.get, trial="1", outcome="o")


def test_PLANT_r2_fresh_reads_the_records_own_prompt(monkeypatch):          # codex0
    import hashlib
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import rob2_contextual as rc
    p = b"the current prompt"
    run = {"state": "RAN_OK", "record_id": "mc-x", "prompt_sha256": hashlib.sha256(p).hexdigest()}
    monkeypatch.setattr(rc, "record_prompt_sha256", lambda rid: hashlib.sha256(b"another prompt").hexdigest())
    assert rc.fresh(run, p) is None                                    # the manifest says current; the record does not
    monkeypatch.setattr(rc, "record_prompt_sha256", lambda rid: hashlib.sha256(p).hexdigest())
    assert rc.fresh(run, p) is not None


def test_PLANT_r2_freeze_files_must_exist_at_the_anchor(monkeypatch):       # codex4
    def git(*a):
        if a[0] in ("log", "rev-parse"):
            return type("R", (), {"returncode": 0, "stdout": "deadbeef"})()
        if a[0] == "cat-file":
            return type("R", (), {"returncode": 1 if a[-1].endswith("robgrade/prompt_licence.py") else 0, "stdout": ""})()
        return type("R", (), {"returncode": 0, "stdout": ""})()
    monkeypatch.setattr(cs, "_git", git)
    with pytest.raises(SystemExit, match="not in the pre-registration"):
        cs.check_prereg("deadbeef")


# ================= review round 3 (codex; agy RAN_ERROR twice): failing-first tests =================
def test_PLANT_r3_a_quote_must_be_about_the_question():                     # codex0
    # a randomisation quote cannot support 5.1 (analysis plan), however the rationale is worded
    why = "central web-based randomisation shows the prespecified analysis plan was followed"
    assert cx.verify(_reading(("5.1", "PY", QUOTE, SRC["id"], why)), [SRC], ["5.1"])["5.1"]["answer"] == "NI"
    # ... while the same quote can support 1.2 (allocation concealment)
    assert cx.verify(_reading(("1.2", "PY", QUOTE, SRC["id"], GOOD_WHY)), [SRC], ["1.2"])["1.2"]["answer"] == "PY"


def test_PLANT_r3_explicit_memory_is_not_context():                         # codex0
    why = "My training data confirms central web-based randomisation was concealed"
    assert cx.verify(_reading(("1.2", "PY", QUOTE, SRC["id"], why)), [SRC], ["1.2"])["1.2"]["answer"] == "NI"


def test_PLANT_r3_mechanism_wording_is_not_mistaken_for_memory():           # codex3 (narrowed)
    src = dict(SRC, text="A double-blind trial; participants who withdrew because of worsening symptoms were not "
                         "followed up.")
    why = "participants who withdrew because of worsening symptoms are known to differ, so missingness depends on outcome"
    v = cx.verify(_reading(("3.4", "PY", "withdrew because of worsening symptoms", SRC["id"], why)), [src], ["3.4"])
    assert v["3.4"]["answer"] == "PY"


def test_PLANT_r3_general_knowledge_without_quoted_context_stays_ni():     # codex3; REVERSED in round 5
    # round 3 declined this; round 5 reverses it -- the RoB 2 guidance asks 3.3/3.4 to reason about the clinical
    # setting, so quoted clinical context plus a grounded rationale is context there. A question OTHER than 3.3/3.4
    # still needs a quote about its own topic:
    src = dict(SRC, text="A trial in patients with schizophrenia.")
    why = "In schizophrenia patients, continuing symptoms are known to increase dropout"
    assert cx.verify(_reading(("3.4", "PY", "patients with schizophrenia", SRC["id"], why)), [src], ["3.4"])["3.4"]["answer"] == "PY"
    assert cx.verify(_reading(("3.1", "PN", "patients with schizophrenia", SRC["id"], why)), [src], ["3.1"])["3.1"]["answer"] == "NI"


def test_PLANT_r3_ctx_score_accepts_a_branch_opened_by_a_contextual_answer():  # codex1
    spec = dict(BASE, **{"2.1": "Y", "2.2": "Y", "2.3": "NI"})
    base = {"trials": {"1": _obj(spec)}}
    assert base["trials"]["1"]["domains"]["D2"]["answers"]["2.4"]["answer"] == "NA"
    src = dict(SRC, text="Protocol deviations because of the trial context were reported in 12 participants.")
    c = {"2.3": dict(_vv(src, "Protocol deviations because of the trial context",
                         "protocol deviations because of the trial context occurred"), decided_by="both readers",
                     context=[])}
    ctx = {"trials": {"1": cx.apply(base["trials"]["1"], c, records={"2.3": ["mc-n"]})}}
    a = ctx["trials"]["1"]["domains"]["D2"]["answers"]
    assert a["2.3"]["answer"] == "PY" and a["2.4"]["answer"] == "NI"        # opened, unanswered -> NI, never guessed
    n = cs.check_contextual_doc("s", base, ctx, AFTER, record_time=lambda rid: "2026-10-12T23:00:00+00:00",
                                verify_records=lambda *a, **k: None)
    assert n == {"2.3": 1}


def test_PLANT_r3_reader_prompts_must_be_identical_and_registered():       # codex2
    good = {"mc-c": _rec2("codex", "1.2", "PY", QUOTE), "mc-a": _rec2("agy", "1.2", "PY", QUOTE)}
    cs.verify_records("1.2", _stored(), good.get, trial="1", outcome="o")
    differ = dict(good, **{"mc-a": dict(good["mc-a"], prompt_text=good["mc-a"]["prompt_text"] + " ")})
    with pytest.raises(SystemExit, match="same registered prompt"):
        cs.verify_records("1.2", _stored(), differ.get, trial="1", outcome="o")
    other = {k: dict(r, prompt_text="ANOTHER INSTRUCTION" + r["prompt_text"][r["prompt_text"].index("\nTRIAL:"):])
             for k, r in good.items()}
    with pytest.raises(SystemExit, match="same registered prompt"):
        cs.verify_records("1.2", _stored(), other.get, trial="1", outcome="o")


def test_PLANT_r3_the_adjudicator_must_have_seen_the_cited_readings():      # codex2
    recs = {"mc-c": _rec2("codex", "1.2", "PY", QUOTE), "mc-a": _rec2("agy", "1.2", "NI", ""),
            "mc-j": _rec2("adjudicator", "1.2", "PY", QUOTE)}
    a = dict(_stored(note="adjudicator: x", context=[{"who": "adjudicator", "quote": QUOTE, "source_id": SRC["id"],
                                                     "source_sha256": SRC["sha256"], "rationale": GOOD_WHY}]),
             records=["mc-c", "mc-a", "mc-j"])
    with pytest.raises(SystemExit, match="readings"):                       # this adjudicator prompt shows none
        cs.verify_records("1.2", a, recs.get, trial="1", outcome="o")


def test_PLANT_r3_a_context_without_a_source_digest_is_refused():           # codex4
    recs = {"mc-c": _rec2("codex", "1.2", "PY", QUOTE), "mc-a": dict(_rec2("agy", "1.2", "PY", QUOTE), input_digests=[])}
    a = _stored(context=[dict(_stored()["context"][0]), dict(_stored()["context"][1], source_sha256=None)])
    a["context"][1]["rationale"] = GOOD_WHY
    with pytest.raises(SystemExit, match="sha256"):
        cs.verify_records("1.2", a, recs.get, trial="1", outcome="o")


def test_PLANT_r3_a_tampered_rationale_is_refused():                         # codex5
    recs = {"mc-c": _rec2("codex", "1.2", "PY", QUOTE), "mc-a": _rec2("agy", "1.2", "PY", QUOTE)}
    a = _stored()
    a["context"][1]["rationale"] = "something else entirely"
    with pytest.raises(SystemExit, match="rationale|context"):
        cs.verify_records("1.2", a, recs.get, trial="1", outcome="o")


def test_PLANT_r3_every_readers_quote_is_shown_with_its_source():           # codex6
    sys.path.insert(0, ROOT)
    from robgrade import rob2_tab as tab
    c = cx.combine({"1.2": _vv(SRC, QUOTE)}, {"1.2": _vv(SRC_B, QUOTE_B, "an interactive voice response system conceals it")}, {})
    new = cx.apply(_obj(BASE), c, records={"1.2": ["mc-c", "mc-a"]})
    note = tab.contextual_note(new["domains"]["D1"])
    assert f"'{QUOTE}' ({SRC['id']})" in note and f"'{QUOTE_B}' ({SRC_B['id']})" in note


# ================= review round 4 (codex + agy): failing-first tests =================
def test_PLANT_r4_the_handbooks_own_ctu_example_is_context():               # codex0
    src = dict(SRC, text="A trial of 4000 patients run for regulatory purposes by an experienced clinical trials unit.")
    q = "run for regulatory purposes by an experienced clinical trials unit"
    why = "an experienced clinical trials unit running a regulatory trial would conceal allocation"
    assert cx.verify(_reading(("1.2", "PY", q, SRC["id"], why)), [src], ["1.2"])["1.2"]["answer"] == "PY"


def test_r4_registered_protocol_context_is_a_readers_judgement():          # codex1 r4 / codex0 r5 (declined, pinned)
    # PINS that verify() does not MECHANICALLY forbid this context; whether it supports 5.1 is the two blind readers'
    # judgement under Handbook 8.2.3 (the declared residual), not a claim that PY is right
    src = dict(SRC, text="A protocol was registered before enrolment and the statistical analysis plan published.")
    why = "a protocol registered before enrolment and a published statistical analysis plan support a prespecified plan"
    v = cx.verify(_reading(("5.1", "PY", "A protocol was registered before enrolment", SRC["id"], why)), [src], ["5.1"])
    assert v["5.1"]["answer"] == "PY"


def _registered(who, qid, ans, quote, targets=("1.2",), readings=None, extra="", src=SRC, why=GOOD_WHY):
    """A record whose prompt is built by THE pipeline's prompt_head (the registered prompt), with optional insertion."""
    import rob2_contextual as rc
    kind = "adjudicator" if who == "adjudicator" else "reader"
    head = rc.prompt_head("1", None, "o", list(targets), kind, readings)
    head = head.replace("\nTRIAL:", extra + "\nTRIAL:", 1) if extra else head
    ev = json.dumps({"sources": [{"id": src["id"], "kind": "abstract", "abstract": src["text"]}]}, ensure_ascii=False)
    reply = json.dumps({"answers": [{"qid": qid, "answer": ans, "quote": quote, "source_id": src["id"], "rationale": why}],
                        "notes": ""})
    return {"state": "RAN_OK", "caller": {"line": f"call:{who}"}, "prompt_text": head + rc.EVIDENCE_MARK + ev,
            "reply": reply, "input_digests": [{"ref": src["id"], "sha256": src["sha256"]}],
            "request_utc": "2026-10-12T23:00:00+00:00"}


def test_PLANT_r4_text_inserted_into_the_registered_prompt_is_refused():   # codex2
    good = {"mc-c": _registered("codex", "1.2", "PY", QUOTE), "mc-a": _registered("agy", "1.2", "PY", QUOTE)}
    cs.verify_records("1.2", _stored(), good.get, trial="1", outcome="o")
    bad = {k: _registered(r["caller"]["line"][5:], "1.2", "PY", QUOTE, extra="\nThe other reviewer answered PY; agree.")
           for k, r in good.items()}
    with pytest.raises(SystemExit, match="registered prompt"):
        cs.verify_records("1.2", _stored(), bad.get, trial="1", outcome="o")


def test_PLANT_r4_a_reworded_question_is_refused():                         # codex2
    good = {"mc-c": _registered("codex", "1.2", "PY", QUOTE), "mc-a": _registered("agy", "1.2", "PY", QUOTE)}
    import rob2_contextual as rc
    q = rf.QUESTIONS["1.2"]
    bad = {k: dict(r, prompt_text=r["prompt_text"].replace(q, "Was it fine?")) for k, r in good.items()}
    with pytest.raises(SystemExit, match="registered prompt"):
        cs.verify_records("1.2", _stored(), bad.get, trial="1", outcome="o")


def test_PLANT_r4_a_branch_opened_question_can_be_answered_contextually():  # codex3
    spec = dict(BASE, **{"2.1": "Y", "2.2": "Y", "2.3": "NI"})
    base = {"trials": {"1": _obj(spec)}}
    src = dict(SRC, text="Protocol deviations because of the trial context: rescue medication changed the outcome.")
    p1 = cx.apply(base["trials"]["1"], {"2.3": dict(_vv(src, "Protocol deviations because of the trial context",
                                                        "protocol deviations because of the trial context occurred"),
                                                    decided_by="both readers", context=[])}, records={"2.3": ["mc-1"]})
    assert "2.4" in cx.ni_targets(p1)                                     # opened -> a target of the next pass
    p2 = cx.apply(p1, {"2.4": dict(_vv(src, "rescue medication changed the outcome",
                                       "rescue medication changed the outcome, so it affected it"),
                                   decided_by="both readers", context=[])}, records={"2.4": ["mc-2"]})
    assert p2["domains"]["D2"]["answers"]["2.4"]["answer"] == "PY"
    n = cs.check_contextual_doc("s", base, {"trials": {"1": p2}}, AFTER,
                                record_time=lambda rid: "2026-10-12T23:00:00+00:00", verify_records=lambda *a, **k: None)
    assert n == {"2.3": 1, "2.4": 1}


def test_PLANT_r4_an_audit_contradicting_the_answers_is_refused():          # codex4
    base, ctx = _docs()
    ctx["trials"]["1"]["domains"] = copy.deepcopy(base["trials"]["1"]["domains"])     # answer restored to NI ...
    ctx["trials"]["1"]["overall"] = copy.deepcopy(base["trials"]["1"]["overall"])
    ctx["trials"]["1"]["contextual_audit"] = {"1.2": {"answer": "PY", "decided_by": "both readers", "rationale": "r",
                                                      "records": ["mc-new"]}}  # ... while its audit says PY
    with pytest.raises(SystemExit, match="audit"):
        cs.check_contextual_doc("s", base, ctx, AFTER, record_time=lambda rid: "2026-10-12T23:00:00+00:00",
                                verify_records=lambda *a, **k: None)


def test_PLANT_r4_freeze_covers_ni_policy_and_the_record_store():           # codex5
    for f in ("outputs/robgrade/NI_POLICY.md", "reproducible_ai/model_source.py"):
        assert f in cs.POLICY_FILES, f


def test_PLANT_r4_a_closed_branch_may_drop_a_direct_answer():               # agy0
    base = {"trials": {"1": _obj(dict(BASE, **{"3.1": "NI", "3.2": "N", "3.3": "N"}))}}
    assert base["trials"]["1"]["domains"]["D3"]["answers"]["3.3"]["answer"] == "N"
    ctx = {"trials": {"1": cx.apply(base["trials"]["1"], {"3.1": dict(_vv(SRC, QUOTE), decided_by="both readers",
                                                                       context=[])}, records={"3.1": ["mc-n"]})}}
    n = cs.check_contextual_doc("s", base, ctx, AFTER, record_time=lambda rid: "2026-10-12T23:00:00+00:00",
                                verify_records=lambda *a, **k: None)
    assert n == {"3.1": 1}


def test_PLANT_r4_a_missing_record_is_refused_not_a_crash():                 # agy2
    base, ctx = _docs()
    with pytest.raises(SystemExit, match="missing"):
        cs.check_contextual_doc("s", base, ctx, AFTER, record_time=None, verify_records=lambda *a, **k: None)


def test_PLANT_r4_extra_or_duplicate_records_are_refused():                 # agy3
    recs = {"mc-c": _rec2("codex", "1.2", "PY", QUOTE), "mc-a": _rec2("agy", "1.2", "PY", QUOTE),
            "mc-c2": _rec2("codex", "1.2", "NI", "")}
    with pytest.raises(SystemExit, match="exactly"):
        cs.verify_records("1.2", dict(_stored(), records=["mc-c", "mc-a", "mc-c2"]), recs.get, trial="1", outcome="o")


# ================= review round 5 (codex REVISE 6; agy ACCEPT): failing-first tests =================
def test_PLANT_r5_prior_knowledge_of_the_trial_is_not_context():            # codex2
    src = dict(SRC, text="Randomisation details were omitted.")
    why = "Prior knowledge of this trial confirms randomisation was concealed"
    v = cx.verify(_reading(("1.2", "PY", "Randomisation details were omitted", SRC["id"], why)), [src], ["1.2"])
    assert v["1.2"]["answer"] == "NI"


def test_PLANT_r5_missingness_questions_take_clinical_context():           # codex3 (guidance: 3.3/3.4 reason about the setting)
    src = dict(SRC, text="A trial of treatment for schizophrenia.")
    why = "in schizophrenia, continuing symptoms make dropout more likely, so missingness could depend on the outcome"
    v = cx.verify(_reading(("3.4", "PY", "A trial of treatment for schizophrenia", SRC["id"], why)), [src], ["3.4"])
    assert v["3.4"]["answer"] == "PY"


def test_PLANT_r5_a_missing_reader_voids_the_pass():                         # codex5
    import rob2_contextual as rc
    a = {"1.2": dict(_vv(SRC, QUOTE))}
    assert rc.pass_decisions(a, None, {"1.2": dict(_vv(SRC, QUOTE))}, ["1.2"]) == \
        {"1.2": {"answer": "NI", "decided_by": "a reader's record is missing or failed: no contextual answer"}}


# ---- the scorer REPLAYS the registered pipeline from the held records (codex1, codex4)
def test_PLANT_r5_scored_objects_must_be_what_the_pipeline_reproduces():
    base, ctx = _docs()
    regen = copy.deepcopy(ctx["trials"]["1"])
    cs.check_replay("s", ctx, {"1": regen})                               # identical: accepted
    regen["domains"]["D1"]["answers"]["1.2"] = base["trials"]["1"]["domains"]["D1"]["answers"]["1.2"]
    with pytest.raises(SystemExit, match="reproduces"):
        cs.check_replay("s", ctx, {"1": regen})


def test_PLANT_r5_every_held_record_must_be_in_the_run_manifest():
    runs = {"s::1::o": {"passes": [{"codex": {"record_id": "mc-c"}, "agy": {"record_id": "mc-a"}}]}}
    cs.check_manifest(runs, held={"mc-c", "mc-a"})
    with pytest.raises(SystemExit, match="manifest"):
        cs.check_manifest(runs, held={"mc-c", "mc-a", "mc-dropped"})


# ================= review round 6 (codex REVISE 6; agy ACCEPT): failing-first tests =================
def test_PLANT_r6_an_earlier_article_is_not_context():                      # codex1 (partly)
    src = dict(SRC, text="Randomisation details were omitted.")
    why = "Randomisation used concealed allocation according to an earlier article"
    v = cx.verify(_reading(("1.2", "PY", "Randomisation details were omitted", SRC["id"], why)), [src], ["1.2"])
    assert v["1.2"]["answer"] == "NI"


def test_PLANT_r6_awareness_from_the_interventions_themselves():           # codex2
    src = dict(SRC, text="Participants received surgery or physiotherapy.")
    why = "participants could distinguish surgery from physiotherapy"
    v = cx.verify(_reading(("2.1", "PY", "Participants received surgery or physiotherapy", SRC["id"], why)), [src], ["2.1"])
    assert v["2.1"]["answer"] == "PY"


def test_PLANT_r6_mechanism_wording_with_commonly_at_3_4():                 # codex2
    src = dict(SRC, text="A trial of treatment for schizophrenia.")
    why = "in schizophrenia, continuing symptoms commonly make dropout more likely"
    v = cx.verify(_reading(("3.4", "PY", "A trial of treatment for schizophrenia", SRC["id"], why)), [src], ["3.4"])
    assert v["3.4"]["answer"] == "PY"
    # ... while "what trials usually do" still is not context for a question about a trial's own conduct
    why2 = "central web-based randomisation is commonly concealed"
    assert cx.verify(_reading(("1.2", "PY", QUOTE, SRC["id"], why2)), [SRC], ["1.2"])["1.2"]["answer"] == "NI"


def test_PLANT_r6_every_post_registration_decision_record_must_be_consumed():   # codex3, codex4, codex5
    held = {"mc-c": "RAN_OK", "mc-a": "RAN_OK", "mc-x": "RAN_ERROR"}
    cs.check_consumed(consumed={"mc-c", "mc-a"}, held=held)              # a failed retry attempt is accounted for
    with pytest.raises(SystemExit, match="not consumed"):
        cs.check_consumed(consumed={"mc-c"}, held=held)                 # a parked RAN_OK record (e.g. an unused pass)


def test_PLANT_r6_a_consumed_record_must_postdate_the_preregistration():   # codex4
    with pytest.raises(SystemExit, match="predates"):
        cs.check_consumed_times({"mc-old"}, AFTER, record_time=lambda rid: "2026-10-12T19:00:00+00:00")
    cs.check_consumed_times({"mc-new"}, AFTER, record_time=lambda rid: "2026-10-12T23:00:00+00:00")


def test_PLANT_r6_process_drops_unexecuted_passes_and_reports_consumed(monkeypatch):   # codex3
    import rob2_contextual as rc
    base = _obj(dict(BASE))                                               # targets 1.2, 5.1
    item = {"pmid": "1", "nct": None, "outcome": "o", "key": "s::1::o", "sources": [SRC]}
    monkeypatch.setattr(rc.rd, "open_sources", lambda it: [SRC])
    monkeypatch.setattr(rc, "prompt", lambda it, targets, kind="reader", readings=None: ("P:" + ",".join(targets)).encode())
    monkeypatch.setattr(rc, "fresh", lambda run, p: run if run and run.get("state") == "RAN_OK" else None)
    monkeypatch.setattr(rc, "_reading", lambda run: {"answers": []})
    runs = {"s::1::o": {"passes": [{"codex": {"state": "RAN_OK", "record_id": "mc-c"},
                                    "agy": {"state": "RAN_OK", "record_id": "mc-a"}},
                                   {"codex": {"state": "RAN_OK", "record_id": "mc-parked"},
                                    "agy": {"state": "RAN_OK", "record_id": "mc-parked2"}}]}}
    new, r, c = rc.process(item, base, runs, False, {})
    assert len(r["passes"]) == 1                                          # the unexecuted pass is dropped
    assert set(r["consumed"]) == {"mc-c", "mc-a"}
