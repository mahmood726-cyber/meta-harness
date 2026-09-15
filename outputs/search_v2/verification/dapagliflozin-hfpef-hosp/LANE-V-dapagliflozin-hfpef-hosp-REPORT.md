V-dapagliflozin-hfpef-hosp VERDICTS: NEW 18; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 0; NOT_RCT 0; WRONG_* 0; DUPLICATE_OF_ACCOUNTED 18; UNDECIDABLE 0; NOT_VERIFIED_CAP 0
automated screen agreed on 0 of 18 verified
r2 includes 23 of 2757
already accounted for 5
NEW 18

Measurement Status
- Counts above are MEASURED from the named cache/review files.
- Duplicate interpretation is INFERRED from same NCT/acronym links in the snapshot/review records.
- PubMed/HTTP fetch status is MEASURED: No HTTP bodies were fetched; all verdicts used committed snapshot title/abstract fields.
- Cap status is MEASURED: No cap applied; all NEW records verified.

ELIGIBLE_RCT ids with titles
None

DUPLICATE_OF_ACCOUNTED pairs
- 37952176 -> Same NCT/acronym as pooled DELIVER (PMID 36027570; NCT03619213); not a new trial for pooling.
- 38639697 -> Same NCT/acronym as declared-absent PRESERVED-HF (PMID 34711976; NCT03030235); not a new trial for pooling.
- 39046727 -> Same NCT/acronym as declared-absent CAMEO-DAPA (PMID 37534453; NCT04730947); not a new trial for pooling.
- 39101201 -> Same NCT/acronym as declared-absent CAMEO-DAPA (PMID 37534453; NCT04730947); not a new trial for pooling.
- 36326604 -> Same NCT/acronym as pooled DELIVER (PMID 36027570; NCT03619213); not a new trial for pooling.
- 37208998 -> Same NCT/acronym as pooled DELIVER (PMID 36027570; NCT03619213); not a new trial for pooling.
- 37212168 -> Same NCT/acronym as pooled DELIVER (PMID 36027570; NCT03619213); not a new trial for pooling.
- 37294244 -> Same NCT/acronym as pooled DELIVER (PMID 36027570; NCT03619213); not a new trial for pooling.
- 37869881 -> Same NCT/acronym as declared-absent PRESERVED-HF (PMID 34711976; NCT03030235); not a new trial for pooling.
- 36029467 -> Same NCT/acronym as pooled DELIVER (PMID 36027570; NCT03619213); not a new trial for pooling.
- 36041668 -> Same NCT/acronym as pooled DELIVER (PMID 36027570; NCT03619213); not a new trial for pooling.
- 36041912 -> Same NCT/acronym as pooled DELIVER (PMID 36027570; NCT03619213); not a new trial for pooling.
- 36114137 -> Same NCT/acronym as pooled DELIVER (PMID 36027570; NCT03619213); not a new trial for pooling.
- 36190011 -> Same NCT/acronym as pooled DELIVER (PMID 36027570; NCT03619213); not a new trial for pooling.
- 36372069 -> Same NCT/acronym as pooled DELIVER (PMID 36027570; NCT03619213); not a new trial for pooling.
- NCT04730947 -> Same NCT/acronym as declared-absent CAMEO-DAPA (PMID 37534453; NCT04730947); not a new trial for pooling.
- NCT03619213 -> Same NCT/acronym as pooled DELIVER (PMID 36027570; NCT03619213); not a new trial for pooling.
- NCT03030235 -> Same NCT/acronym as declared-absent PRESERVED-HF (PMID 34711976; NCT03030235); not a new trial for pooling.

Commands Run
- `Get-Content -LiteralPath .\LANE_PROMPT.md`
- `Get-Content -LiteralPath .\LIVE_CONTEXT.md  # failed: LIVE_CONTEXT.md not present in current directory`
- `Test-Path -LiteralPath F:\ProjectIndex\INDEX.md; Test-Path -LiteralPath F:\E156\rewrite-workbook.txt`
- `Get-Content -LiteralPath F:\ProjectIndex\INDEX.md`
- `Get-Content -LiteralPath F:\E156\rewrite-workbook.txt`
- `git status --short`
- `Get-Content -LiteralPath .\protocols\dapagliflozin-hfpef-hosp.md`
- `Get-Content -LiteralPath .\topics\dapagliflozin-hfpef-hosp.json`
- `Get-Content -LiteralPath .\docs\reviews\dapagliflozin-hfpef-hosp\review.json`
- `python -c "import json,sys; sys.path.insert(0,.); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open(topics/dapagliflozin-hfpef-hosp.json,encoding=utf-8)); d=json.load(open(cache/dapagliflozin-hfpef-hosp/records.json,encoding=utf-8)); m=_dedup(d, cfg.get(pivotal_trials)); print(sorted(x[id] for x in screen.run(m,cfg)[decisions] if x[decision]==include))"`
- `python -c "import json,pprint; p=cache/dapagliflozin-hfpef-hosp/snapshots/2026-09-15r2-search_v2/records.json; d=json.load(open(p,encoding=utf-8)); print(type(d).__name__); print(sorted(d.keys()) if isinstance(d,dict) else list); print(records, len(d.get(records,[]))); print(screening keys, sorted(d.get(screening,{}).keys()) if isinstance(d,dict) else None); r=d.get(records,[{}])[0]; print(record keys, sorted(r.keys())); dec=d.get(screening,{}).get(decisions,[]); print(decisions, len(dec)); print(decision keys, sorted(dec[0].keys()) if dec else None)"`
- `python -c "import json,pprint; d=json.load(open(docs/reviews/dapagliflozin-hfpef-hosp/review.json,encoding=utf-8)); print(top keys, sorted(d.keys())); print(outcomes type, type(d.get(outcomes)).__name__); print(outcomes len, len(d.get(outcomes,[])) if isinstance(d.get(outcomes),list) else na); o=d.get(outcomes,[{}])[0] if isinstance(d.get(outcomes),list) else {}; print(outcome keys, sorted(o.keys())); print(trials, o.get(trials)); print(declared_absent_trials, d.get(declared_absent_trials) or o.get(declared_absent_trials))"`
- `python -c "...r2 NEW summary..."  # failed: PowerShell newline quoting produced SyntaxError before file writes`
- `@' ... r2 NEW summary Python script ... '@ | python -`
- `@' ... candidate abstract/title inspection Python script ... '@ | python -`
- `Test-Path -LiteralPath .\lane_v; if (Test-Path -LiteralPath .\lane_v) { Get-ChildItem -LiteralPath .\lane_v -Force | Select-Object Name,Mode,Length }`
- `Test-Path -LiteralPath .\LANE-V-dapagliflozin-hfpef-hosp-REPORT.md`
- `@' ... lane_v JSON/report generation and validation Python script ... '@ | python -  # this command`
