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
        rows = topic(slug)
        p = os.path.join(OUT, f"findings_{slug}.json")
        with open(p + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"slug": slug, "findings": rows}, fh, indent=1, ensure_ascii=False)
        os.replace(p + ".tmp", p)
        print(slug, [(r["label"], r["state"]) for r in rows])


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
