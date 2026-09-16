# LANE RB Report

## What Was Wrong

MEASURED: The EXSCEL D5 plant was a real machine re-derivation failure. In old commit `aa8ed28a`, GLP-1 trial `28910237` had D5 `some concerns` with basis `the pooled outcome matches no registered primary or secondary outcome (registered primary: 'Primary Efficacy Outcome MACE Events') -- possibly post-hoc/unregistered`. That was wrong because the registered primary outcome description says `cardiovascular death, nonfatal MI, or nonfatal stroke`, which is the pooled 3-point MACE component set.

MEASURED: The mechanism was a title/label-only D5 comparison. `scripts/rob2_build.py` was not carrying AACT outcome descriptions into the RoB object, and `harness/rob2.py` did not compare pooled and registered composite outcome components. The fix carries `measure`, `title`, and `description`, derives component sets, treats unknown registry text as `not_assessable`, and names the output family `registry-machine-signal-restricted`.

MEASURED: The machine RoB objects now carry `rule_id`, `inputs`, `derived_at_build`, and `rob_basis`; `harness/gate.py::check_rob_rederivable` refuses pages whose stored registry-machine RoB level is missing metadata or no longer re-runs from its own rule inputs. `docs/rob_rederivation_sweep.json` records the corpus sweep.

MEASURED: A second GLP-1 sensitivity bug was exposed after fixing D5. The primary outcome trial label for SOUL was `SOUL`, but RoB ratings were keyed by PMID `40162642`; `harness/rob_sensitivity.py` and `harness/grade.py` now join on label first, then PMID/id.

MEASURED: The arm contrast disclosure was overstated. It previously rendered as `registry-confirmed` even though the machine only has an AACT arm-label parser. `harness/armcontrast.py`, `scripts/arm_contrast_build.py`, `harness/page.py`, `harness/limitations.py`, and `harness/compat.py` now label this as `parser-confirmed contrast` and state that it measures the parser, not the trial.

## Plant And Re-Derivation

MEASURED: `tests/test_rob_rederivation.py::test_exscel_d5_prefixed_object_fails_rederivation_with_quoted_fields` is the plant. It loads `aa8ed28a:docs/reviews/glp1-ra-mace-t2d/review.json` and asserts:

```python
assert stored["level"] == "some concerns"
assert rederived["level"] == "low"
assert comparison["method"] == "component_set"
assert comparison["pooled_components"] == ["CV_DEATH", "NONFATAL_MI", "NONFATAL_STROKE"]
assert comparison["registered_components"] == ["CV_DEATH", "NONFATAL_MI", "NONFATAL_STROKE"]
assert "cardiovascular death, nonfatal MI, or nonfatal stroke" in comparison["registered_text"]
```

MEASURED: The same test file includes true-negative and uncertainty checks: a real registered-primary mismatch remains `some concerns`, and unknown registry outcome text becomes `not_assessable`, not `low`.

MEASURED: The arm parser plant shows pre-fix class terms fail for EXSCEL (`unverified_granularity`), while post-fix topic agent aliases verify `exenatide once weekly`.

MEASURED: Targeted plant run: `python -m pytest tests\test_rob_rederivation.py -q` -> `5 passed in 2.66s`.

MEASURED: Final corpus sweep: `python scripts\rob_rederivation_sweep.py --write` -> `0 ratings not reproducible from their own rule of 388 machine ratings over 32 topics`; domain totals were `D1_randomisation: 0 of 97`, `D2_deviations: 0 of 97`, `D4_outcome_measurement: 0 of 97`, and `D5_selective_reporting: 0 of 97`.

## Rebuilt Pages And Changed Outputs

MEASURED: Rebuilt all 32 review pages: `balanced-crystalloids-vs-saline-mortality`, `colchicine-postop-af`, `colchicine-recurrent-pericarditis`, `colchicine-secondary-cv-prevention`, `corticosteroids-cap-mortality`, `corticosteroids-covid19-mortality`, `dapagliflozin-hfpef-hosp`, `denosumab-vertebral-fracture`, `doac-vte-recurrence`, `dpp4-mace-t2d`, `empagliflozin-hfpef-hosp`, `esketamine-trd-madrs`, `finerenone-ckd-t2d-renal`, `glp1-ra-mace-t2d`, `iv-iron-hfref-hosp`, `melatonin-primary-insomnia-sol`, `metformin-pcos-ovulation`, `noac-vs-warfarin-af-stroke`, `omega3-cardiovascular-events`, `pcsk9-mace`, `probiotics-aad-prevention`, `sacubitril-valsartan-hfref`, `semaglutide-obesity-mace`, `semaglutide-obesity-weight`, `sglt2-ckd-progression`, `sglt2-hfref-hosp-cvdeath`, `sglt2-primary-prevention-hf`, `spironolactone-hfref-mortality`, `statins-primary-prevention-elderly`, `ticagrelor-vs-clopidogrel-acs`, `tocilizumab-covid19-mortality`, `tranexamic-acid-pph`.

MEASURED: For each of those 32 slugs, rebuilt bytes changed in `docs/reviews/<slug>/review.json`, `index.html`, `manifest.json`, and `REPRODUCTION.json`. MEASURED: 32 blind pages under `docs/m/*/index.html` changed. MEASURED: `docs/index.html`, `docs/gate_scorecard.json`, `docs/fix_ledger.json`, and 3 evidence README fix-state lines changed because tests require generated registries/views to be current.

MEASURED: GLP-1 before/after:

| Field | Before (`aa8ed28a`) | After final rebuild |
| --- | --- | --- |
| EXSCEL D5 | MEASURED: `some concerns`; basis said no registered primary/secondary match | MEASURED: `low`; basis says registered primary matches pooled outcome by component set `(CV_DEATH, NONFATAL_MI, NONFATAL_STROKE)` |
| RoB coverage | MEASURED: `7 of 8`, `rob_covered=false`; SOUL level was `null` | MEASURED: `8 of 8`, `rob_covered=true`; SOUL level is `low` |
| Full pool | MEASURED: `k=8, HR 0.856 [0.8086, 0.9061]` | MEASURED: `k=8, HR 0.856 [0.8086, 0.9061]` |
| Low-only pool | MEASURED: `k=6, HR 0.8321 [0.7668, 0.9029]` | MEASURED: `k=8, HR 0.856 [0.8086, 0.9061]` |
| Arm contrast | MEASURED: `0 of 8`; EXSCEL `unverified_granularity` | MEASURED: `8 of 8`; EXSCEL `parser-confirmed contrast: keyword 'exenatide' matched AACT arm intervention 'exenatide once weekly'` |

MEASURED: Corpus arm-parser count moved from `64 of 104` over `32` topics in old commit `aa8ed28a` to `72 of 101` over `32` topics after the final rebuild. The denominator changed because the regenerated parser cache now scopes to the current per-topic pooled-trial objects.

MEASURED: Current served-surface label scan over `docs/index.html`, `docs/reviews`, `docs/m`, and `harness` found no hits for `registry-confirmed`, `source identifiers resolve`, `arm identity`, `design verified`, `Randomised contrast`, `RoB 2`, or `Risk of Bias 2`. MEASURED: A broader archival `docs/` scan still finds old wording inside archived evidence/fair-judge records; those are not current review pages.

## Tests And Reproduction

MEASURED: `python scripts\reproduce_review.py` -> `32/32 reproduce (all reproducible)`.

MEASURED: `python -m pytest tests -x -q` -> `644 passed in 179.48s (0:02:59)`.

MEASURED: `git diff --check` produced no output.

MEASURED: The gate-scorecard registry was updated for the new gate, and `python -m pytest tests\test_gate_scorecard.py::test_real_registry_passes -q` passed before the final full-suite run.

## What I Did Not Do

CLAIMED: I did not change topic trial inclusion/exclusion rules, primary pool membership, effect extraction, `harness/synth*`, or estimator code.

CLAIMED: I did not run search/network refresh scripts. The rebuild/reproduction path used committed caches.

CLAIMED: I did not stage, commit, stash, reset, or push anything.

CLAIMED: I did not edit `F:\E156\rewrite-workbook.txt`; I only read it for the session-start rule.

## Files Changed Or Added

MEASURED: Tracked diff before this report was `244 files changed, 28731 insertions(+), 2197 deletions(-)`. Untracked new lane deliverables are listed below. Pre-existing untracked lane-control files observed but not treated as work output: `LANE_PROMPT.md`, `lane.log`, `lane.pid`, `lane.winpid`.

MEASURED source/code changes:

- `harness/rob2.py`
- `harness/gate.py`
- `harness/armcontrast.py`
- `harness/rob_sensitivity.py`
- `harness/grade.py`
- `harness/page.py`
- `harness/limitations.py`
- `harness/compat.py`
- `harness/pipeline.py`
- `scripts/rob2_build.py`
- `scripts/arm_contrast_build.py`
- `scripts/rob_rederivation_sweep.py` (added)
- `tests/test_rob_rederivation.py` (added)
- `tests/test_compat_key.py`
- `registry/gate_scorecard.json`

MEASURED generated data/docs:

- `docs/rob_rederivation_sweep.json` (added)
- `docs/gate_scorecard.json`
- `docs/fix_ledger.json`
- `docs/index.html`
- `docs/evidence/design-key-2026-09-14/README.md`
- `docs/evidence/hazard-consumers-2026-09-14/README.md`
- `docs/evidence/search-v2-measurement-2026-09-15/README.md`
- `cache/embeddings.json`
- `cache/<32 review slugs>/rob2.json`
- `cache/<32 review slugs>/arm_contrast.json`
- `docs/reviews/<32 review slugs>/review.json`
- `docs/reviews/<32 review slugs>/index.html`
- `docs/reviews/<32 review slugs>/manifest.json`
- `docs/reviews/<32 review slugs>/REPRODUCTION.json`
- `docs/m/<32 blind ids>/index.html`
- `LANE-RB-REPORT.md` (added)

## Static Vs Dynamic Hardcode Disclosure

| Value | Classification | Basis |
| --- | --- | --- |
| GLP-1 before values from `aa8ed28a` | MEASURED static historical artefact | Read with `git show aa8ed28a:docs/reviews/glp1-ra-mace-t2d/review.json` |
| GLP-1 after values | MEASURED generated artefact | Read from final `docs/reviews/glp1-ra-mace-t2d/review.json` |
| RoB sweep counts | MEASURED generated artefact | Produced by `scripts/rob_rederivation_sweep.py --write` |
| Arm-parser corpus counts | MEASURED generated artefact | Computed from `docs/reviews/*/review.json` before and after |
| Test/reproduction summaries | MEASURED command output | Quoted from the commands in section 4 |
| Report prose about intent/no-commit/no-search | CLAIMED operator action | Based on commands run in this lane |
