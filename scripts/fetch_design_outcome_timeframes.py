"""Record AACT time_frame for every registered-outcome and registry-result row the topics hold (a FETCH-time step; the
offline pipeline replays from the committed sidecars).

  python scripts/fetch_design_outcome_timeframes.py [--snapshot DIR]

harness/family_compact.py keeps design_outcomes as (id, nct_id, measure, outcome_type) and outcomes as (id, nct_id, title),
dropping time_frame, so a registry outcome's TIMEPOINT could never be compared with the target's. This reads the SAME local
AACT snapshot the held rows cite (their `snapshot`), streams design_outcomes.txt and outcomes.txt once each, and writes per
topic cache/<slug>/design_outcome_timeframes.json:
  {source, snapshot_folder, data_current_to, read_utc,
   tables: {<table>: {file, sha256}},
   rows: {<id>: {...}}                  design_outcomes rows (measure, time_frame, population, outcome_type)
   results_rows: {<id>: {...}}}         outcomes rows (title, time_frame, population, outcome_type)
Each row carries row_sha256 = sha256 of the canonical JSON of the columns read, and text_matches_held: whether the
snapshot's measure/title equals the held one (a mismatch is surrogate-id drift; such a row must not be used). The held
family rows are not rewritten (their row_sha256 values stay as served).
"""
from __future__ import annotations

import argparse
import datetime
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import aact  # noqa: E402

TABLES = {"design_outcomes": ("measure", "rows", ("id", "nct_id", "outcome_type", "measure", "time_frame", "population")),
          "outcomes": ("title", "results_rows", ("id", "nct_id", "outcome_type", "title", "time_frame", "population"))}


def _canon(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _held_rows():
    """{slug: {table: {id: (nct_id, text, snapshot)}}} from every topic's family_registry.rows.json.gz."""
    out = {}
    for p in sorted((ROOT / "cache").glob("*/family_registry.rows.json.gz")):
        rows = json.loads(gzip.open(p, "rt", encoding="utf-8").read())
        items = rows if isinstance(rows, list) else (rows.get("rows") or [])
        held = {t: {} for t in TABLES}
        for r in items:
            t = r.get("table")
            if t not in TABLES:
                continue
            inline = r.get("inline") or {}
            rid = str((r.get("row_key") or {}).get("id") or inline.get("id"))
            held[t][rid] = (r.get("nct_id") or inline.get("nct_id"), inline.get(TABLES[t][0]), r.get("snapshot"))
        if any(held.values()):
            out[p.parent.name] = held
    return out


def _stream(path: Path, want: set[str]):
    h, found, header = hashlib.sha256(), {}, None
    with open(path, "rb") as fb:
        for raw in fb:
            h.update(raw)
            line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
            if header is None:
                header = line.split("|")
                continue
            rid = line.split("|", 1)[0]
            if rid in want:
                vals = line.split("|")
                found[rid] = dict(zip(header, vals + [""] * (len(header) - len(vals))))
    return h.hexdigest(), found


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", help="AACT snapshot folder (default: the one the held rows cite)")
    a = ap.parse_args(argv)
    held = _held_rows()
    snaps = {s for tabs in held.values() for rows in tabs.values() for (_, _, s) in rows.values() if s}
    if len(snaps) != 1 and not a.snapshot:
        raise SystemExit(f"refused: held rows cite snapshots {sorted(snaps)}; name one with --snapshot")
    snap = Path(a.snapshot or (Path(aact.snapshot_dir() or "").parent / snaps.pop()))
    tables = {}
    for t in TABLES:
        f = snap / f"{t}.txt"
        if not f.exists():
            raise SystemExit(f"refused: {f} not found (fail closed)")
        want = {rid for tabs in held.values() for rid in tabs[t]}
        tables[t] = (f.name, *_stream(f, want))
    read_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data_to = ("2026-08-27 (measured: max(last_update_submitted_qc_date), AACT_SNAPSHOT_README.md)"
               if snap.name == "2026-08-30" else "NOT_MEASURED")
    stats = {t: [0, 0, 0] for t in TABLES}           # held, found, text drift
    for slug, tabs in held.items():
        doc = {"source": "AACT (local snapshot; ClinicalTrials.gov registry export)", "snapshot_folder": snap.name,
               "data_current_to": data_to, "read_utc": read_utc,
               "tables": {t: {"file": tables[t][0], "sha256": tables[t][1]} for t in TABLES}}
        for t, (text_col, key, cols) in TABLES.items():
            rec = {}
            for rid, (nct, text, _) in sorted(tabs[t].items()):
                stats[t][0] += 1
                r = tables[t][2].get(rid)
                if r is None:
                    rec[rid] = {"nct_id": nct, "state": "ROW_NOT_IN_SNAPSHOT"}
                    continue
                stats[t][1] += 1
                ok = r.get("nct_id") == nct and (r.get(text_col) or "").strip() == (text or "").strip()
                stats[t][2] += not ok
                rec[rid] = {"nct_id": r.get("nct_id"), text_col: r.get(text_col), "outcome_type": r.get("outcome_type"),
                            "time_frame": r.get("time_frame") or None, "population": r.get("population") or None,
                            "text_matches_held": ok,
                            "row_sha256": hashlib.sha256(_canon({c: r.get(c, "") for c in cols}).encode("utf-8")).hexdigest()}
            doc[key] = rec
        (ROOT / "cache" / slug / "design_outcome_timeframes.json").write_text(
            json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"snapshot {snap.name}; read {read_utc}; topics {len(held)}; " + "; ".join(
        f"{t}: held {s[0]}, found {s[1]}, text drift {s[2]}, sha256 {tables[t][1][:16]}" for t, s in stats.items()))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
