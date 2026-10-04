"""TYPED FINDINGS about comparator rows, checked against the trial's OWN primary (G1 binding lane, Mahmood 4 Oct).

Rule F1 COMPARATOR_COUNTS_EQUAL_SUM_OF_COMPONENTS
  The comparator's per-arm events (events_t / events_c) equal, in BOTH arms, the SUM of two to four outcomes the trial
  POSTED separately on CT.gov (AACT, versioned snapshot) -- e.g. cardiovascular death + MI + stroke -- while the trial
  posts its own first-event composite with different counts. Summing components counts a patient with two events twice
  and is not the trial's composite. Arms are matched by N (posted group totals), never by order. Span: the AACT outcome
  ids, titles and counts, with the snapshot digest. Recorded only when the decomposition is UNIQUE (one subset of
  outcomes reproduces both arms); two or more subsets -> F1_AMBIGUOUS, recorded, never asserted.

    python scripts/g1_binding_findings.py SLUG [SLUG ...]   -> outputs/k_gap/g1_binding/findings_<slug>.json
"""
from __future__ import annotations

import io
import itertools
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from kgap import aact_adapter  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding")


def _int(v):
    try:
        f = float(str(v).replace(",", ""))
        return int(f) if f == int(f) else None
    except (TypeError, ValueError):
        return None


def arm_counts(reg, oid, n_t, n_c):
    """(count_t, count_c) of one posted outcome, its two groups matched to the arms by their posted N; None when the
    Ns do not identify the arms (equal, or not both present)."""
    g = [(x.get("count"), x.get("n")) for x in (reg.get("groups") or {}).get(oid) or []
         if x.get("count") is not None and x.get("n") is not None]
    if n_t == n_c:
        return None
    t = [c for c, n in g if n == n_t]
    c = [c for c, n in g if n == n_c]
    return (t[0], c[0]) if len(t) == 1 and len(c) == 1 else None


_STOP = {"from", "causes", "cause", "leading", "with", "without", "requiring", "other", "any", "acute", "fatal", "nonfatal",
         "non-fatal", "first", "event", "events"}


def _words(s):
    return {w for w in re.findall(r"[a-z]{4,}", (s or "").lower()) if w not in _STOP}


def component_filter(components):
    """A posted outcome may be a COMPONENT only when its title holds every content word of one of the trial's own
    declared components (topics/<slug>.json primary_outcome.trial_annotations[pmid].components) -- never a composite
    ('first event' / 'composite' titles), never an outcome outside the composite (total mortality, AF, VTE)."""
    sets = [w for w in (_words(c) for c in components or []) if w]

    def ok(title):
        if re.search(r"\bfirst\b|\bcomposite\b", title or "", re.I):
            return False
        t = _words(title)
        return any(w <= t for w in sets)
    return ok


def component_sum(reg, cr, max_k=4, allowed=None):
    """F1 for one comparator row against one registry: (state, detail). `allowed(title)` restricts which posted
    outcomes may be summed as components (component_filter); None = any non-composite outcome."""
    e_t, n_t, e_c, n_c = (_int(cr.get(k)) for k in ("events_t", "n_t", "events_c", "n_c"))
    if None in (e_t, n_t, e_c, n_c):
        return "NOT_APPLICABLE", "comparator row has no typed counts"
    outs = reg.get("outcomes") or {}
    per = {oid: arm_counts(reg, oid, n_t, n_c) for oid in outs}
    per = {oid: v for oid, v in per.items() if v}
    comp_ids = sorted(o for o in per if (allowed or (lambda t: not re.search(r"\bfirst\b|\bcomposite\b", t or "",
                                                                             re.I)))(outs[o].get("title")))
    if not per:
        return "NOT_APPLICABLE", "no posted outcome with both arms identified by N"
    single = [oid for oid, v in per.items() if v == (e_t, e_c)]
    if single:
        return "COMPARATOR_COUNTS_EQUAL_ONE_POSTED_OUTCOME", [{"outcome_id": o, "title": outs[o].get("title"),
                                                              "counts": per[o]} for o in single]
    hits = []
    ids = sorted(per)
    for k in range(2, max_k + 1):
        for combo in itertools.combinations(comp_ids, k):
            if sum(per[o][0] for o in combo) == e_t and sum(per[o][1] for o in combo) == e_c:
                hits.append(combo)
    if not hits:
        return "NO_DECOMPOSITION", None
    if len(hits) > 1:
        return "F1_AMBIGUOUS", [list(h) for h in hits[:5]]
    combo = hits[0]
    # the trial's own first-event composite of (at least) those components, when posted: the number it should have been
    comps = [{"outcome_id": o, "title": outs[o].get("title"), "type": outs[o].get("type"), "counts_t_c": per[o]}
             for o in combo]
    # a posted composite OF THESE components: a first-event / composite title naming at least two of the summed ones
    cw = [_words(outs[o].get("title")) for o in combo]
    own = [{"outcome_id": o, "title": outs[o].get("title"), "type": outs[o].get("type"), "counts_t_c": per[o]}
           for o in ids if o not in combo and re.search(r"\bfirst\b|\bcomposite\b", outs[o].get("title") or "", re.I)
           and sum(1 for w in cw if w and w <= _words(outs[o].get("title"))) >= 2]
    return "COMPARATOR_COUNTS_EQUAL_SUM_OF_COMPONENTS", {"components": comps, "trial_composites_posted": own}


# ---------------------------------------------------------------------------------------------------------------------
# Rule F2 ORIENTATION_STATED_BY_COMPARATOR -- the comparator's OWN words fix its MD direction: 'mean improvement in X' /
#   'efficacy in reducing X (weighted mean difference = <positive>)' state that a POSITIVE difference is a REDUCTION with
#   the intervention (control minus intervention). Ours is intervention minus control (harness/secondary_meta.py,
#   md = mean_t - mean_c). Mirrored conventions are NOT a sign error on either side: the finding says which convention
#   each uses, with the comparator's sentence as span; a value only flips sign when compared.
# Rule F3 SAME_TRIAL_DIFFERENT_REPORT -- the comparator's row cites a report (its own reference list, joined by first
#   author + year to the row label) that differs from our pooled report, while both reports' PubMed DataBank lists name
#   the SAME registration: a population / analysis-set difference between two reports of one trial, not a value error.
_IMPROVE = re.compile(r"mean improvement in ([a-z ]{3,60}?)(?:[,.;]| and )", re.I)
_REDUCE = re.compile(r"(?:efficacy|effect)[^.]{0,40}? in reducing ([a-z ]{3,60}?) \((?:weighted )?mean difference[^=]{0,30}=\s*"
                     r"(\d+(?:\.\d+)?)", re.I)


def orientation_stated(comparator_text):
    """(convention, spans) from the comparator's own sentences, or (None, [])."""
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", comparator_text or ""))
    spans = [t[max(0, m.start() - 40): m.end() + 40] for m in _REDUCE.finditer(t)]
    spans += [t[max(0, m.start() - 20): m.end() + 20] for m in _IMPROVE.finditer(t)]
    return ("POSITIVE_IS_REDUCTION_WITH_INTERVENTION", spans) if spans else (None, [])


def cited_report(comparator_text, row_label):
    """PMID of the comparator's reference whose first author and year are the row label's ('Wade AG, 2011 [21]')."""
    m = re.match(r"\s*([A-Z][A-Za-z'\-]+)\b.*?\b((?:19|20)\d\d)\b", row_label or "")
    if not m:
        return None
    sur, yr = m.groups()
    hits = []
    for r in re.finditer(r"<ref\b[^>]*>(.*?)</ref>", comparator_text or "", re.S):
        body = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", r.group(1))).strip()
        if re.match(rf"(?:\d+\s+)?{re.escape(sur)}\b", body) and re.search(rf"\(\s*{yr}\s*\)|\b{yr}\b", body):
            pm = re.search(r"\b(\d{7,8})\b", body)
            hits.append(pm.group(1) if pm else None)
    return hits[0] if len(hits) == 1 else None


def same_trial_different_report(cited_pmid, our_pmid, databank):
    if not cited_pmid or not our_pmid or cited_pmid == our_pmid:
        return None
    a = set((databank.get(cited_pmid) or {}).get("databank") or []) | set((databank.get(cited_pmid) or {}).get("abstract") or [])
    b = set((databank.get(our_pmid) or {}).get("databank") or []) | set((databank.get(our_pmid) or {}).get("abstract") or [])
    common = sorted(a & b)
    return {"cited_pmid": cited_pmid, "our_pmid": our_pmid, "registration": common} if len(common) == 1 else None


def orientation_findings(slug):
    """F2 / F3 for every comparator row of an MD topic that disagrees in sign with ours, or is UNKNOWN orientation."""
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", slug + ".json"), encoding="utf-8"))
    comp = str(o.get("comparator_pmid"))
    d = os.path.join(ROOT, "cache", "comparators", comp)
    jats = next((os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith("_kgap_jats.xml")), None) if os.path.isdir(d) else None
    if not jats:
        return []
    ct = open(jats, encoding="utf-8", errors="replace").read()
    conv, spans = orientation_stated(ct)
    dbp = os.path.join(ROOT, "outputs", "k_gap", "pubmed_databank_ncts.json")
    databank = json.load(open(dbp, encoding="utf-8")) if os.path.exists(dbp) else {}
    rows = []
    for x in o["trials"]:
        cr = x.get("comparator_row") or {}
        if (cr.get("measure") or "").upper() != "MD" or not str(x.get("family") or "").startswith("PMID "):
            continue
        prov = x.get("comparator_row_provenance") or {}
        cited = cited_report(ct, prov.get("row_label") or x["label"])
        st = same_trial_different_report(cited, str(x["family"])[5:], databank)
        rows.append({"rule": "F2" + ("+F3" if st else ""), "slug": slug, "label": x["label"],
                     "comparator_convention": conv, "comparator_spans": spans[:3],
                     "our_convention": "INTERVENTION_MINUS_CONTROL (harness/secondary_meta.py: md = mean_t - mean_c)",
                     "comparator_row": {k: cr.get(k) for k in ("measure", "effect", "lower", "upper")},
                     "comparator_row_label": prov.get("row_label"), "comparator_cited_report": cited,
                     "same_trial_different_report": st,
                     "verdict": ("CONVENTIONS_MIRRORED_NOT_A_SIGN_ERROR" if conv else "COMPARATOR_CONVENTION_NOT_STATED")
                                + ("; DIFFERENT_REPORT_OF_THE_SAME_TRIAL" if st else ""),
                     "span_source": f"comparator JATS {os.path.basename(jats)}; PubMed DataBank (outputs/k_gap/pubmed_databank_ncts.json)"})
    return rows


def topic(slug):
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", slug + ".json"), encoding="utf-8"))
    T = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "k_gap_table.json"), encoding="utf-8"))
    tab = {(t["slug"], t["label"]): t for t in T["trials"]}
    cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    ann = (cfg.get("primary_outcome") or {}).get("trial_annotations") or {}
    rows = []
    for x in o["trials"]:
        cr = x.get("comparator_row") or {}
        ncts = sorted(set((tab.get((slug, x["label"])) or {}).get("ncts") or []) |
                      set(re.findall(r"NCT\d{8}", str(x.get("family") or ""))))
        pm = set(re.findall(r"\b\d{6,9}\b", str(x.get("family") or ""))) | set((tab.get((slug, x["label"])) or {}).get("pmids") or [])
        comps = [c for p_ in sorted(pm) for c in (ann.get(p_) or {}).get("components") or []]
        for nct in ncts:
            aact_adapter.ensure([nct])
            reg = aact_adapter.registry_for(nct)
            if not reg:
                continue
            state, detail = component_sum(reg, cr, allowed=component_filter(comps) if comps else None)
            if state in ("NOT_APPLICABLE", "NO_DECOMPOSITION"):
                continue
            rows.append({"rule": "F1", "slug": slug, "label": x["label"], "nct": nct, "state": state,
                         "comparator_row": {k: cr.get(k) for k in ("measure", "effect", "lower", "upper", "events_t",
                                                                    "n_t", "events_c", "n_c")},
                         "our_value": x.get("our_value"), "detail": detail,
                         "span_source": f"AACT snapshot {reg['_snapshot']['id']} (digest {reg['_snapshot']['digest'][:16]})"})
    return rows


def main(argv):
    os.makedirs(OUT, exist_ok=True)
    for slug in argv:
        rows = topic(slug) + orientation_findings(slug)
        p = os.path.join(OUT, f"findings_{slug}.json")
        with open(p + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"slug": slug, "findings": rows}, fh, indent=1, ensure_ascii=False)
        os.replace(p + ".tmp", p)
        print(slug, [(r["label"], r.get("state") or r.get("verdict")) for r in rows])


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
