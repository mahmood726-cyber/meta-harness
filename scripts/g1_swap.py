"""PRE-REGISTERED COMPARATOR SWAPS (Mahmood 6 Oct: "solve it through comparator swaps"), the 5 Oct process as a
reproducible harness. Stages, each a subcommand:

  rules SLUG...      write registry/comparator_selection/<slug>.rule.json from the topic's OWN protocol fields
                     (topics/<slug>.json: question, eligibility, intervention/comparator terms, primary outcome, estimand,
                     timepoint). Commit + push BEFORE any search: the rule's git SHA is the pre-registration.
  search SLUG...     recorded literature search (PubMed esearch + Europe PMC, response sha256 kept)
  screen SLUG...     C1 mechanically (licence CC BY / CC0 from Europe PMC, else Unpaywall); C2-C6 per C1-passing candidate
                     by ONE recorded codex call over the candidate's held CC BY text, every PASS gated on a verbatim quote
  select SLUG...     scripts/g1_comparator_select.py (deterministic: the rule alone)

Rule R0 (the "blocks a match" test, decided before any search): the CURRENT comparator is assessed against C1-C6 by the
same procedure; it is retired only when it FAILS at least one criterion (recorded with that criterion's evidence); when
it passes all six it is KEPT (NO_SWAP: the block is acquisition, not the comparator) and no replacement is chosen.
How our own pool compares with any candidate is never an input.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
SEL = os.path.join(ROOT, "registry", "comparator_selection")
RATIO = {"HR", "RR", "OR"}


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def protocol(slug):
    """The protocol fields a rule quotes, taken from the topic file only."""
    c = _j(os.path.join(ROOT, "topics", slug + ".json"))
    po = c.get("primary_outcome") or {}
    est = (po.get("estimand") or "").upper()
    return {"file": f"topics/{slug}.json", "question": c.get("question") or c.get("title"),
            "eligibility": c.get("eligibility_summary") or None,
            "intervention_terms": c.get("intervention_terms") or [], "comparator_terms": c.get("comparator_terms") or [],
            "primary_outcome": po.get("name"), "estimand": est, "timepoint": po.get("timepoint"),
            "analysis_population": po.get("population"), "current_comparator": str(c.get("comparator_pmid"))}


def rule(slug):
    p = protocol(slug)
    est = p["estimand"]
    fam = ("ratio (HR, RR or OR)" if est in RATIO else f"{est} (a standardised difference fails)")
    t1 = (f"1 = {est}; 0 = another ratio" if est in RATIO else f"1 = {est} on the protocol's scale; 0 = other")
    return {
        "slug": slug,
        "purpose": ("PRE-REGISTERED selection rule for a replacement comparator meta (Mahmood 6 Oct: 'solve it through "
                    "comparator swaps'). Committed BEFORE any candidate search; candidates are judged per criterion from "
                    "their own text, and the pick follows from R0, the criteria and the tie-breaks alone. How our pool "
                    "compares with any candidate is NOT an input."),
        "protocol_reference": p,
        "R0_current_comparator": {
            "comparator_pmid": p["current_comparator"],
            "test": ("the current comparator is assessed against C1-C6 by the same procedure as every candidate. It is "
                     "RETIRED only if it fails at least one criterion (reason = that criterion, span = its evidence); if it "
                     "passes all six it is KEPT and the topic is NO_SWAP (the block is acquisition, not the comparator)."),
            "excluded_from_candidates_when_retired": True},
        "criteria": [
            {"id": "C1_OPEN_LICENCE", "pass_if": "the meta's full text is held under CC BY or CC0 (Europe PMC licence field, "
                                                  "else the Unpaywall location licence); any other licence, or free-to-read "
                                                  "without a licence, fails (lane licence rule)"},
            {"id": "C2_RCT_ONLY", "pass_if": "the analysis pools randomised controlled trials only (its own eligibility / "
                                             "methods statement)"},
            {"id": "C3_POPULATION", "pass_if": f"the pooled analysis is in the protocol's population: {p['question']}"
                                               + (f" (eligibility: {p['eligibility']})" if p["eligibility"] else "")},
            {"id": "C4_INTERVENTION_VS_COMPARATOR",
             "pass_if": f"the pooled comparison is {' / '.join(p['intervention_terms'][:6])} versus "
                        f"{' / '.join(p['comparator_terms'][:6])}"},
            {"id": "C5_OUTCOME_AND_ESTIMAND", "pass_if": f"it pools {p['primary_outcome']} (protocol timepoint: "
                                                         f"{p['timepoint']}) on the estimand family {fam}"},
            {"id": "C6_ROWS_AND_POOLED", "pass_if": "it prints per-trial rows for that outcome (a table, or a forest plot "
                                                    "with counts or effects, in the article or its own open supplement) AND "
                                                    "a pooled result for it"}],
        "tie_breaks": [
            {"id": "T1_ESTIMAND_MATCH", "order": "descending", "score": t1},
            {"id": "T2_MOST_RECENT", "order": "descending", "score": "publication year, then month"},
            {"id": "T3_LARGEST_K", "order": "descending", "score": "number of trials in the pooled analysis of the protocol outcome"}],
        "if_none_pass": ("NO_ACHIEVABLE_COMPARATOR: record the closest candidate and its single failing criterion; the "
                         "topic keeps its current comparator; no criterion is relaxed after the search"),
        "selector": "scripts/g1_comparator_select.py (deterministic; reads this rule and the typed candidates file)",
        "candidates_file": f"registry/comparator_selection/{slug}.candidates.json",
        "process": "scripts/g1_swap.py (rules -> search -> screen -> select); enumeration and acquisition follow the pick"}


def cmd_rules(slugs):
    for s in slugs:
        p = os.path.join(SEL, f"{s}.rule.json")
        if os.path.exists(p):
            old = _j(p)
            if old.get("process", "").startswith("scripts/g1_swap.py"):
                print(s, "rule exists (kept: a pre-registration is never rewritten)")
                continue
            raise SystemExit(f"{s}: a rule from an earlier round exists ({p}); refusing to overwrite a pre-registration")
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(rule(s), fh, indent=1, ensure_ascii=False)
        print(s, "rule written")


# ---------------------------------------------------------------------------------------------------------------- search
# the day the stage actually ran (a fixed "2026-10-06" would stamp later searches with a false date); held files are
# found by glob, so earlier-dated copies are still read
DATE = os.environ.get("G1_SWAP_DATE") or __import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%d")
CONTACT = "meta-harness@example.org"          # never a personal address in a request


def _terms(p):
    t = [x for x in p["intervention_terms"] if len(x) >= 3]
    return t[:12]


PAGE_CAP = 20000          # ids per database; a search past this is written TRUNCATED, never complete


PUBMED_LIMIT = 9999      # ESearch cannot page past retstart 9998; beyond it the search is TRUNCATED (Europe PMC pages on)


def pubmed_ids(get_raw, term, cap=PUBMED_LIMIT):
    """Every PubMed id for the query, paged by retstart to esearch's own count. (ids, {count, fetched, state, sha256s})"""
    ids, shas, count, start = [], [], None, 0
    while True:
        for attempt in range(5):
            st, b = get_raw("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                            {"db": "pubmed", "term": term, "retstart": str(start), "retmax": str(min(500, cap - start)),
                             "retmode": "json", "tool": "meta-harness", "email": CONTACT})
            # PubMed echoes raw control characters in querytranslation (strict=False); a rate-limit reply is a JSON
            # error with no count -- retried with backoff, and after 5 the search fails closed (never a short 'complete')
            r = (json.loads(b.decode("utf-8", "replace"), strict=False) if b[:1] == b"{" else {}).get("esearchresult") or {}
            if "count" in r:
                break
            __import__("time").sleep(2 * (attempt + 1))
        else:
            raise SystemExit(f"REFUSED: PubMed esearch returned no count at retstart {start}: {b[:200]!r}")
        shas.append(hashlib.sha256(b).hexdigest())
        count = int(r["count"])
        page = r.get("idlist") or []
        ids += page
        start += len(page)
        if not page or start >= count or start >= cap:
            break
    ids = list(dict.fromkeys(ids))
    return ids, {"count": count, "fetched": len(ids), "state": "COMPLETE" if len(ids) >= count else "TRUNCATED",
                 "response_sha256s": shas}


def europepmc_ids(get_raw, query, cap=PAGE_CAP):
    """Every Europe PMC hit's PMID, paged by cursorMark to its own hitCount. Hits without a PMID are counted, not kept."""
    pmids, shas, hits, seen, cur = [], [], None, 0, "*"
    while True:
        st, b = get_raw("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                        {"query": query, "format": "json", "pageSize": "1000", "resultType": "lite", "cursorMark": cur})
        r = json.loads(b.decode("utf-8"), strict=False)
        shas.append(hashlib.sha256(b).hexdigest())
        hits = int(r.get("hitCount") or 0)
        page = (r.get("resultList") or {}).get("result") or []
        seen += len(page)
        pmids += [x.get("pmid") for x in page if x.get("pmid")]
        nxt = r.get("nextCursorMark")
        if not page or not nxt or nxt == cur or seen >= hits or seen >= cap:
            break
        cur = nxt
    pmids = list(dict.fromkeys(pmids))
    return pmids, {"count": hits, "fetched_hits": seen, "with_pmid": len(pmids),
                   "state": "COMPLETE" if seen >= hits else "TRUNCATED", "response_sha256s": shas}


def cmd_search(slugs):
    """Recorded search per topic: PubMed esearch + Europe PMC, both restricted to meta-analyses / systematic reviews and
    built mechanically from the topic's intervention terms. Each database is paged to its own count (the 7 Oct first run
    stopped at 600 / 1000 and reported its reach as the population); response sha256s and every hit kept."""
    from harness import http
    for s in slugs:
        p = protocol(s)
        iv = " OR ".join(f'"{t}"' for t in _terms(p))
        pq = f'({iv}) AND (meta-analysis[pt] OR meta-analys*[ti] OR "systematic review"[ti] OR "network meta"[ti])'
        pm, pm_meta = pubmed_ids(http.get_raw, pq)
        eq = f'({iv}) AND (TITLE:"meta-analysis" OR TITLE:"meta analysis" OR TITLE:"systematic review" OR PUB_TYPE:"Meta-Analysis")'
        ep, ep_meta = europepmc_ids(http.get_raw, eq)
        ids = sorted(set(pm) | set(ep) | {p["current_comparator"]})
        recs = {}
        for i in range(0, len(ids), 150):
            r = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                              {"db": "pubmed", "id": ",".join(ids[i:i + 150]), "retmode": "json", "tool": "meta-harness",
                               "email": CONTACT})
            for k in r["result"].get("uids", []):
                v = r["result"][k]
                recs[k] = {"title": v.get("title"), "pubdate": v.get("pubdate"), "journal": v.get("source"),
                           "pubtypes": v.get("pubtype"),
                           "pmcid": next((a["value"] for a in v.get("articleids", []) if a["idtype"] == "pmc"), None),
                           "doi": next((a["value"] for a in v.get("articleids", []) if a["idtype"] == "doi"), None)}
        out = {"slug": s, "date": DATE, "rule": f"registry/comparator_selection/{s}.rule.json",
               "pubmed": dict({"query": pq, "n": len(pm)}, **pm_meta),
               "europepmc": dict({"query": eq, "n": len(ep)}, **ep_meta),
               "current_comparator_added": p["current_comparator"], "records": recs}
        if len(recs) < len(ids):
            out["records_state"] = f"TRUNCATED: {len(recs)} summaries for {len(ids)} ids"
        with open(os.path.join(SEL, f"{s}.search.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False)
        print(s, "pubmed", f"{len(pm)}/{pm_meta['count']}", pm_meta["state"], "europepmc",
              f"{ep_meta['fetched_hits']}/{ep_meta['count']}", ep_meta["state"], "records", len(recs), "of", len(ids), flush=True)


# ---------------------------------------------------------------------------------------------------------------- screen
SCREEN_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["criteria", "pooled"],
                 "properties": {
                     "criteria": {"type": "object", "additionalProperties": False,
                                  "required": ["C2_RCT_ONLY", "C3_POPULATION", "C4_INTERVENTION_VS_COMPARATOR",
                                               "C5_OUTCOME_AND_ESTIMAND", "C6_ROWS_AND_POOLED"],
                                  "properties": {c: {"type": "object", "additionalProperties": False,
                                                     "required": ["verdict", "quote"],
                                                     "properties": {"verdict": {"type": "string",
                                                                                "enum": ["PASS", "FAIL", "UNCLEAR"]},
                                                                    "quote": {"type": ["string", "null"]}}}
                                                 for c in ("C2_RCT_ONLY", "C3_POPULATION", "C4_INTERVENTION_VS_COMPARATOR",
                                                           "C5_OUTCOME_AND_ESTIMAND", "C6_ROWS_AND_POOLED")}},
                     "pooled": {"type": "object", "additionalProperties": False,
                                "required": ["measure", "estimate", "lower", "upper", "k", "quote"],
                                "properties": {"measure": {"type": ["string", "null"]}, "estimate": {"type": ["string", "null"]},
                                               "lower": {"type": ["string", "null"]}, "upper": {"type": ["string", "null"]},
                                               "k": {"type": ["integer", "null"]}, "quote": {"type": ["string", "null"]}}}}}

SCREEN_INSTR = """You assess ONE published meta-analysis against a PRE-REGISTERED selection rule. You are given the rule's
criteria C2-C6 and the meta's full text. For EACH criterion give PASS, FAIL or UNCLEAR and quote, character for character,
the shortest passage of the text that decides it (null only for UNCLEAR when nothing in the text bears on it). PASS needs a
quote that shows the criterion is met; FAIL needs a quote that shows it is not. Judge only from the text. Then, for the
pooled analysis of the protocol outcome, copy as printed: the measure, the pooled estimate and both 95% CI bounds, the
number of trials k in that pooled analysis, and the quote that prints them (nulls if not printed)."""


def jats_text(xml):
    import html as _h
    x = re.sub(r"</t[dh]>", " | ", xml)
    x = re.sub(r"</(?:tr|p|title|caption|label|ref)>", "\n", x)
    t = _h.unescape(re.sub(r"<[^>]+>", " ", x))
    return "\n".join(re.sub(r"[ \t]+", " ", ln).strip() for ln in t.splitlines() if ln.strip())


def _norm(t):
    return re.sub(r"\s+", " ", (t or "")).strip().lower()


def _quoted(q, nt):
    """A quote supports a claim only if it is non-empty after folding AND verbatim in the folded text (an all-whitespace
    quote folds to '' -- contained in every text: codex binding-v8-fe3ed2a7:g2#5)."""
    nq = _norm(q)
    return bool(nq) and nq in nt


def _num_tokens(q):
    """Whole numeric tokens of a quote, signed; a dash right after a digit is a range dash ('0.70-1.03'), not a minus."""
    text = (q or "").replace(",", "")
    out = []
    for m in re.finditer(r"([-−–]?)(\d*\.\d+|\d+(?:\.\d+)?)", text):
        before = text[:m.start()].rstrip()
        prev = before[-1] if before else " "
        # a dash after a digit -- spaced or not: '0.80-1.01', '0.80 - 1.01' -- is a RANGE dash, never a minus; any other
        # leading dash is the number's sign. A leading decimal ('.85') is read as 0.85, never as 85 (codex v8-p0-fixes)
        glued = m.start() > 0 and (text[m.start() - 1].isdigit() or text[m.start() - 1] == ".")
        spaced_after_digit = bool(m.group(1)) and not glued and (prev.isdigit() or prev == ".")
        neg = bool(m.group(1)) and not glued and not spaced_after_digit
        if spaced_after_digit:
            # '1.2 -3.4': two values or a range -- AMBIGUOUS, the token supports neither sign (refuse, never guess:
            # v8-p1-fixes g1#1 / v8-round3 g1#1)
            continue
        out.append(float(m.group(2)) * (-1 if neg else 1))
    return out


def enumeration_state(units, refused, pooled):
    """ENUMERATED only when every accepted unit stands, none was refused, AND the units account for the trial count the
    source prints for the pooled analysis (the gated k). One accepted unit used to make a two-trial analysis 'complete'
    (codex binding-v8-fe3ed2a7:g2#7); without a printed k completeness cannot be shown, so cmd_apply never adopts it."""
    if not units:
        return "NOT_ENUMERATED"
    if refused:
        return "ENUMERATION_INCOMPLETE"
    k = (pooled or {}).get("k")
    if k is None:
        return "ENUMERATION_K_NOT_STATED"
    if len({u.get("pmid") for u in units}) != int(k):
        return "ENUMERATION_INCOMPLETE" if len(units) < int(k) else "ENUMERATION_EXCEEDS_STATED_K"
    return "ENUMERATED"


def label_cites(lab, xml, refs):
    """The reference numbers the text CITES right after a label: an <xref rid=...> mapped through the meta's own
    reference list, or a literal '[n]' / '[n,m]' / '[n-m]'. Empty when the label is never followed by a citation."""
    rid2num = {r.get("rid"): n for n, r in refs.items() if r.get("rid")}
    x = re.sub(r'<xref\b[^>]*\brid="([^"]+)"[^>]*>.*?</xref>',
               lambda m: " [" + ",".join(rid2num.get(r, "?") for r in m.group(1).split()) + "] ", xml, flags=re.S)
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x))
    out = set()
    if not (lab or "").strip():
        return out
    # the label as a WHOLE word: 'Lee' never matches inside 'Kleen' (codex v8-p1-fixes g1#2)
    for m in re.finditer(r"(?<!\w)" + re.escape(lab.strip()) + r"(?!\w)", t, re.I):
        # only the citation DIRECTLY after the label (an 'et al.' / year may sit between) -- never one further on, which
        # belongs to the next named study ('Alpha [1]. Excluded: Beta [2]')
        c = re.match(r"\s*(?:et\s+al\.?,?\s*)?(?:\(?\d{4}[a-z]?\)?,?\s*)?\[([\d,\s\-–]+)\]", t[m.end():])
        for grp in ([c.group(1)] if c else []):
            grp = re.sub(r"\s*[\-–]\s*", "-", grp)        # '[3 - 5]' is the range 3-5 (codex v8-p1-fixes g1#3)
            for part in re.split(r"[,\s]+", grp.strip()):
                rng = re.split(r"[\-–]", part)
                if len(rng) == 2 and rng[0].isdigit() and rng[1].isdigit():
                    out.update(str(i) for i in range(int(rng[0]), int(rng[1]) + 1))
                elif part.isdigit():
                    out.add(part)
    return out


_TRIAL_ADJ = r"(?:randomi[sz]ed|controlled|clinical|phase\s*(?:[1-4]|iv|i{1,3}))"
_COUNT_WORDS = ("one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
                "seventeen eighteen nineteen twenty").split()


_TENS = ("twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")
# a count right after one of these is approximate, a bound or a comparison, never an exact k ('at least five', 'more than
# 5', 'up to five', 'about 12'; codex swap-setquote-r11 #3) -- a closed class of English approximators
_APPROX = {"least", "most", "than", "about", "approximately", "around", "nearly", "almost", "over", "under", "some",
           "roughly", "circa", "ca", "to", "upto", "beyond", "exceeding", "below", "above",
           # a count after 'of' is a denominator or a total ('50% of ten trials', 'two of the five'; codex
           # swap-setquote-r12 #1): never the contributing k. 'a total of 5 trials' is refused too -- refusal is safe
           "of", "between",
           # an estimate or approximation of the count ('An estimated five trials'; codex swap-setquote-r17 #1)
           "estimated", "est", "approx", "approximate", "apparently", "reportedly", "possibly", "probably", "likely",
           "perhaps", "potentially", "presumably", "expected", "anticipated", "projected",
           # 'At a minimum five trials' (codex swap-setquote-r18 #1)
           "minimum", "maximum", "min", "max"}


_RESTRICT = re.compile(r"\b(?:subsets?|subgroups?|only|some\s+of|of\s+which|of\s+whom|of\s+these|of\s+those|of\s+them|"
                       r"among\s+(?:them|these|those)|minority|portion|part\s+of|fractions?|not\s+all|except|excluding|"
                       r"apart\s+from|other\s+than|remaining|rest\s+of|few(?:er)?|several|"
                       # trials taken OUT of the analysis are not its k ('Five trials were excluded from the mortality
                       # analysis'; codex swap-setquote-r16 #3)
                       r"exclu\w*|omit\w*|withdr\w*|removed|dropped|lost\s+to|"
                       # a FRACTION of the trials ('Six trials were included; half reported mortality'; codex
                       # swap-setquote-r17 #3). A bare 'most' is not here: doac 29795629's own sentence says 'in most
                       # studies of secondary prevention' of OTHER studies; the narrower 'most ... reported' form is below
                       r"half|halves|quarters?|thirds?|majority|proportion|percent|per\s+cent|"
                       # trials WITHOUT the outcome's data ('Five trials lacked mortality data'; codex swap-setquote-r18
                       # #2). 'without' is deliberately absent: doac's sentence says 'with or without pulmonary embolism'
                       r"lack\w*|missing|unavailable|unreported|not\s+report\w*|did\s+not\s+(?:report|contribute|provide)|"
                       # 'no mortality data', 'no outcome events' (codex swap-setquote-r19 #2)
                       r"no\s+(?:\w+\s+){0,2}(?:data|events?|outcomes?)|"
                       # 'most' as a share of THESE trials ('Five trials were included; most reported mortality'; codex
                       # swap-setquote-r22 #2): 'most' then a reporting verb within two words, or 'most of the/them'.
                       # doac's 'in most studies of secondary prevention' (other studies) does not match
                       r"most\s+(?:of\s+(?:the|them|these|those)|(?:\w+\s+){0,2}(?:reported|report|contributed|provided|"
                       r"included|had|showed|found|were|was|did|gave|yielded)))\b", re.I)


def _stray_percent(sent):
    """A percentage in a count sentence that is not a CI level or a heterogeneity statistic ('40% reported mortality';
    codex swap-setquote-r16 #1): the sentence describes a fraction of the trials, so it never supplies k."""
    t = re.sub(r"\b9[059](?:\.\d+)?\s*%\s*(?:CI|CrI|confidence|credible|prediction|PI)\b", " ", sent, flags=re.I)
    t = re.sub(r"\bI\s*(?:2|²|\^2)?\s*(?:=|:|of)?\s*\d+(?:\.\d+)?\s*%", " ", t, flags=re.I)
    return "%" in t


def _clean(q):
    # whitespace of every kind is one space before anything is matched (codex swap-setquote-r3 #2: 'Phase\nthree')
    s = " ".join(str(q or "").split())
    # every dash is a hyphen ('twenty‑five', en / em dash, minus; codex swap-setquote-r6 #2)
    s = re.sub(r"[‐‑‒–—−]", "-", s)
    # a slash with spaces round it is still a range ('Phase one / two studies'; codex swap-setquote-r9 #1)
    s = re.sub(r"\s*/\s*", "/", s)
    # a bracket right after a bound symbol does not detach the bound from its count ('≥(five trials)'; codex
    # swap-setquote-r20 #2)
    return re.sub(r"([~<>≤≥])\s*[(\[]\s*", r"\1", s)


def _sentences(q):
    """Sentences: split after . ! ? followed by space and a capital, digit or opening bracket. A semicolon joins clauses
    of ONE sentence ('RR .85 (95% CI .70-1.03); 12 trials.' prints its count with its estimate), so it never splits. A missed split only
    MERGES two sentences, and a merged sentence holding two numerals is refused by printed_counts -- never admitted."""
    return [x for x in re.split(r"(?<=[.!?])\s+(?=[\"'(\[]?[A-Z0-9])", _clean(q)) if x.strip()]


def _numerals(sent):
    """Every quantity in a sentence that could be a count: whole numbers (not decimals, percentages or a phase number)
    and number words (incl. 'both', 'dozen'). Statistics like 0.88 or 95% are not numerals."""
    n = 0
    # numbers that are never a quantity of trials are removed first (the Part B replay refused colchicine's 'the 3 RCTs
    # ... I 2 = 0 % [ 20 - 22 ]' as four numerals): bracketed citation markers ('[20-22]', '[3, 5]') and the squared
    # statistics written with a 2 (I2 / I 2 / I^2, chi2, tau2). A removed number can only stop a refusal; the count
    # itself must still match the trial-count grammar in _counts_in.
    sent = re.sub(r"\[\s*\d+(?:\s*[-,]\s*\d+)*\s*\]", " ", sent)
    sent = re.sub(r"\b(?:I|chi|tau|χ|τ)\s*(?:\^\s*)?2\b", " ", sent, flags=re.I)
    # scientific notation is one number, not an integer prefix ('5e1'; codex swap-setquote-r24 #3)
    for m in re.finditer(r"(?<![\w.,/])\d+(?:,\d{3})*(?![.,]?\d)(?![eE][+-]?\d)(?!\s*%)", sent):
        if not re.search(r"\bphase\s*$", sent[:m.start()], re.I):
            n += 1
    words = list(_COUNT_WORDS) + list(_TENS) + ["hundred", "thousand", "million", "dozen", "both", "zero", "none", "nil"]
    # singular and collective quantities are quantities too ('mortality was reported by a single trial'; codex
    # swap-setquote-r20 #1) -- but not inside a hyphenated compound ('all-cause mortality', 'single-centre'; codex
    # swap-setquote-r21 #2, a false refusal)
    collective = ["single", "sole", "lone", "multiple", "numerous", "various", "many", "each", "every", "another", "all"]
    sent = re.sub(r"\ban?\s+(?:" + _TRIAL_ADJ + r"\s+){0,3}(?:trial|study|rct)\b", " one ", sent, flags=re.I)
    for m in re.finditer(r"\b(?:" + "|".join(words) + r")\b|(?<![\w-])(?:" + "|".join(collective) + r")(?![\w-])",
                         sent, re.I):
        if not re.search(r"\bphase\s*$", sent[:m.start()], re.I):
            n += 1
    return n


def printed_counts(q):
    """Trial counts PRINTED in a quote, read SENTENCE BY SENTENCE, and only from a sentence holding exactly ONE numeral
    (codex swap-setquote-r11 #2: 'Two of the five trials'; also 'one in five', '12 trials, 3,456 participants' -- any
    sentence with two quantities is ambiguous and refused, a closed rule instead of one patch per phrasing)."""
    out = set()
    for sent in _sentences(q):
        # a sentence that restricts the result to a SUBSET never supplies k, whichever path reads it (codex
        # swap-setquote-r15 #1: 'Five trials were included, but only a subset reported mortality (RR ...)')
        if _numerals(sent) == 1 and not _RESTRICT.search(sent) and not _stray_percent(sent):
            out |= _counts_in(sent)
    return out


def _counts_in(s):
    """In one cleaned sentence: 'k = n'; or n -- digits or a number word -- followed by up to three TRIAL ADJECTIVES
    (randomised, controlled, clinical, Phase 3) and then trials / studies / RCTs. A digit that is itself a phase number
    ('Phase 3 studies') is never a count, and any other word between the count and 'studies' refuses."""
    out = set()
    tail = r"\s+(?:" + _TRIAL_ADJ + r"\s+){0,3}(?:trials|studies|rcts)\b"
    # the WORD before the count decides, not a fixed-width lookbehind (three review rounds each found a new gap):
    # never after another number word ('twenty five', 'twenty-one'), 'and' / 'hundred' / 'thousand' ('one hundred and
    # twenty'), or 'phase' ('Phase 3', 'Phase three')
    tens = {"twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"}
    # 'zero' / 'none' start a range too ('between zero and five trials'; codex swap-setquote-r13 #2)
    number_words = set(_COUNT_WORDS) | tens | {"hundred", "thousand", "million", "zero", "none", "nil"}

    def prev_tokens(i, n=2):
        """The n whitespace/hyphen-separated tokens right before position i, lower-cased, punctuation KEPT."""
        # an opening bracket on its own is no token ('Approximately (five trials)'; codex swap-setquote-r12 #2)
        toks = [t.lower().lstrip("([{\"'‘“") for t in re.split(r"[\s-]+", s[:i].strip())]
        return [t for t in toks if t][-n:]

    def blocked_before(i):
        """The count is part of a larger number, a spelled decimal or a phase: the token right before it is a number word
        ('twenty five', 'thirty-five'), 'point' ('four point five'; codex r5 #1) or 'phase'; or it is 'and' right after a
        number word ('one hundred and twenty'). Punctuation on the previous token ends the link ('Phase 3: 5 randomized
        trials' -> 5; codex r5 #2), and a plain conjunction ('cohorts and 5 randomized trials') blocks nothing."""
        # an OPENING bracket or quote does not end the link ('(Phase three studies)', '(twenty five trials)'; codex r6 #1);
        # trailing punctuation does ('Phase 3: 5 randomized trials')
        pt = [t.lstrip("([{\"'‘“") for t in prev_tokens(i)]
        # punctuation never hides an approximator ('Approximately: five trials'; codex swap-setquote-r19 #3); it still
        # ends the link for a phase ('Phase 3: 5 randomized trials' -> 5)
        if pt and pt[-1].rstrip(":;,.!?)]}\"'’”") in _APPROX:
            return True
        if not pt or not re.fullmatch(r"[a-z]+", pt[-1]):
            return False
        if pt[-1] in number_words or pt[-1] in ("phase", "point") or pt[-1] in _APPROX:
            return True
        # 'of the ten trials', 'of these 5 studies': the article does not break the denominator link (codex
        # swap-setquote-r14 #1: '50% of the ten trials')
        # ... nor does an adjective ('50% of the eligible ten trials'; codex swap-setquote-r15 #3): 'of' / 'between'
        # anywhere in the three tokens before the count marks it a denominator
        if any(t in ("of", "between") for t in prev_tokens(i, 3)):
            return True
        # 'and' / 'to' / 'or' right after a number joins a larger number or a RANGE ('one hundred and twenty', 'two to five
        # trials', '3 or 4 studies'; codex swap-setquote-r8 #2): the end of a range is never an exact count
        # 'in' / 'of' after a number is a proportion ('one in five trials', 'three of five studies'; codex
        # swap-setquote-r10 #1): its denominator is not the number of contributing trials
        return (pt[-1] in ("and", "to", "or", "in", "of") and len(pt) == 2
                and (pt[0] in number_words or bool(re.fullmatch(r"\d+", pt[0]))))

    def bound_after(j):
        """A bound written AFTER the trials word: 'Five trials at most', '5 studies or more' (codex swap-setquote-r14 #2)."""
        # a bracket may open before it ('Five trials (at most)'; codex swap-setquote-r15 #2)
        # 'at the most' too (codex swap-setquote-r16 #2)
        # ... and 'at a minimum' (codex swap-setquote-r21 #1)
        return bool(re.match(r"\s*[,(\[]?\s*(?:(?:at\s+(?:the\s+|a\s+)?(?:most|least|maximum|minimum)|or\s+(?:more|fewer|less|so|over|under)|"
                             r"(?:as\s+a\s+)?(?:maximum|minimum)|and\s+(?:more|above|over)|"
                             # a trailing approximation ('five trials, approximately'; codex swap-setquote-r23 #1)
                             r"approx\w*|about|roughly|circa|estimated|give\s+or\s+take|or\s+thereabouts)\b|\+)",
                             s[j:], re.I))

    # 'k = n', with the same bound check after it as any other count ('k = 5 or more'; codex swap-setquote-r22 #1)
    # ... and the same check BEFORE it, read before the 'k' ('approximately k = 5'), and never the integer prefix of a
    # number in scientific notation ('k = 5e1') (codex swap-setquote-r24 #2, #3)
    for m in re.finditer(r"\bk\s*=\s*(\d+)(?![.,]\d)(?![eE][+-]?\d)", s, re.I):
        if not bound_after(m.end()) and not blocked_before(m.start()):
            out.add(int(m.group(1)))
    # a whole number, never '11.6', 'BRCA1' or one end of a slash range ('Phase 1/2 studies')
    # ... nor a bound written as a symbol ('~5', '>5', '≥5 trials')
    for m in re.finditer(r"(?<![\w.,/~<>≤≥-])(?<![~<>≤≥] )(\d+)(?![.,]\d)(?![eE][+-]?\d)(?!/)" + tail, s, re.I):
        if not blocked_before(m.start(1)) and not bound_after(m.end()):
            out.add(int(m.group(1)))
    # a hyphen before a number word means a compound ('thirty-five'; codex swap-setquote-r4 #1)
    # a slash joins a range ('Phase one/two studies'; codex swap-setquote-r7 #2): a number word beside '/' is never a count
    # ... and a symbol bound before a number word is a bound too ('≥five trials'; codex swap-setquote-r13 #1)
    for m in re.finditer(r"(?<![\w/~<>≤≥-])(?<![~<>≤≥] )(" + "|".join(_COUNT_WORDS) + r")(?![\w/-])" + tail, s, re.I):
        if not blocked_before(m.start(1)) and not bound_after(m.end()):
            out.add(_COUNT_WORDS.index(m.group(1).lower()) + 1)
    return out


def mentions_a_count(q):
    """Does the pooled quote speak to k at all? Deliberately coarse, with no distance window (codex swap-setquote-r9 #2:
    a 40-character window missed '25 high-quality, multicentre, ... trials'): it names trials / studies / RCTs AND holds
    any whole number that is not a decimal or a percentage, or any number word. A false 'yes' only refuses the claim."""
    s = " ".join(str(q or "").split())
    if not re.search(r"\b(?:trials?|stud(?:y|ies)|rcts?)\b", s, re.I):
        return False
    words = "|".join(_COUNT_WORDS + ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
                                     "hundred", "dozen", "both", "either", "neither"])
    return bool(re.search(r"(?<![\d.,])\d+(?![.,]?\d)(?!\s*%)", s)
                or re.search(r"\b(?:" + words + r")\b", s, re.I))


def _bound_counts(sent, vals):
    """The counts of one sentence that are BOUND to the stated result: printed in the clause (';'-separated) that prints
    every stated value, or in a clause that is nothing but a count ('RR .85 (95% CI .70-1.03); 12 trials.'). A count in
    a clause about something else never binds (codex swap-setquote-r23 #2: 'Five trials reported recurrence; mortality
    RR 0.85 (...)'). The sentence-level rules of printed_counts (one quantity, restrictions, percentages) apply first."""
    cnt = printed_counts(sent)
    if not cnt:
        return set()
    clauses = [c for c in _clean(sent).split(";") if c.strip()]
    res = [c for c in clauses if all(any(abs(v - t) < 1e-9 for t in _num_tokens(c)) for v in vals)] if vals else clauses
    if len(res) != 1:
        return set()
    bare = re.compile(r"^\W*(?:k\s*=\s*\d+|\d+\s+(?:" + _TRIAL_ADJ + r"\s+){0,3}(?:trials|studies|rcts))\W*$", re.I)
    ok = [res[0]] + [c for c in clauses if c is not res[0] and bare.match(c)]
    return {n for n in cnt if any(n in _counts_in(c) for c in ok)}


def pooled_gate(pl, nt, set_quote=None, verified_units=None):
    """The pooled claim stands only if its quote is verbatim in the held text, every stated estimate / bound EQUALS a whole
    numeric token of that quote (never a substring: '0.8' inside '0.85' -- g2#3), and a stated k is PRINTED in the quote
    as 'k = n' or 'n trials / studies / RCTs' (g2#4: an invented k reached the T3 largest-k tie-break). Returns
    (pooled or None, k or None)."""
    q = pl.get("quote")
    if not _quoted(q, nt):
        return None, None
    toks = _num_tokens(q)
    for key in ("estimate", "lower", "upper"):
        if pl.get(key) in (None, ""):
            continue
        try:
            v = float(str(pl[key]).replace("−", "-").replace("–", "-"))
        except ValueError:
            return None, None
        if not any(abs(v - t) < 1e-9 for t in toks):
            return None, None
    k = pl.get("k")
    if k is not None:
        # k is read ONLY from the sentence(s) of the pooled quote that print the pooled ESTIMATE (codex swap-setquote-r17
        # #2: 'Six trials were included. Only three trials reported mortality (RR 0.85).' -- the restricted outcome
        # sentence refused its own count and the review-wide sentence's 6 survived). A count elsewhere is never k.
        sents = _sentences(q)
        # the sentence must print the WHOLE stated result -- estimate and both bounds -- not merely the estimate's value,
        # which can be another outcome's CI bound (codex swap-setquote-r19 #1: 'Five trials reported recurrence (RR 0.70,
        # 95% CI 0.50-0.85). Mortality RR 0.85 (...)')
        vals = [float(str(pl[key]).replace("−", "-").replace("–", "-")) for key in ("estimate", "lower", "upper")
                if pl.get(key) not in (None, "")]
        if vals:
            sents = [x for x in sents if all(any(abs(v - t) < 1e-9 for t in _num_tokens(x)) for v in vals)]
        # exactly ONE sentence may print the result: two sentences printing identical numbers for different outcomes
        # are ambiguous, never unioned (codex swap-setquote-r21 #3)
        printed = _bound_counts(sents[0], vals) if len(sents) == 1 else set()
        # ... or, ONLY when the pooled quote prints no count, in the meta's own SET QUOTE verbatim in the held text (doac
        # 29795629: 'In the five Phase 3 studies ...'). The pooled result's own count always wins: a review-wide count
        # never overrides it (codex swap-setquote-r7 #1); a set quote not in the text is never read
        # The fallback is closed whenever the pooled quote MENTIONS a count at all, parsed or not ('twenty-five trials
        # contributed' is a count this reader refuses; a review-wide 'included 40 trials' must not stand in for it --
        # codex swap-setquote-r8 #1)
        # STRUCTURAL rule, replacing a blacklist that four review rounds each found a new hole in (codex swap-setquote-r10
        # #2 'Both trials ...' beside 'included 40 trials'): the set quote's count stands for k only when the pooled quote
        # lies INSIDE the set-quote sentence -- the count and the pooled result are printed together -- and that sentence
        # prints exactly ONE count. A review-wide count elsewhere in the paper can therefore never stand in.
        # Read ONLY the one sentence of the set quote that holds the pooled quote (codex swap-setquote-r11 #1: substring
        # containment let 'We included 40 trials.' speak for a pooled result two sentences later).
        # both sides through the same cleaning (dashes, slashes, whitespace): the comparison is of like with like
        sent = next((x for x in _sentences(set_quote) if _norm(_clean(q)) in _norm(x)), None) if set_quote else None
        # ... and CORROBORATED: text alone cannot prove whose count a sentence prints (codex swap-setquote-r12 #3: 'Of the
        # 40 trials, those reporting mortality gave RR 0.85'), so the borrowed count must equal the number of per-trial
        # units the enumeration independently verified, with none refused. Without that the fallback is closed.
        # ... and the sentence must not restrict the pooled result to a SUBSET of the counted trials ('Five trials were
        # included, but only a subset reported mortality'; codex swap-setquote-r13 #3): a closed class of restricting
        # phrases closes the fallback
        # ... and no percentage in the sentence ('mortality was reported by 40%'; codex swap-setquote-r14 #3).
        # RESIDUAL, stated rather than chased: whether every counted trial contributed to THIS outcome is a semantic
        # question that prose rules cannot close (r8-r14 each found a new paraphrase). A k taken this way is therefore
        # never silent: it carries k_basis SET_QUOTE_SENTENCE with the sentence (dash- and whitespace-normalised), and
        # the signing packet shows that sentence to the reviewer, who confirms the reading before the adoption is applied.
        fallback = False
        if (not printed and sent and _quoted(set_quote, nt) and not mentions_a_count(q) and verified_units
                and not _RESTRICT.search(sent) and not _stray_percent(sent)):
            # a CI level is not a fraction of the trials: the same percentage test as every other count sentence (codex
            # swap-setquote-r23 #3 -- '"%" not in sent' refused 'Five trials reported mortality RR 0.85 (95% CI ...)')
            c = _bound_counts(sent, vals)
            if c == {verified_units}:
                printed, fallback = c, True
        # k is a whole number as stated, never truncated (a fractional '11.6' is not 11 -- v8-p0-fixes g1#3), and the
        # value handed downstream is the validated integer
        try:
            kf = float(str(k).strip())
        except (TypeError, ValueError):
            return None, None
        if kf != int(kf) or int(kf) not in printed:
            return None, None
        k = int(kf)
        if fallback:
            pl = dict(pl, k_basis={"from": "SET_QUOTE_SENTENCE", "sentence": sent, "verified_units": verified_units,
                                   "reviewer_check": "the count in this sentence must be the trials in THIS pooled result"})
    return pl, k


def held_jats(pmid, pmcid):
    """The candidate's open JATS (Europe PMC fullTextXML), held at cache/comparators/<pmid>/<date>_kgap_jats.xml."""
    from harness import http
    d = os.path.join(ROOT, "cache", "comparators", str(pmid))
    have = sorted(f for f in (os.listdir(d) if os.path.isdir(d) else []) if f.endswith("_kgap_jats.xml"))
    if have:
        return os.path.relpath(os.path.join(d, have[-1]), ROOT).replace("\\", "/")
    try:
        st, b = http.get_raw(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML", tries=2, timeout=120)
    except Exception:  # noqa: BLE001 - an unfetchable text is 'not held' (C2-C6 stay UNCLEAR), never a crash or a pass
        return None
    if st != 200 or b"<article" not in b[:4000]:
        return None
    os.makedirs(d, exist_ok=True)
    rel = f"cache/comparators/{pmid}/{DATE}_kgap_jats.xml"
    with open(os.path.join(ROOT, rel), "wb") as fh:
        fh.write(b)
    return rel


def c1(pmid, rec):
    """C1 mechanically: Europe PMC licence CC BY / CC0, else an Unpaywall OA location licence CC BY / CC0."""
    import g1_licence as gl
    lic = gl.licence(pmid)
    if lic.get("open"):
        return {"verdict": "PASS", "evidence": f"Europe PMC licence {lic.get('license')}, {lic.get('pmcid')}"}, lic.get("pmcid")
    if lic.get("license"):
        return {"verdict": "FAIL", "evidence": f"Europe PMC licence {lic.get('license')} (not CC BY / CC0)"}, lic.get("pmcid")
    doi = rec.get("doi")
    if not doi:
        return {"verdict": "FAIL", "evidence": "no Europe PMC licence and no DOI"}, lic.get("pmcid")
    from harness import http
    try:
        u = http.get_json(f"https://api.unpaywall.org/v2/{doi}", {"email": CONTACT}, tries=2)
    except Exception as exc:  # noqa: BLE001 - unknown is not open
        return {"verdict": "UNCLEAR", "evidence": f"Unpaywall lookup failed: {str(exc)[:80]}"}, lic.get("pmcid")
    lics = sorted({str(l.get("license") or "") for l in u.get("oa_locations") or [] if l.get("license")})
    if any(x in ("cc-by", "cc0", "public-domain") for x in lics):
        return {"verdict": "PASS", "evidence": f"Unpaywall OA location licence {lics}"}, lic.get("pmcid")
    return {"verdict": "FAIL", "evidence": f"no CC BY / CC0 licence (Europe PMC none; Unpaywall {lics or u.get('oa_status')})"}, lic.get("pmcid")


ON_TOPIC = None


def on_topic(title, p):
    t = (title or "").lower()
    return any(x.lower() in t for x in p["intervention_terms"] if len(x) >= 3) or \
        bool(re.search(r"\b(" + "|".join(re.escape(x.lower()) for x in p["intervention_terms"] if len(x) >= 3) + r")", t))


def screen_item(s, p, pmid, rec, rule_):
    rel = held_jats(pmid, rec.get("pmcid_open"))
    if not rel:
        return None
    text = jats_text(open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read())
    crit = "\n".join(f"{c['id']}: PASS if {c['pass_if']}" for c in rule_["criteria"] if c["id"] != "C1_OPEN_LICENCE")
    prompt = (SCREEN_INSTR + f"\n\nPROTOCOL: {p['question']}\nPRIMARY OUTCOME: {p['primary_outcome']} "
              f"(estimand {p['estimand']}, timepoint {p['timepoint']})\nCRITERIA:\n{crit}\n<<<TEXT\n{text[:180000]}\nTEXT>>>\n").encode("utf-8")
    return {"key": f"swapscreen::{s}::{pmid}", "pmid": pmid, "slug": s, "prompt": prompt, "text": text, "held": rel,
            "digests": [{"ref": rel, "sha256": hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest(),
                         "what": "the candidate meta's open JATS (CC BY / CC0), rendered to text, first 180000 chars"}]}


A_CRIT = ("C2_RCT_ONLY", "C3_POPULATION", "C4_INTERVENTION_VS_COMPARATOR", "C5_OUTCOME_AND_ESTIMAND")
A_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["criteria"],
            "properties": {"criteria": {"type": "object", "additionalProperties": False, "required": list(A_CRIT),
                                        "properties": {c: {"type": "object", "additionalProperties": False,
                                                           "required": ["verdict", "quote"],
                                                           "properties": {"verdict": {"type": "string",
                                                                                      "enum": ["PASS", "FAIL", "UNCLEAR"]},
                                                                          "quote": {"type": ["string", "null"]}}}
                                                       for c in A_CRIT}}}}
A_INSTR = """STAGE A (abstract only). You assess ONE published meta-analysis from its TITLE and ABSTRACT against criteria
C2-C5 of a PRE-REGISTERED rule. Answer FAIL only when the abstract itself shows the criterion is NOT met, quoting that
passage character for character; answer PASS when it shows it is met (with the quote); otherwise UNCLEAR. A full-text
reading follows for every candidate not excluded here, so prefer UNCLEAR whenever the abstract does not decide."""


def abstract_of(text_xml):
    m = re.search(r"<abstract\b.*?</abstract>", text_xml, re.S)
    t = re.search(r"<article-title\b.*?</article-title>", text_xml, re.S)
    return (jats_text(t.group(0)) if t else "") + "\n" + (jats_text(m.group(0)) if m else "")


def gate_screen(claim, text):
    """A verdict counts only with its quote verbatim in the held text (whitespace / case folded); otherwise UNCLEAR."""
    nt = _norm(text)
    out = {}
    for cid, v in (claim.get("criteria") or {}).items():
        q = v.get("quote")
        ok = _quoted(q, nt)
        if v.get("verdict") in ("PASS", "FAIL"):
            out[cid] = ({"verdict": v["verdict"], "evidence": q} if ok else
                        {"verdict": "UNCLEAR", "evidence": (f"QUOTE_NOT_IN_TEXT: {q[:120]}" if q else "no quote")})
        else:                                   # the reader itself said UNCLEAR: labelled as such, never as a gate refusal
            out[cid] = {"verdict": "UNCLEAR", "evidence": f"READER_UNCLEAR: {q[:120]}" if q else "READER_UNCLEAR"}
    pooled, k = pooled_gate(claim.get("pooled") or {}, nt)
    return out, pooled, k


def recover(items, runs, rec_dir):
    """Ledger entries rebuilt from the RECORDS by prompt sha256 (a run interrupted before its ledger save must never be
    paid for twice). Returns how many were recovered."""
    import base64
    want = {hashlib.sha256(it["prompt"]).hexdigest(): it for it in items}
    n = 0
    for f in (sorted(os.listdir(rec_dir)) if os.path.isdir(rec_dir) else []):
        if not f.endswith(".json"):
            continue
        rec = _j(os.path.join(rec_dir, f))
        sha = hashlib.sha256(base64.b64decode((rec.get("prompt") or {}).get("b64") or "")).hexdigest()
        it = want.get(sha)
        if it and rec.get("state") == "RAN_OK" and (runs.get(it["key"]) or {}).get("prompt_sha256") != sha:
            runs[it["key"]] = {"record_id": rec["record_id"], "state": "RAN_OK", "prompt_sha256": sha,
                               "recovered_from_record": True}
            n += 1
    return n


def _run_calls(todo, runs, rec_dir, mcl, ms, fp, slugs):
    """Recorded calls, local at G1_CODEX_CONCURRENCY and (G1_REMOTE_SHARE=1) every other one on the worker."""
    import concurrent.futures as cf
    import shutil
    from kgap import runs_store
    conc = int(os.environ.get("G1_CODEX_CONCURRENCY", "5"))
    remote = todo[1::2] if os.environ.get("G1_REMOTE_SHARE") == "1" else []
    local = [it for it in todo if it not in remote]
    purpose = lambda it: (f"G1 comparator swap: screen candidate {it['pmid']} for {it['slug']} "
                          f"({'stage A abstract C2-C5' if it.get('stage') == 'A' else 'full text C2-C6'}, rule)")

    def one(it):
        rec = mcl.call(it["prompt"], schema=json.loads(json.dumps(it.get("schema") or SCREEN_SCHEMA)), model=fp.MODEL,
                       effort=fp.EFFORT, caller={"file": "scripts/g1_swap.py", "line": "screen", "purpose": purpose(it)},
                       input_digests=it["digests"], timeout_s=1500)
        ms.write_record(rec, rec_dir)
        return it["key"], {"record_id": rec["record_id"], "state": rec["state"], "host": "local",
                           "prompt_sha256": hashlib.sha256(it["prompt"]).hexdigest()}

    def remote_batch():
        import g1_remote_codex as rc
        jobs = [{"key": it["key"], "prompt": it["prompt"], "schema": it.get("schema") or SCREEN_SCHEMA, "model": fp.MODEL,
                 "effort": fp.EFFORT, "caller": {"file": "scripts/g1_swap.py", "line": "screen", "purpose": purpose(it)},
                 "input_digests": it["digests"], "timeout_s": 1500} for it in remote]
        res = rc.submit(jobs, "swapscreen", concurrency=conc) if jobs else {}
        out = {}
        for it in remote:
            v = res.get(it["key"]) or {}
            if v.get("record_path"):
                os.makedirs(rec_dir, exist_ok=True)
                shutil.copy(v["record_path"], os.path.join(rec_dir, v["record_id"] + ".json"))
                out[it["key"]] = {"record_id": v["record_id"], "state": v["state"], "host": "worker",
                                  "prompt_sha256": hashlib.sha256(it["prompt"]).hexdigest()}
            else:
                print(it["key"], "WORKER", v.get("error"), flush=True)
        return out
    with cf.ThreadPoolExecutor(max_workers=1) as rex:
        fut = rex.submit(remote_batch)
        with cf.ThreadPoolExecutor(max_workers=conc) as ex:
            futs = [ex.submit(one, it) for it in local]
            for f in cf.as_completed(futs):
                try:
                    k, r = f.result()
                    runs[k] = r
                    print(k, r["state"], r["record_id"], flush=True)
                    if sum(1 for v in runs.values() if v is r) and len(runs) % 20 == 0:
                        runs_store.save(runs, slugs=set(slugs))      # periodic: an interruption loses <= 20 entries
                except Exception as exc:  # noqa: BLE001 - a refused call is named, never dropped
                    print("LOCAL CALL FAILED", type(exc).__name__, str(exc)[:200], flush=True)
        try:
            for k, r in fut.result().items():
                runs[k] = r
                print(k, r["state"], r["record_id"], "worker", flush=True)
        except Exception as exc:  # noqa: BLE001 - worker failure is reported; the local half stands
            print("WORKER BATCH FAILED", type(exc).__name__, str(exc)[:300], flush=True)
    runs_store.save(runs, slugs=set(slugs))


def _t2(pubdate):
    m = re.match(r"(\d{4})\s*(\w{3})?", pubdate or "")
    mon = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10,
           "Nov": 11, "Dec": 12}.get((m.group(2) or "")[:3].title(), 0) if m else 0
    return int(m.group(1)) * 100 + mon if m else 0


def read_limit(items, cands_all, limit):
    """READ ORDER (7 Oct): limit 'r0' reads the CURRENT comparator only (rule R0 decides first: a passing current
    comparator is KEPT and no candidate matters); an integer N reads the current comparator plus the N NEWEST C1-PASS
    candidates per topic. Every candidate left unread is marked read=NOT_READ_EARLY_STOP, and
    g1_comparator_select.unread_problem refuses any pick an unread candidate could still outrank."""
    if limit is None:
        return items, set()
    keep, dropped = [], set()
    for s in {it["slug"] for it in items}:
        cur = protocol(s)["current_comparator"]
        mine = [it for it in items if it["slug"] == s]
        rest = sorted((it for it in mine if it["pmid"] != cur),
                      key=lambda it: (-_t2(cands_all[s][0][it["pmid"]].get("pubdate")), it["pmid"]))
        n = 0 if limit == "r0" else int(limit)
        keep += [it for it in mine if it["pmid"] == cur] + rest[:n]
        dropped |= {it["key"] for it in rest[n:]}
    return keep, dropped


def cmd_screen(slugs, run=False, limit=None):
    import concurrent.futures as cf
    from kgap import runs_store
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    import k_gap_forest_plot as fp
    rec_dir = os.path.join(ROOT, "evidence", "model_calls", "swap_screen")
    runs = runs_store.load()
    items, cands_all = [], {}
    for s in slugs:
        p, rule_ = protocol(s), _j(os.path.join(SEL, f"{s}.rule.json"))
        srch = _j(os.path.join(SEL, f"{s}.search.json"))
        cands = {}
        for pmid, rec in srch["records"].items():
            if pmid != p["current_comparator"] and not on_topic(rec.get("title"), p):
                continue                                   # off-topic title: not a candidate (listed by count)
            v, pmcid = c1(pmid, rec)
            rec = dict(rec, pmcid_open=pmcid)
            cands[pmid] = {"pmid": pmid, "title": rec.get("title"), "pubdate": rec.get("pubdate"), "doi": rec.get("doi"),
                           "pmcid": pmcid, "is_current_comparator": pmid == p["current_comparator"],
                           "criteria": {"C1_OPEN_LICENCE": v}}
            if v["verdict"] == "PASS" and pmcid:
                it = screen_item(s, p, pmid, rec, rule_)
                if it:
                    items.append(it)
                    cands[pmid]["held"] = it["held"]
        cands_all[s] = (cands, len(srch["records"]))
        print(s, "on-topic", len(cands), "C1 PASS", sum(c["criteria"]["C1_OPEN_LICENCE"]["verdict"] == "PASS" for c in cands.values()),
              "to read", sum(1 for it in items if it["slug"] == s), flush=True)

    items, unread = read_limit(items, cands_all, limit)

    def done(it):
        r = runs.get(it["key"]) or {}
        return r.get("prompt_sha256") == hashlib.sha256(it["prompt"]).hexdigest() and r.get("state") == "RAN_OK" and \
            os.path.exists(os.path.join(rec_dir, str(r.get("record_id")) + ".json"))

    # ---- STAGE A: the candidate's own abstract; a gated FAIL on C2-C5 excludes, nothing else is decided here
    a_items = []
    for it in items:
        rule_ = _j(os.path.join(SEL, f"{it['slug']}.rule.json"))
        ab = abstract_of(open(os.path.join(ROOT, it["held"]), encoding="utf-8", errors="replace").read())
        crit = "\n".join(f"{c['id']}: PASS if {c['pass_if']}" for c in rule_["criteria"] if c["id"] in A_CRIT)
        pr = protocol(it["slug"])
        prompt = (A_INSTR + f"\n\nPROTOCOL: {pr['question']}\nPRIMARY OUTCOME: {pr['primary_outcome']} (estimand "
                  f"{pr['estimand']})\nCRITERIA:\n{crit}\n=== TITLE AND ABSTRACT ===\n{ab}\n").encode("utf-8")
        a_items.append(dict(it, key=it["key"].replace("swapscreen::", "swapscreenA::"), prompt=prompt, text=ab,
                            schema=A_SCHEMA, stage="A"))
    excluded = {}
    print("recovered from records:", recover(a_items + items, runs, rec_dir), flush=True)
    if run:
        _run_calls([a for a in a_items if not done(a)], runs, rec_dir, mcl, ms, fp, slugs)
    for a in a_items:
        if done(a):
            r = runs[a["key"]]
            claim = json.loads(ms.replay(ms.load_record(os.path.join(rec_dir, r["record_id"] + ".json"))).decode("utf-8"))
            crit, _, _ = gate_screen(claim, a["text"])
            fails = {k: v for k, v in crit.items() if v["verdict"] == "FAIL"}
            if fails:
                excluded[a["key"].replace("swapscreenA::", "swapscreen::")] = (crit, r["record_id"])
    items = [it for it in items if it["key"] not in excluded]
    todo = [it for it in items if not done(it)]
    if run and todo:
        _run_calls(todo, runs, rec_dir, mcl, ms, fp, slugs)
    if False:
        conc = int(os.environ.get("G1_CODEX_CONCURRENCY", "5"))
        remote = todo[1::2] if os.environ.get("G1_REMOTE_SHARE") == "1" else []
        local = [it for it in todo if it not in remote]
        purpose = lambda it: f"G1 comparator swap: screen candidate {it['pmid']} for {it['slug']} (C2-C6, rule)"

        def one(it):
            rec = mcl.call(it["prompt"], schema=json.loads(json.dumps(SCREEN_SCHEMA)), model=fp.MODEL, effort=fp.EFFORT,
                           caller={"file": "scripts/g1_swap.py", "line": "screen", "purpose": purpose(it)},
                           input_digests=it["digests"], timeout_s=1500)
            ms.write_record(rec, rec_dir)
            return it["key"], {"record_id": rec["record_id"], "state": rec["state"], "host": "local",
                               "prompt_sha256": hashlib.sha256(it["prompt"]).hexdigest()}

        def remote_batch():
            import g1_remote_codex as rc
            import shutil
            jobs = [{"key": it["key"], "prompt": it["prompt"], "schema": SCREEN_SCHEMA, "model": fp.MODEL,
                     "effort": fp.EFFORT, "caller": {"file": "scripts/g1_swap.py", "line": "screen", "purpose": purpose(it)},
                     "input_digests": it["digests"], "timeout_s": 1500} for it in remote]
            res = rc.submit(jobs, "swapscreen", concurrency=conc) if jobs else {}
            out = {}
            for it in remote:
                v = res.get(it["key"]) or {}
                if v.get("record_path"):
                    os.makedirs(rec_dir, exist_ok=True)
                    shutil.copy(v["record_path"], os.path.join(rec_dir, v["record_id"] + ".json"))
                    out[it["key"]] = {"record_id": v["record_id"], "state": v["state"], "host": "worker",
                                      "prompt_sha256": hashlib.sha256(it["prompt"]).hexdigest()}
                else:
                    print(it["key"], "WORKER", v.get("error"), flush=True)
            return out
        with cf.ThreadPoolExecutor(max_workers=1) as rex:
            fut = rex.submit(remote_batch)
            with cf.ThreadPoolExecutor(max_workers=conc) as ex:
                futs = [ex.submit(one, it) for it in local]
                for f in cf.as_completed(futs):
                    try:
                        k, r = f.result()
                        runs[k] = r
                        print(k, r["state"], r["record_id"], flush=True)
                    except Exception as exc:  # noqa: BLE001 - a refused call is named, never dropped
                        print("LOCAL CALL FAILED", type(exc).__name__, str(exc)[:200], flush=True)
            for k, r in fut.result().items():
                runs[k] = r
                print(k, r["state"], r["record_id"], "worker", flush=True)
        runs_store.save(runs, slugs=set(slugs))
    by_key = {it["key"]: it for it in items}
    for s in slugs:
        cands, n_rec = cands_all[s]
        for pmid, c in cands.items():
            it = by_key.get(f"swapscreen::{s}::{pmid}")
            r = runs.get(f"swapscreen::{s}::{pmid}") or {}
            ex = excluded.get(f"swapscreen::{s}::{pmid}")
            if f"swapscreen::{s}::{pmid}" in unread:
                c["read"] = "NOT_READ_EARLY_STOP"
            if ex:
                c["criteria"].update(ex[0])
                c["criteria"]["C6_ROWS_AND_POOLED"] = {"verdict": "UNCLEAR", "evidence": "not read: excluded at stage A"}
                c["pooled"], c["record_id"], c["stage"] = None, ex[1], "A_EXCLUDED"
                k = None
            elif it and done(it):
                claim = json.loads(ms.replay(ms.load_record(os.path.join(rec_dir, r["record_id"] + ".json"))).decode("utf-8"))
                crit, pooled, k = gate_screen(claim, it["text"])
                c["criteria"].update(crit)
                c["pooled"], c["record_id"] = pooled, r["record_id"]
            else:
                for cid in ("C2_RCT_ONLY", "C3_POPULATION", "C4_INTERVENTION_VS_COMPARATOR", "C5_OUTCOME_AND_ESTIMAND",
                            "C6_ROWS_AND_POOLED"):
                    c["criteria"].setdefault(cid, {"verdict": "UNCLEAR", "evidence": "not read: C1 failed / no open JATS / not run"})
                k = None
            m = re.match(r"(\d{4})\s*(\w{3})?", c.get("pubdate") or "")
            mon = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10,
                   "Nov": 11, "Dec": 12}.get((m.group(2) or "")[:3].title(), 0) if m else 0
            meas = ((c.get("pooled") or {}).get("measure") or "").upper()
            est = protocol(s)["estimand"]
            c["tie_breaks"] = {"T1_ESTIMAND_MATCH": 1 if (est in meas or {"HAZARD": "HR", "RISK": "RR", "ODDS": "OR"}.get(meas.split()[0] if meas else "", "") == est) else 0,
                               "T2_MOST_RECENT": int(m.group(1)) * 100 + mon if m else 0,
                               "T3_LARGEST_K": k or 0}
        out = {"slug": s, "rule": f"registry/comparator_selection/{s}.rule.json",
               "rule_commit": __import__("subprocess").run(["git", "-C", ROOT, "log", "-1", "--format=%H", "--",
                                                            f"registry/comparator_selection/{s}.rule.json"],
                                                           capture_output=True, text=True).stdout.strip(),
               "search_file": f"registry/comparator_selection/{s}.search.json", "records_searched": n_rec,
               "screening": ("title prefilter: the topic's intervention terms in the title (else off-topic, not listed); "
                             "C1 mechanically from licence metadata; C2-C6 by one recorded codex call per C1-PASS candidate "
                             "over its held CC BY/CC0 JATS (evidence/model_calls/swap_screen), each verdict counted only "
                             "with its quote verbatim in the held text (else UNCLEAR). Nothing about our pool is read."),
               "candidates": sorted(cands.values(), key=lambda c: c["pmid"])}
        with open(os.path.join(SEL, f"{s}.candidates.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False)
        npass = sum(all(v.get("verdict") == "PASS" for v in c["criteria"].values()) for c in cands.values())
        print(s, "candidates", len(cands), "all-PASS", npass, flush=True)


# ----------------------------------------------------------------------------------------------------------- enumerate
ENUM_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["set_quote", "pooled", "trials"],
               "properties": {
                   "set_quote": {"type": ["string", "null"]},
                   "pooled": SCREEN_SCHEMA["properties"]["pooled"],
                   "trials": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                                         "required": ["label", "ref", "row_quote"],
                                                         "properties": {"label": {"type": "string"},
                                                                        "ref": {"type": ["string", "null"]},
                                                                        "row_quote": {"type": ["string", "null"]}}}}}}
ENUM_INSTR = """You ENUMERATE the trial set of ONE published meta-analysis for ONE outcome. From its full text list EVERY
randomised trial included in its pooled analysis of the stated outcome (the analysis matching the protocol): the trial's
label exactly as the meta prints it, the meta's reference number for it exactly as printed (e.g. "23"), and, if the meta
prints that trial's row for this outcome in its text or tables, the row quoted character for character (else null).
Quote the sentence, table caption or figure caption that states which / how many trials the pooled analysis includes
(set_quote), and copy the pooled result as printed (measure, estimate, both 95% CI bounds, k, quote). List only what the
text shows; never add a trial from your own knowledge."""


def jats_refs(xml):
    """{ref label number: {pmid, title, rid}} from the meta's own JATS reference list."""
    out = {}
    for r in re.findall(r"<ref\b[^>]*>.*?</ref>", xml, re.S):
        lab = re.search(r"<label>\s*\[?(\d+)\]?\.?\s*</label>", r)
        rid = re.search(r'<ref\b[^>]*\bid="([^"]+)"', r)
        num = lab.group(1) if lab else (re.search(r"(\d+)$", rid.group(1)).group(1) if rid and re.search(r"(\d+)$", rid.group(1)) else None)
        if not num:
            continue
        pm = re.search(r'<pub-id pub-id-type="pmid">\s*(\d+)\s*</pub-id>', r)
        ti = re.search(r"<article-title\b[^>]*>(.*?)</article-title>", r, re.S)
        au = re.search(r"<surname>([^<]+)</surname>", r)
        yr = re.search(r"<year>(\d{4})</year>", r)
        out[num] = {"pmid": pm.group(1) if pm else None, "title": jats_text(ti.group(1)) if ti else None,
                    "first_author": au.group(1) if au else None, "year": yr.group(1) if yr else None,
                    "rid": rid.group(1) if rid else None}
    return out


def enum_item(s, pmid, rel):
    p = protocol(s)
    xml = open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
    text = jats_text(xml)
    prompt = (ENUM_INSTR + f"\n\nPROTOCOL: {p['question']}\nOUTCOME: {p['primary_outcome']} (estimand {p['estimand']}, "
              f"timepoint {p['timepoint']})\n<<<TEXT\n{text[:180000]}\nTEXT>>>\n").encode("utf-8")
    return {"key": f"swapenum::{s}::{pmid}", "slug": s, "pmid": pmid, "prompt": prompt, "text": text, "xml": xml,
            "held": rel, "schema": ENUM_SCHEMA, "stage": "ENUM",
            "digests": [{"ref": rel, "sha256": hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest(),
                         "what": "the picked comparator's open JATS (CC BY / CC0), rendered to text, first 180000 chars"}]}


def gate_enum(claim, it):
    """Units the text supports: label printed in the text; row quote (if any) verbatim; identity from the meta's own
    reference list (printed PMID) or an exact title lookup. Returns (units, refused, pooled, set_quote)."""
    import ref_title_pmid_lookup as rl
    nt = _norm(it["text"])
    refs = jats_refs(it["xml"])
    units, refused = [], []
    for t in claim.get("trials") or []:
        lab, ref, rq = t.get("label") or "", str(t.get("ref") or "").strip(), t.get("row_quote")
        why = None
        if not _quoted(lab, nt):
            why = "LABEL_NOT_IN_TEXT"
        elif rq and not _quoted(rq, nt):
            why = "ROW_QUOTE_NOT_IN_TEXT"
        r = refs.get(ref) if ref else None
        if not why and not r:
            why = "REFERENCE_NUMBER_NOT_IN_THE_METAS_REFERENCE_LIST"
        if not why:
            # the label and the reference number are one claim: a label the text cites with OTHER reference numbers, and
            # never with this one, is bound to the wrong reference (codex binding-v8-fe3ed2a7:g2#6)
            cited = label_cites(lab, it["xml"], refs)
            if cited and ref not in cited:
                why = "LABEL_CITES_ANOTHER_REFERENCE:" + ",".join(sorted(cited, key=int))
        if why:
            refused.append({"label": lab, "ref": ref, "why": why})
            continue
        pmid, ident = r["pmid"], "COMPARATOR_REFERENCE_LIST_PMID" if r["pmid"] else None
        if not pmid and r.get("title"):
            hit = rl.lookup({"key": f"{it['pmid']}:REF:{ref}", "title": r["title"], "first_author": r.get("first_author") or "",
                             "year": r.get("year") or ""})
            if hit.get("state") == "CONFIRMED":
                pmid, ident = hit.get("pmid"), "CONFIRMED"
        if not pmid:
            refused.append({"label": lab, "ref": ref, "why": "IDENTITY_UNRESOLVED", "reference_title": r.get("title")})
            continue
        span = rq if rq else (r.get("title") or lab)
        units.append({"label": lab, "ref": ref, "pmid": pmid, "identity": ident, "span": span, "scope": "IN_SCOPE",
                      "rule_id": None})
    # the set-quote count is corroborated by the units verified above: distinct PMIDs, and only when nothing was refused
    verified = len({u["pmid"] for u in units}) if units and not refused else None
    pooled, _k = pooled_gate(claim.get("pooled") or {}, nt, set_quote=claim.get("set_quote"), verified_units=verified)
    sq = claim.get("set_quote")
    return units, refused, pooled, (sq if _quoted(sq, nt) else None)


def cmd_enumerate(slugs, run=False):
    """For each topic whose selection picked a NEW comparator: one recorded enumeration call, gated; writes
    registry/comparator_enumerations/<slug>.json in k_gap_table's enumeration schema (+ the pooled result)."""
    from kgap import runs_store
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    import k_gap_forest_plot as fp
    rec_dir = os.path.join(ROOT, "evidence", "model_calls", "swap_enum")
    runs = runs_store.load()
    items = []
    for s in slugs:
        sel = _j(os.path.join(SEL, f"{s}.selection.json"))
        pk = (sel.get("pick") or {}).get("pmid")
        if sel.get("result") not in ("PICKED", "PICKED_BY_RATIFIED_EXCEPTION") or not pk:
            print(s, "no new comparator:", sel.get("result"))
            continue
        c = next(x for x in _j(os.path.join(SEL, f"{s}.candidates.json"))["candidates"] if x["pmid"] == pk)
        items.append(enum_item(s, pk, c["held"]))
    done = lambda it: (runs.get(it["key"]) or {}).get("prompt_sha256") == hashlib.sha256(it["prompt"]).hexdigest() and \
        os.path.exists(os.path.join(rec_dir, str((runs.get(it["key"]) or {}).get("record_id")) + ".json"))
    if run:
        _run_calls([it for it in items if not done(it)], runs, rec_dir, mcl, ms, fp, slugs)
    for it in items:
        if not done(it):
            print(it["slug"], "NOT_RUN")
            continue
        r = runs[it["key"]]
        claim = json.loads(ms.replay(ms.load_record(os.path.join(rec_dir, r["record_id"] + ".json"))).decode("utf-8"))
        units, refused, pooled, sq = gate_enum(claim, it)
        state = enumeration_state(units, refused, pooled)
        enum = {"slug": it["slug"], "comparator_pmid": it["pmid"], "status": state,
                "enumerated_from": (f"the comparator's own text (PMID {it['pmid']}; held {it['held']}), recorded read "
                                    f"{r['record_id']} gated by scripts/g1_swap.py gate_enum"),
                "set_span": sq, "pooled": pooled, "refused": refused,
                "source": {"path": it["held"], "sha256": hashlib.sha256(open(os.path.join(ROOT, it["held"]), "rb").read()).hexdigest(),
                           "span_match": "markup-aware, whitespace-normalised"},
                "units": units}
        outp = os.path.join(ROOT, "registry", "comparator_enumerations", it["slug"] + ".swap.json")
        with open(outp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(enum, fh, indent=1, ensure_ascii=False)
        print(it["slug"], it["pmid"], state, "units", len(units), "refused", len(refused), "pooled", bool(pooled), flush=True)


# --------------------------------------------------------------------------------------------------------------- apply
def _held_old(slug, old_pmid):
    """The retired comparator's held text, if any (for its retirement spans)."""
    d = os.path.join(ROOT, "cache", "comparators", str(old_pmid))
    j = sorted(f for f in (os.listdir(d) if os.path.isdir(d) else []) if f.endswith("_kgap_jats.xml"))
    if j:
        return os.path.relpath(os.path.join(d, j[-1]), ROOT).replace("\\", "/")
    t = os.path.join(ROOT, "cache", slug, "comparator_fulltext.txt")
    return os.path.relpath(t, ROOT).replace("\\", "/") if os.path.exists(t) else None


def kgap_span(span):
    """A unit span as k_gap_table.enumeration_units checks it: that reader tag-strips the held JATS to spaces (held_norm)
    and needs each ' / '-separated line verbatim there, refusing the whole enumeration on one miss. This script renders
    a table row with its cells joined ' | ', which is in neither form. The row with cells joined by single spaces is
    contiguous in held_norm, so the whole row stays one line and its identity is kept."""
    return " ".join(c.strip() for c in re.split(r"\s*\|\s*", str(span)) if c.strip())


def retirement_code(fails):
    """The retirement reason names only the criteria R0 FAILED. A criterion left UNCLEAR because reading stopped at the
    first failure was never judged, so it is listed as not read, never as a failure (doac R0: C1 FAIL, C2-C6 UNCLEAR).
    None when nothing failed: such a comparator has no retirement reason."""
    failed = [f["criterion"] for f in fails if f.get("verdict") == "FAIL"]
    if not failed:
        return None
    unread = [f["criterion"] for f in fails if f.get("verdict") != "FAIL"]
    return "R0:" + "+".join(failed) + (f" (not read after the failure: {', '.join(unread)})" if unread else "")


def cmd_apply(slugs):
    """The swap through the normal path, only for a topic whose selection PICKED a new comparator AND whose enumeration
    is complete (status ENUMERATED): enumeration file, adoption record, comparators.json entry (old one kept under
    'replaces' with its retirement), topic comparator_pmid. A KEEP / NO_ACHIEVABLE topic is never touched."""
    import shutil
    for s in slugs:
        sel = _j(os.path.join(SEL, f"{s}.selection.json"))
        ep = os.path.join(ROOT, "registry", "comparator_enumerations", f"{s}.swap.json")
        if sel.get("result") not in ("PICKED", "PICKED_BY_RATIFIED_EXCEPTION"):
            print(s, "not applied:", sel.get("result"))
            continue
        if not os.path.exists(ep) or _j(ep).get("status") != "ENUMERATED" or not _j(ep).get("pooled"):
            print(s, "not applied: enumeration", (_j(ep).get("status") if os.path.exists(ep) else "MISSING"),
                  "pooled", bool(os.path.exists(ep) and _j(ep).get("pooled")))
            continue
        en = _j(ep)
        new, old = str(sel["pick"]["pmid"]), str((sel.get("R0") or {}).get("comparator_pmid"))
        cand = next(c for c in _j(os.path.join(SEL, f"{s}.candidates.json"))["candidates"] if c["pmid"] == new)
        src = en["source"]["path"]
        # 1. enumeration: the old comparator's file (if any) is retired beside, never deleted
        cur = os.path.join(ROOT, "registry", "comparator_enumerations", f"{s}.json")
        if os.path.exists(cur) and str(_j(cur).get("comparator_pmid")) != new:
            os.makedirs(os.path.join(ROOT, "registry", "comparator_enumerations", "retired"), exist_ok=True)
            shutil.move(cur, os.path.join(ROOT, "registry", "comparator_enumerations", "retired",
                                          f"{s}.{_j(cur).get('comparator_pmid')}.json"))
        enum = {k: en[k] for k in ("slug", "comparator_pmid", "status", "enumerated_from", "set_span", "source", "units")}
        # spans in k_gap_table's contract (verbatim in held_norm), not this script's ' | ' table rendering
        enum["units"] = [dict(u, span=kgap_span(u["span"])) for u in en["units"]]
        with open(cur, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(enum, fh, indent=1, ensure_ascii=False)
        # 2. retirement: R0's failing criteria; spans only where the evidence is verbatim in the old comparator's held text
        held = _held_old(s, old)
        ht = _norm(jats_text(open(os.path.join(ROOT, held), encoding="utf-8", errors="replace").read())) if held else ""
        fails = (sel.get("R0") or {}).get("failing") or []
        spans = [f["evidence"] for f in fails if f.get("evidence") and ht and _norm(f["evidence"]) in ht]
        code = retirement_code(fails)
        if not code:
            print(s, "not applied: R0 records no FAILED criterion, so the old comparator has no retirement reason")
            continue
        retired = {"comparator_pmid": old, "reason_code": code,
                   "why": "; ".join(f"{f['criterion']} {f['verdict']}: {str(f.get('evidence'))[:200]}" for f in fails),
                   "spans": spans, "source": ({"path": held, "sha256": hashlib.sha256(open(os.path.join(ROOT, held), "rb").read()).hexdigest()}
                                              if held else None),
                   "retired_on": DATE, "record": "kept: cache/<slug>/comparators.json 'replaces', and the G1 denominator ledger"}
        pl = en["pooled"]
        adoption = {"slug": s, "comparator_pmid": new, "comparator_pmcid": cand.get("pmcid"),
                    "comparator_type": "COMPARATOR_WITH_PER_TRIAL_ROWS",
                    "selection": {"rule_commit": sel["rule_commit"], "selection_file": f"registry/comparator_selection/{s}.selection.json",
                                  "result": sel["result"], "R0": sel.get("R0"),
                                  "decided_by": "Mahmood 2026-10-06: 'solve it through comparator swaps' (pre-registered rule)"},
                    "terms": {"per_trial_comparison": "from the comparator's own per-trial rows (read through the existing secondary-meta path)"},
                    "pooled_result": {"measure": pl.get("measure"), "estimate": pl.get("estimate"), "ci_low": pl.get("lower"),
                                      "ci_high": pl.get("upper"), "k": pl.get("k"), "spans": {"result": pl.get("quote")},
                                      "source": {"path": src, "sha256": en["source"]["sha256"]},
                                      # how k was read: present only when it came from the set-quote sentence, which the
                                      # signing packet then shows (normalised) for the reviewer's reading
                                      **({"k_basis": pl["k_basis"]} if pl.get("k_basis") else {})},
                    "trial_set": [{"label": u["label"], "pmid": u["pmid"]} for u in en["units"]], "retired": retired}
        with open(os.path.join(SEL, f"{s}.adoption.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(adoption, fh, indent=1, ensure_ascii=False)
        # 3. comparators.json + topic
        cp = os.path.join(ROOT, "cache", s, "comparators.json")
        oldc = _j(cp)
        if oldc and str(oldc[0].get("id")) == new:
            oldc = [{k: v for k, v in e.items() if k != "retired"} for e in oldc[0].get("replaces") or []]
        entry = {"id": new, "citation": f"{cand.get('title')} PMID {new}", "year": (cand.get("pubdate") or "")[:4],
                 "comparator_type": "COMPARATOR_WITH_PER_TRIAL_ROWS",
                 "scope_note": (f"Registered comparator identity (adopted {DATE}, pre-registered selection rule "
                                f"{str(sel['rule_commit'])[:9]}). Its trial set and pooled result are typed, with spans "
                                f"verified in held sources, in registry/comparator_selection/{s}.adoption.json and "
                                f"registry/comparator_enumerations/{s}.json."),
                 "held": True, "document_ref": src, "document_sha256": en["source"]["sha256"],
                 "trial_set": [], "k": None, "effect": None, "ci": None, "i2": None, "pi": None, "method": None,
                 "replaces": [dict(e, retired={"reason_code": retired["reason_code"],
                                               "span": (spans[0] if spans else retired["why"][:300]), "date": DATE}) for e in oldc]}
        with open(cp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump([entry], fh, indent=2, ensure_ascii=False)
        tp = os.path.join(ROOT, "topics", s + ".json")
        t = _j(tp)
        t["comparator_pmid"] = new
        with open(tp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(t, fh, indent=2, ensure_ascii=False)
        print(s, "SWAPPED", old, "->", new, "units", len(en["units"]), "retired", retired["reason_code"], flush=True)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    cmd, *args = sys.argv[1:]
    run = "--run" in args
    limit = next((a.split("=", 1)[1] for a in args if a.startswith("--newest=")), "r0" if "--r0" in args else None)
    args = [a for a in args if not a.startswith("--")]
    {"rules": cmd_rules, "search": cmd_search, "screen": lambda a: cmd_screen(a, run=run, limit=limit),
     "enumerate": lambda a: cmd_enumerate(a, run=run), "apply": cmd_apply}[cmd](args)
