"""model-call-as-source: record, replay, proposal, gate.

Every test asserts a PROPERTY (a refusal fires, bytes are identical, a status cannot move) and plants the defect it
guards against. None pins a corpus count. The live caller is never exercised here: these tests run with every
credential variable unset and with the network and process-spawning primitives replaced by tripwires.
"""
from __future__ import annotations

import ast
import base64
import copy
import json
import os
import socket
import subprocess
from pathlib import Path

import pytest

from reproducible_ai import model_source as ms
from harness import result_changes

ROOT = Path(__file__).resolve().parents[1]

HELD = ("Oral Semaglutide and Cardiovascular Outcomes in Patients with Type 2 Diabetes. METHODS: We performed a "
        "randomized, double-blind, placebo-controlled trial involving 3183 patients with type 2 diabetes. The primary "
        "analysis was performed in the intention-to-treat population.")
HELD_SHA = ms.sha256_bytes(HELD.encode("utf-8"))


def _record(response: bytes = b'{"answer": 1}', **over):
    kw = dict(
        prompt_bytes=b"Read the record and answer.\n",
        response_bytes=response,
        model={"id_requested": "planted-model", "id_reported": "planted-model", "provider": "planted"},
        params={"reasoning_effort": "low"},
        not_controllable=["temperature", "seed"],
        client={"name": "fixture", "version": "0"},
        request_utc="2026-09-23T22:00:00Z",
        response_utc="2026-09-23T22:00:05Z",
        caller={"file": "tests/test_model_source.py", "line": 1, "purpose": "fixture"},
        input_digests=[{"ref": "fixture:held", "sha256": HELD_SHA, "what": "held text"}],
    )
    kw.update(over)
    return ms.build_record(**kw)


# ---------------------------------------------------------------------------------------------------- the record
def test_record_carries_every_field_and_is_content_addressed():
    rec = _record()
    for k in ("record_id", "model", "params", "not_controllable", "prompt", "response", "request_utc", "caller",
              "input_digests", "state", "client"):
        assert k in rec, k
    assert base64.b64decode(rec["prompt"]["b64"]) == b"Read the record and answer.\n"
    assert rec["prompt"]["sha256"] == ms.sha256_bytes(b"Read the record and answer.\n")
    # content addressing: the id is a function of everything else, so two different calls never share an id
    assert rec["record_id"] == ms.record_id_of(rec)
    assert _record(response=b"other")["record_id"] != rec["record_id"]


@pytest.mark.parametrize("missing", ["prompt_bytes", "model", "caller", "input_digests"])
def test_a_call_whose_inputs_are_not_recoverable_is_not_a_source(missing):
    with pytest.raises(ms.RecordIncomplete):
        _record(**{missing: b"" if missing == "prompt_bytes" else ({} if missing != "input_digests" else [])})


def test_an_unpinned_model_is_refused():
    with pytest.raises(ms.RecordIncomplete):
        _record(model={"id_requested": "x", "provider": "p"})   # no id_reported: the pin is not known


def test_ran_error_is_recorded_and_never_replays_as_a_response():
    rec = _record(response=b"", state="RAN_ERROR", error="client exited 1")
    assert rec["state"] == "RAN_ERROR"
    with pytest.raises(ms.ReplayRefused):
        ms.replay(rec)


# ---------------------------------------------------------------------------------------------------- replay
@pytest.fixture
def offline(monkeypatch):
    """No credentials, no network, no child process: a replay that needs any of them fails loudly."""
    for k in list(os.environ):
        if any(t in k.upper() for t in ("OPENAI", "ANTHROPIC", "CODEX", "GEMINI", "API_KEY")):
            monkeypatch.delenv(k, raising=False)

    def trip(*a, **k):
        raise AssertionError("replay reached for the network or a child process")
    monkeypatch.setattr(socket, "socket", trip)
    monkeypatch.setattr(socket, "create_connection", trip)
    monkeypatch.setattr(subprocess, "Popen", trip)
    monkeypatch.setattr(subprocess, "run", trip)
    return True


def test_replay_is_byte_identical_offline(offline):
    payload = "réponse ✓ \r\n with CRLF and bytes \x00 kept".encode("utf-8")
    rec = _record(response=payload)
    back = json.loads(json.dumps(rec))          # through the storage format and back
    assert ms.replay(back) == payload
    assert ms.replay(back) == ms.replay(back)


def test_replay_through_a_committed_file_is_byte_identical(tmp_path, offline):
    payload = b"line one\r\nline two\n"
    rec = _record(response=payload)
    path = ms.write_record(rec, tmp_path)
    assert ms.replay(ms.load_record(path)) == payload


@pytest.mark.parametrize("where", ["response_b64", "response_sha", "prompt_b64", "model", "params", "input_digests"])
def test_a_tampered_record_is_refused_loudly(where, offline):
    rec = _record()
    bad = copy.deepcopy(rec)
    if where == "response_b64":
        bad["response"]["b64"] = base64.b64encode(b'{"answer": 2}').decode()
    elif where == "response_sha":           # tamper consistently: new bytes AND their digest
        bad["response"]["b64"] = base64.b64encode(b'{"answer": 2}').decode()
        bad["response"]["sha256"] = ms.sha256_bytes(b'{"answer": 2}')
        bad["response"]["bytes"] = len(b'{"answer": 2}')
    elif where == "prompt_b64":
        bad["prompt"]["b64"] = base64.b64encode(b"a different question").decode()
    elif where == "model":
        bad["model"]["id_reported"] = "some-other-model"
    elif where == "params":
        bad["params"]["reasoning_effort"] = "high"
    else:
        bad["input_digests"][0]["sha256"] = "0" * 64
    with pytest.raises(ms.ReplayRefused):
        ms.replay(bad)


def test_write_record_refuses_to_overwrite_a_stored_response(tmp_path):
    rec = _record()
    path = ms.write_record(rec, tmp_path)
    forged = copy.deepcopy(rec)
    forged["response"]["b64"] = base64.b64encode(b"forged").decode()
    path.write_text(json.dumps(forged), encoding="utf-8")
    with pytest.raises(ms.ReplayRefused):
        ms.write_record(rec, tmp_path)       # the file on disk no longer matches: refuse, do not paper over


def test_replay_module_cannot_reach_a_model():
    """Structural: reproducible_ai/model_source.py imports nothing that can call out. The live caller lives elsewhere."""
    tree = ast.parse((ROOT / "reproducible_ai" / "model_source.py").read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    forbidden = {"subprocess", "socket", "urllib", "http", "requests", "httpx", "openai", "anthropic", "asyncio"}
    assert not (names & forbidden), names & forbidden


# ---------------------------------------------------------------------------------------------------- live caller
HEADER = (b"OpenAI Codex v0.0\n--------\nworkdir: C:\\somewhere\nmodel: planted-model\nprovider: planted\n"
          b"reasoning effort: low\nsession id: s-1\n--------\nuser\nprompt\ncodex\nanswer\ntokens used\n1,234\n")


def _fake(rc=0, last=b'{"items": []}', stderr=HEADER, stdout=b""):
    return lambda prompt, schema, model, effort, timeout_s: {"rc": rc, "stdout": stdout, "stderr": stderr,
                                                              "last_message": last, "argv": ["fake"]}


def _live(**kw):
    from reproducible_ai import model_call_live
    return model_call_live.call(b"prompt bytes\n", schema={"type": "object"}, model="planted-model", effort="low",
                                caller={"file": "t", "line": 1, "purpose": "p"},
                                input_digests=[{"ref": "x", "sha256": HELD_SHA}], client_version="fake 0", **kw)


def test_live_call_success_is_a_replayable_record(offline):
    rec = _live(runner=_fake())
    assert rec["state"] == "RAN_OK" and rec["model"]["id_reported"] == "planted-model"
    assert ms.replay(rec) == b'{"items": []}'


@pytest.mark.parametrize("runner", [
    _fake(rc=1), _fake(last=b"  \n"), _fake(stderr=b""),
    _fake(stderr=HEADER.replace(b"model: planted-model", b"model: another-model")),
    _fake(stderr=HEADER.replace(b"reasoning effort: low", b"reasoning effort: xhigh"))])
def test_live_call_failure_is_ran_error_never_an_empty_answer(runner, offline):
    """Plants: a crashed client, an empty final message, an unreported model, a model other than the one requested,
    and an effort other than the one set -- each becomes RAN_ERROR, never a replayable response."""
    rec = _live(runner=runner)
    assert rec["state"] == "RAN_ERROR" and rec["error"]
    with pytest.raises(ms.ReplayRefused):
        ms.replay(rec)


def test_client_header_is_parsed_and_the_local_path_is_dropped(offline):
    from reproducible_ai import model_call_live
    h = model_call_live.client_header(HEADER.decode())
    assert h["model"] == "planted-model" and h["session id"] == "s-1" and h["tokens used"] == "1,234"
    assert "workdir" not in h
    rec = _live(runner=_fake())
    assert "somewhere" not in json.dumps(rec)


# ---------------------------------------------------------------------------------------------------- proposals
def _proposal():
    rec = _record()
    return ms.Proposal(task="estimand", item_id="glp1::PMID 1::analysis_set", record_id=rec["record_id"],
                       claim={"field": "analysis_set", "value": "intention-to-treat",
                              "quote": "The primary analysis was performed in the intention-to-treat population."})


def test_a_proposal_is_proposed_and_cannot_be_promoted_by_assignment():
    p = _proposal()
    assert p.status == "PROPOSED"
    with pytest.raises(AttributeError):
        p.status = "ACCEPTED"
    with pytest.raises(AttributeError):
        p.claim = {}


@pytest.mark.parametrize("use", ["float", "int", "bool", "index", "iter", "getitem", "len", "format", "json", "add",
                                 "compare", "hash"])
def test_a_proposal_reaching_an_admission_path_raises(use):
    """Every way a producer, a pool, a predicate or a renderer could consume a value: each must raise."""
    p = _proposal()
    ops = {
        "float": lambda: float(p), "int": lambda: int(p), "bool": lambda: bool(p), "index": lambda: [0, 1][p],
        "iter": lambda: list(p), "getitem": lambda: p["value"], "len": lambda: len(p),
        "format": lambda: f"{p}", "json": lambda: json.dumps({"row": p}), "add": lambda: p + 1,
        "compare": lambda: p < 1, "hash": lambda: {p: 1},
    }
    with pytest.raises((ms.ProposalNotAdmissible, TypeError)) as ei:
        ops[use]()
    assert "PROPOSED" in str(ei.value) or isinstance(ei.value, TypeError)


def test_a_proposal_planted_in_the_real_pooling_and_screening_entry_points_raises():
    """Plants into the harness's own consumers, not a mock: synth.pool (the one canonical pooling path), a Study
    carrying a proposal as a count, and screen.screen_record (the rule screen)."""
    from harness import screen, synth
    p = _proposal()
    with pytest.raises(ms.ProposalNotAdmissible):
        synth.pool([p])
    cfg = json.loads((ROOT / "topics" / "glp1-ra-mace-t2d.json").read_text(encoding="utf-8"))
    with pytest.raises(ms.ProposalNotAdmissible):
        screen.screen_record(p, cfg["include"], set())
    with pytest.raises((ms.ProposalNotAdmissible, TypeError)):
        synth.pool([synth.Study("x", p, 100, 5, 100)])


def test_admit_refuses_a_bare_proposal():
    with pytest.raises(ms.ProposalNotAdmissible):
        ms.admit(_proposal(), entry=None, record=None, held_text=None)
    rec, entry = _entry()
    with pytest.raises(ms.ProposalNotAdmissible):       # verified, replayable, but OPEN: refused
        ms.admit(ms.Proposal.from_entry(entry), entry=entry, record=rec, held_text=HELD)


def test_no_pinned_producer_can_read_a_proposal():
    """Structural: nothing in the certificate's code closure imports model_source or names the proposal store."""
    cert_paths = sorted({p for p in ms.pinned_closure(ROOT)})
    assert cert_paths, "the certificate closure could not be read -- this check would pass vacuously"
    offenders = []
    for rel in cert_paths:
        f = ROOT / rel
        if not f.exists() or f.suffix != ".py":
            continue
        src = f.read_text(encoding="utf-8")
        if "model_source" in src or "model_proposals" in src or "model_calls" in src:
            offenders.append(rel)
    assert offenders == []


def _importers_of_package(files):
    out = []
    for f in files:
        tree = ast.parse(Path(f).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            mods = ([a.name for a in node.names] if isinstance(node, ast.Import)
                    else [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
            if any(m.split(".")[0] == "reproducible_ai" for m in mods) or "model_proposals" in ast.dump(node):
                out.append(Path(f).name)
                break
    return out


def test_no_harness_module_and_no_build_entry_point_imports_the_package():
    """Wider than the certificate closure: every harness/*.py (the certificate's own in-tree scan scope,
    harness/certificate.py) and the build/reproduce entry points. The package sits OUTSIDE harness/ so that adding it
    does not re-certify 32 pages for a module no page uses; this test is what makes that placement honest."""
    targets = sorted((ROOT / "harness").glob("*.py")) + [ROOT / "scripts" / "build_topic.py",
                                                         ROOT / "scripts" / "reproduce_review.py"]
    assert len(targets) > 10
    assert _importers_of_package(targets) == []


def test_the_import_sweep_can_fire(tmp_path):
    """Plants: an import of the package, and a read of the proposal store, are each caught by the SAME scan."""
    a = tmp_path / "a.py"
    a.write_text("from reproducible_ai import model_source\n", encoding="utf-8")
    b = tmp_path / "b.py"
    b.write_text("import json\nrows = json.load(open('registry/model_proposals/screening.json'))\n", encoding="utf-8")
    c = tmp_path / "c.py"
    c.write_text("import json\n", encoding="utf-8")
    assert _importers_of_package([a, b, c]) == ["a.py", "b.py"]


# ---------------------------------------------------------------------------------------------------- verifiers
def test_estimand_span_must_be_located_in_the_held_text():
    ok = ms.verify_estimand({"field": "analysis_set", "value": "intention-to-treat",
                             "quote": "The primary analysis was performed in the intention-to-treat population."}, HELD)
    assert ok["state"] == "VERIFIER_PASS"
    assert HELD[ok["start"]:ok["end"]] == "The primary analysis was performed in the intention-to-treat population."
    bad = ms.verify_estimand({"field": "analysis_set", "value": "intention-to-treat",
                              "quote": "The analysis used the full analysis set."}, HELD)
    assert bad["state"] == "VERIFIER_REFUSED" and "SPAN_NOT_IN_SOURCE" in bad["problems"][0]


def test_estimand_value_outside_the_rule_vocabulary_is_refused():
    r = ms.verify_estimand({"field": "analysis_set", "value": "modified ITT (as I understand it)",
                            "quote": "The primary analysis was performed in the intention-to-treat population."}, HELD)
    assert r["state"] == "VERIFIER_REFUSED"


def test_estimand_not_stated_carries_no_span():
    assert ms.verify_estimand({"field": "analysis_window", "value": "NOT_STATED", "quote": None}, HELD)["state"] == "VERIFIER_PASS"
    r = ms.verify_estimand({"field": "analysis_window", "value": "NOT_STATED", "quote": "placebo-controlled"}, HELD)
    assert r["state"] == "VERIFIER_REFUSED"


def _estimand_tables():
    import importlib.util
    out = {}
    for rel in ("scripts/build_bundle.py", "scripts/verify_bundle.py", "docs/scripts/verify_bundle.py"):
        spec = importlib.util.spec_from_file_location("_t_" + rel.replace("/", "_"), ROOT / rel)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        out[rel] = mod._ESTIMAND
    return out


def _drift(tables):
    base = tables["scripts/build_bundle.py"]
    return sorted(rel for rel, t in tables.items() if t != base)


def test_the_estimand_rule_the_gate_uses_is_the_one_the_served_verifier_runs():
    """The gate reads build_bundle._ESTIMAND; the served checker (docs/scripts/verify_bundle.py) carries its own copy.
    If they drift, 'the same verifier' is false. Plant: a copy with one pattern changed is reported."""
    tables = _estimand_tables()
    assert _drift(tables) == []
    planted = copy.deepcopy(tables)
    planted["docs/scripts/verify_bundle.py"]["analysis_set"] = planted["docs/scripts/verify_bundle.py"]["analysis_set"][:-1]
    assert _drift(planted) == ["docs/scripts/verify_bundle.py"]


def test_estimand_not_stated_is_compared_with_the_rule_over_the_whole_text():
    """Both silent = agreement (batchable). The model saying NOT_STATED where the rule's own regex DOES find a
    statement in the held text = disagreement (individual signature)."""
    silent = ms.verify_estimand({"field": "analysis_window", "value": "NOT_STATED", "quote": None}, HELD)
    assert silent["agreement"].startswith("RULE_MODEL_AGREE") and not ms.needs_individual_signature(silent)
    missed = ms.verify_estimand({"field": "analysis_set", "value": "NOT_STATED", "quote": None}, HELD)
    assert missed["rule_on_text"]["values"] == ["intention-to-treat"]
    assert missed["agreement"].startswith("RULE_MODEL_DISAGREE") and ms.needs_individual_signature(missed)


def test_estimand_rule_on_the_span_is_recorded_not_resolved():
    r = ms.verify_estimand({"field": "analysis_set", "value": "per-protocol",
                            "quote": "The primary analysis was performed in the intention-to-treat population."}, HELD)
    # the rule reads intention-to-treat in the very span the model cites: a disagreement, recorded, never resolved
    assert r["state"] == "VERIFIER_PASS"
    assert r["rule_on_span"]["values"] == ["intention-to-treat"]
    assert r["agreement"].startswith("RULE_MODEL_DISAGREE")


LOCATE_OK = {"span": "The primary analysis was performed in the intention-to-treat population.",
             "is_target_outcome": True, "population_matches": True, "both_arms": True, "timepoint": "unspecified",
             "why": "fixture"}


def test_locate_span_must_be_in_the_held_abstract_and_a_target_claim_must_quote():
    assert ms.verify_locate(LOCATE_OK, HELD)["state"] == "VERIFIER_PASS"
    planted = dict(LOCATE_OK, span="The primary analysis was per protocol.")
    assert "SPAN_NOT_IN_SOURCE" in ms.verify_locate(planted, HELD)["problems"][0]
    assert ms.verify_locate(dict(LOCATE_OK, span=None), HELD)["state"] == "VERIFIER_REFUSED"      # target without a span
    assert ms.verify_locate(dict(LOCATE_OK, span=None, is_target_outcome=False), HELD)["state"] == "VERIFIER_PASS"
    assert ms.verify_locate(dict(LOCATE_OK, both_arms="yes"), HELD)["state"] == "VERIFIER_REFUSED"


def test_a_recorded_remake_is_compared_with_the_unrecorded_prior_and_disagreement_needs_an_individual_signature():
    agree = ms.verify_locate(LOCATE_OK, HELD, prior={"is_target_outcome": True, "population_matches": True})
    assert agree["agreement"].startswith("PRIOR_MODEL_AGREE") and not ms.needs_individual_signature(agree)
    flip = ms.verify_locate(LOCATE_OK, HELD, prior={"is_target_outcome": False, "population_matches": True})
    assert flip["agreement"].startswith("PRIOR_MODEL_DISAGREE") and "is_target_outcome: prior=False model=True" in flip["agreement"]
    assert ms.needs_individual_signature(flip)
    assert ms.needs_individual_signature(ms.verify_locate(LOCATE_OK, HELD))         # no prior: never batchable


def test_outcome_identity_is_typed_and_compared_with_its_prior():
    ok = {"candidate_population": "p", "candidate_timepoint": "t", "candidate_definition": "d", "is_match": True,
          "rationale": "r"}
    assert ms.verify_outcome_identity(ok, "title: x", {"is_match": True})["agreement"].startswith("PRIOR_MODEL_AGREE")
    assert ms.needs_individual_signature(ms.verify_outcome_identity(ok, "title: x", {"is_match": False}))
    assert ms.verify_outcome_identity(dict(ok, is_match="true"), "title: x")["state"] == "VERIFIER_REFUSED"
    assert ms.verify_outcome_identity({k: v for k, v in ok.items() if k != "rationale"}, "t")["state"] == "VERIFIER_REFUSED"
    assert ms.verify_outcome_identity(dict(ok, candidate_definition=" "), "t")["state"] == "VERIFIER_REFUSED"


def test_screening_quote_must_be_located_and_axes_typed():
    axes = {"population": {"verdict": "MET", "quote": "3183 patients with type 2 diabetes"},
            "intervention": {"verdict": "MET", "quote": "Oral Semaglutide"},
            "comparator": {"verdict": "MET", "quote": "placebo-controlled"},
            "design": {"verdict": "MET", "quote": "randomized, double-blind, placebo-controlled trial"}}
    ok = ms.verify_screening({"axes": axes}, HELD, rule_decision="include")
    assert ok["state"] == "VERIFIER_PASS" and ok["model_decision"] == "ELIGIBLE"
    assert ok["agreement"] == "RULE_MODEL_AGREE"
    planted = copy.deepcopy(axes)
    planted["population"]["quote"] = "3183 adults with heart failure"
    assert ms.verify_screening({"axes": planted}, HELD, rule_decision="include")["state"] == "VERIFIER_REFUSED"
    typed = copy.deepcopy(axes)
    typed["design"]["verdict"] = "PROBABLY"
    assert ms.verify_screening({"axes": typed}, HELD, rule_decision="include")["state"] == "VERIFIER_REFUSED"
    missing = copy.deepcopy(axes)
    del missing["comparator"]
    assert ms.verify_screening({"axes": missing}, HELD, rule_decision="include")["state"] == "VERIFIER_REFUSED"


def test_screening_disagreement_is_recorded_and_needs_an_individual_signature():
    axes = {"population": {"verdict": "NOT_MET", "quote": "3183 patients with type 2 diabetes"},
            "intervention": {"verdict": "MET", "quote": "Oral Semaglutide"},
            "comparator": {"verdict": "MET", "quote": "placebo-controlled"},
            "design": {"verdict": "MET", "quote": "randomized, double-blind, placebo-controlled trial"}}
    r = ms.verify_screening({"axes": axes}, HELD, rule_decision="include")
    assert r["model_decision"] == "INELIGIBLE"
    assert r["agreement"].startswith("RULE_MODEL_DISAGREE(rule=include, model=INELIGIBLE")
    assert ms.needs_individual_signature(r)


# ---------------------------------------------------------------------------------------------------- committed data
def _pilot():
    import importlib.util
    spec = importlib.util.spec_from_file_location("_mh_pilot_t", ROOT / "scripts" / "model_source_pilot.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_committed_record_replays_or_is_a_recorded_error(offline):
    recs = sorted((ROOT / ms.RECORD_DIR).glob("*.json"))
    for p in recs:
        r = ms.load_record(p)
        assert p.stem == r["record_id"], f"{p.name}: file name is not the record's content id"
        assert ms.record_problems(r) == [], p.name
        if r["state"] == "RAN_OK":
            ms.replay(r)
        else:
            assert r["error"] and r["response"]["bytes"] == 0, p.name
        blob = json.dumps(r)
        assert "\\Users\\" not in blob and ":\\\\" not in blob, f"{p.name} carries a local path"


def test_the_source_of_a_proposal_is_the_earliest_ordinary_call_whatever_the_file_order():
    """Plants: a stability re-ask, a later ordinary call, and an error -- presented in every order -- never displace
    the earliest RAN_OK ordinary call as the proposal's source. (Before this, the queue took the LAST record in
    file-name order: a hash, so a second call of the same prompt made the source arbitrary.)"""
    import itertools
    pilot = _pilot()
    first = _record(request_utc="2026-09-23T22:00:00Z", response_utc="2026-09-23T22:00:05Z")
    later = _record(response=b'{"answer": 9}', request_utc="2026-09-24T09:00:00Z", response_utc="2026-09-24T09:00:05Z")
    reask = _record(response=b'{"answer": 7}', request_utc="2026-09-23T21:00:00Z", response_utc="2026-09-23T21:00:05Z",
                    caller={"file": "t", "line": 1, "purpose": pilot.STABILITY_PURPOSE + first["record_id"]})
    err = _record(response=b"", state="RAN_ERROR", error="x", request_utc="2026-09-23T20:00:00Z",
                  response_utc="2026-09-23T20:00:05Z")
    for perm in itertools.permutations([first, later, reask, err]):
        assert pilot.source_record(list(perm))["record_id"] == first["record_id"]
    assert pilot.source_record([reask]) is None           # a re-ask alone is never a source
    assert pilot.source_record([err])["state"] == "RAN_ERROR"


def test_a_frozen_population_never_shrinks_when_the_rule_moves(tmp_path, monkeypatch):
    """Plants on a synthetic population: A is now excluded by the rule, B's held text changed, C is newly selected.
    A stays (with the rule's NEW decision recorded), B becomes HELD_TEXT_DRIFT, C is reported as drift, not added."""
    pilot = _pilot()
    sha = lambda t: ms.sha256_bytes(t.encode("utf-8"))  # noqa: E731
    pop = {"task": "screening", "N": 2, "items": [
        {"item_id": "A", "slug": "s", "held_ref": "r", "held_sha256": sha("a"), "rule_decision": "include"},
        {"item_id": "B", "slug": "s", "held_ref": "r", "held_sha256": sha("b"), "rule_decision": "include"}]}
    (tmp_path / "screening.population.json").write_text(json.dumps(pop), encoding="utf-8")
    now = [{"item_id": "A", "slug": "s", "held_ref": "r", "held_text": "a", "held_sha256": sha("a"), "rule_decision": "exclude"},
           {"item_id": "B", "slug": "s", "held_ref": "r", "held_text": "b2", "held_sha256": sha("b2"), "rule_decision": "include"},
           {"item_id": "C", "slug": "s", "held_ref": "r", "held_text": "c", "held_sha256": sha("c"), "rule_decision": "include"}]
    monkeypatch.setattr(pilot, "Q_DIR", tmp_path)
    monkeypatch.setitem(pilot.CANDIDATES, "screening", lambda: now)
    got = {i["item_id"]: i for i in pilot.pilot_items("screening")}
    assert sorted(got) == ["A", "B"]
    assert got["A"]["rule_decision"] == "exclude" and got["A"]["rule_decision_at_freeze"] == "include"
    assert got["A"].get("held_text") == "a"
    assert got["B"]["state"] == "HELD_TEXT_DRIFT" and "held_text" not in got["B"]
    assert pilot.population_drift("screening") == {"frozen_not_selected_now": ["A"], "selected_now_not_frozen": ["C"]}
    with pytest.raises(SystemExit):
        pilot.cmd_freeze("screening", "0" * 40)          # a population is frozen once


@pytest.mark.parametrize("task", ["screening", "estimand", "outcome_identity", "locate", "screening_reader2", "screening_excluded"])
def test_a_committed_queue_covers_its_whole_denominator_and_claims_nothing_it_cannot_show(task):
    q = ROOT / ms.PROPOSAL_DIR / f"{task}.json"
    if not q.exists():
        pytest.skip(f"no committed {task} queue in this tree")
    pilot = _pilot()
    doc, rows = pilot.gated(task)
    items = pilot.pilot_items(task)
    # the denominator is the FROZEN population (committed beside the queue), every member present with a state
    pop = json.loads(pilot.population_path(task).read_text(encoding="utf-8"))
    assert doc["N"] == pop["N"] == len(pop["items"]) == len(items) == len(doc["items"])
    assert sorted(e["item_id"] for e in doc["items"]) == sorted(i["item_id"] for i in pop["items"])
    # no stored record goes unused: every callable item's batch found its record (no silent re-call)
    assert not [e["item_id"] for e in doc["items"] if e.get("state") == "NOT_YET_CALLED"]
    held = {i["item_id"]: i.get("held_text") for i in items}
    planted = 0
    for e, _, _ in rows:     # plant on REAL entries: the task's own verifier must refuse a one-word corruption
        if "claim" not in e or held.get(e["item_id"]) is None:
            continue
        bad = copy.deepcopy(e)
        c = bad["claim"]
        if task == "outcome_identity":
            c["is_match"] = "yes"                                           # typed check
        elif task == "locate":
            if not c.get("span"):
                continue
            c["span"] += " zz-planted-word"                                 # span ladder
        else:
            q = [v for v in ((c.get("axes") or {"x": c}).values()) if isinstance(v, dict) and v.get("quote")]
            if not q:
                continue
            q[0]["quote"] += " zz-planted-word"                             # span ladder
        assert ms.reverify(bad, held[e["item_id"]])["state"] == "VERIFIER_REFUSED", e["item_id"]
        planted += 1
        if planted >= 5:
            break
    assert planted > 0 or not any("claim" in e for e in doc["items"])
    for e, status, problems in rows:
        if "claim" not in e:
            assert e["state"] in ("NO_HELD_TEXT", "HELD_TEXT_DRIFT", "RAN_ERROR", "RESPONSE_NOT_A_CLAIM", "NOT_YET_CALLED")
            continue
        assert e["status"] == "PROPOSED"                   # the stored word never says more than PROPOSED
        sig = e.get("reviewer_countersignature") or {}
        if sig.get("state") != "OPEN":
            # a signature present in the file must pass the gate today, or the file claims something it cannot show
            assert status == "COUNTERSIGNED", (e["item_id"], problems)


# ---------------------------------------------------------------------------------------------------- the gate
def _entry():
    rec = _record(response=json.dumps({"field": "analysis_set", "value": "intention-to-treat",
                                        "quote": "The primary analysis was performed in the intention-to-treat population."}).encode())
    claim = json.loads(ms.replay(rec))
    ver = ms.verify_estimand(claim, HELD)
    entry = ms.queue_entry(task="estimand", item_id="glp1::PMID 1::analysis_set", record=rec, claim=claim,
                           verification=ver, held_ref="fixture:held", held_sha256=HELD_SHA)
    return rec, entry


def test_queue_entry_starts_open_and_proposed():
    rec, entry = _entry()
    assert entry["reviewer_countersignature"] == {"state": "OPEN"}
    assert ms.status_of(entry, rec, HELD) == "PROPOSED"


def _sign(entry, rec, **over):
    block = ms.render_proposal_block(entry, rec)
    sig = {"state": "SEEN_AND_SIGNED", "by": "Reviewer Fixture", "when_utc": "2026-09-24T09:00:00Z",
           "rendered_sha256": result_changes.rendered_sha256(block),
           "how_it_reached_the_reviewer": "the rendered block itself (fixture)"}
    sig.update(over)
    e = copy.deepcopy(entry)
    e["reviewer_countersignature"] = sig
    return e


def test_all_three_conditions_are_needed_and_none_suffices_alone():
    rec, entry = _entry()
    signed = _sign(entry, rec)
    assert ms.status_of(signed, rec, HELD) == "COUNTERSIGNED"
    # (a) the verifier refuses -> stays PROPOSED even when signed
    tampered_text = HELD.replace("intention-to-treat", "full analysis")
    assert ms.status_of(signed, rec, tampered_text) == "PROPOSED"
    # (b) the record does not replay -> stays PROPOSED even when signed and verified
    bad = copy.deepcopy(rec)
    bad["response"]["b64"] = base64.b64encode(b"{}").decode()
    assert ms.status_of(signed, bad, HELD) == "PROPOSED"
    # (c) no countersignature / OPEN / a signature over different bytes / missing basis -> PROPOSED
    assert ms.status_of(entry, rec, HELD) == "PROPOSED"
    assert ms.status_of(_sign(entry, rec, rendered_sha256="f" * 64), rec, HELD) == "PROPOSED"
    assert ms.status_of(_sign(entry, rec, how_it_reached_the_reviewer=" "), rec, HELD) == "PROPOSED"
    assert ms.status_of(_sign(entry, rec, state="ASSUMED_ACCEPTED"), rec, HELD) == "PROPOSED"


def test_the_claim_in_the_queue_must_be_the_claim_the_record_replays():
    rec, entry = _entry()
    signed = _sign(entry, rec)
    forged = copy.deepcopy(signed)
    forged["claim"]["value"] = "per-protocol"          # queue edited after the call; the record says otherwise
    assert ms.status_of(forged, rec, HELD) == "PROPOSED"


def test_a_whitespace_only_edit_is_caught_although_the_signature_digest_normalises_whitespace():
    """result_changes.rendered_sha256 collapses whitespace, so a signature cannot tell 'a  b' from 'a b'. The gate does
    not rely on it for that: the queued claim must equal the stored response's claim exactly."""
    rec, entry = _entry()
    signed = _sign(entry, rec)
    edited = copy.deepcopy(signed)
    edited["claim"]["quote"] = edited["claim"]["quote"].replace("primary analysis", "primary  analysis")
    edited["verification"] = ms.verify_estimand(edited["claim"], HELD.replace("primary analysis", "primary  analysis"))
    assert result_changes.rendered_sha256(ms.render_proposal_block(edited, rec)) == signed["reviewer_countersignature"]["rendered_sha256"]
    problems = ms.gate_problems(edited, rec, HELD.replace("primary analysis", "primary  analysis"))
    assert any(p.startswith("CLAIM_NOT_THE_RECORDED_ONE") for p in problems)


def test_no_timeout_or_default_promotes_a_proposal():
    rec, entry = _entry()
    aged = copy.deepcopy(entry)
    aged["queued_utc"] = "2000-01-01T00:00:00Z"
    aged["reviewer_countersignature"] = {"state": "OPEN", "default_after_days": 0}
    assert ms.status_of(aged, rec, HELD) == "PROPOSED"


def test_a_disagreement_refuses_a_batch_signature():
    rec = _record(response=json.dumps({"field": "analysis_set", "value": "per-protocol",
                                       "quote": "The primary analysis was performed in the intention-to-treat population."}).encode())
    claim = json.loads(ms.replay(rec))
    entry = ms.queue_entry(task="estimand", item_id="x", record=rec, claim=claim,
                           verification=ms.verify_estimand(claim, HELD), held_ref="fixture:held", held_sha256=HELD_SHA)
    batch = _sign(entry, rec, state="BATCH_SEEN_AND_SIGNED", batch_id="B1")
    assert ms.status_of(batch, rec, HELD) == "PROPOSED"
    assert ms.status_of(_sign(entry, rec), rec, HELD) == "COUNTERSIGNED"


def test_an_unstable_agreement_refuses_a_batch_signature():
    """A proposal that agrees with the rule, but whose identical-prompt re-ask reached a different decision, is not
    batch-signable (observed: LEADER, ELIGIBLE on the source call, CANNOT_TELL on the re-ask). The flag is shown in
    the block the reviewer signs, and the gate treats it as binding."""
    rec, entry = _entry()
    assert not ms.needs_individual_signature(entry["verification"])
    unstable = copy.deepcopy(entry)
    unstable["individual_signature_required"] = True
    unstable["reask"] = {"records": ["mc-x"], "same_derived_decision": False, "decisions": ["ELIGIBLE", "CANNOT_TELL"]}
    assert "re-ask" in ms.render_proposal_block(unstable, rec)
    assert ms.status_of(_sign(unstable, rec, state="BATCH_SEEN_AND_SIGNED", batch_id="B1"), rec, HELD) == "PROPOSED"
    assert ms.status_of(_sign(unstable, rec), rec, HELD) == "COUNTERSIGNED"
    assert ms.status_of(_sign(entry, rec, state="BATCH_SEEN_AND_SIGNED", batch_id="B1"), rec, HELD) == "COUNTERSIGNED"


def test_countersigned_is_review_material_not_an_admission():
    """Even a fully countersigned proposal returns an inert object: the build has no reader for it in this landing."""
    rec, entry = _entry()
    signed = _sign(entry, rec)
    out = ms.admit(ms.Proposal.from_entry(signed), entry=signed, record=rec, held_text=HELD)
    assert out["status"] == "COUNTERSIGNED"
    assert out["admits_into_build"] is False
    other = ms.Proposal(signed["task"], signed["item_id"], signed["record_id"], {"field": "analysis_set", "value": "as-treated", "quote": None})
    with pytest.raises(ms.ProposalNotAdmissible):       # a different claim riding on a signed entry
        ms.admit(other, entry=signed, record=rec, held_text=HELD)


def test_render_block_is_deterministic_and_names_the_record():
    rec, entry = _entry()
    a, b = ms.render_proposal_block(entry, rec), ms.render_proposal_block(copy.deepcopy(entry), rec)
    assert a == b
    assert rec["record_id"] in a and rec["response"]["sha256"] in a and "PROPOSED" in a
