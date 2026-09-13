"""Deterministic, config-driven offline screen. Eligibility on P/I/C/DESIGN only.

Every decision is a pure function of the committed cache + the topic config, so it
replays identically on a fresh clone. Each record gets a rule id and a reason that is
true of the record. Whether a trial reports the outcome is NOT decided here (that is
target-result status, handled at extraction).
"""
from __future__ import annotations
import re as _re

# Token-boundary matcher cache: a bare-substring `in` test matched a screening term inside a
# longer word, so 'rat' (population_none animal term) matched 'prepaRATion' / 'administRATion'
# and excluded human RCTs as animal studies (an external audit's finding, reproduced on
# probiotics 17604300/11148433/21871144). A term must match as a whole token: its edges are
# delimited by a non-alphanumeric boundary, so hyphens/spaces/digits at a term edge still
# delimit and multi-word / hyphenated terms ("in vitro", "sglt-2") match verbatim.
_BOUND_CACHE: dict = {}


def _boundary_re(term: str):
    """Whole-token match by default. A trailing '*' makes the term a STEM (leading boundary +
    prefix, any word continuation) so intentional stems like 'antibiotic-associated diarr*'
    match 'diarrhoea'/'diarrhea' while a bare 'rat' matches neither 'preparation' nor 'ration'."""
    r = _BOUND_CACHE.get(term)
    if r is None:
        if term.endswith("*"):
            r = _re.compile(r"(?<![a-z0-9])" + _re.escape(term[:-1]))
        else:
            r = _re.compile(r"(?<![a-z0-9])" + _re.escape(term) + r"(?![a-z0-9])")
        _BOUND_CACHE[term] = r
    return r


# A negated occurrence of an EXCLUSION term must not fire the exclusion: "no withdrawal effects",
# "without diabetes", "no rebound insomnia" describe the ABSENCE of the concept, so they are not the
# excluded population/intervention. Melatonin's Lemoine 2007 (PMID 18036082) -- a real prolonged-release
# melatonin RCT in primary-insomnia outpatients >=55 -- was wrongly X2-excluded because its title says
# "no withdrawal effects" and the population_none term 'withdrawal' matched. Cold-audit NEW class:
# lexical matching creates false EXCLUSIONS via negated terms (the mirror of false inclusions).
_NEGATION = _re.compile(
    r"(?:\bno\b|\bnot\b|\bnon-?\b|\bwithout\b|\bfree of\b|\babsence of\b|\babsent\b|\bnever\b|"
    r"\block of\b|\black of\b|\bnegative for\b|\bnil\b)[\w\s,'\"()-]{0,18}$", _re.I)


def _negated_at(text_lower: str, start: int) -> bool:
    """True if the term matched at `start` is negated by a nearby preceding cue (within ~24 chars)."""
    return bool(_NEGATION.search(text_lower[max(0, start - 26):start]))


def _has(text: str, terms) -> str | None:
    """Return the first exclusion term with a NON-negated occurrence in text (else None). A term that
    appears only in negated form ('no withdrawal', 'without diabetes') does not count as a match."""
    t = text.lower()
    for term in terms or []:
        tl = (term or "").lower().strip()
        if not tl:
            continue
        for m in _boundary_re(tl).finditer(t):
            if not _negated_at(t, m.start()):
                return term
    return None


def _all_occurrences_qualified(text: str, term: str, qualifiers) -> bool:
    """True iff `term` occurs in `text` and EVERY occurrence is immediately preceded by a phenotype
    qualifier (e.g. 'mildly ' before 'reduced ejection fraction' -> HFmrEF, an included phenotype). Used
    to suppress a nested exclusion term when the record is uniformly the qualified (included) variant; a
    single unqualified occurrence (a genuine HFrEF) returns False so the exclusion still fires."""
    low = text.lower()
    t = (term or "").lower()
    if not t:
        return False
    ql = [q.lower().strip() for q in qualifiers]
    i, found = low.find(t), False
    while i != -1:
        found = True
        pre = low[max(0, i - 16):i].rstrip()
        if not any(pre.endswith(q) for q in ql):
            return False
        i = low.find(t, i + 1)
    return found


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


import re as _re2
# Review/meta-analysis markers in the TITLE: PubMed often tags a meta-analysis only "Journal Article"
# (colchicine-postop 29766857 "...: A Meta-Analysis" and 36531704 "Meta-analysis of randomized..." were
# pubtype 'Journal Article' and slipped past a pubtype-only review check, then pooled their pooled RR as
# if a trial). A primary RCT report never titles itself a meta-analysis/systematic review.
_REVIEW_TITLE = _re2.compile(
    r"\bmeta[-\s]?anal(?:ysis|yses)\b|\bsystematic review\b|\bnetwork meta[-\s]?analysis\b|"
    r"\bpooled analysis\b|\bumbrella review\b|\bscoping review\b|\bnarrative review\b|"
    r"\bsystematic literature review\b", _re2.I)


def _is_review(rec) -> bool:
    pts = [p.lower() for p in rec.get("pubtypes", [])]
    if any(("review" in p) or ("meta-analysis" in p) or ("meta analysis" in p) for p in pts):
        return True
    # Title-declared meta-analysis/review with an INCOMPLETE pubtype -- but only when the record does
    # NOT carry a genuine primary-study pubtype. A primary RCT (pubtype 'Randomized Controlled Trial' /
    # 'Clinical Trial') that ALSO reports a pooled sub-analysis is still a trial: RE-COVER II (24344086),
    # "Treatment of acute VTE with dabigatran or warfarin and pooled analysis", is pubtype-RCT and must
    # not be reclassified a review by the title marker.
    if any(("randomized controlled trial" in p) or ("clinical trial" in p) for p in pts):
        return False
    return bool(_REVIEW_TITLE.search(rec.get("title", "") or ""))


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


# QUASI-randomisation: alternate/pseudo allocation is NOT a true RCT even when PubMed tags it
# "Randomized Controlled Trial" (metformin-PCOS cold audit: Chaudhury 2008 is pubtype-RCT but Cochrane
# classifies it quasi-RCT with cycle-level data). Full-text/abstract evidence overrides the pubtype in
# BOTH directions -- the mirror of the Chen 2023 pubtype-omission case.
_QUASI = _re.compile(r"quasi[-\s]?random|pseudo[-\s]?random|alternat(?:e|ely|ing)\s+"
                     r"(?:allocation|assignment|assigned|allocated)|alternate[-\s]?day allocation", _re.I)
# The ABSTRACT BODY describing the paper itself as a randomised trial (a self-description, not a review
# citing trials): 'randomized, double-blind', 'randomly assigned to', '1:1 randomisation', etc.
_BODY_RCT = _re.compile(
    r"random(?:i[sz]ed|ly)\b[^.]{0,40}?(?:double[-\s]?blind|placebo|1:1|parallel|to receive|"
    r"controlled trial|clinical trial|assigned|allocated|two groups|three groups)"
    r"|(?:double[-\s]?blind|placebo-controlled)[^.]{0,40}?random(?:i[sz]ed|ly)", _re.I)


def _body_says_rct(rec) -> bool:
    """The abstract body explicitly describes THIS study as a randomised trial. Used so an incomplete
    PubMed PublicationType (missing 'Randomized Controlled Trial') is treated as UNKNOWN, not
    NOT-AN-RCT -- the Chen 2023 (esketamine) loss: pubtype 'Journal Article' only, abstract says
    'Phase 3, randomized, double-blind, 1:1 ... vs matching placebo'."""
    return bool(_BODY_RCT.search(rec.get("abstract", "") or ""))


# Publication types that are NOT a primary RCT REPORT. A Comment/Editorial/Letter summarising a trial,
# a Clinical Trial PROTOCOL (no results yet), a Review/Meta-analysis, an Erratum/News all cite
# "randomized ... placebo-controlled" language and would otherwise be swept in by the body-RCT signal.
# (Regression guard: the body-RCT fix wrongly included a Cochrane-review Comment (27688016), a study
# Protocol (31712614) and an Editorial (39529940) into probiotics.)
_NONPRIMARY_PT = ("comment", "editorial", "letter", "news", "erratum", "review", "meta-analysis",
                  "meta analysis", "protocol", "guideline", "biography", "retracted publication",
                  "retraction of publication", "systematic review")


def _quasi_or_nonprimary(rec, pts) -> bool:
    """True if the record is quasi/alternate-allocated OR carries a non-primary publication type
    (comment/editorial/protocol/review/letter/erratum). Shared by both screeners."""
    if any(any(np in p for np in _NONPRIMARY_PT) for p in pts):
        return True
    return bool(_QUASI.search((rec.get("abstract", "") or "") + " " + (rec.get("title", "") or "")))


def _is_rct(rec) -> bool:
    if rec["id_type"] == "pmid":
        # A primary RCT report, NOT a review/meta-analysis that merely discusses RCTs.
        if _is_review(rec):
            return False
        pts = [p.lower() for p in rec.get("pubtypes", [])]
        # A non-primary publication type (comment/editorial/protocol/review/letter/erratum) is not a
        # completed primary RCT report, whatever its abstract cites.
        if any(any(np in p for np in _NONPRIMARY_PT) for p in pts):
            return False
        # NEGATIVE OVERRIDE: an explicit quasi/alternate-allocation statement in the body means this is
        # not a true RCT, even if the pubtype says "Randomized Controlled Trial".
        if _QUASI.search((rec.get("abstract", "") or "") + " " + (rec.get("title", "") or "")):
            return False
        if any("randomized controlled trial" in p for p in pts):
            return True
        # A design/protocol/rationale paper by TITLE is not a completed RCT (even with RCT language).
        if _TITLE_RCT_NOT.search(rec.get("title", "") or ""):
            return False
        # A missing RCT pubtype is UNKNOWN, not NOT-AN-RCT: accept an explicit self-declaration in the
        # TITLE or in the ABSTRACT BODY (full text/abstract overrules incomplete metadata).
        return _title_says_rct(rec) or _body_says_rct(rec)
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
    # NESTED-TERMINOLOGY guard (audit 16): an excluded phenotype term whose occurrence in the record's own
    # text is QUALIFIED into a DIFFERENT, included phenotype must not exclude it. "reduced ejection fraction"
    # (HFrEF, excluded) sits inside "mildly reduced ejection fraction" (HFmrEF, included); a bare-HFmrEF
    # record matches the exclusion and X2 fires first. Suppress the exclusion only when EVERY occurrence of
    # the matched term is immediately preceded by a phenotype qualifier ("mildly", "or preserved"), i.e. the
    # record is the included variant everywhere it appears — a genuine HFrEF ("reduced ejection fraction",
    # "with reduced ejection fraction") still excludes because its occurrence is unqualified.
    if bad and _all_occurrences_qualified(poptext, bad, ("mildly ", "or preserved ", "preserved or ", "mid-range ")):
        bad = None
    if bad:
        return ("exclude", "X2", f"wrong population: title/conditions mention '{bad}'.",
                _span(raw_pop, bad))
    popok = _has(poptext, inc.get("population_any"))
    if inc.get("population_any") and not popok:
        return ("exclude", "X2",
                f"population not on-topic: title/conditions do not mention any of {inc['population_any']} "
                f"(an incidental abstract mention does not qualify).",
                f"examined title/conditions: “{_quote(raw_pop)}”")
    # Title-anchoring for the intervention exists to reject INCIDENTAL abstract mentions in PMID
    # records; for a CT.gov (nct) record the STRUCTURED interventions field is reliable and must be
    # used (else an edoxaban AF trial whose title is "A Study to Assess..." is wrongly X3-excluded
    # though its interventions field says Edoxaban). So anchor only for PMID records.
    anchor = inc.get("intervention_in_title") and rec["id_type"] == "pmid"
    itext = _poptext(rec) if anchor else text
    itext_raw = raw_pop if anchor else raw_all
    matched_int = _has_intervention(itext, inc["intervention_any"]) if inc.get("intervention_any") else None
    if inc.get("intervention_any") and not matched_int:
        return ("exclude", "X3",
                f"the randomised intervention is not {inc['intervention_any']} "
                f"(not named in title/conditions; an incidental abstract mention does not qualify).",
                f"examined: “{_quote(itext_raw)}”")
    # INTERVENTION-IDENTITY exclusion (cold-audit NEW class: lexical matching false-INCLUDES records
    # whose intervention only SHARES A SUBSTRING/CLASS with ours). A record can match intervention_any
    # ("melatonin") yet be the WRONG thing: a receptor agonist/analogue (tasimelteon, ramelteon,
    # beta-methyl-6-chloromelatonin -> "melatonin agonist"), a COMBINATION (melatonin + magnesium +
    # zinc), or a trial that only MEASURES our drug while randomising another (doxepin, with melatonin
    # as a biomarker). intervention_none lists those excluded forms; a match here excludes even though
    # intervention_any matched. Negation-aware (via _has), so "not a receptor agonist" would not fire.
    bad_int = _has(itext, inc.get("intervention_none"))
    if bad_int:
        return ("exclude", "X3", f"intervention is the wrong form: matches excluded '{bad_int}' "
                f"(receptor agonist/analogue, combination, or measured-not-randomised).",
                _span(itext_raw, bad_int))
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
    # Reason built from the ACTUAL matched terms of THIS record, never a fixed template: an external
    # audit found the old reason hard-coded intervention_any[0] ('RCT of sitagliptin' on every DPP-4
    # trial, including alogliptin/saxagliptin ones) and claimed 'double-blind placebo-controlled' even
    # for non-blindable interventions (prone positioning). Design clause reflects what was required.
    design_clause = ("double-blind/placebo-controlled RCT" if inc.get("design_double_blind")
                     else "randomised controlled trial")
    return ("include", "INCLUDE",
            f"eligible {design_clause}: intervention {matched_int or '(as configured)'}, "
            f"comparator {comp or '(as configured)'}, population {popok or 'the target population'} "
            f"— P/I/C/design met.",
            ev or _quote(raw_pop))


_RANDOM_TEXT = _re.compile(r"randomi[sz]ed|randomly (?:assigned|allocated)", _re.I)


def screen_record_2(rec, inc):
    """SECOND, independently-implemented rule screener (for dual screening). Deliberately uses a
    DIFFERENT information basis than screen_record: it judges population/intervention/comparator from
    the FULL abstract body (not title/registry-conditions only) and accepts an RCT from a
    'randomised/randomly assigned' statement anywhere. It is therefore BROADER, and disagreements with
    screener 1 are exactly the title-anchored-vs-body question that caused past defects. NOT
    independent of screener 1 in the statistical sense (same author, same criteria) — that caveat is
    stated on the page; the rule-based screener 1 remains the adjudicator."""
    if _is_review(rec):
        return "exclude"
    text = _text(rec)
    _pts = [p.lower() for p in rec.get("pubtypes", [])]
    if rec["id_type"] == "pmid" and (
            _quasi_or_nonprimary(rec, _pts)
            or _TITLE_RCT_NOT.search(rec.get("title", "") or "")):
        return "exclude"  # quasi/alternate allocation, non-primary pubtype, or protocol/design paper
    is_rct = (rec["id_type"] != "pmid"
              or any("randomized controlled trial" in p for p in _pts)
              or _title_says_rct(rec) or bool(_RANDOM_TEXT.search(rec.get("abstract", "") or "")))
    if not is_rct:
        return "exclude"
    if _has(text, inc.get("population_none")):
        return "exclude"
    if inc.get("population_any") and not _has(text, inc.get("population_any")):
        return "exclude"
    if inc.get("intervention_any") and not _has_intervention(text, inc["intervention_any"]):
        return "exclude"
    if inc.get("comparator_any") and not _has(text, inc["comparator_any"]):
        return "exclude"
    if inc.get("design_double_blind") and not _double_blind(rec, text):
        return "exclude"
    return "include"


def _is_unresolved(rec) -> bool:
    """A record with NO retrievable text/metadata to screen on (bare NCT enumeration entry with no
    title, abstract, conditions or interventions). Its eligibility is UNKNOWN, not excluded — a
    screening decision either way is a metadata-completeness artifact, not a judgement. Third instance
    of the 'missing field means ineligible' shape (after the pubtype bug); resolved as its own state."""
    return not any((rec.get("title"), rec.get("abstract"),
                    rec.get("conditions"), rec.get("interventions")))


def run_dual(all_recs: list, config: dict) -> dict:
    """Run both rule screeners and report the disagreement rate (PRISMA item 8) over RESOLVED records
    only. Deterministic, replay-safe. Adjudicator = screener 1. Records with no retrievable text are
    'unresolved' (UNKNOWN != excluded) and counted separately, not as screening disagreements."""
    inc = config.get("include", {})
    neg = set(config.get("negative_control_pmids", []))
    dis = []
    agree = 0
    unresolved = 0
    for rec in all_recs:
        if _is_unresolved(rec):
            unresolved += 1
            continue
        d1 = screen_record(rec, inc, neg)[0]
        d2 = screen_record_2(rec, inc)
        if d1 == d2:
            agree += 1
        else:
            dis.append({"id": rec["id"], "screener1": d1, "screener2": d2})
    n = agree + len(dis)  # resolved records only
    return {"n": n, "agree": agree, "disagree": len(dis), "unresolved": unresolved,
            "disagreement_rate_pct": round(100 * len(dis) / n, 1) if n else None,
            "disagreements": dis[:60],
            "method": "two independently-implemented rule screeners (screener 2 judges from the full "
                      "abstract body; screener 1 from title/registry-conditions). Adjudicator: screener 1.",
            "caveat": "the two rule sets share an author and the same eligibility criteria, so they are "
                      "NOT statistically independent; this agreement overstates inter-rater reliability. "
                      "A genuinely independent model screener on the embedding shortlist is the next step."}


def run(all_recs: list, config: dict) -> dict:
    inc = config.get("include", {})
    neg = set(config.get("negative_control_pmids", []))
    # Companion/duplicate/design reports are NOT independent trials (unit-of-analysis / duplicate-
    # publication defect the external audit named: a "design and rationale" paper or a secondary report
    # of an already-pooled trial was being counted as an eligible trial). A CURATED map (not a title
    # heuristic, which false-fires on real trials) excludes them and links each to its parent.
    companions = {str(c["pmid"]): c for c in (config.get("companion_reports") or [])}
    # CONFIRMED non-contrast eviction (armcontrast into screening): a curated, audit-confirmed list of
    # trials whose randomised contrast is NOT the intervention-vs-comparator of interest. Evicted at
    # ELIGIBILITY (not admitted then disclosed after pooling) with reason code X-CONTRAST. Matches on
    # raw id / NCT / acronym so a registry-only record is caught. Confirmed-only (never unverified).
    evict = config.get("contrast_evictions") or []
    decisions = []
    for rec in all_recs:
        rid = str(rec.get("id"))
        _ekeys = {str(rec.get("id")), str(rec.get("nct") or ""), str(rec.get("acronym") or "")}
        _ehit = next((e for e in evict
                      if str(e.get("key")) in _ekeys
                      or any(str(a) in _ekeys for a in (e.get("alt") or []))), None)
        if _ehit:
            decisions.append({"id": rec["id"], "id_type": rec["id_type"],
                              "label": rec.get("acronym") or "", "decision": "exclude",
                              "rule_id": "X-CONTRAST",
                              "reason": f"CONTRAST_ABSENT: {_ehit.get('basis')} (audit-confirmed non-contrast; "
                                        f"evicted at eligibility, not pooled).",
                              "span": (rec.get("title") or "")[:120]})
            continue
        if rid in companions:
            c = companions[rid]
            decisions.append({"id": rec["id"], "id_type": rec["id_type"],
                              "label": rec.get("acronym") or "", "decision": "exclude",
                              "rule_id": "X-DEDUP",
                              "reason": f"companion/duplicate report of {c.get('parent')} "
                                        f"({c.get('kind', 'secondary/design report')}) — not an independent "
                                        f"trial; its parent is handled separately.",
                              "span": (rec.get("title") or "")[:120]})
            continue
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
