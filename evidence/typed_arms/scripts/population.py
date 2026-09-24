"""Enumerate the served count-data rows (outcome trials carrying ai/ci) from a named ref's docs/reviews/*/review.json.

Writes evidence/typed_arms/population.json: every row with its served F4B slots (ai, n1i, ci, n2i), its held document
reference, its served spans, and the registry arms of its trial family -- the inputs extraction binds against.
The ref is recorded; the population is FROZEN at that ref (a later rule never shrinks it)."""
import json, subprocess, sys, hashlib, os

REF = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
OUT = os.path.join(os.path.dirname(__file__), "..", "population.json")

def git(*a, binary=False):
    r = subprocess.run(["git", *a], capture_output=True)
    if r.returncode:
        raise SystemExit(f"git {' '.join(a)} failed: {r.stderr.decode()[:300]}")
    return r.stdout if binary else r.stdout.decode()

sha = git("rev-parse", REF).strip()
slugs = [p.split("/")[-1] for p in git("ls-tree", "--name-only", sha, "docs/reviews/").split()]
rows, kinds = [], {}
for slug in slugs:
    raw = git("show", f"{sha}:docs/reviews/{slug}/review.json", binary=True)
    d = json.loads(raw)
    pc = d.get("protocol_config") or {}
    iline, question = pc.get("intervention_i_line"), d.get("question")
    fams = {f.get("family_id") or f.get("trial_family_id") or f.get("id"): f for f in d.get("trial_families", [])}
    for oi, o in enumerate(d.get("outcomes", [])):
        for ti, t in enumerate(o.get("trials") or []):
            if t.get("ai") is None and t.get("ci") is None:
                continue
            fam = fams.get(t.get("family_id") or t.get("trial_family_id"))
            rid = f"CD-{slug}-{oi}-{ti}"
            rows.append({
                "row_id": rid, "slug": slug, "outcome_index": oi, "trial_index": ti,
                "outcome_name": o.get("name"), "outcome_kind": o.get("kind"), "primary": o.get("primary"),
                "served_estimand": o.get("served_estimand") or o.get("estimand"),
                "outcome_population": o.get("population"), "outcome_timepoint": o.get("timepoint"),
                "trial_id": t.get("trial_id") or t.get("id"), "label": t.get("label"),
                "family_id": t.get("family_id") or t.get("trial_family_id"),
                "served": {k: t.get(k) for k in ("ai", "n1i", "ci", "n2i")},
                "has_comparator_direction": "comparator_direction" in t,
                "has_arm_ownership": any(k in t for k in ("arms", "arm_id", "arm_observations")),
                "kind": t.get("kind"), "provenance": t.get("provenance"),
                "document_ref": t.get("document_ref"), "document_sha256": t.get("document_sha256"),
                "document_candidates": t.get("document_candidates"),
                "held_document": t.get("held_document"),
                "endpoint_result_span": t.get("endpoint_result_span"),
                "source": t.get("source"), "spans": t.get("spans"),
                "analysis_set": t.get("analysis_set"), "follow_up_window": t.get("follow_up_window"),
                "registry_arms": (fam or {}).get("arms"),
                "intervention_i_line": iline, "question": question,
                "row_sha256": hashlib.sha256(json.dumps(t, sort_keys=True).encode()).hexdigest(),
            })
json.dump({"ref": sha, "rule": "outcomes[*].trials[*] with ai or ci not null, in docs/reviews/*/review.json",
           "n": len(rows), "rows": rows}, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(sha, len(rows), sum(r["has_comparator_direction"] for r in rows), sum(r["has_arm_ownership"] for r in rows))
