# REPRO300 — source-only preflight (development-only)

30 October 2026. This is a **proposed source-only guard**, not a new scientific protocol, enrolled review, immutable registration, external adjudication or claim of clinical validation. The separate 300-review recruitment targets remain 100 Cochrane data-accessible reviews, 100 other open-data published meta-analyses, 50 documented-correction reviews and 50 reviews not selected for known errors. Targets are not completed counts.

## Reproduced false pass and minimal correction

Local v0.2 prototype allowed the SAME published review CD999991 to appear twice with different analysis IDs, different family labels and different strata. Both rows were credited as eligible candidates, inflating a benchmark whose unit is **reviews**, not analyses. The new source-only preflight refuses duplicate canonical review IDs even across analyses and strata. DOI case variants are refused. Positive synthetic controls preserve distinct review IDs. Analysis IDs remain separate metadata for future statistical method matching.

A second previously reproduced prototype bypass allowed a post-preflight candidate to be injected without changing the source-frame hash; stale candidate receipts now refuse after recomputing against source and exposure inputs. An incomplete four-stratum pilot produces no partial draw.

Local synthetic pre-push check: **22/22 pytest tests PASS**. Disabling the review-identity guard makes the two new negative tests FAIL; this demonstrates sensitivity to that one deliberately introduced regression. GitHub full verify, OS CI, and mutation on the exact published GitHub commit remain to be verified separately.

## Eligibility and access are NOT established by this module

The source SHA256, DOI/CD ID, licence URL, source availability, original-text inspection, prior-exposure family and AI-processing rights are **caller declarations only**. They are schema checked, not independently authenticated. SOURCE_UNAVAILABLE, unverified rights, observed prior tuning/known-source exposure and unverifiable exposure status block candidate selection rather than creating numerical failures. The previous estimate that approximately 10% of primary trial publications were accessible has not been reaudited against a complete numerator/denominator.

Before freezing any real selected review, independently verify its publication and analysis identities, underlying study IDs and family equivalence, original source bytes/digests, actual license and permitted processing mode, exclusion from all historical Pairwise70/EvidenceAtlas/Metanew/Meta-Harness development and correspondence, external seed commitment and time-ordered immutable selection frame. A review whose identity exists under multiple aliases/DOIs or shares study families cannot be considered independent until source-verified reconciliation. The preflight normalises the narrow Cochrane pattern `CD######` / `10.1002/14651858.CD######(.pubN)` to one review key for duplicate refusal across versions and strata. This is NOT a complete alias resolver; linked reviews, errata and cross-review shared-study families still require source-led checks.

No real cases are recruited, source-access-confirmed, numerically executed, or adjudicated by this proposal. Distinguish (A) mathematical reproduction conditional on structured extracted data from (B) extraction coverage and correctness starting with original trial publications. Cases with forest-plot-only counts, inaccessible text, uncertain OCR or restricted downloads are NOT_ASSESSED/ACCESS_BLOCKED, not errors.

Upstream evidence: Overmind overmind/evidence/data/gold_reviews/COCHRANE_REPRODUCTION.md historical development fixtures and user-supplied accessibility estimate; Meta-Harness docs/cochrane_headtohead.json CD013505 text-only coverage limitation; Metanew backend/etl/ingest.py CSV parser risk. Cochrane's data-package specification effective 23 September 2026: https://documentation.cochrane.org/revman-kb/data-package-specification-249561249.html . Cochrane data reuse requires review-specific terms, and AI uploads may be restricted: https://www.cochrane.org/pl/form/cochrane-library-data-request .

## Integration acceptance

Only a successful exact-final-head GitHub verify, applicable platform/negative tests, actual rulesets and ordinary expected-head merge justify production integration; then verify default-branch CI. No human scientific adjudication, prospective benchmark B advancement, CROSS-EXCH denominator change, historical certificate change, protected human data change or deployment request is authorised by these code tests.

## Full verification failure and repair — 30 October 2026

The first PR #205 exact-head full GitHub Actions run (#41004033058) **FAILED**:
8 unit tests failed and 0/32 historical review-page certificate replays reproduced. Its
new experimental module was placed directly under `harness/`. Even when a module
is not in the signed import closure, the historical certificate's release-hashed
`certificate_scope.not_covered.in_tree_modules_not_imported_by_any_root`
explicitly enumerates such modules. Therefore adding that file changed the
certificate scope for all 32 sealed releases. The historical certificates are not
stale permission to regenerate or weaken them.

The repair **moves the byte-identical, genuinely development-only source preflight**
from `harness/repro300_preflight.py` to `benchmarks/repro300_preflight.py`, with
an explicit benchmarks package and adjusted test import. It changes no historical
production import, certificate builder, scope rule, historical release, output,
pipeline or build input. A new negative-regression test verifies that the
experimental module is not under `harness/` and that the saved certificate scope
still agrees with the current scope computation. This separation is appropriate
only while REPRO300 remains isolated development tooling. Any eventual
production-path import or release integration must be independently assessed
against historical code closure, with ordinary full verification; no certificate
regeneration or bypass is authorised here. Re-run exact new-head full GitHub CI
and relevant platform tests: previous-head PASS never transfers after a change.

## Cochrane DOI alias refusal — 30 October 2026

Static inspection of the merged preflight exposed a review-denominator false-pass: `CD013505` and `10.1002/14651858.CD013505.pub2` had different casefolded identifiers, allowing two analyses with different family labels to count as two reviews. The bounded fix normalises only the Cochrane CD/DOI pattern, preserves original declared source IDs and hashes, and refuses duplicate reviews across strata, analysis and DOI versions. Synthetic tests cover CD-vs-DOI, version-vs-version and a distinct-review positive control. This is not licence verification, independently authenticated source identity or prospective enrolment. Exact-head GitHub CI, OS checks and protected merge remain separate gates.
