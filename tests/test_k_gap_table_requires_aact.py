"""Plant: k_gap_table refuses to run when harness.aact finds no snapshot. Without it the acronym identity routes resolve
nothing and every trial they would have identified silently becomes UNRESOLVED (6 Oct worker run, AACT_DIR unset:
glp1 EXSCEL, empagliflozin EMPEROR-Preserved lost their identities; the regen still reported a fixed point)."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]


def test_no_snapshot_refuses(monkeypatch):
    import k_gap_table as k
    from harness import aact
    monkeypatch.setattr(aact, "snapshot_dir", lambda root=None: None)
    with pytest.raises(SystemExit, match="no AACT snapshot"):
        k.main(["--offline", "--no-write"])


def test_a_snapshot_without_studies_refuses(monkeypatch, tmp_path):
    import k_gap_table as k
    from harness import aact
    monkeypatch.setattr(aact, "snapshot_dir", lambda root=None: str(tmp_path))
    with pytest.raises(SystemExit, match="no AACT snapshot"):
        k.require_aact_snapshot()
