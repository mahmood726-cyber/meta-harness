"""The F4 schema's population, frozen: every object in cache/<slug>/verified_arms.json carrying ai/n1i/ci/n2i, at a
named ref. Writes evidence/typed_arms/f4b/held_population.json in the shape check_typed_arms.check_row reads.
The review's intervention line (for G6/G5b) is read from the served docs/reviews/<slug>/review.json at the same ref.

usage: python held_population.py <ref>"""
import hashlib, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF = sys.argv[1] if len(sys.argv) > 1 else "origin/main"


def git(*a):
    r = subprocess.run(["git", *a], capture_output=True, cwd=HERE)
    if r.returncode:
        raise SystemExit(r.stderr.decode()[:300])
    return r.stdout


sha = git("rev-parse", REF).decode().strip()
files = [p for p in git("ls-tree", "-r", "--full-tree", "--name-only", sha, "cache/").decode().split()
         if re.fullmatch(r"cache/[^/]+/verified_arms\.json", p)]
rows = []
for f in sorted(files):
    slug = f.split("/")[1]
    va = json.loads(git("show", f"{sha}:{f}"))
    try:
        rv = json.loads(git("show", f"{sha}:docs/reviews/{slug}/review.json"))
        iline = (rv.get("protocol_config") or {}).get("intervention_i_line")
    except SystemExit:
        iline = None
    for pid, v in va.items():
        items = v if isinstance(v, list) else [v]
        for i, e in enumerate(items):
            if isinstance(e, dict) and all(isinstance(e.get(k), (int, float)) and not isinstance(e.get(k), bool)
                                           for k in ("ai", "n1i", "ci", "n2i")):
                key = f"{slug}/{pid}" + (f"/{i}" if isinstance(v, list) else "")
                rows.append({"row_id": "HE-" + re.sub(r"[^A-Za-z0-9]+", "-", key), "held_key": key, "slug": slug,
                             "outcome_index": None, "trial_index": i if isinstance(v, list) else None,
                             "outcome_name": e.get("outcome"), "trial_id": f"PMID {pid}", "family_id": f"PMID-{pid}",
                             "served": {k: e[k] for k in ("ai", "n1i", "ci", "n2i")}, "provenance": e.get("provenance"),
                             "row_sha256": hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest(),
                             "registry_arms": None, "intervention_i_line": iline,
                             "has_comparator_direction": "comparator_direction" in e,
                             "has_observations": "observations" in e})
out = {"ref": sha, "rule": "objects in cache/<slug>/verified_arms.json carrying ai, n1i, ci, n2i (the F4 schema's 34)",
       "n": len(rows), "files": len(files), "rows": rows}
json.dump(out, open(os.path.join(HERE, "held_population.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
print(sha[:8], len(rows), "entries in", len(files), "files;", sum(r["has_comparator_direction"] for r in rows),
      "with comparator_direction;", sum(r["has_observations"] for r in rows), "with observations")
