"""Codex (read-only, recorded) on the review-tabs handover items H2-H19, A1: root cause, PRESENTATION vs SERVED, fix, plant.
Every call is appended to calls.jsonl with prompt / input / output sha256 and the token count.

  CODEX_EXE=<codex cli> python run_jobs.py <phase> [job ...]      phase: classify | review
"""
import concurrent.futures as cf
import datetime
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
WORK = Path(os.environ.get("CODEX_WORK", "C:/mh-lanes/tmp-pva/codex3"))
CODEX = os.environ.get("CODEX_EXE") or "codex"   # the codex CLI executable (on Windows: the npm codex.cmd)
JOBS = {
    "A": (["H2", "H4", "H5"], ["dpp4-mace-t2d"]),
    "B": (["H3", "H13", "H19"], ["finerenone-ckd-t2d-renal", "semaglutide-obesity-weight", "tranexamic-acid-pph", "iv-iron-hfref-hosp"]),
    "C": (["H6", "H7", "H8", "H9"], ["doac-vte-recurrence", "sacubitril-valsartan-hfref", "tocilizumab-covid19-mortality",
                                     "tranexamic-acid-pph", "colchicine-recurrent-pericarditis"]),
    "D": (["H10", "H11", "H12", "H14"], ["pcsk9-mace", "metformin-pcos-ovulation", "melatonin-primary-insomnia-sol",
                                         "tocilizumab-covid19-mortality", "tranexamic-acid-pph"]),
    "E": (["H15", "H16", "H17", "H18", "A1"], ["empagliflozin-hfpef-hosp", "metformin-pcos-ovulation", "finerenone-ckd-t2d-renal",
                                               "statins-primary-prevention-elderly", "esketamine-trd-madrs", "dpp4-mace-t2d"]),
}


def setup(job: str, phase: str) -> Path:
    items, slugs = JOBS[job]
    d = WORK / phase / job
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(W / "harness", d / "harness", ignore=shutil.ignore_patterns("__pycache__"))
    for s in slugs:
        (d / "reviews" / s).mkdir(parents=True)
        for f in ("review.json", "index.html"):
            shutil.copy(W / "docs" / "reviews" / s / f, d / "reviews" / s / f)
    (d / "registry").mkdir()
    for f in ("g1_decisions.json", "result_change_reinstatements.json", "comparator_switch_signatures.json"):
        shutil.copy(W / "registry" / f, d / "registry" / f)
    shutil.copy(W / "docs" / "result_changes.json", d / "docs_result_changes.json")
    shutil.copy(W / "outputs" / "pva-2026-10-08" / "REVIEW_TABS_HANDOVER.md", d / "HANDOVER.md")
    if phase == "review":   # every review object, so a counter-example on any topic can be found
        for rj in sorted((W / "docs" / "reviews").glob("*/review.json")):
            dst = d / "reviews" / rj.parent.name / "review.json"
            if not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(rj, dst)
    if phase == "review" and (A / "review_diff.patch").is_file():
        shutil.copy(A / "review_diff.patch", d / "PROPOSED_FIX.patch")
    return d


def job(phase: str, job_id: str) -> dict:
    items, slugs = JOBS[job_id]
    d = setup(job_id, phase)
    prompt = (A / f"prompt_{phase}.md").read_text(encoding="utf-8").replace("{ITEMS}", ", ".join(items))
    (A / phase / "prompts").mkdir(parents=True, exist_ok=True)
    (A / phase / "out").mkdir(parents=True, exist_ok=True)
    (A / phase / "logs").mkdir(parents=True, exist_ok=True)
    pf = A / phase / "prompts" / f"job{job_id}.md"
    pf.write_text(prompt, encoding="utf-8")
    out = A / phase / "out" / f"job{job_id}.json"
    tmp = WORK / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "TEMP": str(tmp), "TMP": str(tmp), "TMPDIR": str(tmp)}
    t0, start = time.time(), datetime.datetime.now().isoformat(timespec="seconds")
    try:
        with open(pf, "rb") as fin:
            p = subprocess.run([CODEX, "exec", "-s", "read-only", "--skip-git-repo-check", "-C", str(d), "--output-schema",
                                str(A / f"schema_{phase}.json"), "-o", str(out), "-"], stdin=fin, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=3000, env=env)
        rc, so, se = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, so, se = "TIMEOUT", str(e.stdout or ""), str(e.stderr or "")
    import gzip
    (A / phase / "logs" / f"job{job_id}.log.gz").write_bytes(gzip.compress((so + "\n----STDERR----\n" + se).encode("utf-8")))
    tok = re.findall(r"tokens used\s*\n?\s*([\d,]+)", so + se)
    model = re.search(r"model:\s*(\S+)", so + se)
    inputs = hashlib.sha256()
    for f in sorted((d / "reviews").rglob("*")) + [d / "HANDOVER.md"]:
        if f.is_file():
            inputs.update(f.read_bytes())
    rec = {"phase": phase, "job": job_id, "items": items, "start": start, "seconds": round(time.time() - t0), "rc": rc,
           "model": model.group(1) if model else None, "tokens": tok[-1] if tok else None,
           "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "inputs_sha256": inputs.hexdigest(),
           "output_exists": out.is_file(), "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest() if out.is_file() else None}
    with open(A / "calls.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


if __name__ == "__main__":
    phase = sys.argv[1]
    only = sys.argv[2:] or list(JOBS)
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        for rec in ex.map(lambda j: job(phase, j), only):
            print(json.dumps(rec), flush=True)
