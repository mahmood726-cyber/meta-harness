"""LANE: not-extracted re-check, OUTCOME-SCOPED (fixes the any-effect over-match). For each
declared-absent 'not extracted' trial, use the OUTCOME's registered keywords to select the outcome's
OWN sentences from the held abstract, then look for an effect+CI or arm counts WITHIN those sentences
only. Collapses the noisy 189 to candidates where the MISSING outcome's number is actually present.
Writes scratchpad/notextracted_scoped.json (OUT-first)."""
import json, os, sys, io, re, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import extract
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
OUT = os.path.join(ROOT, "scratchpad", "notextracted_scoped.json")
json.dump({"status": "STARTED"}, open(OUT, "w", encoding="utf-8"))
_ABS = re.compile(r"not extracted|no effect|no percentage-corroborated|not found in the abstract", re.I)
_EFF = re.compile(r"\b(?:RR|OR|HR|IRR|rate ratio|risk ratio|hazard ratio|odds ratio)\b[^.]{0,40}?\d+\.\d+[^.]{0,50}?(?:CI|confidence|\d+\.\d+\s*(?:to|[-\u2013])\s*\d+\.\d+)", re.I)
_ARM = re.compile(r"\b\d+\s*/\s*\d{2,}\b|\b\d+\s+of\s+\d{2,}\b", re.I)
_HARM = re.compile(r"bleed|h[ae]morrhage|diarrh|adverse|hypoglyc|hyperkal|discontinu", re.I)
def kwmap(slug):
    t = json.load(open(os.path.join(ROOT,"topics",slug+".json"),encoding="utf-8"))
    m = {}
    po = t.get("primary_outcome") or {}
    if po.get("name"): m[po["name"]] = po.get("keywords") or []
    for o in (t.get("secondary_outcomes") or []) + (t.get("harm_outcomes") or []):
        if o.get("name"): m[o["name"]] = o.get("keywords") or []
    return m
flags=[]; checked=0
for rp in sorted(glob.glob(os.path.join(ROOT,"docs","reviews","*","review.json"))):
    slug=os.path.basename(os.path.dirname(rp)); rv=json.load(open(rp,encoding="utf-8"))
    recs={str(x.get("id")):(x.get("abstract") or "") for x in json.load(open(os.path.join(ROOT,"cache",slug,"records.json"),encoding="utf-8")).get("records",[])}
    km=kwmap(slug)
    for o in rv.get("outcomes",[]):
        kws=km.get(o.get("name")) or []
        if not kws: continue
        for t in o.get("declared_absent_trials",[]) or []:
            if not _ABS.search(t.get("reason") or ""): continue
            pid=str(t.get("label") or t.get("id") or "").replace("PMID ","")
            ab=recs.get(pid,"")
            if not ab: continue
            checked+=1
            sents=extract._outcome_sentences(ab,kws)  # the OUTCOME's own sentences
            joined=" ".join(sents)
            m=_EFF.search(joined) or _ARM.search(joined)
            if m:
                flags.append({"slug":slug,"outcome":o.get("name"),"pmid":pid,"is_harm":bool(_HARM.search(o.get("name") or "")),"found":m.group(0)[:80]})
harms=[f for f in flags if f["is_harm"]]
json.dump({"status":"DONE","checked":checked,"scoped_candidates":len(flags),"harms":len(harms),"flags":flags},open(OUT,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(f"OUT_WRITTEN {OUT} checked={checked} scoped_candidates={len(flags)} harms={len(harms)}")
