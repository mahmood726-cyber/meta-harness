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
