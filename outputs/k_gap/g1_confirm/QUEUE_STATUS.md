# G1 confirm-unverified: queue status (4 Oct, on acq/k-gap e89dfe864)

## Result

**n flipped UNVERIFIED -> PRIMARY = 1** (Safdar et al 2008, probiotics-aad-prevention).

**Search.** The search key is the comparator's own row. What counts is the trial's own span: "Antibiotic-associated
diarrhoea occurred in 6/16 (37%) in the placebo group and 4/23 (17%) patients in the Florajen group".
- Arms are CONSISTENT.
- 39 of the 40 randomised were analysed.
- Agreement with the comparator row is recorded NOT_INDEPENDENT.

**Measured as an A/B** on the same tracker, with the same held caches as the k-gap lane:

| | Without bindings | With bindings |
|---|---|---|
| probiotics-aad-prevention k matched | 15 | 16 |
| INDEPENDENTLY CONFIRMED (whole tracker) | 86 | 87 of 367 |

## Queue: 101 UNVERIFIED rows (bindings.json lists every row with its reason)

| Class | n | Why it cannot be confirmed by a primary binding |
|---|---|---|
| TEXT bound | 1 | (flipped) |
| NOT_ELIGIBLE | 33 | named scope / estimand difference: not this topic's result (e.g. DAPA-HF / EMPEROR-Reduced in primary prevention) |
| TYPED_REFUSAL / _NAMES | 8 | our own typed refusal: design (cluster / crossover), estimand class, per-protocol, unbound endpoint |
| SUBGROUP_OR_POST_HOC | 1 | DECLARE-TIMI 58: the 'HF without known reduced EF' subgroup |
| TUPLE_NOT_PRINTED_IN_HELD_PRIMARY | 58 | every held open source (abstract, PMC OA, Unpaywall, posted CT.gov results) tried; the comparator's tuple is not printed in any of them |

### The 58 not printed, by what was held and why the tuple is absent

**Held open sources by row type.**

| | Full text held | Abstract only (no open full text) |
|---|---|---|
| Counts rows | 18 | 21 |
| Effect-only rows | 4 | 15 |

**Effect-only rows.** Mostly an effect the COMPARATOR computed (RR / MD from arm data), which no primary prints:
- omega-3: 9
- melatonin: 5
- balanced crystalloids: 2

**Counts rows, by hand diagnosis of every window holding both event counts.**
- **Not printed anywhere in the held texts:** 31 of 39.
- **Printed in a shape the rule refuses:**
  - Cindoruk: the count is the word "Nine"; counts must be printed as whole numbers.
  - Raja 2005: "first group" / "second group" with equal arms (50 / 50); arm ownership is unresolvable.
  - Bravo: the outcome is called "acute diarrhea", not the topic outcome. No data-derived head-noun rule exists: no
    topic's outcome terms share a stem. Loosening the gate by hand was declined.
- **Event counts, not patients:**
  - HEART-FID: "a total of 297 and 332 hospitalizations".
  - EFFECT-HF: "13 in each group" (hospitalizations).
- **Comparator arm mis-assignment (a FINDING, not a confirmation):** Velasco 2019. The comparator's treatment arm
  50/247 is the trial's "Both (n 247)" column, i.e. probiotic PLUS placebo, against the unblinded control 14/67.
- **Paywalled full text:** the rest. The cascade holds only the abstract.

## Routes tried

| Route | Result |
|---|---|
| OA full text, via the shared cascade | 174 PMIDs: PMC OA 37, Unpaywall OA 59, none 78 |
| AACT posted results (2026-08-30 snapshot) | for every row with an NCT: 0 matches |
| FDA | pcsk9 ODYSSEY trials: the Praluent medical review (BLA 125559, 2015) prints per-study MACE only as Figure 40 and image tables. No text layer; the cascade's rule is typed text, never OCR. Blocked. |
| EMA | iron (FAIR-HF, HEART-FID, EFFECT-HF), esketamine Trial B: the comparator's tuples are pooled or derived figures no regulator prints |

**Queue exhausted** for deterministic routes; the remainder is blocked as classified above.


## Round 2 (4 Oct): Codex reading lanes as proposals; deterministic gate; trackers not regenerated (the captain does)

**Result: n flipped = 2.**

| Trial | Topic | Without | With | What the binding is | Agreement with the comparator |
|---|---|---|---|---|---|
| Safdar | probiotics-aad-prevention | 15 | 16 | comparator tuple found in the trial's abstract | NOT_INDEPENDENT |
| DELIVER | dapagliflozin-hfpef-hosp | 0 | 1 | the trial's OWN whole-trial tuple | NOT_COMPARABLE:COUNTS_VS_EFFECT (computed) |

**DELIVER in detail.** The trial's own whole-trial primary composite of worsening heart failure or cardiovascular death:
512 of 3131 on dapagliflozin vs 610 of 3132 on placebo (PMID 36027570 abstract). The comparator's row, HR 0.63 with
368 / 371, is the HFimpEF subgroup: a comparator-side finding.

Both were verified as an A/B per topic on the same tracker (without / with bindings). The tracker files were then
restored, not committed.

**Lanes.** CONFPROP1-3 (codex gpt-5.5, concurrency 3, offline). Each read the held open texts of the 59 rows whose
tuple is not printed, and classified every row:

| Verdict | Rows |
|---|---|
| PRINTED_SAME | 6 |
| PRINTED_DIFFERENT | 13 |
| PERCENT_ONLY | 14 |
| NOT_REPORTED | 20 |
| SUBGROUP_ONLY | 4 |
| WORD / OTHER FORM | 2 |

This also cross-checks independently the round-1 verdict that the comparator tuple is not printed: 0 PRINTED_SAME
proposals survive the gate.

**Gate** (`scripts/g1_confirm_proposals.py`, 30 plants). A proposal is admitted only when the held bytes carry every
fact: verbatim quotes, counts, the outcome named by a non-generic topic term, no subgroup / adjusted / event-count
language, and arms established.
- **Same-tuple mode:** 0 admitted.
  - Shimbo: "water diarrhea".
  - Bravo: "acute diarrhea".
  - Cindoruk: "Nine".
  - Yokoyama: the comparator row is effect-only.
  - HEART-FID: hospitalizations, not patients.
  - Raja: the arm sizes are not printed.
- **Own-tuple mode** (matched = any verified typed tuple, Mahmood 3 Oct): 1 admitted (DELIVER). Refused:
  - LoDoCo, JELIS, SOFA (Brouwer): the outcome is named only generically ("primary outcome / end point"), and is not
    the topic's composite.
  - Nestler, Nilsen: word counts.
  - COPS (Tong): events, not patients.
  - Velasco: the outcome is not named.
- **Discrepancy candidates:** 12 rows where the trial's own text prints different numbers from the comparator
  (proposal_gate.json `discrepancy_candidates`). They are findings, never flips.

**Other reports cited by the texts:** 4, all already held or design / protocol papers. Nothing to fetch.

**Queue exhausted.** Every remaining row is classified above or in round 1.
