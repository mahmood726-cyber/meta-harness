import json
import os
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import heldout  # noqa: E402


KEY = "k" * 32
IDENTIFIER = "zz-plant-alpha-beta-gamma"
SHORT_FORM = "zz-plant"


def _git(root, *args):
    # never inherit a hook's GIT_DIR / GIT_INDEX_FILE / GIT_WORK_TREE: under a commit hook this `git init` + `git config`
    # re-initialised the LIVE repository (a lane clone: core.bare=true + this identity, 4 Oct 2026;
    # plant tests/test_git_env_never_reaches_a_live_repo.py)
    return subprocess.run(
        ["git", *args],
        cwd=root,
        env={k: v for k, v in os.environ.items() if not k.startswith("GIT_")},
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout.strip()


def _init_repo(root):
    _git(root, "init")
    _git(root, "config", "user.name", "Heldout Test")
    _git(root, "config", "user.email", "heldout@example.test")


def _write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def _commit(root, message):
    _git(root, "add", "-A")
    _git(root, "commit", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _token(identifier):
    return heldout.hmac_token(KEY, identifier)


def _registry(*tokens, enforced_since=None):
    return {
        "version": 1,
        "tokens": list(tokens),
        "enforced_since": enforced_since,
    }


def _registry_with_canary(*tokens, enforced_since=None):
    return _registry(heldout.canary_token(KEY), *tokens, enforced_since=enforced_since)


@contextmanager
def _temp_repo():
    with tempfile.TemporaryDirectory(prefix="heldout-test-", ignore_cleanup_errors=True) as raw:
        root = Path(raw)
        _init_repo(root)
        yield root


def test_tracked_file_hit_reports_hmac_without_plaintext(monkeypatch):
    monkeypatch.setenv("HELDOUT_KEY", KEY)
    sealed = _token(IDENTIFIER)
    registry = _registry_with_canary(sealed, enforced_since=None)
    with _temp_repo() as repo:
        _write(repo, "registry/heldout_sealed.json", json.dumps(registry))
        _write(repo, "notes/plant.txt", f"candidate {IDENTIFIER}\n")
        _commit(repo, "initial clean fixture")

        hits = heldout.scan_tree(repo, KEY, registry)
        ok, reasons = heldout.check(repo)

    assert hits == [{"path": "notes/plant.txt", "identifier_hmac": sealed, "line_no": 1}]
    assert ok is False
    report = "\n".join(reasons)
    assert sealed[:12] in report
    assert IDENTIFIER not in report
    assert "plant-alpha" not in report



def test_sealed_registry_metadata_is_scanned_after_commit(monkeypatch):
    """A sealed slug in registry metadata must not bypass the tree detector."""
    monkeypatch.setenv("HELDOUT_KEY", KEY)
    sealed = _token(IDENTIFIER)
    registry = _registry_with_canary(sealed)
    registry["_doc"] = f"synthetic held-out name: {IDENTIFIER}"
    with _temp_repo() as repo:
        _write(repo, "registry/heldout_sealed.json", json.dumps(registry))
        _commit(repo, "safe registry fixture message")
        hits = heldout.scan_tree(repo, KEY, registry)
        ok, reasons = heldout.check(repo)
    assert hits == [
        {"path": "registry/heldout_sealed.json", "identifier_hmac": sealed, "line_no": 1}
    ]
    assert ok is False
    report = "\\n".join(reasons)
    assert sealed[:12] in report
    assert IDENTIFIER not in report


def test_sealed_staged_registry_metadata_refuses_even_with_clean_worktree(monkeypatch):
    """A staged private name cannot be hidden by restoring the worktree copy."""
    monkeypatch.setenv("HELDOUT_KEY", KEY)
    sealed = _token(IDENTIFIER)
    clean = _registry_with_canary(sealed)
    leaked = dict(clean, _doc=f"synthetic held-out name: {IDENTIFIER}")
    with _temp_repo() as repo:
        _write(repo, "registry/heldout_sealed.json", json.dumps(clean))
        _commit(repo, "safe registry baseline")
        _write(repo, "registry/heldout_sealed.json", json.dumps(leaked))
        _git(repo, "add", "registry/heldout_sealed.json")
        _write(repo, "registry/heldout_sealed.json", json.dumps(clean))
        assert heldout.scan_tree(repo, KEY, clean) == []
        hits = heldout.scan_staged_index(repo, KEY, clean)
        ok, reasons = heldout.check(repo)
    assert hits == [
        {"path": "registry/heldout_sealed.json", "identifier_hmac": sealed, "line_no": 1}
    ]
    assert ok is False
    report = "\\n".join(reasons)
    assert "staged index blob" in report
    assert IDENTIFIER not in report


def test_clean_sealed_registry_remains_accepted(monkeypatch):
    """HMAC-only registry entries are safe; refusal is limited to plaintext leaks."""
    monkeypatch.setenv("HELDOUT_KEY", KEY)
    registry = _registry_with_canary(_token(IDENTIFIER))
    with _temp_repo() as repo:
        _write(repo, "registry/heldout_sealed.json", json.dumps(registry))
        _commit(repo, "safe HMAC-only registry")
        assert heldout.scan_tree(repo, KEY, registry) == []
        assert heldout.scan_staged_index(repo, KEY, registry) == []
        ok, reasons = heldout.check(repo)
    assert ok is True and reasons == []


def test_staged_index_catches_sealed_identifier_hidden_by_clean_worktree(monkeypatch):
    """A pre-commit hook must examine the staged bytes, not just the current file."""
    monkeypatch.setenv("HELDOUT_KEY", KEY)
    sealed = _token(IDENTIFIER)
    registry = _registry_with_canary(sealed)
    with _temp_repo() as repo:
        _write(repo, "registry/heldout_sealed.json", json.dumps(registry))
        _write(repo, "notes/probe.txt", "safe text\n")
        _commit(repo, "clean initial files")
        _write(repo, "notes/probe.txt", IDENTIFIER + "\n")
        _git(repo, "add", "notes/probe.txt")
        _write(repo, "notes/probe.txt", "safe text\n")

        assert heldout.scan_tree(repo, KEY, registry) == []
        hits = heldout.scan_staged_index(repo, KEY, registry)
        ok, reasons = heldout.check(repo)

    assert hits == [{"path": "notes/probe.txt", "identifier_hmac": sealed, "line_no": 1}]
    assert ok is False
    assert any("staged index blob" in reason and sealed[:12] in reason for reason in reasons)
    assert IDENTIFIER not in "\n".join(reasons)


def test_staged_index_reads_added_file_even_if_worktree_file_deleted():
    sealed = _token(IDENTIFIER)
    registry = _registry(sealed)
    with _temp_repo() as repo:
        _write(repo, "base.txt", "safe\n")
        _commit(repo, "initial")
        probe = _write(repo, "notes/staged.txt", IDENTIFIER + "\n")
        _git(repo, "add", "notes/staged.txt")
        probe.unlink()

        assert heldout.scan_tree(repo, KEY, registry) == []
        hits = heldout.scan_staged_index(repo, KEY, registry)

    assert hits == [{"path": "notes/staged.txt", "identifier_hmac": sealed, "line_no": 1}]


def test_staged_path_only_refuses_without_disclosing_identifier(monkeypatch):
    """Staged filename disclosures must be refused without printing sealed names."""
    monkeypatch.setenv("HELDOUT_KEY", KEY)
    sealed = _token(IDENTIFIER)
    registry = _registry_with_canary(sealed)
    with _temp_repo() as repo:
        _write(repo, "registry/heldout_sealed.json", json.dumps(registry))
        _write(repo, "base.txt", "safe\n")
        _commit(repo, "clean baseline")
        path = f"notes/prefix-{IDENTIFIER}-suffix.txt"
        _write(repo, path, "safe\n")
        _git(repo, "add", path)
        hits = heldout.scan_staged_index(repo, KEY, registry)
        ok, reasons = heldout.check(repo)

    assert hits == [{"kind": "staged_path", "identifier_hmac": sealed}]
    assert not ok
    report = "\n".join(reasons)
    assert "staged path" in report and sealed[:12] in report
    assert IDENTIFIER not in report and path not in report


def test_tracked_filename_is_refused_in_clean_ci_checkout(monkeypatch):
    """The staged-only scan is empty after commit, but the tracked name is still sealed."""
    monkeypatch.setenv("HELDOUT_KEY", KEY)
    sealed = _token(IDENTIFIER)
    registry = _registry_with_canary(sealed)
    with _temp_repo() as repo:
        _write(repo, "registry/heldout_sealed.json", json.dumps(registry))
        path = f"notes/prefix-{IDENTIFIER}-suffix.txt"
        _write(repo, path, "safe contents\n")
        _commit(repo, "safe contents only")
        assert heldout.scan_staged_index(repo, KEY, registry) == []
        assert heldout.scan_tree(repo, KEY, registry) == []
        hits = heldout.scan_tracked_filenames(repo, KEY, registry)
        ok, reasons = heldout.check(repo)
    assert hits == [{"kind": "tracked_path", "identifier_hmac": sealed}]
    assert not ok
    report = "\n".join(reasons)
    assert "tracked filename" in report and sealed[:12] in report
    assert IDENTIFIER not in report and path not in report


@pytest.mark.parametrize("payload", [IDENTIFIER + "\\n", "clean contents\\n"])
def test_missing_tracked_worktree_file_refuses_even_without_a_staged_change(monkeypatch, payload):
    """A missing tracked file is still part of HEAD; a tree-scan skip is unsafe."""
    monkeypatch.setenv("HELDOUT_KEY", KEY)
    registry = _registry_with_canary(_token(IDENTIFIER))
    with _temp_repo() as repo:
        _write(repo, "registry/heldout_sealed.json", json.dumps(registry))
        tracked = _write(repo, "notes/tracked.txt", payload)
        _commit(repo, "clean tracked baseline")
        tracked.unlink()  # unstaged deletion; Git still lists the committed path
        assert _git(repo, "diff", "--cached", "--name-only") == ""
        assert heldout.scan_staged_index(repo, KEY, registry) == []
        with pytest.raises(RuntimeError, match="tracked file unreadable"):
            heldout.scan_tree(repo, KEY, registry)
        ok, reasons = heldout.check(repo)
    report = "\\n".join(reasons)
    assert ok is False
    assert "tracked file unreadable" in report
    assert "notes/tracked.txt" not in report and IDENTIFIER not in report


def test_tracked_file_permission_error_refuses_without_path_disclosure(monkeypatch):
    """A read denial is a refusal, not a clean tree; diagnostics redact paths."""
    import builtins

    registry = _registry(_token(IDENTIFIER))
    with _temp_repo() as repo:
        _write(repo, "notes/tracked.txt", "clean\\n")
        _commit(repo, "clean baseline")
        denied = str(repo / "notes" / "tracked.txt")
        original_open = builtins.open

        def deny_selected(path, *args, **kwargs):
            if os.fspath(path) == denied:
                raise PermissionError("synthetic access denied: " + denied)
            return original_open(path, *args, **kwargs)

        monkeypatch.setattr(builtins, "open", deny_selected)
        with pytest.raises(RuntimeError, match="tracked file unreadable") as err:
            heldout.scan_tree(repo, KEY, registry)
        assert denied not in str(err.value)
        assert "notes/tracked.txt" not in str(err.value)


def test_tracked_unicode_filename_content_is_scanned_after_commit():
    """Git C-quotes non-ASCII names in text ls-files; NUL paths must be decoded."""
    sealed = _token(IDENTIFIER)
    registry = _registry(sealed)
    with _temp_repo() as repo:
        path = "notes/café.txt"
        _write(repo, path, f"record {IDENTIFIER}\n")
        _commit(repo, "safe fixture")
        assert heldout.scan_staged_index(repo, KEY, registry) == []
        hits = heldout.scan_tree(repo, KEY, registry)
    assert hits == [{"path": path, "identifier_hmac": sealed, "line_no": 1}]


def test_sealed_tracked_filename_plus_content_never_leaks_path(monkeypatch):
    """A content hit must not undo the tracked-path HMAC redaction."""
    monkeypatch.setenv("HELDOUT_KEY", KEY)
    sealed = _token(IDENTIFIER)
    registry = _registry_with_canary(sealed)
    with _temp_repo() as repo:
        _write(repo, "registry/heldout_sealed.json", json.dumps(registry))
        path = f"notes/{IDENTIFIER}.txt"
        _write(repo, path, f"record {IDENTIFIER}\n")
        _commit(repo, "safe fixture")
        hits = heldout.scan_tree(repo, KEY, registry)
        ok, reasons = heldout.check(repo)
    assert hits == [{"path": "<redacted tracked path>", "identifier_hmac": sealed, "line_no": 1}]
    assert not ok
    report = "\n".join(reasons)
    assert sealed[:12] in report
    assert IDENTIFIER not in report and path not in report


def test_committed_symlink_target_is_scanned_without_following_external_file(monkeypatch):
    """Committed symlink bytes may be sealed even when the external content is clean."""
    monkeypatch.setenv("HELDOUT_KEY", KEY)
    outside_identifier = "unrelated-external-secret"
    sealed_target = _token(IDENTIFIER)
    sealed_outside = _token(outside_identifier)
    registry = _registry_with_canary(sealed_target, sealed_outside)
    with tempfile.TemporaryDirectory(prefix="heldout-link-outside-") as scratch:
        outside = Path(scratch) / f"external-{IDENTIFIER}.txt"
        outside.write_text(outside_identifier + "\\n", encoding="utf-8")
        with _temp_repo() as repo:
            _write(repo, "registry/heldout_sealed.json", json.dumps(registry))
            (repo / "link.txt").symlink_to(outside)
            _commit(repo, "clean symlink fixture")
            assert heldout.scan_staged_index(repo, KEY, registry) == []
            hits = heldout.scan_tree(repo, KEY, registry)
            ok, reasons = heldout.check(repo)

    assert hits == [{"path": "link.txt", "identifier_hmac": sealed_target, "line_no": 1}]
    assert ok is False
    report = "\\n".join(reasons)
    assert sealed_target[:12] in report
    assert sealed_outside[:12] not in report
    assert IDENTIFIER not in report
    assert outside_identifier not in report


def test_clean_committed_symlink_stays_clean():
    """Ordinary in-repository symlink targets remain an accepted positive control."""
    registry = _registry(_token(IDENTIFIER))
    with _temp_repo() as repo:
        _write(repo, "notes/safe.txt", "safe content\\n")
        (repo / "link.txt").symlink_to("notes/safe.txt")
        _commit(repo, "clean symlink fixture")
        assert heldout.scan_tree(repo, KEY, registry) == []


def test_short_form_hit_is_detected_in_tracked_file():
    sealed = _token(SHORT_FORM)
    registry = _registry(sealed)
    with _temp_repo() as repo:
        _write(repo, "scripts/search_probe.py", f"TARGET = '{SHORT_FORM}'\n")
        _commit(repo, "initial clean fixture")

        hits = heldout.scan_tree(repo, KEY, registry)

    assert hits == [{"path": "scripts/search_probe.py", "identifier_hmac": sealed, "line_no": 1}]


def test_commit_scan_only_reports_messages_after_enforcement():
    sealed = _token(IDENTIFIER)
    with _temp_repo() as repo:
        _write(repo, "notes.txt", "start\n")
        _commit(repo, "initial clean fixture")
        _write(repo, "notes.txt", "before\n")
        before = _commit(repo, f"mention {IDENTIFIER} before enforcement")
        _write(repo, "notes.txt", "after\n")
        after = _commit(repo, f"mention {IDENTIFIER} after enforcement")

        hits = heldout.scan_commit_messages(repo, KEY, _registry(sealed, enforced_since=before))
        before_hits = heldout.scan_commit_messages(repo, KEY, _registry(sealed, enforced_since=after))

    assert hits == [{"sha": after, "identifier_hmac": sealed}]
    assert before_hits == []



def test_merge_second_parent_commit_message_is_checked_after_enforcement():
    """An innocuous merge message must not hide a sealed side-branch commit."""
    sealed = _token(IDENTIFIER)
    with _temp_repo() as repo:
        _write(repo, "base.txt", "baseline\\n")
        enforced_since = _commit(repo, "clean baseline")
        original_branch = _git(repo, "branch", "--show-current")
        _git(repo, "checkout", "-b", "synthetic-side-branch")
        _write(repo, "side.txt", "safe body\\n")
        side_sha = _commit(repo, f"side-branch mentions {IDENTIFIER}")
        _git(repo, "checkout", original_branch)
        _git(repo, "merge", "--no-ff", "-m", "clean merge message", "synthetic-side-branch")
        hits = heldout.scan_commit_messages(
            repo, KEY, _registry(sealed, enforced_since=enforced_since)
        )
    assert hits == [{"sha": side_sha, "identifier_hmac": sealed}]




def test_self_test_requires_sealed_canary_and_passes_when_present():
    ok, detail = heldout.self_test(KEY, _registry())
    assert ok is False
    assert "canary not sealed" in detail

    ok, detail = heldout.self_test(KEY, _registry(heldout.canary_token(KEY)))
    assert ok is True
    assert "scan_tree" in detail


def test_check_fails_closed_when_key_is_missing(monkeypatch):
    with tempfile.TemporaryDirectory(prefix="heldout-nokey-", ignore_cleanup_errors=True) as raw:
        root = Path(raw)
        monkeypatch.delenv("HELDOUT_KEY", raising=False)
        monkeypatch.setattr(heldout, "KEY_FILE", str(root / "missing.key"))

        ok, reasons = heldout.check(root)

    assert ok is False
    assert reasons == [heldout.MISSING_KEY_REASON]


def test_candidate_identifiers_extracts_slug_from_paths():
    text = "see topics/zz-plant-alpha.json and docs/reviews/zz-plant-alpha/"

    assert "zz-plant-alpha" in set(heldout.candidate_identifiers(text))


def test_seven_component_sealed_slug_is_detected_inside_longer_path():
    """A path-embedded seven-part topic must not evade six-window HMAC matching."""
    identifier = "alpha-bravo-charlie-delta-echo-foxtrot-golf"
    evidence = f"topics/prefix-{identifier}-suffix.json"
    sealed = _token(identifier)
    registry = _registry_with_canary(sealed)

    assert identifier in set(heldout.candidate_identifiers(evidence))
    assert heldout._matching_hmacs(evidence, KEY, registry) == [sealed]
    assert heldout._Matcher(KEY, registry)(evidence) == [sealed]
    assert heldout.check_message(f"reported prefix-{identifier}-suffix", KEY, registry) == [sealed]

    with _temp_repo() as repo:
        _write(repo, "notes/evidence.txt", evidence + "\n")
        _commit(repo, "synthetic held-out path-slug regression")
        hits = heldout.scan_tree(repo, KEY, registry)
    assert hits == [{"path": "notes/evidence.txt", "identifier_hmac": sealed, "line_no": 1}]


def test_seven_component_sealed_tracked_filename_refuses_without_plaintext(monkeypatch):
    """Long sealed topic in an otherwise clean committed filename must refuse."""
    monkeypatch.setenv("HELDOUT_KEY", KEY)
    identifier = "alpha-bravo-charlie-delta-echo-foxtrot-golf"
    sealed = _token(identifier)
    registry = _registry_with_canary(sealed)
    name = f"notes/prefix-{identifier}-suffix.txt"
    with _temp_repo() as repo:
        _write(repo, "registry/heldout_sealed.json", json.dumps(registry))
        _write(repo, name, "safe body\n")
        _commit(repo, "synthetic clean filename contents")
        hits = heldout.scan_tracked_filenames(repo, KEY, registry)
        ok, reasons = heldout.check(repo)
    assert hits == [{"kind": "tracked_path", "identifier_hmac": sealed}]
    assert ok is False
    report = "\n".join(reasons)
    assert "tracked filename" in report
    assert identifier not in report and name not in report


def test_extreme_hyphen_chain_refuses_instead_of_truncating(monkeypatch):
    """Resource limits must cause a real fail-closed check, not a false pass."""
    oversized = "-".join(f"part{i}" for i in range(heldout.MAX_HYPHEN_COMPONENTS + 1))
    with pytest.raises(ValueError, match="held-out scan refused"):
        list(heldout.candidate_identifiers(oversized))
    monkeypatch.setenv("HELDOUT_KEY", KEY)
    registry = _registry_with_canary()
    with _temp_repo() as repo:
        _write(repo, "registry/heldout_sealed.json", json.dumps(registry))
        _write(repo, "notes/oversized.txt", oversized + "\n")
        _commit(repo, "synthetic overlong-chain refusal")
        ok, reasons = heldout.check(repo)
    assert ok is False
    assert any("hyphenated run has" in reason for reason in reasons)


def test_real_registry_loads_and_self_test_passes_when_key_available():
    registry = heldout.load(ROOT)

    assert isinstance(registry.get("tokens"), list)
    key = heldout.load_key(ROOT)
    if key is None:
        pytest.skip("held-out key not available; real-registry self_test skipped")
    ok, detail = heldout.self_test(key, registry)
    assert ok is True, detail


def test_matcher_equals_the_per_line_scan():
    """The cached whole-scan matcher must return exactly what the per-line _matching_hmacs returns (2026-10-02:
    the held-out limb took 7-10 min in CI rebuilding the keyed HMAC for every identifier on every line)."""
    import hashlib as _h
    import hmac as _hm
    from harness import heldout as H
    key = "matcher-equivalence-key"
    lines = ["the dapagliflozin-hfpef-hosp page cites PMID 12345678 and nct01035255",
             "a-b-c-d-e-f-g-h hyphen windows; Mixed-CASE-Slug repeated: mixed-case-slug",
             "", "no identifiers ??? ..", "x" * 2, "dapagliflozin-hfpef-hosp again on another line"]
    planted = ["hfpef-hosp", "12345678", "c-d-e-f-g-h", "mixed-case-slug"]
    reg = {"tokens": [_hm.new(key.encode(), p.encode(), _h.sha256).hexdigest() for p in planted] + ["0" * 64]}
    m = H._Matcher(key, reg)
    for line in lines:
        assert m(line) == H._matching_hmacs(line, key, reg), line
    assert any(m(line) for line in lines), "plant did not fire: no planted identifier was found"
    assert H._Matcher(key, {"tokens": []})(lines[0]) == []
