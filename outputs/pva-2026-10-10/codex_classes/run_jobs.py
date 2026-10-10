"""Codex (read-only, recorded) on the page lane's generated-text classes C1-C8 (dispatches r5-r25, HANDOVER "PAGE"):
for each class, find the generating code, enumerate EVERY instance across the 32 served pages, say whether a fix moves a
served number, and propose the fix + a plant that fails first. Every call is appended to calls.jsonl with prompt / input /
output sha256, the reported model and the token count.

The work dir holds ONLY public material: harness/ code, topics/ protocol configs, and the 32 served review pages and
review objects. Never cache/ (held texts), never registry/model_calls (recorded prompts), never audit/external (D8).

  CODEX_EXE=<codex cli> python run_jobs.py [C1 ...]
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
W = A.parents[2]                                   # the repository root
WORK = Path(os.environ.get("CODEX_WORK", "C:/mh-lanes/tmp-pva/codex_classes"))
CODEX = os.environ.get("CODEX_EXE") or "codex"   # the codex CLI executable (on Windows: the npm codex.cmd)
CLASSES = json.loads((A / "classes.json").read_text(encoding="utf-8"))


def setup(cid: str) -> Path:
    d = WORK / cid
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(W / "harness", d / "harness", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(W / "topics", d / "topics")
    for rj in sorted((W / "docs" / "reviews").glob("*/review.json")):
        (d / "reviews" / rj.parent.name).mkdir(parents=True)
        for f in ("review.json", "index.html"):
            shutil.copy(rj.parent / f, d / "reviews" / rj.parent.name / f)
    return d


def job(cid: str) -> dict:
    c = CLASSES[cid]
    d = setup(cid)
    prompt = (A / "prompt.md").read_text(encoding="utf-8").replace("{CLASS_ID}", cid).replace(
        "{CLASS_NAME}", c["name"]).replace("{CLASS_RULE}", c["rule"]).replace("{CLASS_SEEN}", c["seen"])
    for sub in ("prompts", "out", "logs"):
        (A / sub).mkdir(parents=True, exist_ok=True)
    pf = A / "prompts" / f"{cid}.md"
    pf.write_text(prompt, encoding="utf-8")
    out = A / "out" / f"{cid}.json"
    tmp = WORK / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "TEMP": str(tmp), "TMP": str(tmp), "TMPDIR": str(tmp)}
    t0, start = time.time(), datetime.datetime.now().isoformat(timespec="seconds")
    try:
        with open(pf, "rb") as fin:
            p = subprocess.run([CODEX, "exec", "-s", "read-only", "--skip-git-repo-check", "-C", str(d), "--output-schema",
                                str(A / "schema.json"), "-o", str(out), "-"], stdin=fin, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=3600, env=env)
        rc, so, se = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, so, se = "TIMEOUT", str(e.stdout or ""), str(e.stderr or "")
    (A / "logs" / f"{cid}.log.gz").write_bytes(gzip.compress((so + "\n----STDERR----\n" + se).encode("utf-8")))
    tok = re.findall(r"tokens used\s*\n?\s*([\d,]+)", so + se)
    model = re.search(r"model:\s*(\S+)", so + se)
    inputs = hashlib.sha256()
    for f in sorted(d.rglob("*")):
        if f.is_file():
            inputs.update(f.relative_to(d).as_posix().encode() + b"\0" + f.read_bytes())
    rec = {"job": cid, "class": c["name"], "start": start, "seconds": round(time.time() - t0), "rc": rc,
           "model": model.group(1) if model else None, "tokens": tok[-1] if tok else None,
           "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "inputs_sha256": inputs.hexdigest(),
           "output_exists": out.is_file(), "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest() if out.is_file() else None}
    with open(A / "calls.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


if __name__ == "__main__":
    only = sys.argv[1:] or list(CLASSES)
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for rec in ex.map(job, only):
            print(json.dumps(rec), flush=True)
