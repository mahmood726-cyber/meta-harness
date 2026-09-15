V-corticosteroids-covid19-mortality VERDICTS: NEW 19; ELIGIBLE_RCT 2; ELIGIBLE_RCT_NO_PRIMARY 3; NOT_RCT 2; WRONG_* 5; DUPLICATE_OF_ACCOUNTED 2; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 5
automated screen agreed on 5 of 19 verified
r2 includes 27 of 10607; already accounted for 8; NEW 19

Numbers: MEASURED from the listed local JSON files and harness command. Verdict labels: INFERRED from each quoted snapshot record span. No PubMed efetch was run, because no new PMID include had an empty or truncated snapshot abstract; therefore the raw HTTP body directory is intentionally empty.

ELIGIBLE_RCT ids with titles (MEASURED ids/titles; verdict INFERRED)
- 35295605 - Methylprednisolone Pulses in Hospitalized COVID-19 Patients Without Respiratory Failure: A Randomized Controlled Trial.
- 35361632 - Intravenous methylprednisolone pulses in hospitalised patients with severe COVID-19 pneumonia: a double-blind, randomised, placebo-controlled trial.

DUPLICATE_OF_ACCOUNTED pairs (INFERRED from NCT/acronym in the snapshot record)
- 35788622 -> declared-absent COVIDICUS / NCT04344730 (same NCT).
- 34917633 -> accounted MetCOVID PMID 32785710 / NCT04343729 (same NCT; day-120 follow-up).

Verdict Table
- 42079491 - ELIGIBLE_RCT_NO_PRIMARY - screen_agrees=true - quote: The primary outcome was the WHO ordinal scale at day 28. Secondary outcomes included in-hospital and 90-day mortality, oxygen and ventilation requirements, and hospital length of stay.
- 39086948 - ELIGIBLE_RCT_NO_PRIMARY - screen_agrees=true - quote: The primary endpoints included the incidence of moderate or severe ARDS and all-cause mortality within 30 days post-enrollment.
- 37189034 - WRONG_INTERVENTION - screen_agrees=false - quote: Both groups received dexamethasone 6 mg daily for 10 days.
- 35295605 - ELIGIBLE_RCT - screen_agrees=true - quote: Patients admitted for confirmed SARS-CoV-2 pneumonia with raised inflammatory markers but without respiratory failure after the first week of symptom onset were randomized to receive a 3-day course of intravenous MPP (120 mg/day) or placebo. The secondary outcomes were 28-day mortality
- 35361632 - ELIGIBLE_RCT - screen_agrees=true - quote: The key secondary outcomes were survival free from invasive ventilation with orotracheal intubation and overall survival.
- 35537738 - NOT_RCT - screen_agrees=false - quote: DESIGN: Meta-epidemiological study.
- 35617986 - WRONG_COMPARATOR - screen_agrees=false - quote: We assessed the combination of baricitinib plus remdesivir versus dexamethasone plus remdesivir in preventing progression to mechanical ventilation or death in hospitalised patients with COVID-19.
- 35788622 - DUPLICATE_OF_ACCOUNTED - screen_agrees=false - quote: TRIAL REGISTRATION: ClinicalTrials.gov Identifier: NCT04344730; EudraCT: 2020-001457-43.
- 36173596 - WRONG_COMPARATOR - screen_agrees=false - quote: comparing the efficacy and safety of an oral combination of prednisone (60 mg/day for 3 days) and colchicine (at loading doses of 1-1.5 mg/day for 3 days, followed by 0.5 mg/day for 11 days) with the standard treatment, based on intravenous dexamethasone.
- 36384737 - WRONG_POPULATION - screen_agrees=false - quote: Prednisolone does not improve olfactory function after COVID-19: a randomized, double-blind, placebo-controlled trial.
- 34153729 - NOT_RCT - screen_agrees=false - quote: While data from the control arm, consisting of patients administered usual care, were obtained through retrospective review of their electronic medical records.
- 34917633 - DUPLICATE_OF_ACCOUNTED - screen_agrees=false - quote: Trial Registration: ClinicalTrials.gov, Identifier: NCT04343729.
- 35036193 - WRONG_COMPARATOR - screen_agrees=false - quote: No study has compared these two against each other. We aimed to compare the efficacy and safety of HDD against TCZ in moderate to severe COVID-ARDS.
- 32943404 - ELIGIBLE_RCT_NO_PRIMARY - screen_agrees=true - quote: The study end-point was the time of clinical improvement or death, whichever came first.
- NCT04244591 - REGISTRY_ONLY_NO_PUBLICATION - screen_agrees=false - quote: conditions: COVID-19 Infections; interventions: methylprednisolone therapy; Standard care; allocation: RANDOMIZED; has_results: False
- NCT04343729 - REGISTRY_ONLY_NO_PUBLICATION - screen_agrees=false - quote: conditions: SARS-CoV Infection; Severe Acute Respiratory Syndrome (SARS) Pneumonia; interventions: Methylprednisolone Sodium Succinate; Placebo solution; allocation: RANDOMIZED; has_results: False
- NCT04438980 - REGISTRY_ONLY_NO_PUBLICATION - screen_agrees=false - quote: conditions: Covid-19 Pneumonia; interventions: Methylprednisolone; Placebo; allocation: RANDOMIZED; has_results: False
- NCT04640168 - REGISTRY_ONLY_NO_PUBLICATION - screen_agrees=false - quote: conditions: COVID-19; interventions: Baricitinib; Dexamethasone; Placebo; Remdesivir; allocation: RANDOMIZED; has_results: True
- NCT04673162 - REGISTRY_ONLY_NO_PUBLICATION - screen_agrees=false - quote: conditions: Covid19; interventions: Methylprednisolone, Placebo; allocation: RANDOMIZED; has_results: False

Commands Run (MEASURED)
- `Get-Content -Raw -LiteralPath .\LANE_PROMPT.md`
- `if (Test-Path -LiteralPath 'F:\ProjectIndex\INDEX.md') { Get-Content -Raw -LiteralPath 'F:\ProjectIndex\INDEX.md' } elseif (Test-Path -LiteralPath '.\LIVE_CONTEXT.md') { Get-Content -Raw -LiteralPath '.\LIVE_CONTEXT.md' }`
- `if (Test-Path -LiteralPath 'F:\E156\rewrite-workbook.txt') { Get-Content -Raw -LiteralPath 'F:\E156\rewrite-workbook.txt' } elseif (Test-Path -LiteralPath '.\LIVE_CONTEXT.md') { Get-Content -Raw -LiteralPath '.\LIVE_CONTEXT.md' }`
- `git status --short`
- `Get-Content -Raw -LiteralPath .\protocols\corticosteroids-covid19-mortality.md`
- `Get-Content -Raw -LiteralPath .\topics\corticosteroids-covid19-mortality.json`
- `Get-Content -Raw -LiteralPath .\docs\reviews\corticosteroids-covid19-mortality\review.json`
- `python -c \"import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/corticosteroids-covid19-mortality.json',encoding='utf-8')); d=json.load(open('cache/corticosteroids-covid19-mortality/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))\"`
- `python -c \"import json; p='cache/corticosteroids-covid19-mortality/snapshots/2026-09-15r2-search_v2/records.json'; d=json.load(open(p,encoding='utf-8')); print(type(d).__name__); print(d.keys() if isinstance(d,dict) else 'list'); print('n_records', len(d['records'] if isinstance(d,dict) and 'records' in d else d)); dec=(d.get('screening',{}).get('decisions') if isinstance(d,dict) else None); print('n_decisions', len(dec or [])); print('first_record_keys', list((d['records'][0] if isinstance(d,dict) else d[0]).keys()))\"`
- `python -c \"import json; r=json.load(open('docs/reviews/corticosteroids-covid19-mortality/review.json',encoding='utf-8')); print('top keys', sorted(r.keys())); print('outcomes type', type(r.get('outcomes')).__name__); print('declared_absent_trials', r.get('declared_absent_trials')); outs=r.get('outcomes') or []; print('n_outcomes', len(outs)); print('first outcome keys', sorted(outs[0].keys()) if outs else None); print('first outcome trials', outs[0].get('trials') if outs else None)\"`
- `python -c \"import json; d=json.load(open('cache/corticosteroids-covid19-mortality/snapshots/2026-09-15r2-search_v2/records.json',encoding='utf-8')); dec=(d.get('screening',{}).get('decisions') or []); inc=[x for x in dec if x.get('decision')=='include']; print('includes',len(inc)); print([x.get('id') for x in inc[:30]])\"`
- `python -c <population-inspection one-liner with inline def> (failed with SyntaxError; no files written)`
- `@' <population-inspection Python script> '@ | python -`
- `@' <new-include abstract dump Python script> '@ | python -`
- `@' <NCT structured-field inspection Python script> '@ | python -`
- `rg -n \"NCT04244591|NCT04343729|NCT04438980|NCT04640168|NCT04673162\" .`
- `Get-ChildItem -LiteralPath .\cache\corticosteroids-covid19-mortality -Recurse -File | Select-Object -ExpandProperty FullName`
- `@' <retrieval-ledger record inspection Python script> '@ | python -`
- `python -c \"import json; d=json.load(open('cache/corticosteroids-covid19-mortality/snapshots/2026-09-15r2-search_v2/retrieval_ledger.json',encoding='utf-8')); print(type(d), d.keys() if isinstance(d,dict) else 'list'); print(json.dumps(list(d.items())[:3], indent=2)[:2000])\"`
- `@' <retrieval-ledger per-id inspection Python script> '@ | python -`
- `@' <candidate-export schema cross-check Python script> '@ | python -`
- `Test-Path -LiteralPath .\lane_v; if (Test-Path -LiteralPath .\lane_v) { Get-ChildItem -LiteralPath .\lane_v -Force | Select-Object -ExpandProperty FullName }`
- `@' <artifact writer Python script> '@ | python - (failed: quote too long for 35295605)`
- `@' <artifact writer Python script> '@ | python -`
- `@' <artifact validator Python script> '@ | python -`
- `git status --short`
