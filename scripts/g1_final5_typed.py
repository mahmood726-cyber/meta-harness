"""FINAL-5 typed (deterministic) readers, binding lane, 8 Oct 2026. Regex / table typing first; the recorded model readers
(scripts/g1_final5_readers.py) are second readers only, and never see a non-CC text.

  RECOVERY ventilated subgroup  the trial's own supplementary appendix (PMC7383595 OA package, NEJM COVID licence: NOT
                                redistributable, so it is held LOCALLY, git-ignored, pinned by sha256, and never shown to a
                                model). Table S2 is read by two independent PDF engines (poppler pdftotext -raw and MuPDF);
                                the K5 binding names one as the document and the other as the second extraction.
  CONFIRM-HF (D14)              Table 2 of the held CC BY text; second readers: the two recorded final-5 readers.
  ENGAGE (D16 C, AACT route)    AACT 2026-08-30 outcome_analyses for NCT00781391: every posted analysis of the primary is
                                classified FOUND / REFUSED with its reason (only a 95% CI for the ITT high-dose v warfarin
                                comparison of the primary outcome is FOUND).
  CoDEX 28-day                  AACT (no posted results), held abstract (percentages only), PMC body (publisher withholds).

    python scripts/g1_final5_typed.py [--fetch]   -> outputs/k_gap/g1_binding/final5_typed.json
                                                     (+ the K5 bindings, staged for registry/d12_counts_for_matching.json)
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "final5_typed.json")
SUPP = os.path.join("outputs", "k_gap", "_supp", "PMC7383595")      # git-ignored (outputs/k_gap/.gitignore)
RECOVERY_PDF = {"url": "https://pmc-oa-opendata.s3.amazonaws.com/PMC7383595.1/NEJMoa2021436_appendix.pdf",
                "sha256": "ba84d546708aa8ed90bfc05006af9a83e7809cda526793d13a24b5e90f06b234",
                "licence": "PMC OA COVID-19 licence (NEJM): re-use and analysis permitted, NOT a CC licence -- held "
                           "locally only, never committed, never in a model prompt (D8)"}


def _sha_text(p):
    return hashlib.sha256(open(p, encoding="utf-8").read().encode("utf-8")).hexdigest()


def _plain(t, fmt="xml"):
    """The same rendering g1_d12 matches against: only markup ('xml') is tag-stripped; extracted PDF text is not."""
    import html
    s = t or ""
    if fmt == "xml":
        s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", s).strip()


def recovery_texts(fetch=False):
    """(raw_path, mupdf_path) repo-relative, or (None, why). Fetches only with --fetch; the PDF must hash to the pin."""
    d = os.path.join(ROOT, SUPP)
    pdf = os.path.join(d, "NEJMoa2021436_appendix.pdf")
    if not os.path.exists(pdf):
        if not fetch:
            return None, "NOT_HELD (run with --fetch)"
        os.makedirs(d, exist_ok=True)
        from harness import http
        data = http.get_bytes(RECOVERY_PDF["url"]) if hasattr(http, "get_bytes") else None
        if data is None:
            import urllib.request
            req = urllib.request.Request(RECOVERY_PDF["url"], headers={"User-Agent": "meta-harness (meta-harness@example.org)"})
            data = urllib.request.urlopen(req, timeout=120).read()
        if hashlib.sha256(data).hexdigest() != RECOVERY_PDF["sha256"]:
            return None, "FETCHED_BYTES_DO_NOT_MATCH_THE_PIN"
        open(pdf, "wb").write(data)
    if hashlib.sha256(open(pdf, "rb").read()).hexdigest() != RECOVERY_PDF["sha256"]:
        return None, "HELD_PDF_DOES_NOT_MATCH_THE_PIN"
    raw = os.path.join(d, "appendix.poppler_raw.txt")
    mu = os.path.join(d, "appendix.mupdf.txt")
    if not os.path.exists(raw):
        subprocess.run(["pdftotext", "-raw", "-enc", "UTF-8", pdf, raw], check=True)
    if not os.path.exists(mu):
        import fitz
        with fitz.open(pdf) as doc:
            open(mu, "w", encoding="utf-8", newline="\n").write("\n".join(p.get_text() for p in doc))
    return (os.path.relpath(raw, ROOT).replace("\\", "/"), os.path.relpath(mu, ROOT).replace("\\", "/")), None


def recovery_binding(fetch=False):
    got, why = recovery_texts(fetch)
    if not got:
        return None, why
    raw, mu = got
    t1 = _plain(open(os.path.join(ROOT, raw), encoding="utf-8").read(), "text")
    t2 = _plain(open(os.path.join(ROOT, mu), encoding="utf-8").read(), "text")
    cap = ("Table S2: Impact of adjusting for the 1.1-year age imbalance between randomised arms on the estimated effect "
           "of allocation to dexamethasone on 28-day mortality")
    head = "Dexamethasone (n=2104) Usual care (n=4321)"
    rx = re.compile(r"Invasive mechanical ventilation (\d+)/(\d+) \(([\d.]+)%\) (\d+)/(\d+) \(([\d.]+)%\) "
                    r"0\.64 \(0\.51-0\.81\)")
    m1, m2 = rx.search(t1[t1.rfind(cap):]), rx.search(t2[t2.rfind(cap):])
    if not (m1 and m2) or m1.group(0) != m2.group(0):
        return None, "TWO_ENGINES_DO_NOT_HOLD_THE_SAME_ROW"
    et, nt, pt, ec, nc, pc = m1.groups()
    et, nt, ec, nc = int(et), int(nt), int(ec), int(nc)
    # the printed percentages are events/N at their printed precision (a typed self-check, not a source)
    if round(100 * et / nt, 1) != float(pt) or round(100 * ec / nc, 1) != float(pc):
        return None, "PERCENT_NOT_EVENTS_OVER_N"
    return {"slug": "corticosteroids-covid19-mortality", "label": "RECOVERY", "pmid": "32678530", "ncts": [],
            "own_tuple": True, "tuple_kind": "COUNTS", "rule": "K5", "source_kind": "SUPPLEMENT",
            "outcome": "28-day all-cause mortality",
            "analysis_set": "SUBGROUP: receiving invasive mechanical ventilation at randomisation (the comparator "
                            "pooled this subgroup: 324 + 683 = 1007)",
            "values": {"events_t": et, "n_t": nt, "events_c": ec, "n_c": nc},
            "source": f"RECOVERY supplementary appendix Table S2 ({RECOVERY_PDF['url']}, pdf sha256 "
                      f"{RECOVERY_PDF['sha256']}; {RECOVERY_PDF['licence']})",
            "doc": {"path": raw, "format": "text", "text_sha256": _sha_text(os.path.join(ROOT, raw)),
                    "what": "poppler pdftotext -raw of the pinned appendix (local, git-ignored)"},
            "caption_span": cap, "header_span": head, "row_span": m1.group(0),
            "outcome_from": "caption", "cells": {"events_t": 0, "events_c": 2},
            "second_reader": {"kind": "SECOND_EXTRACTION",
                              "doc": {"path": mu, "format": "text", "text_sha256": _sha_text(os.path.join(ROOT, mu)),
                                      "what": "MuPDF (PyMuPDF) text of the same pinned appendix: an independent engine"},
                              "row_span": m2.group(0)},
            "decision": "D12 (Mahmood 'approve d12', 8 Oct): a held primary span, verbatim"}, None


def confirm_hf_binding():
    path = "cache/iv-iron-hfref-hosp/ft_25176939.txt"
    t = _plain(open(os.path.join(ROOT, path), encoding="utf-8").read())
    cap, head = "Hospitalizations and deaths (full-analysis set)", "FCM ( n = 150) Placebo ( n = 151)"
    m = re.search(r"Hospitalizations due to worsening HF (\d+) (\d+) \(([\d.]+)\) (\d+) (\d+) \(([\d.]+)\)", t)
    if not m or cap not in t or head not in t:
        return None, "TABLE_2_ROW_NOT_FOUND"
    ev_t, pt_t, _r1, ev_c, pt_c, _r2 = m.groups()
    led = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "final5_readers.json"), encoding="utf-8"))
    rids = [r["record_id"] for r in led["rows"] if r["label"] == "CONFIRM-HF" and r["verdict"] == "GATED"]
    return {"slug": "iv-iron-hfref-hosp", "label": "CONFIRM-HF", "pmid": "25176939", "ncts": ["NCT01453608"],
            "own_tuple": True, "tuple_kind": "COUNTS", "rule": "K5", "source_kind": "FULL_TEXT",
            "outcome": "Heart-failure hospitalization (patients with >=1 hospitalisation due to worsening HF)",
            "analysis_set": "full-analysis set (Table 2 caption)",
            "values": {"events_t": int(pt_t), "n_t": 150, "events_c": int(pt_c), "n_c": 151},
            "events_total_not_patients": {"t": int(ev_t), "c": int(ev_c)},
            "source": "PMID 25176939 PMC4359359 (CC BY 4.0) Table 2",
            "doc": {"path": path, "format": "xml", "text_sha256": _sha_text(os.path.join(ROOT, path)),
                    "what": "held CC BY full text"},
            "caption_span": cap, "header_span": head, "row_span": m.group(0),
            "outcome_from": "row", "cells": {"events_t": 1, "events_c": 4},
            "second_reader": {"kind": "RECORDED_READERS", "dir": "evidence/model_calls/final5", "record_ids": rids},
            "decision": "D14 (V10-04Q, Mahmood 'yes all v10'): the incidence numerator is patients, 10 v 25 of "
                        "150/151; with D12 for the matching use"}, None


V12_02Q = ("V12-02Q (choice B, Mahmood 9 Oct 'yes all as recommended', packet ae88366b...): EFFECT-HF left UNBOUND -- "
           "the 11 v 6 are safety-set patients and the safety-set N is not printed, so there are no verbatim "
           "denominators. Supersedes D15's 11/86 v 6/86 FAS binding.")


def effect_hf_row():
    """D15 bound EFFECT-HF 11/86 v 6/86 on the FAS; V12-02Q (B) superseded it. No row is ever produced again."""
    return None, V12_02Q


def unbind_effect_hf():
    """V12-02Q: the acquisition ledger's EFFECT-HF row returns to main's pre-D15 row (not admitted), marked with the
    decision. Only that row changes."""
    p = os.path.join(ROOT, "registry", "g1_acquired", "iv-iron-hfref-hosp.json")
    raw = open(p, encoding="utf-8").read()
    d = json.loads(raw)
    i = [k for k, r in enumerate(d["rows"]) if r.get("label") == "EFFECT-HF [21]"]
    if len(i) != 1:
        raise SystemExit(f"EFFECT-HF rows in the acquisition ledger: {len(i)}")
    r = d["rows"][i[0]]
    if r.get("verdict") == "ADMITTED":
        prev = r.get("superseded") or {}
        r = {k: v for k, v in r.items() if k not in ("verdict", "decision", "admitted", "typed_by", "superseded")}
        r.update({k: prev[k] for k in ("record_id", "verdict", "model") if k in prev})
    r["unbound_by"] = V12_02Q
    d["rows"][i[0]] = r
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(d, indent=1, ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""))


def comparator_findings():
    """registry/g1_signed_comparator_findings.json: D14 (SIGNED) for CONFIRM-HF; EFFECT-HF's twin finding PROPOSED only
    (D15 binds the counts but does not name the comparator side -- that is a question for Mahmood)."""
    cfm, eff = "cache/iv-iron-hfref-hosp/ft_25176939.txt", "cache/iv-iron-hfref-hosp/ft_28701470.txt"
    doc = lambda p: {"path": p, "format": "xml", "text_sha256": _sha_text(os.path.join(ROOT, p))}  # noqa: E731
    return {"rule": "g1_tracker.signed_comparator_findings: applied only when SIGNED and verified at build",
            "findings": [
                {"slug": "iv-iron-hfref-hosp", "pmid": "25176939", "label": "CONFIRM-HF", "state": "SIGNED",
                 "decision": "D14 (V10-04Q)", "finding": "COMPARATOR_COUNTS_ARE_EVENTS",
                 "signed": "Mahmood 'yes all v10', packet sha256 9086d538fdb85c5901cb0222ed459f43264487b1886731fbf3cbf9ee669101ff",
                 "doc": doc(cfm), "row_span": "Hospitalizations due to worsening HF 10 10 (7.6) 32 25 (19.4)",
                 "cells": {"comparator": {"events_t": 0, "events_c": 3}, "ours": {"events_t": 1, "events_c": 4}},
                 "comparator_counts": {"events_t": 10, "events_c": 32}, "our_counts": {"events_t": 10, "events_c": 25},
                 "unit_spans": {"comparator": "Total number of events",
                                "ours": "computed using the number of subjects with the end-point/event"},
                 "note": "Table 2 (full-analysis set): 'Total number of events' 10 v 32; patients with an event 10 v 25"},
                {"slug": "iv-iron-hfref-hosp", "pmid": "28701470", "label": "EFFECT-HF", "state": "SIGNED",
                 "decision": "V12-03Q (sign)", "finding": "COMPARATOR_COUNTS_ARE_EVENTS",
                 "signed": "Mahmood 'yes all as recommended' (9 Oct), registry/v12_signatures.json, packet "
                           "ae88366bf626bc1eebbb60dd02324e7f8ae0b248e4ee995f3ff7de86f5b92933, item section 0ef88d69...",
                 "doc": doc(eff),
                 "row_span": "26 of them for worsening HF (13 in each group) in 17 patients (11 patients on FCM and 6 "
                             "on usual care).",
                 "cells": {"comparator": {"events_t": 1, "events_c": 1}, "ours": {"events_t": 3, "events_c": 4}},
                 "comparator_counts": {"events_t": 13, "events_c": 13}, "our_counts": {"events_t": 11, "events_c": 6},
                 "unit_spans": {"comparator": "A total of 58 hospitalizations occurred during the study",
                                "ours": "in 17 patients (11 patients on FCM and 6 on usual care)"},
                 "note": "the comparator's 13 v 13 are the 26 worsening-HF HOSPITALISATIONS (13 in each group); the "
                         "patients are 11 v 6. Its 88 is the safety-set FCM N (FAS 86 + 2), not printed by the paper"}]}


def engage_aact():
    """Every posted analysis of NCT00781391, classified against the D16 C target."""
    d = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "engage_aact_rows.json"), encoding="utf-8"))
    T = d["tables"]
    oc = {r["id"]: r for r in T["outcomes.txt"]}
    gr = {r["id"]: r["title"] for r in T["result_groups.txt"]}
    ag = {}
    for r in T["outcome_analysis_groups.txt"]:
        ag.setdefault(r["outcome_analysis_id"], []).append(gr.get(r["result_group_id"]))
    rows = []
    for a in T["outcome_analyses.txt"]:
        o = oc.get(a["outcome_id"], {})
        groups = sorted(g for g in ag.get(a["id"], []) if g)
        why = []
        t_ = str(o.get("title") or "").lower()
        if "stroke" not in t_ or not ("systemic embol" in t_ or "see" in t_.replace("(", " ").replace(")", " ").split()):
            why.append(f"NOT_STROKE_OR_SEE ({str(o.get('title') or '')[:60]})")      # codex final5-binding-r1b g1#4
        if o.get("outcome_type") != "PRIMARY":
            why.append(f"NOT_THE_PRIMARY_OUTCOME ({o.get('outcome_type')}: {o.get('title', '')[:80]})")
        if not str(o.get("population") or "").startswith("ITT"):
            why.append(f"NOT_ITT ({str(o.get('population') or '')[:40]})")
        if not any(g.startswith("High Dose Edoxaban") for g in groups):
            why.append("NOT_HIGH_DOSE")
        # the OTHER group must be warfarin: high dose v low dose is not the comparison (codex final5-binding-r1a g1#4)
        if len(groups) != 2 or not any(g.startswith("Warfarin") for g in groups):
            why.append("NOT_V_WARFARIN")
        if str(a.get("ci_percent")) not in ("95", "95.0"):
            why.append(f"CI_IS_{a.get('ci_percent')}%_NOT_95%")
        rows.append({"analysis_id": a["id"], "outcome_id": a["outcome_id"], "param": a["param_type"],
                     "value": a["param_value"], "ci_percent": a["ci_percent"], "ci": [a["ci_lower_limit"], a["ci_upper_limit"]],
                     "groups": groups, "verdict": "FOUND" if not why else "REFUSED", "why": why})
    found = [r for r in rows if r["verdict"] == "FOUND"]
    return {"route": "AACT 2026-08-30 outcome_analyses (binding lane)", "nct": "NCT00781391",
            "result": "FOUND" if found else "NOT_FOUND", "found": found, "analyses": rows,
            "second_readers": "recorded codex readers final5::ENGAGE-AACT::A/B (outputs/k_gap/g1_binding/final5_readers.json)"}


def codex_28d():
    """Each route is READ now; a route that cannot be read is NOT_CHECKED, and absence is claimed only when every route
    was read (codex final5-binding-r1a g1#5: the routes were fixed strings)."""
    nct, pmid, routes = "NCT04327401", "32876695", []
    snap = os.environ.get("AACT_SNAPSHOT") or "F:/AACT-storage/AACT/2026-08-30"
    op = os.path.join(snap, "outcomes.txt")
    if os.path.isfile(op):
        n = 0
        with open(op, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if nct in line and line.split("|", 2)[1:2] == [nct]:
                    n += 1
        routes.append({"route": f"AACT {os.path.basename(snap.rstrip('/'))}",
                       "outcome": "NO_POSTED_RESULTS" if n == 0 else f"POSTED_OUTCOMES:{n}"})
    else:
        routes.append({"route": "AACT", "outcome": "NOT_CHECKED (no snapshot)"})
    rp = os.path.join(ROOT, "cache", "corticosteroids-covid19-mortality", "records.json")
    ab = None
    if os.path.isfile(rp):
        ab = next((r.get("abstract") for r in json.load(open(rp, encoding="utf-8")).get("records", [])
                   if str(r.get("id")) == pmid), None)
    if not (ab or "").strip():
        # no record, or a record with no abstract: nothing was read (codex final5-binding-r2 g1#3)
        routes.append({"route": "held abstract", "outcome": "NOT_CHECKED (no abstract held)"})
    else:
        sents = [s for s in re.split(r"(?<=[.;])\s+", ab) if re.search(r"mortality|death|died", s, re.I)
                 and re.search(r"28", s)]
        # a count written as a fraction, 'e of N', a percentage, or in prose ('45 patients ... died') (r2 g1#2)
        cnt = re.compile(r"(?<![\d.])\d+\s*(?:/|of)\s*\d+(?![\d.])|\d+(?:[.,]\d+)?\s*%|"
                         r"(?<![\d.,-])\d+\s+(?:deaths|died|deceased)\b|"
                         # people counted only when THEY died in the same clause (codex final5-binding-r3 g1#2)
                         r"(?<![\d.,-])\d+\s+(?:patients|participants)\b[^.;]{0,80}?\b(?:died|deaths?|deceased)\b|"
                         # ... or the death named first ('mortality occurred in 45 patients'; r4 g1#3)
                         r"\b(?:died|deaths?|deceased|mortality occurred)\b[^.;]{0,40}?\bin\s+\d+\s+(?:patients|participants)\b",
                         re.I)
        counts = [s for s in sents if cnt.search(s)]
        routes.append({"route": "held abstract", "outcome": (f"COUNTS_OR_PERCENTS_PRINTED:{counts[:2]}" if counts else
                                                             "NO_COUNTS (28-day mortality sentences: "
                                                             f"{len(sents)}, none with a count or a percentage)")})
    fi = os.path.join(ROOT, "outputs", "k_gap", "fulltext_index.json")
    st = (json.load(open(fi, encoding="utf-8")).get(pmid) or {}) if os.path.isfile(fi) else None
    # only a recorded retrieval OUTCOME is a check: an entry with a licence but no state read nothing (r2 g1#4); a HELD
    # body is a candidate to read, never an absence
    absent = ("FETCH_EMPTY", "NO_PMCID", "PUBLISHER_DISALLOWS_XML")
    s_ = (st or {}).get("state")
    routes.append({"route": "PMC body", "outcome": (f"{s_} ({st.get('copy_licence') or 'licence unread'})" if s_ in absent
                                                    else f"HELD_BODY_UNREAD ({st.get('copy_licence')})" if s_ == "HELD"
                                                    else f"NOT_CHECKED (index state {s_!r})")})
    oks = [r["outcome"] for r in routes]
    res = ("NOT_CHECKED" if any(o.startswith("NOT_CHECKED") for o in oks) else
           "CANDIDATE" if any(o.startswith(("POSTED", "COUNTS", "HELD_BODY")) for o in oks) else "NOT_FOUND")
    return {"trial": "CoDEX", "pmid": pmid, "nct": nct, "result": res, "routes": routes}


def main(argv):
    out = {"items": {}}
    b1, w1 = recovery_binding(fetch="--fetch" in argv)
    b2, w2 = confirm_hf_binding()
    out["items"]["RECOVERY"] = b1 or {"state": "NOT_STAGED", "why": w1}
    out["items"]["CONFIRM-HF"] = b2 or {"state": "NOT_STAGED", "why": w2}
    b3, w3 = effect_hf_row()
    out["items"]["EFFECT-HF"] = (b3 or {}).get("admitted", {}).get("value") and b3 or {"state": "NOT_STAGED", "why": w3}
    if "--apply-v12-02q" in argv:
        unbind_effect_hf()
    if "--write-findings" in argv:
        with open(os.path.join(ROOT, "registry", "g1_signed_comparator_findings.json"), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(json.dumps(comparator_findings(), indent=1, ensure_ascii=False) + "\n")
    out["items"]["ENGAGE"] = engage_aact()
    out["items"]["CoDEX"] = codex_28d()
    out["k5_bindings"] = [b for b in (b1, b2) if b]
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    for k, v in out["items"].items():
        print(k, v.get("values") or v.get("result") or v.get("why"))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
