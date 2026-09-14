import subprocess
import shutil
import uuid
from pathlib import Path

from harness import honest_ratchet


def test_compare_refuses_when_stale_marker_drops():
    reasons = honest_ratchet.compare(
        "<div>STALE — this topic's result is not current.</div>",
        "<div>current</div>",
    )
    assert reasons == ["stale: base count 1, new count 0"]


def test_compare_allows_marker_preserved():
    assert honest_ratchet.compare(
        "<div>STALE — this topic's result is not current.</div>",
        "<div>STALE — this topic's result is not current.</div>",
    ) == []


def test_compare_allows_marker_added():
    assert honest_ratchet.compare(
        "<div>current</div>",
        "<div>STALE — this topic's result is not current.</div>",
    ) == []


def test_compare_refuses_retraction_count_drop():
    reasons = honest_ratchet.compare(
        "<div>RETRACT retracted</div>",
        "<div>RETRACT</div>",
    )
    assert reasons == ["retraction: base count 2, new count 1"]


def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def test_check_refuses_when_working_tree_drops_pinned_identity():
    root = Path.cwd() / ".tmp_honest_ratchet" / uuid.uuid4().hex
    repo = root / "repo"
    try:
        repo.mkdir(parents=True)
        (repo / "docs").mkdir()
        _git(repo, "init")
        _git(repo, "config", "user.email", "test@example.test")
        _git(repo, "config", "user.name", "Test User")
        (repo / "docs" / "index.html").write_text(
            "<html><body>Pinned audit identity</body></html>",
            encoding="utf-8",
        )
        _git(repo, "add", "docs/index.html")
        _git(repo, "commit", "-m", "base")

        (repo / "docs" / "index.html").write_text("<html><body>quiet</body></html>", encoding="utf-8")
        ok, reasons = honest_ratchet.check(repo, "HEAD")
        assert ok is False
        assert reasons == ["docs/index.html: pinned_identity: base count 1, new count 0"]
    finally:
        shutil.rmtree(root.parent, ignore_errors=True)
