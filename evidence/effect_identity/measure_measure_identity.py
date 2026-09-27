"""n of N: served effect rows whose MEASURE changes when classified from the statistical model (measure_identity), and rows whose
source term says 'relative risk' about a time-to-event process with no model held (candidates, not changed). Report only.

usage: python evidence/effect_identity/measure_measure_identity.py [<ref>]"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from harness import measure_identity as mi   # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, check=True).stdout


def measure(ref=PINNED):
    slugs = sorted({p.split("/")[2] for p in _git("ls-tree", "-r", "--name-only", ref, "docs/reviews").decode().split()
                    if p.count("/") == 3 and p.endswith("review.json")})
    rows, n = [], 0
    for slug in slugs:
        rv = json.loads(_git("show", f"{ref}:docs/reviews/{slug}/review.json"))
        recs = {}
        for path in (f"cache/{slug}/records.json", f"docs/cache/{slug}/records.json"):
            try:
                recs = {str(r.get("id")): r for r in json.loads(_git("show", f"{ref}:{path}")).get("records") or []}
                break
            except subprocess.CalledProcessError:
                continue
        reg = mi.registry_models(slug)
        for o in rv.get("outcomes") or []:
            for t in o.get("trials") or []:
                if t.get("effect") is None:
                    continue
                n += 1
                pid = str(t.get("id") or "").replace("PMID ", "")
                rec = recs.get(pid) or {}
                nct = rec.get("nct") or (pid if pid.upper().startswith("NCT") else None)
                c = mi.classify(t, o.get("name"), nct, reg, rec.get("abstract"))
                served = str(t.get("scale") or "").upper()
                changed = c["model"] != "NOT_STATED" and c.get("scale") and c["scale"] != served
                candidate = (not changed and c["source_term"] == "relative risk" and c["outcome_process"] == "TIME_TO_EVENT_RATE"
                             and c["model"] == "NOT_STATED")
                cp = mi.ci_level_provenance(t)
                if changed or candidate or cp:
                    rows.append({"slug": slug, "outcome": o.get("name"), "id": t.get("id"), "served_scale": served,
                                 "classified": c, "changed": bool(changed), "time_to_event_rr_model_not_held": bool(candidate),
                                 "ci_level_provenance": cp})
    return {"ref": ref, "served_effect_rows": n, "measure_changed": sum(r["changed"] for r in rows),
            "rr_time_to_event_model_not_held": sum(r["time_to_event_rr_model_not_held"] for r in rows),
            "ci_level_not_95": sum(1 for r in rows if r["ci_level_provenance"]), "rows": rows}


if __name__ == "__main__":
    print(json.dumps(measure(*(sys.argv[1:2] or [PINNED])), indent=1, ensure_ascii=False))
