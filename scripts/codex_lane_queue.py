"""Run the per-topic verification lanes (brief-V) through Codex at concurrency 3, one fresh clone per lane, harvesting
each lane's artefacts into outputs/search_v2/verification/ the moment its report exists.

Liveness is judged at the leaf: a lane counts as RUNNING only while its lane.log grows or its process is alive; a lane
whose log carries "tokens used" but no report is recorded as ENDED-WITHOUT-ARTEFACT (never as done). A lane that
raises is recorded with its last 20 log lines. Exit codes are never consulted.

Usage: python scripts/codex_lane_queue.py --base <sha> --brief <template.md> --topics measurement|development|all [--max 3]
Resumable: a topic whose harvested report already exists is skipped.
"""
from __future__ import annotations
import argparse
import datetime
import io
import json
import os
import shutil
import subprocess
import sys
import time

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARVEST = os.path.join(ROOT, "outputs", "search_v2", "verification")
SPLIT = os.path.join(ROOT, "registry", "search_benchmark_split.json")
LANE_ROOT = "C:/mh-r-"


def _utc():
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _topics(which):
    a = json.load(open(SPLIT, encoding="utf-8"))["assignments"]
    if which == "all":
        order = [s for s, v in sorted(a.items()) if v["set"] == "MEASUREMENT"] + [s for s, v in sorted(a.items()) if v["set"] == "DEVELOPMENT"]
        return order
    return [s for s, v in sorted(a.items()) if v["set"] == which.upper()]


def _log(msg):
    line = f"{_utc()} {msg}"
    print(line, flush=True)
    with open(os.path.join(HARVEST, "queue.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _launch(slug, base, template):
    lane = f"V-{slug}"
    brief = open(template, encoding="utf-8").read().replace("{SLUG}", slug)
    bpath = os.path.join(HARVEST, f"brief-{lane}.md")
    with open(bpath, "w", encoding="utf-8", newline="\n") as f:
        f.write(brief)
    extra = f"cache/{slug}/snapshots/2026-09-15r2-search_v2"
    proc = subprocess.run(["sh", os.path.join(ROOT, "scripts", "codex_lane.sh"), lane, base, bpath, extra],
                          capture_output=True, text=True)
    out = (proc.stdout.strip() or proc.stderr.strip())
    _log(f"launch {lane}: {out}")
    if not out.startswith("LANE ") or "REFUSED" in out:
        return None
    return lane


def _alive(pid):
    r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True)
    return str(pid) in r.stdout


STALE_SECONDS = 900


def _state(lane):
    """Leaf-level liveness: the report artefact; else the Windows PID recorded at launch (lane.winpid) plus log
    growth. A lane whose log carries 'tokens used' and whose process is gone ended without an artefact; a lane whose
    process is gone without that line died; a lane whose log has not grown for STALE_SECONDS is reported STALE
    (still counted as occupying a slot -- a stale lane is investigated, never silently replaced)."""
    clone = LANE_ROOT + lane
    log = os.path.join(clone, "lane.log")
    report = os.path.join(clone, f"LANE-{lane}-REPORT.md")
    if os.path.exists(report):
        return "REPORT"
    if not os.path.exists(log):
        return "NO-LOG"
    text = open(log, encoding="utf-8", errors="replace").read()
    wp = os.path.join(clone, "lane.winpid")
    pid = open(wp).read().strip() if os.path.exists(wp) else ""
    alive = _alive(pid) if pid else None
    if "tokens used" in text and alive is False:
        return "ENDED-NO-REPORT"
    if alive is False:
        return "DIED"
    if time.time() - os.path.getmtime(log) > STALE_SECONDS:
        return "STALE"
    return "RUNNING"


def _harvest(lane, slug, state):
    clone = LANE_ROOT + lane
    dst = os.path.join(HARVEST, slug)
    os.makedirs(dst, exist_ok=True)
    for name in (f"LANE-{lane}-REPORT.md", "lane.log"):
        p = os.path.join(clone, name)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(dst, name))
    lv = os.path.join(clone, "lane_v")
    if os.path.isdir(lv):
        for name in os.listdir(lv):
            src = os.path.join(lv, name)
            d = os.path.join(dst, name)
            if os.path.isdir(src):
                shutil.copytree(src, d, dirs_exist_ok=True)
            else:
                shutil.copy(src, d)
    model = ""
    logp = os.path.join(clone, "lane.log")
    if os.path.exists(logp):
        for line in open(logp, encoding="utf-8", errors="replace"):
            if line.startswith("model:"):
                model = line.strip()
                break
    first = ""
    rp = os.path.join(dst, f"LANE-{lane}-REPORT.md")
    if os.path.exists(rp):
        first = open(rp, encoding="utf-8", errors="replace").readline().strip()
    row = {"lane": lane, "slug": slug, "state": state, "model_line": model, "report_first_line": first, "harvested_utc": _utc()}
    with open(os.path.join(HARVEST, "ledger.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    _log(f"harvest {lane}: state={state} {model} :: {first[:160]}")
    # the clone is ~200 MB and its job is done; a lane that ended without its artefact keeps its clone for inspection
    if state == "REPORT" and first.strip():
        shutil.rmtree(clone, ignore_errors=True)
        _log(f"removed {clone}")
    elif state == "REPORT":
        _log(f"KEPT {clone}: report file present but EMPTY (treated as not done; harvest dir removed)")
        shutil.rmtree(dst, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--brief", required=True)
    ap.add_argument("--topics", default="measurement")
    ap.add_argument("--max", type=int, default=3)
    args = ap.parse_args(argv)
    os.makedirs(HARVEST, exist_ok=True)
    queue = [s for s in _topics(args.topics) if not os.path.exists(os.path.join(HARVEST, s, f"LANE-V-{s}-REPORT.md"))]
    _log(f"queue: {len(queue)} topics, max {args.max} concurrent, base {args.base[:12]}")
    running: dict[str, str] = {}   # lane -> slug
    while queue or running:
        for lane, slug in list(running.items()):
            st = _state(lane)
            if st == "STALE":
                _log(f"STALE {lane}: no log growth for {STALE_SECONDS}s (slot kept; investigate)")
            if st in ("REPORT", "ENDED-NO-REPORT", "DIED"):
                _harvest(lane, slug, st)
                del running[lane]
        # concurrency counts EVERY live lane on this machine (R-lanes launched by hand included), not just ours
        others = 0
        for name in os.listdir("C:/"):
            if name.startswith("mh-r-") and name[5:] not in running:
                lane = name[5:]
                if os.path.exists(os.path.join(LANE_ROOT + lane, "lane.pid")) and _state(lane) in ("RUNNING", "STALE"):
                    others += 1
        while queue and len(running) + others < args.max:
            # never two lanes on one worktree: the launcher refuses an existing clone
            slug = queue.pop(0)
            lane = _launch(slug, args.base, args.brief)
            if lane is None:
                # a refused launch (disk, or a clone left behind) is not a running lane; re-queue and back off
                queue.append(slug)
                _log(f"launch refused for {slug}; waiting 120 s")
                time.sleep(120)
                break
            running[lane] = slug
        time.sleep(30)
    _log("queue drained")
    return 0


if __name__ == "__main__":
    sys.exit(main())
