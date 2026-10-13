"""AMENDMENT A2 to the pre-registered contextual-answer rule (signed: Mahmood via Dispatch, 13 Oct 2026,
outputs/robgrade/SIGNING_A2.md). Written BEFORE the amendment and run failing first.

The defect: the pipeline parsed a reply strictly (scripts/rob2_dual.parse), the scorer leniently. agy began 15 of 58
contextual replies with prose, so the pipeline read agy as answering NI to everything; agreements became
disagreements and went to the adjudicator. The pre-registered scorer refused to score."""
import inspect
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from robgrade import contextual as cx  # noqa: E402
import rob2_contextual as rc  # noqa: E402
import rob2_ctx_score as cs  # noqa: E402
import rob2_dual as rd  # noqa: E402

REPLY = {"answers": [{"qid": "1.2", "answer": "PY", "quote": "central web-based randomisation", "source_id": "a",
                      "rationale": "central web-based randomisation means concealed"}], "notes": ""}
PROSE = ("I am checking the workspace files to see if there is any existing script.\n```json\n" +
         json.dumps(REPLY) + "\n```\n").encode("utf-8")


# ---- part 1: ONE reply parser, everywhere
def test_PLANT_a2_parse_reply_reads_a_prose_prefixed_reply():
    assert cx.parse_reply(PROSE) == REPLY
    assert cx.parse_reply(json.dumps(REPLY).encode()) == REPLY
    assert cx.parse_reply(b"no json here") is None
    assert cx.parse_reply(b'{"verdict": "x"}') is None                  # a JSON object without an answers list


def test_PLANT_a2_the_pipeline_the_scorer_and_the_dual_reading_use_the_same_parser():
    assert rd.parse(PROSE) == REPLY                                        # the dual reading (was None: strict JSON)
    assert "cx.parse_reply(" in inspect.getsource(rc._reading)             # the contextual pipeline
    assert "cx.parse_reply(" in inspect.getsource(cs._verified)            # the scorer
    assert "parse_reply(" in inspect.getsource(rd.parse)


def test_PLANT_a2_a_prose_prefixed_agreement_is_an_agreement():
    src = {"id": "a", "text": "Allocation by central web-based randomisation.", "sha256": "a" * 64, "open_for_prompt": True}
    a = cx.verify(cx.parse_reply(json.dumps(REPLY).encode()), [src], ["1.2"])
    b = cx.verify(cx.parse_reply(PROSE), [src], ["1.2"])
    c = rc.pass_decisions(a, b, {}, ["1.2"])
    assert c["1.2"]["answer"] == "PY" and c["1.2"]["decided_by"] == "both readers"


# ---- part 2: the contextual scorer accepts declared, SIGNED amendments (real git, as A1)
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


def _git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), "-c", "core.hooksPath=/dev/null", *a], check=True, env=ENV,
                          capture_output=True, text=True, encoding="utf-8").stdout.strip()


def _repo(tmp_path, signed=True, edit_after=False, superseded=(), commit_amendment=True):
    repo = tmp_path / "r"
    (repo / "scripts").mkdir(parents=True)
    (repo / "outputs" / "robgrade").mkdir(parents=True)
    (repo / "scripts" / "rob2_contextual.py").write_text("v1\n", encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "prereg")
    sha = _git(repo, "rev-parse", "HEAD")
    (repo / "scripts" / "rob2_contextual.py").write_text("v2 amended\n", encoding="utf-8")
    entry = {"id": "A2", "file": "scripts/rob2_contextual.py", "prereg": sha,
             "from_blob": _git(repo, "rev-parse", f"{sha}:scripts/rob2_contextual.py"),
             "to_blob": _git(repo, "hash-object", "--", "scripts/rob2_contextual.py"),
             # bound to exactly the reviewed change (round 8): the sha256 of the file's diff from the pre-registration
             "patch_sha256": __import__("hashlib").sha256(subprocess.run(
                 ["git", "-C", str(repo), "diff", sha, "--", "scripts/rob2_contextual.py"], capture_output=True,
                 text=True, encoding="utf-8").stdout.encode("utf-8")).hexdigest(),
             "superseded_records": list(superseded)}
    if signed:
        entry["signed"] = {"by": "Mahmood", "via": "Dispatch", "date": "2026-10-13"}
    (repo / "outputs" / "robgrade" / "AMENDMENTS.json").write_text(json.dumps({"amendments": [entry]}), encoding="utf-8")
    if commit_amendment:                               # round 9: a declaration counts only once committed
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "amendment")
    if edit_after:
        (repo / "scripts" / "rob2_contextual.py").write_text("v3 edited after\n", encoding="utf-8")
    return repo, sha


def _use(monkeypatch, repo):
    monkeypatch.setattr(cs, "ROOT", str(repo))
    monkeypatch.setattr(cs, "AMENDMENTS", str(repo / "outputs" / "robgrade" / "AMENDMENTS.json"))


def test_PLANT_a2_a_signed_declared_amendment_is_accepted(tmp_path, monkeypatch):
    repo, sha = _repo(tmp_path)
    _use(monkeypatch, repo)
    assert cs.declared(sha, "scripts/rob2_contextual.py") is True


def test_PLANT_a2_an_unsigned_or_later_edited_amendment_is_refused(tmp_path, monkeypatch):
    repo, sha = _repo(tmp_path, signed=False)
    _use(monkeypatch, repo)
    assert cs.declared(sha, "scripts/rob2_contextual.py") is False
    repo2, sha2 = _repo(tmp_path / "b", edit_after=True)
    _use(monkeypatch, repo2)
    assert cs.declared(sha2, "scripts/rob2_contextual.py") is False


# ---- part 3: the defect's adjudications are KEPT, and accounted for only as declared superseded records
def test_PLANT_a2_superseded_records_come_only_from_a_signed_amendment(tmp_path, monkeypatch):
    repo, sha = _repo(tmp_path, superseded=["mc-adj-1", "mc-adj-2"])
    _use(monkeypatch, repo)
    assert cs.superseded_records(sha) == {"mc-adj-1", "mc-adj-2"}
    repo2, sha2 = _repo(tmp_path / "b", signed=False, superseded=["mc-adj-1"])
    _use(monkeypatch, repo2)
    assert cs.superseded_records(sha2) == set()


def test_PLANT_a2_a_superseded_record_is_accounted_for_and_never_read():
    held = {"mc-c": "RAN_OK", "mc-a": "RAN_OK", "mc-adj-old": "RAN_OK"}
    cs.check_consumed({"mc-c", "mc-a"}, held, superseded={"mc-adj-old"})          # kept, accounted for
    with pytest.raises(SystemExit, match="not consumed"):
        cs.check_consumed({"mc-c", "mc-a"}, held, superseded=set())                # undeclared: an omission
    with pytest.raises(SystemExit, match="superseded"):
        cs.check_consumed({"mc-c", "mc-a", "mc-adj-old"}, held, superseded={"mc-adj-old"})   # read: not superseded


# ---- part 4: the re-run reuses every fresh reader record (a parser change does not change a prompt)
def test_PLANT_a2_reader_prompts_are_unchanged_by_the_amendment():
    # the reader prompt is built only from prompt_head + evidence: the parser is not part of it, so every recorded
    # reader call stays fresh and is reused; only adjudications over the corrected readings are new
    src = inspect.getsource(rc.prompt_head) + inspect.getsource(rc.prompt)
    assert "parse" not in src


# ================= review of A2 (round 7; codex REVISE 8, agy RAN_ERROR): failing-first tests =================
def test_PLANT_a2r_braces_in_prose_do_not_hide_the_answer_object():         # codex6
    assert cx.parse_reply(("Note {draft}.\n" + json.dumps(REPLY)).encode()) == REPLY
    assert cx.parse_reply((json.dumps(REPLY) + "\nNote {end}.").encode()) == REPLY


def test_PLANT_a2r_two_answer_objects_are_ambiguous():                       # codex2, codex6
    other = dict(REPLY, answers=[dict(REPLY["answers"][0], answer="PN")])
    assert cx.parse_reply((json.dumps(REPLY) + "\n" + json.dumps(other)).encode()) is None


def test_PLANT_a2r_duplicate_keys_are_ambiguous():                          # codex4
    dup = '{"answers": [{"qid": "1.2", "answer": "PY", "answer": "PN", "quote": "q", "source_id": "a", "rationale": "r"}], "notes": ""}'
    assert cx.parse_reply(dup.encode()) is None


def test_PLANT_a2r_conflicting_rows_for_one_question_are_ni():              # codex4
    src = {"id": "a", "text": "Allocation by central web-based randomisation.", "sha256": "a" * 64, "open_for_prompt": True}
    row = REPLY["answers"][0]
    both = {"answers": [row, dict(row, answer="PN")], "notes": ""}
    v = cx.verify(both, [src], ["1.2"])
    assert v["1.2"]["answer"] == "NI" and v["1.2"]["dropped"]["why"] == "AMBIGUOUS_CONFLICTING_ROWS"
    v = cx.verify({"answers": [dict(row, answer="PN"), row], "notes": ""}, [src], ["1.2"])     # either order
    assert v["1.2"]["answer"] == "NI"


def test_PLANT_a2r_an_unreadable_reply_voids_the_pass_like_a_missing_reader(monkeypatch):   # codex2
    monkeypatch.setattr(rc, "fresh", lambda run, p: run if run and run.get("state") == "RAN_OK" else None)
    monkeypatch.setattr(rc, "prompt", lambda it, targets, kind="reader", readings=None: b"P")
    replies = {"mc-c": {"answers": [dict(REPLY["answers"][0], source_id="a")], "notes": ""}, "mc-a": None}
    monkeypatch.setattr(rc, "_reading", lambda run: replies.get(run["record_id"]) if run else None)
    src = {"id": "a", "text": "Allocation by central web-based randomisation.", "sha256": "a" * 64, "open_for_prompt": True}
    run = {"codex": {"state": "RAN_OK", "record_id": "mc-c"}, "agy": {"state": "RAN_OK", "record_id": "mc-a"},
           "adjudicator": {"state": "RAN_OK", "record_id": "mc-j"}}
    obj = _base_obj()
    new, c, used = rc._one_pass({"pmid": "1", "nct": None, "outcome": "o"}, obj, ["1.2"], run, False, {}, [src])
    assert c["1.2"]["answer"] == "NI" and "missing or failed" in c["1.2"]["decided_by"]
    assert "mc-j" not in used                                              # no adjudication between one reader and nobody


def _base_obj():
    from robgrade import rob2_formal as rf
    a = lambda v, q: rf.answer(v, how="t", span=f"s {q}", source_sha256="0" * 64) if v != "NI" else rf.answer("NI", how="t")
    spec = {"1.1": "Y", "1.2": "NI", "1.3": "N", "2.1": "N", "2.2": "N", "2.6": "Y", "3.1": "Y", "4.1": "N", "4.2": "N",
            "4.3": "N", "5.1": "Y", "5.2": "N", "5.3": "N"}
    return rf.assessment("PMID 1", "o", {q: a(v, q) for q, v in spec.items()})


def test_PLANT_a2r_only_the_a2_code_files_can_be_declared(tmp_path, monkeypatch):   # codex0
    repo, sha = _repo(tmp_path)
    _use(monkeypatch, repo)
    doc = json.loads((repo / "outputs/robgrade/AMENDMENTS.json").read_text(encoding="utf-8"))
    doc["amendments"][0]["file"] = "outputs/robgrade/calibration_v31.json"     # an INPUT can never be amended
    (repo / "outputs/robgrade/AMENDMENTS.json").write_text(json.dumps(doc), encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "x")
    assert cs.declared(sha, "outputs/robgrade/calibration_v31.json") is False


def test_PLANT_a2r_only_mahmoods_signature_counts(tmp_path, monkeypatch):    # codex0
    repo, sha = _repo(tmp_path)
    _use(monkeypatch, repo)
    doc = json.loads((repo / "outputs/robgrade/AMENDMENTS.json").read_text(encoding="utf-8"))
    doc["amendments"][0]["signed"]["by"] = "someone"
    (repo / "outputs/robgrade/AMENDMENTS.json").write_text(json.dumps(doc), encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "x")
    assert cs.declared(sha, "scripts/rob2_contextual.py") is False


def test_PLANT_a2r_a_superseded_record_must_be_a_held_earlier_adjudication():   # codex1
    held = {"mc-c": "RAN_OK", "mc-a": "RAN_OK", "mc-j": "RAN_OK"}
    roles = {"mc-c": "codex", "mc-a": "agy", "mc-j": "adjudicator"}
    times = {"mc-c": "2026-10-13T08:00:00+00:00", "mc-a": "2026-10-13T08:00:00+00:00", "mc-j": "2026-10-13T08:00:00+00:00"}
    amended = "2026-10-13T12:00:00+00:00"
    cs.check_superseded({"mc-j"}, held, roles, times, amended)                       # an earlier adjudication: fine
    with pytest.raises(SystemExit, match="adjudicator"):
        cs.check_superseded({"mc-c"}, held, roles, times, amended)                   # a reader: never
    with pytest.raises(SystemExit, match="not held"):
        cs.check_superseded({"mc-gone"}, held, roles, times, amended)
    with pytest.raises(SystemExit, match="after the amendment"):
        cs.check_superseded({"mc-j"}, held, roles, dict(times, **{"mc-j": "2026-10-13T13:00:00+00:00"}), amended)


def test_PLANT_a2r_preflight_lists_every_call_the_rerun_would_make(monkeypatch):    # codex7
    monkeypatch.setattr(rc, "fresh", lambda run, p: run if run and run.get("state") == "RAN_OK" else None)
    monkeypatch.setattr(rc, "prompt", lambda it, targets, kind="reader", readings=None: b"P")
    monkeypatch.setattr(rc, "_reading", lambda run: None)
    monkeypatch.setattr(rc.rd, "open_sources", lambda it: [])
    item = {"pmid": "1", "nct": None, "outcome": "o", "key": "s::1::o"}
    calls = rc.preflight(item, _base_obj(), {"s::1::o": {"passes": [{"codex": {"state": "RAN_OK", "record_id": "c"}}]}})
    assert calls == [(0, "agy")]                                             # codex is reused; agy would be called


# ================= review of A2 (round 8; codex REVISE 7, agy quota exhausted): failing-first tests =================
def test_PLANT_a2r8_a_malformed_envelope_makes_the_reply_ambiguous():       # codex3
    assert cx.parse_reply(b'{"answers":{"answers":[]},"answers":[]}') is None
    row = json.dumps(REPLY["answers"][0])
    assert cx.parse_reply(('{"answers": {"answers": [' + row + ']}, "answers": []}').encode()) is None


def test_PLANT_a2r8_a_row_that_is_not_an_object_makes_the_reply_unreadable():   # codex4
    assert cx.parse_reply(b'{"answers": [42], "notes": ""}') is None
    assert cx.parse_reply(('{"answers": [' + json.dumps(REPLY["answers"][0]) + ', "x"], "notes": ""}').encode()) is None


def test_PLANT_a2r8_a_closed_branch_keeps_its_contextual_decision_visible():   # codex6
    from robgrade import rob2_formal as rf
    a = lambda v, q: rf.answer(v, how="t", span=f"s {q}", source_sha256="0" * 64) if v != "NI" else rf.answer("NI", how="t")
    spec = {"1.1": "Y", "1.2": "Y", "1.3": "N", "2.1": "N", "2.2": "N", "2.6": "Y", "3.1": "NI", "3.3": "NI", "3.4": "NI",
            "4.1": "N", "4.2": "N", "4.3": "N", "5.1": "Y", "5.2": "N", "5.3": "N"}
    obj = rf.assessment("PMID 1", "o", {q: a(v, q) for q, v in spec.items()})
    ctx = lambda q, quote: {"answer": "PY", "quote": quote, "source_id": "s", "source_sha256": "a" * 64, "rationale": "r",
                            "decided_by": "both readers", "context": [{"who": "reader 1", "quote": quote, "source_id": "s",
                                                                       "source_sha256": "a" * 64, "rationale": "r"}]}
    new = cx.apply(obj, {"3.1": ctx("3.1", "data complete for all"), "3.3": ctx("3.3", "dropout linked to symptoms")},
                   records={"3.1": ["x"], "3.3": ["x"]})
    assert new["domains"]["D3"]["answers"]["3.3"]["answer"] == "NA"
    assert new["contextual_audit"]["3.3"]["context"][0]["quote"] == "dropout linked to symptoms"   # kept in the audit
    assert new["domains"]["D3"]["answers"]["3.3"]["closed_contextual"]["answer"] == "PY"           # and on the answer
    # RENDERING it is out of A2's signed scope (robgrade/rob2_tab.py is frozen and not amendable): it goes with the
    # served-tab signing


def _rec_legacy(who, reply_text, trial="1", outcome="o", qid="1.2"):
    import rob2_contextual as rcm
    head = rcm.prompt_head(trial, None, outcome, [qid], "reader")
    return {"state": "RAN_OK", "caller": {"line": f"call:{who}"}, "prompt_text": head + rcm.EVIDENCE_MARK + '{"sources": []}',
            "reply": reply_text, "input_digests": [], "request_utc": "2026-10-13T08:00:00+00:00"}


def _adj_legacy(readings, trial="1", outcome="o", qid="1.2"):
    import rob2_contextual as rcm
    head = rcm.prompt_head(trial, None, outcome, [qid], "adjudicator", readings)
    return {"state": "RAN_OK", "caller": {"line": "call:adjudicator"}, "prompt_text": head + rcm.EVIDENCE_MARK + '{"sources": []}',
            "reply": "{}", "input_digests": [], "request_utc": "2026-10-13T08:00:00+00:00"}


def test_PLANT_a2r8_supersession_must_be_proven_defect_caused():           # codex0
    unread = {"answer": "NI", "rationale": None}                          # what verify(None) gave the old pipeline
    ok_row = {"answer": "PY", "quote": "q", "source_id": "s", "source_sha256": "a" * 64, "rationale": "r"}
    prose = "I am checking the workspace files.\n" + json.dumps(REPLY)     # unreadable to the OLD strict parser
    recs = {"mc-c": _rec_legacy("codex", json.dumps(REPLY)), "mc-a": _rec_legacy("agy", prose),
            "mc-j": _adj_legacy({"1.2": {"reader 1": ok_row, "reader 2": unread}})}
    # CORRECTED in round 10 (codex1): this reader saw no sources, so its PY verifies to NI under A2 too -- the
    # disagreement was genuine, not defect-caused (the round-8 expected value True was wrong; see test_PLANT_a2r10_*)
    assert cs.defect_caused("mc-j", recs.get, list(recs)) is False
    # a GENUINE disagreement (both readers readable, both read): not defect-caused, cannot be superseded
    recs2 = {"mc-c": _rec_legacy("codex", json.dumps(REPLY)), "mc-a": _rec_legacy("agy", json.dumps(REPLY)),
             "mc-j": _adj_legacy({"1.2": {"reader 1": ok_row, "reader 2": dict(ok_row, answer="PN")}})}
    assert cs.defect_caused("mc-j", recs2.get, list(recs2)) is False


def test_PLANT_a2r8_declarations_are_bound_to_the_reviewed_patch(tmp_path, monkeypatch):   # codex1
    repo, sha = _repo(tmp_path)
    _use(monkeypatch, repo)
    doc = json.loads((repo / "outputs/robgrade/AMENDMENTS.json").read_text(encoding="utf-8"))
    patch = subprocess.run(["git", "-C", str(repo), "diff", sha, "--", "scripts/rob2_contextual.py"], capture_output=True,
                           text=True, encoding="utf-8").stdout
    import hashlib
    doc["amendments"][0]["patch_sha256"] = hashlib.sha256(patch.encode("utf-8")).hexdigest()
    (repo / "outputs/robgrade/AMENDMENTS.json").write_text(json.dumps(doc), encoding="utf-8")
    assert cs.declared(sha, "scripts/rob2_contextual.py") is True
    doc["amendments"][0]["patch_sha256"] = "0" * 64                        # not the reviewed patch
    (repo / "outputs/robgrade/AMENDMENTS.json").write_text(json.dumps(doc), encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "x")
    assert cs.declared(sha, "scripts/rob2_contextual.py") is False


# ================= review of A2 (round 9; codex REVISE 7, agy quota): failing-first tests =================
def test_PLANT_a2r9_a_broken_outer_envelope_makes_the_reply_unreadable():   # codex2
    valid = json.dumps(REPLY)
    assert cx.parse_reply(('{"answers":' + valid + ',').encode()) is None
    assert cx.parse_reply(('{ "answers" : [' + valid).encode()) is None


def test_PLANT_a2r9_a_genuinely_empty_reader_is_not_a_defect(tmp_path):    # codex1
    unread = {"answer": "NI", "rationale": None}
    ok_row = {"answer": "PY", "quote": "q", "source_id": "s", "source_sha256": "a" * 64, "rationale": "r"}
    empty = 'Prose first. {"answers": [], "notes": ""}'                   # unreadable to the old parser, EMPTY under A2
    recs = {"mc-c": _rec_legacy("codex", json.dumps(REPLY)), "mc-a": _rec_legacy("agy", empty),
            "mc-j": _adj_legacy({"1.2": {"reader 1": ok_row, "reader 2": unread}})}
    assert cs.defect_caused("mc-j", recs.get, list(recs)) is False       # the reader really gave no answer


def test_PLANT_a2r9_the_reader_record_must_be_for_the_same_pass():         # codex1
    unread = {"answer": "NI", "rationale": None}
    ok_row = {"answer": "PY", "quote": "q", "source_id": "s", "source_sha256": "a" * 64, "rationale": "r"}
    prose = "I am checking.\n" + json.dumps(REPLY)
    # the only prose reader record is for ANOTHER question set (a different pass): not this adjudication's reader
    recs = {"mc-c": _rec_legacy("codex", json.dumps(REPLY)), "mc-a": _rec_legacy("agy", prose, qid="5.1"),
            "mc-j": _adj_legacy({"1.2": {"reader 1": ok_row, "reader 2": unread}})}
    assert cs.defect_caused("mc-j", recs.get, list(recs)) is False


def test_PLANT_a2r9_declarations_are_read_from_the_committed_history(tmp_path, monkeypatch):   # codex0
    repo, sha = _repo(tmp_path, commit_amendment=False)
    _use(monkeypatch, repo)
    assert cs.declared(sha, "scripts/rob2_contextual.py") is False       # uncommitted declaration and code: not yet
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "amend")
    assert cs.declared(sha, "scripts/rob2_contextual.py") is True        # committed through history: declared
    (repo / "scripts" / "rob2_contextual.py").write_text("v3 changed after the commit\n", encoding="utf-8")
    assert cs.declared(sha, "scripts/rob2_contextual.py") is False       # the working file differs from the commit


# ================= review of A2 (round 10; codex REVISE 8, agy ACCEPT): failing-first tests =================
def test_PLANT_a2r10_a_broken_envelope_with_another_first_key_is_unreadable():   # codex3
    valid = json.dumps(REPLY)
    assert cx.parse_reply(('{"notes":"","answers":' + valid + ',').encode()) is None
    assert cx.parse_reply(('{"notes": "x", "answers": [' + valid).encode()) is None
    assert cx.parse_reply(("Prose. " + valid + " More prose.").encode()) == REPLY      # unchanged: a valid reply reads


SRC_Q = {"id": "s", "text": "Allocation by central web-based randomisation.", "sha256": "a" * 64}


def _rec_src(who, reply_text, qid="1.2", utc="2026-10-13T08:00:00+00:00", text=SRC_Q["text"]):
    import rob2_contextual as rcm
    head = rcm.prompt_head("1", None, "o", [qid], "reader")
    ev = json.dumps({"sources": [{"id": "s", "kind": "abstract", "abstract": text}]})
    return {"state": "RAN_OK", "caller": {"line": f"call:{who}"}, "prompt_text": head + rcm.EVIDENCE_MARK + ev,
            "reply": reply_text, "input_digests": [{"ref": "s", "sha256": SRC_Q["sha256"]}], "request_utc": utc}


def _adj_src(readings, utc="2026-10-13T09:00:00+00:00", text=SRC_Q["text"]):
    import rob2_contextual as rcm
    head = rcm.prompt_head("1", None, "o", ["1.2"], "adjudicator", readings)
    ev = json.dumps({"sources": [{"id": "s", "kind": "abstract", "abstract": text}]})
    return {"state": "RAN_OK", "caller": {"line": "call:adjudicator"}, "prompt_text": head + rcm.EVIDENCE_MARK + ev,
            "reply": "{}", "input_digests": [{"ref": "s", "sha256": SRC_Q["sha256"]}], "request_utc": utc}


GOOD = {"answers": [{"qid": "1.2", "answer": "PY", "quote": "central web-based randomisation", "source_id": "s",
                     "rationale": "central web-based randomisation means concealed"}], "notes": ""}
UNREAD_ = {"answer": "NI", "rationale": None}


def test_PLANT_a2r10_a_defect_needs_a_changed_ANSWER():                     # codex1
    ok_row = {"answer": "PY", "quote": "q", "source_id": "s", "source_sha256": "a" * 64, "rationale": "r"}
    # the hidden reply really says PY (its source IS in its prompt): the defect turned PY into the unread NI
    recs = {"mc-c": _rec_src("codex", json.dumps(GOOD)), "mc-a": _rec_src("agy", "Checking.\n" + json.dumps(GOOD)),
            "mc-j": _adj_src({"1.2": {"reader 1": ok_row, "reader 2": UNREAD_}})}
    assert cs.defect_caused("mc-j", recs.get, list(recs)) is True
    # the hidden reply is an explicit NI with a rationale: NI either way -- the adjudication was genuine
    ni = {"answers": [{"qid": "1.2", "answer": "NI", "quote": "", "source_id": "", "rationale": "nothing said"}], "notes": ""}
    recs2 = dict(recs, **{"mc-a": _rec_src("agy", "Checking.\n" + json.dumps(ni))})
    assert cs.defect_caused("mc-j", recs2.get, list(recs2)) is False


def test_PLANT_a2r10_the_reader_must_predate_the_adjudication_and_share_its_evidence():   # codex2
    ok_row = {"answer": "PY", "quote": "q", "source_id": "s", "source_sha256": "a" * 64, "rationale": "r"}
    adj = _adj_src({"1.2": {"reader 1": ok_row, "reader 2": UNREAD_}})
    later = {"mc-c": _rec_src("codex", json.dumps(GOOD)),
             "mc-a": _rec_src("agy", "Checking.\n" + json.dumps(GOOD), utc="2026-10-13T10:00:00+00:00"), "mc-j": adj}
    assert cs.defect_caused("mc-j", later.get, list(later)) is False         # made after the adjudication
    other_ev = {"mc-c": _rec_src("codex", json.dumps(GOOD)),
                "mc-a": _rec_src("agy", "Checking.\n" + json.dumps(GOOD),
                                 text="Allocation by central web-based randomisation; other evidence."), "mc-j": adj}
    assert cs.defect_caused("mc-j", other_ev.get, list(other_ev)) is False   # a different evidence block


def test_PLANT_a2r10_an_unreadable_adjudicator_reply_decides_nothing(monkeypatch):   # codex7
    monkeypatch.setattr(rc, "fresh", lambda run, p: run if run and run.get("state") == "RAN_OK" else None)
    monkeypatch.setattr(rc, "prompt", lambda it, targets, kind="reader", readings=None: kind.encode())
    src = {"id": "a", "text": "Allocation by central web-based randomisation.", "sha256": "a" * 64, "open_for_prompt": True}
    row = dict(REPLY["answers"][0])
    replies = {"mc-c": {"answers": [row], "notes": ""}, "mc-a": {"answers": [dict(row, answer="PN")], "notes": ""},
               "mc-j": None}
    monkeypatch.setattr(rc, "_reading", lambda run: replies.get(run["record_id"]) if run else None)
    monkeypatch.setattr(rc, "record_prompt_sha256", lambda rid: __import__("hashlib").sha256(b"adjudicator").hexdigest()
                        if rid == "mc-j" else None)    # r12: the adjudicator record is HELD, for this prompt
    run = {"codex": {"state": "RAN_OK", "record_id": "mc-c"}, "agy": {"state": "RAN_OK", "record_id": "mc-a"},
           "adjudicator": {"state": "RAN_OK", "record_id": "mc-j",      # r11: an attempt on THIS prompt is on record
                           "prompt_sha256": __import__("hashlib").sha256(b"adjudicator").hexdigest()}}
    new, c, used = rc._one_pass({"pmid": "1", "nct": None, "outcome": "o"}, _base_obj(), ["1.2"], run, False, {}, [src])
    assert c["1.2"]["answer"] == "NI" and c["1.2"]["decided_by"] != "adjudicator"


# ================= review of A2 (round 11; codex REVISE 7, agy ACCEPT): failing-first tests =================
def test_PLANT_a2r11_an_escaped_answers_key_is_still_an_envelope():                 # codex2
    valid = json.dumps(REPLY)
    key = '"' + chr(92) + 'u0061nswers"'                  # the JSON escape of "answers": decodes to the same key
    assert cx.parse_reply(("{" + key + ": [" + valid).encode()) is None
    assert cx.parse_reply(('{"notes": "", ' + key + ": " + valid + ",").encode()) is None
    # a WELL-FORMED envelope with the escaped key is still read
    assert cx.parse_reply(json.dumps(REPLY).replace('"answers"', key).encode()) == REPLY


def _disagreeing(monkeypatch):
    import hashlib
    monkeypatch.setattr(rc, "fresh", lambda run, p: run if run and run.get("state") == "RAN_OK"
                        and run.get("prompt_sha256") == hashlib.sha256(p).hexdigest() else None)
    monkeypatch.setattr(rc, "prompt", lambda it, targets, kind="reader", readings=None: kind.encode())
    row = dict(REPLY["answers"][0])
    replies = {"mc-c": {"answers": [row], "notes": ""}, "mc-a": {"answers": [dict(row, answer="PN")], "notes": ""}}
    monkeypatch.setattr(rc, "_reading", lambda run: replies.get(run["record_id"]) if run else None)
    sha = hashlib.sha256(b"reader").hexdigest()
    src = {"id": "a", "text": "Allocation by central web-based randomisation.", "sha256": "a" * 64, "open_for_prompt": True}
    return {"codex": {"state": "RAN_OK", "record_id": "mc-c", "prompt_sha256": sha},
            "agy": {"state": "RAN_OK", "record_id": "mc-a", "prompt_sha256": sha}}, src


def test_PLANT_a2r11_a_replayed_disagreement_never_adjudicated_refuses(monkeypatch):   # codex0
    run, src = _disagreeing(monkeypatch)
    item = {"pmid": "1", "nct": None, "outcome": "o"}
    with pytest.raises(rc.MissingAdjudication):
        rc._one_pass(item, _base_obj(), ["1.2"], dict(run), False, {}, [src])
    # a superseded (defect-run) adjudication answered a DIFFERENT prompt: it is not this disagreement's adjudication
    old = dict(run, adjudicator={"state": "RAN_OK", "record_id": "mc-old", "prompt_sha256": "0" * 64})
    with pytest.raises(rc.MissingAdjudication):
        rc._one_pass(item, _base_obj(), ["1.2"], old, False, {}, [src])


def test_PLANT_a2r11_a_recorded_failed_adjudication_is_an_honest_NI(monkeypatch):
    import hashlib
    run, src = _disagreeing(monkeypatch)
    run["adjudicator"] = {"state": "RAN_ERROR", "record_id": "mc-x", "prompt_sha256": hashlib.sha256(b"adjudicator").hexdigest()}
    monkeypatch.setattr(rc, "record_prompt_sha256", lambda rid: hashlib.sha256(b"adjudicator").hexdigest()
                        if rid == "mc-x" else None)    # r12: the failed attempt is HELD, for this prompt
    new, c, used = rc._one_pass({"pmid": "1", "nct": None, "outcome": "o"}, _base_obj(), ["1.2"], run, False, {}, [src])
    assert c["1.2"]["answer"] == "NI" and c["1.2"]["decided_by"] != "adjudicator"


# ================= review of A2 (round 12; codex REVISE 6, agy ACCEPT): failing-first tests =================
def test_PLANT_a2r12_a_manifest_hash_without_a_held_attempt_is_no_adjudication(monkeypatch):   # codex0
    import hashlib
    run, src = _disagreeing(monkeypatch)
    want = hashlib.sha256(b"adjudicator").hexdigest()
    run["adjudicator"] = {"state": "RAN_ERROR", "record_id": "mc-gone", "prompt_sha256": want}
    monkeypatch.setattr(rc, "record_prompt_sha256", lambda rid: None)            # not held
    with pytest.raises(rc.MissingAdjudication):
        rc._one_pass({"pmid": "1", "nct": None, "outcome": "o"}, _base_obj(), ["1.2"], dict(run), False, {}, [src])
    monkeypatch.setattr(rc, "record_prompt_sha256", lambda rid: "1" * 64)       # held, but answered another prompt
    with pytest.raises(rc.MissingAdjudication):
        rc._one_pass({"pmid": "1", "nct": None, "outcome": "o"}, _base_obj(), ["1.2"], dict(run), False, {}, [src])


def test_PLANT_a2r12_a_row_field_of_the_wrong_type_makes_the_reply_unreadable():   # codex4
    for field, bad in (("answer", ["PY"]), ("qid", ["1.2"]), ("quote", {"q": 1}), ("source_id", 3),
                       ("rationale", ["r"])):
        row = dict(REPLY["answers"][0], **{field: bad})
        assert cx.parse_reply(json.dumps({"answers": [row], "notes": ""}).encode()) is None, field


# ================= review of A2 (round 13; codex REVISE 5, agy ACCEPT): failing-first tests =================
def test_PLANT_a2r13_a_key_mentioned_in_prose_is_not_a_broken_envelope():          # codex4
    valid = json.dumps(REPLY)
    assert cx.parse_reply(('The field "answers": holds one row per question.\n' + valid).encode()) == REPLY
    assert cx.parse_reply(('I return "answers":\n```json\n' + valid + '\n```').encode()) == REPLY
    # ... but an "answers" KEY of a broken object (after '{' or ',') still voids the reply (rounds 9-11)
    assert cx.parse_reply(('{"notes": "",  "answers": ' + valid + ',').encode()) is None
    assert cx.parse_reply(('{ "answers": [' + valid).encode()) is None


def test_PLANT_a2r13_the_defect_reader_must_be_the_UNIQUE_candidate():               # codex2
    ok_row = {"answer": "PY", "quote": "q", "source_id": "s", "source_sha256": "a" * 64, "rationale": "r"}
    adj = _adj_src({"1.2": {"reader 1": ok_row, "reader 2": UNREAD_}})
    one = {"mc-c": _rec_src("codex", json.dumps(GOOD)), "mc-a": _rec_src("agy", "Checking.\n" + json.dumps(GOOD)),
           "mc-j": adj}
    assert cs.defect_caused("mc-j", one.get, list(one)) is True
    # a second earlier agy attempt on the same targets and evidence: which one the adjudicator saw is not proven
    two = dict(one, **{"mc-a2": _rec_src("agy", "Checking.\n" + json.dumps(GOOD), utc="2026-10-13T08:30:00+00:00")})
    assert cs.defect_caused("mc-j", two.get, list(two)) is False


# ================= review of A2 (round 14; codex REVISE 5, agy ACCEPT): failing-first test =================
def test_PLANT_a2r14_a_broken_object_missing_its_comma_is_still_broken():             # codex0
    valid = json.dumps(REPLY)
    assert cx.parse_reply(('{"notes": "" "answers": ' + valid).encode()) is None
    assert cx.parse_reply(('{"notes": "}" "answers": ' + valid + "}").encode()) is None
    assert cx.parse_reply(('{"notes": "x"\n"answers": [' + valid).encode()) is None
    # the round-13 prose cases still read
    assert cx.parse_reply(('The field "answers": holds one row per question.\n' + valid).encode()) == REPLY
