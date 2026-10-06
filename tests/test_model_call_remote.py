"""reproducible_ai/model_call_remote.RemoteCodexRunner: the SAME codex call on the worker -- prepared work dir shipped,
identical sandboxed argv, last message fetched back, remote dir removed; a transport failure is a failed call."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from reproducible_ai import model_call_live as mcl  # noqa: E402
from reproducible_ai import model_call_remote as mr  # noqa: E402


def _fake(log, fail_scp=False):
    def execute(argv, timeout, input=None):
        log.append(argv)
        if argv[0] == "scp" and argv[-1].endswith("last.txt"):
            open(argv[-1], "wb").write(b'{"ok": true}')
            return 0, b"", b""
        if argv[0] == "scp":
            src = argv[-2]
            assert {"prompt.txt", "schema.json", "LANE_CONTEXT.md"} <= set(os.listdir(src))
            return (1, b"", b"lost connection") if fail_scp else (0, b"", b"")
        if "codex --version" in argv[-1]:
            return 0, b"codex-cli 9.9.9", b""
        if "certutil" in argv[-1]:
            return 0, ("SHA256 hash:\r\n" + "ab" * 32 + "\r\nCertUtil: done").encode(), b""
        return 0, b"", (b"OpenAI Codex v0.154.0\n--------\nworkdir: x\nmodel: gpt-6-astra\nprovider: openai\n"
                        b"approval: never\nsandbox: read-only\n--------\nuser\nPROMPT\ntokens used\n12\n")
    return execute


def test_the_remote_call_ships_the_workdir_runs_the_same_sandboxed_argv_and_cleans_up(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_CALL_WORKDIR", str(tmp_path))
    log = []
    r = mr.RemoteCodexRunner(host="u@h", execute=_fake(log))
    out = r(b"PROMPT", {"type": "object"}, "gpt-6-astra", "high", 60)
    assert out["rc"] == 0 and out["last_message"] == b'{"ok": true}' and out["argv"][0] == "codex@worker"
    cmd = next(a[-1] for a in log if a[0] == "ssh" and " exec " in a[-1])
    for flag in ("--ignore-user-config", "--sandbox read-only", "project_doc_max_bytes=0", "< prompt.txt", "-m gpt-6-astra"):
        assert flag in cmd
    assert any("rmdir /s /q" in a[-1] for a in log if a[0] == "ssh")          # remote dir removed
    assert r.version() == "worker codex-cli 9.9.9" and r.agents_digest["sha256"] == "ab" * 32


def test_a_transport_failure_is_a_failed_call_not_an_exception(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_CALL_WORKDIR", str(tmp_path))
    out = mr.RemoteCodexRunner(host="u@h", execute=_fake([], fail_scp=True))(b"P", {}, "m", "low", 60)
    assert out["rc"] != 0 and b"TRANSPORT" in out["stderr"] and out["last_message"] == b""


def test_call_records_the_workers_client_and_agents_digest(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_CALL_WORKDIR", str(tmp_path))
    r = mr.RemoteCodexRunner(host="u@h", execute=_fake([]))
    monkeypatch.setattr(mcl, "log_call", lambda rec, facts, path=None: None)
    rec = mcl.call(b"PROMPT", schema={"type": "object"}, model="gpt-6-astra", effort="low",
                   caller={"file": "t", "line": "1", "purpose": "t"}, input_digests=[], runner=r)
    assert rec["state"] == "RAN_OK" and rec["client"]["version"] == "worker codex-cli 9.9.9"
    assert any(d.get("sha256") == "ab" * 32 for d in rec["input_digests"])
