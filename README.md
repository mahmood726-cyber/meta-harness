# Reproducible meta-analysis harness

**What this is.** A harness that builds a meta-analysis from a *committed protocol*
and publishes it as a tabbed, auditable page. Every one of the 32 served pages is
**re-derivable from committed inputs**: it replays from the committed cache on a fresh
clone (the `verify` limb runs that replay on all 32 before anything deploys).

**What is NOT established, stated up front.** Registration-time reproduction is *not*
established for the legacy corpus. No topic has a protocol-only registration commit
(each protocol was first committed inside a build), and every page carries a
retraction of the earlier claim that re-running from the protocol SHA regenerates it
byte-for-byte: the build consumes post-registration state that the protocol commit
does not pin. Nor was `k` met by our own search on most topics: 11 of 32 ran
known-item retrieval and 17 title-seeded retrieval (trial sets pre-identified), 4 a
hand-written keyword search, 0 a registered concept search — every page states its
class and retracts any systematic-search claim. The 32 legacy topics are therefore
the adversarial regression corpus, not a validation set; prospective validation is
specified, not landed (`docs/PROSPECTIVE_VALIDATION_SPEC.md`).

**What this is not.** It is **not** a claim of stronger evidence than the published
comparators. The offer is **greater auditability**: every number traces to a
committed source, every absence is *declared* rather than left blank, and any
hand-edit breaks the gate.

## The loop
```
protocol committed (intended FIRST; for the legacy corpus it was committed inside a build)
  -> search  -> screen (a rule id on every record)
  -> extract (five fields, source hierarchy)
  -> synthesise UNDER THE DECLARED METHOD
  -> tabbed page -> published on this surface
  -> replay from the COMMITTED CACHE on a fresh clone and diff (reproduction census, 32 of 32)
  -> blinded AI judges OUR URL vs THE PUBLISHED OPEN-ACCESS META
```
The replay step proves re-derivability from committed inputs, not reproduction from
registration — see "What is NOT established" above.
Every deficiency a judge names is fixed in the **harness**, never patched on the
page.

## The two-limb publication gate (`harness/gate.py`, enforced by `.githooks/pre-commit`)
A page publishes only if **both** hold:

1. **Reproducibility & integrity** — replays from the committed cache on a fresh
   clone with the reproduction census at **0 failures**; the *served* analysis method
   equals the *declared* method; nothing is hand-made (any hand-edit changes the served
   bytes and breaks the census pin).
2. **Named published open-access comparator** — a comparator with PMID/DOI, marked
   open access, with the **trial-set overlap stated on the page**. An identical
   estimate on an identical trial set is arithmetic, not corroboration — so the page
   states how `k` was met (known-item / title-seeded / hand-written keyword / concept
   search) and any parity figure is reported split by that class; the known-item and
   title-seeded groups are not evidence of search capability. The exact trial-set
   overlap is not yet machine-measured on any topic (comparator tables are not
   machine-exposed); the page states what is verifiable by date.

`tests/test_gate.py` proves the gate **refuses** each failure mode. Run it:
```
python tests/test_gate.py
```

The gate is fail-closed: if it cannot execute, it refuses. **Never** `--no-verify`,
never edit a gate that is refusing you — fix the harness that produced the page.

## Design-decision contract
Detected design hazards are not warnings. Each pooled study now carries a typed
design action (`ALLOW`, `ALLOW_WITH_LABEL`, `ADJUST`, `MANUAL_REVIEW`, or
`REFUSE`) plus evidence-backed `correlation_handling`; a validity-critical
hazard cannot proceed to PM/HKSJ as prose only. The current non-parallel-design
state is **PREVALENCE UNKNOWN** until an ontology-backed registry sweep is
complete.

## How a commit lands (gate authority, 2026-09-14)
The gates above are enforced **server-side**, so they survive `git clone` and do not depend
on anyone having installed a hook:

- **Pages deploys only from a green `verify`.** The Pages source is "GitHub Actions"; the sole
  deploy path is the `deploy` job in `.github/workflows/verify.yml`, which `needs: verify`.
  A red `verify` means no deploy and the last good deployment stays served.
- **`main` accepts a push only if `verify` already passed on that exact SHA** (repository
  ruleset, no bypass actors). So every landing is: push to a branch -> wait for `verify`
  -> `git push origin <sha>:main`. A direct push of an unchecked or red commit is rejected
  by the server (`GH013`). The same rule blocks force-pushes and deletion of `main`.
- `.githooks/pre-commit` (`git config core.hooksPath .githooks`) runs the same standard
  locally so you find out before the push; it is a convenience, not the enforcement.

The refusals were demonstrated before being relied on: `evidence/gate-authority-2026-09-14/`.

## Prospective validation
The auditor's freeze requirements and protocol (architecture identity, raw-input preservation, the defect
ledger outside the frozen tree, the no-silent-rerun policy, custody, release timing, model-stage binding, the frozen
eligibility universe, and the tamper-evident-not-blinded claim) are recorded as requirements in
`docs/PROSPECTIVE_VALIDATION_SPEC.md` (served at `/PROSPECTIVE_VALIDATION_SPEC.md`).

## Reproducibility contract
- Stdlib-only. The page is a **pure, deterministic** function of a `review.json`
  object; `review_sha256` covers the review core, `html_sha256` covers the served
  page. The census (`harness/census.py`) re-derives both on a fresh clone.
- The search is **fetch-once**: results are cached in-repo under `cache/` and
  committed, so screening/extraction/synthesis replay **offline** and identically.
- The index (`harness/index.py`) is **generated, never hand-maintained**.

## Layout
```
protocols/        one .md per PICO topic; its commit is the intended registration (not protocol-only for the legacy 32)
cache/            committed fetch-once search caches (offline-replayable)
harness/          canonical, page, census, gate, index (+ pipeline, synth to come)
docs/             GitHub Pages root: generated index + reviews/<slug>/
tests/            gate refusal proof
PICO.md           the preregistered 20-40 topic list
```
