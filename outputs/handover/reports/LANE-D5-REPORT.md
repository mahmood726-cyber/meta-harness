# LANE D5 report

## Summary

D5 was wrong because it could treat outcome-label similarity as evidence that the pooled outcome was registered. I changed D5 to use deterministic registered-outcome identity evidence: component-set matching for known composite families, explicit primary/secondary registry rows, quoted registry text in the basis, and fail-closed `not_assessable` when registry outcomes are absent/unknown. I also removed the embedding-backed D5 re-derivation path from the publication gate so semantic/title similarity cannot silently convert stored D5 ratings to low.

The visible family is now `registry-machine-signal-restricted` / partial machine assessment, not `RoB2`. Per-trial cache entries now carry `rob_basis`, `assessed_domains`, and `unassessed_domains`; low-only sensitivity now carries `low_only_kind`.

## Mechanism and files

Core implementation:

- `harness/rob2.py`: component signatures for 3-point MACE, MADRS change, recurrent VTE, all-cause mortality, kidney/cardiorenal composites, and HHF; secondary component-subset handling for HHF where the registered secondary is CV death/HHF; absent/unknown registry outcomes return `not_assessable`.
- `scripts/rob2_build.py`: deterministic matcher, multi-NCT PMID linkage through AACT derived references, combined D5 primary/secondary rows across linked registrations, and per-trial `rob_basis`.
- `harness/gate.py` and `scripts/rob_rederivation_sweep.py`: no embedding matcher for D5 re-derivation.
- `harness/rob_sensitivity.py`: `low_only_kind` in `{bias_sensitivity, information_availability_sensitivity, mixed}` plus adverse/unassessed exclusion counts.
- `harness/page.py`, `harness/limitations.py`, `harness/pipeline.py`, `docs/rob_spancheck.json`, visible helper strings: renamed the family to partial machine assessment.
- `tests/test_d5_rule.py`: D5 planted cases against `ad5e7c66` objects and cached registry rows.
- `scripts/d5_rule_sweep.py` and `docs/d5_rule_sweep.json`: corpus sweep.

RB patch carry-through also touched arm-contrast/gate/rederivation surfaces already documented in `LANE-RB-REPORT.md`.

## D5 plant

Exact assertions added:

- false positives fixed: stored `ad5e7c66` D5 was `some concerns`; post-fix D5 is `low`; registered text must contain the expected registry outcome phrase.
- positive controls stay low: DAPA-CKD, CREDENCE, EMPA-KIDNEY remain `low` as registered primaries.
- synthetic unregistered outcome returns `some concerns`.
- absent/UNKNOWN registry outcomes return `not_assessable`.

Quoted output from `python -m pytest tests\test_d5_rule.py -q -s`:

```text
glp1-ra-mace-t2d 28910237: pre=some concerns post=low registered=Primary Efficacy Outcome MACE Events ...
doac-vte-recurrence 21128814: pre=some concerns post=low registered=Percentage of Participants With Symptomatic Recurrent Venous Thromboembolism [VTE] ...
sglt2-primary-prevention-hf 28605608: pre=some concerns post=low registered=Composite of Cardiovascular (CV) Death Events or Hospitalization for Heart Failure ...
esketamine-trd-madrs 37025256: pre=some concerns post=low registered=Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score ...
esketamine-trd-madrs 31109201: pre=some concerns post=low registered=Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score ...
esketamine-trd-madrs NCT02422186: pre=some concerns post=low registered=Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score ...
esketamine-trd-madrs NCT02417064: pre=some concerns post=low registered=Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score ...
sglt2-ckd-progression 32970396: pre=low post=low registered=Time to the First Occurrence of Any of the Components of the Composite: \u226550% Sustained Decline in eGFR or Reaching ESRD or CV Death or Renal Death.
sglt2-ckd-progression 30990260: pre=low post=low registered=Primary Composite Endpoint of Doubling of Serum Creatinine (DoSC), End-stage Kidney Disease (ESKD), and Renal or Cardiovascular (CV) Death
sglt2-ckd-progression 36331190: pre=low post=low registered=Interventional Part: Time to First Occurrence of Kidney Disease Progression or Cardiovascular Death ('as Adjudicated')
3 passed in 80.52s (0:01:20)
```

## Corpus sweep

`python scripts\d5_rule_sweep.py --write` wrote `docs/d5_rule_sweep.json`.

```text
19 pages whose low-risk stratum was decided by an overturned D5 signal of 29 pages with a low-only stratum
35 trials D5 changed of 97 pooled trials
```

Pages whose low-only stratum changed because of D5 signal correction:

`colchicine-postop-af`, `colchicine-recurrent-pericarditis`, `corticosteroids-cap-mortality`, `corticosteroids-covid19-mortality`, `doac-vte-recurrence`, `dpp4-mace-t2d`, `esketamine-trd-madrs`, `glp1-ra-mace-t2d`, `melatonin-primary-insomnia-sol`, `omega3-cardiovascular-events`, `pcsk9-mace`, `probiotics-aad-prevention`, `sacubitril-valsartan-hfref`, `semaglutide-obesity-mace`, `semaglutide-obesity-weight`, `sglt2-primary-prevention-hf`, `spironolactone-hfref-mortality`, `statins-primary-prevention-elderly`, `tocilizumab-covid19-mortality`.

## Rebuilt pages

All 32 canonical review pages and their blind `docs/m/*` mirrors were rebuilt. `scripts/reproduce_review.py` reported `32/32 reproduce (all reproducible)`.

| page | index.html bytes HEAD -> current | low-only before -> after | changed D5 trials |
|---|---:|---|---|
| `balanced-crystalloids-vs-saline-mortality` | 102407 -> 100804 (-1603) | k=2 RR 0.9774 [NA, NA] -> k=2 RR 0.9774 [NA, NA]; kind=bias_sensitivity | - |
| `colchicine-postop-af` | 102814 -> 103425 (+611) | k=4 RR 0.6735 [0.376, 1.2067] -> k=2 RR 0.5251 [0.0084, 32.8002]; kind=bias_sensitivity | 32720823, 25172965 |
| `colchicine-recurrent-pericarditis` | 97105 -> 97254 (+149) | k=2 RR 0.4813 [NA, NA] -> none; kind=bias_sensitivity | 24694983, 21873705 |
| `colchicine-secondary-cv-prevention` | 165915 -> 166571 (+656) | k=3 HR 0.8134 [0.5074, 1.3039] -> k=3 HR 0.8134 [0.5074, 1.3039]; kind=bias_sensitivity | - |
| `corticosteroids-cap-mortality` | 123096 -> 123326 (+230) | k=1 RR 0.5253 [NA, NA] -> none; kind=bias_sensitivity | 36942789 |
| `corticosteroids-covid19-mortality` | 91826 -> 92395 (+569) | none -> k=1 RR 0.83 [0.7454, 0.9242]; kind=bias_sensitivity | 32678530 |
| `dapagliflozin-hfpef-hosp` | 90813 -> 91222 (+409) | k=1 HR 0.82 [0.7304, 0.9205] -> k=1 HR 0.82 [0.7304, 0.9205]; kind=bias_sensitivity | - |
| `denosumab-vertebral-fracture` | 83534 -> 83946 (+412) | k=1 RR 0.32 [0.2548, 0.4018] -> k=1 RR 0.32 [0.2548, 0.4018]; kind=bias_sensitivity | - |
| `doac-vte-recurrence` | 155663 -> 156825 (+1162) | k=4 HR 0.917 [0.6926, 1.2141] -> k=6 HR 0.9092 [0.7478, 1.1054]; kind=bias_sensitivity | 22449293, 21128814 |
| `dpp4-mace-t2d` | 75123 -> 76261 (+1138) | k=3 HR 1.0074 [0.8391, 1.2094] -> k=2 HR 1.0082 [0.5699, 1.7836]; kind=bias_sensitivity | 28893244 |
| `empagliflozin-hfpef-hosp` | 93590 -> 93987 (+397) | k=1 HR 0.79 [0.6917, 0.9022] -> k=1 HR 0.79 [0.6917, 0.9022]; kind=bias_sensitivity | - |
| `esketamine-trd-madrs` | 112522 -> 113871 (+1349) | none -> k=4 MD -3.3445 [-6.0701, -0.6189]; kind=bias_sensitivity | 37025256, 31109201, NCT02422186, NCT02417064 |
| `finerenone-ckd-t2d-renal` | 80482 -> 81163 (+681) | k=2 HR 0.8407 [NA, NA] -> k=2 HR 0.8407 [NA, NA]; kind=bias_sensitivity | - |
| `glp1-ra-mace-t2d` | 94406 -> 96515 (+2109) | k=7 HR 0.8388 [0.7839, 0.8975] -> k=8 HR 0.856 [0.8086, 0.9061]; kind=bias_sensitivity | 28910237 |
| `iv-iron-hfref-hosp` | 94024 -> 94247 (+223) | n/a |  |
| `melatonin-primary-insomnia-sol` | 113458 -> 113744 (+286) | k=1 MD -17.4 [-28.5214, -6.2786] -> none; kind=bias_sensitivity | 20712869 |
| `metformin-pcos-ovulation` | 136055 -> 136493 (+438) | k=2 OR 4.3142 [0.0033, 5557.8501] -> k=2 OR 4.3142 [0.0033, 5557.8501]; kind=bias_sensitivity | - |
| `noac-vs-warfarin-af-stroke` | 87763 -> 88676 (+913) | k=4 HR 0.8069 [0.6611, 0.985] -> k=4 HR 0.8069 [0.6611, 0.985]; kind=bias_sensitivity | - |
| `omega3-cardiovascular-events` | 180940 -> 181781 (+841) | k=5 RR 0.9775 [0.9018, 1.0595] -> k=5 RR 0.9272 [0.781, 1.1008]; kind=bias_sensitivity | 30415628, 30146932, 22686415, 20929341 |
| `pcsk9-mace` | 70888 -> 71442 (+554) | k=2 HR 0.85 [NA, NA] -> k=1 HR 0.85 [NA, NA]; kind=bias_sensitivity | 30403574 |
| `probiotics-aad-prevention` | 423551 -> 424582 (+1031) | k=16 RR 0.702 [0.5352, 0.921] -> k=13 RR 0.7867 [0.58, 1.0671]; kind=bias_sensitivity | 40488914, 39529939, 35727573 |
| `sacubitril-valsartan-hfref` | 91283 -> 91604 (+321) | k=1 HR 0.8 [0.7328, 0.8733] -> none; kind=bias_sensitivity | 25176015 |
| `semaglutide-obesity-mace` | 80438 -> 81048 (+610) | none -> k=1 HR 0.8 [0.7155, 0.8944]; kind=bias_sensitivity | 37952131 |
| `semaglutide-obesity-weight` | 129071 -> 129379 (+308) | k=2 MD -11.8449 [NA, NA] -> none; kind=bias_sensitivity | 33625476, 33567185 |
| `sglt2-ckd-progression` | 93496 -> 94488 (+992) | k=3 HR 0.6836 [0.5537, 0.844] -> k=3 HR 0.6836 [0.5537, 0.844]; kind=bias_sensitivity | - |
| `sglt2-hfref-hosp-cvdeath` | 75001 -> 75770 (+769) | k=2 RR 0.7755 [NA, NA] -> k=2 RR 0.7755 [NA, NA]; kind=bias_sensitivity | - |
| `sglt2-primary-prevention-hf` | 186763 -> 187376 (+613) | k=3 HR 0.7023 [0.5281, 0.934] -> k=3 HR 0.6736 [0.485, 0.9357]; kind=bias_sensitivity | 28605608, 30415602 |
| `spironolactone-hfref-mortality` | 136350 -> 136866 (+516) | k=3 RR/HR 0.8685 [0.3062, 2.4635] -> k=2 RR/HR 0.7218 [0.3236, 1.6097]; kind=bias_sensitivity | 28824029 |
| `statins-primary-prevention-elderly` | 88391 -> 88925 (+534) | k=2 HR 0.6803 [NA, NA] -> k=1 HR 0.61 [NA, NA]; kind=bias_sensitivity | 42670961 |
| `ticagrelor-vs-clopidogrel-acs` | 75893 -> 76167 (+274) | n/a |  |
| `tocilizumab-covid19-mortality` | 124155 -> 124720 (+565) | none -> k=1 OR 0.83 [0.7285, 0.9456]; kind=bias_sensitivity | 33933206 |
| `tranexamic-acid-pph` | 95007 -> 95296 (+289) | n/a |  |

## Reworded blocks for integrator

- Risk-of-bias tab heading: `Registry-machine-signal-restricted partial machine assessment`.
- Span-check doc: `Partial machine assessment span-check... partial machine domain ratings...`.
- D5 basis strings now quote the registered outcome text, for example: `prespecified secondary outcome, registered '...'` and `the pooled outcome is a prespecified component of a registered secondary outcome; registered '...'`.
- Risk sensitivity blocks and manuscript now state low-only kind, for example: `Low-only kind: bias_sensitivity (1 adverse rating exclusion(s), 0 unassessed-domain exclusion(s)).`
- Gate and re-derivation sweep no longer load embeddings for D5 re-derivation.

## Static vs dynamic hardcode disclosure

| Item | Static or dynamic | Disclosure |
|---|---|---|
| Component signatures in `harness/rob2.py` | static method code | MACE, MADRS change, recurrent VTE, all-cause mortality, kidney/cardiorenal composite, HHF. These are rule signatures, not results. |
| `SECONDARY_COMPONENT_SUBSET_ALLOWED` | static method code | Restricted to HHF as a component of a registered secondary CV death/HHF composite. |
| Registered outcome rows | dynamic source-backed | Read from cached AACT/design-outcome records and linked NCT IDs; D5 basis quotes the registry text. |
| Low-only stratum kind | dynamic object-derived | Computed from excluded adverse ratings and excluded unassessed trials in `harness/rob_sensitivity.py`. |
| Sweep baseline | static lane baseline | `BASE_REF = ad5e7c66`, per prompt. |
| Registry-history changes after enrollment | not assessed unless cached | I did not find/use a cached registry-history source in this lane; absent/unknown registry outcome evidence fails closed as `not_assessable`. |

## Tests and replay

Commands run:

```text
python -m pytest tests\test_d5_rule.py -q -s
3 passed in 80.52s (0:01:20)

python scripts\rob_rederivation_sweep.py --write
0 ratings not reproducible from their own rule of 388 machine ratings over 32 topics

python scripts\reproduce_review.py
32/32 reproduce (all reproducible)

python -m pytest tests\test_embed_cases.py -q
3 passed in 6.48s

python -m pytest tests -x -q
724 passed in 1282.65s (0:21:22)
```

I also regenerated `docs/fix_ledger.json` and `docs/gate_scorecard.json` after the gate requested them.

## What I did not do

- No commit.
- No pooling/statistical estimator changes.
- No edits to `harness/synth.py`.
- No screening/search/GRADE aggregation change.
- No live network search. The old embedding-backed D5 gate path that loaded model weights was removed, and `cache/embeddings.json` was restored to `HEAD`.
- No portfolio index/workbook update; this lane did not change project submission status.

## Files changed or added

Added:

- `LANE-D5-REPORT.md`
- `tests/test_d5_rule.py`
- `scripts/d5_rule_sweep.py`
- `docs/d5_rule_sweep.json`

Also present from the RB patch/application path:

- `tests/test_rob_rederivation.py`
- `scripts/rob_rederivation_sweep.py`
- `docs/rob_rederivation_sweep.json`

Main modified source:

- `harness/rob2.py`
- `scripts/rob2_build.py`
- `harness/rob_sensitivity.py`
- `harness/gate.py`
- `scripts/rob_rederivation_sweep.py`
- `harness/page.py`
- `harness/limitations.py`
- `harness/pipeline.py`
- `docs/rob_spancheck.json`
- visible helper/test strings that still said `RoB2`

Generated artefacts:

- all 32 `cache/*/rob2.json`
- all 32 `docs/reviews/*/{index.html,review.json,manifest.json,REPRODUCTION.json}`
- all 32 affected `docs/m/*/index.html` blind mirrors
- `docs/index.html`
- `docs/fix_ledger.json`
- `docs/gate_scorecard.json`
- `registry/gate_scorecard.json`
