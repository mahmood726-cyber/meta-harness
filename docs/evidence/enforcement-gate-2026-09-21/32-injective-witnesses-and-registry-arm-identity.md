# Injective role-labelled witnesses, and arm identity carried end to end

Two further auditor passes reshaped F4. Both were reproduced on the real path before anything was built.
Measured 2026-09-24. Nothing landed; no served number moved.

## 1. The non-injective witness — sharper than the pair swap

Change **only** `ai`, 2347 -> 1687 (the genuine *placebo* count). Keep `n1i=4949, ci=1687, n2i=4952`.
Every digit is authentic and present. Through the real `harness.verify.verify_pooled` on the real held
abstract:

    AUTHENTIC                       RR 1.3921   verify_pooled=verified   gate PASS
    NON_INJECTIVE (ai -> 1687)      RR 1.0006   verify_pooled=verified   gate PASS
    hand_binding._tuple_in(...)     True in both cases

`"1687"` occurs **once** in the abstract and witnesses **both** arm slots, because `1687/4949 = 34.088%`
and `1687/4952 = 34.067%` both display `34.1%`. The finding is erased — 1.392 to essentially the null —
**with no invented number**, so no digit check can reach it.

**The invariant is not "the two numbers must differ."** It is that one source occurrence may not witness
two mutually exclusive arm-specific fields.

## 2. The CT.gov route discards arm identity it already has

    harness/target_endpoint.py:759   _counts_from_om() classifies intervention/comparator groupIds
    harness/target_endpoint.py:788   returns intervention_arm, comparator_arm
    harness/target_endpoint.py:875   c["endpoint_counts"] = {k: counts[k] for k in ("ai","n1i","ci","n2i")}
    harness/target_endpoint.py:877   the arm NAMES survive only inside a PROSE span
    harness/target_endpoint.py:1014  row.update({"ai":..., "n1i":..., "ci":..., "n2i":...})

Searched across `harness/` and `scripts/`: `intervention_arm` / `comparator_arm` appear **only** in
`target_endpoint.py`. Nothing downstream reads them. The registry states which arm owns each count and
the projection throws it away one line later — so this could never have been a `hand_binding`-only fix.

Cochrane's *Handbook* and the RevMan data-package specification both treat Arm, Reference arm, Sample
size and Cases as constituents of the result object rather than free text; schema v2 follows that.

## 3. My own first injectivity rule was wrong, and authentic data proved it

I wrote: *the four role-specific witnesses must have four distinct coordinates*. Measured against the 32
authentic rows in evid2's `TYPED_ARMS.json`:

    witnesses recorded at SENTENCE granularity (their current data):
        "all four coordinates distinct"     would refuse  25 of 32 authentic rows
        "no coordinate shared across arms"  would refuse  16 of 32 authentic rows

Those are not violations. Example, PMID 30418475 "Adverse events": one span `[2628:2731]` —
*"Adverse events occurred in 2697 (77.2%) and 2723 (78.1%) patients in the linagliptin and placebo gro…"*
— is recorded as `events_evidence` for **both** arms. The sentence establishes ownership by order; its
coordinates simply cannot say which number each field points at.

At **token** granularity the rule behaves exactly as intended, verified on real source bytes:

    "530"  balanced-crystalloids abstract : 2 occurrences [851:854], [905:908]
           -> ai=530 and ci=530 each get their own coordinate -> PASS   (a real case (d))
    "1687" REWIND abstract                 : 1 occurrence
           -> both arms must share it -> ARM_WITNESS_NOT_INJECTIVE      -> REFUSED

So the requirement is: **the coordinate locates the field's own numeric token, not the enclosing
sentence.** A fraction ("530 of 2433 patients in the BMES group") then needs no exception, because
`events` points at `530` and `total` at `2433`.

Had this not been measured, the rule would have refused roughly three quarters of the authentic corpus —
the over-fix that case (d) exists to catch, committed in the fix itself.

## 4. The regression, through the complete producer -> renderer -> publication gate

Lane F4G, 18 cases on a synthetic topic. Ownership verdicts, all correct:

| case | ownership | first semantic blocker |
|---|---|---|
| AUTHENTIC | PASS | — |
| ONLY_INTERVENTION_EVENTS | REFUSE | `ARM_EVENT_OWNER_MISMATCH` |
| NON_INJECTIVE_VALUE_ATTACK | REFUSE | `ARM_EVENT_OWNER_MISMATCH` |
| WHOLE_OBJECT_REVERSED | REFUSE | `CONTRAST_REVERSED_POLICY` |
| EQUAL_DISTINCT_WITNESSES | PASS | — |
| WHOLE_PAIR_SWAP | REFUSE | `ARM_EVENT_OWNER_MISMATCH` |
| EVENT_ONLY_SWAP | REFUSE | `ARM_EVENT_OWNER_MISMATCH` |
| DENOMINATOR_ONLY_SWAP | REFUSE | `COUNT_DENOMINATOR_MISMATCH` |
| SHARED_COORDINATE | REFUSE | `ARM_WITNESS_NOT_INJECTIVE` |
| PERCENTAGE_WILDCARD_DENOMINATORS | REFUSE | `COUNT_DENOMINATOR_MISMATCH` |
| ABSENT_COUNT | REFUSE | `COUNT_EVENT_ARM_UNBOUND` |
| MISSING_OBJECTS | REFUSE | `COUNT_ARM_OBJECTS_MISSING` |
| HAND_PROSE_AUTHENTIC / HAND_PROSE_EQUAL | PASS | — |
| ABSTRACT_MACHINE / REGISTRY_MACHINE | PASS | — |
| TABLE_EQUAL_DISTINCT | PASS | — |
| RESTORE | PASS | — |

Two mechanisms, two distinct codes: an event that no longer belongs to its `group_id` is
`ARM_EVENT_OWNER_MISMATCH`; two fields sharing a witness coordinate is `ARM_WITNESS_NOT_INJECTIVE`.
Case (d) passes on three routes — prose, table, and equal values with distinct witnesses.

## What this does NOT establish

Every case's **complete-gate** verdict is REFUSE, first blocker `L1: manifest missing 'protocol_sha'`.
A synthetic topic has no protocol marker, certificate, tracked cache, replay config or named OA
comparator, and the lane refused to fabricate any of them. Complete-gate certification, a full BUNDLE
build, the standalone bundle ownership replay, and migration of the real corpus data are **NOT_REACHED**
and are not claimed.

`COUNT_ARM_OBJECTS_MISSING` on real served rows remains correct: the typed objects are the data lane's
half, and no observation was generated, inferred or defaulted for a real corpus row.
