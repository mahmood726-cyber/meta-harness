"""Worklist for the evidence lane: one entry per target row, with the SERVED value read from the served
review.json (origin/main bytes in this tree) and the held documents that exist for the trial.

Population (N named, two sets, may overlap):
  P53 = evidence/inputs/the53.json   -- pooled primary rows inadmissible on P5 at 38c04411
  U23 = evidence/inputs/src.json rows -- served rows lane UA found with no locatable source
Nothing here decides anything; it only enumerates and reads.
"""
import json, os, re, glob, hashlib, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def served_rows(slug, trial, outcome_name=None):
    rev = J(f"docs/reviews/{slug}/review.json")
    hits = []
    for oi, o in enumerate(rev["outcomes"]):
        if outcome_name is None and not o.get("primary"):
            continue
        if outcome_name is not None and o["name"] != outcome_name:
            continue
        for ti, t in enumerate(o.get("trials") or []):
            if t.get("id") == trial:
                hits.append((oi, ti, o, t))
    return rev, hits


def held_docs(slug, pid):
    out = []
    d = os.path.join(ROOT, "cache", slug)
    for p in sorted(glob.glob(os.path.join(d, f"*{pid}*"))) if pid else []:
        if os.path.isfile(p):
            out.append({"path": os.path.relpath(p, ROOT).replace("\\", "/"), "sha256": sha(p), "bytes": os.path.getsize(p)})
    rec = os.path.join(d, "records.json")
    if pid and os.path.isfile(rec):
        data = json.load(open(rec, encoding="utf-8"))
        for k, v in data.items():
            if isinstance(v, list):
                for i, r in enumerate(v):
                    if isinstance(r, dict) and str(r.get("id")) == pid:
                        out.append({"path": f"cache/{slug}/records.json#/{k}/{i}", "sha256": sha(rec),
                                    "abstract_chars": len(r.get("abstract") or ""), "nct": r.get("nct"),
                                    "doi": r.get("doi"), "title": r.get("title")})
    return out


KEEP = ("id", "label", "effect", "ci_low", "ci_high", "scale", "provenance", "source", "endpoint_binding",
        "endpoint_result_span", "registry_title", "registry_timeframe", "analysis_set", "nct", "events_t", "n_t",
        "events_c", "n_c", "mean_t", "sd_t", "mean_c", "sd_c", "document_ref", "source_span", "se", "log_effect")


def entry(kind, key, slug, trial, outcome=None, extra=None):
    pid = trial.replace("PMID ", "").strip() if trial.startswith("PMID") else None
    rev, hits = served_rows(slug, trial, outcome)
    e = {"kind": kind, "key": key, "slug": slug, "trial": trial, "pid": pid,
         "served": [{"json_ref": f"docs/reviews/{slug}/review.json#/outcomes/{oi}/trials/{ti}",
                     "outcome": o["name"], "primary": o.get("primary"),
                     "row": {k: t[k] for k in KEEP if k in t}} for oi, ti, o, t in hits],
         "held": held_docs(slug, pid or trial)}
    e.update(extra or {})
    return e


def main():
    work = []
    for i, r in enumerate(J("evidence/inputs/the53.json"), 1):
        work.append(entry("P53", f"P53-{i:02d}", r["slug"], r["trial"],
                          extra={"family_id": r["family_id"], "absence_code": r["absence_code"],
                                 "eligibility_state": r["eligibility_state"]}))
    for r in J("evidence/inputs/src.json")["rows"]:
        work.append(entry("U23", r["ua_id"], r["page"], r["trial_id"], r["outcome"],
                          extra={"primary_cause": r["primary_cause"], "cause_subtype": r.get("cause_subtype")}))
    s16 = os.path.join(ROOT, "evidence/inputs/s16.json")
    if os.path.exists(s16):
        for i, r in enumerate(J("evidence/inputs/s16.json")["rows"], 1):
            work.append(entry("S16", f"S16-{i:02d}", r["slug"], r["trial"], r["outcome"]))
    mr = os.path.join(ROOT, "evidence/inputs/m_rows.json")
    if os.path.exists(mr):
        for i, r in enumerate(J("evidence/inputs/m_rows.json")["rows"], 1):
            work.append(entry("M", f"M-{i:02d}", r["slug"], r["trial"], r["outcome"]))
    unserved = [w["key"] for w in work if len(w["served"]) != 1]
    json.dump({"population": {"P53": {"N": 53}, "U23": {"N": 23}, "S16": {"N": 16}, "M": {"N": 15}}, "served_row_not_exactly_one": unserved,
               "rows": work}, open(os.path.join(ROOT, "evidence/worklist.json"), "w", encoding="utf-8"), indent=1)
    print(f"rows {len(work)}; served-row count != 1 for {len(unserved)}: {unserved}")
    nf = [w["key"] for w in work if not any("ft_" in h["path"] or h["path"].endswith(".xml") for h in w["held"])]
    print(f"no held full text: {len(nf)} of {len(work)}")


if __name__ == "__main__":
    main()
