# LANE SC2 Report

Base checked at start: MEASURED `ad5e7c66`. No commit was made.

`BRIEF-SC.md` was absent, so field names and finish conditions came from `LANE_PROMPT.md`.

## What Was Wrong

- MEASURED mechanism: `population_none` ran as a hard veto before entry-condition context, so diabetes terms excluded HFrEF registry rows even when heart-failure entry-condition text was present.
- MEASURED affected plant: `NCT04385589` in `sglt2-hfref-hosp-cvdeath` was `exclude/X2` for diabetic wording before this lane.
- MEASURED contrast defect: `MIRO-CKD` / `NCT06350123` in `sglt2-ckd-progression` was `include/INCLUDE` even though all cached registry arms received dapagliflozin and the randomised contrast isolates balcinrenone.
- MEASURED metadata defect: sparse NCT rows did not carry lifecycle keys through screening/outcome rows, so CS could not see `phase`, `status`, or `primary_completion` even when the cache lacks values.
- CLAIMED from lane prompt and encoded as no-fetch misses: DEFINE-HF, Empire HF, EMPERIAL-Reduced, CONFIDENCE 2025, PMID 8888663, and PMID 20299607.

Files implementing the mechanism:

- `harness/screen_entry.py`: entry-condition-only population veto helper, comparator overrides, contrast eviction helper, completeness/lifecycle annotation.
- `harness/screen.py`: applies entry-condition population exception, explicit comparator override, `X-CONTRAST`, and additive decision metadata.
- `harness/pipeline.py`: propagates screen-entry metadata into review screening rows and declared-absent outcome rows.
- `topics/sglt2-hfref-hosp-cvdeath.json`: diabetes entry-condition exception, `NCT04385589` comparator override, completeness states, named misses.
- `topics/sglt2-ckd-progression.json`: MIRO-CKD contrast eviction.
- `topics/finerenone-ckd-t2d-renal.json` and `topics/spironolactone-hfref-mortality.json`: named eligible misses only.

## Plant Details

- MEASURED `NCT04385589`: before `exclude/X2`; after `include/INCLUDE`, comparator override term `insulin`, `phase=None`, `status=None`, `primary_completion=None`, `completeness_state="target outcome absent by design (short mechanistic/functional trial)"`.
- MEASURED `NCT06229678`: before `include/INCLUDE`; after still `include/INCLUDE`, with keys `phase=None`, `status=None`, `primary_completion=None`, `completeness_state="eligible ongoing mechanistic trial; target outcome absent by design"`.
- MEASURED `NCT04304560`: additional same-mechanism HFrEF flip found by sweep, before `exclude/X2`; after `include/INCLUDE`. Cached row is double-blind dapagliflozin vs placebo with HFrEF and type 2 diabetes condition text.
- MEASURED `NCT06350123` / MIRO-CKD: before `include/INCLUDE`; after `exclude/X-CONTRAST`, `contrast_rule="CONTRAST_ABSENT"`.
- MEASURED synthetic CONFIDENCE test: screens `include/INCLUDE` with positive finerenone contrast, then primary kidney outcome extraction returns `absent=True` because the synthetic abstract reports UACR only, not the configured kidney composite.

## Sweep Artefact

Wrote `docs/entry_condition_sweep.json` from `scripts/entry_condition_sweep.py`.

- MEASURED topics: `38`.
- MEASURED screened records in legacy-vs-current comparison: `3911`.
- MEASURED decision flips: `3` - `NCT06350123`, `NCT04304560`, `NCT04385589`.
- MEASURED keyword-population screen denominator: `38 of 38` topic configs have `population_none`.
- MEASURED named eligible misses entered: `6`.
- MEASURED named miss states: `5` as `REACH_MISS(named)` and `1` as `REACH_MISS(named: CONFIDENCE 2025, finerenone+empagliflozin factorial)`.

## Page Deltas

Rebuilt and replayed:

- `sglt2-hfref-hosp-cvdeath`
- `sglt2-ckd-progression`

MEASURED `sglt2-hfref-hosp-cvdeath`:

- Before screening counts: screened `18`, included `3`, X2 exclusions `5`, declared-absent primary rows `1`.
- After screening counts: screened `18`, included `5`, X2 exclusions `3`, declared-absent primary rows `3`.
- Before rendered sentence: `3 trial families met P/I/C/design (screening); 2 reported this outcome with an extractable number and were pooled; the remaining 1 trial family are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).`
- After rendered sentence: `5 trial families met P/I/C/design (screening); 2 reported this outcome with an extractable number and were pooled; the remaining 3 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).`

MEASURED `sglt2-ckd-progression`:

- Before screening counts: screened `35`, included `8`, X-CONTRAST exclusions `0`, declared-absent primary rows `5`.
- After screening counts: screened `35`, included `7`, X-CONTRAST exclusions `1`, declared-absent primary rows `4`.
- Before rendered sentence: `8 trial families met P/I/C/design (screening); 3 reported this outcome with an extractable number and were pooled; the remaining 5 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).`
- After rendered sentence: `7 trial families met P/I/C/design (screening); 3 reported this outcome with an extractable number and were pooled; the remaining 4 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).`

## Static vs Dynamic Hardcode Disclosure

| Item | Static or dynamic | Disclosure |
| --- | --- | --- |
| Diabetes entry-condition exception terms | Static config | Static terms in `topics/sglt2-hfref-hosp-cvdeath.json`; dynamic match against cached title/conditions decides whether X2 fires. |
| `NCT04385589` comparator override | Static named override | Static adjudication from lane prompt plus cached interventions; used only for the named sparse registry row. |
| NCT lifecycle fields | Dynamic cache read | Keys are propagated for NCT rows; values are `None` when absent from cache. No lifecycle value was invented. |
| Completeness states | Static labels | Static labels for `NCT04385589` and `NCT06229678`; copied only to matched rows. |
| MIRO-CKD contrast eviction | Static named eviction | Static audit-confirmed row in topic config; dynamic screening emits `X-CONTRAST`. |
| Named eligible misses | Static lane list | Stored as reach misses only. No network fetch or synthetic source record was created. |
| Sweep counts | Dynamic from cache | Counts come from committed `cache/<slug>/records.json` plus current topic configs. |

## Tests and Replay

- MEASURED `python -m py_compile harness\screen_entry.py scripts\entry_condition_sweep.py tests\test_screen_entry.py`: exit `0`, no output.
- MEASURED `python -m pytest tests\test_screen_entry.py -q`: `7 passed in 14.93s`
- MEASURED `python scripts\reproduce_review.py sglt2-hfref-hosp-cvdeath`: `1/1 reproduce (all reproducible)`
- MEASURED `python scripts\reproduce_review.py sglt2-ckd-progression`: `1/1 reproduce (all reproducible)`
- MEASURED `git diff --check`: exit `0`, no output.
- MEASURED `python -m pytest tests -x -q`: interrupted after it stalled past the displayed `19%` progress marker; no pytest summary line was produced.
- MEASURED follow-up `python -m pytest tests\test_architecture_identity.py::test_topic_config_byte_change_changes_identity -vv --timeout=60 --tb=short`: timed out after `60.0s` inside `harness/gitblob.py::_is_git_toplevel`, waiting on `subprocess.run(...)` for git toplevel detection. This is outside the SC2 screen-entry path.

## Did Not Do

- Did not commit, stage, stash, checkout, reset, or clean.
- Did not fetch network sources.
- Did not invent values for missing registry lifecycle fields.
- Did not edit `F:\ProjectIndex\INDEX.md` or `F:\E156\rewrite-workbook.txt`; this lane did not change portfolio status or submission state.
- Did not touch user rewrite sections.

## Changed or Added Files

Added:

- `harness/screen_entry.py`
- `scripts/entry_condition_sweep.py`
- `tests/test_screen_entry.py`
- `docs/entry_condition_sweep.json`
- `LANE-SC2-REPORT.md`

Modified:

- `harness/screen.py`
- `harness/pipeline.py`
- `topics/sglt2-hfref-hosp-cvdeath.json`
- `topics/sglt2-ckd-progression.json`
- `topics/finerenone-ckd-t2d-renal.json`
- `topics/spironolactone-hfref-mortality.json`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/review.json`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/index.html`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/manifest.json`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/REPRODUCTION.json`
- `docs/reviews/sglt2-ckd-progression/review.json`
- `docs/reviews/sglt2-ckd-progression/index.html`
- `docs/reviews/sglt2-ckd-progression/manifest.json`
- `docs/reviews/sglt2-ckd-progression/REPRODUCTION.json`
- `docs/m/m6dd4233b/index.html`
- `docs/m/me17c0a34/index.html`
- `registry/blind_map.json`

Pre-existing/unowned untracked lane files left untouched: `LANE_PROMPT.md`, `lane.log`, `lane.pid`, `lane.winpid`.
