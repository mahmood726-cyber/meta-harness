"""CODEX-2: every real codex call leaves a per-lane record -- prompt (by digest), tool calls with their outcome, files
read, tokens -- and the record itself carries the counts."""
from __future__ import annotations

import json
from pathlib import Path

from reproducible_ai import model_call_live as live

FIX = Path(__file__).resolve().parent / "fixtures" / "codex_stderr_rejected_exec.txt"
PROMPT = b"Label these sentences."
OK_EXEC = ("OpenAI Codex v0.153.4\n--------\nworkdir: <workdir>\nmodel: gpt-6-astra\nprovider: openai\napproval: never\n"
           "sandbox: read-only\nreasoning effort: medium\nreasoning summaries: none\nsession id: x\n--------\nuser\n"
           "Label these sentences.\ncodex\nreading\nexec\npowershell -Command Get-Content C:\\Users\\mahmo\\.claude\\AGENTS.md in "
           "C:\\mh-lanes\\mcall\\mcall-abc123\n succeeded in 21ms:\n# AGENTS\ncodex\n{\"items\": []}\ntokens used\n12,345\n")


def test_a_real_rejected_tool_call_is_counted_with_its_tokens():
    f = live.transcript_facts(FIX.read_text(encoding="utf-8"), b"")
    assert f["tokens_used"] == 25808 and f["tool_calls_n"] == 1 and f["tool_calls_rejected_n"] == 1 and f["files_read"] == []


def test_a_successful_read_is_logged_with_the_file_and_the_prompt_is_replaced_by_its_digest():
    f = live.transcript_facts(OK_EXEC, PROMPT)
    assert f["tokens_used"] == 12345 and f["tool_calls_n"] == 1 and f["tool_calls_rejected_n"] == 0
    assert any(p.endswith("AGENTS.md") for p in f["files_read"])
    assert "Label these sentences." not in f["transcript_redacted"] and "<prompt sha256" in f["transcript_redacted"]
    assert "mcall-abc123" not in f["transcript_redacted"]


def _fake(rc=0):
    def runner(prompt, schema, model, effort, timeout_s):
        return {"rc": rc, "stdout": b"", "stderr": OK_EXEC.replace("gpt-6-astra", model).encode(),
                "last_message": b'{"items": []}', "argv": ["fake-client", "exec"]}
    return runner


def test_every_real_call_writes_one_lane_log_line(tmp_path, monkeypatch):
    # plant (fired before CODEX-2's fix: call() wrote nothing but a stderr digest)
    log = tmp_path / "rai.jsonl"
    monkeypatch.setattr(live, "LANE_LOG", log)
    monkeypatch.setattr(live, "codex_runner", _fake())
    monkeypatch.setattr(live.log_call, "__defaults__", (log,))
    rec = live.call(PROMPT, schema={"type": "object"}, model="gpt-6-astra", effort="medium",
                    caller={"file": "t", "line": "1", "purpose": "test"}, input_digests=[], runner=None,
                    client_version="0.153.4")
    lines = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 1 and lines[0]["record_id"] == rec["record_id"]
    assert lines[0]["tokens_used"] == 12345 and lines[0]["files_read"] and lines[0]["prompt_sha256"]
    assert rec["client_evidence"]["tool_calls_n"] == 1 and rec["client_evidence"]["tokens_used"] == 12345


def test_a_test_runner_does_not_write_the_lane_log(tmp_path, monkeypatch):
    log = tmp_path / "rai.jsonl"
    monkeypatch.setattr(live.log_call, "__defaults__", (log,))
    live.call(PROMPT, schema={"type": "object"}, model="gpt-6-astra", effort="medium",
              caller={"file": "t", "line": "1", "purpose": "test"}, input_digests=[], runner=_fake(),
              client_version="0.153.4")
    assert not log.exists()
