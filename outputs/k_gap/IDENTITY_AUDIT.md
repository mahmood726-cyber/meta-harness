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

**Limits, stated not dropped:**
- The labeller is the resolver's author (same session). Not independent.
- The sample is burned: any change to the resolver is revalidated on a NEW seed drawn after the change.
- This audits IDENTITY only. The gap CLASS depends on our pipeline's own states (declared-absent reason codes,
  families, records), which are read, not re-judged here.
