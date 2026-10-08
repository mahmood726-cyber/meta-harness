"""Codex rendering checks for the rapidmeta-v1 tabs: 7 jobs of up to 5 topics, 5 concurrent, every call recorded.
Each job's folder is a read-only extract: per topic the rendered markup of the checked tabs + its review.json, the
registry files the tabs read, and the renderer. Prompt on stdin; temp on C:; output schema-checked."""
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
W = Path("C:/mh-lanes/wt-tabs")
CODEX = "C:/Users/mahmo/AppData/Roaming/npm/codex.cmd"
TABS = ("protocol", "search", "included", "extraction", "riskofbias", "analysis", "outcomes", "comparator", "changes",
        "reproduction")
REG = ("g1_abandoned.json", "g1_decisions.json", "result_change_reinstatements.json", "comparator_switch_signatures.json",
       "provenance_hand_entered.json")
SEC = re.compile(r'<section class="tab" id="tab-([a-z]+)">(.*?)</section>(?=<section class="tab"|</main>)', re.S)


def extract(slug: str, dst: Path):
    page = (W / "docs" / "reviews" / slug / "index.html").read_text(encoding="utf-8")   # round 3: the SERVED bytes
    secs = {m.group(1): m.group(0) for m in SEC.finditer(page)}
    ov = secs.get("overview", "")
    banner = re.search(r"<div class='topic-status.*?</div>", ov, re.S)
    parts = [f"<section id='tab-overview-status'>{banner.group(0) if banner else ''}</section>"] + [secs.get(t, "") for t in TABS]
    (dst / slug).mkdir(parents=True, exist_ok=True)
    (dst / slug / "tabs.html").write_text("\n".join(parts), encoding="utf-8")
    shutil.copy(W / "docs" / "reviews" / slug / "review.json", dst / slug / "review.json")


def job(i: int, slugs: list[str]) -> dict:
    d = A / "jobs" / f"job{i}"
    if d.exists():
        shutil.rmtree(d)
    (d / "registry").mkdir(parents=True)
    for s in slugs:
        extract(s, d)
    for r in REG:
        shutil.copy(W / "registry" / r, d / "registry" / r)
    shutil.copy(W / "harness" / "review_tabs.py", d / "RENDERER.py")
    prompt = (A / "prompt_template.md").read_text(encoding="utf-8").replace("{SLUGS}", "\n".join(f"- {s}" for s in slugs))
    (A / "prompts").mkdir(exist_ok=True)
    (A / "out").mkdir(exist_ok=True)
    (A / "logs").mkdir(exist_ok=True)
    pf = A / "prompts" / f"job{i}.md"
    pf.write_text(prompt, encoding="utf-8")
    out = A / "out" / f"job{i}.json"
    tmp = A / "tmp"
    tmp.mkdir(exist_ok=True)
    env = {**os.environ, "TEMP": str(tmp), "TMP": str(tmp), "TMPDIR": str(tmp)}
    t0, start = time.time(), datetime.datetime.now().isoformat(timespec="seconds")
    try:
        with open(pf, "rb") as fin:
            p = subprocess.run([CODEX, "exec", "-s", "read-only", "--skip-git-repo-check", "-C", str(d), "--output-schema",
                                str(A / "schema.json"), "-o", str(out), "-"], stdin=fin, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=2700, env=env)
        rc, so, se = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, so, se = "TIMEOUT", str(e.stdout or ""), str(e.stderr or "")
    (A / "logs" / f"job{i}.log").write_text(so + "\n----STDERR----\n" + se, encoding="utf-8")
    tok = re.findall(r"tokens used\s*\n?\s*([\d,]+)", so + se)
    model = re.search(r"model:\s*(\S+)", so + se)
    rec = {"job": i, "slugs": slugs, "start": start, "seconds": round(time.time() - t0), "rc": rc,
           "model": model.group(1) if model else None, "tokens": tok[-1] if tok else None,
           "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
           "inputs_sha256": hashlib.sha256(b"".join((d / s / "tabs.html").read_bytes() for s in slugs)).hexdigest(),
           "output_exists": out.is_file(), "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest() if out.is_file() else None}
    with open(A / "calls.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


if __name__ == "__main__":
    slugs = sorted(p.parent.name for p in (W / "docs" / "reviews").glob("*/review.json"))
    batches = [slugs[i:i + 5] for i in range(0, len(slugs), 5)]
    only = [int(x) for x in sys.argv[1:]] or list(range(len(batches)))
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        for rec in ex.map(lambda i: job(i, batches[i]), only):
            print(json.dumps(rec), flush=True)
