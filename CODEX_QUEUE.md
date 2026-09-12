# Codex work queue — meta-harness (hand-off for full-width, post-reset continuation)

Durable brief so Codex (or a future session) can keep the mechanical work running after Claude Code resets.
**Every task keeps the bar: verify against source, refuse on ambiguity, name every decline, never relax a
gate to grow a number, push every commit and confirm the live URL.** Repo: `C:/meta-harness`. Invocation:
`codex exec -s workspace-write -c sandbox_workspace_write.network_access=false -C /c/meta-harness --skip-git-repo-check "<task>" </dev/null`
(network OFF for offline analysis; serialise any network fetch, never run fetch-heavy lanes in parallel — a
throttled 429 silently degrades the cache, see JUDGELOG). After any change: `python -m pytest -q`,
`python scripts/reproduce_review.py`, `python -m harness.gate docs/reviews/*`, regenerate the index
(`python -m harness.index docs`), commit, `git push origin main`, then poll the Pages build and fetch the
live URL to confirm — a landing is not landed until read live.

## Priority queue (highest value first)

0. **[DONE cycle 75] omega3 ORIGIN wrong-endpoint — FIXED via a verified-effects override tier.** In
   `omega3-cardiovascular-events`, ORIGIN (PMID 22686415) is pooled as its PRIMARY outcome "death from
   cardiovascular causes" (HR 0.98) under our MACE / major-vascular-events outcome; the correct value is the
   major-vascular-events HR **1.01** (1034/6239 vs 1017/6266), stated in the same abstract. Magnitude is
   negligible (both null) but it is the wrong endpoint. **Constraints learned this session (do not repeat):**
   a broad "prefer specific keyword over generic 'primary outcome' anchor" reordering REGRESSES sglt2-ckd
   (flips CREDENCE from its intended primary composite 0.70 to a renal-specific sub-composite 0.66,
   inconsistent with DAPA-CKD/EMPA-KIDNEY); removing the generic keywords from the omega3 topic breaks 4
   other omega3 trials that legitimately match on "primary outcome". A SAFE fix is one of: (a) tighten
   `extract._effective_kws` so the generic anchor is disabled when the trial's stated primary-definition
   endpoint does not match our outcome by MORE than a single generic disease word (ORIGIN's "death from
   cardiovascular causes" shares only "cardiovascular" with MACE) — then reproduce ALL 29 and confirm ONLY
   omega3 moves; or (b) a committed per-(trial,outcome) override that beats the abstract for ORIGIN only.
   Verify against source, reproduce all 29, gate, push, confirm live.

1. **Adversarial per-trial source re-verification of the remaining ~19 topics** (the oldest 10 are done, see
   JUDGELOG cycle 75). For each pooled trial in each remaining topic, check against `cache/<slug>/records.json`:
   number-in-source, arm identity (not swapped/inverted), scale/estimand match, subgroup (whole-trial not a
   slice), multi-arm (no silent single-arm pick), factorial (marginal not a cell), timepoint. Flag `DEFECT:`
   with the correct value if a wrong number is live; correct or withdraw the page and record it. Write to
   `scratchpad/audit_<slug>.md`. This is the single most important remaining check — a defect here is a
   wrong number currently served.

2. **GRADE certainty rating per topic** (currently NOT built — a named wall in COMPLETION.md). From each
   page's rendered evidence only (RoB2 block, heterogeneity I²/τ², imprecision from k and CI width,
   indirectness from the scope note, publication-bias note), assign a per-domain and overall GRADE
   (high/moderate/low/very-low) with a one-line reason each. Never invent data; where a domain cannot be
   rated from what is on the page, say "not assessable from the served page". Emit a structured
   `docs/grade.json` keyed by slug and render a GRADE section (mirror `_error_coverage_section` — object-
   derived, no hand-typed numbers, so the anti-drift guard stays satisfied).

3. **Extend the independent number-in-source check to all 29** (deterministic; the oldest 10 pass). Reconcile
   any apparent miss the way cycle 75 did (a ratio may be count-derived: RR from RRR/rates, rate-ratio from
   events) before flagging — only a number that cannot be derived from a stated source value is a defect.

4. **Continuous-primary candidate sweep, continued** (bar-limited — 5/5 declined so far; do NOT lower the
   bar). Probe further single-dose two-arm drug/outcome pairs against posted ClinicalTrials.gov results for a
   raw per-arm mean±SD at one common timepoint across same-scope trials. Register (protocol committed first =
   registration) only a topic that clears the bar; otherwise decline with the reason named. LSM/SE endpoints
   and scale/timepoint/design-heterogeneous symptom scales are declines, not builds.

5. **Specification curve** for a topic with real analytic choices (e.g., fixed vs random effects, HKSJ on/off,
   estimand variants), rendered as a sensitivity panel — the second named wall in COMPLETION.md.

## How to correct a per-trial defect SAFELY (the sanctioned pattern — use this, not a broad extractor change)
When the abstract extractor pools a source-backed but WRONG number for one trial+outcome (wrong endpoint,
wrong denominator, a subgroup, an AE count as another outcome), correct it with a **narrow, flagged,
regression-tested, reversible** override — never a broad extractor change (a broad "prefer specific keyword
over the generic 'primary outcome' anchor" reorder regressed sglt2-ckd and broke 4 omega3 trials this run):
1. Add a committed `verified_effects` entry for that PMID with `"override": true`, the correct effect/CI/scale,
   the **verbatim source span** it comes from, and a `verification` note showing the arithmetic
   (`harness/pipeline._build_outcome` checks override entries at the TOP of the hierarchy — above the
   abstract — but ONLY when the flag is present, so unflagged entries stay pure fallbacks and no other page
   moves). Template: `cache/omega3-cardiovascular-events/verified_effects.json` (ORIGIN 22686415 → HR 1.01).
   For a DENOMINATOR/count fix where the value is auto-poolable, correct `verified_arms.json` instead
   (END-AF 27502857 → 26/179 vs 37/181). For an AE-count-as-another-outcome, the general null-result-clause
   guard (`extract._kw_only_in_null_result`) already declares it absent (COPPS-2 25172965).
2. **Regression-test it** (see `tests/test_verified_override.py`): assert the override wins, an UNFLAGGED
   entry does NOT, and the OLD bug reproduces without the override.
3. Rebuild all 29, `reproduce_review.py`, and confirm **ONLY the intended page moves**. Push, read live.

## Invariants a task must never break
- The two-limb gate and `reproduce_review.py` must stay green; the pre-commit hook regenerates the index and
  requires a byte-match, so any hand-typed prose number that is not object-derived or whitelisted will fail
  `_validate_prose_numbers` (that is intended — derive it or whitelist it with a reason).
- 33/33 error-library coverage; every pooled number verified against its committed source.
- Never edit the gate to pass; never `--no-verify`; never work in `C:/rmfw`.

## Extended-audit residue (cycle 75) — 2 findings QUEUED with evidence (verified, disclosed/nuanced, safe fix)
Both are lower-severity than the 10 defects fixed this cycle (disclosed or metadata), queued to avoid a
time-pressured regression like the reverted specific-over-generic reorder:
- **[DONE cycle 75] sglt2-ckd-progression — resolved to clean HR pool** (DAPA-CKD 0.61 + EMPA-KIDNEY 0.72 reported kidney HRs via verified_effects override; CREDENCE kept at primary 0.70). DAPA-CKD and EMPA-KIDNEY
  are pooled from arm counts (RR) while CREDENCE is HR; the page LABELS the pool "mixed (HR/RR)" (disclosed,
  not hidden). The trials report kidney-composite HRs directly (DAPA-CKD ~0.61 [0.51-0.72], EMPA-KIDNEY
  ~0.72 [0.64-0.82] — VERIFY against each cached abstract for the exact kidney-composite HR and CI). Fix:
  verified_effects override:true for DAPA-CKD (32970396) and EMPA-KIDNEY (36331190) to their published
  kidney-composite HRs, AND confirm CREDENCE (30990260) is its primary-composite HR 0.70 (NOT the
  renal-specific 0.66 — see cycle 75: that sub-composite is a different estimand and inconsistent with
  DAPA/EMPA primaries). Result: a clean HR pool. Reproduce must move ONLY sglt2-ckd.
- **[DONE cycle 75] noac-vs-warfarin ENGAGE-AF 60mg CI 97.5%->95%** (converted to 0.745-1.016 in dose_selection.json). The dose_selection entry stores HR 0.87
  (0.73-1.04), but the source labels that a 97.5% CI ("hazard ratio, 0.87; 97.5% CI, 0.73 to 1.04"). Treating
  a 97.5% CI as 95% understates the SE and overstates this trial's inverse-variance weight. Fix: either
  convert the 97.5% CI to a 95% CI (z=1.96 vs 2.24: SE = (ln0.87-ln0.73)/2.24; 95% CI = exp(lnHR +/- 1.96*SE))
  before storing, or add a per-trial ci_level field the synth path honours. Low magnitude, one trial.

## Extended-audit residue part 2 (cycle 75) — low-severity, verified, disclosed/labelled (queued)
The full harvest of all 5 extended lanes found these beyond the 10 fixed + 2 queued above. None is a hidden
wrong number (each is disclosed or a config-metadata label), so they are polish, not corrections:
- **config `estimand` vs rendered scale mismatches** (the page renders the trial's TRUE scale, correctly —
  these are honest, just a config-target-vs-actual label gap): corticosteroids-covid19 declares OR but the
  k=1 RECOVERY row renders IRR 0.83 (rate ratio); denosumab-vertebral "Nonvertebral fracture" declares RR
  but renders HR 0.80; corticosteroids-cap "Hyperglycaemia" declares RR, pool labelled "mixed (OR/RR)" with
  Aujesky OR 1.96. Safe fix: set each outcome's declared `estimand` in the topic JSON to the scale actually
  reported (IRR/HR/OR), OR leave as-is (rendered scale is already honest). Do NOT force a count-derived
  conversion that loses the trial's reported estimand.
- **semaglutide GI completeness** (not a wrong number — the SAE-as-GI defect is already fixed and those
  cells are declared-absent): STEP-1/STEP-3 DO report real GI adverse-event rates in their abstracts
  (e.g. STEP-3 ~82.8% vs 63.2%). Recover them as verified_arms override entries (derived counts) to raise
  the GI harm outcome's k from the current honest-but-thin state. Verify each % x N against the abstract.
- **melatonin k=1 is Circadin's pre-planned age-65-80 analysis** (n=137/144 of 791), NOT whole-trial — this
  is DISCLOSED on the page ("population: Pre-planned analysis on ITT population age 65-80") and is the
  trial's registered primary analysis, so it is honest as rendered; no change needed unless a whole-trial
  sleep-latency MD/SD becomes available (none in the cached source).
- **corticosteroids-cap 36942789 (CAPE COD) timepoint label**: pooled number is 28-day mortality; the
  outcome declares "30-day or in-hospital". 28d ~ 30d (defensible harmonisation); align the label or note it.

## Reviewed and judged DEFENSIBLE (cycle 75 full harvest) — recorded so they are not re-flagged as defects
- **statins-primary-prevention-elderly / JUPITER (20404379)**: pools JUPITER's age>=70 subgroup (5695 of
  17,802), which the audit flagged as "subgroup". For a primary-prevention-ELDERLY topic this is the CORRECT
  data (the elderly subset is what the topic is about); the source is the trial's pre-specified elderly
  analysis and the row renders HR 0.61 honestly. Config estimand says RR (rendered HR) — a label nuance only.
- **sglt2-hfref-hosp-cvdeath / DAPA-HF (31535829)**: DAPA-HF's primary composite is CV death or worsening HF
  (hospitalisation OR urgent HF visit); EMPEROR-Reduced (32865377) is CV death or HF hospitalisation. Pooling
  both under "CV death or HF hospitalisation" is the field-standard sglt2-HFrEF harmonisation (the urgent-visit
  component is small and every published sglt2-HFrEF MA pools these two composites together). Negligible
  magnitude; not a wrong number. Optionally rename the outcome to "...or worsening heart failure" to match.

# ===================================================================================
# FORWARD PLAN — per-stage weakness assessment + improvement plan (cycle 75, object-derived)
# ===================================================================================
#
# STATUS (cycle 77 — cross-family independence + corpus-growth preregistration):
#  [DONE] ⭐ CROSS-FAMILY INDEPENDENCE (fixes the deepest weakness 'everything is self-assessed'):
#         Gemini 3.1 Pro via AGY (non-Claude, shares no architecture) re-extracted every pooled number from
#         the same committed source. Agrees 84/90 comparable (93.3%); 3-family agreement (harness+GPT-5+Gemini)
#         on 62; 0 wrong after adjudicating all 6 disagreements. scripts/crossfamily_compare.py, committed raw
#         docs/crossfamily_raw.json (regenerates without re-calling), rendered on index. LIVE.
#  [DONE] PROVENANCE metric (docs/provenance.json, 75/99 abstract) + 3 stated LIMITATIONS (OA-only comparators,
#         self-hosted registration, own topic selection) + error-rate shared-architecture caveat. LIVE.
#  [DONE] ERROR-RATE freshness guard + committed sample (docs/error_rate_sample.json). Screening kappa=0.84.
#         Harms-row sweep (docs/harms_audit.json): 1 under-extraction fixed, 1 bar-held decline, rest correct.
#  [DONE-BATCH] Preregistered 15-topic EXPANSION TIER (PREREGISTRATION_v2.md) before running; larger evidence
#         bases + 5 declared-hard. dpp4-mace-t2d build lane piloted (caught CT.gov %-as-count + CAROLINA active
#         comparator itself — verify-before-build working in-lane).
#  REMAINING QUEUE (continue at 16+ lanes; fetch SERIALISED to avoid 429):
#   - BUILD THE EXPANSION TIER: one lane per remaining topic (sglt2-primary-prevention-hf, ics-copd,
#     statin-secondary, doac-vte, ppi-stress-ulcer, thrombectomy-stroke, aspirin-primary, beta-blocker-post-mi,
#     ace-inhibitor-hfref, tirzepatide-weight, canagliflozin-amputation, remdesivir-covid, intensive-bp,
#     vitamin-d-fracture). Author config+protocol from the template, fetch (serial), build, VERIFY every number
#     vs source (a generated config is a hypothesis), gate, live, parity, blind judge. Declines are output.
#   - COCHRANE HEAD-TO-HEAD (external gold standard): pick a topic where a Cochrane/OA review publishes its
#     per-trial extracted data (RevMan data tables), extract theirs, compare our per-trial numbers to their
#     HAND extraction trial-by-trial. Closest external validation without a human.
#   - CROSS-FAMILY blind JUDGING (re-run page-vs-comparator judgement with a non-Claude judge) + cross-family
#     SCREENING adjudication (fixes 'two rule sets share an author').
#   - Complete-evidence-base LABEL where k is small because the literature is small (render as complete, not thin).
#   - Cluster DESIGN-EFFECT correction (unit_of_analysis already flags; needs a stated ICC); SEARCH independent
#     seed set (absolute recall); RoB2-from-methods with span sampling + agreement rate stated.
#   - Drive the abstract share below 75/99 (promote abstract numbers to structured/full-text tiers).
#
# CYCLE-77 CLOSE:
#  [FIXED] dpp4-mace-t2d TECOS 4-point-composite estimand defect (caught by cross-family Fable QA on a page
#    that passed every internal gate) -> TECOS declared absent, dpp4 k=2. Guard extract.composite_component_
#    mismatch() added + regression-tested. Defect tally 15.
#  [HELD] sglt2-primary-prevention-hf (k=4 build in scratchpad/sglt2_hold/) — 3 of 4 HHF HRs (EMPA-REG 0.65,
#    VERTIS 0.70; CANVAS 0.67 ambiguous) are SECONDARY outcomes NOT in the committed abstracts; the lane's
#    verified_effects overrides cite uncached label/secondary sources. TO SHIP: fetch each trial's HHF-outcome
#    source (secondary paper / DailyMed label / CT.gov results) into cache/sglt2-primary-prevention-hf/, verify
#    the per-arm HHF counts + HR against it, then protocol-first commit + gate (only DECLARE 0.73 is currently
#    abstract-verifiable). Do NOT ship on a lane's hand-authored override alone — a build-lane override is a
#    hypothesis until its digits are in a COMMITTED source (dpp4 shipped because its HRs were verbatim in the
#    abstracts; sglt2-pp is held because they are not).
#  RULE for all expansion builds: ship only when every pooled number is located in a COMMITTED source span;
#  secondary-outcome effects (HHF, components) usually need their own source fetched, not the primary abstract.
#
# STATUS (cycle 76 — executed against the Codex budget; all pushed and verified live):
#  [DONE] C1 / Stage-1 ERROR RATE — blind accuracy census (47 Codex lanes): 99 pooled numbers
#         independently re-extracted from source BLIND to the stored value; 95/99 re-checkable, 92
#         exact, 0 confirmed our-errors after adjudication; the census SURFACED + FIXED one wrong-
#         endpoint defect (semaglutide GI-AE). Rendered on the index (docs/error_rate.json);
#         scripts/error_rate_compare.py + error_rate_pass2.py.
#  [DONE] Stage-2 RISK OF BIAS — RoB-stratified sensitivity re-pool per primary (harness/rob_sensitivity.py),
#         regenerated into review.json + rendered; coverage measured (46/79 trials, 13/29 topics, 0 'high').
#         NOT done: model-assisted RoB2 FROM METHODS TEXT to raise coverage (R1) — still queued.
#  [DONE] Stage-3 GRADE — partial object-derived certainty (harness/grade.py) rendered on the RoB tab;
#         publication bias from the registry ghost census, indirectness left to human judgement.
#  [DONE] Stage-4 PAPER — object-derived Manuscript tab (harness/manuscript.py) + gate limb
#         check_manuscript_numbers (refuses any un-derived numeral; negative-tested).
#  [DONE] Stage-7 ANALYSIS A1 — leave-one-out + most-influential-trial already compute in-pipeline and
#         render. NOT done: A2 cluster design-effect correction, A3 specification curve — still queued.
#  [IN PROGRESS] Stage-5 SCREENING — blind independent (model) third-screener wave run; Cohen's kappa via
#         scripts/screen_reproducibility.py -> docs/screen_reproducibility.json (reproducibility, not a
#         human gold standard).
#  [QUEUED] Stage-6 SEARCH independent seed set; Stage-8 EXTRACTION abstract-share reduction; C2 external
#         human review; R1 RoB2-from-methods; A2/A3 above; PROTOCOL PR1/PR2.
# ===================================================================================
Severity order (biggest gaps first). Numbers verified against the committed artefacts this cycle:
99 pooled pairs (99/99 verified), 76/99 from abstracts, 11/99 hand-verified/override, 12 audit defects
fixed, 21/29 primary pools k<=2, 8/29 cross the null, RoB 13-14 to the comparator, reach 9/9, extraction
0/626, declared-absent 646/670 = literature's limit vs 6 = ours. Correction to the human assessment: the
PROTOCOL *file* is hand-authored markdown, not generated from a PICO object; what IS object-generated is the
served ELIGIBILITY statement (`screen.describe_eligibility` from the include object, gated declared==served).

## CROSS-CUTTING (the two biggest gaps — do these first)
- **C1 — We have NEVER measured our own residual error rate.** Evidence: 12 defects were found by the
  cycle-75 source audit on pages that passed every gate limb; we have a found-defect count, not a rate.
  Fix: draw a RANDOM sample of pooled trial-outcome numbers (pre-registered n, fixed seed recorded before
  drawing), re-verify each independently against source, report an error rate WITH a binomial interval.
  Regression risk: none (measurement only). This is the single most important number the project lacks.
- **C2 — No independent human has reviewed a page.** Fix: package 3-5 pages for external review; record
  findings. Risk: none.

## EXTRACTION (highest single-stage priority)
- Strong: source ladder; model-locates/code-parses/round-trip-decides; 99/99 verified; dual extraction; the
  guard set; the flagged-override tier. Weak: **76 of 99 pooled values come from ABSTRACTS** (weakest
  source) and 11/99 are hand-verified/override; residual error unmeasured (see C1).
- **E1** raise the structured/full-text share, lower the abstract share: for each abstract-sourced pooled
  number, try to promote it to a CT.gov structured or PMC full-text source and cross-check. Evidence:
  provenance counts in review.json. Fix: re-run extraction preferring higher rungs where available;
  reproduce all 29, only intended pages move. Risk: MEDIUM (could change numbers — verify each against
  source, treat like the audit fixes).

## RISK OF BIAS (our weakest dimension — blind judge 13-14 TO THE COMPARATOR)
- Weak: mostly registry-derived; most domains not assessed; no overall judgement; no RoB-stratified
  sensitivity. Evidence: fair_judge.json risk_of_bias_reporting.
- **R1** model-assisted RoB2 from the METHODS text, a verbatim span per domain, rendered "model-assessed,
  span-checkable" (partial+labelled beats absent) — same discipline as outcome-identity (model locates,
  never supplies a number). **R2** a RoB-stratified sensitivity analysis (drop high-RoB trials, re-pool).
  Risk: LOW-MEDIUM (rendered disclosure + a sensitivity pool; does not change the primary).

## PAPER (weakest deliverable — we produce pages, not manuscripts; no generator exists)
- **P1** generate a full manuscript per review FROM the object: structured abstract, methods describing what
  actually ran, results with forest plots, limitations in prose, data-availability with the protocol SHA +
  the one command. **Under a NEW gate limb: no number in manuscript prose lacks a matching object field**
  (the `_validate_prose_numbers` pattern, applied to the manuscript). Risk: LOW (additive artefact + a
  gate limb that can only refuse).

## GRADE (absent; rendered as signals only — ME-30)
- **G1** compute the mechanical domains into `docs/grade.json` + a rendered section (object-derived, like
  `_error_coverage_section`): **imprecision** from the 95% CI vs a decision threshold; **inconsistency**
  from tau2/I2; **publication bias from the ghost-protocol/registry census, NOT funnel asymmetry** (better
  than standard at our k). Leave indirectness + RoB as labelled judgement. Render a PARTIAL GRADE stating
  each domain's basis. Risk: LOW (additive, object-derived).

## ANALYSIS
- Verified absent: leave-one-out, meta-regression, specification curve, design-effect/ICC correction (0
  hits each in harness/); tau2 unstable at k<=2 (21/29). Strong: PM+HKSJ validated <1e-6; prediction
  intervals; estimand homogeneity.
- **A1** leave-one-out + influence on every pool (cheap, no new data). **A2** design-effect correction for
  the cluster/crossover trials unit_of_analysis already flags (needs an ICC assumption — state it). **A3**
  the specification curve (fixed-vs-random, HKSJ on/off, estimand variants). Risk: A1 LOW; A2 MEDIUM
  (changes weights — disclose the ICC); A3 LOW (sensitivity panel).

## SEARCH
- Strong: registry-first; citation chasing (reach 9/9); verbatim re-runnable queries; four-state record;
  drift mode. Weak: **recall is measured against the comparator's trial list (partly circular)**; only
  PubMed + Europe PMC + CT.gov (no CENTRAL/Embase); no grey-literature or language statement.
- **S1** build an INDEPENDENT known-item seed set per topic and measure recall against that, not the
  comparator. **S2** state language + date restrictions explicitly on each page. Risk: LOW (measurement +
  disclosure).

## SCREENING
- Strong: dual screeners + adjudicator; rule id + verbatim span per decision; P/I/C/design only; per-topic
  controls. Weak: no measured sensitivity/specificity/kappa against a gold set; the two rule screeners
  share an author; controls are the comparator's includes.
- **SC1** hand-label a gold set (~200 records across topics), report sensitivity, specificity, kappa vs the
  screener. Risk: LOW (measurement).

## PROTOCOL
- Strong: SHA-registered before the run; declared==served eligibility gate; pivotal trials named;
  amendments are commits. Weak: **registration is self-hosted (same agent writes protocol + runs analysis,
  no external timestamp)**; estimand/model/estimator/outcome-set only partly pre-specified.
- **PR1** publish the protocol hash externally (OSF/PROSPERO-style) so registration is not self-certified.
  **PR2** pre-specify estimand + model + estimator + full outcome set explicitly in the protocol file.
  Risk: LOW.
