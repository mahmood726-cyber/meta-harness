"""A prompt longer than the Windows command line (32,767 chars, WinError 206) must not travel as the --print
argument. It is written to the call's work dir and agy is told to read it; short prompts are unchanged."""
import subprocess

from reproducible_ai import model_call_live as mcl


def _capture(monkeypatch):
    seen = {}

    def fake_run(argv, cwd=None, **kw):
        seen["argv"] = list(argv)
        seen["files"] = {p.name: p.read_bytes() for p in __import__("pathlib").Path(cwd).iterdir()}
        return subprocess.CompletedProcess(argv, 0, b"{}", b"")

    monkeypatch.setattr(mcl.subprocess, "run", fake_run)
    monkeypatch.setattr(mcl, "_agy_exe", lambda: "agy")
    return seen


def test_long_prompt_goes_to_a_workdir_file_not_argv(monkeypatch):
    seen = _capture(monkeypatch)
    prompt = ("x" * 99 + "\n").encode() * 500          # 50,000 bytes
    mcl.agy_runner(prompt, {"type": "object"}, 60)
    assert all(len(a) < 8000 for a in seen["argv"]), "a long prompt must not be an argv element"
    assert seen["files"].get(mcl.AGY_PROMPT_FILE) == prompt, "the exact prompt bytes must be in the work dir"
    assert mcl.AGY_PROMPT_FILE in seen["argv"][seen["argv"].index("--print") + 1]


def test_short_prompt_is_unchanged(monkeypatch):
    seen = _capture(monkeypatch)
    mcl.agy_runner(b"Reply OK", {"type": "object"}, 60)
    assert seen["argv"][seen["argv"].index("--print") + 1] == "Reply OK"
    assert getattr(mcl, "AGY_PROMPT_FILE", "agy_prompt.txt") not in seen["files"]
