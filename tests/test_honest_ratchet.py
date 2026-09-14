import hashlib
import json
import subprocess
import tempfile
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


def test_compare_refuses_bare_retract_drop_case_insensitive():
    reasons = honest_ratchet.compare(
        "<div>We retract the old claim.</div>",
        "<div>quiet</div>",
    )
    assert any(reason.startswith("retraction:") for reason in reasons)


def test_compare_refuses_search_provenance_phrase_drop():
    reasons = honest_ratchet.compare(
        "<div>Search provenance — not a completed systematic search.</div>",
        "<div>quiet</div>",
    )
    assert reasons == ["search_provenance: base count 2, new count 0"]


def test_blocks_extract_absent_and_banner_text_with_sha256():
    found = honest_ratchet.blocks(
        "<div class='absent'><strong>Search provenance</strong>&nbsp;missing</div>"
        "<div class=\"banner\">Visible <em>warning</em></div>"
    )
    assert found == [
        {
            "cls": "absent",
            "text": "Search provenance missing",
            "sha256": hashlib.sha256(b"Search provenance missing").hexdigest(),
        },
        {
            "cls": "banner",
            "text": "Visible warning",
            "sha256": hashlib.sha256(b"Visible warning").hexdigest(),
        },
    ]


def test_compare_blocks_refuses_lost_unacknowledged_block():
    base = honest_ratchet.blocks("<div class='absent'>Search provenance lost</div>")
    reasons = honest_ratchet.compare_blocks(base, [], {"acknowledgements": []}, "docs/reviews/x/index.html")

    assert len(reasons) == 1
    assert reasons[0].startswith(f"lost absent block {base[0]['sha256']}: Search provenance lost")


def test_compare_blocks_allows_acknowledged_replacement_block():
    base = honest_ratchet.blocks("<div class='absent'>Search provenance lost</div>")
    new = honest_ratchet.blocks("<div class='banner'>Replacement state</div>")
    acknowledgements = {
        "acknowledgements": [
            {
                "page": "docs/reviews/x/index.html",
                "lost_sha256": base[0]["sha256"],
                "lost_text_prefix": "Search provenance",
                "replaced_by_sha256": new[0]["sha256"],
                "reason": "reviewed replacement",
                "when_utc": "2026-09-14T20:00:00Z",
                "by": "Unit Test",
            }
        ]
    }

    assert honest_ratchet.compare_blocks(base, new, acknowledgements, "docs/reviews/x/index.html") == []


def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def test_check_refuses_when_working_tree_drops_pinned_identity():
    with tempfile.TemporaryDirectory(prefix="honest-ratchet-test-", ignore_cleanup_errors=True) as raw:
        repo = Path(raw) / "repo"
        repo.mkdir(parents=True)
        (repo / "docs").mkdir()
        _git(repo, "init")
        _git(repo, "config", "user.email", "test@example.test")
        _git(repo, "config", "user.name", "Test User")
        (repo / "docs" / "ratchet_acknowledgements.json").write_text(
            json.dumps({"_doc": "test acknowledgements", "acknowledgements": []}) + "\n",
            encoding="utf-8",
        )
        (repo / "docs" / "index.html").write_text(
            "<html><body>Pinned audit identity</body></html>",
            encoding="utf-8",
        )
        _git(repo, "add", "docs/index.html", "docs/ratchet_acknowledgements.json")
        _git(repo, "commit", "-m", "base")

        (repo / "docs" / "index.html").write_text("<html><body>quiet</body></html>", encoding="utf-8")
        ok, reasons = honest_ratchet.check(repo, "HEAD")
        assert ok is False
        assert reasons == ["docs/index.html: pinned_identity: base count 1, new count 0"]


def test_check_refuses_when_working_tree_drops_absent_block():
    with tempfile.TemporaryDirectory(prefix="honest-ratchet-test-", ignore_cleanup_errors=True) as raw:
        repo = Path(raw) / "repo"
        repo.mkdir(parents=True)
        (repo / "docs").mkdir()
        _git(repo, "init")
        _git(repo, "config", "user.email", "test@example.test")
        _git(repo, "config", "user.name", "Test User")
        (repo / "docs" / "ratchet_acknowledgements.json").write_text(
            json.dumps({"_doc": "test acknowledgements", "acknowledgements": []}) + "\n",
            encoding="utf-8",
        )
        (repo / "docs" / "index.html").write_text(
            "<html><body><div class='absent'>Search provenance lost block text</div></body></html>",
            encoding="utf-8",
        )
        _git(repo, "add", "docs/index.html", "docs/ratchet_acknowledgements.json")
        _git(repo, "commit", "-m", "base")

        (repo / "docs" / "index.html").write_text("<html><body>quiet</body></html>", encoding="utf-8")
        ok, reasons = honest_ratchet.check(repo, "HEAD")
        assert ok is False
        assert any("lost absent block" in reason for reason in reasons)
        assert any("Search provenance lost block text" in reason for reason in reasons)
