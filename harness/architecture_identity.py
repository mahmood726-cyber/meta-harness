"""Architecture identity for replayable production records.

This module binds the checked-out code, workflow, configuration, dependency,
retrieval, and model-stage surfaces into a deterministic digest. It is meant to
be run from the repository root in CI, but it also degrades deterministically
when a temporary copy is not a git worktree.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from harness import gitblob
from harness.canonical import canonical_json


PINNING_REASON = (
    "requirements.txt has no exact pins; no lockfile; CI installs latest at run time"
)
REPO_ROOT = Path(__file__).resolve().parents[1]
SHA40_RE = re.compile(r"^[0-9a-fA-F]{40}$")

HARNESS_IMPORT_DISTS = {
    "numpy": "numpy",
    "scipy": "scipy",
    "openpyxl": "openpyxl",
    "sentence_transformers": "sentence-transformers",
}

LOCKFILE_CANDIDATES = (
    "requirements.lock",
    "requirements.txt.lock",
    "poetry.lock",
    "Pipfile.lock",
    "uv.lock",
    "conda-lock.yml",
    "environment.lock.yml",
)

RETRIEVAL_ENDPOINTS = {
    "harness/fetch.py": [
        ("pubmed_eutils", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"),
        ("clinicaltrials_gov_v2", "https://clinicaltrials.gov/api/v2/studies"),
        ("pmc_oa", "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"),
        ("europe_pmc_search", "https://www.ebi.ac.uk/europepmc/webservices/rest/search"),
        ("europe_pmc_articles", "https://www.ebi.ac.uk/europepmc/webservices/rest/MED/{pmid}/{kind}"),
        ("unpaywall", "https://api.unpaywall.org/v2/{doi}"),
    ],
    "harness/acquisition.py": [
        ("pubmed_eutils", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"),
    ],
    "harness/registry_first.py": [
        ("clinicaltrials_gov_v2", "https://clinicaltrials.gov/api/v2/studies"),
        ("pubmed_eutils", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"),
        ("isrctn", "https://www.isrctn.com/api/query/format/default"),
    ],
    "harness/http.py": [
        ("generic_urlopen", "urllib.request.Request/urlopen caller-supplied URLs"),
    ],
}


def _as_root(root: str | os.PathLike[str] | None) -> Path:
    return Path(root).resolve() if root is not None else REPO_ROOT


def _rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root).as_posix()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


def _file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _git(root: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (OSError, ValueError):
        return None
    if proc.returncode != 0:
        return None
    out = proc.stdout.strip()
    return out or None


def _git_blob_sha(root: Path, relpath: str) -> str | None:
    # The blob git would store (clean filter applied) via one batched `git hash-object --stdin-paths`
    # per component (harness/gitblob.py). The earlier in-process sha1 of the raw bytes avoided ~19 s of
    # per-file subprocesses but differed between a CRLF worktree and an LF checkout -- an architecture
    # identity that depends on which machine computed it is not an identity.
    return gitblob.blob_sha(root, relpath)


def _iter_files(root: Path, rel_dir: str, pattern: str = "*") -> list[Path]:
    base = root / rel_dir
    if not base.exists():
        return []
    return sorted(p for p in base.rglob(pattern) if p.is_file())


def _file_digest_component(root: Path, files: list[Path]) -> dict[str, Any]:
    records = []
    for path in sorted(files):
        rel = _rel(root, path)
        records.append({"path": rel, "sha256": _file_sha256(path)})
    payload = "".join(f"{r['path']}\0{r['sha256']}\n" for r in records)
    return {"sha256": _sha256_text(payload), "files": records}


def _blob_component(root: Path, rel_dirs: tuple[str, ...]) -> dict[str, Any]:
    files: list[Path] = []
    for rel_dir in rel_dirs:
        glob = "*.py" if rel_dir in {"harness", "scripts"} else "*"
        files.extend(_iter_files(root, rel_dir, glob))
    records = _blob_records(root, files)
    payload = "".join(f"{r['path']}\0{r['git_blob_sha']}\n" for r in records)
    return {"sha256": _sha256_text(payload), "files": records}


def _blob_records(root: Path, files: list[Path]) -> list[dict[str, Any]]:
    """Blob identities as git stores them (clean filter applied), one batched git call for the set:
    a CRLF worktree and an LF checkout must yield the same architecture identity (harness/gitblob.py)."""
    rels = [_rel(root, path) for path in sorted(files)]
    shas = gitblob.blob_shas(root, rels)
    return [{"path": rel, "git_blob_sha": shas.get(rel)} for rel in rels]


def _configuration_component(root: Path) -> dict[str, Any]:
    files: list[Path] = []
    for rel_dir, glob in (("topics", "*.json"), ("protocols", "*.md"), ("registry", "*.json")):
        files.extend(_iter_files(root, rel_dir, glob))
    records = _blob_records(root, files)
    payload = "".join(f"{r['path']}\0{r['git_blob_sha']}\n" for r in records)
    return {"sha256": _sha256_text(payload), "files": records}


def _requirement_lines(req_path: Path) -> list[str]:
    if not req_path.is_file():
        return []
    lines = []
    for raw in req_path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            lines.append(line)
    return lines


def _has_exact_pins(lines: list[str]) -> bool:
    return bool(lines) and all(("==" in line or "===" in line) for line in lines)


def _installed_version(distribution: str) -> dict[str, Any]:
    try:
        return {"installed": True, "version": importlib.metadata.version(distribution)}
    except importlib.metadata.PackageNotFoundError:
        return {"installed": False, "version": None}


def _dependencies(root: Path) -> dict[str, Any]:
    req_path = root / "requirements.txt"
    req_lines = _requirement_lines(req_path)
    lockfiles = [name for name in LOCKFILE_CANDIDATES if (root / name).is_file()]
    installed_versions = {
        import_name: {
            "distribution": dist,
            **_installed_version(dist),
        }
        for import_name, dist in HARNESS_IMPORT_DISTS.items()
    }
    payload: dict[str, Any] = {
        "requirements_txt_sha256": _file_sha256(req_path),
        "requirements": req_lines,
        "installed_versions": installed_versions,
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": Path(sys.executable).name,
        },
    }
    pinned = _has_exact_pins(req_lines) and bool(lockfiles)
    payload["lockfiles_present"] = lockfiles
    payload["pinned"] = pinned
    if not pinned:
        payload["reason"] = PINNING_REASON
    payload["sha256"] = _sha256_text(canonical_json(payload))
    return payload


def _workflow(root: Path) -> dict[str, Any]:
    files = _iter_files(root, ".github/workflows")
    comp = _file_digest_component(root, files)
    uses = []
    for path in files:
        rel = _rel(root, path)
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            m = re.match(r"^\s*-?\s*uses:\s*['\"]?([^'\"\s#]+)", line)
            if not m:
                continue
            spec = m.group(1)
            action, ref = spec.rsplit("@", 1) if "@" in spec else (spec, None)
            uses.append(
                {
                    "path": rel,
                    "line": lineno,
                    "uses": spec,
                    "action": action,
                    "ref": ref,
                    "pinned_to_sha": bool(ref and SHA40_RE.fullmatch(ref)),
                }
            )
    return {"sha256": comp["sha256"], "files": comp["files"], "uses": uses}


def _hooks(root: Path) -> dict[str, Any]:
    return _file_digest_component(root, _iter_files(root, ".githooks"))


def _retrieval_adapters(root: Path) -> dict[str, Any]:
    adapters = []
    for relpath in sorted(RETRIEVAL_ENDPOINTS):
        endpoints = [
            {"label": label, "url": url, "mutable_external": True}
            for label, url in RETRIEVAL_ENDPOINTS[relpath]
        ]
        adapters.append(
            {
                "path": relpath,
                "version_git_blob_sha": _git_blob_sha(root, relpath),
                "file_sha256": _file_sha256(root / relpath),
                "endpoints": endpoints,
            }
        )
    payload: dict[str, Any] = {"adapters": adapters}
    payload["sha256"] = _sha256_text(canonical_json(payload))
    return payload


def _model_stages(root: Path) -> dict[str, Any]:
    inventory = root / "docs/model_stage_inventory.json"
    if not inventory.is_file():
        payload: dict[str, Any] = {
            "inventory_path": "docs/model_stage_inventory.json",
            "inventory_sha256": None,
            "stages": [],
            "missing": True,
        }
        payload["sha256"] = _sha256_text(canonical_json(payload))
        return payload
    data = json.loads(inventory.read_text(encoding="utf-8"))
    payload = {
        "inventory_path": "docs/model_stage_inventory.json",
        "inventory_sha256": _file_sha256(inventory),
        "stages": data.get("stages", []),
    }
    payload["sha256"] = _sha256_text(canonical_json(payload))
    return payload


def _parse_workflow_jobs(text: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    jobs_start = None
    for idx, line in enumerate(lines):
        if re.match(r"^jobs:\s*$", line):
            jobs_start = idx
            break
    if jobs_start is None:
        return []
    job_ranges: list[tuple[str, int, int]] = []
    for idx in range(jobs_start + 1, len(lines)):
        m = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", lines[idx])
        if m:
            if job_ranges:
                name, start, _ = job_ranges[-1]
                job_ranges[-1] = (name, start, idx)
            job_ranges.append((m.group(1), idx, len(lines)))
    jobs: list[dict[str, Any]] = []
    for name, start, end in job_ranges:
        block = lines[start:end]
        needs: str | list[str] | None = None
        condition: str | None = None
        for line in block:
            needs_m = re.match(r"^    needs:\s*(.+?)\s*$", line)
            if needs_m:
                raw = needs_m.group(1).strip()
                if raw.startswith("[") and raw.endswith("]"):
                    needs = [x.strip().strip("'\"") for x in raw[1:-1].split(",") if x.strip()]
                else:
                    needs = raw.strip("'\"")
            if_m = re.match(r"^    if:\s*(.+?)\s*$", line)
            if if_m:
                condition = if_m.group(1).strip()
        jobs.append({"name": name, "needs": needs, "if": condition})
    return jobs


def _build_deploy_path(root: Path) -> dict[str, Any]:
    verify = root / ".github/workflows/verify.yml"
    text = verify.read_text(encoding="utf-8", errors="replace") if verify.is_file() else ""
    jobs = _parse_workflow_jobs(text)
    deploy_jobs = [
        {"name": job["name"], "needs": job.get("needs"), "if": job.get("if")}
        for job in jobs
        if "deploy" in job["name"].lower()
    ]
    payload: dict[str, Any] = {
        "verify_yml_sha256": _file_sha256(verify),
        "jobs": jobs,
        "deploy_jobs": deploy_jobs,
    }
    payload["sha256"] = _sha256_text(canonical_json(payload))
    return payload


def components(root: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """Return the deterministic architecture component map for ``root``."""

    repo = _as_root(root)
    return {
        "commit_sha": _git(repo, "rev-parse", "HEAD") or "UNAVAILABLE",
        "tree_sha": _git(repo, "rev-parse", "HEAD^{tree}") or "UNAVAILABLE",
        "dependencies": _dependencies(repo),
        "workflow": _workflow(repo),
        "hooks": _hooks(repo),
        "harness_code": _blob_component(repo, ("harness", "scripts")),
        "configuration": _configuration_component(repo),
        "retrieval_adapters": _retrieval_adapters(repo),
        "model_stages": _model_stages(repo),
        "build_deploy_path": _build_deploy_path(repo),
    }


def identity_from_components(component_map: dict[str, Any]) -> str:
    """Return the architecture identity for an already-built component map."""

    return _sha256_text(canonical_json(component_map))


def identity(root: str | os.PathLike[str] | None = None) -> str:
    """Return the architecture identity digest for ``root``."""

    return identity_from_components(components(root))


def mutable_dependencies(root: str | os.PathLike[str] | None = None) -> list[str]:
    """Return all architecture surfaces that are not immutably pinned."""

    comp = components(root)
    mutable: list[str] = []
    deps = comp["dependencies"]
    if not deps.get("pinned"):
        mutable.append(f"requirements.txt: {deps.get('reason', PINNING_REASON)}")

    for use in comp["workflow"].get("uses", []):
        if not use.get("pinned_to_sha"):
            mutable.append(
                f"{use['path']}:{use['line']}: {use['uses']} is not pinned to a 40-hex commit SHA"
            )

    for adapter in comp["retrieval_adapters"].get("adapters", []):
        for endpoint in adapter.get("endpoints", []):
            if endpoint.get("mutable_external"):
                mutable.append(
                    f"retrieval_adapters.{adapter['path']}.{endpoint['label']}: "
                    f"{endpoint['url']} is a mutable external API"
                )

    for stage in comp["model_stages"].get("stages", []):
        pinning = stage.get("snapshot_pinning", {})
        if not pinning.get("pinned"):
            reason = pinning.get("reason") or "model snapshot is not immutable"
            mutable.append(
                f"model_stages.{stage.get('name')}: {stage.get('model_identifier')} unpinned - {reason}"
            )
    return mutable


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print the architecture identity.")
    parser.add_argument("--root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--json", action="store_true", help="Emit a single JSON object.")
    parser.add_argument("--check", help="Expected architecture identity.")
    args = parser.parse_args(argv)

    root = _as_root(args.root)
    comp = components(root)
    ident = identity_from_components(comp)
    mutable = mutable_dependencies(root)

    if args.json:
        print(
            canonical_json(
                {
                    "identity": ident,
                    "components": comp,
                    "mutable_dependencies": mutable,
                }
            )
        )
    else:
        print(f"architecture_identity: {ident}")
        print("components:")
        print(json.dumps(comp, indent=2, sort_keys=True))
        print("mutable_dependencies:")
        print(json.dumps(mutable, indent=2, sort_keys=True))

    if args.check and args.check != ident:
        print(
            f"architecture identity mismatch: expected {args.check}, observed {ident}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
