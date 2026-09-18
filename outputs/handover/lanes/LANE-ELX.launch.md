# LANE ELX — one defect on the served glp1 page: a trial whose source is COMMITTED is rendered "value not in committed source" (ELIXA). Missing-state vocabulary folded into the existing modules; ELIXA rendered SOURCE_CONFLICT with every span; membership sensitivity rendered as a demonstration, not a result. Base 237e9094.

Report file: `LANE-ELX-REPORT.md`. Fresh checkout of main at 237e9094 (served tonight: glp1 review_sha256 98726cc125e9fcc7). Record `git rev-parse HEAD`.
Never reset/checkout/stash. No commit. No network. Extend existing modules only (`harness/invalidation.py` owns the missing codes,
`harness/claimgraph.py::regulatory_fact` owns held-document facts, `harness/page.py` renders, `harness/synth.py` pools, `harness/envelope.py`
builds the strand); no new framework, no new module unless a decision has no owner (say which and why).

## The defect (Mahmood's review of edaf5f6b, item 1, MAJOR; audit item 0)
Served glp1 renders ELIXA (PMID 26630143, NCT01147250) as `NOT_IN_COMMITTED_SOURCE / known_eligible_missing: named, value not in
committed source; no number computed`, while the FDA statistical review IS committed on this very tree:
`outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf` (+ `.pdf.txt`), listed in
`outputs/handover/glp1_regulatory/regulatory_sources_glp1.json` -- and the same page quotes that document's Table 55 and Table 17 for
harms. The same defect class applies to FLOW (`held/209637s025lbl.pdf`, label Table 10) and, if a document is held, FREEDOM-CVO.
Rule: a trial whose named source is held (committed bytes, digest recorded) can NEVER be in a "not in committed source" state.

## Inputs you must copy onto this tree first (page inputs; they belong in the same increment as the rebuild)
- `C:\mh-base\outputs\handover\glp1_regulatory\regulatory_sources_glp1.json` (handover branch, commit 00fb83e2) -> same path here. It
  carries the ELIXA decision with `source_conflict` (eight verbatim spans: the same 3-component MACE result, 792 events 392/400 ITT
  on-study, printed as 1.02 (0.887, 1.172), 1.02 (0.89, 1.18), the 4-point primary 1.017 (0.886, 1.168) etc.), FLOW's label span, and
  the ladder attempts. Prove every `document_sha256` in it against `git show HEAD:<held path> | sha256sum` before using it; refuse a
  mismatch in the report.
- `C:\mh-base\outputs\handover\glp1_reviewerB\ADJUDICATIONS.json` -> `outputs/handover/glp1_regulatory/ADJUDICATIONS.json`
  (ADJ-GLP1-003 FLOW locking span, ADJ-GLP1-005 ELIXA conflict; both PROPOSED, NOT countersigned by Mahmood -- render them as such).

## Required end state on the glp1 page (and any page the same code path touches)
1. Missing-state vocabulary, as codes in `harness/invalidation.py` (extend the reason objects, keep every existing code that is still
   true): NOT_DISCOVERED / DISCOVERED_NOT_RETRIEVED / SOURCE_RETRIEVED_NOT_EXTRACTED (alias HELD_NOT_YET_EXTRACTED) /
   EXTRACTED_SOURCE_CONFLICT / EXTRACTED_NOT_ADMISSIBLE / POOLABLE. The state is DERIVED from what is on the tree: a held document
   naming the trial => at least SOURCE_RETRIEVED_NOT_EXTRACTED; an extraction record => EXTRACTED_*; a `source_conflict` record =>
   EXTRACTED_SOURCE_CONFLICT; an adjudication in state PROPOSED never promotes past that. `known_eligible_missing` stays only for a
   trial with NO held document.
2. ELIXA row: state EXTRACTED_SOURCE_CONFLICT; held document path + full sha256; ALL spans verbatim (every numeric rendering, with page
   numbers), the endpoint identified by its DEFINITION span (the 3-component definition sentence), never by a CI fingerprint;
   `adjudication: ADJ-GLP1-005 PROPOSED (not countersigned)`; NOT pooled; k stays 8 and the pooled 0.856 (0.81-0.90) is unchanged.
3. FLOW row: whatever the tree supports honestly -- the label is held (Table 10: 3P 0.82 (0.68, 0.98), 212/1767 vs 254/1766; ADJ-GLP1-003
   PROPOSED) => EXTRACTED_* pending adjudication, not pooled, spans shown. FREEDOM-CVO: derive; if nothing is held, its state says so.
4. Membership sensitivity as a DEMONSTRATION with state `HETEROGENEITY_MEMBERSHIP_SENSITIVE`: compute with the production pooling
   function (`harness/synth.py`, same estimator as the primary: Paule-Mandel tau^2, HKSJ on t with k-1 df, log scale) the pool of the
   8 served rows PLUS the proposed ELIXA row under ADJ-GLP1-005, and render k, estimate, CI, tau^2, I^2, prediction interval for BOTH
   pools side by side, labelled "under the PROPOSED adjudication -- not a result; the primary k=8 pool is unchanged". Expected shape
   (verify, do not hardcode): I^2 from ~0.9% to ~35%, prediction interval crossing 1. The numbers on the page must be computed at
   build time from the rows, never typed in.
5. The headline paragraph must not gain any new numeral from this demonstration (Mahmood: values live in the audit section).

## Plants (write and run FIRST on the untouched tree; save output to `.tmp/elx/prefix_pytest.txt`)
`tests/test_held_source_never_not_in_committed_source.py`:
- for every review, for every trial rendered with a "not in committed source" state, assert NO committed held document names that
  trial (by NCT or PMID in the regulatory manifest) -- FIRES on 237e9094 for ELIXA and FLOW;
- the ELIXA row on the rebuilt glp1 page carries EXTRACTED_SOURCE_CONFLICT, the held sha256, at least eight spans, the definition span
  and `ADJ-GLP1-005 PROPOSED`; no `1.02` appears in the headline paragraph; k == 8 and the pooled estimate equals the served value;
- the membership demonstration block carries HETEROGENEITY_MEMBERSHIP_SENSITIVE and both pools, its numbers equal to a direct call of
  the pooling function on the same rows (recompute in the test).
A fix that clears every failure is a loosened test: re-read each assertion after the fix.

## Then
- rebuild glp1 only (`python scripts/build_topic.py glp1-ra-mace-t2d --now 2026-09-11`), then all 32 if the code path is shared
  (it is: invalidation/page) -- record which pages' `review_sha256`/`html_sha256` moved and why (full-field diff for any page other
  than glp1 whose review object changed; a page must not change for a reason you cannot name);
- `python scripts/retraction_survival.py 237e9094` => 32 of 32 or STOP;
- `python -m pytest tests -q -p no:cacheprovider -x -k "invalid or page or synth or envelope or held or eligib or endpoint"` counts;
- `python scripts/verify_all.py` if time allows (record limb results; the honest ratchet vs 237e9094 will need acknowledgements for
  the glp1 marker counts that change -- list each proposed acknowledgement with its reason; do not sign them).

## Report (MEASURED / INFERRED / CLAIMED; `n of N`)
Plants pre/post; the ELIXA/FLOW/FREEDOM-CVO states before and after with the deriving evidence; the two pools with every number;
diff summary; pages moved; what this increment does NOT establish (the countersignatures; FACT binding of the 8 pooled rows; CENTRAL).
Never a backslash escape through a heredoc; write regexes to files. No commit.
