"""Migrate lane handover ADJUDICATIONS.json decisions into registry/adjudications.json, field for field.

Every decision is copied as written (no value is retyped); the registry adds `status` (PROPOSED unless the
record already says WITHDRAWN/COUNTERSIGNED), `countersignature` (null: none has been given), `origin`
(which handover file, which adjudicator block) and the content hash. Re-running is idempotent: an id already
in the registry is left alone. Run from the repository root: python scripts/adjudication_migrate.py
"""
from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import adjudication  # noqa: E402


def main() -> int:
    path = os.path.join(ROOT, adjudication.REGISTRY_PATH)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    else:
        doc = {"object": "ADJUDICATION_REGISTRY",
               "_doc": ("One record per adjudication; sha256 = content hash of the record without sha256/countersignature; "
                        "served rows cite {adjudication_id, adjudication_sha256, status, countersigned} built by "
                        "harness.adjudication.reference. Countersigning sets status COUNTERSIGNED and signs record_sha256; "
                        "it does not move the hash. Withdrawing sets WITHDRAWN; a served row may not cite a withdrawn record."),
               "records": []}
    have = {r["id"] for r in doc["records"]}
    added = []
    for src in sorted(glob.glob(os.path.join(ROOT, "outputs", "handover", "*", "ADJUDICATIONS.json"))):
        with open(src, encoding="utf-8") as f:
            lane = json.load(f)
        rel = os.path.relpath(src, ROOT).replace(os.sep, "/")
        for dec in lane.get("decisions", []):
            if dec.get("id") in have:
                continue
            rec = dict(dec)
            state = str(dec.get("state") or "")
            rec["status"] = ("WITHDRAWN" if state.startswith("WITHDRAWN") else
                             "COUNTERSIGNED" if state.startswith("COUNTERSIGNED") else "PROPOSED")
            rec["countersignature"] = None
            rec["origin"] = {"handover_file": rel, "set_date_utc": lane.get("date_utc"), "adjudicator": lane.get("adjudicator")}
            rec = adjudication.seal(rec)
            doc["records"].append(rec)
            have.add(rec["id"])
            added.append(rec["id"])
    doc["records"].sort(key=lambda r: r["id"])
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    adjudication.load(ROOT)  # refuses if anything written is invalid
    print(f"registry: {len(doc['records'])} records; added {added or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
