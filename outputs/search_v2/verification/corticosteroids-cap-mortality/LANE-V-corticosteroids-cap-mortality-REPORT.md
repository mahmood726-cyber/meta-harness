V-corticosteroids-cap-mortality VERDICTS: NEW 26; ELIGIBLE_RCT 1; ELIGIBLE_RCT_NO_PRIMARY 4; NOT_RCT 7; WRONG_* 2; DUPLICATE_OF_ACCOUNTED 12; UNDECIDABLE 0; NOT_VERIFIED_CAP 0
automated screen agreed on 5 of 26 verified
r2 includes 35 of 1465; already accounted for 9; NEW 26

MEASURED: Counts above come from the r2 snapshot decisions, required legacy include replay, and served review primary-outcome accounted labels.
MEASURED: No PubMed efetch was needed; every PMID NEW record had a non-empty, complete-looking snapshot abstract, and NCT-only records had no PMID to efetch.
INFERRED: Duplicate labels use same NCT/acronym/trial-name relationships visible in snapshot fields or title/abstract text.

ELIGIBLE_RCT ids with titles:
- 41159889: A Pragmatic Trial of Glucocorticoids for Community-Acquired Pneumonia.

DUPLICATE_OF_ACCOUNTED pairs:
- 38082273 -> PMID 25608756 (same STEP/NCT00973154 trial)
- 34782191 -> PMID 33446608 (same Santeon-CAP/NCT01743755 trial)
- 30485501 -> PMID 25608756 (same STEP/NCT00973154 trial)
- 30873676 -> PMID 25608756 (same STEP trial)
- 31540339 -> PMID 25688779 (same NCT00908713 trial)
- 28617807 -> PMID 25688779 (same NCT00908713 trial)
- 27471201 -> PMID 25608756 (same STEP/NCT00973154 trial)
- 27614658 -> PMID 25608756 (same STEP/NCT00973154 trial)
- NCT02517489 -> PMID 36942789 (same CAPE_COD/NCT02517489 trial)
- 24974155 -> PMID 25608756 (STEP/NCT00973154 protocol)
- NCT01743755 -> PMID 33446608 (same Santeon-CAP/NCT01743755 trial)
- NCT00908713 -> PMID 25688779 (same NCT00908713 trial)

Commands run:
- `Get-Content -Raw -LiteralPath 'LANE_PROMPT.md'`
- `Get-Content -Raw -LiteralPath 'F:\ProjectIndex\INDEX.md'`
- `Get-Content -Raw -LiteralPath 'F:\E156\rewrite-workbook.txt'`
- `git status --short`
- `Get-Content -Raw -LiteralPath 'protocols\corticosteroids-cap-mortality.md'`
- `Get-Content -Raw -LiteralPath 'topics\corticosteroids-cap-mortality.json'`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/corticosteroids-cap-mortality.json',encoding='utf-8')); d=json.load(open('cache/corticosteroids-cap-mortality/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `python - <<'PY' ... PY  # failed in PowerShell before reading review.json`
- `python -c "import json; d=json.load(open('docs/reviews/corticosteroids-cap-mortality/review.json',encoding='utf-8')); print('top keys', sorted(d.keys())); ..."`
- `python -c "import json; p='cache/corticosteroids-cap-mortality/snapshots/2026-09-15r2-search_v2/records.json'; d=json.load(open(p,encoding='utf-8')); print(type(d).__name__); ..."`
- `python -c "import json,collections; p='cache/corticosteroids-cap-mortality/snapshots/2026-09-15r2-search_v2/records.json'; d=json.load(open(p,encoding='utf-8')); dec=d.get('screening',{}).get('decisions',[]); ..."`
- `python -c "import json; d=json.load(open('docs/reviews/corticosteroids-cap-mortality/review.json',encoding='utf-8')); out=[o for o in d.get('outcomes',[]) if o.get('primary')][0]; ..."`
- `python -c "import json,sys; ... def key(r): ..."  # failed SyntaxError in one-line NEW-set draft`
- `python -c "import json,sys; ... key=lambda r: ...; new=[r for r in inc if key(r) not in accounted]; ..."`
- `python -c "import json,sys; ... print(json.dumps(rows, ensure_ascii=False, indent=2))"`
- `python -c "import json; d=json.load(open('cache/corticosteroids-cap-mortality/snapshots/2026-09-15r2-search_v2/records.json',encoding='utf-8')); ids={'NCT01743755','NCT00908713','NCT02517489','NCT04652414'}; ..."`
- `python -c "import json,sys; ... for r in new: print(key(r), r.get('year'), 'len', len(a), 'title=', r.get('title')); ..."`
- `python -c "import json; ids=['34782191','34031890','NCT04652414','30485501','30873676']; ..."`
- `python -c "import json; ids=['31282921','31540339','28617807','27471201','27614658']; ..."`
- `python -c "import json; ids=['NCT02517489','24817026','24974155','22379064','22402329']; ..."`
- `python -c "import json; ids=['22410382','22855392','NCT01743755','20133929','17710485','NCT00908713']; ..."`
- `python -c "import json,sys; ... print(json.dumps(sorted(rows,key=lambda x:str(x.get('id'))), ensure_ascii=False, indent=2))"`
- `PowerShell here-string piped to python - (writer/validator for lane_v JSON, raw directory, and report)`
