"""RECORD the per-arm posted PERCENTAGES and analysed Ns of chosen AACT outcomes (outputs/k_gap/aact_arm_percentages.json).

A percentage is never a count (kgap/aact_adapter rules 2), so these are never data. They exist for one typed CHECK:
whether a comparator's printed per-arm counts are consistent with what the trial registered (g1_tracker.arm_check) --
e.g. a row whose events were exchanged between arms. outcome_measurements.txt is 3 GB, so the values are extracted once
per outcome and committed; the tracker reads only this file.

    python scripts/aact_arm_percentages.py NCT01131676:258266632 [NCT:OUTCOME_ID ...]
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from kgap import aact_adapter  # noqa: E402

OUTP = os.path.join(ROOT, "outputs", "k_gap", "aact_arm_percentages.json")


def _rows(snap, name):
    csv.field_size_limit(10 ** 8)
    with open(os.path.join(snap, name), encoding="utf-8", errors="replace", newline="") as fh:
        yield from csv.DictReader(fh, delimiter="|", quoting=csv.QUOTE_NONE)


def extract(pairs):
    snap = aact_adapter.snapshot_dir()
    sid = (aact_adapter.snapshot() or {}).get("id")
    oids = {o for _n, o in pairs}
    meas, counts, titles, otitle = {}, {}, {}, {}
    for r in _rows(snap, "outcome_measurements.txt"):
        if r.get("outcome_id") in oids:
            meas.setdefault(r["outcome_id"], []).append(r)
    for r in _rows(snap, "outcome_counts.txt"):
        if r.get("outcome_id") in oids and (r.get("units") or "").lower() == "participants":
            counts[(r["outcome_id"], r["result_group_id"])] = int(r["count"])
    gids = {r["result_group_id"] for v in meas.values() for r in v}
    for r in _rows(snap, "result_groups.txt"):
        if r.get("id") in gids:
            titles[r["id"]] = r.get("title")
    out = {}
    for nct, oid in pairs:
        ms = [r for r in meas.get(oid, []) if r.get("nct_id") == nct]
        if not ms:
            out[f"{nct}:{oid}"] = {"state": "NOT_FOUND", "snapshot": sid}
            continue
        out[f"{nct}:{oid}"] = {
            "state": "RECORDED", "snapshot": sid, "nct": nct, "outcome_id": oid, "outcome_title": ms[0].get("title"),
            "units": ms[0].get("units"), "param_type": ms[0].get("param_type"),
            "groups": [{"group_id": r["result_group_id"], "title": titles.get(r["result_group_id"]),
                        "n_analysed": counts.get((oid, r["result_group_id"])), "value": r.get("param_value")}
                       for r in ms]}
    return out


def main(argv):
    pairs = [tuple(a.split(":", 1)) for a in argv if ":" in a]
    cur = json.load(open(OUTP, encoding="utf-8")) if os.path.exists(OUTP) else {}
    cur.update(extract(pairs))
    with open(OUTP, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(cur, fh, indent=1, sort_keys=True, ensure_ascii=False)
    print(json.dumps({k: (v.get("state"), [(g["title"], g["n_analysed"], g["value"]) for g in v.get("groups") or []])
                      for k, v in cur.items()}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
