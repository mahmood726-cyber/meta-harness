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


def _event(
    implementation: str,
    *,
    verification: str = "NONE",
    scope: str = "INSTANCE",
    commit: str = "",
    reason: str = "plant event",
) -> dict:
    return {
        "implementation": implementation,
        "verification": verification,
        "scope": scope,
        "when_utc": "2026-09-14T00:00:00Z",
        "by": OTHER,
        "commit": commit,
        "evidence": [],
        "reason": reason,
    }


def _seal(root: Path, paths: list[str] | None = None) -> dict:
    paths = paths or ["scope.txt"]
    deps = {
        rel: blob
        for rel, blob in fixstate._scope_blob_shas(root, paths).items()
        if isinstance(blob, str)
    }
    return {
        "sealed_utc": "2026-09-14T00:00:00Z",
        "commit": _git(root, "rev-parse", "HEAD"),
        "dependencies": deps,
        "configuration": {"plant": "true"},
    }


def _verification(
    root: Path,
    *,
    claim_id: str = "FIX-PLANT-1",
    kind: str = "internal_agent",
    identity: str = OTHER,
    evidence: list[dict] | None = None,
    scope_paths: list[str] | None = None,
    commit: str | None = None,
) -> dict:
    if evidence is None:
        evidence = [
            {
                "path": "docs/evidence/proof.txt",
                "sha256": _sha256(root / "docs/evidence/proof.txt"),
            }
        ]
    return {
        "claim_id": claim_id,
        "verifier": {"identity": identity, "kind": kind},
        "evidence": evidence,
        "architecture_identity": "a" * 64,
        "method": "plant verification",
        "scope_paths": scope_paths or ["scope.txt"],
        "when_utc": "2026-09-14T00:00:00Z",
        "commit": commit or _git(root, "rev-parse", "HEAD"),
    }


def _entry(
    root: Path,
    *,
    implementation: str = "LANDED",
    verification: str = "NONE",
    scope: str = "INSTANCE",
    kind: str = "fix",
    fix_id: str = "FIX-PLANT-1",
    verified_by: dict | None = None,
    verifications: list[dict] | None = None,
    executable_evidence: dict | None = None,
    seal: dict | None = None,
    author: str = AUTHOR,
) -> dict:
    if verified_by is None:
        verified_by = {"identity": None, "kind": None}
    if verifications is None:
        verifications = []
    if verification == "INTERNAL" and not verifications:
        verified_by = {"identity": OTHER, "kind": "internal_agent"}
        verifications = [_verification(root, claim_id=fix_id)]
    if verification == "INDEPENDENT" and not verifications:
        verified_by = {"identity": EXTERNAL, "kind": "external_auditor"}
        verifications = [
            _verification(
                root,
                claim_id=fix_id,
                kind="external_auditor",
                identity=EXTERNAL,
                evidence=[{"external_record": "github actions run 1", "commit": "abc123"}],
            )
        ]
    return {
        "finding_id": "PLANT-1",
        "fix_id": fix_id,
        "title": "plant transition",
        "kind": kind,
        "implementation": implementation,
        "verification": verification,
        "scope": scope,
        "author": author,
        "opened_utc": "2026-09-14T00:00:00Z",
        "evidence_dir": "",
        "events": [
            _event(
                implementation,
                verification=verification,
                scope=scope,
                commit=_git(root, "rev-parse", "HEAD") if implementation == "LANDED" else "",
            )
        ],
        "verified_by": verified_by,
        "verifications": verifications,
        "authored_against": [],
        "generalized_on": [],
        "executable_evidence": executable_evidence,
        "seal": seal if seal is not None else _seal(root),
    }


def _store(entry: dict) -> dict:
    return {
        "schema_version": fixstate.SCHEMA_VERSION,
        "implementations": list(fixstate.CONTROL_IMPLEMENTATIONS),
        "verification_levels": list(fixstate.VERIFICATIONS),
        "scopes": list(fixstate.SCOPES),
        "freshness": list(fixstate.FRESHNESS),
        "entries": [entry],
    }


def _write_store(root: Path, store: dict) -> None:
    _write(root, "registry/fixes.json", json.dumps(store, ensure_ascii=False, indent=1) + "\n")


def _render_views(root: Path) -> None:
    render_fix_ledger.render(root)


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _write(repo, "README.md", "base\n")
    _write(repo, "scope.txt", "scope v1\n")
    _write(repo, "docs/evidence/proof.txt", "proof\n")
    _commit(repo, "initial")
    return repo


def _reasons(repo: Path, entry: dict) -> list[str]:
    store = _store(entry)
    _write_store(repo, store)
    _render_views(repo)
    ok, reasons = fixstate.check(repo)
    assert not ok
    return reasons


def test_old_status_key_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    entry = _entry(repo)
    entry["status"] = "LANDED"

    reasons = fixstate.validate_store(repo, _store(entry))

    assert any("refused old authority key 'status'" in r for r in reasons)


def test_old_ladder_word_is_refused_anywhere_in_entry(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    entry = _entry(repo)
    entry["events"][0]["reason"] = "VERIFIED"

    reasons = fixstate.validate_store(repo, _store(entry))

    assert any("refused old ladder word 'VERIFIED'" in r for r in reasons)


def test_specified_on_fix_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    entry = _entry(repo, implementation="SPECIFIED")

    reasons = fixstate.validate_store(repo, _store(entry))

    assert any("SPECIFIED is allowed only for controls" in r for r in reasons)


def test_internal_verifier_must_differ_from_author(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    ver = _verification(repo, identity=AUTHOR)
    entry = _entry(
        repo,
        verification="INTERNAL",
        verified_by={"identity": AUTHOR, "kind": "internal_agent"},
        verifications=[ver],
    )

    reasons = _reasons(repo, entry)

    assert any("verification INTERNAL verifier must differ from author" in r for r in reasons)


def test_independent_needs_external_auditor(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    entry = _entry(
        repo,
        verification="INDEPENDENT",
        verified_by={"identity": OTHER, "kind": "internal_agent"},
        verifications=[_verification(repo, kind="internal_agent", identity=OTHER)],
    )

    reasons = _reasons(repo, entry)

    assert any("verification INDEPENDENT needs an external_auditor verification" in r for r in reasons)


def test_independent_needs_external_evidence(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    entry = _entry(
        repo,
        verification="INDEPENDENT",
        verified_by={"identity": EXTERNAL, "kind": "external_auditor"},
        verifications=[_verification(repo, kind="external_auditor", identity=EXTERNAL)],
    )

    reasons = _reasons(repo, entry)

    assert any("verification INDEPENDENT needs external evidence outside this repository" in r for r in reasons)


def test_broad_scope_without_named_topic_list_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    entry = _entry(repo, scope="CORPUS", executable_evidence=None)

    reasons = _reasons(repo, entry)

    assert any("scope CORPUS needs executable_evidence naming the demonstrated topic list" in r for r in reasons)


def test_verified_claim_with_empty_seal_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    empty_seal = {
        "sealed_utc": "2026-09-14T00:00:00Z",
        "commit": _git(repo, "rev-parse", "HEAD"),
        "dependencies": {},
        "configuration": {},
    }
    entry = _entry(repo, verification="INTERNAL", seal=empty_seal)

    reasons = _reasons(repo, entry)

    assert any("needs a non-empty seal" in r for r in reasons)


def test_stored_freshness_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    entry = _entry(repo)
    entry["freshness"] = "CURRENT"

    reasons = fixstate.validate_store(repo, _store(entry))

    assert any("missing keys" not in r and "unexpected keys: freshness" in r for r in reasons)


def test_freshness_is_computed_from_seal(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    entry = _entry(repo, verification="INTERNAL")

    assert fixstate.freshness(entry, repo) == ("CURRENT", [])

    _write(repo, "scope.txt", "scope v2\n")
    state, moved = fixstate.freshness(entry, repo)
    assert state == "STALE"
    assert moved == ["scope.txt"]

    _write(repo, "scope.txt", "scope v1\n")
    assert fixstate.freshness(entry, repo) == ("CURRENT", [])


def test_migration_reencodes_v2_store_and_refuses_second_run(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    head = _git(repo, "rev-parse", "HEAD")
    old_store = {
        "schema_version": 2,
        "statuses": [
            "SPECIFIED",
            "REPORTED",
            "LANDED",
            "INTERNALLY_VERIFIED",
            "INDEPENDENTLY_VERIFIED",
            "GENERALIZED",
        ],
        "entries": [
            {
                "finding_id": "PLANT-OLD",
                "fix_id": "FIX-OLD",
                "title": "old internal plant",
                "kind": "fix",
                "status": "INTERNALLY_VERIFIED",
                "author": AUTHOR,
                "opened_utc": "2026-09-14T00:00:00Z",
                "evidence_dir": "",
                "history": [
                    {
                        "status": "LANDED",
                        "when_utc": "2026-09-14T00:00:00Z",
                        "by": AUTHOR,
                        "commit": head,
                        "evidence": [],
                        "reason": "landed",
                    },
                    {
                        "status": "INTERNALLY_VERIFIED",
                        "when_utc": "2026-09-14T00:00:01Z",
                        "by": OTHER,
                        "commit": head,
                        "evidence": ["docs/evidence/proof.txt"],
                        "reason": "checked",
                    },
                ],
                "authored_against": [],
                "generalized_on": [],
                "executable_evidence": None,
                "verified_by": {"identity": OTHER, "kind": "internal_agent"},
                "verifications": [
                    {
                        "claim_id": "FIX-OLD",
                        "verifier": {"identity": OTHER, "kind": "internal_agent"},
                        "evidence": [
                            {
                                "path": "docs/evidence/proof.txt",
                                "sha256": _sha256(repo / "docs/evidence/proof.txt"),
                            }
                        ],
                        "architecture_identity": "a" * 64,
                        "method": "migration from legacy VERIFIED history; architecture identity recorded at migration",
                        "scope": ["scope.txt"],
                        "scope_blob_shas": fixstate._scope_blob_shas(repo, ["scope.txt"]),
                        "when_utc": "2026-09-14T00:00:01Z",
                        "commit": head,
                    }
                ],
            }
        ],
    }
    _write_store(repo, old_store)

    migrated = fixstate.migrate_v2_to_v3(repo)

    entry = migrated["entries"][0]
    assert migrated["schema_version"] == 3
    assert "status" not in json.dumps(entry)
    assert entry["implementation"] == "LANDED"
    assert entry["verification"] == "INTERNAL"
    assert entry["scope"] == "INSTANCE"
    assert entry["verifications"][0]["scope_paths"] == ["scope.txt"]
    assert entry["seal"]["dependencies"]["scope.txt"]

    proc = subprocess.run(
        [sys.executable, "-m", "harness.fixstate", "--migrate-v2-to-v3"],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1
    assert "already schema v3" in proc.stdout


def test_real_store_validates() -> None:
    ok, reasons = fixstate.check(ROOT)

    assert ok, "\n".join(reasons)
