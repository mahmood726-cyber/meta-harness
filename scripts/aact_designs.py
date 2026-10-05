"""RECORD the registered DESIGN (allocation, masking, official title) of trials whose blinding our screen could not
read from the record or an open full text (exclusion audit INSUFFICIENT_RECORD:BLINDING_NOT_STATED), linked PMID ->
NCT through AACT's own study_references. outputs/k_gap/aact_designs.json; the tracker reads only this file
(g1_tracker.registered_blinding). The registry row is the held span; nothing here is data.

    python scripts/aact_designs.py            # every BLINDING_NOT_STATED pmid in outputs/k_gap/exclusion_audit.json
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from kgap import aact_adapter, identity_chain as ic  # noqa: E402

OUTP = os.path.join(ROOT, "outputs", "k_gap", "aact_designs.json")


def _rows(snap, name):
    csv.field_size_limit(10 ** 8)
    with open(os.path.join(snap, name), encoding="utf-8", errors="replace", newline="") as fh:
        yield from csv.DictReader(fh, delimiter="|", quoting=csv.QUOTE_NONE)


def main(argv):
    audit = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "exclusion_audit.json"), encoding="utf-8"))
    want = sorted({str(r["pmid"]) for r in audit.get("rows") or []
                   if (r.get("class"), r.get("subclass")) == ("INSUFFICIENT_RECORD", "BLINDING_NOT_STATED")})
    snap = aact_adapter.snapshot_dir()
    sid = (aact_adapter.snapshot() or {}).get("id")
    link = {p: dict(v) for p, v in ic.pmid_to_ncts(want, snap).items()}
    basis = {p: "AACT study_references" for p, v in link.items() if v}
    # no registry citation of the paper: its TITLE names the trial ('... Results From the PARALLEL-HF Study') and that
    # acronym names exactly ONE registration in AACT's own acronym field -> that NCT (unique-or-nothing)
    import re
    sys.path.append(os.path.join(ROOT, "scripts"))
    import g1_tracker as gt
    slug_of = {str(r["pmid"]): r["slug"] for r in audit.get("rows") or []}
    title_acr = {}
    for p in want:
        if link.get(p):
            continue
        t = (gt.held_record(slug_of[p], p) or {}).get("title") or ""
        title_acr[p] = {ic._fold(a) for a in re.findall(r"\b([A-Z][A-Z0-9]{2,}(?:-[A-Z0-9]+)*)\b", t) if len(a) >= 4}
    acr_hits = {}
    wanted = {a for v in title_acr.values() for a in v}
    if wanted:
        for r in _rows(snap, "studies.txt"):
            a = ic._fold(r.get("acronym") or "")
            if a in wanted:
                acr_hits.setdefault(a, set()).add(r["nct_id"])
    for p, acrs in title_acr.items():
        hits = {n for a in acrs for n in acr_hits.get(a, set())}
        if len(hits) == 1 and all(len(acr_hits.get(a, set())) <= 1 for a in acrs):
            link[p] = {next(iter(hits)): True}
            basis[p] = f"TITLE_ACRONYM_UNIQUE_IN_AACT ({', '.join(sorted(acrs))})"
    ncts = {n for d in link.values() for n in d}
    des, stu = {}, {}
    for r in _rows(snap, "designs.txt"):
        if r.get("nct_id") in ncts:
            des[r["nct_id"]] = {k: r.get(k) for k in ("allocation", "masking", "subject_masked", "investigator_masked")}
    for r in _rows(snap, "studies.txt"):
        if r.get("nct_id") in ncts:
            stu[r["nct_id"]] = {"official_title": r.get("official_title"), "brief_title": r.get("brief_title")}
    out = {}
    for p in want:
        ns = sorted(link.get(p) or [])
        if len(ns) != 1:
            out[p] = {"state": "NO_UNIQUE_REGISTRATION", "ncts": ns, "snapshot": sid}
            continue
        n = ns[0]
        out[p] = {"state": "RECORDED", "nct": n, "snapshot": sid, **(des.get(n) or {}), **(stu.get(n) or {}),
                  "link": basis.get(p)}
    with open(OUTP, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, ensure_ascii=False)
    for p, v in out.items():
        print(p, v.get("state"), v.get("nct"), v.get("allocation"), v.get("masking"), (v.get("official_title") or "")[:90])


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
