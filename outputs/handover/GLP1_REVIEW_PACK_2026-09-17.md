# GLP-1 RA vs placebo, 3-point MACE in type 2 diabetes — review pack for Mahmood (17 Sep 2026, 20:45)

Everything below is labelled MEASURED (read from committed objects or fetched bytes), INFERRED, or CLAIMED. No lane ids or file names; the handover branch carries every artefact for anyone who wants them.

## 1. What is served right now — MEASURED on fetched bytes

URL: https://mahmood726-cyber.github.io/meta-harness/reviews/glp1-ra-mace-t2d/
Served commit: `3cf73885ffc83f6fcc4db273c6510a5416cdcde0` (`_production/manifest.json` `commit_sha`), page 195,407 bytes, sha256 prefix `81bae4e28600842e`; 32 of 32 review pages byte-identical to a clean clone of main at that commit.

- Registered protocol: the B-prime amendment (16 Sep 2026), labelled **RETROSPECTIVE**, anchored to commit `b10c53d3` (the commit that amended it); both readings of the FLOW eligibility question disclosed. Binding compatibility axes (endpoint components, HR, end-of-study censoring) declared executably in a further dated clarification (17 Sep) — on the landing-4 candidate, not yet served.
- Primary result served: **k = 8, HR 0.856 (0.809–0.906), τ² ≈ 0.00004** — the legacy pool (LEADER, SUSTAIN-6, EXSCEL, Harmony, REWIND, PIONEER 6, AMPLITUDE-O, SOUL). Certainty: **provisional** (RoB is a partial machine assessment; D3 unassessed). This is the same number as the 16 Sep baseline; what changed on the served page is below.
- Harms: the 15 harm items a held source reports are now each an extracted value with its verbatim span or a typed refusal with code, reason and span (33 `REFUSED_ON_EVIDENCE` rows rendered; 0 `HARMS_INCOMPLETE`). Nothing that a source reports is rendered as absence.
- Design: every pooled row's design is either established from the committed registry cache or rendered `UNPROVEN` — the 98-of-98 silent `ALLOW_WITH_LABEL` fail-open is gone.
- Retractions/scope-mismatch statements: kept count-exact on all 32 pages through both regenerations (proved before each hook).
- **Not on the served page yet:** ELIXA's and FREEDOM-CVO's FDA-derived values (`1.24`, `0.887` absent), FLOW, the strands, the FACT provenance table, the envelope/fragility. They exist, measured, on the landing-4 candidate (§2).

## 2. The landing-4 candidate — built, measured, NOT served (candidate ref on GitHub: `refs/lanes/landing4-candidate` = `60c5cd67`)

Strands, pooled by the unchanged engine (REML/PM, HKSJ with floor, PI with t(k−1)), every member row a FACT (document digest + span located at a recorded offset):

| Strand | k (of candidates) | HR | 95% CI | τ² | 95% PI |
|---|---|---|---|---|---|
| CONVENTIONAL_GLP1RA (primary) | 7 of 10 | 0.888 | 0.828–0.953 | 0.0012 | 0.796–0.992 |
| GLP1RA_ANY_DELIVERY | 8 of 11 | 0.898 | 0.816–0.989 | 0.0067 | 0.723–1.116 |

Members (primary): LEADER, SUSTAIN-6, EXSCEL, REWIND, PIONEER 6, SOUL, **ELIXA** (strict 3-point HR 1.02 (0.887–1.172), 400/3,034 vs 392/3,034, FDA Statistical Review NDA 208471, Table 8 — level 2, document held and digested). Any-delivery adds **FREEDOM-CVO** (HR 1.24 (0.90–1.70), 85/2,075 vs 69/2,081, FDA EMDAC briefing NDA 209053, Table 19, end-of-study ITT — level 2, held); its end-of-treatment row 1.36 (0.96–1.92) is rendered as a sensitivity value and never pooled.

Refused, with the axis named on the page: **FLOW** (HR 0.82 held at level 1; endpoint identity resolved from the registry at level 3; **censoring not stated in any held text** — the registry composite row says on-treatment, the component rows say in-trial, the abstract says neither), **AMPLITUDE-O** (censoring not stated in the held abstract or registry rows), **Harmony** (composite components' fatality unspecified in held text). Nothing was filled from memory or from what CVOTs usually do.

Envelope (all specifications committed objects; NOT_COMPUTABLE where an input is not held): the "all candidates, censoring unverified" specifications give k = 10, HR 0.861 and k = 11, HR 0.867 — the numbers a conventional review would print; they reproduce from the held member objects but are not accepted pools under the declared binding axes. Conclusion fragility and the disagreement decomposer vs the held comparator are built and render on the candidate.

Changes from the 16 Sep baseline (hash `90c01bcfbd124495`), by name: FLOW — retained-and-refused on censoring (was: excluded by slug convenience); FREEDOM-CVO — pooled in the any-delivery strand from a held FDA document (was: declared absent); ELIXA — pooled in the primary strand from a held FDA document (was: declared absent as a 4-point trial); Harmony and AMPLITUDE-O — refused on typed axes (were: pooled from abstracts). Certainty — provisional with the unassessed domain named (was: "moderate, 0 downgrades", arithmetically impossible).

## 3. Against the published meta-analyses — INFERRED from the held comparator text and the candidate objects

- Completeness: the published reviews pool 7–8 dedicated CVOTs from abstracts. The harness now holds two regulatory documents no published review used at the 3-point level (ELIXA's strict 3-point analysis; FREEDOM-CVO's end-of-study analysis) and refuses three trials the published reviews pool, for reasons it can name and cite. Under the declared axes it pools fewer trials (7 vs 8) and gets a slightly weaker but overlapping estimate (0.888 vs 0.856); the all-candidate specification reproduces the published-style number (0.861) and is shown as such.
- Auditability: every pooled value carries a document digest and a located span; every refusal names its axis; the harm debt is itemised; the search is disclosed as known-item retrieval with the amended independent-search obligation marked UNMET — the published reviews claim systematic searches the harness does not claim.
- Falls behind: the independent concept search (MEDLINE/CENTRAL/ICTRP/registry) required by the amendment has not been executed; the FLOW/AMPLITUDE-O/Harmony refusals would likely lift with full texts the harness does not hold (NEJM/Lancet gated; no author manuscripts found).

## 4. Honest weak points

1. The landing-4 candidate is refused by its own standard (7 of 11 limbs). The dominant cause is a contract decision for you: the FACT provenance contract demands a UTC retrieval *instant*; the legacy records carry a *date*. Either date-precision provenance is typed and accepted (my recommendation: `retrieved_utc_precision: date`, disclosed) or 25 pages lose their pooled numbers until re-retrieved. I did not decide this.
2. Prose-as-objects on glp1: 848 registered of 2,749 visible units on the fully merged renderer (the denominator grew as every object began rendering); 12 legacy overclaiming sentences were identified for rewriting as interpretation-with-alternative or removal.
3. The hostile audit (same access as the authors) found 9 confirmed defects, all fixed at source with the auditor's own reproductions — but only on the candidate, not on the served page.
4. The Gemini second reviewer is an audit observation, not a source (its decoding is not pinned; not replayable); disagreement rate 2 of 11 (18%), both resolved by span + registered rule; influence on served values: none.
5. The protocol amendments are retrospective and say so; where a methods choice's answer was known (FLOW eligibility; analysis-set as a compat axis on colchicine-postop-af), both answers are rendered.

## 5. Cost — MEASURED where stated

Codex: 32 lanes today, **9,837,838 tokens** total (of which 412,171 wasted on two integration bases I built incorrectly and one over-strict stop rule — mine, not the lanes'). Claude: this session ran the whole day as the integrator; turns were not counted precisely (INFERRED: several hundred tool calls). By layer: harms debt (5 lanes, ~1.5M tokens) and the integration rounds (6 lanes, ~3.5M) dominate; the glp1-specific architecture (provenance, typing, strands, prose, audit, fixes: 14 lanes, ~3.6M).

## 6. What finishes it (in order)
Your decision on §4.1 → one integration lane (running overnight on the concrete refusals) → the ratchet signatures → hook → CI → main → served-byte proof → the 3-point values on the page a reader gets.
