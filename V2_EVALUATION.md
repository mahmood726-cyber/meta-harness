# Evaluation of the existing rct-extractor-v2 as a candidate extractor (2026-09-12)

`C:\Projects\rct-extractor-v2` (RCT Extractor v5.0) — `rct_extractor.api.extract(text)` returns reported
effects (HR/OR/RR/MD/SMD/IRR + CI + source_text), team-of-rivals consensus, proof-carrying numbers,
internal-consistency screening, and an arm-level extractor per detected specialty. Evaluated the same way
as everything else: the known defect set, and as a THIRD extractor over the committed pooled numbers.
Read-only; V2 never supplied a number here — this only measures whether to adopt it. Harness `eval` script
at `scratchpad/v2_eval.py`.

## (A) Defect set — 6 of 10 PASS

| Case | V2 | Note |
|---|---|---|
| EMPEROR HR from composite sentence | PASS (HR 0.79) | |
| DAPA-HF HR | PASS (HR 0.74) | |
| RECOVERY rate ratio | PASS (IRR 0.83) | |
| SU.FOL.OM3 factorial (omega-3 HR, not B-vitamin) | **PASS (HR 1.08)** | correctly did NOT bind the 0.90 B-vitamin arm |
| RR-labelled-as-RR (not OR) | PASS (RR 0.68) | |
| appendicitis wrong-outcome NEGATIVE | PASS (no effect) | correctly rejects |
| Hernández HFNC arm counts (13/264 vs 32/263) | **FAIL** (nothing) | no generic counts→2×2/RR path |
| LoDoCo2 arm counts (187/2762 vs 264/2760) | **FAIL** (nothing) | same |
| semicolon `(6.2%; 95% CI …)` | **FAIL** (nothing) | |
| CANTOS multi-arm dose HRs | **FAIL** (nothing) | |

V2 is strong on **reported prose effect+CI**, including the hard factorial-disambiguation and RR-vs-OR
labelling cases, and correctly rejects the negative. It fails exactly where the harness is strong:
arm-count → 2×2, the `(P%; CI)` pattern, and multi-arm dose surfacing.

## (B) Third extractor vs the committed pooled numbers (V2 fed the FULL ABSTRACT), by kind

- **reported-effect numbers (n=48): AGREE 42 · DISAGREE 3 · NO_EXTRACTION 3** — 87.5% agreement; a
  genuine independent corroboration of the harness's effect extractions.
- **count-derived numbers (n=44): AGREE 20 · DISAGREE 15 · NO_EXTRACTION 9** — V2 has no generic
  counts→RR path; where it "disagrees" it grabbed a *reported* effect of a **different estimand** than the
  harness's count-derived RR, or a different unscoped outcome.
- **continuous (n=1): 0 agree** — V2 returned "OR 8" on the melatonin sleep-latency abstract, a **false
  positive** (there is no odds ratio in it).

**Every disagreement was investigated; none revealed a harness error.** The two opposite-direction cases:
corticosteroids-cap 25688779 — harness pooled the *hyperglycaemia harm* (11/61 vs 7/59, RR 1.52, verified);
V2 grabbed the mortality effect. omega3 20929341 (Alpha Omega) — harness pooled the primary MACE HR 1.01
(verbatim "hazard ratio with EPA-DHA, 1.01"); V2 grabbed a different subgroup HR. The root cause of the
disagreements is that **V2 has no outcome-identity gate** — it extracts *some* effect from an abstract, not
necessarily the outcome/arm/dose the review targets.

## Verdict — measured, NOT adopted

V2 is a capable reported-effect extractor but is **not stronger than the current harness path**, and its
strength is already covered while its weaknesses are the harness's core:
1. **No outcome-identity scoping** — it returns whatever effect it finds, so as a blind third extractor it
   produces wrong-outcome/wrong-arm numbers (the corticosteroids/omega3/RE-LY disagreements) and would need
   the harness's own outcome-identity + subgroup + multi-arm gates in front of it to be trusted.
2. **No counts→2×2 path in the generic route** — 44 of our 93 numbers are count-derived, and V2 extracts
   nothing usable there (Hernández/LoDoCo2 FAIL, 24/44 miss or mis-extract).
3. **False positives on out-of-domain abstracts** — the melatonin "OR 8" is exactly the wrong-number risk
   the bar forbids.
The corroboration it does provide (42/48 reported-effect agreement) is already supplied by the harness's
existing dual-extraction + CT.gov cross-source layers, so adopting V2 adds integration cost and
false-positive noise for marginal, overlapping value. **An existing component is a candidate, not a
mandate.** Not adopted; the measurement is recorded here.

The one idea worth keeping from V2 for later, if a specific gap ever appears: its factorial-disambiguation
and RR-vs-OR labelling were clean on the defect set — a narrowly-scoped, outcome-gated corroborator on
*reported-effect* sentences only (never counts, never continuous) could be revisited, but only behind the
harness's outcome-identity gate and never as a number source.

## Addendum — V2 at scale over every declared-absent cell (2026-09-12)

Ran V2 over all declared-absent cells across the 27 live topics (its exact niche: "an effect is reported
but the harness found no usable 2×2"), under a strict outcome-identity gate (a V2 effect counts only if
V2's own endpoint/source_text names the declared outcome). Result: **1 of 626 cells** flagged as plausibly
fillable, **625 correctly absent** — and the 1 (probiotics 26973849, S. boulardii AAD HR 1.02) is an
**HR-vs-RR estimand mismatch** with our count-based pool. So V2 recovers **zero** clean numbers our
extractor missed. Two conclusions: (1) the harness's declared-absent decisions are **independently
validated** — an unrelated extractor cannot recover them under outcome-identity; (2) V2's lack of an
outcome-identity gate makes it unusable as a recovery rung here, confirming the do-not-adopt verdict. The
value it does have (prose effect+CI on the RIGHT outcome) is already covered by the harness + dual-extraction.
