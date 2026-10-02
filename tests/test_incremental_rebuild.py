"""Plants for scripts/incremental_rebuild.py: the planner must call a topic stale when ANY recorded input moves.

A planner that misses a change ships a page built from old inputs while reporting it current -- the failure that
makes an incremental build worse than a slow one. Each plant moves one kind of input in a scratch tree and requires
the planner to name it; the unchanged tree must plan nothing.
"""
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("incremental_rebuild", ROOT / "scripts" / "incremental_rebuild.py")
inc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(inc)


@pytest.fixture
def tree(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".gitattributes").write_text("* text=auto eol=lf\n", encoding="utf-8")
    for slug in ("alpha", "beta"):
        d = tmp_path / "docs" / "reviews" / slug
        d.mkdir(parents=True)
        (d / "review.json").write_text("{}", encoding="utf-8")
        c = tmp_path / "cache" / slug
        c.mkdir(parents=True)
        (c / "records.json").write_text(f'{{"slug": "{slug}"}}', encoding="utf-8")
    (tmp_path / "harness").mkdir()
    (tmp_path / "harness" / "synth.py").write_text("X = 1\n", encoding="utf-8")
    monkeypatch.setattr(inc, "ROOT", tmp_path)
    monkeypatch.setattr(inc, "DEPS", tmp_path / "registry" / "build_deps")
    from harness import gitblob
    inc.DEPS.mkdir(parents=True)
    for slug in ("alpha", "beta"):
        files = [f"cache/{slug}/records.json", "harness/synth.py"]
        shas = gitblob.blob_shas(tmp_path, files)
        (inc.DEPS / f"{slug}.json").write_text(json.dumps({
            "slug": slug, "now": "2026-09-11", "environment": inc.environment(),
            "files": {f: shas[f] for f in files},
            "dirs": {f"cache/{slug}": inc._listing_sha(f"cache/{slug}")},
            "outputs": [f"docs/reviews/{slug}/review.json"]}), encoding="utf-8")
    return tmp_path


def test_an_unchanged_tree_plans_nothing(tree):
    assert inc.plan() == {}


def test_PLANT_a_topic_input_moves_only_that_topic(tree):
    (tree / "cache" / "alpha" / "records.json").write_text('{"slug": "alpha", "moved": 1}', encoding="utf-8")
    st = inc.plan()
    assert set(st) == {"alpha"} and st["alpha"] == ["file cache/alpha/records.json"]


def test_PLANT_shared_code_moves_every_topic(tree):
    (tree / "harness" / "synth.py").write_text("X = 2\n", encoding="utf-8")
    assert set(inc.plan()) == {"alpha", "beta"}


def test_PLANT_a_new_file_in_a_listed_directory_is_a_change(tree):
    (tree / "cache" / "beta" / "ft_123.txt").write_text("held full text", encoding="utf-8")
    assert inc.plan() == {"beta": ["listing cache/beta"]}


def test_PLANT_a_deleted_input_is_a_change(tree):
    (tree / "cache" / "beta" / "records.json").unlink()
    assert "file cache/beta/records.json" in inc.plan()["beta"]


def test_PLANT_missing_map_and_new_environment_rebuild(tree, monkeypatch):
    (inc.DEPS / "alpha.json").unlink()
    assert inc.plan()["alpha"] == ["no dependency map recorded"]
    monkeypatch.setattr(inc, "environment", lambda: {"python": "9.9", "numpy": None, "scipy": None})
    assert inc.plan()["beta"][0].startswith("environment")


def test_a_crlf_checkout_is_not_a_change(tree):
    # identity is git's blob after the clean filter, so a Windows CRLF worktree reads current (harness/gitblob.py)
    (tree / "harness" / "synth.py").write_bytes(b"X = 1\r\n")
    assert inc.plan() == {}
