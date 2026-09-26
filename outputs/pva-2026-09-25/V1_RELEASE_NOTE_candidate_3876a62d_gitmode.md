# V1 release note -- independent section (FINAL for V1 `3876a62dca66`)

*Measured on the SERVED V1 bytes: production record: NOT MEASURED. Archive: NOT BUILT. Artefacts: served/scorecard.json, tabs.json, producer.txt, f6.json.*

## 0. What V1 is

- **Contents.** The main line as frozen on 26 Sep (6260e70c), plus two changes: the family-eligibility check fix (P5, from the
  notice-review lane) and one retrospective protocol clarification (D3, PRESERVED-HF), which is labelled on its page as
  retrospective. V1: `3876a62dca66` contains frozen main 6260e70c; its served verifier (docs/scripts/verify_bundle.py, sha256 d1ba9320) does NOT have the ordered-contrast value checks; the P5 fix is present (randomised_contrasts takes declared comparators); D3 is applied, labelled RETROSPECTIVE_PROTOCOL_CLARIFICATION (pre_specified=False, affects NCT03030235); **its recorded question calls the condition 'the DELIVER registry condition', but the family it affects is PRESERVED-HF (NCT03030235), not DELIVER (NCT03619213)**.
- **The GLP-1 result.** The pooled primary result is **k = 8 trials, HR 0.856 (95% CI 0.809-0.906)**. FLOW and ELIXA are not in it.
  Adding them would give k = 10, HR 0.861 (0.807-0.919). That change is shown on the page as a **pending result change**, awaiting
  the reviewer's signature, and does not alter the served number. V1 serves k = 8, HR 0.856 (0.8086-0.9061); the served GLP-1 page **does not show a pending block naming FLOW and ELIXA**.

## 1. Reproductions

- **The served GLP-1 pool is reproduced exactly, by an outside party and by this lane.** An independent audit of the served page
  (hash `90c01bcf`, 16 Sep) reported **k = 8, HR 0.856 (0.809-0.906)**. The served result is **0.8560 (0.8086-0.9061)**, equal to
  the three decimals the auditor printed. This lane recomputed it with the served verifier's own `pool()` from the served inputs
  (Paule-Mandel tau^2, HKSJ on t_{k-1}) and got the same result. The evidence lane's independent computation through the production
  path (`harness.known_missing` -> `harness.synth.pool`) gets it too. V1 serves k = 8, HR 0.856 (0.8086-0.9061) [bundle verifier baseline PASS].
- **What that reproduction does not show.** The published Hasebe 2025 meta-analysis (k = 10, HR 0.86 [0.82-0.91]) matches our
  number. The project's own record calls this **accidental**: Hasebe restricts to oral or bolus subcutaneous GLP-1RAs and we do not.
  Agreement under a different protocol is a coincidence, not validation.
- **Every page reproduces its certificate from four downloaded files.** V1: 32 of 32 pages RESULT REPRODUCED at full scope (P2 PASS).
- **The served bytes are the committed bytes.** V1: 284 of 284 fetched files equal the committed bytes (P1 PASS); no production record (P0 n/a).

## 2. Auditor findings closed, with the test evidence

| finding | fixed in | evidence the fix is real |
|---|---|---|
| The served extractor read a FRAGMENT of a number (`n = 2` out of `2,523`, `211` out of `1,211`, `3` out of `7.3`) | c82e86bd (R1+R4) | 5 of 5 plants read the fragment on the pre-fix served regexes; post-fix 14/14 tests pass; 0 of 256 served values changed |
| Arm-swap routes in the typed-arm gate (5 of 11 REWIND-style) | f3034ecc (G1-G7) | the 9 new tests fail on the old gate and pass on the new one (this lane ran both) |
| The witness accepted one group of a grouped number (`033` of `10,033` / `10<U+2008>033`) | c6205f0d (EVID2-C6) | 8 of 8 edge cases through the real check (left, middle and right groups refused; whole numbers kept) |
| Witness role not anchored to the protocol | 54a09dc1 (T6) | both refusal limbs are killed when disabled (mutation test) |
| Held files could have their fetch provenance rewritten | 0a2a7a4b | a re-fetch of identical bytes keeps the first ledger entry |
| The evidence lane's renderer deleted text after a literal `<` (**65** of 359 renders; the first record's 113 included 48 renders where the first fix leaked markup, corrected in the lane's own record) | 8db26154, f849e524 | failing-first test; all pinned spans still verify |
| Every page must name the program that checks it, its sha256 and its limits | 41f3e2d0, 752e9c1f | a page naming a stale verifier fails CI (it fired on a lane branch on 25 Sep) |
| **"All the tabs are empty"** (reported by Mahmood): the verifier box and certificate sat above every tab | c23a7e91 | on the LIVE site, **2,304 of 2,304** browser checks (32 pages x 1280 and 375 px x 12 tabs x 3 click scenarios); a layout test on every page plus 5 plants |

### The 26 Sep auditor pass: one-value edits to LEADER's analysis identity

An outside auditor, working against the live GLP-1 bundle (`release_sha256` 57dcc327, before the ordered-contrast lane's
checks), reported that changing ONE recorded value of the LEADER row, and leaving its basis alone, passes the estimand checks
(P10/P11). This lane reproduced all four on the frozen main 6260e70c (which serves that bundle): each edited bundle gets verdict
PASS with LEADER still admissible. Each row below is then measured on the V1 commit with the same edit (`v1_accept.py` P6), and
on the fix branches with each branch's own verifier.

| edit to LEADER (one value) | live 57dcc327 | in V1 | where it is fixed |
|---|---|---|---|
| AUD-1 comparator direction reversed (placebo vs liraglutide) | passes (reproduced) | **OPEN** in V1 (LEADER stays admissible; P6 `aud1_comparator_reversed:LEADER`) | **[NOT MEASURED ON V1: no fix branch measured]** |
| AUD-2 estimator changed (hazard ratio -> rate ratio) | passes (reproduced) | **OPEN** in V1 (LEADER stays admissible; P6 `aud2_estimator_changed:LEADER`) | **[NOT MEASURED ON V1: no fix branch measured]** |
| AUD-3 a REGISTERED_DEFAULT analysis set re-valued per-protocol | passes (reproduced) | **OPEN** in V1 (LEADER stays admissible; P6 `aud3_default_set_per_protocol:LEADER`) | **[NOT MEASURED ON V1: no fix branch measured]** |
| AUD-4 `analysis_identity_key` edited on its own (it is stored, not recomputed, for ordinary rows) | passes (reproduced) | **OPEN** in V1 (LEADER stays admissible; P6 `aud4_identity_key_tampered:LEADER`) | **[NOT MEASURED ON V1: no fix branch measured]** |
| AUD-5 `analysis_identity_key` leaves out comparator direction (read from the served key, not an edit) | omitted (read) | **OPEN** in V1: the served LEADER key has no comparator direction (`analysis_set=intention-to-treat (registered primary-analysis default)[...`) | **[NOT MEASURED ON V1: no fix branch measured]** |

## 3. Named limitations

- **Two sets of checks are built and tested, but are not in this release (planned for V1.0.1).** The ordered-contrast value checks
  (which arm is compared against which, and which estimator was used, checked against the source text) are on the ordered-contrast
  lane's branch (`oc/ordered-contrast` 23642e0d). The pooled-input linkage (so that a trial the verifier refuses cannot still be
  pooled) and the five separate verdicts (reported one by one, instead of a single PASS or FAIL) are on the POOL lane's branch. Until they land, a verifier PASS does not mean every pooled trial is admissible. V1: the verifier reports one PASS/FAIL, not separate verdicts (P5b FAIL). HARMONY Outcomes is in the pooled k and its row is INADMISSIBLE (failing P5_family_eligible), while the verifier's verdict is PASS.
  **[NOT MEASURED ON V1: producer probe not run]**
- **Edits to a trial's recorded analysis that the checks do not catch (the 26 Sep auditor pass).** In V1, reversing which arm a trial's result compares against (LEADER recorded as placebo vs liraglutide) is not caught; changing the recorded estimator of a pooled result (LEADER's hazard ratio relabelled a rate ratio) is not caught; re-labelling a default analysis set as per-protocol is not caught: the check compares where a value came from, not the value itself; the analysis identity key of an ordinary row is stored, not recomputed, so an edited key is not caught; the analysis identity key leaves out comparator direction, so two results that differ only in which arm they compare against share one key. Each was reproduced on the live release and measured on V1. Where a V1.1 branch was measured to refuse one, the auditor table in section 2 names it; the others have no measured fix.
- **Search.** **No V1 page claims a systematic search.** The trials were found by known-item retrieval (starting from trials already
  known), not by a discovery search. Every page carries its retrieval label: 17 of 32 TITLE-SEEDED RETRIEVAL, 11 KNOWN-ITEM
  RETRIEVAL, 4 HAND-WRITTEN KEYWORD SEARCH (counted on the served pages). A registered discovery search for GLP-1 on the V1.1 branch
  (`evid2/v11-discovery-glp1`, 8481d3c9 and cb26c226) found all 10 of the 10 known eligible trials; it is not in V1.
- **Risk of bias.** The ratings are **model- and registry-derived domain ratings, not reviewer-judged RoB 2 assessments, and they are
  not specific to the outcome being pooled.** A different model family spot-checked a seeded sample: 32 of 33 scoreable ratings agree,
  and 12 of 45 were unscoreable. Outcome-specific RoB 2 *proposals* (`evid/v1.1-rob2`) are V1.1 work.
- **A text-stripping bug with no effect on any served result (PVA-D15).** `harness/absence.py` removes markup with `<[^>]+>`, so a
  literal "P<0.001" in an abstract deletes the text up to the next ">". Measured on the served pages: 7 of 670 absence claims sit on
  deleted text, and **0 of 670 decisions change** when the text is restored. Two lanes measured this independently and got the same
  zero. The fix is tested on the V1.1 branch (`oc/v11-tag-strip`). V1: NOT fixed -- harness/absence.py at V1 still strips with `<[^>]+>`.
- **"Every regex site is planted" covers 401 sites, not all of them.** The regex layer's own inventory counts **401** sites ("407 of
  407" counts the plants, RAI-C12), and it cannot see **9 sites** that build their pattern by joining strings (RAI-C13). One of those,
  `harness/hand_binding._present`, still matches number fragments: a CI bound of 1.0 counts as present in "1.03", and 10 in "10,033"
  (PVA-D12). On the 39 served hand-bound rows, **0 of 132 values** depend on a fragment. It is latent, with no served effect today.
- **Retrospective protocol amendments.** 11 of 32 protocols carry a RETROSPECTIVE amendment: a rule written after registration and
  labelled as such on the page. Those rules are disclosed, not pre-registered.
- **The PRESERVED-HF clarification (D3) is one of them.** It rules whether the registry condition "Chronic Heart Failure With
  Preserved Systolic Function" names the review's population ("preserved ejection fraction"). The trial is PRESERVED-HF
  (NCT03030235, PMID 34711976), not DELIVER (NCT03619213). A yes adds a population term after registration, so it is a
  retrospective clarification, not a pre-registered rule. V1: Applied, labelled RETROSPECTIVE_PROTOCOL_CLARIFICATION (pre_specified=False, affects NCT03030235); **its recorded question calls the condition 'the DELIVER registry condition', but the family it affects is PRESERVED-HF (NCT03030235), not DELIVER (NCT03619213)**.
- **The bundle's own copies of the evidence are not all checked.** A pooled row's `span.text` in BUNDLE.json can be replaced with a
  sentence that is not in the abstract and the verifier still passes (PVA-D11). V1: span.text replacement is NOT caught (P6: 10 of 19 named mutations caught for their intended reason; not caught: mixed_tuple, estimand_contradictory, estimand_malformed, span_text_replaced, aud1_comparator_reversed, aud2_estimator_changed, aud3_default_set_per_protocol, aud4_identity_key_tampered, rewind_arm_swap).
- **Who signed.** A countersignature records a name, a time and the digest of what was signed. Nothing authenticates who applied it
  (EG-F2); the signature verifier binds the bytes, not the person.
- **The ten minutes after a deploy.** The CDN caches each file for 600 s and ignores request-side cache control, so a reader can
  briefly get files from two releases, and the auditor reports a generic MISMATCH. Wait ten minutes and re-run.

## 4. What we do not claim

**V1 claims auditability, not correctness. Every served number can be traced to the bytes it came from and re-run by anyone, and each
page states what its checks do not cover. V1 does not claim that any pooled estimate is clinically right, that any search was
systematic, that any risk-of-bias rating is a reviewer's judgement, that the held sources are the complete publications, or that a
verifier PASS means the evidence is admissible.**
