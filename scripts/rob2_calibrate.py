"""CALIBRATION of the formal RoB 2 against the comparators' PUBLISHED per-trial risk-of-bias judgements.

Inputs: outputs/robgrade/rob2/<slug>.json (ours: scripts/rob2_dual.py) and outputs/robgrade/reference/<slug>.json
(theirs: scripts/rob2_reference.py, a recorded dual transcription of the comparator's figure). Pairs are (trial, domain)
where the trial is in our served pool AND bound to a row of the comparator's figure through its reference list.

Domain mapping. A RoB 2 comparator maps one-to-one. A RoB 1 comparator ('Cochrane risk of bias tool') maps:
  D1 <- the worse of random sequence generation and allocation concealment
  D2 <- blinding of participants and personnel        D3 <- incomplete outcome data
  D4 <- blinding of outcome assessment                D5 <- selective reporting
  levels: low -> LOW, unclear / some concerns -> SOME_CONCERNS, high -> HIGH. 'Other bias' has no RoB 2 domain.
This is an APPROXIMATION (RoB 1 rates a study, RoB 2 a result; RoB 1 'unclear' is not RoB 2 'some concerns'), stated
on the report, never hidden.

Excluded from kappa and COUNTED (coverage, never dropped): our domain INSUFFICIENT_OPEN_SOURCE; a reference cell
unresolved or 'not shown'; a column the mapping cannot place.

Statistics per domain: n, raw agreement, Cohen's kappa (unweighted) and linear-weighted kappa on the ordinal
LOW < SOME_CONCERNS < HIGH, each with its asymptotic 95% CI (Fleiss, Cohen & Everitt 1969 variance); kappa is
undefined when either rater uses one category only (reported as such, never as 0 or 1).

    python scripts/rob2_calibrate.py [SLUG ...]     -> outputs/robgrade/calibration.json + CALIBRATION.md
"""
from __future__ import annotations

import io
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OURS = os.path.join(ROOT, "outputs", "robgrade", "rob2")
REF = os.path.join(ROOT, "outputs", "robgrade", "reference")
OUT = os.path.join(ROOT, "outputs", "robgrade", "calibration.json")
MD = os.path.join(ROOT, "outputs", "robgrade", "CALIBRATION.md")
CATS = ["LOW", "SOME_CONCERNS", "HIGH"]
LEVEL = {"low": "LOW", "unclear": "SOME_CONCERNS", "some concerns": "SOME_CONCERNS", "high": "HIGH"}

# column label (normalised) -> RoB 2 domain, for RoB 1 and RoB 2 figures
COLUMN_RULES = [
    (r"random sequence|sequence generation|randomi[sz]ation process|\bD1\b|randomi[sz]ation", "D1"),
    (r"allocation concealment", "D1"),
    (r"blinding of participants|performance bias|deviations? from intended|\bD2\b", "D2"),
    (r"incomplete outcome|attrition|missing outcome|\bD3\b", "D3"),
    (r"blinding of outcome|detection bias|measurement of the outcome|\bD4\b", "D4"),
    # 'Selective OUTCOME reporting' (probiotics 34385227): the first calibration run left all 32 of its D5 cells unmapped
    (r"selective (?:outcome )?reporting|reporting bias|selection of the reported|\bD5\b", "D5"),
    (r"^overall", "OVERALL"),
]


def domain_of(column):
    c = " ".join((column or "").lower().split())
    for pat, d in COLUMN_RULES:
        if re.search(pat, c, re.I):              # the label is lower-cased: a 'D3' pattern must not be case-sensitive
            return d
    return None


def worse(*levels):
    ls = [l for l in levels if l in CATS]
    return max(ls, key=CATS.index) if ls else None


def reference_domains(row, columns):
    """{D1..D5, OVERALL: level or None} from one reference row (RoB 1 D1 = worse of its two columns)."""
    by = {}
    for col in columns:
        d = domain_of(col)
        v = LEVEL.get((row["cells"].get(col) or "").lower())
        if d:
            by.setdefault(d, []).append(v)
    out = {}
    for d, vs in by.items():
        out[d] = None if any(v is None for v in vs) else worse(*vs)
    return out


def kappa(pairs, weighted=False):
    """Cohen's kappa (unweighted or linear-weighted) with the asymptotic 95% CI; None when undefined."""
    n = len(pairs)
    if n == 0:
        return None
    k = len(CATS)
    idx = {c: i for i, c in enumerate(CATS)}
    obs = [[0.0] * k for _ in range(k)]
    for a, b in pairs:
        obs[idx[a]][idx[b]] += 1 / n
    ra = [sum(obs[i]) for i in range(k)]
    cb = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    if sum(1 for x in ra if x > 0) < 2 and sum(1 for x in cb if x > 0) < 2:
        return {"kappa": None, "why": "both raters used one category only"}
    w = [[1 - abs(i - j) / (k - 1) if weighted else (1.0 if i == j else 0.0) for j in range(k)] for i in range(k)]
    po = sum(w[i][j] * obs[i][j] for i in range(k) for j in range(k))
    pe = sum(w[i][j] * ra[i] * cb[j] for i in range(k) for j in range(k))
    if pe >= 1:
        return {"kappa": None, "why": "expected agreement is 1"}
    kap = (po - pe) / (1 - pe)
    # Fleiss, Cohen & Everitt (1969) asymptotic variance (general weighted form)
    wi = [sum(cb[j] * w[i][j] for j in range(k)) for i in range(k)]
    wj = [sum(ra[i] * w[i][j] for i in range(k)) for j in range(k)]
    s = sum(ra[i] * cb[j] * (w[i][j] - (wi[i] + wj[j])) ** 2 for i in range(k) for j in range(k)) - pe ** 2
    se = math.sqrt(max(s, 0) / (n * (1 - pe) ** 2))
    return {"kappa": round(kap, 3), "ci": [round(kap - 1.96 * se, 3), round(kap + 1.96 * se, 3)], "po": round(po, 3),
            "pe": round(pe, 3)}


def pairs_for(slug):
    ours = json.load(open(os.path.join(OURS, f"{slug}.json"), encoding="utf-8"))
    ref = json.load(open(os.path.join(REF, f"{slug}.json"), encoding="utf-8"))
    tool = (ref.get("tool") or "")
    by_pmid = {}
    for lab, row in (ref.get("rows") or {}).items():
        if row.get("pmid"):
            by_pmid.setdefault(row["pmid"], []).append((lab, row))
    pairs, excluded, unmatched = [], [], []
    for pmid, o in ours["trials"].items():
        rows = by_pmid.get(pmid) or []
        if len(rows) != 1:
            unmatched.append({"pmid": pmid, "why": f"reference rows bound to it: {len(rows)}"})
            continue
        lab, row = rows[0]
        rd = reference_domains(row, ref.get("columns") or [])
        for d in ("D1", "D2", "D3", "D4", "D5"):
            mine = o["domains"][d]["judgement"]
            theirs = rd.get(d)
            ans = o["domains"][d]["answers"].values()
            src = {str(a.get("source_ref") or "").split(":")[0] for a in ans if a.get("answer") not in ("NI", "NA", None)}
            rec = {"slug": slug, "pmid": pmid, "label": lab, "domain": d, "ours": mine, "theirs": theirs, "tool": tool,
                   "ni_answers": sum(1 for a in ans if a.get("answer") == "NI"), "questions": len(ans),
                   "source_kinds": sorted(src), "from_full_text": "fulltext" in src}
            if mine not in CATS:
                excluded.append(dict(rec, why="ours " + str(mine)))
            elif theirs not in CATS:
                excluded.append(dict(rec, why="reference cell unresolved / not shown / no mapped column"))
            else:
                pairs.append(rec)
    return pairs, excluded, unmatched, tool


def main(argv):
    slugs = [a for a in argv if not a.startswith("--")] or sorted(
        f[:-5] for f in os.listdir(REF) if f.endswith(".json") and os.path.exists(os.path.join(OURS, f)))
    allp, alle, allu, tools = [], [], [], {}
    for s in slugs:
        p, e, u, t = pairs_for(s)
        allp += p
        alle += e
        allu += [dict(x, slug=s) for x in u]
        tools[s] = t
    per = {}

    def stats(ps):
        return {"n": len(ps), "raw_agreement": round(sum(a == b for a, b in ps) / len(ps), 3) if ps else None,
                "kappa": kappa(ps), "kappa_linear_weighted": kappa(ps, weighted=True)}
    for d in ("D1", "D2", "D3", "D4", "D5"):
        xs = [x for x in allp if x["domain"] == d]
        ps = [(x["ours"], x["theirs"]) for x in xs]
        per[d] = dict(stats(ps), excluded=sum(1 for x in alle if x["domain"] == d),
                      confusion={f"{a}->{b}": sum(1 for x, y in ps if (x, y) == (a, b)) for a in CATS for b in CATS
                                 if any((x, y) == (a, b) for x, y in ps)},
                      ni_share=round(sum(x["ni_answers"] for x in xs) / max(1, sum(x["questions"] for x in xs)), 3),
                      # the information the readers had: a domain with any answer from a full text v abstract/registry only
                      strata={"any_answer_from_full_text": stats([(x["ours"], x["theirs"]) for x in xs if x["from_full_text"]]),
                              "abstract_or_registry_only": stats([(x["ours"], x["theirs"]) for x in xs if not x["from_full_text"]])})
    out = {"topics": slugs, "tools": tools, "per_domain": per, "pairs": allp, "excluded": alle, "unmatched_trials": allu}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    lines = ["# RoB 2 calibration v published comparator judgements", "",
             f"Topics: {', '.join(slugs)}. Reference tools: " + "; ".join(f"{s}: {t or '?'}" for s, t in tools.items()), "",
             "| domain | n pairs | raw agreement | kappa (95% CI) | linear-weighted kappa (95% CI) | excluded |",
             "|---|---|---|---|---|---|"]
    for d, v in per.items():
        def fk(k):
            return "undefined" if not k or k.get("kappa") is None else f"{k['kappa']} ({k['ci'][0]}, {k['ci'][1]})"
        lines.append(f"| {d} | {v['n']} | {v['raw_agreement']} | {fk(v['kappa'])} | {fk(v['kappa_linear_weighted'])} | {v['excluded']} |")
    lines += ["", "| domain | share of answers NI | kappa, any answer from a full text (n) | kappa, abstract/registry only (n) |",
              "|---|---|---|---|"]
    for d, v in per.items():
        s = v["strata"]

        def fs(x):
            k = x["kappa"]
            return f"{'undefined' if not k or k.get('kappa') is None else k['kappa']} ({x['n']})"
        lines.append(f"| {d} | {v['ni_share']} | {fs(s['any_answer_from_full_text'])} | {fs(s['abstract_or_registry_only'])} |")
    lines += ["", f"Unmatched trials (in our pool, not bound to exactly one reference row): {len(allu)}"]
    with open(MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
