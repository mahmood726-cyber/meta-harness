"""PER-TRIAL PRIMARY VERIFICATION of a topic's outcome from each trial's OWN report (flip plan #6 tocilizumab,
#4 pcsk9 'PMC for the rest'; 5 Oct). One job per trial, recorded, through the build's own machinery -- nothing typed by
hand, no gate loosened:

  report    the trial's report that names the topic's INTERVENTION in its title (deterministic): among the trial's
            known PMIDs (sweep targets: k-gap table + AACT RESULT references), else Europe PMC hits for its NCT
            (recorded query); exactly one candidate, or the trial is recorded REPORT_AMBIGUOUS / REPORT_NOT_FOUND
  value     secondary_meta_build.primary_value(slug, pmid, run, runs, want="counts"): regex on the abstract, the typed
            full-text rung (PMC OA, else Unpaywall's open copy), then a RECORDED locator (codex) whose quote must be
            verbatim in the report and contain every number it copies (sm.gate_locator_claim)
  timepoint for a topic that registers one (tocilizumab: 28 days), the verified span must STATE it
            (secondary_meta_build.meta_timepoint of the span == the protocol's) -- else TIMEPOINT_NOT_IN_SPAN
  output    registry/model_proposals/g1_primary_verify_<slug>.json: per trial the report, the value (counts + span +
            how), or why not. This is the per-trial primary evidence a SERVED-POOL notice needs; it is not itself a
            counted tracker route for a trial outside our pool (is_matched: in our pool, or a two-source SWEEP_*).

    python scripts/g1_primary_verify.py --run SLUG [LABEL ...]
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_forest_reader as gfr  # noqa: E402
import secondary_meta_build as smb  # noqa: E402
from harness import secondary_meta as sm  # noqa: E402

# one ledger per box: the worker (run-remote.ps1) writes its own, merged afterwards by key
RUNS = os.environ.get("G1_PV_RUNS") or os.path.join(ROOT, "registry", "model_proposals", "g1_primary_verify_runs.json")
INTERVENTION = {"tocilizumab-covid19-mortality": r"tocilizumab|interleukin[- ]6 receptor|IL-6 receptor|IL-6R",
                "pcsk9-mace": r"alirocumab|evolocumab|PCSK9|proprotein convertase",
                "omega3-cardiovascular-events": r"omega-3|n-3|fish oil|eicosapentaenoic|icosapent|docosahexaenoic|"
                                                r"fatty acid"}


def _meta(pmid, run, pubtypes):
    """(title, pub types) of a PMID from Europe PMC (core); pub types recorded in the output's 'pubtypes'."""
    from harness import http
    if not run:
        return None
    try:
        st, b = http.get_raw("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                             {"query": f"EXT_ID:{pmid} AND SRC:MED", "format": "json", "resultType": "core"}, tries=2)
        r = (json.loads(b.decode("utf-8")).get("resultList") or {}).get("result") or []
        if not r:
            return None
        pubtypes[pmid] = list((r[0].get("pubTypeList") or {}).get("pubType") or [])
        return r[0].get("title")
    except Exception:  # noqa: BLE001
        return None


RCT_TYPE = re.compile(r"randomi[sz]ed controlled trial", re.I)
NOT_REPORT = re.compile(r"comment|letter|erratum|correction|editorial|review|protocol", re.I)


def nct_hits(nct, run):
    from harness import http
    if not run or not nct:
        return []
    try:
        st, b = http.get_raw("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                             {"query": f'"{nct}" AND SRC:MED', "format": "json", "resultType": "lite",
                              "pageSize": "50"}, tries=2)
        return [(r["pmid"], r.get("title") or "") for r in (json.loads(b.decode("utf-8")).get("resultList") or {})
                .get("result") or [] if r.get("pmid")]
    except Exception:  # noqa: BLE001
        return []


def own_pmids(ts):
    """Each trial's PMIDs minus those also listed for a trial of a DIFFERENT registration (a pooled analysis or shared
    reference is never one trial's own report). Sharing within one registration (CORIMUNO-TOCI-1 / -ICU) is kept, so
    the claimed-by-two refusal still sees it."""
    regs = {}
    for t in ts:
        for p in set(t.get("pmids") or []):
            regs.setdefault(p, set()).add(tuple(sorted(t.get("ncts") or [t["label"]])))
    return [[p for p in (t.get("pmids") or []) if len(regs[p]) == 1] for t in ts]


def settle(results):
    """Several candidate reports of one trial: PRIMARY_VERIFIED only when every report that verified gives the SAME
    counts; disagreement or none verified is recorded, never chosen between."""
    key = ("events_t", "n_t", "events_c", "n_c")
    ok = [r for r in results if r.get("state") == "PRIMARY_VERIFIED"]
    vals = {tuple((r.get("value") or {}).get(k) for k in key) for r in ok}
    if not ok:
        return {"state": "NO_REPORT_VERIFIED:" + ",".join(sorted({str(r.get("state")).split(":")[0] for r in results}))}
    if len(vals) > 1:
        return {"state": "REPORTS_DISAGREE", "values": sorted(vals, key=str)}
    return dict(ok[0], settled_by=f"VERIFIED_REPORTS_AGREE_{len(ok)}")


def choose_report(slug, t, run, titles, pubtypes):
    """(pmid, basis) or (None, why): the ONE report whose title names the intervention; when several do, the ONE whose
    publication type is a randomised controlled trial (never a comment / letter / erratum / review / protocol)."""
    pat = INTERVENTION[slug]
    cands = []
    for p in t.get("pmids") or []:
        if p not in titles:
            titles[p] = _meta(p, run, pubtypes)
        if titles[p] and re.search(pat, titles[p], re.I):
            cands.append(p)
    basis = "TRIAL_PMIDS_TITLE_NAMES_INTERVENTION"
    if not cands:
        for p, ti in nct_hits((t.get("ncts") or [None])[0], run):
            titles.setdefault(p, ti)
            if re.search(pat, ti, re.I) and not re.search(r"meta-analys|systematic review|protocol|rationale|"
                                                          r"design|statistical analysis plan", ti, re.I):
                cands.append(p)
        basis = "EPMC_NCT_HITS_TITLE_NAMES_INTERVENTION"
    cands = list(dict.fromkeys(cands))
    if len(cands) > 1:
        for p in cands:
            if p not in pubtypes:
                _meta(p, run, pubtypes)
        rct = [p for p in cands if any(RCT_TYPE.search(x) for x in pubtypes.get(p) or [])
               and not any(NOT_REPORT.search(x) for x in pubtypes.get(p) or [])]
        if len(rct) == 1:
            return rct[0], basis + "+PUBTYPE_RCT"
    if len(cands) == 1:
        return cands[0], basis
    t["_cands"] = cands
    return None, ("REPORT_NOT_FOUND" if not cands else f"REPORT_AMBIGUOUS:{cands[:6]}")


MAX_CANDIDATES = 4


def verify_many(slug, t, run, runs, titles, spec, chosen):
    """An ambiguous choice of <= MAX_CANDIDATES reports: verify each, settle() by agreement."""
    pmid, basis = chosen
    if pmid or not basis.startswith("REPORT_AMBIGUOUS"):
        return verify(slug, t, run, runs, titles, spec, chosen)
    cands = t.get("_cands") or []
    if not cands or len(cands) > MAX_CANDIDATES:
        return verify(slug, t, run, runs, titles, spec, chosen)
    each = [verify(slug, t, run, runs, titles, spec, (p, "CANDIDATE")) for p in cands]
    out = {"label": t["label"], "ncts": t.get("ncts"), "report_pmid": None, "report_basis": basis,
           "candidates": each}
    out.update(settle(each))
    return out


def verify(slug, t, run, runs, titles, spec, chosen):
    pmid, basis = chosen
    out = {"label": t["label"], "ncts": t.get("ncts"), "report_pmid": pmid, "report_basis": basis,
           "report_title": titles.get(pmid) if pmid else None}
    if not pmid:
        return out
    prim, how = smb.primary_value(slug, pmid, run, runs, want="counts")
    out["how"] = how
    if not prim:
        out["state"] = f"NO_PRIMARY_VALUE:{how}"
        return out
    out["value"] = prim
    days = sm._days(spec.get("timepoint") or "")
    if days is not None:
        # the verified span must STATE the protocol's length of time, in any explicit form ('died within 28 days',
        # 'day 28', '28-day mortality'); another length stated ('15 days') or none -> not verified
        span = prim.get("span") or ""
        n = str(int(days))
        if not re.search(rf"(?<!\d){n}[- ]?(?:days?|d)\b|\bday[- ]?{n}(?!\d)", span, re.I):
            out["state"] = "TIMEPOINT_NOT_IN_SPAN"
            return out
    out["state"] = "PRIMARY_VERIFIED"
    return out


def main(argv):
    run = "--run" in argv
    args = [a for a in argv if not a.startswith("--")]
    slug, labels = args[0], set(args[1:])
    import g1_two_source_sweep as sw
    ts = sw.targets([slug], None).get(slug) or []
    if labels:
        ts = [t for t in ts if t["label"] in labels]
    spec = smb.spec_of(slug)
    runs = gfr._j(RUNS) if os.path.exists(RUNS) else {}
    outp = os.path.join(ROOT, "registry", "model_proposals", f"g1_primary_verify_{slug}.json")
    prev = gfr._j(outp) if os.path.exists(outp) else {}
    titles = prev.get("titles") or {}
    pubtypes = prev.get("pubtypes") or {}
    with gfr.RunLock(RUNS) if run else _null():
        # SEQUENTIAL first: report choice and each report's record fetch (shared files); then the jobs in parallel
        for t, own in zip(ts, own_pmids(ts)):
            t["pmids"] = own
        chosen = [choose_report(slug, t, run, titles, pubtypes) for t in ts]
        # a report claimed by two trials is neither's own report: both become ambiguous
        claims = {}
        for (pm, _), t in zip(chosen, ts):
            if pm:
                claims.setdefault(pm, []).append(t["label"])
        chosen = [(pm, b) if not pm or len(claims[pm]) == 1 else (None, f"REPORT_CLAIMED_BY_{len(claims[pm])}_TRIALS:{pm}")
                  for pm, b in chosen]
        for (pm, b), t in zip(chosen, ts):
            for p in ([pm] if pm else (t.get("_cands") or [])[:MAX_CANDIDATES] if b.startswith("REPORT_AMBIGUOUS") else []):
                smb._trial_text(slug, p, run)
        with cf.ThreadPoolExecutor(max_workers=3) as ex:          # codex concurrency 3 (only the locator rung calls it)
            res = list(ex.map(lambda tc: verify_many(slug, tc[0], run, runs, titles, spec, tc[1]), zip(ts, chosen)))
        gfr._save(RUNS, runs)
    from collections import Counter
    out = {"slug": slug, "spec": {k: spec.get(k) for k in ("estimand", "timepoint")}, "titles": titles,
           "pubtypes": pubtypes,
           "tally": dict(Counter((r.get("state") or r.get("report_basis") or "?").split(":")[0] for r in res)),
           "trials": res}
    gfr._save(outp, out)
    print(json.dumps(out["tally"]))
    for r in res:
        v = r.get("value") or {}
        print(f"  {r['label'][:22]:22s} {str(r.get('report_pmid')):9s} {str(r.get('state') or r.get('report_basis'))[:48]:48s}"
              f" {v.get('events_t')}/{v.get('n_t')} vs {v.get('events_c')}/{v.get('n_c')}")


class _null:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
