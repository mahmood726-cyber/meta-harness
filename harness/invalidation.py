"""Invalidation propagation.

A single per-topic verdict computed from committed signals already in the review core. When any
invalidating condition holds, the topic is STALE: a dependent output (the pooled estimate, its
completeness, or the trials behind it) is known to be incomplete, superseded, or unproven, and
every surface that presents that output must say so rather than imply currency. The corpus index
publishes the count as it falls -- if 28 of 32 are current, it says 28 of 32.

Pure function of the core (integrity, per-outcome results, source_status all live there), so it is
part of the reproducible object and both build and replay produce it identically.

Conditions (each NAMED on the page so a reader sees WHY, and evidenced from committed state):
  retracted_pooled_trial        : a pooled trial is retracted / under an expression of concern
                                  (the estimate rests on retracted data)
  primary_reported_not_extracted: the PRIMARY outcome names trials that reported it but could not
                                  be pooled (the headline k is known-incomplete)
  eligible_declared_absent      : a screened-in trial is flagged ELIGIBLE yet not pooled
                                  (a known eligible trial missing from the pool)
  search_source_errored         : a search source returned RAN_ERROR (retrieval completeness for
                                  this topic is unproven, not merely zero)
"""


def _primary(core):
    outs = core.get("outcomes") or []
    return next((o for o in outs if o.get("primary")), (outs[0] if outs else None))


def assess(core, signals=None):
    """signals (optional): externally-computed, committed, per-topic signals the core does not carry
    on its own -- {'search_not_executed': {'class':..., 'detail':...} | None,
    'known_eligible_missing': [ {trial, mechanism, ...}, ... ]}. Passed in (not read here) so assess
    stays a pure function and both build and replay produce the same verdict."""
    signals = signals or {}
    reasons = []
    # 0. Search provenance: a topic whose "search" was a RAN_ERROR-rendered-as-run or explicit
    #    PMID-enumeration has NO genuine executed concept search -- its completeness claim is void.
    sne = signals.get("search_not_executed")
    if sne:
        reasons.append({"code": "search_not_executed",
                        "detail": "no genuine executed concept search (" + str(sne.get("class"))
                                  + "): " + str(sne.get("detail", "known-item retrieval cannot discover "
                                  "an unknown eligible trial"))})
    # 0b. A named eligible trial the audits identified is not in the pool (completeness void, and the
    #     pooled estimate is known-incomplete). Names carried even before external PMID verification.
    kem = signals.get("known_eligible_missing") or []
    if kem:
        names = ", ".join(str(x.get("trial")) for x in kem[:6])
        reasons.append({"code": "known_eligible_missing",
                        "detail": "a trial identified as eligible under the registered PICO is not pooled ("
                                  + names + (", and others" if len(kem) > 6 else "")
                                  + ") — the pooled result and completeness claim cannot be current"})
    # 1. Retraction / expression of concern among the POOLED trials.
    integ = core.get("integrity") or {}
    retr = list(integ.get("retracted") or [])
    conc = list(integ.get("concern") or [])
    if retr or conc:
        bits = []
        if retr:
            bits.append("retracted: " + ", ".join(str(x) for x in retr[:5]))
        if conc:
            bits.append("expression of concern: " + ", ".join(str(x) for x in conc[:5]))
        reasons.append({"code": "retracted_pooled_trial",
                        "detail": "a pooled trial's integrity is compromised (" + "; ".join(bits)
                                  + ") — the pooled estimate rests on it"})
    # 2. PRIMARY outcome reported-but-not-extracted (a reported eligible trial not poolable).
    prim = _primary(core)
    pres = (prim or {}).get("result") or {}
    if pres.get("reported_not_extracted"):
        rb = pres.get("reported_by") or []
        reasons.append({"code": "primary_reported_not_extracted",
                        "detail": "the primary outcome is reported by trials that could not be pooled ("
                                  + ", ".join(str(x) for x in rb[:5]) + ") — the pooled k is known-incomplete"})
    # 3. A screened-in trial explicitly flagged ELIGIBLE yet declared absent from the pool.
    elig = []
    for o in (core.get("outcomes") or []):
        for a in (o.get("declared_absent_trials") or []):
            r = (a.get("reason") or "")
            if r.strip().upper().startswith("ELIGIBLE"):
                elig.append(str(a.get("id") or a.get("label")))
    if elig:
        reasons.append({"code": "eligible_declared_absent",
                        "detail": "a screened-in trial is flagged ELIGIBLE under the registered PICO yet not "
                                  "pooled (" + ", ".join(dict.fromkeys(elig))[:120] + ")"})
    # 4. A search source errored (retrieval completeness unproven, distinct from RAN_ZERO). Suppressed
    #    when search_not_executed already fired for this topic -- that is the same fact, stated once.
    ss = (core.get("search") or {}).get("source_status") or {}
    errored = [name for name, st in ss.items() if st == "RAN_ERROR"]
    if errored and not sne:
        reasons.append({"code": "search_source_errored",
                        "detail": "a search source returned an error (" + ", ".join(errored)
                                  + ") — retrieval completeness for this topic is unproven"})
    return {"stale": bool(reasons), "reasons": reasons}
