"""Re-validate the RECORDED blind query proposals (rounds r1, r2, precise; scripts/g1_query_audit.py) against the CURRENT
comparators of the active topics still short on search recall (outputs/search_audit/active/ACTIVE_AUDIT.json `short`).

The proposals were written blind (the proposer never saw any comparator trial) for the topic's registered PICO, so
they are equally blind to a comparator adopted later (V8). Same validation (recorded esearch '(<q>) AND <pmid>[uid]'
probes) against the current registered queries, cap 10,000 (the expanded-search cap; decision 7 Oct, amendment A6).

  python scripts/g1_active_query_revalidate.py   -> outputs/search_audit/active/query_revalidation.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import g1_query_audit as Q  # noqa: E402

SA = ROOT / "outputs" / "search_audit"
ACT = SA / "active" / "ACTIVE_AUDIT.json"
OUT = SA / "active" / "query_revalidation.json"
CAP = 10000
ROUNDS = (("r1", "query_audit.json"), ("r2", "query_audit_r2.json"), ("precise", "query_audit_precise.json"))


def main(argv):
    a = json.load(open(ACT, encoding="utf-8"))
    Q.VOLUME_CAP = CAP
    res = {}
    for t in a["topics"]:
        if not t["short"] and t["slug"] not in argv:
            continue
        trials = [r for r in t["trials"] if r["kind"] == "ELIGIBLE" and (r["pmids"] or r["ncts"])]
        cur = Q.current_queries(t["slug"])
        props = []
        for tag, f in ROUNDS:
            q = (json.load(open(SA / f, encoding="utf-8"))["topics"].get(t["slug"])) if (SA / f).exists() else None
            if not q:
                continue
            v = Q.validate(t["slug"], q["proposal"], trials, cur)
            props.append({"round": tag, "record": q["record"], "query": q["proposal"]["pubmed_query"], "validation": v})
            print(t["slug"], tag, "|", v["verdict"], "| current", v["recall_current"], "union", v["recall_union"], "| volume",
                  v["proposed_pubmed_count"], "|", [r["label"] for r in v["per_trial"] if r["proposed_matches"]], flush=True)
        res[t["slug"]] = {"short": t["short"], "proposals": props}
    json.dump({"schema": 1, "cap": CAP, "topics": res}, open(OUT, "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False)


if __name__ == "__main__":
    main(sys.argv[1:])
