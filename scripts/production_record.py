"""PRODUCTION RECORD -- build once, verify that immutable artifact, deploy exactly it, fetch it back and prove it.

WHY (2026-09-14, evidence/artifact-identity-2026-09-14/01-*). The first gated deploy re-checked-out the commit
inside the deploy job and re-tarred docs/ into a NEW artifact that the verify job had never seen. The two trees
agreeing was an assumption (same git SHA), not a check. The auditor's invariant, adopted: exactly one production
path; it cannot execute unless every mandatory verifier passed on the exact commit AND the exact artifact being
deployed; the deploy step consumes the verified artifact rather than rebuilding; and the served bytes are fetched
back independently and proven equal to the verified digests, per file (never an archive hash -- archive metadata
can change while contents do not).

THE CHAIN, one record (production-record.json), each link a measured value:
  commit_sha -> verify run id/attempt -> per-file SHA-256 manifest of docs/ (computed in the verify job, from the
  tree the standard just passed) -> pages artifact id (uploaded by the verify job, from that tree) -> deploy job:
  artifact downloaded and every file checked against the manifest BEFORE deploying -> deployment (environment,
  page_url, deployment id) -> every manifest path fetched from the live site and its body digest compared ->
  verdict. The record also binds each review page's exact-byte attestation: docs/reviews/<slug>/manifest.json
  html_sha256 must equal the per-file digest of that index.html (the page's internal "content hash" is a hash of
  the canonical review OBJECT; the exact-byte hash lives here, detached).

Subcommands (stdlib only; run by .github/workflows/verify.yml):
  manifest        --docs docs --out PATH             write the per-file manifest from the verified tree
  check-artifact  --manifest PATH --tar PATH         every file in the pages artifact == manifest (set + digests)
  attest          --manifest PATH --base-url URL --record PATH [--pages-artifact-id ID] [--retry-seconds N]
                  fetch every path from the live site, compare body digests, write the chained record
  publish-record  --record PATH --repo OWNER/REPO --token TOKEN --branch production-records
                  append the record to an orphan branch (durable, anonymously readable, outside main's ruleset)
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

_IMPORT_ROOT = Path(__file__).resolve().parents[1]
if str(_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_IMPORT_ROOT))
from harness.target import TargetUnresolvable, describe_target, refusal as target_refusal

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

RECORD_DIRNAME = "_production"      # served at <site>/_production/manifest.json inside the pages artifact
MANIFEST_NAME = "manifest.json"


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _now() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, encoding="utf-8", errors="replace").strip()


def _walk_files(docs: str) -> list[str]:
    out = []
    for root, _dirs, files in os.walk(docs):
        for fn in files:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, docs).replace(os.sep, "/")
            if rel.startswith(RECORD_DIRNAME + "/"):
                continue  # the manifest cannot contain its own digest
            out.append(rel)
    return sorted(out)


def _script_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _manifest_target(docs: str) -> str:
    repo_root = _script_root()
    docs_abs = os.path.abspath(docs)
    paths = [os.path.join(docs_abs, rel) for rel in _walk_files(docs)]
    try:
        return describe_target(repo_root, refs=("HEAD",), paths=paths, label="production_record.manifest")
    except TargetUnresolvable as exc:
        return target_refusal("production_record.manifest", str(exc))


def _load_manifest_for_target(path: str, label: str) -> tuple[dict | None, str | None]:
    try:
        return json.load(open(path, encoding="utf-8")), None
    except (OSError, ValueError) as exc:
        return None, target_refusal(label, f"manifest unreadable: {exc}")


def _is_git_worktree(root: Path) -> bool:
    proc = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=root, capture_output=True, text=True)
    if proc.returncode != 0:
        return False
    try:
        return Path(proc.stdout.strip()).resolve() == root.resolve()
    except OSError:
        return False


def _describe_from_manifest(manifest: str, man: dict, paths: list[str], label: str) -> str:
    """The deploy job has NO checkout by design (verify.yml: it downloads the artifact verify produced and nothing
    else), so a TARGET line for it cannot come from git. It names what the job actually reads: the manifest's
    commit_sha as head and the manifest file's own digest as the tree. 2026-09-15: every deploy since d15867aa
    (14 runs) died on `ModuleNotFoundError: harness` before this line could even be attempted -- verify green,
    site stale at 34747bd6 -- and with harness shipped it would have died here on `ref not resolvable: HEAD`."""
    if not paths:
        return target_refusal(label, "file set is empty")
    head = str(man.get("commit_sha") or "").strip()
    if not head:
        return target_refusal(label, "manifest carries no commit_sha")
    tree = f"artifact:manifest-sha256={_sha256_file(manifest)[:16]}"
    shown = " ".join(str(x).replace("\\", "/") for x in paths[:3]) + (" ..." if len(paths) > 3 else "")
    return f"TARGET {label}: head={head} base=none tree={tree} files={len(paths)} {shown}".rstrip()


def _artifact_target(manifest: str, tar_path: str) -> str:
    repo_root = _script_root()
    man, err = _load_manifest_for_target(manifest, "production_record.check_artifact")
    if err:
        return err
    paths = [manifest, tar_path, *list((man.get("files") or {}).keys())]
    if not _is_git_worktree(repo_root):
        return _describe_from_manifest(manifest, man, paths, "production_record.check_artifact")
    refs = (man.get("commit_sha"),) if man.get("commit_sha") else ()
    try:
        return describe_target(repo_root, refs=refs, paths=paths, label="production_record.check_artifact")
    except TargetUnresolvable as exc:
        return target_refusal("production_record.check_artifact", str(exc))


def _attest_target(manifest: str, base_url: str) -> str:
    repo_root = _script_root()
    man, err = _load_manifest_for_target(manifest, "production_record.attest")
    if err:
        return err
    base = base_url.rstrip("/") + "/"
    urls = [base + rel for rel in (man.get("files") or {})]
    if not _is_git_worktree(repo_root):
        return _describe_from_manifest(manifest, man, urls, "production_record.attest")
    refs = (man.get("commit_sha"),) if man.get("commit_sha") else ()
    try:
        return describe_target(repo_root, refs=refs, paths=urls, label="production_record.attest")
    except TargetUnresolvable as exc:
        return target_refusal("production_record.attest", str(exc))


def cmd_manifest(a) -> int:
    target_line = _manifest_target(a.docs)
    print(target_line)
    if target_line.startswith("TARGET production_record.manifest: COULD-NOT-EXECUTE"):
        return 1
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from harness import architecture_identity

    architecture_components = architecture_identity.components(repo_root)
    architecture_digest = architecture_identity.identity_from_components(architecture_components)
    docs = a.docs
    files = {rel: _sha256_file(os.path.join(docs, rel)) for rel in _walk_files(docs)}
    # Bind each review page's detached exact-byte attestation to the per-file digest.
    bindings, broken = [], []
    for rel in files:
        if rel.startswith("reviews/") and rel.endswith("/manifest.json"):
            slug = rel.split("/")[1]
            try:
                m = json.load(open(os.path.join(docs, rel), encoding="utf-8"))
            except (OSError, ValueError) as exc:
                broken.append(f"{rel}: unreadable ({exc})")
                continue
            page = f"reviews/{slug}/index.html"
            ok = (m.get("html_sha256") == files.get(page))
            bindings.append({"slug": slug, "page": page, "manifest_html_sha256": m.get("html_sha256"),
                             "file_sha256": files.get(page), "review_sha256": m.get("review_sha256"), "bound": ok})
            if not ok:
                broken.append(f"{page}: manifest html_sha256 {m.get('html_sha256')} != file digest {files.get(page)}")
    commit = os.environ.get("GITHUB_SHA") or _git("rev-parse", "HEAD")
    rec = {"_doc": "Per-file SHA-256 manifest of the served tree, computed in the verify job from the tree the "
                   "standard passed. Fetch any path and compare: sha256(body) must equal files[path].",
           "commit_sha": commit, "computed_utc": _now(),
           "verify_run_id": os.environ.get("GITHUB_RUN_ID"), "verify_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
           "workflow_ref": os.environ.get("GITHUB_WORKFLOW_REF"), "n_files": len(files), "files": files,
           "architecture_identity": architecture_digest, "architecture_components": architecture_components,
           "review_page_bindings": bindings}
    if broken:
        print("MANIFEST REFUSED: exact-byte attestation not bound:\n  " + "\n  ".join(broken))
        return 1
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    io.open(a.out, "w", encoding="utf-8", newline="\n").write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print(f"manifest: {len(files)} files, {len(bindings)} review pages bound, commit {commit[:12]} -> {a.out}")
    return 0


def cmd_check_artifact(a) -> int:
    target_line = _artifact_target(a.manifest, a.tar)
    print(target_line)
    if target_line.startswith("TARGET production_record.check_artifact: COULD-NOT-EXECUTE"):
        return 1
    man = json.load(open(a.manifest, encoding="utf-8"))
    want = man["files"]
    got = {}
    with tarfile.open(a.tar) as t:
        for m in t.getmembers():
            if not m.isfile():
                continue
            rel = m.name.lstrip("./")
            if rel.startswith(RECORD_DIRNAME + "/"):
                continue
            got[rel] = _sha256_bytes(t.extractfile(m).read())
    missing = sorted(set(want) - set(got))
    extra = sorted(set(got) - set(want))
    differ = sorted(p for p in set(want) & set(got) if want[p] != got[p])
    if missing or extra or differ:
        print(f"ARTIFACT REFUSED: missing={missing[:5]} extra={extra[:5]} differ={differ[:5]} "
              f"(counts {len(missing)}/{len(extra)}/{len(differ)})")
        return 1
    print(f"artifact == manifest: {len(got)} files, all digests equal (commit {man['commit_sha'][:12]})")
    return 0


def _fetch(url: str, timeout: int = 60) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": "meta-harness-attest/1.0", "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as exc:
        return exc.code, b""


def cmd_attest(a) -> int:
    target_line = _attest_target(a.manifest, a.base_url)
    print(target_line)
    if target_line.startswith("TARGET production_record.attest: COULD-NOT-EXECUTE"):
        return 1
    man = json.load(open(a.manifest, encoding="utf-8"))
    base = a.base_url.rstrip("/") + "/"
    deadline = time.time() + a.retry_seconds
    pending = dict(man["files"])
    fetched: dict[str, dict] = {}
    rounds = 0
    while pending and time.time() < deadline:
        rounds += 1
        for rel, want in list(pending.items()):
            url = base + rel + f"?attest={os.environ.get('GITHUB_RUN_ID', '0')}-{rounds}"
            status, body = _fetch(url)
            got = _sha256_bytes(body) if status == 200 else None
            fetched[rel] = {"url": base + rel, "http_status": status, "fetched_sha256": got, "verified_sha256": want,
                            "equal": got == want, "round": rounds, "fetched_utc": _now()}
            if got == want:
                pending.pop(rel)
        if pending:
            time.sleep(min(30, max(5, a.retry_seconds // 20)))
    ok = not pending
    record = {
        "_doc": ("Production record: one chain from commit to served bytes. Every value here was measured by the "
                 "workflow that deployed; nothing is asserted. Verify any link yourself: fetch url, sha256 the body, "
                 "compare with verified_sha256; GET the artifact by pages_artifact_id on the Actions API."),
        "verdict": "ATTESTED" if ok else "MISMATCH",
        "commit_sha": man["commit_sha"], "verify_run_id": man.get("verify_run_id"),
        "verify_run_attempt": man.get("verify_run_attempt"), "workflow_ref": man.get("workflow_ref"),
        "deploy_run_id": os.environ.get("GITHUB_RUN_ID"), "deploy_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "deploy_job": os.environ.get("GITHUB_JOB"), "environment": a.environment, "page_url": a.base_url,
        "pages_artifact_id": a.pages_artifact_id, "manifest_sha256": _sha256_file(a.manifest),
        "architecture_identity": man.get("architecture_identity"),
        "architecture_components": man.get("architecture_components"),
        "n_files": len(man["files"]), "n_equal": sum(1 for v in fetched.values() if v["equal"]),
        "n_mismatch": len(pending), "fetch_rounds": rounds, "attested_utc": _now(),
        "review_page_bindings": man.get("review_page_bindings"), "files": fetched,
    }
    os.makedirs(os.path.dirname(a.record) or ".", exist_ok=True)
    io.open(a.record, "w", encoding="utf-8", newline="\n").write(json.dumps(record, indent=1, sort_keys=True) + "\n")
    print(f"ATTEST {record['verdict']}: {record['n_equal']} of {record['n_files']} served files equal their verified "
          f"digest after {rounds} round(s); commit {man['commit_sha'][:12]}; pages artifact {a.pages_artifact_id}")
    if pending:
        for rel in list(pending)[:10]:
            print(f"  MISMATCH {rel}: served {fetched[rel]['fetched_sha256']} (http {fetched[rel]['http_status']}) "
                  f"!= verified {pending[rel]}")
    return 0 if ok else 1


def cmd_publish_record(a) -> int:
    rec = json.load(open(a.record, encoding="utf-8"))
    sha = rec["commit_sha"]
    with tempfile.TemporaryDirectory() as tmp:
        url = f"https://x-access-token:{a.token}@github.com/{a.repo}.git"
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        r = subprocess.run(["git", "clone", "--quiet", "--depth", "1", "--branch", a.branch, url, tmp],
                           capture_output=True, text=True, env=env)
        if r.returncode != 0:  # branch does not exist yet: create it orphan
            subprocess.run(["git", "init", "-q", tmp], check=True)
            subprocess.run(["git", "-C", tmp, "checkout", "-q", "--orphan", a.branch], check=True)
            io.open(os.path.join(tmp, "README.md"), "w", encoding="utf-8").write(
                "# production-records\n\nOne JSON per deployment, written by the deploy job of verify.yml. "
                "Each binds commit -> verify run -> per-file manifest -> pages artifact -> deployment -> served digests.\n")
        dst = os.path.join(tmp, f"{sha}.json")
        io.open(dst, "w", encoding="utf-8", newline="\n").write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
        subprocess.run(["git", "-C", tmp, "add", "-A"], check=True)
        subprocess.run(["git", "-C", tmp, "-c", "user.name=verify.yml deploy job", "-c",
                        "user.email=actions@github.com", "commit", "-q", "-m",
                        f"production record {sha[:12]}: {rec['verdict']} ({rec['n_equal']}/{rec['n_files']} served files equal)"],
                       check=True)
        r = subprocess.run(["git", "-C", tmp, "push", "-q", url, f"HEAD:refs/heads/{a.branch}"],
                           capture_output=True, text=True, env=env)
        if r.returncode != 0:
            print("PUBLISH-RECORD FAILED: " + (r.stderr or r.stdout).replace(a.token, "***"))
            return 1
        print(f"published {sha[:12]}.json to branch {a.branch}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("manifest"); m.add_argument("--docs", default="docs"); m.add_argument("--out", required=True)
    c = sub.add_parser("check-artifact"); c.add_argument("--manifest", required=True); c.add_argument("--tar", required=True)
    t = sub.add_parser("attest"); t.add_argument("--manifest", required=True); t.add_argument("--base-url", required=True)
    t.add_argument("--record", required=True); t.add_argument("--pages-artifact-id", default=None)
    t.add_argument("--environment", default="github-pages"); t.add_argument("--retry-seconds", type=int, default=600)
    u = sub.add_parser("publish-record"); u.add_argument("--record", required=True); u.add_argument("--repo", required=True)
    u.add_argument("--token", required=True); u.add_argument("--branch", default="production-records")
    a = p.parse_args(argv)
    return {"manifest": cmd_manifest, "check-artifact": cmd_check_artifact,
            "attest": cmd_attest, "publish-record": cmd_publish_record}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
