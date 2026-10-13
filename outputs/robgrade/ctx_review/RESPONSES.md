# Responses to the recorded review of the contextual-answer rule

## Round 1 (13 Oct 2026): codex REVISE (7 findings), agy REVISE (8); blind, recorded (codex.json, agy.json)

Every finding is ACCEPTED: 14 in full and 1 in part. Each has a failing-first test (14 failed on the code reviewed,
then pass).

| # | finding | response | test |
|---|---|---|---|
| codex0 | a verbatim quote does not prove it supports the inference: a generic or empty rationale passes | ACCEPTED IN PART. An empty rationale, or one reasoning from what trials usually do ("usually", "typically", "standard practice", "most trials", ...), is not context: the answer stays NI. RESIDUAL, stated: whether a quote is RELEVANT is the readers' judgement. Two blind readers must agree (or the adjudicator decides), and the quote is always shown beside the answer, so a reader of the page can judge it too. | test_PLANT_r1_a_generic_or_empty_rationale_is_not_context |
| codex1, agy1 | the scorer checks only that provenance fields are non-empty | ACCEPTED. `verify_records` requires both readers' records (and the adjudicator's when it decided), each RAN_OK. The deciding reply(ies) must say this answer from this source, the stored quote must be verbatim in the source the RECORDED PROMPT showed under that id, and that source's sha256 must be among the call's input digests. | test_PLANT_r1_records_* (5) |
| codex2, agy6 | a deleted direct answer escapes comparison | ACCEPTED. Each domain's answer keys, the domain set, the trial and the outcome must equal v3.1's. | test_PLANT_r1_ctx_score_refuses_a_deleted_direct_answer |
| codex3, agy2 | a domain made INSUFFICIENT skips recomputation; the overall and most label fields are unchecked | ACCEPTED. INSUFFICIENT status must equal v3.1's; the whole NI label and the overall are recomputed and compared. | test_PLANT_r1_ctx_score_refuses_a_domain_made_insufficient, ..._an_edited_overall_or_label |
| codex4 | a stale record (made for another prompt) can be replayed | ACCEPTED. `fresh()`: a record is used only when its prompt sha256 equals the current prompt's; otherwise the question stays NI. | test_PLANT_r1_a_stale_record_is_not_replayed |
| codex5 | the freeze omits files the score depends on | ACCEPTED. Added scripts/rob2_calibrate.py, scripts/rob2_dual.py, robgrade/rob2_typed.py, robgrade/prompt_licence.py, robgrade/rob2_tab.py and tests/test_rob2_tab.py. | test_PLANT_r1_freeze_covers_the_pipeline |
| codex6, agy4 | the renderer reads the v3.1 objects, so contextual answers never reach the display | ACCEPTED. `rob2_tab.py --ctx` renders outputs/robgrade/rob2_ctx into tab_preview_ctx/. An end-to-end test shows the contextual note and quote in the HTML. | test_PLANT_the_contextual_preview_renders_the_contextual_objects |
| agy0 | the adjudicator can override two readers who agree on NI | ACCEPTED. Agreement (PY/PN or NI) is never adjudicated. In the pipeline, a "disagreement" is now two different verified answers. | test_PLANT_r1_readers_agreeing_on_ni_are_never_overridden |
| agy3 | no upper bound on quote length | ACCEPTED: over 300 characters is dropped (C3). | test_PLANT_r1_a_quote_over_300_characters_is_dropped |
| agy5 | an adjudicated NI is not recorded as the adjudicator's | ACCEPTED: decided_by = adjudicator. | test_PLANT_r1_an_adjudicated_ni_is_recorded_as_the_adjudicators |
| agy7 | a target the reader skipped is missing from verify's output | ACCEPTED: it is NI. | test_PLANT_r1_a_target_the_reader_skipped_is_ni |

Also re-checked after the fixes: the integration dry run (rob2_contextual.py with no records) reproduces every v3.1
object exactly.

## Round 2 (13 Oct 2026): codex REVISE (8), agy REVISE (8)

All 16 are answered: 15 ACCEPTED, 1 accepted in part. Each has a failing-first test (15 failed on the code reviewed,
then pass).

| # | finding | response | test |
|---|---|---|---|
| codex0 | records are not bound to the trial or outcome; `fresh()` trusts the run file's hash | ACCEPTED. Each record's prompt must name THIS trial and outcome. `fresh()` also re-derives the held record's own prompt sha256. | test_PLANT_r2_records_bind_trial_and_outcome, test_PLANT_r2_fresh_reads_the_records_own_prompt |
| codex1 | an adjudicated answer is accepted though the readers agreed | ACCEPTED. The readers' re-verified answers must differ before an adjudication counts. | test_PLANT_r2_adjudication_needs_a_real_disagreement |
| codex2 | recorded replies bypass verify() (an empty quote, an unchecked rationale, a substituted displayed quote) | ACCEPTED. The scorer puts every recorded reply through the SAME `contextual.verify` against the sources its own prompt showed. The stored context must equal the verified context(s) exactly. | test_PLANT_r2_records_are_re_verified_empty_quote_refused |
| codex3 | a memory-based or unlisted generic rationale passes | ACCEPTED. Memory and outside-knowledge markers are added, AND the rationale must refer to the quoted words (it shares a word of 5+ letters with the quote). The reader instructions now say so. RESIDUAL, stated: a model could still name a quoted word while reasoning from memory; two blind readers, re-verification, and the quote shown on the page are the remaining defences. | test_PLANT_r2_a_memory_rationale_is_not_context, test_PLANT_r2_a_rationale_must_refer_to_the_quoted_words |
| codex4 | a frozen file untracked at the anchor passes | ACCEPTED. Every frozen file must exist in the pre-registration commit (`git cat-file -e`). | test_PLANT_r2_freeze_files_must_exist_at_the_anchor |
| codex5, agy0 | two readers agreeing from different sources are falsely refused | ACCEPTED. Each reader is verified against its OWN cited source; both contexts are stored. | test_PLANT_r2_two_sources_verify_each_against_its_own |
| agy5 | reader 2's context is discarded | ACCEPTED. `context` holds both readers' quote, source, sha256 and rationale. | test_PLANT_r2_agreement_from_two_sources_keeps_both_contexts |
| codex6, agy3 | an adjudicated NI loses its audit trail | ACCEPTED. `contextual_audit` keeps every decision (NI included) with its decider, rationale and records; the answer stays the v3.1 NI. | test_PLANT_r2_an_adjudicated_ni_keeps_its_audit_and_the_ni_answer |
| codex7 | "contextual answers move a judgement only where NI was decisive" is false (a PY at 1.3 can raise D1) | ACCEPTED. CONTEXTUAL_POLICY section 3 is corrected: judgements may move in EITHER direction, in pairs that were not NI-driven too. | (policy text) |
| agy1 | a source keyed 'abstract' raises KeyError | ACCEPTED as hardening. Pipeline sources carry 'text'; sources rebuilt from a recorded prompt carry 'abstract'. verify() reads either. | test_PLANT_r2_an_abstract_source_keyed_abstract_is_read |
| agy2 | a contextual gatekeeper answer closes a branch, and the scorer refuses the resulting NA | ACCEPTED. The scorer allows NI -> NA exactly where a contextual answer in that domain closed the branch. | test_PLANT_r2_ctx_score_accepts_a_branch_closed_by_a_contextual_answer |
| agy4 | upstream and downstream NI questions are asked together | ACCEPTED IN PART. One prompt per trial is kept (cost and latency); `apply()` turns a contextual answer on a question the new answers no longer ask into NA, so a moot downstream answer never stands. | test_PLANT_r2_a_contextual_answer_on_a_question_no_longer_asked_is_na |
| agy6 | the overall label is silent about contextual answers | ACCEPTED. It names the domains with a contextual answer. | test_PLANT_r2_overall_label_discloses_contextual_answers |
| agy7 | the adjudicated verification path is untested | ACCEPTED. | test_PLANT_r2_an_authentic_adjudication_verifies |

Round-1 tests updated to the round-2 contract (not weakened):
- the record tests now use re-verifiable fixtures (grounded rationales, trial/outcome lines, both contexts), with the
  same refusals asserted;
- the stale-record test now supplies the held record's prompt hash;
- the normalisation test has a grounded rationale;
- the `verify_records` stubs accept keyword arguments.

## Round 3 (13 Oct 2026): codex REVISE (7); agy RAN_ERROR on both attempts (client status ERROR, recorded)

All 7 are answered: 5 ACCEPTED, 2 accepted in part. 9 failing-first tests (9 failed on the code reviewed, then pass).

| # | finding | response | test |
|---|---|---|---|
| codex0 | memory-based reasoning still passes (one shared word plus an incomplete blacklist) | ACCEPTED. A pre-registered RELEVANCE GATE: the quote must contain one of its signalling question's topic stems (contextual.QUESTION_TERMS; e.g. 5.1 needs plan / protocol / prespecified / registration), so a randomisation quote cannot carry an analysis-plan answer. Explicit memory markers are added ("training data", "my training", "I know"). | test_PLANT_r3_a_quote_must_be_about_the_question, test_PLANT_r3_explicit_memory_is_not_context |
| codex3 | the blacklist also rejects legitimate mechanism wording ("are known") | ACCEPTED IN PART. "is/are/as/well known" are removed from the blacklist; mechanism wording grounded in a relevant quote now passes. DECLINED in part: a rationale resting on GENERAL clinical knowledge, with no quoted context about the question (the reviewer's "patients with schizophrenia" example), stays NI. Mahmood's rule requires the context to be QUOTED. | test_PLANT_r3_mechanism_wording_is_not_mistaken_for_memory, test_PLANT_r3_general_knowledge_without_quoted_context_stays_ni |
| codex1 | a contextual answer can OPEN a branch (2.3 PY asks 2.4, 2.5); the scorer refuses the NA -> NI | ACCEPTED IN PART. The scorer allows NA -> NI exactly where a contextual answer in that domain opened the branch. The newly asked questions are NI, never guessed. A second contextual pass on newly opened questions is NOT part of the rule (stated in the policy). | test_PLANT_r3_ctx_score_accepts_a_branch_opened_by_a_contextual_answer |
| codex2 | the scorer does not bind records to the registered prompt, blindness, or what the adjudicator saw | ACCEPTED. Both readers' recorded prompts must be byte-identical (blind, same evidence) and begin with the registered reader instruction. The adjudicator's must begin with the registered adjudication instruction, and its "THE TWO READINGS" block must equal the two re-verified readings exactly. | test_PLANT_r3_reader_prompts_must_be_identical_and_registered, test_PLANT_r3_the_adjudicator_must_have_seen_the_cited_readings |
| codex4 | a second context can lack any source digest | ACCEPTED. Every deciding reply must cite a source whose sha256 its call recorded. | test_PLANT_r3_a_context_without_a_source_digest_is_refused |
| codex5 | stored rationales are not checked against the deciding replies | ACCEPTED. The stored context must equal the verified one in quote, source, sha256 AND rationale. Fixtures now carry the rationales. | test_PLANT_r3_a_tampered_rationale_is_refused |
| codex6 | the renderer shows only reader 1's quote | ACCEPTED. Every reader's quote is shown with its source. | test_PLANT_r3_every_readers_quote_is_shown_with_its_source |

Fixture changes (not weakened):
- record fixtures carry the registered prompt heads, and every source the prompt showed (both readers see the same
  prompt);
- the adjudicator fixture shows the two readings it decided between;
- stored contexts carry their rationales.

agy has now failed in rounds 3 (both attempts) after succeeding in rounds 1-2. Its round-1 and round-2 findings are
all answered above.

## Round 4 (13 Oct 2026): codex REVISE (6), agy REVISE (4)

Answered: 8 ACCEPTED, 1 accepted in part, 1 DECLINED with its basis. 8 failing-first tests (8 failed on the code
reviewed, then pass), plus 2 pins.

| # | finding | response | test |
|---|---|---|---|
| codex0 | the round-3 topic gate rejects the Handbook's OWN example (an experienced CTU, a regulatory trial) | ACCEPTED -- the round-3 gate was wrong. 1.1 and 1.2 also take trial-conduct stems (trials unit, CTU, regulator, coordinating centre, multicentre, sponsor, contract research). On general clinical knowledge without quoted context (the round-3 schizophrenia example), the round-3 decline stands: Mahmood's rule requires QUOTED context. | test_PLANT_r4_the_handbooks_own_ctu_example_is_context |
| codex1 | "a registered protocol" plus a rationale passes for 5.1 | DECLINED. Inferring a prespecified plan from a registered protocol and a published SAP is the contextual judgement Handbook 8.2.3 allows, with its rationale in the free text. Here it needs a relevant quote, a rationale referring to it, agreement of two blind readers, and the scorer's re-verification; the quote is shown on the page. That the inference holds remains the declared residual: a mechanical rule cannot decide it without forbidding what the Handbook permits. | test_r4_registered_protocol_context_is_a_readers_judgement (pin) |
| codex2 | a prefix check lets text be inserted after the instruction, or a question be reworded; the fixtures used placeholder question text | ACCEPTED. The scorer rebuilds each recorded prompt's head with the pipeline's own `prompt_head` from the trial, outcome, targets (and readings), and requires byte equality. The fixtures now build their prompts with `prompt_head`. | test_PLANT_r4_text_inserted_into_the_registered_prompt_is_refused, test_PLANT_r4_a_reworded_question_is_refused |
| codex3 | questions opened by a contextual answer are forced to NI without assessment | ACCEPTED. Up to 3 contextual passes: a newly asked NI question gets its own pass; a question decided in a pass is never re-asked. The scorer accepts a contextual answer on an OPENED question (NA in v3.1, asked now). | test_PLANT_r4_a_branch_opened_question_can_be_answered_contextually |
| codex4 | the decision audit is never reconciled with the answers | ACCEPTED. Every stored contextual answer must have a matching audit decision, and every PY/PN decision must stand in the answers (or on a branch since closed), with the same records. An NI decision must have left no contextual answer. Found while fixing: `apply()` REPLACED the incoming audit, so a second pass erased the first pass's decisions; it now extends it. | test_PLANT_r4_an_audit_contradicting_the_answers_is_refused |
| codex5 | NI_POLICY.md and reproducible_ai/model_source.py are not frozen | ACCEPTED: both added. | test_PLANT_r4_freeze_covers_ni_policy_and_the_record_store |
| agy0 | closing a branch would wrongly refuse a direct answer becoming NA | ACCEPTED IN PART: it does not arise. A direct answer on a closed branch STAYS as answered (normalisation only turns NI/None into NA, and that is judgement-neutral). The scorer accepts it, and a test pins it. | test_PLANT_r4_a_closed_branch_may_drop_a_direct_answer (pin) |
| agy1 | the live path decides re-calls from the run file, not `fresh()` | ACCEPTED. | (rob2_contextual._one_pass) |
| agy2 | a missing record raises TypeError instead of a refusal | ACCEPTED: refused, with the record id. | test_PLANT_r4_a_missing_record_is_refused_not_a_crash |
| agy3 | duplicate or extraneous records per role are not refused | ACCEPTED: exactly one record per role (codex, agy, plus the adjudicator when it decided). | test_PLANT_r4_extra_or_duplicate_records_are_refused |

## Round 5 (13 Oct 2026): agy ACCEPT (0 findings); codex REVISE (6)

Answered: 3 ACCEPTED, 1 accepted in part, 1 ACCEPTED reversing my own round-3 decline, 1 DECLINED (the standing
judgement question). 6 failing-first tests (6 failed on the code reviewed, then pass).

| # | finding | response | test |
|---|---|---|---|
| codex0 | the pinned "registered protocol -> 5.1 PY" expectation is unjustified | DECLINED, as in round 4. The test pins only that verify() does not MECHANICALLY forbid this context (its docstring now says so). Whether it supports 5.1 is the readers' judgement under Handbook 8.2.3, the declared residual. | test_r4_registered_protocol_context_is_a_readers_judgement |
| codex1 | the scorer rebuilds only the prompt head; evidence inside a record could be substituted | ACCEPTED, by a stronger design. The scorer REPLAYS the frozen pipeline (scripts/rob2_contextual.process, replay mode, no model call) from the v3.1 objects, the run manifest, the held records and the AUTHORITATIVE trial sources (scripts/rob2_dual.items). The scored objects must equal the regenerated ones exactly. A record whose prompt was not built from the real sources is not fresh there, so substituted evidence cannot reproduce. | test_PLANT_r5_scored_objects_must_be_what_the_pipeline_reproduces |
| codex4 | a decision can be selectively omitted (restore NI, delete its audit entry) | ACCEPTED. The same replay reproduces the omitted decision, so the scored object differs and is refused. Every held contextual record made after the pre-registration must also be referenced by the run manifest. | test_PLANT_r5_scored_objects_must_be_what_the_pipeline_reproduces, test_PLANT_r5_every_held_record_must_be_in_the_run_manifest |
| codex5 | a missing or failed reader is treated as a disagreement, so one reader plus the adjudicator decide | ACCEPTED. A missing or failed reader VOIDS the pass: no contextual answer, and no adjudication. | test_PLANT_r5_a_missing_reader_voids_the_pass |
| codex2 | "prior knowledge of this trial" still passes | ACCEPTED IN PART: added to the memory markers. RESIDUAL, stated again: lexical defences cannot catch every phrasing of memory. The remaining defences are two blind readers, the relevant-quote and rationale-refers-to-quote gates, the scorer's re-verification and replay, and the quote shown on the page. | test_PLANT_r5_prior_knowledge_of_the_trial_is_not_context |
| codex3 | the topic gate rejects quoted clinical context for 3.4, which the guidance endorses | ACCEPTED, REVERSING my round-3 decline. 3.3 and 3.4 ask whether missingness COULD or is LIKELY to depend on the outcome's true value, and the RoB 2 guidance asks the assessor to reason about the clinical setting there. So for 3.3/3.4 the topic gate is not applied: quoted clinical context with a rationale referring to it is context. Every other question still needs a quote about its own topic. The round-3 test is reversed accordingly. | test_PLANT_r5_missingness_questions_take_clinical_context, test_PLANT_r3_general_knowledge_without_quoted_context_stays_ni (reversed) |

## Round 6 (13 Oct 2026): agy ACCEPT (0 findings, second round running); codex REVISE (6)

Answered: 4 ACCEPTED, 1 accepted in part, 1 DECLINED (the standing judgement question). 6 failing-first tests (6
failed on the code reviewed, then pass).

| # | finding | response | test |
|---|---|---|---|
| codex0 | registered protocol -> 5.1 PY (third time) | DECLINED (rounds 4-5). verify() does not mechanically forbid it; the readers judge it under Handbook 8.2.3. Escalated with the residual, below. | (pin) |
| codex1 | a quoted omission plus an outside assertion ("according to an earlier article") passes | ACCEPTED IN PART: outside-source phrasings (an earlier / another / previous / separate article, paper, report, publication) are added to the MEMORY markers. The residual stands: no lexical check catches every phrasing. | test_PLANT_r6_an_earlier_article_is_not_context |
| codex2 | the lexical gates force NI on guidance-endorsed reasoning: awareness from the interventions themselves (2.1); "commonly" in a clinical mechanism (3.4) | ACCEPTED. SETTING-BASED questions (2.1, 2.2, 3.3, 3.4: the guidance reasons from the setting there) skip the topic gate and the USUAL ("what trials usually do") markers. The MEMORY markers still apply everywhere. "Commonly" stays not-context for a question about a trial's own conduct (e.g. 1.2). | test_PLANT_r6_awareness_from_the_interventions_themselves, test_PLANT_r6_mechanism_wording_with_commonly_at_3_4 |
| codex3 | records parked in an unexecuted later pass escape the manifest check, which tests reference, not use | ACCEPTED. The replay reports the records it actually READ (`consumed`), and runs are cut to the passes executed. Every held post-registration RAN_OK record must have been consumed. | test_PLANT_r6_every_post_registration_decision_record_must_be_consumed, test_PLANT_r6_process_drops_unexecuted_passes_and_reports_consumed |
| codex4 | records that decided NI may predate the pre-registration | ACCEPTED. Every CONSUMED record, NI-deciding ones included, must postdate it. | test_PLANT_r6_a_consumed_record_must_postdate_the_preregistration |
| codex5 | a normal retry leaves a failed attempt that the manifest check refuses | ACCEPTED. A RAN_ERROR attempt carries no decision: it is accounted for (reported in ctx_score.json), never refused. | test_PLANT_r6_every_post_registration_decision_record_must_be_consumed |

## Where the review ended
Six rounds, 60 findings: round 1 15, round 2 16, round 3 7, round 4 10, round 5 6, round 6 6. By reviewer: codex 40
(7 + 8 + 7 + 6 + 6 + 6), agy 20 (8 + 8 + 0 + 4 + 0 + 0). agy ACCEPTED rounds 5 and 6; it failed in round 3 on both
attempts (client ERROR, recorded).

Accepted with failing-first tests, including two reversals of my own earlier declines:
- round-3 codex3 / round-5 codex3: 3.3/3.4 take quoted clinical context;
- round-3 gate / round-4 codex0: the CTU example.

ONE question stays open, and it is a judgement, not a defect: codex holds, in every round from 2 on, that a
contextual PY/PN is accepted on a relevant quote, a rationale referring to it, two blind readers' agreement and
re-verification, without proof that the inference is right (e.g. a registered protocol -> 5.1 PY). This lane treats
that as the Handbook 8.2.3 judgement Mahmood signed for, and declares it as the residual. It is shown on the page with
every quote, so a reader can judge it.

The round-6 fixes were not themselves re-reviewed; they are covered by their tests and by the end-to-end check below.

## Amendment A2 review, round 7 (13 Oct 2026): codex REVISE (8); agy RAN_ERROR (recorded)

A2 was signed by Mahmood (via Dispatch, 13 Oct, outputs/robgrade/SIGNING_A2.md) as a DEFECT FIX. It is reviewed here
BEFORE it is applied. A finding that would change the pre-registered RULE is out of scope.

Answered: 6 ACCEPTED, 1 DECLINED as out of scope, 1 DECLINED (the standing question). 9 failing-first tests in
tests/test_rob2_amendment_a2.py: 7 failed on the reviewed code; 2 already passed for the wrong reason and are kept
as pins.

| # | finding | response | test |
|---|---|---|---|
| codex0 | any signed-looking entry could amend ANY frozen file, inputs included | ACCEPTED. Only the four A2 code files are AMENDABLE (contextual.py, rob2_contextual.py, rob2_ctx_score.py, rob2_dual.py). The rule text, the inputs (split, comparators, v3.1 objects, calibration) and the tests never are. Only the signer "Mahmood" counts. | test_PLANT_a2r_only_the_a2_code_files_can_be_declared, test_PLANT_a2r_only_mahmoods_signature_counts |
| codex1 | supersession could exempt a reader, or an id that is not held | ACCEPTED. A superseded record must be held, RAN_OK, an ADJUDICATOR record, and made before the amendment's declared applied_utc. | test_PLANT_a2r_a_superseded_record_must_be_a_held_earlier_adjudication |
| codex2 | an unreadable RAN_OK reply still became an all-NI reader and could create a disagreement | ACCEPTED. An unreadable reply (no single answer object) voids the pass, like a missing reader: no contextual answer, no adjudication. | test_PLANT_a2r_an_unreadable_reply_voids_the_pass_like_a_missing_reader, test_PLANT_a2r_two_answer_objects_are_ambiguous |
| codex4 | duplicate keys or duplicate question rows are resolved silently | ACCEPTED. A duplicate key makes an object ambiguous (rejected), and two rows for one question with different answers give NI (AMBIGUOUS_CONFLICTING_ROWS), in either order. | test_PLANT_a2r_duplicate_keys_are_ambiguous, test_PLANT_a2r_conflicting_rows_for_one_question_are_ni |
| codex6 | braces in surrounding prose break the first-brace/last-brace slice | ACCEPTED. The parser decodes every candidate object (json raw_decode at each '{'); exactly one distinct answer object is an answer, and two or more are ambiguous. | test_PLANT_a2r_braces_in_prose_do_not_hide_the_answer_object |
| codex7 | the re-run may need new READER calls, not only adjudications; the source-text test proves nothing | ACCEPTED. `preflight()` lists every call a live re-run would make, without making any: stale or missing readers, and adjudications where both readers are held (a stated lower bound). The re-run is preceded by this preflight, and its counts are reported. | test_PLANT_a2r_preflight_lists_every_call_the_rerun_would_make |
| codex3 | add 4.3 to the setting-based questions | DECLINED, OUT OF SCOPE. It would change the pre-registered RULE, and A2 is signed as a defect fix only. Recorded for a future amendment, Mahmood's call. | -- |
| codex5 | the registered-protocol judgement | DECLINED (standing; rounds 4-6). | -- |

## Amendment A2 review, round 8 (13 Oct 2026): codex REVISE (7); agy RAN_ERROR ("Individual quota reached", recorded)

Answered: 4 ACCEPTED, 1 ACCEPTED with a stated residual, 2 DECLINED as out of A2's signed scope. 5 failing-first
tests (5 failed on the reviewed code, then pass).

| # | finding | response | test |
|---|---|---|---|
| codex0 | any earlier adjudication could be declared superseded, a genuine one included | ACCEPTED. A superseded adjudication must be PROVEN defect-caused (`defect_caused`). Its recorded prompt must show one reader as the unread signature ({"answer": "NI", "rationale": null}) on every question it decided, and that reader's held record for the same trial and outcome must be unreadable to the OLD strict parser yet readable to the A2 parser. | test_PLANT_a2r8_supersession_must_be_proven_defect_caused |
| codex1 | an editable declaration with copied signature metadata could authorise any change to amendable code | ACCEPTED, with a residual. Each declaration carries the sha256 of exactly the reviewed change (the file's git diff from the pre-registration), recomputed by the scorer, so no change after review can be declared under it. RESIDUAL, stated: the signature is a record in the repository, not a cryptographic one; the commit history is the trust root. | test_PLANT_a2r8_declarations_are_bound_to_the_reviewed_patch |
| codex3 | after rejecting a duplicate-key envelope, the parser scanned inside it and could accept an embedded answer object | ACCEPTED. A malformed answer envelope (a duplicate key, answers not a list, a row not an object) makes the whole reply unreadable. Decoding resumes AFTER an envelope, never inside it. | test_PLANT_a2r8_a_malformed_envelope_makes_the_reply_ambiguous |
| codex4 | `{"answers": [42]}` was a readable all-NI reader | ACCEPTED: every row must be an object, or the reply is unreadable (and voids the pass). | test_PLANT_a2r8_a_row_that_is_not_an_object_makes_the_reply_unreadable |
| codex6 | closing a branch dropped that contextual decision's quotes | ACCEPTED for the DATA: the audit keeps each decision's contexts, and the NA answer on a closed branch carries the closed decision. RENDERING it is out of A2's scope (robgrade/rob2_tab.py is frozen and not amendable); it goes with the served-tab signing. | test_PLANT_a2r8_a_closed_branch_keeps_its_contextual_decision_visible |
| codex2 | "the original manuscript confirms..." still passes | DECLINED, out of scope: extending the memory markers changes the pre-registered RULE. The standing residual applies; recorded for a future amendment. | -- |
| codex5 | 4.3 / "commonly" | DECLINED, out of scope (as round 7): a rule change, recorded for a future amendment. | -- |

## Amendment A2 review, round 9 (13 Oct 2026): codex REVISE (7); agy RAN_ERROR (quota, reset 16 min later; recorded)

Answered: 3 ACCEPTED, 3 DECLINED as out of A2's signed scope, 1 DECLINED (standing). 4 failing-first tests (4
failed on the reviewed code, then pass).

| # | finding | response | test |
|---|---|---|---|
| codex0 | the declaration file is editable alongside the code; the claimed trust root (history) is never checked | ACCEPTED. Declarations are read from the COMMITTED HEAD, never from the working tree, and the amended file in use must equal its HEAD version. An amendment exists only once it has passed the hook into a commit. A2 is therefore committed BEFORE the re-run and the score. | test_PLANT_a2r9_declarations_are_read_from_the_committed_history |
| codex1 | "unreadable to the old parser" does not prove a defect-caused adjudication (a reader that gave no answer is unread under both); matching trial/outcome admits other passes | ACCEPTED. The reader record must be THE SAME PASS's reader call (its registered targets cover the adjudicated questions). Under A2 its re-verified reading must DIFFER from the unread signature: a reader that really gave no answer leaves the adjudication genuine. | test_PLANT_a2r9_a_genuinely_empty_reader_is_not_a_defect, test_PLANT_a2r9_the_reader_record_must_be_for_the_same_pass |
| codex2 | a syntactically broken outer answer envelope lets an embedded object through | ACCEPTED. Any `{"answers":` start that fails to decode makes the reply unreadable. | test_PLANT_a2r9_a_broken_outer_envelope_makes_the_reply_unreadable |
| codex3 | "according to the original manuscript" (memory markers) | DECLINED, out of scope (a RULE change). The residual is stated; recorded for a future amendment. | -- |
| codex4 | 4.3 setting-based | DECLINED, out of scope (a RULE change); recorded for a future amendment. | -- |
| codex6 | rendering closed-branch decisions | DECLINED, out of scope (robgrade/rob2_tab.py is frozen and not amendable). The data is kept (round 8); rendering goes with the served-tab signing. | -- |
| codex5 | the registered-protocol judgement | DECLINED (standing). | -- |

Recorded for Mahmood, as candidates for a future amendment to the RULE (not A2): extend the memory markers to
references to unseen sources; 4.3 as setting-based; "commonly" in mechanism wording; render closed-branch decisions.

## Amendment A2 review, round 10 (13 Oct 2026): codex REVISE (8); agy ACCEPT

Answered: 4 ACCEPTED, 1 DECLINED with the standing stated residual, 3 DECLINED as out of A2's signed scope. 4
failing-first tests, plus 1 corrected expectation (5 failed on the reviewed code, then all 30 A2 tests pass; 331 lane
tests pass). The stricter parser changes how 0 of the 155 held contextual replies read. Under the stricter criterion
all 11 superseded adjudications are still proven defect-caused (dry declaration).

| # | finding | response | test |
|---|---|---|---|
| codex1 | defect_caused compared whole dicts, so an NI with a rationale counted as "changed"; the r8 test expected True although its reader saw no sources | ACCEPTED. The comparison is now by ANSWER. A defect-caused adjudication needs the hidden reply's A2-verified answer to be PY/PN where the unread signature gave NI. The r8 expectation was WRONG: with no sources the PY verifies to NI, so the disagreement was genuine. It is corrected to False, and the defect case is tested with a reader whose source is in its prompt. | test_PLANT_a2r10_a_defect_needs_a_changed_ANSWER; corrected test_PLANT_a2r8_supersession_must_be_proven_defect_caused |
| codex2 | target inclusion does not identify the original reader call (time, evidence) | ACCEPTED. The reader record must also PREDATE the adjudication and carry the SAME evidence block the adjudicator was shown. | test_PLANT_a2r10_the_reader_must_predate_the_adjudication_and_share_its_evidence |
| codex3 | a broken envelope whose first key is not "answers" escapes the guard | ACCEPTED. Any `"answers":` key outside every well-formed envelope makes the reply unreadable, whatever key the envelope starts with. | test_PLANT_a2r10_a_broken_envelope_with_another_first_key_is_unreadable |
| codex7 | an unreadable adjudicator reply became an adjudicator-owned NI | ACCEPTED. An unreadable adjudicator reply decides nothing, and the question is NI as "no contextual answer agreed". The record is still read (consumed), but it is never cited as a decision. | test_PLANT_a2r10_an_unreadable_adjudicator_reply_decides_nothing |
| codex0 | a committed declaration does not authenticate approval | DECLINED, standing stated residual (round 8). The signature is a repository record, not a cryptographic one. Each declaration binds the exact reviewed patch (sha256), is read only from committed HEAD, and enters history only through the hook. The trust root is the commit history and Mahmood's relayed signature, which is recorded verbatim in SIGNING_A2.md. | -- |
| codex4 | unseen-source reliance (memory markers) | DECLINED, out of scope (a RULE change); recorded for a future amendment. | -- |
| codex5 | 4.3 setting-based | DECLINED, out of scope (a RULE change); recorded for a future amendment. | -- |
| codex6 | closed-branch decisions are not rendered; the round-8 test checks storage only | DECLINED, out of scope (robgrade/rob2_tab.py is frozen). Codex is right that the round-8 wording "visible" overstated it: the decision is KEPT IN THE DATA, not rendered. Rendering goes with the served-tab signing. | -- |

## Amendment A2 review, round 11 (13 Oct 2026): codex REVISE (7); agy ACCEPT

Answered: 2 ACCEPTED, 1 DECLINED with the standing stated residual, 1 DECLINED by design, 3 DECLINED as out of A2's
signed scope. 2 failing-first tests, plus 1 companion (2 failed on the reviewed code, then all 33 A2 tests pass; 334
lane tests pass). One round-10 fixture gained the prompt hash its run entry would really carry; its assertion is
unchanged. The changes alter the reading of 0 of 155 held replies, and the preflight is unchanged (7 adjudications).

| # | finding | response | test |
|---|---|---|---|
| codex0 | a superseded adjudication could be replaced by NI if the corrected readers still disagree and no new adjudication exists | ACCEPTED. A REPLAY that meets a disagreement with no adjudication attempt on THAT prompt (none at all, or only a superseded one of other readings) raises MissingAdjudication: the scorer cannot reproduce the pipeline and refuses. A recorded FAILED attempt on that prompt remains an honest NI. | test_PLANT_a2r11_a_replayed_disagreement_never_adjudicated_refuses, test_PLANT_a2r11_a_recorded_failed_adjudication_is_an_honest_NI |
| codex2 | an escaped key ("\u0061nswers") bypasses the broken-envelope guards | ACCEPTED. Keys are compared DECODED: any object key that decodes to "answers" counts, in the envelope-start check and in the outside-every-envelope check. A well-formed envelope written with the escaped key is still read. | test_PLANT_a2r11_an_escaped_answers_key_is_still_an_envelope |
| codex6 | an "answers": key mentioned in prose voids an otherwise unique reply | DECLINED, by design. A reply that carries an answers key outside every well-formed envelope is ambiguous, so it is read as unreadable, which voids the pass and leaves NI: the conservative default, never a manufactured answer. Measured impact: 0 of 155 held replies. | -- |
| codex1 | committed metadata self-authorises amendments | DECLINED, standing stated residual. The scorer is itself amendable code: anyone able to commit could also change this check, so no in-repository check can authenticate its own author. The trust root is the commit history, the hook, and Mahmood's relayed signature recorded in SIGNING_A2.md. Each declaration binds the exact reviewed patch. | -- |
| codex3 | unseen-source reliance | DECLINED, out of scope (a RULE change); recorded for a future amendment. | -- |
| codex4 | 4.3 setting-based | DECLINED, out of scope (a RULE change); recorded for a future amendment. | -- |
| codex5 | closed-branch rendering | DECLINED, out of scope (rob2_tab.py is frozen); stored, not rendered (round 10 wording). | -- |

## Amendment A2 review, round 12 (13 Oct 2026): codex REVISE (6); agy ACCEPT

Answered: 2 ACCEPTED, 1 DECLINED by design (repeated), 3 DECLINED as out of A2's signed scope or the standing residual.
2 failing-first tests (2 failed on the reviewed code, then all 35 A2 tests pass). The round-10 and round-11 fixtures
now state that their adjudicator records are held (the new contract); their assertions are unchanged. The parser
changes since round 9 alter the reading of 0 of 391 held replies (155 contextual; 236 dual, NI and reference).

| # | finding | response | test |
|---|---|---|---|
| codex0 | the MissingAdjudication guard trusted a manifest hash; an entry with no held record passed | ACCEPTED. The attempt must be a HELD record whose own recorded prompt is this prompt; a manifest hash alone, or a held record of another prompt, is no adjudication, and the replay refuses. The r11 failed-attempt case now holds its record. | test_PLANT_a2r12_a_manifest_hash_without_a_held_attempt_is_no_adjudication |
| codex4 | a row with a list-valued answer passes the parser and crashes verify | ACCEPTED. Every text field of a row (qid, answer, quote, source_id, rationale) must be a string, null or absent; otherwise the reply is malformed and unreadable (it voids the pass). | test_PLANT_a2r12_a_row_field_of_the_wrong_type_makes_the_reply_unreadable |
| codex5 | a prose mention of an "answers" key voids a unique reply | DECLINED, by design (round 11): an answers key outside every well-formed envelope makes the reply ambiguous, so it voids the pass and leaves NI. It cannot manufacture an answer. Impact: 0 of 391 held replies. | -- |
| codex1 | 4.3 / USUAL filter | DECLINED, out of scope (a RULE change); recorded for a future amendment. | -- |
| codex2 | unseen-source reliance | DECLINED, out of scope (a RULE change); the stated residual stands; recorded for a future amendment. | -- |
| codex3 | closed-branch rendering | DECLINED, out of scope (rob2_tab.py is frozen); stored, not rendered. | -- |

## Amendment A2 review, round 13 (13 Oct 2026): codex REVISE (5); agy ACCEPT

Answered: 2 ACCEPTED, 3 DECLINED as out of A2's signed scope. 2 failing-first tests (2 failed on the reviewed code,
then all 37 A2 tests pass). Unchanged reading of 391 of 391 held replies. Under the stricter proof, exactly 11 of the
39 held adjudications are still proven defect-caused.

| # | finding | response | test |
|---|---|---|---|
| codex2 | an earlier matching reader is not proof that it supplied the unread slot | ACCEPTED. The defect-run reader must be the UNIQUE held call that matches: same role, trial and outcome, registered targets covering the adjudicated ones, earlier, same evidence block. Two candidate attempts leave which reply the adjudicator saw unproven, so the adjudication stays genuine (fail closed). | test_PLANT_a2r13_the_defect_reader_must_be_the_UNIQUE_candidate |
| codex4 | a prose mention of the key voids a valid reply, contrary to A2's signed promise to ignore prose | ACCEPTED (the earlier decline is withdrawn: the signed text promises it). Only an object KEY counts: an "answers" key that opens an object or follows a comma. A key merely mentioned in prose is ignored, while a broken object's answers key still voids the reply (round 9-11 tests unchanged). | test_PLANT_a2r13_a_key_mentioned_in_prose_is_not_a_broken_envelope |
| codex0 | unseen-source reliance | DECLINED, out of scope (a RULE change); the stated residual stands; recorded for a future amendment. | -- |
| codex1 | 4.3 setting-based | DECLINED, out of scope (a RULE change); recorded for a future amendment. | -- |
| codex3 | closed-branch rendering | DECLINED, out of scope (rob2_tab.py is frozen); stored, not rendered. | -- |

## Amendment A2 review, round 14 (13 Oct 2026): codex REVISE (5); agy ACCEPT

Answered: 1 ACCEPTED, 4 DECLINED as out of A2's signed scope. 1 failing-first test (it failed on the reviewed code, then
all 38 A2 tests pass). Unchanged reading of 391 of 391 held replies.

| # | finding | response | test |
|---|---|---|---|
| codex0 | the round-13 boundary (key after '{' or ',') let a broken object with a MISSING comma through | ACCEPTED, and the round-13 boundary is withdrawn: it was the wrong distinction. An "answers" key outside every well-formed envelope now voids the reply when an object opened BEFORE it failed to decode, so the key belongs to a broken object (missing comma, stray brace in a string, cut-off reply). With no failed '{' before it, it is a key merely mentioned in prose and is ignored. | test_PLANT_a2r14_a_broken_object_missing_its_comma_is_still_broken |
| codex3 | the frozen round-6 test requires NI for "commonly" in a mechanism rationale | DECLINED, out of scope. tests/test_rob2_contextual.py is frozen with the pre-registered RULE; changing what the USUAL filter rejects is a rule amendment. Recorded for a future amendment (as rounds 7-13). | -- |
| codex1 | unseen-source reliance | DECLINED, out of scope (a RULE change); the stated residual stands; recorded for a future amendment. | -- |
| codex2 | 4.3 setting-based | DECLINED, out of scope (a RULE change); recorded for a future amendment. | -- |
| codex4 | closed-branch rendering | DECLINED, out of scope (rob2_tab.py is frozen); stored, not rendered. | -- |

## Amendment A2 review, round 15 (13 Oct 2026): codex REVISE (5); agy ACCEPT -- review closed, A2 applied

Answered: 5 DECLINED (1 by design, 4 out of A2's signed scope). No new finding that could change an answer.

| # | finding | response |
|---|---|---|
| codex3 | an undecodable prose brace before a prose mention of the key voids a valid reading | DECLINED, by design. Rounds 13 and 14 show that no syntactic rule separates "key of a broken object" from "key mentioned in prose" in every case. Each error has a direction: treating a broken object as prose READS an answer from a fragment (round 14's finding), while treating prose as broken VOIDS the pass and leaves NI. The parser takes the second; it cannot manufacture an answer. Measured impact: 0 of 391 held replies. |
| codex0 | unseen-source reliance | DECLINED, out of scope (a RULE change); the stated residual stands. |
| codex1 | 4.3 setting-based | DECLINED, out of scope (a RULE change). |
| codex2 | "commonly" in the frozen round-6 test | DECLINED, out of scope (a RULE change). |
| codex4 | closed-branch rendering | DECLINED, out of scope (rob2_tab.py is frozen); stored, not rendered. |

Closing the A2 review: agy has ACCEPTED every round since 10. Codex's remaining findings are the four RULE-scope
items that A2's signature does not cover, plus one fail-closed design choice. Recorded for Mahmood as candidates for a
future amendment to the RULE: (1) memory markers for references to unseen sources; (2) 4.3 as setting-based;
(3) "commonly" in mechanism wording (and the frozen round-6 test that encodes it); (4) rendering closed-branch
decisions on the served tab.

## Amendment A3 and the two pre-registered variants, review round 16 (13 Oct 2026): codex REVISE (5); agy REVISE (6)

Mahmood (via Dispatch, 13 Oct; outputs/robgrade/SIGNING_RULE_CANDIDATES.md): "ok" to the four codex candidates.
Adopt 1 (references to sources the readers never saw) and 4 (closed-branch decisions on the served tab) directly, as
amendment A3. 2 (4.3 setting-based) and 3 ("commonly") are pre-registered variants, scored separately.

Answered: 10 ACCEPTED, 1 DECLINED. 7 failing-first tests (7 failed on the reviewed code, then pass). Two of them had
FIXTURE errors, found by diagnosis and corrected (stated below). All 173 contextual and A2/A3 tests pass. Effect:
agy3 showed that the shown registry kinds are registry_text/registry_row, so the reviewed A3 dropped citations of a
registry the readers WERE shown. With it fixed, a live A3 re-run needs 0 new calls (it was 3).

| # | finding | response | test |
|---|---|---|---|
| agy3 | registry sources are kind registry_text / registry_row, never "registry": a shown registry was treated as unseen | ACCEPTED. The kind is matched by its prefix. | test_PLANT_a3r16_a_shown_registry_source_of_either_kind_may_be_named |
| codex1 | a document mentioned ANYWHERE in a shown source exempted any claim attributed to it ("The protocol was unavailable." exempted "according to the protocol, ... concealed") | ACCEPTED. A document counts as reported only in the QUOTED SENTENCE of the cited shown source (a sentence ends at . ! ?). The frozen r4 case, where the plan is reported in the quoted sentence, stands. RESIDUAL, stated: within that one sentence, a mention is not parsed for what it asserts. | test_PLANT_a3r16_a_document_merely_mentioned_ELSEWHERE_in_the_source_is_not_reported_context |
| agy0, agy1, agy2, agy4 | raw substring matching ("sap" in "saphenous"); aliases not recognised (SAP / statistical analysis plan, fig 1 / Figure 1, protocols / protocol) | ACCEPTED. Documents are matched as words by the same patterns in the rationale and in the quoted sentence, compared by canonical name. FIXTURE corrected: agy2's quote "participant flow" fails the 3.1 topic gate before the document check is reached; the test now quotes "participant flow and complete follow-up". | test_PLANT_a3r16_documents_are_matched_as_words_with_their_aliases |
| agy5 | "non-adherence to the protocol", "deviations from the protocol" were read as documents | ACCEPTED. Protocol as a concept (per-protocol; deviation from / adherence to / violation of the protocol; protocol deviation) is removed before documents are matched. | test_PLANT_a3r16_protocol_as_a_concept_is_not_a_document |
| codex2 | A2's historical defect proof was re-judged by A3's verifier | ACCEPTED. defect_caused judges a reader under A2's rule (check_unseen=False): A3 cannot unmake an A2 supersession proof. | test_PLANT_a3r16_an_A2_supersession_proof_is_judged_under_A2s_rule |
| codex4 | a variant could be computed before its document existed | ACCEPTED. The pipeline refuses --variant unless the variant's document is committed and unedited. | test_PLANT_a3r16_a_variant_never_runs_before_its_document_is_committed |
| codex0 | the variant manifest could omit (or replace) fresh base readers, and the replay would still match | ACCEPTED. A variant OVERLAYS the base manifest. The base's fresh records are always present, the variant stores only the entries it adds, and the scorer refuses a variant entry that stands in for a base reader of the same prompt. FIXTURE corrected: the test's assessment first had only D1 answers, so every other question was a target. | test_PLANT_a3r16_a_variant_overlays_the_base_manifest |
| codex3 | MEMORY markers ("published protocol", "previously reported") reject context the quote reports | DECLINED, out of A3's signed scope. A3 adds a check for unseen sources; it does not relax the pre-registered MEMORY markers. The direction is conservative (NI). Recorded for Mahmood as a candidate. | -- |

The variant documents were corrected before registration. A variant may need a reader call for a later pass whose
question set differs from the base's (not only adjudications), and the mechanical check now reads 0 new A3 calls.

## A3 review, round 17 (13 Oct 2026): codex REVISE (4); agy REVISE (4)

Answered: 6 ACCEPTED (two of them raised by both reviewers), 1 DECLINED. 5 failing-first tests (5 failed on the
reviewed code, then pass); 178 contextual and A2/A3 tests pass. Mechanical checks unchanged: A2's 11 proofs hold,
and an A3 re-run needs 0 new calls.

| # | finding | response | test |
|---|---|---|---|
| codex1, agy0 | a quote ending with its own full stop let the sentence search run into the NEXT sentence, re-opening round 16's hole | ACCEPTED. A quote that ends its sentence ends it. | test_PLANT_a3r17_a_quote_ending_its_sentence_does_not_reach_into_the_next |
| codex0, agy3 | an overlay entry could shadow a base entry of the same prompt by changing its state, or by replacing an adjudicator | ACCEPTED. A variant entry for a prompt the base already answered is refused, in ANY role and whatever its id or state. RESIDUAL, stated: if the base's only attempt on a prompt FAILED, the variant cannot re-attempt it under that prompt; the scorer refuses loudly rather than score it. | test_PLANT_a3r17_a_variant_entry_may_never_shadow_a_base_entry_of_the_same_prompt |
| agy1 | "the manuscript" / "the original publication" were unseen even when the full text was shown | ACCEPTED. They are the full text: allowed when a CC full text is shown, unseen otherwise. | test_PLANT_a3r17_the_manuscript_is_the_shown_full_text |
| agy2 | registry aliases (ClinicalTrials.gov, trial register) were separate documents | ACCEPTED. They are one document, the registry. | test_PLANT_a3r17_registry_aliases_are_one_document |
| codex3 | a rationale that DISCLAIMS a document ("No protocol was available, but ...") was dropped | ACCEPTED. "no X", "without (access to) the X", "the X was not available / unavailable" are disclaimers, not reliance; an affirmative reliance still drops. | test_PLANT_a3r17_a_document_the_rationale_says_was_NOT_available_is_not_relied_on |
| codex2 | the MEMORY markers ("published report") still reject a report that was shown | DECLINED, out of A3's scope (as round 16). A3 adds a check; relaxing the pre-registered MEMORY markers is a further rule change. Recorded for Mahmood. | -- |

## A3 review, round 18 (13 Oct 2026): codex REVISE (3); agy ACCEPT

Answered: 2 ACCEPTED, 1 DECLINED. 2 failing-first tests (2 failed on the reviewed code, then pass); 180 contextual
and A2/A3 tests pass. Mechanical checks unchanged (A2's 11 proofs hold; an A3 re-run needs 0 new calls).

| # | finding | response | test |
|---|---|---|---|
| codex0 | an overlay entry for a DIFFERENT prompt replaced a fresh base reader before freshness was judged, voiding the pass | ACCEPTED. In every pass, a base record that is fresh for the prompt is used, whatever the overlay holds for that role (readers and the adjudicator). A variant can add records, never hide one. | test_PLANT_a3r18_a_fresh_base_record_always_wins_over_an_overlay |
| codex1 | a quoted sentence that says the document was UNAVAILABLE counted as reporting it | ACCEPTED. A document is reported only where the sentence names it without saying it was not available (the same disclaimer test as the rationale's). | test_PLANT_a3r18_a_source_sentence_saying_the_document_was_unavailable_does_not_report_it |
| codex2 | MEMORY markers vs a shown "published report" | DECLINED, out of A3's scope (rounds 16-17). Recorded for Mahmood as a candidate rule change. | -- |

## A3 review, round 19 (13 Oct 2026): codex REVISE (3); agy ACCEPT

Answered: 2 ACCEPTED, 1 DECLINED. 2 failing-first tests (2 failed on the reviewed code, then pass), and 1 earlier
expectation revised by the decision below; 182 contextual and A2/A3 tests pass. Mechanical checks unchanged.

| # | finding | response | test |
|---|---|---|---|
| codex0 | a quote cropped just after a disclaimer ("Without access to the protocol, ...") re-authorised the document, because the quote was checked on its own | ACCEPTED. Reported documents come from the quoted SENTENCE alone, which contains the quote and any disclaimer; the quote alone only when no shown source is named. | test_PLANT_a3r19_a_quote_cropped_after_a_disclaimer_does_not_report_the_document |
| codex1 | a shown full text authorised "the parent publication": kind is not identity | ACCEPTED. "Original / parent / primary / main publication, paper, report or article" names ANOTHER paper than the shown one: unseen unless the quoted sentence reports it. "The manuscript" and "the full text" remain the shown full text. This partly REVISES the round-17 answer to agy1 for "original publication"; that test's expectation is changed, with the reason, in the test. | test_PLANT_a3r19_a_shown_full_text_is_not_another_publication |
| codex2 | MEMORY markers vs a shown "published report" | DECLINED, out of A3's scope (rounds 16-18). Recorded for Mahmood as a candidate rule change. | -- |

## A3 review, round 20 (13 Oct 2026): codex REVISE (3); agy ACCEPT

Answered: 2 ACCEPTED, 1 DECLINED. 2 failing-first tests (2 failed on the reviewed code, then pass); 184 contextual
and A2/A3 tests pass. Mechanical checks unchanged.

| # | finding | response | test |
|---|---|---|---|
| codex0 | with a full text shown, "the original manuscript" passed (read as the shown text) | ACCEPTED. An original / parent / primary / main MANUSCRIPT names another paper too. RESIDUAL, stated, in the conservative direction (NI): a shown "main report" that the rationale explicitly identifies as the cited source still counts as unseen, because a name does not establish document identity. | test_PLANT_a3r20_an_original_manuscript_is_another_paper_than_the_shown_full_text |
| codex2 | "Fig. 1" ended the quoted sentence and cut the document out of it | ACCEPTED. The full stop of a known abbreviation (Fig., Figs., No., vs., et al., e.g., i.e., approx., ref., suppl., tab.) does not end a sentence. | test_PLANT_a3r20_an_abbreviation_does_not_end_the_quoted_sentence |
| codex1 | MEMORY markers vs a shown "published report" | DECLINED, out of A3's scope (rounds 16-19). Recorded for Mahmood as a candidate rule change. | -- |

## A3 review, round 21 (13 Oct 2026): codex REVISE (3); agy ACCEPT

Answered: 1 ACCEPTED, 2 DECLINED (1 shown to be already correct). 1 failing-first test (it failed on the reviewed
code, then passes) and 1 pin; 186 contextual and A2/A3 tests pass. Mechanical checks unchanged.

| # | finding | response | test |
|---|---|---|---|
| codex0 | a shown registry exempted every registry citation, including another NAMED register (ISRCTN, EudraCT, ...) | ACCEPTED. The shown registry is always ClinicalTrials.gov (an NCT record), so a named register other than it is another document: unseen unless the quoted sentence reports it, with or without its number (ISRCTN12345678 = ISRCTN). A reported named register is also "the registry" the rationale may then name. | test_PLANT_a3r21_another_NAMED_registry_is_unseen_when_only_clinicaltrials_gov_is_shown |
| codex2 | "protocol deviations" (with a space) was read as a document | DECLINED: already correct. Executed on the reviewed code, codex's exact case returns PY: the concept pattern matches "protocol" followed by a hyphen OR a space. Pinned by a test so it stays so. | test_a3r21_protocol_deviations_is_a_concept_PINNED |
| codex1 | MEMORY markers vs a shown "published report" | DECLINED, out of A3's scope (rounds 16-20). Recorded for Mahmood as a candidate rule change. | -- |

## A3 review, round 22 (13 Oct 2026): codex REVISE (2); agy ACCEPT

Answered: 1 ACCEPTED (with a stated residual), 1 DECLINED. 1 failing-first test (it failed on the reviewed code,
then passes); 187 contextual and A2/A3 tests pass. Mechanical checks unchanged.

| # | finding | response | test |
|---|---|---|---|
| codex0 | registry IDENTITY: a shown registry exempted another trial's record | ACCEPTED, as far as wording can establish identity. A trial identifier in the rationale (NCT, ISRCTN, ACTRN, ChiCTR, EudraCT, DRKS, CTRI, PACTR, IRCT, JPRN, UMIN, NTR numbers) must be one the readers were shown, in a shown source's text or its registry id. "Another / a different / a separate registry record" is unseen by its own words. RESIDUAL, stated: an UNNUMBERED, unqualified reference ("record B") cannot be identified from wording. | test_PLANT_a3r22_a_trial_identifier_must_be_one_the_readers_were_shown |
| codex1 | MEMORY markers vs a shown "published report" | DECLINED, out of A3's scope (rounds 16-21). Recorded for Mahmood as a candidate rule change. | -- |

The bound of A3, stated: A3 catches a rationale that relies on a document by naming its kind (protocol, analysis
plan, supplement, manuscript, another publication, a register), its alias or its trial identifier, when the readers
were not shown it and the quoted sentence does not report it. Which document an unnamed, unnumbered reference means is
reference resolution that wording cannot settle. That remains the residual, and its failure direction is the
contextual answer standing (the readers' judgement, Handbook 8.2.3).

## A3 review, round 23 (13 Oct 2026): codex REVISE (3); agy ACCEPT

Answered: 2 ACCEPTED, 1 DECLINED. 1 failing-first test (it failed on the reviewed code, then passes) and 1 fixture
revised; 188 contextual and A2/A3 tests pass. Mechanical checks unchanged.

| # | finding | response | test |
|---|---|---|---|
| codex1 | "another registry record" was rejected even when the quoted sentence itself reports it | ACCEPTED. As for every document, "another record" that the quoted sentence reports is reported context. | test_PLANT_a3r23_another_record_REPORTED_in_the_quoted_sentence_may_be_named |
| codex2 | the round-22 positive control asserted PY on a source saying randomisation details were OMITTED | ACCEPTED (a fixture error). The test checks identity, but its positive control now quotes real concealment context ("Allocation by central web-based randomisation") with the shown identifier. | test_PLANT_a3r22_a_trial_identifier_must_be_one_the_readers_were_shown (revised) |
| codex0 | MEMORY markers vs a shown "published report" | DECLINED, out of A3's scope (rounds 16-22). Recorded for Mahmood as a candidate rule change. | -- |

## A3 review, round 24 (13 Oct 2026): codex REVISE (2); agy RAN_ERROR (no reply; recorded)

agy ran (Gemini, status SUCCESS, about 66k output tokens, nearly all thinking) but returned no readable reply after
its retry. The round is recorded as a failed attempt, not an acceptance; round 25 re-asks both reviewers.

Answered: 1 ACCEPTED, 1 DECLINED. 1 failing-first test (it failed on the reviewed code, then passes); 189 contextual
and A2/A3 tests pass.

| # | finding | response | test |
|---|---|---|---|
| codex0 | the round-23 "another record" allowance ignored a disclaimer in the quoted sentence ("Another registry record was unavailable ...") | ACCEPTED. "Another record" is reported only where the sentence names it WITHOUT saying it was unavailable: the same disclaimer test as every other document. | test_PLANT_a3r24_another_record_the_sentence_says_was_unavailable_is_not_reported |
| codex1 | MEMORY markers vs a shown "published report" | DECLINED, out of A3's scope (rounds 16-23). Recorded for Mahmood as a candidate rule change. | -- |

## A3 review, round 25 (13 Oct 2026): codex REVISE (3); agy ACCEPT

Answered: 2 ACCEPTED, 1 DECLINED. 2 failing-first tests (2 failed on the reviewed code, then pass); 191 contextual
and A2/A3 tests pass. Mechanical checks unchanged. Both fixes apply the existing disclaimer rule where it was missing.

| # | finding | response | test |
|---|---|---|---|
| codex0 | an identifier a shown text says was UNAVAILABLE ("Record NCT09999999 was unavailable") counted as shown | ACCEPTED. An identifier is shown when it is a shown registry's own id, or a shown text names it without saying it was unavailable. | test_PLANT_a3r25_an_identifier_a_shown_text_says_was_unavailable_is_not_shown |
| codex2 | a rationale DISCLAIMING another record ("No other registry record was available, but ...") was dropped | ACCEPTED. A disclaimed "another record" is not reliance (as for every document since round 17). | test_PLANT_a3r25_a_rationale_disclaiming_another_record_does_not_rely_on_it |
| codex1 | MEMORY markers vs a shown "published report" | DECLINED, out of A3's scope (rounds 16-24). Recorded for Mahmood as a candidate rule change. | -- |

## A3 review, round 26 (13 Oct 2026): codex REVISE (3); agy ACCEPT

Answered: 2 ACCEPTED, 1 DECLINED. 2 failing-first tests (2 failed on the reviewed code, then pass); 193 contextual
and A2/A3 tests pass. Mechanical checks unchanged.

| # | finding | response | test |
|---|---|---|---|
| codex0 | a bare mention of another trial's identifier ANYWHERE in a shown text authorised reliance on its record | ACCEPTED. Identifiers now follow the same rule as documents: reported only by the shown registry's own id, or by the QUOTED SENTENCE (named there, not said to be unavailable). | test_PLANT_a3r26_an_identifier_counts_as_reported_only_in_the_quoted_sentence |
| codex2 | a rationale DISCLAIMING an identifier ("Record NCT... was unavailable, but ...") was dropped | ACCEPTED. A disclaimed identifier is not reliance, as for documents and "another record". | test_PLANT_a3r26_a_rationale_disclaiming_an_identifier_does_not_rely_on_it |
| codex1 | MEMORY markers vs a shown "published report" | DECLINED, out of A3's scope (rounds 16-25). Recorded for Mahmood as a candidate rule change. | -- |

A3 now applies ONE rule to every reference (document kind, alias, register, identifier, "another record"). A
reference the rationale makes, and does not disclaim, must be to something the readers were shown: a source of that
kind or that id, or something the quoted sentence names without saying it was unavailable.

## A3 review, round 27 (13 Oct 2026): codex REVISE (2); agy ACCEPT -- review closed, A3 applied

Answered: 1 ACCEPTED, 1 DECLINED. 1 failing-first test (it failed on the reviewed code, then passes); 194 contextual
and A2/A3 tests pass. Mechanical checks unchanged (A2's 11 proofs hold; an A3 re-run needs 0 new calls).

| # | finding | response | test |
|---|---|---|---|
| codex0 | "Another registry record was unavailable" did not disclaim "the registry": the noun "record" stood between the document and the disclaimer | ACCEPTED. A disclaimer may follow the document's noun (record, entry, registration, report, document, plan, text, data, file). | test_PLANT_a3r27_a_disclaimer_after_the_documents_noun_still_counts |
| codex1 | MEMORY markers vs a shown "published report" | DECLINED, out of A3's scope (rounds 16-26). Recorded for Mahmood as a candidate rule change. | -- |

Closing the A3 review, and why. The announced stopping rule was "a round with no new in-scope codex finding". It is
NOT met, and the review is closed anyway, deliberately:
- agy ACCEPTED every completed round from 18 to 27 (round 24 returned no reply).
- Since round 22, every codex finding has been a further WORDING edge of one uniform rule: a reference to a document
  or record, in the rationale or the quoted sentence, recognised by wording, with or without a disclaimer. Each was
  real, and each was fixed with a failing-first test (12 review rounds, 30 accepted findings on A3).
- A wording matcher has no fixed point against a reviewer generating new phrasings.
RESIDUAL, stated: references and disclaimers are recognised by WORDING, so a phrasing outside the patterns is not
recognised. For an unrecognised reference the failure direction is the contextual answer standing (the readers'
judgement, Handbook 8.2.3); for an unrecognised disclaimer it is NI.

Recorded for Mahmood, as further candidate rule changes (not A3): (5) let the MEMORY markers yield when the named
report is the shown source ("the published report", raised by codex in every round from 16 to 27); (6) the A3
wording residual above.
