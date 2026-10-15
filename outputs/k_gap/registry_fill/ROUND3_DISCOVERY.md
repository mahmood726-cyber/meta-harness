# Round 3: source discovery + new adapters (15 Oct 2026)

Target: the **133** G1-missing trials in the 14 topics with a missing eligible trial (Captain's G1 table).

## 1. Discovery probe (32 stratified trials x 59 sources; 12 parallel Codex jobs, read-only)

Sample: seed 20261015, at least 1 per topic, proportional otherwise. Each (trial, source) pair was recorded with a
status, URL, stated terms and a verbatim snippet of at most 200 characters (`discovery/`). Every source was covered
32/32. No number from these jobs enters any dataset.

**18 of 32 trials** have per-arm TARGET data openly readable somewhere.

| source | target | other per-arm | named, no data | blocked | not found / n.a. / error |
|---|---|---|---|---|---|
| Europe PMC (full text / abstract) | **11** | 12 | 3 | 4 | 2 |
| Cochrane (secondary; Wiley copyright) | 7 | 0 | 3 | 13 | 9 |
| ClinicalTrials.gov posted results | 4 | 3 | 12 | 0 | 13 |
| Primary paper / OpenAlex / Unpaywall OA copies | 4 each (overlapping) | 2 | 1–9 | 15–24 | 0–4 |
| EudraCT (EU CTR) results | 1 | 2 | 2 | 0 | 27 |
| NICE, PBAC, G-BA, PMDA, FDA EUA memo, Drugs@FDA reviews, Roche lay summary | 1 each (mostly EMPACTA) | 0–2 | 0–8 | 0–4 | rest |
| all other regulators, HTA bodies, evidence reports, sponsor registers, other registries | 0 | 0–2 | 0–19 | 0–32 | rest |

The zeros are mostly **front-door reach, not absence**:
- Bot challenges: ISRCTN, ANZCTR, CTRI, EMA search, medRxiv/bioRxiv, CDA-AMC, AHRQ, Cochrane, Bayer. FDA's site search sends
  scripts to an abuse-detection page.
- Account or terms gates: EMA clinical data portal (EMA account), Health Canada (binding terms; decision 11).
- JavaScript-only search: MHRA, WHO.
- 403 refusals: NIHR, Epistemonikos.

None of these was bypassed.

## 2. New and fixed adapters (all deterministic; Codex-built, reviewed, planted)

| adapter | live result over the 133 |
|---|---|
| FDA: supplement reviews from the Drugs@FDA overview; reviews before labels; failure reason recorded | named 11 trial-document pairs; typed 0; 6 pairs need a two-reader model read |
| EMA (round 1 route) | named 8; typed 0; 7 need a two-reader model read |
| CDA-AMC via NCBI litarch (sanctioned bulk archive; CC BY-NC-ND, typed-only) | 27 reviews held; named 2 (FAIR-HF, EFFECT-HF); per-trial sponsor data **redacted** (9,822 blocks in the Ferinject HF review); admitted 0 |
| IQWiG (codes found in G-BA download filenames) | named 5 (pcsk9); typed 0 |
| Health Canada listing (metadata only; terms never requested) | submissions listed for **12 of 14 topics (114 of 133 trials)**, e.g. ACTEMRA sNDS 2022-10-13 (COVID), PRALUENT, MYINFLA, VASCEPA; contents behind the terms (Mahmood's act) |
| EudraCT results (new) | 53 NCTs -> 12 with a EudraCT number -> 8 with results -> 0 bound (below) |
| table-failure diagnostic (counts only, D8-safe) | 29 trials with a reachable held open copy: 17 NO_OUTCOME_TABLE, 7 NO_ARM_HEADER, 2 ARM_HEADER_NOT_MAPPED, 2 NO_TABLE, 1 binds (SMART: a cluster design, refused by the tracker) |
| sentence reader (new; counts only) | 120 held copies, 466 outcome sentences, 0 candidates. The CC-licensed copies show why: they are protocols, secondary analyses and substudies, not the primary-results papers |

Six defects were found by running on live data, each fixed with a plant:
1. The litarch list's Latin-1 byte left every drug with no CADTH document.
2. IQWiG codes sit in link filenames, which text extraction drops.
3. The Health Canada parser knew only synthetic header names.
4. The EudraCT parser knew only synthetic HTML.
5. "No public results" pages were classed as parse failures.
6. Overlapping runs interleaved JSON writes; now locked and merged on write.

## 3. Candidates found, with named divergences (none bound)

| trial (topic) | source | value as printed | divergence from the topic |
|---|---|---|---|
| REMDACTA (tocilizumab) | EudraCT 2020-002275-34 | time to death to Day 28, HR 0.948 (0.65–1.39) | HR vs OR; mITT |
| EFFECT-HF (iv iron) | EudraCT 2011-000603-40 | first hospitalisation or death for worsening CHF, HR 1.76 (0.67–5.114) | composite with death; safety set; 24 weeks; the CHF-hospitalisation rate alone is printed as % only |
| EMPACTA (tocilizumab) | PMDA English review report (Public Data License 1.0); CT.gov; Roche lay summary | Day-28 all-cause mortality per arm + HR | mITT; CT.gov gives % only. **PMDA was skipped by Mahmood on 13 Oct** |
| PreToVid (tocilizumab) | EudraCT 2020-001375-32; PMC (CC BY) | 30-day survival, Cox HR | 30 days vs 28; HR vs OR; primary analysis uses a 90% CI |
| COVINTOC (tocilizumab) | PMC (Elsevier COVID-19 permission, not CC) | 28-day mortality by arm | mITT; identity still to be verified (identification queue) |
| ODYSSEY LONG TERM (pcsk9) | NICE TA393, G-BA | HR 0.52 (0.31–0.90) | **NOT_BOUND, Mahmood 15 Oct** (post hoc; safety population; on-treatment window) |

## 4. k gained (n of 133)

| source | PRIMARY_VERIFIED gained |
|---|---|
| FDA, EMA, NICE, PBAC, G-BA, IQWiG, CDA-AMC, Health Canada (listing), EudraCT | 0 |
| literature re-read (table diagnostic, sentence reader) | 0 |

**Topics fully matched: 0 of 19.**

## 5. Where the remaining k is (and what would unlock it)

1. **Health Canada CSRs:** 114 of 133 trials sit in topics with a listed submission. This needs Mahmood to accept
   the terms; even then it is typed-only (clause 3.4).
2. **EMA clinical data portal:** needs an EMA account (Mahmood); scope is narrow (2016–2022, COVID products, and from
   2023/2025).
3. **PMDA:** a review report found under Public Data License 1.0 gives EMPACTA per arm. The 13 Oct skip could be
   reconsidered (Mahmood).
4. **Second reader:** 13 FDA/EMA trial-document pairs need two readers plus an adjudicator. agy is out until 17 Oct;
   the Claude CLI's OAuth session has expired (Mahmood to sign in).
5. **Primary-results papers** are mostly paywalled (NEJM/JAMA/Lancet). The open copies we hold are protocols and
   secondary analyses. This is the structural limit of the literature route.
