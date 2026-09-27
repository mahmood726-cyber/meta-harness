"""Old vs new _ctgov_candidates class on every held registry outcome measure x every declared outcome, all topics."""
import json, os, subprocess, sys, types, glob, collections
ROOT = os.getcwd(); sys.path.insert(0, ROOT)
from harness import target_endpoint as new
src = subprocess.run(["git","show","6311abb9:harness/target_endpoint.py"],capture_output=True).stdout.decode()
old = types.ModuleType("harness._te_old"); old.__package__="harness"; exec(compile(src,"te@6311abb9","exec"), old.__dict__)
changes, n = [], 0
for tp in sorted(glob.glob("topics/*.json")):
    slug = os.path.basename(tp)[:-5]
    t = json.load(open(tp, encoding="utf-8"))
    rp = f"cache/{slug}/records.json"
    if not os.path.exists(rp): continue
    ctr = (json.load(open(rp, encoding="utf-8")).get("ctgov_results") or {})
    specs = []
    for k in ("primary_outcome","secondary_outcomes","harm_outcomes","comparator_outcomes"):
        v = t.get(k); specs += [s for s in (v if isinstance(v,list) else [v] if v else []) if isinstance(s,dict)]
    iv = t.get("intervention_terms") or []; cp = t.get("comparator_terms") or []
    for nct, oms in ctr.items():
        for spec in specs:
            a = old._ctgov_candidates(oms, spec, iv, cp); b = new._ctgov_candidates(oms, spec, iv, cp)
            ka = [(c.get("classification_text","")[:60], c.get("target_endpoint_class")) for c in a]
            kb = [(c.get("classification_text","")[:60], c.get("target_endpoint_class")) for c in b]
            n += len(ka)
            for x, y in zip(ka, kb):
                if x[1] != y[1]: changes.append((slug, nct, spec.get("name"), x[0], x[1], y[1]))
            if len(ka) != len(kb): changes.append((slug, nct, spec.get("name"), "COUNT", len(ka), len(kb)))
print("candidates compared:", n, "class changes:", len(changes))
print(collections.Counter((c[4], c[5]) for c in changes).most_common())
for c in changes[:40]: print(c)
