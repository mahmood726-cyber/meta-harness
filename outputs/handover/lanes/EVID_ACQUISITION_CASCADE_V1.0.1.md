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

## Fixtures added 2026-09-27 (dapagliflozin HFmrEF/HFpEF review)

### Result-status vocabulary: `harness/result_status.py`
- One derived, mutually exclusive state per trial x outcome, first match wins: ADMITTED_PENDING_SIGNATURE / ADMITTED /
  EXTRACTED_NOT_ADMITTED / WITHDRAWN(reason) / SOURCE_HELD_RESULT_NOT_EXTRACTED / SOURCE_ABSENT. A withdrawal is also
  kept as history on any row.
- DELIVER (PMID 36027570): the page said its primary result was "reported but not extractable"; its own row held the
  extraction HR 0.82 (0.73-0.92) with its span (and the reason audit had already flagged the stored code as false).
  Now EXTRACTED_NOT_ADMITTED, extraction named, the withdrawn CV-death-only value 0.88 kept as history. Not admitted:
  admitting it changes the served primary and needs Mahmood's signature.
- The outcome's "not extracted" sentence is rebuilt from the states. STATUS_VS_EXTRACTION (a sentence calling a trial
  not extractable while its state holds an extraction) blocks. **Served V1: 2 of 32 topics** carried it: DELIVER
  (dapagliflozin-hfpef-hosp) and EMPEROR-Preserved PMID 34449189 (empagliflozin-hfpef-hosp).
- ADMITTED_PENDING_SIGNATURE is a page overlay from the OPEN result-change notices (outside the review core), so a
  countersignature never moves the core hash.

### One paper, two trials: `harness/multi_trial_report.py`, `docs/multi_trial_reports.json`
- McMurray et al., Circulation 2024 (PMID 38059368; DOI 10.1161/circulationaha.123.065061) is linked to BOTH
  registrations: DETERMINE-Preserved NCT03877224 (n=504) and DETERMINE-Reduced NCT03877237 (n=313). Relevance is derived
  from each trial's own population span against this review's rules: Preserved in; Reduced out ('reduced ejection
  fraction'). The combined 'DETERMINE-Pooled' analysis (n=817) is recorded as NEVER_IMPORTED; a pooled row carrying it,
  or a row from the Reduced trial, is COMBINED_POPULATION_IMPORTED (blocking).
- Full text and supplement: NOT held (not in PMC; the repository copy's PDF answers 403). The Preserved-specific
  event and safety data were examined in the trial's own ClinicalTrials.gov posted results (public domain, held):
  randomised 253 vs 251; safety set 252 vs 249; serious AEs 26/252 vs 19/249; deaths 3/252 vs 2/249 to day 119;
  cardiac-failure SAEs 2 vs 4 (acute 1 vs 2, congestive 2 vs 0). No CV-death/worsening-HF outcome measure (16-week
  trial). Examined, NOT admitted (it would change a served number: a decision for Mahmood).

## Fixtures added 2026-09-27 (denosumab review, hash 9503a92d)

### Status vocabulary refined (`harness/result_status.py`, `harness/unextracted.py`)
Order = exclusivity: ADMITTED_PENDING_SIGNATURE · ADMITTED · REPORTED_ZERO_EVENTS · EXTRACTED_NOT_ADMITTED · WITHDRAWN ·
REPORTED_UNRESOLVED · NOT_MEASURED (only from a witnessed `not_measured_span`) · RETRIEVED_NOT_REPORTED (always scoped:
"not found in the inspected abstract / full text") · NOT_YET_RETRIEVED (the former SOURCE_ABSENT; one state, one
string). The former SOURCE_HELD_RESULT_NOT_EXTRACTED is split into the three REPORTED_* / RETRIEVED_* states.
- Root cause of FREEDOM "ABSENT_BY_DESIGN": `unextracted._is_design_absent` counted REFUSED_ON_EVIDENCE (a statement
  about what the inspected ABSTRACT says) as a design absence. Removed; ABSENT_BY_DESIGN is no longer emitted. A test
  that asserted a timepoint mismatch was "absent by design" defended the defect and is rewritten to the requirement.
- Plant: DESIGN_ABSENCE_VS_HELD_RESULT blocks a not-measured / absent-by-design claim on a row whose held source holds
  or reports the result.

### FREEDOM (PMID 19671655, NCT00089791)
- Serious infection: **159/3,886 vs 133/3,876**, bound (EXACT_TARGET) to Table 1 of the trial's own infection report
  (Watts et al., Osteoporos Int 2012, PMID 21892677, CC BY-NC, held) — a companion report of FREEDOM, one trial. The
  earlier typed refusal (true of the abstract and the registry's unaggregated terms) is kept as `supersedes`.
- SAE: **1,004/3,886 vs 972/3,876**, bound to a committed excerpt of the trial's posted registry results (public
  domain). NEJM Table 3 is not held (publisher 403; the CC BY repository copy exposes no file link).
- Safety population labelled **as treated** on both rows: "Seven participants who were randomized to placebo but
  received denosumab in error are summarized in the denosumab arm" (registry; the infection report says the same).
- Both are new served results (k=None → k=1): notices OPEN.

### Koh 2016 (PMID 27189284, NCT01457950) — not in the committed search; known-eligible-missing
- Phases split (docs/comparison_families.json): double-blind 6-month denosumab vs placebo 69 vs 66 ELIGIBLE;
  open-label extension (every participant on denosumab, 60 vs 63) INELIGIBLE (X3).
- SAE: SOURCE_INTERNALLY_INCONSISTENT scoped to SAE: narrative 6 (9%) vs 2 (3%); Table 3 double-blind 2 (3) vs 1 (2)
  under n=69/66; and the trial's registry gives a THIRD value, 7/69 vs 2/66 (recorded as a source conflict). The
  reviewer's page citations (p910, p912) are journal pagination, not verifiable from the XML.
- Vertebral fracture: RETRIEVED_NOT_REPORTED, scoped to the inspected full text ('fracture' only in the background).

### Nakamura 2012 (PMID 21927920) — not in the committed search; known-eligible-missing
- Held abstract: 226 randomised to denosumab 14/60/100 mg or placebo for 12 months; "No new vertebral fracture was
  observed on spinal radiographs in either group." → **REPORTED_ZERO_EVENTS** (witness re-verified; never "not
  reported"; not estimable on a ratio scale). Full text not open.

### Defects found and fixed on the way
- The screening-ledger whitelist in pipeline.py dropped `comparisons`/`pending_decisions`, so no comparison table
  ever rendered (my page test used a hand-built review; a served-page test now guards it). The known-missing candidate
  list dropped declared states the same way.
- A companion-report folder named `FREEDOM#infection-report` was cut at `#` (the document-reference fragment
  separator); the cascade now uses `__`.
- docs/refusals.json refused CoDEX "until its spans are committed"; once they were, the build refused itself
  (REFUSED_AND_POOLED). CoDEX was removed from that refusal (Metcovid, still unheld, remains) with a `superseded` record.

## Source versioning and protocol-text scope (DOAC-VTE review, hash 5f9c2b44)

### Version chains (`harness/source_versions.py`, `docs/source_versions.json`)
Every version of a result is recorded (ORIGINAL / ERRATUM / CORRECTION / CSR / CSR_ERRATUM / REGULATORY) with its
source, date, held witness (path + sha256 + verbatim span) or the reason it is not held, its value and its cells, plus
ONE governing decision {DECIDED | PENDING, version, reason}. Nothing is overwritten. A correction applies to the cells
it lists (`apply_per_cell`); a correction that is not held cannot govern; VERSION_SUPERSEDED_SERVED and
VERSION_CHAIN_UNSHOWN block. Chains render on their rows; chains for trials outside the pool render in their own block.

- **Hokusai-VTE primary**: original 130/4,118 vs 146/4,122, HR 0.89 (0.70-1.13) — NEJM abstract, FDA label Jan 2015
  and FDA label Oct 2023 (public domain, held). Reported CSR erratum (26 Feb 2015, Table 11.2): 131, HR 0.90
  (0.709-1.136) — **not held**: the government portals hosting CSRs require accepting terms of use / registering,
  which I did not do without permission. Governing: **PENDING**, original served, chain shown. Note: the regulator's
  own label dated eight years after the erratum still carries 130 / 0.89.
- **Hokusai-VTE major or CRNM**: 349 vs 423 (abstract, label); reported erratum warfarin 424, not held; PENDING.
- **Hokusai-VTE major bleeding**: 56/4,118 vs 66/4,122 on treatment (FDA label Table 6.3, held); the published HR 0.84
  (0.592-1.205) is in the unheld CSR. REPORTED_UNRESOLVED (this review admits the published HR, not a count-derived RR;
  AMPLIFY precedent). The old refusal ("combines major and CRNM") was true only of the abstract; restated.
- **J-EINSTEIN**: the journal erratum (held, CC BY) governs per cell: '1.4%' → '1.3%' in the abstract and Results,
  ARD 3.9% (−3.4 to 23.8) → ARR 4.0% (−2.9 to 24.0), Table 3 2.9% → 2.8%; Table 3 '1.4%' is KEPT ("calculated by
  another definition"). A global replace would have changed it (tested).

### Scope from the protocol's own text (`harness/scope_decision.py`, `docs/scope_decisions.json`)
- The committed search queries the six pivotal UIDs named in the protocol's Search section — the comparator's six
  phase-3 trials. That is a SEARCH LIMITATION, disclosed on the page; it is not an eligibility rule.
- **J-EINSTEIN** (PMID 25717286; NCT01516840 + NCT01516814, one programme, one trial): ELIGIBLE by I1-I4 (verbatim rule
  spans + held evidence). 100 randomised 81:19; 3 rivaroxaban patients from one site excluded for GCP non-compliance;
  symptomatic recurrent VTE **1/78 vs 0/19** (EXTRACTED_NOT_ADMITTED: outside the search); 1/78 vs 1/19 is the broader
  symptomatic-or-asymptomatic-deterioration composite and is not used.
- **BOTTICELLI** (PMID 18541000): ELIGIBLE by I1-I4 (the comparator rule explicitly includes parenteral → VKA);
  dose-ranging / phase 2 are not protocol exclusions. 17/358 vs 5/118 is the composite with asymptomatic imaging
  deterioration → REPORTED_UNRESOLVED; symptomatic-only split not in the held abstract; three dose arms.
- SCOPE_RULE_NOT_IN_PROTOCOL and SCOPE_INHERITED_FROM_COMPARATOR block.

## Final state of this branch (all 32 topics rebuilt on the final harness)

### Served diff vs the screening-roles base 7e70759a (`evidence/acquisition_cascade/SERVED_DIFF_vs_screening_roles.json`)
4 of 32 topics move a served number (5 outcomes); 28 unchanged; no result-state-only changes.

| Topic | Outcome | Before | After | Why | Notice |
|---|---|---|---|---|---|
| colchicine-recurrent-pericarditis | Recurrent pericarditis (primary) | 0.4643, k=2 | 0.4813, k=2 | CORP-2 pooled from counts, not the mislabelled RRR | OPEN |
| colchicine-secondary-cv-prevention | GI adverse effects | 5.375 (1.60-18.10), k=1 | no result | Akrami held out (safety-denominator conflict) | OPEN |
| corticosteroids-covid19-mortality | 28-day mortality (primary) | 0.83 (0.75-0.93), k=1 | 0.85, k=2, interval withheld | CoDEX Table 2 row admitted | OPEN |
| denosumab-vertebral-fracture | Serious adverse events | no result | 1.03 (0.95-1.11), k=1 | FREEDOM registry results, as treated | OPEN |
| denosumab-vertebral-fracture | Serious infection | no result | 1.19 (0.95-1.49), k=1 | FREEDOM infection report (companion) | OPEN |

### Gate
26 of 32 pages pass the full page gate. The 6 refusals are designed holds: 4 pages carry the OPEN notices above
(`result_change_countersigned`), and colchicine-postop-af / semaglutide-obesity-weight keep the pre-existing
HARMS_INCOMPLETE sign-off item from the screening-roles branch.

### HM3 pinned controls
The pinned snapshot is never rewritten. This branch's changes to the 17 HM3 pages are DECLARED by name:
`screening_roles_supersession.json` (regenerated by `scripts/hm3_screening_supersession.py`, now covering both
landings): added keys `comparisons` / `pending_decisions`; REMAP-CAP's row (X2 → awaiting classification); FREEDOM
serious infection's decided harm row superseded (REFUSED_ON_EVIDENCE → pooled 159/3,886 vs 133/3,876). The COVID
primary move is declared in the pinned file's `superseded` section (additions only; pinned values untouched).

### Defects found in my own work during the final verification, and fixed
- `result_status.derive` overwrote a HARMS_INCOMPLETE reason (semaglutide lost the named unresolved report 40189961
  and "must not render this as harm absence"); it now rewrites only the generic sentence it owns.
- Undeclared-platform screening re-screened COPPER / I-SPY COVID without condition labels even for X3 decisions,
  changing their evidence span; only an X2 is re-screened now, and both rows match the pinned control again.
- The page verifier checked a hand row's cited span only (denominators live in table headers); it now uses the
  binder's own rule against the named held document. A first "whole document" attempt let a planted wrong count pass
  and was replaced before commit.
- Four new renderers iterated dicts in insertion order and failed the census's canonical-JSON determinism check;
  sorted, with a reversed-key-order test.

### Known limitations (not fixed here)
- The hand binder accepts a percentage-corroborated count in place of a denominator, so for FREEDOM serious infection
  a denominator off by 7 still verifies (159/3,893 rounds to the printed 4.1%). Binder semantics, pre-existing.
- colchicine-postop-af's definition-heterogeneity cell depends on dict key order under a reversed-order probe
  (pre-existing; its census passes in build order). Flagged as a separate task.
- The full test suite was not run (too slow for this environment / disk); the targeted suites listed in the commits
  were.

### Decisions owed to Mahmood
1. Countersign (or reject) the 5 OPEN result-change notices above.
2. Whether I may access a CSR portal (terms of use / registration) to hold the Hokusai-VTE CSR erratum; and whether a
   held correction should govern (all Hokusai chains are PENDING, original served).
3. A timepoint-window policy (CAPE COVID day 21, REMAP-CAP day 90, COVIDICUS 60-day): none is declared, so none is
   substituted.
4. Whether to admit DELIVER's held HR 0.82 (0.73-0.92), DETERMINE-Preserved's registry rows, SONIA, J-EINSTEIN
   (1/78 vs 0/19) and Koh's double-blind phase — each is held and shown, none admitted.
5. The three REMAP-CAP pending decisions (influenza stratum, day 90, Bayesian adjusted estimate).

## Committed / not committed
Committed: targets, ATTEMPTS.jsonl (contact address redacted to `<contact>`; response sha256s unchanged), CANDIDATES,
REPORT, HELD.json (sha256 of every held document), and the two CC-BY documents that witness a scored row
(PMC6720402 CC BY 4.0, PMC9531702 CC BY 3.0). The other 117 held full texts stay local (gitignored; 19 carry no licence
statement) and are re-fetchable and verifiable by their recorded sha256.

## DPP-4 round (2026-09-27): source preservation, TECOS 3-point MACE, OMNeON / CARMELINA HHF

### Source preservation and coverage (`harness/source_coverage.py`)
- Every held original carries `sha256`, `source`, `retrieved_utc` and `representation: ORIGINAL_VERBATIM` in HELD.json
  (54 earlier entries backfilled from ATTEMPTS by sha256, none unmatched). Excerpts are separate files, labelled.
- Each absent row is stamped with `source_coverage` against the verbatim Europe PMC record: VERBATIM / EXCERPT /
  ALTERED / UNVERIFIED. On an EXCERPT or ALTERED record an absence is never a publication-level claim: it becomes
  REPORTED_UNRESOLVED (the verbatim original mentions the outcome) or NOT_YET_RETRIEVED. RETRIEVED_NOT_REPORTED names
  its coverage in its statement. New blocking kind ABSENCE_ON_EXCERPT.
- Plant: OMNeON (PMID 28893244), whose committed abstract is ALTERED (10 sentences, including both hHF results,
  missing).
- **CORRECTION (same day, after commit 9727c3d8):** that commit reported "8 absent rows rest on 3 ALTERED records
  (32862667, 32785710, 28893244)". Two of the three were wrong. The sentence-and-label classifier had never had its
  error rate measured. Once the lanes held 211 verbatim originals it graded **99 of 211** ALTERED, and the differences
  checked were heading artefacts: a case-insensitive label strip turning "The aim of" into "The of", half-stripped
  "Conclusions and relevance", unknown headings, flattened superscripts (10<sup>8</sup> → "108"). The classifier is
  now a word-level diff: ALTERED = words added or changed, or cut from inside a kept sentence; EXCERPT = whole
  sentences missing; runs of heading words and same-characters-different-spacing seams are ignored; the missing and
  inserted text is NAMED in the coverage record.
  Measured after the fix, on the 211 records the absent rows rest on: **VERBATIM 207, ALTERED 2, UNVERIFIED 2**.
  - The 2 ALTERED are real abridgements, and both were checked by hand: OMNeON 28893244 (hHF results and the
    business-decision sentence missing) and SOUL 40162642 (background, secondary-outcome and SAE sentences missing,
    the same defect the bundle verifier found independently).
  - Validation: the 5 records that fixed the tests, plus an 8-record sample (seed 20260927) used to add the
    spacing rule, are BURNED.
  - A fresh 6-record sample (seed 20260928), plus the lowest-ratio VERBATIM record, all read VERBATIM correctly by
    raw word diff (only heading colons and labels differ).
  - Every VERBATIM grade has a cache/verbatim length ratio of 0.947-1.008, so no abridgement is hidden among them.
  - Labeller = the classifier's author, a stated weakness.

### Served changes (both OPEN notices, countersignature owed)
| Outcome | Before | After | Why |
|---|---|---|---|
| 3-point MACE (primary) | k 3, 1.0074 (0.8391-1.2094) | k 4, 1.0007 (0.8998-1.1129) | TECOS 745/7,332 vs 746/7,339, HR 0.99 (0.89-1.10), EMA SmPC Table 3, ITT, Cox stratified by region; version chain DECIDED on the regulator's table (article full text not open) |
| Hospitalization for heart failure | k 1, 1.00 (0.83-1.20) | k 3, 0.8929 (0.5434-1.4672) | OMNeON 20/2092 vs 33/2100, HR 0.60 (0.35-1.05) from the verbatim CC-BY publication; CARMELINA 209/3494 vs 226/3485, HR 0.90 (0.74-1.08) from the accepted manuscript (one-sentence excerpt committed; the manuscript itself stays local) |

Final check on this state: 32/32 rebuilt; gate 25/32 (7 designed holds: 5 pages with OPEN notices, 2 pre-existing
HARMS_INCOMPLETE); served diff vs 7e70759a: 5 topics / 7 outcomes moved, each with exactly one OPEN notice and no
notice without a move. The signed 2026-09-20 DPP-4 HHF notice is kept unchanged.

### Cascade hardening
`_get` refuses any URL that is not http(s) to a public host, directly or by redirect (REFUSED_NONPUBLIC_HOST): a
DSpace repository advertised `citation_pdf_url` http://localhost:4000/... and a lane's cascade requested it (it
failed harmlessly; the guard makes it impossible).

## Codex acquisition lanes (2026-09-27, running)
- Two sparse detached worktrees `F:/mh-lanes-wt/acq-a`, `acq-b` (13 MB each: harness/, the cascade script, topics/,
  protocols/, evidence/acquisition_cascade/, docs/*.json); lane files excluded via info/exclude (`**/*.log`, .lane/).
- Worklist: 640 served rows (REPORTED_UNRESOLVED 104, NOT_YET_RETRIEVED 137, RETRIEVED_NOT_REPORTED 399 not on a
  verbatim abstract), 261 distinct reports, 31 topics, split by load. Codex runs the cascade (open routes only) and
  writes `.lane/RESULT.json`; it does not commit.
- Verification (`verify_lane`): document hash = lane's claim = HELD.json; span occurs in the held bytes; every value
  is a token inside the verified span; an absence names coverage the lane actually holds; request hosts audited.
  Proven on planted rows (wrong value, paraphrased span, wrong hash, absence without the abstract held: each refused;
  the true row passes).
- Known: Codex's global AGENTS.md made both lanes READ F:/ProjectIndex/INDEX.md and the E156 workbook at start,
  despite the brief. The sandbox confines writes to the worktree; reads outside it are a brief violation to fix at
  the next launch.

### Lane round 1 results (both lanes exited 0; 640 rows answered)
- Lane verdicts: FOUND 60, REPORTED_NOT_EXTRACTABLE 245, NOT_REPORTED 232, NOT_HELD 103. The lanes' NOT_REPORTED verdicts
  are NOT imported as claims: the harness re-derives every state from the coverage of what is held.
- **34 of 60 FOUND rows verify** against the held bytes; 26 do not, and none of those shows a wrong number. The
  failures are: numbers written as words ("five (out of 12)"), zero-event sentences whose denominators come from
  elsewhere, spans cut at "vs." by the lane's own sentence splitter, and PDF tables with no machine-readable header.
  All 60 are in `evidence/acquisition_cascade/LANE_CANDIDATES.json` with their verification outcome.
  **None is admitted.** Admitting one is a served-number change (notice plus signature).
- The verifier found and fixed two of its own defects before relying on it:
  - it rejected ".55" (journals that drop the leading zero);
  - a heredoc turned `\b` into a backspace byte, so the table-header path never matched.
  Plants: a wrong value, a paraphrased span, a wrong hash, an absence without the abstract held, a wrong header
  denominator, and a denominator present elsewhere in the paper but not in the table's header each fail; true rows
  pass.
- Merged into this branch:
  - 444 held JSON records (Europe PMC records carrying the verbatim abstracts, and ClinicalTrials.gov results), with
    their HELD.json entries;
  - 1,758 attempt lines.
  The lanes' 34 PMC XML full texts stay local, with `licence_detected` recorded in HELD.json; none is both CC BY/CC0
  and the witness of a verified row. PDFs and HTML are never copied.
  The merge refuses to run twice. It did run twice once and doubled the attempt lines; that was caught by line count
  and restored before anything was committed.
- Two repository pages advertised `citation_pdf_url` on a local host (localhost:4000, *.cpd.local). The requests
  failed harmlessly; the cascade now refuses them (REFUSED_NONPUBLIC_HOST).

### Rebuild on the word-level classifier and the held verbatim abstracts (all 32 topics)
- All 32 rebuilt. Every review.json, CERTIFICATE.json, EXECUTION_RECORD.json and page was checked present and
  parseable: an exit code is not the probe.
- Gate 25/32; the 7 refusals are the same designed holds.
- Served diff vs 7e70759a: the same 5 topics and 7 outcomes move, each with one OPEN notice; no pooled state change.
- Absent-row states vs 9727c3d8/22240c2d:
  - 514 absences move from UNVERIFIED to VERBATIM coverage (the lanes' verbatim abstracts);
  - 5 false ALTERED grades return to VERBATIM;
  - SOUL (40162642) GI adverse events and discontinuation move RETRIEVED_NOT_REPORTED → NOT_YET_RETRIEVED: the
    cached abstract is abridged, so the page no longer says the publication omits them;
  - CoDEX (32785710) SAE moves NOT_YET_RETRIEVED → RETRIEVED_NOT_REPORTED: its abstract is now verified verbatim, so
    the absence is scoped, with coverage named.
- `scripts/verify_lane_result.py` is now in the repository, with `tests/test_verify_lane_result.py`. It plants 9 XML
  and 4 PDF cases; the PDF cases skip visibly where the local-only manuscript is absent. It verifies PDF spans
  against its OWN pypdf page text, with header and row on the same page; HTML against tag-stripped text; XML
  against raw bytes and the same table's <thead>.

### Lane round 2 (stopped by the disk gate, as designed)
Free space on F: fell from ~1.4 GB to ~0.3 GB during the rebuild. The lanes hold about 120 MB, pytest about 1 MB,
and my scratch files are unchanged, so the cause is outside this lane's writes (not identified; nothing I did not
create was deleted).
- Lane B stopped before any work.
- Lane A re-examined its 13 failed FOUND rows (7 FOUND, 4 REPORTED_ZERO_EVENTS, 2 REPORTED_NOT_EXTRACTABLE per the
  lane) and stopped before fetching.
- Resume point: acq-a/.lane/RESULT_R2.json `resume_at`. The lane outputs are not yet verified or merged.
- Lane A round 2, part A (before the disk gate): all 11 of its claims verify (7 FOUND, 4 REPORTED_ZERO_EVENTS).
- Verifier corrections found while checking lane output:
  - REPORTED_ZERO_EVENTS rows were marked ok with NO check. The verifier only examined FOUND and NOT_REPORTED. Every
    other verdict is now `ok: null` (NO_CLAIM_CHECKED), never a pass.
  - A zero-event row now needs a span that states zero and a span of its own for each arm size.
  - PMC HTML tables (`<table><thead>`) are read like JATS XML tables.
  - Arm sizes quoted with markup are matched in the raw bytes.
  - For a table row, an arm size must lie inside the SAME `<table>`.
  - Thin-space thousands ("10 033") are read as numbers.
  - Planted: a zero not stated, no arm span, a wrong arm size, an arm span from another table, and one from outside
    the table in a synthetic Lancet-style control each fail; true rows pass.
- **Candidates now: 60, 48 verified (44 FOUND, 4 zero-event) across 10 topics** (probiotics 18, DOAC-VTE 8,
  tocilizumab 8, balanced crystalloids 4, DPP-4 4, GLP-1 2, and one each in 4 others). One entry per
  (topic, outcome, trial); a later round supersedes an earlier one (11 did). None admitted.

### Lane round 3: concordance of the 48 verified candidates (no network), and the admission queue
- Codex judged each verified row against its topic's protocol: endpoint, timepoint, population, design, report role,
  and whether the review's current exclusion reason still applies. Every judgement carries verbatim spans.
- Span check (`evidence/acquisition_cascade/LANE_CONCORDANCE.VERIFIED.json`): every protocol, source-definition and
  timepoint span is found verbatim. 22 population and 4 design fields are unsupported: labels were written, not
  quotes.
- Judgements: endpoint EXACT 24, UNCLEAR 24; timepoint SAME 12, UNCLEAR 35, DIFFERENT 1; report role PRIMARY 39,
  COMPANION 9; the current exclusion reason no longer applies for 37.
- `evidence/acquisition_cascade/ADMISSION_QUEUE.json`: **TIER_1 2, TIER_2 15, TIER_3 31. NOTHING ADMITTED.**
  - TIER_1 = numbers verified, endpoint EXACT, timepoint SAME, reason removed, every span found. Both TIER_1 rows are
    tocilizumab 28-day all-cause mortality, and both were checked by hand against the held text:
    - TOCIBRAS (33472855): "Mortality up to 28 days" 14/65 vs 6/64, OR 2.70 (0.97-8.35); the primary analysis is
      intention-to-treat. Held CC-BY PMC XML.
    - CORIMUNO-TOCI-1 (33080017): 7 vs 8 deaths at day 28, **adjusted** HR 0.92 (0.33-2.53), ITT. The abstract gives
      no arm denominators, so admitting it also needs a decision on pooling an adjusted HR with count-based rows.
  - Five more tocilizumab 28-day mortality rows are TIER_2 (EXACT, timepoint SAME, reason removed; only a population
    or design span unsupported).
  - Admitting the tocilizumab rows would change that review's PRIMARY served result: a notice and Mahmood's
    signature first.
- **Codex read F:/ProjectIndex/INDEX.md and F:/E156/rewrite-workbook.txt in rounds 1, 2 and 3.** The briefs forbid
  it, and round 2 onwards forbid it by name. The reads come from Codex's global AGENTS.md, which a brief does not
  override. The sandbox stops writes outside the worktree; the reads are a standing breach. I have not edited the
  global Codex config: that is Mahmood's call. Options: a lane-local CODEX_HOME, or removing that instruction from
  the global AGENTS.md.

## Round 2026-09-27 (late): empagliflozin-HFpEF, esketamine, finerenone and GLP-1 fixtures

### Root cause found on the way: registration records lost their identity
`design_key.registry_designs()` merged each cached AACT design row into the SHARED CT.gov record object. The design
row's own `id` (the AACT designs row id, e.g. 227983957) overwrote the trial's NCT id. From that point in the build
onward, every registration record in every topic was keyed by a database row id. Two consequences:
- **Lifecycle.** The held AACT dates were never found, and an empty status defaulted to "completed". EMPA-PRED
  (RECRUITING, planned completion 2030-12-31) was served as "eligible, completed, awaiting results". FineCaRe and
  NCT07775846 (planned 2028/2029) made the finerenone pool read "incomplete".
- **Identity.** The identity lookup failed and fell back to the row id. So a registration's `trial_family_id` was its
  NCT while its publication's was the acronym: one trial, two families. It now follows the identity module's own key.
  The HM3 control declares every changed field row by row (`other_fields_changed`, before and after), and its test now
  refuses any undeclared field change on a declared row. It used to check only decision, rule and reason.

Fixes:
- **Records** are copied, identity keys are never overwritten, and the design row id is kept as `design_row_id`.
- **`harness/lifecycle.py`:** `recruitment_status`, `completion_date`, `planned_vs_actual_completion` (the registry's
  own date type first, then the source date) and `source_date`. A planned date never yields COMPLETED; an UNKNOWN
  status is never "completed".
- **Published trials** read "completed, results available" whatever their registry status, which is still shown.

The rebuild moved no pooled number through this fix. Two further registrations are now held UNRESOLVED by the
protocol-conflict rule: NCT05735197 (sglt2-ckd, masking SINGLE) and NCT07143136 (colchicine-secondary-cv, masking
NONE). Both were screened in by the "placebo implies blinded" default, and neither was pooled.

### Empagliflozin-HFpEF
- **EMPA-PRED:** ONGOING, PLANNED 2030-12-31. `awaiting_classification` (A-PROTOCOL-CONFLICT): registry masking
  SINGLE against a double-blind protocol, and "Empagliflozin 25 MG" against the protocol's "Empagliflozin 10 mg
  daily" (a verbatim protocol span in the topic config).
- **EMPERIAL** (PMID 33351892): both registrations linked, Reduced NCT03448419 and Preserved NCT03448406. The Reduced
  NCT was first guessed wrong, answered 404, and was then confirmed by the registration's own title.
  - Preserved's composite is RETRIEVED_NOT_REPORTED from its held registry results; this replaces
    SOURCE_NOT_RETRIEVED, and the old state is kept as `supersedes`. The same fix applies to DETERMINE-Preserved.
  - Exploratory harms: SAE 20/157 vs 29/158 is bound to the posted registry results. Any AE (79/157 vs 93/158) and AE
    leading to discontinuation (9/157 vs 8/158) stay REPORTED_UNRESOLVED: Table 4 is not openly held (Europe PMC not
    OA; Unpaywall no open location). The relayed numbers are recorded as relayed, never rendered as data.
- **EMPA-VISION** (PMID 37070436, CC BY; NCT03332212): a cohort family. The HFpEF cohort (18 vs 18) is eligible on its
  own population, and the HFrEF cohort (17 vs 19) cannot veto it. The whole-trial 72 is held out of any pool. It is
  still a known-missing entry: the search never found it.

### Esketamine
- Mahmood's two messages are recorded verbatim, attributed, relayed via Dispatch and labelled RETROSPECTIVE. They are
  implemented as the field `oad_initiation`, never a keyword:
  - TRANSFORM-1, -2, -3 and Chen: at randomisation.
  - Takahashi: lead-in, continued unchanged. It qualifies as a disclosed design difference, and it is the sensitivity
    analysis's only member.
- **Takahashi is held UNRESOLVED, not INCLUDED.** The 2026-09-16 phase-2 amendment excludes it. That amendment says
  the exclusion "was declared in the protocol", but the registered protocol (5e2b43c6) has none, and the ruling covered
  the OAD, not the phase. Pending: Mahmood's phase-2 ruling and a multi-arm dose selection.
  **Served consequence: none yet** (Day-28 MADRS k=3). Handoff: `outputs/handover/lanes/TO_OC_TAKAHASHI_ESKETAMINE.md`.

### Finerenone
- **FIGARO Table 2** is bound: hyperkalaemia 396/3683 vs 193/3658, and discontinuation due to hyperkalaemia 46 vs 13.
  Both outcomes go from no result to k=1; notices OPEN.
- **FIDELIO:** Table 2 is not openly held (403 twice). Its rows stay REPORTED_UNRESOLVED on their own evidence.
- **FIVE-STAR** (PMID 41351003; 102 randomised; CAVI) and **CONFIDENCE** (judged per arm pair: A vs C eligible) are
  known-missing entries with held sources.
- **FIDELITY** is a pooled report of the two families, never a third trial, and never imported.
- **Completeness** is claimed per outcome: kidney composite PROVISIONAL; hyperkalaemia and discontinuation INCOMPLETE.

### GLP-1 (signature item)
- **ELIXA:** a structured SOURCE_EFFECT_CONFLICT (narrative (0.887, 1.172) vs Table 8 (0.89, 1.18), one page). The
  narrative governs, on computed evidence. The generator refuses to make a bundle while a conflict is undecided, and the
  notice discloses the conflict with both diagnostics.
- **FREEDOM-CVO:** the Table 18 pooled row (same numerator 85) is named "not this row".
- **Source hierarchy:** a precedence order, not a prohibition. PIONEER 6 AE leading to discontinuation, 184/1591 vs
  104/1592 (registry, level 3), takes the outcome from k 1 to 2; notice OPEN. GI adverse events is REPORTED_UNRESOLVED.

### Known limitation found this round
A row whose REPORTED_UNRESOLVED state rested only on the outcome's "reported but not extracted" flag drops to
"retrieved, not reported" once the outcome gains its first pooled row. FIDELIO's rows now carry their own evidence;
other topics have not been swept for this.

## Round 2026-09-28: melatonin and metformin-PCOS fixtures

### Melatonin
- **Wade 2011** (21091391): a companion of Wade 2010 in family NCT00397189, never a second trial.
  - Its Table 3 all-adult result (18-80: -14.6 (43.9, 360) vs -7.9 (50.9, 362); 55-80: -15.4 vs -5.5) is **not openly
    held** (Curr Med Res Opin: Europe PMC not OA, Unpaywall no open location). It is a RELAYED version in chain
    NCT00397189:SOL-diary-3wk.
  - Governing is **PENDING**: the protocol itself adopted the pre-specified 65-80 subgroup (served: -19.1 (47.3, 137)
    vs -1.7 (47.8, 144)). Whether the all-adult result should govern once held is Mahmood's protocol decision.
  - Wade 2010's own Table 3 has no all-adult row: its other block is the low-excretor subgroup (86 vs 86).
- **Lemoine** (22346363): a post-hoc pooled analysis of four already-counted RCTs (18036082, 19584739, 20712869,
  17875243); its safety set also pools open-label studies.
  - Now X-DEDUP, linked to its constituents, and its pools are never imported.
  - Its pinned HM3 harm decision is declared superseded as LINKED_NOT_A_TRIAL (a new supersession kind: the report must
    be X-DEDUP and must be no trial row at all).
- **ABSTRACT_ONLY full texts:** a committed `ft_` file whose publisher withholds the XML body is never handed to a
  consumer as a full text. That is 14 of 61 corpus files, including Almeida Montes, Moll and CARMELINA. Almeida Montes'
  funding row had said "full text scanned". The page lists these files.
- **Wade 2010 arm labels:** PDF Table 8 (394 = placebo) vs PDF Table 9 and the held XML (394 = melatonin).
  - ADJUDICATED only through the registry's posted results (flow and AE groups: Circadin 394, Placebo 395). This is
    computed, never declared.
  - Same-article corroboration does not count, and nothing is auto-flipped. Plants cover same-article-only, none at
    all, and a flipped pooled row.
  - PDF Table 8 is not held by this lane: the BMC PDF location answered a 3 KB non-PDF page.
- **Luthringer 2009:** 3-week randomised period; "outcome reported; analysis-ready extraction pending", no SDs imputed.

### Metformin-PCOS
- **Moll discontinuation:** REPORTED_UNRESOLVED on the abstract's risk difference. The reason audit no longer calls it
  "value absent": a cited span with a numeric result held verbatim means a value present in another estimand class.
  - The full report's 18/111 vs 6/114 is in `docs/relayed_values.json` as relayed, NOT held (BMJ 403, PMC bot-check;
    the `ft_` file is abstract-only). It is shown beside the discontinuation row only, never as data.
  - The pinned HM3 entry is NOT edited. A first attempt edited it; the HM3 contract test caught that, and it was
    reverted.
  - The GI row is SIGNAL_SPURIOUS, so it reads "not reported", never "reported".
- **Family invariant** (`harness/family_invariant.py`, blocking): every pooled input belongs to exactly one family, and
  the contributing count equals the number of distinct families pooled.
  - Trials with no registry link get a stable identity, `PMID:<primary report>`, and are counted: metformin now has 3
    contributing families for 3 inputs.
  - 0 violations across all 32 topics. Family denominators rise where publication-only trials were dropped (probiotics
    +106).

### Verification
- 32/32 topics rebuilt. No served number moved this round; Lemoine left melatonin's declared-absent lists.
- Gate 23/32 (the same 9 designed holds). Served diff vs 7e70759a: 10 moved outcomes, each with one OPEN notice.
- GLP-1 signature bundle regenerated: **8244e2c9**.
- 551 tests passed, 0 failed, in a per-file run. The first combined run crashed (exit 127, memory) after two failures;
  both were real (the HM3 contract and pages tests) and are fixed. A pass count taken through `tail` also hides
  "N failed, M passed" lines, so the grep for "failed" is explicit.

## Round 2026-09-28b: NOAC-AF and PCSK9 fixtures

### NOAC-AF (generator: `outputs/handover/noac_sources/make_noac_fixtures.py`, idempotent)
- **RE-LY stroke/SE, version chain `RE-LY:stroke-SE:150mg`, governing DECIDED on v3.**
  - Versions:
    - v0: NEJM 2009 abstract, RR 0.66 (0.53-0.82), with counts 134 vs 199 relayed.
    - v1: FDA PRADAXA label, Oct 2010, Table 4: 134 vs 202, HR 0.65 (0.52, 0.81).
    - v2: the investigators' "Newly identified events in the RE-LY trial" (PMID 21047252). NOT held (NEJM 403, not OA).
    - v3: FDA label, Jan 2024, Table 11, "Randomized ITT": 135 vs 203, HR 0.65 (0.52, 0.81).
    - v3b: EMA SmPC Table 22, which reproduces v3.
  - The served row (`dose_selection.json`, 150 mg) is now 0.65 (0.52-0.81). Pool 0.8069 -> 0.8040, and the interval
    stays below 1. A plant confirms that serving 0.66 under the DECIDED chain raises VERSION_SUPERSEDED_SERVED.
- **Major bleeding recovered (k 0 -> 4, 0.8544, 0.6439-1.1336).**
  - RE-LY: bound to FDA 2010 Table 2, 399 vs 421, HR 0.93 (0.81, 1.07), randomised. Chain PENDING:
    - the original 375 vs 397 carries the same tuple with different counts (an identical effect is not an identical
      version);
    - the EMA SmPC gives 409 vs 426 with no HR;
    - FDA 2024's 0.97 (0.84, 1.12) is a different population (treated patients, on treatment + 2 days).
  - ROCKET-AF: bound to the FDA XARELTO label Table 5, 395 vs 386, HR 1.04 (0.90, 1.20), on treatment plus 2 days
    (safety population). A plant confirms the major + CRNM composite 1.03 (0.96-1.11) never binds as major bleeding.
  - Two root causes fixed:
    - `target_endpoint._keyword_family_match`: an "-ing" keyword now also matches its whole-word event noun ("Major
      bleed"; stem of 4 or more letters).
    - `compat_check._derive_analysis_set`: a BOUND hand row keeps its declared analysis set instead of the abstract's
      per-protocol efficacy population.
- **Edoxaban phase II** (`docs/registry_publications.json`, `harness/registry_publications.py`, witnesses fail closed).
  Each publication is a report of its registration, never a second trial:
  - Weitz 2010 -> NCT00504556: abstract only; NOT_YET_RETRIEVED.
  - Chung 2011 -> NCT00806624: stroke/SE REPORTED_ZERO_EVENTS ("No thromboembolic events occurred in any treatment
    group"). The publication says 235 randomised vs the registry's 234; recorded, not resolved.
  - Yamashita 2012 -> NCT00829933 (J-STAGE PDF held locally, excerpt committed):
    - stroke/SE: zero events in the compared 60 mg and warfarin arms (the one event was in the 45 mg arm);
    - major bleeding: 2/130 vs 0/125, EXTRACTED_NOT_ADMITTED.
- **J-ROCKET AF** (NCT00494871, PMID 22664783) goes in `docs/known_eligible_missing.json`: an independent phase III
  trial, absent from the inventory, NOT pooled.
  - The three held analyses: PP on treatment 0.49 (0.24-1.00); ITT including 30-day follow-up 0.82 (0.46-1.45), the
    candidate; ITT on treatment 0.48 (0.23-1.00).
  - Compatibility decisions are pending (15 mg dose; INR 1.6-2.6 for patients aged 70 or over). The page is STALE for it.

### PCSK9 (generator: `outputs/handover/pcsk9_sources/make_pcsk9_fixtures.py`, idempotent)
- **GLAGOV MACE**: never "not reported". NOT_YET_RETRIEVED via the acquisition state MAIN_RESULT_NOT_HELD (the new
  rule in `result_status`).
  - Table 4 is not held: JAMA not open; Amsterdam UMC PDF 403; ruj.uj.edu.pl URLError twice (recorded); the registry
    posts no MACE.
  - 59/484 vs 74/484 is relayed, not held.
  - COMPONENT_SUM_AS_COMPOSITE (blocking) stops component rows being summed into a patient composite.
- **ODYSSEY LONG TERM MACE**: the post-hoc refusal stands; the row is EXTRACTED_NOT_ADMITTED.
  - The reason auditor had called it REASON_FALSE_VALUE_HELD. It is now REASON_TRUE when the span carrying the value
    itself says "post hoc"; a plant confirms a span without "post hoc" stays falsifiable.
  - `outcome_post_hoc_not_pooled` is a typed refusal only on a span that says post hoc (fail closed).
  - POST_HOC_POOLED is blocking.
- **Safety rows, from the trials' own Table 3s** (FOURIER UNIGE published version; ODYSSEY Szeged accepted manuscript;
  both held locally, committed as TABLES excerpts):
  - injection-site: FOURIER 296/13,769 vs 219/13,756, ODYSSEY 360/9,451 vs 203/9,443 (k 0 -> 2);
  - AE -> discontinuation: ODYSSEY 343/9,451 vs 324/9,443 (k 0 -> 1).
- **Restricted discontinuation rows** (`docs/outcome_restrictions.json`, `harness/outcome_restriction.py`):
  - FOURIER's treatment-attributed 226 vs 201 is EXTRACTED_NOT_ADMITTED, attribution TREATMENT_ATTRIBUTED.
  - OUTCOME_RESTRICTION_MISMATCH (blocking) refuses that row, and ODYSSEY's 26 vs 3 injection-site discontinuations,
    for the unrestricted outcome.
  - The reason auditor now reads the held document a refusal cites, and recognises table count cells "n (x.x)".

### Notices (OPEN, reason-locked; history untouched)
- Four new notices were appended to `docs/result_changes.json`:
  - NOAC stroke/SE (the RE-LY governing change plus the J-ROCKET inventory change: two changes, signable separately);
  - NOAC major bleeding;
  - PCSK9 injection-site;
  - PCSK9 AE -> discontinuation.
- Caution: `scripts/refresh_result_change_notices.py` DROPS history notices whose change predates the base commit
  (probiotics, tocilizumab, tranexamic acid) and would overwrite signed ones. It must not be run to rewrite the file;
  append new notices instead.

### Decisions for Mahmood
- Signatures for the four notices.
- RE-LY major bleeding: keep the randomised 0.93, or adopt the on-treatment 0.97 to match the other three trials.
- J-ROCKET AF compatibility: the dose and the INR target.
- Whether to admit the phase II edoxaban trials.
- GLAGOV: once Table 4 can be held, a compatible HR for the first-MACE counts.

### Latent debt surfaced by the FULL suite (and what was done)
The previous round's "551 passed" covered a 53-file SUBSET. This round ran all 240 test files, one file at a time,
and found failures accumulated by earlier rounds of this lane. They are fixed at the source, except one.
- **RoB sensitivity re-pooled on the declared estimand (OR), not the served scale (RR).**
  - COVID's "full" stratum read 0.8288 vs the served 0.85 once the CoDEX count row entered the pool.
  - `rob_sensitivity.sensitivity` now uses `result.scale`.
- **RoB and arm-contrast coverage were missing for newly pooled trials** (COVID CoDEX 32876695, DPP-4 TECOS
  26052984). Added by `scripts/rob2_build.py --write` and `scripts/arm_contrast_build.py --write`: purely additive,
  no existing assessment changed.
- **The override audit was out of 1:1.**
  - 8 new override rows were added, each with its judgement.
  - 7 superseded rows were MOVED to `docs/evidence/override-audit-2026-09-14/superseded.json`, with what replaced
    them; none was deleted.
  - The HM2 contract now accepts a row that is declared superseded.
- **Notices lacked two required sentences.** "the numbers are not asserted wrong" and "eligible evidence awaiting
  adjudication" were missing on 14 OPEN notices of this lane. Appended; no signed notice was edited.
- **Two tests pinned old behaviour, now rewritten as requirements.**
  - The TECOS test still asserted "declared absent". The requirement is now that, if TECOS is pooled, it is the SmPC
    3-point row, never the 4-point 0.98.
  - The NOAC effect label expected "3 HR + 1 RR". The requirement is now that the label never hides a mix; there are
    now 4 HR.
- **Stale derived renders:** the fix ledger and the fix-state lines were re-rendered.
- **The one new regex site now has plants and a labelling spec** (`regex_layer`; N_SITES 375 -> 376).
- **OPEN, not fixable here:** `test_error_rate_is_fresh_against_current_pooled_population`. The error-rate census
  must be re-run for the newly pooled numbers: a blind re-extraction (`scripts/error_rate_compare.py` +
  `error_rate_pass2.py`), then hand adjudication of each mismatch. It is a measurement, not a code fix.

### Verification (final state)
- 32/32 topics rebuilt after the last harness change.
- Gate: 21/32 pass. The 11 designed holds are 9 pages with OPEN notices and 2 HARMS_INCOMPLETE pages.
- Served diff vs 7e70759a: 14 moved outcomes, each with exactly one OPEN notice; no notice without a move.
- GLP-1 signature bundle regenerated: **5160a1d6**. HM3 supersession regenerated.
- Full per-file suite: 240 files, 239 green, **4679 passed, 1 failed** (the error-rate census above).
  - `test_architecture_identity` needs 12m50s alone. The first run's 1500 s limit was hit under contention.
