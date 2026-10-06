"""SECONDARY_SINGLE from a meta's OPEN SUPPLEMENTARY TABLE (G1 binding lane). Deterministic: no model.

Mahmood 3 Oct (scripts/g1_tracker.py secondary_single): with NO primary source openly available, a per-trial row from
ONE published meta that is NOT the comparator counts when that meta reproduces its OWN printed pooled result from its
rows, the row passes typed admission, and no other non-comparator row contradicts it. This module applies exactly those
conditions to a meta whose per-trial rows are printed only in its supplementary .docx (Europe PMC supplementaryFiles;
open access, legitimate). Rules:

  S1  EXCERPT     the supplement is held locally (outputs/k_gap/_ft/, gitignored: its licence may forbid redistribution);
                  only the typed numbers are committed -- the binary-outcome rows for the topic outcome, the dose column,
                  and the meta's own printed pooled sentence -- with the supplement's sha256.
  S2  CONTROL     the meta's printed pooled results are reproduced from the excerpt under the meta's OWN stated rules
                  (printed in its methods: node threshold, 0.5 correction for single-zero studies, double-zero excluded).
                  Inverse-variance common effect is used ONLY when the meta prints tau^2 = 0 (REML with tau^2 = 0 is the
                  common-effect pool); otherwise the control is NOT_REPRODUCIBLE and no row is admitted. Equality at
                  the printed precision for the point estimate and both bounds, for every printed node.
  S3  ADMIT       per trial: the row is the topic outcome (the supplement's own horizon column names a topic timepoint);
                  the row's arm Ns equal the same trial's Ns in every other row of the same source table, in the same
                  orientation (swapped -> ARM_N_SWAPPED_WITHIN_SOURCE, else ARM_N_INCONSISTENT_WITHIN_SOURCE); a trial
                  split into subgroup rows ('*' rows) -> SUBGROUP_SPLIT_ROWS; the source's own data-source column naming
                  another secondary -> SECONDARY_OF_SECONDARY. Every refusal is named, with the rows as span.
  S4  CIRCULARITY the meta is never the topic comparator (PMID or DOI).

    python scripts/g1_binding_secondary.py SLUG META_PMID PMCID [--run]  -> outputs/k_gap/g1_binding/secondary_<slug>.json
"""
from __future__ import annotations

import hashlib
import html
import io
import json
import math
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding")
HELD = os.path.join(ROOT, "outputs", "k_gap", "_ft")


def docx_tables(b):
    x = zipfile.ZipFile(io.BytesIO(b)).read("word/document.xml").decode("utf-8", "replace")
    out = []
    for tbl in re.findall(r"<w:tbl>.*?</w:tbl>", x, re.S):
        out.append([[html.unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", tc))).strip()
                     for tc in re.findall(r"<w:tc>.*?</w:tc>", tr, re.S)]
                    for tr in re.findall(r"<w:tr[ >].*?</w:tr>", tbl, re.S)])
    return out


def _key(label):
    return re.sub(r"[#*]", "", label or "").strip().lower()


def excerpt(tables, outcome_re):
    """S1: binary rows [label, drug, outcome, e_t, n_t, e_c, n_c], the dose table, the horizon/data-source table."""
    binary, dose, horizon = [], {}, {}
    for t in tables:
        head = [c.lower() for c in (t[0] if t else [])]
        for r in t:
            if len(r) >= 7 and all(re.fullmatch(r"\d+", c or "") for c in r[3:7]):
                binary.append(r[:7])
            elif len(r) >= 5 and re.search(r"\d{4}", r[0]) and re.fullmatch(r"\d+\.\d+", r[3] or "") \
                    and "equivalentdose" in "".join(head).replace(" ", ""):
                dose.setdefault(_key(r[0]), float(r[3]))
            elif len(r) >= 3 and re.search(r"\d{4}", r[0]) and "time horizon" in head and "outcome data source" in head:
                horizon[_key(r[0])] = {"horizon": r[1], "data_source": r[2]}
    rows = [r for r in binary if re.search(outcome_re, r[2], re.I)]
    return {"outcome_rows": rows, "all_binary_rows": binary, "dose": dose, "horizon": horizon}


def log_rr(a, n1, c, n2):
    if a == 0 and c == 0:
        return None
    if 0 in (a, c):
        a, c, n1, n2 = a + .5, c + .5, n1 + 1, n2 + 1
    return math.log((a / n1) / (c / n2)), 1 / a - 1 / n1 + 1 / c - 1 / n2


def node_pool(rows, dose, threshold):
    """S2: inverse-variance common-effect RR per node (higher >= threshold, lower < threshold)."""
    acc = {"higher": [], "lower": []}
    for r in rows:
        d = dose.get(_key(r[0]))
        if d is None:
            return None, f"NO_DOSE_FOR:{r[0]}"
        z = log_rr(*map(int, r[3:7]))
        if z:
            acc["higher" if d >= threshold else "lower"].append(z)
    out = {}
    for k, L in acc.items():
        w = sum(1 / v for _, v in L)
        m = sum(l / v for l, v in L) / w
        se = 1 / math.sqrt(w)
        out[k] = {"k": len(L), "rr": (math.exp(m), math.exp(m - 1.959964 * se), math.exp(m + 1.959964 * se))}
    return out, None


def _eq(x, printed):
    dec = len(printed.split(".")[1]) if "." in printed else 0
    return abs(round(x, dec) - float(printed)) < 1e-9


def positive_control(ex, printed, threshold, tau2_printed):
    if tau2_printed != "0":
        return {"reproduced": False, "why": "NOT_REPRODUCIBLE: tau^2 not printed as 0 (the REML fit is not reconstructed)"}
    pooled, err = node_pool(ex["outcome_rows"], ex["dose"], threshold)
    if err:
        return {"reproduced": False, "why": err}
    res = {}
    for node, (pt, lo, hi) in printed.items():
        got = pooled[node]["rr"]
        res[node] = {"printed": [pt, lo, hi], "computed": [round(v, 4) for v in got], "k": pooled[node]["k"],
                     "equal": _eq(got[0], pt) and _eq(got[1], lo) and _eq(got[2], hi)}
    return {"reproduced": all(v["equal"] for v in res.values()), "nodes": res, "threshold": threshold,
            "model": "inverse-variance common effect (meta prints tau^2 = 0)"}


def admit(trial_key, ex, timepoint_re):
    """S3 for one trial: (values, None) or (None, refusal)."""
    rows = [r for r in ex["outcome_rows"] if _key(r[0]) == trial_key]
    split = [r for r in ex["outcome_rows"] if _key(r[0]) == trial_key and "*" in r[0]]
    span = {"rows": rows}
    if not rows:
        return None, {"why": "NO_ROW_IN_SOURCE"}
    if split or len(rows) > 1:
        return None, {"why": "SUBGROUP_SPLIT_ROWS", **span}
    hz = ex["horizon"].get(trial_key) or {}
    span["horizon"] = hz
    if not re.search(timepoint_re, hz.get("horizon") or "", re.I):
        return None, {"why": "HORIZON_NOT_TOPIC_TIMEPOINT", **span}
    if re.search(r"secondary source", hz.get("data_source") or "", re.I):
        return None, {"why": "SECONDARY_OF_SECONDARY", **span}
    e_t, n_t, e_c, n_c = map(int, rows[0][3:7])
    others = [r for r in ex["all_binary_rows"] if _key(r[0]) == trial_key and r not in rows]
    span["other_rows"] = others
    for o in others:
        on_t, on_c = int(o[4]), int(o[6])
        if (on_t, on_c) == (n_c, n_t) and n_t != n_c:
            return None, {"why": "ARM_N_SWAPPED_WITHIN_SOURCE", **span}
        if (on_t, on_c) != (n_t, n_c):
            return None, {"why": "ARM_N_INCONSISTENT_WITHIN_SOURCE", **span}
    return {"events_t": e_t, "n_t": n_t, "events_c": e_c, "n_c": n_c}, None


def fetch_supplement(pmcid):
    import urllib.request
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/supplementaryFiles"
    with urllib.request.urlopen(url, timeout=120) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    docs = [n for n in z.namelist() if n.lower().endswith(".docx")]
    if len(docs) != 1:
        raise RuntimeError(f"{pmcid}: expected one .docx supplement, got {docs}")
    return docs[0], z.read(docs[0])


# The meta's own printed statements, quoted from its open JATS (PMC13613698) -- the numbers the control must reproduce.
METAS = {
    "42402602": {"pmcid": "PMC13613698", "doi": "10.1186/s13054-026-06185-5", "licence": "CC BY-NC-ND 4.0",
                 "outcome_re": r"all causes mortality \(short term\)",
                 "threshold": 7.5, "threshold_span": "Interventions were classified as higher dose (≥ 7.5 mg/d), lower "
                                                     "dose (< 7.5 mg/d), or control (placebo or usual care).",
                 "tau2_printed": "0", "tau2_span": "Heterogeneity was low (I 2 = 17.6%; τ² = 0; Q test P = .20).",
                 "correction_span": "A continuity correction of 0.5 was applied to single-zero studies, whereas "
                                    "double-zero studies were excluded from relative effect estimation.",
                 "printed": {"higher": ("0.83", "0.74", "0.92"), "lower": ("0.84", "0.75", "0.95")},
                 "printed_span": "Compared with placebo, higher-dose corticosteroids (RR, 0.83; 95% CI, 0.74–0.92; low "
                                 "confidence) and lower-dose corticosteroids (RR, 0.84; 95% CI, 0.75–0.95; moderate "
                                 "confidence) were associated with lower short-term all-cause mortality."}}

# our tracker label stem -> the supplement's row key (author year), joined by the trial's PMID in OUR tracker
TRIAL_KEYS = {"corticosteroids-cap-mortality": {"15557131": "confalonieri 2005", "8339624": "marik 1993",
                                                "4404939": "mchardy and schonell 1972", "20133929": "snijders 2010",
                                                "21636122": "meijvis 2011", "17710485": "mikami 2007",
                                                "25608756": "blum 2015"}}
TIMEPOINT_RE = {"corticosteroids-cap-mortality": r"30-day|in-hospital"}


def main(argv):
    slug, meta, run = argv[0], argv[1], "--run" in argv
    m = METAS[meta]
    held = os.path.join(HELD, f"suppl_{meta}.docx")
    if not os.path.exists(held):
        if not run:
            sys.exit(f"{held} not held; rerun with --run to fetch {m['pmcid']} supplementaryFiles")
        name, b = fetch_supplement(m["pmcid"])
        os.makedirs(HELD, exist_ok=True)
        open(held, "wb").write(b)
    b = open(held, "rb").read()
    tracker = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", slug + ".json"), encoding="utf-8"))
    comp = str(tracker.get("comparator_pmid"))
    if meta == comp:
        sys.exit("S4: the meta is the topic comparator -- refused (anti-circularity)")
    ex = excerpt(docx_tables(b), m["outcome_re"])
    pc = positive_control(ex, m["printed"], m["threshold"], m["tau2_printed"])
    res = []
    for x in tracker["trials"]:
        pmid = str(x.get("family") or "").replace("PMID ", "")
        key = TRIAL_KEYS.get(slug, {}).get(pmid)
        if not key or x.get("route") not in ("NO_ROW", "UNVERIFIED"):
            continue
        vals, why = admit(key, ex, TIMEPOINT_RE[slug]) if pc["reproduced"] else (None, {"why": "CONTROL_NOT_REPRODUCED"})
        res.append({"slug": slug, "label": x["label"], "pmid": pmid, "source_row_key": key, "admitted": bool(vals),
                    "values": vals, **({"refusal": why} if why else {"span": {
                        "rows": [r for r in ex["outcome_rows"] if _key(r[0]) == key],
                        "horizon": ex["horizon"].get(key)}})})
    out = {"slug": slug, "meta_pmid": meta, "meta_doi": m["doi"], "pmcid": m["pmcid"], "licence": m["licence"],
           "supplement_sha256": hashlib.sha256(b).hexdigest(), "comparator_pmid": comp,
           "rules": "S1-S4 (scripts/g1_binding_secondary.py)", "meta_statements": {k: m[k] for k in (
               "threshold_span", "tau2_span", "correction_span", "printed_span")},
           "positive_control": pc, "excerpt": {"outcome_rows": ex["outcome_rows"], "dose": ex["dose"],
                                               "horizon": ex["horizon"],
                                               "other_rows_of_target_trials": [r for r in ex["all_binary_rows"] if _key(
                                                   r[0]) in TRIAL_KEYS.get(slug, {}).values() and r not in ex["outcome_rows"]]},
           "bindings": res}
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"secondary_{slug}.json")
    with open(p + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    os.replace(p + ".tmp", p)
    print("control", pc["reproduced"], {k: (v["computed"], v["printed"]) for k, v in (pc.get("nodes") or {}).items()})
    for r in res:
        print(f"{r['source_row_key']:28s} {'ADMIT ' + str(r['values']) if r['admitted'] else 'REFUSE ' + r['refusal']['why']}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
