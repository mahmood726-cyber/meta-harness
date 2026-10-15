# Screener instrument audit: C2, C3, C4

Fixed seed `20261015`; sample saved before cached full texts were opened. All 70 papers were independently read for design, RCT count and trial-ID attribution. Criteria and verdicts unchanged.

| First-failure criterion | Sampled | Exclusion CORRECT | Exclusion WRONG |
|---|---:|---:|---:|
| C2 | 20 | 16 | 4 |
| C3 | 30 | 13 | 17 |
| C4 | 20 | 19 | 1 |

Counts concern the named exclusion criterion, not final eligibility. All C2/C3/C4 judgments, verbatim excerpts, source locations, registry attributions and screener evidence for every paper are in `audit_result.json`.

C3 ambiguity: PMC12606885 says "Nine studies (27 RCTs)" in its abstract but "k = 9, 27 ESs" in results. The primary count retains CORRECT under the written fail-closed rule. Accepting nine RCTs as resolved would move one C3 case from CORRECT to WRONG. Two retracted pairwise RCT papers remain CORRECT C2 exclusions.

## Evidence for every WRONG exclusion

- **C3 - PMC7931800 (PMID 33681281)**: k=13. "A total of 13 RCTs were included in this meta-analysis." [Cached source](../cache/benchmarks/v1/PMC7931800.xml).
- **C3 - PMC13454307 (PMID 42577520)**: k=9. "Nine studies met the inclusion criteria." [Cached source](../cache/benchmarks/v1/PMC13454307.xml).
- **C3 - PMC12946738 (PMID 41767388)**: k=13. "This study analyzed data from 13 randomized controlled trials (RCTs) with 1,333 participants" [Cached source](../cache/benchmarks/v1/PMC12946738.xml).
- **C3 - PMC13026131 (PMID 41897256)**: k=20. "Twenty randomized controlled trials involving 1067 participants were included." NMA plus explicit conventional pairwise synthesis. [Cached source](../cache/benchmarks/v1/PMC13026131.xml).
- **C3 - PMC13194511 (PMID 42181548)**: k=8. "Eight randomized controlled trials (RCTs) with 755 participants were included." [Cached source](../cache/benchmarks/v1/PMC13194511.xml).
- **C3 - PMC13334920 (PMID 42172285)**: k=6. "Six RCTs reporting on couples without severe male factor infertility were included." Six main-analysis trials; five additional trustworthiness-excluded studies only in sensitivity analysis. [Cached source](../cache/benchmarks/v1/PMC13334920.xml).
- **C3 - PMC12975744 (PMID 41822303)**: k=11. "22 studies were included (11 RCT, 11 observational studies" Separate pairwise RCT synthesis: 11 RCTs in review, 5 in meta-analysis; both in eligible range. [Cached source](../cache/benchmarks/v1/PMC12975744.xml).
- **C3 - PMC13357176 (PMID 42444654)**: k=13. "Thirteen randomized controlled trials involving 527 children were included" [Cached source](../cache/benchmarks/v1/PMC13357176.xml).
- **C3 - PMC12079849 (PMID 40369457)**: k=19. "We included 19 RCTs involving 1,803 participants." 26 manuscripts are reports of 19 trials, not 26 RCTs. [Cached source](../cache/benchmarks/v1/PMC12079849.xml).
- **C3 - PMC12241801 (PMID 40641927)**: k=3. "There were three RCTs (13, 15, 17, 22–24); the rest were cohort studies" Mixed cohort/RCT synthesis; abstract does not state RCT as included design. C3 assessed independently: explicit three RCTs. [Cached source](../cache/benchmarks/v1/PMC12241801.xml).
- **C3 - PMC12662476 (PMID 41327742)**: k=14. "Fourteen published RCTs" [Cached source](../cache/benchmarks/v1/PMC12662476.xml).
- **C3 - PMC13283822 (PMID 42338516)**: k=14. "Fourteen randomized controlled trials were pooled for analysis." [Cached source](../cache/benchmarks/v1/PMC13283822.xml).
- **C3 - PMC12355156 (PMID 40822250)**: k=6. "The final analysis included 6 studies" Count as stated; no outcome-specific count substituted. [Cached source](../cache/benchmarks/v1/PMC12355156.xml).
- **C3 - PMC10955066 (PMID 38516003)**: k=3. "five studies (three RCT and two observational studies)" Mixed observational/RCT pooled analysis; C3 count explicitly three. [Cached source](../cache/benchmarks/v1/PMC10955066.xml).
- **C3 - PMC8192720 (PMID 34122180)**: k=25. "Among the 25 RCTs" 25 included; 24 quantitatively synthesized; both in eligible range. [Cached source](../cache/benchmarks/v1/PMC8192720.xml).
- **C3 - PMC8076535 (PMID 33928022)**: k=8. "A total of eight randomized trials involving 1,349 advanced NSCLC patients with sensitive EGFR mutation were included in the meta-analysis." [Cached source](../cache/benchmarks/v1/PMC8076535.xml).
- **C3 - PMC12152056 (PMID 40493076)**: k=3. "In total, 1432 participants were included from the three trials" Included IDs: NCT04700345 MAGIC-MT; NCT04402632 EMBOLISE; NCT04410146 STEM. Ongoing trials are not included in k. [Cached source](../cache/benchmarks/v1/PMC12152056.xml).
- **C2 - PMC11688350 (PMID 39744133)**: "For most comparisons, the results were homogeneous in pairwise meta-analyses and network meta-analyses." "Randomized placebo-controlled trials (RCTs) examining the pharmacological prevention of adult migraine patients were included." Pairwise plus NMA, not NMA-only. [Cached source](../cache/benchmarks/v1/PMC11688350.xml).
- **C2 - PMC9654326 (PMID 36360901)**: "Randomized placebo-controlled clinical trials that used manual therapy as a sham treatment on subjects suffering from pain were included." 53 included reports/trials as stated; 48 quantitatively pooled. [Cached source](../cache/benchmarks/v1/PMC9654326.xml).
- **C2 - PMC7191827 (PMID 32349720)**: "Randomized controlled trials comparing LABA and LAMA were included" "We searched relevant randomized control trials (RCTs)" Abstract uses randomized control trials; body confirms design. [Cached source](../cache/benchmarks/v1/PMC7191827.xml).
- **C2 - PMC12708242 (PMID 41415558)**: "Trials comparing PD-1/PD-L1 inhibitors + nab-paclitaxel-platinum (experimental) versus chemotherapy alone (control) were included." [Cached source](../cache/benchmarks/v1/PMC12708242.xml).
- **C4 - PMC10011644 (PMID 36926026)**: k=6; all 6 included trials identified in Table 1: EUCLID: "NCT01732822"; ACTIVE A: "NCT00249873"; PLATO: "NCT00391872"; PHILO: "NCT01294462"; PRoFESS: "NCT00153062"; ePAD: "NCT01802775". Six included IDs in Table 1; NCT01864005 and NCT00396877 explicitly excluded. [Cached source](../cache/benchmarks/v1/PMC10011644.xml).

## Method and limits

Single-reader model audit, not blinded dual-human adjudication. Read cached abstracts and methods/results; inspect body/tables and embedded supplemental text for IDs. Quotes preserve source wording with whitespace normalized. Registry references, review registrations, excluded/ongoing trials and external supplemental files do not count. Mixed/non-RCT papers that reached C4 are recorded as earlier-gate discrepancies, not treated as a vacuous C4 pass.

| Component | Static or dynamic |
|---|---|
| Seed, sample sizes, written criteria | Static, specified before reading |
| Sample, hashes, counts | Computed from disk |
| Adjudications and quotes | Source-backed manual annotations |

Validation: **PASS** - seeded sample reproduced; 70 unique records; quote excerpts verified; XML hashes and PMID/PMCID identities match the screened input; candidate hash unchanged from before reading; preregistration hash matches frozen input. No commits or verdict changes.
