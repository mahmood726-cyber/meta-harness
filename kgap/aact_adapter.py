"""AACT SNAPSHOT ADAPTER: posted CT.gov results as a PRIMARY source (Mahmood decision 2 Oct, 2a). SHARED G1 INTERFACE.

A versioned local AACT snapshot (pipe-delimited flat files) is read for a set of NCTs into a typed index:

    registry_for(nct) -> {
        "_snapshot":    {"id": "AACT 2026-08-30", "digest": <sha256 over the files read>},
        "outcomes":     {outcome_id: {title, time_frame, type, population, units_analyzed}},
        "analyses":     [{outcome_id, param_type, param_value, ci_lower, ci_upper}],
        "groups":       {outcome_id: [{group, count, n}]},     # arm counts: COUNT/NUMBER measurements x 'measure' N
        "group_titles": {result_group_id: title},
    } | None    (None: the NCT has no posted outcomes in this snapshot)

    ensure(ncts)            index every NCT not yet held (ONE streaming pass over the files for the missing set)
    snapshot()              {"id", "digest", "files": {name: {size, mtime, sha256}}} (digest cached by size+mtime)

The index lives at $KGAP_AACT_INDEX or outputs/k_gap/_aact_results.json (gitignored: it is derived data). An index
built from a DIFFERENT snapshot digest is never mixed with this one: ensure() rebuilds it whole. The snapshot
directory is $AACT_SNAPSHOT or the default below; a missing snapshot raises (fail closed), it never returns empty.

Consumers: scripts/secondary_meta_build.primary_sources (typed verification) and harness.secondary_meta
.typed_match_registry / registry_fields / registry_vs_publication (the typed comparison).

    python -m kgap.aact_adapter NCT01179048 NCT04320615 ...
"""
from __future__ import annotations

import csv
import re
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SNAPSHOT = "F:/AACT-storage/AACT/2026-08-30"
FILES = ("outcomes.txt", "outcome_analyses.txt", "outcome_measurements.txt", "outcome_counts.txt", "result_groups.txt",
         "outcome_analysis_groups.txt")
DIGEST_CACHE = os.path.join(ROOT, "outputs", "k_gap", "aact_snapshot_digest.json")
# The INDEX RULES version is part of every entry's tag: changing how an entry is derived (rules 2: counts only in people
# units, integral; N only in people units) makes every older entry stale, exactly as a new snapshot does.
INDEX_RULES = 3        # 3: every analysis carries the result groups it compares (outcome_analysis_groups)
COUNT_PARAMS = ("COUNT_OF_PARTICIPANTS", "NUMBER", "COUNT_OF_UNITS")
# An arm's EVENT COUNT is an integral value in PEOPLE units. 'NUMBER 63.6 percentage of patients' (NCT03794349) is a
# rate, not 63 events; a Kaplan-Meier percentage is never a count. The N is the 'measure' scope count in people units
# ('Participants'), never 'Patient-months' or 'Eyes'.
PEOPLE_UNITS = re.compile(r"^\s*(?:number of |count of )?(?:participants?|subjects?|patients?|people|persons?|"
                          r"individuals?)\s*$", re.I)
csv.field_size_limit(10 ** 8)


def snapshot_dir():
    d = os.environ.get("AACT_SNAPSHOT") or DEFAULT_SNAPSHOT
    missing = [f for f in FILES if not os.path.exists(os.path.join(d, f))]
    if missing:
        raise FileNotFoundError(f"AACT snapshot {d} lacks {missing}: set AACT_SNAPSHOT (fail closed, never empty)")
    return d


def index_path():
    return os.environ.get("KGAP_AACT_INDEX") or os.path.join(ROOT, "outputs", "k_gap", "_aact_results.json")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _dir_id(d):
    """The snapshot DIRECTORY's identity for the hash cache, as a digest (a committed file never carries a local path)."""
    return hashlib.sha256(os.path.abspath(d).replace("\\", "/").lower().encode("utf-8")).hexdigest()[:16]


def snapshot():
    """The snapshot's identity: its version AND a sha256 per file read, cached against size+mtime (the 3 GB file is
    hashed once). digest = sha256 over the file names + their hashes, in FILES order."""
    d = snapshot_dir()
    old = _j(DIGEST_CACHE) if os.path.exists(DIGEST_CACHE) else {}
    files = {}
    for f in FILES:
        st = os.stat(os.path.join(d, f))
        # a cached hash is reused only for the SAME directory: two snapshots with one basename, equal sizes and equal
        # mtimes must not share an identity
        prev = ((old.get("files") or {}).get(f) or {}) if old.get("dir_sha256") == _dir_id(d) else {}
        if prev.get("size") == st.st_size and prev.get("mtime") == int(st.st_mtime) and prev.get("sha256"):
            files[f] = prev
            continue
        h = hashlib.sha256()
        with open(os.path.join(d, f), "rb") as fh:
            for blk in iter(lambda: fh.read(1 << 22), b""):
                h.update(blk)
        files[f] = {"size": st.st_size, "mtime": int(st.st_mtime), "sha256": h.hexdigest()}
    out = {"id": "AACT " + os.path.basename(d.rstrip("/\\")), "dir_sha256": _dir_id(d),
           "digest": hashlib.sha256("".join(f + files[f]["sha256"] for f in FILES).encode()).hexdigest(),
           "files": files}
    if out != old:
        with open(DIGEST_CACHE, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1)
    return out


def _rows(name, want):
    with open(os.path.join(snapshot_dir(), name), encoding="utf-8", errors="replace", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="|", quoting=csv.QUOTE_NONE):
            if r.get("nct_id") in want:
                yield r


def build_entries(ncts, tag):
    """One streaming pass over the snapshot for `ncts`: the typed entry per NCT (see module docstring)."""
    want = set(ncts)
    idx = {n: {"_snapshot": tag, "outcomes": {}, "analyses": [], "groups": {}, "group_titles": {}} for n in want}
    for r in _rows("outcomes.txt", want):
        idx[r["nct_id"]]["outcomes"][r["id"]] = {"title": r.get("title"), "time_frame": r.get("time_frame"),
                                                 "type": r.get("outcome_type"), "population": r.get("population"),
                                                 "units_analyzed": r.get("units_analyzed")}
    for r in _rows("result_groups.txt", want):
        if (r.get("result_type") or "").lower() == "outcome":
            idx[r["nct_id"]]["group_titles"][r["id"]] = r.get("title")
    # which result groups each analysis compares: RE-LY posts two Cox HRs for stroke/SE (0.65 and 0.90) and only this
    # table says which is dabigatran 150 mg vs warfarin
    agroups = {}
    for r in _rows("outcome_analysis_groups.txt", want):
        agroups.setdefault(r["outcome_analysis_id"], []).append(r["result_group_id"])
    for r in _rows("outcome_analyses.txt", want):
        idx[r["nct_id"]]["analyses"].append({"outcome_id": r["outcome_id"], "param_type": r.get("param_type"),
                                             "param_value": r.get("param_value"), "ci_lower": r.get("ci_lower_limit"),
                                             "ci_upper": r.get("ci_upper_limit"), "analysis_id": r["id"],
                                             "groups": sorted(agroups.get(r["id"], [])),
                                             "groups_description": (r.get("groups_description") or "")[:200]})
    counts, ns = {}, {}
    for r in _rows("outcome_measurements.txt", want):
        # a categorised/classified measurement is one cell of a breakdown, never the arm's event count; the value must
        # be a whole number of PEOPLE (a percentage / proportion / rate is not a count, however it is typed)
        if (r.get("param_type") or "").upper() in COUNT_PARAMS and not (r.get("category") or r.get("classification")) \
                and PEOPLE_UNITS.match(r.get("units") or ""):
            try:
                v = float(r["param_value_num"])
            except (TypeError, ValueError):
                continue
            if v == int(v) and v >= 0:
                counts[(r["nct_id"], r["outcome_id"], r["result_group_id"])] = int(v)
    for r in _rows("outcome_counts.txt", want):
        if (r.get("scope") or "").lower() == "measure" and PEOPLE_UNITS.match(r.get("units") or ""):
            try:
                ns[(r["nct_id"], r["outcome_id"], r["result_group_id"])] = int(r["count"])
            except (TypeError, ValueError):
                pass
    for (n, oid, gid), c in counts.items():
        if (n, oid, gid) in ns:
            idx[n]["groups"].setdefault(oid, []).append({"group": gid, "count": c, "n": ns[(n, oid, gid)]})
    return idx


_CACHE = {}


def _load():
    p = index_path()
    if p not in _CACHE:
        _CACHE[p] = _j(p) if os.path.exists(p) else {}
    return _CACHE[p]


def ensure(ncts):
    """Index every NCT in `ncts` not already held FROM THIS SNAPSHOT. Returns {"added", "held", "snapshot"}."""
    tag = dict({k: v for k, v in snapshot().items() if k in ("id", "digest")}, rules=INDEX_RULES)
    idx = _load()
    stale = [n for n, v in idx.items() if (v or {}).get("_snapshot") != tag]
    if stale:                                     # never mix two snapshots in one index: rebuild the stale entries
        for n in stale:
            idx.pop(n)
    need = sorted({n for n in ncts if str(n).startswith("NCT")} - set(idx))
    if need:
        idx.update(build_entries(need, tag))
        p = index_path()
        os.makedirs(os.path.dirname(p), exist_ok=True)
        # MERGE with what another process wrote since we loaded, then replace atomically: parallel batch workers
        # must never read a half-written index nor drop each other's entries
        if os.path.exists(p):
            for k, v in _j(p).items():
                if k not in idx and (v or {}).get("_snapshot") == tag:
                    idx[k] = v
        tmp = f"{p}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(idx, fh)
        os.replace(tmp, p)
    return {"added": len(need), "rebuilt_stale": len(stale), "held": len(idx), "snapshot": tag}


def registry_for(nct):
    """The typed posted-results entry for one NCT, or None when it has no posted outcomes (or is not indexed:
    call ensure() first -- a lookup never touches the 3 GB files)."""
    v = _load().get(nct)
    return v if v and v.get("outcomes") else None


if __name__ == "__main__":
    print(json.dumps(ensure(sys.argv[1:]), indent=1))
