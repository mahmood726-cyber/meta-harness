"""Resolve a G1 DIFFERENT_CONCLUSION, trial by trial: whose number is right (spans), whether each difference is a
population / design / analysis-set / timepoint scope difference or an error on one side, and whether the comparator's
conclusion survives on the shared trials.

    python scripts/g1_reconcile.py SLUG   -> outputs/k_gap/g1_reconcile/<slug>.json and .md (its own directory: every
    reader of outputs/k_gap/g1/*.json takes each file there as a tracker row)

Reads only what the harness already holds and derives: outputs/k_gap/g1/<slug>.json (scripts/g1_tracker.py),
outputs/k_gap/exclusion_audit.json (scripts/k_gap_exclusion_audit.py), cache/<slug>/records.json (held abstracts),
harness/analysis_set.py. Pools with the tracker's own pooler and verdict (scripts/g1_tracker.same_trials_pool,
result_verdict), method = the one the tracker reproduced the comparator with. No number is typed in by hand: every
row is a comparator printed row, a served row, or counts read from a quoted span.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
OUT = os.path.join(ROOT, "outputs", "k_gap")

import g1_tracker as gt  # noqa: E402
from harness import analysis_set  # noqa: E402
from harness import secondary_meta as sm  # noqa: E402
RECON_DIR = os.path.join(OUT, "g1_reconcile")
ANALYSIS_SET_DIFFERENCE = "ANALYSIS_SET_DIFFERENCE"
UNREPRODUCED_NEAREST_SET = "COMPARATOR_ROW_UNREPRODUCED:NEAREST_HELD_SET_NAMED"
SET_CLASSES = (ANALYSIS_SET_DIFFERENCE, UNREPRODUCED_NEAREST_SET)


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _pid(x):
    return str(x.get("family") or "").replace("PMID ", "").strip() or None


def _sentence_with(text, term):
    for s in re.split(r"(?<=[.;])\s+(?=[A-Z])", re.sub(r"\s+", " ", text or "")):
        if term and term.lower() in s.lower():
            return s[:300]
    return None


def analysis_set_open_span(body):
    """The full text's own design self-description, quoted (the audit's OPEN_DESIGN_SELF)."""
    import k_gap_exclusion_audit as ea
    m = ea.OPEN_DESIGN_SELF.search(body)
    if not m:
        return None
    s = body.rfind(".", 0, m.start()) + 1
    e = body.find(".", m.end())
    return body[s:e + 1].strip()[:300]


def _counts_row(t, c, measure="RR"):
    return {"measure": measure, "effect": None, "lower": None, "upper": None, "events_t": t["events"], "n_t": t["n"],
            "events_c": c["events"], "n_c": c["n"]}


def _pool(rows, method_label):
    """One side's rows pooled by the tracker's method; None when fewer than 2 or a row is not poolable."""
    rows = [gt.as_row(r, f"r{i}") for i, r in enumerate(rows) if r]
    if len(rows) < 2:
        return None
    yv = [sm.row_yi_vi(r) for r in rows]
    if any(v is None for v in yv):
        return None
    import math
    method, hk = method_label.replace("+HK", ""), method_label.endswith("+HK")
    mu, lo, hi = (math.exp(x) for x in sm.pool([v[0] for v in yv], [v[1] for v in yv], method, hk))
    return {"k": len(rows), "estimate": round(mu, 4), "ci_low": round(lo, 4), "ci_high": round(hi, 4),
            "conclusion": "BENEFIT" if hi < 1 else "HARM" if lo > 1 else "NULL_INCLUDED"}


def reconcile(slug):
    g = _j(os.path.join(OUT, "g1", f"{slug}.json"))
    audit = {(r["slug"], r["pmid"]): r for r in _j(os.path.join(OUT, "exclusion_audit.json"))["rows"]}
    recs = {str(r.get("id")): r for r in _j(os.path.join(ROOT, "cache", slug, "records.json")).get("records", [])}
    cfg = _j(os.path.join(ROOT, "topics", slug + ".json"))
    inc = cfg.get("include") or {}
    treat, ctrl = inc.get("intervention_any") or [], list(inc.get("comparator_any") or []) + list(inc.get("comparator_any_extra") or [])
    kw = (cfg.get("primary_outcome") or {}).get("keywords") or []
    method = (g.get("same_trials") or {}).get("method") or "FE"
    rows = []
    named = {d.get("trial"): d for d in g.get("named_differences") or []}
    for x in g["trials"]:
        pid = _pid(x)
        rec = recs.get(pid) or {}
        cr = x.get("comparator_row")
        row = {"trial": x["label"], "pmid": pid, "comparator_row": cr, "our_row": x.get("our_value"),
               "in_our_pool": x.get("in_our_pool")}
        a = audit.get((slug, pid)) if pid else None
        if a:
            # the class the TRACKER uses: the audit's, or the committed full-text pass's deterministic resolution
            cls_t, sub_t = gt.exclusion_audit_class(slug, pid)
            if (cls_t, sub_t) != (a["class"], a["subclass"]):
                a = dict(a, class_=a["class"], subclass_abstract=a["subclass"], **{"class": cls_t, "subclass": sub_t})
                ftp = os.path.join(OUT, "_ft", f"{pid}.txt")
                if os.path.exists(ftp):
                    import hashlib
                    body = open(ftp, encoding="utf-8").read()
                    row["fulltext_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
                    m = analysis_set_open_span(body)
                    if m:
                        row["fulltext_span"] = m
        if x.get("in_our_pool"):
            ag = str(x.get("agreement_with_comparator_row") or "")
            at = x.get("analysis_set_attribution") or {}
            if ag.startswith("AGREE"):
                row.update(cls="SAME_NUMBER", verdict="both sides hold the same result", basis=ag)
            elif ag.startswith("NOT_COMPARABLE"):
                # matched, but the comparator prints no per-trial row to compare (never a disagreement)
                row.update(cls="MATCHED_NO_COMPARATOR_ROW", verdict="matched; the comparator prints no per-trial row",
                           basis=ag)
            elif at.get("per_set"):
                per = {p["analysis_set"]: p for p in at["per_set"]}
                theirs = at.get("reproduced_by") or at.get("nearest")
                # the class says only what was SHOWN (NR-C20 #1): a held set that REPRODUCES the comparator's row is an
                # analysis-set difference; a row no held set reproduces has a NEAREST set, and its provenance stays open
                row.update(cls=ANALYSIS_SET_DIFFERENCE if at.get("state") == "REPRODUCED" else UNREPRODUCED_NEAREST_SET,
                           comparator_row_attribution=at.get("state"), nearest_set_to_comparator_row=theirs,
                           verdict=(f"both numbers are in the report: we pool the {at.get('ours')} counts (registered "
                                    f"estimand: {(cfg.get('primary_outcome') or {}).get('population')}); the comparator's row "
                                    + ("IS" if at.get("state") == "REPRODUCED" else "is nearest to, but is not reproduced by,")
                                    + f" the {theirs} analysis"),
                           ours_span=(per.get(at.get("ours")) or {}).get("span"), theirs_span=(per.get(theirs) or {}).get("span"),
                           per_set=at["per_set"], right_number_for_protocol=at.get("ours"))
            else:
                row.update(cls="DISAGREE_UNATTRIBUTED", verdict="no held analysis set explains the comparator row", basis=ag)
        elif (x.get("scope_difference") or {}).get("kind") == "NOT_AN_INCLUDED_TRIAL":
            d = x["scope_difference"]
            row.update(cls="NOT_AN_INCLUDED_TRIAL", verdict=("a reference of the comparator, not one of its trials: " + d["basis"]),
                       stating_span=d["span"]["text"], comparator_span=d["comparator_span"]["text"])
        elif a:
            term = (re.search(r"'([^']+)'", a["subclass"]) or [None, None])[1]
            row.update(cls=f"{a['class']}:{a['subclass'].split(' (')[0].split(':')[0]}", audit=a,
                       stating_span=_sentence_with((rec.get("title") or "") + ". " + (rec.get("abstract") or ""),
                                                   term or ("open-label" if "OPEN_LABEL" in a["subclass"] else None)))
            if a["class"] == "TRUE_SCOPE_DIFFERENCE":
                # the tracker's named difference carries the span it VERIFIED (a full-text span with its body's sha256):
                # use it, so a clone without the gitignored body never rewrites "the full text states it" as "the record"
                nsp = (named.get(x["label"]) or {}).get("span") or {}
                if not row.get("fulltext_span") and nsp.get("field") == "fulltext":
                    row["fulltext_span"] = nsp.get("text")
                    row["fulltext_sha256"] = nsp.get("fulltext_sha256")
                if row.get("fulltext_span"):
                    row["stating_span"] = row["fulltext_span"]
                    row["verdict"] = ("out of the registered protocol's scope; the held OA FULL TEXT states it (the abstract "
                                      "did not)")
                else:
                    row["verdict"] = "out of the registered protocol's scope; the record states it"
            elif a["class"] == "INSUFFICIENT_RECORD":
                bc = analysis_set.percent_back_calculation(rec.get("abstract") or "", treat, ctrl, kw + ["AF"])
                row["verdict"] = "the held record does not state the fact the protocol needs; full text required"
                if bc and bc.get("treatment"):
                    rr = analysis_set.rr_ci(bc["treatment"]["events"], bc["treatment"]["n"], bc["control"]["events"], bc["control"]["n"])
                    row["back_calculated_counts"] = bc
                    row["back_calculated_rr"] = [round(v, 4) for v in rr]
                    row["comparator_row_reproduced_from_counts"] = bool(cr and all(
                        analysis_set._same_at_printed(v, cr[k]) for v, k in zip(rr, ("effect", "lower", "upper"))))
            elif a["class"] == "SCREENER_ERROR":
                bc = analysis_set.percent_back_calculation(rec.get("abstract") or "", treat, ctrl, kw)
                row["verdict"] = ("our screen is wrong: the record is a randomised report of an eligible trial; its result "
                                  + ("is extractable from the held abstract" if bc and bc.get("treatment") else
                                     "is NOT extractable from the held abstract (percentages only, arm sizes not stated): "
                                     "full text required"))
            if "comparator_row_reproduced_from_counts" not in row and rec.get("abstract") and cr:
                # whatever the class: do the comparator's printed row and the counts our held text implies agree?
                bc = analysis_set.percent_back_calculation(rec["abstract"], treat, ctrl, kw + ["AF"])
                if bc and bc.get("treatment"):
                    rr = analysis_set.rr_ci(bc["treatment"]["events"], bc["treatment"]["n"], bc["control"]["events"],
                                            bc["control"]["n"])
                    row["back_calculated_counts"] = bc
                    row["back_calculated_rr"] = [round(v, 4) for v in rr]
                    row["comparator_row_reproduced_from_counts"] = all(
                        analysis_set._same_at_printed(v, cr[k]) for v, k in zip(rr, ("effect", "lower", "upper")))
        elif x.get("blocker") == "IDENTITY_UNRESOLVED":
            cited = CITED_OUTSIDE_SOURCES.get((slug, x["label"]))
            if cited and cited_reference_holds(cited):
                # identity resolved by the COMPARATOR'S OWN reference, verbatim in its held JATS; the trial is in a
                # journal none of the registered sources indexes -- an eligible open gap with a precise blocker, never
                # a scope difference (being unfindable is not an eligibility criterion)
                row.update(cls="NOT_IN_REGISTERED_SOURCES", cited_reference=cited,
                           verdict=("identified by the comparator's own reference list; not indexed in PubMed or Europe "
                                    "PMC, so outside the registered search sources: stays ELIGIBLE and open"),
                           searches=IDENTITY_SEARCHES.get((slug, x["label"])))
            else:
                row.update(cls="IDENTITY_UNRESOLVED", verdict="the comparator's label resolves to no held record",
                           searches=IDENTITY_SEARCHES.get((slug, x["label"])))
        else:
            row.update(cls=x.get("blocker") or "UNCLASSIFIED")
        rows.append(row)

    # --- does the comparator's conclusion survive?
    def theirs(r):
        return r["comparator_row"]
    shared = [r for r in rows if r["in_our_pool"] and r["comparator_row"]]
    scope_out = [r for r in rows if str(r.get("cls", "")).startswith("TRUE_SCOPE_DIFFERENCE")]
    in_scope = [r for r in rows if r not in scope_out and r["comparator_row"]]

    def _set_row(r, name):
        p = next(p for p in r["per_set"] if p["analysis_set"] == name)
        return {"measure": "RR", "effect": f"{p['rr']}", "lower": f"{p['ci'][0]}", "upper": f"{p['ci'][1]}"}

    def ours_or_itt(r):
        if r.get("cls") in SET_CLASSES:
            return _set_row(r, r["right_number_for_protocol"])
        return r["our_row"] if r["in_our_pool"] else r["comparator_row"]

    def nearest_set(r):
        # the held set NEAREST the comparator's row (or reproducing it) -- a sensitivity scenario, never the comparator's
        # established analysis set unless it reproduces the row
        if r.get("cls") in SET_CLASSES:
            return _set_row(r, r["nearest_set_to_comparator_row"])
        return r["our_row"]

    scen = {
        "A_shared_trials_comparator_rows": _pool([theirs(r) for r in shared], method),
        "B_shared_trials_our_rows_ITT": _pool([r["our_row"] for r in shared], method),
        "C_shared_trials_held_set_nearest_the_comparator_row": _pool([nearest_set(r) for r in shared], method),
        "D_comparator_rows_all_printed": _pool([theirs(r) for r in rows if r["comparator_row"]], method),
        "E_comparator_rows_protocol_scope_only": _pool([theirs(r) for r in in_scope], method),
        "F_protocol_scope_only_with_ITT_where_held": _pool([ours_or_itt(r) for r in in_scope], method),
    }
    members = {"A": shared, "B": shared, "C": shared, "D": [r for r in rows if r["comparator_row"]], "E": in_scope,
               "F": in_scope}
    for k, v in scen.items():
        if v:
            v["trials"] = [r["trial"] for r in members[k[0]]]
            # rows that are ONLY the comparator's own printed row (no held source reproduces them): never verification
            v["comparator_only_rows"] = [r["trial"] for r in members[k[0]] if not r["in_our_pool"]
                                         and not r.get("comparator_row_reproduced_from_counts")
                                         and (k[0] in ("D", "E") or not r["in_our_pool"])]
    aset = next((r["trial"] for r in rows if r.get("cls") in SET_CLASSES), None)
    surv = {
        "comparator_published": g.get("comparator"),
        "method": method,
        # no poolable shared rows on either side is NOT a survival (None == None): it is not testable on rows
        "on_shared_trials": ("NOT_TESTABLE_ON_SHARED_ROWS" if not (scen["A_shared_trials_comparator_rows"]
                                                                    and scen["B_shared_trials_our_rows_ITT"])
                             else "SURVIVES" if (scen["B_shared_trials_our_rows_ITT"] or {}).get("conclusion") ==
                             (scen["A_shared_trials_comparator_rows"] or {}).get("conclusion") else "DOES_NOT_SURVIVE"),
        "why": f"the shared-trial benefit depends on which analysis set of the {aset} report is pooled"
        if (scen["C_shared_trials_held_set_nearest_the_comparator_row"] or {}).get("conclusion") ==
        (scen["A_shared_trials_comparator_rows"] or {}).get("conclusion") != (scen["B_shared_trials_our_rows_ITT"] or {}).get("conclusion")
        else None,
    }
    if (g.get("same_trials") or {}).get("state") == "WHOLE_POOL_MEASURE_DIFFERS":
        # same trials, different measures: decide what IS decidable without arm sizes (harness/event_total_check.py)
        from harness import comparator_membership as cmb, event_total_check as etc
        crec = recs.get(str(g.get("comparator_pmid"))) or {}
        st = cmb.stated_trial_count(crec.get("abstract") or "")
        matched = [r["pmid"] for r in rows if r["in_our_pool"] and r["pmid"]]
        surv["whole_pool"] = {"ours": g.get("ours"), "theirs": g.get("comparator"), "same_trials": g.get("same_trials"),
                              "event_total_check": etc.check(crec.get("abstract") or "",
                                                             [(cfg.get("comparator_outcomes") or [{}])[0].get("name") or ""] + kw,
                                                             (st or {}).get("n_patients"),
                                                             {p: (recs.get(p) or {}).get("abstract") or "" for p in matched})}
    return {"slug": slug, "comparator_pmid": g.get("comparator_pmid"), "trials": rows, "scenarios": scen,
            "comparator_conclusion": surv, "n_comparator_trials": len(rows),
            "classes": {c: sum(1 for r in rows if r.get("cls") == c) for c in sorted({r.get("cls") for r in rows})}}


# identity searches done for labels that resolve to no record (recorded, so the gap is not silent)
IDENTITY_SEARCHES = {
    ("colchicine-postop-af", "Sarzaeem [23]"): [
        {"source": "PubMed (NCBI E-utilities via the session's PubMed tool)", "when": "2026-10-02",
         "query": "Sarzaeem[Author] AND colchicine", "hits": 0},
        {"source": "PubMed", "when": "2026-10-02",
         "query": "colchicine atrial fibrillation coronary artery bypass Iran randomized 2014", "hits": 0},
        {"source": "Europe PMC REST search", "when": "2026-10-03",
         "query": 'TITLE:"Low dose Colchicine in prevention of atrial fibrillation after coronary artery bypass graft"',
         "hits": 0},
        {"source": "Europe PMC REST search", "when": "2026-10-03", "query": 'AUTH:"Sarzaeem M" AND colchicine', "hits": 0},
        {"source": "Europe PMC REST search", "when": "2026-10-03", "query": 'JOURNAL:"Tehran Univ Med J" AND colchicine',
         "hits": 0}],
}

# a comparator label resolved by the comparator's OWN reference entry (its JATS, committed on acq/k-gap), when the cited
# journal is outside the registered sources; the entry is re-read and must hold verbatim (cited_reference_holds)
CITED_OUTSIDE_SOURCES = {
    ("colchicine-postop-af", "Sarzaeem [23]"): {
        "jats": "cache/comparators/36050741/2026-09-30_kgap_jats.xml", "git_blob": "d2ba96473500b49a9276767d18a59fcb3c93ca51",
        "ref_id": "CR23", "must_contain": ["Sarzaeem", "Low dose Colchicine in prevention of atrial fibrillation after "
                                            "coronary artery bypass graft", "Tehran Univ Med J", "2014"],
        "citation": ("Sarzaeem M, Shayan N, Bagheri J, Jebelli M, Mandegar M. Low dose Colchicine in prevention of atrial "
                     "fibrillation after coronary artery bypass graft: a double blind clinical trial. Tehran Univ Med J "
                     "2014;72:147-154")},
}


def cited_reference_holds(c):
    """The comparator's reference entry, read from the pinned JATS blob, contains every required string."""
    import subprocess
    try:
        x = subprocess.run(["git", "cat-file", "-p", c["git_blob"]], cwd=ROOT, capture_output=True, check=True,
                           stdin=subprocess.DEVNULL).stdout.decode("utf-8")
    except subprocess.CalledProcessError:
        return False
    m = re.search(r'<ref id="' + re.escape(c["ref_id"]) + r'">.*?</ref>', x, re.S)
    entry = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(0))) if m else ""
    return bool(entry) and all(t in entry for t in c["must_contain"])


def to_md(r):
    L = [f"# G1 reconciliation: {r['slug']} (comparator PMID {r['comparator_pmid']})", "",
         "Every number is a comparator printed row, a served row, or counts read from a quoted span "
         "(scripts/g1_reconcile.py).", "", "| comparator trial | class | verdict | comparator row | ours | span |",
         "|---|---|---|---|---|---|"]
    for t in r["trials"]:
        cr = t.get("comparator_row") or {}
        ours = t.get("our_row") or {}
        span = t.get("ours_span") or t.get("stating_span") or ""
        L.append(f"| {t['trial']} (PMID {t.get('pmid')}) | {t.get('cls')} | {t.get('verdict', '')} | "
                 f"{cr.get('measure', '')} {cr.get('effect', '')} ({cr.get('lower', '')}-{cr.get('upper', '')}) | "
                 f"{ours.get('events_t', '')}/{ours.get('n_t', '')} vs {ours.get('events_c', '')}/{ours.get('n_c', '')} | "
                 f"{span[:160].replace('|', '/')} |")
    L += ["", "## Does the comparator's conclusion survive?", "",
          f"Method: {r['comparator_conclusion']['method']} (the tracker reproduced the comparator with it).", "",
          "| scenario | trials | RR (95% CI) | conclusion | provenance |", "|---|---|---|---|---|"]
    for k, v in r["scenarios"].items():
        if v:
            co = v.get("comparator_only_rows") or []
            L.append(f"| {k} | {', '.join(v.get('trials', []))} | {v['estimate']} ({v['ci_low']}-{v['ci_high']}) | "
                     f"{v['conclusion']} |" + (f" comparator-only (unverified) rows: {', '.join(co)} |" if co else " |"))
        else:
            L.append(f"| {k} | - | fewer than 2 poolable rows | - |")
    s = r["comparator_conclusion"]
    L += ["", f"**On the shared trials: {s['on_shared_trials']}.** {s.get('why') or ''}"]
    wp = s.get("whole_pool")
    if wp:
        ec = wp["event_total_check"]
        L += ["", "## Whole pools (the same trials, different measures)", "",
              f"- ours: {wp['ours']}", f"- comparator: {wp['theirs']}", f"- {wp['same_trials'].get('state')}",
              f"- event-total check: **{ec['state']}** -- {ec.get('basis') or ''}",
              f"  - comparator: \"{(ec.get('comparator_rates') or {}).get('span')}\""]
        for pmid, v in (ec.get("per_trial") or {}).items():
            L.append(f"  - PMID {pmid}: {v['events']} -- \"{v['span'][:220]}\"")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    slug = sys.argv[1]
    res = reconcile(slug)
    os.makedirs(RECON_DIR, exist_ok=True)
    with open(os.path.join(RECON_DIR, f"{slug}.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
    md = to_md(res)
    with open(os.path.join(RECON_DIR, f"{slug}.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(md)
    print(md)
