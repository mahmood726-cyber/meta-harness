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
            "required": ["name", "family", "measure", "estimate", "lower", "upper", "k", "timepoint", "quote"],
            "properties": {
                "name": {"type": "string"},
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
    "harm) or OTHER_EFFICACY; the measure as printed; the estimate, lower and upper bound EXACTLY as printed (strings); "
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
    return {"key": f"d10inv::{slug}::{pmid}", "slug": slug, "pmid": pmid, "prompt": prompt, "text": text,
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


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    cmd, *args = sys.argv[1:]
    run = "--run" in args
    args = [a for a in args if not a.startswith("--")]
    {"inventory": lambda a: cmd_inventory(a, run=run)}[cmd](args)
