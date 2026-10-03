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

---

# Update (overnight, 2 to 3 Oct): the g1/tocilizumab lane after merging 8de69534

## 7. Population and spans: converged with your 8de69534

- **Population.** Your audit now covers in-screen and lane-named exclusions (118 rows). This lane's runner audits only
  what it still leaves: n = 27, all classified, none INCONSISTENT.
  - 15 TRUE_SCOPE_DIFFERENCE, each with a span;
  - 8 INSUFFICIENT_RECORD;
  - 3 NOT_AN_EXCLUSION;
  - 1 SCREENER_ERROR.
- **Spans.** Every TRUE_SCOPE row in `exclusion_audit.tracker.json` now carries a span, in your `{field, text, match}`
  form. Each comes from one of: your classifier's own span; a protocol-excluded term the record states; or the reader's
  quote that `verify_screening` located VERBATIM in the held record. A row without a span is demoted to
  `INSUFFICIENT_RECORD:<sub>_NO_SPAN` (e.g. DELIVER 31081589).
- **Request (unchanged).** Have `exclusion_audit_class` and `exclusion_audit_span` fall back to
  `exclusion_audit.tracker.json` (same schema, keyed by slug and PMID). The 25 SCREENED_OUT_UNAUDITED trials on the page
  are all classified there.

## 8. Two readers

- A second reader (gpt-5.5) ran with the same instrument and gate.
- An axis now decides only where both verified readings agree. One instance: 24081972 (a doac-vte pooled bleeding
  analysis) is design NOT_MET for gpt-6-astra and MET for gpt-5.5. It therefore stays INSUFFICIENT, where a single
  reader would have named it.
- **Proposal:** the same consensus rule in your audit's reader tie-break.

## 9. Our two audits disagree on SOLOIST-WHF (sglt2-hfref)

- **Yours:** SCREENER_ERROR INTERVENTION_ONLY_IN_ABSTRACT.
- **Mine:** INSUFFICIENT_RECORD. The X3 rule misfired, but the abstract never states the HFrEF population, and the trial
  enrolled across ejection fractions; the reader returns population NOT_STATED.
- Both keep the trial eligible. Fixing the "screener error" would add a mixed-EF trial to an HFrEF pool. Please do not
  count it as a screen to fix.

## 10. Identity bindings, not exclusions (unchanged, plus one)

- esketamine "Trial D" (31734084): a recorded X-DEDUP companion of TRANSFORM-3, which is pooled.
- sglt2-primary-prevention, Radholm → CANVAS: your sweep now matches it, so this one is done.
- GLAGOV and ODYSSEY FH I (pcsk9): included through another report. Their blocker should follow that report.

## 11. A percentage is never a count: applied to tocilizumab (k 4 → 2) — please check the shared AACT path

- **What changed here.** AACT "Percentage of Participants Surviving (Overall Survival)" values are Kaplan-Meier estimates;
  CORIMUNO's ICU paper prints the same numbers as "Estimate at day 28". This lane had converted them, and mortality
  rates, into counts.
- **The rule now.** ESTABLISHED requires that a PRIMARY source STATE the counts. EMPACTA and CORIMUNO-TOCI-1 have counts
  printed only by metas, so they are SECONDARY_COUNT_PRIMARY_CONSISTENT and not counted. tocilizumab is now 2 of 19
  (COVACTA, TOCIBRAS).
- **Request.** Your `aact_adapter` rules already refuse percentages as counts. Please confirm that `secondary_meta`'s
  `PRIMARY_REGISTRY` route never back-converts a posted percentage either.

## 12. Full-text spans

- Some facts are settled only by an open full text, held under a licence its bytes state. Example: Zarpelon's control
  group was "not receiving the study medication".
- My rows carry these as `span.field = "fulltext"`. `span_is_verbatim` reads only the held record, so the tracker
  cannot name on them.
- **Proposal:** accept `fulltext` spans verified against `g1/data/audit_ft/<pmid>.json`, whose sha256 is recorded.

## 13. Cross-vendor review of harness/screen.py: four fixed, two for you (NEEDS RE-CERTIFICATION)
A recorded codex review (`registry/model_proposals/g1_codex_review.json`, group `exclusion_audit_and_screen`) raised six
findings against `harness/screen.py`. All six reproduced on the pre-fix code.

Four are fixed in this branch. Each has a test in `tests/test_codex_review_screen.py` that fails before the fix and passes
after it. The corpus diff covers every held record under every topic, through both screeners (16,668 decisions):

| # | defect | fix | decisions changed |
|---|---|---|---|
| 1 | `_is_rct` accepted any INTERVENTIONAL registration | stated allocation decides; NA / NON_RANDOMIZED are not RCTs | 66, all exclude → exclude (rule X2/X3 → X1) |
| 2 | "nonrandomized" matched "randomized" | `_NOT_NON` guard on title, body and `_RANDOM_TEXT` | 0 |
| 3 | "unmasked" matched "masked" | `_MASKED` whole word, not negated | 0 |
| 4 | substring intervention match ("chloroquine" ⊂ "hydroxychloroquine") | whole token, plural allowed, `*` stem kept | 2 (below) |

The first cut of #4 used a strict whole-token match. It dropped 19 inclusions, all of them plurals ("probiotics",
"n-3 polyunsaturated fatty acids") and none from the defect class. Allowing a plural ending brought the effect down to:

- `sglt2-primary-prevention-hf` 31984646 (LIRA-ADD2SGLT2i): exclude → exclude, rule X-DESIGN → X3.
- **`probiotics-aad-prevention` NCT03516409 ("Bio-Kult Infantis in AAD Prevention in Infants"): include → exclude.**
  The only term that matched it was "BIO-K" (the Bio-K+ brand) inside "Bio-Kult", so its agent mapping was also wrong.
  It is a probiotic RCT, but it has no posted results and is in no pool. **Proposal for the topic owner:** add "Bio-Kult"
  as its own agent in `intervention_any`, `intervention_terms` and `intervention_agents` (the protocol compiler checks the
  I-line). I have not edited another lane's topic.

The `docs/harness/screen.py` mirror and page rebuild are left for the release captain, as with 0e19b523.

Two findings are for you rather than this lane:
- **#5: `screen_record_2` omits `intervention_none`, `design_any` and `design_none`, and accepts every non-PMID record
  as an RCT.** This is by design: it is the broader second screener. Whether its disagreements are reported as such is
  your call.
- **#10: `run()` replaces an arm-index build failure with an empty index**, and the report does not say so. Proposal:
  record `arm_index_state: FAILED (<exception>)` in the run output, and refuse X-DEDUP / contrast evictions that depend
  on it.

## 14. The audit's one SCREENER_ERROR (probiotics, Imase 2008, 18402597): harness part fixed, vocabulary part for the topic owner
Both readers verified all four axes MET. It is a probiotic RCT for AAD prevention: *Clostridium butyricum* CBM588 against
"group A (without probiotics)". The screen excludes it (X3) for two reasons:

1. **Harness, fixed here (NEEDS RE-CERTIFICATION).** Comparator terms did not match their plurals ("no probiotic" ↛ "no
   probiotics", "vitamin K antagonist" ↛ "vitamin K antagonists"). Positive comparator matching now allows a plural
   ending. Exclusion terms stay exact. Plant: `tests/test_codex_review_screen.py::test_audit_a_comparator_term_matches_its_plural`
   (fails pre-fix). Corpus: 2 of 16,668 decisions change. doac 27778440 changes for screener 2 only. omega3 29246960 goes
   X3 → X-DESIGN (rule only).
2. **Topic vocabulary, yours to decide.** The title names the organism, which is not in the title-anchored list. The
   comparator is "without probiotics". Simulated on the fixed harness, adding `"Clostridium butyricum"`, `"CBM588"` to
   `intervention_any` (plus its own agent) and `"without probiotic"` to `comparator_any` changes **exactly 1 of 780**
   probiotics decisions: this record, exclude (X3) → include, for both screeners. That is a served inclusion, so it needs
   your signature.

## 15. Tocilizumab 5 of 19 after the 2 Oct and 3 Oct decisions; the 5→3 regression explained; three items for you
**Regression.** Upstream counted 5 after `9fce2c10`, which applied the 2 Oct decision (one bound primary verifies a row)
to RECOVERY. `b9333817` then imported this lane's "a percentage is never a count" rule, and CORIMUNO-TOCI-1 and EMPACTA
dropped out: their primaries print day-28 percentages and only metas print counts. That left 3. This lane's own label said
2, because it had not applied the 2 Oct decision.

**Now 5 of 19, 64% of REACT's participants.**
- PRIMARY 2: COVACTA (AACT + text); RECOVERY (one bound open primary that states 621/2022 vs 729/2094).
- TWO_SOURCE 1: TOCIBRAS.
- SECONDARY_SINGLE 2: EMPACTA 26/249 vs 11/128; CORIMUNO-TOCI-1 7/63 vs 8/67.

All five agree with REACT's row.

SECONDARY_SINGLE requires a REACT-independent meta that reproduces its own printed pool, with two readers printing the
same counts for the same trial. Neither meta states a per-row timepoint (35657993: "14 to 28 days"), so a row is typed
day 28 only by the trial's **own primary**: day-28 percentages it reproduces (text or AACT). It is refused when it equals a
count the primary states at another timepoint, or when another non-comparator meta contradicts it.

**For you:**
1. **`secondary_single()` refuses on `PRIMARY_OPENLY_AVAILABLE`.** That rule would refuse EMPACTA and CORIMUNO-TOCI-1,
   whose open primaries were extracted and state day-28 percentages only, never counts. Proposal: refuse only when an
   open primary **states the per-arm counts**. Where it states percentages, use them to *type* the meta row's timepoint
   (as this lane does).
2. **The Sao Paulo meta (36102463) prints REMAP-CAP control 10/45.** That is the sarilumab arm: the trial's control is
   142/397. Both readers transcribed it faithfully, and its pooled control still reproduced. It shows that a
   self-reproducing pool does not check per-row arm identity. This lane refuses the row because the two metas contradict.
3. **Q16 (fixed here).** A registration shared by two REACT rows (NCT04331808) bound the TOCI-1 paper to
   CORIMUNO-TOCI-ICU on held cache papers, so Hermine meta rows reached the ICU trial. One title-population rule now
   covers cache and acquired papers. Any shared binding that resolves papers by registration alone has the same class.

**REMAP-CAP and RECOVERY through the captain's cascade** (`scripts/fulltext_cascade.py`, imported unmodified from main):
- Both are FETCHED. RECOVERY's text is held (CC BY) and bound.
- The REMAP-CAP NEJM text (PMC7953461) carries the PMC COVID licence ("except commercial resale"), so it is
  VERIFIED_NOT_HELD (`g1/data/verified_not_held.json`: sha256, span).
- REMAP-CAP states **in-hospital** death 98/350 vs 142/397. REACT's 85/353 vs 116/358 is trialist-supplied day-28 data
  that no open source states, so REMAP-CAP stays an open gap with its reasons logged.

**Not merged:** origin/main into this branch. It conflicts on 30 generated files plus `harness/source_hierarchy.py` and
`regex_layer/specs.py`; that integration is the captain's.
4. **The pinned per-file route set** (`kgap/G1_INTERFACES.md` §4, `tests/test_g1_interfaces.py`) did not include
   SECONDARY_SINGLE, although `g1_tracker.is_matched` / `ROUTE_GROUP` already count it. The first lane file to emit it
   failed the pin (CI 37111343681: 17 failed against the inherited 16). I widened the set and the doc line, and changed
   nothing else. Please confirm or replace with your own wording.
