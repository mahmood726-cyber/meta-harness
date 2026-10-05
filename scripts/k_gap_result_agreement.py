"""G1 RESULT AGREEMENT: for every trial that BOTH the comparator meta and our served pool include, does the
comparator report the same result for that trial as we do?

The comparator's per-trial number is LOCATED by a recorded model call (one per topic) and PARSED by code:
  - the model quotes, verbatim from the held comparator text, the passage reporting that trial's effect for the
    outcome (a sentence, or a table row) and, when the scale is only in a column header / caption, that header too;
  - the gate: every quote is in the WHOLE held text (whitespace-normalised) and the trial's label is in its quote;
  - the number comes from harness.extract.extract_effect on the quote, else from a bare 'x (lo-hi)' in the row with
    the scale taken from the quoted header. The model's own reading of the number is never used.
Ours: the served review's primary trial row (effect+CI, or RR/OR computed from its arm counts).
Agreement: same scale, point and both CI bounds within +-0.01 (two-decimal rounding), or +-0.02 on a counts-derived
ratio (rounding of reconstructed CIs). Nothing is changed by this script.

    python scripts/k_gap_result_agreement.py --run      # live, concurrency 3
    python scripts/k_gap_result_agreement.py --verify   # replay stored records only
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from reproducible_ai import model_source as ms  # noqa: E402
from kgap import k_gap  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
PROP = os.path.join(ROOT, "registry", "model_proposals", "k_gap_result_agreement.json")
REC_DIR = os.path.join(ROOT, ms.RECORD_DIR)
MODEL, EFFORT = "gpt-6-astra", "medium"

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {"items": {
    "type": "array", "items": {"type": "object", "additionalProperties": False,
                               "required": ["item", "state", "quote", "scale_quote"],
                               "properties": {"item": {"type": "string"},
                                              "state": {"type": "string", "enum": ["REPORTED", "NOT_REPORTED"]},
                                              "quote": {"type": ["string", "null"]},
                                              "scale_quote": {"type": ["string", "null"]}}}}}}

INSTR = """Below, between <<<TEXT and TEXT>>>, is the text of a published meta-analysis (tables included, cells separated by
spaces). For EACH trial listed under ITEMS, find where the meta-analysis reports THAT TRIAL'S OWN effect estimate for
the OUTCOME named below (a sentence, or a row of a table). Do not run commands or read files. Use only the text.
  REPORTED      quote: copy EXACTLY, character for character, the shortest passage that contains the trial's name (as
                written in the text) AND its effect estimate with confidence interval. If the scale (hazard ratio, risk
                ratio, odds ratio ...) is not in that passage but in a table's column header or caption, also copy that
                header/caption exactly into scale_quote; otherwise scale_quote is null.
  NOT_REPORTED  the text does not state that trial's own estimate for this outcome (e.g. only in a figure, or only a
                pooled estimate). quote and scale_quote are null.
Never compute, convert or round a number. Never use knowledge outside the text.
"""

# signed numbers (after folding U+2212 etc. to "-"); a RevMan forest row lists arm means, SDs, n and weight BEFORE
# the effect, so the effect is the LAST "x (lo, hi)" triple in the quoted row
_BARE = re.compile(r"(-?\d+(?:\.\d+)?)\s*[\(\[]\s*(-?\d+(?:\.\d+)?)\s*(?:,|to|\s-\s|(?<=\d)-(?=-?\d))\s*(-?\d+(?:\.\d+)?)\s*[\)\]]")
_SCALE = (("HR", re.compile(r"\bHR\b|hazard ratio", re.I)), ("RR", re.compile(r"\bRR\b|risk ratio|relative risk", re.I)),
          ("OR", re.compile(r"\bOR\b|odds ratio")), ("MD", re.compile(r"\bMD\b|mean difference", re.I)))


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _norm(s):
    return re.sub(r"\s+", " ", (s or "").replace(" ", " ")).strip()


def _scale_of(text):
    for name, rx in _SCALE:
        if rx.search(text or ""):
            return name
    return None


def parse_comparator_effect(quote, scale_quote):
    """(scale, point, lo, hi) from the quoted passage -- code, not the model."""
    from harness import extract
    e = extract.extract_effect(quote or "")
    if e:
        return (e.scale if hasattr(e, "scale") else e[0], float(e[1]), float(e[2]), float(e[3]))
    q = k_gap.fold_dashes(quote or "").replace("\u2212", "-")
    ms_ = list(_BARE.finditer(q))
    sc = _scale_of(scale_quote) or _scale_of(quote)
    if ms_ and sc:
        m = ms_[-1]
        return (sc, float(m.group(1)), float(m.group(2)), float(m.group(3)))
    return None


def _ratio_ci(a, n1, c, n2, kind):
    if None in (a, n1, c, n2) or min(n1, n2) <= 0:
        return None
    if a == 0 or c == 0 or a == n1 or c == n2:
        a, c, n1, n2 = a + 0.5, c + 0.5, n1 + 1, n2 + 1   # continuity correction only when a cell is zero
    if kind == "RR":
        est = (a / n1) / (c / n2)
        se = math.sqrt(1 / a - 1 / n1 + 1 / c - 1 / n2)
    else:
        b, d = n1 - a, n2 - c
        est = (a * d) / (b * c)
        se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return (kind, est, math.exp(math.log(est) - 1.959964 * se), math.exp(math.log(est) + 1.959964 * se))


def our_effect(t, scale):
    """Our served trial row on the comparator's scale when we can put it there without assumptions."""
    if t.get("effect") is not None and t.get("ci_low") is not None:
        return ((t.get("scale") or "").upper(), float(t["effect"]), float(t["ci_low"]), float(t["ci_high"])), "reported"
    if scale in ("RR", "OR") and all(t.get(k) is not None for k in ("ai", "n1i", "ci", "n2i")):
        return _ratio_ci(t["ai"], t["n1i"], t["ci"], t["n2i"], scale), "from_counts"
    if scale == "MD" and all(t.get(k) is not None for k in ("mean1", "sd1", "nc1", "mean2", "sd2", "nc2")):
        md = float(t["mean1"]) - float(t["mean2"])
        se = math.sqrt(float(t["sd1"]) ** 2 / float(t["nc1"]) + float(t["sd2"]) ** 2 / float(t["nc2"]))
        return ("MD", md, md - 1.959964 * se, md + 1.959964 * se), "from_counts"
    return None, "not_comparable"


def _decimals(x) -> int:
    """Printed precision. A STRING keeps its trailing zeros ('1.10' -> 2); a float cannot ('1.10' becomes 1.1 -> 1),
    which let a forest plot's printed 1.10 'agree' with our 1.11."""
    if isinstance(x, str):
        m = re.search(r"\.(\d+)", x)
        return len(m.group(1)) if m else 0
    r = repr(float(x))
    return len(r.split(".")[1].rstrip("0")) if "." in r else 0


def agree(ours, theirs, how):
    """Rounding-aware: two reported numbers agree when they are equal at the COARSER precision either side states
    (a paper's -12.4 (-13.4, -11.5) and a forest plot's -12.44 (-13.37, -11.51) are the same result). A value we
    derived from counts has no stated precision; it is compared at the comparator's precision + half a unit."""
    if not ours or not theirs:
        return "NOT_COMPARABLE"
    if ours[0] != theirs[0]:
        return f"SCALE_DIFFERS({ours[0]} vs {theirs[0]})"
    ok = []
    for i in (1, 2, 3):
        d = _decimals(theirs[i]) if how == "from_counts" else min(_decimals(ours[i]), _decimals(theirs[i]))
        d = max(d, 1)
        ok.append(abs(float(ours[i]) - float(theirs[i])) <= 0.5 * 10 ** -d + 1e-9)
    if all(ok):
        return "AGREE"
    if ok[0]:
        return "POINT_AGREES_CI_DIFFERS"
    return "DISAGREE"


def item_key(item) -> str:
    m = re.match(r"\s*(T\d+)", str(item or ""))
    return m.group(1) if m else str(item or "")


def topics():
    t = _j(os.path.join(OUT, "k_gap_table.json"))
    out = {}
    for r in t["trials"]:
        if r["gap_class"] == "POOLED" and r["unit_source"] in ("JATS_TABLE", "MODEL_PROPOSAL_GATED"):
            out.setdefault(r["slug"], []).append(r)
    return out


OURS_SOURCE = "served"          # or "rebuilt": the in-memory pool this branch's extractor would serve
WITH_SUPP = False               # --with-supplements: the comparator's cached supplement text is appended to the held
                                # text, and the gate searches the SAME concatenation the model was shown
SUPP_DATE = "2026-09-29"


def ours_rows(slug):
    if OURS_SOURCE == "rebuilt":
        import importlib.util
        spec = importlib.util.spec_from_file_location("cf", os.path.join(ROOT, "scripts", "k_gap_counterfactual.py"))
        cfm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cfm)
        rev = cfm.build(slug)
    else:
        rev = _j(os.path.join(ROOT, "docs", "reviews", slug, "review.json"))
    prim = next((o for o in rev["outcomes"] if o.get("primary")), {})
    return prim, {str(t.get("id", "")).replace("PMID ", ""): t for t in prim.get("trials", [])}


def items():
    its = []
    for slug, rows in sorted(topics().items()):
        prim, by = ours_rows(slug)
        text, ref = k_gap.held_text(slug)
        if WITH_SUPP:
            pmid = re.search(r"comparators/(\d+)/", ref)
            sp = k_gap.comparator_supplements(pmid.group(1), "", [], SUPP_DATE, offline=True) if pmid else {}
            if sp.get("state") == "CACHED" and sp.get("text"):
                text = text + "\n\n=== COMPARATOR SUPPLEMENTARY FILES ===\n" + sp["text"]
                ref = ref + f" + supplements sha256:{sp['sha256']}"
        keyed, seen = [], set()
        for r in rows:
            ours = next((by[p] for p in r["pmids"] if p in by), None)
            if ours is None:
                # the family may be pooled under a different report of the same trial
                fam = set(r["pmids"])
                ours = next((t for pid, t in by.items() if pid in fam), None)
            if ours is None or r["label"] in seen:
                continue
            seen.add(r["label"])
            acr = sorted({(v or {}).get("acronym") for v in (r.get("study") or {}).values() if (v or {}).get("acronym")})
            keyed.append({"label": r["label"], "ours": ours, "pmids": r["pmids"][:3], "ncts": r["ncts"][:2], "acronyms": acr})
        if keyed:
            its.append({"slug": slug, "outcome": prim.get("name"), "estimand": prim.get("estimand"),
                        "text": text, "ref": ref, "keyed": [(f"T{n + 1}", k) for n, k in enumerate(keyed)]})
    return its


def prompt(it):
    body = INSTR + f"\nOUTCOME: {it['outcome']} (this review's estimand: {it['estimand']})\nITEMS:\n"
    for key, k in it["keyed"]:
        body += f"  {key}: {k['label']}\n"
    return (body + "<<<TEXT\n" + it["text"] + "\nTEXT>>>\n").encode("utf-8")


def run_one(it):
    from reproducible_ai import model_call_live
    p = prompt(it)
    rec = model_call_live.call(p, schema=SCHEMA, model=MODEL, effort=EFFORT,
                               caller={"file": "scripts/k_gap_result_agreement.py", "line": "run_one",
                                       "purpose": f"G1 per-trial result location {it['slug']} (acq/k-gap lane)"},
                               input_digests=[{"ref": it["ref"], "sha256": hashlib.sha256(it["text"].encode("utf-8")).hexdigest(),
                                               "what": "held comparator text shown whole"}], timeout_s=1500)
    ms.write_record(rec, REC_DIR)
    return {"slug": it["slug"], "record_id": rec["record_id"], "state": rec["state"],
            "prompt_sha256": hashlib.sha256(p).hexdigest()}


WITH_FOREST = False             # --with-forest: a shared trial the comparator's TEXT does not report is looked up among
                                # the rows of a forest-plot figure that PASSED k_gap_forest_plot's recomputation gate
FOREST = os.path.join(ROOT, "registry", "model_proposals", "k_gap_forest_plot.json")
_FOREST = None


_FAY = os.path.join(OUT, "pubmed_first_author_year.json")


def first_author_year(pmid):
    """(surname lower-case, year) of a PMID from PubMed esummary, cached in outputs/k_gap/pubmed_first_author_year.json."""
    c = _j(_FAY) if os.path.exists(_FAY) else {}
    if pmid not in c:
        from harness import http
        try:
            d = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                              {"db": "pubmed", "id": pmid, "retmode": "json"}, tries=2).get("result", {}).get(pmid, {})
            au = (d.get("sortfirstauthor") or "").split(" ")[0].lower()
            yr = (re.search(r"\d{4}", d.get("pubdate") or "") or [None])[0] if d.get("pubdate") else None
            c[pmid] = [au, yr] if au and yr else None
        except Exception:  # noqa: BLE001 - an unreachable esummary means no join, never a guess
            return None
        with open(_FAY, "w", encoding="utf-8") as fh:
            json.dump(c, fh, indent=1, sort_keys=True)
    return tuple(c[pmid]) if c.get(pmid) else None


_RY = os.path.join(OUT, "pubmed_record_years.json")


def record_years(pmid):
    """The record's OWN publication years from PubMed esummary -- issue year (pubdate), electronic-publication year
    (epubdate) and first public availability (history aheadofprint / pubmed / entrez: Metcovid entered PubMed
    2020-08-14, issue 2021, no epubdate) -- cached in outputs/k_gap/pubmed_record_years.json. A meta cites a trial by either. None when unreachable
    (never a guess)."""
    c = _j(_RY) if os.path.exists(_RY) else {}
    if pmid not in c:
        from harness import http
        try:
            d = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                              {"db": "pubmed", "id": pmid, "retmode": "json"}, tries=2).get("result", {}).get(pmid, {})
        except Exception:  # noqa: BLE001 - an unreachable esummary means no extra year, never a guess
            return None
        dates = [d.get("pubdate"), d.get("epubdate")] + [h.get("date") for h in d.get("history") or []
                                                          if h.get("pubstatus") in ("aheadofprint", "pubmed", "entrez")]
        ys = sorted({m.group(0) for x in dates for m in [re.search(r"\d{4}", x or "")] if m})
        c[pmid] = ys or None
        with open(_RY, "w", encoding="utf-8") as fh:
            json.dump(c, fh, indent=1, sort_keys=True)
    return c.get(pmid)


def forest_row(slug, label, pmids=(), acronyms=()):
    """(scale, point, lo, hi) of the gated forest-plot row whose printed label IS this trial's comparator label
    (dash-folded, case-insensitive: equal, or one label's first token equal to the other's). None when the figure did
    not pass its gate or no row carries the label -- never a nearest match."""
    global _FOREST
    if _FOREST is None:
        _FOREST = _j(FOREST).get("results", {}) if os.path.exists(FOREST) else {}
    r = _FOREST.get(slug) or {}
    if r.get("state") != "PASS":
        return None
    norm = lambda x: re.sub(r"\s+", " ", k_gap.fold_dashes(str(x or "")).strip().lower())   # noqa: E731
    toks = lambda x: re.findall(r"[a-z0-9]+", norm(x))                                        # noqa: E731
    want = norm(re.sub(r"[\[(]\s*\d+\s*[\])]\s*$", "", label))      # drop a trailing citation number '[16]' / '(8)'
    rows = r["gate"]["rows"]
    hits = [x for x in rows if norm(x["label"]) == want]
    if not hits and toks(want) and len(toks(want)[0]) >= 4 and not toks(want)[0].isdigit():
        # first WORD token equal ('SELECT 18' ~ 'SELECT, 2023'; tokenised, so a trailing comma does not block it)
        hits = [x for x in rows if toks(x["label"])[:1] == toks(want)[:1]]
    if len(hits) != 1 and pmids:
        # no name match ('9 [28]'), or the surname matches several rows ('Imazio' = Imazio 2011 AND Imazio 2014): join
        # through the resolved report's PubMed first author AND year -- both must match one row ('Wallentin 2009')
        ay = [a for a in (first_author_year(p) for p in pmids) if a]
        hits = [x for x in rows for (au, yr) in ay if au in toks(x["label"]) and yr in toks(x["label"])]
    if len(hits) != 1 and acronyms:
        # the comparator labels rows by trial ACRONYM (FIDELIO-DKD) where our label is an author: join through the
        # acronym AACT registers for the row's NCT, as a whole label or as the label's leading tokens
        want_a = [toks(a) for a in acronyms if a]
        hits = [x for x in rows for a in want_a if a and toks(x["label"])[:len(a)] == a]
    if len(hits) != 1:
        return None
    x = hits[0]
    pr = x.get("printed") or {}
    # the PRINTED strings, so the comparison keeps the plot's precision (trailing zeros included)
    return ((r.get("measure") or "").upper().strip(), pr.get("effect") or x["effect"], pr.get("lower") or x["lower"],
            pr.get("upper") or x["upper"])


def gate(claim, label, held):
    if not isinstance(claim, dict) or claim.get("state") not in ("REPORTED", "NOT_REPORTED"):
        return {"state": "VERIFIER_REFUSED", "problems": ["NOT_TYPED"]}
    if claim["state"] == "NOT_REPORTED":
        return {"state": "VERIFIER_PASS", "reported": False}
    probs = []
    h = _norm(held)
    q, sq = _norm(claim.get("quote")), _norm(claim.get("scale_quote"))
    if not q or q not in h:
        probs.append("QUOTE_NOT_IN_SOURCE")
    if sq and sq not in h:
        probs.append("SCALE_QUOTE_NOT_IN_SOURCE")
    lab_tokens = [x for x in re.split(r"[\s,;()\[\]]+", k_gap.fold_dashes(label)) if len(x) >= 3 and not x.isdigit()]
    if lab_tokens and not any(k_gap.fold_dashes(tok).lower() in k_gap.fold_dashes(q).lower() for tok in lab_tokens[:2]):
        probs.append("LABEL_NOT_IN_QUOTE")
    eff = parse_comparator_effect(claim.get("quote"), claim.get("scale_quote")) if not probs else None
    if not probs and eff is None:
        probs.append("NO_PARSEABLE_EFFECT_IN_QUOTE")
    return {"state": "VERIFIER_REFUSED" if probs else "VERIFIER_PASS", "problems": probs, "reported": True,
            "comparator_effect": eff}


def main(argv):
    global OURS_SOURCE
    global WITH_SUPP
    if "--ours-rebuilt" in argv:
        OURS_SOURCE = "rebuilt"
    WITH_SUPP = "--with-supplements" in argv
    global WITH_FOREST
    WITH_FOREST = "--with-forest" in argv
    base = PROP.replace(".json", ".supp.json") if WITH_SUPP else PROP
    its = items()
    data = _j(base) if os.path.exists(base) else {}
    runs = data.get("runs", {})
    if WITH_SUPP and os.path.exists(PROP):
        # a topic with no supplement text has a byte-identical prompt: its recorded served run is the same call
        for slug, r in _j(PROP).get("runs", {}).items():
            runs.setdefault(slug, r)
    if "--run" in argv:
        done = {r["prompt_sha256"] for r in runs.values() if r["state"] == "RAN_OK"}
        todo = [it for it in its if hashlib.sha256(prompt(it)).hexdigest() not in done]
        print(f"topics {len(its)}, shared trials {sum(len(i['keyed']) for i in its)}, to run {len(todo)}", flush=True)
        with cf.ThreadPoolExecutor(max_workers=3) as ex:
            for r in ex.map(run_one, todo):
                runs[r["slug"]] = r
                print(r["slug"], r["state"], r["record_id"], flush=True)
    rows = []
    from collections import Counter
    for it in its:
        run = runs.get(it["slug"])
        resp = {}
        if run and run["state"] == "RAN_OK" and run["prompt_sha256"] == hashlib.sha256(prompt(it)).hexdigest():
            try:
                # the model may echo the item as 'T1: LEADER' (key + the label it was shown): key on the leading T<n>.
                # Keying on the exact string dropped all 46 answers as NO_ANSWER in the first run.
                resp = {item_key(x.get("item")): x for x in json.loads(ms.replay(ms.load_record(
                    os.path.join(REC_DIR, run["record_id"] + ".json"))).decode("utf-8")).get("items", [])}
            except Exception:  # noqa: BLE001
                resp = {}
        for key, k in it["keyed"]:
            claim = resp.get(key)
            g = gate(claim, k["label"], it["text"]) if claim else {"state": "NO_ANSWER"}
            theirs = g.get("comparator_effect")
            ours, how = our_effect(k["ours"], theirs[0] if theirs else None)
            verdict = ("NOT_REPORTED_BY_COMPARATOR" if g.get("state") == "VERIFIER_PASS" and not g.get("reported")
                       else agree(ours, theirs, how) if g.get("state") == "VERIFIER_PASS" else "GATE_REFUSED_OR_NO_ANSWER")
            src = "comparator_text"
            if WITH_FOREST and verdict == "NOT_REPORTED_BY_COMPARATOR":
                fr = forest_row(it["slug"], k["label"], k.get("pmids") or (), k.get("acronyms") or ())
                if fr:
                    theirs = fr
                    ours, how = our_effect(k["ours"], theirs[0])
                    verdict, src = "FOREST_" + agree(ours, theirs, how), "FOREST_PLOT_MODEL_READ_RECOMPUTED"
            rows.append({"slug": it["slug"], "label": k["label"], "our_id": k["ours"].get("id"), "ours": ours,
                         "ours_basis": how, "theirs": theirs, "theirs_source": src, "verdict": verdict, "gate": g,
                         "claim": claim, "record_id": (run or {}).get("record_id")})
    tally = Counter(r["verdict"].split("(")[0] for r in rows)
    out = {"n_topics": len(its), "n_shared_trials": len(rows), "tally": dict(tally), "runs": runs, "rows": rows,
           "ours_source": OURS_SOURCE}
    out["with_supplements"] = WITH_SUPP
    out["with_forest"] = WITH_FOREST
    target = base if OURS_SOURCE == "served" else base.replace(".json", ".rebuilt.json")
    if WITH_FOREST:
        target = target.replace(".json", ".forest.json")
    with open(target, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)
    print(json.dumps({k: out[k] for k in ("n_topics", "n_shared_trials", "tally")}, indent=1))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
