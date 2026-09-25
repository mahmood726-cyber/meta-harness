"""For every departing trial of the 41 notices: what the held family record (cache/<slug>/families.json at the judged
commit) actually contains, beside the absence code the gate gave. Read-only; git show only."""
import collections
import json
import subprocess
import sys
from pathlib import Path

W = Path(r"C:/mh-lanes/nr/wt")
REV = "1fa77f2c4852ee79e55d540083e3c35bbff0cecc"


def show(path):
    p = subprocess.run(["git", "show", f"{REV}:{path}"], cwd=W, capture_output=True)
    return json.loads(p.stdout) if p.returncode == 0 else None


audit = json.loads((W / "registry/notice_adjudication.json").read_text(encoding="utf-8"))
fams = {}
rows = []
for row in audit["notices"]:
    slug = row["slug"]
    if slug not in fams:
        d = show(f"cache/{slug}/families.json") or {}
        fams[slug] = {f["family_id"]: f for f in (d.get("families") or [])}
    for t in row["departing_trials"]:
        f = fams[slug].get(t["family_id"])
        rows.append({
            "audit_id": row["audit_id"], "slug": slug, "trial": t["trial_id"], "family": t["family_id"],
            "label": t["eligibility_label"], "code": t["absence_code"],
            "family_held": f is not None,
            "arms": [a.get("label", {}).get("value") for a in (f or {}).get("arms") or []],
            "arm_absence_code": (f or {}).get("arm_absence_code"),
            "randomised_contrasts": (f or {}).get("randomised_contrasts"),
            "eligibility": (f or {}).get("eligibility"),
        })
print(len(rows), "departing memberships")
print(collections.Counter((r["code"], r["family_held"], bool(r["arms"]), bool(r["randomised_contrasts"])) for r in rows))
for r in rows:
    print(r["audit_id"], r["trial"], r["family"], r["label"], r["code"], "| arms:", r["arms"][:4],
          "| contrasts:", json.dumps(r["randomised_contrasts"])[:120], "| elig:", json.dumps(r["eligibility"])[:160])
Path(r"C:/mh-lanes/nr/work/departing_evidence.json").write_bytes(json.dumps(rows, ensure_ascii=False, indent=1).encode())
