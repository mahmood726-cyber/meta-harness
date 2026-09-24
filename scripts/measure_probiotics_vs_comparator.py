"""Cross-check (read-only): of the trials the probiotics comparator meta-analysis (Goodman 2021 BMJ Open; its list is
committed in docs/evidence/probiotics-search-diagnostic-2026-09-15/01-their-42.txt) included, which does the served
review EXCLUDE -- and are they among the records both recorded model readers read as ELIGIBLE against the exclusion?
A published review's inclusion is an independent, model-free signal. Prints; writes nothing."""
import json, re
from pathlib import Path
txt = Path("docs/evidence/probiotics-search-diagnostic-2026-09-15/01-their-42.txt").read_text(encoding="utf8")
theirs = {m.group(2): m.group(1).strip() for m in re.finditer(r"^\| \d+ \| ([^|]+)\|[^|]*\|[^|]*\| (\d+) \|", txt, re.M)}
rev = json.loads(Path("docs/reviews/probiotics-aad-prevention/review.json").read_text(encoding="utf8"))
served = {str(r["id"]): r["decision"] for r in rev["screening"]["records"]}
rep = json.loads(Path("outputs/model_source/READERS_screening_excluded.json").read_text(encoding="utf8"))
both = [i.split("::")[1].split(":", 1)[1] for i in rep["both_against_rule"] if i.startswith("probiotics-aad-prevention")]
print("comparator (Goodman 2021) trials with a PMID:", len(theirs))
print("  of those, served as include:", sum(served.get(p) == "include" for p in theirs), "| exclude:", sum(served.get(p) == "exclude" for p in theirs), "| not screened:", sum(p not in served for p in theirs))
hit = [p for p in both if p in theirs]
print("probiotics records BOTH readers call ELIGIBLE against the exclusion:", len(both), "| of which the comparator INCLUDED:", len(hit))
for p in hit: print("   ", p, theirs[p])
