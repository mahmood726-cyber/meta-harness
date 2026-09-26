"""The auditor's three one-value LEADER mutations, run through a REAL verify_bundle.py (not a reduction).

usage: python .audit_probe_real.py <verifier.py> (--git <commit> | --url <site root>) [--repo <git dir>]
The served tree is read either from git objects at <commit>:docs/ (no checkout: C: is tight) or from the live site. Exactly one
value in reviews/<slug>/BUNDLE.json's LEADER row is changed in memory; every other byte is untouched. A run that raises or returns
no verdict prints NO VERDICT and is never a pass. The restore control must PASS, or the other rows mean nothing."""
import argparse
import copy
import importlib.util
import json
import subprocess
import sys

SLUG, LEADER = "glp1-ra-mace-t2d", "27295427"
BUNDLE = f"reviews/{SLUG}/BUNDLE.json"

ap = argparse.ArgumentParser()
ap.add_argument("verifier")
g = ap.add_mutually_exclusive_group(required=True)
g.add_argument("--git")
g.add_argument("--url")
ap.add_argument("--repo", default="C:/mh-lanes/oc")
a = ap.parse_args()

spec = importlib.util.spec_from_file_location("vb_real", a.verifier)
vb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vb)


class GitStore(vb.Store):
    def __init__(self, commit, repo):
        super().__init__(None, None)
        self.commit, self.repo = commit, repo

    def get(self, path):
        if path in self.cache:
            return self.cache[path]
        p = subprocess.run(["git", "cat-file", "blob", f"{self.commit}:docs/{path}"], cwd=self.repo, capture_output=True, stdin=subprocess.DEVNULL)
        if p.returncode != 0:
            raise vb.Refusal("ARTEFACT_UNREACHABLE", f"{path} is not present in the served tree")
        self.cache[path] = p.stdout
        return p.stdout


def fresh():
    return GitStore(a.git, a.repo) if a.git else vb.Store(None, a.url)


def leader_row(b):
    for r in b["verification_rows"]:
        if str((r.get("trial") or {}).get("id", "")).replace("PMID ", "") == LEADER:
            return r
    raise SystemExit("LEADER row not found in BUNDLE.json")


def mutate(fn):
    s = fresh()
    b = json.loads(s.get(BUNDLE).decode("utf-8"))
    before = None
    if fn:
        r = leader_row(b)
        before = fn(r)
    s.cache[BUNDLE] = json.dumps(b).encode("utf-8")
    return s, before


def m_comparator(r):
    f = r["analysis_identity"]["comparator_direction"]; old = f["value"]; f["value"] = "placebo vs GLP-1 RA"; return old


def m_estimator(r):
    f = r["analysis_identity"]["estimator"]; old = f["value"]; f["value"] = "odds ratio"; return old


def m_analysis_set(r):
    f = r["analysis_identity"]["analysis_set"]; old = (f["value"], f["basis"]); f["value"] = "per-protocol"; return old


def m_key_edited(r):
    # the key alone is edited (the default rendered as a statement): the fields are untouched, so only a RECOMPUTED key can see it
    ai = r["analysis_identity"]; old = ai["analysis_identity_key"]; ai["analysis_identity_key"] = old.replace("default)[REG]", "default)[STA]"); return old


def m_registered_swapped(r):
    f = r["analysis_identity"]["analysis_set"]; old = f["registered"]; f["registered"] = "per-protocol"; return old


FORMAT_319 = False


CASES = [("canonical (control)", None), ("comparator_direction -> 'placebo vs GLP-1 RA'", m_comparator),
         ("estimator -> 'odds ratio'", m_estimator), ("analysis_set value -> 'per-protocol' (basis stays REGISTERED_DEFAULT)", m_analysis_set),
         ("analysis_identity_key edited alone ([REG] -> [STA])", m_key_edited),
         ("analysis_set.registered -> 'per-protocol' (basis REGISTERED_DEFAULT)", m_registered_swapped),
         ("restore (control)", None)]
if "--format319" in sys.argv:
    pass

out = []
print(f"verifier {a.verifier} sha256 {vb.sha256(open(a.verifier, 'rb').read())}")
print(f"bytes    {'git ' + a.git + ':docs/' if a.git else a.url}")
for name, fn in CASES:
    try:
        s, before = mutate(fn)
        rep = vb.run(s, SLUG, None)
    except Exception as e:  # noqa: BLE001
        print(f"{name:<70} NO VERDICT ({type(e).__name__}: {str(e)[:120]})")
        out.append({"case": name, "verdict": None, "error": str(e)[:300]})
        continue
    row = next((x for x in rep.get("rows", []) if x.get("pmid") == LEADER), {})
    lead_fail = sorted({f.split(" ")[0] for f in rep.get("failures", []) if LEADER in f})
    all_fail = sorted({f.split(" ")[0] for f in rep.get("failures", [])})
    preds = {k: v for k, v in (row.get("predicates") or row.get("P") or {}).items() if k.startswith(("P10", "P11", "P15"))}
    key = ((row.get("analysis_identity") or {}).get("analysis_identity_key")) if isinstance(row.get("analysis_identity"), dict) else None
    print(f"{name:<70} verdict {rep.get('verdict')!s:<8} LEADER {row.get('final')!s:<12} LEADER codes {lead_fail} {preds}")
    out.append({"case": name, "was": before, "verdict": rep.get("verdict"), "leader_final": row.get("final"), "leader_codes": lead_fail,
                "all_codes": all_fail, "predicates": preds, "failures": [f[:400] for f in rep.get("failures", []) if LEADER in f]})
json.dump(out, open(".audit_probe_result.json", "w", encoding="utf-8"), indent=1)
