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
