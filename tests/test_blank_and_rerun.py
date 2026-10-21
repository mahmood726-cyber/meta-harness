"""scripts/blank_and_rerun.py (port M-C, 2026-10-21): blank a function in place, re-run its pytest selection.

BOTH directions, on a SYNTHETIC package built in tmp_path (never a harness module: the tool edits files in place).
The planted defect is the hollow test -- it compares a stored reference to itself and passes with or without the
function it names; the tool must call it HOLLOW. The known-answer test beside it must BITE, or the tool flags
everything. The safety plants: a dirty or untracked file is refused untouched, and the file is restored byte-for-byte
(sha256) after every outcome, including an interrupt mid-run.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "blank_and_rerun.py"

POOL = (
    "import functools\n"
    "\n"
    "def dl_tau2(q, df, c):\n"
    "    \"\"\"DerSimonian-Laird tau^2.\"\"\"\n"
    "    return max(0.0, (q - df) / c)\n"
    "\n"
    "def i2(q, df):\n"
    "    return max(0.0, (q - df) / q)\n"
    "\n"
    "class Pooler:\n"
    "    @functools.lru_cache\n"
    "    def k(self, n): return n\n"
)
# known-answer: calls the function, compares to a reference value
BITING = (
    "import pool\n"
    "def test_dl_tau2_known_answer():\n"
    "    assert abs(pool.dl_tau2(12.0, 4, 20.0) - 0.4) < 1e-12\n"
)
# HOLLOW (the plant): names i2, compares the stored reference to itself, never calls it
HOLLOW = (
    "import pool\n"
    "R_I2 = 0.6666666666666666\n"
    "def test_i2_matches_r():\n"
    "    ours = 0.6666666666666666\n"
    "    assert abs(ours - R_I2) < 1e-12\n"
)


@pytest.fixture(scope="module")
def bar():
    spec = importlib.util.spec_from_file_location("blank_and_rerun", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false", *args],
                   cwd=root, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A committed tiny package: pool.py, one biting test file, one hollow test file, its own pytest rootdir."""
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    (tmp_path / "pool.py").write_bytes(POOL.encode("utf-8"))
    (tmp_path / "test_biting.py").write_text(BITING, encoding="utf-8")
    (tmp_path / "test_hollow.py").write_text(HOLLOW, encoding="utf-8")
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "fixture")
    return tmp_path


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------------------ both directions
def test_a_known_answer_test_bites(bar, repo):
    r = bar.check(str(repo), "pool.py", ["dl_tau2"], ["test_biting.py"], timeout=120)
    assert r["baseline"]["exit_code"] == 0
    assert [f["verdict"] for f in r["functions"]] == ["BITES"]
    assert r["functions"][0]["marker_seen"] is True           # it failed BECAUSE of the blank
    assert bar.exit_code([r]) == 0


def test_planted_hollow_test_is_called_hollow(bar, repo):
    r = bar.check(str(repo), "pool.py", ["i2"], ["test_hollow.py"], timeout=120)
    assert [f["verdict"] for f in r["functions"]] == ["HOLLOW"]
    assert bar.exit_code([r]) == 1


def test_one_hollow_function_among_biting_ones_fails_the_run(bar, repo):
    r = bar.check(str(repo), "pool.py", ["dl_tau2", "i2"], ["test_biting.py", "test_hollow.py"], timeout=120)
    assert {f["function"]: f["verdict"] for f in r["functions"]} == {"dl_tau2": "BITES", "i2": "HOLLOW"}
    assert bar.exit_code([r]) == 1


def test_return_none_mode_bites_too(bar, repo):
    r = bar.check(str(repo), "pool.py", ["dl_tau2"], ["test_biting.py"], timeout=120, mode="return-none")
    assert r["functions"][0]["verdict"] == "BITES"


# ------------------------------------------------------------------------------------------------ ERROR, never a pass
def test_a_selection_red_before_blanking_is_error_not_hollow(bar, repo):
    (repo / "test_biting.py").write_text(BITING + "def test_red():\n    assert False\n", encoding="utf-8")
    r = bar.check(str(repo), "pool.py", ["dl_tau2"], ["test_biting.py"], timeout=120)
    assert r["functions"][0]["verdict"] == "ERROR" and "BEFORE blanking" in r["functions"][0]["reason"]
    assert bar.exit_code([r]) == 2


def test_a_selection_that_collects_nothing_is_error(bar, repo):
    r = bar.check(str(repo), "pool.py", ["dl_tau2"], ["test_biting.py", "-k", "no_such_test"], timeout=120)
    assert r["baseline"]["exit_code"] == 5
    assert r["functions"][0]["verdict"] == "ERROR"


def test_a_missing_function_is_error(bar, repo):
    r = bar.check(str(repo), "pool.py", ["reml_tau2"], ["test_biting.py"], timeout=120)
    assert r["functions"][0]["verdict"] == "ERROR" and "not found" in r["functions"][0]["reason"]


def test_a_timeout_is_error_and_the_file_is_restored(bar, repo):
    before = _sha(repo / "pool.py")

    def runner(root, tests, timeout, calls=[]):
        calls.append(1)
        return (0, "ok", False) if len(calls) == 1 else (None, "timed out", False)
    r = bar.check(str(repo), "pool.py", ["dl_tau2"], ["test_biting.py"], timeout=1, runner=runner)
    assert r["functions"][0]["verdict"] == "ERROR"
    assert _sha(repo / "pool.py") == before


# ------------------------------------------------------------------------------------------------ in-place safety
def test_the_file_is_restored_byte_for_byte_after_every_outcome(bar, repo):
    before = _sha(repo / "pool.py")
    r = bar.check(str(repo), "pool.py", ["dl_tau2", "i2", "Pooler.k"], ["test_biting.py", "test_hollow.py"],
                  timeout=120)
    assert r["sha256_before"] == r["sha256_after"] == before == _sha(repo / "pool.py")
    assert (repo / "pool.py").read_bytes() == POOL.encode("utf-8")
    assert not list(repo.rglob("*.pyc")), "a blanked .pyc must not outlive the run"


def test_crlf_file_is_restored_and_blanked_with_its_own_line_endings(bar, repo):
    crlf = POOL.replace("\n", "\r\n").encode("utf-8")
    (repo / "pool.py").write_bytes(crlf)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "crlf")
    out = bar.blank_function(crlf.decode("utf-8"), "dl_tau2")
    assert "\r\n" in out and "\n" not in out.replace("\r\n", "")
    bar.check(str(repo), "pool.py", ["dl_tau2"], ["test_biting.py"], timeout=120)
    assert (repo / "pool.py").read_bytes() == crlf


def test_an_interrupt_mid_run_still_restores_the_file(bar, repo):
    before = _sha(repo / "pool.py")

    def runner(root, tests, timeout, calls=[]):
        calls.append(1)
        if len(calls) == 1:
            return 0, "baseline", False
        assert "NotImplementedError" in (repo / "pool.py").read_text(encoding="utf-8")   # it really is blanked now
        raise KeyboardInterrupt
    with pytest.raises(KeyboardInterrupt):
        bar.check(str(repo), "pool.py", ["dl_tau2"], ["test_biting.py"], timeout=120, runner=runner)
    assert _sha(repo / "pool.py") == before


def test_planted_dirty_file_is_refused_untouched(bar, repo):
    (repo / "pool.py").write_text(POOL + "# local edit\n", encoding="utf-8")
    dirty = _sha(repo / "pool.py")
    with pytest.raises(bar.Refused, match="already modified"):
        bar.check(str(repo), "pool.py", ["dl_tau2"], ["test_biting.py"], timeout=120)
    assert _sha(repo / "pool.py") == dirty


def test_planted_untracked_file_is_refused(bar, repo):
    (repo / "extra.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    with pytest.raises(bar.Refused, match="not tracked"):
        bar.check(str(repo), "extra.py", ["f"], ["test_biting.py"], timeout=120)


def test_a_failed_restore_is_loud(bar, repo, monkeypatch):
    monkeypatch.setattr(bar, "sha256", lambda path: "0" * 64)
    with pytest.raises(bar.Refused, match="RESTORE FAILED"):
        bar.check(str(repo), "pool.py", ["dl_tau2"], ["test_biting.py"], timeout=120)


# ------------------------------------------------------------------------------------------------ blanking
def test_blanking_keeps_signature_decorators_docstring_line_and_neighbours(bar):
    out = bar.blank_function(POOL, "dl_tau2")
    assert "def dl_tau2(q, df, c):\n" in out and "return max(0.0, (q - df) / c)" not in out
    assert "def i2(q, df):\n    return max(0.0, (q - df) / q)\n" in out
    compile(out, "x.py", "exec")


def test_blanking_a_decorated_one_line_method(bar):
    out = bar.blank_function(POOL, "Pooler.k")
    assert "@functools.lru_cache\n    def k(self, n): raise NotImplementedError" in out
    compile(out, "x.py", "exec")


def test_blanking_a_body_that_contains_a_form_feed(bar):
    src = "def f():\n    x = 1\f\n    return x\n\ndef g():\n    return 2\n"
    out = bar.blank_function(src, "f")
    assert "def g():\n    return 2\n" in out and "return x" not in out


# ------------------------------------------------------------------------------------------------ CLI
def test_cli_targets_file_json_and_exit_code(repo, tmp_path_factory):
    targets = tmp_path_factory.mktemp("t") / "targets.json"
    targets.write_text(json.dumps([{"file": "pool.py", "functions": ["dl_tau2"], "tests": ["test_biting.py"]},
                                   {"file": "pool.py", "functions": ["i2"], "tests": ["test_hollow.py"]}]),
                       encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(repo), "--targets", str(targets), "--json"],
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 1, r.stdout + r.stderr
    doc = json.loads(r.stdout)
    assert [f["verdict"] for res in doc["results"] for f in res["functions"]] == ["BITES", "HOLLOW"]


def test_cli_refusal_exit_code(repo):
    (repo / "pool.py").write_text("# dirty\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(repo), "--file", "pool.py", "--function", "dl_tau2",
                        "--tests", "test_biting.py"], capture_output=True, text=True, timeout=300)
    assert r.returncode == 3 and "REFUSED" in r.stderr


def test_opt_in_only_nothing_in_harness_or_verify_all_imports_it():
    for p in [*ROOT.glob("harness/**/*.py"), ROOT / "scripts" / "verify_all.py"]:
        assert "blank_and_rerun" not in p.read_text(encoding="utf-8", errors="replace"), p
