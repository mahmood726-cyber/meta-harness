# LANE RO — a refusal creates a RECOVERY OBLIGATION, not a terminal state. TECOS's strict 3-point HR sits in the primary full text one retrieval step away; EXAMINE needs a declared CI-conversion policy. Make the obligation an object with a status, corpus-wide.

Report file: `LANE-RO-REPORT.md`. Base `ad5e7c66`. Read `harness/absence.py` (RR typed codes), `harness/claimgraph.py` (CG), `docs/known_eligible_missing.json`, the dpp4 page objects. Keep logic in `harness/recovery.py`.

## Findings (topic 12 `dpp4-mace-t2d`; CLAIMED until re-measured)
- TECOS: the abstract's 4-point MACE HR was correctly refused (different composite from the review's strict 3-point); its strict 3-point HR 0.99 (0.89–1.10) is in the primary full text. Today the refusal is terminal and the page's known-missing panel cannot estimate.
- EXAMINE: reports a one-sided upper bound (HR 0.96; upper boundary of one-sided repeated CI 1.16). Entering it requires a declared conversion policy (one-sided 97.5% bound → two-sided 95% equivalent; render `derived` with the formula and the assumption). Without the policy the row is `REFUSED_NO_CONVERSION_POLICY`; with it, `derived`.
- Both are the same class as ODYSSEY LONG TERM post-hoc MACE (VS lane), COCS/COPPS extraction debt (CK2/RX), and every `in source not held` state.

## Build
1. `harness/recovery.py`: every refusal / typed absence on a pooled-eligible trial spawns `recovery_obligation = {trial, outcome, kind ∈ {FULL_TEXT_RETRIEVAL, REGISTRY_RESULTS, CONVERSION_POLICY, ADJUDICATION}, status ∈ {OPEN, IN_PROGRESS, DISCHARGED(effect, span), REFUSED(reason)}, owed_since}`. Status is derived: `DISCHARGED` only when a held span supplies the value under the declared policy. A page with OPEN obligations on trials that could move the pool renders them next to the known-missing panel ("recoverable, not recovered: n").
2. Conversion policy object in the protocol compiler: `ci_conversion = {one_sided_bound → two_sided: <method>}`; absent → `CONVERSION_POLICY_UNDECLARED` fires where a one-sided bound is the only held effect (EXAMINE).
3. Plants (pre-fix `ad5e7c66`): `tests/test_recovery.py` — TECOS refusal terminal pre-fix (no obligation field; quote the refusal text) → `OPEN(FULL_TEXT_RETRIEVAL)` post-fix; EXAMINE → `CONVERSION_POLICY_UNDECLARED` pre-fix, `derived` post-fix ONLY if the one-sided bound is in a held span (else stays OPEN with the reason); synthetic: a held span discharges an obligation; a discharged obligation whose span is later removed → reopens (test by mutating a copy).
4. Sweep `scripts/recovery_sweep.py` → `docs/recovery_sweep.json`: over 32 pages, `n obligations OPEN of N obligations`, by kind; `n pages with ≥1 OPEN obligation on a trial that could move the primary pool of 32`, named.
5. Rebuild dpp4 and any other affected page; replay; list reworded blocks.

Do not pool TECOS or EXAMINE (their values are not in held text); do not fetch. Do not touch `harness/synth.py`, screening, search. No network.
