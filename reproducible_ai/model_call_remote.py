"""A REMOTE codex runner: the same `codex exec` call as model_call_live.codex_runner, executed on the Tailscale worker.

Only the CALL runs remotely. The prompt is built here, the licence guard runs here (model_call_live.call, before any
runner), the gates and the record live here. The worker receives the prepared work directory -- prompt, output schema,
LANE_CONTEXT.md, attached images; nothing else -- runs the identical argv (read-only sandbox, --ignore-user-config,
project docs off), and returns stdout / stderr / the last message, then the remote directory is removed.

The record says where it ran: argv[0] is 'codex@worker', client_version is the worker's own `codex --version`, and the
worker's ~/.codex/AGENTS.md digest replaces the local one (agents_digest). A failure of the transport (ssh / scp) is
returned as a failed call (rc != 0 with the transport's stderr) -- data, never an exception -- like any other failed call.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from reproducible_ai import model_call_live as mcl

HOST = os.environ.get("MH_WORKER_HOST", "mahmo@100.80.183.43")
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", "-o", "LogLevel=ERROR"]
SCP = ["scp", "-q", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", "-o", "LogLevel=ERROR"]
REMOTE_BASE = "mcall-remote"            # under the worker user's home


def _run(argv, timeout, input=None):
    try:
        p = subprocess.run(argv, input=input, capture_output=True, timeout=timeout,
                           stdin=None if input is not None else subprocess.DEVNULL)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        return -9, exc.stdout or b"", (exc.stderr or b"") + f"\nTIMEOUT after {timeout}s".encode()


class RemoteCodexRunner:
    """Callable with codex_runner's signature. `execute` is the transport (injectable for tests)."""

    real = True                         # a real call: model_call_live.call logs it to the lane log

    def __init__(self, host=HOST, execute=_run):
        self.host, self.execute = host, execute
        self._version = None
        self._agents = None

    # ------------------------------------------------------------------ what the record says about the client
    def version(self):
        if self._version is None:
            rc, so, se = self.execute(SSH + [self.host, "codex --version"], 120)
            self._version = ("worker " + (so or se).decode("utf-8", "replace").strip()) if rc == 0 else \
                f"worker UNKNOWN (rc {rc})"
        return self._version

    @property
    def agents_digest(self):
        if self._agents is None:
            rc, so, _se = self.execute(SSH + [self.host, 'certutil -hashfile "%USERPROFILE%\\.codex\\AGENTS.md" SHA256'],
                                       120)
            lines = [x.strip().replace(" ", "") for x in so.decode("utf-8", "replace").splitlines()]
            h = next((x.lower() for x in lines if len(x) == 64 and all(c in "0123456789abcdefABCDEF" for c in x)), None)
            self._agents = {"ref": "client-injected:worker ~/.codex/AGENTS.md (content not copied)", "sha256": h,
                            "what": "the WORKER's user-level instructions the client may prepend"} if (rc == 0 and h) \
                else {}
        return self._agents or None

    # ------------------------------------------------------------------ the call
    def __call__(self, prompt: bytes, schema: dict, model: str, effort: str, timeout_s: int, images: tuple = ()):
        rid = "mcall-" + uuid.uuid4().hex[:12]
        local = Path(tempfile.mkdtemp(prefix="rcall-", dir=os.environ.get("MODEL_CALL_WORKDIR") or None)) / rid
        local.mkdir()
        try:
            mcl.prepare_workdir(local, schema)
            (local / "prompt.txt").write_bytes(prompt)
            attach = []
            for n, src in enumerate(images or ()):
                name = f"image_{n}{os.path.splitext(str(src))[1].lower()}"
                shutil.copyfile(src, local / name)
                attach += ["-i", name]
            rc, so, se = self.execute(SSH + [self.host, f"if not exist {REMOTE_BASE} mkdir {REMOTE_BASE}"], 120)
            rc, so, se = self.execute(SCP + ["-r", str(local), f"{self.host}:{REMOTE_BASE}/"], 300) if rc == 0 \
                else (rc, so, se)
            if rc != 0:
                return {"rc": rc or 1, "stdout": so, "stderr": b"TRANSPORT (scp) " + se, "last_message": b"",
                        "argv": ["codex@worker", "TRANSPORT_FAILED"]}
            args = ["exec", "--ephemeral", "--skip-git-repo-check", "--ignore-user-config", "--sandbox", "read-only",
                    "--cd", ".", "--output-schema", "schema.json", "--output-last-message", "last.txt", "-m", model,
                    *attach, "-c", f"model_reasoning_effort={effort}", "-c", "project_doc_max_bytes=0", "-"]
            cmd = f"cd /d %USERPROFILE%\\{REMOTE_BASE}\\{rid} && codex " + " ".join(args) + " < prompt.txt"
            rc, so, se = self.execute(SSH + [self.host, cmd], timeout_s + 60)
            lrc, _o, _e = self.execute(SCP + [f"{self.host}:{REMOTE_BASE}/{rid}/last.txt", str(local / "last.txt")], 300)
            last = (local / "last.txt").read_bytes() if lrc == 0 and (local / "last.txt").exists() else b""
            return {"rc": rc, "stdout": so, "stderr": se, "last_message": last, "argv": ["codex@worker"] + args}
        finally:
            self.execute(SSH + [self.host, f"rmdir /s /q %USERPROFILE%\\{REMOTE_BASE}\\{rid}"], 120)
            shutil.rmtree(local.parent, ignore_errors=True)


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()
