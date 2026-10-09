"""codex v13-04-r1 P2: the pre-screen must refuse a dirty tree and never leave a candidate deleted."""
import importlib.util
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_s = importlib.util.spec_from_file_location("pre", os.path.join(ROOT, "scripts", "v13_04_prescreen.py"))
pre = importlib.util.module_from_spec(_s)
_s.loader.exec_module(pre)


def test_PLANT_a_missing_candidate_deletes_nothing(tmp_path, monkeypatch):
    (tmp_path / "a.txt").write_text("held", encoding="utf-8")
    monkeypatch.setattr(pre, "ROOT", str(tmp_path))
    monkeypatch.setattr(pre, "git", lambda *a: type("R", (), {"stdout": ""})())
    rc, why, after = pre.run_slug("s", ["a.txt", "b.txt"])
    assert rc == 2 and "missing" in why and (tmp_path / "a.txt").exists()


def test_PLANT_a_dirty_tree_is_refused(monkeypatch):
    monkeypatch.setattr(pre, "git", lambda *a: type("R", (), {"stdout": " M notes.txt\n"})())
    with pytest.raises(SystemExit):
        pre.main()
