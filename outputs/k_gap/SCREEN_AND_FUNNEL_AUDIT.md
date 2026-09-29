# Identification, screening and Unpaywall funnels (acq/k-gap, 2026-09-29)

Generated from:
- `counterfactual_members.json` (`scripts/k_gap_counterfactual.py --members`);
- `screen_audit.json` (`scripts/k_gap_screen_audit.py`);
- `unpaywall_funnel.json` (`scripts/k_gap_unpaywall_funnel.py --reprobe`).

Each is an in-memory rebuild by the real harness (dedup → screen → extract → admit); nothing in `cache/`, `topics/` or
`docs/` changes.

## 1a. Comparator reference seeding into identification (71 confirmed-set identification gaps)

- **Every seeded comparator report enters screening, at trial level: 197 of 197.**
  - The earlier "98 of 180 never screened" counted PMIDs. 94 of those were extra reports of a trial already
    screened through another report (67 TOPCAT reports, 22 of NCT01730534), which `_dedup` correctly folds to one
    report per NCT.
  - The funnel now labels them `SCREENED_VIA_OTHER_REPORT`.
- **Defect found in the seeding itself:** 7 of 71 rows were seeded with the wrong paper.
  - Where a comparator table's cross-references are distrusted (omega-3, numbered one off from its reference
    list), the resolver settles the row by author and year, but seeding used `cited_pmids`: the link the resolver
    had rejected. Eritsland 1996 was seeded as DART.
  - Fixed in `member_pmids`, with a plant test that fails on the old code.
  - The same fault was in the identity reader-2 display (commit 75e060a).
- **Where the seeded identification gaps go** (trial level, before the 7-row fix; rerun pending):
  - screened out X2 21, X1 15, X3 13, X-DESIGN 1;
  - declared absent 7 (OUTCOME_NOT_IN_SOURCE);
  - pooled or via an included report 5;
  - not seeded 27. These are REFERENCE_SEED candidate rows, other-agent rows, and the 7 rows seeded with the
    wrong PMID.
- **So identification is not the binding step once seeded: screening is.**

## 1b. The 55 confirmed-member screening exclusions, by reason

| class | n of 55 | reading |
|---|---|---|
| **flips to include under condition-as-outcome** (screener `prevention` semantics, trigger: population term = primary-outcome keyword) | **5** | all probiotics-AAD (Gotz, Hickson, Koning, Lönnermark, Ouwehand); each checked by hand as an AAD-prevention trial. `topics/probiotics-aad-prevention.json` does not set `include.prevention` |
| flips under the typographic-hyphen fold | **0** | the probiotics titles use other words ("ampicillin-associated", "diarrhoea associated with antibiotics"), not U+2010 |
| outcome-conditional eligibility fix | not tested | that fix is not on this branch |
| scope excluded by protocol (`population_none` term) | 13 | ablation, lung resection, CABG, stroke, AF, covid, eye disease, HF in the CKD topic, HFrEF in the primary-prevention topic, stable CAD ×2, TXA prevention ×3. True under our protocol; a SCOPE difference from the comparator, not a screening defect |
| population term absent from title/conditions | 10 | **4 look like vocabulary gaps** (a new class, not an existing fix): Nidorf "secondary prevention of cardiovascular disease", Burr 1989 "myocardial reinfarction", Burr 2003 "men with angina", Brouwer "implantable cardioverter defibrillator". 5 are H. pylori-eradication probiotic trials with no AAD term even in the abstract, and 1 is WOMAN-2, a prevention trial excluded by scope anyway |
| design protocol (double-blind / required context) | 8 | deliberate protocol difference |
| other-agent trial carrying our drug label | 7 | **a table defect, not screening**: sacubitril's comparator (an NMA) lists SOLVD, CHARM, Val-HeFT… and omega-3 lists Tuttle. These should leave the denominator as OTHER_AGENT |
| not an RCT by the record | 5 | true by the record's publication type and abstract |
| comparator term absent | 3 | Akodad (usual care, no placebo), PCOSMIC, ticagrelor ref 2 |
| an included report exists (gap is downstream) | 2 | |
| no report screened | 2 | Macchia 2013, Nigam 2014 (omega-3) |

**n of 55 that flip under the existing fixes: 5. True exclusions: 50.** Of those 50:

- 24 are deliberate protocol choices (scope 13, design 8, comparator 3);
- 7 are table labelling errors;
- 4 are candidate vocabulary gaps (new, unverified);
- 5 are not RCTs by record;
- 6 are other population-term absences;
- 4 are downstream of screening or never screened.

Caveat: the audit classes are mechanical from the rule and reason. The vocabulary-gap and flip readings are my own
hand check, and I also wrote the classifier. No independent reader has checked them.

## 2. Unpaywall: found → reaches extraction → fetched → parsed → located → admitted (148 rows over 32 topics)

| step | n | detail |
|---|---|---|
| S0 found (row has an is_oa Unpaywall location) | 148 | all topics; the 61 in `SUMMARY.md` is the confirmed, non-deliberate subset |
| **S1 blocked upstream: the copy cannot help** | **111** | identification 52, screening 34, scope 16, measure 9 |
| S1 not declared absent | 3 | already pooled 1; OA DOI is not our record's 2 |
| S2/S3 no usable text | 12 | fetch error 5; HTML under 3000 chars (landing page, JS shell, abstract-only) 7 |
| S4 text parsed, result not located | 21 | OUTCOME_NOT_IN_SOURCE 16; extraction not performed 2; endpoint unbound 1; counts not corroborated 1; known-reported not yet extracted 1 |
| **S5 admitted** | **1** | |

- **Reading:** the drop is mostly not Unpaywall. **111 of 148 (75%) never reach extraction in our pipeline**: the
  identification and screening gaps of section 1.
- Of the 34 that do, 22 parse, and 16 of those are OUTCOME_NOT_IN_SOURCE. Those 16 are next: is the outcome truly
  absent, or in a flattened PDF table that the UNSTRUCTURED rule refuses by design?
- **Recording defect fixed:** `unpaywall_text` had dropped each URL attempt's status. It now keeps them, and the
  12 no-text rows carry a recorded reason.
