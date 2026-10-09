"""The auditor Markdown generator runs end to end at a commit (it broke silently when #35 removed a page helper it used:
nothing exercised it). Plant: a missing helper or a changed signature fails this test, not the auditor's delivery."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_auditor_md as B  # noqa: E402


def _head():
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()


def _check(tmp_path, commit, live=True):
    lc = {"commit": commit, "checked_utc": "2026-10-09T00:00:00+00:00", "reviews_match": 32, "reviews_n": 32,
          "reviews_with_tab_contract": 32 if live else 0, "audit_status": 200 if live else 404, "audit_match": live, "live": live}
    p = tmp_path / "live_check.json"
    p.write_text(json.dumps(lc), encoding="utf-8")
    return p


def test_generator_builds_every_review_section_at_head(tmp_path):
    head = _head()
    text = B.build(head, head, str(_check(tmp_path, head)))
    n = len(subprocess.run(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", head, "docs/reviews"],
                           capture_output=True, text=True, check=True).stdout.split("/review.json")) - 1
    assert text.count("\n### 2.") == n and n >= 32
    assert "NOT live" not in text and "class **UNKNOWN**" not in text


def test_banner_follows_the_recorded_live_check(tmp_path):
    head = _head()
    assert "The new RapidMeta tab set is NOT live" in B.build(head, head, str(_check(tmp_path, head, live=False)))


def test_a_live_check_of_another_commit_is_refused(tmp_path):
    head = _head()
    import pytest
    with pytest.raises(SystemExit):
        B.build(head, head, str(_check(tmp_path, "0" * 40)))
