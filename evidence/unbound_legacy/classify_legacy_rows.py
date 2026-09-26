"""What would the 65 served UNBOUND_LEGACY rows be if the REAL classifier ran on them? (report only)

usage: python evidence/unbound_legacy/classify_legacy_rows.py <ref> <impact.json> <out.json>
For each legacy row from measure.py: the outcome's own spec (topics/<slug>.json at <ref>, primary / secondary / harm / comparator
outcome matched by name), the row's held abstract (docs/cache/<slug>/records.json at <ref>, by PMID), and harness
target_endpoint.classify_bound(spec, abstract, source), the function every classified route uses. A row whose source is not an
abstract quotation (registry / derived) is reported as NOT_AN_ABSTRACT_ROW: its identity would have to come from its registry
outcome measure, which this script does not guess."""
import json
import os
import subprocess
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from harness import target_endpoint as te   # noqa: E402


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL, check=True).stdout


def outcome_spec(topic, name):
    for key in ("primary_outcome", "secondary_outcomes", "harm_outcomes", "comparator_outcomes"):
        v = topic.get(key)
        for s in (v if isinstance(v, list) else [v] if v else []):
            if isinstance(s, dict) and s.get("name") == name:
                return s
    return None


def main(ref, impact_path, out_path):
    impact = json.load(open(impact_path, encoding="utf-8"))
    topics, records, out = {}, {}, []
    for e in impact["outcomes"]:
        slug = e["slug"]
        topics.setdefault(slug, json.loads(_git("show", f"{ref}:topics/{slug}.json")))
        if slug not in records:
            records[slug] = {}
            for path in (f"docs/cache/{slug}/records.json", f"cache/{slug}/records.json"):   # only bundled topics serve docs/cache
                try:
                    records[slug] = {str(r["id"]): r for r in json.loads(_git("show", f"{ref}:{path}"))["records"]}
                    break
                except subprocess.CalledProcessError:
                    continue
        spec = outcome_spec(topics[slug], e["outcome"])
        for r in e["legacy_rows"]:
            pmid = str(r["id"] or "").replace("PMID ", "")
            row = {"slug": slug, "outcome": e["outcome"], "kind": e["kind"], "id": r["id"], "provenance": r["provenance"]}
            if spec is None:
                row["class"] = "NO_SPEC_FOUND"
            elif r["provenance"] != "abstract":
                row["class"] = "NOT_AN_ABSTRACT_ROW"
            elif pmid not in records[slug]:
                row["class"] = "NO_HELD_ABSTRACT"
            else:
                full_source = r["source"]
                c = te.classify_bound(spec, records[slug][pmid].get("abstract", ""), full_source)
                row.update({"class": c["target_endpoint_class"], "binding_reason": c.get("endpoint_binding_reason"),
                            "extra": c.get("extra_components"), "missing": c.get("missing_components"),
                            "spec_has_components": bool(te.canonical_components(spec))})
            out.append(row)
    summary = Counter(r["class"] for r in out)
    admissible = [r for r in out if r["class"] == "EXACT_TARGET"]
    res = {"ref": ref, "rows": len(out), "summary": dict(summary), "would_be_admitted_if_classified": len(admissible), "detail": out}
    json.dump(res, open(out_path, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps({k: res[k] for k in ("ref", "rows", "summary", "would_be_admitted_if_classified")}, indent=1))
    by = Counter((r["slug"], r["class"]) for r in out)
    for (s, c), n in sorted(by.items()):
        print(f"  {s:42s} {c:22s} {n}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
