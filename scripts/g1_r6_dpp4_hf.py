"""R6 P2 (dpp4-mace-t2d, harm outcome 'Hospitalization for heart failure'), binding lane, 9 Oct 2026. Typed first,
recorded codex second readers; nothing served changes -- the pool before / after goes to the captain as a V14 item.

Served today: SAVOR-TIMI 53 + TECOS, k=2, HR 1.1296 (CI withheld at k=2). Each candidate is bound from its OWN PubMed
abstract, fetched verbatim now (efetch; the held copy of 28893244 is ABRIDGED -- 1,138 of 2,124 characters -- and omits
this very clause: the k-gap source-preservation finding R6 P1) and pinned by the sha256 of the AbstractText:
  omarigliptin  PMID 28893244 NCT01703208: 'The hHF outcome occurred in 20/2092 ... 33/2100 ... HR of 0.60 (95% CI 0.35,
                1.05)'
  CARMELINA     PMID 30586723 NCT01897532: the FIRST-event hHF HR 0.90 (0.74-1.08), 209/3494 v 226/3485 -- never the
                recurrent-event rate ratio (0.94, 0.75-1.20) printed in the same sentence
  EXAMINE       PMID 25765696 NCT00968708: 'Hospital admission for heart failure was the first event in 85 ... 79 ...
                (HR 1.07, 95% CI 0.79-1.46)' -- a PRINTED 95% CI (EXAMINE's MACE is excluded under D7 for its 98% CI;
                this is a different clause). REFUSED on definition: both recorded readers read 'was the first event'
                as the first event of the exploratory extended-MACE composite -- not time to first hHF. Reconciled: out.

    python scripts/g1_r6_dpp4_hf.py [--readers]   -> outputs/k_gap/g1_binding/r6_dpp4_hf.json
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "r6_dpp4_hf.json")
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "r6_dpp4_hf")
SLUG, OUTCOME = "dpp4-mace-t2d", "Hospitalization for heart failure"
TARGETS = [
    {"label": "omarigliptin (O-QWEST)", "pmid": "28893244", "nct": "NCT01703208", "state": "BIND",
     "span": "The hHF outcome occurred in 20/2092 patients in the omarigliptin group (0.96%; 0.51/100 patient-years) and "
             "33/2100 patients in the placebo group (1.57%; 0.85/100 patient-years), with an HR of 0.60 (95% CI 0.35, 1.05)",
     "value": {"measure": "HR", "effect": 0.60, "lower": 0.35, "upper": 1.05, "events_t": 20, "n_t": 2092,
               "events_c": 33, "n_c": 2100}},
    {"label": "CARMELINA", "pmid": "30586723", "nct": "NCT01897532", "state": "BIND",
     "span": "Linagliptin versus placebo did not affect the incidence of hHF (209/3494 [6.0%] versus 226/3485 [6.5%], "
             "respectively; hazard ratio [HR], 0.90; 95% CI, 0.74-1.08)",
     "value": {"measure": "HR", "effect": 0.90, "lower": 0.74, "upper": 1.08, "events_t": 209, "n_t": 3494,
               "events_c": 226, "n_c": 3485}},
    {"label": "EXAMINE", "pmid": "25765696", "nct": "NCT00968708", "state": "REFUSED_DEFINITION",
     "span": "Hospital admission for heart failure was the first event in 85 (3·1%) patients taking alogliptin compared "
             "with 79 (2·9%) taking placebo (HR 1·07, 95% CI 0·79-1·46)",
     "value": {"measure": "HR", "effect": 1.07, "lower": 0.79, "upper": 1.46, "events_t": 85, "n_t": None,
               "events_c": 79, "n_c": None},
     "caveat": "'was the first event' counts patients whose FIRST event in the exploratory extended-MACE composite was "
               "hHF (both recorded readers, 9 Oct) -- a competing-event component count, not time to first hHF; no "
               "denominators in the clause. Refused on definition; EXAMINE stays out of the hHF pool (reconciled)."},
]
SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["state", "quote", "hr", "lower", "upper", "events_t", "n_t", "events_c", "n_c", "definition_note"],
          "properties": {"state": {"type": "string", "enum": ["FOUND", "NOT_REPORTED"]}, "quote": {"type": "string"},
                         "hr": {"type": ["number", "null"]}, "lower": {"type": ["number", "null"]},
                         "upper": {"type": ["number", "null"]}, "events_t": {"type": ["integer", "null"]},
                         "n_t": {"type": ["integer", "null"]}, "events_c": {"type": ["integer", "null"]},
                         "n_c": {"type": ["integer", "null"]}, "definition_note": {"type": "string"}}}
INSTR = {"A": "You are reader A. Below is ONE trial report's PubMed abstract. Find the result for hospitalization for "
              "heart failure as TIME TO FIRST hHF (not recurrent events, not a composite with death). Quote the clause "
              "verbatim; copy the HR, 95% CI and per-arm counts exactly as printed (drug arm first: events_t / n_t; "
              "placebo: events_c / n_c); null when not printed. definition_note: what exactly the numbers count.",
         "B": "You are reader B, an independent second reader (no other answer is shown to you). Read the abstract below "
              "sceptically: is there a FIRST-EVENT hospitalization-for-heart-failure hazard ratio with a 95% CI for the "
              "drug versus placebo -- not a recurrent-event rate ratio, not a composite, not a subgroup? Quote it "
              "verbatim, copy numbers exactly (drug arm = events_t / n_t), null when not printed, and say in "
              "definition_note exactly what the counted events are."}


def _abstracts(pmids):
    from harness import http, fetch
    x = http.get_text(f"{fetch.EUTILS}/efetch.fcgi", {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml",
                                                      "tool": "meta-harness", "email": "meta-harness@example.org"})
    out = {}
    for art in re.findall(r"<PubmedArticle>.*?</PubmedArticle>", x, re.S):
        pm = re.search(r"<PMID[^>]*>(\d+)", art).group(1)
        ab = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", " ".join(
            re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", art, re.S))))).strip()
        # the trial's identifiers come from the article ITSELF -- its databank accession numbers and its own abstract --
        # never from its reference list or linked comments (codex r6-dpp4-hf-r1 #3: a cited paper's NCT satisfied it)
        own = re.sub(r"<ReferenceList>.*?</ReferenceList>|<CommentsCorrectionsList>.*?</CommentsCorrectionsList>", " ",
                     art, flags=re.S)
        ids = re.findall(r"<AccessionNumber>(NCT\d{8})</AccessionNumber>", own) + re.findall(r"NCT\d{8}", ab)
        out[pm] = {"abstract": ab, "sha256": hashlib.sha256(ab.encode("utf-8")).hexdigest(), "ncts": sorted(set(ids))}
    return out


def _nums(q):
    q = re.sub(r"(?<=\d)·(?=\d)", ".", q)
    return {float(x) for x in re.findall(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])", q)}


def verify(t, ab):
    """None when the binding's span is verbatim in the trial's own abstract and every value is printed in it."""
    if not ab:
        return "ABSTRACT_NOT_FETCHED"
    if t["nct"] not in ab["ncts"]:
        return "ABSTRACT_DOES_NOT_CARRY_THE_TRIAL_NCT"
    if t["span"] not in ab["abstract"]:
        return "SPAN_NOT_VERBATIM"
    ns = _nums(t["span"])
    miss = [k for k, v in t["value"].items() if k != "measure" and v is not None and float(v) not in ns]
    return f"VALUE_NOT_IN_SPAN:{miss}" if miss else None


def gate(a, ab, t):
    if a.get("state") != "FOUND":
        return "NOT_REPORTED_BY_READER"
    parts = [re.sub(r"\s+", " ", x).strip() for x in str(a.get("quote") or "").splitlines() if x.strip()]
    if not parts or any(len(x) < 20 or x not in ab for x in parts):
        return "QUOTE_NOT_VERBATIM"
    ns = _nums(" ".join(parts))
    miss = [k for k in ("hr", "lower", "upper") if a.get(k) is None or float(a[k]) not in ns]
    if miss:
        return f"NUMBER_NOT_IN_QUOTE:{miss}"
    # agreement is about OUR clause: the reader's quote must overlap the binding's own span, so a matching number tuple
    # from another endpoint, subgroup or composite never counts as confirmation (cf. codex review10-r1 #2)
    # EVERY quoted passage must lie inside our span, or contain it (codex r6-dpp4-hf-r1 #2: one 40-character overlap let
    # a second line carrying another endpoint's numbers through)
    sp = re.sub(r"\s+", " ", t["span"])
    if not all(x.rstrip(".") in sp or sp in x for x in parts):
        return "GATED_OTHER_CLAUSE"
    v = t["value"]
    same = (a["hr"], a["lower"], a["upper"]) == (v["effect"], v["lower"], v["upper"])
    # the counts take part too: a reader that reverses the arms does not agree (codex r6-dpp4-hf-r1 #1)
    for k in ("events_t", "n_t", "events_c", "n_c"):
        if a.get(k) is not None and v.get(k) is not None and a[k] != v[k]:
            same = False
    return "GATED_AGREES" if same else "GATED_DIFFERS"


def readers(abs_, run):
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    led = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "r6_dpp4_hf_readers.json")
    prev = json.load(open(led, encoding="utf-8")) if os.path.exists(led) else {}
    jobs = [(t, who) for t in TARGETS for who in ("A", "B")]

    def one(job):
        t, who = job
        ab = abs_.get(t["pmid"]) or {}
        p = f"{INSTR[who]}\n\nTRIAL: {t['label']} ({t['nct']})\n<<<ABSTRACT PMID {t['pmid']}\n{ab.get('abstract')}\nABSTRACT>>>\n"
        p = p.encode("utf-8")
        ps, key = hashlib.sha256(p).hexdigest(), f"{t['pmid']}::{who}"
        r0 = prev.get(key) or {}
        fp = os.path.join(REC_DIR, f"{r0.get('record_id')}.json")
        if os.path.exists(fp) and r0.get("prompt_sha256") == ps:
            rec = ms.load_record(fp)
        elif run:
            rec = mcl.call(p, schema=SCHEMA, model="gpt-6-astra", effort="high",
                           caller={"file": "scripts/g1_r6_dpp4_hf.py", "line": "readers", "lane": "g1/binding",
                                   "purpose": f"R6 P2 dpp4 hHF second reader {who} {t['label']}"},
                           input_digests=[{"ref": f"PMID {t['pmid']} PubMed abstract (efetch, verbatim)",
                                           "sha256": ab.get("sha256"), "what": "the trial's own abstract"}],
                           timeout_s=1200)
            os.makedirs(REC_DIR, exist_ok=True)
            ms.write_record(rec, REC_DIR)
        else:
            return key, {"state": "NOT_RUN"}
        a = json.loads(ms.replay(rec).decode("utf-8")) if rec.get("state") == "RAN_OK" else {}
        return key, {"record_id": rec["record_id"], "prompt_sha256": ps, "answer": a,
                     "gate": gate(a, ab.get("abstract") or "", t) if a else "RAN_ERROR"}
    out = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for k, r in ex.map(one, jobs):
            out[k] = r
    with open(led, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return out


def pools(bound):
    from harness import synth as S
    d = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "review.json"), encoding="utf-8"))
    o = [o for o in d["outcomes"] if o["name"] == OUTCOME][0]
    rows = [S.Study(label=str(t.get("label")), effect=t["effect"], ci_low=t["ci_low"], ci_high=t["ci_high"]) for t in o["trials"]]

    def show(rs):
        r = S.pool(rs, "HR")
        return {"k": r.k, "estimate": round(r.estimate, 4),
                "ci": [round(r.ci_low, 4), round(r.ci_high, 4)] if r.k > 2 else "WITHHELD (k=2)", "tau2": round(r.tau2, 5)}
    add = [S.Study(label=t["label"], effect=t["value"]["effect"], ci_low=t["value"]["lower"], ci_high=t["value"]["upper"])
           for t in bound]
    res = {"served_trials": [t.get("label") for t in o["trials"]], "before": show(rows), "after_bound": show(rows + add)}
    return res


def main(argv):
    abs_ = _abstracts([t["pmid"] for t in TARGETS])
    rd = readers(abs_, run="--readers" in argv)
    rows, bound = [], []
    for t in TARGETS:
        why = verify(t, abs_.get(t["pmid"]))
        rs_ = {w: (rd.get(f"{t['pmid']}::{w}") or {}).get("gate") for w in ("A", "B")}
        ok = why is None and t["state"] == "BIND" and all(g == "GATED_AGREES" for g in rs_.values())
        rows.append(dict(t, abstract_sha256=(abs_.get(t["pmid"]) or {}).get("sha256"), verify=why or "VERIFIED",
                         second_readers=rs_, verdict="STAGED_FOR_V14" if ok else
                         (t["state"] if t["state"] != "BIND" else "NOT_STAGED")))
        if ok:
            bound.append(t)
    out = {"slug": SLUG, "outcome": OUTCOME, "rows": rows, "pools": pools(bound), "applied": "NOTHING (V14)",
           "g1_effect": "none: G1 compares the primary outcome (3-point MACE); this is a harm outcome"}
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    for r in rows:
        print(r["label"], r["verify"], r["second_readers"], r["verdict"])
    print(json.dumps(out["pools"], indent=1))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
