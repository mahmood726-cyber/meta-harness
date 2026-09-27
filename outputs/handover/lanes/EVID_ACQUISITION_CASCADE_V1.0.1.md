# V1.0.1 acquisition cascade: ICAP / CORP / CORP-2 (branch `evid/v1.0.1-acquisition-cascade`)

Not landed. Branch from `evid/v1.0.1-screening-roles` (7e70759a). One served-number change is queued for Mahmood's
signature (notice in `docs/result_changes.json`, countersignature OPEN).

## What was asked
Find the pericarditis fixture rows by harness, not by waiting for PDFs: legitimate open routes only, every attempt
recorded (URL, time, status, sha256); deterministic extraction first; PRIMARY vs SECONDARY_SOURCE provenance tiers;
SOURCE_EFFECT_CONFLICT on disagreement; a report per target.

## Result per target (evidence/acquisition_cascade/REPORT.md)

| Trial | Target | Found | Tier | Where |
|---|---|---|---|---|
| ICAP | recurrence 11/120 vs 25/120 | **no** | — | no open source carries it; the one secondary table that names ICAP 'Recurrence %' (PMC9531702, 16.7%) is the incessant-or-recurrent composite (20/120) and is refused as a mislabelled row |
| ICAP | GI 11 vs 10 | **no** | — | — |
| ICAP | discontinuation 14 vs 10/12 | **no** | — | — |
| CORP | GI 4/60 vs 3/60 | **no** | — | — |
| CORP | withdrawal 5/60 vs 4/60 | **no** | — | — |
| CORP-2 | recurrence 26/120 vs 51/120 | **yes** | PRIMARY | the trial's own abstract (`cache/colchicine-recurrent-pericarditis/records.json#PMID-24694983`) |

Plainly: for ICAP and CORP **no primary and no secondary source reachable by an open route gives the arm-level
counts**. The primary papers are paywalled (NEJM bronze URL and the CORP green-repository handle both return 403 to an
honest client; recorded, not retried with a disguised one); none is in the Europe PMC OA subset; none of the three
NCTs has posted results; openFDA has no matching label (404), EMA search returns 401, NICE returns only a search page.
119 open-access citing papers were held and scanned: the deterministic scan found no arm-level count pair on the
trials' arm denominators in any row or sentence naming these trials (what it did find is summary percentages and
metadata; counts drawn only inside forest-plot images are not readable by this scan and were not attempted). The fixture rows still need the PDFs (or a reviewer transcription
bound to held bytes).

## What CORP-2's "0.49" is
The abstract prints "relative risk 0·49; 95% CI 0·24–0·65" in the same sentence as 26/120 vs 51/120. The counts give
RR 0.51 (0.34–0.76); 1 − (0.51, 0.76, 0.34) = (0.49, 0.24, 0.66). **It is the relative risk REDUCTION printed under
the label "relative risk".** The harness had served it as the RR (source hierarchy preferred the printed ratio).

## Mechanisms (all tested before the fix; pre-fix records in evidence/screening_roles/TESTS_PREFIX.txt)
- `harness/design_key.ratio_label_audit` — a printed ratio outranks the same source's counts only if it agrees with
  them. MISLABELLED_RRR (fits 1 − x with the interval flipped) is refused and the counts are pooled
  (`KEEP_COUNTS_PUBLISHED_RATIO_MISLABELLED_RRR`); INCONSISTENT keeps its precedence (it may be adjusted) and is
  recorded, not guessed. `tests/test_ratio_label_audit.py` (4).
- `harness/provenance_tiers.py` — PRIMARY vs SECONDARY_SOURCE; endpoint row-label must/must-not match (ICAP
  "incessant" composite refused); counts only on the trial's arm denominators, percentages must corroborate counts;
  percentage-only rows corroborate but never supply counts, and one equal to the excluded endpoint's percentage is
  refused as mislabelled; SOURCE_EFFECT_CONFLICT when accepted witnesses disagree (secondary vs secondary or vs
  primary); a secondary-only result carries serve label "secondary-source".
- `gate.check_provenance_tiers` + page label — a served row with `provenance_tier: SECONDARY_SOURCE` must name a
  hashed citing document and show the visible `secondary-source` badge beside the row; a row labelled PRIMARY on a
  secondary-only witness is refused. Scorecard entry added. `tests/test_provenance_tiers.py` (13).
- `scripts/acquisition_cascade.py fetch|scan`, `scripts/acquisition_report.py`. One honest User-Agent; 401/402/403/
  429/451 and challenge pages are recorded as BLOCKED and never retried; held documents are write-once with sha256.
  Model-call proposals were not needed: no open text had a number whose role regex could not bind.

## Served-number change (signature required)
colchicine-recurrent-pericarditis, Recurrent pericarditis: k=2, 0.4643 → 0.4813 (CORP-2 now from counts; membership
unchanged; interval withheld at k=2 as before). Notice appended to `docs/result_changes.json` (state OPEN).

## Fixtures added 2026-09-27 (colchicine-secondary-cv-prevention)

### COPS report family (one trial, two reports)
- 12-month primary report PMID 32862667 and the 2-year follow-up letter (Tong et al., Circulation 2021;144:1584-1586,
  DOI 10.1161/CIRCULATIONAHA.121.054610), which the cascade resolved to **PMID 34748393** (Europe PMC, recorded).
- Declared in `docs/report_families.json`; `harness/report_family.py` re-hashes each witness, requires its span
  verbatim, and parses the follow-up from the span (12 from "Over the 12-month follow-up", 24 from "Two-Year
  Follow-Up of the Australian COPS Randomized Clinical Trial"); a declared value the span does not state fails closed.
- Protocol timepoint "trial end" → **timepoint report = the 2-year report**; the 12-month report is a
  SENSITIVITY_CANDIDATE. The 12-month abstract itself says follow-up was "a minimum of 12 months".
- The 2-year result is **DISCOVERED_NOT_RETRIEVED**: a letter with no abstract, not in the Europe PMC OA subset,
  publisher PDF 403 (not retried), and the repository copy Unpaywall lists as CC-BY is "All Rights Reserved" on
  figshare with no files. So it is neither pooled nor refused on its numbers; the existing refusal (judged on the
  12-month abstract) now carries its report role and names the timepoint report and its state on the page.
- Counted as one trial. New blocking consistency kinds in the screening gate: FAMILY_DOUBLE_COUNT (two reports of one
  family pooled as two rows) and FAMILY_TIMEPOINT_UNLABELLED (a row or refusal judged on a non-timepoint report
  without saying so).

### Akrami 2021: analysis-population conflict, endpoint-scoped
- Held: CC BY 4.0 JATS XML (PMC8650300) and the CONSORT figure (publisher static host; Europe PMC's figure URL was
  403 and was not retried). Manifest `outputs/handover/colchicine_secondary_cv_sources/`.
- 7 verbatim spans: Results "122 and 129 subjects were assigned"; abstract "120 assigned … and 129"; abstract "249
  patients were recruited"; Table 1 headings n = 120 / n = 129; Discussion "two patients left the study due to drug
  intolerance" and "did not tolerate the effects, thereby were excluded"; abstract GI "15 (12.5%) … and 3 (2.5%)"
  (3/129 = 2.3%, 3/120 = 2.5%: the placebo percentage fits 120, not the 129 randomised).
- The diagram (Randomized n=251; colchicine allocated 122, "Lost to follow-up (n=2)", analysed 120; placebo 129/129)
  is an image: carried as a **declared model transcription** pinned to the image sha256, never as a verbatim span.
  122/129/120 are corroborated in text; "Lost to follow-up (n=2)" and "Randomized (n=251)" are image-only.
- SOURCE_INTERNALLY_INCONSISTENT with `scope_outcomes` = the harm outcomes (GI adverse effects, non-CV death). New
  mechanism: `claimgraph.hold_internally_inconsistent` holds a scoped row out of THAT outcome's pool at build time
  (before, a scoped inconsistency only marked the screening record and never un-pooled anything, because ICAP and
  Mashayekhi were never pooled). Efficacy pool unchanged.

Tests: `tests/test_report_family_and_scoped_hold.py` (11; 8 failed with the fix removed, recorded in
evidence/screening_roles/TESTS_PREFIX.txt).

## Fixtures added 2026-09-27 (CAP- and COVID-corticosteroids reviews)

### Platform / multi-comparison registrations: `harness/comparison_family.py`, `docs/comparison_families.json`
- A registration's condition labels list EVERY comparison's population, so they are never used to screen one
  comparison. A declared family is screened per comparison, each on its own witnessed spans (the span is the only
  text judged; a declared field cannot add a term; a tampered witness or a declared timepoint the span does not state
  fails closed).
- **REMAP-CAP (NCT02735707), CAP review**: was X2 "title/conditions mention 'covid'". Now judged per domain:
  - non-pandemic corticosteroid domain (fixed-duration hydrocortisone vs control; PMID 40261382, CC BY-NC, held):
    population "patients with severe community-acquired pneumonia"; COVID is the domain's OWN exclusion ("known or
    presumed COVID-19 infection"), so not a veto; 658 randomised (536 vs 122); day-90 mortality 78/521 vs 12/122;
    Bayesian adjusted OR 1.52-1.63 across influenza x shock strata → **awaiting classification** (new PRISMA row),
    primary-pool eligibility UNRESOLVED pending MIXED_POPULATION_STRATUM (the protocol excludes influenza; the domain
    randomises it as a stratum), TIMEPOINT (day 90 vs the protocol's 30-day), ADJUSTED_ESTIMATE.
  - COVID-19 corticosteroid domain (PMID 32876697): INELIGIBLE in the CAP review on its OWN population.
- **COVIDICUS (NCT04344730), COVID review**: comparisons per recruitment period. P1 (to 2020-09-17): high-dose
  dexamethasone 36 vs placebo 37 → ELIGIBLE; primary pool pending TIMEPOINT (60-day primary). Its own mortality is
  NOT in the main text (the period effect is only a model covariate) and Supplement 2 is behind PMC's proof-of-work
  check (recorded, not solved; publisher 403) → DISCOVERED_NOT_RETRIEVED. P2: high-dose vs standard-dose dexamethasone
  234 vs 239 → INELIGIBLE (X3, active comparator). The whole-trial 60-day HR 0.96 (0.69-1.33) is recorded as
  REFUSED_WHOLE_TRIAL_ACROSS_COMPARISONS, and `hold_whole_trial` holds any whole-trial row of a multi-comparison
  family out of every pool.
- **Undeclared platforms**: screened with their condition labels removed; design / intervention / comparator rules
  stand (COPPER, I-SPY COVID stay X3); a population failure the title does not settle → awaiting classification
  (A-PLATFORM-DOMAINS-UNDECLARED): Precision T1D Platform NCT07594145 in finerenone-ckd-t2d-renal.
- **Corpus (served V1 ledger at HEAD)**: 4 of 4 platform registrations screened across 32 topics were rejected; 2 of
  those on a population term read off the registration's condition labels (REMAP-CAP 'covid'; NCT07594145 'heart
  failure'). `scripts/platform_registration_audit.py`. The detector finds registrations whose own title/acronym says
  platform, so N is a lower bound (RECOVERY's registration title does not say so).

### Recovered rows and acquisition states
- **CoDEX (PMID 32876695)**: 28-day all-cause mortality 85/151 vs 91/148, Table 2 "28-Day results" row, a SECONDARY
  outcome in CoDEX and exactly this review's outcome and timepoint. The PMC page is free to read but not openly
  licensed, so it stays local; the harness binds to a committed verbatim EXCERPT (table caption, header rows, the
  section row and the result row; header names the page sha256). Binder: BOUND, EXACT_TARGET. `timepoint_span` must sit
  in the same held document (new load check). **Served-number change: COVID primary k=1 0.83 → k=2 0.85** (notice).
- **CAPE COVID (PMID 32876689)**: deaths 11 vs 20 at DAY 21 (committed abstract; 76 vs 73 randomised) → typed refusal
  TIMEPOINT_MISMATCH: no window policy is declared, so day 21 is never substituted for day 28. The reviewer's 75
  analysed is in the full text, not held. A window policy is a protocol decision owed to Mahmood.
  (Correction on the way: PMID 32876697, first fetched under the CAPE label, is the REMAP-CAP COVID domain report.)
- **METCOVID (PMID 32785710)**: acquisition state MAIN_RESULT_NOT_HELD · PROTOCOL_PREFERRED_ANALYSIS_IN_SUPPLEMENT ·
  SUPPLEMENT_NOT_HELD (`docs/acquisition_states.json`, rendered on its absent row). The requested state "main result
  recovered" is NOT what happened: the publisher PDF is 403, the PMC page is abstract-only and its PDF is behind the
  proof-of-work check, Europe PMC returned 500, and the repository copy's PDF link points at localhost.
- **SONIA (PMID 41159889), CAP review**: already a known-eligible-missing trial (search vocabulary gap). The cascade
  holds its CC BY full text; PRIMARY row day 30: 246/1089 vs 284/1091 (HR 0.84, 0.73-0.97). Open-label is a RoB
  matter here (the CAP protocol sets design_double_blind false). Entry enriched; nothing pooled.
- Defect found by the SONIA fixture and fixed: `provenance_tiers.evaluate` required equal denominators for a two-arm
  witness (an unstated equal-arms assumption); it now requires each denominator to be one of the trial's arm sizes.

### Legitimate-route limits met in this batch (recorded, not worked around)
PMC answers its PDF and supplement links with a proof-of-work bot check ("POW_CHALLENGE"); the cascade now records
that as BLOCKED_CHALLENGE_PAGE. JAMA / OUP publisher PDFs: 403.

SERVED_DIFF_PLACEHOLDER

## Committed / not committed
Committed: targets, ATTEMPTS.jsonl (contact address redacted to `<contact>`; response sha256s unchanged), CANDIDATES,
REPORT, HELD.json (sha256 of every held document), and the two CC-BY documents that witness a scored row
(PMC6720402 CC BY 4.0, PMC9531702 CC BY 3.0). The other 117 held full texts stay local (gitignored; 19 carry no licence
statement) and are re-fetchable and verifiable by their recorded sha256.
