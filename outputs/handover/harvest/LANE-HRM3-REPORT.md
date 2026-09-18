# LANE HRM3 report

MEASURED: requested integration and verification complete. No commit, push, fetch,
or external network access performed. `git rev-parse HEAD`: `432294dba25dc5c7f33f3427a68299f79d73e71c`.
Source `C:/mh-r-HRM2` was read only. The initial destination worktree contained
only lane control files; no pre-existing implementation edits were overwritten.

## Merge and every resolution

The source status is retained in [source-status.txt](outputs/hrm3/source-status.txt).
All 202 non-conflicting files from the 205-path allowed source set were copied;
the three named Python files were merged using `3cf73885` as base, F/HEAD as ours,
and the HRM2 worktree as theirs. The path inventory is
[copied-paths.json](outputs/hrm3/copied-paths.json). The prescribed exclusions were
lane.log, lane.pid, lane.winpid, LANE_PROMPT.md, .tmp and LANE-*.

1. `harness/gate.py`: retained all E surface-check helpers/functions, CERT's
   `check_certificate`, CMP's `check_no_independent_corroboration_claim`, then
   HRM2's `check_harms_synthesis_gated` and `check_adjustment_span_backed` in that
   order. Page-gate invocations use the same ordering for these additions.
   Each of the seven checks is invoked exactly once and registered exactly once
   by gate_id. All 43 of 43 pre-existing top-level gate definitions other than
   `gate_page` are AST-identical to F; all 37 of 37 page-gate checks occur once.
2. `harness/limitations.py`: kept E's `review=None` argument and downstream
   review-dependent behavior, and inserted HRM2's harms-incomplete ledger branch
   and early return before ordinary outcome limitations.
3. `harness/page.py`: the first merge produced a whole-file conflict due to
   mixed line endings. LF-normalized temporary copies yielded two substantive
   conflicts. The first retains HRM2's ledger helper and incomplete-harms early
   return plus E's `review=None` argument and primary-review context. The second
   appends HRM2's harm ledger before E's primary-result wrapper return. All
   imports and nonconflicting tab changes from both sides survived, including
   adjustment-status rendering and E/CERT/CMP rendering.
4. `registry/gate_scorecard.json`: after the requested copy, restored every F
   entry and appended the two new HRM2 gate IDs. All 59 of 59 F entries are equal
   as objects; the final registry contains 61 unique entries of 61 entries.
   No event, adjudication, baseline, gate requirement or ratchet acknowledgement
   was weakened or fabricated.

Evidence: [merge contract](outputs/hrm3/merge-contract.json),
[integration audit](outputs/hrm3/integration-audit.json).

## Plants on the merged tree (pasted)

Command: `python -m pytest tests/test_hrm2_plants.py -v -s`.
The first three tests are the requested plants; the fourth preserves explicit
non-reporting semantics. All four tests passed.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\mahmo\AppData\Local\Programs\Python\Python313\python.exe
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: C:\mh-r-HRM3
plugins: anyio-4.13.0, hypothesis-6.155.6, base-url-2.1.0, playwright-0.8.0, timeout-2.4.0
collecting ... collected 4 items

tests/test_hrm2_plants.py::test_typed_refusal_quantitative_plant PASSED
tests/test_hrm2_plants.py::test_refusal_relabelled_as_unresolved_plant REGRESSION PLANT: relabelled refusal -> check_harms_complete REFUSED
PASSED
tests/test_hrm2_plants.py::test_unsupported_adjustment_plant PASSED
tests/test_hrm2_plants.py::test_explicit_nonreporting_refusal_does_not_enter_reporting_ledger PASSED

============================== 4 passed in 3.03s ==============================
```

Focused command: `python -m pytest tests/test_hrm_gating.py tests/test_design_key.py -q -s`.

```text
............
12 passed in 3.10s
```

## Build, renderer order and source audit

MEASURED: rebuilt 32 of 32 live review pages from existing held caches using
`python scripts/in3_run.py build`, with build date 2026-09-11 retained as the
existing deterministic fixture date. The temporary per-topic blind_map rewrite
was restored after the build. No new studies, dates, identifiers or estimates
were supplied. [Build output](outputs/hrm3/build.txt).

Commands then ran in order: harms_recovery_sweep.py, adjustment_label_sweep.py,
render_fix_ledger.py, rewrite_fixstate_lines.py, build_evidence_index.py,
render_gate_gaps.py, render_gate_scorecard.py, external_agreement.py, then
`python -m harness.index docs`. Every command exited 0.
[Exact commands and exits](outputs/hrm3/command-exits.json).

The process-wide existing `scripts/in3_offline/sitecustomize.py` guard was
inherited by Python subprocesses. AACT_DIR pointed to an asserted-empty absolute
`.tmp/empty_aact` directory. Browser contracts use local routes/listeners.

MEASURED against F: original trial inputs (including IDs, dates and source spans),
refusal codes, original reporting states, debt flags, outcome names and numerical
k/estimate/CI/tau2/scale values were preserved across 32 of 32 live reviews.
Design-derived labels/correlation metadata are excluded from unchanged-input
assertions because that is the requested adjustment change. Added reporting
ledger rows are checked against existing source-reported flags and retain their
original states. `check_harms_complete`, membership and synthesis remain unchanged.
[Per-outcome second-pass audit](outputs/hrm3/second-pass-audit.json).
This audits held source-backed fields; it is not a fresh literature verification.

MEASURED: 46 of 61 harm outcomes have quantitative synthesis suppressed, affecting
27 of 32 live reviews. All 95 of 95 published per-outcome trial rows have
UNRESOLVED adjustment status; 0 of those 95 rows have a located span supporting
an adjusted/unadjusted assertion. Scale-derived published labels, including
PUBLISHED_HR, are retained. Reconstructed rows are outside that denominator.

## Retraction survival (pasted)

Command: `python scripts/retraction_survival.py 432294db`.

```text
pages with every marking kept (count >= base): 32 of 32
```

## Empty-AACT reproduction (pasted)

Command: `python scripts/reproduce_review.py`, with the absolute empty AACT_DIR
and inherited offline guard described above.

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

## Full standard table (pasted)

Command: `python scripts/verify_all.py` initially exited 1 with an empty capture;
that run was inconclusive and was not treated as a passing verification. The
rerun calls the same unchanged `scripts.verify_all.main()` entrypoint through
`.tmp/hrm3_verify_capture.py` with line-buffered live output; no limb or gate
logic was changed. Exact invocation is in command-exits.json. The rerun exited 1:
10 of 11 verification limbs PASS, with only the expected honest-state ratchet
REFUSED. The unit-test limb includes the existing E/CERT/CMP tests and browser
contracts, including HRM's all-served-harm-panel contract. Publication gate:
32 of 32 live review pages PASS. No integration page-gate refusal required a fix.

```text
VERIFY-ALL: 11 limbs, all run, fail-closed. root=C:\mh-r-HRM3
  [             PASS] unit tests (pytest tests/)  (420s)
  [             PASS] offline reproduction (every live page replays from committed cache)  (85s)
  [             PASS] publication gate on every live review page  (73s)
  [             PASS] index currency (generated == committed docs/index.html)  (3s)
  [             PASS] served-artefact leak scan (docs/*.json)  (1s)
  [             PASS] held-out leak detector (registry/heldout_sealed.json)  (388s)
  [             PASS] search completeness (search_v2 measurement current; every state explicit; no zero from an exit code)  (3s)
  [             PASS] fix-state discipline (registry/fixes.json)  (72s)
  [          REFUSED] honest-state ratchet (no page may get quieter)  (13s)
  [             PASS] gate scorecard (every gate accounted for)  (1s)
  [             PASS] gate gaps table (sealed what-it-would-not-stop rows)  (5s)
VERIFY-ALL: REFUSED -- 1 of 11 limbs not PASS. Fix the harness, never the gate.
```

Full evidence: [verify-all.txt](outputs/hrm3/verify-all.txt).

## Honest ratchet refusal (pasted; integrator signs)

```text
[          REFUSED] honest-state ratchet (no page may get quieter)  (13s)
        TARGET verify_all.limb_honest_ratchet: head=432294dba25dc5c7f33f3427a68299f79d73e71c base=none tree=dirty:234 files files=34 docs/index.html docs/ratchet_acknowledgements.json docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html ...
        TARGET honest_ratchet: head=432294dba25dc5c7f33f3427a68299f79d73e71c base=2304824034b4ba8677da2d2d2453352711ed2a9b tree=dirty:234 files files=34 docs/index.html docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html docs/reviews/colchicine-postop-af/index.html ... base_resolution=merge-base origin/main pages=33 block_floor_refs=2304824034b4ba8677da2d2d2453352711ed2a9b,50f5a67b4fb19ada4716a0df6e6b68c2e4618304
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: not_assessed: base count 10, new count 6
        docs/reviews/esketamine-trd-madrs/index.html: declared_absent: base count 12, new count 11
        docs/reviews/probiotics-aad-prevention/index.html: not_assessed: base count 34, new count 24
        docs/index.html: lost banner block 2c1c3da7038bd131e062ff9854e52955fbfc9f879c8cda1c38a211b17e690ec9: Gate scorecard: plant validations and production refusals Adjudication coverage first, so the unresolved cannot disappea
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 1158f8935c9c47a2685dad719ef8d411cf1af64a0f89cad4447f3d3543c09ed4: DECLARED ABSENT. DESIGN REFUSAL: after refusing reconstructed non-parallel designs without an explicit design adjustment
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 35058ebae3177e56f4a895db383c9b55873db12d137ac96aee2284d7619ddabb: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 24694983, 23992557, 21873705 mention this outcome in th
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block dbbbd408ec262767dde20079bb7b4a012975f768bb21d8062298b136d4f3eb59: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 19671655 mention this outcome in the committed abstract
        docs/reviews/doac-vte-recurrence/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 63c17a3b1a6ff026e3216b53bd3c6078e2df601534271776decdd9f03b2480f6: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 33264825, 34449181, 26325557 mention this outcome in th
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 7d2411912d3b55496a33fe9a0905f6480d10aec4d43fb37141f183cb736add53: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 30415637, 30415628, 30146932 mention this outcome in th
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block c839630e932144f699429abbe2e861a0bd987344d8372c0a5b2ce106b59be677: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 31535829 mention this outcome in the committed abstract
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 7c17773d7ee68a33cf2378a420020f88a59523b40af38f32bd6b4e6cda18f6d1: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 42670961 mention this outcome in the committed abstract
```

No ratchet reset, acknowledgement or bypass was introduced. This lane does not
claim a fully green standard, release certification, or authorization to ship.

## Static versus dynamic disclosure

| Component | Static configuration | Dynamic evidence / transformation |
|---|---|---|
| Merge | Required F/base identities and lane order | Read-only source status, three-way diffs, AST and registry comparison |
| Harms | Requested suppression wording and existing state vocabulary | Held reporting rows, refusal codes, spans and completeness predicate |
| Adjustment | Scale label/status vocabulary | Located source-span validation and 95-row published-input sweep |
| Research values | No new research constants | F-to-merged comparison of held IDs, dates, inputs and numerical outputs |
| Plants | Explicit synthetic test-only fixtures | Executed gate refusals and renderer assertions |
| Verification | Existing full-standard checks; retained fixture build date | Cache rebuild, survival, empty-AACT replay, browser tests and full table |

INFERRED: preserving resolved typed-refusal ledger states while suppressing an
incomplete quantitative harms synthesis avoids equating ledger resolution with
complete numerical extraction.

CLAIMED: only the local integration and measurements documented above. Integrator
ratchet sign-off remains outstanding. No deployment or clinical safety claim.
