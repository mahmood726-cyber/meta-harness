import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from harness import honest_ratchet


ROOT = Path(__file__).resolve().parents[1]


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


def _ack(page, lost, new, reason="reviewed replacement"):
    return {"page": page, "lost_sha256": lost["sha256"], "lost_text_prefix": lost["text"][:20],
            "replaced_by_sha256": new["sha256"], "reason": reason, "when_utc": "2026-09-14T20:00:00Z", "by": "Unit Test"}


def test_compare_blocks_follows_a_transitive_acknowledgement_chain():
    """A base several commits back skips intermediate replacements: A -> B and B -> C are each reviewed,
    only C is on the page. Plant (pre-fix): with A -> B and B -> C both signed, the base block A was still
    refused because B is not on the page. Every link must still be a signed acknowledgement."""
    page = "docs/reviews/x/index.html"
    a = honest_ratchet.blocks("<div class='banner'>Gate scorecard: 41 gates ; 29 PLANT_ONLY</div>")[0]
    b = honest_ratchet.blocks("<div class='banner'>Gate scorecard: 41 gates ; 33 PLANT_ONLY</div>")[0]
    c = honest_ratchet.blocks("<div class='banner'>Gate scorecard: 42 gates ; 33 PLANT_ONLY</div>")[0]
    chain = {"acknowledgements": [_ack(page, a, b), _ack(page, b, c)]}
    assert honest_ratchet.compare_blocks([a], [c], chain, page) == []
    # a broken chain (the middle link missing, or unsigned) still refuses
    assert honest_ratchet.compare_blocks([a], [c], {"acknowledgements": [_ack(page, a, b)]}, page) != []
    unsigned = {"acknowledgements": [_ack(page, a, b), dict(_ack(page, b, c), by="")]}
    assert honest_ratchet.compare_blocks([a], [c], unsigned, page) != []
    # a chain on a different page does not carry over
    other = {"acknowledgements": [_ack(page, a, b), _ack("docs/index.html", b, c)]}
    assert honest_ratchet.compare_blocks([a], [c], other, page) != []


def _git(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}  # never a hook's GIT_DIR
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True, env=env)


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


def test_cli_refuses_unresolvable_base_with_target_line():
    with tempfile.TemporaryDirectory(prefix="honest-ratchet-target-", ignore_cleanup_errors=True) as raw:
        repo = Path(raw) / "repo"
        repo.mkdir(parents=True)
        _git(repo, "init")
        _git(repo, "config", "user.email", "test@example.test")
        _git(repo, "config", "user.name", "Test User")
        (repo / "README.md").write_text("base\n", encoding="utf-8", newline="\n")
        _git(repo, "add", "README.md")
        _git(repo, "commit", "-m", "base")

        proc = subprocess.run(
            [sys.executable, "-m", "harness.honest_ratchet", "--base", "no-such-ref"],
            cwd=repo,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    assert proc.returncode == 1
    assert "TARGET honest_ratchet: COULD-NOT-EXECUTE base ref not resolvable: no-such-ref" in proc.stdout
