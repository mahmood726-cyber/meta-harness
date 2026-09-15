"""Archive a snapshot's raw HTTP bodies OFF-TREE, keeping their digests in-tree.

The acquisition contract preserves every raw external input. A search_v2 run of one topic writes 200-600 MB of raw
bodies (2.5 GB for the 11 development topics); they cannot live in the repository. What lives in-tree is the
snapshot's `raw/INDEX.json` (one row per HTTP call: source id, url, params, status, fetched_utc, adapter blob sha,
body_sha256, file_sha256) and an `ARCHIVE.json` pointer written here; the bodies move to an archive root outside
the tree, keyed by the same relative paths. `--check` re-hashes every archived file against INDEX.json and refuses
on any mismatch or absence -- a body that cannot be produced is reported, never assumed.

Usage:
  python scripts/archive_raw_bodies.py move  --snapshot cache/<slug>/snapshots/<dir> --archive-root <path>
  python scripts/archive_raw_bodies.py check --snapshot cache/<slug>/snapshots/<dir> [--archive-root <path>]
"""
from __future__ import annotations
import argparse
import datetime as _dt
import hashlib
import io
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ARCHIVE_ROOT = os.environ.get("META_HARNESS_RAW_ARCHIVE", r"F:\meta-harness-raw-archive")


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_index(snapshot: str) -> list[dict]:
    p = os.path.join(snapshot, "raw", "INDEX.json")
    if not os.path.isfile(p):
        raise SystemExit(f"COULD-NOT-EXECUTE: no raw/INDEX.json under {snapshot}")
    return json.load(open(p, encoding="utf-8"))


def _rel_snapshot(snapshot: str) -> str:
    return os.path.relpath(os.path.abspath(snapshot), ROOT).replace("\\", "/")


def move(snapshot: str, archive_root: str) -> int:
    index = _load_index(snapshot)
    rel = _rel_snapshot(snapshot)
    dest_root = os.path.join(archive_root, rel)
    moved = 0
    for row in index:
        src = os.path.join(snapshot, row["path"])
        dst = os.path.join(dest_root, row["path"])
        if os.path.isfile(src):
            if _sha256(src) != row["file_sha256"]:
                raise SystemExit(f"REFUSED: {src} does not match INDEX file_sha256; nothing moved")
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            moved += 1
        elif not os.path.isfile(dst):
            raise SystemExit(f"REFUSED: {row['path']} is neither in the snapshot nor in the archive")
    # remove now-empty per-source dirs
    raw_root = os.path.join(snapshot, "raw")
    for name in sorted(os.listdir(raw_root)):
        d = os.path.join(raw_root, name)
        if os.path.isdir(d) and not os.listdir(d):
            os.rmdir(d)
    pointer = {
        "archive_root": archive_root,
        "archived_relpath": rel,
        "moved_utc": _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "bodies": len(index),
        "index_sha256": _sha256(os.path.join(snapshot, "raw", "INDEX.json")),
        "custody": "raw bodies held off-tree by the session author's machine; digests in raw/INDEX.json are the in-tree "
                   "authority; a body the archive cannot produce reads as NOT PRESERVED, never as preserved",
    }
    with open(os.path.join(snapshot, "ARCHIVE.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(pointer, f, indent=1)
        f.write("\n")
    return moved


def check(snapshot: str, archive_root: str | None) -> tuple[int, list[str]]:
    index = _load_index(snapshot)
    pointer_path = os.path.join(snapshot, "ARCHIVE.json")
    pointer = json.load(open(pointer_path, encoding="utf-8")) if os.path.isfile(pointer_path) else None
    root = archive_root or (pointer or {}).get("archive_root")
    rel = _rel_snapshot(snapshot)
    problems: list[str] = []
    ok = 0
    for row in index:
        local = os.path.join(snapshot, row["path"])
        archived = os.path.join(root, rel, row["path"]) if root else None
        path = local if os.path.isfile(local) else (archived if archived and os.path.isfile(archived) else None)
        if path is None:
            problems.append(f"NOT PRESERVED: {row['path']} (not in snapshot; not in archive {root})")
            continue
        if _sha256(path) != row["file_sha256"]:
            problems.append(f"DIGEST MISMATCH: {row['path']}")
            continue
        ok += 1
    return ok, problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["move", "check"])
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--archive-root", default=None)
    args = ap.parse_args(argv)
    snapshot = os.path.join(ROOT, args.snapshot) if not os.path.isabs(args.snapshot) else args.snapshot
    if args.action == "move":
        n = move(snapshot, args.archive_root or DEFAULT_ARCHIVE_ROOT)
        print(f"archived {n} raw bodies from {_rel_snapshot(snapshot)}; INDEX.json and ARCHIVE.json stay in-tree")
        return 0
    ok, problems = check(snapshot, args.archive_root)
    print(f"raw bodies preserved: {ok} of {ok + len(problems)} for {_rel_snapshot(snapshot)}")
    for p in problems:
        print("  - " + p)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
