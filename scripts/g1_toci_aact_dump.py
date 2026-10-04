"""G1 tocilizumab: print every POSTED mortality outcome (title, time frame, population, groups with count and analysed N)
for the given NCTs, from the local AACT snapshot. Read-only exploration for g1/tocilizumab.py."""
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import aact  # noqa: E402

NCTS = set(sys.argv[1:])
MORT = re.compile(r"mortal|death|died|dead|surviv|vital status|alive", re.I)


def main():
    outs = {}
    for r in aact._iter_rows(aact._table("outcomes")):
        if r["nct_id"] in NCTS and MORT.search((r.get("title") or "") + " " + (r.get("description") or "")):
            outs[r["id"]] = r
    groups = {}
    for r in aact._iter_rows(aact._table("result_groups")):
        if r["nct_id"] in NCTS:
            groups[r["id"]] = r.get("title")
    meas, cnts = defaultdict(list), defaultdict(dict)
    for r in aact._iter_rows(aact._table("outcome_measurements")):
        if r.get("outcome_id") in outs:
            meas[r["outcome_id"]].append((groups.get(r.get("result_group_id")), r.get("classification") or r.get("category"),
                                          r.get("param_type"), r.get("param_value")))
    for r in aact._iter_rows(aact._table("outcome_counts")):
        if r.get("outcome_id") in outs:
            cnts[r["outcome_id"]][groups.get(r.get("result_group_id"))] = r.get("count")
    for oid, o in sorted(outs.items(), key=lambda kv: (kv[1]["nct_id"], kv[1].get("title") or "")):
        print(f"\n## {o['nct_id']} [{o.get('outcome_type')}] {o.get('title')}\n   time: {o.get('time_frame')}\n"
              f"   population: {(o.get('population') or '')[:200]}\n   units: {o.get('units')} param: {o.get('param_type')}")
        for g, cls, pt, v in meas[oid]:
            print(f"   {g!s:45} | {cls!s:25} | {pt} {v} | analysed N {cnts[oid].get(g)}")


if __name__ == "__main__":
    main()
