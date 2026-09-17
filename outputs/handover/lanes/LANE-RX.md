# LANE RX — two corpus-wide instruments, no extraction changes: (1) every reason code (`not extracted`, `estimand mismatch`, `declared absent`, every typed absence) verified against the cached source; (2) for every included trial, which registered outcomes were never extracted although a held source reports them.

Report file: `LANE-RX-REPORT.md`. Base `ad5e7c66`. Lane EX (running concurrently) FIXES extraction; you MEASURE. Do not change extractor output, pools, or reason codes on pages — build the instruments, the plants, the sweeps, and a per-page render block "reason-code audit" that shows the verdict beside each code. Keep logic in `harness/reason_audit.py` and `harness/unextracted.py`.

## What to verify (RR lane's typed codes in `harness/absence.py`; every declared-absent / refusal row on 32 pages)
For each reason code attached to a (trial, outcome): locate in the held sources (abstract, full text if held, CT.gov results, registry record) whether the outcome value IS present. Verdicts: `REASON_TRUE` (value absent from every held source, code consistent), `REASON_FALSE_VALUE_HELD(source_id, span)` (the number is in a source we hold — extraction debt, the code is a lie), `REASON_WRONG_KIND` (value absent but the code names the wrong cause, e.g. `estimand mismatch` where the outcome is simply not reported), `NOT_VERIFIABLE(no held source)`.
Named pre-fix cases (topics 1–16; CLAIMED until you locate them): COPS 24/396 vs 38/399 "no poolable value"; Akrami MACE 8/120 vs 28/129 unextracted while its GI counts are used; esketamine 34696742 false reason; Moll 18/111 vs 6/114; COCS "not extracted — the outcome's number IS in the source"; DPP4 TECOS strict 3-point in full text (not held → `NOT_VERIFIABLE` or `in source not held`); pcsk9 ODYSSEY LONG TERM post-hoc MACE (if the VS lane's record is not in your clone, skip and say so).

## Unextracted-outcome sweep
For every included trial × every registered outcome of its page (primary, harms strands, secondaries the protocol registers): `EXTRACTED`, `HELD_NOT_EXTRACTED(source_id, span)`, `NOT_IN_HELD_SOURCES`, `ABSENT_BY_DESIGN`. Named: 1996 RALES dose-ranging hyperkalemia dose-response (if cached); EMPHASIS K+ >5.5 158/1336 vs 96/1340; FIDELIO/FIGARO hyperkalemia; DAPA-HF volume depletion / DKA; FOURIER/ODYSSEY injection-site reactions and AE discontinuation; COCS diarrhoea; COPPS-2 adverse events. All CLAIMED; report only what you locate.

## Plants (pre-fix `ad5e7c66`)
`tests/test_reason_audit.py`: COCS row's code is `REASON_FALSE_VALUE_HELD` with the span quoted; a synthetic row whose value is genuinely absent → `REASON_TRUE`; a synthetic `estimand mismatch` on an unreported outcome → `REASON_WRONG_KIND`; `tests/test_unextracted.py`: Akrami MACE `HELD_NOT_EXTRACTED` with span; synthetic controls per verdict.

## Sweeps
`scripts/reason_audit_sweep.py` → `docs/reason_audit_sweep.json`: `n reason codes FALSE (value held) of N reason codes on 32 pages`, by code kind and page; `n NOT_VERIFIABLE of N`. `scripts/unextracted_sweep.py` → `docs/unextracted_sweep.json`: `n (trial, outcome) pairs HELD_NOT_EXTRACTED of N pairs`, by outcome kind (primary / harm / secondary) and page.

Render the audit block on every page (additive); rebuild; replay; list reworded blocks. Do not touch extraction, pooling, membership, screening, search. No network.

## Added 2026-09-16 13:58 (topics 17, 18)
- balanced-crystalloids PRISMA "6 eligible but outcome not extracted": three of the six had mortality numbers FOUND and were design-refused → `retrieved_refused` not `not_retrieved` — a `REASON_WRONG_KIND` case for your audit; BaSICS renal outcomes refused on a factorial guard while the source table is headed balanced vs saline → `REASON_FALSE_VALUE_HELD` if the table is in held text.
- semaglutide-obesity-weight: GI events STEP 1 969/1306 vs 314/655 (discontinuation 59/1306 vs 5/655), STEP 3 337/407 vs 129/204 (14/407 vs 0/204) → classify HELD_NOT_EXTRACTED vs IN_SOURCE_NOT_HELD per span; STEP 3 Novo Nordisk funding sentence likewise (FU lane extracts; you audit the "unknown" code).
