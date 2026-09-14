# Reproducible meta-analysis harness

**What this is.** A harness that builds a meta-analysis from a *committed protocol*
and publishes it as a tabbed, auditable page. The protocol commit SHA **is** the
registration: it lands before any search runs.

**What this is not.** It is **not** a claim of stronger evidence than the published
comparators. The offer is **greater auditability**: every number traces to a
committed source, every absence is *declared* rather than left blank, and any
hand-edit breaks the gate.

## The loop
```
protocol committed FIRST (the SHA is the registration)
  -> search  -> screen (a rule id on every record)
  -> extract (five fields, source hierarchy)
  -> synthesise UNDER THE DECLARED METHOD
  -> tabbed page -> published on this surface
  -> re-run from that SHA on a FRESH CLONE and diff (reproduction census)
  -> blinded AI judges OUR URL vs THE PUBLISHED OPEN-ACCESS META
```
Every deficiency a judge names is fixed in the **harness**, never patched on the
page.

## The two-limb publication gate (`harness/gate.py`, enforced by `.githooks/pre-commit`)
A page publishes only if **both** hold:

1. **Reproducibility & integrity** — reproduces from a fresh clone with the
   reproduction census at **0 failures**; the *served* analysis method equals the
   *declared* method; nothing is hand-made (any hand-edit changes the served bytes
   and breaks the census pin).
2. **Named published open-access comparator** — a comparator with PMID/DOI, marked
   open access, with the **trial-set overlap stated on the page**. An identical
   estimate on an identical trial set is arithmetic, not corroboration — so `k`
   must be met by *our own* search, and the overlap is always shown.

`tests/test_gate.py` proves the gate **refuses** each failure mode. Run it:
```
python tests/test_gate.py
```

The gate is fail-closed: if it cannot execute, it refuses. **Never** `--no-verify`,
never edit a gate that is refusing you — fix the harness that produced the page.

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

## Reproducibility contract
- Stdlib-only. The page is a **pure, deterministic** function of a `review.json`
  object; `review_sha256` covers the review core, `html_sha256` covers the served
  page. The census (`harness/census.py`) re-derives both on a fresh clone.
- The search is **fetch-once**: results are cached in-repo under `cache/` and
  committed, so screening/extraction/synthesis replay **offline** and identically.
- The index (`harness/index.py`) is **generated, never hand-maintained**.

## Layout
```
protocols/        one .md per PICO topic; committing it is the registration
cache/            committed fetch-once search caches (offline-replayable)
harness/          canonical, page, census, gate, index (+ pipeline, synth to come)
docs/             GitHub Pages root: generated index + reviews/<slug>/
tests/            gate refusal proof
PICO.md           the preregistered 20-40 topic list
```
