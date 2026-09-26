# The typed object reaches BUNDLE — and nothing downstream checks it

Lane F4I, `/f/mh-f4`, 2026-09-25, on the **real** topic `glp1-ra-mace-t2d` using the data lane's **real**
exported rows. Nothing landed; `docs/` was never written; no certified bundle was produced.

## Why a real topic was needed

Three prior attempts died on the same cause — a synthetic topic is not a certified published review:

    F4E4  complete-gate PASS   blocked: no protocol_sha, certificate, tracked cache, comparator
    F4G   BUNDLE projection    exercised; full build NOT_REACHED
    F4H   full BUNDLE build    crashed on the absent synthetic CERTIFICATE.json

`glp1-ra-mace-t2d` is the only served topic with a real certificate and a `BUNDLE.json`, and evid2's
export happens to contain **exactly the two rows the gate refuses** there.

## The result

**BUNDLE construction REACHED; publication REFUSED; standalone ownership UNENFORCED.**

    both requested typed rows arrived in the object returned by the complete production builder
    successful production BUNDLE write                     0 of 1 full-build attempts
    COUNT_ARM_OBJECTS_MISSING, after the real rows present  gone for 2 of 2 rows
    first ownership blocker now                            COUNT_SOURCE_UNAVAILABLE

The write is refused by the CLI at `scripts/build_bundle.py:2428` on accumulated problems, with the
review/certificate mismatch checked at `:2237` — the same certificate pinning that gates every patch in
this stack. The production projection is `:2156`, inserted by the full builder at `:2305`, whose complete
object is returned at `:2407`.

### The defect

> In a supplemental control using the authentic served envelope and the exact production-generated count
> field, the authentic case **and all 3 of 3 bundle-only attacks returned `PASS` with no failures.**

The typed role object is carried all the way into BUNDLE, and **the standalone verifier does not check
it**. A bundle-only mutation of arm ownership is not refused. The direct full-build diagnostic returned
FAIL for all 4 of 4 cases on unrelated artifact/certificate mismatches, and **none of those is credited
as an ownership refusal** — correctly, since crediting them would be exactly the "unrelated first
blocker" error the contract forbids.

This is the same class as the served-verifier defect in
`33-freedom-semantic-repair-and-the-served-route-defect.md`, now proven by execution on the real topic
with real data. Acceptance item (e) — *both* the producer route and the independent verifier must
enforce — is **not satisfied on the BUNDLE route**.

## The granularity gap closes mechanically

evid2's witnesses are at sentence granularity; injectivity needs the token. The lane was permitted to
**narrow within** an already-located span, never outside it, and used this deterministic rule:

> require exactly one complete integer token equal to the supplied field value inside evid2's recorded
> text; add that token's local offsets to the recorded start; require the resulting half-open interval to
> remain entirely inside the original; refuse zero or multiple matches as `UNNARROWABLE`; never search
> beyond the recorded text.

    narrowable field witnesses    8 of 8   across the two requested rows
    UNNARROWABLE                  0 of 2   rows

So the remaining work on evid2's 32 rows is mechanical, not a re-extraction — as schema v2 predicted.

## What was checked rather than assumed

- **Row identity before mutation.** Both exported `served_row_sha256` values matched, and the lane
  documented the exact hash encoding (default spacing, default ASCII escaping) rather than normalising
  fields to force a match.
- **Registry arm identity, independently.** All **4 of 4** exported arm IDs, labels and roles were
  checked against this topic's preserved AACT `design_groups` rows in
  `docs/acquisitions/glp1-ra-mace-t2d/aact_rows_2026-08-30/rows.json`. That validates group identity —
  explicitly *not* a registry observation source.
- **The held representation.** REWIND's is exactly `"TITLE: " + title + "\n\n" + abstract + "\n"`, whose
  SHA-256 matches evid2's `copy_sha256`, with each original sentence coordinate reproducing its recorded
  text.

## Stated limits

LEADER's full text is not held here — the served bundle declares it `NOT_IN_PACKAGE_LICENCE` — so its
refinements use evid2's supplied located text and independent replay against the original full text is
**NOT_REACHED**. No replacement text was generated or fetched. `percentage_corroboration: null` records
that no percentage object was supplied rather than asserting one.

## What this means

The data half works: given real typed rows, `COUNT_ARM_OBJECTS_MISSING` clears on both rows and the typed
object survives into the BUNDLE object. What does not work is the **consumer**. Two routes now
demonstrably fail to enforce ownership on artefacts that carry it:

    the SERVED verifier   0 of 3 mutating FREEDOM cases refused   (33-...)
    the BUNDLE route      0 of 3 bundle-only attacks refused      (this file)

Both need repair, and both sit behind the same 32-topic regeneration that gates everything else.
