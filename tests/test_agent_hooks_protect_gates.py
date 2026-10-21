"""agent_hooks/protect_gates.py: the opt-in hook that refuses a lane's agent edits to the gates.

Both directions, as everywhere here: a guard that blocks everything passes every must-block test, and one that blocks
nothing passes every must-allow test; only the pair says anything. The move this suite exists for: an agent that cannot
make tests/test_model_inventory.py pass adds its new subprocess to UNRESOLVED_SUBPROCESS and reports green.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import agent_hooks
from agent_hooks import protect_gates as pg

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "agent_hooks" / "protect_gates.py"
LANE = "C:\\wt\\some-lane\\"


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch, tmp_path):
    for k in (pg.OVERRIDE_ENV, pg.REASON_ENV):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv(pg.LEDGER_ENV, str(tmp_path / "ledger.jsonl"))   # never the real ledger


def call(tool, key, value):
    return {"tool_name": tool, "tool_input": {key: value}}


# -------------------------------------------------------------------------------------------- planted gate edits
PLANTED = [
    "tests/test_model_inventory.py", "tests/conftest.py", "harness/conftest.py", "pytest.ini", "tox.ini",
    "setup.cfg", "pyproject.toml", ".githooks/pre-commit", ".githooks/commit-msg", ".github/workflows/verify.yml",
    ".github/workflows/new.yml", "scripts/verify_all.py", "registry/gate_gaps.json", "registry/gate_scorecard.json",
    "registry/heldout_sealed.json", "registry/authorised_exceptions.json", "docs/ratchet_acknowledgements.json",
    "harness/honest_ratchet.py", "agent_hooks/protect_gates.py", "agent_hooks/override_ledger.jsonl",
    ".claude/settings.local.json",
]


@pytest.mark.parametrize("tool", pg.EDIT_TOOLS)
@pytest.mark.parametrize("rel", PLANTED)
def test_planted_gate_edit_is_blocked(rel, tool):
    key = "notebook_path" if tool == "NotebookEdit" else "file_path"
    for path in (rel, "/repo/" + rel, LANE + rel.replace("/", "\\"), rel.upper()):
        code, msg = pg.decide(call(tool, key, path))
        assert code == pg.BLOCKED, path
        assert "tell the human" in msg and "Do NOT work around" in msg and pg.OVERRIDE_ENV in msg


def test_the_agent_cannot_widen_the_model_inventory_allow_list():
    """The motivating move, through MultiEdit on an absolute worktree path."""
    payload = {"tool_name": "MultiEdit", "tool_input": {
        "file_path": LANE + "tests\\test_model_inventory.py",
        "edits": [{"old_string": "UNRESOLVED_SUBPROCESS = {",
                   "new_string": "UNRESOLVED_SUBPROCESS = {\n    ('scripts/mine.py', 'cmd'): 'fine',"}]}}
    code, msg = pg.decide(payload)
    assert code == pg.BLOCKED and "allow-lists" in msg


@pytest.mark.parametrize("cmd", [
    "echo '{}' > docs/ratchet_acknowledgements.json",
    "echo x >> registry/gate_gaps.json",
    "sed -i 's/b8925e04~1/HEAD/' harness/honest_ratchet.py",
    "git checkout HEAD~3 -- scripts/verify_all.py",
    "git restore --source=main tests/conftest.py",
    "rm -f .githooks/pre-commit",
    "rm -rf .github/workflows",
    "cd registry && rm heldout_sealed.json",
    "mv registry/authorised_exceptions.json /tmp/x",
    "cp /tmp/loose.json registry/gate_scorecard.json",
    "printf 'addopts = --deselect tests/test_model_inventory.py' > pytest.ini",
    "python -c \"import json; json.dump({}, open('registry/gate_gaps.json', 'w'))\"",
    "python -c \"from pathlib import Path; Path('tests/test_model_inventory.py').write_text('')\"",
    "Set-Content -Path registry\\gate_gaps.json -Value '{}'",
])
def test_planted_shell_write_to_a_gate_is_blocked(cmd):
    assert pg.decide(call("Bash", "command", cmd))[0] == pg.BLOCKED, cmd


# ------------------------------------------------------------------------------------------ unrelated: allowed
@pytest.mark.parametrize("path", [
    "harness/pipeline.py", "scripts/g1_batch.py", "tests/test_new_lane_check.py", "tests/test_honest_ratchet.py",
    "docs/gate_scorecard.json", "registry/gate_gaps_notes.md", "registry/fixes.json", "docs/conftest-notes.md",
    "LANE-XX-REPORT.md", "PORT_REPORT.json", LANE + "agent_hooks\\README.md",
])
def test_unrelated_edit_is_allowed(path):
    assert pg.decide(call("Edit", "file_path", path)) == (pg.ALLOWED, "")


@pytest.mark.parametrize("cmd", [
    "python -m pytest tests/test_model_inventory.py tests/test_agent_hooks_protect_gates.py -q 2>&1 | tail -5",
    "cat registry/authorised_exceptions.json",
    "grep -n UNRESOLVED tests/test_model_inventory.py",
    "python scripts/verify_all.py > scratch/verify.log 2>&1",
    "git diff -- .github/workflows/verify.yml",
    "git log --oneline -3 -- registry/gate_gaps.json",
    "echo hello > notes.txt",
    "rm -rf scratch/tmp",
])
def test_reading_or_unrelated_bash_is_allowed(cmd):
    assert pg.decide(call("Bash", "command", cmd)) == (pg.ALLOWED, ""), cmd


def test_read_and_other_tools_are_never_blocked():
    assert pg.decide(call("Read", "file_path", "registry/gate_gaps.json"))[0] == pg.ALLOWED
    assert pg.decide(call("Grep", "path", ".githooks"))[0] == pg.ALLOWED


# ------------------------------------------------------------------------------------------ override: ledgered
def test_human_override_allows_and_every_use_is_ledgered(monkeypatch, tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    monkeypatch.setenv(pg.OVERRIDE_ENV, "1")
    monkeypatch.setenv(pg.REASON_ENV, "retire resolved HM3 declarations")
    p1 = dict(call("Edit", "file_path", "registry/gate_gaps.json"), session_id="s-1")
    p2 = call("Bash", "command", "rm .githooks/commit-msg")
    assert pg.decide(p1) == (pg.ALLOWED, "")
    assert pg.decide(p2) == (pg.ALLOWED, "")
    assert pg.decide(call("Edit", "file_path", "harness/pipeline.py")) == (pg.ALLOWED, "")   # not a use: not ledgered
    lines = [json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 2
    assert lines[0]["tool"] == "Edit" and lines[0]["session_id"] == "s-1"
    assert lines[0]["targets"][0].startswith("registry/gate_gaps.json")
    assert lines[0]["reason"] == "retire resolved HM3 declarations" and lines[0]["version"] == pg.VERSION
    assert lines[1]["tool"] == "Bash" and lines[1]["targets"][0].startswith(".githooks/")
    assert re.fullmatch(r"[0-9a-f]{64}", lines[1]["tool_input_sha256"])


def test_override_that_cannot_be_ledgered_is_refused(monkeypatch, tmp_path):
    monkeypatch.setenv(pg.OVERRIDE_ENV, "1")
    monkeypatch.setenv(pg.LEDGER_ENV, str(tmp_path))          # a directory: the append fails
    code, msg = pg.decide(call("Write", "file_path", "scripts/verify_all.py"))
    assert code == pg.BLOCKED and "could not be ledgered" in msg


@pytest.mark.parametrize("value", ["0", "true", "yes", ""])
def test_only_the_exact_override_value_counts(monkeypatch, tmp_path, value):
    monkeypatch.setenv(pg.OVERRIDE_ENV, value)
    assert pg.decide(call("Edit", "file_path", "tests/conftest.py"))[0] == pg.BLOCKED
    assert not (tmp_path / "ledger.jsonl").exists()


# ------------------------------------------------------------------------------------- garbage input: fail closed
@pytest.mark.parametrize("payload", [
    None, [], "Edit", 3,
    {},                                                                  # no tool_name
    {"tool_name": "Edit"},                                               # no tool_input
    {"tool_name": "Write", "tool_input": {}},                            # no path
    {"tool_name": "Edit", "tool_input": {"file_path": ""}},
    {"tool_name": "Edit", "tool_input": {"file_path": ["registry/gate_gaps.json"]}},
    {"tool_name": "Bash", "tool_input": {"command": None}},
    {"tool_name": "Bash", "tool_input": "rm registry/gate_gaps.json"},
])
def test_unreadable_payload_is_refused(payload):
    code, msg = pg.decide(payload)
    assert code == pg.BLOCKED and "NOT checked" in msg and "fail closed" in msg


def _run(stdin_text, **env_extra):
    env = {k: v for k, v in os.environ.items() if k not in (pg.OVERRIDE_ENV, pg.REASON_ENV)}
    env.update(env_extra)
    return subprocess.run([sys.executable, str(HOOK)], input=stdin_text, capture_output=True, text=True, env=env,
                          cwd=str(ROOT), timeout=60)


@pytest.mark.parametrize("garbage", ["this is not json", "", "[1, 2]", "{\"tool_name\": \"Write\"", "null"])
def test_end_to_end_garbage_input_is_refused_with_exit_2(garbage):
    r = _run(garbage)
    assert r.returncode == 2 and "NOT checked" in r.stderr


def test_end_to_end_exit_codes_follow_the_hook_contract(tmp_path):
    blocked = _run(json.dumps(call("Write", "file_path", "registry/heldout_sealed.json")))
    assert blocked.returncode == 2 and "BLOCKED" in blocked.stderr
    allowed = _run(json.dumps(call("Write", "file_path", "scripts/new_tool.py")))
    assert allowed.returncode == 0 and allowed.stderr == ""
    ledger = tmp_path / "e2e.jsonl"
    over = _run(json.dumps(call("Edit", "file_path", ".github/workflows/verify.yml")),
                **{pg.OVERRIDE_ENV: "1", pg.LEDGER_ENV: str(ledger)})
    assert over.returncode == 0 and len(ledger.read_text(encoding="utf-8").splitlines()) == 1


# ------------------------------------------------------------------------------------ the guard stays honest
def test_every_named_gate_file_exists_so_the_guard_protects_something():
    """A renamed gate would leave the guard protecting a path that no longer exists, silently."""
    not_in_repo_yet = {"agent_hooks/override_ledger.jsonl", ".claude/settings.json", ".claude/settings.local.json"}
    missing = [rel for rel in pg.PROTECTED_FILES if rel not in not_in_repo_yet and not (ROOT / rel).is_file()]
    assert missing == []
    assert (ROOT / "tests" / "conftest.py").is_file() and all((ROOT / d).is_dir() for d in pg.PROTECTED_DIRS)


def test_version_is_one_constant():
    assert agent_hooks.__version__ == pg.VERSION == "1.0.0"
    r = subprocess.run([sys.executable, str(HOOK), "--version"], capture_output=True, text=True, timeout=60)
    assert r.stdout.strip() == pg.VERSION


def test_opt_in_nothing_in_harness_scripts_or_ci_imports_the_hook():
    pat = re.compile(r"agent_hooks|protect_gates")
    for sub, glob in (("harness", "*.py"), ("scripts", "*.py"), (".githooks", "*"), (".github/workflows", "*")):
        for p in (ROOT / sub).glob(glob):
            if p.is_file():
                assert not pat.search(p.read_text(encoding="utf-8", errors="replace")), p


def test_readme_install_snippet_is_valid_json_and_names_the_hook():
    text = (ROOT / "agent_hooks" / "README.md").read_text(encoding="utf-8")
    snippet = re.search(r"```json\n(.*?)```", text, re.S).group(1)
    entry = json.loads(snippet)["hooks"]["PreToolUse"][0]
    assert set(entry["matcher"].split("|")) == set(pg.EDIT_TOOLS) | {"Bash"}
    assert "agent_hooks/protect_gates.py" in entry["hooks"][0]["command"]


def test_selftest_passes():
    r = subprocess.run([sys.executable, str(HOOK), "--selftest"], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
