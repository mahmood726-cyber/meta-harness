"""V1 post-deploy phase in ONE command (page-verifier and archive lane). Everything is measured on the SERVED V1 bytes or on the
exact V1 commit; nothing is carried forward from a rehearsal. Each step writes its artefact under --work and can be re-run alone.

  python v1_final.py --v1 <sha> --work <dir on a drive with >= 3.5 GB free> [--steps record,served,tabs,producer,f6,archive,note]
                     [--f6-script PATH]  (default: the V1 commit's scripts/f6_acceptance.py; else the main lane's local copy,
                                          recorded by sha256 -- it is not on origin)

Steps:
  record    wait for 'production record <v1[:12]>: ATTESTED (n/n ...)' on origin/production-records (max 90 min), then 660 s
            (the CDN max-age, so the served bytes are the new release only)
  served    v1_accept.py --source served --prev auto, all probes P0-P9           -> served/scorecard.json
  tabs      tab_acceptance_live.py on every served page, 1280x800 and 375x812   -> tabs.json
  producer  producer_probe.py in a full checkout of V1 (B3/D1)                  -> producer.txt
  f6        the section F.6 acceptance suite (19 cases) in the same checkout     -> f6.json (the suite's own report)
  archive   release_archive.py build-release --commit V1 --acceptance served/scorecard.json; check it -> archive/
  note      fill the release note's V1: lines from the artefacts above          -> V1_RELEASE_NOTE_final.md + RESULTS.json
The full checkout is created once for producer+f6 and removed afterwards (it is ~2.1 GB)."""
from __future__ import annotations

import argparse
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

REPO = "C:/mh-lanes/pva"
HERE = Path(__file__).resolve().parent
PY = sys.executable
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}


def sh(args, cwd=None, timeout=7200, check=False):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL, timeout=timeout, env=ENV)
    if check and p.returncode != 0:
        raise SystemExit(f"REFUSED: {' '.join(map(str, args))[:200]} -> rc {p.returncode}\n{p.stdout[-1500:]}\n{p.stderr[-1500:]}")
    return p


def git(*a, check=True):
    return sh(["git", "-C", REPO, *a], check=check).stdout.strip()


def stamp(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def step_record(v1, work):
    want = f"production record {v1[:12]}"
    for i in range(90):
        git("fetch", "-q", "origin", "production-records")
        rec = [s for s in git("log", "origin/production-records", "--format=%s").splitlines() if s.startswith(want)]
        if rec:
            (work / "record.txt").write_text(rec[0] + "\n", encoding="utf-8")
            stamp(f"RECORD: {rec[0]}; waiting 660 s for the CDN max-age")
            time.sleep(660)
            return rec[0]
        time.sleep(60)
    raise SystemExit(f"REFUSED: no production record for {v1[:12]} after 90 min -- the served audit is NOT RUN")


def step_served(v1, work):
    out = work / "served"
    p = sh([PY, str(HERE / "v1_accept.py"), "--release", v1, "--prev", "auto", "--work", str(out), "--source", "served"],
           timeout=5400)
    (work / "served.log").write_text(p.stdout + p.stderr, encoding="utf-8")
    stamp("served battery:\n" + "\n".join(l for l in p.stdout.splitlines() if l.startswith("[P") or "prev auto" in l))
    return json.loads((out / "scorecard.json").read_text(encoding="utf-8"))


def step_tabs(v1, work):
    p = sh([PY, str(HERE / "tab_acceptance_live.py"), "--slugs-from", v1, "--out", str(work / "tabs.json")], timeout=3600)
    s = json.loads((work / "tabs.json").read_text(encoding="utf-8"))["summary"]
    stamp(f"tabs: {s['passed']}/{s['checks']} all_pass={s['all_pass']} above={s['above_max']}")
    return s


def make_checkout(v1, work):
    wt = work / "wt"
    if wt.exists():
        return wt
    free = shutil.disk_usage(str(work)).free / 2**30
    if free < 3.0:
        raise SystemExit(f"REFUSED: only {free:.1f} GB free under {work}; a full checkout needs ~2.1 GB and the floor is ~1 GB after")
    sh(["git", "-C", REPO, "worktree", "add", "--no-checkout", "--detach", str(wt), v1], check=True)
    sh(["git", "-C", str(wt), "sparse-checkout", "disable"], check=False)
    sh(["git", "-C", str(wt), "checkout"], timeout=3600, check=True)
    n_tracked = len(sh(["git", "-C", str(wt), "ls-files"]).stdout.splitlines())
    n_disk = sum(1 for p in wt.rglob("*") if p.is_file() and ".git" not in p.parts)
    if n_disk < n_tracked:                 # a truncated checkout is the thin-tree hazard: refuse, never build from it
        raise SystemExit(f"REFUSED: checkout has {n_disk} files for {n_tracked} tracked -- incomplete tree")
    stamp(f"full checkout of {v1[:12]} at {wt}: {n_disk} files for {n_tracked} tracked")
    return wt


def remove_checkout(work):
    wt = work / "wt"
    if wt.exists():
        sh(["git", "-C", REPO, "worktree", "remove", "--force", str(wt)], timeout=1800)
        stamp("full checkout removed")


def step_producer(v1, work):
    wt = make_checkout(v1, work)
    p = sh([PY, str(HERE / "producer_probe.py"), str(wt)], cwd=wt, timeout=3600)
    (work / "producer.txt").write_text(p.stdout + p.stderr, encoding="utf-8")
    stamp("producer probe:\n" + p.stdout[-1500:])
    return p.stdout


def step_f6(v1, work, f6_script):
    wt = make_checkout(v1, work)
    in_v1 = wt / "scripts" / "f6_acceptance.py"
    src = in_v1 if in_v1.is_file() else Path(f6_script)
    if not src.is_file():
        raise SystemExit("REFUSED: no F.6 suite in the V1 commit and none at --f6-script")
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    if src != in_v1:
        shutil.copyfile(src, in_v1)          # run the main lane's suite against the V1 tree; recorded as external
    t0 = time.time()
    p = sh([PY, "scripts/f6_acceptance.py"], cwd=wt, timeout=6 * 3600)
    (work / "f6.log").write_text(p.stdout + p.stderr, encoding="utf-8")
    rep = wt / "f6_repaired.json"
    report = json.loads(rep.read_text(encoding="utf-8")) if rep.is_file() else {"error": "no f6_repaired.json", "rc": p.returncode}
    report["_pva"] = {"suite_source": "V1 commit" if src == in_v1 else f"external copy {src}", "suite_sha256": digest,
                      "rc": p.returncode, "seconds": round(time.time() - t0), "v1": v1}
    (work / "f6.json").write_text(json.dumps(report, indent=1, default=str), encoding="utf-8")
    stamp(f"F.6: rc={p.returncode} in {report['_pva']['seconds']} s; restored={report.get('original_bytes_restored')}")
    return report


def step_archive(v1, work):
    out = work / "archive"
    acc = work / "served" / "scorecard.json"
    args = [PY, "scripts/release_archive.py", "build-release", "--commit", v1, "--label", "v1", "--out", str(out)]
    if acc.is_file():
        args += ["--acceptance", str(acc)]
    b = sh(args, cwd=REPO, timeout=3600, check=True)
    z = next(out.glob("v1/*/*.zip"))
    c = sh([PY, "scripts/release_archive.py", "check", str(z)], cwd=REPO, timeout=3600)
    (work / "archive.log").write_text(b.stdout + c.stdout + c.stderr, encoding="utf-8")
    stamp(f"archive: {b.stdout.strip()[-300:]}\n{c.stdout[-800:]}")
    return {"zip": str(z), "sha256": hashlib.sha256(z.read_bytes()).hexdigest(), "bytes": z.stat().st_size,
            "check_rc": c.returncode, "check": c.stdout[-1200:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v1", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--steps", default="record,served,tabs,producer,f6,archive,note")
    ap.add_argument("--f6-script", default="F:/mh-gate/scripts/f6_acceptance.py")
    a = ap.parse_args()
    git("fetch", "-q", "origin")
    v1 = git("rev-parse", a.v1)
    work = Path(a.work)
    work.mkdir(parents=True, exist_ok=True)
    steps = a.steps.split(",")
    res_path = work / "RESULTS.json"
    res = json.loads(res_path.read_text(encoding="utf-8")) if res_path.is_file() else {}
    res.update(v1=v1, started=res.get("started") or datetime.datetime.now().isoformat(timespec="seconds"))
    try:
        if "record" in steps:
            res["record"] = step_record(v1, work)
        if "served" in steps:
            sc = step_served(v1, work)
            res["served"] = {pid: {"ok": p["ok"], "what": p["what"]} for pid, p in sc["probes"].items()}
        if "tabs" in steps:
            res["tabs"] = step_tabs(v1, work)
        if "producer" in steps:
            res["producer"] = step_producer(v1, work)[-3000:]
        if "f6" in steps:
            f6 = step_f6(v1, work, a.f6_script)
            res["f6"] = {"pva": f6.get("_pva"), "restored": f6.get("original_bytes_restored"),
                         "summary": {k: f6.get(k) for k in ("lane_acceptance", "summary", "acceptance") if k in f6}}
    finally:
        if "producer" in steps or "f6" in steps:
            remove_checkout(work)
        res_path.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    if "archive" in steps:
        res["archive"] = step_archive(v1, work)
        res_path.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    if "note" in steps:
        p = sh([PY, str(HERE / "fill_release_note.py"), "--results", str(res_path), "--work", str(work)], check=True)
        stamp(p.stdout[-600:])
    stamp(f"RESULTS: {res_path}")


if __name__ == "__main__":
    main()
