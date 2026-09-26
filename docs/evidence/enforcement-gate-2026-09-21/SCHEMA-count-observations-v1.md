# Typed per-arm count observation — schema v1 (STABLE, for the evid2 data lane)

Owner: the F4 repair lane. Extracted from the real code (`harness/count_observations.py` as patched by
`F4B.patch` + `F4D.patch`), not transcribed from a summary. **evid2 produces DATA to this schema; this
schema does not change under evid2.** If a field here is wrong or unusable, say so and it will be
versioned to v2 — do not silently diverge, and do not rename a field, because
`observation_mismatch()` compares them by name.

Canonical patches: `C:\mh-artefacts\patches\` (POOL, MASKING, ARM_final, REGSPAN) and
`C:\mh-artefacts\f4b\F4B.patch`, `C:\mh-artefacts\f4d\F4D.patch`.
`F4D.patch` is cumulative against `a4e556e3` and already contains the F4B prerequisite.

## The object

One observation per arm, two per count row, emitted in intervention-then-comparator order.

    {
      "arm":        {"role": "intervention" | "comparator", "name": <source arm name, verbatim>},
      "arm_id":     <normalized(arm.name).lower()>,        # row-local source-name identity,
                                                           # NOT a registry arm id, NOT synonym-resolved
      "events":     <int>,
      "n":          <int>,
      "total":      <int>,                                 # alias of n; MUST equal n
      "outcome":    <the outcome spec's name>,
      "population": <str> | null,                          # null unless exactly ONE is found
      "window":     <object> | null,                       # null unless any field is set
      "span": {
        "events":      <witness>,
        "denominator": <witness + {"basis": <how the n was established>, "derivation": null}>,
        "context":     <witness, role "outcome/population/window">
      },
      "percentage_corroboration": [ {"reported": "<pct as printed>", "agrees": <bool>} ],
      "context_state": {
        "population": "BOUND" | "NO_EVIDENCE",
        "window":     "OBSERVED" | "NO_EVIDENCE"
      }
    }

### `witness`

    {
      "role":            "events" | "denominator" | "outcome/population/window",
      "document_ref":    <the held document reference>,
      "document_sha256": <sha256 of the held document>,
      "text":            <the exact located substring>,
      "representation":  "extract._norm + hand_binding._EN_DASH",
      "start": <int> | null,          # offsets address NORMALIZED held text, never a claimed string
      "end":   <int> | null
    }

A table witness additionally carries `column`, `table_row_offset`, `table_row`, and
`representation: "table cell/header text at the identified row and column"`, with `start`/`end` null —
a table row names its row and column instead of inventing prose offsets.

## The two rules that decide admission

1. **A denominator must be a reported per-arm n bound to a span**, or be derived with its basis declared
   in `span.denominator.basis`. **A rounded percentage may CORROBORATE a denominator and must never
   stand in for one.** Percentages live only in `percentage_corroboration`; they never supply `n`.
   Refusals: `COUNT_DENOMINATOR_UNBOUND` ("no unique reported per-arm denominator; percentages cannot
   supply n"), `COUNT_DENOMINATOR_MISMATCH` ("claimed n differs from the reported n attached to this
   arm").
2. **Each event count is bound to its arm by source structure, never by name order.**

## Validation your data must survive (`observation_mismatch`)

Supplied observations are compared against observations **independently re-extracted from the source**:

- the supplied list must be a list of the same length as the computed list;
- `events`, `n`, `total` must each be `type(...) is int` — a bool, a float or a numeric string fails;
- these fields must match exactly, by name:
  `("arm_id", "arm", "events", "n", "total", "outcome", "population", "window", "span")`.

Any difference yields `ARM_OWNERSHIP_MISMATCH` and the row abstains. Omitting `observations` entirely is
permitted (extraction may not have run); supplying them wrongly is not.

## Contrast contract (`declared_contract`)

    row["contrast"] = {"numerator": <arm>, "denominator": <arm>, "scale": "RR" | "OR"}

Only the configured intervention/comparator orientation is publishable. A deliberately reversed contrast
returns **`CONTRAST_REVERSED_POLICY`** — a *policy* refusal, not a claim the reversed calculation is
invalid; changing the published estimand requires changing the protocol/config. Anything else malformed
returns `COUNT_CONTRAST_INVALID`. Source mention order is irrelevant to this decision.

## Refusal codes evid2 may see

    ARM_OWNERSHIP_MISMATCH        supplied observation differs from its named source witness
    ARM_OWNERSHIP_CONTRADICTED    counts bound to the wrong arm by structure
    COUNT_AMBIGUOUS               competing structural observations for the endpoint
    COUNT_ARM_OBJECTS_MISSING     a pooled count trial carries no observations/arm terms
    COUNT_SOURCE_UNBOUND          re-binding at publication failed
    COUNT_DENOMINATOR_UNBOUND     no unique reported per-arm denominator
    COUNT_DENOMINATOR_MISMATCH    claimed n differs from the reported n for that arm
    CONTRAST_REVERSED_POLICY      reversed contrast; change the protocol, not the label
    COUNT_CONTRAST_INVALID        malformed contrast object

## The population evid2 is producing for

**34 count rows** — held entries carrying all four of `ai/n1i/ci/n2i`, across 18 `verified_arms.json`
files (259 held entries in total; the other 225 are not count-shaped). Measured twice, by two independent
instruments that agree:

    missing comparator_direction            34 of 34
    missing typed observation objects       34 of 34
    existing typed objects in the corpus     0 of 34   -> UNEXERCISED as persisted inputs

Provenance census of those 34, so the kinds of item are named before the number:

    fulltext_verified_arms  14      abstract_verified        8      abstract_verified_arms  6
    aact_verified            3      published_rate           2      registry_verified       1

Two cautions from our own mistakes, which will cost evid2 time if repeated:

- **Approval metadata is not source.** An entry's `source`/`verification`/`provenance` prose often
  restates the arithmetic (e.g. "818/7942=10.3%"). The witness must address the resolved held document.
- **The bytes checked depend on provenance.** `harness/verify.py:73` sends the digit check to the held
  **abstract** only for `("abstract", "pmc_fulltext", "abstract_verified")`; every other provenance is
  checked against the **source span**. That is 26 of 34 rows. Check the text the verifier actually
  consults for that row, not the one you assume.
