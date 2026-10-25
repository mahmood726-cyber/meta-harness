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
import re
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


def _rel_snapshot(snapshot: str) -> str:
    """A raw archive may not address an unrelated tree through '../'."""
    # Resolve the directory itself, not merely its textual path: an in-tree
    # symlink may point to records outside the repository.
    rel = os.path.relpath(os.path.realpath(snapshot), os.path.realpath(ROOT)).replace("\\", "/")
    if rel == ".." or rel.startswith("../") or rel == ".":
        raise SystemExit("REFUSED: snapshot must be a directory inside the repository")
    return rel


def _inside(path: str, directory: str) -> bool:
    """Resolve symlinks before trusting an indexed source or archive path."""
    try:
        return os.path.commonpath((os.path.realpath(path), os.path.realpath(directory))) == os.path.realpath(directory)
    except ValueError:
        return False


def _require_off_tree_archive(archive_root: str) -> None:
    """Never mistake a repository-local directory for off-tree custody.

    realpath also catches an archive-root symlink back into the repository.
    This checks storage location only; off-tree does NOT mean independently
    held or externally attested.
    """
    if not isinstance(archive_root, str) or not archive_root.strip() or _inside(archive_root, ROOT):
        raise SystemExit("REFUSED: archive root must resolve outside the repository")


def _load_index(snapshot: str) -> list[dict]:
    """Verify INDEX against the snapshot ledger before considering any body preserved."""
    p = os.path.join(snapshot, "raw", "INDEX.json")
    ledger_path = os.path.join(snapshot, "retrieval_ledger.json")
    if not os.path.isfile(p) or not os.path.isfile(ledger_path):
        raise SystemExit("REFUSED: raw/INDEX.json and retrieval_ledger.json are both required")
    try:
        with open(p, "rb") as fh:
            index_bytes = fh.read()
        with open(ledger_path, encoding="utf-8") as fh:
            ledger = json.load(fh)
        index = json.loads(index_bytes)
    except (ValueError, UnicodeError, OSError) as exc:
        raise SystemExit(f"REFUSED: corrupt raw index or retrieval ledger: {exc}") from exc
    snapshot_meta = ledger.get("snapshot") if isinstance(ledger, dict) else None
    digest = hashlib.sha256(index_bytes).hexdigest()
    if (not isinstance(snapshot_meta, dict)
            or snapshot_meta.get("mode") != "REFRESH"
            or snapshot_meta.get("raw_index_sha256") != digest):
        raise SystemExit("REFUSED: raw INDEX digest/mode not bound to a REFRESH retrieval ledger")
    raw_calls = snapshot_meta.get("raw_calls")
    if (type(raw_calls) is not int or raw_calls < 1
            or not isinstance(index, list) or len(index) != raw_calls):
        raise SystemExit("REFUSED: raw INDEX count is inconsistent with retrieval ledger")
    pointer_path = os.path.join(snapshot, "ARCHIVE.json")
    if os.path.isfile(pointer_path):
        try:
            with open(pointer_path, encoding="utf-8") as fh:
                pointer = json.load(fh)
        except (ValueError, OSError) as exc:
            raise SystemExit(f"REFUSED: invalid archive pointer: {exc}") from exc
        if (not isinstance(pointer, dict)
                or pointer.get("index_sha256") != digest
                or pointer.get("archived_relpath") != _rel_snapshot(snapshot)):
            raise SystemExit("REFUSED: archive pointer and raw INDEX disagree")
    seen: set[str] = set()
    for row in index:
        if not isinstance(row, dict):
            raise SystemExit("REFUSED: raw INDEX has a non-object row")
        path, source_id = row.get("path"), row.get("source_id")
        if not isinstance(path, str) or not isinstance(source_id, str):
            raise SystemExit("REFUSED: raw INDEX has invalid source/path")
        pieces = path.split("/")
        if (len(pieces) != 3 or pieces[0] != "raw" or pieces[1] != source_id
                or not re.fullmatch(r"[A-Za-z0-9._#-]+", source_id)
                or source_id in (".", "..")
                or not re.fullmatch(r"[0-9]{3,}\.json", pieces[2])
                or path in seen):
            raise SystemExit("REFUSED: unsafe or duplicate raw INDEX path")
        seen.add(path)
        if not isinstance(row.get("file_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", row["file_sha256"]):
            raise SystemExit("REFUSED: invalid raw body wrapper digest in INDEX")
    return index


def _body_paths(snapshot: str, dest_root: str | None, relative: str) -> tuple[str, str | None]:
    src = os.path.join(snapshot, *relative.split("/"))
    if not _inside(src, os.path.join(snapshot, "raw")):
        raise SystemExit("REFUSED: raw INDEX source escapes the snapshot (possibly symlinked)")
    dst = os.path.join(dest_root, *relative.split("/")) if dest_root else None
    if dst and not _inside(dst, dest_root):
        raise SystemExit("REFUSED: raw INDEX archive destination escapes archive root")
    return src, dst


def move(snapshot: str, archive_root: str) -> int:
    _require_off_tree_archive(archive_root)
    index = _load_index(snapshot)
    rel = _rel_snapshot(snapshot)
    dest_root = os.path.join(archive_root, rel)
    # Preflight ALL entries before moving ANY one, so late corruption cannot
    # leave a half-migrated archive with no reliable pointer.
    plan = []
    for row in index:
        src, dst = _body_paths(snapshot, dest_root, row["path"])
        if not os.path.isfile(src) and not os.path.isfile(dst):
            raise SystemExit(f"REFUSED: {row['path']} is neither in snapshot nor archive")
        for existing in (src, dst):
            if os.path.isfile(existing) and _sha256(existing) != row["file_sha256"]:
                raise SystemExit(f"REFUSED: {existing} differs from frozen raw INDEX; nothing moved")
        plan.append((src, dst))
    moved = 0
    for src, dst in plan:
        if os.path.isfile(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            moved += 1
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
    if root is not None:
        _require_off_tree_archive(root)
    rel = _rel_snapshot(snapshot)
    problems: list[str] = []
    ok = 0
    for row in index:
        local, archived = _body_paths(
            snapshot, os.path.join(root, rel) if root else None, row["path"]
        )
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
