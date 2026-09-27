"""(1) Two quotes that the gate rightly rejected are cosmetic misquotes of real held text; re-check them with the exact held
bytes and record the amendment (codex outputs are never edited). (2) Run the identity locator over every gate-passing finding:
flag claims that sit in NO json object or in MANY (a generic string proves nothing about one row)."""
import json
import sys

import locate_claims as L
import verify_spans as v

sys.stdout.reconfigure(encoding="utf-8")
AMEND = [
    {"topic": "tocilizumab-covid19-mortality", "match": "RECOVERY's reported rate ratio", "role": "evidence",
     "old": "rate ratio 0.85; 95% CI 0.76-0.94; p=0.0028", "new": "rate ratio 0·85; 95% CI 0·76-0·94; p=0·0028",
     "why": "held abstract uses the Lancet middle dot; codex wrote full stops"},
    {"topic": "semaglutide-obesity-mace", "match": "16 trials", "role": "evidence",
     "old": "Treatment with GLP-1 RAs", "new": "treatment with GLP-1 RAs",
     "why": "held text is mid-sentence lower case; codex capitalised it"},
]
gate = json.load(open("span_gate.json", encoding="utf-8"))
amended = []
for a in AMEND:
    fs = json.load(open(f"out/{a['topic']}.json", encoding="utf-8"))["findings"]
    n, f = next((i, f) for i, f in enumerate(fs) if a["match"] in f["title"])
    qs = [f["claim"]] + f["evidence"]
    fixed = [dict(q, quote=q["quote"].replace(a["old"], a["new"])) for q in qs]
    st = [v.found(q["file"], q["quote"]) for q in fixed]
    ok = all(s.startswith("OK") for s in st)
    amended.append({**a, "n": n, "all_quotes_verified_after_amend": ok, "statuses": st})
    for r in gate[a["topic"]]["rows"]:
        if r["n"] == n:
            r["spans_verified"] = ok
            r["amended"] = a["why"]
    print(f"AMEND {a['topic']} [{n}]: {a['why']} -> verified {ok}")
json.dump(gate, open("span_gate.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(amended, open("amendments.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

ident = {}
for slug, val in gate.items():
    fs = json.load(open(f"out/{slug}.json", encoding="utf-8"))["findings"]
    for r in val["rows"]:
        f = fs[r["n"]]
        loc = L.locate(f["claim"]["file"], f["claim"]["quote"])
        ident[f"{slug}#{r['n']}"] = {"class": f["class"], "title": f["title"], "claim_file": f["claim"]["file"],
                                     "objects": None if loc is None else len(loc),
                                     "ids": None if loc is None else [ids for _, ids in loc[:4]]}
json.dump(ident, open("identity.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
zero = [k for k, x in ident.items() if x["objects"] == 0]
many = [k for k, x in ident.items() if x["objects"] and x["objects"] > 2]
nonjson = [k for k, x in ident.items() if x["objects"] is None]
print(f"identity: {len(ident)} findings; claim in exactly 1-2 json objects: {len(ident) - len(zero) - len(many) - len(nonjson)}; "
      f"in 0 objects: {len(zero)}; in >2 objects: {len(many)}; claim not in a json file: {len(nonjson)}")
for k in zero + many:
    print("  CHECK", k, ident[k]["objects"], ident[k]["title"][:80])
