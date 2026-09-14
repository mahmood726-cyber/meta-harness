import json
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import heldout

SLUG_A = "__heldout_plant_alpha__"
SLUG_B = "zz-plant-topic-beta"


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


def _init_repo(root):
    _git(root, "init")


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
        "user.name=Heldout Test",
        "-c",
        "user.email=heldout@example.test",
        "commit",
        "-m",
        message,
    )
    return _git(root, "rev-parse", "HEAD")


def _registry(slugs=None, enforced_since=None, forbidden_paths=None, allowed_paths=None):
    return {
        "slugs": slugs or [SLUG_A, SLUG_B],
        "enforced_since": enforced_since,
        "forbidden_paths": forbidden_paths
        or [
            "tests/",
            "scripts/search_",
            "harness/acquisition.py",
            "harness/lexicon.py",
        ],
        "allowed_paths": allowed_paths
        or [
            "docs/search_recall_heldout.json",
            "docs/reviews/<slug>/",
            "docs/m/",
            "topics/<slug>.json",
            "protocols/<slug>.md",
            "cache/<slug>/",
            "registry/heldout.json",
        ],
    }


@contextmanager
def _temp_repo():
    with tempfile.TemporaryDirectory(prefix="heldout-test-", dir=ROOT) as raw:
        root = Path(raw)
        _init_repo(root)
        yield root


def test_path_scan_reports_forbidden_slug_and_skips_allowed_slug():
    with _temp_repo() as repo:
        registry = _registry(
            slugs=[SLUG_A],
            forbidden_paths=["tests/", "docs/reviews/"],
            allowed_paths=["docs/reviews/<slug>/", "registry/heldout.json"],
        )
        _write(repo, "tests/test_x.py", f"TARGET = '{SLUG_A}'\n")
        _write(repo, f"docs/reviews/{SLUG_A}/index.html", f"<p>{SLUG_A}</p>\n")
        _commit(repo, "initial clean fixture")

        hits = heldout.scan_paths(repo, registry)

    assert hits == [
        {
            "path": "tests/test_x.py",
            "slug": SLUG_A,
            "line_no": 1,
            "line": f"TARGET = '{SLUG_A}'",
        }
    ]


def test_path_scan_reports_short_form_in_search_script():
    with _temp_repo() as repo:
        registry = _registry(slugs=[SLUG_B], forbidden_paths=["scripts/search_"])
        _write(repo, "scripts/search_rebuild.py", "TARGETS = ['zz-plant']\n")
        _commit(repo, "initial clean fixture")

        hits = heldout.scan_paths(repo, registry)

    assert len(hits) == 1
    assert hits[0]["path"] == "scripts/search_rebuild.py"
    assert hits[0]["slug"] == SLUG_B


def test_commit_scan_only_reports_messages_after_enforcement():
    with _temp_repo() as repo:
        _write(repo, "notes.txt", "start\n")
        _commit(repo, "initial clean fixture")
        _write(repo, "notes.txt", "before\n")
        before = _commit(repo, f"mention {SLUG_A} before enforcement")
        _write(repo, "notes.txt", "after\n")
        after = _commit(repo, f"mention {SLUG_A} after enforcement")

        hits = heldout.scan_commit_messages(repo, _registry(slugs=[SLUG_A], enforced_since=before))

    assert len(hits) == 1
    assert hits[0]["sha"] == after
    assert hits[0]["slug"] == SLUG_A
    assert "after enforcement" in hits[0]["excerpt"]


def test_check_message_reports_slug_and_allows_clean_message():
    with _temp_repo():
        registry = _registry(slugs=[SLUG_B])

        assert heldout.check_message(f"fix {SLUG_B} recall", registry) == [SLUG_B]
        assert heldout.check_message("tighten acquisition replay ledger", registry) == []


def test_measurement_current_enforces_engine_sha_and_history():
    with _temp_repo() as repo:
        _write(repo, "harness/acquisition.py", "\"\"\"contract\"\"\"\n")
        _commit(repo, "initial clean fixture")
        registry = _registry(enforced_since="HEAD")

        ok, detail = heldout.measurement_current(repo, registry)
        assert ok is False
        assert detail == "no published held-out measurement"

        _write(
            repo,
            "docs/search_recall_heldout.json",
            json.dumps({"engine_sha": "stale", "history": [{"engine_sha": "stale"}]}),
        )
        ok, detail = heldout.measurement_current(repo, registry)
        assert ok is False
        assert "engine changed since the published measurement" in detail

        current = _git(repo, "hash-object", "harness/acquisition.py")
        _write(
            repo,
            "docs/search_recall_heldout.json",
            json.dumps({"engine_sha": current, "history": [{"engine_sha": current}]}),
        )
        ok, detail = heldout.measurement_current(repo, registry)
        assert ok is True
        assert detail == "published held-out measurement matches current engine"

        ok, detail = heldout.measurement_current(repo, _registry(enforced_since=None))
        assert ok is True
        assert detail == "not enforced yet"


def test_real_registry_parses_and_current_tree_has_no_forbidden_mentions():
    registry = heldout.load(ROOT)

    assert len(registry["slugs"]) == 5
    hits = heldout.scan_paths(ROOT, registry)
    assert hits == [], f"real registry path violations: {hits}"
