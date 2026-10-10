"""REVIEW 15 SWEEP: report-to-trial linking with INHERITED eligibility. Read-only over the served review.json + the cached
records of every topic.

A record the screen EXCLUDED on population (X2) is a candidate flip when it is a REPORT of a trial family whose
structural screen says ELIGIBLE (UNKNOWN / INELIGIBLE families are listed, never flipped), by a TYPED link only:
  DATABANK   its PubMed DataBank / registry field names an NCT that is one of the family's registry ids
  ABSTRACT   its title/abstract states an NCT that is one of the family's registry ids
  ACRONYM    its TITLE names the family's registry acronym as an exact upper-case token (>= 4 letters), and the family's
             acronym is unique among the topic's families ('in SELECT', 'the PARALLEL-HF trial'); a common word in
             lower or title case never links ('Select patients ...')
A linked report inherits the family's eligibility instead of being screened on its own title phrase (SELECT 38907684,
"... Overweight or Obesity but Without Diabetes in SELECT", excluded X2). An unlinked record is untouched.

    python scripts/g1_report_link_sweep.py -> outputs/k_gap/report_link_sweep.json + .md
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NCT = re.compile(r"NCT\d{8}")


def fam_index(fams):
    idx, acr = {}, {}
    for f in fams:
        if f.get("is_trial_family") is False:
            continue
        a = f.get("aliases") or {}
        for rid in (a.get("registry_ids") or []) + ((f.get("identity_basis") or {}).get("registry_ids") or []):
            if str(rid).startswith("NCT"):
                idx[str(rid)] = f
        for ac in a.get("acronym") or []:
            core = re.sub(r"[^A-Za-z0-9-]", "", str(ac))
            if len(re.sub(r"[^A-Za-z]", "", core)) >= 4:
                acr.setdefault(core.upper(), []).append(f)
    return idx, {k: v[0] for k, v in acr.items() if len(v) == 1}


def topic(slug):
    rp = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
    cp = os.path.join(ROOT, "cache", slug, "records.json")
    if not (os.path.exists(rp) and os.path.exists(cp)):
        return None
    r = json.load(open(rp, encoding="utf-8"))
    recs = {str(x.get("id")): x for x in (json.load(open(cp, encoding="utf-8")).get("records") or [])}
    idx, acr = fam_index(r.get("trial_families") or [])
    included = {str(x["id"]) for x in (r.get("screening") or {}).get("records") or [] if x.get("decision") == "include"}
    out = []
    for d in (r.get("screening") or {}).get("records") or []:
        if d.get("decision") != "exclude" or d.get("rule_id") != "X2":
            continue
        rec = recs.get(str(d["id"])) or {}
        title, abstract = rec.get("title") or "", rec.get("abstract") or ""
        links = []
        for n in [rec.get("nct")] if rec.get("nct") else []:
            if n in idx:
                links.append(("DATABANK", n, idx[n]))
        for n in sorted(set(NCT.findall(title + " " + abstract))):
            if n in idx and not any(l[1] == n for l in links):
                links.append(("ABSTRACT", n, idx[n]))
        for core, f in acr.items():
            if re.search(rf"(?<![A-Za-z0-9-]){re.escape(core)}(?![A-Za-z0-9-])", title):   # exact UPPER-case token
                links.append(("ACRONYM", core, f))
        if not links:
            continue
        fams = {l[2]["family_id"]: l[2] for l in links}
        if len(fams) != 1:
            out.append({"id": d["id"], "title": title[:200], "state": "AMBIGUOUS_LINK",
                        "links": [(k, v, f["family_id"]) for k, v, f in links]})
            continue
        f = next(iter(fams.values()))
        st = (f.get("eligibility") or {}).get("state")
        fam_ids = {str(p.get("report_id")) for p in f.get("reports") or []} | set(map(str, (f.get("aliases") or {})
                                                                                      .get("registry_ids") or []))
        has_inc = bool(fam_ids & included)
        # two readings of 'eligible family' (the K-5 open rule): STRICT = structural screen ELIGIBLE; RECONCILED = the
        # family has an INCLUDED record and is not INELIGIBLE (SELECT in sema-MACE: structural UNKNOWN, primary included)
        state = ("FLIP_STRICT" if st == "ELIGIBLE" else
                 "FLIP_RECONCILED_ONLY" if has_inc and st != "INELIGIBLE" else f"LINKED_FAMILY_{st}")
        out.append({"id": d["id"], "title": title[:200], "family_id": f["family_id"], "family_state": st,
                    "family_has_included_record": has_inc, "links": [(k, v) for k, v, _f in links], "state": state})
    return out


def main():
    ab = {t["slug"] for t in json.load(open(os.path.join(ROOT, "registry", "g1_abandoned.json"), encoding="utf-8"))
          .get("topics", [])}
    res, md = {}, ["# Review 15 sweep: X2 report exclusions with a TYPED link to a trial family (nothing applied)", "",
                   "| topic | active | X2 linked | flips STRICT (family ELIGIBLE) | + flips RECONCILED only | ambiguous | records (S=strict, R=reconciled) |",
                   "|---|---|---|---|---|---|---|"]
    for slug in sorted(os.listdir(os.path.join(ROOT, "docs", "reviews"))):
        t = topic(slug)
        if t is None:
            continue
        res[slug] = t
        fs = [x for x in t if x["state"] == "FLIP_STRICT"]
        fr = [x for x in t if x["state"] == "FLIP_RECONCILED_ONLY"]
        md.append(f"| {slug} | {'no' if slug in ab else 'yes'} | {len(t)} | {len(fs)} | {len(fr)} | "
                  f"{sum(1 for x in t if x['state'] == 'AMBIGUOUS_LINK')} | "
                  + "; ".join(f"{'S' if x in fs else 'R'} {x['id']}->{x['family_id']} ({'/'.join(k for k, _v in x['links'])})"
                              for x in fs + fr) + " |")
    json.dump(res, open(os.path.join(ROOT, "outputs", "k_gap", "report_link_sweep.json"), "w", encoding="utf-8",
                        newline="\n"), indent=1, ensure_ascii=False)
    open(os.path.join(ROOT, "outputs", "k_gap", "report_link_sweep.md"), "w", encoding="utf-8", newline="\n").write(
        "\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
