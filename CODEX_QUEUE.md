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

## Invariants a task must never break
- The two-limb gate and `reproduce_review.py` must stay green; the pre-commit hook regenerates the index and
  requires a byte-match, so any hand-typed prose number that is not object-derived or whitelisted will fail
  `_validate_prose_numbers` (that is intended — derive it or whitelist it with a reason).
- 33/33 error-library coverage; every pooled number verified against its committed source.
- Never edit the gate to pass; never `--no-verify`; never work in `C:/rmfw`.
