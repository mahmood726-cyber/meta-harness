"""ONE adjudicated screening record per report, and everything that talks about screening DERIVED from it.

External review of colchicine-postop-af (2026-09-26): the COPPS AF substudy (PMID 22090167) was "screened in" in the
page narrative, excluded X1 "not a randomized controlled trial" in the ledger (while its own span listed the publication
type Randomized Controlled Trial), listed in its trial family, and recommended for inclusion by the adjudicator -- four
statements about one report, from four independent writers, none checked against another.

The record (built by harness.screen._link_and_record) carries three decisions:
  parent_eligibility   ELIGIBLE / INELIGIBLE / NOT_ASSESSED
  report_relevance     PRIMARY_REPORT / SECONDARY_REPORT (linked to its parent family) / NO_RESULTS_REPORT /
                       COMPANION_REPORT
  result_admissibility per outcome: POOLED / DECLARED_ABSENT(code) / NOT_IN_OUTCOME (filled here, after outcomes)
and the ledger decision/rule SET from it. This module fills admissibility, copies the record onto the family object's
report entry, derives the screening narrative, and CHECKS that ledger, family object, narrative and record agree.
"""
from __future__ import annotations

import re
from typing import Any

BLOCKING = ("LEDGER_VS_RECORD", "FAMILY_VS_RECORD", "NARRATIVE_VS_LEDGER", "REASON_VS_SPAN", "FAMILY_VS_LEDGER",
            "OMISSION_VS_RECORD", "OMISSION_VS_PROTOCOL", "FAMILY_DOUBLE_COUNT", "FAMILY_TIMEPOINT_UNLABELLED",
            "STATUS_VS_EXTRACTION", "STATUS_MISSING", "REPORT_TRIAL_UNLINKED", "COMBINED_POPULATION_IMPORTED")
ADVISORY = ("ADJUDICATOR_VS_LEDGER",)
_PMID = re.compile(r"(?<![\d.])(\d{7,8})(?![\d.])")
_SCREENED_IN = re.compile(r"screened[\s-]+in\b", re.I)
_SCREENED_OUT = re.compile(r"\bscreened[\s-]+out\b|\bexcluded at screening\b", re.I)


def _rid(x) -> str:
    """'ACRONYM · 12345678' / 'PMID 12345678' / '12345678' -> '12345678'."""
    s = str(x or "")
    if "·" in s:
        s = s.split("·")[-1]
    return s.replace("PMID", "").strip()


def _rows(review):
    return ((review or {}).get("screening") or {}).get("records") or []


# ------------------------------------------------------------------------------------------------ derivation
def fill_admissibility(review: dict[str, Any]) -> None:
    """Decision 3, per outcome, from the built outcomes: POOLED, DECLARED_ABSENT (with its code), or NOT_IN_OUTCOME."""
    per = {}
    for o in review.get("outcomes") or []:
        name = o.get("name")
        for t in o.get("trials") or []:
            per.setdefault(_rid(t.get("id")), {})[name] = {"state": "POOLED"}
        for a in o.get("declared_absent_trials") or []:
            per.setdefault(_rid(a.get("id")), {})[name] = {
                "state": "DECLARED_ABSENT", "code": a.get("reason_code") or a.get("state") or a.get("absent_kind"),
                "reason": (a.get("reason") or "")[:400]}
    # an internally-inconsistent held source marks ONLY its scoped endpoints (the whole document when unscoped)
    from .invalidation import SOURCE_INTERNALLY_INCONSISTENT, inconsistency_scope, missing_state
    names = [o.get("name") for o in review.get("outcomes") or []]
    for fact in review.get("held_regulatory_facts") or []:
        if missing_state(fact) != SOURCE_INTERNALLY_INCONSISTENT:
            continue
        rid = _rid(fact.get("trial_key") or fact.get("trial"))
        for name in (inconsistency_scope(fact) or names):
            per.setdefault(rid, {})[name] = {"state": SOURCE_INTERNALLY_INCONSISTENT,
                                             "spans": sorted(s.get("kind") for s in fact.get("spans") or [])}
    for r in _rows(review):
        sr = r.get("screening_record")
        if not sr:
            continue
        if r.get("decision") != "include":
            sr["result_admissibility"] = {"state": "NOT_ASSESSED", "basis": "not screened in for pooling"}
            continue
        outs = per.get(_rid(r.get("id")), {})
        sr["result_admissibility"] = {"state": "ASSESSED",
                                      "per_outcome": {o.get("name"): outs.get(o.get("name"), {"state": "NOT_IN_OUTCOME"})
                                                      for o in review.get("outcomes") or []}}


def _summary(sr):
    return {k: sr.get(k) for k in ("report_id", "parent_family", "ledger_decision", "ledger_rule")} | {
        "parent_eligibility": (sr.get("parent_eligibility") or {}).get("state"),
        "report_relevance": (sr.get("report_relevance") or {}).get("state"),
        **({"linked_to": sr["report_relevance"]["linked_to"]} if (sr.get("report_relevance") or {}).get("linked_to") else {})}


def attach_to_families(review: dict[str, Any]) -> None:
    """The family object's report entry carries the SAME record summary (derived, never re-decided)."""
    by_id = {_rid(r.get("id")): r["screening_record"] for r in _rows(review) if r.get("screening_record")}
    for fam in review.get("trial_families") or []:
        for rep in fam.get("reports") or []:
            sr = by_id.get(_rid(rep.get("report_id")))
            if sr:
                rep["screening_record"] = _summary(sr)


def derive_narrative(review: dict[str, Any]) -> list[str]:
    """Sentences about secondary / linked reports, generated from their records only."""
    primary = next((o for o in review.get("outcomes") or [] if o.get("primary")), {}) or {}
    out = []
    for r in _rows(review):
        sr = r.get("screening_record") or {}
        rel = sr.get("report_relevance") or {}
        if rel.get("state") != "SECONDARY_REPORT":
            continue
        rid, fam = sr.get("report_id"), sr.get("parent_family") or "its parent trial"
        if sr.get("ledger_decision") == "include":
            adm = ((sr.get("result_admissibility") or {}).get("per_outcome") or {}).get(primary.get("name")) or {}
            tail = {"POOLED": "it is pooled in the primary outcome",
                    "DECLARED_ABSENT": f"for the primary outcome it is declared absent ({adm.get('code')})",
                    }.get(adm.get("state"), "it is not in the primary outcome")
            out.append(f"PMID {rid} is screened in as a secondary report of {fam} (parent trial eligible); {tail}.")
        elif sr.get("ledger_rule") == "X-LINKED":
            out.append(f"PMID {rid} is a secondary report of {fam}, linked to report {rel.get('linked_to')}; "
                       "the trial is counted once.")
    review["screening_narrative"] = out
    return out


def derive(review: dict[str, Any]) -> None:
    fill_admissibility(review)
    attach_to_families(review)
    derive_narrative(review)


# ------------------------------------------------------------------------------------------------ the check
def _prose(review):
    """Every free-text field that states a screening decision about a named report."""
    items = [("evidence_base_caveat", review.get("evidence_base_caveat")),
             ("comparator_scope_note", review.get("comparator_scope_note")),
             ("reproduction.parity.reason", ((review.get("reproduction") or {}).get("parity") or {}).get("reason"))]
    items += [("screening_narrative", s) for s in review.get("screening_narrative") or []]
    return [(k, v) for k, v in items if isinstance(v, str) and v]


# An omission reason that says the POPULATION is wrong: "population is ACUTE ... pericarditis, NOT the recurrent ..."
_POP_OMISSION = re.compile(r"population (?:is|was|:)\s*(?P<pop>[^,;.]{3,90}?)\s*(?:,\s*)?(?:NOT|not)\b"
                           r"|wrong population[:\s]+(?P<pop2>[^,;.]{3,90})", re.S)


def _omission_statements(review):
    """(report id, field, text) for every statement the page makes about why a report is left out."""
    rows = {_rid(r.get("id")): r for r in _rows(review)}
    acronym = {}
    for r in _rows(review):
        rid = str(r.get("id") or "")
        if "·" in rid:
            acronym[rid.split("·")[0].strip().lower()] = _rid(rid)
    out = []
    for o in review.get("outcomes") or []:
        for a in o.get("declared_absent_trials") or []:
            out.append((_rid(a.get("id")), f"declared_absent[{o.get('name')}]", a.get("reason") or ""))
        for km in ((o.get("known_missing_sensitivity") or {}).get("rows") or []):
            key = str(km.get("trial_key") or km.get("name") or "")
            rid = _rid(key) if _rid(key) in rows else acronym.get(key.strip().lower())
            text = " ".join(str(km.get(k) or "") for k in ("why_eligible", "note", "verify_basis"))
            if not rid:
                named = sorted({i for i in _PMID.findall(text) if i in rows})
                rid = named[0] if len(named) == 1 else None      # the row's own text names exactly one screened report
            if rid:
                out.append((rid, "known_missing_sensitivity", text))
    return out


def _population_omission(text):
    m = _POP_OMISSION.search(text or "")
    return (m.group("pop") or m.group("pop2") or "").strip() if m else None


def consistency_problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    """Every disagreement between ledger, record, family object, narrative and adjudicator about one report.
    Kinds in BLOCKING fail the gate; ADJUDICATOR_VS_LEDGER is a recorded open question (advisory)."""
    probs = []
    rows = {_rid(r.get("id")): r for r in _rows(review)}

    def add(kind, rid, detail):
        probs.append({"kind": kind, "report_id": rid, "blocking": kind in BLOCKING, "detail": detail})

    for rid, r in rows.items():
        sr = r.get("screening_record")
        if sr and (r.get("decision"), r.get("rule_id")) != (sr.get("ledger_decision"), sr.get("ledger_rule")):
            add("LEDGER_VS_RECORD", rid, f"ledger {r.get('decision')}/{r.get('rule_id')} vs record "
                                         f"{sr.get('ledger_decision')}/{sr.get('ledger_rule')}")
        if (r.get("rule_id") == "X1" and "not a randomized controlled trial" in (r.get("reason") or "")
                and "randomized controlled trial" in (r.get("span") or "").lower()):
            add("REASON_VS_SPAN", rid, "X1 'not a randomized controlled trial' beside its own span listing the "
                                       "publication type Randomized Controlled Trial")
        rec_dec = r.get("adjudicator_recommended_decision")
        if rec_dec and rec_dec != r.get("decision"):
            add("ADJUDICATOR_VS_LEDGER", rid, f"adjudicator recommends {rec_dec}; ledger {r.get('decision')}/{r.get('rule_id')}")

    for fam in review.get("trial_families") or []:
        for rep in fam.get("reports") or []:
            rid = _rid(rep.get("report_id"))
            r = rows.get(rid)
            if not r:
                continue
            sr = r.get("screening_record")
            fsr = rep.get("screening_record")
            if sr:
                if fsr is None or fsr != _summary(sr):
                    add("FAMILY_VS_RECORD", rid, f"family {fam.get('family_id')} report entry {fsr} vs record {_summary(sr)}")
                if sr.get("parent_family") and fam.get("family_id") != sr.get("parent_family"):
                    add("FAMILY_VS_RECORD", rid, f"listed under family {fam.get('family_id')}, screened as a report of "
                                                 f"{sr.get('parent_family')}")
            elif (r.get("rule_id") == "X1" and "not a randomized controlled trial" in (r.get("reason") or "")
                  and str(rep.get("role") or "").upper() in ("PRIMARY", "SUBGROUP", "SECONDARY_ANALYSIS")
                  and str(fam.get("family_id") or "").startswith("NCT")):
                add("FAMILY_VS_LEDGER", rid, f"family {fam.get('family_id')} lists it as a {rep.get('role')} report of a "
                                             "registered trial; the ledger rejects it as not an RCT")

    # OMISSION reasons belong to the same record: a report whose record says its parent trial is ELIGIBLE may not be
    # explained anywhere on the page as left out for its POPULATION, and a population refusal must not name a
    # population the protocol's own include rules admit (ICAP, colchicine-recurrent-pericarditis: "population is ACUTE
    # (first-episode) pericarditis, NOT the recurrent-pericarditis population" against a protocol that includes acute
    # first episodes -- beside a caveat saying ICAP is eligible and not refused for population).
    inc = _protocol_include(review)
    for rid, field, text in _omission_statements(review):
        pop = _population_omission(text)
        if not pop or rid not in rows:
            continue
        sr = rows[rid].get("screening_record") or {}
        if (sr.get("parent_eligibility") or {}).get("state") == "ELIGIBLE" or rows[rid].get("decision") == "include":
            add("OMISSION_VS_RECORD", rid, f"{field}: omitted for population '{pop}', but the screening record says the "
                                           f"parent trial is eligible ({rows[rid].get('decision')}/{rows[rid].get('rule_id')})")
        if inc and _in_protocol_population(pop, inc):
            add("OMISSION_VS_PROTOCOL", rid, f"{field}: refused for population '{pop}', which the protocol's include rules "
                                             f"admit (population_any {inc.get('population_any')})")
    for field, text in _prose(review):
        for sent in re.split(r"(?<=[.;])\s+", text):
            ids = [i for i in _PMID.findall(sent) if i in rows]
            if not ids:
                continue
            says_in, says_out = bool(_SCREENED_IN.search(sent)), bool(_SCREENED_OUT.search(sent))
            for rid in ids:
                dec = rows[rid].get("decision")
                if says_in and dec != "include":
                    add("NARRATIVE_VS_LEDGER", rid, f"{field}: '{sent.strip()[:160]}' vs ledger {dec}/{rows[rid].get('rule_id')}")
                if says_out and dec == "include":
                    add("NARRATIVE_VS_LEDGER", rid, f"{field}: '{sent.strip()[:160]}' vs ledger include")
    # REPORT FAMILIES (several reports of one trial): one trial, and a verdict on a non-timepoint report says so
    from . import report_family
    for p in report_family.problems(review):
        add(p["kind"], p["report_id"], p["detail"])
    # MULTI-TRIAL REPORTS: an article linked to every registration it reports; a combined analysis never imported
    from . import multi_trial_report
    for p in multi_trial_report.problems(review):
        add(p["kind"], p["report_id"], p["detail"])
    # RESULT STATUS: the page's words about a trial's result agree with its derived state
    from . import result_status
    if any(o.get("trials") or o.get("declared_absent_trials") for o in review.get("outcomes") or []) and \
            any("result_status" in t for o in review.get("outcomes") or []
                for t in (o.get("trials") or []) + (o.get("declared_absent_trials") or [])):
        for p in result_status.problems(review):
            add(p["kind"], p["report_id"], p["detail"])
    return probs


def _protocol_include(review):
    """The protocol's stated scope: the include rules the screen enforces, stamped on the review at build time
    (screening.protocol_include); for a review built before that stamp, the topic config the screen reads."""
    inc = (review.get("screening") or {}).get("protocol_include")
    if inc:
        return inc
    import json, os
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "topics", f"{review.get('slug')}.json")
    try:
        return json.load(open(p, encoding="utf-8")).get("include") or {}
    except (OSError, ValueError):
        return {}


def _in_protocol_population(pop: str, inc: dict) -> bool:
    """The population named in a refusal is inside the protocol's stated scope: it matches population_any and no
    population_none term (the same matcher the screen uses)."""
    from . import screen
    any_terms = list(inc.get("population_any") or []) + list(inc.get("population_any_extra") or [])
    return bool(any_terms and screen._has(pop.lower(), any_terms) and not screen._has(pop.lower(), inc.get("population_none")))


def gate_reasons(review: dict[str, Any]) -> list[str]:
    return [f"SCREENING_RECORD_INCONSISTENT {p['kind']} {p['report_id']}: {p['detail']}"
            for p in consistency_problems(review) if p["blocking"]]
