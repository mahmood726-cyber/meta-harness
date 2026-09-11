# Working plan — front-four first, Codex lane contract, target metric

Written 2026-09-11 mid-run. This is the contract the run works to. It exists because
wave-5 leaked: four lanes explored real records and **committed nothing** — Codex burned
for zero checkable output, twice. Never again by contract, not by memory.

## Engine roles (never the reverse)
- **Codex (GPT-5, ~87%, 3 days):** everything mechanical and parallel — fetch, screen,
  extract, render, regression re-runs, topic-config authoring, comparator trial-list
  extraction, PUB-UNEXT classification. Cheap; relaunch rather than debug.
- **Me (Claude Code, expires 3pm 2026-09-12):** verify extractions against source, decide
  what a defect means, fix the harness, gate, publish, adjudicate lane output. The
  expensive thing is verification; that is the thing worth my budget. Never idle while a
  lane runs — always verifying/measuring/fixing in parallel.

## Codex lane contract (a lane is DONE only if it satisfies all of this)
1. **Named artefact at a named path, in the working tree.** For a topic lane:
   `topics/<slug>.json`, `protocols/<slug>.md`, `cache/<slug>/records.json`, and
   `VERIFY-<slug>.md` (every pooled number + the VERBATIM source sentence it came from).
   For a classification lane: `<out>.md` with per-trial verdicts + source quotes.
   A lane that "explored records" and produced no artefact is a **FAILED lane**.
2. **Verify by MODEL TOKENS consumed + ARTEFACT present — never the exit code.** Codex
   sandbox blocks `.git`, so lanes never commit; the integrator (me) commits on main.
3. **`< /dev/null` is mandatory.** A backgrounded `codex exec` without it hangs reading
   stdin at zero tokens while looking alive.
4. **Liveness = (tokens climbing) AND (artefact appearing) on a timer.** A lane showing
   neither gets **killed and relaunched** — relaunch is free, a silent lane costs a wave.
5. **Integration:** I copy artefacts to main, commit protocol (=registration SHA), run
   `build_topic` on main (offline replay from committed cache = deterministic), **verify
   every extraction against source by hand**, gate, publish, live-fetch. A lane's VERIFY
   is a lead, not a licence — the number ships only after I confirm it TRUE.

## Wave sizing / refill
- Keep every lane full; refill on landing. Size the wave so I can verify what lands rather
  than accumulate an unverified backlog. **Throughput = pages that survive a blind judge**,
  not lanes started. Each lane owns its own clone (`C:\mh-lane<N>`) at the current main SHA.

## NOT worth spending on
Re-running a passing check to look busy; speculative rewrites of working machinery;
hand-debugging a lane when relaunch is cheaper; building anything a live topic does not need
(spec-curve / living-updates / leave-one-out are DEFERRED until the front four are strong).

## Front four, in order, each with a measurement
1. **SEARCH → k** (the number that decides "equal on data"). Per topic: **our k vs the
   comparator's k**, and every shortfall named by cause —
   `not-found` / `found-but-screened-out` / `found-published-but-unextractable` /
   `registry-only-no-results`. Finish Europe PMC / CT.gov / AACT reach; add registry-only
   and regulatory (EMA EPAR, FDA) sources — the one "better-than-published" lever kept
   near-term, because posted/registry/regulatory results attack publication bias directly
   (bempedoic k=1 was false: evidence sat in a supplement + EMA pool). Re-fetch every
   existing topic to bank the gains.
2. **SCREENING** — precision AND recall. Positive control recovers the comparator's trials;
   negative control rejects an off-topic trial. Eligibility on **P/I/C/design only**, never
   on whether the outcome is reported. Keyword brittleness fixed as a CLASS (done: the
   discriminating-word anchor; FIGARO guard) — keep hardening.
3. **EXTRACTION → data + outcomes** — arm counts where they exist; a published effect+CI is
   a poolable input and must never be silently dropped; **match the comparator's whole
   outcome SET, not just its primary**; carry harms. Every number verified TRUE vs source
   before publish.
4. **PROTOCOL** — registered before any run; criteria testable; **the protocol text must
   describe the analysis that actually ran** (no Wald-declared/HKSJ-served mismatch).

## The report every batch
Two-line header —
`HARNESS-PRODUCED PAGES LIVE: n of N` / `BLIND-JUDGED: n of N (w/l/d)` (state that the wins
are AUDITABILITY wins) — **plus the target metric: our k vs comparator k per topic with the
shortfall cause named.** The count is pushed only with what the improved front end produces.

## Absolute rules (unchanged)
No `--no-verify`; never edit a refusing gate; never bump a baseline; no tuning to pass; no
hollow tabs; no comparator that is us; honest k over inflated k; every extraction TRUE vs
source; a landing isn't landed until the LIVE URL is fetched; a wrong number that
gate-passes is the only failure mode that matters — keep declining.

## Lane artefact durability (added after empagliflozin was lost to a clone reset)
A Codex lane cannot commit (sandbox blocks .git), so its output exists ONLY as untracked files
in its clone. Therefore:
- **Never `git reset --hard`, `git clean`, or re-dispatch into a clone that holds uncommitted
  lane output.** Harvest first: `sh scripts/harvest_lane.sh <clone> <scratch/harvest/<job>>`.
- **Harvest a lane's artefacts to durable scratch the moment it completes**, before any reuse.
- **Cleanup is scoped and never touches a tree another lane holds. Never `prune`.**
- A lane whose output exists only uncommitted is a lane you may have to run twice — the two
  losses this project took (empagliflozin, the gated statins page) were both this exact shape.

## Lane artefacts topic-scoped + verified-by-name (donor-evidence fix)
Untracked files survive `git reset --hard`, so a reused clone can still hold a PRIOR lane's
RECALL-*.md / VERIFY-*.md — and two recall lanes once read another topic's stale file as their own
(the donor-evidence shape). Structural rules:
- Before reusing an IDLE clone (one no live lane holds) for a new lane, `git clean -fdq` it to remove
  stale untracked artefacts. Never clean a tree another lane is using.
- Read a lane artefact ONLY by exact topic-scoped name AND content-verified: `sh scripts/read_lane.sh
  <clone> <KIND> <slug>` refuses a file that doesn't reference <slug>. Never `ls KIND-*.md | head`.
