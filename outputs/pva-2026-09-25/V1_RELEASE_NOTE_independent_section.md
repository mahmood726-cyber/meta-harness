# V1 release note -- independent section: what V1 proves, and what it does not

*Written by the page-verifier and archive lane, which did not build V1. Every claim cites a probe or a commit and was run on bytes
this lane fetched or took from git, not on anyone's working tree. **STATUS: DRAFT (25 Sep, ~21:00), written against main
29f0a719 before the freeze.** At the freeze and after the deploy, each line marked **V1:** is filled from this lane's run on the
SERVED V1 bytes, or deleted. No line is carried forward from a rehearsal.*

## 1. Reproductions

- **The served GLP-1 pool is reproduced by an outside party and by this lane.** An independent audit of the served page (hash
  `90c01bcf`, 16 Sep) reported **k = 8, HR 0.856 (0.809-0.906)**. The served result is **0.8560 (0.8086-0.9061)**, equal to the three
  decimals the auditor printed. This lane recomputed it with the served verifier's own `pool()` from the served inputs (Paule-Mandel
  tau^2, HKSJ on t_{k-1}) and got the same result. The evidence lane's independent BEFORE computation through the production path
  (`harness.known_missing` -> `harness.synth.pool`) gets it too. **V1: re-run on the served V1 bundle.**
- **What that reproduction does not show.** The published Hasebe 2025 meta-analysis (k = 10, HR 0.86 [0.82-0.91]) matches our
  number. The project's own record calls this **accidental**: Hasebe restricts to oral or bolus subcutaneous GLP-1RAs and we do not.
  Agreement under a different protocol is a coincidence, not validation.
- **Every page reproduces its certificate from four downloaded files.** On the live site after the tabs deploy, **32 of 32** pages
  printed `RESULT REPRODUCED` at full scope with the served auditor. **V1: re-run on served V1.**
- **The served bytes are the committed bytes.** 284 of 284 fetched files equal `git show` at the release commit, and the deploy
  attests 1194 of 1194. **V1: re-run.**

## 2. Auditor findings closed, with the test evidence (all on main before the freeze)

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

## 3. Named limitations

- **Search.** **No V1 page claims a systematic search.** Every page carries a retrieval label: 17 of 32 TITLE-SEEDED RETRIEVAL, 11
  KNOWN-ITEM RETRIEVAL, 4 HAND-WRITTEN KEYWORD SEARCH (counted on the served pages). A registered discovery search for GLP-1
  (`evid2/v11-discovery-glp1`) is V1.1 work, not in V1.
- **Risk of bias.** The ratings are **model- and registry-derived domain ratings, not reviewer-judged RoB 2 assessments.** A different
  model family spot-checked a seeded sample: 32 of 33 scoreable ratings agree, and 12 of 45 were unscoreable. Outcome-specific RoB 2
  *proposals* (`evid/v1.1-rob2`) are V1.1 work.
- **Tag stripping in the served absence code (PVA-D15).** `harness/absence.py` strips tags with `<[^>]+>`, so a literal `P<0.001` in
  an abstract deletes text up to the next `>`, and its "abstracts are a no-op" guard does not hold. Measured on main: 7 of 670 served
  absence claims sit on text it deletes; **0 of 670 decisions change** when the text is restored; the check is plant-proved. It is a
  live defect with no served consequence today. The ordered-contrast lane measured it independently on the live pages, with the same
  denominator and the same zero (670 rows, 0 changes), and has a tested fix on a **V1.1 branch** (oc/v11-tag-strip: 7 plants fail
  pre-fix). **V1: state it is not fixed in V1 unless that branch lands by the freeze.**
- **Retrospective protocol amendments.** 11 of 32 protocols carry a RETROSPECTIVE amendment: a rule written after registration and
  labelled as such on the page. Those rules are disclosed, not pre-registered.
- **The retrospective clarification on HFpEF wording (named "DELIVER" in the release plan) concerns PRESERVED-HF.** The ruling asks
  whether the registry condition "Chronic Heart Failure With Preserved Systolic Function" names the review's population ("preserved
  ejection fraction"). The trial is PRESERVED-HF (NCT03030235, PMID 34711976), not DELIVER (NCT03619213). The signing plan was relabelled
  (nr 8a8c2e50) after this lane's finding. A yes adds a population term after registration, so it is a retrospective clarification, not a
  pre-registered rule. **V1: state whether it was ruled, and how.**
- **Verifier PASS is not "admissible".** On the served GLP-1 bundle, HARMONY Outcomes fails the family-eligibility predicate and is
  still in the k = 8 pool with verdict PASS. The admissible-only pool (k = 7, 0.866 [0.814-0.922]) is not on the page. The checklist
  requires four separate verdicts (byte integrity, arithmetic, admissibility, publication eligibility); **neither verifier emits them
  on any candidate this lane has seen.** A recovery of HARMONY's entry population exists on the evidence lane (P53-17) and would move
  no number. **V1: fill from P5b / P7.**
- **A refused row can still be pooled.** Run on planted inputs, the real producer records a damaged row INADMISSIBLE and still pools
  it, so the published estimate moves (0.855993 -> 0.854643 for one truncated CI). No gate on main reads admission at pooling.
  **V1: fill from producer_probe.py on the V1 commit.**
- **The bundle's own copies of the evidence are not all checked.** A pooled row's `span.text` in BUNDLE.json can be replaced with a
  sentence that is not in the abstract and the verifier still passes (PVA-D11). **V1: fill from P6.**
- **Who signed.** A countersignature records a name, a time and the digest of what was signed. Nothing authenticates who applied it
  (EG-F2); the signature verifier binds the bytes, not the person.
- **The ten minutes after a deploy.** The CDN caches each file for 600 s and ignores request-side cache control, so a reader can briefly
  get files from two releases, and the auditor reports a generic MISMATCH. Wait ten minutes and re-run.
- **"Every regex site is planted" is 401 sites, not all of them.** The regex layer's own inventory counts **401** sites; "407 of 407"
  counts the plants (RAI-C12). The inventory also cannot see **9 sites** that build their pattern by concatenation (RAI-C13). One of
  them, `harness/hand_binding._present`, still reads number fragments: a CI bound of 1.0 counts as present in "1.03", and 10 in
  "10,033" (PVA-D12). Measured on the 39 served hand-bound rows, **0 of 132 values** depend on a fragment, and the check is
  plant-proved. It is latent, with no served consequence today.

### Not merged by the freeze (as of 29f0a719; **V1: re-check at the freeze**)
- ordered-contrast and estimator checks P10/P11 and the pool guard (oc 88f07c74 .. 23642e0d);
- ~~rai's R1+R4 pinned landing re-certification~~ **LANDED 26 Sep 01:24 (c62b6b12)**, rebased on the tabs fix; proved live (1194/1194;
  served battery PASS; 2,304/2,304 live tab checks; 0 served numbers moved);
- the 41 result-change notices: **0 of 41 signed**; the notice anchors and the P5 check patch (nr) are on branches;
- the GLP-1 FLOW + ELIXA admission (k 8 -> 10, 0.856 -> 0.861): Mahmood's chat approval is recorded as intent, not as a signature; it
  is queued for his signature, not landed; this lane reproduced its before -> after exactly; ELIXA's 3-point MACE is 'prespecified
  secondary' in one FDA review and a 'sensitivity analysis' in another;
- the four separate verdicts (checklist B4) and the admission gate at pooling (checklist D1, B3).

## 4. What we do not claim

**V1 claims auditability, not correctness. Every served number can be traced to the bytes it came from and re-run by anyone, and each
page states what its checks do not cover. V1 does not claim that any pooled estimate is clinically right, that any search was
systematic, that any risk-of-bias rating is a reviewer's judgement, that the held sources are the complete publications, or that a
verifier PASS means the evidence is admissible.**
