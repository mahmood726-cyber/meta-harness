"""PLANT: a REAL agy call (runner is model_call_live.agy_runner) must reach log_call with every key it requires.

9 Oct 2026: agy_call built a facts dict without 'outside_workdir_reads'; log_call raised KeyError after the model had
answered and before the record was returned, so a real Gemini call went unrecorded. The existing agy tests pass a fake
runner, which skips log_call, so none of them could see it. Here the fake is installed AS agy_runner.
"""
from __future__ import annotations

import base64
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


def test_PLANT_agy_call_refuses_a_non_open_text_before_running(monkeypatch):
    import base64  # noqa: F401
    import pytest
    ran = []
    monkeypatch.setattr(mcl, "agy_runner", lambda *a, **k: ran.append(1) or {})
    prompt = ("<<<TEXT\n" + "A trial sentence of full text. " * 400 + "\nTEXT>>>").encode()
    with pytest.raises(mcl.LicenceRefused):
        mcl.agy_call(prompt, schema={"type": "object"}, client_version="agy-test",
                     caller={"file": "tests/test_agy_call_logging.py", "line": "2", "purpose": "plant", "lane": "test"},
                     input_digests=[{"ref": "held open text PMID 99999999 (HELD_CACHE_FT)", "sha256": "a" * 64}],
                     settings=("Gemini 3.1 Pro (High)", "c" * 64))
    assert ran == [], "the model was called before the licence guard refused"


def _chunk_runner(seen, answer_canaries):
    def run(prompt, schema, timeout_s, images=(), files=()):
        seen["prompt"], seen["files"] = prompt, dict(files)
        cans = [line.rsplit(": ", 1)[1] for d in seen["files"].values() for line in d.decode().splitlines()
                if line.startswith("END OF PART")]
        resp = json.dumps({"ok": "OK", "parts_read": cans[:answer_canaries]})
        out = {"status": "SUCCESS", "response": resp, "num_turns": 1, "usage": {"total_tokens": 7}, "denied_actions": []}
        log = 'I1009 x m.go:1] Propagating selected model override to backend: label="Gemini 3.1 Pro (High)"\n'
        return {"rc": 0, "stdout": json.dumps(out).encode(), "stderr": b"", "log": log.encode(), "argv": ["<agy>"]}
    return run


def _chunk_call(runner, prompt):
    return mcl.agy_call(prompt, schema={"type": "object"}, client_version="agy-test", runner=runner, chunk_chars=1000,
                        caller={"file": "tests/test_agy_call_logging.py", "line": "3", "purpose": "plant", "lane": "test"},
                        input_digests=[], settings=("Gemini 3.1 Pro (High)", "c" * 64))


def test_chunked_transport_keeps_the_full_prompt_in_the_record_and_sends_a_short_instruction():
    seen, prompt = {}, ("x" * 2500).encode()
    rec = _chunk_call(_chunk_runner(seen, 99), prompt)
    assert rec["state"] == "RAN_OK", rec.get("error")
    assert len(seen["prompt"]) < 2000 and len(seen["files"]) == 3            # the argv carries only the instruction
    assert "".join(d.decode().split("\n\nEND OF PART")[0] for d in seen["files"].values()) == prompt.decode()
    assert base64.b64decode(rec["prompt"]["b64"]) == prompt if "b64" in rec["prompt"] else True
    assert len(rec["params"]["transport"]["canaries"]) == 3


def test_PLANT_an_answer_missing_a_part_canary_is_RAN_ERROR():
    """A file tool that truncates (or a model that stops early) must not yield a usable review."""
    rec = _chunk_call(_chunk_runner({}, 2), ("y" * 2500).encode())
    assert rec["state"] == "RAN_ERROR" and "2 of 3 part canaries" in rec["error"]
