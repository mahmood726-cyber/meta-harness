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
