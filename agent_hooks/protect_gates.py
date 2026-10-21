#!/usr/bin/env python3
"""protect_gates.py -- an OPT-IN Claude Code PreToolUse hook: a lane's agent may not edit the files that decide what
"the gate passed" means in meta-harness.

WHAT IT IS. Before the agent runs Edit / Write / MultiEdit / NotebookEdit -- or a Bash command that writes to, moves,
restores or deletes a file -- the hook checks the target against PROTECTED below: pytest configuration and every
conftest.py, the local git hooks, the CI workflows, scripts/verify_all.py, the gate registries, the honest-state
ratchet's acknowledgements and baseline, and the allow-lists in tests/test_model_inventory.py. A match is BLOCKED
(exit 2) and the agent is told to disclose instead.

WHY. "Fix the harness, never the gate" (.githooks/pre-commit) was text. Changing a gate is the cheapest way for an agent
to turn red into green: add an entry to UNRESOLVED_SUBPROCESS, acknowledge a ratchet drop, widen an authorised exception,
deselect a test in conftest.py. Measured, not hypothetical: Gomez (arXiv:2608.29460) found 23.6% of agent runs
edited tests to pass, cut to 5.3% by an explicit "report the broken test" route; SpecBench (arXiv:2605.21384), CATCH
(arXiv:2609.39533). See docs/ai-coding-research-log.md.

THE OVERRIDE IS FOR HUMANS, AND IS LEDGERED. Set MH_ALLOW_GATE_EDIT=1 (optionally MH_ALLOW_GATE_EDIT_REASON="...") in
the shell that LAUNCHES Claude Code. The hook reads its own process environment, which a command typed by the agent does
not change. Every protected edit the override lets through is appended to agent_hooks/override_ledger.jsonl (path
overridable with MH_AGENT_HOOK_LEDGER); if that append fails, the edit is BLOCKED -- an unledgered override is not one.

FAIL CLOSED. Hook input that is not a JSON object, or an edit-tool call whose target path cannot be read, is BLOCKED
(exit 2). (The source hook failed open with exit 1; meta-harness gates refuse when they cannot execute.)

WHAT IT DOES NOT CHECK, named rather than implied.
  - Bash detection is a heuristic: a protected path plus a write-shaped verb in the same command segment, a redirect
    onto a protected path, or an in-line python write anywhere in the command. A command that builds the path at
    runtime is not caught. `git stash` / `git reset --hard` / `git checkout <branch>` are not treated as writes.
  - It does not stop edits to other test files: lanes legitimately ADD tests. Review test diffs.
  - It does not check what a human commits. CI (scripts/verify_all.py) and review remain the enforcement.

EXIT CODES (Claude Code's PreToolUse contract): 0 allowed; 2 BLOCKED, the reason on stderr is shown to the agent.

    python agent_hooks/protect_gates.py --selftest   # proves it fires, and that it does not
    python agent_hooks/protect_gates.py --version

Offline, standard library only, no model call. Nothing in harness/ imports this file.
"""
from __future__ import annotations

import datetime
import getpass
import hashlib
import json
import os
import posixpath
import re
import sys
from pathlib import Path

VERSION = "1.0.0"  # keep equal to agent_hooks.__version__ (tests/test_agent_hooks_protect_gates.py checks)

ALLOWED, BLOCKED = 0, 2
OVERRIDE_ENV = "MH_ALLOW_GATE_EDIT"
REASON_ENV = "MH_ALLOW_GATE_EDIT_REASON"
LEDGER_ENV = "MH_AGENT_HOOK_LEDGER"
DEFAULT_LEDGER = Path(__file__).resolve().parent / "override_ledger.jsonl"

# Repo-relative path -> why it is protected. Matched case-insensitively against the END of the target path on a
# component boundary, so absolute paths, worktree paths and Windows separators all match.
PROTECTED_FILES = {
    "scripts/verify_all.py": "the publication standard CI and .githooks/pre-commit run",
    "registry/gate_gaps.json": "the declared gate gaps (what a gate is allowed not to catch)",
    "registry/gate_scorecard.json": "the gate scorecard",
    "registry/heldout_sealed.json": "the sealed held-out set",
    "registry/authorised_exceptions.json": "the authorised exceptions to the gates",
    "docs/ratchet_acknowledgements.json": "the honest-state ratchet's acknowledgements (a page may get quieter only here)",
    "harness/honest_ratchet.py": "the honest-state ratchet's baseline (MARKERS, BLOCK_RATCHET_BASE_REFS)",
    "tests/test_model_inventory.py": "the model-call / subprocess / model-output allow-lists",
    "agent_hooks/protect_gates.py": "this guard",
    "agent_hooks/override_ledger.jsonl": "the ledger of human overrides of this guard",
    ".claude/settings.json": "where this guard is installed",
    ".claude/settings.local.json": "where this guard is installed",
}
# Protected wherever they appear: pytest configuration. Only tests/conftest.py exists today; any new one changes what
# the suite collects or skips. (pyproject.toml / setup.cfg hold nothing else in this repo, so unlike the source they are
# protected by default.)
PROTECTED_NAMES = ("conftest.py", "pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml")
# Directories whose every file is a gate.
PROTECTED_DIRS = {
    ".githooks": "the local publication gate (pre-commit, commit-msg)",
    ".github/workflows": "the CI workflows",
}

EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
PATH_KEYS = ("file_path", "notebook_path", "path")

# A shell verb that writes, moves, restores or deletes the files it names. Deliberately narrow: READING a gate (cat,
# grep, python -m pytest tests/test_model_inventory.py 2>&1) must stay allowed.
WRITE_VERB = re.compile(
    r"(^|[\s(])(sed\s+(-[a-zA-Z]*i|--in-place)|tee|rm|rmdir|mv|cp|truncate|touch|dd|install|ln|chmod"
    r"|git\s+(checkout|restore|rm|mv|apply|am|cherry-pick|revert|update-index)"
    r"|perl\s+-[a-zA-Z]*i|Set-Content|Add-Content|Out-File|Remove-Item|Move-Item|Copy-Item|Clear-Content|New-Item)\b"
)
# A redirect and its target: `> f`, `>> f`, `1> f`; not `2>&1`.
REDIRECT = re.compile(r"(?:^|[^>&0-9])\d?>>?\s*(?!&)([^\s;|&()<>]+)")
# An in-line interpreter write (python -c "...open(p, 'w')...") anywhere in the command.
INLINE_WRITE = re.compile(
    r"write_text|write_bytes|\.unlink\(|os\.remove|os\.replace|os\.rename|shutil\.(move|copy|rmtree)"
    r"|json\.dump\(|open\([^)]*,\s*(mode\s*=\s*)?['\"][wax]"
)
SEGMENT_SPLIT = re.compile(r"&&|\|\||[;|\n]")
TOKEN_SPLIT = re.compile(r"[\s'\"`;|&()<>=,]+")


def _norm(path: str) -> str:
    p = path.strip().replace("\\", "/")
    p = posixpath.normpath(p) if p else p
    return p.lower().rstrip("/")


def protected_reason(path: str):
    """Why `path` is protected, or None."""
    if not isinstance(path, str) or not path.strip():
        return None
    norm = _norm(path)
    padded = "/" + norm
    for rel, why in PROTECTED_FILES.items():
        if padded.endswith("/" + rel):
            return "%s (%s)" % (rel, why)
    base = norm.rsplit("/", 1)[-1]
    if base in PROTECTED_NAMES:
        return "%s (pytest configuration)" % base
    for d, why in PROTECTED_DIRS.items():
        if padded.endswith("/" + d) or ("/" + d + "/") in padded:
            return "%s/ (%s)" % (d, why)
    return None


_BARE_BASENAMES = {rel.rsplit("/", 1)[-1]: rel for rel in PROTECTED_FILES}


def _token_reason(token: str):
    """protected_reason for a shell token; a bare file name (the shell may have cd'd) matches by name."""
    why = protected_reason(token)
    if why:
        return why
    t = _norm(token)
    if "/" not in t and t in _BARE_BASENAMES:
        return protected_reason(_BARE_BASENAMES[t])
    if "/" not in t and t in (".githooks", "workflows"):
        return protected_reason(".github/workflows" if t == "workflows" else t)
    return None


def _tokens(text: str):
    return [t for t in TOKEN_SPLIT.split(text) if t]


def bash_targets(command: str) -> list:
    """Protected paths that a write-shaped Bash command touches."""
    hits = []
    for target in REDIRECT.findall(command):
        why = _token_reason(target)
        if why:
            hits.append(why)
    for segment in SEGMENT_SPLIT.split(command):
        if WRITE_VERB.search(segment):
            hits += [w for w in map(_token_reason, _tokens(segment)) if w]
    if INLINE_WRITE.search(command):
        hits += [w for w in map(_token_reason, _tokens(command)) if w]
    return sorted(set(hits))


def targets(payload: dict):
    """(protected targets, fail-closed reason or None) for one PreToolUse payload."""
    tool = payload.get("tool_name")
    args = payload.get("tool_input")
    if not isinstance(tool, str):
        return [], "payload has no string tool_name"
    if tool == "Bash":
        if not isinstance(args, dict) or not isinstance(args.get("command"), str):
            return [], "Bash call without a string tool_input.command"
        return bash_targets(args["command"]), None
    if tool in EDIT_TOOLS:
        if not isinstance(args, dict):
            return [], "%s call without a tool_input object" % tool
        paths = [args.get(k) for k in PATH_KEYS if k in args]
        if not paths or not all(isinstance(p, str) and p.strip() for p in paths):
            return [], "%s call whose target path cannot be read" % tool
        return sorted({w for w in map(protected_reason, paths) if w}), None
    return [], None


def _ledger_path() -> Path:
    return Path(os.environ.get(LEDGER_ENV) or DEFAULT_LEDGER)


def _ledger(payload: dict, hits: list) -> None:
    """Append one override use. Raises OSError if it cannot be written."""
    tool_input = payload.get("tool_input")
    entry = {
        "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hook": "agent_hooks/protect_gates.py",
        "version": VERSION,
        "override": OVERRIDE_ENV,
        "reason": os.environ.get(REASON_ENV, ""),
        "os_user": _user(),
        "session_id": payload.get("session_id", ""),
        "cwd": payload.get("cwd", ""),
        "tool": payload.get("tool_name"),
        "targets": hits,
        "tool_input_sha256": hashlib.sha256(
            json.dumps(tool_input, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest(),
    }
    path = _ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")


def _user() -> str:
    try:
        return getpass.getuser()
    except Exception:  # noqa: BLE001 -- no user name is not a reason to lose the ledger line
        return ""


def _refuse_unreadable(why: str) -> tuple:
    return BLOCKED, (
        "BLOCKED by protect_gates (opt-in hook, v%s): could not read the hook input (%s), so the call was NOT "
        "checked; refusing (fail closed). If this repeats, tell the human: the hook or Claude Code's hook payload "
        "is broken." % (VERSION, why))


def decide(payload) -> tuple:
    """(exit_code, message) for one PreToolUse payload."""
    if not isinstance(payload, dict):
        return _refuse_unreadable("payload is not a JSON object")
    hits, unreadable = targets(payload)
    if unreadable:
        return _refuse_unreadable(unreadable)
    if not hits:
        return ALLOWED, ""
    if os.environ.get(OVERRIDE_ENV) == "1":
        try:
            _ledger(payload, hits)
        except OSError as exc:
            return BLOCKED, (
                "BLOCKED by protect_gates (v%s): %s=1 is set but the override could not be ledgered to %s (%s). "
                "An unledgered override is refused." % (VERSION, OVERRIDE_ENV, _ledger_path(), exc))
        return ALLOWED, ""
    return BLOCKED, (
        "BLOCKED by protect_gates (opt-in hook, v%s): %s.\n"
        "This file decides what 'the gate passed' means in meta-harness, so a lane's agent may not edit it.\n"
        "Do NOT work around this (no other tool, no shell, no generated path). Fix the harness, never the gate.\n"
        "Instead: stop and tell the human which gate you believe is wrong, why, and the exact change you propose\n"
        "(put it in your lane report). A human makes it, or relaunches Claude Code with %s=1 for one session;\n"
        "every use of that override is ledgered." % (VERSION, "; ".join(hits), OVERRIDE_ENV))


# ---------------------------------------------------------------------------------------------- selftest (both ways)
def _call(tool: str, key: str, value: str) -> dict:
    return {"tool_name": tool, "tool_input": {key: value}}


MUST_BLOCK = [
    _call("Edit", "file_path", "C:/wt/lane/tests/test_model_inventory.py"),
    _call("Write", "file_path", "C:\\wt\\lane\\registry\\gate_gaps.json"),
    _call("MultiEdit", "file_path", "/repo/tests/conftest.py"),
    _call("Edit", "file_path", ".github/workflows/verify.yml"),
    _call("Write", "file_path", ".githooks/pre-commit"),
    _call("Bash", "command", "echo '{}' > docs/ratchet_acknowledgements.json"),
    _call("Bash", "command", "sed -i s/b8925e04/HEAD/ harness/honest_ratchet.py"),
    _call("Bash", "command", "git checkout HEAD~3 -- scripts/verify_all.py"),
    _call("Bash", "command", "cd registry && rm heldout_sealed.json"),
]
MUST_ALLOW = [
    _call("Edit", "file_path", "harness/pipeline.py"),
    _call("Write", "file_path", "tests/test_new_lane_check.py"),
    _call("Edit", "file_path", "docs/gate_scorecard.json"),
    _call("Read", "file_path", "registry/gate_gaps.json"),
    _call("Bash", "command", "python -m pytest tests/test_model_inventory.py -q 2>&1 | tail -5"),
    _call("Bash", "command", "cat registry/authorised_exceptions.json"),
    _call("Bash", "command", "python scripts/verify_all.py > scratch/verify.log"),
]


def selftest() -> int:
    failures = []
    saved = {k: os.environ.pop(k, None) for k in (OVERRIDE_ENV, REASON_ENV)}
    try:
        failures += ["MISSED: %r" % (p,) for p in MUST_BLOCK if decide(p)[0] != BLOCKED]
        failures += ["FALSE BLOCK: %r" % (p,) for p in MUST_ALLOW if decide(p)[0] != ALLOWED]
        if decide("not a dict")[0] != BLOCKED:
            failures.append("unreadable input was not refused")
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v
    if failures:
        for f in failures:
            print("SELFTEST FAIL: %s" % f)
        return 1
    print("selftest OK -- %d must-block blocked, %d must-allow allowed, unreadable input refused."
          % (len(MUST_BLOCK), len(MUST_ALLOW)))
    return 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return selftest()
    if "--version" in argv:
        print(VERSION)
        return 0
    try:
        payload = json.loads(sys.stdin.read() or "null")
    except (ValueError, UnicodeDecodeError) as exc:
        code, msg = _refuse_unreadable("not JSON: %s" % exc)
    else:
        code, msg = decide(payload)
    if msg:
        print(msg, file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
