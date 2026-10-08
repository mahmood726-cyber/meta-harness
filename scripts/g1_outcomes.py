"""D10 MULTI-OUTCOME (Mahmood, relayed 2026-10-07), under registry/outcome_amendments/D10_rule.json (committed a40e00850
BEFORE any of this ran). Stages, each a subcommand:

  inventory SLUG...  what the CURRENT comparator prints: R1 regex over its held text (local, any licence, typed reading
                     only) + R2 one recorded codex call over its CC BY / CC0 full text, or only title + abstract when the
                     copy is not CC BY / CC0. Every R2 claim is kept only with a quote verbatim in the text it was given
                     and every number a whole token of that quote.
                     -> registry/outcome_amendments/<slug>.inventory.json
  propose SLUG...    the rule's P1 / P2 / P3 families applied deterministically to the gated inventory
                     -> registry/outcome_amendments/<slug>.proposal.json
"""
from __future__ import annotations

import glob
import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
OUT = os.path.join(ROOT, "registry", "outcome_amendments")
RULE = os.path.join(OUT, "D10_rule.json")
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "d10_inventory")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def topic(slug):
    return _j(os.path.join(ROOT, "topics", slug + ".json"))


# ------------------------------------------------------------------------------------------------- the comparator text
def comparator_sources(slug):
    """(pmid, cc_jats_rel or None, regex_text, regex_refs, abstract). regex_text = every held text of the comparator
    (newest JATS rendered with its tables, else the committed held document) + its held supplements -- typed reading
    only. cc_jats_rel is set only when that JATS's own <permissions> name a CC licence AND the lane licence rule
    (scripts/g1_licence.py: Europe PMC CC BY / CC0) agrees."""
    import g1_swap as sw
    import g1_licence as gl
    from kgap import k_gap
    from reproducible_ai import record_licence as rl
    pmid = str(topic(slug)["comparator_pmid"])
    d = os.path.join(ROOT, "cache", "comparators", pmid)
    jats = sorted(glob.glob(os.path.join(d, "*_kgap_jats.xml")))
    parts, refs, cc = [], [], None
    if jats:
        rel = os.path.relpath(jats[-1], ROOT).replace("\\", "/")
        xml = open(jats[-1], encoding="utf-8", errors="replace").read()
        parts.append(sw.jats_text(xml))
        refs.append(rel)
        abstract = sw.abstract_of(xml)
        if rl.jats_licence(jats[-1]) == "CC" and (gl.licence(pmid) or {}).get("open"):
            cc = rel
    else:
        text, ref = k_gap.held_text(slug)
        parts.append(text)
        refs.append(ref)
        abstract = ""
    for f in sorted(glob.glob(os.path.join(d, "*supplements.txt")) + glob.glob(os.path.join(d, "*_S3_appendix.tsv"))
                    + glob.glob(os.path.join(d, "*_repository_main.txt"))):
        parts.append(open(f, encoding="utf-8", errors="replace").read())
        refs.append(os.path.relpath(f, ROOT).replace("\\", "/"))
    if not abstract.strip():
        abstract = _pubmed_abstract(pmid)
    return pmid, cc, "\n".join(parts), refs, abstract


def _pubmed_abstract(pmid):
    import k_gap_table as kt
    return (kt.comparator_abstracts([pmid], True) or {}).get(pmid, "") or ""


# --------------------------------------------------------------------------------------------------- R1: regex inventory
_NUM = r"[-−–]?\d+(?:\.\d+)?"
_ABBR = r"(?:\s*[\(\[](?:a?HR|RR|OR|W?MD|SMD|RD)[\)\]])?"
EFFECT = re.compile(
    r"(?P<m>\b(?:a?HR|RR|OR|W?MD|SMD|RD|hazard ratios?|risk ratios?|relative risks?|odds ratios?|"
    r"(?:weighted |standardi[sz]ed )?mean differences?)\b)" + _ABBR + r"\s*(?:[:=,]|of|was|were)?\s*(?P<e>" + _NUM + r")\s*"
    r"[\(\[,;]?\s*(?:(?:95\s*%\s*)?(?:CI|confidence intervals?|CrI)(?:\s*\(CI\))?[\s:,=]*[\(\[]?)?\s*(?P<l>" + _NUM + r")\s*"
    r"(?:to|-|–|—|,)\s*(?P<u>" + _NUM + r")", re.I)
# 1:1 character normalisation for MATCHING only (spans are sliced from the original at the same offsets): Lancet's
# middle-dot decimal '0·77', and the PDF-extraction glyph '¼' printed for '=' ('RR ¼0.40')
_NORM_1TO1 = str.maketrans({"·": ".", "¼": "="})


def _num(x):
    return x.replace("−", "-").replace("–", "-")


MORT = re.compile(r"\b(all[- ]cause (?:mortality|deaths?)|deaths? from any cause|any[- ]cause (?:deaths?|mortality)|"
                  r"total mortality|overall mortality)\b", re.I)
HARM = re.compile(r"\b(serious adverse events?|adverse events?|discontinu\w+|(?:drug )?withdrawals?|hypoglyc\w+|bleed\w*|"
                  r"ha?emorrhag\w+|ketoacidosis|amputations?|infections?|hypersensitivity|thrombo\w+|nausea|vomiting|"
                  r"gastrointestinal|myopathy|myalgia|hyperkala?emia|hypotension|angio-?o?edema|acute kidney injury|"
                  r"injection[- ]site)\b", re.I)
SECONDARY = re.compile(r"\bsecondary (?:efficacy )?(?:outcomes?|end ?points?)\s*(?:were|was|included|comprised|consisted of|"
                       r"of interest were|:)\s*(?P<list>[^.]{5,500})", re.I)


def _sentences(text):
    for block in re.split(r"\n+", text):
        for s in re.split(r"(?<=[.;])\s+(?=[A-Z(])", block):
            s = s.strip()
            if s:
                yield s


_CLAUSE_CUT = re.compile(r";|, but |, whereas |, while |, and |\. ", re.I)


def clause_of(s, start, end):
    """The clause that prints a number: from the last ';' / ', but' / ', whereas' / ', while' / ', and' before it, to the
    number (codex review 8 Oct d10#1 / #4: 'All-cause mortality was not reported, but aspirin reduced bleeding (RR 0.70'
    was labelled mortality; 'Denosumab was not evaluated, but risedronate ... (RR 0.80' passed as denosumab's)."""
    head = s[:start]
    cut = max((m.end() for m in _CLAUSE_CUT.finditer(head)), default=0)
    return s[cut:end]


def regex_inventory(text):
    """[{family, measure, estimate, lower, upper, span}] for every sentence printing a ratio / mean difference with an
    interval, labelled by the fixed families; plus the methods' named secondary outcomes. Matching runs on a 1:1
    normalised copy; every span is the ORIGINAL text at the same offsets."""
    hits, seen = [], set()
    for s in _sentences(text):
        n = s.translate(_NORM_1TO1)
        for m in EFFECT.finditer(n):
            a, b = (0, len(s)) if len(s) <= 400 else (max(0, m.start() - 250), m.end() + 60)
            span = s[a:b]
            clause = clause_of(s, m.start(), m.end())
            fam = "ALL_CAUSE_MORTALITY" if MORT.search(clause) else "HARM" if HARM.search(clause) else "OTHER"
            key = (fam, m.group("e"), m.group("l"), m.group("u"))
            if key in seen:
                continue
            seen.add(key)
            hits.append({"family": fam, "measure": m.group("m"), "estimate": _num(m.group("e")),
                         "lower": _num(m.group("l")), "upper": _num(m.group("u")), "span": span, "clause": clause})
    secs = [{"span": m.group(0)[:500], "list": m.group("list").strip()} for s in _sentences(text)
            for m in SECONDARY.finditer(s)]
    return hits, secs


# ------------------------------------------------------------------------------------------------ R2: recorded codex
INV_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["prespecified_secondaries", "outcomes"],
    "properties": {
        "prespecified_secondaries": {"type": "object", "additionalProperties": False, "required": ["names", "quote"],
                                     "properties": {"names": {"type": "array", "items": {"type": "string"}},
                                                    "quote": {"type": ["string", "null"]}}},
        "outcomes": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["name", "family", "contrast", "population", "measure", "estimate", "lower", "upper", "k",
                         "timepoint", "quote"],
            "properties": {
                "name": {"type": "string"},
                "contrast": {"type": "string"}, "population": {"type": ["string", "null"]},
                "family": {"type": "string", "enum": ["PRIMARY", "ALL_CAUSE_MORTALITY", "HARM", "OTHER_EFFICACY"]},
                "measure": {"type": "string"}, "estimate": {"type": ["string", "null"]},
                "lower": {"type": ["string", "null"]}, "upper": {"type": ["string", "null"]},
                "k": {"type": ["integer", "null"]}, "timepoint": {"type": ["string", "null"]},
                "quote": {"type": "string"}}}}}}

INV_INSTR = (
    "You are inventorying a published META-ANALYSIS. List EVERY outcome for which it prints a POOLED result (a point "
    "estimate with a two-sided interval, on a ratio scale such as HR / RR / OR, or a mean difference) in the text below. "
    "For each: its name in the article's own words; family = PRIMARY (the article's primary outcome), ALL_CAUSE_MORTALITY "
    "(death from any cause), HARM (adverse events, serious adverse events, discontinuation for adverse events, or a named "
    "harm) or OTHER_EFFICACY; contrast = the two things compared for THAT result, in the article's words (e.g. 'drug X "
    "vs placebo' -- in a network meta-analysis or a per-drug / per-subgroup result, the specific drug and comparator of "
    "that number, never the class); population = the subgroup or population THAT number is restricted to, in the "
    "article's words, or null when it is the whole analysis; list per-drug and per-subgroup results as SEPARATE entries; "
    "the measure as printed; the estimate, lower and upper bound EXACTLY as printed (strings); "
    "k = the number of trials pooled if printed beside it, else null; the timepoint if printed, else null; and quote = "
    "the shortest VERBATIM passage of the text that prints the name and the numbers together. Separately, if the "
    "methods name prespecified SECONDARY outcomes, list their names and give the verbatim sentence as quote (else "
    "names [] and quote null). Copy text exactly; never compute, convert or infer a number; omit an outcome rather than "
    "guess. Answer with JSON only.")


def inv_item(slug):
    pmid, cc, _, _, abstract = comparator_sources(slug)
    if cc:
        import g1_swap as sw
        text = sw.jats_text(open(os.path.join(ROOT, cc), encoding="utf-8", errors="replace").read())
        prompt = (INV_INSTR + f"\n\nCOMPARATOR PMID {pmid} (CC BY / CC0 full text)\n<<<TEXT\n{text[:180000]}\nTEXT>>>\n").encode("utf-8")
        dg = [{"ref": cc, "sha256": hashlib.sha256(open(os.path.join(ROOT, cc), "rb").read()).hexdigest(),
               "what": "the comparator meta's open JATS (CC BY / CC0), rendered to text, first 180000 chars"}]
        kind = "CC_FULL_TEXT"
    else:
        text = abstract
        prompt = (INV_INSTR + f"\n\nCOMPARATOR PMID {pmid} (title and abstract only: its full text is not CC BY / CC0)\n"
                  f"=== TITLE AND ABSTRACT ===\n{text}\n").encode("utf-8")
        dg = [{"ref": f"abstract PMID {pmid}", "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
               "what": "the comparator's PubMed title + abstract (its full text is not CC BY / CC0)"}]
        kind = "ABSTRACT_ONLY"
    return {"key": f"d10inv::{slug}::{pmid}::v2", "slug": slug, "pmid": pmid, "prompt": prompt, "text": text,
            "digests": dg, "schema": INV_SCHEMA, "source_kind": kind}


def gate_inventory(claim, text):
    """Gated R2: an outcome stands only with its quote verbatim in the text given and every printed number a whole
    token of that quote (g1_swap.pooled_gate, k checked when stated); the prespecified list only with its quote."""
    import g1_swap as sw
    nt = sw._norm(text)
    kept, refused = [], []
    for o in claim.get("outcomes") or []:
        pl = {"measure": o.get("measure"), "estimate": o.get("estimate"), "lower": o.get("lower"),
              "upper": o.get("upper"), "k": o.get("k"), "quote": o.get("quote")}
        pooled, k = sw.pooled_gate(pl, nt)
        if pooled is None and o.get("k") is not None:      # a k not printed in the quote drops k, never the result
            pooled, k = sw.pooled_gate(dict(pl, k=None), nt)
        if pooled is None or o.get("estimate") in (None, "") or o.get("lower") in (None, "") or o.get("upper") in (None, ""):
            refused.append({"name": o.get("name"), "why": "QUOTE_OR_NUMBERS_NOT_VERBATIM"})
            continue
        kept.append(dict(o, k=k))
    ps = claim.get("prespecified_secondaries") or {}
    pre = ps if (ps.get("names") and sw._quoted(ps.get("quote"), nt)) else {"names": [], "quote": None}
    return kept, refused, pre


def cmd_inventory(slugs, run=False):
    import g1_swap as sw
    from kgap import runs_store
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    import k_gap_forest_plot as fp
    runs = runs_store.load()
    items = [inv_item(s) for s in slugs]
    done = lambda it: (runs.get(it["key"]) or {}).get("prompt_sha256") == hashlib.sha256(it["prompt"]).hexdigest() and \
        (runs.get(it["key"]) or {}).get("state") == "RAN_OK" and \
        os.path.exists(os.path.join(REC_DIR, str(runs[it["key"]].get("record_id")) + ".json"))
    print("recovered from records:", sw.recover(items, runs, REC_DIR), flush=True)
    if run:
        sw._run_calls([it for it in items if not done(it)], runs, REC_DIR, mcl, ms, fp, slugs,
                      purpose=lambda it: f"D10 multi-outcome: inventory of comparator {it['pmid']} for {it['slug']} "
                                         f"({it['source_kind']}), rule D10-MULTI-OUTCOME-PROPOSAL-v1",
                      line="inventory", batch="d10inv", caller_file="scripts/g1_outcomes.py")
    for it in items:
        s = it["slug"]
        pmid, cc, rtext, rrefs, _ = comparator_sources(s)
        hits, secs = regex_inventory(rtext)
        kept, refused, pre, rid = [], [], {"names": [], "quote": None}, None
        if done(it):
            rid = runs[it["key"]]["record_id"]
            claim = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, rid + ".json"))).decode("utf-8"))
            kept, refused, pre = gate_inventory(claim, it["text"])
        out = {"slug": s, "comparator_pmid": pmid, "rule": "registry/outcome_amendments/D10_rule.json",
               "R1_regex": {"sources": rrefs, "hits": hits, "named_secondaries": secs},
               "R2_codex": {"source_kind": it["source_kind"], "record_id": rid, "outcomes": kept, "refused": refused,
                            "prespecified_secondaries": pre}}
        with open(os.path.join(OUT, f"{s}.inventory.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        fams = {}
        for o in kept:
            fams[o["family"]] = fams.get(o["family"], 0) + 1
        print(s, pmid, it["source_kind"], "R1 hits", len(hits), "mort", sum(h["family"] == "ALL_CAUSE_MORTALITY" for h in hits),
              "R2 kept", len(kept), fams, "refused", len(refused), "prespec", len(pre["names"]), flush=True)


# ------------------------------------------------------------------------------------------------------------ propose
_STOP = {"the", "and", "of", "in", "with", "for", "or", "to", "a", "an", "on", "at", "by", "vs", "versus", "do", "does",
         "change", "adults", "patients", "people", "compared", "from", "any", "all", "rate", "risk", "events", "event"}


def _words(t):
    return {w for w in re.findall(r"[a-z][a-z0-9-]{2,}", (t or "").lower()) if w not in _STOP}


def negation_differs(a, b):
    """One name negates a word the other asserts: 'nonfatal' / 'non-fatal' v 'fatal' (codex review 8 Oct d10#8)."""
    def neg(ws):
        return {re.sub(r"^non-?", "", w) for w in ws if re.match(r"^non-?\w{3,}", w)}
    na, nb = neg(a), neg(b)
    # only a CONTRADICTION: one name negates a word the other asserts. A word negated on one side and absent on the other
    # is not one (DOAC's composite primary names both 'nonfatal PE' and 'fatal PE')
    return bool((na & b) or (nb & a))


def is_our_primary(name, t):
    """The candidate IS our primary outcome: its words overlap our primary's name by >= half of either, or it contains
    one of our primary's specific keywords (>= 8 characters)."""
    po = t["primary_outcome"]
    a, b = _words(name), _words(po["name"])
    # Jaccard >= 0.5: one shared word ('death' in 'Death within 24 h' v 'Death due to bleeding') is not identity (7 Oct)
    if negation_differs(a, b):
        return False
    if a and b and len(a & b) / len(a | b) >= 0.5:
        return True
    return any(len(k) >= 8 and k.lower() in (name or "").lower() for k in po.get("keywords") or [])


def linked_to(name, t):
    """An outcome already declared in topics/<slug>.json (secondary or harm) that the candidate names -> its name."""
    low = (name or "").lower()
    for o in (t.get("secondary_outcomes") or []) + (t.get("harm_outcomes") or []):
        if _phrase_in(o["name"].lower(), low) or _phrase_in(low, o["name"].lower()) or \
                any(len(k) >= 6 and k.lower() == low for k in o.get("keywords") or []):
            return o["name"]
    return None


def _phrase_in(needle, hay):
    """A whole phrase, not negated by a 'non' / 'non-' / 'no ' prefix (codex review 8 Oct d10#2)."""
    return bool(needle) and bool(re.search(r"(?<![\w-])(?<!non-)(?<!non )(?<!no )" + re.escape(needle) + r"(?![\w-])", hay))


def _population_score(quote, t):
    return len(_words(quote) & _words(t.get("question")))


def _prespecified(name, pre):
    a = _words(name)
    return any(a and len(a & _words(n)) >= max(1, len(a) / 2) for n in pre.get("names") or [])


def candidates(inv, t):
    """Every inventoried outcome with a verbatim basis, as {name, family, measure, estimate, lower, upper, k, timepoint,
    quote, basis}. R2 (gated) first; R1 regex hits add ALL_CAUSE_MORTALITY / HARM entries only where R2 had none of
    that family (abstract-only reads), named by the fixed lexicon."""
    out, excluded = [], []
    pre = inv["R2_codex"]["prespecified_secondaries"]
    cls = class_level_printed(inv["R2_codex"]["outcomes"], t)
    for o in inv["R2_codex"]["outcomes"]:
        fam = "ALL_CAUSE_MORTALITY" if (MORT.search(o["name"]) or o["family"] == "ALL_CAUSE_MORTALITY") else o["family"]
        why = None if contrast_is_ours(o.get("contrast"), t, cls) else "OTHER_CONTRAST"
        why = why or (None if population_is_ours(o.get("population"), t) else "OTHER_POPULATION")
        c = dict(o, family=fam, basis=f"R2 {inv['R2_codex']['source_kind']} record {inv['R2_codex']['record_id']}",
                 prespecified=_prespecified(o["name"], pre))
        (excluded.append(dict(c, excluded=why)) if why else out.append(c))
    have = {c["family"] for c in out}
    named = _term_re(_intervention_terms(t))
    for h in inv["R1_regex"]["hits"]:
        if h["family"] == "ALL_CAUSE_MORTALITY" and "ALL_CAUSE_MORTALITY" not in have:
            nm = "All-cause mortality"
        elif h["family"] == "HARM" and "HARM" not in have:
            nm = HARM.search(h["span"]).group(1)
        else:
            continue
        c = {"name": nm, "family": h["family"], "contrast": None, "population": None, "measure": h["measure"],
             "estimate": h["estimate"], "lower": h["lower"], "upper": h["upper"], "k": None, "timepoint": None,
             "quote": h["span"], "basis": "R1 regex over the held comparator text", "prespecified": False}
        # a regex span has no typed contrast: it must at least NAME our intervention
        (out.append(c) if named.search(h.get("clause") or h["span"]) else
         excluded.append(dict(c, excluded="CLAUSE_DOES_NOT_NAME_OUR_INTERVENTION")))
    return out, excluded


GENERIC_CONTROL = ["placebo", "control", "usual care", "standard care", "standard of care", "no treatment"]


def _flat(v):
    if isinstance(v, str):
        return [v]
    if isinstance(v, dict):
        return [x for k, w in v.items() for x in [k] + _flat(w)]
    if isinstance(v, (list, tuple)):
        return [x for w in v for x in _flat(w)]
    return []


def _intervention_terms(t):
    """Our intervention's names: terms, agents (a list or a {agent: aliases} map) and class terms."""
    return [x for x in _flat(t.get("intervention_terms")) + _flat(t.get("intervention_agents")) +
            _flat(t.get("intervention_class_terms")) if len(x) >= 3]


def _term_re(terms):
    terms = [x for x in terms if x]
    if not terms:
        return re.compile(r"(?!x)x")              # matches nothing (codex review 8 Oct d10#6: '' matched every boundary)
    return re.compile(r"\b(" + "|".join(re.escape(x) for x in sorted(set(terms), key=len, reverse=True)) + r")", re.I)


def _general_terms(t):
    agents = {a.lower() for a in _flat(t.get("intervention_agents"))}
    return [x for x in _flat(t.get("intervention_class_terms")) + _flat(t.get("intervention_terms"))
            if len(x) >= 3 and x.lower() not in agents]


def class_level_printed(outcomes, t):
    """Does this comparator print ANY result whose contrast names our class (not one agent)?"""
    g = _general_terms(t)
    return bool(g) and any(_term_re(g).search(o.get("contrast") or "") for o in outcomes)


def contrast_is_ours(contrast, t, class_level_printed=True):
    """The result's own contrast names OUR intervention (an agent, a term or the class) AND our comparator (its terms or
    a generic control). A network meta-analysis's 'risedronate vs placebo' is not denosumab's result (7 Oct)."""
    c = contrast or ""
    comp = [x for x in (t.get("comparator_terms") or []) if len(x) >= 3]
    # a generic control is OUR comparator only when our comparator is itself a control (codex review 8 Oct d10#5:
    # 'aspirin versus placebo' passed for an aspirin-versus-clopidogrel topic)
    if any(_term_re(GENERIC_CONTROL).search(x) for x in comp):
        comp = comp + GENERIC_CONTROL
    if not (_term_re(_intervention_terms(t)).search(c) and _term_re(comp).search(c)):
        return False
    # a CLASS topic (>= 2 agents) whose comparator prints class-level results: the result must be the class's, never one
    # agent's split ('canagliflozin vs placebo' inside an SGLT2-inhibitor meta, 7 Oct). A comparator that pools ONE
    # agent only (iv-iron 39727669: FCM) has no class result -- its single-agent contrast IS the whole analysis.
    agents = _flat(t.get("intervention_agents"))
    names = list(t.get("intervention_agents").keys()) if isinstance(t.get("intervention_agents"), dict) else agents
    if len(names) >= 2 and class_level_printed:
        general = _general_terms(t)
        return bool(general and _term_re(general).search(c))
    return True


def population_is_ours(population, t):
    """The whole analysis (null), or a subgroup whose words overlap our protocol question / eligibility."""
    if not population:
        return True
    ours = f"{t.get('question') or ''} {t.get('eligibility_summary') or ''}"
    neg = re.compile(r"\b(?:without|excluding|non-?|no|not)\s+(\w+)", re.I)
    ours_neg = {w.lower() for w in neg.findall(ours)}
    # 'Adults without diabetes' shares 'diabetes' with 'adults with diabetes' -- and contradicts it (codex review 8 Oct)
    if any(w.lower() in _words(ours) and w.lower() not in ours_neg for w in neg.findall(population)):
        return False
    return bool(_words(population) & (_words(t.get("question")) | _words(t.get("eligibility_summary"))))


def propose(slug):
    """The committed rule (D10_rule.json) applied: P1 all-cause mortality, P2 key harms (one per distinct harm), P3 the
    comparator's prespecified secondaries with a printed result; our primary never; already-declared -> LINKED; at most 5
    NEW in family order, then the comparator's order. Where one outcome is printed for several populations, the entry
    whose quote shares most words with our protocol question is taken; a tie is flagged, never guessed."""
    t = topic(slug)
    inv = _j(os.path.join(OUT, f"{slug}.inventory.json"))
    allc, excluded = candidates(inv, t)
    cands = [c for c in allc if not is_our_primary(c["name"], t)]
    fam_of = lambda c: ("P1_ALL_CAUSE_MORTALITY" if c["family"] == "ALL_CAUSE_MORTALITY" else
                        "P2_KEY_HARMS" if c["family"] == "HARM" else
                        "P3_PRESPECIFIED_SECONDARIES" if c["family"] == "OTHER_EFFICACY" and c["prespecified"] else None)
    groups = {}
    for i, c in enumerate(cands):
        # an outcome we ALREADY declare is linked whatever family the reader gave it (DOAC bleeding was read as
        # OTHER_EFFICACY, 7 Oct): family labels decide only what is NEW
        f = fam_of(c) or ("LINK_ONLY" if linked_to(c["name"], t) else None)
        if not f:
            continue
        key = (f, "mortality" if f.startswith("P1") else " ".join(sorted(_words(c["name"]))))
        groups.setdefault(key, []).append((i, c))
    picked, linked, flags = [], [], []
    for (f, _), members in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[1][0][0])):
        best = max(_population_score(c["quote"], t) for _, c in members)
        top = [c for _, c in members if _population_score(c["quote"], t) == best]
        c = top[0]
        if len(top) > 1 and len({(x["estimate"], x["lower"], x["upper"]) for x in top}) > 1:
            flags.append({"outcome": c["name"], "flag": "SEVERAL_POPULATIONS_TIED", "entries": [x["quote"][:200] for x in top]})
            continue
        ln = linked_to(c["name"], t)
        entry = {"family": f, "name": c["name"], "comparator_result": {k: c.get(k) for k in
                 ("measure", "estimate", "lower", "upper", "k", "timepoint")}, "span": c["quote"], "basis": c["basis"]}
        (linked.append(dict(entry, linked_to=ln)) if ln else picked.append(entry))
    new = picked[:5]
    out = {"slug": slug, "comparator_pmid": inv["comparator_pmid"], "rule": "registry/outcome_amendments/D10_rule.json",
           "new_outcomes": new, "beyond_cap": picked[5:], "linked_existing": linked, "flags": flags,
           "not_proposed_primary_like": [c["name"] for c in allc if is_our_primary(c["name"], t)],
           "excluded": [{k: c.get(k) for k in ("name", "contrast", "population", "excluded", "basis")} for c in excluded]}
    with open(os.path.join(OUT, f"{slug}.proposal.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return out


def cmd_propose(slugs):
    for s in slugs:
        o = propose(s)
        print(f"## {s}: new {len(o['new_outcomes'])} linked {len(o['linked_existing'])} flags {len(o['flags'])}")
        for e in o["new_outcomes"]:
            r = e["comparator_result"]
            print(f"   NEW {e['family'][:2]} {e['name'][:60]} | {r['measure']} {r['estimate']} ({r['lower']}, {r['upper']}) k={r['k']} | {e['basis'][:20]}")
        for e in o["linked_existing"]:
            print(f"   LINK {e['name'][:50]} -> {e['linked_to']}")
        for e in o["flags"]:
            print(f"   FLAG {e['flag']} {e['outcome'][:50]}")


# ----------------------------------------------------------------------------------------------------------- register
AMEND_DATE = "2026-10-07"
AMEND_HEAD = f"## Amendment {AMEND_DATE} (D10 multi-outcome: outcomes the comparator also reports)"


def estimand_of(measure):
    m = (measure or "").upper()
    for pat, est in ((r"\bSMD\b|STANDARDI[SZ]ED MEAN", "SMD"), (r"\bW?MD\b|MEAN DIFFERENCE", "MD"),
                     (r"\bA?HR\b|HAZARD", "HR"), (r"\bRR\b|RISK RATIO|RELATIVE RISK", "RR"), (r"\bOR\b|ODDS", "OR")):
        if re.search(pat, m):
            return est
    return None


_LEAD = re.compile(r"^(?:the\s+)?(?:incidence|rate|risk|occurrence|mean|change in|variations? in)\s+(?:of\s+)?", re.I)


def spec_of(entry):
    """The outcome spec the rule fixes: the comparator's own wording; estimand = its printed measure family; keywords =
    its outcome phrase (and the phrase without a leading 'incidence of' / 'mean' ...), plus the fixed P1 synonyms."""
    rule = _j(RULE)
    name = entry["name"].strip()
    phrase = name.lower()
    kws = [phrase] + ([_LEAD.sub("", phrase)] if _LEAD.sub("", phrase) != phrase else [])
    if entry["family"].startswith("P1"):
        kws += rule["proposal"]["P1_synonyms"]
    r = entry["comparator_result"]
    spec = {"name": name[0].upper() + name[1:], "estimand": estimand_of(r.get("measure")),
            "keywords": list(dict.fromkeys(kws)), "timepoint": r.get("timepoint") or "trial-reported follow-up",
            "amendment": f"{AMEND_DATE} D10 ({entry['family']})"}
    if entry["family"].startswith("P2"):
        spec["population"] = "trial-reported randomized comparison / safety population"
    return spec


def _excerpt(span, n=220):
    s = re.sub(r"\s+", " ", span or "").strip()
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + " …"


def amendment_text(slug, prop, specs, rule_sha, prop_sha):
    lines = [AMEND_HEAD,
             "**Status: registered BEFORE any extraction of these outcomes; retrospective with respect to the trial pool**",
             "(the pool, search and eligibility were fixed before D10 and are unchanged). Decision: Mahmood D10 (relayed",
             f"{AMEND_DATE}): add outcomes the comparator meta also reports -- all-cause mortality, key harms and its",
             f"prespecified secondaries. Rule `registry/outcome_amendments/D10_rule.json` (commit {rule_sha}); proposal",
             f"`registry/outcome_amendments/{slug}.proposal.json` (commit {prop_sha}). The outcomes were chosen from the",
             f"comparator's (PMID {prop['comparator_pmid']}) own text by that rule alone; no trial-level result for them",
             "was extracted or viewed by this lane before this amendment.", ""]
    for e, sp in zip(prop["new_outcomes"], specs):
        kind = "harm outcome" if e["family"].startswith("P2") else "secondary outcome"
        r = e["comparator_result"]
        lines += [f"- **New {kind}: {sp['name']}** ({e['family']}). Estimand {sp['estimand']}; timepoint {sp['timepoint']};",
                  f"  keywords {', '.join(sp['keywords'])}. The comparator prints {r.get('measure')} {r.get('estimate')}",
                  f"  ({r.get('lower')} to {r.get('upper')}): \"{_excerpt(e['span'])}\" [{e['basis'].split(' record ')[0]}]."]
    for e in prop["linked_existing"]:
        r = e["comparator_result"]
        lines += [f"- **Linked, already registered: {e['linked_to']}** -- compared with the comparator's \"{e['name']}\",",
                  f"  {r.get('measure')} {r.get('estimate')} ({r.get('lower')} to {r.get('upper')}). No change to its spec."]
    lines += ["- **Extraction.** The served ladder is unchanged (abstract, CT.gov results, held open full texts, verified",
              "  inputs); trials it leaves without a value may be read by recorded codex over open sources only (CC BY / CC0",
              "  full text, abstracts, AACT, FDA, EMA with acknowledgement, NICE OGL/CC), every value quote-gated.",
              "- **Comparison.** Each outcome's pooled result is compared with the comparator's printed result on the",
              "  comparator's measure; a measure difference is reported, never converted. Nothing is served until",
              "  Mahmood signs its notice.", ""]
    return "\n".join(lines)


def cmd_register(slugs):
    import subprocess
    sha = lambda p: subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%h", "--", p], capture_output=True,
                                   text=True).stdout.strip() or None
    rule_sha = sha("registry/outcome_amendments/D10_rule.json")
    for s in slugs:
        prop = _j(os.path.join(OUT, f"{s}.proposal.json"))
        prop_sha = sha(f"registry/outcome_amendments/{s}.proposal.json")
        if not prop["new_outcomes"] and not prop["linked_existing"]:
            print(s, "nothing to register")
            continue
        if not (rule_sha and prop_sha):
            raise SystemExit(f"{s}: the rule and the proposal must be COMMITTED before registration")
        pp = os.path.join(ROOT, "protocols", f"{s}.md")
        md = open(pp, encoding="utf-8").read()
        if AMEND_HEAD in md:
            print(s, "already registered (kept: an amendment is never rewritten)")
            continue
        tp = os.path.join(ROOT, "topics", f"{s}.json")
        t = _j(tp)
        specs = [spec_of(e) for e in prop["new_outcomes"]]
        have = {o["name"].lower() for o in (t.get("secondary_outcomes") or []) + (t.get("harm_outcomes") or [])}
        clash = [sp["name"] for sp in specs if sp["name"].lower() in have or not sp["estimand"]]
        if clash:
            raise SystemExit(f"{s}: refusing -- name clash or no estimand for {clash}")
        for e, sp in zip(prop["new_outcomes"], specs):
            t.setdefault("harm_outcomes" if e["family"].startswith("P2") else "secondary_outcomes", []).append(sp)
        with open(tp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(t, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(pp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(md.rstrip("\n") + "\n\n" + amendment_text(s, prop, specs, rule_sha, prop_sha))
        print(s, "registered", len(specs), "new,", len(prop["linked_existing"]), "linked", flush=True)


# ------------------------------------------------------------------------------------------------------------ extract
def d10_outcomes(slug):
    """[(our outcome name, spec, kind, comparator entry)] for the registered D10 outcomes and the linked existing ones."""
    t = topic(slug)
    prop = _j(os.path.join(OUT, f"{slug}.proposal.json"))
    out = []
    by = {e["name"].lower(): e for e in prop["new_outcomes"]}
    for kind in ("secondary_outcomes", "harm_outcomes"):
        for sp in t.get(kind) or []:
            if str(sp.get("amendment", "")).startswith(AMEND_DATE + " D10"):
                e = by.get(sp["name"].lower())
                out.append((sp["name"], sp, "harm" if kind == "harm_outcomes" else "efficacy", e))
    # linked: the best-matching comparator entry per already-registered outcome (most shared words)
    best = {}
    for e in prop["linked_existing"]:
        sc = len(_words(e["name"]) & _words(e["linked_to"]))
        if e["linked_to"] not in best or sc > best[e["linked_to"]][0]:
            best[e["linked_to"]] = (sc, e)
    allspec = {o["name"]: (o, k) for k in ("secondary_outcomes", "harm_outcomes") for o in t.get(k) or []}
    for name, (_, e) in best.items():
        sp, k = allspec[name]
        out.append((name, sp, "harm" if k == "harm_outcomes" else "efficacy", e))
    return out


def _row_of(tr):
    """A served-ladder trial row: its arm counts live on ai / n1i / ci / n2i ('ci' = control EVENTS, not an interval;
    reading effect_object dropped every count, 7 Oct). The source sentence is kept whole for the identity guard."""
    cnt = dict(zip(("events_t", "n_t", "events_c", "n_c"), (tr.get("ai"), tr.get("n1i"), tr.get("ci"), tr.get("n2i"))))
    cnt = {k: int(v) for k, v in cnt.items() if isinstance(v, (int, float)) and v == int(v)}
    return {"id": tr.get("id"), "scale": tr.get("scale"), "effect": tr.get("effect"), "ci_low": tr.get("ci_low"),
            "ci_high": tr.get("ci_high"), "counts": cnt if len(cnt) == 4 else None,
            "provenance": tr.get("provenance"), "source": tr.get("source")}


def _fmt(v):
    return [f"{v:g}", f"{v:.2f}", f"{v:.1f}"] if isinstance(v, float) else [str(v)]


def ladder_misbound(r, spec):
    """The served ladder's row is about ANOTHER outcome -> the reason, else None (the row is not used and is named).
      structured CT.gov  the posted outcome title must pass g1_tracker.binding_verdict for OUR outcome ('HF
                         Hospitalisations' is not 'Non-HF hospitalizations')
      abstract           the row's number must sit in the SAME clause as our outcome's words: the text since the last
                         ')' or ';' before the number names a keyword (DECLARE's renal HR 0.76 preceded 'death from any
                         cause')"""
    import g1_tracker as gt
    src = r.get("source") or ""
    kws = [k for k in (spec.get("keywords") or []) if len(k) >= 4] + [spec["name"]]
    m = re.search(r"outcome '([^']+)'", src)
    if m:
        bv = gt.binding_verdict(spec["name"], kws, m.group(1), 2)
        return None if bv["verdict"] == "BINDABLE" else f"STRUCTURED_TITLE_IS_ANOTHER_OUTCOME: '{m.group(1)}' ({bv['gate']})"
    v = r.get("effect") if r.get("effect") is not None else (r.get("counts") or {}).get("events_t")
    if v is None:
        return None
    body = src.split(":", 1)[1] if ":" in src[:80] else src
    pos = min((p.start() for f in _fmt(v) for p in [re.search(rf"(?<![\d.]){re.escape(f)}(?![\d])", body)] if p),
              default=None)
    if pos is None:
        # FAIL CLOSED: a number the row's own source does not show cannot be tied to our outcome (STAREE's stored
        # source stops before its HR 0.94 -- this branch returned 'fine' and the composite passed, 7 Oct)
        return "NUMBER_NOT_IN_THE_ROW'S_SOURCE (the clause cannot be checked)"
    seg = body[:pos]
    seg = seg[max(seg.rfind(")"), seg.rfind(";")) + 1:]
    hit = next((k for k in kws if k.lower() in seg.lower()), None)
    if not hit:
        return f"NUMBER_NOT_IN_THE_OUTCOME'S_CLAUSE: '{_excerpt(seg, 120)}'"
    # a QUALIFIED subset: 'cardiac serious adverse events' is not serious adverse events (IRONMAN, 7 Oct)
    i = seg.lower().find(hit.lower())
    prev = re.findall(r"[A-Za-z-]+", seg[:i])[-1:] if i > 0 else []
    if prev and QUALIFIER.fullmatch(prev[0]):
        return f"QUALIFIED_SUBSET: '{prev[0]} {hit}'"
    # a COMPOSITE named in the clause: the tracker's own definition / composite gates on the clause as a title
    # ('Death from any cause, dementia, or persistent physical disability' is not all-cause mortality: STAREE, 7 Oct)
    bv = gt.binding_verdict(spec["name"], kws, seg, 2)
    if bv["verdict"] != "BINDABLE" and bv.get("gate") == "ESTIMAND":
        return f"COMPOSITE_OR_OTHER_DEFINITION: {_excerpt(bv.get('reason'), 160)}"
    # ...and a plain ENUMERATION around the keyword ('X, Y, or Z occurred'), which that gate does not read
    after, before = seg[i + len(hit):], seg[:i].rstrip()
    if re.match(r"\s*(?:,\s*[^,;()]{2,60}){0,4},?\s+(?:or|and/or)\s+\w", after) or \
            re.search(r"(?:,|\bor|\band/or)$", before):
        return f"COMPOSITE_ENUMERATION: '{_excerpt(seg[max(0, i - 60):i + len(hit) + 80], 160)}'"
    return None


QUALIFIER = re.compile(r"cardiac|cardiovascular|renal|kidney|hepatic|liver|gastrointestinal|respiratory|pulmonary|"
                       r"neurologic(?:al)?|psychiatric|ocular|skin|infusion|injection|treatment-related|drug-related|"
                       r"related|fatal|non-fatal|nonfatal|bleeding|infectious|vascular", re.I)


def _arm(title, t):
    """'intervention' / 'control' / None for a posted group title, by OUR terms: the intervention names one of our agents /
    terms (a 'placebo for <drug>' clause is not the drug); the control names our comparator or a generic control and no
    intervention term."""
    import g1_binding_aact as ba
    rest = ba.PLACEBO_FOR.sub(" ", title or "")
    iv = bool(_term_re(_intervention_terms(t)).search(rest))
    ct = bool(_term_re([x for x in (t.get("comparator_terms") or []) if len(x) >= 3] + GENERIC_CONTROL).search(rest))
    return "intervention" if iv and not ct else "control" if ct and not iv else None   # both / neither: unmapped


def _two_arms(groups, t):
    """groups: [(title, affected, at_risk)] -> (e_t, n_t, e_c, n_c, refusal). Intervention arms SUMMED (one group, the
    shared control counted once); exactly one control; a 'total' group ignored."""
    iv, ct = [], []
    for title, a, n in groups:
        if re.fullmatch(r"\s*total\s*", title or "", re.I):
            continue
        role = _arm(title, t)
        (iv if role == "intervention" else ct if role == "control" else []).append((a, n, title))
        if role is None:
            return None, f"UNMAPPED_GROUP:{(title or '')[:60]}"
    if len(ct) != 1 or not iv:
        return None, f"ARMS:{len(iv)}_intervention_{len(ct)}_control"
    if any(x[0] is None or x[1] in (None, 0) for x in iv + ct):
        return None, "COUNT_MISSING"
    return (sum(x[0] for x in iv), sum(x[1] for x in iv), ct[0][0], ct[0][1]), None


def _aact_rows(name, nct):
    from kgap import aact_adapter as aa
    return list(aa._rows(name, {nct}))


def is_total_sae(name):
    """'(Incidence of) serious adverse events' -- never a qualified subset ('Cardiac serious adverse events'), which the
    AACT 'Total, serious adverse events' row does not measure (codex review 8 Oct d10#3)."""
    return bool(re.fullmatch(r"(?:total |any |all )?serious adverse events?", _LEAD.sub("", (name or "").strip().lower())))


def aact_typed(nct, outcome_name, spec, t):
    """Typed AACT rungs for one (trial, outcome): TC reported_event_totals (all-cause mortality / serious adverse
    events), TD a reported_events term equal to one of the outcome's keywords. -> (row or None, [refusals])."""
    from kgap import aact_adapter as aa
    snap = (aa.snapshot() or {}).get("id")
    titles = {r["ctgov_group_code"]: r.get("title") for r in _aact_rows("result_groups.txt", nct)
              if (r.get("result_type") or "").lower().startswith("reported event")}
    refusals = []
    kws = [k.lower() for k in spec.get("keywords") or []]
    is_mort = any(MORT.search(k) for k in kws) or bool(MORT.search(outcome_name))
    is_sae = is_total_sae(outcome_name)
    if is_mort or is_sae:
        cls = "Total, all-cause mortality" if is_mort else "Total, serious adverse events"
        rows = [r for r in _aact_rows("reported_event_totals.txt", nct) if r.get("classification") == cls]
        groups = [(titles.get(r["ctgov_group_code"]), _int(r.get("subjects_affected")), _int(r.get("subjects_at_risk")))
                  for r in rows]
        if groups:
            v, why = _two_arms(groups, t)
            if v:
                span = " | ".join(f"{g[0]}: {g[1]}/{g[2]}" for g in groups)
                return {"rung": "AACT_EVENT_TOTALS", "counts": dict(zip(("events_t", "n_t", "events_c", "n_c"), v)),
                        "span": f"AACT {snap} {nct} reported_event_totals '{cls}': {span}"}, refusals
            refusals.append({"rung": "AACT_EVENT_TOTALS", "why": why})
    if not is_mort:
        ev = [r for r in _aact_rows("reported_events.txt", nct)
              if (r.get("adverse_event_term") or "").strip().lower() in kws]
        types = {r.get("event_type") for r in ev}
        if len(types) > 1:
            refusals.append({"rung": "AACT_REPORTED_EVENTS", "why": "TERM_IN_SERIOUS_AND_OTHER (patients may be counted twice)"})
        elif ev:
            terms = {r["adverse_event_term"].strip().lower() for r in ev}
            if len(terms) > 1:
                refusals.append({"rung": "AACT_REPORTED_EVENTS", "why": f"SEVERAL_MATCHING_TERMS:{sorted(terms)}"})
            else:
                groups = [(titles.get(r["ctgov_group_code"]), _int(r.get("subjects_affected")), _int(r.get("subjects_at_risk")))
                          for r in ev]
                v, why = _two_arms(groups, t)
                if v:
                    span = " | ".join(f"{g[0]}: {g[1]}/{g[2]}" for g in groups)
                    return {"rung": "AACT_REPORTED_EVENTS", "counts": dict(zip(("events_t", "n_t", "events_c", "n_c"), v)),
                            "span": f"AACT {snap} {nct} reported_events {ev[0].get('event_type')} '{ev[0]['adverse_event_term']}': {span}"}, refusals
                refusals.append({"rung": "AACT_REPORTED_EVENTS", "why": why})
    return None, refusals


def _int(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def cmd_extract(slugs):
    """Stage 1: the served ladder in memory (k_gap_counterfactual.build_with_held_sources; docs/reviews never written)
    -> each D10 / linked outcome's rows and absences; then the typed AACT rungs for the trials the ladder left empty.
    -> registry/outcome_amendments/<slug>.extraction.json"""
    import k_gap_counterfactual as cf
    for s in slugs:
        outs = d10_outcomes(s)
        if not outs:
            print(s, "no D10 outcomes")
            continue
        t = topic(s)
        recs = {r["id"]: r for r in _j(os.path.join(ROOT, "cache", s, "records.json"))["records"]}
        core, _ = cf.build_with_held_sources(s)
        by = {o["name"]: o for o in core["outcomes"]}
        pool_ids = sorted({str(x.get("id")) for o in core["outcomes"]
                           for x in (o.get("trials") or []) + (o.get("declared_absent_trials") or [])})
        res = {"slug": s, "comparator_pmid": t["comparator_pmid"], "pool": [], "outcomes": []}
        for pid in pool_ids:
            pm = pid.replace("PMID ", "")
            nct = (recs.get(pm) or {}).get("nct")
            res["pool"].append({"id": pid, "nct": nct if isinstance(nct, str) else (nct or [None])[0]})
        for name, sp, kind, comp in outs:
            o = by.get(name) or {}
            rows = [_row_of(tr) for tr in o.get("trials") or []]
            have = {r["id"] for r in rows}
            typed, gaps = [], []
            for p in res["pool"]:
                if p["id"] in have:
                    continue
                row, refusals = aact_typed(p["nct"], name, sp, t) if p["nct"] else (None, [{"why": "NO_NCT"}])
                (typed.append(dict(row, id=p["id"], nct=p["nct"])) if row else
                 gaps.append({"id": p["id"], "nct": p["nct"], "typed_refusals": refusals}))
            res["outcomes"].append({"name": name, "kind": kind, "spec": sp,
                                    "comparator_result": (comp or {}).get("comparator_result"),
                                    "comparator_name": (comp or {}).get("name"), "comparator_span": (comp or {}).get("span"),
                                    "ladder_rows": rows, "ladder_result": o.get("result"),
                                    "ladder_absent": [{"id": a.get("id"), "reason_code": a.get("reason_code")}
                                                      for a in o.get("declared_absent_trials") or []],
                                    "typed_rows": typed, "gaps": gaps})
            print(s, "|", name[:40], "| ladder", len(rows), "| typed", len(typed), "| gaps", len(gaps), flush=True)
        with open(os.path.join(OUT, f"{s}.extraction.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, ensure_ascii=False, default=str)
            fh.write("\n")


# ------------------------------------------------------------------------------------------- acquire (recorded rung)
ACQ_REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "d10_extract")


def outcome_cfg(t, spec):
    """The topic config with the D10 outcome in the primary slot: g1_trial_acquire's evidence builder, deterministic
    readers and gate all read cfg['primary_outcome'] -- unchanged code, pointed at this outcome."""
    po = {k: spec.get(k) for k in ("name", "keywords", "estimand", "timepoint", "population") if spec.get(k) is not None}
    return dict(t, primary_outcome=po)


def acquire_items(slug):
    """One item per (gap trial, D10 outcome) left by extract stage 1: deterministic readers first (typed_first); an item
    carries a prompt only when an open source exists and nothing deterministic admitted a value."""
    import g1_trial_acquire as ta
    t = topic(slug)
    ex = _j(os.path.join(OUT, f"{slug}.extraction.json"))
    items, settled = [], []
    # ONE AACT detail pass for every NCT before any evidence() (each call would otherwise stream the 3 GB files)
    ta.aact_detail(sorted({n for o in ex["outcomes"] for g in o["gaps"] for n in
                           [g.get("nct")] + list(ta.registered_ncts(g["id"].replace("PMID ", "")) if str(g["id"]).startswith("PMID ") else [])
                           if n}))
    for o in ex["outcomes"]:
        cfg = outcome_cfg(t, o["spec"])
        for g in o["gaps"]:
            pmid = g["id"].replace("PMID ", "") if str(g["id"]).startswith("PMID ") else None
            ncts = sorted({n for n in [g.get("nct")] + list(ta.registered_ncts(pmid) if pmid else []) if n})
            tg = {"slug": slug, "label": f"{g['id']} :: {o['name']}", "pmid": pmid, "ncts": ncts}
            try:
                ev, held = ta.evidence(tg, cfg, str(t["comparator_pmid"]))
            except Exception as exc:  # noqa: BLE001 - recorded, never fatal
                settled.append({"outcome": o["name"], "id": g["id"], "state": "EVIDENCE_ERROR", "why": str(exc)[:200]})
                continue
            v, adm = ta.typed_first(tg, cfg, held)
            if v == "ADMITTED":
                settled.append({"outcome": o["name"], "id": g["id"], "state": "TYPED_ADMITTED", "kind": adm["kind"],
                                "span": adm["span"], "source": adm["source"], "row": _row_dict(adm["row"])})
                continue
            if not any(a.get("state") == "POSTED" for a in ev["aact"].values()) and not held["text"] \
                    and not ev.get("regulatory"):
                settled.append({"outcome": o["name"], "id": g["id"], "state": "NO_OPEN_SOURCE"})
                continue
            p = (ta.INSTR + "\n\n=== EVIDENCE ===\n" + json.dumps(ev, ensure_ascii=False, indent=0, default=str)).encode("utf-8")
            psha = hashlib.sha256(p).hexdigest()
            items.append({"key": f"d10ext::{slug}::{g['id']}::{o['name']}", "slug": slug, "pmid": g["id"],
                          "outcome": o["name"], "prompt": p, "schema": ta.SCHEMA, "_held": held, "_cfg": cfg,
                          "digests": [{"ref": "evidence", "sha256": psha,
                                       "what": "inline evidence: AACT snapshot rows, PMC OA / CC Unpaywall text, FDA / "
                                               "EMA / NICE windows, meta rows (g1_trial_acquire.evidence, D10 outcome)"}]})
    return items, settled


def _row_dict(row):
    return {k: getattr(row, k, None) for k in ("measure", "effect", "lower", "upper", "events_t", "n_t", "events_c", "n_c")}


def cmd_acquire(slugs, run=False):
    import g1_swap as sw
    import g1_trial_acquire as ta
    from kgap import runs_store
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    import k_gap_forest_plot as fp
    runs = runs_store.load()
    for s in slugs:
        if not os.path.exists(os.path.join(OUT, f"{s}.extraction.json")):
            print(s, "no extraction (run extract first)")
            continue
        items, settled = acquire_items(s)
        done = lambda it: (runs.get(it["key"]) or {}).get("prompt_sha256") == hashlib.sha256(it["prompt"]).hexdigest() \
            and (runs.get(it["key"]) or {}).get("state") == "RAN_OK" and \
            os.path.exists(os.path.join(ACQ_REC_DIR, str(runs[it["key"]].get("record_id")) + ".json"))
        print(s, "items", len(items), "settled without a call", len(settled), "recovered", sw.recover(items, runs, ACQ_REC_DIR),
              flush=True)
        if run:
            sw._run_calls([it for it in items if not done(it)], runs, ACQ_REC_DIR, mcl, ms, fp, [s],
                          purpose=lambda it: f"D10 multi-outcome: {it['slug']} / {it['pmid']} / {it['outcome'][:40]} "
                                             f"(open sources only; g1_trial_acquire gates)",
                          line="acquire", batch="d10ext", caller_file="scripts/g1_outcomes.py")
        out = list(settled)
        for it in items:
            if not done(it):
                out.append({"outcome": it["outcome"], "id": it["pmid"], "state": "NOT_RUN"})
                continue
            rid = runs[it["key"]]["record_id"]
            resp = json.loads(ms.replay(ms.load_record(os.path.join(ACQ_REC_DIR, rid + ".json"))).decode("utf-8"))
            verdict, adm = ta.gate(resp, it["_held"], it["_cfg"], s)
            e = {"outcome": it["outcome"], "id": it["pmid"], "state": verdict, "record_id": rid,
                 "model_verdict": resp.get("verdict"), "why": resp.get("why")}
            if verdict == "ADMITTED":
                e.update(kind=adm["kind"], span=adm.get("span"), quote=adm.get("quote"), source=adm["source"],
                         row=_row_dict(adm["row"]))
            out.append(e)
        p = os.path.join(OUT, f"{s}.acquired.json")
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"slug": s, "rows": out}, fh, indent=1, ensure_ascii=False, default=str)
            fh.write("\n")
        from collections import Counter
        print(s, dict(Counter(e["state"] for e in out)), flush=True)


# ------------------------------------------------------------------------------------------------------------ compare
def _f(x):
    if x in (None, ""):
        return None
    try:
        return float(re.sub(r"(?<=\d)·(?=\d)", ".", str(x)).replace("−", "-").replace("–", "-"))
    except ValueError:
        return None


def our_rows(slug, o, acquired):
    """Every row we hold for one outcome: ladder (served path), typed AACT, and gated recorded rows (ADMITTED only).
    -> ([{id, source_kind, measure, effect, lower, upper, events_t, n_t, events_c, n_c, basis}], [misbound ladder rows])"""
    rows, misbound = [], []
    for r in o["ladder_rows"]:
        c = r.get("counts") or {}
        why = ladder_misbound(r, o["spec"])
        if why:
            misbound.append({"id": r["id"], "why": why, "source": _excerpt(r.get("source"), 300)})
            continue
        rows.append({"id": r["id"], "source_kind": "LADDER", "measure": (r.get("scale") or "").upper(), "effect": r.get("effect"),
                     "lower": r.get("ci_low"), "upper": r.get("ci_high"), **{k: c.get(k) for k in ("events_t", "n_t", "events_c", "n_c")},
                     "basis": r.get("source")})
    for r in o["typed_rows"]:
        rows.append({"id": r["id"], "source_kind": r["rung"], "measure": None, "effect": None, "lower": None, "upper": None,
                     **r["counts"], "basis": r["span"]})
    for a in acquired:
        if a.get("outcome") == o["name"] and a.get("state") in ("ADMITTED", "TYPED_ADMITTED"):
            w = a["row"]
            rows.append({"id": a["id"], "source_kind": "ACQUIRED_" + str(a.get("kind")), "measure": (w.get("measure") or "").upper(),
                         "effect": _f(w.get("effect")), "lower": _f(w.get("lower")), "upper": _f(w.get("upper")),
                         **{k: w.get(k) for k in ("events_t", "n_t", "events_c", "n_c")},
                         "basis": f"{a.get('source')} | {_excerpt(a.get('span') or a.get('quote'), 300)}"
                                  + (f" | record {a['record_id']}" if a.get("record_id") else "")})
    return rows, misbound


def to_study(r, measure):
    """A synth.Study on the COMPARATOR's measure, or (None, why). Counts pool as that measure (OR / RR) directly; an
    effect pools only when printed on that measure; anything else is a MEASURE_DIFFERENCE -- never converted."""
    from harness import synth
    cnt = all(isinstance(r.get(k), int) for k in ("events_t", "n_t", "events_c", "n_c"))
    if cnt and measure in ("OR", "RR") and r["n_t"] > 0 and r["n_c"] > 0 and r["events_t"] <= r["n_t"] and r["events_c"] <= r["n_c"]:
        return synth.Study(label=r["id"], ai=r["events_t"], n1i=r["n_t"], ci=r["events_c"], n2i=r["n_c"], measure=measure,
                           derivation="reported"), None
    if r.get("effect") is not None and r.get("lower") is not None and r.get("upper") is not None and \
            (r.get("measure") or "") == measure:
        return synth.Study(label=r["id"], effect=float(r["effect"]), ci_low=float(r["lower"]), ci_high=float(r["upper"]),
                           measure=measure, derivation="reported"), None
    return None, f"MEASURE_DIFFERENCE: ours {r.get('measure') or 'counts'} vs comparator {measure} (never converted)"


def compare_outcome(slug, o, acquired, pool_n):
    import g1_tracker as gt
    from harness import synth
    cr = o.get("comparator_result") or {}
    m = estimand_of(cr.get("measure")) or (o["spec"].get("estimand") or "").upper()
    theirs = {"estimate": _f(cr.get("estimate")), "ci_low": _f(cr.get("lower")), "ci_high": _f(cr.get("upper"))}
    rows, misbound = our_rows(slug, o, acquired)
    studies, md = [], []
    for r in rows:
        st, why = to_study(r, m)
        (studies.append(st) if st else md.append({"id": r["id"], "why": why, "measure": r.get("measure"),
                                                  "effect": r.get("effect"), "lower": r.get("lower"), "upper": r.get("upper")}))
    out = {"outcome": o["name"], "kind": o["kind"], "comparator": {"name": o.get("comparator_name"), "measure": m,
           **theirs, "k": cr.get("k"), "span": o.get("comparator_span")}, "our_rows": rows, "ladder_rows_misbound": misbound, "measure_differences": md,
           "k_ours_on_measure": len(studies), "pool_trials": pool_n,
           "basis_note": "the comparator printed a POOLED result only (no per-trial rows): our pool vs its printed pool; "
                         "the two trial sets can differ"}
    if None in theirs.values():
        out["verdict"] = {"verdict": "COMPARATOR_RESULT_NOT_TYPED"}
        return out
    if studies:
        p = synth.pool(studies, scale=m)
        ours = {"estimate": p.estimate, "ci_low": p.ci_low, "ci_high": p.ci_high}
        out["ours"] = {"k": p.k, "measure": m, **{k: round(v, 4) for k, v in ours.items()}, "tau2": round(p.tau2, 4),
                       "ci_provenance": p.ci_provenance}
        out["verdict"] = gt.result_verdict(ours, theirs, m)
    elif md:
        # only other-scale rows: the same-conclusion test (as the primary), never a conversion
        scales = {d["measure"] for d in md}
        if len(scales) == 1 and all(d["effect"] is not None for d in md):
            sc = scales.pop()
            p = synth.pool([synth.Study(label=d["id"], effect=float(d["effect"]), ci_low=float(d["lower"]),
                                        ci_high=float(d["upper"]), measure=sc, derivation="reported") for d in md], scale=sc)
            ours = {"estimate": p.estimate, "ci_low": p.ci_low, "ci_high": p.ci_high}
            out["ours"] = {"k": p.k, "measure": sc, **{k: round(v, 4) for k, v in ours.items()}, "ci_provenance": p.ci_provenance}
            same = gt._concl(ours, sc) == gt._concl(theirs, m)
            out["verdict"] = {"verdict": "MEASURE_DIFFERENCE_SAME_CONCLUSION" if same else "DIFFERENT_CONCLUSION",
                              "basis": f"our {sc} vs the comparator's {m}: never converted"}
        else:
            out["verdict"] = {"verdict": "MEASURE_DIFFERENCE_NOT_POOLABLE"}
    else:
        out["verdict"] = {"verdict": "NO_ROWS"}
    return out


def cmd_compare(slugs):
    for s in slugs:
        p = os.path.join(OUT, f"{s}.extraction.json")
        if not os.path.exists(p):
            continue
        ex = _j(p)
        ap = os.path.join(OUT, f"{s}.acquired.json")
        acquired = _j(ap)["rows"] if os.path.exists(ap) else []
        res = {"slug": s, "comparator_pmid": ex["comparator_pmid"], "outcomes": [compare_outcome(s, o, acquired, len(ex["pool"]))
                                                                                 for o in ex["outcomes"]]}
        with open(os.path.join(OUT, f"{s}.comparison.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, ensure_ascii=False, default=str)
            fh.write("\n")
        for c in res["outcomes"]:
            o, t = c.get("ours") or {}, c["comparator"]
            print(f"{s} | {c['outcome'][:38]} | ours k={o.get('k')} {o.get('measure')} {o.get('estimate')} ({o.get('ci_low')}, "
                  f"{o.get('ci_high')}) of {c['pool_trials']} | theirs {t['measure']} {t['estimate']} ({t['ci_low']}, {t['ci_high']}) "
                  f"| {c['verdict']['verdict']}", flush=True)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    cmd, *args = sys.argv[1:]
    run = "--run" in args
    args = [a for a in args if not a.startswith("--")]
    {"inventory": lambda a: cmd_inventory(a, run=run), "propose": cmd_propose, "register": cmd_register, "extract": cmd_extract, "acquire": lambda a: cmd_acquire(a, run=run), "compare": cmd_compare}[cmd](args)
