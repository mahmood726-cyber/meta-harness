"""G1 tracker entry for sglt2-hfref-hosp-cvdeath (comparator PMID 35112512, LVEF <=40% pool HR 0.74 (0.68-0.81)), as an
OVERLAY on the shared scripts/g1_tracker.topic() (imported, not edited). The shared entry is kept whole; this lane adds
what the shared tracker cannot see yet, each with its basis:

  comparator rows   the comparator prints its LVEF <=40% rows only in Figure 2A. scripts/g1_sglt2_forest.py reads it with
                    TWO independent recorded readers, each gated on its own (G5: the rows recompute the triple printed
                    in the comparator's text). A row is ADMITTED only when both gated readers print it digit for digit;
                    a row the readers differ on carries both readings and is compared under each.
  SOLOIST-WHF       no registration in the comparator's table and an empty AACT acronym; bound to NCT03521934 by the
                    AACT title ('... (SOLOIST-WHF Trial)') AND enrollment 1222 = the comparator's n (two attributes), and
                    its own report (PMID 33200892, retrieved by NCT03521934[si]) is seeded through OUR screen
  EMPEROR-Preserved the shared tracker seeds only a trial's first listed PMID (its design paper, which our screen saw via
                    another report); the trial's own report (PMID 34449189) is seeded here and its screen verdict cited

  python scripts/g1_sglt2_tracker.py   -> outputs/k_gap/g1/sglt2-hfref-hosp-cvdeath.json, then g1_tracker.py --table
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402
from harness import secondary_meta as sm  # noqa: E402

SLUG = "sglt2-hfref-hosp-cvdeath"
FOREST = os.path.join(ROOT, "g1", "data", "sglt2_hfref_forest.json")
SOLOIST_XML = os.path.join(ROOT, "g1", "data", "sglt2", "_soloist_pubmed.xml")
AACT_SOLOIST = os.path.join(ROOT, "g1", "data", "sglt2", "aact_soloist.json")   # every snapshot row naming SOLOIST


def bind_identity(label, n, rows, acronym_only=False):
    """A comparator label with no registration, bound in the AACT snapshot on TWO attributes: the label in the
    registered title AND enrollment == the comparator's n. acronym_only (the plant) binds on the acronym field alone."""
    lab = norm(label)
    if acronym_only:
        return [r["nct_id"] for r in rows if (r.get("acronym") or "").upper() and lab.startswith(r["acronym"].upper())]
    return [r["nct_id"] for r in rows
            if lab in norm((r.get("brief_title") or "") + " " + (r.get("official_title") or ""))
            and str(r.get("enrollment")) == str(n)]


def identities():
    rows = json.load(open(AACT_SOLOIST, encoding="utf-8"))["rows"]
    hit = bind_identity("SOLOIST-WHF", 1222, rows)
    if len(hit) != 1:
        raise SystemExit(f"REFUSED: SOLOIST-WHF binds {hit} (need exactly one)")
    return {"SOLOIST": {"nct": hit[0], "pmid": "33200892",
                        "basis": "AACT 2026-08-30: the label in the registered title AND enrollment 1222 = comparator "
                                 "Table 1 n; AACT acronym empty (acronym-only binds " +
                                 ", ".join(bind_identity("SOLOIST-WHF", 1222, rows, acronym_only=True)) + ", unrelated); "
                                 "PMID 33200892 = the PubMed record retrieved by " + hit[0] + "[si] whose title is the "
                                 "trial's main report"},
            "EMPEROR-PRESERVED": {"nct": "NCT03057951", "pmid": "34449189", "basis": "comparator table registration"}}


AUDIT_FILE = os.path.join(ROOT, "outputs", "k_gap", "exclusion_audit.tracker.json")
AUDIT = ({(r["slug"], str(r["pmid"])): r for r in json.load(open(AUDIT_FILE, encoding="utf-8"))["rows"]}
         if os.path.exists(AUDIT_FILE) else {})


def norm(label):
    """'DAPA‐HF (n = 4744)', 'DAPA-HF †' -> 'DAPA-HF'."""
    s = re.sub(r"[‐-―−]", "-", label or "")
    s = re.sub(r"\(n\s*=\s*[\d ,]+\)|[†‡§*]", "", s)
    return re.sub(r"\s+", " ", s).strip().upper()


def pubmed_record(pmid):
    x = open(SOLOIST_XML, encoding="utf-8").read()
    art = next(a for a in re.findall(r"<PubmedArticle>.*?</PubmedArticle>", x, re.S)
               if re.search(r"<PMID[^>]*>" + pmid + "<", a))
    t = lambda tag: re.sub(r"<[^>]+>", "", " ".join(re.findall(rf"<{tag}[^>]*>(.*?)</{tag}>", art, re.S)))  # noqa: E731
    return {"id": pmid, "id_type": "pmid", "title": t("ArticleTitle"), "abstract": t("AbstractText"),
            "journal": t("ISOAbbreviation"), "year": (re.search(r"<PubDate>.*?<Year>(\d{4})", art, re.S) or [None, None])[1],
            "nct": identities()["SOLOIST"]["nct"], "doi": (re.search(r'<ArticleId IdType="doi">([^<]+)', art) or [None, None])[1],
            "pubtypes": str(re.findall(r"<PublicationType[^>]*>([^<]+)", art))}


def admit(by, require_two=True):
    """A comparator row is ADMITTED only when both gated readers print it digit for digit (require_two=False: the plant)."""
    vals = list(by.values())
    if not require_two and vals:
        return "ADMITTED_TWO_READERS"
    return ("ADMITTED_TWO_READERS" if len(vals) == 2 and vals[0] == vals[1] else
            "READERS_DIFFER" if len(vals) == 2 else "ONE_READER")


def comparator_rows():
    f = json.load(open(FOREST, encoding="utf-8"))
    reads = {}
    for k in ("result", "result_reader2"):
        r = f.get(k) or {}
        if r.get("state") != "PASS":
            continue
        for row in r["gate"]["rows"]:
            reads.setdefault(norm(row["label"]), {})[k] = row["printed"]
    out = {}
    for lab, by in reads.items():
        out[lab] = {"readings": by, "readers": sorted(by), "state": admit(by)}
    return out, f


def as_their(printed, label):
    return sm.SecondaryRow(meta_pmid="35112512", meta_doi="", location={"figure": "2A"}, source_digest="",
                           provenance="FOREST_PLOT_MODEL_READ_RECOMPUTED", trial_label=label, measure="HR",
                           outcome_definition="CV death or first HF hospitalisation, LVEF <=40% subgroup",
                           effect=printed["effect"], lower=printed["lower"], upper=printed["upper"],
                           events_t=None, n_t=None, events_c=None, n_c=None)


def build():
    IDENTITY = identities()
    T = gt._j(os.path.join(gt.OUT, "k_gap_table.json"))
    o = gt.topic(SLUG, T)
    rows, forest = comparator_rows()
    # seed the trials' OWN reports through our build (in memory), exactly as the shared tracker seeds a first PMID
    import k_gap_counterfactual as cfm
    held = gt._j(os.path.join(gt.OUT, "member_records.json"))
    recs = [held[IDENTITY["EMPEROR-PRESERVED"]["pmid"]], pubmed_record(IDENTITY["SOLOIST"]["pmid"])]
    core = cfm.build(SLUG, extra_records=recs)
    fun = cfm.funnel(core, [r["id"] for r in recs], recs)
    cfg = gt._j(os.path.join(ROOT, "topics", SLUG + ".json"))
    scr = {r["id"]: r for r in core["screening"]["records"]}
    pairs = {"result": [], "result_reader2": []}
    for x in o["trials"]:
        key = norm(x["label"])
        idn = next((v for k, v in IDENTITY.items() if key.startswith(k)), None)
        if idn:
            p = idn["pmid"]
            f = dict(fun[p], pmid=p)
            if f["stage"] == "SCREENED_VIA_OTHER_REPORT" and f.get("via_decision") != "include":
                v = scr[f["via"]]
                f = dict(f, stage="SCREENED_OUT", rule_id=v.get("rule_id"), reason=(v.get("reason") or "")[:140])
            x["seeded_funnel"], x["identity"] = f, idn
            if not x.get("family") and idn["nct"]:
                x["family"] = idn["nct"]
            x["our_refusal"] = f"SEEDED PMID {p}: {f['stage']}" + (f" {f.get('rule_id')}: {f.get('reason')}"
                                                                   if f.get("rule_id") else "")
            x["scope_difference"] = gt.scope_difference(x, cfg)
            # the blocker as the shared tracker would compute it for this (now seeded) trial, then the tracker-population
            # exclusion audit (scripts/g1_exclusion_audit_tracker.py): a scope difference is NAMED only when that audit
            # classifies the excluded record TRUE_SCOPE_DIFFERENCE -- the shared gate's rule, applied to the audit that
            # covers this exclusion
            x["blocker"] = gt.blocker_class(x, SLUG)
            au = AUDIT.get((SLUG, p))
            if au and not x["scope_difference"]:
                if au["class"] == "TRUE_SCOPE_DIFFERENCE":
                    term = (re.search(r"mention '([^']+)'", f.get("reason") or "") or [None, None])[1]
                    x["scope_difference"] = {"kind": "PROTOCOL_SCOPE_DIFFERENCE", "rule_id": f.get("rule_id"),
                                             "screen_reason": f.get("reason"),
                                             "protocol_rule": gt.protocol_rule(cfg, term) if term else None,
                                             "registered_eligibility": cfg.get("eligibility_summary"), "pmid": p,
                                             "audit": {"class": au["class"], "subclass": au["subclass"],
                                                       "source": "outputs/k_gap/exclusion_audit.tracker.json"}}
                elif au["class"] in ("SCREENER_ERROR", "INSUFFICIENT_RECORD"):
                    x["blocker"] = f"{au['class']}:{au['subclass']}"
            if x["scope_difference"] and not x["scope_difference"].get("protocol_rule") and f.get("rule_id") == "X3":
                x["scope_difference"]["protocol_rule"] = ("include.intervention_any = " +
                                                          repr((cfg.get("include") or {}).get("intervention_any")))
            if x["scope_difference"] is None and x["route"] == "NO_ROW":
                x["basis"] = f"identity {idn['nct']} ({idn['basis'][:60]}...); {x['our_refusal']}"
        cr = rows.get(key)
        if cr:
            x["comparator_row_readings"] = cr
            if cr["state"] == "ADMITTED_TWO_READERS":
                x["comparator_row"] = dict(next(iter(cr["readings"].values())), measure="HR")
            if x["in_our_pool"]:
                ours = x["our_value"]
                ag = {k: gt.agreement(ours, as_their(v, x["label"])) for k, v in cr["readings"].items()}
                x["agreement_by_reader"] = ag
                x["agreement_with_comparator_row"] = (next(iter(ag.values())) if len(set(ag.values())) == 1
                                                      else "READERS_DIFFER:" + "/".join(f"{k}={v}" for k, v in sorted(ag.items())))
                for k, v in cr["readings"].items():
                    pairs[k].append((gt.as_row(ours, x["label"], "HR"), as_their(v, x["label"])))
    named = [{"trial": x["label"], **x["scope_difference"]} for x in o["trials"] if x.get("scope_difference")]
    o["named_differences"] = named
    o["open_gaps"] = [x["label"] for x in o["trials"] if not x["in_our_pool"] and not x.get("scope_difference")]
    o["N_eligible"] = len(o["trials"]) - len(named)
    o["per_trial_agreement"] = dict(gt.Counter(x["agreement_with_comparator_row"] for x in o["trials"] if x["in_our_pool"]))
    meth = [m for m in (forest["result"]["gate"].get("methods_reproducing") or [])
            if m in ((forest.get("result_reader2") or {}).get("gate") or {}).get("methods_reproducing", [])]
    method = meth[0] if meth else "FE"
    by_reader = {k: gt.same_trials_pool(v, method) for k, v in pairs.items() if v}
    st = by_reader.get("result") or {"state": "NO_COMPARATOR_ROWS"}
    st = dict(st, method_basis=f"a method under which BOTH gated readings reproduce the comparator's printed 0.74 "
                               f"(0.68-0.81): {meth}", by_reader=by_reader,
              readers_agree_on_verdict=len({json.dumps(v.get("verdict"), sort_keys=True) for v in by_reader.values()}) == 1)
    o["same_trials"] = st
    o["comparator_basis"] = (o.get("comparator_basis") or "") + "; LVEF <=40% subgroup rows: Figure 2A, two gated readers"
    o["lane"] = {"script": "scripts/g1_sglt2_tracker.py", "forest": "g1/data/sglt2_hfref_forest.json",
                 "forest_attempts": 1 + len(forest.get("earlier_attempts") or []),
                 "comparator_rows": rows}
    return o


def main():
    o = build()
    p = os.path.join(gt.G1_DIR, SLUG + ".json")
    open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(o, indent=1, ensure_ascii=False, default=str) + "\n")
    print("k matched", o["k_matched"], "of", o["N_eligible"], "eligible (N", o["N_comparator_trials"], ") named",
          [(d["trial"], d["kind"], d.get("rule_id")) for d in o["named_differences"]], "open", o["open_gaps"])
    print("per trial", o["per_trial_agreement"])
    for k, v in o["same_trials"]["by_reader"].items():
        print("same trials", k, v.get("state"), v.get("ours"), v.get("theirs"), v.get("verdict"))


if __name__ == "__main__":
    main()
