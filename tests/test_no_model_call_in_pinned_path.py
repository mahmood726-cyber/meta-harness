"""Reproducible AI (Mahmood, standing): a model may sit anywhere in the harness if its call is reproducible, and a
model never supplies a number. The pinned path -- the certificate's code closure -- is measured for model calls by
scripts/audit_model_calls.py on every tree, so 'none in the pinned path' is a count, never an assumption.
Evidence: docs/evidence/m2-hand-row-binding-2026-09-20/06-reproducible-ai-design-note.md."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import audit_model_calls as amc  # noqa: E402


@pytest.fixture(scope="module")
def report():
    return amc.sweep(amc.pinned_paths("glp1-ra-mace-t2d"))


def test_the_pinned_path_is_the_certificates_closure_and_is_present(report):
    assert report["paths_listed"] >= 80 and report["paths_present"] >= report["paths_listed"] - 1   # effect_type.py is a NOT_PRESENT entry


def test_no_model_call_in_the_pinned_path(report):
    assert report["model_calls"] == [], report["model_calls"]
    assert report["model_client_imports"] == []
    assert set(report["subprocess_programs"]) <= {"git", "python"}, report["subprocess_programs"]
    assert all(x[0] == "harness/http.py" for x in report["http_imports"]), report["http_imports"]


def test_PLANT_a_model_client_import_in_a_pinned_module_is_counted(tmp_path, monkeypatch):
    """The sweep must be able to go red: a pinned module that imports a model client is a model call."""
    (tmp_path / "harness").mkdir()
    (tmp_path / "harness" / "planted.py").write_text("import anthropic\n\ndef f():\n    return anthropic.Anthropic()\n", encoding="utf-8")
    (tmp_path / "harness" / "clean.py").write_text("import json\n\ndef g():\n    return json.dumps({})\n", encoding="utf-8")
    monkeypatch.setattr(amc, "ROOT", str(tmp_path))
    r = amc.sweep(["harness/planted.py", "harness/clean.py"])
    assert r["paths_present"] == 2
    assert [m[:2] for m in r["model_calls"]] == [("harness/planted.py", 1)]


def test_PLANT_a_model_cli_run_as_a_subprocess_is_counted(tmp_path, monkeypatch):
    (tmp_path / "harness").mkdir()
    (tmp_path / "harness" / "planted.py").write_text(
        'import subprocess\n\ndef f(prompt):\n    return subprocess.run(["codex", "exec", prompt], capture_output=True)\n', encoding="utf-8")
    monkeypatch.setattr(amc, "ROOT", str(tmp_path))
    r = amc.sweep(["harness/planted.py"])
    assert r["subprocess_programs"] == ["codex"]
    assert [m[2] for m in r["model_calls"]] == ["subprocess codex"]


def test_control_git_subprocesses_and_stdlib_http_are_not_model_calls(tmp_path, monkeypatch):
    (tmp_path / "harness").mkdir()
    (tmp_path / "harness" / "ok.py").write_text(
        'import subprocess\nimport urllib.request\n\ndef f():\n    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True)\n', encoding="utf-8")
    monkeypatch.setattr(amc, "ROOT", str(tmp_path))
    r = amc.sweep(["harness/ok.py"])
    assert r["model_calls"] == [] and r["subprocess_programs"] == ["git"] and len(r["http_imports"]) == 1
