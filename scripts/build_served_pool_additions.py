"""GENERATE registry/served_pool_additions.json from the SIGNED served-pool refresh notices (never hand-edited).

A signed notice (reason starts 'SERVED-POOL REFRESH', state SEEN_AND_SIGNED / BATCH_SEEN_AND_SIGNED) becomes a register
entry only when ALL hold, else it is listed as excluded with its reason:
  * no trial it enters is held (registry/served_pool_holds.json) -- a held trial excludes the notice WHOLE;
  * every entered id resolves to exactly one tracker-verified row outside the served pool (route PRIMARY / TWO_SOURCE /
    SWEEP_AACT_PRIMARY), with a verbatim span carrying its numbers;
  * the served pool WITHOUT the entered ids reproduces the notice's 'before', and the served pipeline's own result
    function (harness.pipeline._pool_result) over that pool PLUS the entered rows reproduces its signed 'after'
    (both within result_changes._same, 1e-6).
Idempotent: once the rows are served, the served pool minus the entered ids is still the 'before'.

    python scripts/build_served_pool_additions.py [--write]
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import result_changes as rc  # noqa: E402
from harness import pipeline as pl  # noqa: E402
import g1_fill_notices as fn  # noqa: E402
import g1_served_pool_notices as sp  # noqa: E402

REG = os.path.join(ROOT, "registry", "served_pool_additions.json")
HOLDS = os.path.join(ROOT, "registry", "served_pool_holds.json")
PREFIX = "SERVED-POOL REFRESH"


def _num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f else None


_COMPARATOR_KEYS = ("comparator_row", "comparator_row_provenance", "comparator_row_findings", "comparator_sourced",
                    "agreement_with_comparator_row", "comparator_row_reasons", "comparator_row_state")


def _spans(x):
    """Every verbatim span the tracker row (and its acquisition record) carries -- never one from the COMPARATOR's own row:
    our served value must not cite the very meta it is compared with (V6-01's TECOS row cited the comparator's table,
    which labels TECOS's 3-point 0.99 as its 4-point composite; the endpoint gate then refused it)."""
    out = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in _COMPARATOR_KEYS:
                    continue
                if k in ("span", "quote") and isinstance(v, str) and v.strip():
                    out.append(v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(x)
    return out


def _acquired_spans(slug, fam):
    p = os.path.join(ROOT, "registry", "g1_acquired", f"{slug}.json")
    if not os.path.exists(p):
        return []
    pid = fam.replace("PMID ", "").strip()
    d = json.load(open(p, encoding="utf-8"))
    hits = []

    def walk(o):
        if isinstance(o, dict):
            if str(o.get("pmid") or "") == pid and o.get("verdict") == "ADMITTED":
                adm = o.get("admitted") or {}
                hits.extend(s for s in (adm.get("span"), adm.get("quote")) if isinstance(s, str) and s.strip())
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(d)
    return hits


def _held_abstract_spans(slug, pmids):
    """Sentences of the trial's own held abstract (cache/<slug>/records.json) -- committed bytes the pipeline reads."""
    import re
    p = os.path.join(ROOT, "cache", slug, "records.json")
    if not os.path.exists(p):
        return []
    d = json.load(open(p, encoding="utf-8"))
    recs = d if isinstance(d, list) else (d.get("records") if isinstance(d.get("records"), (list, dict)) else d)
    recs = recs if isinstance(recs, list) else list(recs.values())
    out = []
    for r in recs:
        if isinstance(r, dict) and str(r.get("pmid") or r.get("id") or "").replace("PMID ", "") in pmids:
            out.extend(x for x in re.split(r"(?<=[.;])\s+(?=[A-Z])", r.get("abstract") or "") if x.strip())
    return out


def _has(span, *nums):
    from harness import verify
    return all(verify._digits_in(span, n) if isinstance(n, int) else verify._effect_in(span, n) for n in nums)


def _arm_order_ok(span, t, c):
    """The span lists the TREATMENT number before the CONTROL number: some occurrence of t precedes some occurrence of
    c (equal numbers say nothing). Digits being present in any order is not enough -- a span stating 'Treatment: 20 of
    100 ... Control: 10 of 100' never admits 10/100 vs 20/100 (codex review 6 Oct, captain-62d4018f7:g1#1, reproduced)."""
    import re
    if t == c:
        return True
    pos = lambda v: [m.start() for m in re.finditer(r"(?<![\d.,])" + re.escape(str(v)) + r"(?![\d.,]\d)", span)]  # noqa: E731
    pt, pc = pos(t), pos(c)
    return bool(pt and pc) and min(pt) < max(pc)


def report_ids(slug, tid):
    """The held reports (PMIDs) of the trial: a PMID row is its own report; an NCT row's reports are those of the ONE
    family in cache/<slug>/families.json whose family_id is that NCT (else [] -- the row is not admitted)."""
    if tid.startswith("PMID "):
        return [tid.replace("PMID ", "")]
    p = os.path.join(ROOT, "cache", slug, "families.json")
    if not os.path.exists(p):
        return []
    fams = [f for f in json.load(open(p, encoding="utf-8")).get("families") or [] if f.get("family_id") == tid]
    return [r["report_id"] for r in fams[0].get("reports") or []] if len(fams) == 1 else []


def pipeline_row(slug, x, scale):
    """The tracker row as a served-pipeline trial dict, or (None, why)."""
    v = sp.value_of(x) or {}
    fam = str(x.get("family") or "").strip()
    tid = fam if fam.upper().startswith(("PMID ", "NCT")) else f"PMID {fam}"
    counts = [v.get(k) for k in ("events_t", "n_t", "events_c", "n_c")]
    reps = report_ids(slug, tid)
    # the trial's OWN sources first (its acquisition record, then its held abstract), the tracker row's spans last
    spans = _acquired_spans(slug, fam) + _held_abstract_spans(slug, set(reps)) + _spans(x)
    if not reps:
        return None, "no held report of this trial in the topic's family registry"
    base = {"id": tid, "label": x["label"], "provenance": "served_pool_signed_notice", "family_report_id": reps[0],
            "served_pool_admission": {"route": x.get("route"), "basis": x.get("basis"), "report_ids": reps}}
    if scale in ("RR", "OR") and all(c is not None for c in counts):
        a, n1, c, n2 = (int(float(z)) for z in counts)
        span = next((s for s in spans if _has(s, a, n1) and _has(s, c, n2) and _arm_order_ok(s, a, c)
                     and _arm_order_ok(s, n1, n2)), None)
        if not span:
            return None, "no verbatim span carries the counts in treatment-then-control order"
        return dict(base, ai=a, n1i=n1, ci=c, n2i=n2, source=span, derivation="reconstructed"), None
    e, lo, hi = _num(v.get("effect")), _num(v.get("lower")), _num(v.get("upper"))
    if str(v.get("measure") or "").upper() == scale and None not in (e, lo, hi):
        span = next((s for s in spans if _has(s, e) and _has(s, lo) and _has(s, hi)), None)
        if not span:
            return None, "no verbatim span carries the effect and CI"
        return dict(base, effect=e, ci_low=lo, ci_high=hi, scale=scale, source=span, derivation="reported"), None
    return None, f"not fillable on the served scale {scale}"


def _committed():
    """The register as committed (the carry-forward source); [] when absent."""
    if not os.path.exists(REG):
        return []
    return list((json.load(open(REG, encoding="utf-8")) or {}).get("additions") or [])


def hold_applies(h):
    """A hold stays on the record for good. It stops applying only when its SIGNER lifted it: final.state
    LIFTED_BY_SIGNER with who and their verbatim words (Mahmood 7 Oct: 'lift v6-01 and agree'). Any other final state --
    a withdrawal -- keeps the notice out, and a lift with no signer or no quote is not a lift."""
    f = h.get("final") or {}
    return not (f.get("state") == "LIFTED_BY_SIGNER" and str(f.get("by") or "").strip() and str(f.get("quote") or "").strip())


def build(notices=None, holds=None):
    notices = rc.load() if notices is None else notices
    holds = json.load(open(HOLDS, encoding="utf-8"))["holds"] if holds is None else holds
    held = {(h["slug"], h["id"]): h for h in holds if hold_applies(h)}
    adds, excluded = [], []
    for n in notices:
        sig = n.get("reviewer_countersignature") or {}
        if not str(n.get("reason") or "").startswith(PREFIX) or sig.get("state") not in rc.SIGNED_STATES:
            continue
        if rc.not_applied(n):
            continue                     # withdrawn by its signer / superseded: never admitted (and never listed)
        slug, ent = n["slug"], [str(i) for i in n.get("entered_pool") or []]
        tag = f"{slug} / {n['outcome'][:40]} ({n['when_utc']})"
        hit = [held[(slug, i)] for i in ent if (slug, i) in held]
        if hit:
            excluded.append({"notice": tag, "why": "; ".join(f"{h['id']} held: {h['code']}" for h in hit)})
            continue
        prim = fn.served(slug)
        if not prim or prim.get("name") != n["outcome"]:
            excluded.append({"notice": tag, "why": "served primary outcome is not the notice's outcome"})
            continue
        scale = ((prim.get("result") or {}).get("scale") or prim.get("estimand") or "").upper()
        base = dict(prim, trials=[t for t in prim.get("trials") or [] if str(t.get("id")) not in ent])
        studies = fn.served_studies(base, scale)
        before = (rc.result_tuple(pl._pool_result(studies, scale=scale)) if studies
                  else rc.result_tuple({}))
        if not rc._same(n["before"], rc.result_tuple(before)):
            excluded.append({"notice": tag, "why": f"served pool without the entered trials is {before}, notice before {n['before']}"})
            continue
        # CARRY FORWARD: once a signed notice's rows are in the committed register, those exact rows are kept (and
        # re-checked below against the signed after). Re-reading them from the tracker would read back the register's
        # own effect -- the rows are then IN our pool -- and silently drop a signed notice (6 Oct worker run 2: TECOS,
        # COVACTA/TOCIBRAS 'in_our_pool' after the pipeline admitted them). The tracker is read for a FIRST admission only.
        prev = next((e for e in _committed() if e.get("slug") == slug and e.get("outcome") == n["outcome"]
                     and e.get("notice_when_utc") == n["when_utc"]
                     and sorted(r.get("id") for r in e.get("rows") or []) == sorted(ent)), None)
        o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", f"{slug}.json"), encoding="utf-8"))
        inc, _exc = sp.candidates(o)
        rows, why = ([dict(r) for r in prev["rows"]], None) if prev else ([], None)
        for i in ([] if prev else ent):
            xs = [x for x in inc if str(x.get("family") or "").replace("PMID ", "").strip() == i.replace("PMID ", "").strip()]
            if len(xs) != 1:
                why = f"{i}: {len(xs)} tracker-verified rows outside the served pool (need exactly 1)"
                break
            r, w = pipeline_row(slug, xs[0], scale)
            if not r:
                why = f"{i}: {w}"
                break
            rows.append(r)
        if why:
            excluded.append({"notice": tag, "why": why})
            continue
        add_studies = []
        for r in rows:
            st, w = fn.fill_study({"trial": r["label"], "events_t": r.get("ai"), "n_t": r.get("n1i"), "events_c": r.get("ci"),
                                   "n_c": r.get("n2i"), "measure": r.get("scale"), "effect": r.get("effect"),
                                   "lower": r.get("ci_low"), "upper": r.get("ci_high")}, scale)
            add_studies.append(st)
        after = rc.result_tuple(pl._pool_result(studies + add_studies, scale=scale))
        if not rc._same(n["after"], after):
            excluded.append({"notice": tag, "why": f"re-derived after {after} != signed after {n['after']}"})
            continue
        adds.append({"slug": slug, "outcome": n["outcome"], "notice_when_utc": n["when_utc"],
                     "rendered_sha256": sig["rendered_sha256"], "signature_state": sig["state"],
                     "batch_id": sig.get("batch_id"), "before": n["before"], "after": n["after"], "rows": rows})
    return adds, excluded


def main(argv):
    adds, excluded = build()
    for a in adds:
        print("ADMIT ", a["slug"], [r["id"] for r in a["rows"]], a["before"], "->", a["after"])
    for e in excluded:
        print("EXCLUDE", e["notice"], "|", e["why"])
    if "--write" in argv:
        with open(REG, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps({"_doc": "GENERATED by scripts/build_served_pool_additions.py from SIGNED served-pool "
                                 "refresh notices; never hand-edited. Read by harness/served_pool_additions.py.",
                                 "additions": adds, "excluded": excluded}, indent=1, ensure_ascii=False) + "\n")
        print("wrote", REG)


if __name__ == "__main__":
    main(sys.argv[1:])
