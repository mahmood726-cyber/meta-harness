"""RECORDED codex calls on the WORKER PC (Mahmood 6 Oct: "concurrency 5 here and 5 on the worker"). Same recorder, same
records: each job is the exact prompt bytes + schema + model + caller + input digests; the worker runs
reproducible_ai.model_call_live.call in ITS OWN worktree at the lane's PUSHED sha (C:\\mh-worker\\binding-wt, never the
shared worker repo), writes each record, and a sha256 manifest; the records are copied back and accepted only when every
file's sha256 matches the manifest. The licence guard runs inside the recorder on the worker too, on the SAME licence
indexes (copied from here before the batch), so a prompt refused here is refused there.

Transport: Git's ssh/scp (C:\\Program Files\\Git\\usr\\bin): Windows OpenSSH refuses the key while its ACL lists
CodexSandboxUsers (a security setting left to Mahmood). Foreground sessions with ServerAliveInterval survive long runs.

    local:  submit(jobs, batch)  -> {key: {"record": path, ...}}
    worker: python scripts/g1_remote_codex.py --worker <batch dir> [--concurrency 5]
"""
from __future__ import annotations

import base64
import concurrent.futures as cf
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
PEER = os.environ.get("G1_WORKER_PEER", "mahmo@100.80.183.43")
GIT_BIN = r"C:\Program Files\Git\usr\bin"
WT = r"C:\mh-worker\binding-wt"
PY = r"C:\mh-worker\venv\Scripts\python.exe"
LOCAL = os.environ.get("G1_REMOTE_DIR", "C:/mh-tmp/binding/remote")
LICENCE_FILES = ["outputs/k_gap/fulltext_index.json", "outputs/k_gap/unpaywall_text_index.json",
                 "outputs/k_gap/g1_binding/licences.json"]
SSH_OPTS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=20", "-o", "ServerAliveInterval=15"]


def _ssh(cmd, timeout=None):
    return subprocess.run([os.path.join(GIT_BIN, "ssh.exe"), *SSH_OPTS, PEER, cmd], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=timeout)


def _scp(src, dst, timeout=None, tries=3):
    """scp with bounded retries: a transient 'Connection reset by peer' (6 Oct) is retried, a persistent failure raised."""
    import time
    for k in range(tries):
        r = subprocess.run([os.path.join(GIT_BIN, "scp.exe"), *SSH_OPTS, "-r", src, dst], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=timeout)
        if not r.returncode:
            return
        time.sleep(10 * (k + 1))
    raise RuntimeError(f"scp failed after {tries} tries: {r.stderr[-300:]}")


def _remote(path):                       # a Windows path on the worker as an scp target ('C:/mh-worker/...')
    return f"{PEER}:{path.replace(chr(92), '/')}"


def head_sha():
    return subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def sync_worker(sha):
    """The worker worktree at exactly `sha` (which must be pushed); refuses otherwise."""
    r = _ssh(f'cd /d {WT} && git reset --quiet --hard && git fetch --quiet origin && git checkout --quiet --detach {sha} && git rev-parse HEAD', 600)  # my own worktree: only copied indexes to drop
    got = (r.stdout.strip().splitlines() or [""])[-1]
    if got != sha:
        raise RuntimeError(f"REFUSED: worker worktree HEAD {got!r} != {sha} ({r.stderr[-200:]})")
    return got


def submit(jobs, batch, concurrency=5, timeout=7200):
    """jobs: [{key, prompt (bytes), schema, model, effort, caller, input_digests, timeout_s}] -> {key: record dict}."""
    sha = head_sha()
    sync_worker(sha)
    bdir = os.path.join(LOCAL, batch)
    shutil.rmtree(bdir, ignore_errors=True)
    os.makedirs(os.path.join(bdir, "jobs"))
    for i, j in enumerate(jobs):
        d = dict(j, prompt_b64=base64.b64encode(j["prompt"]).decode("ascii"))
        d.pop("prompt")
        json.dump(d, open(os.path.join(bdir, "jobs", f"{i:04d}.json"), "w", encoding="utf-8"))
    rb = WT + "\\_remote\\" + batch
    _ssh(f'if not exist "{WT}\\_remote" mkdir "{WT}\\_remote"', 60)
    _scp(bdir, _remote(WT + "\\_remote\\"), 600)
    for f in LICENCE_FILES:                       # the guard decides on the SAME licence data as here
        if os.path.exists(os.path.join(ROOT, f)):
            _scp(os.path.join(ROOT, f), _remote(WT + "\\" + f.replace("/", "\\")), 600)
    r = _ssh(f'cd /d {WT} && set PYTHONIOENCODING=utf-8&& "{PY}" scripts\\g1_remote_codex.py --worker "{rb}" '
             f'--concurrency {concurrency}', timeout)
    if r.returncode:
        raise RuntimeError(f"worker batch failed rc={r.returncode}: {r.stdout[-400:]} {r.stderr[-400:]}")
    shutil.rmtree(os.path.join(bdir, "out"), ignore_errors=True)
    _scp(_remote(rb + "\\out"), bdir, 600)
    man = json.load(open(os.path.join(bdir, "out", "manifest.json"), encoding="utf-8"))
    out = {}
    for key, m in man.items():
        if m.get("error"):
            out[key] = {"error": m["error"]}
            continue
        p = os.path.join(bdir, "out", m["file"])
        if hashlib.sha256(open(p, "rb").read()).hexdigest() != m["sha256"]:
            raise RuntimeError(f"REFUSED: {m['file']} sha256 differs from the worker manifest")
        out[key] = {"record_path": p, "record_id": m["record_id"], "state": m["state"], "worker_sha": sha}
    _ssh(f'rmdir /s /q "{rb}"', 120)
    return out


def worker_main(bdir, concurrency):
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    od = os.path.join(bdir, "out")
    os.makedirs(od, exist_ok=True)
    jobs = [json.load(open(os.path.join(bdir, "jobs", f), encoding="utf-8")) for f in sorted(os.listdir(os.path.join(bdir, "jobs")))]

    def one(j):
        try:
            rec = mcl.call(base64.b64decode(j["prompt_b64"]), schema=j["schema"], model=j["model"], effort=j["effort"],
                           caller=dict(j["caller"], host="worker"), input_digests=j["input_digests"],
                           timeout_s=j.get("timeout_s") or 1500)
            p = ms.write_record(rec, od)
            return j["key"], {"file": os.path.basename(str(p)), "record_id": rec["record_id"], "state": rec["state"],
                              "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest()}
        except Exception as exc:  # noqa: BLE001 - a refused / failed job is reported by name, never dropped
            return j["key"], {"error": f"{type(exc).__name__}: {str(exc)[:400]}"}
    man = {}
    with cf.ThreadPoolExecutor(max_workers=concurrency) as ex:
        for k, v in ex.map(one, jobs):
            man[k] = v
            print(k, v.get("state") or v.get("error"), flush=True)
    json.dump(man, open(os.path.join(od, "manifest.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    if "--worker" in sys.argv:
        c = int(sys.argv[sys.argv.index("--concurrency") + 1]) if "--concurrency" in sys.argv else 5
        worker_main(sys.argv[sys.argv.index("--worker") + 1], c)
