# LANE HD report

Base and final HEAD: `2a5e0ee9fe72b946ba890cf527182976fb7b3646`. No commit; no network. No release or submission status changed.

Implemented verified byte/text writes, held-digest verification, process-local byte-bound regex receipts, the copy CLI, whole-tree lint and its artefact-reading verify_all limb.

## Measured plant and correction to the brief

The exact supplied standalone pattern cannot produce the requested zero-hit result: after shell corruption it raises `re.error: unterminated character set`. The exact shell run is retained below. A separately labelled minimal extension with a trailing alternative reproduces the silent-zero class. This extension is a regression fixture, not a claim to possess the missing full historical pattern. The unsafe shell consumer ran before invoking the guards; both guards then refused those same bytes.

```text
exact
script verbatim:
cat <<EOF > pattern.py
pattern = r"[/\\]"
EOF

received: b'pattern = r"[/\\]"\n'
hex: 70 61 74 74 65 72 6e 20 3d 20 72 22 5b 2f 5c 5d 22 0a
pre-fix compile error (no zero claimed): unterminated character set at position 0
WriteRoundTripError: C:\mh-r-HD\outputs\hd\exact\pattern.py: expected sha256=ce382fa1efdeac11a7fa9957646ae7d8cf4195356eef730611e783b6b085c7a7; actual sha256=6cdc2c7d105fc3891047b260410f07ca8536cf8ba4d820aa22031950c08d873a; first differing offset=15
guard: {"status": "UNVERIFIED_INSTRUMENT", "matches": null, "pattern_sha256_verified": false}
lint REFUSED: [{"file": "outputs/hd/exact/plant.sh", "line": 1, "body_line": 2, "text": "pattern = r\"[/\\\\]\""}]
fixed: {"status": "OK", "matches": 1, "pattern_sha256_verified": true}
swallowed-alternative
script verbatim:
cat <<EOF > pattern.py
pattern = r"[/\\]|[x]end"
EOF

received: b'pattern = r"[/\\]|[x]end"\n'
hex: 70 61 74 74 65 72 6e 20 3d 20 72 22 5b 2f 5c 5d 7c 5b 78 5d 65 6e 64 22 0a
pre-fix: 0 hits -> confirmed clean
WriteRoundTripError: C:\mh-r-HD\outputs\hd\swallowed-alternative\pattern.py: expected sha256=a5c7eb24ef52abf060ce0e62a16ab725e00c563c1b4eaf8c9b55e15ae60b1403; actual sha256=055d613e9101e550f817ea20b3c0b0f76650e7ba1eab1d377758e3decdac481a; first differing offset=15
guard: {"status": "UNVERIFIED_INSTRUMENT", "matches": null, "pattern_sha256_verified": false}
lint REFUSED: [{"file": "outputs/hd/swallowed-alternative/plant.sh", "line": 1, "body_line": 2, "text": "pattern = r\"[/\\\\]|[x]end\""}]
fixed: {"status": "OK", "matches": 1, "pattern_sha256_verified": true}

```

Layer 1 compares bytes supplied by its caller with bytes on disk; it cannot detect corruption that occurred before those intended bytes were established. `assert_file_bytes` therefore compares shell output with independently retained intended bytes. The writer regression also injects corruption during the write and proves `write_bytes_verified` itself raises. A digest-only held-file check cannot locate the differing offset without the original bytes, and says so explicitly.

Regex consumers must use `safe_regex_scan`: unverified or changed bytes return matches=null and UNVERIFIED_INSTRUMENT; verified malformed regexes return INVALID_INSTRUMENT; valid scans expose the verified flag even when matches=0. Receipts do not survive process restart; verify a held source against an independently retained expected digest. This proves transport integrity, not regex semantic correctness.

## Lint census

Initial pre-plant scan: **0 findings**, 0 read/parse errors, 734 files. Contrary to the expectation in the brief, no pre-existing historical output scripts were flagged in this checked-out tree. No historical outputs were edited.

Final snapshot before this report: **12 findings**, 0 read/parse errors, 779 files. The scan includes untracked/ignored working files and extensionless .githooks; only .git metadata is excluded. Temporary pytest fixtures explain the dynamic .tmp count.

| Directory | Findings |
|---|---:|
| .tmp | 10 |
| outputs | 2 |

Historical outputs findings: none. New output regression plants:
- outputs/hd/exact/plant.sh
- outputs/hd/swallowed-alternative/plant.sh

Production scripts/ and .githooks/ findings: 0. Whole-tree verdict: REFUSED; verify_all limb: REFUSED. The deliberate unsafe evidence remains visible and therefore blocks this gate; it has no allowlist or skip marker.

Complete file/line/body findings and scanned-file inventory: `outputs/heredoc-escape-lint.json`. Initial inventory: `outputs/hd/baseline-lint.json`. The lint never executes scanned scripts; Python shell arguments are inspected statically, including named string assignments. Runtime-generated shell commands remain outside complete static analysis.

## Writer call sites

Converted **98 of 98 inventoried text-writer sites** across 74 scripts. The inventory includes generic text sinks so escape-bearing text passed through variables is covered, plus the R temporary-source writer. Original source snippets and baseline line numbers are in `outputs/hd-call-sites.json`. Raw data byte copies, JSON-only direct dump sinks without literal escapes, and subprocess stdout file descriptors remain unchanged. Context-managed text writers buffer the completed document, then verify it; append preserves existing bytes. They are not concurrent append primitives.

| Original file | Original line |
|---|---:|
| scripts/aact_measure.py | 97 |
| scripts/adjustment_label_sweep.py | 36 |
| scripts/archive_raw_bodies.py | 78 |
| scripts/build_evidence_index.py | 180 |
| scripts/build_search_benchmark.py | 69 |
| scripts/build_search_benchmark.py | 78 |
| scripts/build_topic.py | 44 |
| scripts/codex_lane_queue.py | 45 |
| scripts/codex_lane_queue.py | 53 |
| scripts/codex_lane_queue.py | 129 |
| scripts/comparator_correctness_sweep.py | 211 |
| scripts/comparator_correctness_sweep.py | 340 |
| scripts/comparator_correctness_sweep.py | 471 |
| scripts/comparator_effect_rows_reach.py | 58 |
| scripts/comparator_panel_sweep.py | 41 |
| scripts/comparator_second_pass_sweep.py | 94 |
| scripts/comparator_truth_sweep.py | 97 |
| scripts/compat_direction_sweep.py | 63 |
| scripts/compat_underlying_sweep.py | 129 |
| scripts/consumer_consistency_sweep.py | 78 |
| scripts/cross_source_endpoint_sweep.py | 82 |
| scripts/d5_rule_sweep.py | 122 |
| scripts/decoupling_universal.py | 91 |
| scripts/design_refusal_sweep.py | 110 |
| scripts/design_sweep.py | 138 |
| scripts/eligibility_chain_sweep.py | 76 |
| scripts/endpoint_canonical_sweep.py | 17 |
| scripts/entry_condition_sweep.py | 133 |
| scripts/error_coverage.py | 42 |
| scripts/funding_sweep.py | 155 |
| scripts/hazard_consumer_sweep.py | 129 |
| scripts/hazard_consumer_sweep.py | 218 |
| scripts/hazard_consumer_sweep.py | 289 |
| scripts/hazard_consumer_sweep.py | 317 |
| scripts/hazard_consumer_sweep.py | 359 |
| scripts/hm3_aact_scan.py | 31 |
| scripts/hm3_aact_scan.py | 46 |
| scripts/hm3_aact_scan.py | 44 |
| scripts/hm3_adjudicate.py | 27 |
| scripts/hm3_inventory.py | 32 |
| scripts/hm3_report.py | 79 |
| scripts/hm3_second_pass.py | 59 |
| scripts/hm3_verify.py | 21 |
| scripts/hm3_verify.py | 49 |
| scripts/hm3_verify.py | 32 |
| scripts/hrm2_audit.py | 71 |
| scripts/in3_aact_inventory.py | 39 |
| scripts/in3_finish.py | 22 |
| scripts/in3_harms.py | 16 |
| scripts/in3_report.py | 65 |
| scripts/in3_second_pass.py | 55 |
| scripts/lane_fulltext.py | 72 |
| scripts/limitations_sweep.py | 61 |
| scripts/limitations_sweep.py | 63 |
| scripts/measure_regression_corpus_recall.py | 148 |
| scripts/measure_regression_corpus_recall_search_v2.py | 139 |
| scripts/measure_search_v2_measurement.py | 117 |
| scripts/measure_search_v2_measurement.py | 126 |
| scripts/membership_consistency_sweep.py | 82 |
| scripts/migrate_verified_inputs.py | 34 |
| scripts/missing_effect_sweep.py | 110 |
| scripts/near_match_sweep.py | 178 |
| scripts/or_class_sweep.py | 110 |
| scripts/outcome_judgments.py | 132 |
| scripts/parity_relation_sweep.py | 66 |
| scripts/prisma_fair_compare.py | 436 |
| scripts/prisma_fair_compare.py | 561 |
| scripts/prisma_fair_compare.py | 623 |
| scripts/probiotics_search_diagnostic.py | 74 |
| scripts/probiotics_search_diagnostic.py | 79 |
| scripts/production_record.py | 208 |
| scripts/production_record.py | 290 |
| scripts/production_record.py | 315 |
| scripts/production_record.py | 311 |
| scripts/proposition_sweep.py | 90 |
| scripts/reason_audit_sweep.py | 111 |
| scripts/refresh_error_rate_census.py | 43 |
| scripts/refusal_reason_sweep.py | 149 |
| scripts/render_fix_ledger.py | 157 |
| scripts/render_gate_gaps.py | 101 |
| scripts/rewrite_fixstate_lines.py | 104 |
| scripts/rob_rederivation_sweep.py | 90 |
| scripts/run_prospective_topic.py | 114 |
| scripts/seal_search_vocabulary.py | 174 |
| scripts/search_v2_run.py | 261 |
| scripts/search_v2_run.py | 300 |
| scripts/search_v2_run.py | 332 |
| scripts/search_v2_run_evidence.py | 66 |
| scripts/second_source_sweep.py | 126 |
| scripts/seed_comparator_panels.py | 13 |
| scripts/source_hierarchy_sweep.py | 196 |
| scripts/unextracted_sweep.py | 103 |
| scripts/verification_adjudicate.py | 206 |
| scripts/verify_comparator_lane.py | 50 |
| scripts/verify_comparator_lane.py | 48 |
| scripts/weakness_survey.py | 242 |
| scripts/write_legacy_ledgers.py | 125 |
| scripts/validate_synth.py | 38 |

## Verification

Focused tests:
```text
..................                                                       [100%]
18 passed in 2.02s

```

Full offline suite: **961 passed, 14 failed**, 5 warnings, 318.31 seconds; exact output is `outputs/hd/tests.txt`. It ran before the final integration corrections. Two deployment-bundle failures were fixed by shipping harness/safe_write.py and testing the isolated bundle. The missing gate-registry entry was fixed and its generated view refreshed, with no invented adjudications (the new gate remains UNVALIDATED). The subsequent combined focused/deployment/scorecard rerun passed **37 tests**. The final registry-only correction was rerun separately. Other broad-run failures concern certificate/analysis digests, stale fix-ledger state, and six browser tests blocked by the strict socket guard. The full suite was not rerun; no green full-suite claim is made.

Final deployment/scorecard rerun: `python -m pytest -q tests/test_production_record_deploy_target.py tests/test_gate_scorecard.py` — 19 passed in 22.66 seconds.

Compile check: `python -m compileall -q scripts harness/safe_write.py` PASS. `git diff --check` PASS. No full verify_all PASS is claimed; its new limb deliberately refuses the retained plants. The offline guard blocked all socket connects, including local browser plumbing; UI failures under this guard are not evidence of a rendering defect.

## Static versus dynamic disclosure

| Item | Static or dynamic | Evidence / limit |
|---|---|---|
| Plant patterns and slash input | Static test fixtures | Labelled regression instruments, not research findings |
| Digests, offsets, shell output | Dynamic | Actual sh execution and byte rereads in outputs/hd/plant.txt |
| Lint totals and file inventory | Dynamic | Measured working-tree snapshot; temporary test files can change totals |
| Conversion inventory | Static source analysis plus edits | Original locations and snippets retained in JSON |
| Statistical/clinical claims | None | No source identifiers, dates, or research results changed |

## Remaining blockers

The literal requested exact-pattern zero-hit finish condition is impossible as written; it raises a compile error. The separately labelled extension proves the silent-zero failure instead. Unsafe regression plants are deliberately retained, so whole-tree lint refuses until the owner decides how to archive them outside scanned shell files. No historical findings were fabricated to meet an expected positive baseline count.
