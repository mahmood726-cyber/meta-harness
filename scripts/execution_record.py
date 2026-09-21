"""Execution record: WHICH tree produced a review directory, written by the generator at the end of a build.

The frozen release at 316d2e48 has no such record and its generating tree is therefore UNRECORDED -- that is the true value and it
is not reconstructed here (a retrospectively inferred commit would be a proxy). From the first build that runs this module on, the
record names: generating commit, branch, tree state (CLEAN, or DIRTY with the dirty paths listed -- a scoped pass names its scope),
host, UTC timestamp, interpreter, installed distributions, the command, the inputs it read and the outputs it wrote (sha256 each),
and the release identity (release_sha256 / review_sha256) of the certificate it accompanies.

Ordering, in one sentence: the certificate is computed before this record exists, so the certificate cannot carry the record's
digest; the record carries the certificate's release_sha256 instead, the bundle carries the record's sha256 (review_files), and
scripts/verify_bundle.py recomputes both links and refuses a swapped record. The record is NOT an input to any digest the
certificate covers (its utc/host would make every build a release change) and no reproduction diff reads it.

stdlib only; git is invoked read-only and its absence is recorded, never inferred around."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RECORD_NAME = "EXECUTION_RECORD.json"
RECORD_VERSION = 1
ROOT = Path(__file__).resolve().parents[1]      # scripts/ -> repo root; this module lives under scripts/ because every file under
                                                 # harness/ enters certificate_scope.not_covered and would move release_sha256


def _sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _git(*args: str) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.rstrip("\r\n") if r.returncode == 0 else None      # never strip the left: porcelain lines begin with a status column


def git_state() -> dict:
    """Commit, branch and cleanliness of the tree the generator ran in. NO_GIT when git or the repo is unavailable."""
    head = (_git("rev-parse", "HEAD") or "").strip()
    if not head:
        return {"generating_commit": "NO_GIT", "branch": None, "tree_state": "UNKNOWN_NO_GIT", "dirty_paths": None,
                "meaning": "git was unavailable or this is not a repository; the generating tree cannot be named"}
    branch = (_git("rev-parse", "--abbrev-ref", "HEAD") or "").strip() or None
    status = _git("status", "--porcelain", "--untracked-files=all") or ""
    dirty = sorted(line[3:] for line in status.splitlines() if line.strip())
    return {"generating_commit": head, "branch": branch,
            "tree_state": "DIRTY" if dirty else "CLEAN", "dirty_paths": dirty,
            "meaning": ("the tree differed from the commit in the listed paths; the build read the WORKING TREE, so the commit alone does not "
                        "reproduce it unless those paths are restored" if dirty else
                        "the working tree equalled the commit; the commit reproduces the build")}


def environment() -> dict:
    dists = []
    try:
        from importlib import metadata
        dists = sorted(f"{d.metadata['Name']}=={d.version}" for d in metadata.distributions() if d.metadata and d.metadata.get("Name"))
    except Exception:
        dists = ["UNAVAILABLE"]
    return {"python": sys.version, "executable": sys.executable, "implementation": platform.python_implementation(),
            "platform": platform.platform(), "machine": platform.machine(), "host": platform.node(),
            "installed_distributions": dists,
            "harness_dependency_claim": "the certified analysis code is stdlib-only (certificate_scope.method); installed_distributions is the full "
                                        "interpreter environment, recorded so an outsider can rule the environment in or out, not a dependency list"}


def _key(p: Path) -> str:
    """Repo-relative when the path is inside the repo; otherwise the absolute path (a build outside the tree is recorded as such)."""
    try:
        return str(p.resolve().relative_to(ROOT.resolve())).replace(os.sep, "/")
    except ValueError:
        return str(p.resolve()).replace(os.sep, "/")


def _digests(paths) -> dict:
    out = {}
    for p in paths:
        p = Path(p)
        if p.is_file():
            out[_key(p)] = {"bytes": p.stat().st_size, "sha256": _sha256_file(p)}
    return out


def write_execution_record(review_dir: str | os.PathLike, slug: str, argv: list[str], now_arg: str | None) -> dict:
    """Write <review_dir>/EXECUTION_RECORD.json and return it. Called LAST by the generator, after the certificate exists."""
    rd = Path(review_dir)
    cert_path = rd / "CERTIFICATE.json"
    cert = json.loads(cert_path.read_text(encoding="utf-8")) if cert_path.exists() else {}
    manifest_path = rd / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    cache = ROOT / "cache" / slug
    inputs = _digests([ROOT / "topics" / f"{slug}.json", ROOT / "protocols" / f"{slug}.md"] + sorted(cache.glob("*")) if cache.exists() else
                      [ROOT / "topics" / f"{slug}.json", ROOT / "protocols" / f"{slug}.md"])
    outputs = _digests(p for p in sorted(rd.iterdir()) if p.is_file() and p.name not in (RECORD_NAME, "BUNDLE.json"))
    tree = git_state()
    if tree.get("dirty_paths"):
        # a build always dirties its own outputs before they are committed; separate those from everything else so a reader can
        # see whether the INPUT side of the tree equalled the commit
        own = set(outputs) | {f"docs/reviews/{slug}/{RECORD_NAME}", "docs/index.html", "registry/blind_map.json"}
        own_prefixes = ("docs/m/", "docs/reviews/")      # a run over several topics dirties every review directory before any commit
        def is_own(path):          # git reports repo-relative paths; output keys are repo-relative inside the repo, absolute outside it
            return path in own or path.startswith(own_prefixes) or any(k.endswith("/" + path) or path.endswith("/" + k) for k in own)
        tree["dirty_outputs_of_this_build"] = sorted(p for p in tree["dirty_paths"] if is_own(p))
        tree["dirty_other_paths"] = sorted(p for p in tree["dirty_paths"] if not is_own(p))
        tree["tree_state"] = "DIRTY" if tree["dirty_other_paths"] else "CLEAN_EXCEPT_OWN_OUTPUTS"
        tree["output_path_rule"] = "outputs of a build run: docs/reviews/**, docs/m/**, docs/index.html, registry/blind_map.json; everything else is input or code"
        tree["meaning"] = ("inputs and code equalled the commit; only this build's outputs differ (they are the files a following commit records)"
                           if not tree["dirty_other_paths"] else
                           "paths OTHER than this build's outputs differed from the commit; the commit alone does not reproduce this build")
    record = {
        "record_version": RECORD_VERSION,
        "slug": slug,
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": {"argv": list(argv), "now_argument": now_arg, "cwd": os.getcwd()},
        "tree": tree,
        "environment": environment(),
        "inputs": inputs,
        "outputs": outputs,
        "release": {"release_sha256": cert.get("release_sha256"), "review_sha256": cert.get("review_sha256") or manifest.get("review_sha256"),
                    "html_sha256": manifest.get("html_sha256"), "protocol_sha": manifest.get("protocol_sha"),
                    "meaning": "the certificate this record accompanies; the certificate cannot name this record (it is computed first), so the "
                               "link runs from the record to the certificate and from the bundle's review_files digest to this record"},
        "not_covered_by_this_record": ["network fetches (the build read the committed cache: from_cache=True)",
                                       "the generating tree of releases built before this record existed (UNRECORDED there, not reconstructed)"],
    }
    rd.mkdir(parents=True, exist_ok=True)
    (rd / RECORD_NAME).write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return record


def read_execution_record(review_dir: str | os.PathLike) -> dict | None:
    p = Path(review_dir) / RECORD_NAME
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))
