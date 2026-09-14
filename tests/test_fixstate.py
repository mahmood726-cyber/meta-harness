import json
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import fixstate  # noqa: E402


def _git(root, *args):
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout.strip()


def _write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _commit(root, message):
    _git(root, "add", "-A")
    _git(
        root,
        "-c",
        "user.name=FixState Test",
        "-c",
        "user.email=fixstate@example.test",
        "commit",
        "-m",
        message,
    )
    return _git(root, "rev-parse", "HEAD")


@contextmanager
def _temp_repo():
    with tempfile.TemporaryDirectory(prefix="fixstate-test-", dir=ROOT) as raw:
        root = Path(raw)
        _git(root, "init")
        yield root


def test_no_fix_state_trailer_refused():
    reasons = fixstate.check_message("ordinary subject\n\nbody\n")

    assert any("exactly one Fix-State" in reason for reason in reasons)


def test_two_fix_state_trailers_refused():
    reasons = fixstate.check_message(
        "subject\n\nFix-State: REPORTED\nFix-State: LANDED\n"
    )

    assert any("found 2" in reason for reason in reasons)


def test_not_a_fix_cannot_have_fix_subject():
    reasons = fixstate.check_message("fix the gate\n\nFix-State: NOT-A-FIX\n")

    assert "this message asserts a fix; state it" in reasons


def test_verified_evidence_must_exist_in_parent_not_same_commit():
    with _temp_repo() as repo:
        _write(repo, "notes.txt", "base\n")
        base = _commit(repo, "base\n\nFix-State: LANDED")
        _write(repo, "evidence/proof.txt", "same commit proof\n")
        bad = _commit(
            repo,
            "claim verified\n\n"
            "Fix-State: VERIFIED\n"
            "Fix-Evidence: evidence/proof.txt\n"
            "Fix-Verified-By: independent replay\n",
        )

        hits = fixstate.scan_commits(repo, {"enforced_since": base})

    assert hits and hits[0]["sha"] == bad
    assert any("did not exist in parent tree" in v for v in hits[0]["violations"])


def test_verified_evidence_in_parent_with_verifier_passes():
    with _temp_repo() as repo:
        _write(repo, "evidence/proof.txt", "parent proof\n")
        base = _commit(repo, "base\n\nFix-State: LANDED")
        _write(repo, "notes.txt", "landing\n")
        _commit(
            repo,
            "claim verified\n\n"
            "Fix-State: VERIFIED\n"
            "Fix-Evidence: evidence/proof.txt\n"
            "Fix-Verified-By: independent replay\n",
        )

        hits = fixstate.scan_commits(repo, {"enforced_since": base})

    assert hits == []


def test_verified_missing_verified_by_refused():
    with _temp_repo() as repo:
        _write(repo, "evidence/proof.txt", "parent proof\n")
        base = _commit(repo, "base\n\nFix-State: LANDED")
        message = "claim verified\n\nFix-State: VERIFIED\nFix-Evidence: evidence/proof.txt\n"

        reasons = fixstate.check_message(message, root=repo, parent_tree=base)

    assert any("Fix-Verified-By" in reason for reason in reasons)


def test_verified_evidence_path_must_be_repo_relative():
    with _temp_repo() as repo:
        _write(repo, "evidence/proof.txt", "parent proof\n")
        base = _commit(repo, "base\n\nFix-State: LANDED")
        message = (
            "claim verified\n\n"
            "Fix-State: VERIFIED\n"
            "Fix-Evidence: ../outside.txt\n"
            "Fix-Verified-By: independent replay\n"
        )

        reasons = fixstate.check_message(message, root=repo, parent_tree=base)

    assert any("repo-relative" in reason for reason in reasons)


def test_generalized_overlapping_lists_refused():
    with _temp_repo() as repo:
        _write(repo, "evidence/proof.txt", "parent proof\n")
        base = _commit(repo, "base\n\nFix-State: LANDED")
        message = (
            "claim generalized\n\n"
            "Fix-State: GENERALIZED\n"
            "Fix-Evidence: evidence/proof.txt\n"
            "Fix-Verified-By: independent replay\n"
            "Fix-Authored-Against: topic-a, topic-b\n"
            "Fix-Generalized-On: topic-b, topic-c\n"
        )

        reasons = fixstate.check_message(message, root=repo, parent_tree=base)

    assert any("overlap" in reason for reason in reasons)


def test_generalized_disjoint_lists_passes():
    with _temp_repo() as repo:
        _write(repo, "evidence/proof.txt", "parent proof\n")
        base = _commit(repo, "base\n\nFix-State: LANDED")
        message = (
            "claim generalized\n\n"
            "Fix-State: GENERALIZED\n"
            "Fix-Evidence: evidence/proof.txt\n"
            "Fix-Verified-By: independent replay\n"
            "Fix-Authored-Against: topic-a, topic-b\n"
            "Fix-Generalized-On: topic-c, topic-d\n"
        )

        reasons = fixstate.check_message(message, root=repo, parent_tree=base)

    assert reasons == []


def test_landed_alone_passes():
    assert fixstate.check_message("landed state\n\nFix-State: LANDED\n") == []


def test_commit_scan_inert_until_enforced_since_is_set():
    with _temp_repo() as repo:
        _write(repo, "notes.txt", "base\n")
        _commit(repo, "base without trailer")

        hits = fixstate.scan_commits(repo, {"enforced_since": None})

    assert hits == []


def test_check_ledgers_reports_missing_readme_line_and_missing_fix_state():
    with tempfile.TemporaryDirectory(prefix="fixstate-ledger-", dir=ROOT) as raw:
        root = Path(raw)
        _write(root, "docs/evidence/no-state/README.md", "# Evidence\n")
        _write(root, "docs/fix_ledger.json", json.dumps({"fixes": [{"class": "x"}]}))

        reasons = fixstate.check_ledgers(root)

    assert any("missing four-state Fix state line" in reason for reason in reasons)
    assert any("missing valid fix_state" in reason for reason in reasons)


def test_real_ledgers_are_fix_state_clean_after_lane_e_edits():
    assert fixstate.check_ledgers(ROOT) == []
