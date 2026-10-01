"""Held typed rows: no ABSENT state may stand while a matching typed row is held.

The defect it closes (CAP- and COVID-corticosteroid reviews): absence was decided from ONE text -- usually the abstract -- while
the same trial's held full text carried the value in a table (ESCAPe, Table 2 'Hospital mortality' 34/291 vs 28/281), or another
extraction in the SAME review had already quoted the sentence that carries it (COVID STEROID: the harms extraction quotes
'mortality was 6/16 vs 2/14' while mortality is certified absent).

The invariant, identical for every trial and every absence state:
  * the evidence searched is EVERY held text for the trial -- abstract, cached full text and its tables, registry text -- plus every
    span any extraction in the same review quotes for that trial;
  * a 'matching typed row' is a typed identity (harness.evidence_identity) that names the outcome with its own definition (not a
    residual 'other ...' or restricted subset), at a fitting timepoint, as an outcome count or effect -- measure, comparison and
    population may still differ (they decide ADMISSION, not presence);
  * an absence state with a matching typed row is refused; the row becomes extraction debt carrying the held row, never a value
    admitted automatically.
Counts carried by a held row use OUTCOME-ASCERTAINED denominators (34/291, not 34/297) and carry the missing count; a patient whose
outcome is missing is never counted as a survivor. A trial whose held text reports a non-target subpopulation (ESCAPe: 34% met HCAP
criteria) is flagged for eligibility adjudication rather than admitted.
"""
from __future__ import annotations

import re
from typing import Any

from . import evidence_identity, reason_audit

ABSENT_CODES = ("OUTCOME_NOT_IN_SOURCE", "SOURCE_NOT_RETRIEVED", "outcome_not_reported")
KNOWN_MISSING_ABSENT = "NOT_IN_COMMITTED_SOURCE"
REFUSED_AS = "KNOWN_REPORTED_NOT_YET_EXTRACTED"
# mismatches that decide whether a held row is ABOUT this outcome; the others (measure, comparison, population, design) decide
# whether it can be ADMITTED, which is a separate question
_PRESENCE_FIELDS = ("role", "outcome", "part", "timepoint", "definition")
_EXTRACTION_FIELDS = ("source", "source_span", "verbatim_span", "harm_source_span", "span")
_WORD_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
             "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
             "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
             "eighty": 80, "ninety": 90}
_SUBPOP = re.compile(r"\b((?:\d+(?:\.\d+)?)|(?:[a-z]+(?:-[a-z]+)?))\s*(?:%|percent)\s+of\s+(?:the\s+)?(?:participants|patients|subjects|"
                     r"enrolled patients)\s+(?:met|fulfilled|had)\s+(?:the\s+)?(?:criteria\s+for\s+)?([A-Za-z][\w-]*(?:\s+[\w-]+){0,3}?)"
                     r"\s+criteria\b", re.I)


def _pct(token: str) -> float | None:
    t = token.lower()
    if re.fullmatch(r"\d+(?:\.\d+)?", t):
        return float(t)
    parts = t.split("-")
    if all(p in _WORD_NUM for p in parts):
        return float(sum(_WORD_NUM[p] for p in parts))
    return None


def review_texts(review: dict[str, Any], trial: str) -> list[dict[str, str]]:
    """Every span any extraction in this review quotes for this trial -- held text the review itself has already read."""
    out, seen = [], set()
    for o in review.get("outcomes") or []:
        rows = list(o.get("trials") or []) + list(o.get("declared_absent_trials") or [])
        rows += list(((o.get("result") or {}).get("harm_reporting_trials")) or [])
        for r in rows:
            if not isinstance(r, dict) or reason_audit.canonical_trial_id(r.get("id") or r.get("label") or r.get("trial")) != trial:
                continue
            for f in _EXTRACTION_FIELDS:
                s = r.get(f)
                if isinstance(s, str) and len(s) > 20 and s not in seen:
                    seen.add(s)
                    out.append({"source_id": f"extraction:{o.get('name')}:{f}", "source_kind": "extraction", "text": s})
    return out


def matching_rows(outcome: dict[str, Any], trial: str, sources: list[dict[str, Any]], spec: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Typed rows in these held texts that are ABOUT this outcome (presence fields all fit), most complete first."""
    cands = reason_audit.typed_candidates(outcome, {"id": trial}, sources, spec)
    hits = [c for c in cands if not [m for m in c["mismatch"] if m.split(":", 1)[0] in _PRESENCE_FIELDS]]
    # contradicting a SERVED absence needs the outcome's OWN name; a keyword-only match is left for a reader (possibly held)
    return [c for c in hits if c.get("role") in ("OUTCOME_COUNT", "EFFECT_ESTIMATE")
            and evidence_identity.names_the_outcome(c.get("label") or c["span"], outcome.get("name") or "")]


def subpopulation_flags(sources: list[dict[str, Any]], target_terms: list[str]) -> list[dict[str, Any]]:
    """'34% of participants met HCAP criteria': a stated share of a population the target does not name -> adjudicate eligibility."""
    flags, terms = [], [t.lower() for t in target_terms or []]
    for src in sources or []:
        for m in _SUBPOP.finditer(src.get("text") or ""):
            share, pop = _pct(m.group(1)), m.group(2).strip()
            if share is None or share <= 0 or any(t in pop.lower() or pop.lower() in t for t in terms):
                continue
            flags.append({"flag": "ELIGIBILITY_ADJUDICATION_REQUIRED", "subpopulation": pop, "share_percent": share,
                          "source_id": src.get("source_id"), "span": m.group(0)})
    return flags


def _count(v: Any) -> int | None:
    """A plain non-negative integer count ('1,234' allowed), else None -- never a number guessed from text."""
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v if v >= 0 else None
    t = str(v or "").replace(",", "").strip()
    return int(t) if t.isdigit() else None


def ascertained_counts(row: dict[str, Any]) -> dict[str, Any] | None:
    """Per-arm counts on OUTCOME-ASCERTAINED denominators, with the missing count carried. Never events = N_randomised - survivors."""
    arms = row.get("arms") or []
    if len(arms) != 2 or any(a.get("events") is None or (a.get("n") is None and a.get("n_group") is None) for a in arms):
        return None
    out = []
    if row.get("unit") == "CYCLES":                   # a cycle denominator is cycles, never outcome-ascertained participants
        return {"arms": [{"arm": a.get("arm"), "events": a.get("events"), "n_cycles": a.get("n"), "n_group": a.get("n_group"),
                          "n_ascertained": None, "missing": None, "non_events": None,
                          "denominator_basis": "CYCLES_NOT_PARTICIPANTS"} for a in arms],
                "unit": "CYCLES", "window": row.get("window"), "rule": "cycles are never independent participants"}
    for a in arms:
        grp, n, ev = _count(a.get("n_group")), _count(a.get("n")), _count(a.get("events"))
        if a.get("n") is not None and (n is None or ev is None or ev > n):
            out.append({"arm": a.get("arm"), "events": a.get("events"), "n_ascertained": None, "n_group": a.get("n_group"),
                        "missing": None, "non_events": None,
                        "denominator_basis": "NOT_ASCERTAINABLE: count or denominator is not a plain integer (or events > n)"})
            continue
        if n is None:          # events only, beside the arm's GROUP size: ascertainment is not stated, so no denominator is inferred
            out.append({"arm": a.get("arm"), "events": a["events"], "n_ascertained": None, "n_group": grp, "missing": None,
                        "non_events": None, "denominator_basis": "ANALYSIS_GROUP_ONLY: outcome ascertainment not stated"})
            continue
        out.append({"arm": a.get("arm"), "events": a["events"], "n_ascertained": n, "n_group": grp,
                    "missing": (grp - n) if grp is not None and grp >= n else None, "non_events": n - ev,
                    "denominator_basis": "OUTCOME_ASCERTAINED"})
    return {"arms": out, "window": row.get("window"),   # the safety window travels with the counts; never efficacy follow-up
            "rule": "denominator = outcome-ascertained n; missing carried, never counted as a non-event"}


_REGISTRY_ID = re.compile(r"^(?:NCT\d{8}|ISRCTN\d+|ACTRN\d+|ChiCTR[\w-]+|EUCTR[\w-]+|IRCT\w+|CTRI/[\w/]+|DRKS\d+|JPRN-\w+)$", re.I)


def _all_sources(slug, review, sources_by_trial, trial):
    """Held text for a trial: its own records, what other extractions in the review quote for it, and -- for a REGISTRY id -- every
    held report whose text states that registry number (a publication naming NCT01709981 is a report of that trial, even when the
    family record never linked it; independent codex sweep B4)."""
    out = list(sources_by_trial.get(trial, [])) + review_texts(review, trial)
    if _REGISTRY_ID.match(trial or ""):
        for other, srcs in sources_by_trial.items():
            if other != trial and any(trial.lower() in (s.get("text") or "").lower() for s in srcs):
                out += [dict(s, source_id=f"{s.get('source_id')} (names {trial})") for s in srcs]
    return out


def contradictions(slug: str, review: dict[str, Any], sources_by_trial: dict[str, list], specs: dict[str, Any],
                   target_population_terms: list[str] | None = None) -> list[dict[str, Any]]:
    """Every absence state in this review that a held typed row contradicts. Enumerates its population by KIND."""
    out = []
    for o in review.get("outcomes") or []:
        spec = specs.get(o.get("name")) or {}
        states = [("declared_absent", r, r.get("reason_code")) for r in o.get("declared_absent_trials") or []
                  if r.get("reason_code") in ABSENT_CODES]
        states += [("known_missing", r, r.get("value_status")) for r in (o.get("known_missing_sensitivity") or {}).get("rows") or []
                   if r.get("value_status") == KNOWN_MISSING_ABSENT]
        for kind, r, state in states:
            trial = reason_audit.canonical_trial_id(r.get("id") or r.get("label") or r.get("trial_key"))
            srcs = _all_sources(slug, review, sources_by_trial, trial)
            hits = matching_rows(o, trial, srcs, spec)
            rec = {"slug": slug, "outcome": o.get("name"), "trial": trial, "kind": kind, "state": state, "contradicted": bool(hits)}
            if hits:
                best = hits[0]
                rec.update(held_row={"source_id": best["source_id"], "span": best["span"], "kind": best.get("kind"),
                                     "timepoint": best.get("timepoint"), "mismatch_for_admission": best["mismatch"]},
                           counts=ascertained_counts(best),
                           cross_extraction=best["source_id"].startswith("extraction:"),
                           eligibility=subpopulation_flags(srcs, target_population_terms or []))
            out.append(rec)
    return out


def enforce(slug: str, review: dict[str, Any], sources_by_trial: dict[str, list], specs: dict[str, Any]) -> list[dict[str, Any]]:
    """The producer step: every declared-absent row a held typed row contradicts stops being an absence. Its reason code becomes
    extraction debt carrying the held row (and the absence it replaced); membership and the pool are unchanged, and nothing is
    admitted -- the held row is recorded for extraction, with its ascertained counts and any eligibility flag."""
    changed = []
    found = contradictions(slug, review, sources_by_trial, specs, [review.get("question") or ""])
    by_name = {o.get("name"): o for o in review.get("outcomes") or []}
    for c in found:
        if not c["contradicted"] or c["kind"] != "declared_absent":
            continue
        row = next(r for r in by_name[c["outcome"]].get("declared_absent_trials") or []
                   if reason_audit.canonical_trial_id(r.get("id") or r.get("label")) == c["trial"])
        held = c["held_row"]
        row["absence_refused"] = {"was": row.get("reason_code"), "held_row": held, "counts_ascertained": c["counts"],
                                  "cross_extraction": c["cross_extraction"], "eligibility": c["eligibility"],
                                  "rule": "no absent state stands while a matching typed row is held (harness.held_rows)"}
        row["extraction_debt"] = {"source_id": held["source_id"], "span": held["span"], "counts_ascertained": c["counts"]}
        row["reason_code"] = REFUSED_AS
        row["reason"] = (f"a matching typed row is held ({held['source_id']}): {held['span'][:160]} -- recorded as extraction debt, "
                         f"not as absence")
        changed.append({k: c[k] for k in ("outcome", "trial", "state")} | {"source_id": held["source_id"]})
    review["held_row_invariant"] = {
        "absence_states": len(found), "contradicted": sum(1 for c in found if c["contradicted"]),
        "kinds": sorted({f"{c['kind']}:{c['state']}" for c in found}), "refused_here": changed,
        "rule": "an absence state is refused whenever a matching typed row exists in any held text for the trial, including text "
                "another extraction in this review quotes; known-missing rows are refused in harness.known_missing"}
    return changed
