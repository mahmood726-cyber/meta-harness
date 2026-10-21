import io, json, os, sys
ROOT = "F:/captain3-v15c"
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
os.chdir(ROOT)
import m2_pretriage as m
IDS = {("esketamine-trd-madrs", "NCT02417064"), ("esketamine-trd-madrs", "NCT02422186"),
       ("esketamine-trd-madrs", "PMID 31109201"), ("esketamine-trd-madrs", "PMID 37025256"),
       ("tocilizumab-covid19-mortality", "NCT04320615"), ("tocilizumab-covid19-mortality", "NCT04403685")}
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
rows = [r for r in m.unbound_rows() if (r["slug"], r["id"]) in IDS]
print("selected", len(rows), "of", len(IDS), sorted((r["slug"], r["id"]) for r in rows), flush=True)
assert len(rows) == len(IDS), "row selection mismatch"
res = []
for r in rows:
    x = m.triage(r, out)
    res.append(x)
    print(x["state"], x["slug"], x["id"], x.get("source_ref") or x.get("source_kind"), flush=True)
    json.dump(res, open(os.path.join(out, "pretriage.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("DONE")
