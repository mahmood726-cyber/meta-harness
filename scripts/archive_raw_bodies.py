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
import base64
import binascii
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
    raw_root = os.path.join(snapshot, "raw")
    # Resolve the evidence *container* as well as each numbered body. Without
    # this guard a symlinked raw/ directory can place INDEX and every body
    # outside the snapshot while _body_paths compares each source to the same
    # escaped raw/ directory and accepts it as an in-snapshot file.
    if (os.path.islink(raw_root) or not os.path.isdir(raw_root)
            or not _inside(raw_root, snapshot)
            or os.path.islink(p) or os.path.islink(ledger_path)):
        raise SystemExit("REFUSED: raw evidence directory/index/ledger must be in-snapshot, non-symlink files")
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
    # Treat a linked, dangling, or non-file custody receipt as tampering, not
    # as an absent receipt. In particular a dangling symlink must not turn an
    # archived snapshot back into an apparently unarchived local-only PASS.
    if os.path.islink(pointer_path) or (os.path.lexists(pointer_path) and not os.path.isfile(pointer_path)):
        raise SystemExit("REFUSED: ARCHIVE.json custody receipt must be a regular non-symlink file")
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
        if not isinstance(row.get("body_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", row["body_sha256"]):
            raise SystemExit("REFUSED: missing or malformed HTTP body digest in raw INDEX")
    return index


def _refuse_symlinked_evidence(path: str, base: str) -> None:
    """Every raw body must be a regular copy, not a link to another body.

    Resolving inside the expected directory is not sufficient: a same-tree
    symbolic link can make two indexed HTTP responses share one physical file.
    Archive checks must be able to establish that each numbered body exists
    independently at its declared path. The caller separately checks digests.
    """
    rel = os.path.relpath(path, base)
    probe = base
    for part in rel.split(os.sep):
        probe = os.path.join(probe, part)
        if os.path.islink(probe):
            raise SystemExit("REFUSED: raw evidence path contains a symlink")


def _refuse_hardlinked_body(path: str) -> None:
    """Refuse raw-response aliases that do not use symbolic links.

    Hardlinks can make two indexed HTTP calls (or an indexed call and an
    unindexed path) share one physical file despite having different names.
    An archive PASS must not imply separate preserved response files where
    this cannot be demonstrated. This is an engineering custody safeguard,
    not proof of independent external evidence retention.
    """
    if os.path.isfile(path) and os.stat(path).st_nlink > 1:
        raise SystemExit("REFUSED: raw evidence body has multiple hardlinks")


def _raw_wrapper_matches_index(path: str, row: dict) -> bool:
    """Verify the decoded HTTP bytes, not merely the surrounding JSON file hash.

    RawRecorder.write_snapshot stores base64 HTTP response bytes inside each
    wrapper. INDEX.file_sha256 authenticates the wrapper bytes relative to
    the ledger, but does not establish that the actual response bytes match
    INDEX.body_sha256 or that the wrapper belongs to the indexed API call.
    Refuse missing, malformed or inconsistent inner evidence. The in-tree
    ledger remains self-attested; this is NOT independent custody.
    """
    try:
        with open(path, "rb") as fh:
            payload = json.load(fh)
        if not isinstance(payload, dict) or not isinstance(payload.get("body_bytes_b64"), str):
            return False
        body = base64.b64decode(payload["body_bytes_b64"], validate=True)
        if hashlib.sha256(body).hexdigest() != row["body_sha256"]:
            return False
        if payload.get("body_sha256") != row["body_sha256"]:
            return False
        for field in ("source_id", "url", "params", "status", "fetched_utc",
                      "adapter", "adapter_blob_sha"):
            if payload.get(field) != row.get(field):
                return False
    except (OSError, ValueError, TypeError, UnicodeError, binascii.Error):
        return False
    return True


def _body_paths(snapshot: str, dest_root: str | None, relative: str) -> tuple[str, str | None]:
    # The top-level archive may be off-tree while a nested symlink redirects
    # the snapshot destination back into the repository. Verify the resolved
    # destination root too, on both move and check paths.
    if dest_root is not None:
        _require_off_tree_archive(dest_root)
    src = os.path.join(snapshot, *relative.split("/"))
    if not _inside(src, os.path.join(snapshot, "raw")):
        raise SystemExit("REFUSED: raw INDEX source escapes the snapshot (possibly symlinked)")
    _refuse_symlinked_evidence(src, snapshot)
    dst = os.path.join(dest_root, *relative.split("/")) if dest_root else None
    if dst and not _inside(dst, dest_root):
        raise SystemExit("REFUSED: raw INDEX archive destination escapes archive root")
    if dst:
        _refuse_symlinked_evidence(dst, dest_root)
    # File-level hardlinks evade realpath/containment and symlink checks.
    # Refuse even digest-identical aliases before check or move.
    _refuse_hardlinked_body(src)
    if dst:
        _refuse_hardlinked_body(dst)
    return src, dst


def move(snapshot: str, archive_root: str) -> int:
    _require_off_tree_archive(archive_root)
    # ARCHIVE.json is the custody receipt. An ordinary second move must never
    # replace its original location or timestamp, even when no bodies remain
    # locally. Deliberate archive migration requires a separately reviewed
    # procedure that retains the original custody history.
    if os.path.lexists(os.path.join(snapshot, "ARCHIVE.json")):
        raise SystemExit("REFUSED: ARCHIVE.json already exists; audited archive migration required")
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
            if os.path.isfile(existing):
                if (_sha256(existing) != row["file_sha256"]
                        or not _raw_wrapper_matches_index(existing, row)):
                    raise SystemExit(f"REFUSED: {row['path']} raw wrapper or HTTP body differs from frozen INDEX; nothing moved")
        plan.append((src, dst))
    moved = 0
    for src, dst in plan:
        if os.path.isfile(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            moved += 1
    # Preflight checks precede the filesystem writes. A racing modification,
    # interrupted move, or corrupted destination could otherwise be followed
    # by an ARCHIVE.json custody receipt without checking the archived bytes.
    # Refuse receipt issuance until every final off-tree file is present and
    # still matches both the indexed wrapper and decoded HTTP response.
    for row in index:
        src, dst = _body_paths(snapshot, dest_root, row["path"])
        if (os.path.isfile(src) or not os.path.isfile(dst)
                or _sha256(dst) != row["file_sha256"]
                or not _raw_wrapper_matches_index(dst, row)):
            raise SystemExit(
                f"REFUSED: post-move archive integrity failed for {row['path']}; "
                "custody receipt not issued; inspect partial move manually"
            )
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
    # An arbitrary matching off-tree copy is not evidence of recorded custody.
    # With no ARCHIVE.json, verify local raw bytes only; never let a caller
    # supply an unregistered archive directory and obtain a preservation PASS.
    if pointer is None and archive_root is not None:
        raise SystemExit("REFUSED: off-tree archive check requires an ARCHIVE.json custody receipt")
    # ARCHIVE.json records the claimed custody location. An explicit check
    # root must not substitute a different archive whose matching bytes conceal
    # a missing/corrupt body at the location actually declared by the pointer.
    if pointer is not None:
        pinned_root = pointer.get("archive_root")
        if not isinstance(pinned_root, str) or not pinned_root.strip():
            raise SystemExit("REFUSED: ARCHIVE.json has no valid archive_root")
        _require_off_tree_archive(pinned_root)
        if (archive_root is not None
                and os.path.realpath(archive_root) != os.path.realpath(pinned_root)):
            raise SystemExit("REFUSED: archive root override differs from ARCHIVE.json")
        root = pinned_root
    else:
        root = archive_root
    if root is not None:
        _require_off_tree_archive(root)
    rel = _rel_snapshot(snapshot)
    problems: list[str] = []
    ok = 0
    for row in index:
        local, archived = _body_paths(
            snapshot, os.path.join(root, rel) if root else None, row["path"]
        )
        has_local = os.path.isfile(local)
        has_archived = bool(archived and os.path.isfile(archived))
        if not has_local and not has_archived:
            problems.append(f"NOT PRESERVED: {row['path']} (not in snapshot; not in archive {root})")
            continue
        # A surviving local copy must not certify an archive declared by
        # ARCHIVE.json if the off-tree body has disappeared. This is storage
        # verification, not a claim of independently held evidence.
        if pointer and pointer.get("archive_root") and not has_archived:
            problems.append(f"NOT PRESERVED OFF-TREE: {row['path']} (archive body missing)")
            continue
        # Verify *every* existing copy: local-first selection used to hide
        # damaged off-tree bodies whenever an intact local copy remained.
        copies = ([local] if has_local else []) + ([archived] if has_archived else [])
        if any(_sha256(path) != row["file_sha256"]
               or not _raw_wrapper_matches_index(path, row) for path in copies):
            problems.append(f"RAW RESPONSE MISMATCH: {row['path']} (wrapper, metadata or decoded HTTP body)")
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
