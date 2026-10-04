"""G1 tocilizumab: candidate registrations for REACT's 19 trial names, from the LOCAL AACT snapshot only (no network).
Streams studies + interventions once; prints every interventional study with tocilizumab whose acronym or title names a
REACT label. Read-only; writes nothing. Used to seed g1/tocilizumab.py's identity table, which records its own evidence."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import aact  # noqa: E402

LABELS = ["ARCHITECTS", "BACC", "CORIMUNO", "COV-AID", "COVACTA", "COVIDOSE", "COVIDSTORM", "COVINTOC", "COVITOZ",
          "EMPACTA", "HMO-020-0224", "ImmCoVA", "IMMCoVA", "PreToVid", "RECOVERY", "REMAP-CAP", "REMDACTA", "TOCIBRAS",
          "TOCOVID"]


def main():
    toci = set()
    for r in aact._iter_rows(aact._table("interventions")):
        if re.search(r"tocilizumab|actemra|roactemra", r.get("name") or "", re.I):
            toci.add(r["nct_id"])
    hits = []
    for r in aact._iter_rows(aact._table("studies")):
        n = r["nct_id"]
        text = " ".join(r.get(k) or "" for k in ("acronym", "brief_title", "official_title"))
        lab = [l for l in LABELS if re.search(r"(?<![A-Za-z])" + re.escape(l) + r"(?![A-Za-z])", text, re.I)]
        if lab and n in toci:
            hits.append((n, r.get("acronym"), (r.get("brief_title") or "")[:110], lab, n in toci,
                         r.get("results_first_posted_date") or r.get("results_first_submitted_date")))
    for h in sorted(hits, key=lambda x: str(x[3])):
        print(h)
    print("tocilizumab interventional studies in snapshot:", len(toci), "| label hits:", len(hits))


if __name__ == "__main__":
    main()
