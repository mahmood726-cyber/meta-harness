"""CODEX-2 follow-up: a call is logged under the lane its CALLER names, never under this lane by default.

The fault (found landing R3, 2026-09-25): model_call_live.LANE was hard-coded "rai", so the evidence lane's 53 codex
calls (caller lane 'evid/evidence-records') were written into registry/model_calls/lane_log/rai.jsonl with
"lane": "rai" -- a per-lane record that attributed another lane's calls to this one. Plant: fired on the old code.
"""
import json

from reproducible_ai import model_call_live as live

PROMPT = b"a prompt\n"
OK_EXEC = ("OpenAI Codex v0.153.4\n--------\nworkdir: <workdir>\nmodel: gpt-6-astra\nprovider: openai\napproval: never\n"
           "sandbox: read-only\nreasoning effort: medium\nreasoning summaries: none\nsession id: x\n--------\nuser\n"
           "a prompt\ncodex\n{\"items\": []}\ntokens used\n12,345\n")


def _fake(prompt, schema, model, effort, timeout_s):
    return {"rc": 0, "stdout": b"", "stderr": OK_EXEC.encode(), "last_message": b'{"items": []}',
            "argv": ["fake-client", "exec"]}


def _real_call(tmp_path, monkeypatch, caller):
    monkeypatch.setattr(live, "LANE_LOG_DIR", tmp_path, raising=False)
    monkeypatch.setattr(live, "LANE_LOG", tmp_path / "rai.jsonl")
    monkeypatch.setattr(live, "codex_runner", _fake)
    return live.call(PROMPT, schema={"type": "object"}, model="gpt-6-astra", effort="medium", caller=caller,
                     input_digests=[], runner=None, client_version="0.153.4")


def _lines(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def test_another_lanes_call_is_not_logged_as_this_lane(tmp_path, monkeypatch):
    rec = _real_call(tmp_path, monkeypatch, {"file": "t", "line": "1", "purpose": "x", "lane": "evid/evidence-records"})
    assert _lines(tmp_path / "rai.jsonl") == []
    theirs = _lines(tmp_path / "evid__evidence-records.jsonl")
    assert [x["lane"] for x in theirs] == ["evid/evidence-records"] and theirs[0]["record_id"] == rec["record_id"]
    assert rec["client_evidence"]["lane_log"] == "registry/model_calls/lane_log/evid__evidence-records.jsonl"


def test_a_call_naming_no_lane_is_unattributed_not_this_lane(tmp_path, monkeypatch):
    _real_call(tmp_path, monkeypatch, {"file": "t", "line": "1", "purpose": "x"})
    assert _lines(tmp_path / "rai.jsonl") == []
    assert [x["lane"] for x in _lines(tmp_path / "unattributed.jsonl")] == ["unattributed"]


def test_this_lanes_call_still_lands_in_rai(tmp_path, monkeypatch):
    _real_call(tmp_path, monkeypatch, {"file": "t", "line": "1", "purpose": "x", "lane": "rai"})
    assert [x["lane"] for x in _lines(tmp_path / "rai.jsonl")] == ["rai"]


def test_a_lane_name_cannot_escape_the_log_directory(tmp_path, monkeypatch):
    _real_call(tmp_path, monkeypatch, {"file": "t", "line": "1", "purpose": "x", "lane": "../../harness/x"})
    written = [p for p in tmp_path.rglob("*") if p.is_file()]
    assert len(written) == 1 and written[0].parent == tmp_path and written[0].name.endswith("harness__x.jsonl")
    assert "/" not in written[0].name and ".." not in written[0].name
