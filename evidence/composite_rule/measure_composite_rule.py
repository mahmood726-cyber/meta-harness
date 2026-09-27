"""Corpus-wide: under ONE component rule (harness/composite_rule, via outcome_tiers.composite_compatibility -- the pipeline's own
code), how many rows' admission changes? (report only; external review of colchicine-secondary-cv-prevention, 2026-09-26)

usage: python evidence/composite_rule/measure_composite_rule.py <ref> <out.json>
Every served PRIMARY outcome at <ref> that is a composite (at least one judged row with >=2 typed components): the admitted rows plus
the rows the topic's refusal registry (docs/refusals.json) refused for a composite reason, each read the SAME way (the held
abstract's "primary ... was a composite of" sentence). Default rule (no topic declares a policy today): the outcome's declared
components as the core when it has them, else 3-point; nothing allowed in primary. N = judged rows; n = rows whose served
admission differs from the rule. Rows with no readable definition are listed as NO_DEFINITION and are not in N."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from harness import outcome_tiers as ot   # noqa: E402


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL, check=True).stdout


def _records(ref, slug):
    for path in (f"docs/cache/{slug}/records.json", f"cache/{slug}/records.json"):
        try:
            return {str(r["id"]): r.get("abstract", "") for r in json.loads(_git("show", f"{ref}:{path}"))["records"]}
        except subprocess.CalledProcessError:
            continue
    return {}


def main(ref, out_path):
    names = [n for n in _git("ls-tree", "-r", "--name-only", ref, "docs/reviews").decode().splitlines()
             if n.count("/") == 3 and n.endswith("/review.json")]
    registry = json.loads(_git("show", f"{ref}:docs/refusals.json"))
    per_topic, all_rows = {}, []
    for n in sorted(names):
        slug = n.split("/")[2]
        o = next((x for x in json.loads(_git("show", f"{ref}:{n}")).get("outcomes") or [] if x.get("primary")), None)
        if not o or not (o.get("trials") or registry.get(slug)):
            continue
        spec = json.loads(_git("show", f"{ref}:topics/{slug}.json")).get("primary_outcome") or {}
        cc = ot.composite_compatibility(o, o.get("trials") or [], spec, _records(ref, slug), registry.get(slug))
        if not cc:
            continue
        judged = [r for r in cc["rows"] if r["state"] != "NO_DEFINITION"]
        per_topic[slug] = {"judged": len(judged), "admission_changes": cc["admission_changes"],
                           "refusals_judged_like_an_admitted_row": cc["refusals_judged_like_an_admitted_row"],
                           "no_definition": [r["id"] for r in cc["rows"] if r["state"] == "NO_DEFINITION"]}
        all_rows += [{"slug": slug, **r} for r in cc["rows"]]
    judged = [r for r in all_rows if r["state"] != "NO_DEFINITION"]
    res = {"ref": ref, "composite_primary_topics": len(per_topic), "N_judged_rows": len(judged),
           "n_admission_changes": sum(r["admission_changes"] for r in judged),
           "admitted_moving_to_separate": sum(r["admission_changes"] and r["served"] == "ADMITTED" for r in judged),
           "refused_moving_to_primary": sum(r["admission_changes"] and r["served"] == "REFUSED" for r in judged),
           "refusals_judged_like_an_admitted_row": {s: v["refusals_judged_like_an_admitted_row"] for s, v in per_topic.items() if v["refusals_judged_like_an_admitted_row"]},
           "no_definition_rows": sum(r["state"] == "NO_DEFINITION" for r in all_rows),
           "per_topic": per_topic, "rows": all_rows}
    json.dump(res, open(out_path, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "per_topic")}, indent=1))
    for s, v in per_topic.items():
        print(f"  {s:42s} judged {v['judged']:2d}  changes {len(v['admission_changes'])}  inconsistent-refusals {v['refusals_judged_like_an_admitted_row']}  no-def {len(v['no_definition'])}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
