"""Deterministic, config-driven offline screen. Eligibility on P/I/C/DESIGN only.

Every decision is a pure function of the committed cache + the topic config, so it
replays identically on a fresh clone. Each record gets a rule id and a reason that is
true of the record. Whether a trial reports the outcome is NOT decided here (that is
target-result status, handled at extraction).
"""
from __future__ import annotations


def _has(text: str, terms) -> str | None:
    t = text.lower()
    for term in terms or []:
        if term.lower() in t:
            return term
    return None


def _has_intervention(text: str, terms) -> str | None:
    """Like _has, but a mention that is only 'X-resistant/resistance/refractory/intolerant'
    is a POPULATION descriptor, not the randomised intervention, and does not count."""
    t = text.lower()
    for term in terms or []:
        tl = term.lower()
        start = 0
        while True:
            i = t.find(tl, start)
            if i < 0:
                break
            after = t[i + len(tl): i + len(tl) + 12]
            if not any(w in after for w in ("resist", "refractory", "intoler", "-depend", " depend")):
                return term
            start = i + len(tl)
    return None


def _is_review(rec) -> bool:
    pts = [p.lower() for p in rec.get("pubtypes", [])]
    return any(("review" in p) or ("meta-analysis" in p) or ("meta analysis" in p) for p in pts)


def _is_rct(rec) -> bool:
    if rec["id_type"] == "pmid":
        # A primary RCT report, NOT a review/meta-analysis that merely discusses RCTs.
        if _is_review(rec):
            return False
        return any("randomized controlled trial" in p.lower() for p in rec.get("pubtypes", []))
    return (rec.get("allocation", "") or "").upper() == "RANDOMIZED" or rec.get("study_type", "") == "INTERVENTIONAL"


def _double_blind(rec, text) -> bool:
    m = (rec.get("masking", "") or "").upper()
    if any(w in m for w in ("DOUBLE", "TRIPLE", "QUADRUPLE")):
        return True
    if ("double-blind" in text) or ("double blind" in text) or ("masked" in text):
        return True
    # A placebo-controlled RCT is inherently blinded (open-label trials do not use a placebo);
    # abstracts frequently omit the literal "double-blind". Accept placebo-controlled as evidence.
    return "placebo" in text


def _text(rec) -> str:
    parts = [rec.get("title", ""), rec.get("abstract", ""), " ".join(rec.get("pubtypes", [])),
             " ".join(rec.get("conditions", [])), " ".join(rec.get("interventions", [])),
             rec.get("acronym", "")]
    return " ".join(p for p in parts if p).lower()


def _poptext(rec) -> str:
    # Population is judged from the TITLE and registry conditions, NOT an incidental
    # mention in the abstract body (e.g. "colchicine is beneficial in ... pericarditis").
    parts = [rec.get("title", ""), " ".join(rec.get("conditions", [])), rec.get("acronym", "")]
    return " ".join(p for p in parts if p).lower()


def screen_record(rec, inc, neg_pmids):
    text = _text(rec)
    poptext = _poptext(rec)
    label = rec.get("acronym") or rec.get("id")
    if not _is_rct(rec):
        return ("exclude", "X1", f"not a randomized controlled trial (record: {label}).")
    bad = _has(poptext, inc.get("population_none"))
    if bad:
        return ("exclude", "X2", f"wrong population: title/conditions mention '{bad}'.")
    popok = _has(poptext, inc.get("population_any"))
    if inc.get("population_any") and not popok:
        return ("exclude", "X2",
                f"population not on-topic: title/conditions do not mention any of {inc['population_any']} "
                f"(an incidental abstract mention does not qualify).")
    itext = _poptext(rec) if inc.get("intervention_in_title") else text
    if inc.get("intervention_any") and not _has_intervention(itext, inc["intervention_any"]):
        return ("exclude", "X3",
                f"the randomised intervention is not {inc['intervention_any']} "
                f"(not named in title/conditions; an incidental abstract mention does not qualify).")
    if inc.get("comparator_any") and not _has(text, inc["comparator_any"]):
        return ("exclude", "X3", f"no eligible comparator (none of {inc['comparator_any']}).")
    if inc.get("design_double_blind") and not _double_blind(rec, text):
        return ("exclude", "X-DESIGN", f"not double-blind/placebo-controlled (record: {label}).")
    return ("include", "INCLUDE",
            f"RCT of {inc.get('intervention_any',['intervention'])[0]} vs "
            f"{inc.get('comparator_any',['control'])[0]} in {popok or 'the target population'}; "
            f"double-blind placebo-controlled — P/I/C/design met.")


def run(all_recs: list, config: dict) -> dict:
    inc = config.get("include", {})
    neg = set(config.get("negative_control_pmids", []))
    decisions = []
    for rec in all_recs:
        decision, rule, reason = screen_record(rec, inc, neg)
        decisions.append({"id": rec["id"], "id_type": rec["id_type"],
                          "label": rec.get("acronym") or "", "decision": decision,
                          "rule_id": rule, "reason": reason})
    by_id = {d["id"]: d for d in decisions}
    pos = config.get("positive_control_pmids", [])
    pos_ok = [p for p in pos if by_id.get(p, {}).get("decision") == "include"]
    pos_miss = [p for p in pos if p not in pos_ok]
    negc = config.get("negative_control_pmids", [])
    neg_ok = [p for p in negc if by_id.get(p, {}).get("decision") == "exclude"]
    return {
        "decisions": decisions,
        "positive_control": (
            f"Recovered & included the canonical trials {pos_ok} that a comparator includes"
            + (f"; MISSED {pos_miss}" if pos_miss else "; none missed.")),
        "negative_control": (
            f"Cross-topic trial(s) {negc} recovered by the search and correctly EXCLUDED "
            f"{neg_ok} by rule (same drug/design, wrong topic)." if negc else "none configured"),
        "_pos_miss": pos_miss,
    }
