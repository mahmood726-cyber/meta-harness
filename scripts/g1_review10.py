"""Review-10 F10-1 (glp1-ra-mace-t2d), binding lane, 9 Oct 2026: FLOW's 3-point MACE and ELIXA's GENUINE 3-point MACE,
each re-verified against its own clause and licence, with the G1 / served effect reported BEFORE anything is applied.

  FLOW   PMID 39211948 (Eur Heart J 2024, prespecified CV analysis; PMC11931213, CC BY): the outcome definition and the
         overall result are both verbatim clauses of the held CC BY text.
  ELIXA  NCT01147250 / PMID 26630143: a 3-point (CV death, non-fatal MI, non-fatal stroke) hazard ratio is bound only from
         a clause or table whose OWN definition has exactly those three components. A definition that adds
         hospitalisation for unstable angina is the 4-point primary and is never bound as 3-point (three_point()).
Routes are read now; every one is recorded with its outcome. Nothing served changes: FLOW (and ELIXA if ever found)
go to the captain as V14 items with before / after.

    python scripts/g1_review10.py   -> outputs/k_gap/g1_binding/review10_flow_elixa.json
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "review10_flow_elixa.json")
SLUG = "glp1-ra-mace-t2d"
FLOW_DEF = "the composite of CV death, non-fatal MI or non-fatal stroke (hereafter CV death/MI/stroke)"
FLOW_RES = ("In the overall population, semaglutide reduced rates of the composite of CV death/MI/stroke compared with "
            "placebo [HR 0.82 (95% CI 0.68–0.98)]")
_HR = re.compile(r"(?:HR|hazard ratio)[^0-9]{0,40}?(\d\.\d+)\s*[(\[,;]?\s*(?:95%\s*CI[:,]?\s*)?(\d\.\d+)\s*[-–,]\s*(\d\.\d+)", re.I)


def _ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


_COMP = {"death": re.compile(r"(?:non-?fatal )?(?:cv|cardiovascular) death|death (?:from|due to) cardiovascular causes"),
         "mi": re.compile(r"(?:non-?fatal )?(?:myocardial infarction|mi)"),
         "stroke": re.compile(r"(?:non-?fatal )?stroke")}
_FIRST = re.compile(r"(?:cv|cardiovascular) death|death (?:from|due to) cardiovascular causes|myocardial infarction|\bmi\b|"
                    r"\bstroke\b", re.I)


def three_point(definition, result_clause):
    """(hr, lo, hi) when the DEFINITION names exactly CV death + (non-fatal) MI + (non-fatal) stroke and NOTHING else --
    a whitelist: every listed item must be one of the three (codex review10-r1 #1: a blacklist let 'resuscitated cardiac
    arrest' through) -- and the result clause prints one HR inside its CI; else (None, why)."""
    d = re.sub(r"\([^)]*\)", " ", definition.lower())
    m = _FIRST.search(d)
    if not m:
        return None, "DEFINITION_NOT_THREE_COMPONENTS"
    d = re.split(r";|\bhr\b|hazard ratio|\bgave\b|\bwas\b|\bwere\b", d[m.start():])[0]
    items = [x.strip(" .:-") for x in re.split(r",|\s+or\s+|\s+and\s+|/", d) if x.strip(" .:-")]
    seen = set()
    for it in items:
        k = next((k for k, rx in _COMP.items() if rx.fullmatch(it)), None)
        if k is None:
            return None, f"DEFINITION_HAS_A_FOURTH_COMPONENT:{it[:60]}"
        seen.add(k)
    if seen != set(_COMP):
        return None, "DEFINITION_NOT_THREE_COMPONENTS"
    hits = _HR.findall(result_clause)
    if len(hits) != 1:
        return None, f"RESULT_CLAUSE_HRS:{len(hits)}"
    hr, lo, hi = (float(x) for x in hits[0])
    if not lo <= hr <= hi:
        return None, "HR_NOT_INSIDE_ITS_CI"
    return (hr, lo, hi), None


def reader_verdict(a, txt):
    """(gate, agrees) for a FLOW reader: quote verbatim, the HR and CI printed in it, AND the quote is FLOW's own overall
    3-point result clause -- a matching tuple from another endpoint never agrees (codex review10-r1 #2)."""
    if a.get("state") != "FOUND":
        return "NOT_REPORTED_BY_READER", False
    parts = [_ws(x) for x in str(a.get("quote") or "").splitlines() if _ws(x)]
    if not parts or any(len(x) < 20 or x not in txt for x in parts):
        return "QUOTE_NOT_VERBATIM", False
    q = " ".join(parts)
    miss = [kk for kk in ("hr", "lower", "upper") if a.get(kk) is None or f"{a[kk]:.2f}" not in q]
    if miss:
        return f"NUMBER_NOT_IN_QUOTE:{miss}", False
    res = _ws(FLOW_RES).rstrip(".")
    if not all(x.rstrip(".") in res or res in x for x in parts):
        return "GATED_OTHER_CLAUSE", False
    return "GATED", (a.get("hr"), a.get("lower"), a.get("upper")) == (0.82, 0.68, 0.98)


def ema_three_point_clauses(text):
    """Sentences naming ELIXA (or in a window after it) whose own definition passes three_point (codex review10-r1 #3:
    the EMA route had bypassed it)."""
    out = []
    for m in re.finditer(r"ELIXA", text):
        win = text[m.start():m.start() + 900]
        for sent in re.split(r"(?<=[.])\s+(?=[A-Z])", win):
            if _HR.search(sent):
                got, _why = three_point(sent, sent)
                if got:
                    out.append(sent[:300])
    return list(dict.fromkeys(out))


def label_primary(t):
    """The ADLYXIN label's primary-endpoint table: its own definition and HR, classified by three_point."""
    m = re.search(r"Table \d+: Analysis of the Primary C(?:ardiovascular|V) Endpoint \(time to the first occurrence of "
                  r"the composite of ([^)]{20,200})\).{0,400}?Primary composite CV event.{0,200}?(\d\.\d\d) \((\d\.\d\d), "
                  r"(\d\.\d\d)\)", t, re.I)
    if not m:
        return None
    got, why = three_point(m.group(1), f"HR {m.group(2)} ({m.group(3)}-{m.group(4)})")
    return {"definition": m.group(1), "hr": [float(m.group(2)), float(m.group(3)), float(m.group(4))],
            "three_point": bool(got), "why": why}


def four_point_of(d):
    """The label HR only when its definition is NOT 3-point (codex review10-r1 #4)."""
    return d["hr"] if d and not d["three_point"] and str(d.get("why") or "").startswith("DEFINITION_HAS_A_FOURTH") else None


def doc_route_outcome(text, agency):
    """An unreadable held document is NOT_CHECKED -- never read as absence (codex review10-r1 #5)."""
    return f"NOT_CHECKED ({agency} held text unreadable or digest changed)" if not text else "READ"


def flow():
    import k_gap_counterfactual as k
    import g1_trial_acquire as ta
    txt = _ws(k.pmc_fulltext_cached("39211948"))
    lic = ta.pmc_copy("39211948")
    got, why = (None, "NOT_HELD") if not txt else \
        ((None, "SPANS_NOT_VERBATIM") if FLOW_DEF not in txt or FLOW_RES not in txt else three_point(FLOW_DEF, FLOW_RES))
    return {"trial": "FLOW", "pmid": "39211948", "pmcid": lic.get("pmcid"), "licence": lic.get("licence"),
            "licence_statement": lic.get("statement"), "definition_span": FLOW_DEF, "result_span": FLOW_RES,
            "verdict": "VERIFIED" if got and lic.get("licence") == "CC" else f"NOT_VERIFIED:{why or 'LICENCE'}",
            "value": {"measure": "HR", "effect": got[0], "lower": got[1], "upper": got[2]} if got else None}


def elixa():
    """Every open route for ELIXA's 3-point MACE, read now."""
    import g1_regulatory_source as rs
    routes = []
    ap = os.path.join(os.environ.get("AACT_SNAPSHOT") or "F:/AACT-storage/AACT/2026-08-30", "outcomes.txt")
    if os.path.isfile(ap):
        import csv
        csv.field_size_limit(10 ** 9)
        titles = []
        with open(ap, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f, delimiter="|"):
                if r.get("nct_id") == "NCT01147250":
                    titles.append(r["title"])
        three = [t for t in titles if three_point(t, "HR 1.00 (0.90-1.10)")[0]]
        routes.append({"route": "AACT 2026-08-30 outcomes NCT01147250",
                       "outcome": "THREE_POINT_POSTED" if three else
                       f"NO_THREE_POINT_OUTCOME (posted: {[t[:90] for t in titles]})"})
    else:
        routes.append({"route": "AACT", "outcome": "NOT_CHECKED (no snapshot)"})
    src = json.load(open(rs.SOURCES, encoding="utf-8"))
    lbl, comp4, unread = None, None, []
    for u, r in sorted(src.items()):
        if SLUG not in (r.get("topics") or []) or r.get("state") != "TEXT" or "208471" not in u or "/label/" not in u:
            continue
        raw = rs.doc_text(u)
        if doc_route_outcome(raw, "FDA") != "READ":
            unread.append(u)
            continue
        d = label_primary(_ws(raw))
        if d:
            lbl = dict(d, url=u, doc_sha256=r.get("doc_sha256"))
            comp4 = four_point_of(d)
            break
    routes.append({"route": "FDA ADLYXIN label (NDA208471) Table 12", "outcome":
                   (f"FOUR_POINT_PRIMARY_ONLY: '{lbl['definition']}' HR {lbl['hr']} ({lbl['why']})" if lbl and
                    not lbl["three_point"] else ("THREE_POINT" if lbl else
                                                 (f"NOT_CHECKED ({len(unread)} held labels unreadable)" if unread
                                                  else "NOT_FOUND_IN_HELD_LABELS"))), "detail": lbl})
    try:
        from harness import http
        d = http.get_json("https://api.fda.gov/drug/drugsfda.json", {"search": "application_number:NDA208471"}, tries=2)
        reviews = [dd.get("url") for r in d.get("results", []) for s in r.get("submissions", [])
                   for dd in s.get("application_docs") or [] if (dd.get("type") or "").lower() == "review"]
        routes.append({"route": "openFDA application_docs NDA208471 (typed discovery)",
                       "outcome": f"REVIEWS_LISTED:{reviews}" if reviews else "NO_REVIEW_DOCUMENT_LISTED"})
    except Exception as exc:  # noqa: BLE001 - a failed lookup is recorded, never read as absence
        if "404" in str(exc):          # openFDA answers 'No matches found!' with HTTP 404: a CHECKED absence
            routes.append({"route": "openFDA application_docs NDA208471 (typed discovery)",
                           "outcome": "NO_APPLICATION_RECORD (openFDA 404: no drugsfda record for NDA208471)"})
        else:
            routes.append({"route": "openFDA NDA208471", "outcome": f"NOT_CHECKED ({type(exc).__name__})"})
    ema = [u for u, r in src.items() if SLUG in (r.get("topics") or []) and r.get("agency") == "EMA"
           and r.get("state") == "TEXT"]
    ema_3p, ema_unread = [], []
    for u in ema:
        raw = rs.doc_text(u)
        if doc_route_outcome(raw, "EMA") != "READ":
            ema_unread.append(u)
            continue
        ema_3p += [(u, c) for c in ema_three_point_clauses(_ws(raw))]
    routes.append({"route": f"EMA EPARs held ({len(ema)})", "outcome": "ELIXA_THREE_POINT_CLAUSE" if ema_3p else
                   (f"NOT_CHECKED ({len(ema_unread)} held EPARs unreadable)" if ema_unread else
                    "NO_ELIXA_THREE_POINT_CLAUSE (the Lyxumia EPAR's MACE HR 1.25 (0.67-2.35) is a pre-ELIXA phase 3 "
                    "meta-analysis)"), "candidates": ema_3p[:3]})
    found = [r for r in routes if r["outcome"].startswith(("THREE_POINT", "ELIXA_THREE_POINT"))]
    res = "CANDIDATE" if found else ("NOT_CHECKED" if any(r["outcome"].startswith("NOT_CHECKED") for r in routes)
                                     else "NOT_FOUND")
    return {"trial": "ELIXA", "nct": "NCT01147250", "pmid": "26630143", "result": res, "routes": routes,
            "four_point_hr": comp4}


RSCHEMA = {"type": "object", "additionalProperties": False, "required": ["state", "quote", "hr", "lower", "upper", "definition"],
           "properties": {"state": {"type": "string", "enum": ["FOUND", "NOT_REPORTED"]}, "quote": {"type": "string"},
                          "hr": {"type": ["number", "null"]}, "lower": {"type": ["number", "null"]},
                          "upper": {"type": ["number", "null"]}, "definition": {"type": "string"}}}
RINSTR = {"A": "You are reader A. Below is the held CC BY full text of ONE trial report (FLOW, semaglutide v placebo). "
               "Find the OVERALL-population hazard ratio and 95% CI for the composite of cardiovascular death, non-fatal "
               "myocardial infarction and non-fatal stroke (3-point MACE). Quote the sentence verbatim; copy the numbers "
               "exactly; in 'definition' quote the paper's own definition of that composite. If not printed, NOT_REPORTED.",
          "B": "You are reader B, an independent second reader (you are not shown any other answer). Read the trial report "
               "below sceptically: is there an overall (not subgroup) HR with 95% CI for exactly the 3-component composite "
               "CV death / non-fatal MI / non-fatal stroke -- not a 4-component or kidney composite? Quote the result "
               "sentence and the definition verbatim; copy numbers exactly. If not printed, NOT_REPORTED."}


def flow_readers(run=False):
    """Two recorded codex readers over FLOW's held CC BY text; each answer gated (quote verbatim, numbers in quote)."""
    import concurrent.futures as cf
    import hashlib
    import k_gap_counterfactual as k
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    rec_dir = os.path.join(ROOT, "evidence", "model_calls", "review10")
    txt = _ws(k.pmc_fulltext_cached("39211948"))
    led = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "review10_readers.json")
    prev = json.load(open(led, encoding="utf-8")) if os.path.exists(led) else {}
    out = {}

    def one(who):
        p = (f"{RINSTR[who]}\n\n<<<TEXT PMID 39211948 PMC OA full text (CC BY)\n{txt}\nTEXT>>>\n").encode("utf-8")
        ps = hashlib.sha256(p).hexdigest()
        r0 = prev.get(who) or {}
        fp = os.path.join(rec_dir, f"{r0.get('record_id')}.json")
        if os.path.exists(fp) and r0.get("prompt_sha256") == ps:
            rec = ms.load_record(fp)
        elif run:
            rec = mcl.call(p, schema=RSCHEMA, model="gpt-6-astra", effort="high",
                           caller={"file": "scripts/g1_review10.py", "line": "flow_readers", "lane": "g1/binding",
                                   "purpose": f"review-10 F10-1 FLOW 3-point MACE second reader {who}"},
                           input_digests=[{"ref": "PMID 39211948 PMC OA full text (CC BY)",
                                           "sha256": hashlib.sha256(txt.encode("utf-8")).hexdigest(),
                                           "what": "held CC BY full text, whitespace-normalised"}], timeout_s=1800)
            os.makedirs(rec_dir, exist_ok=True)
            ms.write_record(rec, rec_dir)
        else:
            return who, {"state": "NOT_RUN"}
        a = json.loads(ms.replay(rec).decode("utf-8")) if rec.get("state") == "RAN_OK" else {}
        g, agrees = reader_verdict(a, txt) if a else ("RAN_ERROR", False)
        return who, {"record_id": rec["record_id"], "prompt_sha256": ps, "gate": g, "answer": a, "agrees": agrees}
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        for who, r in ex.map(one, ("A", "B")):
            out[who] = r
    with open(led, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return {w: {k_: r.get(k_) for k_ in ("record_id", "gate", "agrees")} for w, r in out.items()}


def effect(fl):
    from harness import synth as S
    d = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "review.json"), encoding="utf-8"))
    o = [o for o in d["outcomes"] if o.get("primary")][0]
    rows = [S.Study(label=t["label"], effect=t["effect"], ci_low=t["ci_low"], ci_high=t["ci_high"]) for t in o["trials"]]
    b = S.pool(rows, "HR")
    out = {"outcome": o["name"], "before": {"k": b.k, "estimate": round(b.estimate, 4), "ci": [round(b.ci_low, 4),
                                                                                                 round(b.ci_high, 4)]}}
    if fl.get("value"):
        v = fl["value"]
        a = S.pool(rows + [S.Study(label="FLOW", effect=v["effect"], ci_low=v["lower"], ci_high=v["upper"])], "HR")
        out["after_flow"] = {"k": a.k, "estimate": round(a.estimate, 4), "ci": [round(a.ci_low, 4), round(a.ci_high, 4)]}
    return out


def main(argv):
    fl, el = flow(), elixa()
    fl["second_readers"] = flow_readers(run="--readers" in argv)
    g1p = os.path.join(ROOT, "outputs", "k_gap", "g1", f"{SLUG}.json")
    g1 = json.load(open(g1p, encoding="utf-8")) if os.path.exists(g1p) else {}
    cr = next((x.get("comparator_row") for x in g1.get("trials") or [] if x.get("label") == "ELIXA"), None)
    finding = None
    if cr and el.get("four_point_hr") and [float(cr["effect"]), float(cr["lower"]), float(cr["upper"])] == el["four_point_hr"]:
        finding = {"kind": "COMPARATOR_ROW_IS_THE_FOUR_POINT_PRIMARY", "comparator_row": cr,
                   "label_four_point_hr": el["four_point_hr"],
                   "note": "the comparator pooled ELIXA's 4-point primary (incl. unstable-angina hospitalisation) as "
                           "3-point MACE; a named divergence candidate for the captain (V14), never applied here"}
    out = {"F10-1": {"flow": fl, "elixa": el, "comparator_elixa_finding": finding, "served_effect": effect(fl),
                     "g1_effect": {"g1_status_now": (g1.get("g1_status") or {}).get("state"),
                                   "comparator_pmid": g1.get("comparator_pmid"),
                                   "flow_in_comparator_set": any("FLOW" in str(x.get("label")) for x in g1.get("trials") or []),
                                   "expected": "unchanged: FLOW is outside the comparator's trial set (the comparator "
                                               "predates FLOW), so the same-trials comparison does not move; to be "
                                               "confirmed by a recount once the served pool is changed under V14"},
                     "applied": "NOTHING (V14)"}}
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps({"flow": fl["verdict"], "flow_value": fl["value"], "elixa": el["result"],
                      "elixa_routes": [r["outcome"][:110] for r in el["routes"]], "finding": bool(finding),
                      "effect": out["F10-1"]["served_effect"], "g1": out["F10-1"]["g1_effect"]["g1_status_now"],
                      "flow_in_comparator_set": out["F10-1"]["g1_effect"]["flow_in_comparator_set"]}, indent=1))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
