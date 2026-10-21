"""The two independent readers: Claude (anthropic) and Codex (openai). Every call is a recorded model_call_record/1.

Both readers get the SAME prompt, built from the held document alone -- never from the other reader's answer -- and
the record's input_digests prove it (dual.independence_problems checks exactly that). A reader returns
{"items": [{"field", "arm", "value", "quote"}]}; the quote is located in the document deterministically (exactly once,
or the item gets no passage and fails the gate visibly -- an ambiguous quote is never resolved by guessing).

Codex goes through reproducible_ai.model_call_live.call (the repo's existing recorded caller). Claude goes through
claude_call below: `claude -p` (Claude Code, non-interactive), no tools, an empty work dir, prompt on stdin, its own
record built by reproducible_ai.model_source.build_record. The pin: id_reported is the model the client's JSON
`modelUsage` names; it must equal the requested id or the call is RAN_ERROR.
"""
from __future__ import annotations

import base64
import datetime as _dt
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import CONTRACT_VERSION
from . import fields as F
from .passage import locate

CLAUDE_NOT_CONTROLLABLE = ["temperature", "top_p", "seed",
                           "client system instructions (Claude Code built-in, not exposed)"]

RESPONSE_SCHEMA = {
    "type": "object", "required": ["items"], "additionalProperties": False,
    "properties": {"items": {"type": "array", "items": {
        "type": "object", "required": ["field", "arm", "value", "quote"], "additionalProperties": False,
        "properties": {"field": {"type": "string"}, "arm": {"type": ["string", "null"]},
                       "value": {"type": ["number", "string"]}, "quote": {"type": "string"}}}}},
}


def build_prompt(document_text: str, trial_id: str, measure: str) -> bytes:
    wanted = F.REQUIRED_BY_MEASURE[measure] + [("timepoint", None), ("analysis_set", None)]
    lines = [f"- {f}" + (f" (arm: {a})" if a else "") + f": {F.FIELDS[f].kind}"
             + (f", one of {list(F.FIELDS[f].choices)}" if F.FIELDS[f].choices else "")
             + f" -- {F.FIELDS[f].meaning}" for f, a in wanted]
    return (
        f"You are extracting trial-level data for a meta-analysis (extraction contract {CONTRACT_VERSION}).\n"
        f"Trial: {trial_id}. Measure: {measure}.\n\n"
        "Extract ONLY these fields from the DOCUMENT below:\n" + "\n".join(lines) + "\n\n"
        "Rules:\n"
        "1. For every value, copy the shortest passage (a sentence or table row, under 400 characters) that states it, "
        "VERBATIM, character for character, into `quote`. The value must appear literally in that quote.\n"
        "2. Report a number exactly as printed (do not round, convert, or compute). ci_level is a fraction (0.95).\n"
        "3. If a field is not stated in the document, OMIT it. Never infer, never estimate, never compute.\n"
        "4. arm is 'intervention' or 'comparator' for arm-level fields, null otherwise.\n"
        'Answer with ONLY a JSON object: {"items": [{"field": ..., "arm": ..., "value": ..., "quote": ...}]}\n\n'
        "=== DOCUMENT ===\n" + document_text + "\n=== END DOCUMENT ===\n"
    ).encode("utf-8")


def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _claude_exe() -> str:
    exe = shutil.which("claude")
    if not exe:
        raise FileNotFoundError("claude (Claude Code CLI) not on PATH")
    return exe


def claude_runner(prompt: bytes, model: str, timeout_s: int) -> dict:
    """One `claude -p` run in an empty work dir: prompt on stdin, no tools, JSON out. Returns {rc, stdout, stderr, argv}."""
    work = Path(tempfile.mkdtemp(prefix="p3-claude-"))
    try:
        argv = [_claude_exe(), "-p", "--output-format", "json", "--model", model, "--tools", "",
                "--no-session-persistence"]
        try:
            p = subprocess.run(argv, cwd=str(work), input=prompt, capture_output=True, timeout=timeout_s)
            rc, so, se = p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired as exc:
            rc, so, se = -9, exc.stdout or b"", (exc.stderr or b"") + f"\nTIMEOUT after {timeout_s}s".encode()
        red = ["claude", "-p", "--output-format", "json", "--model", model, "--tools", "", "--no-session-persistence",
               f"<stdin: prompt sha256 {hashlib.sha256(prompt).hexdigest()}>"]
        return {"rc": rc, "stdout": so, "stderr": se, "argv": red}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _claude_version() -> str:
    try:
        return subprocess.run([_claude_exe(), "--version"], capture_output=True, text=True, timeout=60).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "UNKNOWN"


def _global_claude_md_digest() -> dict | None:
    p = Path(os.path.expanduser("~")) / ".claude" / "CLAUDE.md"
    if p.is_file():
        return {"ref": "client-global-instructions:~/.claude/CLAUDE.md (content not copied)",
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "what": "the client's global instruction file in force for this call"}
    return None


def claude_call(prompt: bytes, *, model: str, caller: dict, input_digests: list, timeout_s: int = 900,
                runner=None, client_version: str | None = None) -> dict:
    """One Claude call -> one model_call_record/1 (RAN_OK or RAN_ERROR; a failed call is data, never an exception)."""
    from reproducible_ai import model_source, record_licence
    probs = record_licence.record_problems({"record_id": "pre-call", "input_digests": list(input_digests),
                                            "prompt": {"b64": base64.b64encode(prompt).decode("ascii")}})
    if probs:
        raise PermissionError("licence guard refused the prompt: " + "; ".join(probs)[:600])
    real = runner is None
    runner = runner or claude_runner
    digests = list(input_digests)
    g = _global_claude_md_digest() if real else None
    if g:
        digests.append(g)
    digests.append({"ref": "output-schema (stated in the prompt)", "sha256":
                    hashlib.sha256(model_source.canonical(RESPONSE_SCHEMA)).hexdigest(), "what": "answer schema"})
    t0 = _utc()
    r = runner(prompt, model, timeout_s)
    t1 = _utc()
    so, se = r.get("stdout") or b"", r.get("stderr") or b""
    try:
        out = json.loads(so.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        out = None
    out = out if isinstance(out, dict) else {}
    used = sorted((out.get("modelUsage") or {}).keys())
    resp = out.get("result").encode("utf-8") if isinstance(out.get("result"), str) else b""
    err = None
    if r.get("rc") != 0:
        err = f"client exited {r.get('rc')}: " + se.decode("utf-8", "replace")[-600:]
    elif out.get("is_error") or out.get("subtype") != "success":
        err = f"client result subtype {out.get('subtype')!r} is_error={out.get('is_error')!r}"
    elif not resp.strip():
        err = "client exited 0 with an EMPTY result (RAN_ERROR, never RAN_ZERO)"
    elif model not in used:
        err = f"client modelUsage names {used} but {model!r} was requested: the pin does not hold"
    elif (out.get("num_turns") or 0) > 1:
        err = f"{out.get('num_turns')} turns with tools disabled: the call did not run as a single reading"
    state = "RAN_ERROR" if err else "RAN_OK"
    return model_source.build_record(
        prompt_bytes=prompt, response_bytes=resp if state == "RAN_OK" else b"",
        model={"id_requested": model, "id_reported": model if model in used else (",".join(used) or "UNREPORTED"),
               "provider": "anthropic",
               "reported_by": "client JSON modelUsage (claude -p --output-format json); not a server attestation"},
        params={"tools": "none (--tools '')", "output_format": "json", "session_persistence": False,
                "timeout_s": timeout_s, "output_schema": RESPONSE_SCHEMA, "workdir": "empty temp dir"},
        not_controllable=list(CLAUDE_NOT_CONTROLLABLE),
        client={"name": "claude -p", "version": client_version or (_claude_version() if real else "test"),
                "argv": r.get("argv")},
        request_utc=t0, response_utc=t1, caller=caller, input_digests=digests, state=state, error=err,
        client_evidence={"model_usage_keys": used, "num_turns": out.get("num_turns"),
                         "stdout_sha256": hashlib.sha256(so).hexdigest(), "stderr_sha256": hashlib.sha256(se).hexdigest()})


def codex_call(prompt: bytes, *, model: str, effort: str, caller: dict, input_digests: list, runner=None,
               client_version: str | None = None) -> dict:
    from reproducible_ai import model_call_live
    return model_call_live.call(prompt, schema=RESPONSE_SCHEMA, model=model, effort=effort, caller=caller,
                                input_digests=input_digests, runner=runner, client_version=client_version)


def _parse(resp: bytes):
    t = resp.decode("utf-8", "replace").strip()
    if t.startswith("```"):
        t = t.strip("`")
        t = t[t.find("{"):]
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j < i:
        return None
    try:
        d = json.loads(t[i:j + 1])
    except ValueError:
        return None
    return d if isinstance(d, dict) and isinstance(d.get("items"), list) else None


def reading_from_record(record: dict, family: str, document_text: str, document_ref: str, document_sha256: str) -> dict:
    """Turn one call record into a reading. Items keep their claimed value; the passage is located deterministically."""
    reading = {"reader": {"family": family, "model_reported": (record.get("model") or {}).get("id_reported"),
                          "record_id": record.get("record_id")}, "items": [], "state": record.get("state")}
    if record.get("state") != "RAN_OK":
        reading["error"] = record.get("error")
        return reading
    resp = base64.b64decode((record.get("response") or {}).get("b64") or b"")
    d = _parse(resp)
    if d is None:
        reading["error"] = "response is not the contract's JSON object"
        return reading
    for it in d["items"]:
        if not isinstance(it, dict):
            continue
        q = it.get("quote") if isinstance(it.get("quote"), str) else ""
        loc = locate(document_text, q)
        item = {"field": it.get("field"), "arm": it.get("arm"), "value": it.get("value")}
        item["passage"] = None if loc is None else {"document_ref": document_ref, "document_sha256": document_sha256,
                                                     "start": loc[0], "end": loc[1], "quote": q}
        if loc is None:
            item["passage_problem"] = "quote not found exactly once in the document"
        reading["items"].append(item)
    return reading


def run_dual(*, docs_root: str, document_ref: str, trial_id: str, measure: str, claude_model: str, codex_model: str,
             codex_effort: str, caller: dict, claude_runner_fn=None, codex_runner_fn=None) -> dict:
    """Read one trial twice, independently. -> {"readings": [claude, codex], "records": [rec, rec]}"""
    path = os.path.join(docs_root, *document_ref.replace("\\", "/").split("/"))
    raw = Path(path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8")
    prompt = build_prompt(text, trial_id, measure)
    digests = [{"ref": document_ref, "sha256": sha, "what": "the held document the reader extracts from"}]
    rc = claude_call(prompt, model=claude_model, caller=caller, input_digests=digests, runner=claude_runner_fn,
                     client_version="test" if claude_runner_fn else None)
    rx = codex_call(prompt, model=codex_model, effort=codex_effort, caller=caller, input_digests=digests,
                    runner=codex_runner_fn, client_version="test" if codex_runner_fn else None)
    return {"readings": [reading_from_record(rc, "anthropic", text, document_ref, sha),
                         reading_from_record(rx, "openai", text, document_ref, sha)],
            "records": [rc, rx]}
