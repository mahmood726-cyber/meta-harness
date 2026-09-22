# The enforcement gate: the build reads the admission decision (2026-09-21)

**Fix state (orthogonal fields rule): REPORTED / NONE / CORPUS / STALE** - generated from enforcement-gate-2026-09-21; stale dependencies: harness/gate.py, tests/test_admission_enforced.py

Branch `enforcement-gate` on main `38c04411` (clone `F:\mh-gate`).

Until this increment the family-eligibility evidence was prepared BEFORE pooling (`pipeline.outcome_inputs` ->
`trial_family.prepare`) and never read at the pooling convergence point (`target_endpoint.admit_rows` checked the
endpoint binding only); the 13-predicate admission verdict was computed AFTER the build, from the built
`review.json`, by `scripts/build_bundle.py`, and no harness module read it. The checker described the build; it did
not constrain it. Every page said "existing pooling membership is preserved".

**Measured first, on the served bytes of `38c04411`, before any change** (00-03): 87 pooled primary rows across
32 topics (30 with a primary pool); 53 fail P5 (52 UNKNOWN: entry population 16, intervention contrast 16, registry
parent 16, PICD evidence 4; 1 INELIGIBLE); 16 migration-state (P8 only, unbound_legacy); 14 shadow-admissible;
4 fail the bundle's P8 by a producer binding route the rule does not name. The served gate PASSED
`probiotics-aad-prevention` with 11 of 11 pooled primary rows in family state UNKNOWN (01). The new check, run on
those untouched pages, refuses 32 of 32 and names the same 53 rows, cell for cell (02, 03).

**What landed.** `harness/admission.py` is one implementation: `verdict(row, family)` evaluates P5 (the family's
EFFECTIVE eligibility, `trial_family.effective_eligibility` -- the same function `attach_review` writes onto the
page and the certified ledger) and P8 (a producer binding route other than unbound_legacy), in the bundle's
vocabulary (ADMISSIBLE / MIGRATION_STATE_UNBOUND_LEGACY / INADMISSIBLE) with a SCOPE object naming the twelve
predicates the build cannot evaluate. `pipeline._build_outcome` calls `admission.admit` right after `admit_rows`:
an INADMISSIBLE row is set aside on the outcome (`declared_absent_trials`, state
`FAMILY_ELIGIBILITY_NOT_ESTABLISHED` / `FAMILY_INELIGIBLE`) with the tuple it carried, the absence code, the verdict
and the recovery -- the trial is not erased; a build handed no family ledger admits nothing. Every outcome carries an
`admission_summary` (EVALUATED / NOT_EVALUATED / NO_CANDIDATE_ROWS -- a zero is never "safe"), rendered on the page.
`gate.check_admission_enforced` (on by default, in `gate_page`, in the scorecard) refuses an unstamped pooled row, a
stamp that disagrees with the page's own family ledger under the same function, a certified `families.json` that
disagrees with the page, and a screened-in row that VANISHED (neither pooled nor set aside) -- the refusal prints the
in-build scope and the predicates only the bundle evaluates. `scripts/admission_census.py` counts the build's stamps
and refuses to compute a verdict for a row that has none (the shadow census, a second implementation, is retired).

**Plants** (`tests/test_admission_enforced.py`, 12): every one observed FAILING on `38c04411` before the fix,
passing after. No test asserts a corpus number.

**After the regeneration of 32 of 32 topics** (04-07): primary candidate rows N = 87 = pooled 34 + set aside 53; all outcomes N = 127 = pooled 46 + set aside 81. gate sweep after the regeneration: pages refused 24 of 32; refusal reasons by kind {'result-change notice OPEN': 41, 'no pooled primary result': 11} result-change notices in docs/result_changes.json: 54; by countersignature state {'SEEN_AND_SIGNED': 8, 'BATCH_SEEN_AND_SIGNED': 5, 'OPEN': 41} families eligibility-state identity: 2858 certified families across the topics with a review; certified state != page state on 0 The gate is RED by design: pages whose primary pool emptied are
refused by `check_primary_result` (no pooled primary result), and every moved result carries a notice awaiting
Mahmood's countersignature (`check_result_change_countersigned`). The RED state is the deliverable; it turns green
only with the reviewer's decisions -- countersign each notice; establish eligibility per family from held evidence
(the recovery named on every set-aside row) -- never by dropping rows.

**Not decided here.** Whether each of the 53 rows is truly inadmissible: the structural screen proves eligibility
from registry evidence only, so a trial without a resolved registry parent is UNKNOWN by construction. The 4 rows
bound by a producer route the bundle's P8 does not name are pooled in-build and recorded per row
(`bundle_rule_agreement: OTHER_ROUTE`). The certified `families.json` copies (last regenerated at `663d43db`) are not
regenerated here; only their eligibility STATE is read by the gate, and 06 checks it is identical to a fresh
derivation.

**Two Codex lanes at `model_reasoning_effort=xhigh` (gpt-6-astra) worked their own clones (08, 09).** Lane V
reproduced the arrival numbers independently (pre-fix served gate PASS on probiotics; post-fix 32 of 32 refused, 53 of 87
primary) and ran the "drop the rows" red team: 6 of 6 adversarial byte-edited copies refused, 8 of 11 altered trials
named by the admission check. Lane R found, by execution, what byte edits cannot show: **R1** a consistent REBUILD after
deleting one term from the topic's executable include list screened HARMONY out (X3) and passed the whole gate with no
refusal naming it -- fixed by `honest_ratchet.compare_screening` (a screened-in record that leaves the candidate set
needs an acknowledgement naming it; `screening_acknowledgements`); **R2/R3/R4** the known-missing sensitivity panel,
the invalidation what-if and saved strands pooled rows without admission (COCS, P5-UNKNOWN, re-pooled into
colchicine-postop-af's combined sensitivity; the refused HARMONY tuple re-pooled into invalidation prose; iv-iron's six
strand members all INADMISSIBLE) -- every re-pool route now admits each candidate through the one implementation;
**R5** the gate's certified-copy cross-check misread the compact family map (384 false disagreements) -- read as stored;
**R6/R7/R8/R9** census exit 0 on a stamped-INADMISSIBLE pooled row, a pass printing no scope, a P8-only refusal
labelled P5, an all-set-aside pool explained as "not extractable" -- each fixed with a plant
(`tests/test_admission_routes.py`). Two placement defects of mine surfaced the same way (a first rebuild relabelled
three typed design refusals and a withdrawn row as P5; a later consumer relabelled two esketamine set-asides
KNOWN_REPORTED_NOT_YET_EXTRACTED): admission now runs as the last step before the pool, and every relabeller keeps an
admission state.

**Lane S -- the same defect class elsewhere (10).** Three confirmed by plant: F1 the protocol compiler's divergences
(35 on 18 of 32 pages) have no consumer -- an HR->OR estimand change in the protocol rebuilt to the same number and a
passing gate -- and the opt-in eligibility chain, when enabled, OVERWRITES the compiler's divergence list with its own
narrower contract (no estimand criterion), so enabling one implementation erases the other's failure: **two
implementations of one decision, the same defect as the `admission` row-key collision found at the start of this
landing, in another costume -- a reader who fixes one will believe both fixed**; F2 a failed compatibility dimension is
cleared by relabelling the assertion (27 of 32 pages, 66 pre-fix violations -> 0), pool intact; F5 an independent
screener's disagreement pauses neither membership nor the gate. Six more measured on the corpus (F3, F4, F6-F9) and
three untested residuals named. None of these is fixed here: each is its own decision for Mahmood, its own plants,
its own landing.

**A finding of its own, surfaced only because the pools moved: the parity relation was computed against a stale k.**
`parity_relation.compute` read `result.k`, which an emptied pool does not carry, and fell back to the hand-written
`our_k`; the comparator second pass takes `shared_k` from a hand profile of the comparator's own trial list. On the
served module (`38c04411`) an emptied noac pool therefore still read **IDENTICAL_SET, "4 of 4"** with 0 rows retained --
a served claim wrong in the most flattering direction, and invisible to `compare_parity` because the relation "did not
change". The live pool's size is now the k (0 is a value) and a pool cannot share more trials than it holds (the clamp
is recorded on the object); noac reads SUBSET, 0 of 4. A relation computed against a stale k is the container/contents
confusion in another place; plant: `test_parity_relation_reads_the_live_pool_never_the_hand_count_when_the_pool_is_empty`
(pre-fix observation recorded in its docstring).

**A known limit of the acknowledgement form, recorded so it is fixed deliberately rather than rediscovered.**
`honest_ratchet._valid_ack` requires `replaced_by_sha256` to name a block present on the new page: the form cannot say
"no replacement". Of this landing's 232 lost blocks, 142 have a same-heading replacement and 90 have none -- pages that
stopped making a claim (GRADE, leave-one-out, RoB re-pool, k=2 refusals) because their pool emptied. Each of the 90 is
acknowledged against the block that now carries the page's changed claim, with a reason that says so; every entry also
carries `replacement_kind` (SAME_HEADING_RERENDER / STANDS_IN_FOR_ABSENT_CLAIM), an extra key the validator ignores, so an
aggregate over `replaced_by_sha256` alone over-counts replacements by exactly the STANDS_IN entries.

**The one finding under the fixes: the corpus had never had an empty primary pool, so every consumer that derived a
property of the CONTENTS from the CONTAINER had never been tested on an empty or moved container -- and each answered
confidently rather than with an absence.** Enforcing admission emptied 11 primary pools and shrank others; that is what
exposed them. Eight distinct consumers broke this way (in seven modules), every one fixed at cause with a plant or an
in-memory check across all 32 pages:
1. `pipeline` -- GRADE was computed and rendered for a primary with no pooled claim (a certainty surface for a claim the
   page does not make; now omitted, the withdrawn-page rule).
2. `pipeline` -- the empty-pool explanation said "REPORTED but not extractable" when every candidate had been
   extracted and set aside on admission (lane R, R9).
3. `design_variance.check_review` -- `GRADE_MISSING_DESIGN_VARIANCE_RATIONALE` fired on GRADE's intentional absence.
4. `design_variance.current_arm_contrast` -- an empty admitted set returned the UNFILTERED cache: the page said
   "2 of 3 pooled trials" with 0 pooled (lane T, bucket 1).
5. `parity_relation.compute` (+ `comparator_second_pass`) -- an emptied pool has no `result.k`, so the relation fell back
   to the hand count and `shared_k` to the comparator's hand profile: noac read IDENTICAL_SET "4 of 4" with 0 rows (lane
   ACK; the flattering direction).
6. `endpoint_canonical.diagnose` -- an empty pool's strategy set `[]` read as `STRATEGY_COLLAPSED` on metformin.
7. `page` / `limitations` -- the declared-strands block and its object were conditional on a SUPPRESSED primary; when
   iv-iron's pool fell from a suppressed k=2 to an admitted k=1 the topic page lost the whole disclosure while the index
   kept it (lane ACK refused to draft a reason for an index-only replacement).
8. `page` / `limitations` -- the stale-contrast statement and its object were conditional on a non-empty contrast
   table; with every row set aside the statement that the cache named trials no longer pooled was not rendered.
The acknowledgement form's inability to say "no replacement" (above) is the same shape in the ledger: 89 disappearances
have to be recorded as replacements. A future consumer written against a pool should be tested on the empty pool
first; `tests/test_admission_routes.py` and `tests/_contracts.py::partition` now exercise that state.

Files: 00 shadow census on `38c04411` (the last run of the retired instrument); 01 the served gate passing UNKNOWN
families; 02-03 the new check on the served pages, rows named; 04 the admission census after the regeneration;
05 the gate sweep after the regeneration, every refusal reason; 06 the families eligibility-state identity check;
07 the result-change notices drafted (all new ones OPEN; the 13 signed M2 notices kept); 08 lane V; 09 lane R; 10 lane S; 11 lane T; 12 lane ACK; 13 the observed verify_all (run 3, the commit's tree); 14 runs 1-2 (superseded).
