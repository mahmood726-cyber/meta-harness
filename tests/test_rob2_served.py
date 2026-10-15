"""RoB 2 for the SERVED trial-topic pairs (D11 serving; Mahmood 13 Oct: "continue to the served trial-topic pairs").
Written BEFORE scripts/rob2_served.py and run failing first. The served driver reuses the frozen v3.1 dual reading
(scripts/rob2_dual) and the contextual pass under the A3 base (scripts/rob2_contextual) UNCHANGED, redirecting their
stores at run time: it never writes a frozen calibration object, a frozen record store, or a served (docs/) file."""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import rob2_contextual as rc  # noqa: E402
import rob2_dual as rd  # noqa: E402
import rob2_served as sv  # noqa: E402


@pytest.fixture(autouse=True)
def _private_stores(tmp_path, monkeypatch):
    """NO test may write a real served store (14 Oct: a test that called main() without mocking a new stage wrote the
    real served manifest). Every store points under tmp_path, keeping its path suffix."""
    for k, path in list(sv.STORES.items()):
        monkeypatch.setitem(sv.STORES, k, str(tmp_path / os.path.relpath(path, ROOT)))
    monkeypatch.setattr(sv, "SERVED", str(tmp_path / os.path.relpath(sv.SERVED, ROOT)))


def test_PLANT_served_pairs_are_the_primary_outcome_trials_of_every_served_review():
    pairs = sv.served_pairs()
    assert len(pairs) == 32                                           # every served review with a review.json
    assert sum(len(v) for v in pairs.values()) == 91                  # trials of the primary outcomes
    assert all(p.isdigit() for v in pairs.values() for p in v)


def test_PLANT_the_work_list_is_the_served_pairs_without_a_v31_object():
    todo, covered = sv.work_list()
    # 26 covered / 65 to read (an earlier hand count said 13 / 78: it loaded the calibration and DEV objects into one
    # dict per topic, so the 1-trial DEV probiotics object overwrote the 38-trial calibration one)
    assert sum(len(v) for v in covered.values()) == 26 and sum(len(v) for v in todo.values()) == 65
    for slug, pm in covered.items():                                 # covered = an existing frozen v3.1 object
        for p in pm:
            assert p not in todo.get(slug, [])


def test_PLANT_the_redirect_moves_every_store_and_restores_it():
    before = (rd.REC_DIR, rd.OUT_DIR, rd.RUNS, rc.OBJ_DIR, rc.BASE_OUT_DIR, rc.BASE_REC_DIR, rc.BASE_RUNS,
              rc.OUT_DIR, rc.REC_DIR, rc.RUNS, list(rc.REC_READ_DIRS), rc.VARIANT)
    with sv.redirected():
        assert rd.REC_DIR.endswith(os.path.join("evidence", "model_calls", "rob2_served"))
        assert rd.RUNS.endswith("rob2_served_runs.json")
        assert rd.OUT_DIR.endswith(os.path.join("outputs", "robgrade", "served", "rob2"))
        assert rc.OBJ_DIR == rd.OUT_DIR                                 # the contextual pass reads the served objects
        assert rc.REC_DIR.endswith(os.path.join("evidence", "model_calls", "rob2_served_ctx"))
        assert rc.REC_READ_DIRS == [rc.REC_DIR] and rc.VARIANT is None   # the A3 base, never a variant
        assert rc.RUNS.endswith("rob2_served_ctx_runs.json")
        assert rc.OUT_DIR.endswith(os.path.join("outputs", "robgrade", "served", "rob2_ctx"))
        frozen = {before[0], before[1], before[2], before[3], before[4], before[5], before[6]}
        assert not ({rd.REC_DIR, rd.OUT_DIR, rd.RUNS, rc.OUT_DIR, rc.REC_DIR, rc.RUNS} & frozen)
    after = (rd.REC_DIR, rd.OUT_DIR, rd.RUNS, rc.OBJ_DIR, rc.BASE_OUT_DIR, rc.BASE_REC_DIR, rc.BASE_RUNS,
             rc.OUT_DIR, rc.REC_DIR, rc.RUNS, list(rc.REC_READ_DIRS), rc.VARIANT)
    assert after == before


def test_PLANT_the_redirect_restores_even_when_the_run_fails():
    before = (rd.REC_DIR, rd.OUT_DIR, rd.RUNS, rc.OBJ_DIR, rc.OUT_DIR, rc.REC_DIR, rc.RUNS)
    with pytest.raises(RuntimeError):
        with sv.redirected():
            raise RuntimeError("a run stopped half way")
    assert (rd.REC_DIR, rd.OUT_DIR, rd.RUNS, rc.OBJ_DIR, rc.OUT_DIR, rc.REC_DIR, rc.RUNS) == before


def test_PLANT_the_served_driver_never_writes_a_served_page():
    # it READS docs/reviews (the served reviews define the pairs); every store it WRITES lies outside docs/
    docs = os.path.join(ROOT, "docs")
    for name, path in sv.STORES.items():
        assert os.path.commonpath([docs, path]) != docs, name
    with sv.redirected():
        for path in (rd.REC_DIR, rd.OUT_DIR, rd.RUNS, rc.OUT_DIR, rc.REC_DIR, rc.RUNS):
            assert os.path.commonpath([docs, path]) != docs, path


def test_PLANT_the_frozen_pipelines_are_reused_not_copied():
    src = open(os.path.join(ROOT, "scripts", "rob2_served.py"), encoding="utf-8").read()
    for fn in ("rd.items(", "rd.process", "rd.redact_closed_spans(", "rc.main("):
        assert fn in src, fn                                          # the frozen functions themselves
    for copied in ("def process(", "def evidence_block(", "def verify(", "def _one_pass("):
        assert copied not in src, copied                              # never a private copy of them


# ======================= review round 28 (codex REVISE 5, agy ACCEPT): failing-first tests =================
def test_PLANT_r28_a_failed_run_never_restores_the_stores_while_workers_may_live(monkeypatch):   # codex0
    seen = {}

    def boom(argv):
        raise RuntimeError("a contextual job failed while others were in flight")

    def die(code):
        seen["rec_dir_at_exit"] = rc.REC_DIR                   # still the SERVED store: nothing was restored yet
        raise SystemExit(code)
    monkeypatch.setattr(rc, "main", boom)
    monkeypatch.setattr(sv, "_die", die)
    monkeypatch.setattr(sv, "run_dual", lambda todo, live: None)
    for n in ("REC_DIR", "OUT_DIR", "RUNS"):
        monkeypatch.setattr(rd, n, getattr(rd, n))
    for n in ("OBJ_DIR", "BASE_OUT_DIR", "BASE_REC_DIR", "BASE_RUNS", "OUT_DIR", "REC_DIR", "RUNS", "REC_READ_DIRS",
              "VARIANT"):
        monkeypatch.setattr(rc, n, getattr(rc, n))
    with pytest.raises(SystemExit):
        sv.main([])
    assert seen["rec_dir_at_exit"] == sv.STORES["ctx_rec"]


def test_PLANT_r28_covered_means_the_same_trial_AND_the_same_outcome(tmp_path, monkeypatch):   # codex4
    d = tmp_path / "rob2"
    d.mkdir()
    (d / "t.json").write_text(json.dumps({"outcome": "hospitalisation", "trials": {"1": {}, "2": {}}}), encoding="utf-8")
    monkeypatch.setattr(sv, "V31_OBJECTS", [str(d)])
    monkeypatch.setattr(sv, "served_pairs", lambda: {"t": ["1", "2", "3"]})
    monkeypatch.setattr(sv.rd, "served_primary", lambda slug: ("mortality", ["1", "2", "3"]))
    todo, covered = sv.work_list()
    assert todo == {"t": ["1", "2", "3"]} and covered == {}           # another outcome's object covers nothing
    monkeypatch.setattr(sv.rd, "served_primary", lambda slug: ("hospitalisation", ["1", "2", "3"]))
    todo, covered = sv.work_list()
    assert todo == {"t": ["3"]} and covered == {"t": ["1", "2"]}


def test_PLANT_r28_every_manifest_record_carries_the_manifest_prompt(tmp_path, monkeypatch):   # codex1 (served guard)
    monkeypatch.setattr(sv, "_record_prompt_sha256", lambda d, rid: {"r-ok": "p", "r-stale": "OTHER"}.get(rid))
    monkeypatch.setattr(sv, "_record_state", lambda d, rid: "RAN_OK")          # r31: the state is checked too
    monkeypatch.setattr(sv, "_record_role", lambda d, rid: "codex")             # r32: and the role
    monkeypatch.setattr(sv, "_record_bound", lambda d, rid: None)               # r34: (unbound keys: not checked)
    sv.check_manifest_records({"k": {"codex": {"state": "RAN_OK", "record_id": "r-ok", "prompt_sha256": "p"}}}, "d")
    with pytest.raises(SystemExit, match="REFUSED"):
        sv.check_manifest_records({"k": {"codex": {"state": "RAN_OK", "record_id": "r-stale", "prompt_sha256": "p"}}},
                                  "d")


def test_PLANT_r28_replies_with_conflicting_duplicate_rows_are_reported():         # codex2 (served audit)
    reply = {"answers": [{"qid": "1.2", "answer": "PY"}, {"qid": "1.2", "answer": "PN"}, {"qid": "1.1", "answer": "Y"},
                         {"qid": "1.1", "answer": "Y"}]}
    assert sv.conflicting_rows(reply) == ["1.2"]
    assert sv.conflicting_rows({"answers": [{"qid": "1.2", "answer": "PY"}]}) == []


# ======================= review round 29 (codex REVISE 4, agy ACCEPT): failing-first tests =================
import hashlib  # noqa: E402

SRC = {"id": "abstract:PMID 1", "kind": "abstract", "text": "t", "sha256": "0" * 64, "open_for_prompt": True}
ITEM = {"slug": "t", "pmid": "1", "nct": None, "outcome": "o", "sources": [SRC], "machine_d5": None, "key": "t::1::o"}
P = hashlib.sha256(b"READER").hexdigest()


def _world(monkeypatch, replies, record_prompts=None, agree=({}, {}), record_states=None):
    monkeypatch.setattr(sv.rd, "prompt_bytes", lambda item, kind="reader", shown=None:
                        b"READER" if kind == "reader" else ("ADJ:" + json.dumps(shown, sort_keys=True)).encode())
    # rd.replay's REAL contract (codex/agy round 30): the PARSED reply (robgrade.contextual.parse_reply), or None --
    # the round-29 helper returned bytes, which hid a double parse in the driver
    from robgrade import contextual as cx
    monkeypatch.setattr(sv.rd, "replay", lambda run: cx.parse_reply((replies.get((run or {}).get("record_id")) or "")
                                                                    .encode()) if run and run.get("state") == "RAN_OK"
                        else None)
    monkeypatch.setattr(sv, "_record_state", lambda d, rid: (record_states or {}).get(rid, "RAN_OK"))
    # r32: each held record carries the role it was made for
    monkeypatch.setattr(sv, "_record_role", lambda d, rid: {"r-c": "codex", "r-a": "agy", "r-j": "adjudicator"}.get(rid))
    monkeypatch.setattr(sv.rd, "verify_answers", lambda raw, item, allowed=None: {})
    monkeypatch.setattr(sv.rd, "agree", lambda a, b: agree)
    monkeypatch.setattr(sv.rt, "typed_answers", lambda *a, **k: ({}, []))
    monkeypatch.setattr(sv, "_record_prompt_sha256", lambda d, rid: (record_prompts or {}).get(rid, P))


GOOD = json.dumps({"answers": [{"qid": "1.2", "answer": "PY"}], "notes": ""})
RUN = {"codex": {"state": "RAN_OK", "record_id": "r-c", "prompt_sha256": P},
       "agy": {"state": "RAN_OK", "record_id": "r-a", "prompt_sha256": P}}


def test_PLANT_r29_a_clean_item_passes(monkeypatch):
    _world(monkeypatch, {"r-c": GOOD, "r-a": GOOD})
    assert sv.item_verdict(ITEM, RUN, "d") is None


def test_PLANT_r29_a_stale_reader_record_is_refused(monkeypatch):                    # codex0
    _world(monkeypatch, {"r-c": GOOD, "r-a": GOOD})
    old = dict(RUN, codex=dict(RUN["codex"], prompt_sha256="OLD"))                   # manifest AND record agree, on OLD
    monkeypatch.setattr(sv, "_record_prompt_sha256", lambda d, rid: "OLD" if rid == "r-c" else P)
    with pytest.raises(SystemExit, match="REFUSED"):
        sv.item_verdict(ITEM, old, "d")


def test_PLANT_r29_an_unreadable_or_ambiguous_reply_quarantines_the_trial(monkeypatch):   # codex3, codex1
    _world(monkeypatch, {"r-c": GOOD, "r-a": GOOD + GOOD.replace("PY", "PN")})         # two distinct answer objects
    assert "unreadable" in sv.item_verdict(ITEM, RUN, "d")
    dup = json.dumps({"answers": [{"qid": "1.2", "answer": "PY"}, {"qid": "1.2", "answer": "PN"}], "notes": ""})
    _world(monkeypatch, {"r-c": GOOD, "r-a": dup})
    assert "conflicting" in sv.item_verdict(ITEM, RUN, "d")


def test_PLANT_r29_the_adjudicator_must_answer_the_disagreement_the_fresh_readers_make(monkeypatch):   # codex0
    shown = {"1.2": {"reader 1": {"answer": "PY"}, "reader 2": {"answer": "NI"}}}
    pa = hashlib.sha256(("ADJ:" + json.dumps(shown, sort_keys=True)).encode()).hexdigest()
    adj = {"state": "RAN_OK", "record_id": "r-j", "prompt_sha256": pa}
    _world(monkeypatch, {"r-c": GOOD, "r-a": GOOD, "r-j": GOOD}, {"r-j": pa},
           agree=({}, {"1.2": ({"answer": "PY"}, {"answer": "NI"})}))
    assert sv.item_verdict(ITEM, dict(RUN, adjudicator=adj), "d") is None
    with pytest.raises(SystemExit, match="REFUSED"):                                 # an adjudication of OTHER readings
        sv.item_verdict(ITEM, dict(RUN, adjudicator=dict(adj, prompt_sha256="OTHER")), "d")
    _world(monkeypatch, {"r-c": GOOD, "r-a": GOOD, "r-j": GOOD})                       # readers AGREE now
    with pytest.raises(SystemExit, match="REFUSED"):
        sv.item_verdict(ITEM, dict(RUN, adjudicator=adj), "d")


def test_PLANT_r29_a_quarantined_trial_gets_no_object_and_is_listed(monkeypatch, tmp_path):
    monkeypatch.setattr(sv.rd, "OUT_DIR", str(tmp_path))
    monkeypatch.setattr(sv, "item_verdict", lambda item, r, d: "unreadable reply: agy" if item["pmid"] == "2" else None)
    results, quarantined = sv.keep_or_quarantine([({"pmid": "1"}, {"o": 1}, {}), ({"pmid": "2"}, {"o": 2}, {})], "d")
    assert results == {"1": {"o": 1}} and quarantined == {"2": "unreadable reply: agy"}



# ======================= review round 30 (codex REVISE 4, agy REVISE 2): failing-first tests =================
def test_PLANT_r30_a_real_held_reply_through_the_real_replay_is_readable():          # codex0, agy0 (no mock)
    rid = "mc-02ce2c3566607b133e620604b0b10965"                      # a held v3.1 codex reader record
    assert os.path.exists(os.path.join(rd.REC_DIR, rid + ".json"))
    assert rd.replay({"state": "RAN_OK", "record_id": rid}) is not None
    assert sv._reply_problem({"state": "RAN_OK", "record_id": rid}, "codex") is None


def test_PLANT_r30_a_failed_adjudication_must_be_a_HELD_failed_record_of_that_prompt(monkeypatch):   # codex1
    shown = {"1.2": {"reader 1": {"answer": "PY"}, "reader 2": {"answer": "NI"}}}
    pa = hashlib.sha256(("ADJ:" + json.dumps(shown, sort_keys=True)).encode()).hexdigest()
    dis = ({}, {"1.2": ({"answer": "PY"}, {"answer": "NI"})})
    failed = {"state": "RAN_ERROR", "record_id": "r-j", "prompt_sha256": pa}
    _world(monkeypatch, {"r-c": GOOD, "r-a": GOOD}, {"r-j": pa}, agree=dis, record_states={"r-j": "RAN_ERROR"})
    assert sv.item_verdict(ITEM, dict(RUN, adjudicator=failed), "d") is None          # a real failed attempt: honest NI
    _world(monkeypatch, {"r-c": GOOD, "r-a": GOOD}, {"r-j": pa}, agree=dis, record_states={"r-j": None})
    with pytest.raises(SystemExit, match="REFUSED"):                                 # no held attempt
        sv.item_verdict(ITEM, dict(RUN, adjudicator=failed), "d")
    _world(monkeypatch, {"r-c": GOOD, "r-a": GOOD}, {"r-j": pa}, agree=dis, record_states={"r-j": "RAN_OK"})
    with pytest.raises(SystemExit, match="REFUSED"):                                 # a SUCCESS relabelled as failed
        sv.item_verdict(ITEM, dict(RUN, adjudicator=failed), "d")


def test_PLANT_r30_a_reader_entry_state_must_match_its_held_record(monkeypatch):      # codex1
    _world(monkeypatch, {"r-c": GOOD, "r-a": GOOD}, record_states={"r-a": "RAN_ERROR"})
    with pytest.raises(SystemExit, match="REFUSED"):
        sv.item_verdict(ITEM, RUN, "d")


def test_PLANT_r30_the_contextual_stage_never_runs_without_the_guarded_dual_stage(monkeypatch):   # codex2
    monkeypatch.setattr(sv, "_die", lambda code: (_ for _ in ()).throw(SystemExit(code)))   # never os._exit in a test
    with pytest.raises(SystemExit, match="REFUSED"):
        sv.main(["--ctx-only"])


# ======================= review round 31 (codex REVISE 4, agy RAN_ERROR): failing-first tests =================
def test_PLANT_r31_every_manifest_entry_in_ANY_state_must_match_its_held_record(monkeypatch):   # codex1
    monkeypatch.setattr(sv, "_record_prompt_sha256", lambda d, rid: "p")
    monkeypatch.setattr(sv, "_record_state", lambda d, rid: "RAN_OK")
    monkeypatch.setattr(sv, "_record_role", lambda d, rid: "agy")               # r32: and the role
    ctx = {"k": {"passes": [{"agy": {"state": "RAN_ERROR", "record_id": "r-a", "prompt_sha256": "p"}}]}}
    with pytest.raises(SystemExit, match="REFUSED"):                    # a held SUCCESS relabelled as failed
        sv.check_manifest_records(ctx, "d", contextual=True)
    ok = {"k": {"passes": [{"agy": {"state": "RAN_OK", "record_id": "r-a", "prompt_sha256": "p"}}]}}
    sv.check_manifest_records(ok, "d", contextual=True)


def test_PLANT_r31_every_held_success_must_be_accounted_for(tmp_path, monkeypatch):   # codex2
    for rid in ("mc-1", "mc-2"):
        (tmp_path / f"{rid}.json").write_text(json.dumps({"state": "RAN_OK"}), encoding="utf-8")
    (tmp_path / "mc-3.json").write_text(json.dumps({"state": "RAN_ERROR"}), encoding="utf-8")
    dual = {"k": {"codex": {"state": "RAN_OK", "record_id": "mc-1"}, "agy": {"state": "RAN_OK", "record_id": "mc-2"}}}
    sv.check_accounted(dual, str(tmp_path))                              # a held failure need not be named
    with pytest.raises(SystemExit, match="REFUSED"):
        sv.check_accounted({"k": {"codex": dual["k"]["codex"]}}, str(tmp_path))     # mc-2 dropped from the manifest
    ctx = {"k": {"passes": [{"codex": {"state": "RAN_OK", "record_id": "mc-1"}}], "consumed": ["mc-1", "mc-2"]}}
    sv.check_accounted(ctx, str(tmp_path), consumed=True)
    with pytest.raises(SystemExit, match="REFUSED"):                    # held, but never READ by the replay
        sv.check_accounted(dict(ctx, k=dict(ctx["k"], consumed=["mc-1"])), str(tmp_path), consumed=True)


def test_PLANT_r31_existing_manifests_are_checked_BEFORE_any_stage_runs(monkeypatch):   # codex0
    order = []
    monkeypatch.setattr(sv, "work_list", lambda: ({"t": ["1"]}, {}))
    monkeypatch.setattr(sv, "check_manifest_records", lambda runs, d, **kwargs: order.append(("check", d)))
    monkeypatch.setattr(sv, "check_accounted", lambda runs, d, consumed=False, keys=None: order.append(("accounted", d)))
    monkeypatch.setattr(sv, "_die", lambda code: (_ for _ in ()).throw(SystemExit(code)))   # never os._exit in a test
    monkeypatch.setattr(sv, "run_dual", lambda todo, live: order.append(("dual",)))
    monkeypatch.setattr(sv, "run_ctx", lambda slugs, live: order.append(("ctx",)))
    monkeypatch.setattr(sv, "audit", lambda d: [])
    monkeypatch.setattr(sv, "adopt_stage", lambda todo: [])
    for n in ("REC_DIR", "OUT_DIR", "RUNS"):
        monkeypatch.setattr(rd, n, getattr(rd, n))
    for n in ("OBJ_DIR", "BASE_OUT_DIR", "BASE_REC_DIR", "BASE_RUNS", "OUT_DIR", "REC_DIR", "RUNS", "REC_READ_DIRS",
              "VARIANT"):
        monkeypatch.setattr(rc, n, getattr(rc, n))
    sv.main([])
    first_dual = order.index(("dual",))
    first_ctx = order.index(("ctx",))
    assert ("check", sv.STORES["dual_rec"]) in order[:first_dual] and ("accounted", sv.STORES["dual_rec"]) in order[:first_dual]
    assert ("check", sv.STORES["ctx_rec"]) in order[:first_ctx] and ("accounted", sv.STORES["ctx_rec"]) in order[:first_ctx]
    assert order[-2:] == [("check", sv.STORES["ctx_rec"]), ("accounted", sv.STORES["ctx_rec"])]


# ======================= review round 32 (codex REVISE 4, agy REVISE 1): failing-first tests =================
def test_PLANT_r32_an_entry_under_an_unknown_role_is_refused(monkeypatch):           # codex0
    monkeypatch.setattr(sv, "_record_prompt_sha256", lambda d, rid: "p")
    monkeypatch.setattr(sv, "_record_state", lambda d, rid: "RAN_OK")
    monkeypatch.setattr(sv, "_record_role", lambda d, rid: "agy")
    with pytest.raises(SystemExit, match="REFUSED"):
        sv.check_manifest_records({"k": {"spare": {"state": "RAN_OK", "record_id": "r-a", "prompt_sha256": "p"}}}, "d")


def test_PLANT_r32_a_record_is_bound_to_its_role_and_the_readers_are_distinct(monkeypatch):   # codex1
    monkeypatch.setattr(sv, "_record_prompt_sha256", lambda d, rid: "p")
    monkeypatch.setattr(sv, "_record_state", lambda d, rid: "RAN_OK")
    monkeypatch.setattr(sv, "_record_role", lambda d, rid: {"r-c": "codex", "r-a": "agy"}.get(rid))
    e = lambda rid: {"state": "RAN_OK", "record_id": rid, "prompt_sha256": "p"}  # noqa: E731
    sv.check_manifest_records({"k": {"codex": e("r-c"), "agy": e("r-a")}}, "d")
    with pytest.raises(SystemExit, match="REFUSED"):                      # a codex record in the agy slot
        sv.check_manifest_records({"k": {"codex": e("r-c"), "agy": e("r-c")}}, "d")
    with pytest.raises(SystemExit, match="REFUSED"):                      # contextual passes too
        sv.check_manifest_records({"k": {"passes": [{"codex": e("r-a"), "agy": e("r-a")}]}}, "d", contextual=True)


def test_PLANT_r32_a_failed_or_missing_reader_quarantines_the_trial(monkeypatch):     # agy0
    _world(monkeypatch, {"r-c": GOOD}, record_states={"r-a": "RAN_ERROR"})
    failed = dict(RUN, agy={"state": "RAN_ERROR", "record_id": "r-a", "prompt_sha256": P})
    assert "failed" in sv.item_verdict(ITEM, failed, "d")
    _world(monkeypatch, {"r-c": GOOD})
    assert "missing" in sv.item_verdict(ITEM, {"codex": RUN["codex"]}, "d")


class _Done:
    def __init__(self, v):
        self.v = v

    def result(self):
        return self.v


class _Pool:
    def __init__(self, log):
        self.log = log

    def submit(self, fn, item, who, p):
        self.log.append((item["pmid"], who))
        return _Done({"state": "RAN_OK", "record_id": f"r-{item['pmid']}-{who}", "prompt_sha256": "p"})

    def shutdown(self, wait=True):
        pass


def test_PLANT_r32_live_adjudication_waits_for_the_reader_checks(monkeypatch, tmp_path):   # codex3
    log, saved = [], {}

    def fake_process(item, runs, live, pools):
        r = dict(runs.get(item["key"]) or {})
        for who in ("codex", "agy"):
            if (r.get(who) or {}).get("state") != "RAN_OK":
                r[who] = pools[who].submit(None, item, who, b"P").result()
        if (r.get("adjudicator") or {}).get("state") != "RAN_OK":
            r["adjudicator"] = pools["codex"].submit(None, item, "adjudicator", b"A").result()
        return {"overall": {"judgement": "X"}}, r
    monkeypatch.setattr(sv.rd, "process", fake_process)
    monkeypatch.setattr(sv.rd, "items", lambda slug, pm: [{"pmid": p, "key": f"{slug}::{p}", "outcome": "o"} for p in pm])
    monkeypatch.setattr(sv.rd, "prefetch_registry", lambda x: None)
    monkeypatch.setattr(sv.rd, "redact_closed_spans", lambda obj, it: None)
    monkeypatch.setattr(sv.rd, "_save", lambda path, obj: saved.__setitem__(os.path.basename(path), obj))
    monkeypatch.setattr(sv, "_pools", lambda: ({"codex": _Pool(log), "agy": _Pool(log), "adjudicator": None}, _Exec()))
    monkeypatch.setattr(sv, "reader_verdict", lambda item, r, d: "unreadable reply: agy" if item["pmid"] == "bad" else None)
    monkeypatch.setattr(sv, "item_verdict", lambda item, r, d: None)
    monkeypatch.setattr(sv, "SERVED", str(tmp_path))
    monkeypatch.setattr(sv.rd, "RUNS", str(tmp_path / "runs.json"))
    monkeypatch.setattr(sv.rd, "OUT_DIR", str(tmp_path))
    sv.run_dual({"t": ["good", "bad"]}, True)
    assert ("good", "adjudicator") in log and ("bad", "adjudicator") not in log      # no call for a quarantined trial
    assert set(saved["t.json"]["trials"]) == {"good"} and saved["QUARANTINE.json"]["t"] == {"bad": "unreadable reply: agy"}


class _Exec:
    def submit(self, fn, *a):
        return _Done(fn(*a))

    def shutdown(self, wait=True):
        pass


# ======================= review round 33 (codex REVISE 2, agy RAN_ERROR): failing-first test =================
def test_PLANT_r33_an_entry_under_a_key_of_no_served_trial_is_refused(tmp_path):     # codex0
    for rid in ("mc-1", "mc-2"):
        (tmp_path / f"{rid}.json").write_text(json.dumps({"state": "RAN_OK"}), encoding="utf-8")
    parked = {"t::1::o": {"codex": {"state": "RAN_OK", "record_id": "mc-1"}},
              "t::999::o": {"agy": {"state": "RAN_OK", "record_id": "mc-2"}}}       # agy parked under a key of no trial
    with pytest.raises(SystemExit, match="REFUSED"):
        sv.check_accounted(parked, str(tmp_path), keys={"t::1::o"})
    ok = {"t::1::o": {"codex": {"state": "RAN_OK", "record_id": "mc-1"}, "agy": {"state": "RAN_OK", "record_id": "mc-2"}}}
    sv.check_accounted(ok, str(tmp_path), keys={"t::1::o"})


def test_PLANT_r33_the_served_keys_are_the_pipelines_keys(monkeypatch):
    monkeypatch.setattr(sv.rd, "served_primary", lambda slug: ("Mortality", ["1", "2"]))
    assert sv.served_keys({"t": ["1", "2"]}) == {"t::1::Mortality", "t::2::Mortality"}


# ======================= review round 34 (codex REVISE 2, agy RAN_ERROR): failing-first test =================
def test_PLANT_r34_a_record_is_bound_to_the_trial_and_outcome_of_its_key(monkeypatch):   # codex0
    monkeypatch.setattr(sv, "_record_prompt_sha256", lambda d, rid: "p")
    monkeypatch.setattr(sv, "_record_state", lambda d, rid: "RAN_OK")
    monkeypatch.setattr(sv, "_record_role", lambda d, rid: {"r-a1": "agy", "r-c2": "codex"}.get(rid))
    monkeypatch.setattr(sv, "_record_bound", lambda d, rid: {"r-a1": ("111", "Mortality"),
                                                              "r-c2": ("222", "Mortality")}.get(rid))
    e = lambda rid: {"state": "RAN_OK", "record_id": rid, "prompt_sha256": "p"}  # noqa: E731
    sv.check_manifest_records({"t::111::Mortality": {"agy": e("r-a1")}}, "d")
    with pytest.raises(SystemExit, match="REFUSED"):                     # trial A's record under trial B's key
        sv.check_manifest_records({"t::222::Mortality": {"codex": e("r-c2"), "agy": e("r-a1")}}, "d")


# ======================= the killed live run (14 Oct): orphaned records and incremental manifests =================
def _orphans(tmp_path, monkeypatch, recs):
    """recs: {rid: (role, (pmid, outcome), prompt_sha)} written as held RAN_OK records."""
    for rid, (role, bound, ps) in recs.items():
        (tmp_path / f"{rid}.json").write_text(json.dumps({"state": "RAN_OK", "model": {"id_reported": f"m-{role}"},
                                                          "caller": {"line": f"call:{role}"}}), encoding="utf-8")
    monkeypatch.setattr(sv, "_record_role", lambda d, rid: recs.get(rid, (None,))[0])
    monkeypatch.setattr(sv, "_record_bound", lambda d, rid: recs.get(rid, (None, None))[1])
    monkeypatch.setattr(sv, "_record_prompt_sha256", lambda d, rid: recs.get(rid, (None, None, None))[2])
    monkeypatch.setattr(sv.rd, "prompt_bytes", lambda item, kind="reader", shown=None: ("P" + item["pmid"]).encode())
    monkeypatch.setattr(sv.rd, "open_sources", lambda item: [SRC])


IT = [{"slug": "t", "pmid": "1", "outcome": "o", "key": "t::1::o"}, {"slug": "t", "pmid": "2", "outcome": "o", "key": "t::2::o"}]
PS1, PS2 = hashlib.sha256(b"P1").hexdigest(), hashlib.sha256(b"P2").hexdigest()


def test_PLANT_killed_run_a_provable_orphan_is_adopted_into_its_one_slot(tmp_path, monkeypatch):
    _orphans(tmp_path, monkeypatch, {"mc-c1": ("codex", ("1", "o"), PS1), "mc-c2": ("codex", ("2", "o"), PS2)})
    runs = {}
    adopted = sv.adopt_orphans(IT, runs, str(tmp_path))
    assert sorted(adopted) == [("t::1::o", "codex", "mc-c1"), ("t::2::o", "codex", "mc-c2")]
    assert runs["t::1::o"]["codex"] == {"record_id": "mc-c1", "state": "RAN_OK", "error": None, "prompt_sha256": PS1,
                                        "model": "m-codex"}                       # exactly what rob2_dual._call writes


def test_PLANT_killed_run_an_orphan_is_never_adopted_when_its_slot_is_not_provable(tmp_path, monkeypatch):
    _orphans(tmp_path, monkeypatch, {"mc-a": ("codex", ("1", "o"), PS1), "mc-b": ("codex", ("1", "o"), PS1),   # two
                                     "mc-s": ("agy", ("2", "o"), "OLD"),                                    # stale
                                     "mc-x": ("codex", ("9", "o"), PS1),                                    # no such trial
                                     "mc-j": ("adjudicator", ("2", "o"), PS2)})                             # not a reader
    runs = {}
    assert sv.adopt_orphans(IT, runs, str(tmp_path)) == [] and runs == {}
    d = tmp_path / "fresh"
    d.mkdir()
    _orphans(d, monkeypatch, {"mc-c1": ("codex", ("1", "o"), PS1)})
    runs = {"t::1::o": {"codex": {"record_id": "mc-old", "state": "RAN_OK", "prompt_sha256": PS1}}}  # slot already fresh
    assert sv.adopt_orphans(IT, runs, str(d)) == []


def test_PLANT_killed_run_phase_1_saves_the_manifest_after_every_trial(monkeypatch, tmp_path):
    saved_runs = []

    def fake_process(item, runs, live, pools):
        if item["pmid"] == "boom":
            raise RuntimeError("the process was killed here")
        r = {"codex": pools["codex"].submit(None, item, "codex", b"P").result()}
        return {"overall": {"judgement": "X"}}, r
    monkeypatch.setattr(sv.rd, "process", fake_process)
    monkeypatch.setattr(sv.rd, "items", lambda slug, pm: [{"pmid": p, "key": f"{slug}::{p}", "outcome": "o"} for p in pm])
    monkeypatch.setattr(sv.rd, "prefetch_registry", lambda x: None)
    monkeypatch.setattr(sv.rd, "_save", lambda path, obj: saved_runs.append(json.loads(json.dumps(obj)))
                        if path.endswith("runs.json") else None)
    log = []
    # a REAL pool raises only at result(): the lazy executor models a run killed while a later trial is in flight
    monkeypatch.setattr(sv, "_pools", lambda: ({"codex": _Pool(log), "agy": _Pool(log), "adjudicator": None}, _LazyExec()))
    monkeypatch.setattr(sv, "reader_verdict", lambda item, r, d: None)
    monkeypatch.setattr(sv, "SERVED", str(tmp_path))
    monkeypatch.setattr(sv.rd, "RUNS", str(tmp_path / "runs.json"))
    with pytest.raises(RuntimeError):
        sv.run_dual({"t": ["ok", "boom"]}, True)
    assert any("t::ok" in r for r in saved_runs)               # the finished trial's records are named before the kill



class _Lazy:
    def __init__(self, fn, a):
        self.fn, self.a = fn, a

    def result(self):
        return self.fn(*self.a)


class _LazyExec:
    def submit(self, fn, *a):
        return _Lazy(fn, a)

    def shutdown(self, wait=True):
        pass


def test_PLANT_no_test_writes_a_real_served_store():
    for k, path in sv.STORES.items():
        assert os.path.commonpath([ROOT, path]) != ROOT, k                     # all under tmp_path in every test

# Second review: regression tests written before the fixes.
def test_review_1_ambiguous_pair_is_not_adopted(tmp_path, monkeypatch):
    _orphans(tmp_path, monkeypatch, {"mc-new": ("codex", ("1", "o"), PS1)})
    runs = {}
    items = (IT[0], dict(IT[0], slug="other", key="other::1::o"))
    assert sv.adopt_orphans(items, runs, str(tmp_path)) == []
    assert runs == {}


def test_review_2_successful_old_slot_is_not_overwritten(tmp_path, monkeypatch):
    _orphans(tmp_path, monkeypatch, {"mc-old": ("codex", ("1", "o"), "OLD"),
                                   "mc-new": ("codex", ("1", "o"), PS1)})
    old = {"record_id": "mc-old", "state": "RAN_OK", "prompt_sha256": "OLD"}
    runs = {IT[0]["key"]: {"codex": dict(old)}}
    assert sv.adopt_orphans(IT, runs, str(tmp_path)) == []
    assert runs[IT[0]["key"]]["codex"] == old
    with pytest.raises(SystemExit, match="REFUSED.*mc-new"):
        sv.check_accounted(runs, str(tmp_path))


@pytest.mark.parametrize("deferred", (False, True))
def test_review_3_pending_replay_is_quarantined(monkeypatch, deferred):
    _world(monkeypatch, {"r-c": GOOD, "r-a": GOOD},
           agree=({}, {"1.2": ({"answer": "PY"}, {"answer": "NI"})}))
    run = dict(RUN)
    if deferred:
        run["adjudicator"] = {"state": "DEFERRED", "record_id": None, "prompt_sha256": None}
    kept, q = sv.keep_or_quarantine([(ITEM, {}, run)], "d")
    assert kept == {} and q == {"1": "adjudication pending"}


def test_review_3_every_manifest_save_strips_deferred(monkeypatch, tmp_path):
    saved = []
    deferred = {"state": "DEFERRED", "record_id": None, "prompt_sha256": None}
    def process(item, runs, live, pools):
        return {"overall": {"judgement": "X"}}, dict(RUN, adjudicator=dict(deferred))
    monkeypatch.setattr(rd, "process", process)
    monkeypatch.setattr(rd, "items", lambda slug, pm: [ITEM])
    monkeypatch.setattr(rd, "prefetch_registry", lambda jobs: None)
    monkeypatch.setattr(rd, "redact_closed_spans", lambda *args: None)
    monkeypatch.setattr(sv, "reader_verdict", lambda *args: None)
    monkeypatch.setattr(sv, "item_verdict", lambda *args: "adjudication pending")
    with sv.redirected():
        rd._save(rd.RUNS, {"old": {"adjudicator": deferred}})
        save = rd._save
        def capture(path, obj):
            if path == rd.RUNS:
                saved.append(json.loads(json.dumps(obj)))
            save(path, obj)
        monkeypatch.setattr(rd, "_save", capture)
        with pytest.raises(SystemExit, match="REFUSED.*t::1::o.*adjudication"):
            sv.run_dual({"t": ["1"]}, True)
    assert len(saved) >= 3
    assert all(e.get("state") != "DEFERRED" for doc in saved for row in doc.values() for e in row.values())


@pytest.mark.parametrize("reader", ("check_accounted", "adopt_orphans", "_record_state", "_record_role",
                                    "_record_bound", "_record_prompt_sha256", "audit"))
@pytest.mark.parametrize("broken", ("{", "[]"))
def test_review_4_corrupt_record_is_named_refusal(tmp_path, reader, broken):
    path = tmp_path / "mc-broken.json"
    path.write_text(broken, encoding="utf-8")
    with pytest.raises(SystemExit, match=r"REFUSED.*mc-broken\.json"):
        if reader == "check_accounted":
            sv.check_accounted({}, str(tmp_path))
        elif reader == "adopt_orphans":
            sv.adopt_orphans([], {}, str(tmp_path))
        elif reader == "audit":
            sv.audit(str(tmp_path))
        else:
            getattr(sv, reader)(str(tmp_path), "mc-broken")


@pytest.mark.parametrize("extra", ({"passes": [{}]}, {"spare": {}}, {"consumed": []}))
def test_review_5_dual_rejects_unexpected_keys(extra):
    with pytest.raises(SystemExit, match="REFUSED.*(unexpected|unknown)"):
        sv.check_manifest_records({"t::1::o": dict(extra, codex={})}, "dual-records")


def test_review_6_quarantine_is_a_redirected_store(tmp_path):
    assert "quarantine" in sv.STORES
    assert os.path.commonpath((str(tmp_path), sv.STORES["quarantine"])) == str(tmp_path)
    assert os.path.basename(sv.STORES["quarantine"]) == "QUARANTINE.json"


def test_review_6_all_quarantined_slug_contextual_replay(monkeypatch):
    monkeypatch.setattr(rd, "prefetch_registry", lambda jobs: None)
    monkeypatch.setattr(rd, "items", lambda slug, pm: [ITEM] if pm else [])
    monkeypatch.setattr(rd, "process", lambda *args: ({"overall": {"judgement": "X"}}, {}))
    monkeypatch.setattr(rd, "redact_closed_spans", lambda *args: None)
    monkeypatch.setattr(sv, "item_verdict", lambda *args: "missing reader: codex")
    with sv.redirected():
        sv.run_dual({"t": ["1"]}, False)
        assert rd._j(os.path.join(rd.OUT_DIR, "t.json"))["trials"] == {}
        sv.run_ctx(("t",), False)
        assert rd._j(os.path.join(rc.OUT_DIR, "t.json"))["trials"] == {}


# Round 2: decoded-field guards, persisted replay, and live phase-2 closure.
@pytest.mark.parametrize("model", ("broken", [], False))
def test_round2_orphan_malformed_model_is_named_refusal(tmp_path, monkeypatch, model):
    _orphans(tmp_path, monkeypatch, {"mc-only": ("codex", ("1", "o"), PS1)})
    path = tmp_path / "mc-only.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record["model"] = model
    path.write_text(json.dumps(record), encoding="utf-8")
    runs = {}
    with pytest.raises(SystemExit, match=r"REFUSED.*mc-only\.json"):
        sv.adopt_orphans(IT, runs, str(tmp_path))
    assert runs == {}


@pytest.mark.parametrize("reader", ("check_accounted", "adopt_orphans", "_record_state", "_record_role",
                                    "_record_bound", "_record_prompt_sha256", "audit"))
def test_round2_record_readers_reject_malformed_state(tmp_path, reader):
    from reproducible_ai import model_source as ms
    record = {"state": [], "caller": {"line": "call:codex"},
              "prompt": ms._blob(b"TRIAL: 1\nOUTCOME: o\n")}
    (tmp_path / "mc-broken.json").write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(SystemExit, match=r"REFUSED.*mc-broken\.json"):
        if reader == "check_accounted":
            sv.check_accounted({}, str(tmp_path))
        elif reader == "adopt_orphans":
            sv.adopt_orphans([], {}, str(tmp_path))
        elif reader == "audit":
            sv.audit(str(tmp_path))
        else:
            getattr(sv, reader)(str(tmp_path), "mc-broken")


def test_round2_record_role_rejects_falsey_nonobject_caller(tmp_path):
    (tmp_path / "mc-broken.json").write_text(json.dumps({"caller": []}), encoding="utf-8")
    with pytest.raises(SystemExit, match=r"REFUSED.*mc-broken\.json"):
        sv._record_role(str(tmp_path), "mc-broken")


def _round2_disk_disagreement(monkeypatch):
    """Synthetic held records; real preflight, replay, verification and disagreement."""
    from reproducible_ai import model_source as ms
    item = dict(ITEM, sources=[dict(SRC, text="The allocation was concealed.", licence="CC")])
    monkeypatch.setattr(rd, "prefetch_registry", lambda jobs: None)
    monkeypatch.setattr(rd, "items", lambda slug, pm: [item])
    monkeypatch.setattr(sv.rt, "typed_answers", lambda *args, **kwargs: ({}, []))
    monkeypatch.setattr(rd, "_call", lambda *args: pytest.fail("model call attempted"))
    prompt = rd.prompt_bytes(item)
    row, held = {}, {}
    for role, answer in (("codex", "PY"), ("agy", "NI")):
        reply = {"answers": [{"qid": "1.2", "answer": answer, "source_id": SRC["id"],
                              "quote": "The allocation was concealed."}]}
        rec = {"schema": ms.SCHEMA, "state": "RAN_OK", "caller": {"line": f"call:{role}"},
               "model": {"id_reported": "test-fixture"}, "prompt": ms._blob(prompt),
               "response": ms._blob(json.dumps(reply).encode())}
        rec["record_id"] = ms.record_id_of(rec)
        path = ms.write_record(rec, rd.REC_DIR)
        held[path] = path.read_bytes()
        row[role] = {"state": "RAN_OK", "record_id": rec["record_id"], "prompt_sha256": sv._sha(prompt)}
    return item, row, held


def test_round2_persisted_deferred_end_to_end_replay(monkeypatch):
    with sv.redirected():
        item, row, held = _round2_disk_disagreement(monkeypatch)
        old = dict(row, adjudicator={"state": "DEFERRED", "record_id": None, "prompt_sha256": None})
        rd._save(rd.RUNS, {item["key"]: old})
    monkeypatch.setattr(sv, "work_list", lambda: ({"t": ["1"]}, {}))
    monkeypatch.setattr(sv, "served_pairs", lambda: {"t": ["1"]})
    monkeypatch.setattr(rd, "served_primary", lambda slug: ("o", ["1"]))
    monkeypatch.setattr(sv, "_die", lambda code: pytest.fail(f"replay refused: {code}"))
    sv.main(["--dual-only"])
    assert rd._j(sv.STORES["dual_runs"]) == {item["key"]: row}
    assert rd._j(sv.STORES["quarantine"]) == {"t": {"1": "adjudication pending"}}
    assert rd._j(os.path.join(sv.STORES["dual_out"], "t.json"))["trials"] == {}
    assert all(path.read_bytes() == data for path, data in held.items())
    assert set(os.listdir(sv.STORES["dual_rec"])) == {path.name for path in held}


def test_round2_live_missing_phase2_adjudicator_is_refused(monkeypatch):
    with sv.redirected():
        item, row, held = _round2_disk_disagreement(monkeypatch)
        rd._save(rd.RUNS, {item["key"]: row})
        phases = []
        replay_process = rd.process
        def process(it, runs, live, pools):
            assert live
            phases.append(isinstance(pools["codex"], sv._DeferAdjudication))
            return replay_process(it, runs, False, pools)
        monkeypatch.setattr(rd, "process", process)
        with pytest.raises(SystemExit, match="REFUSED.*t::1::o.*adjudication"):
            sv.run_dual({"t": ["1"]}, live=True)
        assert phases == [True, False]
        assert rd._j(rd.RUNS) == {item["key"]: row}
        assert all(path.read_bytes() == data for path, data in held.items())
