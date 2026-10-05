"""OWN-TUPLE EFFECT_CI from the trial's OWN posted CT.gov results (AACT snapshot), for a lane target with no row (G1
binding lane). Deterministic; no model. The posted outcome is chosen by the TOPIC, never by the comparator's numbers:

  A1 OUTCOME   the outcome title names the topic outcome by a non-generic keyword (not 'primary outcome' / 'hazard ratio')
  A2 ESTIMAND  harness.extract.composite_component_mismatch(topic outcome, title + description) == '' -- the same gate the
               tracker's registry binding uses: a 3-point topic never takes a posted 4-point composite ('MACE Plus');
               A2b (stricter, this binder only): an extra component named anywhere in the title or description refuses
  A3 ANALYSIS  a posted analysis of that outcome whose parameter is the topic estimand, with a numeric value AND both CI
               bounds (a one-sided upper bound alone is refused: EFFECT_CI needs both)
  A4 POPULATION intention-to-treat: an outcome whose title/population says per-protocol / on-treatment is refused
  A5 UNIQUE    exactly one (outcome, analysis) survives; two or more -> AMBIGUOUS, refused and named
The span is the AACT fields verbatim (title | description | parameter value [lower, upper]) with the snapshot id; the
tracker's apply_confirm_bindings re-checks that effect and both bounds are verbatim in it.

    python scripts/g1_binding_aact.py   -> outputs/k_gap/g1_binding/bindings_aact.json
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import extract  # noqa: E402
from kgap import aact_adapter  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding")
GENERIC = {"primary outcome", "primary endpoint", "primary end point", "primary composite outcome", "hazard ratio",
           "secondary outcome", "secondary endpoint"}
EST = {"HR": r"hazard ratio", "RR": r"risk ratio|relative risk", "OR": r"odds ratio"}
EXTRA = re.compile(r"unstable angina|revasculari[sz]ation|hospitali[sz]ation for heart failure|heart failure hospitali[sz]ation", re.I)
NOT_ITT = re.compile(r"per[- ]protocol|on[- ]treatment|as[- ]treated", re.I)


def outcome_descriptions(ncts):
    """{outcome_id: description} for the NCTs, one pass over the snapshot's outcomes.txt."""
    want, out = set(ncts), {}
    with open(os.path.join(aact_adapter.snapshot_dir(), "outcomes.txt"), encoding="utf-8", errors="replace", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="|", quoting=csv.QUOTE_NONE):
            if r.get("nct_id") in want:
                out[r["id"]] = r.get("description") or ""
    return out


def candidates(reg, desc, topic_name, keywords, estimand):
    kws = [k.lower() for k in keywords if k and k.lower() not in GENERIC and len(k) >= 4]
    est = re.compile(EST.get(estimand.upper(), re.escape(estimand)), re.I)
    out, refused = [], []
    for oid, o in (reg.get("outcomes") or {}).items():
        title = o.get("title") or ""
        if not any(k in title.lower() for k in kws):
            continue
        why = extract.composite_component_mismatch(topic_name, f"{title} {desc.get(oid, '')}")
        if not why and re.search(r"(\d+)[\s-]?point|three-point", topic_name or "", re.I) and                 EXTRA.search(f"{title} {desc.get(oid, '')}"):
            # A2b (this binder only, stricter than the shared gate, which reads only 'composite'/'primary' clauses): an
            # extra composite component named ANYWHERE in the posted title or description refuses
            why = "A2b: posted outcome names an extra component: " + EXTRA.search(f"{title} {desc.get(oid, '')}").group(0)
        if why:
            refused.append({"outcome_id": oid, "title": title, "gate": "A2_ESTIMAND", "why": why[:160]})
            continue
        if NOT_ITT.search(title) or NOT_ITT.search(o.get("population") or ""):
            refused.append({"outcome_id": oid, "title": title, "gate": "A4_POPULATION", "why": "per-protocol / on-treatment"})
            continue
        for a in reg.get("analyses") or []:
            if a["outcome_id"] != oid or not est.search(a.get("param_type") or ""):
                continue
            if not (a.get("param_value") and a.get("ci_lower") and a.get("ci_upper")):
                refused.append({"outcome_id": oid, "title": title, "gate": "A3_ANALYSIS", "why": f"no two-sided CI ({a.get('param_value')}, lower={a.get('ci_lower')!r}, upper={a.get('ci_upper')!r})"})
                continue
            out.append({"outcome_id": oid, "title": title, "description": desc.get(oid, ""), "type": o.get("type"),
                        "analysis_id": a.get("analysis_id"), "param_type": a["param_type"], "effect": a["param_value"],
                        "lower": a["ci_lower"], "upper": a["ci_upper"]})
    return out, refused


def main():
    targets = json.load(open(os.path.join(OUT, "targets.json"), encoding="utf-8"))
    tgt = [t for t in targets if t.get("ncts") and t.get("route") in ("NO_ROW", "UNVERIFIED")]
    aact_adapter.ensure(sorted({n for t in tgt for n in t["ncts"]}))
    desc = outcome_descriptions(sorted({n for t in tgt for n in t["ncts"]}))
    snap = aact_adapter.snapshot()
    bindings, refused = [], []
    for t in tgt:
        cfg = json.load(open(os.path.join(ROOT, "topics", t["slug"] + ".json"), encoding="utf-8"))
        po = cfg.get("primary_outcome") or {}
        est = (po.get("estimand") or "").upper()
        if est not in EST:
            continue
        for n in t["ncts"]:
            reg = aact_adapter.registry_for(n)
            if not reg:
                continue
            ok, ref = candidates(reg, desc, po.get("name") or "", po.get("keywords") or [], est)
            if len(ok) != 1:
                refused.append({"slug": t["slug"], "label": t["label"], "nct": n,
                                "why": ("A5_AMBIGUOUS" if ok else "NO_ADMISSIBLE_POSTED_OUTCOME"),
                                "candidates": [(c["outcome_id"], c["title"][:80], c["effect"]) for c in ok], "refused": ref})
                continue
            c = ok[0]
            span = f"{c['title']} | {c['description']} | {c['param_type']} {c['effect']} [{c['lower']}, {c['upper']}]"
            bindings.append({"slug": t["slug"], "label": t["label"], "pmid": (t.get("pmids") or [None])[0], "own_tuple": True,
                             "tuple_kind": "EFFECT_CI", "source_kind": "AACT",
                             "source": f"AACT {snap.get('id')} {n} outcome {c['outcome_id']} analysis {c['analysis_id']}",
                             "values": {"measure": est, "effect": c["effect"], "lower": c["lower"], "upper": c["upper"]},
                             "span": span, "rules": "A1-A5 scripts/g1_binding_aact.py", "refused_alternatives": ref})
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "bindings_aact.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"bindings": bindings, "not_bound": refused}, fh, indent=1, ensure_ascii=False)
    for b in bindings:
        print("BOUND", b["slug"][:14], b["label"], b["values"], "|", b["span"][:150])
    for r in refused:
        print("NOT  ", r["slug"][:14], r["label"], r["nct"], r["why"], r["candidates"][:2], [(x["gate"], x["why"][:60]) for x in r["refused"]][:3])


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
