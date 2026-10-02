"""G1 BATCH: the whole G1 pipeline over EVERY topic with a confirmed comparator trial list, three topics at a time.

Per topic, in a subprocess (no shared module state between topics):
  1. scripts/secondary_meta_build.py SLUG   typed comparator/secondary tables by regex, replay of recorded figure reads,
                                            deterministic verify_typed over held OA text + the AACT snapshot, two-source
  2. scripts/g1_tracker.py SLUG             k matched n of N eligible, routes, named differences, blockers, verdict
Seeding (k_gap_counterfactual --members), the exclusion audit and the AACT index (kgap.aact_adapter.ensure over the union
of every topic's NCTs) are run ONCE before the batch, not per topic.

A topic is DONE only when its outputs/k_gap/g1/<slug>.json was written by THIS run (mtime after the run started) and
parses -- never by a process exit code. Failures keep their stderr tail.

    python scripts/g1_batch.py [--jobs 3] [--tracker-only] [SLUG ...]  -> outputs/k_gap/g1_batch.json + G1_TRACKER.md
"""
from __future__ import annotations

import concurrent.futures as cf
import io
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "k_gap")
FOCUS = ["glp1-ra-mace-t2d", "semaglutide-obesity-weight", "noac-vs-warfarin-af-stroke", "tocilizumab-covid19-mortality"]


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _scrub(lines):
    """A failing step's LAST stderr line, any absolute path reduced to its file name (this output is committed)."""
    import re
    s = " ".join(lines)
    return re.sub(r"[A-Za-z]:[\\/][^\s\"']*[\\/]([^\\/\s\"']+)", r"\1", s)[:300]


def topics():
    """EVERY served topic, focus first: a topic whose comparator lists no enumerable trial still gets a row stating
    why (it was silently skipped: denosumab-vertebral-fracture)."""
    import g1_tracker
    served = g1_tracker.served_topics()
    return [s for s in FOCUS if s in served] + sorted(s for s in served if s not in FOCUS)


def run_topic(slug, t0, tracker_only=False):
    env = dict(os.environ, PYTHONUTF8="1")
    rec = {"slug": slug, "steps": []}
    steps = [("secondary_build", [sys.executable, "scripts/secondary_meta_build.py", slug]),
             ("tracker", [sys.executable, "scripts/g1_tracker.py", slug, "--no-table"])]
    for name, args in (steps[1:] if tracker_only else steps):
        s0 = time.time()
        p = subprocess.run(args, cwd=ROOT, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=3600)
        rec["steps"].append({"step": name, "secs": round(time.time() - s0, 1), "rc": p.returncode,
                             "stderr_tail": _scrub((p.stderr or "").strip().splitlines()[-1:]) if p.returncode else ""})
        if p.returncode:
            break
    gp = os.path.join(OUT, "g1", f"{slug}.json")
    ok = os.path.exists(gp) and os.path.getmtime(gp) >= t0
    failed = [st["step"] for st in rec["steps"] if st["rc"]]
    if failed:
        # a fresh artefact does not excuse a failed step: both are reported, and the topic is NOT done
        rec.update(done=False, why=f"STEP_FAILED:{','.join(failed)}" + ("" if ok else "+NO_FRESH_TRACKER_FILE"))
        return rec
    if ok:
        try:
            o = _j(gp)
            rec.update(done=True, k_matched=o["k_matched"], N_eligible=o.get("N_eligible"),
                       N=o["N_comparator_trials"], top_blocker=o.get("top_blocker"),
                       verdict=((o.get("same_trials") or {}).get("verdict") or {}).get("verdict"))
        except (ValueError, KeyError) as exc:
            rec.update(done=False, why=f"TRACKER_FILE_UNREADABLE:{exc}")
    else:
        rec.update(done=False, why="NO_FRESH_TRACKER_FILE")
    return rec


def main(argv):
    jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 3
    slugs = [a for a in argv if not a.startswith("--") and not a.isdigit()] or topics()
    # topics another lane OWNS are never computed here: they are imported from that lane's pinned artefact
    lp = os.path.join(OUT, "g1_lanes.json")
    owned = set(_j(lp)) if os.path.exists(lp) else set()
    slugs = [s for s in slugs if s not in owned]
    t0 = time.time()
    res = []
    with cf.ThreadPoolExecutor(max_workers=jobs) as ex:
        futs = {ex.submit(run_topic, s, t0, "--tracker-only" in argv): s for s in slugs}
        for f in cf.as_completed(futs):
            r = f.result()
            res.append(r)
            print(r["slug"], "DONE" if r.get("done") else "FAILED:" + r.get("why", ""), r.get("k_matched"),
                  r.get("N_eligible"), r.get("top_blocker"), flush=True)
    order = {s: i for i, s in enumerate(slugs)}
    res.sort(key=lambda r: order[r["slug"]])
    out = {"started": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t0)), "wall_secs": round(time.time() - t0, 1),
           "jobs": jobs, "topics": len(slugs), "done": sum(1 for r in res if r.get("done")), "results": res}
    with open(os.path.join(OUT, "g1_batch.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1)
    imp = subprocess.run([sys.executable, "scripts/g1_import_lanes.py"], cwd=ROOT, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, encoding="utf-8", errors="replace",
                         env=dict(os.environ, PYTHONUTF8="1"))
    out["lanes_imported"] = {"rc": imp.returncode, "lines": (imp.stdout or "").strip().splitlines()[-10:],
                             "stderr_tail": _scrub((imp.stderr or "").strip().splitlines()[-1:]) if imp.returncode else ""}
    with open(os.path.join(OUT, "g1_batch.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1)
    tb = subprocess.run([sys.executable, "scripts/g1_tracker.py", "--table"], cwd=ROOT, stdin=subprocess.DEVNULL,
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        env=dict(os.environ, PYTHONUTF8="1"))
    # the table REFUSES when a served topic has no row: that refusal is surfaced, never swallowed
    out["table"] = {"rc": tb.returncode,
                    "stderr_tail": _scrub((tb.stderr or "").strip().splitlines()[-1:]) if tb.returncode else ""}
    with open(os.path.join(OUT, "g1_batch.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1)
    print("BATCH", out["done"], "of", out["topics"], "in", out["wall_secs"], "s", "| table rc", tb.returncode,
          out["table"]["stderr_tail"])


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
