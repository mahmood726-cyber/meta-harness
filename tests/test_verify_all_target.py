from __future__ import annotations

import subprocess
import sys
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_verify_all_refuses_when_cwd_is_not_git_tree(tmp_path: Path) -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_all.py")],
        cwd=tmp_path,
        env={**os.environ, "GIT_CEILING_DIRECTORIES": str(ROOT)},
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert proc.returncode == 1
    assert "TARGET verify_all: COULD-NOT-EXECUTE" in proc.stdout
    assert "VERIFY-ALL: COULD-NOT-EXECUTE" in proc.stdout
