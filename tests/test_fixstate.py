from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import fixstate  # noqa: E402
from scripts import render_fix_ledger  # noqa: E402


AUTHOR = "Claude Opus 5 (session author)"
OTHER = "Codex lane plant"
EXTERNAL = "External auditor plant"


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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def _verification(
    root: Path,
    *,
    kind: str = "internal_agent",
    identity: str = OTHER,
    evidence: list[str] | None = None,
    scope: list[str] | None = None,
    commit: str = "HEAD",
) -> dict:
    evidence = evidence or ["docs/evidence/proof.txt"]
    scope = scope or evidence
    return {
        "claim_id": "FIX-PLANT-1",
        "verifier": {"identity": identity, "kind": kind},
        "evidence": [
            {"path": path, "sha256": _sha256(root / path)}
            for path in evidence
            if (root / path).is_file()
        ],
        "architecture_identity": "a" * 64,
        "method": "plant verification",
        "scope": scope,
        "scope_blob_shas": fixstate._scope_blob_shas(root, scope),
        "when_utc": "2026-09-14T00:00:00Z",
        "commit": commit,
    }


def _entry(
    status: str,
    *,
    root: Path | None = None,
    kind: str = "fix",
    history: list[dict] | None = None,
    author: str = AUTHOR,
    executable_evidence: dict | None = None,
    authored_against: list[str] | None = None,
    generalized_on: list[str] | None = None,
    verified_by: dict | None = None,
    verifications: list[dict] | None = None,
) -> dict:
    if verified_by is None:
        verified_by = {"identity": None, "kind": None}
    if verifications is None:
        verifications = []
    if status == "INTERNALLY_VERIFIED" and root is not None and not verifications:
        verifications = [_verification(root)]
        verified_by = {"identity": OTHER, "kind": "internal_agent"}
    if status == "INDEPENDENTLY_VERIFIED" and root is not None and not verifications:
        verifications = [
            _verification(root, kind="external_auditor", identity=EXTERNAL, evidence=[], scope=["scope.txt"])
            | {"evidence": [{"path": "https://example.test/proof", "sha256": "b" * 64}]}
        ]
        verified_by = {"identity": EXTERNAL, "kind": "external_auditor"}
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
        "verified_by": verified_by,
        "verifications": verifications,
        "authored_against": authored_against or [],
        "generalized_on": generalized_on or [],
        "executable_evidence": executable_evidence,
    }


def _store(entry: dict) -> dict:
    return {
        "schema_version": fixstate.SCHEMA_VERSION,
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
    _write(repo, "scope.txt", "scope v1\n")
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


def test_bare_verified_status_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("REPORTED"))
    current = _entry("LANDED", history=[_hist("LANDED", commit="HEAD")])
    current["status"] = "VERIFIED"
    store = _store(current)
    store["statuses"] = list(fixstate.STATUSES) + ["VERIFIED"]

    reasons = fixstate.validate_store(repo, store)

    assert any("refused bare VERIFIED status" in r for r in reasons)


def test_skipped_transition_step_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("REPORTED"))
    head = _git(repo, "rev-parse", "HEAD")
    current = _entry(
        "INTERNALLY_VERIFIED",
        root=repo,
        history=[
            _hist("REPORTED"),
            _hist("INTERNALLY_VERIFIED", commit=head, evidence=["docs/evidence/proof.txt"]),
        ],
    )
    _write_store(repo, _store(current))
    _render_views(repo)

    reasons = _check(repo)

    assert any("invalid status transition REPORTED->INTERNALLY_VERIFIED" in r for r in reasons)


def test_downgrade_to_reported_without_reason_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(
        tmp_path,
        _entry(
            "INTERNALLY_VERIFIED",
            root=tmp_path / "missing-root",
            history=[
                _hist("LANDED", commit="HEAD"),
                _hist("INTERNALLY_VERIFIED", commit="HEAD", evidence=["docs/evidence/proof.txt"]),
            ],
            verified_by={"identity": OTHER, "kind": "internal_agent"},
            verifications=[],
        ),
    )
    current = _entry(
        "REPORTED",
        history=[
            _hist("LANDED", commit="HEAD"),
            _hist("INTERNALLY_VERIFIED", commit="HEAD", evidence=["docs/evidence/proof.txt"]),
            _hist("REPORTED", reason=""),
        ],
    )
    _write_store(repo, _store(current))
    _render_views(repo)

    reasons = _check(repo)

    assert any("downgrade to REPORTED needs a reason" in r for r in reasons)


def test_downgrade_to_reported_requires_detector_or_stale_reason(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("LANDED", history=[_hist("LANDED", commit="HEAD")]))
    current = _entry(
        "REPORTED",
        history=[
            _hist("LANDED", commit="HEAD"),
            _hist("REPORTED", reason="ordinary regression note"),
        ],
    )
    _write_store(repo, _store(current))
    _render_views(repo)

    reasons = _check(repo)

    assert any("downgrade to REPORTED refused" in r for r in reasons)


def test_downgrade_to_reported_allows_detector_miss_reason(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("LANDED", history=[_hist("LANDED", commit="HEAD")]))
    current = _entry(
        "REPORTED",
        history=[
            _hist("LANDED", commit="HEAD"),
            _hist("REPORTED", reason="detector proven to miss the protected property"),
        ],
    )
    _write_store(repo, _store(current))
    _render_views(repo)

    ok, reasons = fixstate.check(repo)

    assert ok, "\n".join(reasons)


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


def test_internally_verified_by_the_author_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("LANDED", history=[_hist("LANDED", commit="HEAD")]))
    head = _git(repo, "rev-parse", "HEAD")
    current = _entry(
        "INTERNALLY_VERIFIED",
        root=repo,
        history=[
            _hist("LANDED", commit=head),
            _hist("INTERNALLY_VERIFIED", commit=head, by=AUTHOR, evidence=["docs/evidence/proof.txt"]),
        ],
        verified_by={"identity": AUTHOR, "kind": "internal_agent"},
        verifications=[_verification(repo, identity=AUTHOR, commit=head)],
    )
    _write_store(repo, _store(current))
    _render_views(repo)

    reasons = _check(repo)

    assert any("INTERNALLY_VERIFIED verifier must differ from author" in r for r in reasons)


def test_independently_verified_with_only_in_tree_evidence_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("INTERNALLY_VERIFIED", root=tmp_path / "missing-root"))
    head = _git(repo, "rev-parse", "HEAD")
    current = _entry(
        "INDEPENDENTLY_VERIFIED",
        root=repo,
        history=[
            _hist("LANDED", commit=head),
            _hist("INTERNALLY_VERIFIED", commit=head, evidence=["docs/evidence/proof.txt"]),
            _hist("INDEPENDENTLY_VERIFIED", commit=head, by=EXTERNAL, evidence=["docs/evidence/proof.txt"]),
        ],
        verified_by={"identity": EXTERNAL, "kind": "external_auditor"},
        verifications=[_verification(repo, kind="external_auditor", identity=EXTERNAL, commit=head)],
    )
    _write_store(repo, _store(current))
    _render_views(repo)

    reasons = _check(repo)

    assert any("needs external evidence outside this repository" in r for r in reasons)


def test_scope_change_is_refused_until_refresh_stale(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("LANDED", history=[_hist("LANDED", commit="HEAD")]))
    head = _git(repo, "rev-parse", "HEAD")
    current = _entry(
        "INTERNALLY_VERIFIED",
        root=repo,
        history=[
            _hist("LANDED", commit=head),
            _hist("INTERNALLY_VERIFIED", commit=head, evidence=["docs/evidence/proof.txt"]),
        ],
        verifications=[_verification(repo, scope=["scope.txt"], commit=head)],
        verified_by={"identity": OTHER, "kind": "internal_agent"},
    )
    _write_store(repo, _store(current))
    _render_views(repo)
    _write(repo, "scope.txt", "scope v2\n")

    reasons = _check(repo)

    assert any("assurance stale: scope.txt changed" in r for r in reasons)

    before = json.loads((repo / "registry/fixes.json").read_text(encoding="utf-8"))
    before_history_len = len(before["entries"][0]["history"])
    proc = subprocess.run(
        [sys.executable, "-m", "harness.fixstate", "--refresh-stale"],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    after = json.loads((repo / "registry/fixes.json").read_text(encoding="utf-8"))
    entry = after["entries"][0]
    assert entry["status"] == "LANDED"
    assert entry["verified_by"] == {"identity": None, "kind": None}
    assert len(entry["history"]) == before_history_len + 1
    assert entry["history"][-1]["reason"] == "assurance stale: scope.txt changed"

    _render_views(repo)
    ok, refresh_reasons = fixstate.check(repo)
    assert ok, "\n".join(refresh_reasons)


def test_generalized_overlap_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_baseline(tmp_path, _entry("INDEPENDENTLY_VERIFIED", root=tmp_path / "missing-root"))
    head = _git(repo, "rev-parse", "HEAD")
    current = _entry(
        "GENERALIZED",
        root=repo,
        history=[
            _hist("LANDED", commit=head),
            _hist("INTERNALLY_VERIFIED", commit=head, evidence=["docs/evidence/proof.txt"]),
            _hist("INDEPENDENTLY_VERIFIED", commit=head, evidence=["docs/evidence/proof.txt"]),
            _hist("GENERALIZED", commit=head),
        ],
        authored_against=["topic-a", "topic-b"],
        generalized_on=["topic-b", "topic-c"],
        verifications=[_verification(repo, commit=head)],
        verified_by={"identity": OTHER, "kind": "internal_agent"},
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
