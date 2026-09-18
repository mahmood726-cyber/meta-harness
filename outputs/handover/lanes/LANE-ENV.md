# LANE ENV — the glp1 robustness envelope across the DEFENSIBLE specifications, every specification a computed object over held member rows; report the range, and how many specifications preserve direction and exclude 1.

Report file: `LANE-ENV-REPORT.md`. This clone is the landing-4 integration tree (HEAD main 3f8add72 + ~700 changed paths from lanes IN7/FPA/FB — never reset/checkout/stash; record `git rev-parse HEAD` and `git status --short | wc -l`). No commit. No network.

Read first: `harness/envelope.py`, `harness/fragility.py`, `harness/decomposer.py` (lane GS: the existing envelope over specifications, `NOT_COMPUTABLE` where an input is not held), `cache/glp1-ra-mace-t2d/envelope.json`, `harness/strands.py` (CONVENTIONAL k=7 / ANY_DELIVERY k=8 members and refusals), `harness/synth.py` (the pool: PM τ² + HKSJ t(k-1) + floor; the REML/DL/Wald alternatives must be called on the same engine, never re-implemented), `harness/effect_type.py` (typed axes; ELIXA's strict 3-point row vs its 4-point primary; FREEDOM-CVO end-of-study vs end-of-treatment rows), `cache/glp1-ra-mace-t2d/verified_effects.json`, `rob2.json` (machine signals only; RoB is NOT ASSESSED — a low-RoB-only specification is therefore NOT_COMPUTABLE and must say so, not be faked from machine signals), `outputs/handover/glp1_regulatory/regulatory_sources_glp1.json` (held FDA rows incl. FLOW's label row, ADJ-GLP1-003 PROPOSED — FLOW stays refused until adjudicated; a specification "+FLOW (if ADJ-003 accepted)" may be computed and labelled PROPOSED-CONDITIONAL, never as accepted).

## Specifications (each an object with id, description, member set by trial id, estimator, result or NOT_COMPUTABLE with the reason)
1. published-HR-only (rows whose selected estimator is a published HR; reconstructed rows excluded)
2. ± FREEDOM-CVO (CONVENTIONAL vs ANY_DELIVERY)
3. ELIXA strict 3-point (held FDA row) vs ELIXA excluded (never the 4-point 1.02 relabelled — assert in a test that no specification carries the 4-point row)
4. PM vs REML τ² (same HKSJ CI)
5. HKSJ vs Wald CI (same τ²)
6. CV death strict vs CV/undetermined death (only where a held row states which; otherwise NOT_COMPUTABLE naming the trials lacking the span)
7. all-eligible vs low-RoB-only (NOT_COMPUTABLE: RoB 2 not assessed — render the reason)
8. the full factorial of 2×3×4×5 where computable, so the envelope is the set, not a list of eight
Report: min/max HR, min/max CI bounds, n specifications computed of N defined, n preserving direction (HR < 1) of computed, n whose 95% CI excludes 1 of computed, and the NOT_COMPUTABLE list with reasons. Render into the existing envelope block (extend `envelope.py`; every number a computed field with `input_set_version`; prose registered as claim objects so the claim-scope sweep stays `n of n`). Rebuild glp1, replay (`AACT_DIR=.tmp/empty_aact`), run the gate on glp1, `python scripts/claim_scope_sweep.py`, the envelope/fragility/decomposer tests + a new `tests/test_envelope_specifications.py` (plant: a specification that silently drops a member must be refused; the 4-point ELIXA row must never enter).

MEASURED / INFERRED / CLAIMED; `n of N` with N named. Never a backslash escape through a heredoc; write regexes to files. No commit.
