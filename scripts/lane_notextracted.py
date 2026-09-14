"""LANE: re-check every 'not extracted / no effect in abstract' declared-absence against the HELD
abstract. Three confirmed false so far (CLEAR SYNERGY GI, PHILO bleeding, REWIND GI), all harms: we
asserted absence without re-reading the source. For each declared-absent trial whose reason claims the
value is not in the abstract, scan the committed abstract for an effect+CI or arm counts; if present,
FLAG as a candidate false-absence (report harms separately). Local + deterministic. Writes
scratchpad/notextracted_recheck.json (OUT-first).
"""
import json, os, sys, io, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
OUT = os.path.join(ROOT, "scratchpad", "notextracted_recheck.json")
json.dump({"status": "STARTED"}, open(OUT, "w", encoding="utf-8"))

_ABSENCE = re.compile(r"not extracted|no effect|no percentage-corroborated|abstract only|not found in the abstract|no .*ci", re.I)
_EFFECT = re.compile(r"\b(?:RR|OR|HR|IRR|rate ratio|risk ratio|hazard ratio|odds ratio|relative risk)\b[^.]{0,40}?\d+\.\d+[^.]{0,40}?(?:CI|confidence interval|\d+\.\d+\s*(?:to|[-–])\s*\d+\.\d+)", re.I)
_ARMS = re.compile(r"\b\d+\s*/\s*\d{2,}\b|\b\d+\s+of\s+\d{2,}\b|\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten)\s+of\s+\d{2,}\b", re.I)
_HARM = re.compile(r"bleed|h[ae]morrhage|diarrh|adverse|hypoglyc|hyperkal|infection|discontinu|nausea|vomit|injection|hypersensit", re.I)


def held_abstracts(slug):
    p = os.path.join(ROOT, "cache", slug, "records.json")
    if not os.path.exists(p):
        return {}
    r = json.load(open(p, encoding="utf-8"))
    r = r.get("records", r) if isinstance(r, dict) else r
    return {str(x.get("id")): (x.get("abstract") or "") for x in r}


flags = []
checked = 0
for rp in sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json"))):
    slug = os.path.basename(os.path.dirname(rp))
    rv = json.load(open(rp, encoding="utf-8"))
    abstr = held_abstracts(slug)
    for o in rv.get("outcomes", []):
        for t in o.get("declared_absent_trials", []) or []:
            reason = t.get("reason") or ""
            if not _ABSENCE.search(reason):
                continue
            pid = str(t.get("label") or t.get("id") or "").replace("PMID ", "")
            ab = abstr.get(pid, "")
            if not ab:
                continue
            checked += 1
            eff = _EFFECT.search(ab)
            arms = _ARMS.search(ab)
            if eff or arms:
                flags.append({"slug": slug, "outcome": o.get("name"), "pmid": pid,
                              "is_harm": bool(_HARM.search(o.get("name") or "")),
                              "found": (eff.group(0)[:90] if eff else arms.group(0)),
                              "reason_said": reason[:80]})

harms = [f for f in flags if f["is_harm"]]
json.dump({"status": "DONE", "checked": checked, "candidate_false_absences": len(flags),
           "of_which_harms": len(harms), "flags": flags,
           "_doc": "declared-absent 'not extracted' whose HELD abstract nonetheless shows an effect+CI or "
                   "arm counts -> candidate false-absence (needs source confirmation before acting)."},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"OUT_WRITTEN {OUT} checked={checked} candidate_false_absences={len(flags)} harms={len(harms)}")
