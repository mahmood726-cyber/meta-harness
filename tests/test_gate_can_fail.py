"""A function whose ROLE is a gate must be able to refuse -- scripts/gate_can_fail.py, and the ratchet that holds main to it.

The ratchet: every check_/gate_/verify_/limb_/assess_/compare_ function under harness/ and scripts/ that returns a verdict
must have a reachable refusing path, unless it is listed (file, function, reason) in registry/gate_can_fail_baseline.json.
The baseline recorded at port time (2026-10-21) is EMPTY: all 102 verdict-returning gate functions on main could refuse.
A new gate that can only pass fails here; the fix is a refusing path, or a rename if the function is advisory by design --
never a new baseline entry.

Both directions for every rule (ported from e156-ecosystem-starter tests/test_gate_can_fail.py): a detector with only a
positive test passes while matching everything; with only a negative test, while matching nothing.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "gate_can_fail.py"
_s = importlib.util.spec_from_file_location("gate_can_fail", SCRIPT)
gcf = importlib.util.module_from_spec(_s)
_s.loader.exec_module(gcf)


def _tree(tmp_path: Path, files: dict) -> Path:
    for d in gcf.SCAN_DIRS:
        (tmp_path / d).mkdir(exist_ok=True)
    for rel, src in files.items():
        (tmp_path / rel).write_text(src, encoding="utf-8")
    return tmp_path


def _cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


# ------------------------------------------------------------------------------------------- the ratchet on main
def test_no_gate_function_outside_the_baseline_cannot_refuse():
    result = gcf.apply_baseline(gcf.scan(ROOT), gcf.load_baseline(gcf.BASELINE))
    assert result["unparsable"] == [] and result["missing_dirs"] == [], result
    assert result["functions_checked"] > 0, "the lint judged nothing: its scope no longer matches this repo"
    assert result["new_findings"] == [], (
        "a gate function that can only pass -- give it a refusing path (or rename it if advisory by design): "
        + "; ".join("%s::%s (%s)" % (f["file"], f["function"], f["reason"]) for f in result["new_findings"]))
    assert result["verdict"] == "CLEAN"


def test_every_baseline_entry_names_file_function_and_reason():
    doc = json.loads(gcf.BASELINE.read_text(encoding="utf-8"))
    assert doc["lint"] == "scripts/gate_can_fail.py"
    for e in doc["entries"]:
        assert set(e) == {"file", "function", "reason"} and all(e.values()), e


def test_selftest_plants_bad_reads_defects_found_and_good_reads_clean():
    proc = _cli("--selftest")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "selftest OK" in proc.stdout and "DEFECTS-FOUND" in proc.stdout and "CLEAN" in proc.stdout


def test_harness_never_imports_the_lint():
    hits = [p.as_posix() for p in (ROOT / "harness").rglob("*.py")
            if "gate_can_fail" in p.read_text(encoding="utf-8", errors="replace")]
    assert hits == []


# ------------------------------------------------------------------------------------------- plant: must fire
@pytest.mark.parametrize("name", sorted(gcf.KNOWN_BAD))
def test_planted_defect_is_flagged(tmp_path, name):
    _tree(tmp_path, {"scripts/plant.py": gcf.KNOWN_BAD[name]})
    result = gcf.scan(tmp_path)
    assert [f["function"] for f in result["cannot_refuse"]] == [name]
    assert result["verdict"] == "DEFECTS-FOUND"


def test_planted_defect_in_harness_and_in_a_method_is_flagged(tmp_path):
    _tree(tmp_path, {"harness/g.py": "class G:\n    def verify_page(self, p):\n        return 'ok'\n"})
    result = gcf.scan(tmp_path)
    assert [(f["file"], f["function"]) for f in result["cannot_refuse"]] == [("harness/g.py", "G.verify_page")]


def test_new_finding_outside_the_baseline_fails_the_ratchet(tmp_path):
    """The ratchet itself: a baselined defect is tolerated, a NEW one is DEFECTS-FOUND (exit 1)."""
    _tree(tmp_path, {"scripts/old.py": "def check_old():\n    return True\n",
                     "scripts/new.py": "def limb_new():\n    return 'PASS', 'tail'\n"})
    base = tmp_path / "baseline.json"
    base.write_text(json.dumps({"entries": [{"file": "scripts/old.py", "function": "check_old", "reason": "r"}]}),
                    encoding="utf-8")
    result = gcf.apply_baseline(gcf.scan(tmp_path), gcf.load_baseline(base))
    assert [f["function"] for f in result["new_findings"]] == ["limb_new"] and result["baselined"] == 1
    assert _cli(str(tmp_path), "--baseline", str(base)).returncode == 1
    (tmp_path / "scripts" / "new.py").unlink()
    assert _cli(str(tmp_path), "--baseline", str(base)).returncode == 0


# ------------------------------------------------------------------------------------------- plant: must stay silent
@pytest.mark.parametrize("name", sorted(gcf.KNOWN_GOOD))
def test_known_good_is_not_flagged(tmp_path, name):
    _tree(tmp_path, {"scripts/plant.py": gcf.KNOWN_GOOD[name]})
    result = gcf.scan(tmp_path)
    assert result["cannot_refuse"] == []
    assert result["verdict"] == "CLEAN"


def test_a_function_not_named_a_gate_is_never_judged(tmp_path):
    _tree(tmp_path, {"scripts/h.py": "def summarise():\n    return True\n"})
    result = gcf.scan(tmp_path)
    assert result["functions_checked"] == 0 and result["cannot_refuse"] == []


def test_files_outside_harness_and_scripts_are_out_of_scope(tmp_path):
    _tree(tmp_path, {})
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "t.py").write_text("def check_x():\n    return True\n", encoding="utf-8")
    assert gcf.scan(tmp_path)["cannot_refuse"] == []


# ------------------------------------------------------------------------------------------- three verdicts, three codes
def test_exit_codes_are_the_three_verdicts(tmp_path):
    _tree(tmp_path, {"scripts/a.py": "def check_a():\n    return True\n"})
    assert _cli(str(tmp_path)).returncode == 1                                      # DEFECTS-FOUND
    (tmp_path / "scripts" / "a.py").write_text("def check_a(x):\n    return bool(x)\n", encoding="utf-8")
    assert _cli(str(tmp_path)).returncode == 0                                      # CLEAN
    (tmp_path / "scripts" / "b.py").write_text("def check_b(:\n", encoding="utf-8")
    proc = _cli(str(tmp_path), "--json")
    assert proc.returncode == 2 and json.loads(proc.stdout)["verdict"] == "INCONCLUSIVE"


def test_unchecked_never_reads_clean(tmp_path):
    """A missing scan dir, a missing path, an unreadable baseline: INCONCLUSIVE (2), never CLEAN."""
    (tmp_path / "scripts").mkdir()
    assert gcf.scan(tmp_path)["verdict"] == "INCONCLUSIVE"                          # harness/ missing
    assert _cli(str(tmp_path / "nope")).returncode == 2
    _tree(tmp_path, {})
    assert _cli(str(tmp_path), "--baseline", str(tmp_path / "absent.json")).returncode == 2


def test_a_real_defect_outranks_an_unparsable_file(tmp_path):
    _tree(tmp_path, {"scripts/a.py": "def check_a():\n    return True\n", "scripts/b.py": "def check_b(:\n"})
    assert gcf.scan(tmp_path)["verdict"] == "DEFECTS-FOUND"


def test_json_carries_the_denominator_and_version(tmp_path):
    _tree(tmp_path, {"scripts/a.py": "def check_a(x):\n    return not x\n"})
    payload = json.loads(_cli(str(tmp_path), "--json").stdout)
    assert payload["functions_checked"] == 1 and payload["files_parsed"] == 1
    assert payload["lint_version"] == gcf.__version__


def test_empty_set_says_so(tmp_path):
    _tree(tmp_path, {})
    proc = _cli(str(tmp_path))
    assert proc.returncode == 0 and "EMPTY SET" in proc.stdout
