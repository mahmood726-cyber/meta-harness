# PCSK9 review (2026-09-27): one result object across analyses, and declared sparse-data methods -- RETROSPECTIVE, NOT landed

Branch `oc/v101-pcsk9-consistency`, from the V1.0.1 candidate stack (c15ed111). Item (2), narratives derived from input objects and
the result-selection rule, is on `oc/cx-pcsk9-narrative`.

## (1) One result object across analyses (`harness/result_objects.py`)

- **Identity:** a result object is its trial, measure, point estimate and interval.
- **Ledger:** `ledger(review)` records every admission decision on the page against that identity, with the deciding
  analysis's own requirements. That covers each outcome's pooled rows and its refused rows (`refused_effect`), and each strand's
  members and declared absences.
- **Consistency:** `consistency()` flags an object ADMITTED in one analysis and REFUSED in another, unless the admitting analysis
  declares `requirements.waives: [reason_code]` with a `because`.
- **Wiring:** the ledger is written to `review.json` as `result_objects`, and `gate.check_result_object_consistency` refuses a
  contradictory page (L1).

### Corpus at 3876a62d

- 32 pages, **100** result objects, **3** shared by more than one analysis, and **1 contradiction**:
  `41211925|HR|0.75|0.65|0.86`. This is VESALIUS-CV's 3-point MACE (the sentence "A 3-point MACE event occurred in 336
  patients ... hazard ratio, 0.75; 95% CI, 0.65 to 0.86").
  - REFUSED by the main MACE pool: RESULT_INCOMPATIBLE, NEAR_MATCH with no declared near-match permission, "lacks ...
    cardiovascular death".
  - ADMITTED by the strict 3-point strand (FOURIER + VESALIUS -> 0.784243, 0.473854-1.297945), whose endpoint text reads "CV/CHD
    death | MI | ischemic stroke" but which declares no waiver.
- **The main pool is itself inconsistent.** It admits ODYSSEY's composite (CHD death, not CV death) as NEAR_MATCH_DECLARED, while
  refusing VESALIUS's CHD-death composite as undeclared near-match.
- **Resolution is a decision for Mahmood**, and the gate blocks until one is recorded. The options:
  - declare the near-match for VESALIUS in the main pool (k 2 -> 3);
  - have the strand declare that it waives RESULT_INCOMPATIBLE, and say why;
  - drop VESALIUS from the strand.

## (3) Sparse data -- no silent continuity correction

- `synth.Study.yi_vi` now raises `SparseDataMethodNotDeclared` for a study with a zero cell unless its `zero_event_method` is the
  declared `CC_0.5`. That is defence in depth, for every caller.
- The pipeline reads the outcome's declared `sparse_data_method`. `CC_0.5` applies the correction and records it as declared.
  Anything else holds the study as `ZERO_CELL_METHOD_NOT_DECLARED`. The absence layer and consumer_consistency keep that code, so
  it is never re-labelled as extraction debt.
- **Corpus:** **1 of 35** served count rows has a zero cell. RECOVERY (PMID 34138478), serious adverse events, 1/16 vs 0/14, was
  served as a one-trial **OR 2.8065 (0.1056 to 74.5638)** through the automatic 0.5 correction. With no method declared it is
  now held.
- **The notice:** the COVID-19 corticosteroids "Serious adverse events" result is withdrawn.
- **GLAGOV:** its injection-site 2/484 vs 0/484 (cited by the review) is not a served row at the pinned candidate. The same rule
  applies to it wherever it is extracted.
- `tests/test_synth.py::test_zero_cell_continuity_applied_only_to_that_study` asserted the silent correction; it defended the
  defect. It now asserts the requirement: refused without a declared method; with CC_0.5, only that study is corrected.

## Full-corpus rebuild (c15ed111 + this branch)

- All 32 topics build (rc=0, every review.json parses): no caller trips the new refusal unexpectedly.
- Against the served pages there are 32 moves: the stack's 31 recorded moves (`moves_83495751.json`, unchanged) plus **one new
  move**, the COVID-19 serious adverse events withdrawal above.

## Tests

- `tests/test_pcsk9_consistency.py` (6) and `tests/test_synth.py`: 14 passed.
- **Guard removal:** treating every difference as explained turns 3 tests red.
