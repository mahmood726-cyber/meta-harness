"""Search completeness as its own gated stage -- cannot go green on adapter exit codes.

WHY (SEARCH_REBUILD_HANDOVER.md item 4, closed 2026-09-15). A search stage that reports "ran" has reported the
process, not the result. This gate refuses unless the RESULT is on record and current:

  1. ENGINE CURRENCY. registry/search_completeness.json names the candidate file of the published search_v2
     measurement; its engine_sha must equal the blob of harness/search_v2.py in the working tree. An engine change
     without a re-run and a re-publish refuses the standard (the same rule harness/heldout.measurement_current
     applies to the legacy engine).
  2. EVERY MEASUREMENT TOPIC HAS A STATE, and the states are counted separately: RAN_OK, RAN_OK_WITH_SOURCE_ERRORS,
     RAN_ZERO, RAN_ERROR, NOT_RUN. A RAN_ERROR or NOT_RUN topic is named. A topic with zero candidates must be
     RAN_ZERO or RAN_ERROR -- never RAN_OK with nothing (an exit code standing in for a result).
  3. EVERY SOURCE HAS AN EXPLICIT STATE from harness/acquisition.STATES; a RAN_ERROR source carries its error text;
     a RAN_OK source carries at least one record and a RAN_ZERO source none. A source that claims success and
     delivered nothing is the adapter-exit-code failure this gate exists for.
  4. THE MEASURED NUMBER IS PUBLISHED: the sealed-register artefact measured ON search_v2 names the same engine blob
     as the candidate file, and the measurement evidence README names that blob.

The gate reads artefacts only; it never runs a search. Verdicts: PASS with the counted states, or REFUSED with every
violation named.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from . import acquisition as acq

REGISTRY = Path("registry") / "search_completeness.json"
TOPIC_STATES = ("RAN_OK", "RAN_OK_WITH_SOURCE_ERRORS", "RAN_ZERO", "RAN_ERROR", "NOT_RUN")


def _blob(root: Path, rel: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), "hash-object", rel], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"cannot hash {rel}: {(proc.stderr or '').strip()}")
    return proc.stdout.strip()


def _load(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check(root: str | os.PathLike[str]) -> tuple[bool, str]:
    root = Path(root)
    reg_path = root / REGISTRY
    if not reg_path.exists():
        return False, f"COULD-NOT-EXECUTE: {REGISTRY.as_posix()} missing -- no published search_v2 measurement is registered"
    try:
        reg = _load(reg_path)
    except (OSError, ValueError) as exc:
        return False, f"COULD-NOT-EXECUTE: {REGISTRY.as_posix()} unreadable: {exc}"
    problems: list[str] = []
    cand_rel = reg.get("candidate_file")
    engine_rel = reg.get("engine_path") or "harness/search_v2.py"
    split_rel = reg.get("split_file") or "registry/search_benchmark_split.json"
    register_rel = reg.get("register_file")
    readme_rel = reg.get("evidence_readme")
    for rel in (cand_rel, engine_rel, split_rel):
        if not rel or not (root / rel).exists():
            return False, f"COULD-NOT-EXECUTE: registered file missing: {rel}"
    cand = _load(root / cand_rel)
    engine_now = _blob(root, engine_rel)
    engine_measured = str(cand.get("engine_sha") or "")
    # 1. engine currency
    if engine_measured != engine_now:
        problems.append(f"engine changed since the published search_v2 measurement ({engine_measured[:12]} -> {engine_now[:12]}); "
                        f"re-run scripts/search_v2_run.py and re-publish before landing")
    # 2. topic states
    split = _load(root / split_rel).get("assignments") or {}
    measurement = sorted(s for s, v in split.items() if v.get("set") == "MEASUREMENT")
    topics = cand.get("topics") or {}
    counts = {s: 0 for s in TOPIC_STATES}
    named: dict[str, list[str]] = {s: [] for s in TOPIC_STATES}
    for slug in measurement:
        row = topics.get(slug)
        state = (row or {}).get("state") or "NOT_RUN"
        if state not in TOPIC_STATES:
            problems.append(f"{slug}: topic state {state!r} is not one of {TOPIC_STATES}")
            continue
        counts[state] += 1
        named[state].append(slug)
        if row is None:
            continue
        n = int(row.get("candidate_count") or 0)
        if n == 0 and state in ("RAN_OK", "RAN_OK_WITH_SOURCE_ERRORS"):
            problems.append(f"{slug}: state {state} with zero candidates -- an exit code standing in for a result")
        if state == "RAN_ERROR" and not str(row.get("error") or "").strip():
            problems.append(f"{slug}: RAN_ERROR without an error text")
        # 3. source states
        n_err = 0
        for src in row.get("sources") or []:
            sid = src.get("source_id") or "<unknown>"
            st = src.get("state")
            if st not in acq.STATES:
                problems.append(f"{slug}/{sid}: source state {st!r} not in acquisition.STATES")
                continue
            rc = int(src.get("record_count") or 0)
            if st == "RAN_ERROR":
                n_err += 1
                if not str(src.get("error") or "").strip():
                    problems.append(f"{slug}/{sid}: RAN_ERROR without an error text")
            elif st == "RAN_OK" and rc == 0:
                problems.append(f"{slug}/{sid}: RAN_OK with 0 records (adapter exit code, not a result)")
            elif st == "RAN_ZERO" and rc != 0:
                problems.append(f"{slug}/{sid}: RAN_ZERO with {rc} records")
        if n_err and state == "RAN_OK":
            problems.append(f"{slug}: {n_err} sources RAN_ERROR but topic state RAN_OK (source errors folded)")
        if not n_err and state == "RAN_OK_WITH_SOURCE_ERRORS":
            problems.append(f"{slug}: topic state RAN_OK_WITH_SOURCE_ERRORS but no source RAN_ERROR")
    # 4. published
    if register_rel:
        rp = root / register_rel
        if not rp.exists():
            problems.append(f"register artefact missing: {register_rel}")
        else:
            shas = (_load(rp).get("summary") or {}).get("snapshot_engine_shas") or []
            if engine_measured not in shas:
                problems.append(f"{register_rel} was measured on engine {[s[:12] for s in shas]} not {engine_measured[:12]}")
    if readme_rel:
        rd = root / readme_rel
        if not rd.exists():
            problems.append(f"evidence README missing: {readme_rel}")
        else:
            with open(rd, encoding="utf-8") as f:
                if engine_measured not in f.read():
                    problems.append(f"{readme_rel} does not name engine blob {engine_measured[:12]} -- the number is not published")
    state_line = "; ".join(
        f"{s} {counts[s]} of {len(measurement)}" + (f" ({', '.join(named[s])})" if s in ("RAN_ERROR", "NOT_RUN", "RAN_ZERO") and named[s] else "")
        for s in TOPIC_STATES
    )
    if problems:
        return False, "search completeness REFUSED: " + " | ".join(problems) + f" || states: {state_line}"
    return True, f"search_v2 measurement current for engine {engine_now[:12]} ({cand_rel}); states: {state_line}"
