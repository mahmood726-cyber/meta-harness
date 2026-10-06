# K-GAP identity audit (2026-09-29)

**Instrument audited:** the identity resolver in `scripts/k_gap_table.py` (comparator unit -> PMID/NCT).

**Sample:** 25 rows drawn with `random.seed(20260929)` from the 186 confirmed-set, drug-specific, resolved,
not-pooled rows of `k_gap_table.json` (build of 2026-09-28/29). The seed was fixed before the draw. Script:
`python` + `random.sample(rows, 25)` over rows filtered `unit_source != REFERENCE_SEED`, `drug != OTHER_AGENT`,
`status != UNRESOLVED`, `gap_class != POOLED`, in file order.

**Result:** 24 of 25 identities confirmed correct by label vs the cited reference-list entry or AACT brief title
(e.g. `Rubino, 2021` -> NCT03548987 STEP 4; `WOMAN-2` -> NCT03475342; `ASCEND 2018` -> NCT01624727;
`ODYSSEY LONG TERM NCT01507831` -> NCT01507831). 1 of 25 not verifiable from the row alone:
metformin `Liu 2004` -> PMID 15498183, via a single-hit PubMed author+year+agent query.

**Resolution basis in the sample:** 22 of 25 via the comparator's own citation link (table-cell `xref` -> JATS
ref-list PMID), 1 via Author-Year against the comparator's ref-list (`Rubino, 2021`), 1 via an NCT printed in the
table cell, 1 via PubMed author-year single hit. (The table's `identity_basis` also lists `comparator_ref_pmid`
for rows whose PMID was filled by an earlier step; the step that FOUND the PMID is the one counted here.) The riskier paths
(acronym -> AACT, family-acronym, PubMed acronym) did not appear in this draw, so the sample says little about
them. Their known failures were found and fixed before this audit (see commit log: CHADS2/noac, HARMONY-3,
ARTS-HF scope).

## CORRECTION (2026-09-29, later the same night): the self-audit was wrong, and an independent reader found why

**Independent second reader** (`scripts/k_gap_identity_reader2.py`; 40 rows drawn at seed 20260930, fixed before
the draw; recorded Codex calls; gate = verbatim quotes from both the row and the resolved report):
**MATCH 18, CANNOT_TELL 18, NO_MATCH 4.** All 4 NO_MATCH are real resolver errors, all in omega-3:
AREDS2 -> AFFORD, Doi -> AREDS2, GISSI-HF -> JELIS, Kromhout -> a DHA-in-Alzheimer trial.

**Root cause:** the omega-3 comparator's own JATS (PMID 35905212) cites every Table 1 row one reference off from
its reference list (26 of 28 links contradict their row's author/acronym/year). Following the citation link
faithfully resolved each row to the trial in the row above.

**My self-audit missed this and mis-scored one row.** Row 9 (`ASCEND 2018 [47]` -> NCT01624727) was marked
correct. NCT01624727's title ("Slowing HEART diSease With Lifestyle and Omega-3 Fatty Acids") is the Alfaddagh 2017
trial from the row above, so the self-audit was at best **23 of 25**, not 24 of 25. This is the "labeller is the
resolver's author" limit below, happening.

**Fix** (`kgap.k_gap.label_ref_conflict` + `distrust_shifted_tables` in `scripts/k_gap_table.py`, tests in
`tests/test_k_gap.py`): a citation link is followed only when the row's own label does not CONTRADICT the cited
reference (author / registry-or-title acronym / year). When >=3 and >=50% of a table's links contradict their rows,
no link in that table is trusted, and every row resolves from its own label against the (correct) reference list.
Absence is not contradiction: the first version dropped esketamine's 6/6 correct links on the generic label
'Trial A', which the tests now pin.

Corpus-wide after the fix: 28 of 190 table units with a citation link sit in a distrusted table (all omega-3);
single-link conflicts elsewhere 0. Omega-3 re-resolved: Kromhout 2010 is Alpha Omega (NCT00127452), which we POOL.
The earlier "screened out: Alzheimer population" was the shifted identity.

**Limits, stated not dropped:**
- The labeller is the resolver's author (same session). Not independent.
- The sample is burned: any change to the resolver is revalidated on a NEW seed drawn after the change.
- This audits IDENTITY only. The gap CLASS depends on our pipeline's own states (declared-absent reason codes,
  families, records), which are read, not re-judged here.
