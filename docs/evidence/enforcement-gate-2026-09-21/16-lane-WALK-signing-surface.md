# WALK report

Completed the requested presenter, both CLI guarantees, the standalone chain-integrity check, and tests. No commit or push. No signature, state, basis, batch ID, or D01 notice was written into the real ledger or a saved copy of it. Synthetic signing tests use a fictional `synthetic-ledger.json`; tests involving clinical notices only read files or mutate unsigned data in RAM.

Baseline HEAD remains `9ff4c6b07275b737aafb198cdab85ad3fae8058c`. This checkout is detached at the supplied commit, rather than having a local branch name. No Pages build or release promotion was performed; no built pages required restoration.

## CLI behavior, with code evidence

The supplied premise about first-match signing was not true of the checked-out CLI. At baseline `9ff4c6b0`, `scripts/countersign_result_change.py:37` says `if len(hits) != 1:`, line 38 exits with `sys.exit(f"{len(hits)} notices match {slug} / {outcome_sub!r}; name one")`, and line 39 returns `hits[0]` only after that uniqueness check. It selected neither the first nor the last of multiple matches: it refused them. This refusal is preserved and its diagnostic now points to the exact selector: `scripts/countersign_result_change.py:48` — `sys.exit(f"{len(hits)} notices match {slug} / {outcome_sub!r}; name one with --notice-index (zero-based)")`.

Both commands accept `--notice-index N`, where N is a **zero-based ledger array index**, alongside the existing slug and outcome positional arguments. The index must be in range and match those selectors. Evidence: `scripts/countersign_result_change.py:40` — `if not 0 <= notice_index < len(data["notices"]):`; `scripts/countersign_result_change.py:43` — `if n["slug"] != slug or outcome_sub.lower() not in n["outcome"].lower():`; `scripts/countersign_result_change.py:109` — `r.add_argument("--notice-index", type=int, help="exact zero-based index in the ledger; slug/outcome must also match")`; `scripts/countersign_result_change.py:115` — `g.add_argument("--notice-index", type=int, help="exact zero-based index in the ledger; slug/outcome must also match")`.

`sign --expect-digest SHA256` recomputes the canonical rendered block, then refuses before writing if the expected digest differs. Its error names both values. Evidence: `scripts/countersign_result_change.py:85` — `expected = getattr(args, "expect_digest", None)`; `scripts/countersign_result_change.py:86` — `if expected is not None and expected != sha:`; `scripts/countersign_result_change.py:87` — `sys.exit(f"refused: rendered digest mismatch; expected {expected}; actual {sha}; nothing written")`. The file write remains later at `scripts/countersign_result_change.py:99` — `json.dump(data, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)`. Omitting the flag leaves the existing signing behavior intact; this is an opt-in guard, and the walker always includes it.

Tests exercise both commands on each notice in all six duplicate outcome pairs. Legacy substring selection refuses; the exact selector renders the intended digest. Real-ledger sign probes deliberately use a wrong digest and additionally forbid opening that file for writing. Successful signing and legacy-default compatibility are tested only with fictional notices.

## Walker behavior and provenance

Start at the first audited notice:

```powershell
python scripts/sign_walk.py
```

Explicitly choose another audited notice, a fixed queue position, or the pending decision:

```powershell
python scripts/sign_walk.py --notice N20
python scripts/sign_walk.py --position 19
python scripts/sign_walk.py --notice D01
```

Each invocation prints one selected notice and returns. It saves no cursor and performs no signing. An already signed selected notice stays selected and gets no new signing command. Evidence: `scripts/sign_walk.py:239` — `print(present(audit, notices, chains, mapping, position, args.show_group_reason))`; `scripts/sign_walk.py:209` — `lines.append("No signing command offered for an already signed notice.")`; `scripts/sign_walk.py:216` — `lines += [d01(), "STOP. No signature or progress state was written. Another notice requires another explicit invocation."]`.

The exact PowerShell command includes the selected ledger index and freshly recomputed digest. The basis is a `Read-Host` prompt for Mahmood's own account of what he read, rather than a fabricated assertion that he read it: `scripts/sign_walk.py:214` — `+ f" --notice-index {index} --expect-digest {sha} --by 'Mahmood'"`; `scripts/sign_walk.py:215` — `+ " --basis (Read-Host 'Describe how this notice reached you and what you read')"]`.

The walker displays readable text extracted from the canonical HTML block. Its digest covers the canonical HTML, not the audit prose or terminal text. The implementation calls the same rendering helper used by the signing CLI: `scripts/sign_walk.py:145` — `_, block, sha = countersign._block_and_sha(notice)`; `scripts/countersign_result_change.py:65` — `html = page.result_change_block(_annotated(n))`. The historical `n41.json` page-evidence digest is not substituted for this live signing digest.

Recommendations are attributed explicitly: `scripts/sign_walk.py:183` — `lines += ["HARNESS-TEAM ADJUDICATION (recommendation, not Mahmood's decision): " + row["recommendation_reason"],`; `scripts/sign_walk.py:184` — `"HARNESS-TEAM RECOMMENDATION: " + row["recommendation"],`.

| Displayed field | Source and transformation |
| --- | --- |
| Audit ID and priority flag | `n41.json.notices[].audit_id`, `individual_review_required_by_lane`; preserve audit array order within the mandatory tier |
| Shared-reason grouping | `n41.json.decision_groups[]` order, `members`, `title`, `shared_sentence`, `batching_loss`; remaining audit rows retain their array order |
| Exact notice identity | Join audit and live ledger on `(slug, outcome, when_utc)`; require a unique match and matching raw notice fields |
| Before/after and departures/entrants | Live `docs/result_changes.json`: `before`, `after`, `left_pool`, `entered_pool` |
| Chain position and prior signatures | Full live ledger grouped by exact `(slug, outcome)`, ordered by timezone-aware `when_utc`; prior signer/time from `reviewer_countersignature` |
| Direction and scales | Audit `direction`, `direction_explanation`, `scale_before`, `scale_after`, `declared_estimand`, `null_value`; no new clinical interpretation |
| Mechanism | Audit `mechanism`, `mechanism_detail`; canonical rendered block also carries the live ledger's full `reason` |
| Per-notice adjudication and recommendation | Audit `recommendation_reason`, `recommendation`, `individual_review_triggers`, `additional_individual_review_reason`, `gate_requires_per_notice_signature` |
| Trial evidence and recovery | Audit `departing_trials[]`, `recovery_evidence[]`, and `specific_conflicts` where present; displayed IDs, families and candidate tuples checked against their held review JSON pointers |
| Signature digest | Recomputed by `scripts/countersign_result_change.py::_block_and_sha`, using `harness.page.result_change_block` and `harness.result_changes.rendered_sha256` |
| D01 wording | `LANE_PROMPT.md` build item 5; D01 is absent from `n41.json` and is not inserted into the ledger |

The audit-to-ledger join and source hashes refuse stale inputs before presenting a signing command: `scripts/sign_walk.py:82` — `raise ValueError(f"{row['audit_id']}: notice changed since n41.json; refresh audit")`; `scripts/sign_walk.py:101` — `raise ValueError(f"audit source changed: {relative}; refresh n41.json")`. New unaudited OPEN notices also refuse: `scripts/sign_walk.py:93` — `raise ValueError(f"ledger index {index}: OPEN notice has no adjudication in n41.json; refresh audit")`. Signature-only ledger changes are allowed so a later explicit invocation can display the recorded act. A rebuild that changes held review/HTML bytes requires an updated audit.

The order is derived by `scripts/sign_walk.py:30` — `def ordered_notices(audit: dict) -> list[dict]:`:

* Mandatory tier: 18 of 41 audited notices — N04, N05, N08, N09, N13, N17, N19, N20, N21, N23, N24, N26, N28, N29, N34, N36, N38, N40.
* Shared-reason tier: 17 of 41 audited notices — G1: N01, N07, N10, N11, N12, N14, N15, N16, N18, N25, N31, N33, N41; G2: N02, N03, N22, N35.
* Remainder: 6 of 41 audited notices — N06, N27, N30, N32, N37, N39.

The lane's mandatory-review priority is distinct from the gate's signature requirement: the supplied audit records 33 of 41 audited OPEN notices as requiring individual signatures. Grouping is for presentation only; no group signing command is generated. The shared argument appears at the first group member; an explicit `--show-group-reason` repeats it if entering elsewhere. No reading is assumed or recorded. Evidence: `scripts/sign_walk.py:176` — `if member_position == 1 or show_group_reason:`; `scripts/sign_walk.py:182` — `"No prior reading is assumed or recorded.")`.

D01 is visibly **NOT SIGNABLE**. The required order is: Mahmood rules, the RR correction is made, a notice is generated from the actual transition, then it becomes signable. There is no placeholder notice, digest or signing command for D01. Evidence: `scripts/sign_walk.py:129` — `return ("D01 (J-EMPHASIS-HF): NOT SIGNABLE. The RR correction is not in the ledger because the change "`; `scripts/sign_walk.py:227` — `if args.notice == "D01":`. The same D01 reminder appears after each actual notice.

Reading and deciding are Mahmood's acts. Signing is a separate command he runs himself. A script that renders and signs in one pass is a password wearing a convenience. This walker only presents.

## Static versus dynamic disclosure

| Material | Kind | Disclosure |
| --- | --- | --- |
| Tiering policy, one-invocation boundary, D01 pending-decision rule | Static policy | Required by the lane prompt |
| Directions, recommendations, grouping arguments | Supplied audit snapshot | Read from `n41.json`; these are harness-team recommendations, not new findings or Mahmood's approval |
| Clinical IDs, candidate values and before/after transitions | Source-backed data | Read from audit/ledger and checked against held review sources; no fabricated findings |
| Chain ordering, selection and rendering digest | Dynamic deterministic computation | Recomputed from current files |
| Fictional test estimates and signatures | Synthetic test input | Confined to synthetic fixtures; never saved as clinical data |
| Personal name in suggested command | Static lane role | Mahmood is the reviewer named by the prompt; `--basis` is supplied by him when he runs the separate command |

## Verification

Final bounded verification run: **61 passed, 3 deselected**. This comprises 40 new tests and 21 read-only existing notice tests; all 61 selected tests passed.

```powershell
python -B -m pytest -q -p no:cacheprovider tests/test_sign_walk.py tests/test_result_change_chain.py tests/test_countersign_result_change_cli.py tests/test_result_change_notice.py -k 'not ratchet_check_refuses_an_unnoticed_result_change_in_the_working_tree and not gate_holds_a_page_with_an_unsigned_notice and not page_carrying_a_notice_the_file_no_longer_has_is_held'
```

The three deselected existing tests create a temporary Git commit or write state/signatures into a temporary `docs/result_changes.json`. They were excluded to obey this lane's explicit prohibitions. No existing test code was changed.

The first walker run found two test-harness calls that accidentally consumed pytest's CLI arguments; changing those calls to `main([])` resolved them. There are no unresolved test failures. Verification loops were bounded to the initial run, its correction, and the final source-evidence check.

The source review resolved 78 of 78 audited departing trial-outcome memberships to their held source records, comparing trial IDs, family IDs, candidate tuples, absence codes and source excerpts. Ledger identity, dates and raw transitions are checked by `load_walk`; the duplicate-chain tests compare prior signature dates/names directly with live ledger records. Directions and adjudication remain attributed to the supplied audit rather than being re-adjudicated here.

No web sources, new study identifiers, scientific estimates, or study dates were introduced. No page build ran. `git diff --name-only -- docs` is empty; no built pages needed restoration. `git diff --check` passes. This is a local implementation result, not a SHIP/Overmind certification.

## Ledger integrity: every outcome group

The standalone `harness.result_changes.chain_integrity` function is not connected to a publication gate. It is called by the walker to avoid presenting a broken history. It sorts by parsed timezone-aware timestamps, rejects ties, and compares exact dictionaries. Evidence: `harness/result_changes.py:33` — `def chain_integrity(notices: list[dict[str, Any]]) -> list[dict[str, Any]]:`; `harness/result_changes.py:58` — `dated.sort()`; `harness/result_changes.py:62` — `if previous_time == current_time:`; `harness/result_changes.py:64` — `if notices[current].get("before") != notices[previous].get("after"):`.

Result: 48 of 48 distinct `(slug, outcome)` groups pass. There are six of six exact adjacent transitions in the six multi-notice groups; the remaining groups contain a single notice and have no adjacency to check. The six pairs are successive changes, not duplicate mistakes, as stipulated by the orchestrator. The table names the result for every group. Indices below are zero-based ledger array positions, in chronological order.

| Slug | Outcome | Ordered ledger indices | Integrity result |
| --- | --- | --- | --- |
| balanced-crystalloids-vs-saline-mortality | Mortality | 13 | PASS — singleton; no adjacent transition |
| colchicine-postop-af | Postoperative atrial fibrillation | 14 | PASS — singleton; no adjacent transition |
| colchicine-postop-af | Treatment discontinuation | 0 | PASS — singleton; no adjacent transition |
| colchicine-recurrent-pericarditis | Adverse events (gastrointestinal) | 1 | PASS — singleton; no adjacent transition |
| colchicine-secondary-cv-prevention | Gastrointestinal adverse effects | 16 | PASS — singleton; no adjacent transition |
| colchicine-secondary-cv-prevention | Non-cardiovascular death | 17 | PASS — singleton; no adjacent transition |
| colchicine-secondary-cv-prevention | Trial-defined major coronary/cardiovascular composite | 15 | PASS — singleton; no adjacent transition |
| corticosteroids-cap-mortality | Hyperglycaemia | 18 | PASS — singleton; no adjacent transition |
| corticosteroids-covid19-mortality | 28-day all-cause mortality | 19 | PASS — singleton; no adjacent transition |
| corticosteroids-covid19-mortality | Serious adverse events | 20 | PASS — singleton; no adjacent transition |
| dapagliflozin-hfpef-hosp | Adverse events | 21 | PASS — singleton; no adjacent transition |
| denosumab-vertebral-fracture | Hip fracture | 24 | PASS — singleton; no adjacent transition |
| denosumab-vertebral-fracture | New vertebral fracture | 22 | PASS — singleton; no adjacent transition |
| denosumab-vertebral-fracture | Nonvertebral fracture | 23 | PASS — singleton; no adjacent transition |
| doac-vte-recurrence | Any bleeding | 28 | PASS — singleton; no adjacent transition |
| doac-vte-recurrence | Major bleeding | 26 | PASS — singleton; no adjacent transition |
| doac-vte-recurrence | Major or clinically relevant nonmajor bleeding | 27 | PASS — singleton; no adjacent transition |
| doac-vte-recurrence | Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | 25 | PASS — singleton; no adjacent transition |
| dpp4-mace-t2d | 3-point major adverse cardiovascular events | 29 | PASS — singleton; no adjacent transition |
| dpp4-mace-t2d | Adverse events | 30 | PASS — singleton; no adjacent transition |
| dpp4-mace-t2d | Hospitalization for heart failure | 2 | PASS — singleton; no adjacent transition |
| dpp4-mace-t2d | Hypoglycemia | 31 | PASS — singleton; no adjacent transition |
| esketamine-trd-madrs | Adverse events | 33 | PASS — singleton; no adjacent transition |
| esketamine-trd-madrs | Observed-case Day-28 raw change-score MADRS MD | 3 → 32 | PASS — exact before/after continuity |
| glp1-ra-mace-t2d | 3-point major adverse cardiovascular events | 34 | PASS — singleton; no adjacent transition |
| iv-iron-hfref-hosp | Heart-failure hospitalization | 35 | PASS — singleton; no adjacent transition |
| metformin-pcos-ovulation | Ovulation with metformin added to clomifene | 36 | PASS — singleton; no adjacent transition |
| noac-vs-warfarin-af-stroke | Major bleeding | 4 | PASS — singleton; no adjacent transition |
| noac-vs-warfarin-af-stroke | Stroke or systemic embolism | 37 | PASS — singleton; no adjacent transition |
| omega3-cardiovascular-events | Atrial fibrillation | 39 | PASS — singleton; no adjacent transition |
| omega3-cardiovascular-events | Major vascular events / MACE | 5 → 38 | PASS — exact before/after continuity |
| pcsk9-mace | Injection-site reactions | 7 | PASS — singleton; no adjacent transition |
| pcsk9-mace | Major adverse cardiovascular events | 6 → 40 | PASS — exact before/after continuity |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | 8 → 41 | PASS — exact before/after continuity |
| probiotics-aad-prevention | Any adverse events | 9 → 42 | PASS — exact before/after continuity |
| probiotics-aad-prevention | Serious adverse events | 10 → 43 | PASS — exact before/after continuity |
| sacubitril-valsartan-hfref | Composite cardiovascular death or heart-failure hospitalization | 44 | PASS — singleton; no adjacent transition |
| semaglutide-obesity-mace | 3-point major adverse cardiovascular events | 45 | PASS — singleton; no adjacent transition |
| semaglutide-obesity-mace | Adverse events leading to permanent discontinuation | 46 | PASS — singleton; no adjacent transition |
| sglt2-primary-prevention-hf | Hospitalization for heart failure | 47 | PASS — singleton; no adjacent transition |
| sglt2-primary-prevention-hf | Lower-limb amputation | 48 | PASS — singleton; no adjacent transition |
| spironolactone-hfref-mortality | All-cause mortality | 49 | PASS — singleton; no adjacent transition |
| statins-primary-prevention-elderly | Major vascular events | 50 | PASS — singleton; no adjacent transition |
| ticagrelor-vs-clopidogrel-acs | Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke | 51 | PASS — singleton; no adjacent transition |
| ticagrelor-vs-clopidogrel-acs | Major bleeding | 52 | PASS — singleton; no adjacent transition |
| tocilizumab-covid19-mortality | 28-day all-cause mortality | 53 | PASS — singleton; no adjacent transition |
| tocilizumab-covid19-mortality | Serious adverse events | 11 | PASS — singleton; no adjacent transition |
| tranexamic-acid-pph | Thromboembolic events | 12 | PASS — singleton; no adjacent transition |

## Protected bytes and packaging

Ledger SHA-256 before and after: `8b7313114c2c548b0703b0eed35cb2ce574223854f53b73defca5252c8184e4e`; equals `n41.json.source_sha256`.
Audit SHA-256: `6f38447a1d61170874b4302ba9cbe8ef2143ecdaed103f1b0b059062b21dd160`.
The original inventory supplied by the prompt remains unchanged: 13 signed and 41 OPEN, with 54 total ledger notices. No signature was executed on any real notice.

`WALK.patch` combines `git diff --binary HEAD -- harness/result_changes.py scripts/countersign_result_change.py` with `git diff --no-index --binary -- /dev/null PATH` for the new walker, three test files and this report. This includes new files without staging anything. The provided `n41.json`, `LANE_PROMPT.md`, and running `lane.log` are pre-existing untracked lane inputs and are not bundled into the patch. Keep `n41.json` with the patched checkout. `PROGRESS.md` is an ignored recovery savepoint.

One procedural deviation occurred before I could read the lane instructions: I sent Ctrl+C to my own oversized session-context read command to stop its output. I learned the no-process-signal rule from the subsequent `LANE_PROMPT.md` read and sent no further stop, kill or signal actions. No other process was targeted.

Final `git status --short` follows. Apart from the supplied untracked inputs/log and required report/patch, the change surface is source and tests only; there are no changed files under `docs/`.

```text
M harness/result_changes.py
 M scripts/countersign_result_change.py
?? LANE_PROMPT.md
?? WALK.patch
?? WALK_REPORT.md
?? lane.log
?? n41.json
?? scripts/sign_walk.py
?? tests/test_countersign_result_change_cli.py
?? tests/test_result_change_chain.py
?? tests/test_sign_walk.py
```
