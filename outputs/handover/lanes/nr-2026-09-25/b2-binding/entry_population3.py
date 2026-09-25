"""ENTRY_POPULATION_NOT_ESTABLISHED departures: the conditions the P5 test read, from the page's trial_families
node at the judged commit, and the exact substring test re-run on them. Read-only."""
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
    if r["code"] != "ENTRY_POPULATION_NOT_ESTABLISHED" or (r["slug"], r["family"]) in seen:
        continue
    seen.add((r["slug"], r["family"]))
    if r["slug"] not in reviews:
        reviews[r["slug"]] = json.loads(show(f"docs/reviews/{r['slug']}/review.json"))
    fam = next((f for f in reviews[r["slug"]].get("trial_families") or [] if f.get("family_id") == r["family"]), {})
    cond = ((fam.get("population") or {}).get("conditions") or {}).get("value")
    topic = json.loads(show(f"topics/{r['slug']}.json") or b"{}")
    req = trial_family.protocol_requirements(str(W), r["slug"], dict(topic))
    terms = ((req or {}).get("include") or {}).get("population_any") or []
    text = " ".join(cond).lower() if isinstance(cond, list) else str(cond or "").lower()
    passes = any(t.lower() in text for t in terms)
    out.append({"audit_id": r["audit_id"], "slug": r["slug"], "family": r["family"], "conditions": cond,
                "population_any": terms, "substring_test_passes": passes, "family_found": bool(fam)})
    print(f"{r['audit_id']} {r['family']} found={bool(fam)} | conditions={cond} | test passes: {passes}")
Path(r"C:/mh-lanes/nr/work/entry_population.json").write_bytes(json.dumps(out, ensure_ascii=False, indent=1).encode())
