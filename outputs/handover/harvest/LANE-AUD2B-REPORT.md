# AUD2B deletion-invariant report

**8 closed / 1 refuted of 9.** MEASURED scope: the two real review bundles,
their scratch build inputs, the registered split, and their copied certificate
inputs. No commit, reset, checkout, stash, network acquisition, or evidence
fabrication. Existing dirty worktree changes were retained.

This is lane repair completion, **not a release or a claim that both full gates
pass**. IV-iron rebuilt successfully; GLP-1 remains blocked outside ownership.

## Method and baseline limitations

Read LANE_PROMPT.md, LANE-AUD2-REPORT.md, and the F: index/workbook. No submission
or portfolio-status promotion; neither central file was edited.

The real tracked reviews on disk include AUD2's uncommitted work; they are not
represented as pristine HEAD fixtures. Original snapshots are under
`.tmp/aud2b/original-reviews/`; original owned Python implementations are under
`.tmp/aud2b/original/`. Pre-fix production functions were loaded before edits.
Their downstream dependencies and certificate code-identity reads use the
working tree, so these are **not historical clean-checkout release replays**.
The IV probe overlapped its rebuild; its scientific core is compared below.

GLP-1's old reproduction has no receipt list or rendered-evidence seal. Its
initial build refuses `claim-check receipt set missing`. IV-iron has a current
seal and receipts. We test the exact stored-object deletions, and separately
remove the entire derived reproduction block **before** a one-field mutation
to exercise ordinary fresh production build inputs. These two routes are
reported separately; unsealing is not disguised as a one-line stored-object
mutation. No trial identities, outcomes or estimates were added.

The old GLP seal was absent, so the supplementary seal probe computes genuine
receipts and a current certificate on its real review, then uses the saved
pre-fix production build implementation for baseline/deletion. IV-iron has no
PI keys (k=2); a PI deletion on it is inapplicable, not a successful plant.

## Findings

| # | Verdict | Measured finding and closure/refutation |
|---|---|---|
| 1 | CLOSED | GLP's original build refuses its receipt-less claim-check object; deleting that entire object makes the pre-fix build return a manifest. Now any existing reproduction block must contain claim-check receipts. IV's seal already caught the deletion. |
| 2 | CLOSED | IV's pre-fix build returns a manifest after deleting the seal. Current production refuses `reproduction.certificate.rendered_evidence_sha256 missing`. GLP required the genuine-certificate supplement described above. |
| 3 | CLOSED | Pre-fix check remains REFUSED because of existing missing snapshots/drift, but deleting IV's set silently shrinks the measurement denominator from 21 to 20. GLP is DEVELOPMENT, not MEASUREMENT. Both now explicitly refuse `assignments/<slug>/set missing or invalid`; a real clean gate-to-pass transition was not observed. |
| 4 | CLOSED | GLP fresh-input build accepts deletion of pi_low; standalone inconsistency stays assessed with downgrade 0. Now build refuses the missing bound and the domain is NOT_ASSESSABLE. Both lower/upper deletions are tested. IV k=2 has neither bound and was already unassessable. |
| 5 | REFUTED | The audit's asserted disappearance of STALE is wrong for both real reviews: membership_incomplete remains True because invalidation reason codes survive. Production gate.check_known_missing_panel also refuses the deleted panel. The unsealed build alone accepts it, but membership assurance does not improve and the gate catches it. No change to membership logic. |
| 6 | CLOSED | Both fresh-input builds accept deleting an actual trial's domains. Other trials keep the same aggregate unassessed names, masking the loss. Now the build refuses the named rob2.trials/<id>/domains path; direct GRADE also records that missing trial support explicitly. |
| 7 | CLOSED | Both fresh-input builds accept deletion of the first outcome's primary flag. Now the build refuses `outcomes/0/primary missing or invalid`, before significance scan coverage can shrink. |
| 8 | CLOSED | Both copied-cache certificate.compute calls return a certificate binding NOT_PRESENT after families.json deletion. Now both refuse `required inclusion support missing: cache/<slug>/families.json`. |
| 9 | CLOSED | Both fresh-input builds accept removal of grade. Now missing/non-dict grade is an explicit refusal before arithmetic validation can be bypassed. |

The count is by candidate, not by topic: an existing IV seal catching a deletion
does not refute a candidate demonstrated on GLP or on a legitimate fresh-build
input. Existing checks were retained. No new optional support exemption was added.

## Pasted production results

Full pre-fix results: [.tmp/aud2b/before.json](.tmp/aud2b/before.json).
Post-fix results: [.tmp/aud2b/after.json](.tmp/aud2b/after.json).
Direct arithmetic/membership observations:
[semantics-before.json](.tmp/aud2b/semantics-before.json).
Below, RETURNED means the production call returned normally; it does not mean
all later release gates passed.

### Candidate 1

```text
glp1-ra-mace-t2d BEFORE stored: RETURNED build manifest; review_sha256=53eabecbfa8e42355e0777fa8a461355e3a23b8c3241225ef587258e0cb60c9b
iv-iron-hfref-hosp BEFORE stored: ValueError: REQUIRED SUPPORT REFUSED: ["certificate-bound evidence changed before rebuild; required support cannot silently disappear"]
glp1-ra-mace-t2d AFTER: ValueError: REQUIRED SUPPORT REFUSED: ["reproduction.certificate.rendered_evidence_sha256 missing", "claim-check receipt set missing"]
iv-iron-hfref-hosp AFTER: ValueError: REQUIRED SUPPORT REFUSED: ["certificate-bound evidence changed before rebuild; required support cannot silently disappear", "claim-check receipt set missing"]
```

### Candidate 2

```text
glp1-ra-mace-t2d BEFORE: mutation unavailable: 'rendered_evidence_sha256'
iv-iron-hfref-hosp BEFORE stored: RETURNED build manifest; review_sha256=dce9a9505ed09f084f4c56fa49329751498ae5a69faa9a674d62be176c3f1713
glp1-ra-mace-t2d AFTER: ValueError: REQUIRED SUPPORT REFUSED: ["reproduction.certificate.rendered_evidence_sha256 missing", "claim-check receipt set missing"]
iv-iron-hfref-hosp AFTER: ValueError: REQUIRED SUPPORT REFUSED: ["reproduction.certificate.rendered_evidence_sha256 missing"]
glp1 real computed-certificate BEFORE baseline: RETURNED build manifest; review_sha256=53eabecbfa8e42355e0777fa8a461355e3a23b8c3241225ef587258e0cb60c9b
glp1 real computed-certificate BEFORE deleted: RETURNED build manifest; review_sha256=53eabecbfa8e42355e0777fa8a461355e3a23b8c3241225ef587258e0cb60c9b
```

### Candidate 3

```text
glp1-ra-mace-t2d BEFORE baseline: ok=False; RAN_OK 0 of 21; RAN_OK_WITH_SOURCE_ERRORS 21 of 21; RAN_ZERO 0 of 21; RAN_ERROR 0 of 21; NOT_RUN 0 of 21
glp1-ra-mace-t2d BEFORE deleted: ok=False; RAN_OK 0 of 21; RAN_OK_WITH_SOURCE_ERRORS 21 of 21; RAN_ZERO 0 of 21; RAN_ERROR 0 of 21; NOT_RUN 0 of 21
iv-iron-hfref-hosp BEFORE baseline: ok=False; RAN_OK 0 of 21; RAN_OK_WITH_SOURCE_ERRORS 21 of 21; RAN_ZERO 0 of 21; RAN_ERROR 0 of 21; NOT_RUN 0 of 21
iv-iron-hfref-hosp BEFORE deleted: ok=False; RAN_OK 0 of 20; RAN_OK_WITH_SOURCE_ERRORS 20 of 20; RAN_ZERO 0 of 20; RAN_ERROR 0 of 20; NOT_RUN 0 of 20
glp1-ra-mace-t2d AFTER check: [false, "search completeness REFUSED: assignments/glp1-ra-mace-t2d/set missing or invalid"]
iv-iron-hfref-hosp AFTER check: [false, "search completeness REFUSED: assignments/iv-iron-hfref-hosp/set missing or invalid"]
```

### Candidate 4

```text
glp1-ra-mace-t2d BEFORE stored: ValueError: REQUIRED SUPPORT REFUSED: ["claim-check receipt set missing"]
glp1-ra-mace-t2d BEFORE fresh input: RETURNED build manifest; review_sha256=11db14418051804ece2b25f225df1d5f3be9a0f57a0e22a95cf9ad963425ca63
iv-iron-hfref-hosp BEFORE: mutation unavailable: 'pi_low'
glp1-ra-mace-t2d AFTER: ValueError: REQUIRED SUPPORT REFUSED: ["outcomes/0/result/pi_low missing"]
iv-iron-hfref-hosp AFTER not_applicable: "PI bounds absent in real k=2 result"
```

### Candidate 5

```text
glp1-ra-mace-t2d BEFORE stored: ValueError: REQUIRED SUPPORT REFUSED: ["claim-check receipt set missing"]
glp1-ra-mace-t2d BEFORE fresh input: RETURNED build manifest; review_sha256=44dbeea2d31a1d9c36ed1169187a1af7b4309b9ebb51adaa8a771eb8c3527215
iv-iron-hfref-hosp BEFORE stored: ValueError: REQUIRED SUPPORT REFUSED: ["certificate-bound evidence changed before rebuild; required support cannot silently disappear"]
iv-iron-hfref-hosp BEFORE fresh input: RETURNED build manifest; review_sha256=1a2056a7b1dbec0a0a999e2bb69e7d04f64c182e0fa11153bd0c4e7b09ee7720
glp1-ra-mace-t2d AFTER gate: ["L1: known eligible missing evidence is named but the primary outcome has no known_missing_sensitivity panel"]
glp1-ra-mace-t2d AFTER membership_incomplete: true
iv-iron-hfref-hosp AFTER gate: ["L1: known eligible missing evidence is named but the primary outcome has no known_missing_sensitivity panel"]
iv-iron-hfref-hosp AFTER membership_incomplete: true
```

### Candidate 6

```text
glp1-ra-mace-t2d BEFORE stored: ValueError: REQUIRED SUPPORT REFUSED: ["claim-check receipt set missing"]
glp1-ra-mace-t2d BEFORE fresh input: RETURNED build manifest; review_sha256=e5027a70fe3d72fdcae8eea1982ab8295fb38a944f711eae06e9fd0f40f42a87
iv-iron-hfref-hosp BEFORE stored: ValueError: REQUIRED SUPPORT REFUSED: ["certificate-bound evidence changed before rebuild; required support cannot silently disappear"]
iv-iron-hfref-hosp BEFORE fresh input: RETURNED build manifest; review_sha256=44b36e77350f0dce8aa48de1f09e9065cb6251fdf6a23a541c5808dc393c3c53
glp1-ra-mace-t2d AFTER: ValueError: REQUIRED SUPPORT REFUSED: ["rob2.trials/31185157/domains missing"]
glp1-ra-mace-t2d AFTER unassessed_domains: ["imprecision", "inconsistency", "indirectness", "publication_bias", "risk_of_bias", "risk_of_bias: D2_deviations", "risk_of_bias: D3_missing_outcome_data", "risk_of_bias: D4_outcome_measurement", "risk_of_bias: D5_selective_reporting", "risk_of_bias: rob2.trials/31185157/domains missing"]
iv-iron-hfref-hosp AFTER: ValueError: REQUIRED SUPPORT REFUSED: ["rob2.trials/40159390/domains missing"]
iv-iron-hfref-hosp AFTER unassessed_domains: ["imprecision", "inconsistency", "indirectness", "publication_bias", "risk_of_bias", "risk_of_bias: D3_missing_outcome_data", "risk_of_bias: rob2.trials/40159390/domains missing"]
```

### Candidate 7

```text
glp1-ra-mace-t2d BEFORE stored: ValueError: REQUIRED SUPPORT REFUSED: ["claim-check receipt set missing"]
glp1-ra-mace-t2d BEFORE fresh input: RETURNED build manifest; review_sha256=0e15b8dc743b9799bfa11fa8f30e3aa9a3babead2f64e980260e6c5892c7a7e0
iv-iron-hfref-hosp BEFORE stored: ValueError: REQUIRED SUPPORT REFUSED: ["certificate-bound evidence changed before rebuild; required support cannot silently disappear"]
iv-iron-hfref-hosp BEFORE fresh input: RETURNED build manifest; review_sha256=38902d127d820204f90c5d29137e9707486e83b1aac74a9c1f58bf2f8edc475d
glp1-ra-mace-t2d AFTER: ValueError: REQUIRED SUPPORT REFUSED: ["outcomes/0/primary missing or invalid"]
iv-iron-hfref-hosp AFTER: ValueError: REQUIRED SUPPORT REFUSED: ["outcomes/0/primary missing or invalid"]
```

### Candidate 8

```text
glp1-ra-mace-t2d BEFORE baseline: RETURNED certificate; trial_family_map_sha256=d6ba8fa9959f9d014a4bb1c4adedeea5b495cb95041022c0b00d90dc7e26613b
glp1-ra-mace-t2d BEFORE deleted: RETURNED certificate; trial_family_map_sha256=NOT_PRESENT
iv-iron-hfref-hosp BEFORE baseline: RETURNED certificate; trial_family_map_sha256=1febf6b38642f5a6eb00081639042e54f2993300f57237fb4635d731bb6dea7d
iv-iron-hfref-hosp BEFORE deleted: RETURNED certificate; trial_family_map_sha256=NOT_PRESENT
glp1-ra-mace-t2d AFTER: ValueError: required inclusion support missing: cache/glp1-ra-mace-t2d/families.json
iv-iron-hfref-hosp AFTER: ValueError: required inclusion support missing: cache/iv-iron-hfref-hosp/families.json
```

### Candidate 9

```text
glp1-ra-mace-t2d BEFORE stored: ValueError: REQUIRED SUPPORT REFUSED: ["claim-check receipt set missing"]
glp1-ra-mace-t2d BEFORE fresh input: RETURNED build manifest; review_sha256=5a6d5e6ec689ff221ff95f0fcc49cce6cbe9631a947bb8a6d96e161ac3b47534
iv-iron-hfref-hosp BEFORE stored: ValueError: REQUIRED SUPPORT REFUSED: ["certificate-bound evidence changed before rebuild; required support cannot silently disappear"]
iv-iron-hfref-hosp BEFORE fresh input: RETURNED build manifest; review_sha256=4028d5bad378702eaed0500d725d9f410cf321da37631bc8aa23038f37ccddd9
glp1-ra-mace-t2d AFTER: ValueError: REQUIRED SUPPORT REFUSED: ["grade missing: required GRADE assessments"]
iv-iron-hfref-hosp AFTER: ValueError: REQUIRED SUPPORT REFUSED: ["grade missing: required GRADE assessments"]
```

## Changed default-valued reads and required-path decisions

* `census.support_violations`: `core.get("grade") is not None` no longer
  silently skips arithmetic; absent/non-dict GRADE explicitly refuses.
* `rep = core.get("reproduction") or {}` becomes an explicit branch: absence
  is the fresh-build lifecycle before derived receipts exist; a present malformed
  block refuses. This does not declare a scientific support object optional.
* `sealed = rep.get("certificate") or {}` and its truthy seal guard become
  explicit validation of any present certificate's required rendered-evidence seal.
* `cc = rep.get("claim_check") or {}` / `if cc` becomes a required dict/receipts
  check whenever reproduction is present; a missing/empty object is not skipped.
* `grade.grade`: `(row.get('domains') or {}).items()` becomes an explicit
  dict/nonempty check that names missing trial support and marks risk of bias
  unassessed. No empty domain map silently disappears from certainty accounting.
* `grade._inconsistency_domain`: PI/CI `.get` reads now produce named missing
  support and NOT_ASSESSABLE for k>=3. Existing k<3 paths already say unassessable;
  absent non-estimable PI values do not support an assessed claim.
* `search_completeness._check`: assignments `.get(...) or {}` is validated;
  each assignment's `.get("set")` is validated before indexed selection.
* `certificate.compute`: families.json's `exists() ... else NOT_PRESENT` is
  replaced by a required-file refusal and unconditional canonical hash read.

New census primary/PI/domain reads each emit named errors. Unchanged defaults
elsewhere were not represented as exhaustively audited. No existing check or
test expectation was weakened; added tests were corrected for measured fixture
absence instead of inventing fields.

## Verification and remaining blockers

MEASURED commands/logs: [verification.json](.tmp/aud2b/verification.json).

* First deletion-family run: 38 passed / 4 failed. Failures were test fixture
  assumptions: GLP's absent seal, IV's absent lower and upper PI bounds, and
  expecting GLP to possess IV's seal. Corrected only the newly added tests.
* Final `python -m pytest -q tests/test_deletion_invariant.py
  tests/test_consumer_consistency.py tests/test_aud2_receipts_ui.py
  --disable-warnings`: **50 passed**, including all 42 deletion-family tests
  and the local browser contract. See [aud2-suite.txt](.tmp/aud2b/aud2-suite.txt).
* Both rebuilds used `--now 2026-09-11` through an offline wrapper that rejects
  socket connections. IV-iron: exit 0. GLP-1: exit 1,
  `pipeline.build_review_core -> statistical_layers.build -> envelope.build ->
  envelope._regulatory_alternatives -> claimgraph.regulatory_fact ->
  claimgraph._held_path`, `ValueError: provenance paths must be repository-relative`.
  `envelope.py`/`claimgraph.py` are outside lane ownership; not edited.
* Full gates remain refused: registered source snapshot records are absent and
  the search engine differs from the published measurement. GLP additionally has
  old certificate/receipt/typed-claim failures after its blocked rebuild. No
  network replacement records, bypass, or release/Overmind PASS is claimed.
* Python compilation and scoped `git diff --check` pass. The latter emits only
  Git's CRLF normalization warning for certificate.py.

The requested IV rebuild regenerates its review bundle, two blind pages,
review index and blind-map registry using the existing build command. These are
left for integration review; unrelated pre-existing edits remain untouched.

## Static versus dynamic disclosure

| Item | Kind | Evidence boundary |
|---|---|---|
| Required field names, two split states, refusal strings, k>=3 PI applicability | Static contract | Validation policy, not research output |
| Trial keys, outcome membership, dates, effect estimates, domain maps | Dynamic real files | Copied from real review/cache objects; no replacements invented |
| Hashes, check verdicts, receipts, test totals, measurement denominators | Dynamic computed | Production calls and logs linked above |
| GLP seal supplement | Dynamic derived support | Actual receipt/certificate computation, not fabricated research evidence |
| Synthetic controls inherited from AUD2 tests | Test-only | Existing explicit synthetic labels retained; not used as real deletion evidence |

MEASURED: the calls, results and test outcomes above. INFERRED: guards cover
the same missing-field shapes on additional reviews; that wider corpus was not
tested here. CLAIMED only within measured scope: eight candidate gaps closed,
one specific audit assertion refuted; no complete scientific assurance claim.

Second-pass review preserved source trial IDs, study dates and statistical
values in real inputs; mutations remove only named fields. No bibliographic
revalidation or new scientific numeric conclusion was attempted.

* `glp1-ra-mace-t2d` scientific review-core identity unchanged: **True** (canonical review-core hash comparison).
* `iv-iron-hfref-hosp` scientific review-core identity unchanged: **True** (canonical review-core hash comparison).
