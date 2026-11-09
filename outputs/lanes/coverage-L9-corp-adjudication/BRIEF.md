# Lane L9 — a recorded A7 adjudication: pool the counts, show the discrepancy (plants FIRST)

## Context
A7 (`harness/extract.reported_vs_count_derived`) types a source whose reported effect and own-count effect disagree beyond
rounding as SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE; the rounding class is TERMINAL in `harness/pipeline._build_outcome`
(abstract route and full-text route: `absent.append({... **{k: ex[k] for k in _A7_FIELDS}}); continue`).
Mahmood DECIDED (15 Oct) for CORP, colchicine-recurrent-pericarditis, outcome "Recurrent pericarditis", PMID 24694983 --
reported "relative risk 0.49; 95% CI 0.24-0.65" v its own counts 26/120 v 51/120 (= 0.5098): **option (B): pool its counts,
with the discrepancy shown.** Implement that as a recorded, value-bound adjudication -- never a code special case.

## Build
1. `registry/a7_adjudications.json`:
   `{"rule": "...", "adjudications": {"<slug>::<outcome name>::PMID <id>": {"decision": "POOL_COUNTS", "decided_by":
   "Mahmood Ahmad (decision relayed to the coverage lane in chat, 15 Oct 2026)", "date": "2026-10-15",
   "reported": {"scale": "RR", "effect": 0.49, "ci_low": 0.24, "ci_high": 0.65},
   "count_derived": {"ai": 26, "n1i": 120, "ci": 51, "n2i": 120}, "basis": "option (B) of the A7-S1 signing item: the
   counts are the source's own data; the printed 0.49 differs from them by 0.020 (beyond its rounding); pooled with the
   discrepancy shown"}}}` -- the CORP entry exactly as above.
2. `harness/a7_adjudication.py` (harness modules may not import reproducible_ai): `load(path=None)`, and
   `resolve(slug, outcome_name, trial_id, typed)` returning one of:
   - None (no adjudication -> the typed refusal stands, exactly as now);
   - {"state": "ADJUDICATED_POOL_COUNTS", "row": {...}} when the entry's decision is POOL_COUNTS AND its stored
     reported (scale, effect, ci) and count_derived (ai, n1i, ci, n2i) EQUAL what the extractor produced now;
   - {"state": "A7_ADJUDICATION_STALE", ...} when an entry exists but the values differ (the refusal stands; say so);
   - an unknown decision value raises ValueError (fail closed).
   The admitted row carries `ai, n1i, ci, n2i` from the counts, `source` = the count span, `provenance` = the route
   ("abstract" / "pmc_fulltext"), and `reported_vs_count_derived` = {reported, count_derived, decision, decided_by, date}.
3. `harness/pipeline._build_outcome`: at BOTH terminal A7 branches, consult `resolve(...)` (find how the slug is
   available there; pass it in if it is not -- minimal plumbing). POOL_COUNTS -> append the row to `trials` (going
   through the same downstream admissibility the abstract route's rows go through: build it the way the abstract route
   builds `t`), STALE -> keep the refusal and add `a7_adjudication: "STALE"` to it. No adjudication -> unchanged.
4. `harness/page.py`: a pooled trial carrying `reported_vs_count_derived` renders a VISIBLE line in its source cell, e.g.
   "A7: the source reports RR 0.49 (0.24–0.65); its own counts 26/120 v 51/120 give 0.510 — counts pooled by adjudication
   (decided by Mahmood Ahmad, 2026-10-15)". Escape everything.

## Tests (`tests/test_a7_adjudication.py`, synthetic, no cache/ reads) — each FAILS before the change
- POOL_COUNTS with matching values -> resolve returns the admitted row with the counts and the discrepancy record;
- values differ (e.g. counts 27/120) -> A7_ADJUDICATION_STALE; no adjudication -> None;
- unknown decision -> ValueError;
- the registry file holds exactly the CORP entry above and every entry has decision/decided_by/date/reported/count_derived;
- page: the rendered source cell of a row with `reported_vs_count_derived` contains "0.49", "0.510" (or 0.5098 formatted),
  "26/120", "adjudication";
- pipeline: a minimal synthetic `_build_outcome` call (or the smallest real seam) shows an adjudicated trial lands in
  trials and an unadjudicated one stays absent -- if `_build_outcome` is too heavy to call synthetically, test the seam
  function you introduce and SAY SO in the report.
Run `python -m pytest -q -p no:cacheprovider tests/test_a7_adjudication.py tests/test_reported_vs_derived.py
tests/test_a7_oracle.py`. Touch only the files named. No network.

## Finish condition / artefact
`LANE_REPORT.md` (plants and their failing output, the change, passing output, what you could not run) and `lane.patch`
(new files via git diff --no-index if needed). Do not commit or push.
