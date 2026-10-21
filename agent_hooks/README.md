# agent_hooks — opt-in Claude Code hooks for lanes (v1.0.0, 2026-10-21)

Nothing here runs unless a lane turns it on. No gate, CI job, page build or `harness/` module imports this package;
a lane that does not install the hook behaves exactly as before.

## `protect_gates.py` — a lane's agent may not edit the gates

A Claude Code **PreToolUse hook**. Before the agent runs `Edit` / `Write` / `MultiEdit` / `NotebookEdit`, or a `Bash`
command that writes to, moves, restores or deletes a file, the hook checks the target. If it is one of the files
below, the call is **blocked** (exit 2) and the agent is told to stop and say which gate it believes is wrong, why,
and the exact change it proposes — in its lane report — instead of making the change.

| Protected | Why |
|---|---|
| any `conftest.py`, `pytest.ini`, `tox.ini`, `setup.cfg`, `pyproject.toml` | pytest configuration: what is collected, skipped, deselected |
| `.githooks/*` | the local publication gate |
| `.github/workflows/*` | CI |
| `scripts/verify_all.py` | the publication standard CI and the pre-commit hook run |
| `registry/gate_gaps.json`, `registry/gate_scorecard.json`, `registry/heldout_sealed.json`, `registry/authorised_exceptions.json` | the gate registries |
| `docs/ratchet_acknowledgements.json`, `harness/honest_ratchet.py` | the honest-state ratchet's acknowledgements and its baseline (`MARKERS`, `BLOCK_RATCHET_BASE_REFS`) |
| `tests/test_model_inventory.py` | the model-call / subprocess / model-output allow-lists |
| `agent_hooks/protect_gates.py`, `agent_hooks/override_ledger.jsonl`, `.claude/settings*.json` | the guard itself, its ledger, and where it is installed |

Reading any of them (`cat`, `grep`, `python -m pytest tests/test_model_inventory.py 2>&1`) is never blocked, and
adding a new `tests/test_<name>.py` is never blocked.

### Turn it on (per lane)

In the lane's clone or worktree, create or merge into `.claude/settings.local.json` (local, not committed — so the
opt-in is per lane, never for everyone):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash",
        "hooks": [
          {"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/agent_hooks/protect_gates.py\""}
        ]
      }
    ]
  }
}
```

Check it: `python agent_hooks/protect_gates.py --selftest` (and `--version`).

### When a human needs to change a gate

Edit the file yourself, or launch Claude Code from a shell with the override set, for that session only:

```bash
MH_ALLOW_GATE_EDIT=1 MH_ALLOW_GATE_EDIT_REASON="retire resolved HM3 declarations (#109)" claude
```

The hook reads its own process environment, so a command typed by the agent cannot set it. **Every** protected edit
the override lets through is appended to `agent_hooks/override_ledger.jsonl` (UTC time, version, reason, OS user,
session id, tool, targets, sha256 of the tool input). The ledger is part of the lane's diff: the integrator reviews
and commits it with the change. If the ledger cannot be written, the edit is blocked.

### Fail closed

Input that is not a JSON object, or an edit-tool call whose target path cannot be read, is **blocked** with a reason.
(The source hook failed open; meta-harness gates refuse when they cannot execute.)

### Limits, named

- The Bash check is a heuristic: a protected path plus a write verb in the same command segment, a redirect onto a
  protected path, or an in-line python write anywhere in the command. A path built at runtime is not caught, and
  `git stash` / `git reset --hard` / `git checkout <branch>` are not treated as writes. A bare file name in a write
  command (`rm gate_scorecard.json` after a `cd`) is matched by name, so it can also block the same name elsewhere.
- It does not stop edits to other test files. Lanes add tests; review test diffs.
- It is a convenience for lanes, not the enforcement: CI (`scripts/verify_all.py`) and review remain that.

Ported from e156-ecosystem-starter `scripts/protect-test-config.py` v1.0.0; evidence in
`docs/ai-coding-research-log.md`. Tests: `tests/test_agent_hooks_protect_gates.py`.
