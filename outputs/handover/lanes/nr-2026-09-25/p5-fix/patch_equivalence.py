"""The written patch (tf_patched.py) must reproduce the in-memory sweep (fix_sweep.json, FIX-A+B) on every family,
and must never take an ELIGIBLE family out of ELIGIBLE (monotone)."""
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

W = Path(r"C:/mh-lanes/nr/wt")
sys.path.insert(0, str(W))
import harness  # noqa: E402
from harness import trial_family as orig  # noqa: E402

spec = importlib.util.spec_from_file_location("harness.trial_family_patched", r"C:/mh-lanes/nr/work/tf_patched.py",
                                              submodule_search_locations=None)
patched = importlib.util.module_from_spec(spec)
patched.__package__ = "harness"
sys.modules["harness.trial_family_patched"] = patched
spec.loader.exec_module(patched)

REV = "1fa77f2c4852ee79e55d540083e3c35bbff0cecc"
sweep = {(r["slug"], r["family"]): r for r in json.loads(Path(r"C:/mh-lanes/nr/work/fix_sweep.json").read_text())}


def show(path):
    return subprocess.run(["git", "show", f"{REV}:{path}"], cwd=W, capture_output=True, check=True).stdout


def state(c):
    return (c.get("state"), c.get("absence_code") or c.get("code"))


audit = json.loads((W / "registry/notice_adjudication.json").read_text(encoding="utf-8"))
n = same = 0
diff, lost = [], []
for slug in sorted({r["slug"] for r in audit["notices"]}):
    review = json.loads(show(f"docs/reviews/{slug}/review.json"))
    base = orig.protocol_requirements(str(W), slug, json.loads(show(f"topics/{slug}.json")))
    inc = base.get("include") or {}
    agents = list(inc.get("intervention_any") or base.get("intervention_terms") or [])
    comps = list(inc.get("comparator_any") or [])
    for fam in review.get("trial_families") or []:
        if not fam.get("arms") and not fam.get("population"):
            continue
        arms = [dict(a, span=None) for a in fam.get("arms") or [] if a.get("active_interventions") is not None]
        randomized = bool(fam.get("randomised_contrasts")) or str(
            (fam.get("registry_design") or {}).get("allocation", "")).upper() == "RANDOMIZED"
        f1 = copy.deepcopy(fam)
        f1["randomised_contrasts"] = patched.randomised_contrasts(arms, agents, randomized, comps)
        got = state(patched.screen_family(f1, base))
        want = tuple(sweep[(slug, fam["family_id"])]["fixAB"])
        served = tuple(sweep[(slug, fam["family_id"])]["served"])
        n += 1
        same += got == want
        if got != want:
            diff.append((slug, fam["family_id"], want, got))
        if served[0] == "ELIGIBLE" and got[0] != "ELIGIBLE":
            lost.append((slug, fam["family_id"], served, got))
print(f"patched module vs in-memory FIX-A+B: {same} of {n} families identical; differ: {len(diff)}")
for d in diff[:10]:
    print("  DIFF", d)
print(f"ELIGIBLE families the patch takes out of ELIGIBLE: {len(lost)}")
for d in lost[:10]:
    print("  LOST", d)
