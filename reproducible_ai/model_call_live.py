"""The ONLY place a model is called. Produces a reproducible_ai.model_source record; never a claim, never a value.

Kept out of reproducible_ai/model_source.py on purpose: replay must be unable to reach a process or a network (that module's
imports are swept by AST in tests/test_model_source.py), and nothing in the certificate's code closure imports either
module (same test file). A live call is made by scripts/model_source_pilot.py, one at a time.

Clients: the Codex CLI (`codex exec`); and agy (Antigravity CLI, Gemini) -- see agy_call below.
Codex, run non-interactively with
  --ephemeral --skip-git-repo-check --ignore-user-config --sandbox read-only --cd <empty dir> --output-schema <schema>
  --output-last-message <file> --json, the prompt on stdin, and `-m <model> -c model_reasoning_effort=<e>
  -c project_doc_max_bytes=0`.
The response bytes are the bytes of --output-last-message, unaltered. What the client does not let us set is written
into the record's not_controllable list rather than invented: temperature, top_p, seed, the client's own system
instructions. The user's global ~/.codex/AGENTS.md, which the client may inject, is recorded by sha256 as an input
(its content is not copied: it is not ours to publish, and replay does not need it).
"""
from __future__ import annotations

import base64
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


class LicenceRefused(Exception):
    """The prompt would carry text the licence guard (reproducible_ai/record_licence.py) refuses: no call is made."""

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


# CODEX-2: every real call is logged to a per-lane record -- what the model saw besides the prompt, every tool call it
# attempted and how that ended, the files it read, and the tokens the client reported. The prompt itself is in the call
# record (by digest here); the client transcript is kept with the prompt echo replaced by that digest and the local
# work-dir path replaced by <workdir>.
# The log a call goes to is named by its CALLER's lane (caller["lane"]), never by this module: a hard-coded lane filed the
# evidence lane's 53 calls under "rai" (tests/test_lane_log_attribution.py). A caller that names no lane is
# "unattributed" -- visible as such, not silently this lane's.
LANE = "rai"
UNATTRIBUTED = "unattributed"
LANE_LOG_DIR = Path(__file__).resolve().parents[1] / "registry" / "model_calls" / "lane_log"
LANE_LOG = LANE_LOG_DIR / f"{LANE}.jsonl"


def lane_of(caller) -> str:
    lane = caller.get("lane") if isinstance(caller, dict) else None
    return lane.strip() if isinstance(lane, str) and lane.strip() else UNATTRIBUTED


def lane_log_name(lane: str) -> str:
    """One file per lane, inside the log directory whatever the name holds ('evid/x' -> 'evid__x.jsonl')."""
    return re.sub(r"[^A-Za-z0-9_-]", "__", lane) + ".jsonl"
_TOKENS = re.compile(r"tokens used\s*\n\s*([\d,]+)")
_EXEC = re.compile(r"^exec\s*\n(?P<cmd>.+?)\n(?P<outcome>\s*(?:succeeded|failed|exited)[^\n]*)", re.M)
_REJECT = re.compile(r"exec_command failed: (?P<why>[^\n]{0,400})")
_READ_CMD = re.compile(r"(?:Get-Content|cat|type|more|head|tail|sed -n|rg|grep|Select-String|findstr)\b[^\n]*?"
                       r"(?P<path>[\w.\\/:-]+\.(?:md|txt|json|py|csv|html|toml|yaml|yml))", re.I)


def transcript_facts(stderr_text: str, prompt: bytes, workdir_hint: str = "") -> dict:
    """Tokens, tool calls (with outcome) and files read, parsed from the client's stderr; plus the redacted transcript."""
    t = stderr_text.replace("\r\n", "\n")
    m = _TOKENS.search(t)
    tokens = int(m.group(1).replace(",", "")) if m else None
    calls = [{"command": x.group("cmd").strip()[:400], "outcome": x.group("outcome").strip()[:200]} for x in _EXEC.finditer(t)]
    calls += [{"command": None, "outcome": "REJECTED: " + x.group("why")[:300]} for x in _REJECT.finditer(t)]
    files = sorted({r.group("path") for c in calls if c["command"] for r in _READ_CMD.finditer(c["command"])})
    red = t
    p = prompt.decode("utf-8", "replace").replace("\r\n", "\n").strip()
    if p and p in red:
        red = red.replace(p, f"<prompt sha256 {hashlib.sha256(prompt).hexdigest()}>")
    red = re.sub(r"[A-Za-z]:[\\/][^\s'\"]*mcall-[\w]+", "<workdir>", red)
    return {"tokens_used": tokens, "tool_calls": calls, "tool_calls_n": len(calls),
            "tool_calls_rejected_n": sum(1 for c in calls if c["outcome"].startswith("REJECTED")),
            "files_read": files, "transcript_redacted": red}


def log_call(record: dict, facts: dict, path: Path | None = None) -> None:
    lane = lane_of(record.get("caller"))
    path = path or LANE_LOG_DIR / lane_log_name(lane)
    line = {"lane": lane, "record_id": record["record_id"], "state": record["state"],
            "request_utc": record.get("request_utc"), "caller": record.get("caller"),
            "model_requested": (record.get("model") or {}).get("id_requested"),
            "model_reported": (record.get("model") or {}).get("id_reported"),
            "prompt_sha256": (record.get("prompt") or {}).get("sha256"),
            "response_sha256": (record.get("response") or {}).get("sha256"),
            "workdir_files": (record.get("params") or {}).get("workdir_files"),
            **{k: facts[k] for k in ("tokens_used", "tool_calls_n", "tool_calls_rejected_n", "tool_calls", "files_read",
                                     "transcript_redacted", "outside_workdir_reads")}}
    # the lane log is committed too: the same private-text redaction as the record (model_source.redact_private)
    line = model_source._redact_obj(line, None, [0])
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(line, sort_keys=True, ensure_ascii=True) + "\n")


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


def codex_runner(prompt: bytes, schema: dict, model: str, effort: str, timeout_s: int, images: tuple = ()) -> dict:
    """Run one `codex exec`. Returns {rc, stdout, stderr, last_message, argv}; bytes throughout.

    images: files attached with `-i`. Each is COPIED into the empty work dir first, so the argv (and the record) name
    only <workdir>/image_<n><ext>, never the caller's path; the image bytes are digested by call()."""
    work = Path(tempfile.mkdtemp(prefix="mcall-", dir=os.environ.get("MODEL_CALL_WORKDIR") or None))
    try:
        prepare_workdir(work, schema)
        out = work / "last.txt"
        attach = []
        for n, src in enumerate(images or ()):
            dst = work / f"image_{n}{os.path.splitext(str(src))[1].lower()}"
            shutil.copyfile(src, dst)
            attach += ["-i", str(dst)]
        argv = [_codex_exe(), "exec", "--ephemeral", "--skip-git-repo-check", "--ignore-user-config",
                "--sandbox", "read-only", "--cd", str(work), "--output-schema", str(work / "schema.json"),
                "--output-last-message", str(out), "-m", model, *attach,
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
         timeout_s: int = 900, runner: Callable[..., dict] | None = None, client_version: str | None = None,
         images: tuple = ()) -> dict:
    """One model call -> one record (RAN_OK with the response bytes, or RAN_ERROR with the error). Never raises for a
    failed call: a failure is data. Raises RecordIncomplete only when the record itself would be unsound.

    images: files the model is shown (e.g. a forest-plot figure). Their sha256 is recorded as an input digest and in
    params, so the record says exactly which bytes were seen; this is the ONLY route by which a model sees an image."""
    runner = runner or codex_runner
    # LICENCE GUARD AT CALL TIME: the prompt goes into a committed record, so a prompt the record guard would refuse is
    # never sent (6 Oct audit: 44 committed records carried non-CC full text in shapes the after-the-fact test missed)
    from reproducible_ai import record_licence
    probs = record_licence.record_problems({"record_id": "pre-call", "input_digests": list(input_digests),
                                            "prompt": {"b64": base64.b64encode(prompt).decode("ascii")}})
    if probs:
        raise LicenceRefused("; ".join(probs)[:600])
    digests = list(input_digests)
    g = global_agents_digest() if runner is codex_runner else None
    if g:
        digests.append(g)
    digests.append({"ref": "output-schema (inline in params)", "sha256": hashlib.sha256(model_source.canonical(schema)).hexdigest(),
                    "what": "JSON schema the client constrains the final message to"})
    image_digests = []
    for n, src in enumerate(images or ()):
        with open(src, "rb") as fh:
            h = hashlib.sha256(fh.read()).hexdigest()
        image_digests.append(h)
        digests.append({"ref": f"attached image_{n}", "sha256": h, "what": "image attached with -i (copied into the work dir)"})
    t0 = _utc()
    r = runner(prompt, schema, model, effort, timeout_s, images=tuple(images)) if images else \
        runner(prompt, schema, model, effort, timeout_s)
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
    facts = transcript_facts(se.decode("utf-8", "replace"), prompt)
    rec = model_source.build_record(
        prompt_bytes=prompt, response_bytes=last if state == "RAN_OK" else b"",
        model={"id_requested": model, "id_reported": rep or "UNREPORTED", "provider": header.get("provider") or "UNREPORTED",
               "reported_by": "client header (codex exec stderr); not a server attestation of the model revision"},
        params={"reasoning_effort": effort, "sandbox": "read-only", "ephemeral": True, "ignore_user_config": True,
                "project_doc_max_bytes": 0, "output_schema": schema, "timeout_s": timeout_s,
                "workdir_files": {"LANE_CONTEXT.md": LANE_CONTEXT_SHA256, "schema.json": "the output_schema above",
                                  **{f"image_{n}": h for n, h in enumerate(image_digests)}},
                **({"attached_images_sha256": image_digests} if image_digests else {})},
        not_controllable=list(NOT_CONTROLLABLE),
        client={"name": "codex exec", "version": client_version or _codex_version(), "argv": r.get("argv")},
        request_utc=t0, response_utc=t1, caller=caller, input_digests=digests, state=state, error=err,
        client_evidence={"header": header, "stdout_sha256": hashlib.sha256(so).hexdigest(), "stdout_bytes": len(so),
                         "stderr_sha256": hashlib.sha256(se).hexdigest(), "stderr_bytes": len(se),
                         "tokens_used": facts["tokens_used"], "tool_calls_n": facts["tool_calls_n"],
                         "tool_calls_rejected_n": facts["tool_calls_rejected_n"], "files_read": facts["files_read"],
                         "transcript_redacted_sha256": hashlib.sha256(facts["transcript_redacted"].encode("utf-8")).hexdigest(),
                         "lane_log": f"registry/model_calls/lane_log/{lane_log_name(lane_of(caller))}",
                         "note": "raw client streams are hashed; the redacted transcript (prompt echo -> its digest, work "
                                 "dir -> <workdir>) is in the lane log with every tool call and file read"})
    if runner is codex_runner:                  # a real call is logged; a test's fake runner is not
        log_call(rec, facts)
    return rec


# ------------------------------------------------------------------------------------------------ agy (Gemini)
# The second model FAMILY (google) for dual readings: Antigravity CLI `agy --print`, run in the same empty work dir
# (LANE_CONTEXT.md + schema.json + attached images), with --sandbox (terminal restrictions: the client soft-denies
# commands in print mode and lists them as denied_actions) and its own log file.
#   * agy has no image flag: an image is COPIED into the work dir and the prompt names it (image_<n><ext>); the client
#     reads it with its read_file tool. The bytes are digested exactly as for codex.
#   * --json-schema is NOT used: probed 2026-10-02 (agy 1.2.14), it returned an EMPTY response and attempted a shell
#     step. The schema is in the prompt and in schema.json; the response bytes are stored unaltered and parsed and
#     validated deterministically by the caller at replay.
#   * the model is not settable per call (`--print` ignores --model): it is the client setting `model` in
#     ~/.gemini/antigravity-cli/settings.json. That value is recorded as id_requested; id_reported is the label the
#     client's own log says it propagated to the backend. Either missing, or the two differing, is RAN_ERROR.
AGY_NOT_CONTROLLABLE = ["temperature", "top_p", "seed", "client system instructions (agy built-in, not exposed)",
                        "server-side model revision behind the model label", "the client's tool use (sandboxed; "
                        "denied actions are recorded, not prevented from being attempted)"]
AGY_SETTINGS = Path(os.path.expanduser("~")) / ".gemini" / "antigravity-cli" / "settings.json"
_AGY_MODEL_LOG = re.compile(r'Propagating selected model override to backend: label="([^"]+)"')


# the agy client log is mostly the user's session (sign-in identity, token refresh, settings): only the lines that say
# what the CALL did are kept -- the model it propagated, print mode, the sandbox, every tool step and its confirmation
_AGY_KEEP = re.compile(r"model_config_manager|Propagating selected model|printmode\.go|Print mode|sandbox|"
                       r"tool_confirmation|Tool confirmation|run_command|denied|read_file|view_file|write_file", re.I)
_AGY_DROP = re.compile(r"permissions=|trustedWorkspaces|Allow:\[|oauth|auth|token|email|cookie|credential", re.I)


def agy_redact(log_text: str) -> str:
    """The client log as it may be published: an ALLOW-list of call lines (above), with the work dir -> <workdir>,
    other local paths -> <path>, e-mail addresses -> <email>; every other line is dropped and counted."""
    kept, dropped = [], 0
    for ln in log_text.splitlines():
        if not _AGY_KEEP.search(ln) or _AGY_DROP.search(ln):
            dropped += 1
            continue
        ln = re.sub(r"[A-Za-z]:[\\/][^\s'\"]*mcall-[\w]+", "<workdir>", ln)
        ln = re.sub(r"[A-Za-z]:[\\/][^\s'\"\]\)]*", "<path>", ln)
        kept.append(re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "<email>", ln))
    return "\n".join(kept + [f"<{dropped} client-session log lines not published (sign-in, settings, transport)>"])


def _agy_exe() -> str:
    exe = shutil.which("agy")
    if not exe:
        raise FileNotFoundError("agy (Antigravity CLI) not on PATH")
    return exe


def agy_settings_model() -> tuple:
    """(model label the client is set to use, sha256 of the settings file). The settings file is not copied: it holds
    the user's permissions, which are not ours to publish; its digest says which settings were in force."""
    if not AGY_SETTINGS.exists():
        return None, None
    b = AGY_SETTINGS.read_bytes()
    try:
        m = json.loads(b.decode("utf-8")).get("model")
    except (ValueError, UnicodeDecodeError, AttributeError):
        m = None
    return (m if isinstance(m, str) and m.strip() else None), hashlib.sha256(b).hexdigest()


def _agy_version() -> str:
    try:
        out = subprocess.run([_agy_exe(), "--version"], capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        return (out.stdout or out.stderr).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return f"UNKNOWN ({type(exc).__name__})"


def agy_runner(prompt: bytes, schema: dict, timeout_s: int, images: tuple = ()) -> dict:
    """Run one `agy --print`. Returns {rc, stdout, stderr, log, argv}; bytes throughout. The prompt is the --print value
    (agy reads no prompt from stdin in text mode); stdin is the null device."""
    work = Path(tempfile.mkdtemp(prefix="mcall-", dir=os.environ.get("MODEL_CALL_WORKDIR") or None))
    try:
        prepare_workdir(work, schema)
        for n, src in enumerate(images or ()):
            shutil.copyfile(src, work / f"image_{n}{os.path.splitext(str(src))[1].lower()}")
        log = work / "agy.log"
        argv = [_agy_exe(), "--print", prompt.decode("utf-8"), "--output-format", "json", "--sandbox",
                "--disable-slash-commands", "--print-timeout", f"{int(timeout_s)}s", "--log-file", str(log)]
        try:
            p = subprocess.run(argv, cwd=str(work), capture_output=True, timeout=timeout_s + 60, stdin=subprocess.DEVNULL)
            rc, so, se = p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired as exc:
            rc, so, se = -9, exc.stdout or b"", (exc.stderr or b"") + f"\nTIMEOUT after {timeout_s}s".encode()
        lg = log.read_bytes() if log.exists() else b""
        red = ["agy", "--print", f"<prompt sha256 {hashlib.sha256(prompt).hexdigest()}>"] + \
              [a.replace(str(work), "<workdir>") for a in argv[3:]]
        return {"rc": rc, "stdout": so, "stderr": se, "log": lg, "argv": red}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def agy_call(prompt: bytes, *, schema: dict, caller: dict, input_digests: list, timeout_s: int = 600,
             runner: Callable[..., dict] | None = None, client_version: str | None = None, images: tuple = (),
             settings: tuple | None = None) -> dict:
    """One agy call -> one record, same contract as call(): RAN_OK with the model's final message bytes, or RAN_ERROR.

    settings: (model label, settings sha256) -- injected by tests; a real call reads the client's settings file."""
    runner = runner or agy_runner
    requested, settings_sha = settings if settings is not None else agy_settings_model()
    digests = list(input_digests)
    if settings_sha:
        digests.append({"ref": "client-settings:~/.gemini/antigravity-cli/settings.json (content not copied)",
                        "sha256": settings_sha, "what": "the client's model setting and tool permissions in force"})
    digests.append({"ref": "output-schema (inline in params; stated in the prompt)", "sha256":
                    hashlib.sha256(model_source.canonical(schema)).hexdigest(), "what": "JSON schema the answer must meet"})
    image_digests = []
    for n, src in enumerate(images or ()):
        with open(src, "rb") as fh:
            h = hashlib.sha256(fh.read()).hexdigest()
        image_digests.append(h)
        digests.append({"ref": f"workdir image_{n}", "sha256": h, "what": "image copied into the work dir for read_file"})
    t0 = _utc()
    r = runner(prompt, schema, timeout_s, images=tuple(images))
    t1 = _utc()
    so, se, lg = r.get("stdout") or b"", r.get("stderr") or b"", r.get("log") or b""
    names = _AGY_MODEL_LOG.findall(lg.decode("utf-8", "replace"))
    rep = names[-1] if names else None
    resp = b""
    try:
        out = json.loads(so.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        out = None
    out = out if isinstance(out, dict) else {}
    if isinstance(out.get("response"), str):
        resp = out["response"].encode("utf-8")
    err = None
    if r.get("rc") != 0:
        err = f"client exited {r.get('rc')}: " + re.sub(r"[A-Za-z]:[\\/][^\s'\"]*", "<path>", se.decode("utf-8", "replace"))[-600:]
    elif out.get("status") != "SUCCESS":
        err = f"client status {out.get('status')!r} (stdout is not a SUCCESS json object)"
    elif not resp.strip():
        err = "client exited 0 with an EMPTY final message (RAN_ERROR, never RAN_ZERO)"
    elif requested is None:
        err = "client settings name no model: the pin is unknown, so the response is not a source"
    elif rep is None:
        err = "client log reported no model label: the pin is unknown, so the response is not a source"
    elif rep != requested:
        err = f"client log reported model {rep!r} but settings request {requested!r}: the pin does not hold"
    state = "RAN_ERROR" if err else "RAN_OK"
    lg_red = agy_redact(lg.decode("utf-8", "replace"))
    denied = out.get("denied_actions") or []
    rec = model_source.build_record(
        prompt_bytes=prompt, response_bytes=resp if state == "RAN_OK" else b"",
        model={"id_requested": requested or "UNSET", "id_reported": rep or "UNREPORTED", "provider": "google",
               "reported_by": "client log line 'Propagating selected model override to backend' (agy --log-file); "
                              "not a server attestation of the model revision"},
        params={"sandbox": True, "output_format": "json", "json_schema_flag": False, "slash_commands": False,
                "output_schema": schema, "timeout_s": timeout_s,
                "workdir_files": {"LANE_CONTEXT.md": LANE_CONTEXT_SHA256, "schema.json": "the output_schema above",
                                  **{f"image_{n}": h for n, h in enumerate(image_digests)}},
                **({"attached_images_sha256": image_digests} if image_digests else {})},
        not_controllable=list(AGY_NOT_CONTROLLABLE),
        client={"name": "agy --print", "version": client_version or _agy_version(), "argv": r.get("argv")},
        request_utc=t0, response_utc=t1, caller=caller, input_digests=digests, state=state, error=err,
        client_evidence={"status": out.get("status"), "usage": out.get("usage"), "num_turns": out.get("num_turns"),
                         "denied_actions": denied,
                         "stdout_sha256": hashlib.sha256(so).hexdigest(), "stdout_bytes": len(so),
                         "stderr_sha256": hashlib.sha256(se).hexdigest(), "stderr_bytes": len(se),
                         "client_log_redacted_sha256": hashlib.sha256(lg_red.encode("utf-8")).hexdigest(),
                         "client_log_bytes": len(lg), "model_labels_in_log": sorted(set(names)),
                         "lane_log": f"registry/model_calls/lane_log/{lane_log_name(lane_of(caller))}"})
    if runner is agy_runner:                    # a real call is logged; a test's fake runner is not
        log_call(rec, {"tokens_used": (out.get("usage") or {}).get("total_tokens"), "tool_calls_n": len(denied),
                       "tool_calls_rejected_n": len(denied),
                       "tool_calls": [{"command": a.get("display_name"), "outcome": "DENIED: " + str(a.get("action"))}
                                      for a in denied if isinstance(a, dict)],
                       "files_read": [], "transcript_redacted": lg_red})
    return rec
