# Findings and decisions

## 27-01 — Incorrect comparator exclusion: Legro 2007 (PMID 17287476)

The pinned ledger's X3 reason says no eligible comparator. The configured positive
terms include 'placebo group' and 'placebo-controlled', but not bare 'placebo'.
The primary report explicitly randomises 626 women to clomiphene plus placebo,
metformin plus placebo, or combination therapy. The relevant comparison is
combination therapy (209) versus clomiphene plus placebo (209).

The isolated source-informed paraphrase fails the current phrase list and passes
when bare placebo is added. This is not a demonstrated end-to-end fix: full
contrast reasoning, negation, placebo ownership and background treatment must
still be assessed. The study-level exclusion reason is unsupported.

The article separately reports women with no documented ovulation: 35/209 in the
combination group and 52/209 in the clomiphene group. Auditor complements give
174/209 and 157/209 with at least one documented ovulation. Their calculated OR
is 1.646588 (1.019120–2.660386). Adding this candidate diagnostically changes the
pool from 2.073334 (0.092246–46.600793) to 1.803051 (0.386136–8.419298).
This is NOT an approved primary analysis: adjudicate definition, missingness,
follow-up, treatment history, formulation, licensing and binding. Never pool
repeated treatment cycles as independent women.

Severity: changes served wording; a numerical change is conditional on admission.

## 27-02 — Two IVF families misclassified as eligible

NCT01208740 / PMID 21917254 and NCT01233206 / PMID 21982727 are marked eligible
at family level even though their report-level exclusions recognise IVF. Their
original publications establish gonadotropin-stimulated IVF. The protocol excludes
IVF. Correcting those two only changes the displayed eligible-family count 8→6.
This is a local set reconciliation, NOT the definitive eligible census. No current
primary estimate changes. Other unresolved families were not all adjudicated.

Severity: changes a served descriptive number and related wording.

## 27-03 — 'Full text checked' overstates held-document coverage

The Moll harm refusal is reasonable for the held material's limitation, but the
page says full text was checked. `ft_16769748.txt` explicitly notes that the
publisher does not permit full-text XML download. It contains metadata, abstract
and end notes, not the article body/table evidence. The original full HTML gives
18 versus 6 women discontinuing due to side effects, with arm N=111 and 114.
Auditor OR=3.483871 (1.327773–9.141141). This is not an admitted harms estimate.

Correction: classify document coverage explicitly and acquire/admit the specific
outcome source under normal rules; do not equate scanning this XML with scanning
all article results. Do not use this cause-specific endpoint as all-cause dropout
or as overall GI-event incidence.

Severity: changes served wording and source-coverage record; conditional recovery.

## 27-I1 — Integrity update: do not reinstate Kazerooni 2009

PMID 19552904 has a wrong X3 comparator reason: its abstract describes placebo.
However, the original journal retracted the paper on 24 September 2026 (notice
PMID 42781833; DOI 10.1002/ijgo.71389). The notice identifies data anomalies and
states that editors consider the data and conclusions unreliable. The trial
must remain outside the synthesis; update the reason and link the notice.

The September retrieval/integrity check predates the retraction. That historical
check is not itself contradicted, and this audit found no use of the retracted
paper in the current primary pool. The correct comparator observation is NOT an
argument for reinstatement.

Severity: changes current wording/integrity record; no primary numerical change.

## Seeded screening sample

From 154 manually transcribed displayed record IDs, seed
`20261008:metformin-pcos-ovulation:screen` selects indices 9,25,26,35,46:
28118681, 19692630, 19552904, 17287476, 42002670.

28118681 and 42002670: original systematic reviews, appropriate independent-trial
exclusions. 19692630: crossover metformin monotherapy, not the current common-
clomiphene-background comparison; final scope exclusion is supported, not every
word of the recorded X-DESIGN reason. 19552904: keep excluded for retraction,
not the inaccurate comparator rationale. 17287476: relevant trial contrast must
be re-adjudicated; X3 is unsupported.

## Existing limitations and unchanged states

The page already discloses treatment-naive/resistant differences, historical Moll
scope disputes, missing trials, provisional assessment and evidence limitations.
Those are not newly discovered here. Odds ratios above one favour the beneficial
ovulation endpoint; they are not 'twice as many births'. No live-birth conclusion
is obtained from this audit. The comparator's add-on subgroup and the complete
broad review are different sets; no G1 parity/reinstatement is inferred.
