"""APPLY G1-ABANDON-v1 (Mahmood 7 Oct 2026, verbatim: "abandon ten"): write registry/g1_abandoned.json, the register
scripts/render_g1_tracker.py reads. Every entry is ABANDONED_BY_DECISION with his words, the date, the rule's sha256 and
commit, and the topic's score and reason, all copied from committed artefacts:

  rule      registry/g1_abandon_rule.json AS COMMITTED at its pre-registration commit (sha256 must equal RULE_SHA)
  ranking   outputs/k_gap/g1_abandon_rank.json (its rule_sha256 and read_at_commit must equal the rule's)
  decision  the ten slugs approved, which must equal the ranking's own 'abandon' list exactly, in order

Nothing is deleted: pages, rows, findings and signed results stay served. Refuses (exit 1) on any disagreement.

    python scripts/g1_abandon_apply.py [--write]
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "registry", "g1_abandoned.json")
RANK = os.path.join(ROOT, "outputs", "k_gap", "g1_abandon_rank.json")
RULE_PATH = "registry/g1_abandon_rule.json"
RULE_COMMIT = "6f64f13328708727dd9270cc643e72b8747ff69d"
RULE_SHA = "c3ee2f6224b62b0aa50312ace3ae1e634332efeb8e59684176aefce7fed28f1d"
DECISION = {"by": "Mahmood", "words": "abandon ten", "date": "2026-10-07",
            "relayed": "Dispatch chat, 7 Oct 2026",
            "shown_before_assent": "the list with scores, the #10/#11 boundary, and the both-lines display (n of 22 active "
                                   "and n of 32 all topics)"}
APPROVED = ["balanced-crystalloids-vs-saline-mortality", "ticagrelor-vs-clopidogrel-acs", "metformin-pcos-ovulation",
            "colchicine-secondary-cv-prevention", "probiotics-aad-prevention", "colchicine-postop-af", "pcsk9-mace",
            "corticosteroids-cap-mortality", "tocilizumab-covid19-mortality", "omega3-cardiovascular-events"]


def build():
    rule_bytes = subprocess.run(["git", "show", f"{RULE_COMMIT}:{RULE_PATH}"], cwd=ROOT, capture_output=True,
                                check=True).stdout
    if hashlib.sha256(rule_bytes).hexdigest() != RULE_SHA:
        raise SystemExit(f"REFUSED: {RULE_PATH} at {RULE_COMMIT[:8]} is not sha256 {RULE_SHA[:12]}")
    rule = json.loads(rule_bytes)
    rank = json.load(open(RANK, encoding="utf-8"))
    if rank.get("rule_sha256") != RULE_SHA or rank.get("read_at_commit") != RULE_COMMIT:
        raise SystemExit("REFUSED: the ranking was not computed from the pre-registered rule at its commit")
    if rank.get("abandon") != APPROVED:
        raise SystemExit(f"REFUSED: the approved ten differ from the ranking's list: {rank.get('abandon')}")
    by = {r["slug"]: r for r in rank["ranked"]}
    # the ten must BE ranks 1..10 of the ranking and the first kept topic must not be one of them (codex abandon-ten-r2
    # g1#1): a ranking that contradicts itself refuses rather than producing a register
    if [by.get(s, {}).get("rank") for s in APPROVED] != list(range(1, len(APPROVED) + 1)) \
            or len(by) != len(rank["ranked"]):
        raise SystemExit("REFUSED: the approved ten are not ranks 1..10 of the ranking (or a slug is ranked twice)")
    nxt = next(r for r in rank["ranked"] if r["rank"] == len(APPROVED) + 1)
    if nxt["slug"] in APPROVED or nxt.get("abandon") or nxt["U"] > by[APPROVED[-1]]["U"]:
        raise SystemExit(f"REFUSED: rank {nxt['rank']} ({nxt['slug']}) contradicts the boundary")
    topics = []
    for s in APPROVED:
        r = by[s]
        if not r.get("abandon") or r.get("state") == "G1_MATCHED":
            raise SystemExit(f"REFUSED: {s} is not an abandon row of the ranking, or is matched")
        topics.append({
            "slug": s, "state": "ABANDONED_BY_DECISION", "rank": r["rank"], "score_U": r["U"],
            "N_eligible": r["N_eligible"], "open": r["open"], "closed": r["closed"], "closed_trials": r["closed_trials"],
            "swap_adopted": r["swap_adopted"],
            "reason": (f"rank {r['rank']} of {len(rank['ranked'])} under {rule['rule_id']}: U = {r['U']} "
                       f"({r['closed']} of {r['N_eligible']} eligible comparator trials closed -- open routes exhausted or "
                       f"unreachable through open sources -- and {r['open']} open"
                       + ("; a replacement comparator was adopted" if r["swap_adopted"] else "") + ")"),
            "decision": DECISION})
    return {"_doc": __doc__.split("\n\n")[0], "rule_id": rule["rule_id"], "rule_path": RULE_PATH,
            "rule_commit": RULE_COMMIT, "rule_sha256": RULE_SHA, "score": rule["score"],
            "status_of_abandoned": rule["status_of_abandoned"], "population_n": rank["population_n"],
            "boundary": {"last_abandoned": {"slug": APPROVED[-1], "U": by[APPROVED[-1]]["U"]},
                         "first_kept": {"slug": nxt["slug"], "rank": nxt["rank"], "U": nxt["U"]}},
            "decision": DECISION, "topics": topics}


def main(argv):
    d = build()
    for t in d["topics"]:
        print(t["rank"], t["slug"], t["score_U"])
    print("boundary", d["boundary"])
    if "--write" in argv:
        with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(d, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main(sys.argv[1:])
