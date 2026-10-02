# Dispatch: g1/tocilizumab lane → k-gap lane (acq/k-gap) and captain

## 1. SCREENED_OUT_UNAUDITED: the audit's population, not the trials, was the gap

- **Defect.** `scripts/k_gap_exclusion_audit.py` builds its population from `counterfactual_members.json`. The
  tracker sees more exclusions:
  - comparator trials already in our screen ("IN SCREEN PMID …");
  - its own first-PMID seeds;
  - lane-seeded reports.
  These reached the page as SCREENED_OUT_UNAUDITED. The audit reported where it looked.
- **Runner.** `scripts/g1_exclusion_audit_tracker.py` takes the population from the tracker files: every trial the
  shared audit does not cover, including those this audit has already classified, so the denominator cannot shrink.
  - It classifies each with `k_gap_exclusion_audit.classify`, imported unchanged.
  - It then applies four refinements, below.
- **Output.**
  - `outputs/k_gap/exclusion_audit.tracker.json`: **n = 82**, same row schema plus the shared class, the refinement
    used and the reader axes.
  - `g1/EXCLUSION_AUDIT.md`: per-trial table.
  - Result: 52 TRUE_SCOPE_DIFFERENCE / 7 SCREENER_ERROR / 17 INSUFFICIENT_RECORD / 3 INCONSISTENT /
    3 NOT_AN_EXCLUSION.
- **Request.** Make `g1_tracker.exclusion_audit_class` read `exclusion_audit.tracker.json` after `exclusion_audit.json`
  (same schema, keyed by slug and PMID), or adopt the tracker population in the shared audit. Until then, the batch
  topics keep showing SCREENED_OUT_UNAUDITED for trials that are now classified. `sglt2-hfref-hosp-cvdeath` (this lane)
  already reads it.

## 2. Second reader on the whole population (recorded, codex)

- **What ran.** The same instrument as `scripts/k_gap_screen_recheck.py`: its prompt, schema and `verify_screening`
  gate, with gpt-6-astra in batches of 6. It covered 79 callable items.
- **Agreement with our rule.** 44 agree, 13 disagree, 22 cannot tell.
- **Where it is stored.** `registry/model_proposals/k_gap_screen_recheck.tracker.json`; the call records are in
  `registry/model_calls/`.

## 3. Classifier defects (proposed for `k_gap_exclusion_audit.classify`; implemented lane-side in `refine()`)

Plants are in `tests/test_g1_exclusion_audit.py`.

| id | defect | instance | rule now |
|---|---|---|---|
| R1 | a repair flip (`prevention=True`) overrides a population the protocol excludes that the record STATES | WOMAN-2, TXA: "prevent postpartum haemorrhage"; `population_none` lists "prevent" | TRUE_SCOPE when the stated term is confirmed by reader population NOT_MET |
| R0 | a repair flip proves only that THIS rule misfired; the other axes are never checked | SOLOIST-WHF: X3 misfired, but the abstract never states the HFrEF population. LoDoCo, DART: other axes NOT_MET | reader NOT_MET on another axis → TRUE_SCOPE; NOT_STATED → INSUFFICIENT_RECORD |
| R2 | the reader tie-break exists for X2 only | 24081972 (pooled bleeding analysis), DELIVER design paper, PACMAN-AMI, ARTS-HF design paper, ... | reader verdict on the axis the rule tests: X1 → design, blinding X-DESIGN → design, X3 → comparator/intervention. Not a context X-DESIGN rule (Lord 2006) |
| R3 | INSUFFICIENT_RECORD never looks for the full text | Zarpelon: the open full text says the control group was "not receiving the study medication" | full text via the cascade's R1/R2 rungs (`g1/data/audit_ft`), held only under a licence stated in the bytes |

## 4. Screener classes fixed in `harness/screen.py` (NEEDS RE-CERTIFICATION: `analysis_code_sha256` moves)

| class | defect | corpus effect |
|---|---|---|
| RANDOMISED_SUBSTUDY_VETOED_BY_TITLE | the "substudy" title veto excluded a record typed Randomized Controlled Trial whose abstract describes its randomisation (COPPS-POAF, 22090167, the COPPS trial's only report of postoperative AF) | of 3,217 PMID records, 6 are RCT-typed with a substudy title; 3 also self-describe as randomised and now pass X1 |
| BODY_RCT_MISSED_RANDOMIZED_CONTROLLED_STUDY | `_BODY_RCT` lacked "controlled study" (Wu 2020: "a prospective, randomized, controlled study"; PubMed type only "Journal Article") | control: "randomized controlled studies" in a review still does not match |

- **Decision diff** over 15,803 screening decisions (every topic's records plus every seeded member):
  - 80 change: 76 are reason-only (X1 → X2) on the two target records under unrelated topics, and 4 flip to include.
  - The 4 that flip to include: colchicine-postop-af 22090167, colchicine-secondary-cv 34686461, omega3 20952767,
    hfnc 38191347.
- **Served pools** (in-memory build, before and after) are identical on the 3 buildable topics. Each new include is
  declared absent (OUTCOME_NOT_IN_SOURCE), and k and every estimate are unchanged. hfnc cannot be built in this worktree
  (COMPARATOR_PANEL: registered topic source panel missing; this predates the fix).
- **Not changed:** `screen_record_2`, the independent second screener. Any new dual-screening disagreement is
  deliberate.
- **Mirror.** The same hunks are applied to `docs/harness/screen.py`. That mirror ALREADY differed from
  `harness/screen.py` at line 424 before this change.

## 5. Tracker defect: SCREENED_VIA_OTHER_REPORT with an INCLUDED report is not an exclusion

- **The rule.** `blocker_class` stops at `SCREENED_VIA_OTHER_REPORT`. When the via report was included, the trial must
  follow the via report:
  - POOLED → bind the identity;
  - DECLARED_ABSENT → its extraction class;
  - not in the topic's own build → seed it.
- **Instances (3 of 3).**
  - **sglt2-primary-prevention-hf, Radholm (9):** the comparator cites 29526832 (CANVAS Program, NCT01032629). We POOL
    CANVAS via 28605608 (trial_family_id NCT01032629). The comparator's table row has no NCT, and the tracker binds
    only by PMID or table NCT. **k matched 3 → 4 of 7 once bound**, pending the comparator-row comparison.
  - **pcsk9-mace, GLAGOV:** via 27846344 is declared absent (outcome_not_reported).
  - **pcsk9-mace, ODYSSEY FH I:** via 24842558 is not in the topic's own build.

## 6. Remaining SCREENER_ERRORs outside this lane's topics (not fixed here)

- **probiotics-aad-prevention, POPULATION_VOCABULARY ×5** (including Wu 2020 after its X1 fix): H. pylori triple
  therapy and "antibiotic-induced dysbiosis" populations. The reader reads them as population MET. Fixing this is a
  change to the registered protocol's wording, so it is Mahmood's decision, not a harness fix.
- **metformin-pcos-ovulation, COMPARATOR_WORDING ×1 (PCOSMIC).** This is the known head-term class.
