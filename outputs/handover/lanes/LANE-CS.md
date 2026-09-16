# LANE CS — the five-state completeness model: `eligible_declared_absent` is materially overstated because one code covers five different truths. Re-derive it corpus-wide; the STALE reasons must distinguish search-incomplete from clinically-incomplete.

Report file: `LANE-CS-REPORT.md`. Base `ad5e7c66`. Read `harness/invalidation.py`, `harness/absence.py` (RR typed codes), `docs/known_eligible_missing.json`, `docs/never_considered.json`, and lane SC's / SE's briefs if present in the clone root (they reference a four-state model; you supersede it with five and say so). Keep logic in `harness/completeness.py`; wire into invalidation additively.

## The five states (every eligible-but-unpooled trial gets exactly one)
1. `COMPLETED_OUTCOME_HELD_NOT_EXTRACTED` — the number is in a held source (extraction debt; lane EX/RX territory — you classify, you do not extract).
2. `COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD` — the trial reports the target outcome in a publication/registry entry we do not hold (acquisition debt, Phase 2B).
3. `COMPLETED_OUTCOME_ABSENT_BY_DESIGN` — surrogate/mechanistic/functional primary; the target outcome was never measured or is inappropriate (short duration, wrong endpoint class). NOT a threat to the pooled estimate.
4. `ONGOING_OR_NOT_YET_RECRUITING` — registry status recruiting / not yet recruiting / active-not-recruiting; carry `phase`, `primary_completion` (e.g. NCT06229678 Early Phase 1, n=71, completion 2027; FineCaRe Dec 2026; QUARTET-DKD ~Feb 2029; EMPA-CKD not yet recruiting).
5. `TERMINATED_OR_WITHDRAWN_NO_RESULTS` — with the registry reason.
Plus, orthogonal: `REACH_MISS(named)` for trials named by an audit that are not in the corpus at all (Sarzaeem 2014; CONFIDENCE 2025 unless cached; Botticelli-DVT; ODIXa-DVT; J-ROCKET AF; ARISTOTLE-J; PETRO; Nestler 1998; Zarpelon is IN corpus — do not list it here).

## Named cases (CLAIMED until re-measured from cached records)
- finerenone-ckd-t2d-renal: ARTS-DN (823, 90 d, UACR) → state 3; ARTS-DN Japan (96, 90 d, UACR) → 3; FineCaRe (recruiting, Dec 2026) → 4; QUARTET-DKD (not yet recruiting, ~2029) → 4. Today all four are one code `eligible_declared_absent` and the page reads as if four completed trials with missing hard outcomes threaten 0.84.
- sglt2-hfref-hosp-cvdeath: NCT06229678 → 4 (Early Phase 1, mechanistic); DEFINE-HF / Empire HF / EMPERIAL-Reduced (if cached) → 3.
- spironolactone: PMID 8888663, 20299607 (if cached) → 3.
- sglt2-ckd-progression: EMPA-CKD → 4.
- dpp4-mace-t2d: TECOS strict 3-point in primary full text → 2; EXAMINE → 2 (RO lane recovers; you classify).
- colchicine-postop-af: COCS, COPPS → 1; Sarzaeem → REACH_MISS.

## Build
1. `harness/completeness.py`: classifier from the screening ledger row + cached registry record (status, phase, primary completion, primary outcome text) + cached publication (outcome present? design?) → state with `basis` (the field/sentence that decided it). Unknown → `NOT_CLASSIFIABLE(missing: <fields>)`, never a guess.
2. The STALE panel renders the state distribution per page and the sentence: "search-incomplete: yes/no; clinically incomplete for this outcome: yes/no (states 1–2 count; 3–5 do not)". Both are computed, neither typed.
3. Plants (pre-fix `ad5e7c66`): `tests/test_completeness.py` — finerenone four entries all `eligible_declared_absent` pre-fix (quote), four distinct states post-fix; NCT06229678 state 4 with phase/completion; COCS state 1; synthetic per state; `NOT_CLASSIFIABLE` when the registry record lacks status.
4. Sweep `scripts/completeness_sweep.py` → `docs/completeness_sweep.json`: over 32 pages, `n eligible-unpooled entries of N` by state; `n pages clinically incomplete for their outcome of 32` vs `n search-incomplete of 32` (expect 32); pages whose `eligible_declared_absent` count drops to zero clinically-relevant entries, named.
5. Rebuild affected pages; replay; list reworded blocks — the old `eligible_declared_absent` sentences will change on ~27 pages; list every one (page, heading, old, new).

Do not touch: pooling, screening decisions (you classify what screening produced), search. No network.

## Added 2026-09-16 13:58 (topics 17, 18)
- balanced-crystalloids: CRUSADERS (NCT07189091) recruiting to 2028 → state 4 (and SC3 refuses its contrast); FISSH (NCT03677102) completed, ~1,118 pts, 30-day mortality primary, no results publication → new orthogonal flag `COMPLETED_UNPUBLISHED(registry)` — publication-bias surveillance input, and the cleanest case for registry-first discovery (Phase 2B). Design-refused SMART/SALT/SPLIT are NOT completeness states (they are consumed-or-refused evidence, lane CX) — keep them out of `eligible_declared_absent`.
- semaglutide-obesity-weight: STEP 5 → timepoint refusal (not a completeness state); STEP 11 likewise; STEP 6 parent trial vs post-hoc report → the trial is the object (PU identity).
