# Responses to the recorded review of the NI policy (round 1, 12 Oct 2026)

Reviewers: codex (record in `codex.json`) and agy (record in `agy.json`), blind to each other, both verdict REVISE.
The arbiter for every algorithm claim is the RoB 2 full guidance's mapping tables (22 Aug 2019): Table 4 (D1),
Table 6 (D2), Table 10 (D3), Table 12 (D4) and Table 14 (D5). An accepted defect gets a failing-first test
(`F:` logs not committed; the tests are the record); a declined finding is pinned by a test in the table's direction.

| # | finding | response | test |
|---|---|---|---|
| codex0 | D2: 2.4 NI with 2.5 N/NI, and 2.7 NI, should be High | ACCEPTED. Table 6 rows: 2.4 Y/PY/NI with 2.5 N/PN/NI gives High; 2.6 N/PN/NI with 2.7 Y/PY/NI gives High. Engine fixed (v3.1). | test_PLANT_d2_2_4_ni..., test_PLANT_d2_2_7_ni... |
| codex1 | D4: 4.1 NI is grouped with N/PN | ACCEPTED. Table 12 rows 1-4 list 4.1 "N/PN/NI". Only 4.2 NI sets the Some concerns floor. | test_PLANT_d4_4_1_ni_is_grouped_with_no |
| codex2 | the "multiple some concerns" flag fires at 3, and P1 forbids any reviewed High | PARTLY ACCEPTED. "Multiple" means two or more: the flag now fires at 2. The High stays a review author's judgement with reasons (Handbook 8.2.3); it is never automated. P1 is reworded: the NI POLICY changes no judgement, and a review author's override remains possible. | test_PLANT_two_some_concerns_domains_are_flagged_for_review |
| codex3 | "never infer PY" changes what NI means | DECLINED. Mahmood's standing instruction for this lane is "no information when the source is insufficient; never guess". It is stated in NI_POLICY section 3 as a known stricter-than-Handbook reading, and the NI-driven label is what makes its effect visible. | (policy text) |
| codex4 | 3.2 NI is still produced; skipped questions become NI; some fixtures are invalid | ACCEPTED. `applicable()` follows the branching: a skipped, unanswered question is now NA, never NI. This is proven judgement-neutral over every Y/N/NI combination. 3.2 NI is read as N and never resolved. The two invalid fixtures are replaced by valid ones. | test_PLANT_applicable..., test_PLANT_assessment_marks..., test_PLANT_na..._exhaustively |
| codex5 | the counterfactual is a sensitivity, not a causal attribution; the decisive-set docstring was wrong | ACCEPTED. NI_POLICY P5 now says sensitivity, with the closed-branch example. The served label states only what was computed ("would be X if ... reported favourably"). The docstring is corrected. | test_PLANT_ni_driven_never_claims..._exhaustively |
| codex6 | the scorer trusts editable calibration files | ACCEPTED. The scorer rebuilds the pairs from the committed objects and references, recomputes each judgement and label from the stored answers, and refuses an edited label or judgement, a non-TEST trial, or a duplicate pair. | test_PLANT_score_refuses_* |
| codex7 | matching by PMID does not prove the same outcome result | ACKNOWLEDGED, NOT FIXED. This is a real limit of the calibration that predates this policy. Most comparator figures do not state the outcome per row. Disclosed in NI_POLICY section 4 and NI_SCORE.md. | -- |
| codex8 | RoB 1 comparators are labelled RoB 2; the coverage losses are hidden | ACCEPTED. NI_SCORE.md names each comparator's tool, flags mapped RoB 1 as an approximation (Handbook 8.8), and counts excluded records and unmatched trials. | (report) |
| agy0 | D4: 4.5 NI should be Some concerns | DECLINED. Table 12 row 4: 4.4 Y/PY/NI with 4.5 Y/PY/NI gives High. | test_d4_4_5_ni_is_high |
| agy1 | D3: 3.4 NI should be Some concerns | DECLINED. Table 10, last row: 3.3 Y/PY/NI with 3.4 Y/PY/NI gives High. | test_d3_3_4_ni_is_high |
| agy2 | D2: 2.4 N should be Low; 2.4 NI with 2.5 N should be High | PART DECLINED, PART ACCEPTED. Table 6: 2.3 Y/PY with 2.4 N/PN gives Some concerns (declined). 2.4 NI with 2.5 N/PN/NI gives High (accepted, as codex0). | test_d2_deviations_not_affecting..., test_PLANT_d2_2_4_ni... |
| agy3 | D2: 2.7 N should be Low | DECLINED. Table 6 part 2: 2.6 N/PN/NI with 2.7 N/PN gives Some concerns. | test_d2_2_7_no_is_some_concerns |
| agy4 | D1: 1.1 N with 1.2 Y should be High | DECLINED. Guidance Table 3, Some concerns (i.1)+(i.2.1): concealed but not random gives Some concerns. | test_d1_not_random_but_concealed... |
| agy5 | skipped branch questions are stored as NI | ACCEPTED (as codex4). | test_PLANT_assessment_marks... |
| agy6 | the scorer does not filter to TEST | ACCEPTED. A non-TEST pair is refused, not silently filtered. | test_PLANT_score_refuses_a_non_test_trial |
| agy7 | 3.4 cannot be decisive while its parents are NI | DECLINED. Table 10 asks 3.4 whenever 3.3 is Y/PY/NI, and 3.3 is asked after 3.1 N/PN/NI and 3.2 N/PN. With 3.1 NI and 3.3 NI, 3.4 is asked, and its resolution alone lowers High to Some concerns. | test_PLANT_d3_all_ni |

Tally: 17 findings. 10 accepted in full or in part, including all three real algorithm defects (all from codex); 6
declined (5 agy, 1 codex); 1 acknowledged as a limit. Five of agy's six algorithm claims contradict the guidance's own
tables; the sixth (2.4 NI, in agy2) agrees with codex0. All three of codex's algorithm claims were right. That is a
reason the guidance, not either model, is the arbiter.

# Round 2 (12 Oct 2026): codex REVISE with 7 findings; agy RAN_ERROR (client status ERROR after ~107k output tokens,
recorded in round2/; agy is re-run in round 3)

| # | finding | response | test |
|---|---|---|---|
| codex0 | re-argues round-1 codex3: "never infer PY" departs from the Handbook's NI | DECLINED HERE, ESCALATED. The departure is real and is now stated as such. Whether to allow contextual PY/PN (e.g. the Handbook's experienced-CTU example) is Mahmood's decision, not this lane's: his standing instruction is "never guess". Raised in the lane status for his call. | (policy text) |
| codex1 | the vocabulary is enforced only for default-filled answers | ACCEPTED. `normalize_answers` covers every entry: a reader NI on a skipped question becomes NA; NA on an always-asked question becomes NI (`_a` too, so a direct algorithm call cannot read it as a pass); an unanswered asked 3.2 becomes N ("no evidence"). Proven judgement-neutral over all Y/N/NI/NA combinations. | test_PLANT_unanswered_asked_3_2..., test_PLANT_a_reader_ni_on_a_skipped..., test_PLANT_na_on_an_always_asked..., test_PLANT_normalize_answers..._exhaustively |
| codex2 | the scorer does not freeze its inputs | ACCEPTED. The split, the v3 baseline and the comparator transcriptions must be byte-identical to the pre-registration. Every scored answer (value and span) must equal the pre-registration's committed answer after the same normalisation. | test_PLANT_score_refuses_changed_frozen_inputs, test_PLANT_score_refuses_answers_changed... |
| codex3 | a slug given twice is not caught as a duplicate | ACCEPTED. Duplicates are now checked across topics. | test_PLANT_score_refuses_a_slug_given_twice |
| codex4 | the v3 vs v3.1 comparison is not on identical pairs | ACCEPTED. `v3_compare` uses only pairs whose topic, trial, domain and comparator judgement are identical in both, and counts scored pairs with no identical v3 pair. | test_PLANT_v3_comparison_uses_identical_pairs |
| codex5 | NI_SCORE.md lacks the result-identity disclosure that RESPONSES claimed | ACCEPTED (the earlier response overstated it). `DISCLOSURE` is printed in the report and stored in ni_score.json. | test_PLANT_report_states_that_result_identity_is_unverified |
| codex6 | causal wording remains in three places | ACCEPTED. NI_POLICY P2, the engine comment and the test docstring now say "sensitivity, not a causal attribution". | (text) |

# Round 3 (12 Oct 2026): codex REVISE with 5 findings, agy REVISE with 2

| # | finding | response | test |
|---|---|---|---|
| codex0 | "never infer PY" (third time) | ESCALATED to Mahmood (unchanged from round 2). | -- |
| codex1 | NA given to an ASKED conditional question (e.g. 2.7 after 2.6 N) is read as a pass | ACCEPTED. NA on any asked question becomes NI; `ni_label` labels the same normalised answers. This can raise a judgement (2.7 NA becomes NI, so High, Table 6); the neutrality proof is restricted to admissible inputs, and that restriction is stated. | test_PLANT_na_on_an_asked_conditional_question..., test_PLANT_normalize_answers_is_judgement_neutral_on_admissible... |
| codex2 | a dropped trial, or a domain made INSUFFICIENT, passes the frozen check | ACCEPTED. The trial set must equal the pre-registration's, and each domain's INSUFFICIENT status must be unchanged. | test_PLANT_score_refuses_a_trial_dropped..., ..._a_domain_made_insufficient... |
| codex3 | `overall_ni` raises KeyError when a domain is missing | ACCEPTED. It returns None unless all five domains are present and labelled. | test_PLANT_overall_ni_is_none_when_a_domain_is_missing |
| codex4 | BMJ Table 1 and the full guidance differ on D2's 2.4/2.5 branching; the docs claim they agree | ACCEPTED. The discrepancy is stated in `applicable()` and NI_POLICY P0; the full guidance is followed. | (text) |
| agy0 | D1 1.1 N, 1.2 Y, 1.3 Y should be High | DECLINED. Table 4 row "N/PN/NI, Y/PY, Y/PY" gives Some concerns by default. Its remark ("may lead to a judgement of High") describes an author's override, which is never automated. | test_d1_not_random_with_imbalance_is_some_concerns_by_default |
| agy1 | `kappa` uses `and` where the module promises "undefined when EITHER rater uses one category" | ACCEPTED (a contract bug in the calibration statistics, not in the NI policy). | test_PLANT_kappa_undefined_when_either_rater... |

# Round 4 (12 Oct 2026): codex REVISE with 7 findings; agy RAN_ERROR again (client status ERROR after ~95k output
tokens; round 2 failed the same way at ~107k, round 3 succeeded at ~113k -- a client budget, not the prompt)

| # | finding | response | test |
|---|---|---|---|
| codex0 | "never infer PY" (fourth time) | ESCALATED to Mahmood (unchanged). | -- |
| codex1 | normalisation is single-pass: 2.4 NA -> NI opens 2.5, left NA | ACCEPTED. It repeats to a fixpoint, and is proven idempotent over all Y/N/NI/NA combinations. | test_PLANT_normalisation_reaches_a_fixpoint, test_PLANT_normalisation_is_idempotent_exhaustively |
| codex2 | a malformed stored judgement ("LOW_typo") is excluded before any recomputation | ACCEPTED. Every stored judgement (other than INSUFFICIENT_OPEN_SOURCE) is recomputed against the frozen answers. | test_PLANT_score_refuses_a_malformed_judgement |
| codex3 | a topic subset bypasses the frozen cohort | ACCEPTED. The scorer takes the SHA only and scores the four registered comparators. | test_PLANT_score_takes_no_topic_subset |
| codex4 | the anchor is whatever SHA the caller passes | ACCEPTED. The anchor must be the commit that first added NI_POLICY.md, found from git history. | test_PLANT_score_anchor_is_the_commit_that_added_the_policy |
| codex5 | the round-3 kappa change (agy1) is mathematically wrong | ACCEPTED, and the round-3 response is REVERSED. Kappa = (po-pe)/(1-pe) is defined whenever pe < 1. My acceptance in round 3 followed a wrong docstring over the mathematics. The docstring is corrected, and the test that encoded the wrong contract is removed. The old test "all LOW v all LOW is undefined" then failed: pe sums to 0.99999... in floating point, so the undefined test now has a tolerance. | test_PLANT_kappa_is_defined_when_one_rater_is_constant, test_PLANT_one_category_only_is_undefined_not_zero_or_one |
| codex6 | the kappa CI used the null (kappa = 0) variance | ACCEPTED. Fleiss, Cohen & Everitt (1969) non-null variance; hand-checked (45/5/5/45: kappa 0.8, SE 0.06, CI [0.682, 0.918] v the reported [0.604, 0.996]). The CIs published earlier in CALIBRATION.md were too wide; they are regenerated. | test_PLANT_kappa_ci_uses_the_non_null_variance |

# Round 5 (12 Oct 2026): agy ACCEPT (0 findings); codex REVISE with 2 (at most 8 findings asked, each field capped)

| # | finding | response | test |
|---|---|---|---|
| codex0 | "never infer PY" (fifth time) | ESCALATED to Mahmood (unchanged). It is the one open disagreement, and it is a decision, not a defect. | -- |
| codex1 | `domain_object` judged raw answers but labelled normalised ones | ACCEPTED. Every entry point now judges and labels the same normalised answers. | test_PLANT_domain_object_normalises_before_judging |

## Where the review ended
Five rounds, 40 findings: round 1 17, round 2 7, round 3 7, round 4 7, round 5 2 (codex 30; agy 10 across the three
rounds it completed -- it failed twice with a client ERROR, both recorded).
- Accepted and fixed with failing-first tests: 28. These include three real algorithm errors against the guidance
  tables (D2 2.4 NI, D2 2.7 NI, D4 4.1 NI) and two calibration-statistics errors (the kappa definition and its CI).
- Declined against the guidance, each pinned by a test: 7 (6 agy algorithm claims; 1 codex, round-1 codex3).
- Escalated to Mahmood: the contextual PY/PN question (round-1 codex3), re-raised by codex in rounds 2-5 (4 more).
- Acknowledged as a limit: 1 (PMID matching does not prove result identity).
- One response of mine was reversed by a later round: round-3 agy1 (kappa), reversed by round-4 codex5.
No round-5 fix was itself re-reviewed. That is stated here rather than looped further: agy accepted round 5, and
codex's remaining finding was an entry-point gap with a direct test.
