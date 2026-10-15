# Regulator / HTA dossiers, round 2 (15 Oct 2026)

Target: the **133** trials still missing across the **14** G1-unmatched topics that have a missing eligible trial
(Captain's G1 table on main; the other 5 unmatched topics have no missing eligible trial).

## 1. Why round 1 (phase 2) gave 0 — n of N = 133 per agency

| agency | topic has held text | trial named | outcome window in a held doc | window has numbers | typed row parsed | model read | admitted |
|---|---|---|---|---|---|---|---|
| FDA (labels + reviews) | 104 | 12 | 10 (prompt-open, read) | — | 0 | 10 | 0 |
| EMA (EPAR) | 126 | 9 | 9 (prompt-open, read) | — | 0 | 9 | 0 |
| G-BA / IQWiG Module 4 | 67 | 13 | 10 | 6 | 0 | n/a (typed-only) | 0 |
| NICE (round 2, widened) | 133 | 35 (was 20) | 15 | 14 | 0 | n/a (typed-only) | 0 |
| PBAC PSD (new) | 98 | 9 | 9 | 6 | 0 | n/a (typed-only) | 0 |

The dominant stop is **the trial is never named** (named 35 of 133 at best). Reasons, by count over the 133:
- **75 have no searchable name** (no NCT, no acronym, no sponsor code) — a regulator text cannot be matched to them.
- Only **15 are industry-sponsored**; the rest were never part of any marketing-authorisation or reimbursement dossier.
- FDA: held documents are mostly labels; medical/statistical reviews held with text are few, and 23 review PDFs have no
  text layer (scanned; OCR not available in this lane).

Two defects found in our own pipeline (not source limits):
1. **HR topics never had a deterministic regulator route.** `typed_first` tried regulator counts only for RR/OR/RD
   estimands. 7 of the 14 topics are HR (53 of the 133 trials), so for them a regulator / HTA document was never read
   deterministically. Fix in this PR: a typed HR-with-95%-CI reader (`regulatory_typed_effect`), pooled / global /
   meta-analysis statements refused.
2. **Mislabel.** For typed-only agencies (NICE, PBAC, G-BA) the decision read `NAMED_NO_WINDOW_WITH_OUTCOME_TERMS` even
   when outcome windows existed, because the window list was built only from prompt-open documents. Now
   `NAMED_TYPED_ONLY_NO_ROW_PARSED` where windows exist.

## 2. What the named windows actually contain (all real windows are in pcsk9-mace)

| trial | per-trial MACE in a primary sponsor / regulator document? |
|---|---|
| ODYSSEY LONG TERM | **Yes, two independent sponsor documents agree**: G-BA Module 4A alirocumab (2015-11-02) Table 4-20, MACE 26/788 placebo vs 27/1550 alirocumab; NICE TA393 Sanofi submission Table 18 + text, HR 0.52 (95% CI 0.31 to 0.90). Post hoc, **safety population** (>95% of randomised), **treatment-emergent period** (first dose to last dose + 70 days). |
| ODYSSEY FH I, FH II, HIGH FH, COMBO I | **No.** G-BA Table 4-18: "Endpunkt wurde nicht erhoben" (MACE not collected as an endpoint); Sanofi reports adjudicated MACE only **pooled** (TA393 Tables 51–52; EMA EPAR). A pooled row is never a trial row. |
| ODYSSEY JAPAN | Not named in any held document (its label NCT is a 404; decision 4). |
| PACMAN-AMI, GLAGOV, DESCARTES | Named in study-characteristic / lipid tables only; no per-trial MACE row. |
| tocilizumab (14 named in NICE TA971) | Named in the assessment group's study-characteristics table only; mortality pooled, no per-trial row. |
| statins elderly (CARDS, ASCOT-LLA, MEGA) | NICE guideline evidence review text: pooled meta-analysis results, no per-trial row. |
| omega-3 (GISSI-P, ORIGIN, ASCEND) | Cost-effectiveness text and a public-comment table of N / dose; no per-trial outcome row. |

Note on tier: NICE **guideline evidence reviews** and **MTA assessment-group reports** are themselves systematic reviews
(secondary). Only **company / sponsor submissions** (G-BA Module 4, NICE committee-paper company evidence, PBAC
sponsor data, FDA/EMA reviews of the sponsor's CSR) are primary for a trial.

## 3. k gained per source (n of N = 133)

| source | PRIMARY_VERIFIED gained | held pending a binding ruling |
|---|---|---|
| FDA reviews | 0 | 0 |
| EMA EPAR | 0 | 0 |
| G-BA / IQWiG Module 4 | 0 | (counts only; the topic estimand is HR) |
| NICE committee papers | 0 | 1 (ODYSSEY LONG TERM HR, section 4) |
| PBAC PSD | 0 | 0 |
| Health Canada | not attempted: binding click-through terms (Mahmood's act; clause 3.4 forbids model use) | |
| EMA clinical data portal (Policy 0070) | not attempted: registration required | |
| CDA-AMC (CADTH) | not attempted: Cloudflare bot challenge (never solved) | |

**Topics becoming fully matched: 0 of 19.**

## 4. Re-run with the HR route and the relabel (NICE, PBAC, G-BA full fill on all 14 topics; FDA/EMA report-only)

Run over 132 of the 133: Semler (SALT) is skipped by the fill because phase 1 marked it admitted, while the tracker
refuses it as a cluster design (decision 3); it is reported, not silently dropped.

| agency | not named | named, no outcome window | named, typed-only window, no row parsed | named, model read, not gated | typed HR held for a binding ruling | admitted |
|---|---|---|---|---|---|---|
| FDA | 120 | 2 | — | 10 | 0 (report-only check: 17 HR-topic trial/agency pairs named, 0 typed hits) | 0 |
| EMA | 119 (of 128 run) | 0 | — | 9 | 0 | 0 |
| NICE | 97 | 20 | 14 | — | **1** | 0 |
| PBAC | 123 | 0 | 9 | — | 0 | 0 |
| G-BA | 119 | 3 | 10 | — | 0 | 0 |

The one held row: **pcsk9-mace, ODYSSEY LONG TERM, NICE TA393 committee papers (Sanofi evidence submission)**:
HR 0.52 (95% CI 0.31 to 0.90), MACE (CHD death, non-fatal MI, ischaemic stroke, UA hospitalisation), read
deterministically by `regulatory_typed_effect`; decision `TYPED_HELD_PENDING_BINDING_RULING`. The same document states
"performed on the safety population and included only those CV events that occurred in the TEAE period" and that it
is post hoc. G-BA Module 4A Table 4-20 independently gives the counts 26/788 vs 27/1550 (not read by this route: the
reader is English-only and the topic estimand is HR).

**It counts as PRIMARY_VERIFIED only after a binding ruling** in `registry/g1_regulatory_bindings.json` (arm, outcome,
timepoint, population, analysis set, ruled_by, ruled_on, decision, reason). Divergences to rule on: safety population
vs ITT (>95% of randomised); TEAE window (first dose to last dose + 70 days) vs longest follow-up; post hoc analysis.
The published primary paper (Robinson 2015) reports the same post hoc analysis, so the comparator meta almost
certainly used this same estimate.

If bound: pcsk9-mace k +1 of 9 missing; the topic is still not fully matched (FH I, FH II, HIGH FH, COMBO I have no
per-trial MACE in any held primary document; JAPAN, PACMAN-AMI, GLAGOV, DESCARTES none).

## 5. Readers

agy is out until the 17th; the Claude Sonnet CLI's OAuth session has expired and cannot be refreshed without Mahmood
signing in. No model read was needed in round 2: NICE, PBAC and G-BA are typed-only (deterministic) by licence.

## 6. Source terms logged

- PBAC: https://www.pbs.gov.au/general/copyright, read 15 Oct 2026 — reproduction in part for personal use as general
  reference only; all other rights reserved -> typed-only, never shown to a model.
- NICE: typed-only (D8). G-BA: typed-only (D8). FDA: public domain. EMA: allowed with acknowledgement.
