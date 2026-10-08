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
    # every score must BE the pre-registered formula on the row's own counts (codex abandon-ten-r4 g1#1, P0: shifting
    # every U by 100 kept the order and published corrupted scores); the ranking rounds U to 4 dp
    import math

    def _count(v):
        return isinstance(v, int) and not isinstance(v, bool) and v >= 0
    for r in rank["ranked"]:
        # counts must be possible and the score finite before any arithmetic (codex abandon-ten-r5 g1#1, g1#2: a NaN
        # passed the tolerance test; '11 of 0 eligible closed' passed every gate)
        if not all(_count(r.get(k)) for k in ("N_eligible", "open", "closed")) or not (
                r["closed"] <= r["open"] <= r["N_eligible"]) or not isinstance(r.get("U"), (int, float))                 or isinstance(r.get("U"), bool) or not math.isfinite(r["U"]) or not isinstance(r.get("swap_adopted"), bool):
            raise SystemExit(f"REFUSED: {r.get('slug')} has impossible counts or a non-finite score")
        n = r["N_eligible"]
        u = 0.0 if not n else r["closed"] / n + 0.5 * r["open"] / n - 0.5 * (1 if r["swap_adopted"] else 0)
        ct = r.get("closed_trials")
        # closed must be substantiated by that many DISTINCT named trials, not by a string's length (codex abandon-ten-r6
        # g1#1)
        if not isinstance(ct, list) or not all(isinstance(x, str) and x.strip() for x in ct) or len(set(ct)) != len(ct):
            raise SystemExit(f"REFUSED: {r['slug']} closed_trials is not a list of distinct named trials")
        if abs(round(u, 4) - r["U"]) > 1e-9 or r["closed"] != len(ct):
            raise SystemExit(f"REFUSED: {r['slug']} U {r['U']} is not the rule's score on its counts ({round(u, 4)})")
    # the WHOLE ranking must be the rule applied: re-sorted by the rule's own order (U descending, then larger closed,
    # then slug ascending) it must give exactly the recorded ranks, and only ranks 1..10 may carry abandon (codex
    # abandon-ten-r3 g1#1: a later kept topic scoring above the ten passed a rank-11-only check)
    resorted = sorted(rank["ranked"], key=lambda r: (-r["U"], -r["closed"], r["slug"]))
    if [r["rank"] for r in resorted] != list(range(1, len(resorted) + 1)) or             any(bool(r.get("abandon")) != (r["rank"] <= len(APPROVED)) for r in rank["ranked"]):
        raise SystemExit("REFUSED: the ranking is not the rule's own order (U desc, closed desc, slug asc)")
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
