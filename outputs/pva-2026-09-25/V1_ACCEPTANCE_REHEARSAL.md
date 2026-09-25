# V1 acceptance -- rehearsal findings for the main lane (before the Saturday 09:00 freeze)

From the page-verifier and archive lane. Scored against `docs/evidence/enforcement-gate-2026-09-21/18-release-acceptance-checklist.md`
(1fa77f2c) with `outputs/pva-2026-09-25/v1_accept.py`, on git bytes of candidate commits. These are REHEARSALS: the acceptance run
happens on the SERVED bytes of V1 after deploy, and only that result counts.

## Would block acceptance as things stand
| # | checklist | finding | where measured | what closes it |
|---|---|---|---|---|
| B-1 | B4 | Neither verify_bundle.py (main d1ba9320, oc b60f6b31) reports byte integrity / arithmetic / admissibility / publication eligibility as four separate verdicts. | P5b on main f3034ecc and oc 6fadca05 | emit the four verdicts (and define which combination permits release) |
| B-2 | C | HARMONY (30291013) fails P5 and stays in the k=8 pool; the verdict is PASS. The admissible-only pool (k=7, 0.866) is not on the page. | P7 | follows from B-1; plus a page statement |
| B-3 | A(b)(c), B2 | On main's verifier, 5 of 15 named mutations are NOT caught: mixed tuple (LEADER point + SUSTAIN-6 CI), contradictory estimand, malformed estimand, span.text replaced, REWIND arm swap. Cause: the verifier recomputes from review.json and never compares the BUNDLE's own effect / analysis_identity / span.text copies (PVA-D11 widened). | P6 on main | oc's verifier closes 3 of the 5; span.text and a null analysis_set remain open on oc too |
| B-4 | A(a)/B1 + page naming | On oc's head the GLP-1 page names verify_bundle d1ba9320 while b60f6b31 is served; CI is red on exactly this (and on 31/32 reproduce). | P3; CI run on 6fadca05 | V1 must rebuild the pages after the LAST verifier change, then re-certify |
| B-5 | §F | The "§F audit contract" (regex_layer/OWNERSHIP.md) is not published on any branch. | -- | publish it, or state in the release note that §F is not part of V1's acceptance |
| B-6 | A(e), B3, D(1) | The PRODUCER marks a planted row INADMISSIBLE for the intended reasons (P3/P9/P11/P15) and STILL POOLS it (numeric prefix: pooled 0.855993 -> 0.854643); its only problem is the plant's own integrity mismatch, so with consistent digests there is none. The publication gate on main/oc reads no admission (check_admission_enforced exists only on enforcement-gate). HARMONY is the live instance. | producer_probe.py on oc 812840f2 | generate pooling inputs from admissible rows only (D1), or bring the enforcement gate into V1; either way a planted row must leave the pool |
| B-7 | integration | rai's R1+R4 re-certification (e21023a3) and oc's head conflict in 9 files, ALL generated (glp1 BUNDLE/EXECUTION_RECORD/REPRODUCTION/index/manifest, fix_ledger, m2 evidence views); no code conflicts | git merge-tree e21023a3 oc/ordered-contrast | merge the code, then REGENERATE those artefacts (build_topic glp1, build_bundle glp1, fix-state views); never hand-merge generated JSON |
| B-8 | user-visible (Mahmood) | **'All the tabs are empty'**: the verifier box + evidence certificate rendered above the tabs (every tab at y~6,500 desktop / ~12,400 phone; 0/11 tabs visible). **FIX READY: branch `pva/tabs-verify` 5aa9ba89** (page.py re-cert, 0 served numbers moved; 2,304/2,304 browser checks at 1280 and 375 px). | real browser on the live GLP-1 page | take the page.py change into V1: code merges cleanly with rai and oc (0 non-docs conflicts); generated docs conflict (193 with rai, 5 with oc) -> regenerate every page once. Handoff: outputs/pva-2026-09-25/TABS_FIX_HANDOFF.md on that branch |

## Update on oc's handoff head 812840f2 (V1-READY)
- B-4 closed there (the GLP-1 page names the served verifier); P4 no served number moved; P6 13 of 15 caught, mostly at verdict level; still NOT caught: null analysis_set, span.text replaced. B-1, B-2, B-5, B-6 open.

## Caught today, and how
- At ROW level only (the verdict stays PASS; the damaged row turns INADMISSIBLE with the intended predicate): SUSTAIN-6 non-target span
  (P2, P7, P9) and components (P4, P14); AMPLITUDE-O unlisted and missing spans (P2, P7, P9); LEADER numeric prefix, truncated and
  rounded (P3). oc's verifier promotes most of these to verdict FAIL.
- At VERDICT level: FREEDOM-CVO mixed tuple; identity erasure; duplicate ID; pool substitution.
- The checklist E probe (no unsigned served-number change) is positive-controlled: against origin/enforcement-gate (41 OPEN notices) it
  reports **122 changed values, 0 signed**, so it fails as required.

## Mutation definitions
These are this lane's implementations of the mutations the checklist names; the external auditor's own scripts are not in the
repository. Each is either the served verifier's `--corrupt` limb (in memory, with digests following the edit, per checklist A(d)) or
an edit of the served BUNDLE.json only. See `mutations()` in v1_accept.py.
