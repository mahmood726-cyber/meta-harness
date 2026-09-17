# LANE FIX2 report

MEASURED base and final HEAD: `3cf73885ffc83f6fcc4db273c6510a5416cdcde0`. No commit. No network. No deploy.

## Completion and counts

MEASURED finish condition met: 10 of 11 verification limbs PASS; the sole refusal is the expected honest-state ratchet. Reproduction and retraction survival both pass for 32 of 32 served topics. The honest-state ratchet is expected to refuse disclosure replacements; no acknowledgements were added or gates bypassed. The integrator must review and sign those changes.

Denominator: **32 served review topics** under `docs/reviews/*/review.json`, not all topic configurations.

- Certainty became provisional: **32 of 32 pages**.
- RoB-restricted sensitivity suppressed: **29 of 32 pages**. The other three have no re-pool because their primary pool is already refused or incompatible.
- Red-stated (existing invalidation STALE visibly retained): **32 of 32 pages**. This is a retained state, not a claim of 32 newly discovered failures.
- Primary heterogeneity marked STALE for known incomplete membership: **27 of 32 pages**. `search_not_executed` alone does not trigger this narrower predicate.
- Original downgrade totals retained: **32 of 32 reviews**.
- Exact base equality for `outcomes`, `search`, `screening`, `protocol`, `rob2`, and `invalidation`: **32 of 32 reviews**. This also checks source identifiers, dates, primary statistics and membership objects without substituting memory for evidence.
- New served-byte surface gates: **32 of 32 pages pass**.

## Implementation

`harness/grade.py` emits the provisional state whenever a domain is unassessed and supplies `render_certainty(g)` to the manuscript, overview, reporting and shared GRADE block. It reads the existing RoB output-family/rule-ID flags; machine signals remain available but do not count as formal RoB 2 assessment. `membership_incomplete` reads invalidation reason codes and eligible known-missing rows. The GRADE inconsistency basis and primary heterogeneity displays visibly carry STALE and the membership reason. Existing downgrade arithmetic and k=2 conservative floors remain intact.

`harness/rob_sensitivity.py` supplies one suppression reason. Both the page and limitation-object renderers use the same GRADE/RoB blocks; the manuscript uses the same state helpers. Identical full-pool restrictions and formally unassessed restrictions produce a suppression line, not a sensitivity estimate or its old caption. Numerical source objects remain inspectable.

`harness/gate.py` adds `check_certainty_surfaces_agree`, `check_rob_sensitivity_surfaces`, and `check_stale_heterogeneity_surfaces` to the page gate. Its HTML reader uses only the standard library. The three checks are inventoried in `registry/gate_scorecard.json` with no claimed production adjudication. The incompatible-pool leak gate still consumes the retained incompatibility reason after the overall display state becomes provisional. Existing tests were updated only where their old moderate-label/full-pool-row expectations contradicted this lane; arithmetic and pool-refusal checks remain.

No edits to membership, `harness/synth.py`, search, screening, caches, topic specifications, or protocols. No numerical research values were authored.

## Static-versus-dynamic disclosure

| Item | Classification | Source / transformation / validation |
|---|---|---|
| Provisional label; two incomplete-membership reason codes; build date 2026-09-11 | Static contract | Lane instructions; source constants; planted and served-byte checks |
| The 32-topic denominator | Dynamic disk inventory, checked against lane requirement | Served review directories; exact iteration; build/reproduction logs |
| RoB machine state and suppression | Dynamic | Existing output-family/rule IDs, rated trial counts, low-only/full relation; renderer/gate tests |
| Missing-family count | Dynamic | Known-missing panel identities, otherwise declared-absent rows; no count parsed from prose; unavailable count disclosed |
| Estimates, tau², I², PI, downgrade totals | Dynamic, retained | Existing source-backed result/domain objects; exact base comparisons; reproduction |
| Page and object hashes | Dynamic | Manifest and rendered page; no manually assigned hash |
| Prompt's served hash `ab6707c202c8ab5c` | CLAIMED observation in task | Not re-fetched under the no-network instruction |

## Publication-bias mismatch: local evidence boundary

The prompt's served revision differs from the local base. MEASURED: the local base manifest hash is `c51114c17077413c…`, and both its saved abstract and a rerender using the base manuscript source already say publication bias is unassessed. Therefore the prompt's opposite phrase is **not reproduced at this local base**. INFERRED: that served observation belongs to different/stale bytes. The exact deployment cause is unverified, not claimed. The branch now fails closed for missing assessment flags, and the new gate rejects an assessed publication-bias sentence over an unassessed canonical domain.

```text
MEASURED: baseline publication_bias.assessed=False
saved baseline page: Certainty. Partial GRADE certainty was moderate (from 0 downgrade(s); publication bias not assessed automatically; any registry ghost census is descriptive until PICO-scoped, indirectness left to human judgement).
baseline manuscript code rerender: Certainty. Partial GRADE certainty was moderate (from 0 downgrade(s); publication bias not assessed automatically; any registry ghost census is descriptive until PICO-scoped, indirectness left to human judgement).
```

## Rendered GLP-1 evidence (not text composed from JSON)

```text
Certainty. GRADE provisional -- not yet fully assessable (from 0 downgrade(s); publication bias not assessed automatically; any registry ghost census is descriptive until PICO-scoped; unassessed domains: risk_of_bias, inconsistency, publication_bias, indirectness).
Risk of bias | NOT ASSESSED | FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below
Inconsistency | NOT ASSESSED | not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Publication bias (registry-based) | NOT ASSESSED | registry census (118 of ~577 completed unpublished, 20%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=8 of 8)
Prediction interval | 0.81–0.91 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² | 4e-05 (non-zero; not 0) STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² | 0.9% STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Prompt served review_sha256: ab6707c202c8ab5c (CLAIMED in lane; not fetched)
Local base review_sha256: c51114c17077413cdd3aef2b430a751a07c6ad392164fd2ca2b3ce37df0403ca
New review_sha256: 63f1acef16041eeb39defea51e2e98fbd30ac2d53e0cffa4a305501ece244d93
```

## Base plants — verbatim failing output

The seven plants were written first and run before production edits on the recorded base. Later tests additionally mutate each of the four certainty surfaces with the other surfaces intact and preserve the formally assessed, smaller-subset control.

```text
FFFFFFF                                                                  [100%]
================================== FAILURES ===================================
_______________________ test_unassessed_is_provisional ________________________

    def test_unassessed_is_provisional():
        g = grade.grade(review())
>       assert g['certainty'] == 'provisional'
E       AssertionError: assert 'moderate' == 'provisional'
E         
E         - provisional
E         + moderate

tests\test_lane_fix2.py:16: AssertionError
_________________________ test_machine_rob_not_formal _________________________

    def test_machine_rob_not_formal():
>       assert grade._rob_domain(review())['assessed'] is False
E       assert True is False

tests\test_lane_fix2.py:20: AssertionError
_________________ test_incomplete_membership_not_homogeneity __________________

    def test_incomplete_membership_not_homogeneity():
>       assert grade.grade(review())['domains']['inconsistency']['assessed'] is False
E       assert True is False

tests\test_lane_fix2.py:24: AssertionError
____________________ test_identical_rob_pool_not_rendered _____________________

    def test_identical_rob_pool_not_rendered():
        text = limitations._rob_sensitivity_block(review()['rob_sensitivity'])
>       assert 'Low risk of bias only' not in text
E       assert 'Low risk of bias only' not in "<div class=...table></div>"
E         
E         'Low risk of bias only' is contained here:
E           r><tr><td>Low risk of bias only</td><td>k=8, HR 0.856 [0.8086, 0.9061] <em>(all pooled trials are low risk; the re-pool is the full pool)</em></td></tr></table></div>
E         ?           +++++++++++++++++++++

tests\test_lane_fix2.py:29: AssertionError
____________________ test_certainty_surface_plant_refused _____________________

tmp_path = WindowsPath('C:/mh-r-FIX2/.tmp/pytest-of-mahmo/pytest-0/test_certainty_surface_plant_r0')

    def test_certainty_surface_plant_refused(tmp_path):
        r = review()
        r['grade']['certainty'] = 'provisional'
        r['grade']['certainty_state'] = 'GRADE provisional -- not yet fully assessable'
        (tmp_path / 'review.json').write_text(json.dumps(r), encoding='utf-8')
        (tmp_path / 'index.html').write_text('<p>Partial GRADE certainty was <strong>moderate</strong></p>', encoding='utf-8')
>       assert gate.check_certainty_surfaces_agree(tmp_path)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: module 'harness.gate' has no attribute 'check_certainty_surfaces_agree'

tests\test_lane_fix2.py:39: AttributeError
__________________ test_identical_pool_surface_plant_refused __________________

tmp_path = WindowsPath('C:/mh-r-FIX2/.tmp/pytest-of-mahmo/pytest-0/test_identical_pool_surface_pl0')

    def test_identical_pool_surface_plant_refused(tmp_path):
        (tmp_path / 'review.json').write_text(json.dumps(review()), encoding='utf-8')
        (tmp_path / 'index.html').write_text('<tr><td>Low risk of bias only</td><td>k=8</td></tr>', encoding='utf-8')
>       assert gate.check_rob_sensitivity_surfaces(tmp_path)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: module 'harness.gate' has no attribute 'check_rob_sensitivity_surfaces'

tests\test_lane_fix2.py:45: AttributeError
___________________ test_homogeneity_surface_plant_refused ____________________

tmp_path = WindowsPath('C:/mh-r-FIX2/.tmp/pytest-of-mahmo/pytest-0/test_homogeneity_surface_plant0')

    def test_homogeneity_surface_plant_refused(tmp_path):
        (tmp_path / 'review.json').write_text(json.dumps(review()), encoding='utf-8')
        (tmp_path / 'index.html').write_text('<p>The pool is homogeneous; prediction interval not markedly wider than the CI.</p>', encoding='utf-8')
>       assert gate.check_stale_heterogeneity_surfaces(tmp_path)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: module 'harness.gate' has no attribute 'check_stale_heterogeneity_surfaces'

tests\test_lane_fix2.py:51: AttributeError
=========================== short test summary info ===========================
FAILED tests/test_lane_fix2.py::test_unassessed_is_provisional - AssertionErr...
FAILED tests/test_lane_fix2.py::test_machine_rob_not_formal - assert True is ...
FAILED tests/test_lane_fix2.py::test_incomplete_membership_not_homogeneity - ...
FAILED tests/test_lane_fix2.py::test_identical_rob_pool_not_rendered - assert...
FAILED tests/test_lane_fix2.py::test_certainty_surface_plant_refused - Attrib...
FAILED tests/test_lane_fix2.py::test_identical_pool_surface_plant_refused - A...
FAILED tests/test_lane_fix2.py::test_homogeneity_surface_plant_refused - Attr...
7 failed in 5.39s

```

## Build and renderer execution

`python scripts/build_topic.py <slug> --now 2026-09-11` ran for every served topic. Each local fetch cache was preflighted as present; builds did not need network access. The final rebuild followed the source repairs. Renderers ran in the requested order.

| Topic | Final build |
|---|---|
| balanced-crystalloids-vs-saline-mortality | PASS |
| colchicine-postop-af | PASS |
| colchicine-recurrent-pericarditis | PASS |
| colchicine-secondary-cv-prevention | PASS |
| corticosteroids-cap-mortality | PASS |
| corticosteroids-covid19-mortality | PASS |
| dapagliflozin-hfpef-hosp | PASS |
| denosumab-vertebral-fracture | PASS |
| doac-vte-recurrence | PASS |
| dpp4-mace-t2d | PASS |
| empagliflozin-hfpef-hosp | PASS |
| esketamine-trd-madrs | PASS |
| finerenone-ckd-t2d-renal | PASS |
| glp1-ra-mace-t2d | PASS |
| iv-iron-hfref-hosp | PASS |
| melatonin-primary-insomnia-sol | PASS |
| metformin-pcos-ovulation | PASS |
| noac-vs-warfarin-af-stroke | PASS |
| omega3-cardiovascular-events | PASS |
| pcsk9-mace | PASS |
| probiotics-aad-prevention | PASS |
| sacubitril-valsartan-hfref | PASS |
| semaglutide-obesity-mace | PASS |
| semaglutide-obesity-weight | PASS |
| sglt2-ckd-progression | PASS |
| sglt2-hfref-hosp-cvdeath | PASS |
| sglt2-primary-prevention-hf | PASS |
| spironolactone-hfref-mortality | PASS |
| statins-primary-prevention-elderly | PASS |
| ticagrelor-vs-clopidogrel-acs | PASS |
| tocilizumab-covid19-mortality | PASS |
| tranexamic-acid-pph | PASS |

### render_fix_ledger

```text
rendered docs/fix_ledger.json

```

### rewrite_fixstate_lines

```text
rewrote evidence README fix-state lines

```

### build_evidence_index

```text
TARGET evidence_index: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:216 files files=327 docs/evidence/CAPTIONS.json docs/evidence/artifact-identity-2026-09-14/01-prefix-deploy-re-tars-unverified-artifact.txt docs/evidence/artifact-identity-2026-09-14/02-second-path-search.txt ...
wrote 360 evidence index pages

```

### render_gate_gaps

```text
rendered GATE_GAPS.md gate table

```

### render_gate_scorecard

```text
wrote docs\gate_scorecard.json

```

### external_agreement

```text
same-ESTIMAND agreement (different evidence base only): 9/25
  same-estimand arithmetic replication: 2
  same-estimand diverge: 4; cross-estimand pending (suppressed): 10; cross-estimand opposite: 0; non-comparable: 0
  CROSS balanced-crystalloids-vs-saline-mortality: ours 0.9774HR vs theirs 0.92OR -- same-question SUPPRESSED (scale differs)
  CROSS colchicine-secondary-cv-prevention: ours 0.8134HR vs theirs 0.65RR -- same-question SUPPRESSED (scale differs)
  CROSS corticosteroids-covid19-mortality: ours 0.83RR vs theirs 0.66OR -- same-question SUPPRESSED (scale differs)
  CROSS doac-vte-recurrence: ours 0.9091HR vs theirs 0.9RR -- same-question SUPPRESSED (scale differs)
  CROSS omega3-cardiovascular-events: ours 0.9602HR vs theirs 0.94RR -- same-question SUPPRESSED (scale differs)
  CROSS pcsk9-mace: ours 0.8106HR vs theirs 0.83RR -- same-question SUPPRESSED (scale differs)
  CROSS semaglutide-obesity-mace: ours 0.8HR vs theirs 0.79OR -- same-question SUPPRESSED (scale differs)
  CROSS sglt2-primary-prevention-hf: ours 0.6956HR vs theirs 0.63RR -- same-question SUPPRESSED (scale differs)
  CROSS tocilizumab-covid19-mortality: ours 0.85RR vs theirs 0.86OR -- same-question SUPPRESSED (scale differs)
  CROSS tranexamic-acid-pph: ours 0.81RR vs theirs 0.77OR -- same-question SUPPRESSED (scale differs)

```

### index

```text
wrote docs\index.html

```

## Required verification — verbatim outputs

The first exploratory full unit run overlapped the initial rebuild and edits (907 passed, 13 failed). It exposed obsolete test expectations, gate inventory, canonical overview coverage, and the k=2 flag integration. Those were addressed; final verification below runs against stable files. Focused final checks: 13 lane plants/controls passed; the combined lane, GRADE-floor and incompatible-pool check passed 21 tests. No gate was loosened or bypassed.

### Empty-AACT reproduction

Command: `AACT_DIR=<workspace>/.tmp/empty_aact python scripts/reproduce_review.py`. The directory was created empty. The full verification runner inherited this setting too.

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

### Retraction survival

Command: `python scripts/retraction_survival.py 3cf73885`.

```text
pages with every marking kept (count >= base): 32 of 32

```

### Full verification table, including honest-ratchet lost blocks

Command: `python scripts/verify_all.py`. Ratchet losses below are left for integrator review; no signature is supplied here.

```text
TARGET verify_all: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:217 files files=1 scripts/verify_all.py
VERIFY-ALL: 11 limbs, all run, fail-closed. root=C:\mh-r-FIX2
  [             PASS] unit tests (pytest tests/)  (242s)
        TARGET verify_all.limb_unit_tests: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:217 files files=147 tests/test_aact_cache.py tests/test_aact_recurrent_guard.py tests/test_absence_ontology.py ...
  [             PASS] offline reproduction (every live page replays from committed cache)  (49s)
        TARGET verify_all.limb_reproduction: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:218 files files=33 scripts/reproduce_review.py docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json docs/reviews/colchicine-postop-af/review.json ...
  [             PASS] publication gate on every live review page  (56s)
        TARGET verify_all.limb_gate_every_page: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:218 files files=32 docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json docs/reviews/colchicine-postop-af/review.json docs/reviews/colchicine-recurrent-pericarditis/review.json ...
  [             PASS] index currency (generated == committed docs/index.html)  (2s)
        TARGET verify_all.limb_index_currency: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:218 files files=696 docs/index.html docs/evidence/CAPTIONS.json docs/evidence/CAPTIONS.json ...
  [             PASS] served-artefact leak scan (docs/*.json)  (1s)
        TARGET verify_all.limb_leak_scan: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:218 files files=116 docs/arm_object_sweep.json docs/class_discovery.json docs/cochrane_headtohead.json ...
  [             PASS] held-out leak detector (registry/heldout_sealed.json)  (291s)
        TARGET verify_all.limb_heldout: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:218 files files=3 registry/heldout_sealed.json docs/search_recall_regression_corpus.json harness/acquisition.py
  [             PASS] search completeness (search_v2 measurement current; every state explicit; no zero from an exit code)  (2s)
        TARGET verify_all.limb_search_completeness: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:218 files files=3 registry/search_completeness.json harness/search_v2.py harness/search_completeness.py
  [             PASS] fix-state discipline (registry/fixes.json)  (63s)
        TARGET verify_all.limb_fixstate: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:218 files files=3 registry/fixes.json docs/fix_ledger.json scripts/render_fix_ledger.py
  [          REFUSED] honest-state ratchet (no page may get quieter)  (11s)
        TARGET verify_all.limb_honest_ratchet: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:218 files files=34 docs/index.html docs/ratchet_acknowledgements.json docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html ...
        TARGET honest_ratchet: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=2304824034b4ba8677da2d2d2453352711ed2a9b tree=dirty:218 files files=34 docs/index.html docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html docs/reviews/colchicine-postop-af/index.html ... base_resolution=merge-base origin/main pages=33 block_floor_refs=2304824034b4ba8677da2d2d2453352711ed2a9b,50f5a67b4fb19ada4716a0df6e6b68c2e4618304
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: not_assessed: base count 10, new count 6
        docs/reviews/esketamine-trd-madrs/index.html: declared_absent: base count 12, new count 11
        docs/reviews/probiotics-aad-prevention/index.html: not_assessed: base count 34, new count 24
        docs/index.html: lost banner block 2c1c3da7038bd131e062ff9854e52955fbfc9f879c8cda1c38a211b17e690ec9: Gate scorecard: plant validations and production refusals Adjudication coverage first, so the unresolved cannot disappea
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block f85a78807d31d85343a73c78d55902375bf1265142747d58d473e433855e41b4: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 7d49f76d89a220055f1ad2c49e47c1e9533f5eeb0458e5ccb74126a0080713a6: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/colchicine-postop-af/index.html: lost absent block c3dab676c7cc4c4ed7c1430bc1f86f0463968a9ec0d1c2af796b6433c250b494: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/colchicine-postop-af/index.html: lost absent block 8dfc2f4ddd13b517cfa67ebda9a6a3790c8a1fea50c7298b85e933bf628f1531: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block d581286a505b55582c586d2d6eab2fb7c1fff552d507c802bb801d50765ab395: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 275b80a153f01f0d7930a7adecfb86ba9b0eee0b0a7cd982a26748a3c8ac4f41: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 57205a3c80284c1aeff24226ff5968fc5934014af55e2b4724303c7a4e83c3af: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block a54ecd524eced807f0962ba546cc1fda3db13f551f886144467a6f2ea0d59259: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 0f41b767cdeb7f3ac49137913e0bed645a03257d18decfe627336a69244089a4: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 16a31a620c341edc50358ed3a3849f254b021b872920a6a62340b100b4844dff: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 460814ddc2ea0b454e2cc59e9a1ddbc97261099c24c7c68b7000dd33fc92a91d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block f11df83d8cdcdf214dcb3553d8907cc6b8122266f3c059c96f4b9c6d1c37ee9a: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block c2bcf0acd104ff21660b73692747af61dbce3defbf18f5b3c80e1517ca389639: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 78460b7fd842a6407ad20cbdb5d6c465db843d3322956bee461b6900e54a2c20: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block cdf08119611dfcdf4ec945d9bea4e527ef45935a09f48e359cb9a83311f74e12: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block ecc8ed947c95752e72c0a6cab09514ec7c5a34cdfc2717544a6d9011a28156f3: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/doac-vte-recurrence/index.html: lost absent block da01b6ba519d765f1f7085f7413af2667584916e67a43fd872d8f391a72c3f51: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/doac-vte-recurrence/index.html: lost absent block ac057cdbffb6d6ed529764ed96d02c9bdf085df5d37d7c6dd7ccb84bffb0c38c: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 91ec4628b63b3e86d9c7d2f143975fdc54e4c8782edea24d1fdb19b3fb96c48e: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 6fd4fe1fa9d7c27b9dae78df1aa0508709049363a38be5e9069ba7005c2476a2: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 90d9054f250f3f8c546865b94358f617dfe8d76608f9e5870ebc508f90c91590: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 6b24891820614ead5920ab05217a096376de6f5eb595bc20bfa5e723ed576f82: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 7058b2699c4ee2d0f8489f2cd13f365fa05dcf95e49011617b8ecdca765369fd: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 7a1b2f9d0aa30150320bb235576d215f3bc335d0d9a1f07ccb06f24c2efac169: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block cdd5838e9ddf4722e73df01da34e5b8d82b6da2209bfc80e58b07b824f91f06d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 2f96569c95ff0621bf07097dce733e6e727a8f2aa663c83fbc36d42a2ae93a58: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 118737e7052fbdd570b2bb1df218c74b838fe181282b54f53fae236363d15295: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 04a2e41c88e8930b16c4783a824d69b3411af2e0f716308888eb7504faec9d34: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 19e48f45872f041e87da3e5d30365a431e76d3d07e43ea7a5ab24ab068b59b73: Overall certainty: not rateable. the primary pool mixes INCOMPATIBLE estimand classes (HAZARD_RATIO_FIRST_EVENT + INCIDE
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 7b4225b798a5ed89e4d0e8a324f0b622166dcaac88512b73d4dfc3f114f60faf: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 6b77e526173bc21f8c36fc9bb3eeea0c9902d81540ad387fc201c38cb209a983: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 72db58add18abd2662f0e8b4798ff2ee589a750ad3328d91563734f69747b695: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 8e8301343df98222cfe40b761ee7ec58afc1206c5534fee72f5d709f163834e3: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block 496a7c240788f4917387ccc389f17c25551a2842b80391e40c0a7353dfcd57b3: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block baea49ebb9e814194adc1b2736d663afc71255af1fa6cccb8d6d0d1589f72307: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 6398132dae3a1a7108a74c25d54c80f3a739512df47772bc155502751c36b41d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block c77ef0e830e5d74310099c90ef651caad9e1ee2aff8dd7d8de391e991afc6962: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/pcsk9-mace/index.html: lost absent block 7b2d1674478f8315cbef7e6285dad3f45e0a93bc14acce314da847954a6bcbb9: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/pcsk9-mace/index.html: lost absent block 9fb655c4cc64424164f8dee8b10bed1f52ddf44da88fa836084f5ea54e5ed034: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 3690b1ad41faf51a261928ebca1cf523e09cb400f4cc759e307d156697580e8b: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 99becb418875e3d7ddd6dbda49c73006d7252e22eef6dc35199ff53c62376365: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 09ed94fe6e8360cfecf6ad69db79fcb7ca77b505565936768935dc6b62adcb67: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 26ab09f2b6cbce2e1e158fb630fa57a0c0186f3db7491523f7fa2adf79d4fcbc: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 3fe49f850a635eb2189b79baa4f679f142e19bce8eacd03224e40f2a3feee68c: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 45446b368a9c9346efd1ba26dd96de014ee501bb6caa900c82360c75634ad0af: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 0f8ad79d9c66fae246cde2257ffe2107813ab8e139bc575a8052b607ce492c12: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block eb69309ac2fbd67743b0ded82a6daaa5e7316e38145aaa3f3a29d30223c4c4fc: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block db4655aa165a114b729706357dc701b5b8bcd0a7e9d9d21aa8ff9d9cd969266b: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 965250ce4cfd0308b296c784661c49b482f248ddcf01136bde7f1c17d3e77525: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block be6ab27c20f82912a45e9cbf09be8802e97350ee49be185e8851e97a2440fe15: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 8d61bf47c06063dec14f2d4656e683b5c5445128098b53a4545d6f790bf52db7: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block a88aa38b82f42e250de2a7b237f6026ce62106c4c5a06c14521eef07aba1cf69: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 4bfc6a1f39b6524082d059f894fe1d3440e3725de7a19ed581edc014ad0c276d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block a20410a071d279f8c5f0d4f2524c309a86be39ca53864329abebb24238d6d882: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 1b61824a331cba7ed7af28c78c2e1e32f08a54957ed61b788a77d0ea6495dbb8: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block e49ac2b8042d3c0330eac88d67e2accc7128131e64a79ea69ad81323e3b054d1: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block c3fd688cd9c199c13ff366e0812df59617cd1cd51a0c62f409f3ee3598b7f98e: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block f16e90d7d6310cdb9d636170fa9b5160948b9ed4d0d5fc380801531bb72dc82d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block f5fafd4d2f6b2c4d7c6cd44bed380029eed96d2f06707b0b8321289ed32b242c: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block 295a768c15eeb1c46a8cda92832439fa2eb6fb6b500a8f11b2b737f4f9b6bc0d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block ac7d9964082a37db27b76419258d0d324859f0857bdc0357035d21ff2c999a37: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block b8c4b60bd942a25aaaafc43a4cc63dc78c3e705961e0fbf0a49155bf75bfe08b: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 960be40ef77ff4a78df7696b5504db234eb1f8d843aa2fd6152fed50e4fd2b0d: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
  [             PASS] gate scorecard (every gate accounted for)  (1s)
        TARGET verify_all.limb_gate_scorecard: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:218 files files=3 registry/gate_scorecard.json docs/gate_scorecard.json harness/gate_scorecard.py
        TARGET gate_scorecard: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:218 files files=6 registry/gate_scorecard.json docs/gate_scorecard.json scripts/verify_all.py ...
  [             PASS] gate gaps table (sealed what-it-would-not-stop rows)  (5s)
VERIFY-ALL: REFUSED -- 1 of 11 limbs not PASS. Fix the harness, never the gate.

```
