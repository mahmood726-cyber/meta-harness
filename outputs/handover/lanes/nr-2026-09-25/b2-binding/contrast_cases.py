"""INTERVENTION_CONTRAST_NOT_PROVEN departures: the agents the derivation searched for, each arm's linked active
interventions and linkage flag (page trial_families node at the judged commit), and the derivation re-run on them."""
import json
import subprocess
import sys
from pathlib import Path

W = Path(r"C:/mh-lanes/nr/wt")
sys.path.insert(0, str(W))
from harness import trial_family  # noqa: E402

REV = "1fa77f2c4852ee79e55d540083e3c35bbff0cecc"
rows = json.loads(Path(r"C:/mh-lanes/nr/work/departing_evidence.json").read_text(encoding="utf-8"))


def show(path):
    p = subprocess.run(["git", "show", f"{REV}:{path}"], cwd=W, capture_output=True)
    return p.stdout if p.returncode == 0 else None


reviews, seen, out = {}, set(), []
for r in rows:
    if r["code"] != "INTERVENTION_CONTRAST_NOT_PROVEN" or (r["slug"], r["family"]) in seen:
        continue
    seen.add((r["slug"], r["family"]))
    if r["slug"] not in reviews:
        reviews[r["slug"]] = json.loads(show(f"docs/reviews/{r['slug']}/review.json"))
    fam = next((f for f in reviews[r["slug"]].get("trial_families") or [] if f.get("family_id") == r["family"]), {})
    topic = json.loads(show(f"topics/{r['slug']}.json") or b"{}")
    agents = list((topic.get("include") or {}).get("intervention_any") or topic.get("intervention_terms") or [])
    arms = [{"arm_id": a.get("arm_id"), "linkage_complete": a.get("linkage_complete"),
             "active_interventions": a.get("active_interventions"),
             "label": (a.get("label") or {}).get("value") if isinstance(a.get("label"), dict) else a.get("label")}
            for a in fam.get("arms") or []]
    randomized = (fam.get("registry_design") or {}).get("allocation")
    rerun = trial_family.randomised_contrasts(
        [dict(a, span=None) for a in arms if a["active_interventions"] is not None], agents, True)
    out.append({"audit_id": r["audit_id"], "slug": r["slug"], "family": r["family"], "agents": agents,
                "arms": arms, "allocation": randomized, "rerun_contrasts_if_randomized": rerun})
    print(f"{r['audit_id']} {r['family']} alloc={randomized} | agents={agents[:6]}{'...' if len(agents) > 6 else ''}")
    for a in arms:
        print(f"      arm {a['label']!r}: linkage_complete={a['linkage_complete']} active={a['active_interventions']}")
    print(f"      derivation re-run (randomized=True): {len(rerun)} contrast(s)")
Path(r"C:/mh-lanes/nr/work/contrast_cases.json").write_bytes(json.dumps(out, ensure_ascii=False, indent=1).encode())
