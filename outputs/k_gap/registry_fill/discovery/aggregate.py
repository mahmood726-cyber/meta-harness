"""Discovery hit-rate table from job_*/results.jsonl.

Denominator = the 32 sampled trials, per source. A trial-source pair absent from results is reported as NOT_CHECKED
(never silently dropped). Hit = PER_ARM_TARGET; 'any results' = PER_ARM_TARGET or PER_ARM_OTHER."""
import collections
import glob
import json
import os
import sys

D = os.path.dirname(os.path.abspath(__file__))
sample = json.load(open(os.path.join(D, "sample.json"), encoding="utf-8"))
ids = [t["id"] for t in sample["trials"]]
rows, bad = [], 0
for f in sorted(glob.glob(os.path.join(D, "job_*", "results.jsonl"))):
    fam = os.path.basename(os.path.dirname(f)).split("_")[1]
    for line in open(f, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except ValueError:
            bad += 1
            continue
        r["family"] = fam
        rows.append(r)
CANON = {"Cochrane reviews": "Cochrane", "Conference supplements": "Conference abstract supplements",
         "OpenAlex OA copies": "OpenAlex", "Unpaywall OA copies": "Unpaywall",
         "Published primary paper / secondary analyses": "Primary/secondary paper",
         "ClinicalTrials.gov_Documents": "ClinicalTrials.gov Documents",
         "ClinicalTrials.gov_results": "ClinicalTrials.gov posted results", "JPRN_UMIN": "JPRN / UMIN-CTR",
         "WHO_ICTRP": "WHO ICTRP", "FDA Drugs@FDA reviews": "FDA Drugs@FDA medical/statistical/summary reviews"}
for r in rows:
    r["source"] = CANON.get(str(r.get("source")).strip(), str(r.get("source")).strip())
best = {}
RANK = ["PER_ARM_TARGET", "PER_ARM_OTHER", "NAMED_NO_DATA", "BLOCKED_ACCOUNT", "BLOCKED_TERMS", "BLOCKED_BOT_CHALLENGE",
        "PAYWALLED", "NOT_FOUND", "NOT_APPLICABLE", "ERROR"]
for r in rows:
    k = (r["family"], str(r.get("source")).strip(), r.get("trial_id"))
    s = r.get("status")
    if k not in best or (s in RANK and (best[k].get("status") not in RANK or RANK.index(s) < RANK.index(best[k]["status"]))):
        best[k] = r
by_src = collections.defaultdict(dict)
for (fam, src, tid), r in best.items():
    by_src[(fam, src)][tid] = r
table = []
for (fam, src), m in by_src.items():
    c = collections.Counter(m.get(t, {}).get("status", "NOT_CHECKED") for t in ids)
    table.append({"family": fam, "source": src, "N": len(ids), "target": c["PER_ARM_TARGET"],
                  "other": c["PER_ARM_OTHER"], "named": c["NAMED_NO_DATA"],
                  "blocked": sum(c[x] for x in ("BLOCKED_ACCOUNT", "BLOCKED_TERMS", "BLOCKED_BOT_CHALLENGE", "PAYWALLED")),
                  "not_found": c["NOT_FOUND"], "n_a": c["NOT_APPLICABLE"], "error": c["ERROR"],
                  "not_checked": c["NOT_CHECKED"],
                  "licences": sorted({str(x.get("licence_or_terms"))[:60] for x in m.values() if x.get("status") in ("PER_ARM_TARGET", "PER_ARM_OTHER")})[:4]})
table.sort(key=lambda x: (-x["target"], -x["other"]))
trial_any = collections.defaultdict(set)
for (fam, src, tid), r in best.items():
    if r.get("status") == "PER_ARM_TARGET":
        trial_any[tid].add(f"{fam}:{src}")
json.dump({"rows": len(rows), "unparseable_lines": bad, "table": table,
           "trials_with_target_hit": {t: sorted(v) for t, v in trial_any.items()}},
          open(os.path.join(D, "hit_rates.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"rows {len(rows)}  unparseable {bad}  trials with >=1 target hit: {len(trial_any)} of {len(ids)}")
print(f"{'family':9s} {'source':42s} tgt oth nam blk nf  na err nc")
for x in table:
    print(f"{x['family']:9s} {x['source'][:42]:42s} {x['target']:3d} {x['other']:3d} {x['named']:3d} {x['blocked']:3d} "
          f"{x['not_found']:3d} {x['n_a']:3d} {x['error']:3d} {x['not_checked']:3d}")
sys.exit(0)
