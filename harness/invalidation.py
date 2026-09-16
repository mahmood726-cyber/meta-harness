"""Invalidation propagation.

Auditor defect class recorded verbatim: DIAGNOSTIC–DECISION DECOUPLING — a
validity hazard is correctly detected and represented, but its state is not
causally connected to the analytic decision it should constrain. Plain alias:
disclosure-as-control. Class PROCESS, direction optimistic, severity
major-to-critical.

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
  pooled_variance_unsupported   : a reconstructed non-parallel design is still pooled without an
                                  explicit design adjustment
"""
import re
from . import design_key
from . import identity as identity_mod


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


def _norm_term(value):
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _fold_term(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def _slug_form(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")


def _compact(value):
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def _term_keys(value):
    keys = {_norm_term(value), _fold_term(value)}
    return {k for k in keys if k}


def _slug_starts_with(slug, term):
    slug_f = _slug_form(slug)
    sf = _slug_form(term)
    if sf and (slug_f == sf or slug_f.startswith(sf + "-")):
        return True
    cf = _compact(term)
    if not cf:
        return False
    slug_parts = [p for p in slug_f.split("-") if p]
    for idx in range(1, len(slug_parts) + 1):
        if _compact("-".join(slug_parts[:idx])) == cf:
            return True
    return False


def _agent_and_class_maps(config):
    agents = config.get("intervention_agents") or {}
    class_terms = config.get("intervention_class_terms") or []
    term_to_agent = {}
    for agent, terms in agents.items():
        for term in [agent, *(terms or [])]:
            for key in _term_keys(term):
                term_to_agent.setdefault(key, agent)
    class_keys = set()
    for term in class_terms:
        class_keys.update(_term_keys(term))
    return term_to_agent, class_keys


def _scope_amendment(config):
    for amendment in config.get("protocol_scope_amendments") or []:
        if amendment.get("kind") != "identifier_scope" or not amendment.get("date"):
            continue
        body = " ".join(str(amendment.get(k) or "") for k in (
            "heading", "original_scope", "widened_scope", "reason", "pre_specified_list", "body"))
        if "identifier" in body.lower() and any(w in body.lower() for w in ("widen", "scope")):
            return amendment
    return None


def _identifier_level(slug, config):
    """Classify the slug's leading intervention token from declared agents/class terms."""
    slug_l = str(slug or "").lower()
    candidates = []
    for agent, terms in (config.get("intervention_agents") or {}).items():
        for term in [agent, *(terms or [])]:
            if _slug_starts_with(slug_l, term):
                candidates.append(("AGENT", agent, term, len(_compact(term))))
    for term in config.get("intervention_class_terms") or []:
        if _slug_starts_with(slug_l, term):
            candidates.append(("CLASS", None, term, len(_compact(term))))
    if not candidates:
        return "CLASS", None, "identifier leading token is not a declared single agent"
    candidates.sort(key=lambda x: x[3], reverse=True)
    level, agent, term, _ = candidates[0]
    if level == "CLASS":
        return "CLASS", None, f"identifier leading token matches class term {term}"
    return "AGENT", agent, f"identifier leading token matches agent term {term}"


def _record_label(rec):
    raw = str(rec.get("id") or "").strip()
    rid = _norm_id(raw)
    label = str(rec.get("label") or rec.get("trial") or rec.get("acronym") or "").strip()
    if not label and "Â·" in raw:
        label = raw.split("Â·", 1)[0].strip()
    if label and rid and rid not in label:
        return f"{label} {rid}"
    return raw or rid or "unknown"


def identifier_scope(slug, config, screening_records):
    """Detect an agent-named identifier over a class-level included pool.

    Pure function: the slug, config declaration, and screening records are its only inputs.
    """
    level, identifier_agent, note = _identifier_level(slug, config or {})
    term_to_agent, class_keys = _agent_and_class_maps(config or {})
    pooled_agents = {}
    unresolved = []
    for rec in screening_records or []:
        if rec.get("decision") != "include":
            continue
        trial = _record_label(rec)
        matched = rec.get("matched_intervention")
        keys = _term_keys(matched)
        agent = next((term_to_agent[k] for k in keys if k in term_to_agent), None)
        if agent:
            pooled_agents[trial] = agent
            continue
        if any(k in class_keys for k in keys):
            pooled_agents[trial] = f"CLASS:{matched}"
            continue
        unresolved.append({"trial": trial, "matched_intervention": matched})

    verdict = "NOT_APPLICABLE"
    detail = note
    reason = None
    if unresolved:
        verdict = "UNRESOLVED"
        detail = "included screening records have matched_intervention terms absent from the intervention declaration"
    elif level == "AGENT":
        off_agent = {trial: agent for trial, agent in pooled_agents.items() if agent != identifier_agent}
        if off_agent:
            amendment = _scope_amendment(config or {})
            verdict = "DISCLOSED_SCOPE_AMENDMENT" if amendment else "SINGLE_AGENT_OVER_CLASS_POOL"
            assignments = ", ".join(f"{trial}={agent}" for trial, agent in pooled_agents.items())
            k = len(pooled_agents)
            n = len(off_agent)
            iline = config.get("protocol_i_line") or config.get("_protocol_i_line") or "PICO intervention line not found"
            detail = (
                f"the identifier names {identifier_agent} but the pool is class-level ({assignments}): "
                f"under the identifier {n} of {k} pooled trials are ineligible; under the registered "
                f"protocol ({iline}) the identifier is wrong — this page must not be read as evidence "
                f"about {identifier_agent} alone"
            )
            reason = {"code": "identifier_single_agent_class_pool", "detail": detail}
            if amendment:
                detail = (
                    f"the original identifier names {identifier_agent}, but dated protocol amendment "
                    f"{amendment.get('date')} widens the review to {amendment.get('widened_scope') or iline}. "
                    f"Original scope: {amendment.get('original_scope') or identifier_agent}. "
                    f"Pre-specified list: {amendment.get('pre_specified_list') or 'not stated'}. "
                    f"Pool assignment after amendment: {assignments}. The served slug/URL remains pinned."
                )
                reason = None
        else:
            verdict = "MATCH"
            detail = f"identifier names {identifier_agent}; all included records map to that agent"

    return {
        "level": level,
        "identifier_agent": identifier_agent,
        "pooled_agents": pooled_agents,
        "unresolved": unresolved,
        "verdict": verdict,
        "detail": detail,
        **({"amendment": amendment} if "amendment" in locals() and amendment else {}),
        **({"reason": reason} if reason else {}),
    }
def _trial_name(t):
    pid = str(t.get("id") or t.get("label") or "").replace("PMID ", "").strip()
    known = {"29485925": "SMART", "27749094": "SALT", "26444692": "SPLIT", "34375394": "BaSICS"}
    return known.get(pid) or str(t.get("label") or t.get("id") or pid)


def _unsupported_variance_trials(core):
    out = []
    for o in core.get("outcomes") or []:
        if not _present(o.get("result")):
            continue
        for t in o.get("trials") or []:
            d = t.get("design") or {}
            decision = d.get("design_action") or design_key.decision_for_trial(t)
            if decision.get("action") in design_key.BLOCKING_ACTIONS:
                out.append({"trial": _trial_name(t), "design": d.get("design"), "decision": decision})
    seen, uniq = set(), []
    for item in out:
        key = (item["trial"], item["design"])
        if key not in seen:
            seen.add(key)
            uniq.append(item)
    return uniq


def _eligible_not_pooled(core, id_nct=None):
    """Records screened-in (decision=include) but not pooled in ANY outcome — object-derived. Resolves
    identifiers through id_nct (raw id -> nct) so a trial pooled under one identifier and screened under
    another is not falsely flagged (NAMED_BUT_UNBOUND)."""
    id_nct = id_nct or {}
    pooled = set()
    for o in (core.get("outcomes") or []):
        for t in (o.get("trials") or []):
            fam = t.get("trial_family_id")
            if fam:
                pooled.add(fam)
            rid = _norm_id(t.get("id") or t.get("label"))
            pooled.add(rid)
            if rid in id_nct:
                pooled.add(_norm_id(id_nct[rid]))
    try:
        from .claimgraph import strand_member_keys
        pooled.update(strand_member_keys(core.get("strands") or {}))
    except Exception:
        pass
    out = []
    for r in ((core.get("screening") or {}).get("records") or []):
        if r.get("decision") != "include":
            continue
        if r.get("publication_role") in identity_mod.NON_TRIAL_PUBLICATION_ROLES:
            continue
        fam = r.get("trial_family_id")
        if fam and fam in pooled:
            continue
        nid = _norm_id(r.get("id"))
        if nid and nid in pooled:
            continue
        if nid in id_nct and _norm_id(id_nct[nid]) in pooled:
            continue
        if nid:
            out.append(fam or r.get("id"))
    # stable, de-duplicated
    seen = set()
    return [x for x in out if not (x in seen or seen.add(x))]


def _search_not_executed_from_core(core):
    search = core.get("search") or {}
    retrieval = search.get("retrieval") or {}
    if retrieval.get("enumeration_only"):
        return {
            "class": "PMID_ENUMERATION_explicit",
            "detail": "search.retrieval.enumeration_only=true; no discovery-capable concept source ran",
        }
    rc = search.get("retrieval_class") or {}
    if rc.get("retrieval_auditable") is False:
        return {
            "class": rc.get("class") or "UNAUDITABLE_RETRIEVAL",
            "detail": (
                rc.get("retraction")
                or rc.get("distinction")
                or rc.get("label")
                or "retrieval_class says retrieval_auditable=false"
            ),
        }
    return None


def assess(core, signals=None):
    """signals (optional): externally-computed, committed, per-topic signals the core does not carry
    on its own -- {'search_not_executed': {'class':..., 'detail':...} | None,
    'known_eligible_missing': [ {trial, mechanism, ...}, ... ]}. Passed in (not read here) so assess
    stays a pure function and both build and replay produce the same verdict."""
    signals = signals or {}
    reasons = []
    # 0. Search provenance: a topic whose "search" was a RAN_ERROR-rendered-as-run or explicit
    #    PMID-enumeration has NO genuine executed concept search -- its completeness claim is void.
    sne = signals.get("search_not_executed") or _search_not_executed_from_core(core)
    if sne:
        reasons.append({"code": "search_not_executed",
                        "detail": "no genuine executed concept search (" + str(sne.get("class"))
                                  + "): " + str(sne.get("detail", "known-item retrieval cannot discover "
                                  "an unknown eligible trial"))})
    # 0b. A named eligible trial the audits identified is not in the pool (completeness void, and the
    #     pooled estimate is known-incomplete). Names carried even before external PMID verification.
    kem = [x for x in (signals.get("known_eligible_missing") or [])
           if x.get("status") != "verification_failed"]
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
    # 0d. IDENTIFIER SCOPE: an agent-named slug over a class-level included pool is an eligibility
    #     failure upstream of every downstream gate. The page cannot be renamed, so the object carries
    #     the failure and every surface renders it.
    ids = core.get("identifier_scope") or signals.get("identifier_scope") or {}
    if ids.get("verdict") == "SINGLE_AGENT_OVER_CLASS_POOL":
        reasons.append(ids.get("reason") or {
            "code": "identifier_single_agent_class_pool",
            "detail": ids.get("detail", "identifier names a single agent but the included pool is class-level"),
        })
    elif ids.get("verdict") == "UNRESOLVED":
        unr = ids.get("unresolved") or []
        bits = ", ".join(
            f"{x.get('trial')}={x.get('matched_intervention')}" for x in unr[:6]
        )
        reasons.append({"code": "identifier_scope_unresolved",
                        "detail": "included screening records have unmatched intervention terms in the "
                                  "identifier-scope declaration: " + bits})
    # 0e. A pooled reconstructed non-parallel design has no explicit design adjustment. During the
    # marking-only step this keeps the old number visible but stale, labelled as variance-unsupported.
    unsupported = _unsupported_variance_trials(core)
    if unsupported:
        cc = [x["trial"] for x in unsupported if x["design"] == "CLUSTER_CROSSOVER"]
        if cc:
            detail = (", ".join(cc) + ": cluster-crossover pooled through the parallel-group path; "
                      "precision overstated")
        else:
            detail = (", ".join(x["trial"] for x in unsupported)
                      + ": typed design action still blocks the pooled analysis")
        reasons.append({"code": "pooled_variance_unsupported",
                        "detail": detail + " -- the result rests on a variance that ignores the randomisation unit"})
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
    #     Declared strand pools ARE claims (the claim graph counts them), so a page whose only pooled
    #     numbers are strands is not claim-free -- this consumer must read the same membership the
    #     counter reads, or it contradicts the counter (iv-iron: 4 strand claims vs 'Claims checked: 0').
    _strand_pools = sum(1 for _s in ((core.get("strands") or {}).get("strands") or [])
                        if isinstance(_s, dict) and isinstance(_s.get("pool"), dict) and (_s["pool"].get("k") or 0) >= 1)
    if not any(_present(o.get("result")) for o in (core.get("outcomes") or [])) and _strand_pools == 0:
        reasons.append({"code": "no_checkable_claim",
                        "detail": "no outcome or declared strand produced a pooled claim — the canonical-claim "
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
