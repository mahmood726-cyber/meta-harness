# FREEDOM: the semantic repair holds, and the SERVED verifier does not carry it

Lanes FREEDOM (measure) and FREEDOM-2 (implement), `/f/mh-f6`, 2026-09-24/25. Nothing landed; no served
number moved; nothing was rebuilt or signed.

## What acceptance item (b) now has

    5 of 5 requested negative cases   intended FIRST SEMANTIC refusal, in BOTH the patched producer
                                      emission checker AND the independent verifier
    4 of 4 required controls          no semantic refusal; pass the independent verifier and the
                                      publication bundle gate

The four existing cases were measured before anything changed, each with its mutation, its intended code
and its actual blocker:

    freedom_wrong_row              ANALYSIS_IDENTITY_MISMATCH        (4-point row claimed as 3-point)
    freedom_mixed_row              TUPLE_NOT_IN_ANY_CANDIDATE_SPAN
    freedom_numeric_prefix         TUPLE_NOT_IN_ANY_CANDIDATE_SPAN   (1.2 != 1.24)
    freedom_decimal_normalisation  no refusal -- numerically equal decimals must pass (control)

The two missing cases were **defined from held evidence**, not invented:

    sustain6_mi_as_mace       replace the MACE tuple and its result span with the held nonfatal-MI
                              result, preserving the MACE endpoint claim        -> ENDPOINT_INCOMPATIBLE
    amplitudeo_renal_as_mace  replace the MACE tuple and its result span with the held composite-renal
                              result, preserving the CV endpoint claim          -> ENDPOINT_INCOMPATIBLE

Both derive from an actual non-target result clause, with the source `file:line` recorded, and their
setup **fails loudly if the evidence changes** rather than silently becoming a pass. Trial names select
fixtures and are, in the lane's own words, "never enforcement exceptions" — so no PMID special-casing.

## The finding that needs a decision — item (e) is NOT satisfied for the served deployment

    the unchanged SERVED verifier: 0 of 3 mutating FREEDOM cases receive a semantic refusal.
    It reports BOUND, and fails only on CERTIFICATE_MISMATCH.

This is the served code mirror behaving exactly as documented — *"The served code mirror remains pinned
to its release until an authorised rebuild"* (`harness/gate.py:1289`). The consequence is concrete: a
reader who downloads and runs **the verifier we serve** would not catch these mutations today. The repair
exists only in the working tree.

Acceptance item (e) requires **both** the producer route and the independent verifier to enforce the
decision, with no alternative pooling route bypassing the checker. On the served deployment that is
**UNPROVEN**, and the lane explicitly declines to claim otherwise.

**Closing it requires a rebuild and re-release**, which changes served artefacts. That is Mahmood's
decision and signature, not an engineering call, and it was correctly not simulated: rebuilding and
signing were prohibited, and the full renderer/rebuild/publication sequence is recorded **NOT_REACHED**
rather than inferred.

## Also not claimed

The producer check-only route returns REFUSE on intact but **stale release pins**, so these are not full
producer/publication passes. "Universal absence of alternative pooling bypasses" remains UNPROVEN.

## Artefacts

The lane's own patch was 15 MB because its JSON artefacts were swept into the diff — scope was correct
(6 scripts, 5 tests, 1 harness) but it is not landable in that form. A clean source-only patch was
regenerated: **126,844 bytes, 12 source/test files**, secured at `C:\mh-artefacts\freedom\`. It is
cumulative: the POOL repair, my property-test amendments, and FREEDOM-2.

Checked after the lane ran, because these are the things most likely to be quietly damaged: the amended
property test is present, PMID assertions are **0**, and the POOL repair is intact (`and admission else`
occurs 0 times in `scripts/verify_bundle.py`). `tests/test_freedom2.py`: **9 passed**.
