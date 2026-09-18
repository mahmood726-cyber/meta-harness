# LANE CHK — counts from execution receipts

HEAD: `237e90946f5b257265b0a3b1c986a8907d12eded`. No commit, reset, checkout, stash, push or deployment.
The F: index/workbook session context was accessed; neither was edited because this
lane does not change project/submission status. AUD2's report and relevant diffs
were read as design context; its measurements were not treated as this base's evidence.

## MEASURED: pre-fix and post-fix plants

The production tree was untouched when the four original plants ran. Evidence:
[prefix_pytest.txt](.tmp/chk/prefix_pytest.txt). The four assertions were retained
unchanged after implementation and re-read: passing them now is correction of
the demonstrated failures, not deletion or loosening of a plant.

| Plant | Before | After |
|---|---|---|
| IV-iron rendered count equals completed actual checker calls | FIRED: 4 reported / 0 calls | HELD: 4 / 4 |
| Renderer raises: count falls by one, failed: 1 visible | FIRED: stayed 1 rather than falling to 0 | HELD: 3 to 2; one failed receipt and exception text |
| GLP-1 k=8 given k=1-verbatim provenance | FIRED: accepted | HELD: rejected |
| Zero completed checks visibly failing | HELD | HELD |

Pre-fix: 3 of 4 plants fired, 1 of 4 held. Post-fix: 4 of 4 held.
Additional plants cover a checker exception, an inflated legacy count, limb
exceptions and unattended PLANNED limbs. The combined targeted command in
[postfix_pytest.txt](.tmp/chk/postfix_pytest.txt) passed **39 of 39 tests**.
The pre-existing contradiction integration test now expects two completed
surface checks and one FAILED receipt; its original contradiction count and
build-refusal assertions remain. Its output directory now uses pytest's temporary path.

## MEASURED: rebuilds and hashes

Both named topics were built first, then the remaining topics, with
`scripts.build_topic.main(slug, '2026-09-11')`, the same entry point as
`python scripts/build_topic.py <slug> --now 2026-09-11`.
All 32 of 32 cache files were checked before building; the runner blocked socket
connections and used committed caches. [Rebuild log](.tmp/chk/rebuild.txt).

All 32 of 32 HTML hashes moved; 0 of 32 review-core hashes moved.
The table's unit is a completed significance checker invocation on one surface,
so a primary outcome can contribute three receipts. Counts are no longer sums
of outcome and strand inventory. There are 79 completed significance receipts
across the 32 pages, with zero failed/planned receipts in these successful builds.
Zero-check pages retain their failing limitation state.

| Page | Old N | Completed / failed / planned | review SHA moved | HTML SHA moved |
|---|---:|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 0 | 0 / 0 / 0 | no | yes |
| colchicine-postop-af | 1 | 3 / 0 / 0 | no | yes |
| colchicine-recurrent-pericarditis | 1 | 1 / 0 / 0 | no | yes |
| colchicine-secondary-cv-prevention | 1 | 3 / 0 / 0 | no | yes |
| corticosteroids-cap-mortality | 0 | 0 / 0 / 0 | no | yes |
| corticosteroids-covid19-mortality | 1 | 3 / 0 / 0 | no | yes |
| dapagliflozin-hfpef-hosp | 1 | 3 / 0 / 0 | no | yes |
| denosumab-vertebral-fracture | 3 | 5 / 0 / 0 | no | yes |
| doac-vte-recurrence | 1 | 3 / 0 / 0 | no | yes |
| dpp4-mace-t2d | 1 | 3 / 0 / 0 | no | yes |
| empagliflozin-hfpef-hosp | 1 | 3 / 0 / 0 | no | yes |
| esketamine-trd-madrs | 1 | 3 / 0 / 0 | no | yes |
| finerenone-ckd-t2d-renal | 0 | 0 / 0 / 0 | no | yes |
| glp1-ra-mace-t2d | 1 | 3 / 0 / 0 | no | yes |
| iv-iron-hfref-hosp | 4 | 4 / 0 / 0 | no | yes |
| melatonin-primary-insomnia-sol | 1 | 3 / 0 / 0 | no | yes |
| metformin-pcos-ovulation | 1 | 3 / 0 / 0 | no | yes |
| noac-vs-warfarin-af-stroke | 2 | 4 / 0 / 0 | no | yes |
| omega3-cardiovascular-events | 1 | 3 / 0 / 0 | no | yes |
| pcsk9-mace | 2 | 4 / 0 / 0 | no | yes |
| probiotics-aad-prevention | 1 | 3 / 0 / 0 | no | yes |
| sacubitril-valsartan-hfref | 0 | 0 / 0 / 0 | no | yes |
| semaglutide-obesity-mace | 2 | 4 / 0 / 0 | no | yes |
| semaglutide-obesity-weight | 0 | 0 / 0 / 0 | no | yes |
| sglt2-ckd-progression | 3 | 5 / 0 / 0 | no | yes |
| sglt2-hfref-hosp-cvdeath | 0 | 0 / 0 / 0 | no | yes |
| sglt2-primary-prevention-hf | 1 | 3 / 0 / 0 | no | yes |
| spironolactone-hfref-mortality | 1 | 3 / 0 / 0 | no | yes |
| statins-primary-prevention-elderly | 0 | 0 / 0 / 0 | no | yes |
| ticagrelor-vs-clopidogrel-acs | 0 | 0 / 0 / 0 | no | yes |
| tocilizumab-covid19-mortality | 1 | 3 / 0 / 0 | no | yes |
| tranexamic-acid-pph | 2 | 4 / 0 / 0 | no | yes |

Exact old/new hashes are retained in [after.json](.tmp/chk/after.json), with the
pre-edit snapshot in [before.json](.tmp/chk/before.json).
`python scripts/retraction_survival.py 237e9094`: **32 of 32**, exit 0;
[log](.tmp/chk/retraction_survival.txt). Browser E2E
`python -m pytest -q tests/test_certificate_ui.py`: **1 of 1 passed**, exercising
certificate rendering/downloads on all 32 pages using the installed browser.
The existing browser test uses a loopback ephemeral port for lane isolation;
all nonlocal browser requests are aborted. `git diff --check`: PASS.

## Diff summary

- `harness/census.py`: receipt schema with PLANNED, ATTEMPTED, COMPLETED, FAILED,
  reason and canonical inputs digest; actual outcome-surface and strand checker
  calls; renderer/checker exceptions become FAILED and refuse builds; counts and
  checked surfaces derive from completed receipts. Determinism, reproduction,
  proposition and claimgraph records also carry receipts. k=1-verbatim requires k=1.
- `harness/page.py`: computes visible counts from receipts, ignores legacy
  scalar counts, shows failed/not-attempted tallies and retains zero-check warning.
- `scripts/verify_all.py`: plans every limb before execution, emits receipts,
  refuses every state other than COMPLETED; no limb implementation removed or weakened.
- `scripts/reproduce_review.py`: reconstructs the added proposition/claimgraph
  receipts so the existing replay path agrees with the build path. This small
  dependent change is necessary for receipt metadata outside the scientific core.
- Tests and 32 regenerated review bundles. No research inputs or estimates edited.

## Static versus dynamic disclosure

| Item | Kind | Meaning |
|---|---|---|
| State names / check IDs | Static | Execution contract |
| Counts / exceptions / digests | Dynamic | Executed checks and canonical input objects |
| Limb digest | Dynamic target descriptor + limb identity | Local execution context; not a cryptographic attestation of all dependency bytes |
| k=1 token constraint | Static validation | Single-study label cannot certify a multi-study outcome |
| 999 / injected exceptions | Synthetic tests only | Never emitted as scientific findings |
| Trial IDs, dates and statistics | Existing data | All 32 scientific core hashes unchanged |

## Boundaries: INFERRED / CLAIMED

MEASURED: the four plants, cached rebuilds, receipt counts, core/HTML hash comparisons
and retraction survival above. The unchanged core hashes support the inference
that this increment did not alter scientific IDs, dates or statistical outputs;
this is not a new independent bibliographic revalidation of every source.

CLAIMED scope is local execution accounting for these existing checks. A completed
receipt means the named check returned successfully with no detected contradiction,
not that all scientific claims are true. The significance scanner's existing
recognition limits remain. No independent execution attestation is established.
GRADE NOT_ASSESSABLE is a separate increment; certificate binding is a separate
increment. The existing certificate has no checks-passed numerical tally, and
was not expanded to bind these new receipts. This work does not establish complete
interval provenance from a label, exhaustive nested sensitivity checking, or
portfolio certification. No Overmind PASS, submission-ready or shipped claim.



Additional measured validation: offline replay returned 32/32 reproducible. The dedicated served-count browser contract passed 1 of 1, checking visible receipt-derived counts on 32 of 32 pages and the injected failed: 1 state at http://127.0.0.1:8000/. Evidence: [.tmp/chk/counts_ui.txt](.tmp/chk/counts_ui.txt). Its first run failed because the test used an incorrect tab name; the selector was corrected to the existing Reproducibility label, with assertions retained.

Final source review extended the k=1 provenance rejection to strand pools. The final targeted suite passed 39 of 39. A spy over all 32 current cores measured 79 completed actual checker calls; 32 of 32 regenerated receipt sets exactly equal the saved sets, and all 32 pass interval-provenance validation. This final check ran after the strand hardening; the full verifier began before that small extension.

## Full verification: MEASURED

VERIFY-ALL: REFUSED -- 4 of 11 limbs not PASS. Fix the harness, never the gate.

7 of 11 limbs COMPLETED. Full output: [.tmp/chk/verify_all.txt](.tmp/chk/verify_all.txt).

Limb receipts pasted verbatim:

```text
CHECK_RECEIPTS [{"check_id": "limb_unit_tests", "surface": "unit tests (pytest tests/)", "state": "FAILED", "reason": "TARGET verify_all.limb_unit_tests: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:138 files files=158 tests/conftest.py tests/test_aact_cache.py tests/test_aact_recurrent_guard.py ...\n..............................................                           [100%]\n================================== FAILURES ===================================\n__________________________ test_real_store_validates __________________________\n\n    def test_real_store_validates() -> None:\n        ok, reasons = fixstate.check(ROOT)\n    \n>       assert ok, \"\\n\".join(reasons)\nE       AssertionError: docs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py\nE       assert False\n\ntests\\test_fixstate.py:457: AssertionError\n=========================== short test summary info ===========================\nFAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...\n1 failed, 981 passed in 491.70s (0:08:11)", "inputs_sha256": "e35ece9ac3d189584b0c947090d21b69458eaa487ceb813bab792cddf4e1cf74"}, {"check_id": "limb_reproduction", "surface": "offline reproduction (every live page replays from committed cache)", "state": "COMPLETED", "reason": "TARGET verify_all.limb_reproduction: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:141 files files=33 scripts/reproduce_review.py docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json docs/reviews/colchicine-postop-af/review.json ...\nOK  balanced-crystalloids-vs-saline-mortality\n  OK  colchicine-postop-af\n  OK  colchicine-recurrent-pericarditis\n  OK  colchicine-secondary-cv-prevention\n  OK  corticosteroids-cap-mortality\n  OK  corticosteroids-covid19-mortality\n  OK  dapagliflozin-hfpef-hosp\n  OK  denosumab-vertebral-fracture\n  OK  doac-vte-recurrence\n  OK  dpp4-mace-t2d\n  OK  empagliflozin-hfpef-hosp\n  OK  esketamine-trd-madrs\n  OK  finerenone-ckd-t2d-renal\n  OK  glp1-ra-mace-t2d\n  OK  iv-iron-hfref-hosp\n  OK  melatonin-primary-insomnia-sol\n  OK  metformin-pcos-ovulation\n  OK  noac-vs-warfarin-af-stroke\n  OK  omega3-cardiovascular-events\n  OK  pcsk9-mace\n  OK  probiotics-aad-prevention\n  OK  sacubitril-valsartan-hfref\n  OK  semaglutide-obesity-mace\n  OK  semaglutide-obesity-weight\n  OK  sglt2-ckd-progression\n  OK  sglt2-hfref-hosp-cvdeath\n  OK  sglt2-primary-prevention-hf\n  OK  spironolactone-hfref-mortality\n  OK  statins-primary-prevention-elderly\n  OK  ticagrelor-vs-clopidogrel-acs\n  OK  tocilizumab-covid19-mortality\n  OK  tranexamic-acid-pph\n\n32/32 reproduce (all reproducible)", "inputs_sha256": "434f54e835860981b174f0f6924c6666521edb7128f76231e5e04e8f4c798b39"}, {"check_id": "limb_gate_every_page", "surface": "publication gate on every live review page", "state": "COMPLETED", "reason": "TARGET verify_all.limb_gate_every_page: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:141 files files=32 docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json docs/reviews/colchicine-postop-af/review.json docs/reviews/colchicine-recurrent-pericarditis/review.json ...\n32 pages gated", "inputs_sha256": "5d5004c941b94f29eafbfe35f4b11aca0cb3b9d7fd219e3b3d4c33e24bbdd95d"}, {"check_id": "limb_index_currency", "surface": "index currency (generated == committed docs/index.html)", "state": "COMPLETED", "reason": "TARGET verify_all.limb_index_currency: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:141 files files=696 docs/index.html docs/evidence/CAPTIONS.json docs/evidence/CAPTIONS.json ...\ngenerated index == committed docs/index.html; evidence indexes current", "inputs_sha256": "8e3bb1dff78465a67f01c6b964af91e2ff46b1cae52a11f2163ddc473a0621ee"}, {"check_id": "limb_leak_scan", "surface": "served-artefact leak scan (docs/*.json)", "state": "COMPLETED", "reason": "TARGET verify_all.limb_leak_scan: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:141 files files=118 docs/adjustment_label_sweep.json docs/arm_object_sweep.json docs/class_discovery.json ...\nno served aggregate publishes a pooled statistic for a suppressed-state topic", "inputs_sha256": "06e612cd1a1f98f30409765cc4c02e834b27aac39355bff7ca159b1e2fad0b11"}, {"check_id": "limb_heldout", "surface": "held-out leak detector (registry/heldout_sealed.json)", "state": "COMPLETED", "reason": "TARGET verify_all.limb_heldout: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:141 files files=3 registry/heldout_sealed.json docs/search_recall_regression_corpus.json harness/acquisition.py\npublished regression-corpus measurement matches current engine", "inputs_sha256": "dfa9b2b53f6e8485630e737922990fb07280d65138af8bd3a532c61e2cb112ea"}, {"check_id": "limb_search_completeness", "surface": "search completeness (search_v2 measurement current; every state explicit; no zero from an exit code)", "state": "COMPLETED", "reason": "TARGET verify_all.limb_search_completeness: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:141 files files=3 registry/search_completeness.json harness/search_v2.py harness/search_completeness.py\nsearch_v2 measurement current for engine a57dc45d6824 (outputs/search_v2/candidates-2026-09-15r3-all.json); states: RAN_OK 0 of 21; RAN_OK_WITH_SOURCE_ERRORS 21 of 21; RAN_ZERO 0 of 21; RAN_ERROR 0 of 21; NOT_RUN 0 of 21", "inputs_sha256": "266912a724dd7e54f52df8d53d72896308922a0a0aa749814dc03cb3d2a81bc6"}, {"check_id": "limb_fixstate", "surface": "fix-state discipline (registry/fixes.json)", "state": "FAILED", "reason": "TARGET verify_all.limb_fixstate: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:141 files files=3 registry/fixes.json docs/fix_ledger.json scripts/render_fix_ledger.py\ndocs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py", "inputs_sha256": "a290d925188de26fd52b360604c3aee61ee1806dd77fb89cca20b2b6986e6b00"}, {"check_id": "limb_honest_ratchet", "surface": "honest-state ratchet (no page may get quieter)", "state": "FAILED", "reason": "TARGET verify_all.limb_honest_ratchet: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:141 files files=34 docs/index.html docs/ratchet_acknowledgements.json docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html ...\nTARGET honest_ratchet: head=237e90946f5b257265b0a3b1c986a8907d12eded base=2304824034b4ba8677da2d2d2453352711ed2a9b tree=dirty:141 files files=34 docs/index.html docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html docs/reviews/colchicine-postop-af/index.html ... base_resolution=merge-base origin/main pages=33 block_floor_refs=2304824034b4ba8677da2d2d2453352711ed2a9b,50f5a67b4fb19ada4716a0df6e6b68c2e4618304\ndocs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: not_assessed: base count 10, new count 6\ndocs/reviews/esketamine-trd-madrs/index.html: declared_absent: base count 12, new count 11\ndocs/reviews/probiotics-aad-prevention/index.html: not_assessed: base count 34, new count 24", "inputs_sha256": "e522672eeadc45042979119a2a40624394085dc37b9f8620605ec1c3533b54af"}, {"check_id": "limb_gate_scorecard", "surface": "gate scorecard (every gate accounted for)", "state": "COMPLETED", "reason": "TARGET verify_all.limb_gate_scorecard: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:141 files files=3 registry/gate_scorecard.json docs/gate_scorecard.json harness/gate_scorecard.py\nTARGET gate_scorecard: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:141 files files=6 registry/gate_scorecard.json docs/gate_scorecard.json scripts/verify_all.py ...\n61 gates accounted for; 131 events; 72 UNRESOLVED; 58 adjudicated plant validations; 0 with adjudicated production true refusals", "inputs_sha256": "cfcef4c589b5fe4f5393ecab8d99364adee09458a7b23983bdd94a32956de349"}, {"check_id": "limb_gate_gaps", "surface": "gate gaps table (sealed what-it-would-not-stop rows)", "state": "FAILED", "reason": "gate gaps table STALE: GATE_GAPS.md", "inputs_sha256": "94aa4d91b6e273ae3851912d6ae0f67db75cc09aafc5507dccae6f57f3b1ec82"}]
```

Full verification is not a PASS. The refusals above are retained; no limb was bypassed. See [STUCK_FAILURES.md](STUCK_FAILURES.md).

Full-suite detail: 981 of 982 tests passed; the sole failure is test_fixstate.py::test_real_store_validates (stale docs/fix_ledger.json). The 39-test final lane suite and dedicated counts UI ran separately after the full-suite snapshot began.

Ratchet follow-up measurement against the required served base 237e9094: balanced-crystalloids not_assessed 6 -> 6; esketamine declared_absent 11 -> 11; probiotics not_assessed 24 -> 24. Thus all 3 reported marker shortfalls already exist at the served base; none was introduced by this lane. The full ratchet compares an older merge-base and remains REFUSED. Evidence: [.tmp/chk/ratchet-base.json](.tmp/chk/ratchet-base.json). The stale ledger and gate-gaps outputs were not regenerated as part of this one-defect lane, and no claim is made here about their pre-lane validation status.

Lane finish: requested repair, plants, 32-page rebuild/table, retraction gate and report delivered. Full-verifier refusals remain explicitly logged; no release or portfolio-status promotion. Final git diff --check passed.
