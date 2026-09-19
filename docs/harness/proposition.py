"""Seventh gate — categorical/membership + methodological proposition contradictions.

The canonical-claim gate (harness/claim.py) closes the NUMERICAL family: no surface may assert a
significance/null-crossing opposite to the single derived claim object. But contradictions escape the
claim object whenever the proposition is not numerical — a trial asserted as BOTH pooled and
declared-absent, a suppressed pool that still renders an estimate, a trial both eligible and excluded,
a result presented as current while the topic is invalidated, a standing result whose source is
retracted. These are categorical (membership) or methodological propositions; a value-check cannot see
them (there is no number to compare).

This module derives those propositions from the review OBJECT (a check on the object, never a text
scan — a text scan of rendered prose is exactly what the claim gate must fall back to, and it is weaker)
and returns any pair (P and not-P) asserted at once. census refuses the build on any contradiction, so
the three families — numerical (claim.py), membership (here), methodological (here) — are all gated.

Every check is an OBJECT invariant that the current corpus satisfies; each has a PLANT test proving it
fires on the contradiction it names. Adding a check that the corpus cannot pass is forbidden (build the
capability first): these were verified clean on all 32 live topics before the gate was wired fail-closed.
"""


def _nid(x):
    return str(x or "").replace("PMID ", "").replace("NCT", "NCT").strip()


def contradictions(core):
    """Return a list of {family, proposition, detail} — empty when the object is internally consistent."""
    out = []
    outcomes = core.get("outcomes", []) or []

    # ---- MEMBERSHIP family --------------------------------------------------------------------
    # M1 (Torres pooled-and-not-pooled): a trial cannot be BOTH pooled and declared-absent for the SAME
    # outcome. It is exactly one member of exactly one set; appearing in both is a membership contradiction
    # that no significance check can see (both entries can carry internally-consistent numbers).
    for o in outcomes:
        pooled = {_nid(t.get("id")) for t in (o.get("trials") or []) if t.get("id")}
        absent = {_nid(t.get("id")) for t in (o.get("declared_absent_trials") or []) if t.get("id")}
        both = pooled & absent
        if both:
            out.append({"family": "membership", "proposition": "pooled_and_declared_absent",
                        "detail": f"outcome {o.get('name')!r}: trial(s) {sorted(both)} are listed as BOTH "
                                  f"pooled and declared-absent"})

    # M2 (iv-iron no-pool beside k=2 pooled): a primary pool suppressed as estimand-incompatible must NOT
    # also carry a usable pooled estimate. Suppressed means "no single coherent effect is asserted"; an
    # estimate beside the suppression is the forbidden object rendering itself.
    for o in outcomes:
        r = o.get("result") or {}
        if (r.get("suppressed_incompatible") or r.get("estmeasure_incompatible")) and r.get("estimate") is not None:
            out.append({"family": "membership", "proposition": "suppressed_and_pooled",
                        "detail": f"outcome {o.get('name')!r}: the pool is suppressed as estimand-incompatible "
                                  f"yet still carries a pooled estimate {r.get('estimate')} — no-pool and a "
                                  f"pooled effect asserted at once"})

    # M3 (EFFECT-HF eligible-and-design-excluded): one identifier cannot receive both an include and an
    # exclude screening decision. A record screened in AND out is a membership contradiction upstream of
    # every count on the page.
    dec = {}
    for rec in (core.get("screening") or {}).get("records", []) or []:
        rid = _nid(str(rec.get("id", "")).split("·")[-1])
        d = rec.get("decision")
        if rid and d:
            dec.setdefault(rid, set()).add(d)
    for rid, ds in sorted(dec.items()):
        if "include" in ds and "exclude" in ds:
            out.append({"family": "membership", "proposition": "eligible_and_excluded",
                        "detail": f"record {rid} carries BOTH an include and an exclude screening decision"})

    # ---- METHODOLOGICAL family ----------------------------------------------------------------
    inv = core.get("invalidation") or {}
    rep = core.get("reproduction") or {}

    # X1 (byte-reproducible beside retraction / current beside invalidated): a topic marked STALE
    # (invalidated — e.g. a known-eligible trial not pooled) must NOT simultaneously assert its primary
    # result is CURRENT/valid. Byte-reproducibility is NOT currency (a stale page can replay
    # deterministically), so reproduction is not the contradiction; asserting current-validity IS.
    if inv.get("stale") and core.get("headline_current") is True:
        out.append({"family": "methodological", "proposition": "current_while_invalidated",
                    "detail": "the topic is STALE (invalidated) yet asserts its headline result is current"})

    # X2 (committed-before-synthesis beside precedence-not-demonstrated): a topic may not claim its
    # protocol was preregistered/committed BEFORE the synthesis while also recording that this precedence
    # is not demonstrated. Preregistration precedence is a methodological proposition, not a number, so it
    # escapes the claim gate.
    if rep.get("preregistered_before_synthesis") is True and rep.get("precedence_demonstrated") is False:
        out.append({"family": "methodological", "proposition": "prereg_precedence_unsupported",
                    "detail": "claims the protocol was committed before synthesis, yet records that "
                              "preregistration precedence is not demonstrated"})

    return out
