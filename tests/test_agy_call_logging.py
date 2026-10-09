"""PLANT: a REAL agy call (runner is model_call_live.agy_runner) must reach log_call with every key it requires.

9 Oct 2026: agy_call built a facts dict without 'outside_workdir_reads'; log_call raised KeyError after the model had
answered and before the record was returned, so a real Gemini call went unrecorded. The existing agy tests pass a fake
runner, which skips log_call, so none of them could see it. Here the fake is installed AS agy_runner.
"""
from __future__ import annotations

import json

from reproducible_ai import model_call_live as mcl


def test_a_real_path_agy_call_is_logged_and_returns_its_record(tmp_path, monkeypatch):
    def fake(prompt, schema, timeout_s, images=()):
        out = {"status": "SUCCESS", "response": '{"ok": "OK"}', "num_turns": 1, "usage": {"total_tokens": 7},
               "denied_actions": []}
        log = 'I1009 x model_config_manager.go:1] Propagating selected model override to backend: label="Gemini 3.1 Pro (High)"\n'
        return {"rc": 0, "stdout": json.dumps(out).encode(), "stderr": b"", "log": log.encode(),
                "argv": ["agy", "--print", "<prompt>"]}
    monkeypatch.setattr(mcl, "agy_runner", fake)                 # the real-call branch: runner IS agy_runner
    monkeypatch.setattr(mcl, "LANE_LOG_DIR", tmp_path)
    rec = mcl.agy_call(b"ok?", schema={"type": "object"}, client_version="agy-test",
                       caller={"file": "tests/test_agy_call_logging.py", "line": "1", "purpose": "plant", "lane": "test"},
                       input_digests=[], settings=("Gemini 3.1 Pro (High)", "c" * 64))
    assert rec["state"] == "RAN_OK"
    lines = [json.loads(x) for f in tmp_path.iterdir() for x in f.read_text(encoding="utf-8").splitlines()]
    assert [x["record_id"] for x in lines] == [rec["record_id"]]
    assert lines[0]["outside_workdir_reads"] == []
