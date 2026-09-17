# LANE ACQ-<N> — full-text acquisition for named known-eligible-but-unresolved trials; commit the source, extract the target estimand, never weaken a gate

Report file: `LANE-ACQ-<N>-REPORT.md`. Base commit: <BASE>. Network IS allowed in this lane, only via the existing adapters (`harness/fulltext.py`, `harness/fetch.py`, Europe PMC / PMC OA), and every fetched body is saved under `cache/<slug>/fulltext/<pmid>.xml|.json` with its sha256 recorded in `cache/<slug>/fulltext/INDEX.json` (create if absent; follow whatever convention `harness/fulltext.py` already uses — read it first).

## Trials (each: slug · trial · what the served page says today · what is needed)
<TRIAL_LIST>
e.g.
- `dpp4-mace-t2d` · EXAMINE (PMID 23992602) · declared absent: abstract reports a one-sided upper CI bound (HR 0.96, ≤1.16) · need: full text for the two-sided HR and CI on 3-point MACE, or the per-arm counts. Note the served page ALSO lists TECOS (26052984) as declared absent for 4-point MACE and as `known_eligible_missing` for its 3-point MACE reported in the primary publication — the full text should settle which secondary endpoint is 3-point MACE and whether it is pre-specified.
- `glp1-ra-mace-t2d` · FLOW (semaglutide, CKD+T2D) and FREEDOM-CVO (ITCA 650) · `known_eligible_missing` · need: 3-point MACE HR+CI on the target estimand; check FLOW's population against the protocol's population terms (CKD+T2D vs T2D at CV risk) — if the protocol excludes CKD populations, record POPULATION_MISMATCH rather than pooling.
- `omega3-cardiovascular-events` · OMEMI (primary publication not linked) and OMEGA-REMODEL (pending an exposure-duration rule) · need: link the primary publication PMID for OMEMI; state the exposure-duration rule that exists or does not, do not invent one.
- `colchicine-postop-af` · Bessissow (29237033) · declared absent (population: lung resection — the page's later text says EXCLUDED as non-cardiac) · need: confirm from full text whether the population is thoracic non-cardiac surgery; if so it stays excluded on population (X2) and the declared-absent row becomes an exclusion, not an absence.
- `corticosteroids-covid19-mortality` (7 declared-absent) and `tocilizumab-covid19-mortality` (8) · 28-day all-cause mortality per arm is in the full texts (RECOVERY-era trials) · need: per-arm 28-day deaths and denominators with verbatim spans.
- `melatonin-primary-insomnia-sol` (8 declared-absent) · sleep-onset latency mean/SD per arm at end of treatment · population must be adult primary insomnia; timepoint must match; formulation noted.

## Per trial
1. Fetch via the adapter; save; record sha256, URL, retrieval UTC, HTTP status. If not open access: record `FULL_TEXT_NOT_AVAILABLE_OA` and stop for that trial (no paywall workarounds).
2. Extract ONLY the target estimand for the outcome the page declares (effect+CI on the declared scale, or per-arm counts / mean-SD-n), with the verbatim span (≤300 chars) and the table/figure reference. Do not extract other outcomes.
3. Run the page's existing screen + estimand + design gates on the row (`harness/screen.py`, `harness/estmeasure.py`, `harness/design_key.py`): if a gate refuses (estimand class, population, timepoint, design), the row lands declared-absent with THAT typed reason — never edit a gate. If it passes, write an adjudication record `outputs/search_v2/verification/<slug>/LANE-ACQ-<N>-adjudication.json` (trial_key, decision ELIGIBLE, rule ids for P/I/C/design, span) so `check_new_inclusion_adjudicated` (built by lane 2B-1) admits it.
4. Rebuild the page (`build_topic.py <slug> --now 2026-09-16`); `reproduce_review.py <slug>`; before/after k, estimate, CI, τ².

## Plant
`tests/test_acq_source_committed.py`: a pooled row whose `provenance` is `fulltext_verified` must have a matching entry in `cache/<slug>/fulltext/INDEX.json` with a sha256 that hashes the committed file; a synthetic row without it → gate fires. Show it fires on a fixture, then passes on your rows.

Report per trial: fetched (Y/N, status), extracted value + span, gate verdicts, pooled or declared-absent with typed reason, page before/after. `n pooled of N attempted`, N = the trial list above.
