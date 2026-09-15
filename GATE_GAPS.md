# What wrong page could this system still emit? - gate-by-gate adversary map

Audit question: could this system emit an indefensible scientific statement without a gate
preventing it or visibly qualifying it? Every item below names the file/function or evidence file
that supports the claim.

## Prior map recheck

| prior item | verdict | code/evidence checked | residual gap |
|---|---|---|---|
| 1. Two-limb publication gate | STILL TRUE | `harness/gate.py:check_limb1`, `harness/gate.py:check_limb2`, `harness/census.py:verify` | Reproducibility and an OA comparator do not prove scientific correctness. A stable wrong extraction can still replay byte-for-byte if the wrong object is committed. |
| 2. Canonical claim object would not stop categorical or methodological contradictions | NO LONGER TRUE | changed by `c06b4716`; see `harness/proposition.py:contradictions`, `harness/census.py:build_review_dir`, `tests/test_proposition_gate.py` | The new proposition gate stops the five encoded contradiction families. It still will not stop a proposition family not represented in `harness/proposition.py`. |
| 3. Invalidation / STALE misses facts never committed | STILL TRUE | `harness/invalidation.py:assess`, `harness/page.py` STALE rendering, `docs/fix_ledger.json` stale progression | A missing external fact cannot poison the object unless a committed signal represents it. |
| 4. Compatibility key misses endpoint/comparator-scope problems not encoded upstream | STILL TRUE | `harness/compat.py:outcome_key`, `harness/compat.py:check`, `AUDIT_QUEUE.md` item 8 | `compat.check` hard-refuses effect-measure/event-process incompatibility, but comparator scope and some endpoint/timepoint/analysis-set mismatches still depend on upstream representation. |
| 5. Interval provenance cannot detect garbage-in point estimates | STILL TRUE | `harness/census.py:_interval_provenance_check`, `harness/gate.py:check_pooled_verified`, `harness/gate.py:check_method_matches_scale` | A CI provenance token proves route, not that every source digit was the right endpoint, arm, denominator, or timepoint. Method-string/scale mismatches are now checked, but coherent wrong inputs remain possible. |
| 6. Verify gate misses right-number-wrong-endpoint and false refusal reasons | STILL TRUE | `harness/gate.py:check_pooled_verified`, `harness/gate.py:check_access_claim_supported`, `tests/test_percentage_provenance.py`, `AUDIT_QUEUE.md` items 6-7 | Percentage-derived counts badged as verified were closed by `4de360ec`, and unsupported access claims are guarded by `check_access_claim_supported`; right digits on the wrong endpoint and false refusal reasons remain queued. |
| 7. Leak scan is limited to served aggregate JSON attribution | STILL TRUE | `harness/leakscan.py:scan`, `scripts/verify_all.py:limb_leak_scan` | The scan reads `docs/*.json` and attributed sub-objects. It does not prove every possible surface, slug spelling, or unattributed derivative is clean. |
| 8. Percentage-provenance can miss a plausible but wrong denominator | STILL TRUE | `tests/test_percentage_provenance.py`, `harness/gate.py:check_pooled_verified` | The exact percentage-to-count case is guarded, but a wrong outcome-specific denominator that appears in a source can still pass a digit-presence check. |
| 9. RoB coverage does not prove RoB judgement correctness | STILL TRUE | `tests/test_rob_coverage.py`, `harness/grade.py:_rob_domain` | Coverage only proves every pooled trial has an assessment signal. It does not prove the human/judgement labels are correct. |
| 10. Prevention screening does not cover every population modelling defect | STILL TRUE | `harness/gate.py:check_population_identity`, `a1193b9b`, `AUDIT_QUEUE.md` prevention note | A pooled record matching configured `population_none` is refused, but missing or under-specified population terms remain a modelling problem. |

## Prior queue recheck

| prior queue item | verdict | code/evidence checked | residual gap |
|---|---|---|---|
| Categorical + methodological contradictions as an unbuilt seventh gate | NO LONGER TRUE | changed by `c06b4716`; `harness/proposition.py:contradictions`; `tests/test_proposition_gate.py` | Closed for the encoded families only. |
| `DECLARED_ABSENT` split four ways | NO LONGER TRUE | changed by `fb75635b`; `harness/absence.py:classify`; `harness/page.py:_absent_label`; `tests/test_absence_ontology.py` | Classifier accuracy still depends on retrieved source text and outcome keywords. |
| `NOT_ASSESSED` not equal to `NOT_DOWNGRADED` across GRADE domains | NO LONGER TRUE | changed by `445a2ba6`; `harness/grade.py:grade`; `tests/test_grade_unassessed.py` | Wrong assessed-domain judgement remains possible. |
| `Claims checked: 0` as a failing state | NO LONGER TRUE | changed by `f64ee43b` and protected by `5436fe93`; `harness/page.py` claim-check rendering; `harness/invalidation.py`; `tests/test_honest_states_renderable.py` | A page with no checkable pooled claim is visibly limited; the gate still cannot invent a source-backed result. |
| False refusal reasons | STILL TRUE | `AUDIT_QUEUE.md` item 6; `harness/gate.py:check_access_claim_supported` | Unsupported access claims are guarded, but general refusal-reason source-truth remains queued. |
| Extraction hierarchy: published effect beats reconstruction | STILL TRUE | `AUDIT_QUEUE.md` item 7; `harness/pipeline.py` verified-effect and verified-arm override paths | Flagged overrides exist, but the general hierarchy sweep is still queued. |
| Overrides that manufacture an unverified absence/reason | STILL TRUE | `harness/pipeline.py` absent/verified override paths; `tests/test_verified_override.py`; `tests/test_stage_additions.py`; `AUDIT_QUEUE.md` item 6 | Flag-gating is tested; source-truth of override reasons is not generally proven. |
| Trial-to-source-documents object | STILL TRUE | `AUDIT_QUEUE.md` item 2 | No shared source-document object yet spans outcome, funding, RoB, registry, and harms. |
| Randomised-contrast check silently passing an unidentified pooled trial | NO LONGER TRUE | changed by `1b47f58e`; `harness/compat.py:outcome_key`; `docs/fix_ledger.json` architecture gate 5 entry | Unverified contrast is visible; unresolved identifiers can still limit verification. |
| Trial-family / randomised-comparison uniqueness | STILL TRUE | `AUDIT_QUEUE.md` item 1; `harness/gate.py:check_duplicate_publication` | Same-NCT duplicates are refused, but missing/unresolved identifiers remain open. |
| ITT-as-randomised / analysed-N-vs-randomised-N mislabel | STILL TRUE | `harness/extract.py` subgroup and population/analysis-set guards; `docs/definition_audit.json` | Per-protocol/completers effects are guarded, but analysed-vs-randomised denominator provenance is not a standalone gate. |
| Wrong point estimate from wrong per-arm inputs | STILL TRUE | `harness/gate.py:check_pooled_verified`; `harness/census.py:_interval_provenance_check` | Digit presence and CI route do not prove arm/denominator/endpoint binding. |
| `union(displayed queries) == screened set` | STILL TRUE | partially closed by `harness/acquisition.py` ledger and `docs/evidence/legacy-ledgers-2026-09-14/README.md`; see `AUDIT_QUEUE.md` item 3 | Future ledgered snapshots can prove `found_by`; legacy snapshots explicitly cannot recover historical query attribution. |
| Comparator matcher rebuilt on one key | STILL TRUE | `AUDIT_QUEUE.md` item 8; `tests/test_external_agreement_estimand.py` | Estimand matching is tested, but the full comparator axis key remains queued. |
| Systematic-search recall | STILL TRUE | `harness/heldout.py:measurement_current`; `docs/search_recall_regression_corpus.json`; `docs/evidence/search-acquisition-2026-09-14/README.md` | Regression-corpus recall is measured and held-out leakage is guarded; recall itself remains the weakest layer. |

## Gates that exist today, and what each would not stop

<!-- gate-gaps:generated:start -->

The rows below are generated from `registry/gate_gaps.json`; freshness is computed from each row's seal.

### Repository, deployment, and audit-state gates

| gate | what it stops | what it would NOT stop | freshness | source |
|---|---|---|---|---|
| Deploy conditional on verify | A red `verify` SHA reaching Pages through the workflow deploy path. | A repository admin changing Pages back to branch builds, or a green build that is scientifically wrong. | CURRENT | `.github/workflows/verify.yml` deploy job `needs: verify`; `docs/evidence/gate-authority-2026-09-14/README.md`; `docs/evidence/gate-authority-2026-09-14/03-refusal-plant-failing-test-not-deployed.txt` |
| Production-record chain | Deploying an artifact that differs from the manifest built by `verify`; serving bytes that do not match the verified per-file digests. | A verified digest of a wrong page; mutable external APIs changing before the next retrieval snapshot; an admin bypassing the whole GitHub Pages path. | STALE: `scripts/production_record.py` | `scripts/production_record.py:cmd_manifest`, `cmd_check_artifact`, `cmd_attest`; `tests/test_production_record.py`; `docs/evidence/artifact-identity-2026-09-14/04-postfix-first-chained-deploy.txt` |
| Server-side ruleset | A non-admin push to `main` before required status check `verify` has passed on that SHA; force-push and branch deletion. | A repository admin editing or deleting the ruleset. | CURRENT | `docs/evidence/gate-authority-2026-09-14/05-ruleset-created.txt`; `docs/evidence/gate-authority-2026-09-14/06-refusal-server-rejects-direct-push.txt` |
| One-standard verifier | Local hook and CI using different standards; early-exit hiding other failed limbs. | A hook/CI difference caused by partially staged changes; any defect outside the eight limbs. CI is the authority. | STALE: `scripts/verify_all.py` | `scripts/verify_all.py:LIMBS`; `.github/workflows/verify.yml`; `docs/evidence/gate-authority-2026-09-14/09-new-standard-refuses-index-and-test-plants.txt`; `docs/evidence/gate-authority-2026-09-14/README.md` |
| Held-out leak detector | A sealed held-out identifier landing in tracked text or first-parent commit messages after enforcement; an acquisition-engine edit landing without a current regression-corpus measurement. | Out-of-band disclosure; identifiers not sealed; anyone with the key/register knowing the names; recovery of low-entropy names by the key-holder. | STALE: `harness/heldout.py` | `harness/heldout.py:check`, `scan_tree`, `scan_commit_messages`, `measurement_current`; `registry/heldout_sealed.json`; `docs/evidence/independent-verification-2026-09-14/07-heldout-leak-detector.txt` |
| Fix-state object transition checker | Status edits in `registry/fixes.json` that skip a step, lack matching history, downgrade without a reason, land without an existing commit, verify with author/self-created evidence, or generalize back onto authored-against surfaces. | Truthfulness of the evidence content; a plausible but wrong reason written into the object; commit messages (they carry no fix-state authority); commits before the object store existed; admin history rewrites. An independent reviewer can check the cited evidence against each object transition. | STALE: `harness/fixstate.py`, `registry/fixes.json`, `scripts/render_fix_ledger.py` | `harness/fixstate.py:check`, `validate_store`, `check_transitions`; `registry/fixes.json`; `scripts/render_fix_ledger.py`; `docs/evidence/independent-verification-2026-09-14/08-fix-state-ladder.txt`; `docs/evidence/independent-verification-2-2026-09-14/01-fix-state-object-transitions.txt` |
| Honest-state ratchet | Removing already-served warning/state markers from `docs/index.html` or review pages. State: PARTIALLY VERIFIED AGAINST DECLARED SENTINELS. | A wrong warning that remains visible; adding noise; a new untracked surface outside the scanned pages. | STALE: `harness/honest_ratchet.py` | `harness/honest_ratchet.py:MARKERS`, `compare`, `check`; `docs/evidence/independent-verification-2026-09-14/09-honest-state-ratchet.txt` |
| Block-level honest-state ratchet | Removing an already-served `absent` or `banner` block even when phrase counts stay unchanged; 15 pre-fix lost blocks passed the phrase ratchet and are now named by block SHA and prefix. | Softening inside an unchanged block set; a semantically weaker replacement that keeps a reviewed acknowledgement; untracked surfaces outside the scanned pages. | STALE: `harness/honest_ratchet.py`, `tests/test_honest_ratchet.py` | `harness/honest_ratchet.py:blocks`, `compare_blocks`; `tests/test_honest_ratchet.py`; `docs/evidence/ratchet-blocks-2026-09-14/01-prefix-phrase-ratchet-missed-15-blocks.txt` |
| Ratchet acknowledgement mechanism | Treating a lost `absent`/`banner` block as reviewed only when `docs/ratchet_acknowledgements.json` names the page, lost SHA, text prefix, replacement SHA, reason, time, and reviewer. | An acknowledgement can be written wrongly by the integrator; an independent reviewer or auditor can check the lost text prefix, replacement block SHA, and reason against the cited evidence directory. | STALE: `docs/ratchet_acknowledgements.json`, `harness/honest_ratchet.py` | `docs/ratchet_acknowledgements.json`; `harness/honest_ratchet.py:_valid_ack`; `docs/evidence/ratchet-blocks-2026-09-14/README.md` |
| Gate scorecard | Missing registry entries for enumerated gates, stale served `docs/gate_scorecard.json`, missing evidence paths, placeholder dates, and false precision counts. | A gate omitted from the enumerator/static list; truthfulness of cited evidence content; a production control that is green in tests but never adjudicated on a real refusal. Implementation reviewers can check enumerator coverage, and auditors can sample the cited evidence. | STALE: `docs/gate_scorecard.json`, `harness/gate_scorecard.py`, `registry/gate_scorecard.json`, +1 more | `harness/gate_scorecard.py`; `registry/gate_scorecard.json`; `docs/gate_scorecard.json`; `tests/test_gate_scorecard.py`; `docs/evidence/independent-verification-2-2026-09-14/02-gate-scorecard.txt` |
| Architecture identity | Treating changed code, workflow, hooks, topic/protocol/registry config, dependencies, retrieval adapters, model stages, or deploy path as the same architecture. | Making mutable dependencies or live APIs immutable; proving scientific correctness of an architecture. | STALE: `harness/architecture_identity.py` | `harness/architecture_identity.py:components`, `identity`, `mutable_dependencies`; `tests/test_architecture_identity.py`; `docs/evidence/independent-verification-2026-09-14/04-artifact-identity.txt` |
| Target assertion | A check running without printing the HEAD/base/tree/file-or-URL set it inspected, or silently falling back when a named ref/file set cannot be resolved. | A check pointed at the right commit but reading a stale derived file; a target line that is printed but not compared against what the caller intended. The line makes the target auditable, not automatically correct. | STALE: `harness/honest_ratchet.py`, `scripts/verify_all.py` | harness/target.py; scripts/verify_all.py; harness/honest_ratchet.py; docs/evidence/target-assertion-2026-09-14/README.md |

### The eight `verify_all.py` limbs

| gate | what it stops | what it would NOT stop | freshness | source |
|---|---|---|---|---|
| Unit tests | Known tested regressions in `tests/`. | Untested behavior and source-level scientific errors. | STALE: `scripts/verify_all.py` | `scripts/verify_all.py:limb_unit_tests` |
| Offline reproduction | Review pages that no longer replay from committed cache/protocol. | Deterministic wrong extraction. | STALE: `scripts/verify_all.py` | `scripts/verify_all.py:limb_reproduction`; `scripts/reproduce_review.py` |
| Publication gate on every live page | Any current review page failing `harness.gate.gate_page`. | Gaps outside the 20 page checks listed below. | STALE: `harness/gate.py`, `scripts/verify_all.py` | `scripts/verify_all.py:limb_gate_every_page`; `harness/gate.py:gate_page` |
| Index currency | Hand-edited or stale `docs/index.html`. | A generated index built from wrong underlying objects. | STALE: `harness/index.py`, `scripts/verify_all.py` | `scripts/verify_all.py:limb_index_currency`; `harness/index.py:build_index` |
| Served-artefact leak scan | Suppressed/refused topic pooled statistics leaking into `docs/*.json`. | Unattributed leaks, slug spelling misses, or non-JSON surfaces. | STALE: `harness/leakscan.py`, `scripts/verify_all.py` | `scripts/verify_all.py:limb_leak_scan`; `harness/leakscan.py:scan` |
| Held-out detector | See held-out gate above. | See held-out gate above. | STALE: `harness/heldout.py`, `scripts/verify_all.py` | `scripts/verify_all.py:limb_heldout`; `harness/heldout.py:check` |
| Fix-state discipline | See fix-state gate above. | See fix-state gate above. | STALE: `harness/fixstate.py`, `scripts/verify_all.py` | `scripts/verify_all.py:limb_fixstate`; `harness/fixstate.py:check` |
| Honest-state ratchet | See honest-state ratchet above. | See honest-state ratchet above. | STALE: `harness/honest_ratchet.py`, `scripts/verify_all.py` | `scripts/verify_all.py:limb_honest_ratchet`; `harness/honest_ratchet.py:check` |

### Build-time object gates

| gate | what it stops | what it would NOT stop | freshness | source |
|---|---|---|---|---|
| Reproduction census Level A | Non-deterministic render, review hash drift, hand-edited HTML, manifest/page hash mismatch. | Wrong but deterministic review objects. | CURRENT | `harness/census.py:build_review_dir`, `harness/census.py:verify` |
| Reproduction census Level B | Pipeline replay from committed cache/config not matching the committed review core. | A committed cache that is complete-but-wrong, or source facts absent from the cache. | STALE: `harness/gate.py`, `harness/pipeline.py` | `harness/gate.py:check_reproduction`; `harness/pipeline.py:build_review_core` |
| Canonical claim object | Significance/null-crossing wording contradicting the canonical result claim. | A wrong canonical result object; non-significance propositions not encoded elsewhere. | CURRENT | `harness/census.py:_claim_check`; `harness/claim.py` |
| Proposition gate | Encoded membership/methodological contradictions: pooled-and-declared-absent, suppressed-and-pooled, eligible-and-excluded, current-while-invalidated, unsupported preregistration precedence. | Any proposition family not represented in `harness/proposition.py`. | CURRENT | `harness/proposition.py:contradictions`; `tests/test_proposition_gate.py` |
| Compatibility key backstop | Pooled outcomes with incompatible effect-measure/event-process classes. | Comparator scope mismatch, and endpoint/timepoint/analysis-set mismatch if upstream objects do not encode and suppress it. | CURRENT | `harness/compat.py:outcome_key`, `harness/compat.py:check` |
| Interval-provenance gate | A rendered CI without the canonical engine token or a valid k=1 source-reported token. | Wrong point estimate or CI produced by the engine from wrong source inputs. | STALE: `harness/synth.py` | `harness/census.py:_interval_provenance_check`; `harness/synth.py:CI_PROVENANCE` |
| Retrieval ledger and run states | Folded adapter errors, silent top-N truncation, missing per-record `found_by`, and confusing an error/not-run state with zero hits. | A bad but successfully run query; legacy snapshots knowing which historical query found each record. | CURRENT | `harness/acquisition.py` module contract, `validate`, `refresh`; `tests/test_acquisition.py`; `docs/evidence/search-acquisition-2026-09-14/README.md` |
| Structural query classifier + third state | The old hedge where the object did not state known-item vs title-seeded vs concept retrieval, and the title-anchored assumption that misclassified four free-text keyword topics before `HAND_WRITTEN_KEYWORD_SEARCH` existed. | Completeness of known-item, title-seeded, or hand-written keyword retrieval; a free-text query tuned toward known results; recall, relevance, or intent. A search reviewer can inspect the committed query strings and the held-out recall evidence. | STALE: `harness/page.py`, `harness/pipeline.py` | `harness/pipeline.py:classify_query`, `classify_retrieval`; `harness/page.py:_retrieval_class_html`; `tests/test_retrieval_class.py`; `tests/test_honest_states_renderable.py`; `docs/evidence/query-structure-2026-09-14/README.md` |
| Absence-state ontology | Certifying "declared absent" when the source reports the outcome number, only the abstract was retrieved, or the number was found and refused. | A classifier miss when the relevant source text was never retrieved or the keywords miss the outcome sentence. | STALE: `harness/page.py` | `harness/absence.py:classify`; `harness/page.py:_absent_label`; `tests/test_absence_ontology.py` |
| GRADE unassessed-domain cap | Rendering unassessed domains as favorable/no-downgrade or allowing unassessed domains to support HIGH certainty. | Wrong assessed-domain judgement; domains that require human judgement still need a human. | CURRENT | `harness/grade.py:grade`; `tests/test_grade_unassessed.py` |
| `identifier_scope` | Agent-named identifier over a class-level included intervention pool, and unresolved included intervention terms absent from the declaration. | Population and outcome axes of the identifier are unchecked; class-level identifier over a single-agent pool is not flagged; declaration is authored by the same people who wrote the slug. | STALE: `harness/invalidation.py` | `harness/invalidation.py:identifier_scope`; `docs/evidence/identifier-scope-2026-09-14/README.md` |

### The 20 `harness/gate.py` page checks

| gate | what it stops | what it would NOT stop | freshness | source |
|---|---|---|---|---|
| `check_limb1` | Missing required manifest fields, declared/served method mismatch, hand-made marker, bad or missing reproduction census, live census failure. | A wrong review object that reproduces and carries valid hashes. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_cache_tracked` | A page whose `cache/<slug>/records.json` is not git-tracked. | A tracked cache that is incomplete or scientifically wrong. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_reproduction` | Offline replay that cannot execute or whose review core hash differs from the manifest. | Deterministic replay of wrong committed cache/config. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_primary_result` | Publishing a page whose primary outcome has no pooled result. | A present primary result with the wrong trials or endpoint. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_pooled_verified` | Pooling any trial whose digits are not verified/handchecked against the committed source span. | Digits present in source but bound to the wrong outcome, arm, denominator, timepoint, or estimand. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_manuscript_numbers` | Generated manuscript prose containing risky numerals not carried by the review object. | Numerals that are object-derived but scientifically wrong. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_fetch_complete` | Core source `RAN_ERROR` being treated as a complete search. | A `RAN_OK` query with poor recall, or auxiliary-source failure that still matters to a specific claim. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_access_claim_supported` | A full-text access/paywall claim when the PMC full-text adapter did not run. | An access claim after an adapter ran but the interpretation of access was wrong. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_parity_our_k` | Stored parity count out of sync with primary pooled k, or parity prose naming a pooled trial as excluded. | Comparator scope/estimand mismatch when the count happens to agree. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_no_double_counted_trial` | Same trial id pooled more than once within one outcome. | Same trial represented by different identifiers not linked upstream. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_pivotal_present` | Declared pivotal/landmark trials absent from committed cache. | Undeclared pivotal trials, or a bad `pivotal_trials` list. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_controls` | Positive controls not screened in, negative controls screened in, or missing control declarations. | Screening errors outside the declared controls. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_cross_source` | Abstract vs CT.gov direction flip on the same outcome family. | Same-direction magnitude, endpoint, or follow-up-window disagreement. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_retraction` | A retracted trial listed in the committed integrity block. | A retraction not present in the integrity snapshot. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_duplicate_publication` | Two pooled reports sharing one NCT in the same outcome. | Duplicate reports with missing/unresolved NCT links. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_prespecification_in_protocol` | A dose-selection override not documented by the protocol or amendment. | Other unregistered choices not represented as `dose_selection`. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_population_identity` | A pooled record matching the topic's configured `population_none`. | Missing or too-narrow exclusion terms; subtler population drift. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_method_matches_scale` | Per-outcome or manifest method string inconsistent with the pooled scale. | A consistently encoded scale that is the wrong scientific estimand. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_preregistration_not_build` | Prospective-registration claims citing a build commit. | False prospectivity if the evidence sits outside the tested git pattern. | STALE: `harness/gate.py` | harness/gate.py:gate_page |
| `check_limb2` | Missing OA comparator metadata, identifier, URL, overlap counts, or those values absent from the served page. | Scope-mismatched OA comparators and stale comparator estimates. | STALE: `harness/gate.py` | harness/gate.py:gate_page |

<!-- gate-gaps:generated:end -->
## Not a gate, an admin

These are admin-only controls. A gate cannot prevent a repository admin from changing them; the defensible
control is to read the settings and diff them against the evidence baseline.

| admin action | API read that reveals it | expected baseline / source |
|---|---|---|
| Flip Pages source back to branch builds | `GET /repos/mahmood726-cyber/meta-harness/pages` | `build_type` must remain `workflow`; see `docs/evidence/artifact-identity-2026-09-14/02-second-path-search.txt`. |
| Edit/delete ruleset or add bypass actors | `GET /repos/mahmood726-cyber/meta-harness/rulesets` | ruleset id `23314494`, `enforcement: active`, required check `verify`, `bypass_actors: []`; see `docs/evidence/gate-authority-2026-09-14/05-ruleset-created.txt`. |
| Rotate or remove the held-out detector secret | `GET /repos/mahmood726-cyber/meta-harness/actions/secrets/HELDOUT_KEY` or `GET /repos/mahmood726-cyber/meta-harness/actions/secrets` | Metadata can reveal presence and `updated_at`; the value is not readable. Workflow use is in `.github/workflows/verify.yml`, and fail-closed behavior is in `harness/heldout.py:load_key`. |
| Change `github-pages` environment policy | `GET /repos/mahmood726-cyber/meta-harness/environments/github-pages` and `GET /repos/mahmood726-cyber/meta-harness/environments/github-pages/deployment-branch-policies` | main-only branch policy after the `gh-pages` policy was removed; see `docs/evidence/artifact-identity-2026-09-14/02-second-path-search.txt` and `03-latent-paths-closed.txt`. |

## Queue retagged by VALUE / PROCESS / STATE

### VALUE failures

| item | status | source |
|---|---|---|
| Wrong point estimate from wrong arm/count/denominator even when digits are present in a source. | OPEN | `harness/gate.py:check_pooled_verified`; prior item 5 above |
| Right-number-wrong-endpoint. | OPEN | prior item 6 above; `AUDIT_QUEUE.md` items 7-8 |
| Randomised-comparison/trial-family identity can change k and therefore values if reports are unlinked. | PARTLY CLOSED, still OPEN for unresolved identifiers | `harness/gate.py:check_duplicate_publication`; `AUDIT_QUEUE.md` item 1 |

### PROCESS failures

| item | status | source |
|---|---|---|
| Extraction hierarchy: source-reported effect+CI should beat reconstruction. | OPEN | `AUDIT_QUEUE.md` item 7 |
| Search-set provenance closure: every screened record should join to retrieval source/query/timestamp. | PARTLY CLOSED; legacy snapshots remain `LEGACY_UNRECORDED` | `harness/acquisition.py` contract; `docs/evidence/legacy-ledgers-2026-09-14/README.md` |
| Comparator matcher rebuilt against one population/intervention/comparator/endpoint/effect/design/evidence-geometry/search-date key. | OPEN | `AUDIT_QUEUE.md` item 8 |
| Trial-to-available-source-documents object shared by outcome/funding/RoB/registry/harms. | OPEN | `AUDIT_QUEUE.md` item 2 |
| Unit-of-analysis for cluster/crossover and unresolved multi-report identity. | PARTLY CLOSED by duplicate-id and same-NCT checks, still OPEN where identifiers are absent | `harness/gate.py:check_no_double_counted_trial`; `harness/gate.py:check_duplicate_publication`; `docs/fix_ledger.json` audit 26 entry |

### STATE failures

| item | status | source |
|---|---|---|
| Categorical/methodological contradictions beyond numerical claim wording. | CLOSED for encoded families by `c06b4716`; OPEN for unencoded proposition families | `harness/proposition.py:contradictions`; `tests/test_proposition_gate.py` |
| `DECLARED_ABSENT` conflating no data, source not retrieved, extraction gap, and found-but-refused. | CLOSED for current ontology by `fb75635b` | `harness/absence.py:classify`; `tests/test_absence_ontology.py` |
| `NOT_ASSESSED` rendered or counted as favorable/no-downgrade. | CLOSED by `445a2ba6` | `harness/grade.py:grade`; `tests/test_grade_unassessed.py` |
| `Claims checked: 0` as neutral. | CLOSED as a visible failing state | `harness/page.py` claim-check rendering; `harness/invalidation.py` claims-checked-zero reason; `tests/test_honest_states_renderable.py` |
| False refusal reason. | OPEN | `AUDIT_QUEUE.md` item 6 |
| Retrieval class unstated or hedged. | CLOSED by `b8925e04`; legacy retrieval yield remains explicitly unknown where applicable | `harness/pipeline.py:classify_retrieval`; `docs/evidence/search-states-2026-09-14/README.md`; `docs/evidence/legacy-ledgers-2026-09-14/README.md` |
| Inconsistency not automatically assessable when directions conflict or I2 is high. | OPEN | `AUDIT_QUEUE.md` item 9 |
| Comparator "same question" claim when axes do not match. | OPEN | `AUDIT_QUEUE.md` item 8 |

## Refusal history

### Fired or re-demonstrated on today's gate work

| gate | observed firing | source |
|---|---|---|
| Deploy conditional on verify | Plant `a74b5c42` had failing unit tests; `verify` failed, `deploy` skipped, served hash unchanged. | `docs/evidence/gate-authority-2026-09-14/03-refusal-plant-failing-test-not-deployed.txt` |
| Ruleset | Hooks-free direct push to `main` was rejected with required status check `verify` expected. | `docs/evidence/gate-authority-2026-09-14/06-refusal-server-rejects-direct-push.txt` |
| One-standard verify | Hand-edited `docs/index.html` refused by index currency; staged failing test refused by unit-test limb. | `docs/evidence/gate-authority-2026-09-14/09-new-standard-refuses-index-and-test-plants.txt`; `docs/evidence/gate-authority-2026-09-14/11-postfix-ci-refuses-hand-edited-index.txt` |
| Production record | Synthetic manifest refused an unbound review page hash; synthetic artifact mismatch refused a one-byte page difference. The first real chained deploy then attested 238/238 files. | `tests/test_production_record.py`; `docs/evidence/artifact-identity-2026-09-14/04-postfix-first-chained-deploy.txt` |
| Held-out detector | Temp clone with sealed canary in a tracked file was refused without revealing the plaintext. | `docs/evidence/independent-verification-2026-09-14/07-heldout-leak-detector.txt` |
| Fix-state ladder | Object-store plants refuse skipped transitions, status edits without history, self-verification, same-commit evidence, and generalized overlap. | `tests/test_fixstate.py`; `docs/evidence/independent-verification-2026-09-14/08-fix-state-ladder.txt` |
| Honest-state ratchet | Temp working tree with one served STALE marker removed was refused. | `docs/evidence/independent-verification-2026-09-14/09-honest-state-ratchet.txt` |
| Retrieval ledger states | Pre-fix Europe PMC exception folded into `RAN_OK`; HEAD acquisition tests pass and `RAN_ERROR` is representable. | `docs/evidence/independent-verification-2026-09-14/10-acquisition-prefix-defect.txt`; `tests/test_acquisition.py` |
| Concept source as retrieval source | Pre-fix concept-query source plant failed; post-fix the concept source runs first as discovery-capable. | `docs/evidence/search-acquisition-2026-09-14/06-concept-source-plant-fires-prefix.txt`; `tests/test_acquisition.py:test_concept_query_is_a_source_on_every_fetch_and_enumeration_only_topics_discover` |
| Retrieval-class state | Served pages show 11 known-item and 21 title-seeded retrieval states, and zero old hedge hits across 32 pages. | `docs/evidence/independent-verification-2026-09-14/11-retrieval-states-served.txt`; `docs/evidence/search-states-2026-09-14/03-ratchet-and-states-on-regenerated-pages.txt` |

### Still plant-only or limitation-only

| gate | current validation state | source |
|---|---|---|
| Proposition gate | Plant tests prove each encoded contradiction fires; current corpus is contradiction-free. | `tests/test_proposition_gate.py` |
| Architecture identity | Tests prove deterministic identity and identity change on topic byte change; it is an identity digest, not a scientific correctness gate. | `tests/test_architecture_identity.py`; `harness/architecture_identity.py:mutable_dependencies` |
| Legacy retrieval ledgers | The 32 legacy pages expose `LEGACY_UNRECORDED`; this is an honest state, not recovered historical query provenance. | `docs/evidence/legacy-ledgers-2026-09-14/README.md` |

## Standing interpretation

A fix is not treated as done merely because code landed. The current evidence directories use the orthogonal
fix-state fields enforced by `harness/fixstate.py`, and the deployment record binds code, artifact, and served
bytes through `scripts/production_record.py`. The remaining defect map is therefore not "what might be wrong
in memory"; it is the set of wrong outputs not yet structurally refused or visibly qualified by the files
named above.
