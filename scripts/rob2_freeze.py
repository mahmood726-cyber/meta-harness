"""Freeze a rule version BEFORE it is evaluated on TEST: the sha256 of every file that decides a typed answer, the git HEAD,
the time, and the DEV evaluation it was frozen on. A TEST evaluation cites this file; a change to a frozen file after the
freeze makes the TEST number belong to no version (scripts/rob2_calibration_nofn.py refuses it).

    python scripts/rob2_freeze.py v3   -> outputs/robgrade/freeze_v3.json (refuses to overwrite)
"""
import datetime
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["robgrade/rob2_typed.py", "robgrade/rob2_formal.py", "robgrade/prompt_licence.py", "scripts/rob2_dual.py",
         "outputs/robgrade/split.json", "outputs/robgrade/dev/rule_eval.json", "outputs/robgrade/dev/rule_proposals_r2.json"]


def digests():
    return {f: hashlib.sha256(open(os.path.join(ROOT, f), "rb").read()).hexdigest() for f in FILES}


def main(version):
    out = os.path.join(ROOT, "outputs", "robgrade", f"freeze_{version}.json")
    if os.path.exists(out):
        raise SystemExit(f"REFUSED: {out} exists -- a frozen version is never re-frozen")
    head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    rec = {"version": version, "frozen_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "git_head_at_freeze": head, "worktree_uncommitted": True, "files_sha256": digests(),
           "dev_only": "rules mined and checked on DEV (outputs/robgrade/split.json); TEST read once, after this freeze"}
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps(rec, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
