"""Codex (workspace-write in a SPARSE copy, recorded) implements one class fix + its plant from its own read-only report.

The sparse copy is a fresh git repo of public material only: harness/, tests/, topics/, the 32 served review pages and
objects (docs/reviews/*/{review.json,index.html}). Never cache/, registry/model_calls or audit/external (D8). Codex's work
comes back as `git diff` (impl/<C>.patch), which the lane reviews and tests in the full worktree. Every call is
appended to calls.jsonl (prompt / input / output sha256, reported model, tokens).

  CODEX_EXE=<codex cli> python implement.py C1 C2 ...
"""
import concurrent.futures as cf
import datetime
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

A = Path(__file__).resolve().parent
W = A.parents[2]
WORK = Path(os.environ.get("CODEX_WORK", "C:/mh-lanes/tmp-pva/codex_impl"))
CODEX = os.environ.get("CODEX_EXE") or "codex"
CLASSES = json.loads((A / "classes.json").read_text(encoding="utf-8"))


def _git(d, *a):
    return subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, encoding="utf-8", errors="replace")


def setup(cid: str) -> Path:
    d = WORK / cid
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)
    ig = shutil.ignore_patterns("__pycache__", "*.pyc")
    for sub in ("harness", "tests", "topics"):
        shutil.copytree(W / sub, d / sub, ignore=ig)
    for rj in sorted((W / "docs" / "reviews").glob("*/review.json")):
        (d / "docs" / "reviews" / rj.parent.name).mkdir(parents=True)
        for f in ("review.json", "index.html"):
            shutil.copy(rj.parent / f, d / "docs" / "reviews" / rj.parent.name / f)
    shutil.copy(A / "out" / f"{cid}.json", d / "CLASS_REPORT.json")
    _git(d, "init", "-q")
    _git(d, "add", "-A")
    _git(d, "-c", "user.name=pva", "-c", "user.email=pva@local", "commit", "-q", "-m", "base")
    return d


def job(cid: str) -> dict:
    c = CLASSES[cid]
    d = setup(cid)
    prompt = (A / "prompt_implement.md").read_text(encoding="utf-8").replace("{CLASS_ID}", cid).replace(
        "{CLASS_NAME}", c["name"]).replace("{CLASS_RULE}", c["rule"])
    for sub in ("impl_prompts", "impl", "impl_logs"):
        (A / sub).mkdir(parents=True, exist_ok=True)
    pf = A / "impl_prompts" / f"{cid}.md"
    pf.write_text(prompt, encoding="utf-8")
    out = A / "impl" / f"{cid}.summary.json"
    tmp = WORK / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "TEMP": str(tmp), "TMP": str(tmp), "TMPDIR": str(tmp)}
    t0, start = time.time(), datetime.datetime.now().isoformat(timespec="seconds")
    try:
        with open(pf, "rb") as fin:
            p = subprocess.run([CODEX, "exec", "-s", "workspace-write", "--skip-git-repo-check", "-C", str(d),
                                "--output-schema", str(A / "schema_implement.json"), "-o", str(out), "-"], stdin=fin,
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5400, env=env)
        rc, so, se = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, so, se = "TIMEOUT", str(e.stdout or ""), str(e.stderr or "")
    (A / "impl_logs" / f"{cid}.log.gz").write_bytes(gzip.compress((so + "\n----STDERR----\n" + se).encode("utf-8")))
    _git(d, "add", "-A")
    diff = _git(d, "diff", "--cached", "HEAD", "--", "harness", "tests").stdout
    (A / "impl" / f"{cid}.patch").write_text(diff, encoding="utf-8", newline="\n")
    tok = re.findall(r"tokens used\s*\n?\s*([\d,]+)", so + se)
    model = re.search(r"model:\s*(\S+)", so + se)
    rec = {"job": f"implement-{cid}", "class": c["name"], "start": start, "seconds": round(time.time() - t0), "rc": rc,
           "model": model.group(1) if model else None, "tokens": tok[-1] if tok else None,
           "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
           "inputs_sha256": hashlib.sha256((A / "out" / f"{cid}.json").read_bytes()).hexdigest(),
           "patch_sha256": hashlib.sha256(diff.encode()).hexdigest(), "patch_lines": diff.count("\n"),
           "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest() if out.is_file() else None}
    with open(A / "calls.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


if __name__ == "__main__":
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for rec in ex.map(job, sys.argv[1:]):
            print(json.dumps(rec), flush=True)
