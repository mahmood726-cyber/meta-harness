"""Admission of a candidate extraction into a pool -- ONE implementation, read by the build and re-read by the gate.

Until 2026-09-21 the family-eligibility evidence was prepared BEFORE pooling (pipeline.outcome_inputs ->
trial_family.prepare) and never read at the pooling convergence point (target_endpoint.admit_rows checked the
endpoint binding only); the 13-predicate admission verdict was computed AFTER the build, from the built review.json,
by scripts/build_bundle.py, and no harness module read it. The checker described the build; it did not constrain it.
53 of 87 pooled primary rows were INADMISSIBLE on P5 while every page said "existing pooling membership is preserved".

This module is the decision the build acts on. It evaluates, from the objects the build holds at pooling time, the
bundle predicates that those objects can decide -- and NAMES the ones they cannot (SCOPE), so a page's admission
summary states what was checked and what was not. The vocabulary is the bundle's (VERDICTS, predicate ids): one
decision, one vocabulary.

    P5_family_eligible   the trial family's EFFECTIVE eligibility state == ELIGIBLE (trial_family.effective_eligibility:
                         the screen's cell after the attach-time overrides SOURCE_RECORD_DELETED /
                         REGISTRY_PARENT_UNRESOLVED -- the same function attach_review applies, so the state the build
                         decides on is the state the page and the certified families.json carry)
    P8_endpoint_bound    endpoint_binding is a producer binding route other than unbound_legacy. NOTE the divergence
                         from the bundle's string rule (== named_endpoint_resolved_to_definition_span): the producer's
                         hand binder also binds by result_span_enumerates_components and registry_outcome_measure, which
                         the bundle's P8 reads as INADMISSIBLE -- a rule limit raised with the bundle lane (M2 landing
                         message, 2026-09-21), recorded on every such row as bundle_rule_agreement = OTHER_ROUTE, and
                         NOT treated as a refusal in-build. The migration case is the bundle's: P8 the ONLY failing
                         predicate and the binding unbound_legacy -> MIGRATION_STATE_UNBOUND_LEGACY, pooled, counted
                         separately, named on the page.

A row that fails P5 is not pooled and the TRIAL IS NOT ERASED: the candidate extraction is set aside on the outcome
(declared_absent_trials) with the tuple it carried, the family's absence code (UNKNOWN) or the eligibility span
(INELIGIBLE), the verdict object, and the recovery route. Refusing bad extractions must not erase eligible studies.

A build handed no family ledger admits nothing: absence of evidence is not a pass (the gate is on by default).
"""
from __future__ import annotations

from typing import Any

from . import identity
from .trial_family import effective_eligibility

VERDICTS = frozenset({"ADMISSIBLE", "MIGRATION_STATE_UNBOUND_LEGACY", "INADMISSIBLE"})
PASS, FAIL = "PASS", "FAIL"
BOUND_DEFINITION_SPAN = "named_endpoint_resolved_to_definition_span"
UNBOUND_LEGACY = "unbound_legacy"
STATE_NOT_ESTABLISHED = "FAMILY_ELIGIBILITY_NOT_ESTABLISHED"    # P5 by UNKNOWN: a statement about our evidence
STATE_INELIGIBLE = "FAMILY_INELIGIBLE"                          # P5 by INELIGIBLE: a finding with a span
STATE_ENDPOINT_UNBOUND = "ADMISSION_ENDPOINT_UNBOUND"           # P8 only, binding absent (defensive: admit_rows never leaves it absent)
ADMISSION_SET_ASIDE_STATES = (STATE_NOT_ESTABLISHED, STATE_INELIGIBLE, STATE_ENDPOINT_UNBOUND)

SCOPE = {
    "evaluated_in_build": ["P5_family_eligible", "P8_endpoint_bound"],
    "not_evaluated_in_build": ["P1_source_bytes", "P2_span_located", "P3_effect_tokens_in_span", "P4_endpoint_components",
                               "P6_no_unresolved_conflict", "P7_coverage_adequate_for_claim", "P9_span_target_mention",
                               "P10_estimand_evidence", "P11_registered_estimand", "P12_ci_level",
                               "P13_no_extra_components", "P14_missing_components_consistent"],
    "where_the_rest_is_evaluated": "scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, "
                                   "after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them",
    "rule": "final = ADMISSIBLE if no evaluated predicate fails; MIGRATION_STATE_UNBOUND_LEGACY if P8 is the only failing "
            "predicate and the binding is unbound_legacy; INADMISSIBLE otherwise. A row with no family ledger fails P5.",
    "p8_divergence": "in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes "
                     "only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit "
                     "raised with the bundle lane, recorded per row as bundle_rule_agreement)",
}
RECOVERY = ("a reviewer establishes the family's eligibility from held evidence (entry population, randomised contrast, "
            "design) or resolves the registry parent so the structural screen can read it; the candidate tuple then "
            "re-enters admission under the same checks -- never by deleting the trial")


def _families_by_report(family_nodes: list[dict[str, Any]] | None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for f in family_nodes or []:
        for r in f.get("reports") or []:
            out[identity._norm(r.get("report_id"))] = f
    return out


def _family_for(row: dict[str, Any], by_report: dict[str, dict[str, Any]], by_id: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    f = by_report.get(identity._norm(row.get("id")))
    if f is None and row.get("family_id") is not None:
        f = by_id.get(row.get("family_id"))
    return f


def verdict(row: dict[str, Any], family: dict[str, Any] | None) -> dict[str, Any]:
    """The admission verdict object for one candidate row against its family (None = no ledger / no family)."""
    el = effective_eligibility(family) if family else None
    state = (el or {}).get("state")
    p5 = {"state": PASS if state == "ELIGIBLE" else FAIL, "family_id": (family or {}).get("family_id") or row.get("family_id"),
          "eligibility_state": state, "absence_code": (el or {}).get("absence_code"),
          "basis": "trial_family.effective_eligibility on the family ledger the build was handed" if family else
                   "no family ledger / no family for this row: eligibility not evaluated, therefore not established"}
    binding = row.get("endpoint_binding")
    p8 = {"state": PASS if binding and binding != UNBOUND_LEGACY else FAIL, "endpoint_binding": binding,
          "endpoint_admissibility": row.get("endpoint_admissibility"),
          "bundle_rule_agreement": ("BOUND" if binding == BOUND_DEFINITION_SPAN else
                                    "MIGRATION_STATE" if binding == UNBOUND_LEGACY else
                                    "OTHER_ROUTE" if binding else "UNBOUND")}
    predicates = {"P5_family_eligible": p5, "P8_endpoint_bound": p8}
    failing = [k for k, v in predicates.items() if v["state"] != PASS]
    final = ("ADMISSIBLE" if not failing else
             "MIGRATION_STATE_UNBOUND_LEGACY" if failing == ["P8_endpoint_bound"] and binding == UNBOUND_LEGACY else
             "INADMISSIBLE")
    return {"final": final, "failing": failing, "predicates": predicates,
            "evaluated": list(SCOPE["evaluated_in_build"]), "not_evaluated": list(SCOPE["not_evaluated_in_build"])}


_TUPLE_KEYS = ("effect", "ci_low", "ci_high", "scale", "ai", "n1i", "ci", "n2i", "mean1", "sd1", "nc1", "mean2", "sd2", "nc2")


def set_aside_record(row: dict[str, Any], v: dict[str, Any], family: dict[str, Any] | None, outcome_name: str | None) -> dict[str, Any]:
    """The declared-absent record for a row P5 refuses: the trial stays on the outcome with what it carried."""
    p5 = v["predicates"]["P5_family_eligible"]
    ineligible = p5["eligibility_state"] == "INELIGIBLE"
    p5_failed = "P5_family_eligible" in v["failing"]
    el = effective_eligibility(family) if family else {}
    rec = {
        "label": row.get("label"), "id": row.get("id"), "family_id": p5["family_id"],
        # the state names the predicate that failed: P5 (not established / ineligible) or, when the family is
        # eligible and only the endpoint binding is missing, the endpoint vocabulary (lane R finding R8: a P8-only
        # refusal was labelled as a P5 one)
        "absent_kind": "refused_on_evidence" if ineligible else "machine_absent",
        "state": (STATE_INELIGIBLE if ineligible else STATE_NOT_ESTABLISHED) if p5_failed else STATE_ENDPOINT_UNBOUND,
        "reason_code": "P5_family_eligible" if p5_failed else "P8_endpoint_bound",
        "eligibility_state": p5["eligibility_state"], "absence_code": p5["absence_code"],
        "endpoint_binding": row.get("endpoint_binding"), "endpoint_admissibility": row.get("endpoint_admissibility"),
        "endpoint_result_span": row.get("endpoint_result_span"), "held_document": row.get("held_document"),
        "candidate_tuple": {k: row.get(k) for k in _TUPLE_KEYS if row.get(k) is not None},
        "refused_effect": {k: row.get(k) for k in _TUPLE_KEYS if row.get(k) is not None},
        "source": row.get("source", ""), "provenance": row.get("provenance"),
        "admission_verdict": v,
        "reason": (f"endpoint not bound ({row.get('endpoint_binding')!r}) with family eligibility established: the candidate "
                   f"extraction is set aside (P8_endpoint_bound FAIL) for {outcome_name!r}" if not p5_failed else
                   f"family eligibility {p5['eligibility_state']}"
                   + (f" ({p5['absence_code']})" if p5.get("absence_code") else "")
                   + f" for {outcome_name!r}: the candidate extraction is set aside (P5_family_eligible FAIL); the trial "
                     "stays on this outcome as evidence whose eligibility the held record does not establish"
                   if not ineligible else
                   f"family INELIGIBLE on held evidence for {outcome_name!r}: the candidate extraction is refused "
                   "(P5_family_eligible FAIL) with the span that establishes ineligibility"),
        "recovery": RECOVERY,
    }
    if ineligible:
        rec["eligibility_span"] = el.get("span")
    return rec


def admit(rows: list[dict[str, Any]], family_nodes: list[dict[str, Any]] | None, spec: dict[str, Any]):
    """Stamp every candidate row with its verdict (row key admission_verdict -- `admission` is the eligibility chain's
    per-dimension record on opted-in topics); return (kept, set_aside). INADMISSIBLE rows are set aside as
    declared-absent records; ADMISSIBLE and MIGRATION_STATE rows are kept (pooled)."""
    by_report = _families_by_report(family_nodes)
    by_id = {f.get("family_id"): f for f in family_nodes or [] if isinstance(f, dict)}
    kept, aside = [], []
    for t in rows:
        fam = _family_for(t, by_report, by_id)
        v = verdict(t, fam)
        t["admission_verdict"] = v
        if fam is not None and t.get("family_id") is None:
            t["family_id"] = fam.get("family_id")
        if v["final"] == "INADMISSIBLE":
            aside.append(set_aside_record(t, v, fam, spec.get("name")))
        else:
            kept.append(t)
    return kept, aside


def is_set_aside(row: dict[str, Any] | None) -> bool:
    """True for a declared-absent row the BUILD set aside on admission (the one predicate every re-pool route asks)."""
    return isinstance(row, dict) and row.get("state") in ADMISSION_SET_ASIDE_STATES and isinstance(row.get("admission_verdict"), dict)


def _strand_member_family(m: dict[str, Any], by_report: dict[str, dict[str, Any]], by_id: dict[str, dict[str, Any]]):
    for k in ("id", "pmid", "nct", "label", "trial"):
        f = by_report.get(identity._norm(m.get(k))) if m.get(k) else None
        if f is not None:
            return f
    return by_id.get(m.get("family_id")) if m.get("family_id") else None


def admit_strands(doc: dict[str, Any] | None, family_nodes: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Admission of a declared strand's members (a strand is a saved, hand-declared pool -- docs/*_strands.json --
    attached to the page with its saved result). Every member is stamped; a strand with an INADMISSIBLE member is
    marked admission_refused and its saved result must not render (lane R finding R4, 2026-09-21: saved strands
    escaped admission). A member with no family fails P5 like any other row. Returns the counts."""
    if not isinstance(doc, dict):
        return {"strands": 0, "refused": 0}
    by_report = _families_by_report(family_nodes)
    by_id = {f.get("family_id"): f for f in family_nodes or [] if isinstance(f, dict)}
    refused = 0
    for s in doc.get("strands") or []:
        bad = []
        for m in s.get("members") or []:
            if not isinstance(m, dict):
                continue
            fam = _strand_member_family(m, by_report, by_id)
            row = dict(m)
            row.setdefault("endpoint_binding", m.get("endpoint_binding") or "strand_member_declared")
            v = verdict(row, fam)
            m["admission_verdict"] = v
            if fam is not None:
                m["family_id"] = fam.get("family_id")
            if v["final"] == "INADMISSIBLE":
                p5 = v["predicates"]["P5_family_eligible"]
                bad.append(f"{m.get('trial') or m.get('pmid') or m.get('nct')}: {', '.join(v['failing'])}"
                           + (f" (family {p5['family_id']}, eligibility {p5['eligibility_state']}"
                              + (f" {p5['absence_code']}" if p5.get("absence_code") else "") + ")" if fam is not None else " (no family)"))
        if bad:
            refused += 1
            s["admission_refused"] = {"members": bad, "scope": list(SCOPE["evaluated_in_build"]),
                                      "reason": "a declared strand pools only admitted members; its saved result is withheld until every "
                                                "member's family eligibility is established (recovery as for any set-aside row)"}
        else:
            s.pop("admission_refused", None)
    return {"strands": len(doc.get("strands") or []), "refused": refused}


def summary(outcome: dict[str, Any]) -> dict[str, Any]:
    """What the build decided on this outcome, with its scope. A pool that carries no stamped row reads
    NOT_EVALUATED (a zero is 'not observed', never 'safe'); the migration rows are named."""
    pooled = [t for t in outcome.get("trials") or [] if isinstance(t, dict)]
    aside = [a for a in outcome.get("declared_absent_trials") or [] if isinstance(a, dict) and a.get("state") in ADMISSION_SET_ASIDE_STATES]
    stamped = [t for t in pooled if isinstance(t.get("admission_verdict"), dict)]
    unstamped = [str(t.get("id")) for t in pooled if not isinstance(t.get("admission_verdict"), dict)]
    finals = {str(t.get("id")): t["admission_verdict"].get("final") for t in stamped}
    # three states, each named: EVALUATED (every pooled row stamped), NOT_EVALUATED (a pooled row without a verdict:
    # a page built before the build read the decision), NO_CANDIDATE_ROWS (nothing reached admission -- not a zero
    # of anything)
    state = ("NOT_EVALUATED" if unstamped else "EVALUATED" if (stamped or aside) else "NO_CANDIDATE_ROWS")
    return {
        "state": state,
        "rule": SCOPE["rule"],
        "evaluated_in_build": list(SCOPE["evaluated_in_build"]),
        "not_evaluated_in_build": list(SCOPE["not_evaluated_in_build"]),
        "where_the_rest_is_evaluated": SCOPE["where_the_rest_is_evaluated"],
        "p8_divergence": SCOPE["p8_divergence"],
        "pooled_rows": len(pooled),
        "admissible_rows": sorted(i for i, f in finals.items() if f == "ADMISSIBLE"),
        "migration_state_rows": sorted(i for i, f in finals.items() if f == "MIGRATION_STATE_UNBOUND_LEGACY"),
        "other_route_rows": sorted(str(t.get("id")) for t in stamped
                                   if t["admission_verdict"]["predicates"]["P8_endpoint_bound"].get("bundle_rule_agreement") == "OTHER_ROUTE"),
        "set_aside_rows": [{"id": str(a.get("id")), "state": a.get("state"), "eligibility_state": a.get("eligibility_state"),
                            "absence_code": a.get("absence_code")} for a in aside],
        "unstamped_rows": unstamped,
        "pooled_with_a_verdict_other_than_admissible_or_migration": sorted(i for i, f in finals.items()
                                                                          if f not in ("ADMISSIBLE", "MIGRATION_STATE_UNBOUND_LEGACY")),
    }


def describe(s: dict[str, Any]) -> str:
    """The summary as the sentence the page and the census print -- limits first."""
    ev = ", ".join(s["evaluated_in_build"])
    nev = ", ".join(s["not_evaluated_in_build"])
    if s["state"] == "NO_CANDIDATE_ROWS":
        return (f"Admission: no candidate row reached this outcome's pool (nothing pooled, nothing set aside on P5); "
                f"in-build scope is {ev}; {nev} are evaluated only by the bundle ({s['where_the_rest_is_evaluated']}).")
    if s["state"] == "NOT_EVALUATED":
        return (f"Admission NOT EVALUATED on this outcome: {s['pooled_rows']} pooled row(s), "
                f"{len(s['unstamped_rows'])} without a verdict ({', '.join(s['unstamped_rows']) or 'none'}); "
                f"a page built before the build read the admission decision. In-build scope would be {ev}; "
                f"{nev} are evaluated only by the bundle ({s['where_the_rest_is_evaluated']}).")
    bad = s.get("pooled_with_a_verdict_other_than_admissible_or_migration") or []
    return ((f"REFUSAL: {len(bad)} pooled row(s) carry a verdict that does not admit them [{', '.join(bad)}]. " if bad else "")
            + f"Admission evaluated in-build on {ev} only ({nev} are not evaluated here: {s['where_the_rest_is_evaluated']}). "
            f"Pooled {s['pooled_rows']}: admissible {len(s['admissible_rows'])}; migration state (unbound_legacy, pooled and "
            f"counted separately) {len(s['migration_state_rows'])}"
            + (f" [{', '.join(s['migration_state_rows'])}]" if s["migration_state_rows"] else "")
            + f"; bound by a producer route the bundle's P8 does not name {len(s['other_route_rows'])}"
            + (f" [{', '.join(s['other_route_rows'])}]" if s["other_route_rows"] else "")
            + f". Set aside on P5 (family eligibility) {len(s['set_aside_rows'])}"
            + (": " + "; ".join(f"{a['id']} {a['eligibility_state']}" + (f" ({a['absence_code']})" if a.get("absence_code") else "")
                                for a in s["set_aside_rows"]) if s["set_aside_rows"] else "")
            + ". " + s["p8_divergence"] + ".")
