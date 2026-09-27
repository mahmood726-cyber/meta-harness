# V1.0.1 -- the comparator overlap relation, computed (branch evid2/v101-overlap)

From three external reviews (balanced-crystalloids; colchicine-POAF; pericarditis recurrence), 26-27 Sep 2026. Main is frozen: this is a branch for
the release captain. Nothing pooled changed: **0 of 32 pooled results moved.**

## What was wrong
The index said OVERLAPPING against the 2018 Zayed comparator for balanced-crystalloids, while our pool (PLUS, BaSICS)
and Zayed's shared zero trials. The word was inferred from COUNTS (ours_k < theirs_k, plus a publication-date
list), never from the trial sets. Several surfaces (index, parity row, panel, overlap counts) each derived their
own word. Esketamine showed the same defect directly: served `shared_k` 4 with our pool 3.

## The fix: one computed object (harness/overlap_relation.py), read by every surface
- **Sets:**
  - ours = the pooled trial families for the primary outcome;
  - theirs = the comparator's trials, from a typed enumeration only, in this order: an outcome-bound panel, then
    comparator-truth's named set, then the comparator's included-trial table, then the second pass's located
    names.
- **Binding:** by PMID/DOI through each row's own reference link, or by a bibliographic key. Never by name
  similarity.
- **Relation:** IDENTICAL_SET / SUBSET / SUPERSET / OVERLAPPING / DISJOINT is a set operation.
  - DISJOINT also holds by **date proof** (every pooled family first reported after the comparator's year).
  - Otherwise the relation is NOT_ENUMERABLE, with what is known kept as stated constraints. Nothing is inferred
    from counts.
- **Consumers:** the index (a new relation column), the parity row, the comparator panel (a block rendered from
  the object), the manuscript (one sentence in Limitations), the manifest, and `comparator.overlap`, whose counts
  are now a projection of the object.
- **Gate:** `check_overlap_relation_one_object` refuses any page whose projections disagree with the object, or
  that does not render it.

## Comparator trial tables are read from the comparator's own PMC full text (scripts/comparator_trial_tables.py)
- **Where the table can be fetched:** the comparator's JATS is held only if it carries an open licence. Rows are
  located as raw `<tr>` elements and bound to their references (PMID/DOI) through the row's reference link.
- **Result:** 12 comparators newly enumerated, and every stored trial set revalidates. Per-topic states are in
  `evidence/comparator_tables/COMPARATOR_TABLES.json`: NOT_IN_PMC, NOT_OPEN_LICENSE, NO_INCLUDED_TABLE, WRITTEN,
  ALREADY_ENUMERATED.
- **The "not machine-exposed" string is gone from every served overlap object.** Where no table can be fetched, it
  reads "not computed: <reason>".
- **Fixture:** colchicine-POAF against Zhao 2022 (PMC9438305, 9 trials) is **OVERLAPPING**. Shared = COPPS-2
  (Imazio 2014, PMID 25172965) and END-AF Low Dose (Tabbalat 2020, PMID 32720823); Farzaneh (PMID 42132185, 2026)
  is ours only; theirs only = Bessissow, Deftereos ×2, Imazio 2011, Sarzaeem, Tabbalat 2016, Zarpelon.
- **Plant:** balanced-crystalloids is **DISJOINT**, by Zayed's located Table 1 (5 mortality trials; Ratanarat is
  out of scope as AKI/RRT only) AND by date proof.

## Non-PubMed retrieval route (harness/journal_route.py)
- **The route:** a trial reported only in a journal PubMed does not index enters screening and the family ledger
  as a typed JOURNAL record, instead of staying unresolved. The record is bound to a held copy of the journal's
  article page (sha256), with every field located verbatim. Counts read from printed percentages are
  RECONSTRUCTED, round-trip checked, and **not pooled** until the full report is held. That state
  (RECONSTRUCTED_NOT_POOLED) is shown on the page.
- **Fixture: Sarzaeem 2014**, Tehran Univ Med J 72:147-154, from the journal's own page (tumj.tums.ac.ir,
  CC BY-NC 4.0).
  - Magiran returned a Cloudflare bot challenge, which was not bypassed. Crossref has no record.
  - Screening includes it: the abstract's allocation by "a table of random numbers" is now read as
    randomisation, with a plant against quasi-random allocation.
  - It has its own family (SYN-9513c33707df) with a PRIMARY report, and key `bib:tehranunivmedj:2014:72:147`.
  - POAF shows **RECONSTRUCTED 16/108 vs 33/108** (14.8% vs 30.6%, n=108/arm). The pool is unchanged at k=3.
  - The linked full-text PDF was not downloaded (it needs approval). Holding it would allow a pooled row, which
    then needs a result-change notice.

## FISSH candidate (balanced-crystalloids; PMID 28729329, NCT02748382)
`evidence/family_candidates/balanced-crystalloids-vs-saline-mortality/NCT02748382_FISSH.json`:
- **Decision:** ELIGIBLE on P/I/C/design. The registry arms are Ringer's lactate vs normal saline, with an albumin
  co-intervention recorded as a caveat.
- **Target result:** RESULT_NOT_AVAILABLE. The trial was completed in 2017 with n=50; no results are posted and
  no results paper exists.
- **Not pooled.**

## Pericarditis-recurrence fixtures (third external review)
- **Overlap from the committed transcription.** The comparator's Table 1 is in our committed full-text
  transcription, not in PMC. `from_text_spec` (scripts/comparator_trial_tables.py) reads
  `cache/colchicine-recurrent-pericarditis/comparator_table_spec.json` (anchor text and row labels as printed only),
  locates each row, and binds a row only to a unique PRIMARY-role report whose title carries the name as a whole
  token. **Plant: CORP never binds to CORP-2** (PMID 21873705, not 24694983).
- **Result, against the outcome-specific POOLED set (CORP, CORP-2): OVERLAPPING.** Shared = CORP; ours only =
  CORP-2 (NCT00235079); theirs only = Finkelstein, COPE, CORE, COPPS. ICAP is no longer in `only_ours`: it is not
  pooled, and membership in the pooled set is now separate from membership of a family (`bound_to` vs `family`).
- **A separate inventory comparison** is rendered under the relation, and never feeds it:
  - COPPS is SCREENED_OUT (postoperative);
  - Finkelstein, COPE and CORE are NOT_IN_OUR_RECORDS, with the comparator row's printed design kept
    (e.g. COPE "open-label"). So an open-label or postoperative trial is not called "missing eligible".
- **ICAP is one family.** The missing-trial panel named it by acronym and by article title. The family resolver now
  reads registration trailers ("ICAP ClinicalTrials.gov number, NCT00128453"), only when that NCT is the family's
  own, and merges the candidates: one row, family NCT00128453, `also_named` ICAP. Plant: another trial's NCT binds
  nothing.

## Binding a comparator row to a trial we hold without its paper (found by CI, 27 Sep)
A test pinned esketamine's old "Trial set NOT ENUMERATED" wording and failed once Zhao-style PMC reading
enumerated the comparator's table. Reading the new object showed a real defect, not a stale test: **TRANSFORM-3 was
"ours only" and the relation OVERLAPPING; the truth is SUBSET.** The comparator cites TRANSFORM-3's paper (PMID
31734084). We pool TRANSFORM-3 from its registry record (NCT02422186), and screening excluded the paper as its
secondary publication (X-DEDUP), so the paper sat in its own family and the PMID bound the row there. Two typed
steps now resolve such rows, in order:
1. **Screening's dedup parent:** a row bound to a record that X-DEDUP excluded as a secondary publication resolves
   to the family whose registration that decision names, if exactly one family has it.
2. **The acronym printed in the row's own cited article title:** used only when the reference's PMID/DOI binds
   nothing. It must be a whole hyphenated token (TRANSFORM-3 never TRANSFORM-2; PRE-TRANSFORM-3 is not a token) that
   names exactly one family of ours.

Effect across the 32 topics:
- **esketamine:** SUBSET (shared TRANSFORM-2, TRANSFORM-3, Chen 2023). TRANSFORM-1 and SUSTAIN-1 are found in our
  ledger; SUSTAIN-2 is genuinely not in our records.
- **omega3:** the FORWARD row is found in our ledger (NCT00597220). The relation is unchanged.
- **ticagrelor:** the comparator's row 1 (PMID 20079528, PLATO's planned-invasive-strategy paper) is PLATO. Its 22
  rows are therefore 21 trial families. The relation is unchanged (NOT_ENUMERABLE).
- **No other topic changed.**

The plants are in tests/test_comparator_trial_tables.py.

## n of N (final rebuild, 32 of 32 pages rebuilt rc=0 with `--now 2026-09-11`)
- **Served relation word changed: 10 of the 19 topics that served one.** The acknowledgements are in
  `docs/ratchet_acknowledgements.json` (10 parity, 5 block); the list goes to the signing list as label notices.
  - Balanced-crystalloids and corticosteroids-covid19: OVERLAPPING -> DISJOINT.
  - Esketamine and melatonin: OVERLAPPING -> SUBSET.
  - **6 drop to NOT_ENUMERABLE** (noac, pcsk9, probiotics, semaglutide-weight, sglt2-ckd, tranexamic). Their word
    rested on counts or hand prose, and no typed enumeration exists to recompute it. Each can be restored by a
    typed trial set; their comparators are not open-licence in PMC, or have no linked table, or (noac) RE-LY and
    ROCKET AF cannot be bound.
  - Pericarditis keeps OVERLAPPING, but it is now computed from trial identities (above), not inferred.
- **Index ours/theirs/shared changed: 31 of 32.**
- **Computed relation now served on 32 of 32:** DISJOINT 3, IDENTICAL_SET 1, SUBSET 3, SUPERSET 1, OVERLAPPING 6,
  NOT_ENUMERABLE 18.
- **Pooled results moved: 0 of 32.** So no result-change notices are needed.

| topic | served relation (main) | served now | computed object | ours / theirs / shared before | after | comparator table |
|---|---|---|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | OVERLAPPING | **DISJOINT** | DISJOINT | 2 / 6 / not exactly verifiable (comparator trial | 2 / 5 / 0 | ALREADY_ENUMERATED |
| colchicine-postop-af | OVERLAPPING | **OVERLAPPING** | OVERLAPPING | 3 / 9 / not exactly verifiable (comparator trial | 3 / 9 / 2 | WRITTEN |
| colchicine-recurrent-pericarditis | OVERLAPPING | **OVERLAPPING** | OVERLAPPING | 2 / 5 / not exactly verifiable (comparator trial | 2 / 5 / 1 | WRITTEN (text transcription; PMC: NOT_IN_PMC) |
| colchicine-secondary-cv-prevention | — | **—** | OVERLAPPING | 3 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 3 / 15 / 2 | WRITTEN |
| corticosteroids-cap-mortality | — | **—** | NOT_ENUMERABLE | 2 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 2 / not stated in the comparator abstract/fu / not computed: comparator trial set not e | NOT_IN_PMC |
| corticosteroids-covid19-mortality | OVERLAPPING | **DISJOINT** | DISJOINT | 1 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 1 / not stated in the comparator abstract/fu / 0 | NOT_OPEN_LICENSE |
| dapagliflozin-hfpef-hosp | — | **—** | NOT_ENUMERABLE | 0 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 0 / not stated in the comparator abstract/fu / not computed: no pooled trials for the p | NOT_OPEN_LICENSE |
| denosumab-vertebral-fracture | NOT_ENUMERABLE | **NOT_ENUMERABLE** | NOT_ENUMERABLE | 1 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 1 / not stated in the comparator abstract/fu / not computed: comparator trial set not e | NO_INCLUDED_TABLE |
| doac-vte-recurrence | — | **—** | NOT_ENUMERABLE | 6 / 6 / 6 | 6 / 6 / not computed: comparator trial set not e | NOT_IN_PMC |
| dpp4-mace-t2d | — | **—** | NOT_ENUMERABLE | 3 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 3 / not stated in the comparator abstract/fu / not computed: comparator trial set not e | NO_INCLUDED_TABLE |
| empagliflozin-hfpef-hosp | — | **—** | NOT_ENUMERABLE | 0 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 0 / not stated in the comparator abstract/fu / not computed: no pooled trials for the p | NO_INCLUDED_TABLE |
| esketamine-trd-madrs | OVERLAPPING | **SUBSET** | SUBSET | 3 / 4 / 4 | 3 / 6 / 3 | WRITTEN |
| finerenone-ckd-t2d-renal | IDENTICAL_SET | **IDENTICAL_SET** | IDENTICAL_SET | 2 / 2 / 2 | 2 / 2 / 2 | WRITTEN |
| glp1-ra-mace-t2d | SUPERSET | **SUPERSET** | SUPERSET | 8 / 8 / 7 | 8 / 7 / 7 | ALREADY_ENUMERATED |
| iv-iron-hfref-hosp | OVERLAPPING | **OVERLAPPING** | OVERLAPPING | 2 / 6 / not exactly verifiable (comparator trial | 2 / 5 / 1 | WRITTEN |
| melatonin-primary-insomnia-sol | OVERLAPPING | **SUBSET** | SUBSET | 1 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 1 / 19 / 1 | WRITTEN |
| metformin-pcos-ovulation | — | **—** | NOT_ENUMERABLE | 3 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 3 / not stated in the comparator abstract/fu / not computed: comparator trial set not e | NOT_OPEN_LICENSE |
| noac-vs-warfarin-af-stroke | IDENTICAL_SET | **NOT_ENUMERABLE** | NOT_ENUMERABLE | 4 / 4 / 4 | 4 / 4 / not computed: enumerated comparator set  | NOT_OPEN_LICENSE |
| omega3-cardiovascular-events | OVERLAPPING | **OVERLAPPING** | OVERLAPPING | 5 / 28 / not exactly verifiable (comparator trial | 5 / 28 / 3 | WRITTEN |
| pcsk9-mace | DOMINANT_SUBSET | **NOT_ENUMERABLE** | NOT_ENUMERABLE | 2 / 12 / not exactly verifiable (comparator trial | 2 / 12 / not computed: comparator trial set not e | NO_INCLUDED_TABLE |
| probiotics-aad-prevention | OVERLAPPING | **NOT_ENUMERABLE** | NOT_ENUMERABLE | 11 / 42 / not exactly verifiable (comparator trial | 11 / 42 / not computed: enumerated comparator set  | WRITTEN |
| sacubitril-valsartan-hfref | — | **—** | NOT_ENUMERABLE | 2 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 2 / not stated in the comparator abstract/fu / not computed: comparator trial set not e | NO_INCLUDED_TABLE |
| semaglutide-obesity-mace | — | **—** | SUBSET | 1 / 16 / not exactly verifiable (comparator trial | 1 / 16 / 1 | WRITTEN |
| semaglutide-obesity-weight | IDENTICAL_SET | **NOT_ENUMERABLE** | NOT_ENUMERABLE | 2 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 2 / not stated in the comparator abstract/fu / not computed: comparator trial set not e | NO_INCLUDED_TABLE |
| sglt2-ckd-progression | SUBSET | **NOT_ENUMERABLE** | NOT_ENUMERABLE | 3 / 10 / not exactly verifiable (comparator trial | 3 / 10 / not computed: comparator trial set not e | NOT_OPEN_LICENSE |
| sglt2-hfref-hosp-cvdeath | PARITY_REFUTED_BY_N | **PARITY_REFUTED_BY_N** | NOT_ENUMERABLE | 2 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 2 / not stated in the comparator abstract/fu / not computed: comparator trial set not e | NO_INCLUDED_TABLE |
| sglt2-primary-prevention-hf | — | **—** | OVERLAPPING | 4 / 8 / 4 | 4 / 8 / 2 | WRITTEN |
| spironolactone-hfref-mortality | — | **—** | NOT_ENUMERABLE | 3 / 9 / not exactly verifiable (comparator trial | 3 / 9 / not computed: comparator trial set not e | NO_INCLUDED_TABLE |
| statins-primary-prevention-elderly | COMPARATOR_INVALID | **COMPARATOR_INVALID** | DISJOINT | 2 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 2 / 12 / 0 | WRITTEN |
| ticagrelor-vs-clopidogrel-acs | — | **—** | NOT_ENUMERABLE | 2 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 2 / 21 / not computed: enumerated comparator set  | WRITTEN |
| tocilizumab-covid19-mortality | — | **—** | NOT_ENUMERABLE | 1 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 1 / not stated in the comparator abstract/fu / not computed: comparator trial set not e | NOT_OPEN_LICENSE |
| tranexamic-acid-pph | SUBSET | **NOT_ENUMERABLE** | NOT_ENUMERABLE | 1 / not stated in the comparator abstract/fu / not exactly verifiable (comparator trial | 1 / not stated in the comparator abstract/fu / not computed: comparator trial set not e | NO_INCLUDED_TABLE |

## Known gaps, stated
- **The honest ratchet only compares outcomes that exist in the base commit** (harness/honest_ratchet.py ~254). A
  NEW outcome passes it silently; nr's re-derivation caught one on the Q branch.
- **Parallel V1.0.1 branches exist:** v1.0.1/pool-pin, oc/v101-*, and evid/v1.0.1-glp1-admission. All regenerate
  the pages, so whichever integrates second must rebuild after merging.
- **F: had 1.4 GB free during this work**, below the captain's 3 GB note. The growth was other sessions' data;
  none of it was evid2's.
