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
