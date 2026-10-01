"""Reproducible AI (Mahmood, 2026-09-29): every data-touching model call goes through the recorder -- prompt, model id, input digests
and output recorded; replay returns identical bytes; the output is a PROPOSAL the deterministic gate re-checks
(reproducible_ai/model_source.py). This guard makes 'only the recorder calls a model' a checked property of the tree, not a convention:

  1. AST + text scan of every tracked .py, .sh and .ps1 file: a model reached anywhere except the recorder's live caller
     (reproducible_ai/model_call_live.py) FAILS. It reuses the repository's own detector (reproducible_ai.model_inventory.call_sites:
     client imports, a model CLI as an argv head, shutil.which(<cli>)) and closes what that detector does not see: importlib /
     __import__ of a client, os.system / os.popen / a shell-string subprocess naming a model CLI, and model CLIs in shell scripts.
  2. Committed model OUTPUTS the build can read (cache/*/*.json carrying model provenance) must name a record in registry/model_calls.
     The ones that do not are listed below, frozen: the list may only shrink; a new unrecorded output FAILS.
Every exception is named with its reason; none is silent. Each detector is PLANTED below and must fire."""
import ast
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproducible_ai import model_inventory as mi  # noqa: E402

RECORDER = "reproducible_ai/model_call_live.py"
# Named exceptions, each with its reason. Adding one is a reviewed change to this file; none is implied.
EXCEPTIONS = {
    "tests/test_no_model_call_in_pinned_path.py": "a TEST fixture string (argv head 'codex') used to prove the pinned-path audit detects it",
    "tests/test_model_calls_only_via_recorder.py": "this guard's own plants",
    "scripts/codex_lane.sh": "OPEN DEBT (2026-09-29): agent-lane orchestration calls `codex exec` outside the recorder. It drives a "
                             "model as a DEVELOPER (writing patches for review), not as a data source; any data-touching use must "
                             "move behind reproducible_ai. Listed so it is visible, not allowed silently.",
}
# OPEN DEBT, DATA-TOUCHING (found by this guard on 2026-09-29; all on origin/main 65acd80b): evidence-producing runs that call
# `codex exec` directly from shell -- their outputs are model judgments made outside the recorder (no replayable record). Each must be
# re-routed through reproducible_ai/model_call_live.py or retired; the list may only shrink.
EXCEPTIONS.update({p: "OPEN DEBT (data-touching): evidence run calling `codex exec` directly, outside the recorder" for p in (
    "evidence/scripts/retry_failed.sh", "evidence/scripts/run_codex.sh", "evidence/scripts/run_codex_retest.sh",
    "evidence/scripts/run_gap.sh", "evidence/scripts/run_second.sh", "evidence/typed_arms/scripts/run_codex.sh")})
# Committed model outputs with no record (measured on origin/main 65acd80b by reproducible_ai.model_inventory.model_outputs).
# OPEN DEBT: each must be re-made through the recorder or removed; the list may only shrink.
UNRECORDED_OUTPUTS_FROZEN = {
    "cache/antibiotics-vs-appendectomy-appendicitis/locate_judgments.json",
    "cache/balanced-crystalloids-vs-saline-mortality/outcome_judgments.json",
    "cache/colchicine-postop-af/screen_adjudication.json",
    "cache/colchicine-recurrent-pericarditis/screen_adjudication.json",
    "cache/colchicine-secondary-cv-prevention/screen_adjudication.json",
    "cache/finerenone-ckd-t2d-renal/screen_adjudication.json",
    "cache/omega3-cardiovascular-events/screen_adjudication.json",
    "cache/probiotics-aad-prevention/locate_judgments.json",
    "cache/probiotics-aad-prevention/screen_adjudication.json",
    "cache/sglt2-ckd-progression/screen_adjudication.json",
    "cache/statins-primary-prevention-elderly/screen_adjudication.json",
    "cache/ticagrelor-vs-clopidogrel-acs/screen_adjudication.json",
    "cache/vitamin-d-acute-respiratory-infection/locate_judgments.json",
}

_CLI = "|".join(re.escape(c) for c in mi.MODEL_CLIS)
_SHELL_CALL = re.compile(rf"(?:^|[;&|`(]|\$\()\s*(?:nohup\s+|exec\s+|timeout\s+\d+\s+|&\s*)?(?:[\w./\\-]*[/\\])?(?:{_CLI})(?:\.cmd|\.exe)?\b(?!\.\w)",
                         re.I | re.M)
_STRING_CALL = re.compile(rf"^\s*(?:[\w./\\-]*[/\\])?(?:{_CLI})(?:\.cmd|\.exe)?\s+\S", re.I)


def extra_sites(rel: str, src: str) -> list[tuple]:
    """What model_inventory._scan does not see: dynamic imports of a client, and a model CLI inside a SHELL STRING."""
    out = []
    for node in ast.walk(ast.parse(src, filename=rel)):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        fname = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
        a0 = node.args[0] if node.args else None
        s0 = a0.value if isinstance(a0, ast.Constant) and isinstance(a0.value, str) else None
        if fname in ("import_module", "__import__") and s0 and (s0 in mi.MODEL_CLIENTS or s0.split(".")[0] in mi.MODEL_CLIENTS):
            out.append((rel, node.lineno, f"dynamic import {s0}"))
        if fname in ("system", "popen", *mi.SUBPROCESS_FNS) and s0 and _STRING_CALL.search(s0):
            out.append((rel, node.lineno, f"shell string {s0[:40]!r}"))
    return out


def shell_sites(rel: str, text: str) -> list[tuple]:
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        code = line.split("#", 1)[0]
        if _SHELL_CALL.search(code):
            out.append((rel, i, f"shell call {code.strip()[:50]!r}"))
    return out


def tracked(pattern: str) -> list[str]:
    return sorted(subprocess.run(["git", "ls-files", pattern], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split())


def all_sites(root: Path, py: list[str], sh: list[str]) -> list[tuple]:
    sites = mi.call_sites(root, py)
    for rel in py:
        sites += extra_sites(rel, (root / rel).read_text(encoding="utf-8", errors="replace"))
    for rel in sh:
        sites += shell_sites(rel, (root / rel).read_text(encoding="utf-8", errors="replace"))
    return sites


def test_no_module_outside_the_recorder_reaches_a_model():
    sites = all_sites(ROOT, tracked("*.py"), tracked("*.sh") + tracked("*.ps1"))
    outside = sorted({(f, n, w) for f, n, w in sites if f != RECORDER and f not in EXCEPTIONS})
    assert not outside, "model reached outside the recorder:\n" + "\n".join(f"  {f}:{n} {w}" for f, n, w in outside)
    assert any(f == RECORDER for f, _, _ in sites), "the recorder itself is not detected -- the detector is blind"


def test_the_named_exceptions_still_exist_and_still_need_to_be_exceptions():
    # a stale exception is a hole: if the file is gone or no longer calls a model, the entry must be removed
    for rel in EXCEPTIONS:
        p = ROOT / rel
        assert p.exists(), f"exception for a file that no longer exists: {rel}"
        text = p.read_text(encoding="utf-8", errors="replace")
        hits = shell_sites(rel, text) if rel.endswith((".sh", ".ps1")) else \
            mi.call_sites(ROOT, [rel]) + extra_sites(rel, text)
        assert hits or rel.endswith("test_model_calls_only_via_recorder.py"), f"exception no longer needed: {rel}"


def test_no_new_unrecorded_model_output():
    outs = mi.model_outputs(ROOT)
    unrecorded = {o["path"] for o in outs if o["state"] == "UNRECORDED"}
    new = sorted(unrecorded - UNRECORDED_OUTPUTS_FROZEN)
    assert not new, "committed model output with no record in registry/model_calls (route it through the recorder):\n  " + "\n  ".join(new)


# ------------------------------------------------------------------------------------------------------------------ plants
PLANTS = {
    "client_import.py": "import anthropic\n",
    "client_from_import.py": "from openai import OpenAI\n",
    "argv_head.py": "import subprocess\nsubprocess.run(['codex', 'exec', '-'])\n",
    "which.py": "import shutil\nshutil.which('claude')\n",
    "dynamic_import.py": "import importlib\nimportlib.import_module('openai')\n",
    "dunder_import.py": "__import__('anthropic')\n",
    "os_system.py": "import os\nos.system('codex exec --json -')\n",
    "shell_string.py": "import subprocess\nsubprocess.run('claude -p hello', shell=True)\n",
}
SHELL_PLANTS = {"lane.sh": "#!/bin/sh\nnohup codex exec -s read-only - < brief.md\n",
                "lane.ps1": "& gemini -p 'read this table'\n"}
NEGATIVES = {"ok_git.py": "import subprocess\nsubprocess.run(['git', 'status'])\n",
             "ok_word.py": "MODEL_CLIS = ('codex', 'claude')   # a vocabulary tuple, not an argv\nprint('codex is a word')\n",
             "ok.sh": "# codex exec is mentioned in a comment only\ngit status\n"}


@pytest.mark.parametrize("name", sorted(PLANTS))
def test_PLANT_each_way_of_reaching_a_model_is_detected(tmp_path, name):
    (tmp_path / name).write_text(PLANTS[name], encoding="utf-8")
    assert all_sites(tmp_path, [name], []), f"undetected: {PLANTS[name]!r}"


@pytest.mark.parametrize("name", sorted(SHELL_PLANTS))
def test_PLANT_a_model_cli_in_a_shell_script_is_detected(tmp_path, name):
    (tmp_path / name).write_text(SHELL_PLANTS[name], encoding="utf-8")
    assert all_sites(tmp_path, [], [name]), f"undetected: {SHELL_PLANTS[name]!r}"


@pytest.mark.parametrize("name", sorted(NEGATIVES))
def test_negatives_are_not_flagged(tmp_path, name):
    (tmp_path / name).write_text(NEGATIVES[name], encoding="utf-8")
    py, sh = ([name], []) if name.endswith(".py") else ([], [name])
    assert not all_sites(tmp_path, py, sh), NEGATIVES[name]
