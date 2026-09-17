# Design key tranche (2026-09-14)

**Fix state (orthogonal fields rule): LANDED / NONE / INSTANCE / STALE** - generated from TRANCHE-design-key; stale dependencies: GATE_GAPS.md, README.md, docs/evidence/CAPTIONS.json, +15 more

Base commit: `4a2283e9f6bca55101bc918bd5319a963ca7e4ec`.

This tranche supersedes the first AC design-key build by making the design key a typed analytic decision. Every detected design hazard maps to exactly one of `ALLOW`, `ALLOW_WITH_LABEL`, `ADJUST`, `MANUAL_REVIEW`, or `REFUSE`; evidence-backed `correlation_handling` replaces the trusted boolean; and BaSICS uses the source-reported adjusted marginal HR with no significant interaction rather than silently retaining a raw reconstructed RR.

## Evidence files

| file | caption |
|---|---|
| `01-sweep-32.txt` | 32-topic design sweep with detector limits in the first lines, per-pooled-trial rows, and named summary lists. |
| `02-prefix-parallel-path-accepts-cluster.txt` | Prefix plant showing the base reconstruction path emitted an unadjusted SE for a constructed cluster-crossover trial; post-fix refusal and paired-crossover pessimistic-direction calculation. |
| `02a-step1-marked-before-repool.txt` | Step 1 marking-only evidence: `pooled_variance_unsupported` fires while SMART/SALT/SPLIT remain pooled in the plant. |
| `02a-step1-git-diff.txt` | Diff slice for design detection/key plus invalidation marking. |
| `02b-step2-repooled.txt` | Step 2 refusal and balanced-crystalloids before/after pooled numbers. |
| `02b-step2-git-diff.txt` | Diff slice for refusal/re-pool/rendering. |
| `03-regeneration-accounting.txt` | Accounting for the 32 regenerated review directories and generated blind/index surfaces. |
| `04-ratchet-block-replacements.txt` | Block-ratchet replacement ledger for the generated 120-to-115 index banner and balanced-crystalloids blocks replaced by the design-refusal re-pool. |
| `05-typed-actions.txt` | Typed action mapping table and the BaSICS raw-reconstruction plant. |
| `06-correlation-handling-provenance.txt` | Evidence-backed correlation-handling object shape and the trusted-boolean plant. |
| `07-prevalence-unknown.txt` | PREVALENCE UNKNOWN statement with full 32-topic accounting. |
| `08-validity-threatening-classification.txt` | Limitation-classification table and linked-decision publication-gate plant. |

## Sweep summary

- 120 pooled-trial rows across 32 live review directories.
- PREVALENCE UNKNOWN: 3 topics were observed non-parallel by the current reach-limited detectors (`balanced-crystalloids-vs-saline-mortality`, `colchicine-secondary-cv-prevention`, `omega3-cardiovascular-events`), 96 trial-topic pairs still carry no design evidence, and 0 topics remain outside the current registry-field sweep. This is not a corpus prevalence estimate.
- 3 trials were refused: `balanced-crystalloids-vs-saline-mortality:SALT`, `balanced-crystalloids-vs-saline-mortality:SMART`, and `balanced-crystalloids-vs-saline-mortality:SPLIT`.
- 96 unique trial/topic pairs remain `UNKNOWN`: not observed by AACT intervention_model or committed title/abstract text, and not safe to reinterpret as `PARALLEL`.
- BaSICS factorial detection source: committed title/abstract design phrase plus trial reported estimate label. The raw reconstructed RR path plants `MANUAL_REVIEW`; the production build uses the published adjusted HR with evidence-backed `published_model` correlation handling and labels the factorial marginal contrast as `ALLOW_WITH_LABEL`.

## All 32 review directories swept

`balanced-crystalloids-vs-saline-mortality`, `colchicine-postop-af`, `colchicine-recurrent-pericarditis`, `colchicine-secondary-cv-prevention`, `corticosteroids-cap-mortality`, `corticosteroids-covid19-mortality`, `dapagliflozin-hfpef-hosp`, `denosumab-vertebral-fracture`, `doac-vte-recurrence`, `dpp4-mace-t2d`, `empagliflozin-hfpef-hosp`, `esketamine-trd-madrs`, `finerenone-ckd-t2d-renal`, `glp1-ra-mace-t2d`, `iv-iron-hfref-hosp`, `melatonin-primary-insomnia-sol`, `metformin-pcos-ovulation`, `noac-vs-warfarin-af-stroke`, `omega3-cardiovascular-events`, `pcsk9-mace`, `probiotics-aad-prevention`, `sacubitril-valsartan-hfref`, `semaglutide-obesity-mace`, `semaglutide-obesity-weight`, `sglt2-ckd-progression`, `sglt2-hfref-hosp-cvdeath`, `sglt2-primary-prevention-hf`, `spironolactone-hfref-mortality`, `statins-primary-prevention-elderly`, `ticagrelor-vs-clopidogrel-acs`, `tocilizumab-covid19-mortality`, `tranexamic-acid-pph`.

## Fix state

`registry/fixes.json` carries `TRANCHE-design-key` with evidence directory `docs/evidence/design-key-2026-09-14`; rendered ledgers are regenerated from that object.

Integration note (session author, 2026-09-15): on the merged base 9218f8b5 the typed action for a trial whose design is UNKNOWN (no registry intervention model and no design phrase) was changed from ALLOW to ALLOW_WITH_LABEL (`design-key:design-not-observed`): not observed is not parallel, and the pool says so. `01-sweep-32.txt` was regenerated on the merged base; captures 05-08 are the lane's originals (they name the earlier gate id `design-key:parallel-or-unclassified` for that case).
