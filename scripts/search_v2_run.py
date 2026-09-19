"""search_v2 labelled run driver: refresh a set of topics into their own snapshot generation, archive the raw
bodies to a GitHub release, and write ONE candidate file for the run with every topic's state named.

WHY (2026-09-15). The first sealed measurement (snapshot 2026-09-15-search_v2, engine blob 3652170) had 5 of 21
topics RAN_ERROR (the guard refused registered vocabulary) and 295 of 299 source-level RAN_ERRORs were Europe PMC
503s concentrated on the citation-chasing routes, so that route was mostly NOT measured. A re-run after the guard
rule (docs/evidence/search-v2-guard-2026-09-15/PROTOCOL.md) is a second generation of snapshots, kept BESIDE the
first (never overwriting it), on ONE engine blob for every topic in the run, with the previous run's row for each
topic carried in the candidate file so both answers stay visible.

States per topic (never folded): RAN_OK (every source RAN_OK/RAN_ZERO), RAN_OK_WITH_SOURCE_ERRORS (>= 1 source
RAN_ERROR, named), RAN_ZERO (ran, zero candidates), RAN_ERROR (the refresh raised; error + traceback recorded),
NOT_RUN (not attempted in this run).

Usage:
  python scripts/search_v2_run.py refresh --run-date <today-UTC> --label r2 --topics all|measurement|development|<slug,...>
        [--registries ctgov,isrctn] [--release raw-archive-2026-09-15r2-search_v2]
        [--archive-root C:/claude-tmp/arch] [--no-upload] [--tar-only]
  python scripts/search_v2_run.py status --label r2
Resumable: a topic whose snapshot already has records.json + retrieval_ledger.json is reused, not re-fetched.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import traceback

if __name__ == "__main__":  # never at import: a module-level stdout swap closes the importer's stream
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import search_v2  # noqa: E402
from scripts import archive_raw_bodies  # noqa: E402
from scripts.measure_search_v2_measurement import ROUTE_LABELS  # noqa: E402  (one route vocabulary for both runs)

FIRST_RUN_DATE = "2026-09-15"
SPLIT_PATH = os.path.join(ROOT, "registry", "search_benchmark_split.json")
FIRST_RUN_CANDIDATES = {
    "MEASUREMENT": os.path.join(ROOT, "outputs", "search_v2", "candidates-2026-09-15-measurement.json"),
    "DEVELOPMENT": os.path.join(ROOT, "outputs", "search_v2", "candidates-2026-09-15.json"),
}


def _utc() -> str:
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", ROOT, *args], text=True).strip()


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _archive_paths(slug: str, snapshot_dir: str, archive_root: str) -> tuple[str, str, str, str]:
    rel = os.path.relpath(snapshot_dir, ROOT).replace("\\", "/")
    body_root = os.path.join(archive_root, rel)
    asset = f"raw-{slug}-{os.path.basename(snapshot_dir)}.tar.gz"
    tar_path = os.path.join(archive_root, asset)
    return rel, body_root, asset, tar_path


def _tar_body_root(body_root: str, rel: str, tar_path: str) -> tuple[int, str]:
    os.makedirs(os.path.dirname(tar_path), exist_ok=True)
    with tarfile.open(tar_path, "w:gz") as tf:
        tf.add(body_root, arcname=rel)
    return os.path.getsize(tar_path), _sha256_file(tar_path)


def _delete_moved_bodies(body_root: str, archive_root: str) -> None:
    body_root_abs = os.path.abspath(body_root)
    archive_root_abs = os.path.abspath(archive_root)
    if os.path.commonpath([body_root_abs, archive_root_abs]) != archive_root_abs:
        raise SystemExit(f"REFUSED: moved-body path escapes archive root: {body_root}")
    if os.path.isfile(body_root_abs):
        raise SystemExit(f"REFUSED: moved-body path is not a directory: {body_root}")
    shutil.rmtree(body_root_abs)


def _split() -> dict[str, str]:
    data = json.load(open(SPLIT_PATH, encoding="utf-8"))
    return {slug: row["set"] for slug, row in (data.get("assignments") or {}).items()}


def _topics_arg(value: str) -> list[str]:
    split = _split()
    if value == "all":
        return sorted(split)
    if value == "measurement":
        return sorted(s for s, v in split.items() if v == "MEASUREMENT")
    if value == "development":
        return sorted(s for s, v in split.items() if v == "DEVELOPMENT")
    slugs = [s.strip() for s in value.split(",") if s.strip()]
    unknown = [s for s in slugs if s not in split]
    if unknown:
        raise SystemExit(f"unknown slugs (not in the sealed split): {unknown}")
    return slugs


def _registries_arg(value: str) -> tuple[str, ...]:
    registries = tuple(s.strip().lower() for s in value.split(",") if s.strip())
    if not registries:
        raise SystemExit("REFUSED: --registries must name at least one registry")
    search_v2._registry_set(registries)
    return registries


def _dated_label(label: str) -> str:
    if len(label) > 10:
        try:
            datetime.date.fromisoformat(label[:10])
            return label
        except ValueError:
            pass
    return FIRST_RUN_DATE + label


def _snapshot_name(label: str) -> str:
    return f"{_dated_label(label)}-{search_v2.SNAPSHOT_SUFFIX}"


def _candidate_path(label: str, scope: str) -> str:
    return os.path.join(ROOT, "outputs", "search_v2", f"candidates-{_dated_label(label)}-{scope}.json")


def _previous_row(slug: str, split: str) -> dict | None:
    path = FIRST_RUN_CANDIDATES.get(split)
    if not path or not os.path.exists(path):
        return None
    data = json.load(open(path, encoding="utf-8"))
    if split == "MEASUREMENT":
        row = (data.get("topics") or {}).get(slug)
        if not row:
            return None
        return {"candidate_file": os.path.relpath(path, ROOT).replace("\\", "/"), "engine_sha": data.get("engine_sha"),
                "state": row.get("state"), "error": row.get("error"), "candidate_count": row.get("candidate_count"),
                "sources_ran_error": sum(1 for s in (row.get("sources") or []) if s.get("state") == "RAN_ERROR"),
                "sources": len(row.get("sources") or [])}
    items = (data.get("topics") or {}).get(slug)
    if items is None:
        return None
    return {"candidate_file": os.path.relpath(path, ROOT).replace("\\", "/"), "engine_sha": data.get("engine_sha"),
            "state": "RAN (development run; per-source states in its snapshot ledger)", "candidate_count": len(items)}


def _topic_row(slug: str, split: str, row: dict, snapshot_dir: str) -> tuple[list[dict], dict]:
    records_dict = row["records"]
    ledger = row["ledger"]
    source_map = {s["source_id"]: s for s in ledger.get("sources") or []}
    candidates = []
    for rec in records_dict.get("records") or []:
        cid, id_type = search_v2._candidate_id(rec)
        found_by = rec.get("found_by") or []
        kinds = sorted({source_map.get(sid, {}).get("kind", sid) for sid in found_by})
        labels = []
        for kind in kinds:
            lab = ROUTE_LABELS.get(str(kind), str(kind))
            if lab not in labels:
                labels.append(lab)
        candidates.append({
            "id": cid, "id_type": id_type,
            "pmid": rec.get("pmid") or (cid if id_type == "pmid" else ""),
            "nct": rec.get("nct") or (cid if id_type == "nct" else ""),
            "doi": rec.get("doi") or "", "title": rec.get("title") or "",
            "found_by": found_by, "found_by_kinds": kinds,
            "found_by_routes": labels or ["unrouted"], "route": " | ".join(labels) or "unrouted",
        })
    sources = [{"source_id": s.get("source_id"), "kind": s.get("kind"), "state": s.get("state"), "error": s.get("error"),
                "funnel": s.get("funnel"), "record_count": len(s.get("record_ids") or [])} for s in ledger.get("sources") or []]
    n_err = sum(1 for s in sources if s.get("state") == "RAN_ERROR")
    if n_err:
        state = "RAN_OK_WITH_SOURCE_ERRORS"
    elif not candidates:
        state = "RAN_ZERO"
    else:
        state = "RAN_OK"
    meta = {
        "split": split, "state": state,
        "sources_total": len(sources), "sources_ran_error": n_err,
        "sources_ran_error_by_kind": _count_by(s["kind"] for s in sources if s.get("state") == "RAN_ERROR"),
        "snapshot_dir": os.path.relpath(snapshot_dir, ROOT).replace("\\", "/"),
        "candidate_count": len(candidates), "sources": sources,
        "screen_summary": (records_dict.get("search_v2") or {}).get("screen_summary"),
        "vocabulary_exemption": ((records_dict.get("search_v2") or {}).get("queries") or {}).get("vocabulary_exemption"),
    }
    return candidates, meta


def _count_by(items) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in items:
        out[item] = out.get(item, 0) + 1
    return dict(sorted(out.items()))


def _archive_and_upload(
    slug: str,
    snapshot_dir: str,
    archive_root: str,
    release: str | None,
    log,
    *,
    tar_only: bool = False,
) -> dict:
    """Move raw bodies off-tree, tar them, upload to the release, verify the remote asset by size, then free the
    local copies. Returns the public_archive block for ARCHIVE.json; on any failure returns a NOT-PRESERVED record
    rather than raising (the snapshot itself is already written and valid)."""
    rel, body_root, asset, tar_path = _archive_paths(slug, snapshot_dir, archive_root)
    try:
        moved = archive_raw_bodies.move(snapshot_dir, archive_root)
    except SystemExit as exc:
        return {"status": "ARCHIVE-MOVE-REFUSED", "detail": str(exc)}
    log(f"archived {moved} raw bodies from {rel}")
    if tar_only:
        size, sha = _tar_body_root(body_root, rel, tar_path)
        _delete_moved_bodies(body_root, archive_root)
        return {
            "status": "TAR-ONLY-UPLOAD-PENDING",
            "asset": asset,
            "tar_sha256": sha,
            "tar_bytes": size,
            "local_tar": tar_path,
            "github_release": release or f"raw-archive-{os.path.basename(snapshot_dir)}",
        }
    if not release:
        return {"status": "LOCAL-ONLY", "archive_root": archive_root}
    size, sha = _tar_body_root(body_root, rel, tar_path)
    try:
        subprocess.run(["gh", "release", "upload", release, tar_path, "--clobber"], check=True, capture_output=True, text=True)
        view = subprocess.check_output(["gh", "release", "view", release, "--json", "assets"], text=True)
        remote = next((a for a in json.loads(view).get("assets") or [] if a.get("name") == asset), None)
    except (subprocess.CalledProcessError, OSError, ValueError) as exc:
        return {"status": "UPLOAD-FAILED", "asset": asset, "tar_sha256": sha, "tar_bytes": size, "detail": str(exc)[:500],
                "local_tar": tar_path}
    if not remote or int(remote.get("size") or -1) != size:
        return {"status": "UPLOAD-UNVERIFIED", "asset": asset, "tar_sha256": sha, "tar_bytes": size,
                "remote_size": (remote or {}).get("size"), "local_tar": tar_path}
    log(f"uploaded {asset} bytes={size} sha256={sha[:16]} remote_size={remote['size']}")
    os.remove(tar_path)
    shutil.rmtree(body_root, ignore_errors=True)
    return {"status": "RELEASE-ASSET-VERIFIED-BY-SIZE", "github_release": release, "asset": asset, "tar_sha256": sha,
            "tar_bytes": size, "url": f"https://github.com/mahmood726-cyber/meta-harness/releases/tag/{release}",
            "local_mirror": "NONE (deleted after the remote size matched; disk); the release asset and the in-tree "
                            "raw/INDEX.json digests are the only custody"}


def _write_archive_pointer(snapshot_dir: str, public: dict) -> None:
    path = os.path.join(snapshot_dir, "ARCHIVE.json")
    pointer = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    pointer["public_archive"] = public
    if public.get("status") == "RELEASE-ASSET-VERIFIED-BY-SIZE":
        pointer["custody"] = ("raw bodies published as a GitHub release asset (tar_sha256 recorded here; verify the fetched "
                              "bytes against it); NO local mirror retained; raw/INDEX.json digests in-tree are the authority; "
                              "a body the release cannot produce reads NOT PRESERVED")
    elif public.get("status") == "TAR-ONLY-UPLOAD-PENDING":
        pointer["custody"] = "tarball held locally pending upload; digests in-tree are the authority"
    else:
        pointer["custody"] = f"raw bodies NOT PRESERVED publicly ({public.get('status')}); see public_archive.detail"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(pointer, f, indent=1)
        f.write("\n")


def refresh(
    label: str,
    topics: list[str],
    scope: str,
    archive_root: str,
    release: str | None,
    registries: tuple[str, ...],
    *,
    tar_only: bool = False,
    run_date: str | None = None,
) -> int:
    today = datetime.datetime.now(datetime.UTC).date().isoformat()
    if run_date != today:
        raise SystemExit(f"REFUSED: --run-date must equal today's UTC date {today}")
    dated = _dated_label(label)
    if dated != FIRST_RUN_DATE + label and dated[:10] != run_date:
        raise SystemExit("REFUSED: date-prefixed label disagrees with UTC run date")
    label = label if dated != FIRST_RUN_DATE + label else run_date + label
    split = _split()
    snapshot_name = _snapshot_name(label)
    out_path = _candidate_path(label, scope)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    payload = json.load(open(out_path, encoding="utf-8")) if os.path.exists(out_path) else {
        "_doc": ("search_v2 labelled run. One engine blob for every topic in the run; each topic's previous-run row is "
                 "carried in topics[slug].previous_run; RAN_ERROR is recorded with its traceback and never re-run patched."),
        "run_label": label, "snapshot_name": snapshot_name, "snapshot_date": run_date, "scope": scope,
        "registries": registries,
        "engine_sha": _git("hash-object", "--", "harness/search_v2.py"), "base_commit": _git("rev-parse", "HEAD"),
        "guard_protocol": "docs/evidence/search-v2-guard-2026-09-15/PROTOCOL.md",
        "started_utc": _utc(), "topics_requested": topics, "candidates": {}, "topics": {},
    }
    if tuple(payload.get("registries") or ()) != registries:
        raise SystemExit(f"REFUSED: candidate file registries {payload.get('registries')} do not match {list(registries)}")
    engine_now = _git("hash-object", "--", "harness/search_v2.py")
    if payload["engine_sha"] != engine_now:
        raise SystemExit(f"REFUSED: engine blob changed mid-run ({payload['engine_sha'][:12]} -> {engine_now[:12]}); "
                         f"a run is one engine. Start a new label.")
    log_path = os.path.join(ROOT, "outputs", "search_v2", f"run-{label}.log")

    def log(msg: str) -> None:
        line = f"{_utc()} {msg}"
        print(line, flush=True)
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    for slug in topics:
        prev = payload["topics"].get(slug)
        if prev and prev.get("state") not in (None, "NOT_RUN"):
            log(f"skip {slug}: already {prev['state']} in this run")
            continue
        snapshot_dir = os.path.join(ROOT, "cache", slug, "snapshots", snapshot_name)
        existing = search_v2.load_snapshot(slug, label)
        log(f"refresh {slug} ({split[slug]}) -> {snapshot_name}" + (" [reusing existing snapshot]" if existing else ""))
        try:
            row = existing or search_v2.refresh_topic(slug, run_date, snapshot_name=snapshot_name, registries=registries)
            candidates, meta = _topic_row(slug, split[slug], row, snapshot_dir)
        except Exception as exc:  # noqa: BLE001 - lane rule: record the row, never patch and rerun.
            candidates, meta = [], {"split": split[slug], "state": "RAN_ERROR", "error": str(exc),
                                    "traceback": traceback.format_exc(), "candidate_count": 0, "sources": []}
            log(f"RAN_ERROR {slug}: {exc}")
        else:
            if not existing and os.path.isdir(os.path.join(snapshot_dir, "raw")):
                public = _archive_and_upload(slug, snapshot_dir, archive_root, release, log, tar_only=tar_only)
                _write_archive_pointer(snapshot_dir, public)
                meta["raw_archive"] = public
            elif existing:
                ap = os.path.join(snapshot_dir, "ARCHIVE.json")
                meta["raw_archive"] = (json.load(open(ap, encoding="utf-8")).get("public_archive") if os.path.exists(ap) else {"status": "NO-ARCHIVE-POINTER"})
            log(f"done {slug}: {meta['state']} candidates={meta['candidate_count']} sources_ran_error={meta.get('sources_ran_error')}")
        meta["previous_run"] = _previous_row(slug, split[slug])
        meta["finished_utc"] = _utc()
        payload["candidates"][slug] = candidates
        payload["topics"][slug] = meta
        payload["updated_utc"] = _utc()
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    states = _count_by(m["state"] for m in payload["topics"].values())
    not_run = [s for s in topics if s not in payload["topics"]]
    log(f"RUN {label} scope={scope}: states={states} NOT_RUN={len(not_run)} of {len(topics)} -> {os.path.relpath(out_path, ROOT)}")
    return 0


def status(label: str, scope: str) -> int:
    out_path = _candidate_path(label, scope)
    if not os.path.exists(out_path):
        print(f"no candidate file for label {label} scope {scope}")
        return 1
    payload = json.load(open(out_path, encoding="utf-8"))
    for slug in payload.get("topics_requested") or sorted(payload["topics"]):
        m = payload["topics"].get(slug)
        if not m:
            print(f"{slug:42s} NOT_RUN")
            continue
        arch = (m.get("raw_archive") or {}).get("status")
        print(f"{slug:42s} {m['state']:26s} candidates={m.get('candidate_count'):6d} src_err={m.get('sources_ran_error')} archive={arch}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("refresh")
    r.add_argument("--label", required=True)
    r.add_argument("--run-date", required=True, help="must equal today in UTC")
    r.add_argument("--topics", required=True)
    r.add_argument("--scope", default=None, help="name for the candidate file (default: the --topics word)")
    r.add_argument("--registries", default="ctgov", help="comma-separated registry adapters to run: ctgov,isrctn")
    r.add_argument("--archive-root", default=os.environ.get("META_HARNESS_RAW_ARCHIVE", "C:/claude-tmp/arch"))
    r.add_argument("--release", default=None)
    r.add_argument("--no-upload", action="store_true")
    r.add_argument("--tar-only", action="store_true", help="create local tar assets and record upload-pending custody")
    s = sub.add_parser("status")
    s.add_argument("--label", required=True)
    s.add_argument("--scope", required=True)
    args = ap.parse_args(argv)
    if args.cmd == "refresh":
        scope = args.scope or (args.topics if args.topics in ("all", "measurement", "development") else "subset")
        return refresh(
            args.label,
            _topics_arg(args.topics),
            scope,
            args.archive_root,
            None if args.no_upload else args.release,
            _registries_arg(args.registries),
            tar_only=args.tar_only,
            run_date=args.run_date,
        )
    if args.cmd == "status":
        return status(args.label, args.scope)
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    sys.exit(main())
