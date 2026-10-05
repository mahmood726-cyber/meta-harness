"""G1 SEARCH + SCREEN RECALL AUDIT (lane g1/search-screen-audit, 2026-10-05). For every comparator trial of the 32 G1
topics: did OUR registered search identify it, does a published meta's reference / included-study list identify it
(REVIEW_REFERENCE_LIST), and how did OUR screen decide it (rule + verbatim span)? Harness code only: every join is a
deterministic rule over committed artefacts; network probes (miss typing) and model readings are recorded separately
(scripts/g1_search_miss_probe.py, scripts/g1_screen_dual_review.py) and only READ here.

Denominators (enumerated, never assumed -- lessons 'list the KINDS of item before the number'):
  COMPARATOR  every trial row of outputs/k_gap/g1/<slug>.json (the tracker's comparator set, 348 on main 469a97eb)
  ELIGIBLE    COMPARATOR minus the tracker's named differences (N_eligible; the search/screen recall denominator)
  SCREEN_NAMED  named differences that are OUR SCREEN's rule exclusions (X1/X2/X3/X-DESIGN/X-DOSE): the trial left the
              eligible set BECAUSE our screen excluded it, so these are re-checked as possible false exclusions
              (Nidorf/LoDoCo X2 is one) -- never counted as correct by construction

Per trial:
  identity    PMIDs / NCTs from the tracker row (family, seeded_funnel, registry_binding), the identity chain
              (outputs/k_gap/identity_chain.json) and acq's k_gap_table (pinned commit); none -> IDENTITY_UNRESOLVED
  search      IDENTIFIED when a PMID or NCT of the trial is a record our registered search retrieved
              (cache/<slug>/records.json: PubMed records + CT.gov records), or when another report of the same trial
              family (docs/reviews/<slug>/review.json trial_families) is; else NOT_IDENTIFIED
  rrl         COMPARATOR_LIST (the comparator's own included-study table lists it: true for every row, by construction --
              reported, never counted as independent) and OTHER_META (a non-comparator meta's row for the same family:
              registry/secondary_meta/<slug>.json, acq/k-gap, pinned)
  screen      our decision on the identified record(s): include / exclude + rule_id, reason, span; stage FULL_TEXT when
              the decision cites a held full text, else TITLE_ABSTRACT; NOT_SCREENED when no identified record exists
  miss_type   for a search miss, from the recorded probe (outputs/search_audit/search_miss_probe.json): QUERY_GAP,
              DATE_WINDOW, DATABASE_NOT_SEARCHED, IDENTITY_FAILURE, RETRIEVED_NOT_RETAINED; PROBE_PENDING until probed

  python scripts/g1_search_screen_audit.py           -> outputs/search_audit/SEARCH_SCREEN_AUDIT.json + .md
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "search_audit")
ACQ_COMMIT = "8febcb3c1b17a62110673d5e15396094de3839f9"      # origin/acq/k-gap read 2026-10-05 (pinned)
SCREEN_RULES = {"X1", "X2", "X3", "X-DESIGN", "X-DOSE"}
PMID = re.compile(r"\b(\d{6,9})\b")
NCT = re.compile(r"\b(NCT\d{8})\b", re.I)


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _pinned(path):
    """(object, sha256) of a file at the pinned acq commit; (None, None) when absent there."""
    try:
        b = subprocess.run(["git", "-C", ROOT, "show", f"{ACQ_COMMIT}:{path}"], capture_output=True, check=True).stdout
    except subprocess.CalledProcessError:
        return None, None
    return json.loads(b.decode("utf-8")), hashlib.sha256(b).hexdigest()


def _ids(*vals):
    pm, nc = set(), set()
    for v in vals:
        s = json.dumps(v) if not isinstance(v, str) else v
        nc.update(x.upper() for x in NCT.findall(s))
        pm.update(x for x in PMID.findall(re.sub(r"NCT\d{8}", " ", s, flags=re.I)))
    return pm, nc


def trial_ids(t, chain, ktab):
    """PMIDs / NCTs naming this comparator trial, each with where it came from."""
    src = {}

    def add(kind, vals):
        pm, nc = _ids(vals)
        for x in pm | nc:
            src.setdefault(x, set()).add(kind)
    add("tracker.family", t.get("family") or "")
    sf = t.get("seeded_funnel") or {}
    add("tracker.seeded_funnel", [sf.get("pmid") or "", sf.get("nct") or ""])
    add("tracker.registry_binding", (t.get("registry_binding") or {}).get("nct") or "")
    c = chain.get(t["label"]) or {}
    if c.get("state") == "RESOLVED":
        add("identity_chain", [c.get("pmid") or "", c.get("nct") or ""])
    for k in ktab.get(t["label"], []):
        add("k_gap_table", [k.get("pmids") or [], k.get("ncts") or []])
    pm = sorted(x for x in src if not x.startswith("NCT"))
    nc = sorted(x for x in src if x.startswith("NCT"))
    return pm, nc, {k: sorted(v) for k, v in src.items()}


def _stage(rec):
    s = " ".join(str(rec.get(k) or "") for k in ("reason", "span", "rule_id"))
    return "FULL_TEXT" if re.search(r"full[ -]?text", s, re.I) else "TITLE_ABSTRACT"


def topic(slug, acq_meta):
    g = _j(os.path.join(ROOT, "outputs", "k_gap", "g1", f"{slug}.json"))
    rec = _j(os.path.join(ROOT, "cache", slug, "records.json"))
    rev_p = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
    rev = _j(rev_p) if os.path.exists(rev_p) else {}
    chain_all = _j(os.path.join(ROOT, "outputs", "k_gap", "identity_chain.json")).get("results", {})
    chain = {k.split("::", 1)[1]: v for k, v in chain_all.items() if k.startswith(slug + "::")}
    ktab = collections.defaultdict(list)
    for k in acq_meta["k_gap_table"].get("trials", []):
        if k.get("slug") == slug:
            ktab[k.get("label")].append(k)
    retrieved = {str(r["id"]).upper() if str(r["id"]).upper().startswith("NCT") else str(r["id"])
                 for r in (rec.get("records") or []) + (rec.get("ctgov") or [])}
    screened = {str(r["id"]).upper() if str(r["id"]).upper().startswith("NCT") else str(r["id"]): r
                for r in (rev.get("screening") or {}).get("records") or []}
    fam_of = {}                                   # any id -> every id of its trial family (all reports + registrations)
    for f in rev.get("trial_families") or []:
        a = f.get("aliases") or {}
        ids = {str(x).upper() if str(x).upper().startswith("NCT") else str(x)
               for x in (a.get("report_ids") or []) + (a.get("registry_ids") or []) + [f.get("family_id")]
               + [r.get("report_id") for r in f.get("reports") or []] if x}
        for x in ids:
            fam_of.setdefault(x, set()).update(ids)
    sm = acq_meta["secondary_meta"].get(slug) or {}
    comp = str(g.get("comparator_pmid") or sm.get("comparator_pmid") or "")
    other_meta = collections.defaultdict(set)
    for r in sm.get("rows") or []:
        if str(r.get("meta_pmid")) != comp and r.get("family_id"):
            for x in _ids(r["family_id"])[0] | _ids(r["family_id"])[1]:
                other_meta[x].add(str(r["meta_pmid"]))
    named = {d["trial"]: d for d in g.get("named_differences") or []}
    probe = (acq_meta.get("probe") or {}).get(slug) or {}
    rrl = (acq_meta.get("rrl") or {}).get(slug) or {}
    rrl_ids = {i for src in rrl.get("sources") or [] for i in src.get("ids") or []}
    # the comparator's OWN backward lists contain its trials by construction: as a recall MEASURE against that comparator
    # they are circular (a legitimate identification source, never independent evidence that our identification works)
    rrl_indep = {i for src in rrl.get("sources") or [] if src.get("kind") not in ("COMPARATOR_REFERENCES",
                                                                                   "COMPARATOR_REFERENCE_LIST")
                 for i in src.get("ids") or []}
    rows = []
    for t in g["trials"]:
        pm, nc, src = trial_ids(t, chain, ktab)
        nd = named.get(t["label"])
        kind = ("ELIGIBLE" if not nd else "SCREEN_NAMED" if (nd.get("rule_id") in SCREEN_RULES) else "NAMED_OTHER")
        own = set(pm) | set(nc)
        fam = set().union(*(fam_of.get(x, {x}) for x in own)) if own else set()
        hit_own = sorted(own & retrieved)
        hit_fam = sorted((fam - own) & retrieved)
        search = ("IDENTIFIED" if hit_own else "IDENTIFIED_VIA_OTHER_REPORT" if hit_fam else
                  "IDENTITY_UNRESOLVED" if not own else "NOT_IDENTIFIED")
        dec = [dict(screened[x], record=x) for x in sorted((own | fam) & set(screened))]
        inc = [d for d in dec if d.get("decision") == "include"]
        screen = ("NOT_SCREENED" if not dec else "INCLUDED" if inc else "EXCLUDED")
        exc = None if inc or not dec else dec[0]
        om = sorted(set().union(*(other_meta.get(x, set()) for x in own | fam))) if own else []
        p = probe.get(t["label"]) or {}
        rrl_hit = sorted(own & rrl_ids) if own else []
        rrl_ind = sorted(own & rrl_indep) if own else []
        # FIXED identification (counterfactual, from recorded probes): what the harness as fixed on this branch would
        # identify -- the registered search, plus the standing REVIEW_REFERENCE_LIST route, plus a record the registered
        # query matches that the capped legacy retrieval did not retain (CT.gov pagination / uncapped PubMed)
        fixed = (search.startswith("IDENTIFIED") or bool(rrl_hit) or p.get("miss_type") == "RETRIEVED_NOT_RETAINED")
        fixed_ind = (search.startswith("IDENTIFIED") or bool(rrl_ind) or p.get("miss_type") == "RETRIEVED_NOT_RETAINED")
        miss = None
        if search == "IDENTITY_UNRESOLVED":
            miss = "IDENTITY_FAILURE"
        elif search == "NOT_IDENTIFIED":
            miss = p.get("miss_type") or "PROBE_PENDING"
        rows.append({
            "label": t["label"], "kind": kind, "named": ({k: nd.get(k) for k in ("kind", "rule_id", "screen_reason")}
                                                         if nd else None),
            "pmids": pm, "ncts": nc, "id_sources": src,
            "search": search, "search_hit": hit_own or hit_fam,
            "rrl": {"comparator_list": True, "other_metas": om, "standing_route_hit": rrl_hit,
                    "independent_hit": rrl_ind},
            "identified_fixed": fixed, "identified_fixed_independent": fixed_ind,
            "identified_any": search.startswith("IDENTIFIED") or bool(om),
            "screen": screen,
            "screen_exclusion": ({"record": exc["record"], "rule_id": exc.get("rule_id"), "reason": exc.get("reason"),
                                  "span": exc.get("span"), "stage": _stage(exc),
                                  "adjudicator": exc.get("adjudicator_state")} if exc else None),
            "screen_include": ({"record": inc[0]["record"], "stage": _stage(inc[0])} if inc else None),
            "miss_type": miss, "probe": p or None,
            "tracker_gap_class": t.get("gap_class"), "tracker_identification": (t.get("identification") or {}).get("route")
            or ("REVIEW_REFERENCE_LIST" if t.get("identification") else None)})
    el = [r for r in rows if r["kind"] == "ELIGIBLE"]
    found = [r for r in el if r["search"].startswith("IDENTIFIED")]
    s_in = [r for r in found if r["screen"] == "INCLUDED"]
    return {
        "slug": slug, "comparator_pmid": comp, "search_run_utc": rec.get("fetched_utc"),
        "registered_queries": {"pubmed": rec.get("pubmed_queries"), "ctgov": rec.get("ctgov_query")},
        "n_retrieved": len(retrieved), "N_comparator": len(rows), "N_eligible": len(el),
        "N_eligible_tracker": g.get("N_eligible"),
        "search_recall": {"n": len(found), "N": len(el)},
        "search_or_rrl_other_recall": {"n": sum(1 for r in el if r["identified_any"]), "N": len(el)},
        "screen_recall": {"n": len(s_in), "N": len(found)},
        "fixed_identification_recall": {"n": sum(1 for r in el if r["identified_fixed"]), "N": len(el)},
        "rrl_standing_recall": {"n": sum(1 for r in el if r["rrl"]["standing_route_hit"]), "N": len(el)},
        "fixed_identification_recall_independent": {"n": sum(1 for r in el if r["identified_fixed_independent"]),
                                                     "N": len(el)},
        "reference_list_metas": rrl.get("reference_list_metas"),
        "miss_types": dict(collections.Counter(r["miss_type"] for r in el if r["miss_type"])),
        "screen_exclusions_of_eligible": [r["label"] for r in found if r["screen"] == "EXCLUDED"],
        "screen_named_to_recheck": [r["label"] for r in rows if r["kind"] == "SCREEN_NAMED"],
        "trials": rows}


def load_acq():
    kt, kt_sha = _pinned("outputs/k_gap/k_gap_table.json")
    sm, shas = {}, {}
    for f in sorted(os.listdir(os.path.join(ROOT, "outputs", "k_gap", "g1"))):
        s = f[:-5]
        d, h = _pinned(f"registry/secondary_meta/{s}.json")
        if d:
            sm[s], shas[s] = d, h
    pp = os.path.join(OUT, "search_miss_probe.json")
    probe = _j(pp).get("topics", {}) if os.path.exists(pp) else {}
    rp = os.path.join(OUT, "rrl_probe.json")
    rrl = _j(rp).get("topics", {}) if os.path.exists(rp) else {}
    return {"k_gap_table": kt or {}, "secondary_meta": sm, "probe": probe, "rrl": rrl,
            "pins": {"acq_commit": ACQ_COMMIT, "k_gap_table_sha256": kt_sha, "secondary_meta_sha256": shas}}


def main(argv):
    os.makedirs(OUT, exist_ok=True)
    acq = load_acq()
    slugs = argv or sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, "outputs", "k_gap", "g1")) if f.endswith(".json"))
    topics = [topic(s, acq) for s in slugs]
    tot = lambda k: {"n": sum(t[k]["n"] for t in topics), "N": sum(t[k]["N"] for t in topics)}  # noqa: E731
    # denominator check: the eligible count must equal the tracker's own N_eligible, topic by topic
    bad = [t["slug"] for t in topics if t["N_eligible"] != t["N_eligible_tracker"]]
    out = {"schema": 1, "inputs": {"tracker": "outputs/k_gap/g1/*.json", **acq["pins"]},
           "kinds": {k: sum(1 for t in topics for r in t["trials"] if r["kind"] == k)
                     for k in ("ELIGIBLE", "SCREEN_NAMED", "NAMED_OTHER")},
           "denominator_mismatch": bad,
           "totals": {"topics": len(topics), "N_comparator": sum(t["N_comparator"] for t in topics),
                      "search_recall": tot("search_recall"), "search_or_rrl_other_recall": tot("search_or_rrl_other_recall"),
                      "screen_recall": tot("screen_recall"),
                      "rrl_standing_recall": tot("rrl_standing_recall"),
                      "fixed_identification_recall": tot("fixed_identification_recall"),
                      "fixed_identification_recall_independent": tot("fixed_identification_recall_independent"),
                      "miss_types": dict(sum((collections.Counter(t["miss_types"]) for t in topics), collections.Counter()))},
           "topics": topics}
    json.dump(out, open(os.path.join(OUT, "SEARCH_SCREEN_AUDIT.json"), "w", encoding="utf-8", newline="\n"),
              indent=1, ensure_ascii=False)
    open(os.path.join(OUT, "SEARCH_SCREEN_AUDIT.md"), "w", encoding="utf-8", newline="\n").write(render(out))
    print(json.dumps({k: out[k] for k in ("kinds", "denominator_mismatch", "totals")}, indent=1))
    return 1 if bad else 0


def render(o):
    L = ["# Search + screen recall audit (G1, 32 topics)", "",
         f"Inputs: tracker outputs/k_gap/g1 (this branch), acq/k-gap pinned {ACQ_COMMIT[:10]}. Kinds of comparator "
         f"trial: {o['kinds']}. Eligible-set mismatch vs tracker: {o['denominator_mismatch'] or 'none'}.", "",
         f"**Totals:** search recall {o['totals']['search_recall']['n']} of {o['totals']['search_recall']['N']}; "
         f"search or another meta's reference list {o['totals']['search_or_rrl_other_recall']['n']} of "
         f"{o['totals']['search_or_rrl_other_recall']['N']}; screen recall {o['totals']['screen_recall']['n']} of "
         f"{o['totals']['screen_recall']['N']} (of eligible trials our search identified). Miss types: "
         f"{o['totals']['miss_types']}.", "",
         f"**After the class fixes on this branch** (counterfactual, from the recorded probes): the standing "
         f"REVIEW_REFERENCE_LIST route alone identifies {o['totals']['rrl_standing_recall']['n']} of "
         f"{o['totals']['rrl_standing_recall']['N']}; registered search + that route + uncapped retrieval identify "
         f"{o['totals']['fixed_identification_recall']['n']} of {o['totals']['fixed_identification_recall']['N']}. "
         f"**Circular part stated:** the comparator's own reference list contains its trials by construction, so as a "
         f"recall measure against that comparator it proves nothing; without the comparator's backward lists (other "
         f"metas + forward citation only) the fixed identification is "
         f"{o['totals']['fixed_identification_recall_independent']['n']} of "
         f"{o['totals']['fixed_identification_recall_independent']['N']}.", "",
         "| Topic | Eligible | Search n/N | +other metas | RRL route | Fixed ident. | Screen n/N | Misses | Screen-named to recheck |",
         "|---|---|---|---|---|---|---|---|---|"]
    for t in o["topics"]:
        L.append(f"| {t['slug']} | {t['N_eligible']} | {t['search_recall']['n']}/{t['search_recall']['N']} | "
                 f"{t['search_or_rrl_other_recall']['n']}/{t['search_or_rrl_other_recall']['N']} | "
                 f"{t['rrl_standing_recall']['n']}/{t['rrl_standing_recall']['N']} | "
                 f"{t['fixed_identification_recall']['n']}/{t['fixed_identification_recall']['N']} | "
                 f"{t['screen_recall']['n']}/{t['screen_recall']['N']} | "
                 f"{', '.join(f'{k} {v}' for k, v in t['miss_types'].items()) or '-'} | {len(t['screen_named_to_recheck'])} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
