"""Make the branch Mahmood signs on: the release CANDIDATE plus this lane's signing tools plus the candidate's audit
registry. Pure git plumbing (a temporary index): nothing is checked out, nothing is pushed.

  python scripts/v1_sign_branch.py --cand <sha> --registry FILE --branch nr/v1-sign-<c12> [--tools-ref REF]

The tool files are taken from --tools-ref (default: HEAD, i.e. nr/notice-anchors). Before overlaying, every tool
file that ALSO exists in the candidate with different bytes is listed: the candidate's own version may carry a
change the lane must merge rather than overwrite. With --refuse-on-divergence the command then refuses.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ["scripts/notice_anchor.py", "scripts/notice_rejudge.py", "scripts/sign_walk.py",
         "scripts/countersign_result_change.py", "scripts/notice_signing_list.py",
         "scripts/verify_notice_signatures.py", "scripts/rederive_notices.py", "scripts/v1_notice_registry.py",
         "scripts/v1_sign_branch.py"]


def git(*args: str, env=None, data: bytes | None = None) -> str:
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, env=env, input=data)
    if p.returncode != 0:
        raise SystemExit(f"refused: git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode().strip()


def blob(ref: str, path: str) -> str | None:
    p = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{ref}:{path}"], cwd=ROOT, capture_output=True)
    return p.stdout.decode().strip() if p.returncode == 0 else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cand", required=True)
    ap.add_argument("--registry", required=True)
    ap.add_argument("--branch", required=True)
    ap.add_argument("--tools-ref", default="HEAD")
    ap.add_argument("--refuse-on-divergence", action="store_true")
    args = ap.parse_args(argv)
    cand = git("rev-parse", "--verify", f"{args.cand}^{{commit}}")
    tools_ref = git("rev-parse", "--verify", f"{args.tools_ref}^{{commit}}")
    diverged = [p for p in TOOLS if blob(cand, p) and blob(cand, p) != blob(tools_ref, p)]
    for p in diverged:
        print(f"DIVERGED: {p} exists in the candidate with different bytes (candidate {blob(cand, p)[:12]}, "
              f"tools {blob(tools_ref, p)[:12]}) -- review before signing")
    if diverged and args.refuse_on_divergence:
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / "index"))
        git("read-tree", cand, env=env)
        for p in TOOLS:
            b = blob(tools_ref, p)
            if b is None:
                raise SystemExit(f"refused: {p} is not in {tools_ref[:12]}")
            git("update-index", "--add", "--cacheinfo", f"100644,{b},{p}", env=env)
        reg = git("hash-object", "-w", "--", str(Path(args.registry).resolve()))
        git("update-index", "--add", "--cacheinfo", f"100644,{reg},registry/notice_adjudication.json", env=env)
        tree = git("write-tree", env=env)
    msg = (f"Sign branch for the V1 candidate {cand[:12]}: the candidate's pages and ledger, lane NR's signing tools "
           f"(from {tools_ref[:12]}) and the candidate's audit registry. Nothing is signed.\n\n"
           "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>\n")
    commit = git("commit-tree", tree, "-p", cand, "-F", "-", data=msg.encode())
    git("update-ref", f"refs/heads/{args.branch}", commit)
    print(f"{args.branch} -> {commit} (parent {cand[:12]}; {len(TOOLS)} tool files, registry blob {reg[:12]}; "
          f"{len(diverged)} diverged)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
