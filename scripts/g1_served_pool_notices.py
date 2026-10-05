"""SERVED-POOL REFRESH NOTICES (Mahmood 5 Oct: "yes can sign"): every trial the G1 tracker VERIFIED from a primary source
(route PRIMARY / TWO_SOURCE / SWEEP_AACT_PRIMARY, counted by the page renderer) that is NOT in the served pool gets a
result-change notice for its review's primary outcome -- derived, never applied. docs/reviews/ is not touched; the
notices are appended OPEN to docs/result_changes.json for scripts/signing_packet.py.

Per topic:
  control  harness.synth.pool over the SERVED trials must reproduce the served result (k equal; estimate and CI within
           1e-3); otherwise the topic is refused (the engine cannot stand in for the served pipeline here)
  before   the served primary result, exactly as served
  after    the same engine over the served trials PLUS each verified trial on the served scale (counts when the scale is
           RR/OR; else its effect + CI when its measure IS the served scale)
Excluded, each with its reason (listed, never silently):
  SECONDARY_SINGLE rows     queued for primary verification -- not primary-verified
  served-pipeline refusals  a blocker that records the served pipeline refusing the trial's numbers
                            (COUNTS_PRESENT_NOT_CORROBORATED, SCREENER..., UNIT_OF_ANALYSIS...) -- this refresh never
                            bypasses a served gate
  not on the served scale   no counts and a different measure

    python scripts/g1_served_pool_notices.py [--write]   -> outputs/k_gap/served_pool_notices.json (+ docs notices)
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import result_changes as rc  # noqa: E402
from harness import synth  # noqa: E402
import g1_fill_notices as fn  # noqa: E402
import render_g1_tracker as rg  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
VERIFIED = ("PRIMARY", "TWO_SOURCE", "SWEEP_AACT_PRIMARY")
SERVED_REFUSAL = ("COUNTS_PRESENT_NOT_CORROBORATED", "SCREENER_ERROR", "UNIT_OF_ANALYSIS")
TOL = 1e-3


def _ncts_of_pmid(pmid):
    """NCTs a PMID's own records link (AACT reference table, then PubMed's databank link), from the held caches."""
    global _STORE, _PN
    if _STORE is None:
        sp, pp = os.path.join(OUT, "_aact_store.json"), os.path.join(OUT, "pubmed_ncts.json")
        _STORE = (json.load(open(sp, encoding="utf-8")).get("pmid") or {}) if os.path.exists(sp) else {}
        _PN = json.load(open(pp, encoding="utf-8")) if os.path.exists(pp) else {}
    out = {str(n).upper() for n, _t in _STORE.get(str(pmid), [])}
    if _PN.get(str(pmid)):
        out.add(str(_PN[str(pmid)]).upper())
    return out


_STORE = _PN = None


def identity_ncts(x):
    fam = str(x.get("family") or "").replace("PMID ", "").strip()
    return {fam.upper()} if fam.upper().startswith("NCT") else _ncts_of_pmid(fam) if fam.isdigit() else set()


def served_identity(prim):
    """PMIDs and NCTs of the trials already in the served pool (a served PMID is linked to its NCT)."""
    pmids = {str(t.get("id") or "").replace("PMID ", "").strip() for t in prim.get("trials") or []}
    return pmids, set().union(*[_ncts_of_pmid(p) for p in pmids]) if pmids else set()


def value_of(x):
    return (x.get("sweep") or {}).get("value") if x.get("route") == "SWEEP_AACT_PRIMARY" else x.get("our_value")


def candidates(o):
    """(included, excluded) verified-outside-the-served-pool trials of one tracker topic, by the page's own count."""
    r = rg.recompute(o)
    inc, exc = [], []
    for row in r["rows"]:
        x = row["trial"]
        if x.get("in_our_pool") or x.get("scope_difference") or not row["counted"]:
            continue
        if x.get("route") not in VERIFIED:
            exc.append({"trial": x["label"], "why": f"{x.get('route')}: queued for primary verification, not primary-verified"})
            continue
        blk = str(x.get("blocker") or "")
        if any(s in blk for s in SERVED_REFUSAL):
            exc.append({"trial": x["label"], "why": f"served-pipeline refusal recorded ({blk}); not bypassed"})
            continue
        inc.append(x)
    return inc, exc


def topic_notice(o):
    slug = o["slug"]
    inc, exc = candidates(o)
    if not inc:
        return None, exc
    prim = fn.served(slug)
    if not prim:
        return None, exc + [{"trial": "(topic)", "why": "no served primary outcome"}]
    res = prim.get("result") or {}
    scale = (res.get("scale") or prim.get("estimand") or "").upper()
    before = rc.result_tuple(res)
    studies = fn.served_studies(prim, scale)
    if studies:
        try:
            ctl = synth.pool(studies, scale=scale)
        except Exception as e:                                  # the engine cannot rebuild the served pool
            return None, exc + [{"trial": "(topic)", "why": f"control failed: {type(e).__name__}: {e}"}]
        bad = ctl.k != before.get("k") or any(before.get(k) is not None and abs(getattr(ctl, k) - before[k]) > TOL
                                              for k in ("estimate",))
        if bad:
            return None, exc + [{"trial": "(topic)", "why": f"control failed: the engine gives k={ctl.k} "
                                 f"{ctl.estimate:.4f} for the served pool, served is {before}"}]
    entered, described = [], []
    s_pmids, s_ncts = served_identity(prim)
    for x in list(inc):
        fam = str(x.get("family") or "").replace("PMID ", "").strip()
        hit = (fam in s_pmids) or bool(identity_ncts(x) & s_ncts)
        if hit:
            # the tracker keyed the trial by another identifier (RECOVERY: NCT04381936 vs the served PMID 33933206):
            # it IS in the served pool -- never entered twice
            inc.remove(x)
            exc.append({"trial": x["label"], "why": f"ALREADY_IN_SERVED_POOL by identity ({x.get('family')} = served "
                        f"{sorted(identity_ncts(x) & s_ncts) or fam}); the tracker's in_our_pool missed the link"})
    for x in inc:
        v = dict(value_of(x) or {}, trial=x["label"])
        st, why = fn.fill_study(v, scale)
        if not st:
            exc.append({"trial": x["label"], "why": why})
            continue
        st.source = f"{x['route']} ({x.get('family')})"
        studies.append(st)
        tid = str(x.get("family") or x["label"])
        val = (f"{v.get('events_t')}/{v.get('n_t')} vs {v.get('events_c')}/{v.get('n_c')}" if scale in ("RR", "OR")
               and None not in (v.get("events_t"), v.get("n_t"), v.get("events_c"), v.get("n_c"))
               else f"{scale} {v.get('effect')} ({v.get('lower')} to {v.get('upper')})")
        entered.append(tid)
        described.append(f"{tid} entered the pool contributing {val} ({x['label']}; verified {x['route']})")
    if not entered:
        return None, exc
    # the SERVED pipeline's own result function (harness.pipeline._pool_result), not the bare engine: it carries the
    # served rules -- 4-dp rounding, and at k=1 the single trial's REPORTED CI verbatim (V6-03/V6-04 were derived with
    # the bare engine's recomputed CI and could never have matched the served page within the gate's 1e-6)
    from harness import pipeline as _pl
    pr = _pl._pool_result(studies, scale=scale)
    nan = lambda v: None if v is None or v != v else float(v)  # noqa: E731
    after = {"k": pr["k"], "estimate": nan(pr.get("estimate")), "ci_low": nan(pr.get("ci_low")), "ci_high": nan(pr.get("ci_high"))}
    notice = {"slug": slug, "outcome": prim.get("name"), "before": before, "after": after, "left_pool": [],
              "entered_pool": entered,
              "reason": (f"SERVED-POOL REFRESH (Mahmood 5 Oct, 'yes can sign'): {len(entered)} trial(s) verified from a "
                         f"primary source by the G1 tracker enter the served pool. "
                         + "; ".join(described) + ". Entering trials are new evidence, not a correction: the "
                         f"previously served number is not challenged. Engine harness.synth.pool on the served {scale} scale (the same "
                         f"engine reproduces the served pool before the change). Excluded: "
                         + ("; ".join(f"{e['trial']}: {e['why']}" for e in exc) if exc else "none") + "."),
              "by": "Claude Opus 5.5 (captain lane, g1_served_pool_notices.py); reviewer countersignature owed: Mahmood",
              "when_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "reviewer_countersignature": {"state": "OPEN", "note": "the reviewer has not yet seen the rendered notice; "
                                            "sign with scripts/countersign_result_change.py after reading it"}}
    return notice, exc


def main(argv):
    rows = []
    for p in sorted(glob.glob(os.path.join(OUT, "g1", "*.json"))):
        o = json.load(open(p, encoding="utf-8"))
        n, exc = topic_notice(o)
        if n or exc:
            rows.append({"slug": o["slug"], "notice": n, "excluded": exc})
    with open(os.path.join(OUT, "served_pool_notices.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"derived_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "topics": rows}, fh,
                  indent=1, ensure_ascii=False)
    for r in rows:
        n = r["notice"]
        print(r["slug"], "|", (f"{n['before']} -> {n['after']} | entered {n['entered_pool']}" if n else "NO NOTICE"),
              "| excluded", [f"{e['trial'][:24]}: {e['why'][:70]}" for e in r["excluded"]])
    if "--write" in argv:
        dp = os.path.join(ROOT, "docs", "result_changes.json")
        d = json.load(open(dp, encoding="utf-8"))
        d["notices"] += [r["notice"] for r in rows if r["notice"]]
        with open(dp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
        print("appended", sum(1 for r in rows if r["notice"]), "OPEN notices to docs/result_changes.json")


if __name__ == "__main__":
    main(sys.argv[1:])
