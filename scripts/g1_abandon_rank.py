"""Rank topics by unworkability under the PRE-REGISTERED rule registry/g1_abandon_rule.json (Mahmood 6 Oct: "abandon the
ten most unworkable topics"). Reads committed artefacts only, at a named commit (default HEAD), so the ranking replays.
Writes outputs/k_gap/g1_abandon_rank.json with the rule's sha256 and the commit it was read at.

    python scripts/g1_abandon_rank.py [--at <commit>] [--write]
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULE = "registry/g1_abandon_rule.json"
OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_abandon_rank.json")


def _git(*a) -> bytes:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, check=True, stdin=subprocess.DEVNULL).stdout


def _at(commit: str, path: str):
    r = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL)
    return r.stdout if r.returncode == 0 else None


def score_topic(trk: dict, swap_adopted: bool, closed_classes: set) -> dict:
    n = int(trk.get("N_eligible") or 0)
    og = set(trk.get("open_gaps") or [])
    closed = [t["label"] for t in trk.get("trials") or []
              if t.get("label") in og and str(t.get("blocker") or "").split(":")[0] in closed_classes]
    u = 0.0 if n == 0 else len(closed) / n + 0.5 * len(og) / n - 0.5 * (1 if swap_adopted else 0)
    return {"N_eligible": n, "open": len(og), "closed": len(closed), "closed_trials": sorted(closed),
            "swap_adopted": bool(swap_adopted), "U": round(u, 4)}


def rank(commit: str = "HEAD") -> dict:
    commit = _git("rev-parse", commit).decode().strip()
    rule_bytes = _at(commit, RULE)
    if rule_bytes is None:
        raise SystemExit(f"REFUSED: {RULE} is not committed at {commit} -- the rule is registered before any ranking")
    rule = json.loads(rule_bytes)
    closed_classes = set(rule["inputs_committed_artefacts_only"]["CLOSED"])
    names = [l.split("\t")[-1] for l in _git("ls-tree", "-r", "--name-only", commit, "outputs/k_gap/g1/").decode().splitlines()]
    rows, excluded = [], []
    for path in sorted(names):
        if not path.endswith(".json"):
            continue
        trk = json.loads(_at(commit, path))
        slug = trk["slug"]
        if _at(commit, f"docs/reviews/{slug}/review.json") is None:
            continue
        state = (trk.get("g1_status") or {}).get("state")
        if state == "G1_MATCHED":
            excluded.append({"slug": slug, "state": state})
            continue
        swap = _at(commit, f"registry/comparator_selection/{slug}.adoption.json") is not None
        rows.append(dict(slug=slug, state=state, **score_topic(trk, swap, closed_classes)))
    rows.sort(key=lambda r: (-r["U"], -r["closed"], r["slug"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
        r["abandon"] = i <= 10
    return {"rule_id": rule["rule_id"], "rule_path": RULE, "rule_sha256": hashlib.sha256(rule_bytes).hexdigest(),
            "read_at_commit": commit, "population_n": len(rows) + len(excluded), "excluded_matched": excluded,
            "ranked": rows, "abandon": [r["slug"] for r in rows if r["abandon"]]}


def main(argv):
    at = argv[argv.index("--at") + 1] if "--at" in argv else "HEAD"
    res = rank(at)
    for r in res["ranked"]:
        print(f"{r['rank']:>2} {'ABANDON' if r['abandon'] else 'active ':7} U={r['U']:<7} closed {r['closed']}/{r['N_eligible']} "
              f"open {r['open']} swap={int(r['swap_adopted'])} {r['slug']}")
    print(f"excluded (G1_MATCHED): {len(res['excluded_matched'])}; rule {res['rule_id']} sha256 {res['rule_sha256'][:16]} at {res['read_at_commit'][:12]}")
    if "--write" in argv:
        with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, ensure_ascii=False)
            fh.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
