from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import fixstate  # noqa: E402
from scripts import render_fix_ledger  # noqa: E402


AUTHOR = "Claude Opus 5 (session author)"
OTHER = "Codex lane plant"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout.strip()


def _write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def _commit(root: Path, message: str) -> str:
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


def _hist(
    status: str,
    *,
    commit: str = "",
    by: str = OTHER,
    evidence: list[str] | None = None,
    reason: str = "",
) -> dict:
    return {
        "status": status,
        "when_utc": "2026-09-14T00:00:00Z",
        "by": by,
        "commit": commit,
        "evidence": evidence or [],
        "reason": reason,
    }


def _entry(
    status: str,
    *,
    kind: str = "fix",
    history: list[dict] | None = None,
    author: str = AUTHOR,
    executable_evidence: dict | None = None,
    authored_against: list[str] | None = None,
    generalized_on: list[str] | None = None,
) -> dict:
    return {
        "finding_id": "PLANT-1",
        "fix_id": "FIX-PLANT-1",
        "title": "plant transition",
        "kind": kind,
        "status": status,
        "author": author,
        "opened_utc": "2026-09-14T00:00:00Z",
        "evidence_dir": "",
        "history": history if history is not None else [_hist(status)],
        "authored_against": authored_against or [],
        "generalized_on": generalized_on or [],
        "executable_evidence": executable_evidence,
    }


def _store(entry: dict) -> dict:
    return {
        "schema_version": 1,
        "statuses": list(fixstate.STATUSES),
        "entries": [entry],
    }


def _write_store(root: Path, store: dict) -> None:
    _write(
        root,
        "registry/fixes.json",
        json.dumps(store, ensure_ascii=False, indent=1) + "\n",
    )


def _render_views(root: Path) -> None:
    render_fix_ledger.render(root)


def _repo_with_baseline(tmp_path: Path, old_entry: dict, *, evidence_in_base: bool = True) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _write(repo, "README.md", "base\n")
    _commit(repo, "initial")
    if evidence_in_base:
        _write(repo, "docs/evidence/proof.txt", "parent proof\n")
    _write_store(repo, _store(old_entry))
    _render_views(repo)
    _commit(repo, "baseline")
    _write(repo, "anchor.txt", "anchor\n")
    _commit(repo, "anchor")
    return repo


def _check(repo: Path) -> list[str]:
    ok, reasons = fixstate.check(repo)
    assert not ok
    return reasons


def test_skipped_transition_step_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("REPORTED"))
    head = _git(repo, "rev-parse", "HEAD")
    current = _entry(
        "VERIFIED",
        history=[
            _hist("REPORTED"),
            _hist("VERIFIED", commit=head, evidence=["docs/evidence/proof.txt"]),
        ],
    )
    _write_store(repo, _store(current))
    _render_views(repo)

    reasons = _check(repo)

    assert any("invalid status transition REPORTED->VERIFIED" in r for r in reasons)


def test_downgrade_to_reported_without_reason_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(
        tmp_path,
        _entry(
            "VERIFIED",
            history=[
                _hist("LANDED", commit="HEAD"),
                _hist("VERIFIED", commit="HEAD", evidence=["docs/evidence/proof.txt"]),
            ],
        ),
    )
    current = _entry(
        "REPORTED",
        history=[
            _hist("LANDED", commit="HEAD"),
            _hist("VERIFIED", commit="HEAD", evidence=["docs/evidence/proof.txt"]),
            _hist("REPORTED", reason=""),
        ],
    )
    _write_store(repo, _store(current))
    _render_views(repo)

    reasons = _check(repo)

    assert any("downgrade to REPORTED needs a reason" in r for r in reasons)


def test_landed_control_without_executable_evidence_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("SPECIFIED", kind="control"))
    head = _git(repo, "rev-parse", "HEAD")
    current = _entry(
        "LANDED",
        kind="control",
        history=[_hist("SPECIFIED"), _hist("LANDED", commit=head)],
        executable_evidence=None,
    )
    _write_store(repo, _store(current))
    _render_views(repo)

    reasons = _check(repo)

    assert any("control LANDED needs executable_evidence" in r for r in reasons)


def test_landed_control_with_failing_executable_evidence_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("SPECIFIED", kind="control"))
    head = _git(repo, "rev-parse", "HEAD")
    current = _entry(
        "LANDED",
        kind="control",
        history=[_hist("SPECIFIED"), _hist("LANDED", commit=head)],
        executable_evidence={
            "command": f"{sys.executable} -c \"print('NOPE')\"",
            "expected_substring": "OK",
        },
    )
    _write_store(repo, _store(current))
    _render_views(repo)

    reasons = _check(repo)

    assert any("missing expected substring" in r for r in reasons)


def test_verified_by_the_author_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("LANDED", history=[_hist("LANDED", commit="HEAD")]))
    head = _git(repo, "rev-parse", "HEAD")
    current = _entry(
        "VERIFIED",
        history=[
            _hist("LANDED", commit=head),
            _hist("VERIFIED", commit=head, by=AUTHOR, evidence=["docs/evidence/proof.txt"]),
        ],
    )
    _write_store(repo, _store(current))
    _render_views(repo)

    reasons = _check(repo)

    assert any("VERIFIED by must differ from author" in r for r in reasons)


def test_verified_evidence_created_in_same_commit_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("LANDED", history=[_hist("LANDED", commit="HEAD")]), evidence_in_base=False)
    _write(repo, "docs/evidence/proof.txt", "same commit proof\n")
    same_commit = _commit(repo, "add proof")
    current = _entry(
        "VERIFIED",
        history=[
            _hist("LANDED", commit=same_commit),
            _hist("VERIFIED", commit=same_commit, evidence=["docs/evidence/proof.txt"]),
        ],
    )
    _write_store(repo, _store(current))
    _render_views(repo)

    reasons = _check(repo)

    assert any("did not exist in parent tree" in r for r in reasons)


def test_generalized_overlap_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("VERIFIED", history=[_hist("LANDED", commit="HEAD"), _hist("VERIFIED", commit="HEAD", evidence=["docs/evidence/proof.txt"])]))
    head = _git(repo, "rev-parse", "HEAD")
    current = _entry(
        "GENERALIZED",
        history=[
            _hist("LANDED", commit=head),
            _hist("VERIFIED", commit=head, evidence=["docs/evidence/proof.txt"]),
            _hist("GENERALIZED", commit=head),
        ],
        authored_against=["topic-a", "topic-b"],
        generalized_on=["topic-b", "topic-c"],
    )
    _write_store(repo, _store(current))
    _render_views(repo)

    reasons = _check(repo)

    assert any("overlaps generalized_on" in r for r in reasons)


def test_status_edited_without_history_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("REPORTED"))
    current = _entry("LANDED", history=[_hist("REPORTED")])
    _write_store(repo, _store(current))
    _render_views(repo)

    reasons = _check(repo)

    assert any("without matching new history entry" in r for r in reasons)


def test_stale_view_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("REPORTED"))
    _write(repo, "docs/fix_ledger.json", '{"fixes":[]}\n')

    reasons = _check(repo)

    assert any("docs/fix_ledger.json is stale" in r for r in reasons)


def test_real_store_validates() -> None:
    ok, reasons = fixstate.check(ROOT)

    assert ok, "\n".join(reasons)
