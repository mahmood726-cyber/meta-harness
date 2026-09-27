"""Corpus-wide, before wiring: (a) published HRs pooled in non-HR outcomes (SONIA's rule: an HR stays an HR); (b) published ORs in
RR outcomes and whether the reconstruction route can rebuild an RR from held counts. Report only.

usage: python evidence/effect_identity/measure_hr_or_routes.py <ref> <out.json>"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from harness import effect_identity as ei   # noqa: E402


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL, check=True).stdout


def _records(ref, slug):
    for path in (f"docs/cache/{slug}/records.json", f"cache/{slug}/records.json"):
        try:
            return {str(r["id"]): r.get("abstract", "") for r in json.loads(_git("show", f"{ref}:{path}"))["records"]}
        except subprocess.CalledProcessError:
            continue
    return {}


def _vocab(topic):
    interv = set(topic.get("intervention_terms") or []) | set(topic.get("intervention_class_terms") or [])
    for k, v in (topic.get("intervention_agents") or {}).items():
        interv |= {k, *(v or [])}
    return sorted(x for x in interv if x), list(topic.get("comparator_terms") or [])


def main(ref, out_path):
    names = [n for n in _git("ls-tree", "-r", "--name-only", ref, "docs/reviews").decode().splitlines()
             if n.count("/") == 3 and n.endswith("/review.json")]
    hr_rows, or_rows = [], []
    for n in sorted(names):
        slug = n.split("/")[2]
        topic = json.loads(_git("show", f"{ref}:topics/{slug}.json"))
        interv, comp = _vocab(topic)
        recs = None
        for o in json.loads(_git("show", f"{ref}:{n}")).get("outcomes") or []:
            est = (o.get("estimand") or "").upper()
            pooled = (o.get("result") or {}).get("estimate") is not None
            for t in o.get("trials") or []:
                r = ei.hr_route(t, est, o.get("trials") or [])
                if r:
                    hr_rows.append({"slug": slug, "outcome": o.get("name"), "primary": bool(o.get("primary")), "estimand": est, "id": t.get("id"),
                                    "hr": [t.get("effect"), t.get("ci_low"), t.get("ci_high")], "route": r["route"], "pool_served": pooled,
                                    "k": len(o.get("trials") or [])})
                if str(t.get("scale") or "").upper() == "OR" and t.get("effect") is not None and est == "RR":
                    if recs is None:
                        recs = _records(ref, slug)
                    rec = ei.reconstruct_from_counts(t, recs.get(str(t.get("id", "")).replace("PMID ", ""), ""), interv, comp)
                    or_rows.append({"slug": slug, "outcome": o.get("name"), "id": t.get("id"), "or": [t.get("effect"), t.get("ci_low"), t.get("ci_high")],
                                    "state": rec["state"], "why": rec.get("why"), "rr": rec.get("rr"),
                                    "definition": ei.definition_class(t)})
    res = {"ref": ref, "hr_in_non_hr_outcomes": {"n": len(hr_rows), "primary": sum(r["primary"] for r in hr_rows),
                                                 "outcomes": sorted({(r["slug"], r["outcome"]) for r in hr_rows}), "rows": hr_rows},
           "or_in_rr_outcomes": {"n": len(or_rows), "reconstructed": sum(r["state"] == "RECONSTRUCTED" for r in or_rows), "rows": or_rows}}
    json.dump(res, open(out_path, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False, default=list)
    print(json.dumps({"hr_rows": res["hr_in_non_hr_outcomes"]["n"], "hr_primary": res["hr_in_non_hr_outcomes"]["primary"],
                      "or_rows": res["or_in_rr_outcomes"]["n"], "or_reconstructed": res["or_in_rr_outcomes"]["reconstructed"]}))
    for r in hr_rows:
        print(f"  HR  {r['slug']:38s} {'P' if r['primary'] else ' '} est={r['estimand']:3s} k={r['k']} {r['id']:14s} {r['hr']}  [{(r['outcome'] or '')[:28]}]")
    for r in or_rows:
        print(f"  OR  {r['slug']:38s} {r['id']:14s} {r['or']} -> {r['state']} {r['rr'] or r['why'][:90]}  def={r['definition']}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
