"""Audit every screening exclusion of a SEEDED comparator trial: each one is a claim that a published comparator
included something our protocol should not. Deterministic, in-memory, nothing written to cache/ or topics/.

Population: the k-gap table's confirmed-set IDENTIFICATION rows, seeded by scripts/k_gap_counterfactual.py --members
(its funnel, trial level), whose trial ended SCREENED_OUT or entered only through an excluded report of the same NCT.

Each exclusion is re-screened by the real rule set (harness.screen.screen_record) on the SAME record; the unmodified
call must reproduce the recorded rule, or the item is INCONSISTENT and not classified. Then:

  SCREENER_ERROR        the record flips to include under a transform that repairs a KNOWN screener class:
    CONDITION_AS_OUTCOME            population read from title+conditions+abstract, on a topic whose population
                                    term is its primary outcome (the trial names who it enrolled, not what it prevents)
    POPULATION_ONLY_IN_ABSTRACT     the same repair on a topic where the population is NOT the outcome
    COMPARATOR_WORDING              typographic dashes folded ('placebo‐controlled')
    INTERVENTION_ONLY_IN_ABSTRACT   the intervention read from the abstract, not only the title
  INSUFFICIENT_RECORD   no repair flips it and the record lacks the fact the rule needs (no abstract; no
                        randomisation statement; no comparator named; no blinding statement; population term absent
                        from title, conditions AND abstract) -> needs the full text
  TRUE_SCOPE_DIFFERENCE the record STATES the excluding fact: a population our protocol names as out of scope
                        (population_none term), another agent randomised, a non-placebo comparator named
                        (usual care / no treatment / open-label), an open-label design
Each item carries the comparator's own eligibility sentences (from its held text), so the contrast is visible.

    python scripts/k_gap_exclusion_audit.py   -> outputs/k_gap/exclusion_audit.json (small)
"""
from __future__ import annotations

import copy
import io
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "outputs", "k_gap")
_DASH = re.compile("[‐‑‒–—―−]")
ELIG = re.compile(r"\b(?:inclu(?:ded|sion)|eligib\w*|criteria|were considered)\b", re.I)
RANDOM = re.compile(r"\brandomi[sz]\w*|\brandomly\b", re.I)
# THIS study randomised (not: randomised trials exist) -- statins cohorts cite RCTs in their background
RANDOMISED_HERE = re.compile(r"\b(?:were|was|been|are|is)\s+(?:\w+\s+)?randomi[sz]ed|randomly\s+(?:assigned|allocated)|\brandomi[sz]ed\s+(?:to|into|in a|double|placebo|controlled|trial of|\d)", re.I)
# a comparison is STATED (an active or non-placebo comparator), even when no placebo is named
COMPARISON_STATED = re.compile(r"\bversus\b|\bvs\.?\s|compared (?:with|to)|\bcombination\b|with (?:and|or) without|added to", re.I)
BLIND = re.compile(r"\b(?:double|single|triple)[- ]?blind\w*|\bblinded\b|\bmasked\b|open[- ]label|unblinded|not blinded", re.I)
# an open design, also as a bare design adjective: 'a prospective, randomized, open, single-center clinical assay'
# (Zarpelon 27223641 full text) -- 'open' only between design words, never 'open heart' / 'open surgery'
OPEN = re.compile(r"open[- ]label|unblinded|not blinded|non-?blinded|"
                  r"\b(?:randomi[sz]ed|prospective|controlled)\s*,\s*open\s*,|\bopen\s*,\s*(?:single|multi)[- ]?cent(?:er|re)", re.I)
# THIS study self-described as open ('This is a prospective, randomized, open, single-center clinical assay') -- narrow on
# purpose: never 'open-label extension' (a double-blind trial can have one), never 'open heart'
OPEN_DESIGN_SELF = re.compile(r"\b(?:this|the present|our)\s+(?:is\s+an?\s+|was\s+an?\s+)?(?:\w+\s*,\s*){0,3}?"
                              r"(?:randomi[sz]ed|prospective|controlled)\s*,\s*open\s*,", re.I)
OTHER_COMP = re.compile(r"\b(?:usual care|standard (?:of )?care|standard therapy|no treatment|untreated|"
                        r"conventional (?:care|therapy|treatment)|control group received no|best supportive care|"
                        r"control group,? not receiving (?:the )?(?:study )?(?:medication|drug|treatment))\b", re.I)
OBSERVATIONAL = re.compile(r"\bassociation of\b|\bcohort\b|\bobservational\b|\bretrospective\b|\bregistry\b|"
                           r"\bcase series\b|\bcross-sectional\b|population-based|case-control|nationwide", re.I)
ORDER = ("SCREENER_ERROR", "INSUFFICIENT_RECORD", "TRUE_SCOPE_DIFFERENCE", "INCONSISTENT")
# a title marker naming a RESULTS report of a randomised trial (not a design / protocol paper)
RESULTS_REPORT_MARKER = re.compile(r"sub-?study|secondary analysis|post[-\s]?hoc", re.I)


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def population():
    """(slug, label, record, recorded stage) per seeded, excluded comparator trial -- trial level, as the funnel."""
    T = _j(os.path.join(OUT, "k_gap_table.json"))
    cfm = _j(os.path.join(OUT, "counterfactual_members.json"))
    mrec = _j(os.path.join(OUT, "member_records.json"))
    order = ["POOLED", "DECLARED_ABSENT", "SCREENED_VIA_OTHER_REPORT", "INCLUDED_NOT_IN_PRIMARY", "SCREENED_OUT",
             "NOT_IN_SCREEN"]
    pinned = {}
    out = []
    served_screen = {}
    for r in T["trials"]:
        if r["gap_class"] == "SCREEN_OR_ELIGIBILITY" and r["drug"] != "OTHER_AGENT":
            # a comparator trial OUR OWN screen saw and excluded (not seeded): the same claim -- 'a published comparator
            # included something our protocol should not' -- so the same audit gates it (g1_tracker gives it the same
            # funnel record; until 2026-10-02 the audit never saw these: colchicine-postop-af's 6 exclusions all sat
            # SCREENED_OUT_UNAUDITED). Record = the topic's held record; rule = the served screening ledger's.
            if r["slug"] not in served_screen:
                rv = os.path.join(ROOT, "docs", "reviews", r["slug"], "review.json")
                served_screen[r["slug"]] = ({str(x.get("id")): x for x in (_j(rv).get("screening") or {}).get("records", [])}
                                            if os.path.exists(rv) else {})
            if r["slug"] not in pinned:
                rp = os.path.join(ROOT, "cache", r["slug"], "records.json")
                rj = _j(rp) if os.path.exists(rp) else {}
                pinned[r["slug"]] = {str(x.get("id")): x for x in rj.get("records", []) + rj.get("ctgov", [])}
            for p in (r.get("cited_pmids") or r.get("pmids") or []):
                s = served_screen[r["slug"]].get(str(p))
                if s and s.get("decision") == "exclude":
                    out.append({"slug": r["slug"], "label": r["label"], "pmid": str(p),
                                "rec": pinned[r["slug"]].get(str(p)) or mrec.get(str(p)), "stage": "SCREENED_OUT",
                                "recorded_rule": s.get("rule_id"), "origin": "OUR_SCREEN"})
                    break
            continue
        if r["gap_class"] != "IDENTIFICATION" or r["unit_source"] == "REFERENCE_SEED" or r["drug"] == "OTHER_AGENT":
            continue
        seeds = r["cited_pmids"] if set(r.get("cited_pmids") or []) & set(r["pmids"]) else r["pmids"]
        fn = (cfm.get(r["slug"]) or {}).get("funnel") or {}
        hits = sorted(((p, fn[p]) for p in seeds if p in fn), key=lambda x: order.index(x[1]["stage"]))
        if not hits:
            continue
        p, h = hits[0]
        if h["stage"] == "SCREENED_OUT":
            rec = mrec.get(p)
        elif h["stage"] == "SCREENED_VIA_OTHER_REPORT" and h.get("via_decision") == "exclude":
            if r["slug"] not in pinned:
                rj = _j(os.path.join(ROOT, "cache", r["slug"], "records.json"))
                pinned[r["slug"]] = {x.get("id"): x for x in rj.get("records", []) + rj.get("ctgov", [])}
            rec = pinned[r["slug"]].get(h["via"]) or mrec.get(h["via"])
            p = h["via"]
        else:
            continue
        out.append({"slug": r["slug"], "label": r["label"], "pmid": p, "rec": rec, "stage": h["stage"],
                    "recorded_rule": h.get("rule_id") or h.get("via_rule_id")})
    # the unit is (topic, trial): one trial under two table rows of the SAME topic is counted once, keeping the
    # SCREENED_OUT item. The same trial in two TOPICS is two items -- two protocols, two claims (STEP 4 is in both the
    # semaglutide MACE and weight topics, and is classified differently under each).
    seen, dedup, dups = set(), [], []
    for it in sorted(out, key=lambda x: (x["pmid"], x["stage"] != "SCREENED_OUT")):
        if (it["slug"], it["pmid"]) in seen:
            dups.append(f"{it['slug']}::{it['pmid']}::{it['label']}")
            continue
        seen.add((it["slug"], it["pmid"]))
        dedup.append(it)
    DUPLICATES[:] = dups
    return dedup


def comparator_eligibility(slug):
    from kgap import k_gap
    try:
        text, _ = k_gap.held_text(slug)
    except Exception:  # noqa: BLE001
        return []
    sents = re.split(r"(?<=[.;])\s+", re.sub(r"\s+", " ", text))
    return [s[:300] for s in sents if ELIG.search(s) and len(s) > 40][:4]


def _cfg(slug):
    return _j(os.path.join(ROOT, "topics", slug + ".json"))


def decide(rec, inc):
    from harness import screen
    d = screen.screen_record(rec, inc, set())
    return {"decision": d.decision, "rule_id": d.rule_id, "reason": d.reason} if hasattr(d, "decision") else \
        {"decision": d[0], "rule_id": d[1], "reason": d[2]}


def condition_is_outcome(cfg):
    from harness import lexicon
    inc = cfg.get("include") or {}
    pop = {lexicon.fold(t).rstrip("*").strip() for t in (inc.get("population_any") or [])}
    kw = [lexicon.fold(k) for k in ((cfg.get("primary_outcome") or {}).get("keywords") or [])]
    return any(p and any(p in k or k in p for k in kw) for p in pop)


def fold_rec(rec):
    r = dict(rec)
    for k in ("title", "abstract", "acronym"):
        if isinstance(r.get(k), str):
            r[k] = _DASH.sub("-", r[k])
    if isinstance(r.get("conditions"), list):
        r["conditions"] = [_DASH.sub("-", c) if isinstance(c, str) else c for c in r["conditions"]]
    return r


def classify(rec, cfg):
    """(class, subclass, detail) for one excluded record under its topic config."""
    inc = copy.deepcopy(cfg.get("include") or {})
    base = decide(rec, inc)
    if base["decision"] == "include":
        # a FULL TEXT can mention 'placebo-controlled' while citing ANOTHER study (Zarpelon 27223641's sample-size
        # paragraph) and so pass the ruleset's design check; an explicit self-description of THIS study's design as open
        # decides the design axis (the protocol requires double-blind or placebo-controlled)
        if inc.get("design_double_blind") and OPEN_DESIGN_SELF.search(rec.get("abstract") or ""):
            return ("TRUE_SCOPE_DIFFERENCE", "OPEN_DESIGN_STATED_FOR_THIS_STUDY (a placebo mention elsewhere cites another "
                    "study)", base)
        return "INCONSISTENT", "RULESET_INCLUDES", base
    rule, reason = base["rule_id"], base["reason"] or ""
    ab = rec.get("abstract") or ""
    # --- SCREENER_ERROR: a repair of a known class flips it to include
    if decide(fold_rec(rec), inc)["decision"] == "include":
        return "SCREENER_ERROR", "COMPARATOR_WORDING", base
    if rule == "X3" and "no eligible comparator" in reason:
        # the comparator list holds only PHRASES ('placebo group', 'placebo-controlled'): an abstract that says
        # 'metformin or placebo' names the comparator but matches none. Repair: add each phrase's head term.
        heads = sorted({re.split(r"[\s-]", t.strip())[0] for t in (inc.get("comparator_any") or []) if t.strip()})
        rep = dict(inc, comparator_any=list(inc.get("comparator_any") or []) + heads)
        if decide(rec, rep)["decision"] == "include":
            return "SCREENER_ERROR", "COMPARATOR_WORDING", base
    if rule == "X2" and not inc.get("prevention"):
        if decide(rec, dict(inc, prevention=True))["decision"] == "include":
            return ("SCREENER_ERROR", "CONDITION_AS_OUTCOME (population term shared with the outcome)" if condition_is_outcome(cfg)
                    else "POPULATION_ONLY_IN_ABSTRACT",
                    base)
    if rule == "X3" and inc.get("intervention_in_title"):
        if decide(rec, dict(inc, intervention_in_title=False))["decision"] == "include":
            return "SCREENER_ERROR", "INTERVENTION_ONLY_IN_ABSTRACT", base
    # --- no repair flips it: does the record STATE the excluding fact, or simply not say?
    if not ab.strip():
        return "INSUFFICIENT_RECORD", "NO_ABSTRACT", base
    if OBSERVATIONAL.search((rec.get("title") or "") + " " + ab) and not RANDOMISED_HERE.search((rec.get("title") or "") + " " + ab):
        return "TRUE_SCOPE_DIFFERENCE", "OBSERVATIONAL_DESIGN_STATED (protocol requires an RCT)", base
    if rule == "X1":
        from harness import screen as _screen
        mark = _screen._TITLE_RCT_NOT.search(rec.get("title") or "")
        pts = [p.lower() for p in rec.get("pubtypes") or []]
        if mark and any("randomized controlled trial" in p for p in pts) and (RANDOMISED_HERE.search(ab)
                                                                              or _screen._body_says_rct(rec)):
            # the X1 came from a TITLE marker on a record PubMed types as an RCT and whose abstract says THIS study was
            # randomised. A design / protocol paper is legitimately not a results report; a substudy / secondary /
            # post-hoc report IS a randomised report of a trial -- 'not a randomized controlled trial' misstates it
            # (colchicine-postop-af 22090167, the COPPS POAF substudy; the recorded adjudicator already disagreed).
            if RESULTS_REPORT_MARKER.search(mark.group(0)):
                return "SCREENER_ERROR", f"SECONDARY_REPORT_OF_RCT:'{mark.group(0)}' (route to its trial family)", base
            return "TRUE_SCOPE_DIFFERENCE", f"DESIGN_OR_PROTOCOL_PAPER_STATED:'{mark.group(0)}'", base
        return (("TRUE_SCOPE_DIFFERENCE", "NOT_RANDOMISED_STATED", base) if re.search(r"non-?randomi[sz]ed", ab, re.I)
                else ("INSUFFICIENT_RECORD", "DESIGN_NOT_ESTABLISHED_BY_RECORD", base))
    if rule == "X-DESIGN":
        return (("TRUE_SCOPE_DIFFERENCE", "OPEN_LABEL_STATED (protocol requires double-blind)", base) if OPEN.search(ab)
                else ("INSUFFICIENT_RECORD", "BLINDING_NOT_STATED", base))
    if rule == "X3" and "no eligible comparator" in reason:
        return (("TRUE_SCOPE_DIFFERENCE", "NON_PLACEBO_COMPARATOR_STATED (protocol requires placebo)", base)
                if OTHER_COMP.search(ab) or COMPARISON_STATED.search((rec.get("title") or "") + " " + ab)
                else ("INSUFFICIENT_RECORD", "COMPARATOR_NOT_STATED", base))
    if rule == "X3":
        return "TRUE_SCOPE_DIFFERENCE", "OTHER_INTERVENTION_OR_FORM_RANDOMISED", base
    if rule == "X2" and reason.startswith("wrong population"):
        term = (re.search(r"mention '([^']+)'", reason) or [None, ""])[1]
        return "TRUE_SCOPE_DIFFERENCE", f"PROTOCOL_EXCLUDES_POPULATION:'{term}'", base
    if rule == "X2":
        # 'population term absent' cannot tell a vocabulary gap from a different population from an unstated one. The
        # tie-break is the RECORDED second reader's population axis on this same record (scripts/k_gap_screen_recheck.py,
        # quote-verified by model_source.verify_screening): MET -> our wording missed it; NOT_MET -> the record states
        # another population; NOT_STATED / no verified reading -> the record does not say.
        pv = READER.get(str(rec.get("id")))
        if pv == "MET":
            return "SCREENER_ERROR", "POPULATION_VOCABULARY (recorded reader: population MET, quoted)", base
        if pv == "NOT_MET":
            return "TRUE_SCOPE_DIFFERENCE", "POPULATION_OUTSIDE_PROTOCOL (recorded reader: NOT_MET, quoted)", base
        return "INSUFFICIENT_RECORD", "POPULATION_NOT_STATED_IN_RECORD", base
    return "TRUE_SCOPE_DIFFERENCE", f"RULE:{rule}", base


READER = {}
DUPLICATES = []


def load_reader():
    """pmid -> population-axis verdict of the recorded, VERIFIER_PASS second reading (both recheck populations)."""
    for name in ("k_gap_screen_recheck.json", "k_gap_screen_recheck.table.json"):
        p = os.path.join(ROOT, "registry", "model_proposals", name)
        if not os.path.exists(p):
            continue
        for r in _j(p).get("rows", []):
            v = r.get("verification") or {}
            if v.get("state") == "VERIFIER_PASS" and r.get("pmid"):
                READER[str(r["pmid"])] = ((v.get("axes") or {}).get("population") or {}).get("verdict")


def main():
    load_reader()
    pop = population()
    elig = {}
    rows, tally, sub = [], Counter(), Counter()
    for it in pop:
        s = it["slug"]
        if s not in elig:
            elig[s] = comparator_eligibility(s)
        if not it["rec"]:
            cls, sc, base = "INSUFFICIENT_RECORD", "RECORD_NOT_HELD", {}
        else:
            cls, sc, base = classify(it["rec"], _cfg(s))
            if cls != "INCONSISTENT" and base.get("rule_id") != it["recorded_rule"] and it["stage"] == "SCREENED_OUT":
                cls, sc = "INCONSISTENT", f"RULE_{base.get('rule_id')}_NE_RECORDED_{it['recorded_rule']}"
        tally[cls] += 1
        sub[(cls, sc.split(":")[0].split(" (")[0])] += 1
        rows.append({"slug": s, "label": it["label"], "pmid": it["pmid"], "stage": it["stage"],
                     "rule_id": base.get("rule_id") or it["recorded_rule"], "reason": (base.get("reason") or "")[:160],
                     "class": cls, "subclass": sc, "title": ((it["rec"] or {}).get("title") or "")[:140]})
    out = {"n": len(rows), "duplicate_table_rows_counted_once": DUPLICATES, "by_class": {k: tally.get(k, 0) for k in ORDER},
           "by_subclass": {f"{a}/{b}": v for (a, b), v in sorted(sub.items())},
           "comparator_eligibility": elig, "rows": rows}
    json.dump(out, open(os.path.join(OUT, "exclusion_audit.json"), "w", encoding="utf-8", newline="\n"),
              indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("n", "duplicate_table_rows_counted_once", "by_class", "by_subclass")}, indent=1))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
