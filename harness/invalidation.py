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


def _norm_id(x):
    """Normalise an id token so a screening record (often 'ACRONYM · 12345678') and a pooled trial
    ('PMID 12345678') compare equal: take the trailing identifier token, strip a PMID/NCT prefix."""
    s = str(x or "").strip()
    if "·" in s:
        s = s.split("·")[-1].strip()
    s = s.replace("PMID ", "").replace("PMID:", "").strip()
    return s.split()[-1].strip() if s.split() else s


def _present(res):
    return bool(isinstance(res, dict) and not res.get("suppressed_incompatible")
               and res.get("present") is not False and res.get("estimate") is not None)


def _eligible_not_pooled(core, id_nct=None):
    """Records screened-in (decision=include) but not pooled in ANY outcome — object-derived. Resolves
    identifiers through id_nct (raw id -> nct) so a trial pooled under one identifier and screened under
    another is not falsely flagged (NAMED_BUT_UNBOUND)."""
    id_nct = id_nct or {}
    pooled = set()
    for o in (core.get("outcomes") or []):
        for t in (o.get("trials") or []):
            rid = _norm_id(t.get("id") or t.get("label"))
            pooled.add(rid)
            if rid in id_nct:
                pooled.add(_norm_id(id_nct[rid]))
    out = []
    for r in ((core.get("screening") or {}).get("records") or []):
        if r.get("decision") != "include":
            continue
        nid = _norm_id(r.get("id"))
        if nid and nid in pooled:
            continue
        if nid in id_nct and _norm_id(id_nct[nid]) in pooled:
            continue
        if nid:
            out.append(r.get("id"))
    # stable, de-duplicated
    seen = set()
    return [x for x in out if not (x in seen or seen.add(x))]


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
    # 0c. NEVER_CONSIDERED: a trial verified in-scope but absent from every identifier space in the
    #     corpus (not screened, not excluded, not declared absent). The true search-failure measure.
    ncr = signals.get("never_considered") or []
    if ncr:
        names = ", ".join(str(x.get("trial")) for x in ncr[:6])
        reasons.append({"code": "never_considered",
                        "detail": "an in-scope trial was NEVER retrieved (absent from every identifier space): "
                                  + names + " — invisible to screening/PRISMA/declared-absent; the search is "
                                  "demonstrably incomplete"})
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
    # 3. ELIGIBLE-DECLARED-ABSENT, OBJECT-DERIVED (read-only session's predicate, better than a curated
    #    list or a reason-string match that rots when reworded): a record whose COMMITTED SCREENING
    #    decision is 'include' but which is NOT in the pooled set of any outcome is an eligible trial the
    #    pool does not contain -- the completeness claim cannot be current. Derived from the object, so it
    #    catches prose-only admissions (colchicine-postop, probiotics) the reason-string match missed.
    elig = _eligible_not_pooled(core, signals.get("id_nct") or {})
    if elig:
        reasons.append({"code": "eligible_declared_absent",
                        "detail": "screened-in (decision=include) but not pooled in any outcome — eligible "
                                  "trials the pool does not contain: " + ", ".join(elig[:6])
                                  + (f", and {len(elig)-6} more" if len(elig) > 6 else "")
                                  + "; the completeness claim cannot be current"})
    # 3b. A page with NO checkable pooled claim renders 'Claims checked: 0' -- the canonical-claim gate
    #     cannot fire, so a clean-looking output on the WORST page. That is a failing state, not neutral.
    if not any(_present(o.get("result")) for o in (core.get("outcomes") or [])):
        reasons.append({"code": "no_checkable_claim",
                        "detail": "no outcome produced a pooled claim (Claims checked: 0) — the canonical-claim "
                                  "gate cannot fire here, so a page with the weakest evidence would otherwise "
                                  "show the cleanest gate output; treated as a limitation, not a pass"})
    # 4. A search source errored (retrieval completeness unproven, distinct from RAN_ZERO). Suppressed
    #    when search_not_executed already fired for this topic -- that is the same fact, stated once.
    ss = (core.get("search") or {}).get("source_status") or {}
    errored = [name for name, st in ss.items() if st == "RAN_ERROR"]
    if errored and not sne:
        reasons.append({"code": "search_source_errored",
                        "detail": "a search source returned an error (" + ", ".join(errored)
                                  + ") — retrieval completeness for this topic is unproven"})
    return {"stale": bool(reasons), "reasons": reasons}
