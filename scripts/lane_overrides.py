"""LANE: audit every override's reason against source. An override can FORCE a state (esp.
declared-absent) with a hand-written reason nothing verified — how a page can say 'no harms recorded'
while the abstract reports harms. For each override, especially ABSENT ones, check whether the HELD
abstract CONTRADICTS the reason (an ABSENT override whose abstract shows an effect/counts is suspect).
Local + deterministic; flags for human confirmation. Writes scratchpad/override_audit.json (OUT-first).
"""
import json, os, sys, io, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness.verified_inputs import entries, load, runtime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
OUT = os.path.join(ROOT, "scratchpad", "override_audit.json")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({"status": "STARTED"}, open(OUT, "w", encoding="utf-8"))

_EFFECT = re.compile(r"\b(?:RR|OR|HR|IRR|rate ratio|risk ratio|hazard ratio|odds ratio)\b[^.]{0,40}?\d+\.\d+", re.I)
_ARMS = re.compile(r"\b\d+\s*/\s*\d{2,}\b|\b\d+\s+of\s+\d{2,}\b", re.I)


def abstracts(slug):
    p = os.path.join(ROOT, "cache", slug, "records.json")
    if not os.path.exists(p):
        return {}
    r = json.load(open(p, encoding="utf-8"))
    r = r.get("records", r) if isinstance(r, dict) else r
    return {str(x.get("id")): (x.get("abstract") or "") for x in r}


rows = []
for f in glob.glob(os.path.join(ROOT, "cache", "*", "verified_arms.json")) + \
         glob.glob(os.path.join(ROOT, "cache", "*", "verified_effects.json")):
    slug = f.split(os.sep)[-2]
    ab = abstracts(slug)
    values = load(slug)[os.path.basename(f)]
    for pmid, e in ((pid, entry) for pid, value in values.items() for raw in entries(value) for entry in [runtime(raw)]):
        if not (isinstance(e, dict) and e.get("override")):
            continue
        forces = "ABSENT" if e.get("absent") else ("effect" if e.get("effect") is not None else
                 ("arms" if e.get("ai") is not None else ("mean" if e.get("mean1") is not None else "?")))
        has_reason = bool(e.get("reason") or e.get("source"))
        a = ab.get(str(pmid), "")
        # for an ABSENT override, does the abstract CONTRADICT absence (show an effect/counts)?
        contradiction = None
        if e.get("absent") and a:
            m = _EFFECT.search(a) or _ARMS.search(a)
            if m:
                contradiction = m.group(0)[:80]
        rows.append({"slug": slug, "pmid": pmid, "outcome": e.get("outcome"), "forces": forces,
                     "provenance": e.get("provenance"), "has_reason": has_reason,
                     "abstract_contradicts_absent": contradiction})

absent = [r for r in rows if r["forces"] == "ABSENT"]
suspect = [r for r in absent if r["abstract_contradicts_absent"]]
no_reason = [r for r in rows if not r["has_reason"]]
json.dump({"status": "DONE", "total_overrides": len(rows), "absent_overrides": len(absent),
           "absent_with_abstract_contradiction": len(suspect), "overrides_with_no_reason": len(no_reason),
           "rows": rows}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"OUT_WRITTEN {OUT} overrides={len(rows)} absent={len(absent)} "
      f"suspect_absent={len(suspect)} no_reason={len(no_reason)}")
