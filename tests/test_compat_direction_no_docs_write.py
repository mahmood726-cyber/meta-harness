"""A test must not write into docs/ (the served tree).

tests/test_compat_direction.py used to run scripts/compat_direction_sweep.py, which rewrote
docs/compat_direction_sweep.json in place -- and in text mode, so on Windows every "\n" became
"\r\n". The content was identical after normalisation but the working-tree bytes were not: the
next `git add docs` could stage it and anything hashing working-tree bytes saw a difference.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_SWEEP = ROOT / "docs" / "compat_direction_sweep.json"


def _docs_porcelain() -> str:
    return subprocess.check_output(
        ["git", "status", "--porcelain", "--", "docs/"], cwd=ROOT, text=True, encoding="utf-8"
    )


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_compat_direction_tests_leave_docs_untouched():
    porcelain_before = _docs_porcelain()
    sha_before = _sha(DOCS_SWEEP)

    run = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_compat_direction.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert run.returncode == 0, run.stdout[-2000:] + run.stderr[-2000:]
    assert "passed" in run.stdout, run.stdout[-2000:]

    # Bytes, not git's view: git normalises CRLF->LF and can call a rewritten file clean.
    assert _sha(DOCS_SWEEP) == sha_before, "docs/compat_direction_sweep.json bytes changed"
    # On a clean checkout (CI, the hook) porcelain_before is "" so this asserts docs/ stays clean.
    assert _docs_porcelain() == porcelain_before


def test_sweep_writes_lf_bytes_to_requested_path(tmp_path):
    out = tmp_path / "sweep.json"
    subprocess.run(
        [sys.executable, "scripts/compat_direction_sweep.py", "--out", str(out)],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    raw = out.read_bytes()
    assert b"\r" not in raw
    assert raw.endswith(b"}\n")
    assert set(json.loads(raw.decode("utf-8"))["summary"]) == {
        "over_claiming",
        "under_claiming",
        "not_derivable",
    }
