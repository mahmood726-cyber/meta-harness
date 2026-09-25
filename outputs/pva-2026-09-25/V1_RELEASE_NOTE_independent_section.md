# What V1 proves, and what it does not — the independent section

*Written by the page-verifier and archive lane, which did not build V1. Every claim below is tied to a probe that was
run on the bytes the site served for the V1 release, not on a working tree. The probe results are in the acceptance
scorecard shipped inside the V1 archive (`ACCEPTANCE.json`). **STATUS: DRAFT, written before the freeze from rehearsals
on candidate commits. Finalised only after the served-bytes run; every "V1:" line is filled from that run, and a line
with no served-bytes result is deleted, not guessed.***

## What V1 proves, if its acceptance run passes

1. **The site serves exactly the committed bytes.** For every file the audit reads (each page, its review core,
   certificate, manifest, the verifiers, and the GLP-1 bundle's replay set), sha256(fetched from the site) =
   sha256(`git show <V1>:docs/<path>`). The deploy job also attests *n* of *n* served files. (P0, P1)
2. **Every one of the 32 review pages reproduces its certificate from four downloaded files.** The served certificate
   auditor, run on `CERTIFICATE.json`, `review.json`, `manifest.json` and `index.html`, prints `RESULT REPRODUCED` at full
   scope. So the page, the review core and the manifest agree with each other and with a pinned code set. (P2)
3. **Every page names its verifier and what that verifier does not check.** It gives the path, the sha256 of the exact
   bytes served, and the commands to run. A page that names a verifier whose bytes changed fails the build's own test,
   which is not hypothetical: it fired on the ordered-contrast branch on 25 September. (P3)
4. **No served number changed without a signed notice.** Every outcome and trial value that differs from the previous
   release corresponds to a result-change notice countersigned `SEEN_AND_SIGNED` or `BATCH_SEEN_AND_SIGNED` whose
   `after` equals what is served. (P4; checklist E)
5. **For the one page with an evidence bundle (GLP-1), the served package is internally checked.** The pool follows
   from the rows to 1e-9. The admission predicates are recomputed from the served records, not read from the bundle.
   The named deliberate errors are refused (see the table in the scorecard: SUSTAIN-6 non-target and component spans,
   AMPLITUDE-O unlisted and missing spans, the FREEDOM-CVO mixed tuple, numeric-prefix CIs, identity erasure,
   duplicate IDs, pool substitution). (P5, P6)
6. **The release is frozen and can be re-checked offline.** The V1 archive replays with no network and no git: every
   file matches its sums, the auditor reproduces N of N pages, the GLP-1 bundle verifies, and a control that damages one
   value must, and does, fail. `SITE_SHA256SUMS` lets anyone check any other served file of V1 by hash.

## What V1 does not prove

- **That any pooled estimate is scientifically right.** The verifiers check identity, location, arithmetic and the stated
  admission rules; they do not check clinical interpretation or whether the question was the right one.
- **That the held sources faithfully represent the publications.** Most rows are bound to abstracts. The verifiers
  list "upstream fidelity of any representation" under `NOT checked`. For GLP-1, SOUL's held abstract is known to omit
  sentences that the full publication carries.
- **That the search found every eligible trial.** Completeness of the source set is outside every verifier.
- **That "verifier PASS" means "admissible".** On the served GLP-1 bundle, HARMONY Outcomes (PMID 30291013) fails P5
  (entry population not established) and remains in the k=8 pool, while the verifier reports PASS. The admissible-only
  pool (k=7, 0.866 [0.814, 0.922]) is computed "for information" and is not on the page. Checklist C names this
  exactly. V1 separates the four verdicts (byte integrity, arithmetic, admissibility, publication eligibility) only
  if P5b passes. **V1: fill from P5b.**
- **That a row the system refuses is kept out of the pool.** Run on planted inputs, the producer records the damaged row INADMISSIBLE for the right reason and still pools it, and the published estimate moves (measured: 0.855993 -> 0.854643 for one truncated CI). No gate on main reads admission at pooling. HARMONY is the served instance. Checklist D(1) and B3 are met only if V1 generates pooling inputs from admissible rows or carries the enforcement gate. **V1: fill from producer_probe.py on the V1 commit.**
- **That the bundle's own copies of the evidence are checked.** A pooled row's `span.text` in `BUNDLE.json` can be
  replaced with a sentence that is not in the abstract and the verifier still passes (PVA-D11, measured on main and on
  the ordered-contrast branch). On main's verifier the same holds for the row's `effect` and `analysis_identity` copies.
  **V1: fill from P6 (`span_text_replaced`, `mixed_tuple:LEADER`, `estimand_*`, `rewind_arm_swap`).**
- **Row-level refusals do not stop the verdict.** In the verifier's `--corrupt` demonstrations, the damaged row turns
  INADMISSIBLE while the overall verdict stays PASS, by design. A reader must read the row lines, not the verdict line.
- **Row-level verification on 31 of 32 pages.** Only GLP-1 serves an evidence bundle. The other 31 pages are
  certificate-reproducible (claim 2): they are consistent with a pinned code set, but no bundle-level row verification
  exists for them.
- **Who signed.** A countersignature records a name, a time and the digest of the rendered block that was signed. The
  tool accepts any name (EG-F2), so V1 shows that a named signature is attached, not who applied it.
- **The external auditor's own probes.** The mutations in claim 5 are this lane's implementations of the mutations the
  release checklist names. The external auditor's scripts are not in the repository and were not re-run.
- **What a reader sees in the ten minutes after a deploy.** The CDN caches each file separately for 600 s, and
  request-side cache control is ignored. For up to ten minutes after a deploy, a reader can receive files from two
  releases, and the certificate auditor then reports a generic MISMATCH rather than naming the mixed view (CDN-1,
  CDN-D2 open). Wait ten minutes and re-run.
- **Checklist §F.** The main lane keeps an "§F audit contract" that is not published on any branch, so it was not audited.

## Known latent defects with measured zero served impact

- `harness/hand_binding._present` accepts a number that is only the leading fragment of another (CI bound 1.0 in "1.03";
  count 10 in "10,033"). Re-testing all 132 values of the 39 served hand-bound rows against their own spans with a strict
  boundary found 0 that depend on a fragment; the census flags both planted cases (PVA-D12).
- Nine regex sites in `harness/` build their pattern by concatenation and are invisible to the regex inventory, so they
  are neither counted nor planted (RAI-C13).
