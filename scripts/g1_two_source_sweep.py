"""TWO-SOURCE SWEEP over every UNMATCHED comparator trial (Mahmood 3 Oct: 'twenty percent is too low').

For each comparator trial that is neither in our pool nor a named scope/estimand difference (outputs/k_gap/g1/*.json),
try every OPEN source for its typed tuple on the topic outcome, by regex, and verify it:

  (a) AACT posted results by NCT (versioned snapshot): the tracker's registry_binding, through its gates (estimand /
      composite, two arms with people-unit counts) -> PRIMARY_REGISTRY. NCTs come from the k-gap table and from AACT's
      own RESULT/DERIVED references of the trial's PMIDs (kgap.identity_chain.pmid_to_ncts).
  (b) OTHER open-access metas that include the trial, found per trial in Europe PMC (CITES:<trial PMID>_MED, and the
      NCT as text; recorded query + response digest). Each meta's ONE typed JATS table for the topic outcome whose rows
      reproduce its own printed pooled row (secondary_meta_build.typed_table, positive control) gives rows; a row joins
      a comparator trial only through that trial's acronym / label / first-author-year, uniquely
      (secondary_meta_build.family_of_factory over ALL the comparator's trials). Then, exactly as the secondary tier:
        verify_typed      the row's printed numbers found by regex in the trial's held primary text / posted
                          results                                         -> PRIMARY_VERIFIED (route PRIMARY)
        two_source        two INDEPENDENT metas (neither cites the other, no common cited meta, reference lists
                          held) print the same typed tuple               -> TWO_SOURCE_VERIFIED
  (c) regulator documents: the held, hashed FDA/EMA texts of scripts/g1_two_primary.SPECS (RE-LY so far); new ones
      enter by adding a SPEC, never by typing a number.
Rules: the COMPARATOR is never a source (excluded from discovery under every id; g1_countable removes it again); nothing
is typed by hand. FOREST PLOTS (most OA metas print per-trial results only there: 419 of 460 held on 3 Oct had no typed
table for the outcome) are read by the secondary tier's RECORDED model call (secondary_meta_build.read_one, codex,
concurrency 3, replayable), planned greedily so each unmatched trial gets two candidate metas (forest_plan), and pass
the SAME gate as the tier (secondary_meta_build.figure_rows: rows consistent, pooled row printed, rows reproduce it).
A model-read row is a PROPOSAL: it counts only after verify_typed (found in the trial's own text / posted results) or
two_source (an independent meta prints the same tuple). Posted results alone are one source (AACT_ONLY_SINGLE_SOURCE,
recorded, not counted). A trial is SWEEP-VERIFIED only through a counted route (SWEEP_*); its tuple is then compared
with the comparator's own printed row (agreement), which is reported, never used as a source.

    python scripts/g1_two_source_sweep.py [--run] [SLUG ...]   -> outputs/k_gap/sweep/<slug>.json + sweep_summary.json
        --run   network allowed (Europe PMC search, JATS fetch); without it, only recorded searches / held JATS are used
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import os
import re
import sys
import time
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import secondary_meta as sm  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
SWEEP = os.path.join(OUT, "sweep")
SEARCH = os.path.join(SWEEP, "search")
MAX_METAS_PER_TRIAL = 6
META_TITLE = '(TITLE:"meta-analysis" OR TITLE:"meta analysis" OR TITLE:"meta-analyses" OR TITLE:"systematic review")'


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _save(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = f"{p}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, p)


# ------------------------------------------------------------------ targets
def targets(slugs=None, routes=None):
    """{slug: [trial dict]} for every unmatched, un-named comparator trial, with its identity (PMIDs, NCTs, acronyms)."""
    T = _j(os.path.join(OUT, "k_gap_table.json"))
    by = {}
    for t in T["trials"]:
        by.setdefault((t["slug"], t["label"][:60]), t)
    out = {}
    gdir = os.path.join(OUT, "g1")
    for f in sorted(os.listdir(gdir)):
        if not f.endswith(".json") or ".tmp" in f:
            continue
        o = _j(os.path.join(gdir, f))
        if slugs and o["slug"] not in slugs:
            continue
        named = {d.get("trial") for d in o.get("named_differences") or []}
        for x in o.get("trials") or []:
            if x.get("in_our_pool") or x["label"] in named or (routes and x.get("route") not in routes):
                continue
            t = by.get((o["slug"], x["label"])) or {}
            acr = sorted({v["acronym"] for v in (t.get("study") or {}).values() if (v or {}).get("acronym")})
            acr = sorted(set(acr) | label_acronyms(x["label"]))
            out.setdefault(o["slug"], []).append({
                "slug": o["slug"], "label": x["label"], "pmids": list(t.get("pmids") or []),
                "report_pmid": report_pmid(t),
                "cited_pmids": list(t.get("cited_pmids") or []), "ncts": list(t.get("ncts") or []), "acronyms": acr,
                "comparator_row": x.get("comparator_row"), "registry_binding": x.get("registry_binding"),
                "lane_owned": bool(o.get("lane_source"))})
    return out


_YEAR_TAIL = re.compile(r"[-‐ ]?(?:19|20)\d\d$")
_ACR = re.compile(r"^([A-Z][A-Za-z0-9]*(?:[-‐][A-Za-z0-9]+)*)$")


def label_acronyms(label):
    """A trial ACRONYM the comparator's own label carries ('RALES1999' -> RALES, 'ARTS-HF2013' -> ARTS-HF), only when
    distinctive (>= 4 characters, at least two capitals); author labels ('Yusuf, 1991') give none."""
    m = _ACR.match(_YEAR_TAIL.sub("", (label or "").strip()))
    a = m.group(1) if m else ""
    return {a} if len(a) >= 4 and sum(c.isupper() for c in a) >= 2 else set()


def report_pmid(t):
    """The trial REPORT's PMID: the one the comparator cites, else the k-gap reader's shown PMID (never pmids[0]: a
    trial label can carry dozens of linked PMIDs -- TOPCAT has 77)."""
    if t.get("cited_pmids"):
        return str(t["cited_pmids"][0])
    if not t.get("pmids"):
        return None
    import k_gap_identity_reader2 as r2
    try:
        return str(r2.shown_pmid(t))
    except Exception:  # noqa: BLE001 - no shown PMID: the first linked one is not guessed
        return None


def add_registry_ncts(tg):
    """NCTs for PMID-only trials from AACT's OWN-publication references (RESULT/DERIVED), never BACKGROUND."""
    from kgap import aact_adapter, identity_chain as ic
    pm = sorted({p for ts in tg.values() for t in ts if not t["ncts"] for p in [t["report_pmid"]] + t["cited_pmids"] if p})
    if not pm:
        return 0
    link = ic.pmid_to_ncts(pm, aact_adapter.snapshot_dir())
    n = 0
    for ts in tg.values():
        for t in ts:
            if t["ncts"]:
                continue
            got = sorted({nct for p in [t["report_pmid"]] + t["cited_pmids"] if p for nct in (link.get(p) or {})})
            if len(got) == 1:                                     # one trial -> one registration, or none
                t["ncts"], t["nct_basis"] = got, "AACT_RESULT_REFERENCE"
                n += 1
            elif got:
                t["nct_ambiguous"] = got
    return n


# ------------------------------------------------------------------ discovery (recorded)
def search(query, run):
    key = hashlib.sha256(query.encode("utf-8")).hexdigest()[:20]
    p = os.path.join(SEARCH, f"{key}.json")
    if os.path.exists(p):
        return _j(p)
    if not run:
        return {"query": query, "hits": [], "state": "NOT_SEARCHED"}
    from harness import http
    st, b = None, None
    for wait in (0, 5, 20, 60):                    # bounded backoff; a 503 is a state, never a crash or an empty hit list
        time.sleep(wait)
        try:
            st, b = http.get_raw("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                                 {"query": query, "format": "json", "pageSize": "25", "resultType": "lite"}, tries=1,
                                 timeout=60)
            break
        except RuntimeError as exc:
            st = f"FAILED:{str(exc).splitlines()[-1][:80]}"
    if b is None:
        return {"query": query, "hits": [], "state": f"SEARCH_FAILED:{st}"}       # not saved: retried next run
    try:
        d = json.loads(b.decode("utf-8"))
    except ValueError:
        return {"query": query, "hits": [], "state": f"BAD_RESPONSE:{st}"}       # an error page is never data
    hits = [{"pmid": r.get("pmid"), "pmcid": r.get("pmcid"), "doi": (r.get("doi") or "").lower(),
             "cited": r.get("citedByCount"), "year": r.get("pubYear"), "title": (r.get("title") or "")[:200]}
            for r in d.get("resultList", {}).get("result", []) if r.get("pmid")]
    out = {"query": query, "http_status": st, "response_sha256": hashlib.sha256(b).hexdigest(),
           "hitCount": d.get("hitCount"), "hits": hits, "state": "SEARCHED"}
    _save(p, out)
    return out


def discover(t, comp_ids, run, agents=()):
    """Candidate OA metas for ONE trial: those citing its report, those naming its NCT, and those naming its acronym
    together with one of the topic's agents. Discovery needs no trial identity beyond a name; a row still joins only
    through the label/acronym/author-year family check, and counts only after verification."""
    pm = sorted({p for p in [t["report_pmid"]] + t["cited_pmids"][:1] if p})
    qs = [f"CITES:{p}_MED AND {META_TITLE} AND OPEN_ACCESS:y AND HAS_FT:y" for p in pm]
    qs += [f'"{n}" AND {META_TITLE} AND OPEN_ACCESS:y AND HAS_FT:y' for n in t["ncts"][:2]]
    ag = " OR ".join(f'"{a}"' for a in agents[:3])
    qs += [f'"{a}" AND ({ag}) AND {META_TITLE} AND OPEN_ACCESS:y AND HAS_FT:y' for a in t["acronyms"][:2] if ag]
    hits, recs = {}, []
    for q in qs:
        r = search(q, run)
        recs.append({"query": q, "state": r.get("state"), "hitCount": r.get("hitCount"),
                     "response_sha256": r.get("response_sha256")})
        for h in r.get("hits") or []:
            if h["pmid"] in comp_ids or (h.get("doi") and h["doi"] in comp_ids) or h["pmid"] in t["pmids"] + pm:
                continue                                       # the comparator never verifies itself; nor the trial
            hits.setdefault(h["pmid"], h)
    ranked = sorted(hits.values(), key=lambda h: (-(h.get("cited") or 0), h["pmid"]))[:MAX_METAS_PER_TRIAL]
    return [h["pmid"] for h in ranked], recs


# ------------------------------------------------------------------ rows
def entries_for(slug):
    """Every comparator trial of the topic as a family entry (id = its label), so a meta row is assigned to a trial
    only when it names exactly one of them -- matched or not."""
    import k_gap_result_agreement as ra
    T = _j(os.path.join(OUT, "k_gap_table.json"))
    out = []
    for t in T["trials"]:
        if t["slug"] != slug or t.get("drug") == "OTHER_AGENT":
            continue
        acr = sorted({v["acronym"] for v in (t.get("study") or {}).values() if (v or {}).get("acronym")})
        pm = (t.get("pmids") or [None])[0]
        out.append({"id": t["label"][:60], "label": t["label"][:60], "acronyms": acr,
                    "author_year": ra.first_author_year(pm) if pm else None})
    return out


def uncontrolled_tables(meta_pmid, spec):
    """A meta's tables whose CAPTION names the topic outcome and whose rows carry a stated measure, when no table passes
    the pooled-row positive control. Rows from these are CANDIDATES only: they count after verify_typed (the numbers
    found in the trial's own text/registry) or two_source (an independent meta prints the same tuple). Count rows whose
    arm order came from column order alone are dropped (two metas could agree on an inverted ratio)."""
    import secondary_meta_build as smb
    d = os.path.join(smb.k_gap.COMP_DIR, meta_pmid)
    jp = next((os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith("_kgap_jats.xml")), None) \
        if os.path.isdir(d) else None
    if not jp:
        return [], "NO_OPEN_JATS"
    with open(jp, "rb") as fh:
        jb = fh.read()
    if b"<table-wrap" not in jb:
        return [], "NO_TABLES_IN_JATS (figures only -> forest-reader lane)"
    out = []
    for t in sm.typed_rows_from_jats(jb, meta_pmid):
        probe = sm.SecondaryRow(meta_pmid=meta_pmid, meta_doi="", location={"kind": "table", "id": t["table_id"]},
                                source_digest=t["digest"], provenance="TYPED_TABLE", trial_label="",
                                measure=t["measure"] or "", outcome_definition=t["caption"])
        if not t["measure"] or sm.outcome_identity(probe, spec["keywords"], (), tuple(spec.get("core") or ())):
            continue
        keep = [r for r in t["rows"] if not any(f.get("finding") == "ARM_ORDER_FROM_COLUMN_ORDER" for f in r.findings)]
        for r in keep:
            r.provenance = "TYPED_TABLE_UNCONTROLLED"
        if keep:
            out.append(dict(t, rows=keep))
    if not out:
        return [], "NO_TYPED_TABLE_FOR_OUTCOME (figures only -> forest-reader lane)"
    return out, f"UNCONTROLLED_TABLES {[t['table_id'] for t in out]} ({sum(len(t['rows']) for t in out)} rows; count only if verified)"


def forest_plan(ts, metas_by_trial, typed_ok, need=2):
    """Which metas' forest plots to read, greedily: the meta covering the most still-uncovered trials first, until every
    trial has `need` candidate metas read (two independent metas are what the TWO-SOURCE rule asks for)."""
    cover = {t["label"]: 0 for t in ts}
    pool = {m for t in ts for m in metas_by_trial.get(t["label"], []) if m not in typed_ok}
    inc = {m: {t["label"] for t in ts if m in metas_by_trial.get(t["label"], [])} for m in pool}
    plan = []
    while pool:
        m = max(sorted(pool), key=lambda x: sum(1 for lab in inc[x] if cover[lab] < need))
        if not any(cover[lab] < need for lab in inc[m]):
            break
        plan.append(m)
        pool.discard(m)
        for lab in inc[m]:
            cover[lab] += 1
    return plan


def prepare_figures(slug, metas, run):
    """meta -> forest-plot item (JATS figure for the topic outcome + its image), or the reason there is none."""
    import secondary_meta_build as smb
    items, state = {}, {}
    for m in metas:
        try:
            it, why = smb.meta_item(slug, m, offline=not run)
        except Exception as exc:  # noqa: BLE001
            it, why = None, f"ERROR:{type(exc).__name__}:{str(exc)[:80]}"
        if it:
            items[m] = it
        else:
            state[m] = f"NO_FOREST_FIGURE:{why}"
    return items, state


def sweep_topic(slug, ts, run, comp_ids, metas_by_trial, fig_items=None, runs=None):
    import secondary_meta_build as smb
    spec = smb.spec_of(slug)
    fam = smb.family_of_factory(entries_for(slug))
    want = {t["label"] for t in ts}
    metas = sorted({m for t in ts for m in metas_by_trial.get(t["label"], [])})
    rows, meta_state = [], {}
    repro = set()         # metas that SELF-REPRODUCE their printed pooled result (the SECONDARY_SINGLE condition)
    for m in metas:
        try:
            tb = smb.typed_table(slug, m, spec, run)
            tabs, state = ([tb], f"TYPED_TABLE {tb['table_id']} ({len(tb['rows'])} rows, positive control reproduced)") \
                if tb else uncontrolled_tables(m, spec)
        except Exception as exc:  # noqa: BLE001 - one meta's failure is recorded, never fatal
            meta_state[m] = f"ERROR:{type(exc).__name__}:{str(exc)[:80]}"
            continue
        meta_state[m] = state
        if tb:
            repro.add(m)                                   # typed table: its rows reproduced its printed pooled row
        for tbl in tabs:
            for r in tbl["rows"]:
                r = sm.admit(r, spec, fam)
                if r.family_id in want:
                    rows.append(r)
    # (b0) forest plots: the recorded read of each planned meta, through the secondary tier's one gate
    #      (secondary_meta_build.figure_rows: rows consistent, pool printed, rows reproduce it)
    comp_pmid = smb.comparator_pmid(slug)
    for m, it in sorted((fig_items or {}).items()):
        if m in comp_ids:
            continue
        rr = (runs or {}).get(f"{slug}::{m}")
        if not rr or rr["state"] != "RAN_OK" or rr["image_sha256"] != it["image_sha256"]:
            meta_state[m] = (meta_state.get(m, "") + " | FOREST_NOT_YET_READ").strip(" |")
            continue
        try:
            frows, entry = smb.figure_rows(slug, it, rr, spec, comp_pmid)
        except Exception as exc:  # noqa: BLE001
            meta_state[m] = (meta_state.get(m, "") + f" | FOREST_ERROR:{type(exc).__name__}").strip(" |")
            continue
        meta_state[m] = (meta_state.get(m, "") + f" | FOREST {entry.get('figure')} gate {entry.get('gate')} "
                         f"control {(entry.get('positive_control') or {}).get('reproduced')} rows {entry.get('rows_read')}"
                         ).strip(" |")
        if entry.get("gate") == "PASS" and (entry.get("positive_control") or {}).get("reproduced"):
            repro.add(m)                                   # figure read through the tier's gate: pool reproduced
        for r in frows:
            r = sm.admit(r, spec, fam)
            if r.family_id in want:
                rows.append(r)
    # (b0') the DUAL-MODEL forest reader's ACCEPTED rows (scripts/g1_forest_reader.py: codex + agy agree within printed
    #       rounding AND the meta's stated model reproduces its printed pool) -- replayed output, no model here
    import g1_forest_reader as gfr
    dual_metas = set()
    have = {r.meta_pmid for r in rows}         # a meta already giving rows (typed table / tier read) keeps them: two
    for d in gfr.accepted_rows(slug):          # readings of ONE meta would be two rows of one family, refused together
        if str(d.get("meta_pmid")) in comp_ids or str(d.get("meta_pmid")) in have:
            continue
        r = sm.admit(sm.SecondaryRow(**{k: v for k, v in d.items() if k in sm.SecondaryRow.__dataclass_fields__}),
                     spec, fam)
        repro.add(r.meta_pmid)
        dual_metas.add(r.meta_pmid)
        if r.family_id in want:
            rows.append(r)
    for m in sorted(dual_metas):
        meta_state[m] = (meta_state.get(m, "") + " | DUAL_FOREST_READER ACCEPTED (stated-model reconstruction)").strip(" |")
    metas = sorted(set(metas) | set(fig_items or {}) | dual_metas)
    # (b1) the meta's printed numbers in the trial's OWN held primary sources (text, posted results) -> PRIMARY
    smb.ensure_registry(sorted({n for t in ts for n in t["ncts"]}))
    by_label = {t["label"]: t for t in ts}
    terms = [k for k in (spec.get("keywords") or []) if k] + list(spec.get("core") or [])
    for r in rows:
        t = by_label[r.family_id]
        if r.state == sm.UNVERIFIED and (t["report_pmid"] or t["ncts"]):
            sm.verify_typed(r, smb.primary_sources(slug, t["report_pmid"] or "", (t["ncts"] or [None])[0]), terms)
    sm.consolidate(rows)
    sm.cross_check(rows)
    # (b2) two independent metas, same typed tuple
    sm.two_source(rows, smb.refs_of, [smb.meta_aliases(m) for m in metas])

    # (b3) SECONDARY_SINGLE (Mahmood 3 Oct): ONE non-comparator meta that self-reproduces its pooled result counts when
    #      NO primary source is open for the trial. 'Open' = the trial's full text (PMC OA / held / Unpaywall) or its
    #      posted results; its PubMed abstract alone is not (had it printed the number, verify_typed would have matched).
    def primary_open(r):
        t = by_label[r.family_id]
        if not (t["report_pmid"] or t["ncts"]):
            return None
        srcs = smb.primary_sources(slug, t["report_pmid"] or "", (t["ncts"] or [None])[0])
        return next((ref for kind, ref, _ in srcs if not ref.endswith(" abstract")), None)
    sm.secondary_single(rows, comp_ids, primary_open, lambda r: r.meta_pmid in repro)
    countable = {id(r) for r in sm.g1_countable(rows, comp_ids)}
    import g1_tracker as gt
    res = []
    for t in ts:
        mine = [r for r in rows if r.family_id == t["label"]]
        ok = [r for r in mine if id(r) in countable]
        rb = t.get("registry_binding") or {}
        bind = next((c for c in rb.get("candidates") or [] if c.get("verdict") == "BINDABLE"), None)
        route, value = None, None
        if ok:
            best = sorted(ok, key=lambda r: {"PRIMARY": 0, "TWO_SOURCE": 1}.get(sm.route_of(r), 2))[0]
            # a counted route is TWO sources agreeing on the typed tuple (a meta row + the trial's own text, a meta row +
            # posted results, or two independent metas) -- or, by the 3 Oct decision, SECONDARY_SINGLE: one
            # self-reproducing non-comparator meta when no primary source is open (route SWEEP_SECONDARY_SINGLE)
            route = "SWEEP_" + ("META+TRIAL_TEXT" if (best.verification or {}).get("route") == "PRIMARY_TEXT" else
                                "META+AACT" if (best.verification or {}).get("route") == "PRIMARY_REGISTRY" else
                                "TWO_INDEPENDENT_METAS" if sm.route_of(best) == "TWO_SOURCE" else sm.route_of(best))
            value = {k: getattr(best, k) for k in ("measure", "effect", "lower", "upper", "events_t", "n_t",
                                                   "events_c", "n_c")}
            basis = {"meta": best.meta_pmid, "table": (best.location or {}).get("id"),
                     "row_label": best.trial_label, "verification": best.verification}
        elif bind and len(bind.get("arms") or []) == 2:
            a = bind["arms"]
            # posted results ALONE are one source: recorded, never counted (SMART's posted counts cover 5,381 patients,
            # its report 15,802 -- one source cannot tell which population a number belongs to)
            route = "AACT_ONLY_SINGLE_SOURCE"
            value = {"measure": "COUNTS", "arms": [{"title": x.get("title"), "count": x.get("count"), "n": x.get("n")}
                                                   for x in a]}
            basis = {"nct": bind["nct"], "outcome": bind["title"], "snapshot": bind["snapshot"],
                     "analysis": bind.get("analysis")}
        else:
            basis = None
        cr = t.get("comparator_row")
        agree = None
        if value and cr and value.get("measure") != "COUNTS":
            theirs = sm.SecondaryRow(meta_pmid="COMPARATOR", meta_doi="", location={}, source_digest="",
                                     provenance="COMPARATOR_ROW", trial_label=t["label"],
                                     measure=cr.get("measure") or "", outcome_definition="",
                                     **{k: cr.get(k) for k in ("effect", "lower", "upper", "events_t", "n_t",
                                                               "events_c", "n_c")})
            agree = gt.agreement(value, theirs)
        res.append({"label": t["label"], "pmids": t["pmids"], "ncts": t["ncts"], "nct_basis": t.get("nct_basis"),
                    "metas_found": metas_by_trial.get(t["label"], []),
                    "rows": [{"meta": r.meta_pmid, "state": r.state, "row_label": r.trial_label, "measure": r.measure,
                              "effect": r.effect, "lower": r.lower, "upper": r.upper, "events_t": r.events_t,
                              "n_t": r.n_t, "events_c": r.events_c, "n_c": r.n_c, "reasons": r.reasons[:4],
                              "verification": r.verification} for r in mine],
                    "verdict": route or ("ROWS_NOT_VERIFIED" if mine else
                                         "NO_META_ROW" if metas_by_trial.get(t["label"]) else
                                         "NO_IDENTITY" if not (t["pmids"] or t["ncts"]) else "NO_SOURCE_FOUND"),
                    "value": value, "basis": basis, "agreement_with_comparator_row": agree})
    return {"slug": slug, "metas": meta_state, "trials": res,
            "tally": dict(Counter(r["verdict"] for r in res))}


def main(argv):
    import secondary_meta_build as smb
    run = "--run" in argv
    slugs = [a for a in argv if not a.startswith("--")] or None
    t0 = time.time()
    # --routes=UNVERIFIED: the trials that already HAVE one row (cheapest second-source wins) first (Mahmood 3 Oct)
    routes = next((set(a.split("=", 1)[1].split(",")) for a in argv if a.startswith("--routes=")), None)
    tg = targets(slugs, routes)
    n_nct = add_registry_ncts(tg)
    # discovery: per trial, in parallel (network bound; Europe PMC returns 503 above ~2 concurrent)
    metas_by = {}
    disc = {}
    comp = {s: {smb.comparator_pmid(s)} | smb.meta_aliases(smb.comparator_pmid(s)) for s in tg}
    agents = {s: [a for a in (_j(os.path.join(ROOT, "topics", s + ".json")).get("intervention_agents") or
                              _j(os.path.join(ROOT, "topics", s + ".json")).get("intervention_terms") or []) if len(a) >= 4]
              for s in tg}
    jobs = [(s, t) for s, ts in tg.items() for t in ts]
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        for (s, t), (ms_, recs) in zip(jobs, ex.map(lambda st: discover(st[1], comp[st[0]], run, agents[st[0]]), jobs)):
            metas_by.setdefault(s, {})[t["label"]] = ms_
            disc[(s, t["label"])] = recs
    # JATS fetch for every discovered meta, in parallel, before the (sequential, deterministic) row pass
    if run:
        allm = sorted({m for d in metas_by.values() for v in d.values() for m in v})
        with cf.ThreadPoolExecutor(max_workers=4) as ex:
            list(ex.map(lambda m: smb.k_gap.fetch_comparator_jats(m, smb.DATE), allm))
    # forest plots: plan per topic (metas with no typed table), prepare figures, then RECORDED reads, codex at
    # concurrency 3, at most --max-reads per invocation (hourly batches); the ledger is the per-topic runs store
    from kgap import runs_store
    max_reads = next((int(a.split("=", 1)[1]) for a in argv if a.startswith("--max-reads=")), 60)
    runs = runs_store.load()
    fig, fig_state, todo = {}, {}, []
    for s, ts in sorted(tg.items()):
        typed_ok = set()          # typed tables are tried inside sweep_topic; a forest read is planned for every meta
        plan = forest_plan(ts, metas_by.get(s, {}), typed_ok)
        fig[s], fig_state[s] = prepare_figures(s, plan, run)
        for m in plan:
            it = fig[s].get(m)
            rr = runs.get(f"{s}::{m}")
            if it and not (rr and rr["state"] == "RAN_OK" and rr["image_sha256"] == it["image_sha256"]):
                todo.append(it)
    todo = todo[:max_reads] if run else []
    if todo:
        with cf.ThreadPoolExecutor(max_workers=3) as ex:              # codex concurrency 3
            for r in ex.map(smb.read_one, todo):
                runs[r["key"]] = r
                runs_store.save(runs, slugs={r["key"].split("::")[0]})   # ledgered per read: a kill never re-pays
                print("READ", r["key"], r["state"], r["record_id"], flush=True)
        runs_store.save(runs, slugs={it["slug"] for it in todo})
    summary = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "run": run, "ncts_added_from_aact_references": n_nct,
               "forest_reads_this_run": len(todo),
               "forest_planned": sum(len(v) + len(fig_state[k]) for k, v in fig.items()),
               "forest_reads_held": sum(1 for s in fig for m, it in fig[s].items()
                                        if (runs.get(f"{s}::{m}") or {}).get("state") == "RAN_OK"),
               "topics": {}}
    for s, ts in sorted(tg.items()):
        o = sweep_topic(s, ts, run, comp[s], metas_by.get(s, {}), fig.get(s), runs)
        o["metas"].update({m: v for m, v in fig_state[s].items() if m not in o["metas"]})
        for r in o["trials"]:
            r["searches"] = disc.get((s, r["label"]))
        sp = os.path.join(SWEEP, f"{s}.json")
        if routes and os.path.exists(sp):
            # a route-filtered run (--routes=) re-sweeps a SUBSET: merge it into the topic's file, never truncate it
            prev = _j(sp)
            mine = {r["label"] for r in o["trials"]}
            o["trials"] = [r for r in prev.get("trials") or [] if r["label"] not in mine] + o["trials"]
            o["metas"] = dict(prev.get("metas") or {}, **o["metas"])
            o["tally"] = dict(Counter(r["verdict"] for r in o["trials"]))
        _save(sp, o)
        summary["topics"][s] = o["tally"]
        print(s, o["tally"], flush=True)
    tot = Counter()
    for v in summary["topics"].values():
        tot.update(v)
    summary["total"] = dict(tot)
    summary["n_targets"] = sum(len(v) for v in tg.values())
    summary["secs"] = round(time.time() - t0, 1)
    _save(os.path.join(SWEEP, "sweep_summary.json"), summary)
    print(json.dumps({k: summary[k] for k in ("n_targets", "total", "ncts_added_from_aact_references",
                                               "forest_planned", "forest_reads_held", "forest_reads_this_run", "secs")}))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
