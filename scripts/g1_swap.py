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
DATE = "2026-10-06"
CONTACT = "meta-harness@example.org"          # never a personal address in a request


def _terms(p):
    t = [x for x in p["intervention_terms"] if len(x) >= 3]
    return t[:12]


def cmd_search(slugs):
    """Recorded search per topic: PubMed esearch + Europe PMC, both restricted to meta-analyses / systematic reviews and
    built mechanically from the topic's intervention terms. Response sha256 and every hit kept."""
    from harness import http
    for s in slugs:
        p = protocol(s)
        iv = " OR ".join(f'"{t}"' for t in _terms(p))
        pq = f'({iv}) AND (meta-analysis[pt] OR meta-analys*[ti] OR "systematic review"[ti] OR "network meta"[ti])'
        st, b = http.get_raw("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                             {"db": "pubmed", "term": pq, "retmax": "600", "retmode": "json", "tool": "meta-harness",
                              "email": CONTACT})
        pm = json.loads(b.decode("utf-8"))["esearchresult"]["idlist"]
        eq = f'({iv}) AND (TITLE:"meta-analysis" OR TITLE:"meta analysis" OR TITLE:"systematic review" OR PUB_TYPE:"Meta-Analysis")'
        st2, b2 = http.get_raw("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                               {"query": eq, "format": "json", "pageSize": "1000", "resultType": "lite"})
        ep = [r.get("pmid") for r in json.loads(b2.decode("utf-8"))["resultList"]["result"] if r.get("pmid")]
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
               "pubmed": {"query": pq, "n": len(pm), "response_sha256": hashlib.sha256(b).hexdigest()},
               "europepmc": {"query": eq, "n": len(ep), "response_sha256": hashlib.sha256(b2).hexdigest()},
               "current_comparator_added": p["current_comparator"], "records": recs}
        with open(os.path.join(SEL, f"{s}.search.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False)
        print(s, "pubmed", len(pm), "europepmc", len(ep), "records", len(recs), flush=True)


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


def held_jats(pmid, pmcid):
    """The candidate's open JATS (Europe PMC fullTextXML), held at cache/comparators/<pmid>/<date>_kgap_jats.xml."""
    from harness import http
    d = os.path.join(ROOT, "cache", "comparators", str(pmid))
    have = sorted(f for f in (os.listdir(d) if os.path.isdir(d) else []) if f.endswith("_kgap_jats.xml"))
    if have:
        return os.path.relpath(os.path.join(d, have[-1]), ROOT).replace("\\", "/")
    st, b = http.get_raw(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML", tries=2, timeout=120)
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
        ok = bool(q) and _norm(q) in nt
        out[cid] = ({"verdict": v.get("verdict"), "evidence": q} if ok and v.get("verdict") in ("PASS", "FAIL")
                    else {"verdict": "UNCLEAR", "evidence": (f"QUOTE_NOT_IN_TEXT: {q[:120]}" if q else "no quote")})
    pl = claim.get("pooled") or {}
    pooled_ok = bool(pl.get("quote")) and _norm(pl["quote"]) in nt and all(
        str(pl.get(k)) in pl["quote"] for k in ("estimate", "lower", "upper") if pl.get(k))
    k_ok = pooled_ok and pl.get("k") is not None
    return out, (pl if pooled_ok else None), (pl.get("k") if k_ok else None)


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
                except Exception as exc:  # noqa: BLE001 - a refused call is named, never dropped
                    print("LOCAL CALL FAILED", type(exc).__name__, str(exc)[:200], flush=True)
        try:
            for k, r in fut.result().items():
                runs[k] = r
                print(k, r["state"], r["record_id"], "worker", flush=True)
        except Exception as exc:  # noqa: BLE001 - worker failure is reported; the local half stands
            print("WORKER BATCH FAILED", type(exc).__name__, str(exc)[:300], flush=True)
    runs_store.save(runs, slugs=set(slugs))


def cmd_screen(slugs, run=False):
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


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    cmd, *args = sys.argv[1:]
    run = "--run" in args
    args = [a for a in args if not a.startswith("--")]
    {"rules": cmd_rules, "search": cmd_search, "screen": lambda a: cmd_screen(a, run=run)}[cmd](args)
