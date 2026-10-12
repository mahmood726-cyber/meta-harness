"""Plants for the agy recorder's prompt delivery and launch-failure contract (reproducible_ai/model_call_live.agy_runner).

2026-10-12: a RoB 2 full-text prompt as the --print argument hit the Windows command-line cap (WinError 206) and the
exception escaped the recorder. A long prompt now goes to PROMPT.txt in the call's work dir; a launch that fails is a
RAN_ERROR record, never a raise; a prompt that fits is passed exactly as before, so earlier records still replay."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from reproducible_ai import model_call_live as mcl  # noqa: E402

SCHEMA = {"type": "object", "properties": {"ok": {"type": "string"}}, "required": ["ok"]}


def _fake_run(seen):
    def run(argv, cwd=None, **kw):
        seen["argv"] = list(argv)
        seen["files"] = {n: open(os.path.join(cwd, n), "rb").read() for n in os.listdir(cwd)}
        return subprocess.CompletedProcess(argv, 0, json.dumps({"status": "SUCCESS", "response": '{"ok":"y"}'}).encode(), b"")
    return run


def _patch(monkeypatch, tmp_path, run):
    monkeypatch.setenv("MODEL_CALL_WORKDIR", str(tmp_path))
    monkeypatch.setattr(mcl, "_agy_exe", lambda: "agy.exe")
    monkeypatch.setattr(mcl.subprocess, "run", run)


def test_short_prompt_is_unchanged_argv(tmp_path, monkeypatch):
    seen = {}
    _patch(monkeypatch, tmp_path, _fake_run(seen))
    r = mcl.agy_runner(b"short task", SCHEMA, 60)
    assert seen["argv"][2] == "short task"
    assert "PROMPT.txt" not in seen["files"]
    assert r["prompt_delivery"] == {"via": "argv (--print)"}
    assert r["argv"][2].startswith("<prompt sha256 ")


def test_PLANT_long_prompt_goes_to_a_file_not_the_command_line(tmp_path, monkeypatch):
    seen = {}
    _patch(monkeypatch, tmp_path, _fake_run(seen))
    long = ("Read the trial report. " * 3000).encode("utf-8")
    assert len(long) > mcl.AGY_ARGV_MAX
    r = mcl.agy_runner(long, SCHEMA, 60)
    assert seen["argv"][2] == mcl.AGY_PROMPT_FILE_INSTRUCTION
    assert seen["files"]["PROMPT.txt"] == long
    assert sum(len(a) for a in seen["argv"]) < 32767
    assert r["prompt_delivery"]["file_sha256"] == mcl.hashlib.sha256(long).hexdigest()
    rec = mcl.agy_call(long, schema=SCHEMA, caller={"file": "tests/test_agy_runner_delivery.py", "line": 1, "purpose": "plant"}, input_digests=[], runner=lambda *a, **k: r,
                       client_version="test", settings=(None, None))
    assert rec["params"]["prompt_delivery"]["via"].startswith("file")
    assert rec["params"]["workdir_files"]["PROMPT.txt"] == r["prompt_delivery"]["file_sha256"]


def test_PLANT_a_launch_failure_is_a_record_not_a_raise(tmp_path, monkeypatch):
    def boom(argv, **kw):
        raise FileNotFoundError(206, "The filename or extension is too long")
    _patch(monkeypatch, tmp_path, boom)
    r = mcl.agy_runner(b"x", SCHEMA, 60)
    assert r["rc"] == -2 and b"LAUNCH FAILED" in r["stderr"]
    rec = mcl.agy_call(b"x", schema=SCHEMA, caller={"file": "tests/test_agy_runner_delivery.py", "line": 1, "purpose": "plant"}, input_digests=[], runner=lambda *a, **k: r,
                       client_version="test", settings=(None, None))
    assert rec["state"] == "RAN_ERROR"


def test_PLANT_no_client_on_path_is_a_record_not_a_raise(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_CALL_WORKDIR", str(tmp_path))
    monkeypatch.setattr(mcl.shutil, "which", lambda name: None)
    r = mcl.agy_runner(b"x", SCHEMA, 60)
    assert r["rc"] == -2 and b"not on PATH" in r["stderr"]
