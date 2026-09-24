"""The ONLY place a model is called. Produces a reproducible_ai.model_source record; never a claim, never a value.

Kept out of reproducible_ai/model_source.py on purpose: replay must be unable to reach a process or a network (that module's
imports are swept by AST in tests/test_model_source.py), and nothing in the certificate's code closure imports either
module (same test file). A live call is made by scripts/model_source_pilot.py, one at a time.

Client: the Codex CLI (`codex exec`), run non-interactively with
  --ephemeral --skip-git-repo-check --ignore-user-config --sandbox read-only --cd <empty dir> --output-schema <schema>
  --output-last-message <file> --json, the prompt on stdin, and `-m <model> -c model_reasoning_effort=<e>
  -c project_doc_max_bytes=0`.
The response bytes are the bytes of --output-last-message, unaltered. What the client does not let us set is written
into the record's not_controllable list rather than invented: temperature, top_p, seed, the client's own system
instructions. The user's global ~/.codex/AGENTS.md, which the client may inject, is recorded by sha256 as an input
(its content is not copied: it is not ours to publish, and replay does not need it).
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from reproducible_ai import model_source

NOT_CONTROLLABLE = ["temperature", "top_p", "seed", "client system instructions (codex built-in, not exposed)",
                    "server-side model revision behind the model id"]


def _codex_exe() -> str:
    """The client on PATH (on Windows the npm shim codex.CMD). Its local path is never written into a record."""
    exe = shutil.which("codex")
    if not exe:
        raise FileNotFoundError("codex CLI not on PATH")
    return exe


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _codex_version() -> str:
    try:
        out = subprocess.run([_codex_exe(), "--version"], capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        return (out.stdout or out.stderr).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return f"UNKNOWN ({type(exc).__name__})"


def global_agents_digest() -> dict | None:
    p = Path(os.path.expanduser("~")) / ".codex" / "AGENTS.md"
    if not p.exists():
        return None
    return {"ref": "client-injected:~/.codex/AGENTS.md (content not copied)", "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "what": "user-level instructions the client may prepend; recorded so a reader knows the prompt bytes are not the whole context"}


LANE_CONTEXT = """# LANE_CONTEXT -- read this first

This empty directory is the scratch working directory of ONE recorded model call (meta-harness, lane `rai`,
reproducible_ai/model_call_live.py). It holds nothing you need except the output schema.

Your task is ONLY the prompt you were given; everything you need is inside that prompt text. Nothing outside this
prompt is context: do not read, list or search any other file or directory on this machine (no AGENTS.md, CLAUDE.md,
INDEX.md, workbooks, registries, other repositories, home directories). Do not run commands. Do not write anything.
"""
LANE_CONTEXT_SHA256 = hashlib.sha256(LANE_CONTEXT.encode("utf-8")).hexdigest()


def prepare_workdir(work: Path, schema: dict) -> None:
    """What the model can see besides the prompt: the schema and this orientation file, nothing else (its digest is
    recorded in the call's params)."""
    (work / "schema.json").write_text(json.dumps(schema), encoding="utf-8")
    (work / "LANE_CONTEXT.md").write_text(LANE_CONTEXT, encoding="utf-8", newline="\n")


HEADER_KEYS = ("model", "provider", "approval", "sandbox", "reasoning effort", "reasoning summaries", "session id")


def client_header(stderr_text: str) -> dict:
    """The client's own header block (codex-cli 0.153 prints it to stderr): `key: value` lines between the first two
    '--------' rules. `workdir` is dropped (a local path). This is what the CLIENT says it asked for; it is not a
    server attestation of the model revision that answered (that is listed in not_controllable)."""
    parts = stderr_text.split("--------")
    block = parts[1] if len(parts) >= 3 else ""
    out = {}
    for line in block.splitlines():
        k, sep, v = line.partition(":")
        if sep and k.strip() in HEADER_KEYS:
            out[k.strip()] = v.strip()
    m = re.search(r"tokens used\s*\n\s*([\d,]+)", stderr_text)
    if m:
        out["tokens used"] = m.group(1)
    v = re.search(r"OpenAI Codex (v[\w.\-]+)", stderr_text)
    if v:
        out["client banner"] = v.group(1)
    return out


def reported_model(stderr_text: str) -> str | None:
    return client_header(stderr_text).get("model") or None


def codex_runner(prompt: bytes, schema: dict, model: str, effort: str, timeout_s: int) -> dict:
    """Run one `codex exec`. Returns {rc, stdout, stderr, last_message, argv}; bytes throughout."""
    work = Path(tempfile.mkdtemp(prefix="mcall-", dir=os.environ.get("MODEL_CALL_WORKDIR") or None))
    try:
        prepare_workdir(work, schema)
        out = work / "last.txt"
        argv = [_codex_exe(), "exec", "--ephemeral", "--skip-git-repo-check", "--ignore-user-config",
                "--sandbox", "read-only", "--cd", str(work), "--output-schema", str(work / "schema.json"),
                "--output-last-message", str(out), "-m", model,
                "-c", f"model_reasoning_effort={effort}", "-c", "project_doc_max_bytes=0", "-"]
        try:
            p = subprocess.run(argv, input=prompt, capture_output=True, timeout=timeout_s)
            rc, so, se = p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired as exc:
            rc, so, se = -9, exc.stdout or b"", (exc.stderr or b"") + f"\nTIMEOUT after {timeout_s}s".encode()
        last = out.read_bytes() if out.exists() else b""
        return {"rc": rc, "stdout": so, "stderr": se, "last_message": last,
                "argv": ["codex"] + [a.replace(str(work), "<workdir>") for a in argv[1:]]}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def call(prompt: bytes, *, schema: dict, model: str, effort: str, caller: dict, input_digests: list,
         timeout_s: int = 900, runner: Callable[..., dict] | None = None, client_version: str | None = None) -> dict:
    """One model call -> one record (RAN_OK with the response bytes, or RAN_ERROR with the error). Never raises for a
    failed call: a failure is data. Raises RecordIncomplete only when the record itself would be unsound."""
    runner = runner or codex_runner
    digests = list(input_digests)
    g = global_agents_digest() if runner is codex_runner else None
    if g:
        digests.append(g)
    digests.append({"ref": "output-schema (inline in params)", "sha256": hashlib.sha256(model_source.canonical(schema)).hexdigest(),
                    "what": "JSON schema the client constrains the final message to"})
    t0 = _utc()
    r = runner(prompt, schema, model, effort, timeout_s)
    t1 = _utc()
    so, se = r.get("stdout") or b"", r.get("stderr") or b""
    header = client_header(se.decode("utf-8", "replace"))
    rep = header.get("model")
    last = r.get("last_message") or b""
    err = None
    if r.get("rc") != 0:
        err = f"client exited {r.get('rc')}: " + re.sub(r"[A-Za-z]:[\\/][^\s'\"]*", "<path>", se.decode("utf-8", "replace"))[-600:]
    elif not last.strip():
        err = "client exited 0 with an EMPTY final message (RAN_ERROR, never RAN_ZERO)"
    elif rep is None:
        err = "client exited 0 but reported no model id: the pin is unknown, so the response is not a source"
    elif rep != model:
        err = f"client reported model {rep!r} but {model!r} was requested: the pin does not hold"
    elif header.get("reasoning effort") not in (None, effort):
        err = f"client reported reasoning effort {header.get('reasoning effort')!r} but {effort!r} was set"
    state = "RAN_ERROR" if err else "RAN_OK"
    return model_source.build_record(
        prompt_bytes=prompt, response_bytes=last if state == "RAN_OK" else b"",
        model={"id_requested": model, "id_reported": rep or "UNREPORTED", "provider": header.get("provider") or "UNREPORTED",
               "reported_by": "client header (codex exec stderr); not a server attestation of the model revision"},
        params={"reasoning_effort": effort, "sandbox": "read-only", "ephemeral": True, "ignore_user_config": True,
                "project_doc_max_bytes": 0, "output_schema": schema, "timeout_s": timeout_s,
                "workdir_files": {"LANE_CONTEXT.md": LANE_CONTEXT_SHA256, "schema.json": "the output_schema above"}},
        not_controllable=list(NOT_CONTROLLABLE),
        client={"name": "codex exec", "version": client_version or _codex_version(), "argv": r.get("argv")},
        request_utc=t0, response_utc=t1, caller=caller, input_digests=digests, state=state, error=err,
        client_evidence={"header": header, "stdout_sha256": hashlib.sha256(so).hexdigest(), "stdout_bytes": len(so),
                         "stderr_sha256": hashlib.sha256(se).hexdigest(), "stderr_bytes": len(se),
                         "note": "raw client streams are hashed, not stored: they carry a local path (workdir) and echo "
                                 "the prompt; the header's model/provider/effort/session are copied above"})
