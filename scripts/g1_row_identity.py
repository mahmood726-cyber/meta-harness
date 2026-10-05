"""IDENTITY of every accepted forest-reader row, prepared so the row ATTACHES AUTOMATICALLY once its trial is admitted to
our pool (k-gap REVIEW_REFERENCE_LIST route, 5 Oct). Deterministic, offline, no model.

  rows      every secondary row of an ACCEPTED or ACCEPTED_SECOND_SOURCE_ONLY figure in
            registry/model_proposals/g1_forest_reader.json (comparators and other metas)
  evidence  (1) META_REFERENCE -- the row in its OWN meta's JATS reference list: by the citation number its label prints
                ('Can et al35', 'Zhdanova IV, 2001 [31]', 'Gao et al.13'), else by first-author surname (+ year when the
                label prints one), else by the label's acronym in a reference TITLE; a match must be UNIQUE -> PMID / DOI
            (2) NCT_IN_LABEL -- an NCT number printed in the label
            (3) TRACKER -- the topic's comparator trial in the k-gap tracker (read at a PINNED acq/k-gap commit): same
                family PMID / NCT as (1)/(2), else the same acronym, else the same surname + year
            (4) TABLE_NCT -- the NCT(s) k-gap's trial table holds for that PMID
  output    registry/model_proposals/g1_forest_row_identity.json: one record per row (ids, methods, the comparator
            label it attaches to, or why it is unmapped) + coverage per topic. Ambiguity is never resolved by a guess.

    python scripts/g1_row_identity.py --ref <acq/k-gap sha>
"""
from __future__ import annotations

import collections
import io
import json
import os
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_forest_reader as gfr  # noqa: E402

OUT = os.path.join(ROOT, "registry", "model_proposals", "g1_forest_row_identity.json")
STOP = {"et", "al", "trial", "study", "group", "the", "and", "with", "mg", "kg", "dose", "high", "low", "trials",
        "randomized", "randomised", "placebo", "versus", "vs", "phase", "part", "cohort", "sub", "substudy", "of",
        "in", "for", "on", "to", "older", "adults", "patients", "pts", "hfref", "hfpef", "hfmref", "ef"}
SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


def fold(s):
    s = unicodedata.normalize("NFKD", str(s or "")).translate(SUP)
    s = re.sub(r"[‐-―−]", "-", s)                     # every dash is '-': 'EMPA–REG' is one acronym, not two
    return "".join(c for c in s if not unicodedata.combining(c))


def compact(s):
    """A trial name without years, citation numbers and punctuation: 'CONFIRM HF' == 'CONFIRM-HF [2]' == 'CONFIRMHF'."""
    t = re.sub(r"\[\d+\]|\(\d+\)|(?<!\d)(?:19|20)\d\d(?!\d)|\bNCT\d{8}\b", " ", fold(s))
    return re.sub(r"[^A-Z0-9]", "", t.upper())


def words(s):
    return [w for w in re.findall(r"[a-z]+", fold(s).lower()) if len(w) >= 3 and w not in STOP]


def year_of(s):
    ys = re.findall(r"(?<!\d)((?:19|20)\d\d)(?!\d)", fold(s))
    return ys[-1] if ys else None


def refnum_of(s):
    """The citation number a label prints: '[31]', '(24)', a trailing number glued to 'al' ('et al35'), superscripts."""
    t = fold(s)
    m = re.search(r"\[(\d{1,3})\]|\((\d{1,3})\)|al\.?\s*(\d{1,3})\b|[A-Za-z](\d{1,3})\s*$", t)
    return next((g for g in (m.groups() if m else ()) if g), None)


def acronym_of(s):
    """An all-caps token of >=4 characters (letters, digits, dashes), not a year: 'PLATO', 'COV-AID', 'EMPA-REG'.
    Shorter tokens ('HF', 'CAP', 'DM') name nothing on their own."""
    toks = re.findall(r"\b[A-Z][A-Z0-9\-]{3,}\b", fold(s))
    return [t.strip("-") for t in toks if not re.fullmatch(r"(19|20)\d\d", t)]


def _title(cit):
    t = cit.find(".//article-title")
    return " ".join("".join(t.itertext()).split()) if t is not None else ""


def refs_of(pmid):
    """[(label, surname, year, pmid, doi, title)] from the meta's held JATS reference list (or [])."""
    jp = gfr.jats_path(pmid)
    if not jp:
        return []
    out = []
    try:
        root = ET.parse(jp).getroot()
    except ET.ParseError:
        return []
    for r in root.iter("ref"):
        cit = next((c for c in r if c.tag in ("element-citation", "mixed-citation", "citation", "nlm-citation")), None)
        if cit is None:
            continue
        sn = next((n.findtext("surname") for n in cit.iter() if n.tag in ("name", "string-name") and n.findtext("surname")),
                  None)
        if not sn:                     # an unstructured citation: its first author is its first word ('Lee N, Leo YS...')
            m = re.match(r"\s*([A-Z][A-Za-z'\-]{2,})", fold("".join(cit.itertext())))
            sn = m.group(1) if m else None
        pm = next((p.text for p in cit.iter("pub-id") if p.get("pub-id-type") == "pmid" and p.text), None)
        doi = next((p.text for p in cit.iter("pub-id") if p.get("pub-id-type") == "doi" and p.text), None)
        out.append({"label": (r.findtext("label") or "").strip().strip(".[]()"), "surname": sn,
                    "year": (cit.findtext(".//year") or "")[:4], "pmid": (pm or "").strip() or None,
                    "doi": (doi or "").strip() or None, "title": _title(cit),
                    "text": " ".join("".join(cit.itertext()).split())[:400]})
    return out


def match_reference(label, refs):
    """(ref, method) or (None, why)."""
    if not refs:
        return None, "NO_OPEN_REFERENCE_LIST"
    n = refnum_of(label)
    lw, yr = set(words(label)), year_of(label)
    if n:
        hit = [r for r in refs if r["label"] == n]
        # the number is taken only if the cited first author is ALSO in the label (when both are known)
        if len(hit) == 1 and (not lw or not hit[0]["surname"] or set(words(hit[0]["surname"])) & lw):
            return hit[0], f"META_REFERENCE_NUMBER:{n}"
    cand = [r for r in refs if r["surname"] and set(words(r["surname"])) & lw]
    if yr:
        cy = [r for r in cand if r["year"] == yr]
        cand = cy or [r for r in cand if r["year"] and abs(int(r["year"]) - int(yr)) == 1]
    if len(cand) == 1:
        return cand[0], "META_REFERENCE_SURNAME" + ("_YEAR" if yr else "")
    if len(cand) > 1:
        return None, f"AMBIGUOUS_REFERENCE:{len(cand)}"
    ac = acronym_of(label)
    if ac:
        hit = [r for r in refs if any(re.search(r"(?<![A-Za-z0-9-])" + re.escape(a) + r"(?![A-Za-z0-9-])",
                                                fold(r["title"] or r["text"])) for a in ac)]
        if len(hit) == 1:
            return hit[0], "META_REFERENCE_TITLE_ACRONYM"
        if len(hit) > 1:
            return None, f"AMBIGUOUS_ACRONYM_IN_TITLES:{len(hit)}"
    return None, "NO_REFERENCE_MATCH"


def _git_json(ref, path):
    r = subprocess.run(["git", "-C", ROOT, "show", f"{ref}:{path}"], capture_output=True, encoding="utf-8")
    return json.loads(r.stdout) if r.returncode == 0 else None


def tracker_index(slug, ref):
    d = _git_json(ref, f"outputs/k_gap/g1/{slug}.json") or {}
    out = []
    for t in d.get("trials") or []:
        fam = str(t.get("family") or "")
        out.append({"label": t["label"], "family": fam,
                    "pmid": (re.fullmatch(r"PMID (\d+)", fam) or [None, None])[1],
                    "nct": (re.search(r"NCT\d{8}", fam + " " + t["label"]) or [None])[0],
                    "acronyms": set(acronym_of(t["label"])), "words": set(words(t["label"])), "compact": compact(t["label"]),
                    "year": year_of(t["label"]), "in_our_pool": t.get("in_our_pool"), "route": t.get("route")})
    return out


def attach(rowrec, tracker):
    """The comparator trial a row names, by id first, then acronym, then surname + year -- unique or nothing."""
    by = [t for t in tracker if (rowrec.get("pmid") and t["pmid"] == rowrec["pmid"]) or
          (rowrec.get("nct") and t["nct"] == rowrec["nct"])]
    if len(by) == 1:
        return by[0], "TRACKER_ID"
    c = compact(rowrec["row_label"])
    by = [t for t in tracker if len(c) >= 4 and t["compact"] == c]
    if len(by) == 1:
        return by[0], "TRACKER_NAME_EXACT"
    ac = set(acronym_of(rowrec["row_label"]))
    by = [t for t in tracker if ac and t["acronyms"] and (ac & t["acronyms"])]
    if len(by) == 1:
        return by[0], "TRACKER_ACRONYM"
    # by name ONLY with a year on both sides (a shared topic word -- 'covid', 'heart' -- names no trial)
    lw, yr = set(words(rowrec["row_label"])), year_of(rowrec["row_label"])
    by = [t for t in tracker if yr and t["year"] == yr and lw & t["words"]]
    if len(by) == 1:
        return by[0], "TRACKER_SURNAME_YEAR"
    return None, ("TRACKER_AMBIGUOUS" if len(by) > 1 else "NOT_A_COMPARATOR_TRIAL")


def main(argv):
    ref = argv[argv.index("--ref") + 1]
    o = gfr._j(gfr.OUT)
    table = _git_json(ref, "outputs/k_gap/k_gap_table.json") or {"trials": []}
    nct_of_pmid = collections.defaultdict(set)
    for t in table["trials"]:
        for p in t.get("pmids") or []:
            nct_of_pmid[str(p)] |= {str(n).upper() for n in t.get("ncts") or []}
    trackers, refcache, recs = {}, {}, []
    for sec in ("results", "meta_results"):
        for key, v in sorted(o[sec].items()):
            if v.get("state") not in ("ACCEPTED", gfr.SECOND_SOURCE_ONLY):
                continue
            slug = v.get("slug") or key.split("::")[0]
            trackers.setdefault(slug, tracker_index(slug, ref))
            for r in v.get("secondary_rows") or []:
                mp = r["meta_pmid"]
                refcache.setdefault(mp, refs_of(mp))
                rec = {"slug": slug, "figure_key": key, "figure_state": v["state"], "meta_pmid": mp,
                       "is_comparator": mp == gfr.comparator_of(slug), "row_label": r["trial_label"],
                       "pmid": None, "doi": None, "nct": None, "comparator_label": None, "methods": [], "why": []}
                hit, how = match_reference(r["trial_label"], refcache[mp])
                if hit:
                    rec.update(pmid=hit["pmid"], doi=hit["doi"])
                    rec["methods"].append(how)
                    rec["reference"] = hit["text"][:200]
                else:
                    rec["why"].append(how)
                m = re.search(r"NCT\d{8}", fold(r["trial_label"]).upper())
                if m:
                    rec["nct"] = m.group(0)
                    rec["methods"].append("NCT_IN_LABEL")
                t, how = attach(rec, trackers[slug])
                if t:
                    rec.update(comparator_label=t["label"], tracker_family=t["family"], in_our_pool=t["in_our_pool"],
                               route_now=t["route"])
                    rec["pmid"] = rec["pmid"] or t["pmid"]
                    rec["nct"] = rec["nct"] or t["nct"]
                    rec["methods"].append(how)
                else:
                    rec["why"].append(how)
                if rec["pmid"] and not rec["nct"] and len(nct_of_pmid.get(rec["pmid"], ())) == 1:
                    rec["nct"] = next(iter(nct_of_pmid[rec["pmid"]]))
                    rec["methods"].append("TABLE_NCT")
                rec["mapped"] = bool(rec["pmid"] or rec["nct"] or rec["comparator_label"])
                recs.append(rec)
    cov = {}
    for slug in sorted({r["slug"] for r in recs}):
        rs = [r for r in recs if r["slug"] == slug]
        cov[slug] = {"rows": len(rs), "mapped": sum(r["mapped"] for r in rs),
                     "with_pmid": sum(bool(r["pmid"]) for r in rs), "with_nct": sum(bool(r["nct"]) for r in rs),
                     "to_comparator_trial": sum(bool(r["comparator_label"]) for r in rs),
                     "unmapped_why": dict(collections.Counter(w for r in rs if not r["mapped"] for w in r["why"][:1]))}
    tot = {k: sum(c[k] for c in cov.values()) for k in ("rows", "mapped", "with_pmid", "with_nct", "to_comparator_trial")}
    gfr._save(OUT, {"pinned_ref": ref, "coverage_total": tot, "coverage": cov, "rows": recs})
    print(json.dumps(tot))
    for s, c in cov.items():
        print(f"{s:42s} {c['mapped']:4d}/{c['rows']:<4d} pmid {c['with_pmid']:4d} nct {c['with_nct']:4d} "
              f"comparator-trial {c['to_comparator_trial']:4d} {c['unmapped_why']}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
