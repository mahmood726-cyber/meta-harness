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
