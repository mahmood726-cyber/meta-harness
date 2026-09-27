"""Every served move of the V1.0.1 candidate stack against the served pages at 3876a62d (report only).

For each of the 32 topics: every outcome's pooled result (k, estimate, CI, scale, CI refusal), its pooled trial ids and their
n, its declared-absent ids, and the screening decisions. Prints a table and writes moves.json next to the builds."""
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
BUILDS = os.environ.get("V101_BUILDS", "builds")


def served(slug):
    p = subprocess.run(["git", "show", f"{PINNED}:docs/reviews/{slug}/review.json"], cwd=REPO, capture_output=True)
    return json.loads(p.stdout) if p.returncode == 0 else None


def res(o):
    r = o.get("result") or {}
    return {k: r.get(k) for k in ("k", "estimate", "ci_low", "ci_high", "scale")}


def trials(o):
    return sorted((str(t.get("id")), t.get("n1i") or t.get("nc1"), t.get("n2i") or t.get("nc2")) for t in o.get("trials") or [])


def absent(o):
    return sorted(str(a.get("id")) for a in o.get("declared_absent_trials") or [])


def screening(r):
    return {str(d.get("id")): (d.get("decision"), d.get("rule_id")) for d in (r.get("screening") or {}).get("records") or []}


def main():
    slugs = sorted(f[:-5] for f in os.listdir(BUILDS) if f.endswith(".json"))
    moves, same = [], 0
    for slug in slugs:
        a, b = served(slug), json.load(open(os.path.join(BUILDS, slug + ".json"), encoding="utf-8"))
        if a is None:
            moves.append({"slug": slug, "kind": "NOT_SERVED_AT_PIN"})
            continue
        oa = {o["name"]: o for o in a["outcomes"]}
        ob = {o["name"]: o for o in b["outcomes"]}
        for name in sorted(set(oa) | set(ob)):
            x, y = oa.get(name), ob.get(name)
            if x is None or y is None:
                moves.append({"slug": slug, "outcome": name, "kind": "OUTCOME_ADDED" if x is None else "OUTCOME_REMOVED"})
                continue
            d = {}
            if res(x) != res(y):
                d["result"] = [res(x), res(y)]
            if trials(x) != trials(y):
                d["trials"] = [trials(x), trials(y)]
            if absent(x) != absent(y):
                d["absent"] = [absent(x), absent(y)]
            if d:
                moves.append({"slug": slug, "outcome": name, "primary": bool(y.get("primary")), **d})
            else:
                same += 1
        sa, sb = screening(a), screening(b)
        sd = {k: [sa.get(k), sb.get(k)] for k in set(sa) | set(sb) if sa.get(k) != sb.get(k)}
        if sd:
            moves.append({"slug": slug, "kind": "SCREENING", "changes": sd})
    json.dump({"pinned": PINNED, "topics": len(slugs), "unchanged_outcomes": same, "moves": moves},
              open(os.path.join(os.path.dirname(BUILDS), "moves.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"topics {len(slugs)}; outcomes unchanged {same}; moves {len(moves)}")
    for m in moves:
        print(json.dumps(m, ensure_ascii=False)[:400])


if __name__ == "__main__":
    sys.exit(main())
