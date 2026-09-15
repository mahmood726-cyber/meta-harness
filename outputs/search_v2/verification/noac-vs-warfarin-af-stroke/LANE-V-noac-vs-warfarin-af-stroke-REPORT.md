V-noac-vs-warfarin-af-stroke VERDICTS: NEW 262; ELIGIBLE_RCT 3; ELIGIBLE_RCT_NO_PRIMARY 9; NOT_RCT 88; WRONG_* 39; DUPLICATE_OF_ACCOUNTED 0; UNDECIDABLE 11; NOT_VERIFIED_CAP 112
automated screen agreed on 12 of 150 verified
r2 includes 272 of 12238; already accounted for 10; NEW 262
MEASURED: verification cap applied because NEW 262 > 150; first 150 verified by year desc then identifier; 112 marked NOT_VERIFIED_CAP.

## ELIGIBLE_RCT ids with titles
- 36335914: Apixaban for Patients With Atrial Fibrillation on Hemodialysis: A Multicenter Randomized Controlled Trial.
- 33626904: Early Apixaban Use Following Stroke in Patients With Atrial Fibrillation: Results of the AREST Trial.
- 28892526: Rivaroxaban vs Warfarin Sodium in the Ultra-Early Period After Atrial Fibrillation-Related Mild Ischemic Stroke: A Randomized Clinical Trial.

## DUPLICATE_OF_ACCOUNTED pairs
- None MEASURED.

## Count Basis
- MEASURED legacy includes: 10 (19717844, 21830957, 21870978, 24251359, NCT00504556, NCT00806624, NCT00829933, NCT02935855, NCT03153150, NCT05006287).
- MEASURED pooled primary-outcome trial ids: 19717844, 21830957, 21870978, 24251359.
- MEASURED declared-absent primary-outcome trial ids: NCT00504556, NCT00806624, NCT00829933, NCT02935855, NCT05006287, ORGANON.
- MEASURED accounted r2 include records by pmid-else-nct-else-doi key: 10.
- INFERRED labels in notes identify secondary/subgroup analyses from title/abstract wording only; no pooling decision is made here.

## Commands run
- `Get-Content -LiteralPath .\LANE_PROMPT.md`
- `git status --short`
- `if (Test-Path -LiteralPath 'F:\ProjectIndex\INDEX.md') { Get-Content -LiteralPath 'F:\ProjectIndex\INDEX.md' -TotalCount 80 } elseif (Test-Path -LiteralPath '.\LIVE_CONTEXT.md') { Get-Content -LiteralPath '.\LIVE_CONTEXT.md' -TotalCount 120 } else { 'NO_INDEX_OR_LIVE_CONTEXT' }`
- `if (Test-Path -LiteralPath 'F:\E156\rewrite-workbook.txt') { Get-Content -LiteralPath 'F:\E156\rewrite-workbook.txt' -TotalCount 120 } elseif (Test-Path -LiteralPath '.\LIVE_CONTEXT.md') { Get-Content -LiteralPath '.\LIVE_CONTEXT.md' -TotalCount 120 } else { 'NO_WORKBOOK_OR_LIVE_CONTEXT' }`
- `Get-Content -LiteralPath .\protocols\noac-vs-warfarin-af-stroke.md`
- `Get-Content -LiteralPath .\topics\noac-vs-warfarin-af-stroke.json`
- `python -c "import json; p='docs/reviews/noac-vs-warfarin-af-stroke/review.json'; d=json.load(open(p,encoding='utf-8')); print(json.dumps({k:d.get(k) for k in d.keys() if k in ['slug','primary_outcome','declared_absent_trials']}, indent=2)[:12000])"`
- `python -c "import json; p='cache/noac-vs-warfarin-af-stroke/snapshots/2026-09-15r2-search_v2/records.json'; d=json.load(open(p,encoding='utf-8')); print(type(d).__name__, d.keys() if isinstance(d,dict) else len(d)); print('records', len(d.get('records',[]))); print('decisions', len(d.get('screening',{}).get('decisions',[]))); print('first rec keys', sorted(d.get('records',[{}])[0].keys()))"`
- `python -c "import json; d=json.load(open('docs/reviews/noac-vs-warfarin-af-stroke/review.json',encoding='utf-8')); print('keys', sorted(d.keys())); import pprint; pp=pprint.PrettyPrinter(width=120); pp.pprint(d)"`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/noac-vs-warfarin-af-stroke.json',encoding='utf-8')); d=json.load(open('cache/noac-vs-warfarin-af-stroke/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `python -c "import json, collections; p='cache/noac-vs-warfarin-af-stroke/snapshots/2026-09-15r2-search_v2/records.json'; d=json.load(open(p,encoding='utf-8')); dec=d['screening']['decisions']; print('include', sum(1 for x in dec if x.get('decision')=='include'), 'of', len(d['records'])); print('rule counts'); print(collections.Counter(x.get('rule_id') for x in dec if x.get('decision')=='include').most_common(20));"`
- `rg --files -g "*noac-vs-warfarin-af-stroke*"`
- `python - <<'PY' (failed in PowerShell; Bash heredoc syntax unsupported) for review outcome inspection`
- `python - <<'PY' (failed in PowerShell; Bash heredoc syntax unsupported) for include-record inspection`
- `if (Test-Path -LiteralPath .\lane_v) { Get-ChildItem -LiteralPath .\lane_v -Recurse | Select-Object FullName,Length,LastWriteTime | Format-Table -AutoSize } else { 'NO lane_v' }`
- `python -c "import json; d=json.load(open('docs/reviews/noac-vs-warfarin-af-stroke/review.json',encoding='utf-8')); print('outcomes type', type(d.get('outcomes')).__name__); print(json.dumps(d.get('outcomes'), indent=2)[:20000]); print('declared_absent top', json.dumps(d.get('declared_absent_trials'), indent=2))"`
- `python -c "import json; d=json.load(open('cache/noac-vs-warfarin-af-stroke/snapshots/2026-09-15r2-search_v2/records.json',encoding='utf-8')); records={r['id']:r for r in d['records']}; incs=[x for x in d['screening']['decisions'] if x.get('decision')=='include']; print('n_inc',len(incs),'n_records',len(d['records'])); ... first ten include records ..."`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; ... print('legacy', len(legacy_inc), legacy_inc); print('r2_inc', len(incs));"`
- `python -c one-line NEW population computation with local def (failed SyntaxError; compound def after semicolon)`
- `python -c "import json; ... print('include abstracts zero', len(missing), 'short<250', len(short), ...);"`
- `PowerShell here-string piped to python computing accounted set and NEW sorted population`
- `PowerShell here-string piped to python listing empty abstracts among first 150 and cap start`
- `New-Item -ItemType Directory -Force -Path .\lane_v\noac-vs-warfarin-af-stroke-raw | Out-Null; Invoke-WebRequest PubMed efetch PMID 29653640 -OutFile ... (failed connection before body)`
- `curl.exe -L PubMed efetch PMID 29653640 -o .\lane_v\noac-vs-warfarin-af-stroke-raw\pubmed-29653640.xml (failed local Schannel credentials before body)`
- `python -c "import urllib.request; url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=29653640&retmode=xml'; data=urllib.request.urlopen(url, timeout=30).read(); open('lane_v/noac-vs-warfarin-af-stroke-raw/pubmed-29653640.xml','wb').write(data); print(len(data))"`
- `python -c "import xml.etree.ElementTree as ET; p='lane_v/noac-vs-warfarin-af-stroke-raw/pubmed-29653640.xml'; ... print('abstract sections', len(texts)); ..."`
- `python -c "import xml.etree.ElementTree as ET; p='lane_v/noac-vs-warfarin-af-stroke-raw/pubmed-29653640.xml'; ... print(title)"`
- `PowerShell here-string piped to python printing verification rows 1-25`
- `PowerShell here-string piped to python printing verification rows 26-50`
- `PowerShell here-string piped to python compact verification table for rows 1-150`
- `PowerShell here-string piped to python printing full rows 71-90`
- `PowerShell here-string piped to python printing full rows 91-115`
- `PowerShell here-string piped to python printing compact rows 32-70`
- `PowerShell here-string piped to python printing full rows 102-108`
- `PowerShell here-string piped to python printing full rows 116-150`
- `PowerShell here-string piped to python printing full rows 131-134`
- `PowerShell here-string piped to python generating lane_v/noac-vs-warfarin-af-stroke.json and LANE-V-noac-vs-warfarin-af-stroke-REPORT.md with internal validation`

## Validation
- MEASURED JSON objects: 262; expected NEW: 262.
- MEASURED first-line category sum: 262.
- MEASURED non-empty quotes for all non-UNDECIDABLE/non-NOT_VERIFIED_CAP records: PASS.
