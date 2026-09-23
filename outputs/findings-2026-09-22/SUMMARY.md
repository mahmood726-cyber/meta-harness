# 2026-09-22 — what was found, what it costs, what only Mahmood can decide

Measured on branch `enforcement-gate` = `b25027e3`. `main` and the served site are `38c04411`. Nothing below is landed
except the certified-families gate fix (its own commit, this day). Full detail and per-lane artefacts: [INDEX.md](INDEX.md).

---

## The three findings with victims

Everything else in this directory is mechanism. These three are defects an external auditor would care about, each with a
named trial and a served consequence.

### 1. Zhao 2009 — a single-blind trial admitted under a double-blind protocol (live on `main`)
`omega3-cardiovascular-events`, PMID 20146881. Admitted by `screen.py:_double_blind`, whose third branch returns True
because the abstract contains the word **"placebo"**. Two independent public reviews state the trial is single-blind
(PMC3507701 Table 1 "R, SB, PC" and "1 in a single-blind fashion [19]", bound to the PMID and DOI; Cambridge
S0007114512001559 "Prospective, single-blind, randomised, placebo controlled"). The topic's own protocol requires
"double-blind, placebo-controlled **or** blinded inert-control" — a single-blind trial fails even the disjunction.
**Served consequence:** included, unextracted, contributing to 0 of 3 outcome pools (all three `OUTCOME_NOT_IN_SOURCE`).
The eligible denominator is wrong by one; no served number moves. **Prevalence:** lane Z25 checked the other 25
placebo-branch admissions against public registry records, PMC full texts and independent review tables, with a positive
control on Zhao run and timestamped first — 21 confirmed on a public registry record, 4 on weaker public tiers (2
secondary-table-only, 1 authors' pooled report, 1 primary abstract), 0 silent, **1 contradicted**. Zhao is the only one.

### 2. J-EMPHASIS-HF — a composite hazard ratio served as all-cause mortality, in the flattering direction (live on `main`)
`spironolactone-hfref-mortality`, PMID 28824029, NCT01115855, k=1. The page serves **All-cause mortality HR 0.85
(0.53–1.36)**. The held abstract assigns that exact tuple to the trial's **primary composite** ("a composite of death from
cardiovascular causes or hospitalization for HF") and reports mortality separately: **17 of 111 vs 10 of 110**. Re-binding
to the trial's own counts gives **RR 1.685 (0.808–3.514)** — recomputed independently of the lane, exact agreement. The
served value reads as a mortality benefit; the correct value favours placebo.
**Status:** the row already carried `endpoint_binding: unbound_legacy` and `MIGRATION_STATE_UNBOUND_LEGACY`, so the
enforcement gate had marked it unbound on P8 while it stayed pooled under the migration exception.
**Not applied.** A draft result-change notice with the full derivation is at
[PROPOSED_NOTICE_j-emphasis-hf.json](PROPOSED_NOTICE_j-emphasis-hf.json). Changing a served primary result and its scale
is Mahmood's decision (RE-BIND with an HR→RR scale change, or WITHDRAW under an HR-only contract), and it needs his
countersignature — not a quiet repair.

### 3. Comparator direction — undefended, with a working attack
From an external safeguard audit relayed 2026-09-22 (that audit could not reach our served artefacts at all: `curl exit 6,
Could not resolve host` on all five URLs, so **every harness claim in it is INFERRED** and was treated as such; our site is
reachable from here, HTTP 200). Its two attacks, run through our real gate on a copy of the served page with authentic
LEADER text:
- **Reversed direction label, number unchanged: admitted, zero objections.** No direction field exists on any of the 46
  served rows, no reciprocal transform exists anywhere in `harness/`, and the gate returned no reason at all.
- **Right endpoint name, wrong estimand (LEADER's expanded-composite 0.88 under the 3-point MACE row, with its authentic
  span): also undefended semantically.** It was refused only by `CERTIFICATE.json release_sha256` and claimgraph
  `STALE_DEPENDENT` — integrity checks that fire because a built file was edited and **that a legitimate rebuild
  regenerates consistently and therefore silences**. No check objected to the endpoint/estimand mismatch; the in-build
  defence would be P9 `span_target_mention`, which is bundle-only and listed as not evaluated in-build.
Its LEADER numbers were verified against our held full text before anything was built on them: 3-point MACE 0.87
(0.78–0.97) ✓, expanded composite 0.88 (0.81–0.96) ✓, MI 0.86 (0.73–1.00) ✓; its two *later-paper* claims (recurrent-event
0.85, subgroup 0.85/0.76/1.08) are **unverifiable — we do not hold those papers**. Its fixture's arithmetic checks out
(1/0.87 = 1.14943, bounds correctly swapped). The four fixture states become plants in a direction landing, credited to it.

---

## The day's most useful result about how we work: a first-pass finding is a draft

**Findings relayed onward were corrected at least seven times today, and every correction moved in the same direction —
the first pass was too confident.**

| # | first pass | corrected to | by |
|---|---|---|---|
| 1 | placebo branch load-bearing for 5 of 19 served rows | **11 of 35** (the 53 set-asides were pooled on `38c04411`) | lane DB |
| 2 | 0 of 15 blinding refusals false (abstract text only) | **2 of 15** false by the parent trial's registry row | lane DB |
| 3 | 17 empty-container findings | **7** confirmed and fresh-build reachable (1 refuted, 9 downgraded) | lane E2b |
| 4 | 5 of 26 admissions unproven by any held document | **4 of 26** (a held full text DB had not read) | lane U5 |
| 5 | 48 of 53 rows bindable from held text | **36 of 53** strictly (1 contradicted, 11 partial) | lane B53X |
| 6 | 27 of 33 trials need a full-text fetch | **14 of 33** (19 already held, 11 in another document) | lane AS |
| 7 | 12 of 46 served rows carry wrong provenance | **1 wrong served number + 11 wrong labels**, 7 in suppressed harm blocks | lane WSX |

Plus one retraction of my own: I reported ME-09 as a claimed-but-unbuilt defence on the strength of a grep scoped to three
directories. `tests/test_arm_identity.py` exists, 5 tests, all passing; the id is referenced in `docs/error_coverage.json`.
The subsequent audit of all 33 library entries (positive control first) found **0 of 33 named files missing, 0 of 33 ids
unreferenced**.

The mechanism behind all eight is one hazard, written up with five instances at
[HAZARD_exhaustive_claim_over_incomplete_representation.md](HAZARD_exhaustive_claim_over_incomplete_representation.md):
**an exhaustive claim over a representation that does not carry the data always succeeds.** The cure is operational —
*an exhaustive claim needs a positive control that would have fired, or it is not an exhaustive claim* — and the fifth
instance is the instructive one, committed by the author of the file inside a report that quoted it. Knowing the rule is
not the mechanism; the syntactic trigger is.

---

## Mechanism (detail in INDEX.md)

- **A hole in the gate we shipped, found the next day and fixed this day:** a certified `cache/<slug>/families.json`
  holding `{"families": []}` — which the real offline writer emits — switched off the page-vs-certified comparison, and the
  full gate PASSED a page whose non-empty-but-incomplete control it REFUSES. Fixed with four plants observed failing
  pre-fix; an 11-state probe of that file then found a second hole (a top-level list crashed the check instead of refusing).
- **Wrong-span class** (bound, located, and about the wrong thing): 12 of 46 served rows, 29 definite contexts; the two
  original instances were found by accident and no instrument in the harness detects the class.
- **Only 23 of 46 served rows carry a locatable numerical source at all** — 14 are computed values with no source sentence
  by construction, 8 are stored as summaries, 21 of 23 are migration-marked, and **2 are `ADMISSIBLE` with no locatable
  source** (REWIND, DAPA-HF). Every provenance claim is bounded by that denominator.
- **Registry phase-scope** (right NCT, wrong phase): 6 of 634 design-held families, 0 of 39 pooled rows.
- **Screener coverage:** an independent judgment exists on 5 of 32 pages, covering 53 of 269 included rows; absence is
  never agreement.
- **Analysis-set decision, both branches costed:** sourced = 14 of 33 primary trial rows need retrieval, a candidate
  document identified for 14 of 14 (10 registry-first, 1 SAP, 2 OA full texts, 1 free publisher PDF); declared = one
  sentence on 14 of 97 outcomes and nothing moves.

## What only Mahmood can decide
1. J-EMPHASIS-HF: RE-BIND (scale change) or WITHDRAW — the notice is drafted, not raised.
2. The 41 OPEN result-change notices and the 11 emptied primary pools (the publication gate refuses 24 of 32 pages).
3. Analysis set: sourced dimension or declared assumption (costs above).
4. Evidence rank for a hand eligibility route — abstract at registry rank carries 28–32 of B53X's 36 retained rows.
5. Zhao: remove from the eligible denominator with the public evidence cited.
6. The probiotics entry-population rule (the config names the outcome, not the entry condition).
7. Whether the direction contract lands as designed, with the external fixture as its plants.
