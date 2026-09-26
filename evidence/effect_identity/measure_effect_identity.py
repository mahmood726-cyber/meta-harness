"""Corpus-wide: published effects that disagree with their own counts, and transformed effects served without provenance.
(report only; external review of colchicine-recurrent-pericarditis, 2026-09-26)

usage: python evidence/effect_identity/measure_effect_identity.py <ref of the served tree> <out.json>
Every served pooled row of every outcome at <ref>, read from git objects, through harness/effect_identity's OWN functions -- the
same code the pipeline now runs, so the count and the gate cannot disagree:
  conflicts   N = rows with a published effect AND counts for the same result (own cells or a disclosed alternative);
              comparable = those whose published measure is RR or OR (an HR is not the crude ratio of its counts);
              n = SOURCE_EFFECT_CONFLICT, with the mislabel hypotheses that match and whether an adjusted model is documented
  provenance  N = rows serving a reported effect; n = rows whose served tuple is a TRANSFORM of what the source reported (read
              from the row's quotation, then its held abstract) while the row carries no record of it -- every such row today,
              since no served row records a transform"""
import json
import os
import subprocess
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from harness import effect_identity as ei   # noqa: E402


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL, check=True).stdout


def records(ref, slug):
    for path in (f"docs/cache/{slug}/records.json", f"cache/{slug}/records.json"):
        try:
            return {str(r["id"]): r for r in json.loads(_git("show", f"{ref}:{path}"))["records"]}
        except subprocess.CalledProcessError:
            continue
    return {}


def main(ref, out_path):
    names = [n for n in _git("ls-tree", "-r", "--name-only", ref, "docs/reviews").decode().splitlines()
             if n.count("/") == 3 and n.endswith("/review.json")]
    conflicts, provenance, tallies = [], [], Counter()
    for n in sorted(names):
        slug = n.split("/")[2]
        rev = json.loads(_git("show", f"{ref}:{n}"))
        recs = None
        for o in rev.get("outcomes") or []:
            for t in o.get("trials") or []:
                tallies["pooled_rows"] += 1
                if t.get("effect") is None:
                    continue
                tallies["reported_rows"] += 1
                if recs is None:
                    recs = records(ref, slug)
                ab = (recs.get(str(t.get("id", "")).replace("PMID ", "")) or {}).get("abstract")
                c = ei.conflict_check(t, ei.adjusted_documented(t))
                if c:
                    tallies["rows_with_counts"] += 1
                    tallies[f"state_{c['state']}"] += 1
                    if c["state"] != "NOT_COMPARABLE":
                        tallies["comparable"] += 1
                    if c["state"] == "SOURCE_EFFECT_CONFLICT":
                        conflicts.append({"slug": slug, "outcome": o.get("name"), "primary": bool(o.get("primary")), "id": t.get("id"),
                                          "published": c["published"], "counts": c["counts"], "counts_implied": c.get("counts_implied"),
                                          "matching_hypotheses": c.get("matching_hypotheses"), "resolution": c["resolution"],
                                          "selection_rule": t.get("selection_rule")})
                p = ei.transform_provenance(t, ab)
                if p:
                    provenance.append({"slug": slug, "outcome": o.get("name"), "primary": bool(o.get("primary")), "id": t.get("id"),
                                       "served": [t.get("effect"), t.get("ci_low"), t.get("ci_high"), t.get("scale")],
                                       "reported": p["reported"], "reported_measure": p["reported_measure"], "read_from": p["read_from"],
                                       "served_selection_rule": t.get("selection_rule"),
                                       "served_reported_label": (t.get("effect_object") or {}).get("reported_label"),
                                       "records_transform": bool(t.get("effect_transform")), "symmetric_note": p.get("note")})
    res = {"served_tree": ref, "pages": len(names), "tallies": dict(tallies),
           "conflicts": {"n": len(conflicts), "N_comparable": tallies["comparable"], "N_with_counts": tallies["rows_with_counts"],
                         "by_hypothesis": dict(Counter(",".join(c["matching_hypotheses"]) or "NONE" for c in conflicts)),
                         "held": sum(c["resolution"] == "HOLD" for c in conflicts), "rows": conflicts},
           "provenance": {"n_transformed": len(provenance), "n_without_record": sum(not p["records_transform"] for p in provenance),
                          "N_reported": tallies["reported_rows"], "rows": provenance}}
    json.dump(res, open(out_path, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps({"tallies": res["tallies"], "conflicts": {k: v for k, v in res["conflicts"].items() if k != "rows"},
                      "provenance": {k: v for k, v in res["provenance"].items() if k != "rows"}}, indent=1))
    for c in conflicts:
        print(f"  CONFLICT {c['slug']:36s} {c['id']:14s} pub {c['published']['scale']} {c['published']['estimate']} ({c['published']['ci_low']}-{c['published']['ci_high']}) "
              f"counts-RR {c['counts_implied']['RR']} -> {c['matching_hypotheses']} {c['resolution']}  [{(c['outcome'] or '')[:30]}]")
    for p in provenance:
        print(f"  TRANSFORM {p['slug']:35s} {p['id']:14s} reported {p['reported_measure']} {p['reported']} -> served {p['served']} "
              f"rule={p['served_selection_rule']} label={p['served_reported_label']}  [{(p['outcome'] or '')[:30]}]")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
