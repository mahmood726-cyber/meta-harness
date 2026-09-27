# V1.0.1 harness fix: report role in screening (NOT LANDED)

- **Branch:** `evid/v1.0.1-screening-roles`, based on **`v1/candidate` `3876a62d`**. The worktree is `F:\mh-lanes-wt\screen`.
- **Trigger:** an external review of colchicine-postop-af (review hash `48741f59…`, commit `6260e70c`).
- **Codex** was allowed but not needed.

## The defect
The COPPS AF substudy (PMID 22090167) was described four ways, and no one checked them against each other:
- **Narrative** (a hand-written sentence in the topic config): "screened in".
- **Ledger:** excluded X1, "not a randomized controlled trial". The ledger's own span on that row lists the publication type *Randomized Controlled Trial*.
- **Adjudicator:** recommends include.
- **Family object:** lists it as a report of NCT00128427.

Two causes:
1. `screen._is_rct` rejected on the **title word** "substudy" before reading the design.
2. For "prevention" topics, the population **veto** was applied to the abstract body. It fired on COPPS AF's background sentence "Inflammation and pericarditis may be contributing factors …", while the X2 reason said "title/conditions". The same defect was in the second screener.

## The fix
**One screening record per report, carrying three decisions.** `harness/screen._link_and_record` builds it; the ledger fields are *set from* it:

| # | Decision | Values |
|---|---|---|
| 1 | Parent-trial eligibility | ELIGIBLE / INELIGIBLE / NOT_ASSESSED |
| 2 | Report relevance | PRIMARY_REPORT / SECONDARY_REPORT (linked to its parent family) / NO_RESULTS_REPORT / COMPANION_REPORT |
| 3 | Result admissibility | per outcome: POOLED / DECLARED_ABSENT (code) / NOT_IN_OUTCOME, filled after outcomes are built |

- **Secondary reports and substudies** are no longer X1. A secondary report whose parent family already has an included report becomes **X-LINKED** to it, so one trial is counted once. The parent family is the family object's own identity, from `trial_family.prepare`, never a second guess.
- **Protocol, design and analysis-plan papers** get **X-NO-RESULTS**, not "not an RCT".
- **X1 reasons** now name their cause (review / non-primary type / quasi-allocation / not randomised), so a reason never contradicts its own span.
- **Population veto:** both screeners judge it on title and registry conditions only. The positive signal may still use the abstract, as before.
- **Derived artefacts** (`harness/screening_record.py`): the family object's report entry, the screening narrative and per-outcome admissibility are all DERIVED from the record. The hand-written COPPS sentence in `topics/colchicine-postop-af.json` is removed and replaced by the derived sentence.
- **Consistency check:** `consistency_problems` / gate `check_screening_record` fails on LEDGER_VS_RECORD, FAMILY_VS_RECORD, NARRATIVE_VS_LEDGER, REASON_VS_SPAN and FAMILY_VS_LEDGER. ADJUDICATOR_VS_LEDGER is recorded as advisory: the adjudicator is advisory by design.

**Source state SOURCE_INTERNALLY_INCONSISTENT** (in `harness/invalidation.py`) means held and read, but the document's own numbers cannot be reconciled into one set of arm denominators. Such a source is not pooled, not "not retrieved", and never promoted by an adjudication.
- **Fixture:** Mashayekhi 2020 (DOI 10.15171/ipp.2020.11), held under CC BY 4.0 at `outputs/handover/colchicine_poaf_sources/`: PDF sha `7b25535a…`, pypdf 6.13.1 text, and a manifest with 9 offset-verified spans.
- **The contradictions:** 240 randomised and 120 per arm in the text; 81 randomised, with 29 vs 52 allocated, in the flow diagram and table headings; AF 7 (23.9%) vs 13 (25.7%), whose percentages fit neither denominator.
- **Effect on the page:** in colchicine-postop-af's known-missing panel and invalidation reasons it is SOURCE_INTERNALLY_INCONSISTENT and NOT_COMPUTABLE.

## Measured
- **Screening contradictions, corpus-wide:** `scripts/screening_contradictions.py` reads every ledger row of all 32 topics, in full.
  - **v1/candidate: 22 of 3146** screened reports carry a blocking contradiction: 19 REASON_VS_SPAN, 7 FAMILY_VS_LEDGER, 2 NARRATIVE_VS_LEDGER and 1 each of OMISSION_VS_RECORD and OMISSION_VS_PROTOCOL (ICAP), with some reports carrying more than one kind. 5 more carry only an adjudicator disagreement.
  - **This branch: 0 of 3146** blocking. **4** advisory adjudicator disagreements remain as recorded open questions: colchicine-postop-af 39266309, colchicine-recurrent-pericarditis 22430920, omega3 41201837, probiotics 40716758.
  - Evidence: `evidence/screening_roles/CONTRADICTIONS_v1_candidate.json`, `CONTRADICTIONS_after_fix.json`.
- **Served diff against v1/candidate** (`scripts/served_diff_screening.py`, all 32 topics rebuilt):
  - **No pooled number moves in any topic.**
  - **Two result STATES change.** The GI adverse-events outcomes of colchicine-postop-af and semaglutide-obesity-weight become **HARMS_INCOMPLETE**: a secondary report now screened in (COPPS AF 22090167; the STEP 6 post-hoc report 40189961) reports that harm and is not yet extracted. The previous state read "no harm value is poolable"; the new state is more accurate, but it is a served-state change → **for sign-off**.
  - **Declared-absent membership only:** colchicine-secondary-cv-prevention gains 34686461, omega3-cardiovascular-events gains 20952767. Each is screened in, then declared absent, and no result moves.
  - Evidence: `evidence/screening_roles/SERVED_DIFF_vs_v1_candidate.json`.
- **Pinned HM3 controls.** They are superseded by a **declared** file, `docs/evidence/hm3-held-source-audit/screening_roles_supersession.json`. It lists 696 changed screening rows, mostly X1 reasons that now name their cause, plus one harms outcome. `tests/test_hm3_pages.py` accepts exactly those changes; the snapshot is not rewritten.

## Tests
- **`tests/test_screening_record.py`: 14 of 14** pass; 14 fired before the fix (`evidence/screening_roles/TESTS_PREFIX.txt`). They cover:
  - COPPS AF screened in as a secondary report of NCT00128427;
  - the second screener agrees;
  - a secondary report linked to its included primary report and not counted twice;
  - a protocol paper gets X-NO-RESULTS;
  - a genuinely non-randomised report stays X1;
  - every ledger row derives from its record;
  - the served V1 page shows the COPPS contradiction;
  - consistency plants: narrative vs ledger, ledger vs record, family vs record, report under another family;
  - Mashayekhi held and SOURCE_INTERNALLY_INCONSISTENT, never promoted.
- **Full suite:** see the final line of this handover's commit.
- **Environmental failures in the first full run:** a first run lost 23 tests to a full F: disk. F: had filled to 32 KB with 5.2 GB of 1–3-day-old pytest temp directories, which I removed.

## Added from the pericarditis-recurrence review
- **(1) Omission reasons on the one record — DONE.**
  - Per-outcome admissibility now carries each omission's code and reason.
  - Two new blocking checks:
    - **OMISSION_VS_RECORD:** a population omission of a report whose record says the parent is eligible.
    - **OMISSION_VS_PROTOCOL:** a population refusal naming a population the protocol's include rules admit. The include rules are stamped on the review as `screening.protocol_include`.
  - **ICAP (23992557)** was explained three ways, one of them "population is ACUTE (first-episode) pericarditis, NOT the recurrent-pericarditis population", against a protocol that includes acute first episodes.
  - Its note in `docs/known_eligible_missing.json` is corrected; the old note is kept under `superseded_note`, with why.
  - The same stale claim remains in `docs/recovery_log.json`, `docs/search_test_set.json` and `registry/search_benchmark.json`. These are historical logs that the page check does not read; they are left for the owning lanes.
- **(3) Endpoint-scoped SOURCE_INTERNALLY_INCONSISTENT — mechanism DONE, fixture BLOCKED.**
  - A held source's decision may carry `scope_outcomes`.
  - `missing_state(fact, outcome=)` gives SOURCE_INTERNALLY_INCONSISTENT only for those outcomes. The document's other endpoints read SOURCE_RETRIEVED_NOT_EXTRACTED, and an unscoped decision (Mashayekhi) stays whole-document.
  - Screening-record admissibility marks only the scoped endpoint.
  - Tests: `tests/test_omission_and_scope.py`, 7 of 7 (6 fired pre-fix).
  - The ICAP discontinuation fixture (14 vs 10 in Table 3 against 14 vs 12 in the flow diagram) needs the NEJM full text.
- **(2) ICAP Table 2 row recovery, and the CORP safety fixtures — BLOCKED on the sources.**
  - ICAP (NEJM 10.1056/NEJMoa1208536), CORP (Annals) and CORP-2 (Lancet) are subscription-only, with no open-access copy in Europe PMC.
  - One ordinary request to NEJM's PDF returned **403 Forbidden**. The lane does not bypass access controls, and the licences do not permit committing the full text to a public repo.
  - **Path once the PDFs are supplied:** hold them locally (URL and sha256 in `evidence/LOCAL_ACQUISITIONS.json`, not committed). Commit only a short verbatim excerpt: the Table 2 rows with their column headings, the Table 3 and flow-diagram discontinuation lines, and the CORP safety rows, sha-pinned to the held PDF.
  - **Recurrence binding:** bind to the "recurrent course" row (11/120 vs 25/120) plus its headings. The "incessant or recurrent" composite (20/120 vs 45/120) is refused.
  - **Served-number change:** adding ICAP moves Recurrent pericarditis from k=2 to k=3. A result-change notice is added with its countersignature OPEN.

## Targeted verification (4,492 tests, 31 files; the release-archive test is skipped because it needs ~1 GB of temp on a full F:)
4,482 passed and 72 xfailed. The only 10 failures were bundle, execution-record and page-verifier checks against a GLP-1 bundle that was stale after the harness change. The bundle has been regenerated; see the next commit for the rerun.

## Findings not fixed here
- **COPPS AF's AF counts:** its admissibility code is OUTCOME_NOT_IN_SOURCE, while `harness/known_missing.py` hard-codes its AF counts, 20/169 vs 37/167, as IN_COMMITTED_SOURCE. That disagreement predates this change.
- **Advisory adjudicator disagreements:** the four listed above remain open.

## Before landing
- `verify_all.py` has not been run.
- The two HARMS_INCOMPLETE state changes need sign-off.
- This branch and the FLOW/ELIXA branch (`evid/v1.0.1-glp1-admission`) both touch `harness/pipeline.py`, `page.py`, `known_missing.py` and `invalidation.py`, and both regenerate every page. **Merge one, then rebuild the other on top.**
