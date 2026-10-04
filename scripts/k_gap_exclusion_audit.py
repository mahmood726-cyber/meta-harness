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
                        (usual care / no treatment / open-label), an open-label design. STATES means a SPAN: every
                        TRUE_SCOPE_DIFFERENCE carries `span` = {field, text, match}, the record's own words (verbatim in
                        that field) that establish the excluding fact. No span -> INSUFFICIENT_RECORD:<sub>_NO_SPAN, and
                        the trial stays ELIGIBLE (Mahmood 3 Oct: a denominator never shrinks on an unevidenced claim)
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
OPEN = re.compile(r"open[- ]label|unblinded|not blinded|non-?blinded", re.I)
OTHER_COMP = re.compile(r"\b(?:usual care|standard (?:of )?care|standard therapy|no treatment|untreated|"
                        r"conventional (?:care|therapy|treatment)|control group received no|best supportive care)\b", re.I)
OBSERVATIONAL = re.compile(r"\bassociation of\b|\bcohort\b|\bobservational\b|\bretrospective\b|\bregistry\b|"
                           r"\bcase series\b|\bcross-sectional\b|population-based|case-control|nationwide", re.I)
ORDER = ("SCREENER_ERROR", "INSUFFICIENT_RECORD", "TRUE_SCOPE_DIFFERENCE", "INCONSISTENT")
# a record that STATES it analyses data from several trials (pooled / post hoc / secondary analysis), not one trial
SECONDARY_ANALYSIS = re.compile(r"\bpooled analys[ie]s\b|\bpost[- ]hoc analys[ie]s\b|\bsecondary analys[ie]s\b|"
                                r"\bsub-?analys[ie]s\b|"
                                # a COUNTED set of trials ('enrolled in 5 phase III trials'), never 'enrolled in the
                                # trials' (DELIVER's background sentence)
                                r"\b(?:enrolled in|across|from|of) (?:\d+|two|three|four|five|six|seven|eight|nine|ten) "
                                r"(?:phase (?:I{1,3}|[1-3]) )?(?:randomi[sz]ed )?(?:controlled )?trials\b", re.I)
SPAN_FIELDS = ("title", "conditions", "abstract")
SPAN_CAP = 240


# a sentence ends at '. ' -- never at an abbreviation ('Medical vs. surgical', 'et al. ', 'e.g. ', 'i.e. ', 'Dr. ')
_SENT_END = re.compile(r"(?<!\bvs)(?<!\bal)(?<!\be\.g)(?<!\bi\.e)(?<!\bDr)(?<!\bno)\.\s", re.I)


def record_field_texts(rec, fields=SPAN_FIELDS):
    """(field, text) for each string a record holds in `fields` (a list field gives one entry per item)."""
    for f in fields:
        v = (rec or {}).get(f)
        for s in (v if isinstance(v, list) else [v]):
            if isinstance(s, str) and s.strip():
                yield f, s


_SECTION = re.compile(r"(?:^|(?<=[.\s]))([A-Z][A-Z &/]{2,40}):\s")
_BACKGROUND_LABELS = re.compile(r"^(?:BACKGROUND|INTRODUCTION|CONTEXT|RATIONALE|BACKGROUND AND (?:AIMS?|PURPOSE|OBJECTIVES?))$")


def _background_ranges(ab):
    """[start, end) character ranges of a structured abstract's BACKGROUND / INTRODUCTION / CONTEXT / RATIONALE
    sections (label to the next label). An unstructured abstract has none."""
    labs = list(_SECTION.finditer(ab or ""))
    out = []
    for i, m in enumerate(labs):
        if _BACKGROUND_LABELS.match(m.group(1).strip()):
            out.append((m.start(), labs[i + 1].start() if i + 1 < len(labs) else len(ab)))
    return out


def _all_spans(rec, rx, fields=SPAN_FIELDS, avoid=None):
    """Every verbatim span of `rec`: the sentence around each match of `rx` (at most SPAN_CAP chars either side of the
    match) in which `avoid` does not occur, as {field, text, match}, in record order."""
    out = []
    for f, s in record_field_texts(rec, fields):
        ends = [e.start() for e in _SENT_END.finditer(s)]
        bg = _background_ranges(s) if f == "abstract" else []
        for m in rx.finditer(s):
            if any(a0 <= m.start() < b0 for a0, b0 in bg):
                continue                 # a BACKGROUND sentence says nothing about what THIS trial did (CORE, DELIVER)
            i = max((e for e in ends if e < m.start()), default=-1)
            a = max(0 if i < 0 else i + 2, m.start() - SPAN_CAP)
            b = min((e for e in ends if e >= m.end()), default=-1)
            b = len(s) if b < 0 else b + 1
            b = min(b, m.end() + SPAN_CAP)
            txt = s[a:b].strip()
            if avoid is not None and avoid.search(txt):
                continue
            out.append({"field": f, "text": txt, "match": m.group(0)})
    return out


def span_of(rec, rx, fields=SPAN_FIELDS, avoid=None):
    """The first verbatim span (see _all_spans), or None when the record never states it."""
    sp = _all_spans(rec, rx, fields, avoid)
    return sp[0] if sp else None


def _terms_rx(terms):
    ts = [t.strip().rstrip("*") for t in terms or [] if t and t.strip()]
    return re.compile("|".join(r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?![A-Za-z0-9])" for t in ts), re.I) if ts else None


# what THIS study randomised: in the TITLE any statement of the study ('trial', 'study', 'effect of', 'versus'); in the
# ABSTRACT only a sentence about THIS study's allocation -- a background line ('few randomized controlled trials have
# been conducted') states nothing about the trial (PEP-CHF, 3 Oct)
TITLE_STUDY_STATED = re.compile(r"\b(?:trial|study|effects? of|versus|vs\.?|compared|comparing)\b", re.I)
THIS_STUDY_RANDOMISED = re.compile(r"\b(?:this|the present|we)\b[^.]{0,80}?\brandomi[sz]ed|"
                                   r"\b(?:were|was)\s+(?:\w+\s+){0,2}?randomi[sz]ed|randomly\s+(?:assigned|allocated|divided)|"
                                   r"\bcomparing\b", re.I)


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
    for r in T["trials"]:
        # REFERENCE_SEED units are audited too: where the comparator prints no trial table, its reference list IS the
        # unit list, and a reference our screen excluded is as much a claim as a table row (doac-vte 24081972)
        if r["gap_class"] != "IDENTIFICATION" or r["drug"] == "OTHER_AGENT":
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


def population_in_screen():
    """(slug, label, record, recorded rule) per comparator trial ALREADY in our screen and excluded there -- the class
    SCREENED_OUT_UNAUDITED (76 trials over 31 topics on 3 Oct). Read from the tracker files (outputs/k_gap/g1/*.json,
    trials[].seeded_funnel with already_in_screen) and the topic's own pinned records.json; same classifier, same
    INCONSISTENT check as the seeded population."""
    gdir = os.path.join(OUT, "g1")
    out, pinned = [], {}
    for f in sorted(os.listdir(gdir)) if os.path.isdir(gdir) else []:
        if not f.endswith(".json") or ".tmp" in f:
            continue
        o = _j(os.path.join(gdir, f))
        if o.get("lane_source"):
            # a lane-owned topic: the lane NAMED these exclusions; each still needs a span from its record, so the
            # same classifier runs on them (origin LANE_NAMED) -- the tracker demotes an unspanned one to an open gap
            slug = o["slug"]
            # named by the lane, OR screened out with a rule (a lane-named exclusion this audit once demoted must stay
            # in the audit's population, or a later fix of the audit can never re-examine it -- SOLOIST-WHF, 3 Oct)
            lane_items = [d for d in o.get("named_differences") or []
                          if d.get("kind") == "PROTOCOL_SCOPE_DIFFERENCE" and d.get("pmid")]
            seen_lane = {d["trial"] for d in lane_items}
            lane_items += [{"trial": x["label"], "pmid": (x.get("seeded_funnel") or {}).get("pmid"),
                            "rule_id": (x.get("seeded_funnel") or {}).get("rule_id")}
                           for x in o.get("trials") or [] if x["label"] not in seen_lane
                           and (x.get("seeded_funnel") or {}).get("stage") == "SCREENED_OUT"
                           and (x.get("seeded_funnel") or {}).get("pmid")]
            for d in lane_items:
                if slug not in pinned:
                    rp = os.path.join(ROOT, "cache", slug, "records.json")
                    rj = _j(rp) if os.path.exists(rp) else {}
                    pinned[slug] = {str(r.get("id")): r for r in rj.get("records", []) + rj.get("ctgov", [])}
                rec = pinned[slug].get(str(d["pmid"])) or _member_records().get(str(d["pmid"]))
                out.append({"slug": slug, "label": d["trial"], "pmid": str(d["pmid"]), "rec": rec,
                            "stage": "SCREENED_OUT", "recorded_rule": d.get("rule_id"), "origin": "LANE_NAMED"})
            continue
        for x in o.get("trials") or []:
            fn = x.get("seeded_funnel") or {}
            # every comparator trial the tracker saw screened out -- in our screen already, or seeded in memory from a
            # held member record (doac-vte 24081972 was the latter and was never audited)
            if fn.get("stage") != "SCREENED_OUT" or not fn.get("pmid") or x.get("in_our_pool"):
                continue
            slug = o["slug"]
            if slug not in pinned:
                rj = _j(os.path.join(ROOT, "cache", slug, "records.json"))
                pinned[slug] = {str(r.get("id")): r for r in rj.get("records", []) + rj.get("ctgov", [])}
            rec = pinned[slug].get(str(fn["pmid"])) or _member_records().get(str(fn["pmid"]))
            out.append({"slug": slug, "label": x["label"], "pmid": fn["pmid"], "rec": rec,
                        "stage": "SCREENED_OUT", "recorded_rule": fn.get("rule_id"),
                        "origin": "IN_SCREEN" if fn.get("already_in_screen") else "SEEDED_IN_MEMORY"})
    return out


_MREC = {}


def _member_records():
    if not _MREC:
        p = os.path.join(OUT, "member_records.json")
        _MREC.update(_j(p) if os.path.exists(p) else {})
    return _MREC


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
    """(class, subclass, detail) for one excluded record under its topic config. A TRUE_SCOPE_DIFFERENCE is returned
    only with detail['span'] set (the record's words establishing it); without one it is INSUFFICIENT_RECORD."""
    cls, sub, base = _classify(rec, cfg)
    if cls == "TRUE_SCOPE_DIFFERENCE" and not (base or {}).get("span"):
        return "INSUFFICIENT_RECORD", sub.split(" (")[0].split(":")[0] + "_NO_SPAN", base
    return cls, sub, base


_AIM_OF_THIS_STUDY = re.compile(r"\b(?:we|this (?:trial|study))\s+(?:examined|aimed|assessed|evaluated|investigated|"
                                r"sought|tested|asked|determined)\b", re.I)


def _with_span(base, span):
    return dict(base, span=span)


def _classify(rec, cfg):
    inc = copy.deepcopy(cfg.get("include") or {})
    base = decide(rec, inc)
    if base["decision"] == "include":
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
    # the 'prevention' repair turns the protocol into a prevention protocol: never for a protocol that EXCLUDES prevention
    # (tranexamic-acid-pph lists 'prevent' / 'prophylaxis' in population_none; WOMAN-2 is a prophylaxis trial)
    excludes_prevention = any(re.match(r"prevent|prophyla", str(t).strip(), re.I) for t in inc.get("population_none") or [])
    if rule == "X2" and not inc.get("prevention") and not excludes_prevention:
        if decide(rec, dict(inc, prevention=True))["decision"] == "include":
            return ("SCREENER_ERROR", "CONDITION_AS_OUTCOME (population term shared with the outcome)" if condition_is_outcome(cfg)
                    else "POPULATION_ONLY_IN_ABSTRACT",
                    base)
    if rule == "X3" and inc.get("intervention_in_title"):
        # the repair counts only when OUR intervention is what THIS study randomised: a term in the abstract's
        # allocation sentence. A background mention is not one -- SOLOIST-WHF: 'SGLT2 inhibitors reduce the risk ...'
        # (background) vs 'randomly assigned to receive sotagliflozin or placebo' (what was randomised).
        av = _terms_rx(inc.get("intervention_any"))
        alloc = av is not None and any(av.search(s["text"]) for s in _all_spans(rec, THIS_STUDY_RANDOMISED, ("abstract",)))
        if alloc and decide(rec, dict(inc, intervention_in_title=False))["decision"] == "include":
            return "SCREENER_ERROR", "INTERVENTION_ONLY_IN_ABSTRACT", base
    # --- no repair flips it: does the record STATE the excluding fact, or simply not say?
    if not ab.strip():
        return "INSUFFICIENT_RECORD", "NO_ABSTRACT", base
    if OBSERVATIONAL.search((rec.get("title") or "") + " " + ab) and not RANDOMISED_HERE.search((rec.get("title") or "") + " " + ab):
        return ("TRUE_SCOPE_DIFFERENCE", "OBSERVATIONAL_DESIGN_STATED (protocol requires an RCT)",
                _with_span(base, span_of(rec, OBSERVATIONAL, ("title", "abstract"))))
    if rule == "X1" and SECONDARY_ANALYSIS.search((rec.get("title") or "") + " " + ab):
        # the record states it is an analysis ACROSS / OF trials, not a trial's report (doac-vte PMID 24081972:
        # 'bleeding reports from 1034 individuals ... enrolled in 5 phase III trials')
        return ("TRUE_SCOPE_DIFFERENCE", "SECONDARY_ANALYSIS_OF_TRIALS_STATED (protocol includes trial reports)",
                _with_span(base, span_of(rec, SECONDARY_ANALYSIS, ("title", "abstract"))))
    if rule == "X1":
        return (("TRUE_SCOPE_DIFFERENCE", "NOT_RANDOMISED_STATED",
                 _with_span(base, span_of(rec, re.compile(r"non-?randomi[sz]ed", re.I), ("title", "abstract"))))
                if re.search(r"non-?randomi[sz]ed", ab, re.I)
                else ("INSUFFICIENT_RECORD", "DESIGN_NOT_ESTABLISHED_BY_RECORD", base))
    if rule == "X-DESIGN":
        return (("TRUE_SCOPE_DIFFERENCE", "OPEN_LABEL_STATED (protocol requires double-blind)",
                 _with_span(base, span_of(rec, OPEN, ("title", "abstract"))))
                if OPEN.search(ab)
                else ("INSUFFICIENT_RECORD", "BLINDING_NOT_STATED", base))
    if rule == "X3" and "no eligible comparator" in reason:
        # the span must state ANOTHER comparator: a sentence naming a protocol comparator proves nothing
        avoid = _terms_rx(inc.get("comparator_any"))
        sp = span_of(rec, OTHER_COMP, ("title", "abstract"), avoid) or span_of(rec, COMPARISON_STATED, ("title", "abstract"), avoid)
        comps = ", ".join((inc.get("comparator_any") or [])[:4]) or "a named comparator"
        return (("TRUE_SCOPE_DIFFERENCE", f"NON_PROTOCOL_COMPARATOR_STATED (protocol requires {comps})", _with_span(base, sp))
                if OTHER_COMP.search(ab) or COMPARISON_STATED.search((rec.get("title") or "") + " " + ab)
                else ("INSUFFICIENT_RECORD", "COMPARATOR_NOT_STATED", base))
    if rule == "X3":
        # ANOTHER agent randomised must be STATED: a sentence saying what was studied / randomised that names none of
        # the protocol's intervention terms. The screen's 'is not [...]' is an ABSENCE, never on its own a scope fact.
        av = _terms_rx(inc.get("intervention_any"))
        # a record that names OUR intervention as what it studied does not establish that another agent was randomised
        # -- metformin 15498183 randomised metformin under a generic title ('[Clinical study on ...]'). 'As what it
        # studied' = the title or an allocation sentence; a BACKGROUND sentence does not count (SOLOIST-WHF: 'SGLT2
        # inhibitors reduce ...', then 'randomly assigned to receive sotagliflozin or placebo'). With no allocation
        # sentence in the abstract, any mention counts (fail closed: no span).
        alloc = _all_spans(rec, THIS_STUDY_RANDOMISED, ("abstract",))
        where = [t for _, t in record_field_texts(rec, ("title",))] + [s["text"] for s in alloc] if alloc else \
            [t for _, t in record_field_texts(rec, ("title", "abstract"))]
        named_ours = av is not None and any(av.search(t) for t in where)
        sp = None if named_ours else (span_of(rec, TITLE_STUDY_STATED, ("title",), av) or
                                      span_of(rec, THIS_STUDY_RANDOMISED, ("abstract",), av))
        return "TRUE_SCOPE_DIFFERENCE", "OTHER_INTERVENTION_OR_FORM_RANDOMISED", _with_span(base, sp)
    if rule == "X2" and reason.startswith("wrong population"):
        term = (re.search(r"mention '([^']+)'", reason) or [None, ""])[1]
        return ("TRUE_SCOPE_DIFFERENCE", f"PROTOCOL_EXCLUDES_POPULATION:'{term}'",
                _with_span(base, span_of(rec, _terms_rx([term]), ("title", "conditions", "abstract")) if term else None))
    if rule == "X2":
        # THIS STUDY'S STATED AIM names a population the protocol EXCLUDES: a structured abstract often states its aim
        # inside BACKGROUND (WOMAN-2: 'We examined whether giving tranexamic acid shortly after birth can prevent
        # postpartum haemorrhage in women with ... anaemia'), which the background filter skips wholesale. Only an aim
        # sentence about THIS study counts ('we examined / aimed / assessed whether ...'), never other background prose.
        none_rx = _terms_rx(inc.get("population_none"))
        if none_rx is not None:
            for sent in re.split(r"(?<=[.!?])\s+", ab):
                body = re.sub(r"^\s*[A-Z][A-Z /]{2,}:\s*", "", sent)
                # a NEGATED term ('without type 2 diabetes', 'with or without ...') is not the population (screen._has)
                from harness.screen import _has as _screen_has
                term = _screen_has(body, inc.get("population_none") or []) if _AIM_OF_THIS_STUDY.search(body) else None
                if term:
                    return ("TRUE_SCOPE_DIFFERENCE", f"PROTOCOL_EXCLUDES_POPULATION:'{term}' (this study's stated aim)",
                            _with_span(base, {"field": "abstract", "text": body.strip(), "match": term}))
        # 'population term absent' cannot tell a vocabulary gap from a different population from an unstated one. The
        # tie-break is the RECORDED second reader's population axis on this same record (scripts/k_gap_screen_recheck.py,
        # quote-verified by model_source.verify_screening): MET -> our wording missed it; NOT_MET -> the record states
        # another population; NOT_STATED / no verified reading -> the record does not say.
        pv, pq = READER.get(str(rec.get("id"))) or (None, None)
        if pv == "MET":
            return "SCREENER_ERROR", "POPULATION_VOCABULARY (recorded reader: population MET, quoted)", base
        if pv == "NOT_MET":
            # the reader's quote, re-found VERBATIM in this record (never taken on the reader's word)
            sp = span_of(rec, re.compile(re.escape(pq.strip())), ("title", "conditions", "abstract")) if pq and pq.strip() else None
            return "TRUE_SCOPE_DIFFERENCE", "POPULATION_OUTSIDE_PROTOCOL (recorded reader: NOT_MET, quoted)", _with_span(base, sp)
        return "INSUFFICIENT_RECORD", "POPULATION_NOT_STATED_IN_RECORD", base
    return "INSUFFICIENT_RECORD", f"RULE:{rule}_NOT_AUDITABLE", base


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
                READER[str(r["pmid"])] = (((v.get("axes") or {}).get("population") or {}).get("verdict"),
                                          (((r.get("claim") or {}).get("axes") or {}).get("population") or {}).get("quote"))


def main():
    load_reader()
    pop = population()
    have = {(it["slug"], it["pmid"]) for it in pop}
    pop += [it for it in population_in_screen() if (it["slug"], it["pmid"]) not in have]
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
                     "origin": it.get("origin", "SEEDED"),
                     "rule_id": base.get("rule_id") or it["recorded_rule"], "reason": (base.get("reason") or "")[:160],
                     "class": cls, "subclass": sc, "title": ((it["rec"] or {}).get("title") or "")[:140],
                     "span": (base or {}).get("span") if cls == "TRUE_SCOPE_DIFFERENCE" else None})
    out = {"n": len(rows), "duplicate_table_rows_counted_once": DUPLICATES, "by_class": {k: tally.get(k, 0) for k in ORDER},
           "by_subclass": {f"{a}/{b}": v for (a, b), v in sorted(sub.items())},
           "comparator_eligibility": elig, "rows": rows}
    json.dump(out, open(os.path.join(OUT, "exclusion_audit.json"), "w", encoding="utf-8", newline="\n"),
              indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("n", "duplicate_table_rows_counted_once", "by_class", "by_subclass")}, indent=1))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
