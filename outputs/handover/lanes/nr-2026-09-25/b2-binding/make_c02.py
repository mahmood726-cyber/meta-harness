"""Blind packet for codex call NR-C02: classify the binding constraint of each departing membership's P5 failure.
Contains the held rows and the P5 source; contains NO lane label."""
import inspect
import json
import subprocess
import sys
from pathlib import Path

W = Path(r"C:/mh-lanes/nr/wt")
sys.path.insert(0, str(W))
from harness import trial_family  # noqa: E402

REV = "1fa77f2c4852ee79e55d540083e3c35bbff0cecc"
J = Path(r"C:/mh-lanes/nr/codex/c02-binding")
J.mkdir(parents=True, exist_ok=True)
rows = json.loads(Path(r"C:/mh-lanes/nr/work/departing_evidence.json").read_text(encoding="utf-8"))


def show(path):
    p = subprocess.run(["git", "show", f"{REV}:{path}"], cwd=W, capture_output=True)
    return p.stdout if p.returncode == 0 else None


reviews, topics, items = {}, {}, []
for i, r in enumerate(rows, 1):
    slug = r["slug"]
    if slug not in reviews:
        reviews[slug] = json.loads(show(f"docs/reviews/{slug}/review.json"))
        t = json.loads(show(f"topics/{slug}.json") or b"{}")
        req = trial_family.protocol_requirements(str(W), slug, dict(t))
        topics[slug] = {"question": reviews[slug].get("question"),
                        "intervention_agents_searched": list((t.get("include") or {}).get("intervention_any")
                                                             or t.get("intervention_terms") or []),
                        "population_any_terms": ((req or {}).get("include") or {}).get("population_any"),
                        "comparator_any": ((req or {}).get("include") or {}).get("comparator_any")}
    fam = next((f for f in reviews[slug].get("trial_families") or [] if f.get("family_id") == r["family"]), {})
    items.append({
        "item": f"M{i:02d}", "notice": r["audit_id"], "review": slug, "trial": r["trial"], "family_id": r["family"],
        "gate_code": r["code"], "gate_label": r["label"],
        "family_identity_registry_ids": (fam.get("identity_basis") or {}).get("registry_ids"),
        "registry_design": fam.get("registry_design"),
        "registry_conditions": ((fam.get("population") or {}).get("conditions") or {}).get("value"),
        "arms": [{"label": (a.get("label") or {}).get("value") if isinstance(a.get("label"), dict) else a.get("label"),
                  "linkage_complete": a.get("linkage_complete"), "active_interventions": a.get("active_interventions")}
                 for a in fam.get("arms") or []],
        "randomised_contrasts_derived": [{k: c.get(k) for k in ("drug", "background_therapy")}
                                         for c in fam.get("randomised_contrasts") or []],
    })
src = "\n\n".join(inspect.getsource(f) for f in (trial_family.randomised_contrasts, trial_family.effective_eligibility))
cell_src = inspect.getsource(trial_family)
start = cell_src.index("    conditions = (family.get('population',{}).get('conditions') or {}).get('value') or []")
end = cell_src.index("def protocol_requirements")
(J / "packet.json").write_bytes(json.dumps({"topics": topics, "items": items}, ensure_ascii=False, indent=1).encode())
(J / "p5_source.py").write_bytes(("# harness/trial_family.py at 1fa77f2c (excerpts, verbatim)\n\n" + src +
                                  "\n\n# eligibility cell (excerpt of the structural screen)\n" + cell_src[start:end]).encode())
print(len(items), "items;", len(topics), "topics")
