# LANE HRM2 report

No commit, push or network fetch performed. Base: `3cf73885ffc83f6fcc4db273c6510a5416cdcde0`.
Local origin/main remains 2304824034b4ba8677da2d2d2453352711ed2a9b; no fetch was performed. The explicit requested base is used for lane comparisons, while verify_all retains its configured ratchet refs.
The requested implementation and measurements are complete; the expected honest-state ratchet refusal is retained, not bypassed.

## MEASURED

- Rebuilt **32 of 32 pages** from held caches.
- Full `gate.gate_page`: **32 of 32 PASS**, including the unchanged `check_harms_complete`.
- Empty `AACT_DIR` reproduction: **32/32**.
- Retraction survival against the exact requested base: **32 of 32**.
- **46 harm outcomes suppressed of 61**, across **27 of 32 pages**. This denominator includes incomplete blocks that already had no renderable estimate.
- **95 adjustment rows UNRESOLVED of 95** published per-outcome trial rows; reconstructed rows are outside this denominator.
- The second-pass audit compares all original trial inputs, identifiers, dates, source spans, refusal codes, trial states, existing reporting-ledger states, debt flags and calculated k/estimate/CI/tau²/scale against the base. All preserved. Design-derived labels and correlation metadata are excluded from the unchanged-input assertion because the explicitly requested verbatim adjustment work changes them; numerical results remain unchanged.
- Membership code and `harness/synth.py` are untouched. `check_harms_complete` is AST-identical to the base.

## Rule and scope

Typed refusals retain their original codes and states and resolve the extraction obligation. They are **not** added to `known_reported_not_yet_extracted`, and do not set `harms_incomplete` merely because a numerical value could not be extracted.

Separately, any source-reporting trial without an extracted, located value prevents the outcome's quantitative synthesis. The page serves **HARMS EXTRACTION INCOMPLETE — no class-level quantitative safety conclusion issued**, retains the ledger with codes, reasons and spans, and suppresses its canonical quantitative claim. Explicit non-reporting rows do not enter the reporting ledger solely because they have a refusal code. Rows already flagged harm_source_reported=true are also shown even if main omitted them from its result ledger because their unchanged state was RETRIEVED_OUTCOME_NOT_REPORTED; the audit records these additions without relabelling their states.

Copied HRM's `harness/design_key.py`, `harness/adjustment.py`, `scripts/adjustment_label_sweep.py`, `tests/test_design_key.py` and `tests/test_hrm_gating.py` verbatim. Retained the HRM synthesis gate, adjustment gate, rendering and browser contract, with the separate HRM2 synthesis predicate and preserved debt semantics. The prior HM tests were not rewritten.

## Plants FIRST on the unchanged base

The numerical-surface plant failed on the base:

```text
F                                                                        [100%]
================================== FAILURES ===================================
______________ test_refusal_suppresses_pool_and_preserves_ledger ______________

    def test_refusal_suppresses_pool_and_preserves_ledger():
        out = annotate(refused_harm())
        html = page._outcome_block(out, show_inputs=False)
>       assert "HARMS EXTRACTION INCOMPLETE" in html
E       assert 'HARMS EXTRACTION INCOMPLETE' in "<h4>Synthetic bleeding</h4><table class='kv'><tr><th>k</th><td>1</td></tr><tr><th>Single-trial effect</th><td>0.12 (None), 95% CI 0.1�0.2</td></tr></table>"

tests\test_hrm_gating.py:24: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_hrm_gating.py::test_refusal_suppresses_pool_and_preserves_ledger
1 failed in 5.03s
```

The new-gate and unsupported-adjustment plants failed because their gates were absent. The semantic-regression plant **passed on the base**, demonstrating that `check_harms_complete` already refuses a typed refusal deliberately relabelled as unresolved; it is kept permanently alongside the positive assertion that an unmodified typed refusal passes.

```text
FREGRESSION PLANT: relabelled refusal -> check_harms_complete REFUSED
.F
================================== FAILURES ===================================
____________________ test_typed_refusal_quantitative_plant ____________________

tmp_path = WindowsPath('C:/mh-r-HRM2/.tmp/pytest-of-mahmo/pytest-0/test_typed_refusal_quantitativ0')

    def test_typed_refusal_quantitative_plant(tmp_path):
        outcome = fixture()
        write_review(tmp_path, outcome)
        planted = '<h4>Synthetic bleeding</h4><p>Pooled estimate 0.123456</p>'
>       assert gate.check_harms_synthesis_gated(str(tmp_path), planted)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: module 'harness.gate' has no attribute 'check_harms_synthesis_gated'

tests\test_hrm2_plants.py:28: AttributeError
______________________ test_unsupported_adjustment_plant ______________________

tmp_path = WindowsPath('C:/mh-r-HRM2/.tmp/pytest-of-mahmo/pytest-0/test_unsupported_adjustment_pl0')

    def test_unsupported_adjustment_plant(tmp_path):
        outcome = fixture()
        outcome["trials"][0]["design"] = {"estimator_source": "PUBLISHED_UNADJUSTED"}
        write_review(tmp_path, outcome)
>       assert gate.check_adjustment_span_backed(str(tmp_path))
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: module 'harness.gate' has no attribute 'check_adjustment_span_backed'

tests\test_hrm2_plants.py:51: AttributeError
=========================== short test summary info ===========================
FAILED tests/test_hrm2_plants.py::test_typed_refusal_quantitative_plant - Att...
FAILED tests/test_hrm2_plants.py::test_unsupported_adjustment_plant - Attribu...
2 failed, 1 passed in 4.91s
```

Post-fix plants and focused tests:

```text
.REGRESSION PLANT: relabelled refusal -> check_harms_complete REFUSED
...............BASE FIXTURE:
L1: HARMS_INCOMPLETE -- Gastrointestinal adverse events: HARMS_INCOMPLETE -- 1 known reported outcome(s) unresolved (1) among 1 source-reporting trial(s); extracted k=0. The page must not render this as harm absence.
RESOLVED FIXTURE: PASS
........................
40 passed in 3.88s
```

## All-page publication gate

Command: `python -c` importing `harness.gate`, enumerating every `docs/reviews/*/review.json`, calling `gate.gate_page(str(path.parent))`, and printing each verdict and total.

```text
balanced-crystalloids-vs-saline-mortality: PASS
colchicine-postop-af: PASS
colchicine-recurrent-pericarditis: PASS
colchicine-secondary-cv-prevention: PASS
corticosteroids-cap-mortality: PASS
corticosteroids-covid19-mortality: PASS
dapagliflozin-hfpef-hosp: PASS
denosumab-vertebral-fracture: PASS
doac-vte-recurrence: PASS
dpp4-mace-t2d: PASS
empagliflozin-hfpef-hosp: PASS
esketamine-trd-madrs: PASS
finerenone-ckd-t2d-renal: PASS
glp1-ra-mace-t2d: PASS
iv-iron-hfref-hosp: PASS
melatonin-primary-insomnia-sol: PASS
metformin-pcos-ovulation: PASS
noac-vs-warfarin-af-stroke: PASS
omega3-cardiovascular-events: PASS
pcsk9-mace: PASS
probiotics-aad-prevention: PASS
sacubitril-valsartan-hfref: PASS
semaglutide-obesity-mace: PASS
semaglutide-obesity-weight: PASS
sglt2-ckd-progression: PASS
sglt2-hfref-hosp-cvdeath: PASS
sglt2-primary-prevention-hf: PASS
spironolactone-hfref-mortality: PASS
statins-primary-prevention-elderly: PASS
ticagrelor-vs-clopidogrel-acs: PASS
tocilizumab-covid19-mortality: PASS
tranexamic-acid-pph: PASS
32 of 32 PASS
```

## Empty-AACT reproduction and retraction survival

Command: `python scripts/reproduce_review.py` with `AACT_DIR` pointing to an asserted-empty local directory. Subprocesses inherit the offline socket guard.

```text
OK  balanced-crystalloids-vs-saline-mortality
  OK  colchicine-postop-af
  OK  colchicine-recurrent-pericarditis
  OK  colchicine-secondary-cv-prevention
  OK  corticosteroids-cap-mortality
  OK  corticosteroids-covid19-mortality
  OK  dapagliflozin-hfpef-hosp
  OK  denosumab-vertebral-fracture
  OK  doac-vte-recurrence
  OK  dpp4-mace-t2d
  OK  empagliflozin-hfpef-hosp
  OK  esketamine-trd-madrs
  OK  finerenone-ckd-t2d-renal
  OK  glp1-ra-mace-t2d
  OK  iv-iron-hfref-hosp
  OK  melatonin-primary-insomnia-sol
  OK  metformin-pcos-ovulation
  OK  noac-vs-warfarin-af-stroke
  OK  omega3-cardiovascular-events
  OK  pcsk9-mace
  OK  probiotics-aad-prevention
  OK  sacubitril-valsartan-hfref
  OK  semaglutide-obesity-mace
  OK  semaglutide-obesity-weight
  OK  sglt2-ckd-progression
  OK  sglt2-hfref-hosp-cvdeath
  OK  sglt2-primary-prevention-hf
  OK  spironolactone-hfref-mortality
  OK  statins-primary-prevention-elderly
  OK  ticagrelor-vs-clopidogrel-acs
  OK  tocilizumab-covid19-mortality
  OK  tranexamic-acid-pph

32/32 reproduce (all reproducible)
```

Command: `python scripts/retraction_survival.py 3cf73885ffc83f6fcc4db273c6510a5416cdcde0`.

```text
pages with every marking kept (count >= base): 32 of 32
```

## Full verification table

Command: `python scripts/verify_all.py`, with empty `AACT_DIR` and the offline guard. Full table, with every refusal retained:

```text
  [             PASS] unit tests (pytest tests/)  (319s)
  [             PASS] offline reproduction (every live page replays from committed cache)  (66s)
  [             PASS] publication gate on every live review page  (59s)
  [             PASS] index currency (generated == committed docs/index.html)  (2s)
  [             PASS] served-artefact leak scan (docs/*.json)  (0s)
  [             PASS] held-out leak detector (registry/heldout_sealed.json)  (308s)
  [             PASS] search completeness (search_v2 measurement current; every state explicit; no zero from an exit code)  (2s)
  [             PASS] fix-state discipline (registry/fixes.json)  (71s)
  [          REFUSED] honest-state ratchet (no page may get quieter)  (11s)
  [             PASS] gate scorecard (every gate accounted for)  (1s)
  [             PASS] gate gaps table (sealed what-it-would-not-stop rows)  (5s)
VERIFY-ALL: REFUSED -- 1 of 11 limbs not PASS. Fix the harness, never the gate.
```

[Full verification log](outputs/hrm2/verify-all.txt), [build log](outputs/hrm2/build.txt), [state/source/statistics audit](outputs/hrm2/second-pass-audit.json), [adjustment sweep](docs/adjustment_label_sweep.json), [harms sweep](docs/harms_recovery_sweep.json).

The browser test covers every served harm panel using the generated bytes at absolute localhost URLs, blocks external routes, checks visible ledgers and suppression, and checks JavaScript errors. It does not certify a deployment.

## Static versus dynamic disclosure

| Component | Static configuration | Dynamic evidence / transformation |
|---|---|---|
| Synthesis rule | Requested message; existing state vocabulary | Source-reporting rows and located spans from held cache builds |
| Debt semantic | Main's existing typed-refusal resolution | Unchanged states and debt flags checked against base |
| Adjustment labels | Scale prefix and typed adjustment statuses | Exact source-span location validation; corpus sweep |
| Statistics and trial identity | No new research constants, trials or estimates | Existing inputs, identifiers, dates and numerical outputs compared against base |
| Regression plants | Explicit synthetic fixtures only in tests | Before/after assertions and gate refusals executed locally |

## INFERRED / CLAIMED

**INFERRED:** withholding a class-level quantitative harm conclusion whenever a reporting trial lacks an extracted value avoids presenting a partial extraction as a complete quantitative safety synthesis. A resolved ledger does not imply that every reporting trial supplied a usable value.

**CLAIMED:** only the implementation and measured checks above. No new literature search, recovered harm estimates, clinical safety conclusion, certification or release is claimed. The full verification refusal remains visible in `STUCK_FAILURES.md`; no ratchet acknowledgement or baseline reset was introduced.
