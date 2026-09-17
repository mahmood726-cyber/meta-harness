# LANE IN4 — LANDING 4 integration: the glp1 architecture (FACT provenance, protocol-declared binding axes, strands, families, envelope/fragility/decomposer, prose objects) integrated onto the LANDED landing-3 tree, every page rebuilt, the FULL standard run and its table pasted. You integrate; you do not decide policy; you never loosen a gate.

Report file: `LANE-IN4-REPORT.md`. Base: __BASE__ (the landing-3 commit on main; record `git rev-parse HEAD`).

## Inputs — read each lane's report first, then take its WORKING TREE (not its diff): the file lists are in the clones' `git status --short --untracked-files=all` (exclude lane.log/lane.pid/lane.winpid/LANE_PROMPT.md/.tmp/patches_*); copy files in this order, resolving every conflict by hand and listing each resolution:
1. `C:\mh-r-CGX` (FACT object, typed claim graph, tightened gate; report `LANE-CGX-REPORT.md`)
2. `C:\mh-r-TY` (twelve-axis effect type; `LANE-TY-REPORT.md`)
3. `C:\mh-r-CGX2` (contains GL's tree + prose objects; `LANE-CGX2-REPORT.md`, `LANE-GL-REPORT.md` in `C:\mh-r-GL`)
4. `C:\mh-r-TY2` (binding axes from the protocol; glp1 protocol amendment 17 Sep; `LANE-TY2-REPORT.md`)
5. `C:\mh-r-TYPG` (glp1 axis evidence; `LANE-TYPG-REPORT.md`) + the integrator's `docs/parity.json` glp1 row from `refs/lanes/landing4-wip-typg` (443d8a64)
6. `C:\mh-r-FN` (trial families; `LANE-FN-REPORT.md`) — COMPACT before copying: `cache/*/family_registry.json` + `families.json` total 169 MB of verbatim AACT rows; replace verbatim rows by `{table, nct_id, row_sha256, snapshot}` references with a regeneration script (`scripts/build_families.py`, offline from the AACT snapshot) and a test that a regenerated registry hashes identically; keep the per-family fields the page renders.
7. `C:\mh-r-GS` (envelope, fragility, decomposer, GRADE arithmetic; `LANE-GS-REPORT.md`) if it has finished (a `tokens used` line at the end of `C:\mh-r-GS\lane.log`); otherwise skip and say so.
8. `C:\mh-r-CGX3A` (overview/outcome-block prose objects; partial) — take its renderer changes; measure, do not chase.
9. TYP1/TYP2/TYP3 (`C:\mh-r-TYP1..3`): take ONLY the provenance additions (document digests + located spans → FACT) for their pages; do NOT take any change that alters membership; their typing evidence is fine to take (it renders UNKNOWN where the protocol declares nothing binding, per TY2).

## Defects to fix at the source while integrating
- `harness/glp1.py` (lane GL) is a page-named module and its `strands()` RAISES `ValueError('FREEDOM source refused')` when a source row is refused. A refusal must RENDER (typed, with the axis/reason), never crash a build. Replace the module with general strand machinery (`harness/strands.py`: strands declared in `topics/<slug>.json`/protocol, membership per strand from the typed-effect verdicts) and delete the slug-specific filter in `harness/pipeline.py` (marked INTEGRATOR NOTE). Plant: a synthetic two-strand topic with one refused source renders the refusal and pools the rest.
- The FACT gate (CGX) and the binding-axis gate (TY/TY2) must both be live on every page; where legacy rows lack digests they render `UNVERIFIED_FACT` (value shown with the mark) and, for protocols that declare no binding axes, still pool — that is TY2's contract; do not change it.

## Expected glp1 result (MEASURED by TYPG; reproduce it, do not target it)
CONVENTIONAL_GLP1RA k=7 (LEADER, SUSTAIN-6, EXSCEL, REWIND, PIONEER 6, SOUL, ELIXA) HR 0.8884 (0.8284–0.9527) τ² 0.0012 PI 0.796–0.992; GLP1RA_ANY_DELIVERY k=8 (+FREEDOM-CVO) HR 0.8984 (0.8158–0.9894). FLOW, AMPLITUDE-O, Harmony rendered REFUSED with the axis named; the FREEDOM-CVO end-of-treatment 1.36 row rendered as sensitivity, never pooled; the envelope (GS) carries the all-candidate k=10/11 specification (0.8613 / 0.8673) as "censoring unverified", NOT_COMPUTABLE rows for anything without a held value. If your rebuilt page differs from these, report the difference and its cause; do not force agreement.

## Then
Rebuild all 32 topics (`python scripts/build_topic.py <slug> --now 2026-09-11`); renderers in order (`render_fix_ledger.py`, `rewrite_fixstate_lines.py`, `build_evidence_index.py`, `render_gate_gaps.py`, `render_gate_scorecard.py`, `external_agreement.py`, `python -m harness.index docs`); `python scripts/retraction_survival.py __BASE__` (must print 32 of 32 — it is on the base); `python scripts/verify_all.py` — paste the full table. The ratchet limb will refuse (integrator signs); paste its output. Every other limb is expected PASS; for any page the gate refuses, paste the violation verbatim and stop there — never weaken the gate. Report: per page `FACT n of N rows`, `n pages passing the gate of 32`, glp1 strands MEASURED, `claim_scope_sweep` glp1 `n registered of N`.

No commit. No network. Never a backslash escape through a heredoc; write regexes to files. MEASURED/INFERRED/CLAIMED; `n of N` with N named.
