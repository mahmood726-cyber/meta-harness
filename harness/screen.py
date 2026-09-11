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


import re as _re
# A TITLE that declares the paper itself a randomised trial ("... : The BaSICS Randomized Clinical
# Trial", "A Randomised Controlled Trial of ..."). PubMed sometimes omits the "Randomized Controlled
# Trial" PublicationType even for definitive RCTs (BaSICS 34375394 was tagged only "Journal Article"
# and wrongly excluded X1). Guarded: NOT a protocol / secondary analysis / substudy / design paper.
_TITLE_RCT = _re.compile(r"randomi[sz]ed\b.{0,40}\btrial\b", _re.I)
_TITLE_RCT_NOT = _re.compile(r"\bprotocol\b|\bsecondary analysis\b|\bpost[-\s]?hoc\b|\bsubstudy\b|"
                             r"\bsub-study\b|\brationale and design\b|\bstudy design\b|\bstatistical analysis plan\b", _re.I)


def _title_says_rct(rec) -> bool:
    t = rec.get("title", "") or ""
    return bool(_TITLE_RCT.search(t)) and not _TITLE_RCT_NOT.search(t)


def _is_rct(rec) -> bool:
    if rec["id_type"] == "pmid":
        # A primary RCT report, NOT a review/meta-analysis that merely discusses RCTs.
        if _is_review(rec):
            return False
        if any("randomized controlled trial" in p.lower() for p in rec.get("pubtypes", [])):
            return True
        # Fallback: the TITLE explicitly declares a randomised trial (PubMed pubtype lag/omission).
        return _title_says_rct(rec)
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


def _text_raw(rec) -> str:
    parts = [rec.get("title", ""), rec.get("abstract", ""), " ".join(rec.get("pubtypes", [])),
             " ".join(rec.get("conditions", [])), " ".join(rec.get("interventions", [])),
             rec.get("acronym", "")]
    return " ".join(p for p in parts if p)


def _text(rec) -> str:
    return _text_raw(rec).lower()


def _poptext_raw(rec) -> str:
    # Population is judged from the TITLE and registry conditions, NOT an incidental
    # mention in the abstract body (e.g. "colchicine is beneficial in ... pericarditis").
    parts = [rec.get("title", ""), " ".join(rec.get("conditions", [])), rec.get("acronym", "")]
    return " ".join(p for p in parts if p)


def _poptext(rec) -> str:
    return _poptext_raw(rec).lower()


def _span(raw: str, term: str, width: int = 48) -> str:
    """Verbatim window (original case) around the first case-insensitive occurrence of `term` in
    `raw`. The span is a REAL substring of the record's own text, so a reviewer can confirm the rule
    fired on words that are actually present -- never a paraphrase. Empty if not found."""
    if not raw or not term:
        return ""
    i = raw.lower().find(term.lower())
    if i < 0:
        return ""
    a = max(0, i - width // 2)
    b = min(len(raw), i + len(term) + width // 2)
    return ("…" if a > 0 else "") + " ".join(raw[a:b].split()) + ("…" if b < len(raw) else "")


def _quote(raw: str, limit: int = 90) -> str:
    """A verbatim head of the examined text, for ABSENCE rules (why nothing matched): the reviewer
    sees the exact title/fields the screen looked at. Still a true substring of the record."""
    s = " ".join((raw or "").split())
    return (s[:limit] + "…") if len(s) > limit else s


def describe_eligibility(inc: dict) -> str:
    """Render the eligibility statement FROM the structured include object that screen_record
    actually enforces, so the served/declared eligibility on the page cannot drift from the code
    that screens (the "declared method == served method" invariant, at the eligibility level).
    Every clause below corresponds one-to-one to a branch of screen_record."""
    inc = inc or {}
    clauses = ["a randomised controlled trial"]
    pa = inc.get("population_any")
    if pa:
        clauses.append(f"population (in title/registry conditions) mentions one of {pa}")
    pn = inc.get("population_none")
    if pn:
        clauses.append(f"and none of {pn}")
    ia = inc.get("intervention_any")
    if ia:
        loc = "named in title/conditions" if inc.get("intervention_in_title") else "present in the record"
        clauses.append(f"randomised intervention is one of {ia} ({loc})")
    ca = inc.get("comparator_any")
    if ca:
        clauses.append(f"a comparator among {ca}")
    if inc.get("design_double_blind"):
        clauses.append("double-blind or placebo-controlled")
    excl = ["X1 not an RCT", "X2 wrong/off-topic population", "X3 wrong intervention/comparator"]
    if inc.get("design_double_blind"):
        excl.append("X-DESIGN not double-blind/placebo-controlled")
    return ("Included iff ALL hold: " + "; ".join(clauses)
            + ". Excluded (rule id + verbatim span on each record): " + " · ".join(excl) + ".")


def screen_record(rec, inc, neg_pmids):
    """Return (decision, rule_id, reason, span). `span` is a VERBATIM excerpt of the record's own
    text evidencing the decision (a real substring), so every decision is checkable against source."""
    text = _text(rec)
    poptext = _poptext(rec)
    raw_all = _text_raw(rec)
    raw_pop = _poptext_raw(rec)
    label = rec.get("acronym") or rec.get("id")
    if not _is_rct(rec):
        pts = ", ".join(rec.get("pubtypes", [])) or "(no publication types)"
        return ("exclude", "X1", f"not a randomized controlled trial (record: {label}).",
                f"publication types: {pts}")
    bad = _has(poptext, inc.get("population_none"))
    if bad:
        return ("exclude", "X2", f"wrong population: title/conditions mention '{bad}'.",
                _span(raw_pop, bad))
    popok = _has(poptext, inc.get("population_any"))
    if inc.get("population_any") and not popok:
        return ("exclude", "X2",
                f"population not on-topic: title/conditions do not mention any of {inc['population_any']} "
                f"(an incidental abstract mention does not qualify).",
                f"examined title/conditions: “{_quote(raw_pop)}”")
    itext = _poptext(rec) if inc.get("intervention_in_title") else text
    itext_raw = raw_pop if inc.get("intervention_in_title") else raw_all
    if inc.get("intervention_any") and not _has_intervention(itext, inc["intervention_any"]):
        return ("exclude", "X3",
                f"the randomised intervention is not {inc['intervention_any']} "
                f"(not named in title/conditions; an incidental abstract mention does not qualify).",
                f"examined: “{_quote(itext_raw)}”")
    comp = _has(text, inc.get("comparator_any"))
    if inc.get("comparator_any") and not comp:
        return ("exclude", "X3", f"no eligible comparator (none of {inc['comparator_any']}).",
                f"examined: “{_quote(raw_all)}”")
    if inc.get("design_double_blind") and not _double_blind(rec, text):
        masking = rec.get("masking") or "(masking not stated)"
        return ("exclude", "X-DESIGN", f"not double-blind/placebo-controlled (record: {label}).",
                f"no 'placebo'/'double-blind'/'masked' in text; registry masking = {masking}")
    # include: quote the actual matched population and comparator words
    pop_span = _span(raw_pop, popok) if popok else ""
    comp_span = _span(raw_all, comp) if comp else ""
    ev = "; ".join(s for s in (f"population “{pop_span}”" if pop_span else "",
                               f"comparator “{comp_span}”" if comp_span else "") if s)
    return ("include", "INCLUDE",
            f"RCT of {inc.get('intervention_any',['intervention'])[0]} vs "
            f"{inc.get('comparator_any',['control'])[0]} in {popok or 'the target population'}; "
            f"double-blind placebo-controlled — P/I/C/design met.",
            ev or _quote(raw_pop))


def run(all_recs: list, config: dict) -> dict:
    inc = config.get("include", {})
    neg = set(config.get("negative_control_pmids", []))
    decisions = []
    for rec in all_recs:
        decision, rule, reason, span = screen_record(rec, inc, neg)
        decisions.append({"id": rec["id"], "id_type": rec["id_type"],
                          "label": rec.get("acronym") or "", "decision": decision,
                          "rule_id": rule, "reason": reason, "span": span})
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
