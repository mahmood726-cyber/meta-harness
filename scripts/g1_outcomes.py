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
            fam = "ALL_CAUSE_MORTALITY" if MORT.search(span) else "HARM" if HARM.search(span) else "OTHER"
            key = (fam, m.group("e"), m.group("l"), m.group("u"))
            if key in seen:
                continue
            seen.add(key)
            hits.append({"family": fam, "measure": m.group("m"), "estimate": _num(m.group("e")),
                         "lower": _num(m.group("l")), "upper": _num(m.group("u")), "span": span})
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


def is_our_primary(name, t):
    """The candidate IS our primary outcome: its words overlap our primary's name by >= half of either, or it contains
    one of our primary's specific keywords (>= 8 characters)."""
    po = t["primary_outcome"]
    a, b = _words(name), _words(po["name"])
    # Jaccard >= 0.5: one shared word ('death' in 'Death within 24 h' v 'Death due to bleeding') is not identity (7 Oct)
    if a and b and len(a & b) / len(a | b) >= 0.5:
        return True
    return any(len(k) >= 8 and k.lower() in (name or "").lower() for k in po.get("keywords") or [])


def linked_to(name, t):
    """An outcome already declared in topics/<slug>.json (secondary or harm) that the candidate names -> its name."""
    low = (name or "").lower()
    for o in (t.get("secondary_outcomes") or []) + (t.get("harm_outcomes") or []):
        if o["name"].lower() in low or low in o["name"].lower() or \
                any(len(k) >= 6 and k.lower() == low for k in o.get("keywords") or []):
            return o["name"]
    return None


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
        (out.append(c) if named.search(h["span"]) else excluded.append(dict(c, excluded="SPAN_DOES_NOT_NAME_OUR_INTERVENTION")))
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
    if not (_term_re(_intervention_terms(t)).search(c) and
            _term_re([x for x in (t.get("comparator_terms") or []) if len(x) >= 3] + GENERIC_CONTROL).search(c)):
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


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    cmd, *args = sys.argv[1:]
    run = "--run" in args
    args = [a for a in args if not a.startswith("--")]
    {"inventory": lambda a: cmd_inventory(a, run=run), "propose": cmd_propose}[cmd](args)
