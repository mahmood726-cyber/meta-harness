# Typed per-arm count observation — schema **v2** (SUPERSEDES v1) for the evid2 data lane

Owner: the F4 repair lane. **v1 is superseded**; do not produce data to it. Two auditor passes reshaped
the object, and both were reproduced on the real path before this was written.

The two changes from v1, and each exists because of a defect that was executed, not argued:

1. **Witnesses are per-field and INJECTIVE.** v1 let one source span cover a whole tuple.
2. **Arm identity is a `group_id`, carried end to end**, not a name recovered from prose.

---

## Why v1 was not enough — reproduced on the real modules

### The non-injective witness (sharper than the pair swap)

Change **only** `ai`, 2347 -> 1687 (the genuine *placebo* count). Keep `n1i=4949, ci=1687, n2i=4952`.
Every digit is authentic and on the page. Run through the real `harness.verify.verify_pooled` on the real
held abstract:

    AUTHENTIC                          RR 1.3921   verify_pooled=verified   gate PASS
    NON_INJECTIVE (ai -> 1687)         RR 1.0006   verify_pooled=verified   gate PASS
    hand_binding._tuple_in(...)        True in both cases

`"1687"` occurs **once** in the held abstract, and that single occurrence witnesses **both** arm slots,
because `1687/4949 = 34.088%` and `1687/4952 = 34.067%` both display as `34.1%`. The finding is erased —
1.392 to essentially the null — with **no invented number**. No digit check can catch this, because every
digit is genuinely there.

**The invariant is NOT "the two numbers must differ."** Genuinely equal arm values are legitimate and must
pass. The invariant is that **one source occurrence may not witness two mutually exclusive arm-specific
fields**. Equal values are fine *with distinct, role-specific witnesses*.

### The CT.gov route already has arm identity and throws it away

    harness/target_endpoint.py:759   _counts_from_om() classifies intervention/comparator groupIds
    harness/target_endpoint.py:788   returns intervention_arm, comparator_arm
    harness/target_endpoint.py:875   c["endpoint_counts"] = {k: counts[k] for k in ("ai","n1i","ci","n2i")}
    harness/target_endpoint.py:877   the arm NAMES are interpolated into a PROSE span only
    harness/target_endpoint.py:1014  row.update({"ai":..., "n1i":..., "ci":..., "n2i":...})

Searched across `harness/` and `scripts/`: `intervention_arm` / `comparator_arm` appear **only** in
`target_endpoint.py`. **Nothing downstream ever reads them.** The registry tells us exactly which arm each
count belongs to, and the projection at line 875 discards it one line after computing it. So this cannot
be repaired inside `hand_binding` — the typed object must survive
**extraction -> candidate -> row -> verify_pooled -> gate -> BUNDLE**, on every route (CT.gov, hand
override, abstract).

This is not a novel demand. Cochrane's *Handbook for Systematic Reviews of Interventions* treats the
intervention arm, the reference (comparator) arm, the sample size and the number of cases as constituents
of the result itself, and the RevMan data-package specification carries Arm, Reference arm, Sample size
and Cases as fields of the result object rather than as free text. Our result object should do the same.

---

## The object

One observation per arm, **two per count row**, in intervention-then-comparator order.

    {
      "role":       "intervention" | "comparator",
      "group_id":   <registry id, verbatim> | [<id>, ...] | null when no registry result exists,
      "group_id_scope": <the outcome measure / eventGroup the id is defined in>   # REQUIRED with group_id
      "arm_name":   <arm label, verbatim from the source>,
      "events":     <int>,
      "total":      <int>,
      "event_witness": <witness>,          # REQUIRED, role-specific
      "total_witness": <witness>,          # REQUIRED, role-specific
      "outcome":    <the outcome spec's name>,
      "population": <str> | null,          # null unless exactly ONE is found
      "window":     <object> | null,
      "percentage_corroboration": [ {"reported": "<pct as printed>", "agrees": <bool>} ],
      "context_state": {"population": "BOUND"|"NO_EVIDENCE", "window": "OBSERVED"|"NO_EVIDENCE"}
    }

Compatibility with v1: `arm_id` and `n` are retained as aliases (`arm_id` = normalized `arm_name`,
`n` = `total`) so existing consumers do not break, and they must agree with the fields they alias. The
authority is `group_id` + `role`, **not** the name.

### `witness` — now carries its own coordinates

    {
      "role":            "intervention.events" | "intervention.total"
                       | "comparator.events"   | "comparator.total",
      "document_ref":    <the held document reference>,
      "document_sha256": <sha256 of the held document>,
      "text":            <the exact located substring>,
      "representation":  "extract._norm + hand_binding._EN_DASH",
      "start": <int>, "end": <int>,     # offsets into the NORMALIZED held text
      "derivation":      null | {"basis": <how it was derived>, ...}
    }

**`derivation` is REQUIRED on a `*.total` witness**, and it is the field that carries this schema's
central contract. `null` means the denominator is **reported** — located verbatim in the source.
A non-null object means it was **derived**, and must name its basis. **This contract is reported-only:
a `*.total` witness with a non-null `derivation` is refused.** A rounded percentage may corroborate a
denominator and may never supply one, and `percentage_corroboration` is the only place a percentage may
appear.

*This field was missing from the first cut of v2 and was restored after lane F4K refused to migrate a
producer test without it.* The v1 assertion `all(o["span"]["denominator"]["derivation"] is None)` asserts
precisely "this denominator is reported, not derived", and v2 had left it unexpressible — so the one
property the denominator finding exists to protect could not be stated. Neither `.get("derivation") is
None` nor a token-equality substitute preserves it; the field has to be there.

Producer note: `harness/count_observations.py:225` sets the legacy value to `None`, but prose total
witnesses are constructed afresh at `:248`/`:251` and the coordinate helper at `:301` does not pass
`derivation` through, while table totals copy the legacy denominator witness at `:242`. So the producer
must be corrected to carry `derivation` on every route, not only the table one.

A table witness instead carries `group_id`, `column`, `table_row_offset`, `table_row`, with
`start`/`end` null — a table names its row and column rather than inventing prose offsets.

### The injectivity rule, stated so it can be checked mechanically

For the four role-specific fields, the witness **coordinate** must be distinct:

    key(w) = (w.document_ref, w.start, w.end)   or   (w.document_ref, w.group_id, w.column, w.table_row_offset)

    len({key(w) for w in the four witnesses}) == 4

Two fields sharing a coordinate is `ARM_WITNESS_NOT_INJECTIVE`. **Equal VALUES are permitted; shared
COORDINATES are not.** A row reporting 162 and 162 for the two arms is admissible when each 162 has its
own located occurrence, and refused when both point at the same one.

#### The ONE licensed exception: a distributive source phrase

*"17 patients in each group"* genuinely states both arms with one token, and refusing it loses authentic
rows. But a blanket "declared shared witness" re-opens the founding attack, where a single `"1687"`
witnessed both arms and collapsed RR 1.3921 -> 1.0006. The discriminator is that the attack's span is
arm-specific prose — *"1687 (34.1%) participants assigned to placebo"* — and carries **no distributive
marker**.

    a witness MAY be shared across both arms IFF it carries
        "distributive": {"marker": <licensing phrase, verbatim>, "span": [start, end]}
    the marker text must lie INSIDE the witness text, and must be one of a CLOSED list:
        "in each group", "in both groups", "in each arm", "in both arms", "per group", "per arm"

    shared coordinate, no distributive object          -> ARM_WITNESS_NOT_INJECTIVE
    distributive object, marker absent from the text   -> DISTRIBUTIVE_MARKER_ABSENT

The list is closed deliberately. "The writer judged it distributive" is not checkable and would be the
loophole. A distributive phrasing outside the list is **reported, not added locally** — extending the
list is a schema change.

#### The coordinate must locate the FIELD'S OWN TOKEN, not the enclosing sentence

This is the single most important implementation detail, and it was measured against the 32 rows in
`TYPED_ARMS.json` rather than reasoned about:

    witness spans recorded at SENTENCE granularity (current data):
        rule "all four coordinates distinct"      would refuse  25 of 32 authentic rows
        rule "no coordinate shared across arms"   would refuse  16 of 32 authentic rows

Those are not violations — they are coarse spans. Example, PMID 30418475 "Adverse events": one span
`[2628:2731]`, *"Adverse events occurred in 2697 (77.2%) and 2723 (78.1%) patients in the linagliptin and
placebo gro…"*, is recorded as `events_evidence` for **both** arms. The sentence does establish ownership
by order; its coordinates simply cannot say which number each field points at.

At **token** granularity the rule behaves correctly, verified on real source bytes:

    "530"  in the balanced-crystalloids abstract : 2 occurrences, [851:854] and [905:908]
           -> ai=530 and ci=530 each get their OWN coordinate -> distinct -> PASS   (a real case (d))
    "2433" / "2413"                              : 1 occurrence each -> distinct    -> PASS
    "1687" in the REWIND abstract                : 1 occurrence
           -> ai=1687 and ci=1687 must share it  -> ARM_WITNESS_NOT_INJECTIVE       -> REFUSED

And a fraction such as *"530 of 2433 patients (21.8%) in the BMES group"* witnesses both fields of **one**
arm from one sentence, which is legitimate — at token granularity `events` points at `530` and `total` at
`2433`, so the coordinates differ anyway and no exception is needed.

**So: record `start`/`end` as the offsets of the numeric token itself.** Keep the sentence if you like, in
a separate `context` field — but the coordinate that the injectivity check reads must be the token's.
This is the bulk of the remaining work on the 32 rows, and it is mechanical rather than a re-extraction.

---

## Refusal codes evid2 may see

    ARM_WITNESS_NOT_INJECTIVE     two arm-specific fields witnessed by the same source occurrence
    ARM_EVENT_OWNER_MISMATCH      an event count does not belong to the arm its group_id names
    ARM_OWNERSHIP_MISMATCH        supplied observation differs from its re-extracted source witness
    ARM_OWNERSHIP_CONTRADICTED    counts bound to the wrong arm by source structure
    COUNT_DENOMINATOR_UNBOUND     no unique reported per-arm denominator; percentages cannot supply n
    COUNT_DENOMINATOR_MISMATCH    claimed n differs from the reported n for that arm
    COUNT_AMBIGUOUS               competing structural observations for the endpoint
    COUNT_ARM_OBJECTS_MISSING     a pooled count trial carries no observations
    CONTRAST_REVERSED_POLICY      reversed contrast; change the protocol, not the label
    COUNT_CONTRAST_INVALID        malformed contrast object

---

## Instructions for the 34 rows

**Where CT.gov results exist, take arm ownership from the registry `groupId`, never from prose.** The
registry states which arm a count belongs to; a sentence only implies it. Set `group_id` and derive
`role` from the same classification the producer uses (`_classify_arms`, `target_endpoint.py:763`). Set
`group_id: null` only when there is genuinely no registry result, and say so per row.

### There are TWO populations here and they are not the same set

A correction, because it would otherwise make our numbers look contradictory:

    evid2's SERVED count rows (docs/reviews/*/review.json)          35   (32 bound, 3 set aside)
    my HELD hand-extraction entries (cache/*/verified_arms.json)    34
    rows in BOTH                                                    19
    only served                                                     16   (reached the page via CT.gov/AACT)
    only held                                                       15

**For the gate, evid2's served rows are the right denominator** — `check_count_arm_ownership` walks the
served `review.json`, so `COUNT_ARM_OBJECTS_MISSING` is counted over those. My 34 is the hand-binding
population, where the percentage-wildcard and non-injective defects live. Neither number was wrong;
both were quoted without naming the population, which is how two correct measurements became
incomparable. **Continue to produce data for the served rows.**

A real case (d) lives in that set: `PMID 35041780, Mortality, ai=530 ci=530` — genuinely equal event
counts with different denominators (2433 vs 2413), on a served page. Any rule that refused equal values
would refuse this authentic row.

The held population, with its kinds named before the number: **34** held entries carrying all four of
`ai/n1i/ci/n2i`, across 18 `verified_arms.json` files (259 held entries total; the other 225 are not
count-shaped). Measured twice by two independent instruments that agree:

    missing comparator_direction          34 of 34
    missing typed observation objects     34 of 34
    existing typed objects in the corpus   0 of 34   -> UNEXERCISED as persisted inputs

    fulltext_verified_arms 14    abstract_verified 8    abstract_verified_arms 6
    aact_verified 3              published_rate 2       registry_verified 1

Three cautions that have already cost this project time:

- **Approval metadata is not source.** Entry `source`/`verification`/`provenance` prose often restates
  the arithmetic ("818/7942=10.3%"). A witness must address the resolved held document.
- **Which bytes get checked depends on provenance.** `harness/verify.py:73` uses the held abstract only
  for `("abstract","pmc_fulltext","abstract_verified")`; every other provenance is checked against the
  **source span** — that is 26 of 34 rows.
- **A denominator may be registry-attested rather than in the abstract.** One row's `n` was briefly
  reported by us as fabricated; it came from an AACT per-arm total named in the span. Read the whole
  span, not a prefix.
