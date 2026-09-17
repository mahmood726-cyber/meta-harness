# LANE CG2 Report

## 1. What Was Wrong, Mechanism, Files

MEASURED: prefix ref `ad5e7c66` had proposition contradictions on 32 of 32 review pages. Current rebuilt pages have 0 proposition contradictions on 32 of 32 pages.

Mechanism: rendered/reporting prose was making truth claims that were not backed by the review object, or that contradicted it. The repeated classes were:

- publication bias described as assessed when `grade.domains.publication_bias.assessed` was false;
- protocol/config equality described as `declared == enforced` when the prose protocol and executable config diverged;
- protocol-SHA byte reproducibility claimed when the build only supports deterministic replay from the committed cache;
- count/membership prose collapsing different objects, especially primary effect objects vs trial randomisations;
- search-found prose saying a named record was not searched/found when screening records contained it;
- a stale esketamine parity row whose structured `our_k` was 4 but whose reason still said "We pool 2".

Implemented mechanism:

- `harness/propositions.py` adds object-backed proposition records and checks publication-bias state, declared/enforced state, byte-reproducibility state, count/membership assertions, search-found assertions, and state-label collapse.
- `harness/pipeline.py`, `harness/census.py`, `harness/gate.py`, and `scripts/reproduce_review.py` attach and gate those proposition objects.
- `harness/page.py`, `harness/manuscript.py`, and `harness/limitations.py` render cautious prose from those objects instead of hardcoded claims.
- `harness/protocol_compiler.py` now detects the relevant protocol/config divergences, including masking AND/OR, broad cardiovascular-outcome scope, and PCOS ovulation/subfertility context.
- `docs/parity.json` esketamine parity reason now matches the current object: `our_k = 4`, comparator k = 4, no stale "We pool 2" sentence.
- `topics/colchicine-postop-af.json` now says COPPS AF PMID 22090167 was screened in and declared absent for no poolable primary-outcome abstract data, instead of saying it was never searched.

Static-vs-dynamic hardcode disclosure:

| Item | Type | Disclosure |
|---|---|---|
| `_SEARCH_ALIAS_PMIDS` in `harness/propositions.py` | Static mapping | Narrow alias only, e.g. "original copps" to PMID 22090167, used to verify text against screening records. It does not create search results. |
| proposition counts | Dynamic | Derived from `review.json` outcomes, screening records, GRADE fields, protocol divergences, parity rows, and reproduction objects. |
| prefix plant corpus | Dynamic from git | `scripts/proposition_sweep.py` reads prefix artefacts through `git show ad5e7c66:...`. |
| effect sizes/pooling | Not changed | No HR/RR/MD, CI, tau2, search retrieval, screening decision, or harms extraction was handcoded or changed. |

## 2. Plant And Exact Assertions

Focused plant file: `tests/test_propositions.py`.

Exact planted assertions include:

- `test_PLANT_publication_bias_state_fires_on_prefix_objects`: `assert hit["asserted_assessed"] is True` and `assert hit["actual_assessed"] is False`.
- `test_PLANT_declared_equals_enforced_fires_on_named_prefix_objects`: expected divergence codes are subsets of `hit["divergence_codes"]`.
- `test_PLANT_byte_reproducible_fires_on_all_prefix_pages`: `assert len(slugs) == 32` and `assert len(hits) == 32`.
- `test_PLANT_membership_and_count_sentences_fire_on_prefix_objects`: SGLT2 primary prevention `primary_randomisations` asserted 4 vs actual 5; esketamine `parity_our_k` asserted 2 vs actual 4; colchicine postop COPPS PMID 22090167 asserted not found vs actually found.
- Additional measured prefix count: DOAC VTE recurrence `primary_randomisations` asserted 6 vs actual 7.
- `test_PLANT_refused_and_pooled_fires_prefix_and_current_dispute_passes`: old `aa8ed28a` metformin fires `REFUSED_AND_POOLED`; current metformin has no `REFUSED_AND_POOLED` and keeps one explicit `POOL_SCOPE_DISPUTE`.
- Controls: esketamine monotherapy trial PMID 40601310 remains excluded; omega-3 endpoint refusals still include DART and GISSI-HF; synthetic clean page has 0 proposition violations.

Pre-fix measured output from `python scripts\proposition_sweep.py`:

```text
wrote docs\proposition_sweep.json
pre_fix 32 of 32 pages
post_fix 0 of 32 pages
```

MEASURED from `docs/proposition_sweep.json`:

```json
{
  "denominator_pages": 32,
  "pre_pages_with_violations": 32,
  "post_pages_with_violations": 0,
  "pre_by_code_occurrences": {
    "BYTE_REPRODUCIBLE_FALSE": 96,
    "DECLARED_ENFORCED_FALSE": 21,
    "POOLED_COUNT_MISMATCH": 3,
    "PUBLICATION_BIAS_STATE": 96,
    "SEARCH_FOUND_CONTRADICTION": 1
  },
  "pre_pages_by_code_counts": {
    "BYTE_REPRODUCIBLE_FALSE": 32,
    "DECLARED_ENFORCED_FALSE": 21,
    "POOLED_COUNT_MISMATCH": 3,
    "PUBLICATION_BIAS_STATE": 32,
    "SEARCH_FOUND_CONTRADICTION": 1
  }
}
```

Post-fix focused plant test:

```text
........                                                                 [100%]
8 passed in 18.51s
```

Post-fix current-page scan:

```text
review_pages 32
missing_propositions 0 []
proposition_violations 0
```

Stale phrase scan:

```text
stale_phrase_hits 0
```

## 3. Rebuilt Pages And Before/After Content

MEASURED: all 32 canonical review pages changed, along with their `review.json`, `manifest.json`, and `REPRODUCTION.json` files. MEASURED: 64 blind mirror `docs/m/*/index.html` pages changed. Exact file paths are listed in section 6.

Canonical review pages whose rebuilt bytes changed:

- `balanced-crystalloids-vs-saline-mortality`
- `colchicine-postop-af`
- `colchicine-recurrent-pericarditis`
- `colchicine-secondary-cv-prevention`
- `corticosteroids-cap-mortality`
- `corticosteroids-covid19-mortality`
- `dapagliflozin-hfpef-hosp`
- `denosumab-vertebral-fracture`
- `doac-vte-recurrence`
- `dpp4-mace-t2d`
- `empagliflozin-hfpef-hosp`
- `esketamine-trd-madrs`
- `finerenone-ckd-t2d-renal`
- `glp1-ra-mace-t2d`
- `iv-iron-hfref-hosp`
- `melatonin-primary-insomnia-sol`
- `metformin-pcos-ovulation`
- `noac-vs-warfarin-af-stroke`
- `omega3-cardiovascular-events`
- `pcsk9-mace`
- `probiotics-aad-prevention`
- `sacubitril-valsartan-hfref`
- `semaglutide-obesity-mace`
- `semaglutide-obesity-weight`
- `sglt2-ckd-progression`
- `sglt2-hfref-hosp-cvdeath`
- `sglt2-primary-prevention-hf`
- `spironolactone-hfref-mortality`
- `statins-primary-prevention-elderly`
- `ticagrelor-vs-clopidogrel-acs`
- `tocilizumab-covid19-mortality`
- `tranexamic-acid-pph`

Corpus-wide sentence changes:

- Before: `This page is a REPLAY of that snapshot: re-running from the protocol SHA regenerates it byte-for-byte.`
- After: `This page replays the committed retrieval snapshot; it is not a claim that the protocol SHA alone regenerates the page byte-for-byte.`

- Before: `publication bias assessed from the trial registry` / `publication bias is assessed from the registry ghost census`
- After: `publication bias is NOT ASSESSED automatically` and registry ghost census text is descriptive until PICO-scoped.

- Before: manuscript/data availability claimed or implied protocol-SHA byte reproduction.
- After: `Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed.`

Declared/enforced pages:

MEASURED: 21 pages had prefix `DECLARED_ENFORCED_FALSE` contradictions. On affected pages, PRISMA item 5 changed from `Protocol tab - generated from the structured include object (P/I/C/design), so declared == enforced.` to `Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.`

Affected pages:

- `colchicine-recurrent-pericarditis`
- `colchicine-secondary-cv-prevention`
- `corticosteroids-cap-mortality`
- `dapagliflozin-hfpef-hosp`
- `denosumab-vertebral-fracture`
- `dpp4-mace-t2d`
- `empagliflozin-hfpef-hosp`
- `esketamine-trd-madrs`
- `finerenone-ckd-t2d-renal`
- `melatonin-primary-insomnia-sol`
- `metformin-pcos-ovulation`
- `omega3-cardiovascular-events`
- `pcsk9-mace`
- `probiotics-aad-prevention`
- `semaglutide-obesity-mace`
- `semaglutide-obesity-weight`
- `sglt2-ckd-progression`
- `sglt2-hfref-hosp-cvdeath`
- `sglt2-primary-prevention-hf`
- `spironolactone-hfref-mortality`
- `tranexamic-acid-pph`

Count and search-specific changes:

| Page | Before | After |
|---|---|---|
| `doac-vte-recurrence` | rendered/legacy proposition asserted `primary_randomisations=6`; object-derived value was 7 | proposition objects distinguish `primary_effect_objects=6` and `primary_randomisations=7` |
| `sglt2-primary-prevention-hf` | rendered/legacy proposition asserted `primary_randomisations=4`; object-derived value was 5 | proposition objects distinguish `primary_effect_objects=4` and `primary_randomisations=5` |
| `esketamine-trd-madrs` | parity reason said `We pool 2` while structured `our_k` was 4 | parity reason now says current review primary pool contains 4 effect objects; rendered parity is 4 vs 4 `IDENTICAL_SET` |
| `colchicine-postop-af` | caveat said the search never searched for the original COPPS trial | caveat says COPPS AF PMID 22090167 is screened in and declared absent because the abstract lacks poolable arm counts or effect+CI |

## 4. Tests

Final required full suite:

```text
python -m pytest tests -x -q
725 passed in 917.46s (0:15:17)
```

Other focused checks run after implementation:

```text
python -m pytest tests\test_propositions.py -q
8 passed in 18.51s
```

```text
python -m pytest tests\test_membership_consistency.py -q
3 passed in 3.22s
```

```text
python scripts\reproduce_review.py esketamine-trd-madrs
OK  esketamine-trd-madrs
1/1 reproduce (all reproducible)
```

Earlier full-corpus replay loop was run before the final esketamine parity row correction and all 32 reviews printed `OK` with `1/1 reproduce (all reproducible)`. After the parity correction, the affected page `esketamine-trd-madrs` was replayed again successfully.

## 5. What I Did Not Do And Why

- Did not commit, stage, stash, reset, checkout, or clean anything. User explicitly said do not commit, and the lane prompt forbids git mutation commands.
- Did not change pooling math, search retrieval, screening decisions, harms extraction, or `harness/synth.py`.
- Did not add fake studies, simulated data, placeholder effects, or hardcoded outcome results.
- Did not use network access for evidence. The lane was resolved from committed/local objects and prefix git artefacts.
- Did not update `F:\ProjectIndex\INDEX.md` or `F:\E156\rewrite-workbook.txt`; this task changed code/generated artefacts in this repo but did not change project submission state.

## 6. Files Changed Or Added

Pre-report `git status --short --untracked-files=all` had 219 paths. This report adds `?? LANE-CG2-REPORT.md`, shown first below. The untracked lane-control files `LANE_PROMPT.md`, `lane.log`, `lane.pid`, and `lane.winpid` were present and left uncommitted.

```text
?? LANE-CG2-REPORT.md
 M docs/evidence/identifier-scope-2026-09-14/README.md
 M docs/fix_ledger.json
 M docs/gate_scorecard.json
 M docs/index.html
 M docs/m/m031db369/index.html
 M docs/m/m0594e053/index.html
 M docs/m/m078be06c/index.html
 M docs/m/m09091404/index.html
 M docs/m/m0c0e2bf1/index.html
 M docs/m/m0effd17d/index.html
 M docs/m/m152f58d8/index.html
 M docs/m/m175bd0c3/index.html
 M docs/m/m22bf81d5/index.html
 M docs/m/m24cd09bc/index.html
 M docs/m/m250220c2/index.html
 M docs/m/m284e6ef4/index.html
 M docs/m/m28cd9b74/index.html
 M docs/m/m29f6dc16/index.html
 M docs/m/m2da64325/index.html
 M docs/m/m3c1155fb/index.html
 M docs/m/m42da3313/index.html
 M docs/m/m4670a8f9/index.html
 M docs/m/m4ee9db19/index.html
 M docs/m/m51474705/index.html
 M docs/m/m5384fd3c/index.html
 M docs/m/m586876fa/index.html
 M docs/m/m595c5e9f/index.html
 M docs/m/m5b3fd56c/index.html
 M docs/m/m5d324d5e/index.html
 M docs/m/m5e5590d5/index.html
 M docs/m/m612a48aa/index.html
 M docs/m/m660dc5c7/index.html
 M docs/m/m6840fc8a/index.html
 M docs/m/m6c992fd1/index.html
 M docs/m/m6dd4233b/index.html
 M docs/m/m6e7e8ab7/index.html
 M docs/m/m6f3cdffa/index.html
 M docs/m/m7d28b3cd/index.html
 M docs/m/m80e26e26/index.html
 M docs/m/m87167438/index.html
 M docs/m/m89f8021b/index.html
 M docs/m/m8db5253b/index.html
 M docs/m/m904d47d6/index.html
 M docs/m/m971790c1/index.html
 M docs/m/m979b0810/index.html
 M docs/m/m9e04a632/index.html
 M docs/m/ma014d0a4/index.html
 M docs/m/ma0b91971/index.html
 M docs/m/ma178f5d6/index.html
 M docs/m/ma451f131/index.html
 M docs/m/mabc6654a/index.html
 M docs/m/mae710922/index.html
 M docs/m/maf69923c/index.html
 M docs/m/mb53e1ed5/index.html
 M docs/m/mb6ceb13c/index.html
 M docs/m/mc16cd596/index.html
 M docs/m/md1780020/index.html
 M docs/m/md2772f36/index.html
 M docs/m/md68c6ad6/index.html
 M docs/m/md7fd1d6e/index.html
 M docs/m/mdd4bf0ae/index.html
 M docs/m/me0751432/index.html
 M docs/m/me17c0a34/index.html
 M docs/m/me5d639f4/index.html
 M docs/m/me79cb3b0/index.html
 M docs/m/mec03e6db/index.html
 M docs/m/mf6cd36c2/index.html
 M docs/m/mf6f36ebe/index.html
 M docs/parity.json
 M docs/reviews/balanced-crystalloids-vs-saline-mortality/REPRODUCTION.json
 M docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html
 M docs/reviews/balanced-crystalloids-vs-saline-mortality/manifest.json
 M docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json
 M docs/reviews/colchicine-postop-af/REPRODUCTION.json
 M docs/reviews/colchicine-postop-af/index.html
 M docs/reviews/colchicine-postop-af/manifest.json
 M docs/reviews/colchicine-postop-af/review.json
 M docs/reviews/colchicine-recurrent-pericarditis/REPRODUCTION.json
 M docs/reviews/colchicine-recurrent-pericarditis/index.html
 M docs/reviews/colchicine-recurrent-pericarditis/manifest.json
 M docs/reviews/colchicine-recurrent-pericarditis/review.json
 M docs/reviews/colchicine-secondary-cv-prevention/REPRODUCTION.json
 M docs/reviews/colchicine-secondary-cv-prevention/index.html
 M docs/reviews/colchicine-secondary-cv-prevention/manifest.json
 M docs/reviews/colchicine-secondary-cv-prevention/review.json
 M docs/reviews/corticosteroids-cap-mortality/REPRODUCTION.json
 M docs/reviews/corticosteroids-cap-mortality/index.html
 M docs/reviews/corticosteroids-cap-mortality/manifest.json
 M docs/reviews/corticosteroids-cap-mortality/review.json
 M docs/reviews/corticosteroids-covid19-mortality/REPRODUCTION.json
 M docs/reviews/corticosteroids-covid19-mortality/index.html
 M docs/reviews/corticosteroids-covid19-mortality/manifest.json
 M docs/reviews/corticosteroids-covid19-mortality/review.json
 M docs/reviews/dapagliflozin-hfpef-hosp/REPRODUCTION.json
 M docs/reviews/dapagliflozin-hfpef-hosp/index.html
 M docs/reviews/dapagliflozin-hfpef-hosp/manifest.json
 M docs/reviews/dapagliflozin-hfpef-hosp/review.json
 M docs/reviews/denosumab-vertebral-fracture/REPRODUCTION.json
 M docs/reviews/denosumab-vertebral-fracture/index.html
 M docs/reviews/denosumab-vertebral-fracture/manifest.json
 M docs/reviews/denosumab-vertebral-fracture/review.json
 M docs/reviews/doac-vte-recurrence/REPRODUCTION.json
 M docs/reviews/doac-vte-recurrence/index.html
 M docs/reviews/doac-vte-recurrence/manifest.json
 M docs/reviews/doac-vte-recurrence/review.json
 M docs/reviews/dpp4-mace-t2d/REPRODUCTION.json
 M docs/reviews/dpp4-mace-t2d/index.html
 M docs/reviews/dpp4-mace-t2d/manifest.json
 M docs/reviews/dpp4-mace-t2d/review.json
 M docs/reviews/empagliflozin-hfpef-hosp/REPRODUCTION.json
 M docs/reviews/empagliflozin-hfpef-hosp/index.html
 M docs/reviews/empagliflozin-hfpef-hosp/manifest.json
 M docs/reviews/empagliflozin-hfpef-hosp/review.json
 M docs/reviews/esketamine-trd-madrs/REPRODUCTION.json
 M docs/reviews/esketamine-trd-madrs/index.html
 M docs/reviews/esketamine-trd-madrs/manifest.json
 M docs/reviews/esketamine-trd-madrs/review.json
 M docs/reviews/finerenone-ckd-t2d-renal/REPRODUCTION.json
 M docs/reviews/finerenone-ckd-t2d-renal/index.html
 M docs/reviews/finerenone-ckd-t2d-renal/manifest.json
 M docs/reviews/finerenone-ckd-t2d-renal/review.json
 M docs/reviews/glp1-ra-mace-t2d/REPRODUCTION.json
 M docs/reviews/glp1-ra-mace-t2d/index.html
 M docs/reviews/glp1-ra-mace-t2d/manifest.json
 M docs/reviews/glp1-ra-mace-t2d/review.json
 M docs/reviews/iv-iron-hfref-hosp/REPRODUCTION.json
 M docs/reviews/iv-iron-hfref-hosp/index.html
 M docs/reviews/iv-iron-hfref-hosp/manifest.json
 M docs/reviews/iv-iron-hfref-hosp/review.json
 M docs/reviews/melatonin-primary-insomnia-sol/REPRODUCTION.json
 M docs/reviews/melatonin-primary-insomnia-sol/index.html
 M docs/reviews/melatonin-primary-insomnia-sol/manifest.json
 M docs/reviews/melatonin-primary-insomnia-sol/review.json
 M docs/reviews/metformin-pcos-ovulation/REPRODUCTION.json
 M docs/reviews/metformin-pcos-ovulation/index.html
 M docs/reviews/metformin-pcos-ovulation/manifest.json
 M docs/reviews/metformin-pcos-ovulation/review.json
 M docs/reviews/noac-vs-warfarin-af-stroke/REPRODUCTION.json
 M docs/reviews/noac-vs-warfarin-af-stroke/index.html
 M docs/reviews/noac-vs-warfarin-af-stroke/manifest.json
 M docs/reviews/noac-vs-warfarin-af-stroke/review.json
 M docs/reviews/omega3-cardiovascular-events/REPRODUCTION.json
 M docs/reviews/omega3-cardiovascular-events/index.html
 M docs/reviews/omega3-cardiovascular-events/manifest.json
 M docs/reviews/omega3-cardiovascular-events/review.json
 M docs/reviews/pcsk9-mace/REPRODUCTION.json
 M docs/reviews/pcsk9-mace/index.html
 M docs/reviews/pcsk9-mace/manifest.json
 M docs/reviews/pcsk9-mace/review.json
 M docs/reviews/probiotics-aad-prevention/REPRODUCTION.json
 M docs/reviews/probiotics-aad-prevention/index.html
 M docs/reviews/probiotics-aad-prevention/manifest.json
 M docs/reviews/probiotics-aad-prevention/review.json
 M docs/reviews/sacubitril-valsartan-hfref/REPRODUCTION.json
 M docs/reviews/sacubitril-valsartan-hfref/index.html
 M docs/reviews/sacubitril-valsartan-hfref/manifest.json
 M docs/reviews/sacubitril-valsartan-hfref/review.json
 M docs/reviews/semaglutide-obesity-mace/REPRODUCTION.json
 M docs/reviews/semaglutide-obesity-mace/index.html
 M docs/reviews/semaglutide-obesity-mace/manifest.json
 M docs/reviews/semaglutide-obesity-mace/review.json
 M docs/reviews/semaglutide-obesity-weight/REPRODUCTION.json
 M docs/reviews/semaglutide-obesity-weight/index.html
 M docs/reviews/semaglutide-obesity-weight/manifest.json
 M docs/reviews/semaglutide-obesity-weight/review.json
 M docs/reviews/sglt2-ckd-progression/REPRODUCTION.json
 M docs/reviews/sglt2-ckd-progression/index.html
 M docs/reviews/sglt2-ckd-progression/manifest.json
 M docs/reviews/sglt2-ckd-progression/review.json
 M docs/reviews/sglt2-hfref-hosp-cvdeath/REPRODUCTION.json
 M docs/reviews/sglt2-hfref-hosp-cvdeath/index.html
 M docs/reviews/sglt2-hfref-hosp-cvdeath/manifest.json
 M docs/reviews/sglt2-hfref-hosp-cvdeath/review.json
 M docs/reviews/sglt2-primary-prevention-hf/REPRODUCTION.json
 M docs/reviews/sglt2-primary-prevention-hf/index.html
 M docs/reviews/sglt2-primary-prevention-hf/manifest.json
 M docs/reviews/sglt2-primary-prevention-hf/review.json
 M docs/reviews/spironolactone-hfref-mortality/REPRODUCTION.json
 M docs/reviews/spironolactone-hfref-mortality/index.html
 M docs/reviews/spironolactone-hfref-mortality/manifest.json
 M docs/reviews/spironolactone-hfref-mortality/review.json
 M docs/reviews/statins-primary-prevention-elderly/REPRODUCTION.json
 M docs/reviews/statins-primary-prevention-elderly/index.html
 M docs/reviews/statins-primary-prevention-elderly/manifest.json
 M docs/reviews/statins-primary-prevention-elderly/review.json
 M docs/reviews/ticagrelor-vs-clopidogrel-acs/REPRODUCTION.json
 M docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html
 M docs/reviews/ticagrelor-vs-clopidogrel-acs/manifest.json
 M docs/reviews/ticagrelor-vs-clopidogrel-acs/review.json
 M docs/reviews/tocilizumab-covid19-mortality/REPRODUCTION.json
 M docs/reviews/tocilizumab-covid19-mortality/index.html
 M docs/reviews/tocilizumab-covid19-mortality/manifest.json
 M docs/reviews/tocilizumab-covid19-mortality/review.json
 M docs/reviews/tranexamic-acid-pph/REPRODUCTION.json
 M docs/reviews/tranexamic-acid-pph/index.html
 M docs/reviews/tranexamic-acid-pph/manifest.json
 M docs/reviews/tranexamic-acid-pph/review.json
 M harness/census.py
 M harness/gate.py
 M harness/limitations.py
 M harness/manuscript.py
 M harness/page.py
 M harness/pipeline.py
 M harness/protocol_compiler.py
 M registry/blind_map.json
 M registry/gate_scorecard.json
 M scripts/reproduce_review.py
 M tests/test_membership_consistency.py
 M tests/test_protocol_compiler.py
 M tests/test_retrieval_render.py
 M topics/colchicine-postop-af.json
?? LANE_PROMPT.md
?? docs/proposition_sweep.json
?? harness/propositions.py
?? lane.log
?? lane.pid
?? lane.winpid
?? scripts/proposition_sweep.py
?? tests/test_propositions.py
```
