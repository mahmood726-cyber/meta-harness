"""COMPARATOR ENUMERATION from the comparator's OWN supplementary trial table (G1 binding lane; for a topic the tracker
marks COMPARATOR_NOT_ENUMERATED). Deterministic: regex over the typed supplement text (scripts/k_gap_supplements.py,
Europe PMC supplementaryFiles, no OCR); no model.

  E1  a study row is 'Author YYYY[a-z]<ref>[#] <study no> ... <arm 1> <N> <drug ...> <duration>', followed by its other
      arms on continuation lines '<arm> <N> <drug ...>'. A trial is a comparator trial of the topic when one arm names
      the topic's intervention agent.
  E2  in scope when another arm names the topic's comparator (placebo); a trial whose arms hold the agent only against
      ACTIVE drugs is named out of scope (rule COMPARATOR_NOT_PLACEBO, span: its arm lines).
  E3  identity: the row's reference number -> the supplement's own reference list entry -> PubMed, admitted only when
      CONFIRMED by exact title + first author + year (scripts/ref_title_pmid_lookup.py).
What this cannot decide: which in-scope trials the comparator pooled for THIS outcome (eFigure 5 is an image: no text
layer, no OCR) -- recorded as an open question, never assumed.

    python scripts/g1_binding_enumerate.py SLUG [--lookup]   -> outputs/k_gap/g1_binding/enumeration_<slug>.json
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))

OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding")
_ROW = re.compile(r"^(?P<label>[A-Z][A-Za-z'\-]+(?: [A-Z][A-Za-z'\-]+)? (?P<year>(?:19|20)\d\d)[a-z]?)#?(?P<ref>\d{1,3})#?\s+"
                  r"(?P<no>\d{1,3})\s+(?P<rest>.*?)\s+1\s+(?P<n>[\d,]+)\s+(?P<drug>.+?)\s+(?P<dur>\d{1,3})\s*$")
_ARM = re.compile(r"^\s+(?P<arm>[2-9])\s+(?P<n>[\d,]+)\s+(?P<drug>.+?)\s*$")
_REF = re.compile(r"^(?P<num>\d{1,3})\. (?P<body>.+)$")


def parse_table(text):
    rows, cur = [], None
    for ln in (text or "").split("\n"):
        m = _ROW.match(ln)
        if m:
            cur = {"label": m.group("label"), "year": m.group("year"), "ref": m.group("ref"), "study_no": m.group("no"),
                   "arms": [{"arm": 1, "n": int(m.group("n").replace(",", "")), "drug": m.group("drug").strip()}],
                   "lines": [ln.strip()]}
            rows.append(cur)
            continue
        a = _ARM.match(ln)
        if a and cur is not None and len(cur["arms"]) < 6:
            cur["arms"].append({"arm": int(a.group("arm")), "n": int(a.group("n").replace(",", "")),
                                "drug": a.group("drug").strip()})
            cur["lines"].append(ln.strip())
        elif ln.strip() and not a:
            cur = None if not ln.startswith(" ") else cur
    return rows


def parse_refs(text):
    refs, cur = {}, None
    for ln in (text or "").split("\n"):
        m = _REF.match(ln)
        if m:
            cur = m.group("num")
            refs[cur] = m.group("body").strip()
        elif cur and ln.strip() and not re.match(r"^(?:e?Table|e?Figure|\d+\.)", ln.strip()):
            refs[cur] += " " + ln.strip()
    return refs


def ref_fields(body):
    """(first_author, title, year) of a 'Surname AB, ... et al. Title. Journal. YYYY;...' reference."""
    m = re.match(r"(?P<au>[A-Z][A-Za-z'\- ]+?) [A-Z]{1,3}\b.*?(?:et al\.|\.)\s+(?P<title>[^.]{12,300}\.)\s", body + " ")
    y = re.search(r"\b((?:19|20)\d\d);", body)
    return ((m.group("au").strip() if m else ""), (m.group("title").strip().rstrip(".") if m else ""),
            (y.group(1) if y else ""))


def enumerate_topic(slug, lookup=False):
    cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    agents = [a.lower() for a in (cfg.get("intervention_agents") or cfg.get("intervention_terms") or []) if len(a) >= 4]
    comps = [c.lower() for c in (cfg.get("comparator_terms") or ["placebo"])] or ["placebo"]
    comp_pmid = str(cfg.get("comparator_pmid"))
    sup = sorted(glob.glob(os.path.join(ROOT, "cache", "comparators", comp_pmid, "*_kgap_supplements.txt")))
    if not sup:
        return {"slug": slug, "state": "NO_SUPPLEMENT_TEXT_HELD"}
    text = open(sup[-1], encoding="utf-8", errors="replace").read()
    rows, refs = parse_table(text), parse_refs(text)
    out = []
    for r in rows:
        drugs = [a["drug"].lower() for a in r["arms"]]
        if not any(any(ag in d for ag in agents) for d in drugs):
            continue
        has_comp = any(any(c in d for c in comps) for d in drugs)
        au, title, yr = ref_fields(refs.get(r["ref"], ""))
        rec = {"label": r["label"], "study_no": r["study_no"], "ref": r["ref"], "arms": r["arms"],
               "scope": "IN_SCOPE" if has_comp else "OUT_OF_SCOPE:COMPARATOR_NOT_PLACEBO",
               "span": " / ".join(r["lines"]), "reference": refs.get(r["ref"]),
               "ref_first_author": au, "ref_title": title, "ref_year": yr, "pmid": None, "identity": "NOT_LOOKED_UP"}
        if lookup and title:
            import ref_title_pmid_lookup as rl
            hit = rl.lookup({"key": f"{comp_pmid}:SUPPL:{r['ref']}", "title": title, "first_author": au, "year": yr})
            rec["identity"] = hit.get("state")
            rec["pmid"] = hit.get("pmid") if hit.get("state") == "CONFIRMED" else None
        out.append(rec)
    return {"slug": slug, "comparator_pmid": comp_pmid, "source": os.path.relpath(sup[-1], ROOT).replace("\\", "/"),
            "n_table_rows": len(rows), "trials": out,
            "in_scope": sum(1 for t in out if t["scope"] == "IN_SCOPE"),
            "open_question": "which in-scope trials the comparator pooled for the topic OUTCOME: its per-comparison "
                             "figure is an image (no text layer); not assumed"}


ENUM_DIR = os.path.join(ROOT, "registry", "comparator_enumerations")


def write_input(res):
    """The k_gap_table INPUT (scripts/k_gap_table.py enumeration_units): one typed unit per comparator trial -- label,
    the comparator's reference number, the row's arm lines verbatim (span) and the CONFIRMED PMID -- with the held
    source's path and sha256. Only identity-CONFIRMED trials are written; any other refuses the whole file."""
    import hashlib
    bad = [t["label"] for t in res["trials"] if t["identity"] != "CONFIRMED" or not t["pmid"]]
    if bad:
        raise SystemExit(f"{res['slug']}: identity not CONFIRMED for {bad}; input not written")
    src = os.path.join(ROOT, res["source"])
    out = {"slug": res["slug"], "comparator_pmid": res["comparator_pmid"], "status": "ENUMERATED",
           "enumerated_from": f"the comparator's own supplementary trial table (PMID {res['comparator_pmid']}, Europe PMC "
                              f"supplementaryFiles, typed text {res['source']}); rules E1-E3 scripts/g1_binding_enumerate.py",
           "source": {"path": res["source"], "sha256": hashlib.sha256(open(src, "rb").read()).hexdigest()},
           "open_question": res["open_question"],
           "units": [{"label": t["label"], "ref": t["ref"], "pmid": t["pmid"], "identity": t["identity"],
                      "span": t["span"], "arms": t["arms"],
                      "scope": "IN_SCOPE" if t["scope"] == "IN_SCOPE" else "OUT_OF_SCOPE",
                      "rule_id": None if t["scope"] == "IN_SCOPE" else "E2:COMPARATOR_NOT_PLACEBO",
                      "reference": t["reference"]} for t in res["trials"]]}
    os.makedirs(ENUM_DIR, exist_ok=True)
    p = os.path.join(ENUM_DIR, res["slug"] + ".json")
    with open(p + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    os.replace(p + ".tmp", p)
    return p


def main(argv):
    lookup = "--lookup" in argv
    for slug in [a for a in argv if not a.startswith("--")]:
        res = enumerate_topic(slug, lookup)
        if "--write-input" in argv:
            print("wrote", write_input(res))
        os.makedirs(OUT, exist_ok=True)
        p = os.path.join(OUT, f"enumeration_{slug}.json")
        with open(p + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, ensure_ascii=False)
        os.replace(p + ".tmp", p)
        for t in res.get("trials", []):
            print(f"{t['label']:22s} ref {t['ref']:>3s} {t['scope']:36s} {t['identity']:28s} {t['pmid'] or ''}  "
                  f"{' | '.join(a['drug'][:28] for a in t['arms'])}")
        print(slug, res.get("state") or f"{len(res['trials'])} agent trials, {res['in_scope']} in scope")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
