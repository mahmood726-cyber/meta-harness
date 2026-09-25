"""(1) Every departing trial the fix readmits must fail admission on P5 alone (else it stays out regardless).
(2) Over ALL review pages at 1fa77f2c: P5 set-asides on outcomes NOT covered by an audited notice whose family the
fix would make ELIGIBLE -- those would CREATE new result-change notices after the fix."""
import copy
import json
import subprocess
import sys
from pathlib import Path

W = Path(r"C:/mh-lanes/nr/wt")
sys.path.insert(0, str(W))
sys.path.insert(0, r"C:/mh-lanes/nr/work")
import fix_sweep as fs  # noqa: E402  (re-runs the sweep on import; results in fs.rows)
from harness import trial_family  # noqa: E402

REV = fs.REV
audit = json.loads((W / "registry/notice_adjudication.json").read_text(encoding="utf-8"))
noticed = {(r["slug"], r["outcome"]) for r in audit["notices"]}
by_fam = {(r["slug"], r["family"]): r for r in fs.rows}
all_slugs = sorted(p.split("/")[2] for p in subprocess.run(
    ["git", "ls-tree", "-r", "--name-only", REV, "docs/reviews"], cwd=W, capture_output=True, text=True).stdout.split()
    if p.endswith("/review.json") and p.count("/") == 3)
print("\n(1) departing trials the fix readmits: failing predicates on the page")
for n in audit["notices"]:
    review = json.loads(fs.show(f"docs/reviews/{n['slug']}/review.json"))
    out = next(o for o in review["outcomes"] if o["name"] == n["outcome"])
    for t in n["departing_trials"]:
        r = by_fam.get((n["slug"], t["family_id"]))
        if r and r["fixABC"][0] == "ELIGIBLE":
            rec = next(x for x in out["declared_absent_trials"] if x["id"] == t["trial_id"])
            failing = (rec.get("admission_verdict") or {}).get("failing")
            flag = "" if failing == ["P5_family_eligible"] else "   <-- ALSO FAILS " + str(failing)
            print(f"  {n['audit_id']} {t['trial_id']}: failing={failing}{flag}")
print(f"\n(2) P5 set-asides on outcomes WITHOUT an audited notice, across {len(all_slugs)} review pages")
extra = 0
for slug in all_slugs:
    review = json.loads(fs.show(f"docs/reviews/{slug}/review.json"))
    topic = json.loads(fs.show(f"topics/{slug}.json"))
    base = trial_family.protocol_requirements(str(W), slug, dict(topic))
    fams = {f["family_id"]: f for f in review.get("trial_families") or []}
    for o in review.get("outcomes") or []:
        if (slug, o["name"]) in noticed:
            continue
        for rec in o.get("declared_absent_trials") or []:
            if rec.get("reason_code") != "P5_family_eligible":
                continue
            fid = rec.get("family_id")
            r = by_fam.get((slug, fid))
            if r is None and fid in fams:  # page not among the 24: screen it here the same way
                fam = fams[fid]
                arms = [dict(a, span=None) for a in fam.get("arms") or [] if a.get("active_interventions") is not None]
                f1 = copy.deepcopy(fam)
                inc = base.get("include") or {}
                f1["randomised_contrasts"] = fs.contrasts_fixed(
                    arms, list(inc.get("intervention_any") or base.get("intervention_terms") or []),
                    list(inc.get("comparator_any") or []), bool(fam.get("randomised_contrasts")) or str(
                        (fam.get("registry_design") or {}).get("allocation", "")).upper() == "RANDOMIZED")
                after = fs.state(fs.screen_fixed(f1, base))
            else:
                after = r["fixABC"] if r else ("NO_NODE", None)
            if after[0] == "ELIGIBLE":
                extra += 1
                print(f"  NEW-NOTICE RISK {slug} / {o['name']}: {rec['id']} ({fid}) would re-enter; "
                      f"served result {(o.get('result') or {}).get('k')} / {(o.get('result') or {}).get('estimate')}")
print(f"  total: {extra}")
