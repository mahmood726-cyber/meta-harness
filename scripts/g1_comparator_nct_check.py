"""Every NCT a comparator cites for one of its trials, checked against the AACT snapshot's studies table: a registration
that does not exist cannot identify the trial (pcsk9's comparator cites ODYSSEY JAPAN as NCT02017898; the trial is
NCT02107898). Run once per snapshot; replayed offline from registry/comparator_nct_check.json.

  python scripts/g1_comparator_nct_check.py     -> registry/comparator_nct_check.json
"""
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
OUT = os.path.join(ROOT, "registry", "comparator_nct_check.json")


def main():
    from kgap import aact_adapter as a
    T = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "k_gap_table.json"), encoding="utf-8"))
    cited = sorted({n for t in T["trials"] for n in (t.get("ncts") or []) if str(n).startswith("NCT")})
    csv.field_size_limit(10 ** 8)
    have = set()
    with open(os.path.join(a.snapshot_dir(), "studies.txt"), encoding="utf-8", errors="replace", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="|", quoting=csv.QUOTE_NONE):
            if r.get("nct_id") in cited:
                have.add(r["nct_id"])
    snap = a.snapshot()
    out = {"snapshot": {"id": snap["id"], "digest": snap["digest"]}, "n_cited": len(cited),
           "not_in_snapshot": sorted(set(cited) - have)}
    open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
