"""Audit every comparator-trial exclusion the G1 TRACKER shows, not only those the k-gap counterfactual funnel seeded.

scripts/k_gap_exclusion_audit.py classifies a population built from counterfactual_members.json. The tracker sees more:
comparator trials ALREADY in our screen and excluded ('IN SCREEN PMID ...'), and its own first-PMID seeds. Those
reached the page as SCREENED_OUT_UNAUDITED -- the audit reported where it looked, not every exclusion that exists.
This runner takes the population from the tracker files themselves (every trial whose blocker is
SCREENED_OUT_UNAUDITED:<rule> or SCREENED_VIA_OTHER_REPORT), finds the excluded record, and classifies it with the SAME
classifier, imported unchanged (k_gap_exclusion_audit.classify, with its recorded second-reader tie-break):

  TRUE_SCOPE_DIFFERENCE   the record states the excluding fact (protocol rule named)
  SCREENER_ERROR          a repair of a known screener class flips it to include
  INSUFFICIENT_RECORD     the record lacks the fact the rule needs (full text needed)
  INCONSISTENT            the re-screen does not reproduce the recorded rule (not classified)

    python scripts/g1_exclusion_audit_tracker.py [SLUG ...]   -> outputs/k_gap/exclusion_audit.tracker.json
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import k_gap_exclusion_audit as xa  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap", "exclusion_audit.tracker.json")
G1 = os.path.join(ROOT, "outputs", "k_gap", "g1")
PMID_IN = re.compile(r"(?:IN SCREEN|SEEDED) PMID (\d+)")


def _records(slug):
    p = os.path.join(ROOT, "cache", slug, "records.json")
    if not os.path.exists(p):
        return {}
    rj = xa._j(p)
    return {str(x.get("id")): x for k in ("records", "pubmed", "ctgov") for x in (rj.get(k) or []) if isinstance(x, dict)}


LANE_RECORDS = {"sglt2-hfref-hosp-cvdeath": "g1_sglt2_tracker"}   # lanes that seed records held in their own data


def lane_record(slug, pmid):
    """A record a topic LANE seeded from its own held data (sglt2-hfref: SOLOIST-WHF's report, g1/data/sglt2)."""
    mod = LANE_RECORDS.get(slug)
    if not mod:
        return None
    import importlib
    try:
        return importlib.import_module(mod).pubmed_record(pmid)
    except StopIteration:
        return None


SHARED = set()


def population(slugs=None):
    if not SHARED and os.path.exists(os.path.join(xa.OUT, "exclusion_audit.json")):
        SHARED.update((r["slug"], str(r["pmid"])) for r in xa._j(os.path.join(xa.OUT, "exclusion_audit.json"))["rows"])
    mrec = xa._j(os.path.join(xa.OUT, "member_records.json"))
    out = []
    for f in sorted(os.listdir(G1)):
        if not f.endswith(".json"):
            continue
        d = xa._j(os.path.join(G1, f))
        slug = d["slug"]
        if slugs and slug not in slugs:
            continue
        recs = None
        for t in d.get("trials") or []:
            b = str(t.get("blocker") or "")
            sd_src = (((t.get("scope_difference") or {}).get("audit") or {}).get("source") or "")
            # every exclusion the SHARED audit does not cover -- including those THIS audit has already classified (a
            # lane overlay writes our class into the blocker / scope difference; dropping them would shrink the
            # denominator by the items already decided)
            ours = sd_src.endswith("exclusion_audit.tracker.json") or (
                b.split(":", 1)[0] in ("SCREENER_ERROR", "INSUFFICIENT_RECORD") and (slug, str((t.get("seeded_funnel") or {})
                                                                                         .get("pmid"))) not in SHARED)
            if not (b.startswith("SCREENED_OUT_UNAUDITED") or b == "SCREENED_VIA_OTHER_REPORT" or ours):
                continue
            if ours and not b.startswith("SCREENED"):
                b = "SCREENED_OUT_UNAUDITED:" + str((t.get("seeded_funnel") or {}).get("rule_id"))
            m = PMID_IN.search(t.get("our_refusal") or "")
            sf = t.get("seeded_funnel") or {}
            pmid = m.group(1) if m else sf.get("pmid")
            via = sf.get("via") if b == "SCREENED_VIA_OTHER_REPORT" else None
            recs = recs if recs is not None else _records(slug)
            key = via or pmid
            rec = recs.get(str(key)) or mrec.get(str(key)) or lane_record(slug, str(key))
            out.append({"slug": slug, "label": t["label"], "pmid": key, "found_as": pmid, "blocker": b,
                        "recorded_rule": b.split(":", 1)[1] if ":" in b else sf.get("via_rule_id"), "rec": rec,
                        "via_decision": sf.get("via_decision")})
    return out


# ------------------------------------------------------------------ lane refinements (after the shared classifier)
AXES = {}            # (slug, pmid) -> {axis: verdict} from VERIFIER_PASS second readings (all three proposal files)
QUOTES = {}          # (slug, pmid) -> {axis: the verified verbatim quote}
# keyed by TOPIC and record: eligibility is protocol-relative, and one PMID is read under several topics (34449189,
# 27223641, 31535829) -- a pmid-only key let a later topic's verdict overwrite an earlier one's (codex review
# exclusion_audit_and_screen#9)


def _key(slug, pmid):
    return (str(slug), str(pmid))


def quote_span(rec, key, axis):
    """The shared span contract ({field, text, match}, verbatim in the held record's field) from the reader's verified
    quote on `axis`; None when the quote is not verbatim in title / conditions / abstract."""
    q = (QUOTES.get(key) or {}).get(axis)
    if not q or not q.strip():
        return None
    for field in ("title", "conditions", "abstract"):
        v = rec.get(field)
        for item in (v if isinstance(v, list) else [v]):
            if isinstance(item, str) and q in item:
                return {"field": field, "text": q, "match": q, "source": f"recorded reader quote ({axis}, VERBATIM)"}
    return None


FT_DIR = os.path.join(ROOT, "g1", "data", "audit_ft")
NO_PLACEBO_FT = re.compile(r"not receiving the study medication|did not receive (?:any )?(?:study )?(?:medication|drug|"
                           r"placebo)|no placebo was|without placebo|open[- ]label|unblinded|not blinded", re.I)
# a sentence about OTHER studies ('Earlier trials were open-label', 'previous studies used placebo') states nothing about
# this trial: full-text design facts are read from the current study's sentences only (codex review
# exclusion_audit_and_screen#8)
OTHER_STUDY = re.compile(r"\b(?:earlier|previous|prior|past|other|published|existing|former|preceding)\s+(?:[a-z-]+\s+){0,2}"
                         r"(?:trials?|stud(?:y|ies)|reports?|investigations?)\b|\b(?:previous|prior|earlier)ly\b", re.I)
RANDOM_FT = re.compile(r"\brandomly\s+(?:assigned|allocated)|\brandomi[sz](?:ed|ation)\b", re.I)
# negated / non-random allocation in the current study (alternation is not randomisation)
NONRANDOM_FT = re.compile(r"\bnon-?randomi[sz]|\bwithout\s+randomi[sz]|\bnot\s+randomi[sz]|\bquasi-?randomi[sz]|"
                          r"\balternate(?:ly)?\b[^.]{0,40}(?:assign|allocat)|\b(?:assign|allocat)\w*\s+alternate", re.I)


def _current_study(ft):
    """The full text without sentences that describe other studies."""
    return " ".join(x for x in re.split(r"(?<=[.!?])\s+", ft or "") if not OTHER_STUDY.search(x))


BLIND_PLACEBO_FT = re.compile(r"double[- ]blind\w*[^.]{0,80}placebo|placebo[- ]controlled[^.]{0,40}double[- ]blind", re.I)


def load_axes():
    for name in ("k_gap_screen_recheck.json", "k_gap_screen_recheck.table.json", "k_gap_screen_recheck.tracker.json"):
        p = os.path.join(ROOT, "registry", "model_proposals", name)
        if not os.path.exists(p):
            continue
        for r in xa._j(p).get("rows", []):
            v = r.get("verification") or {}
            if v.get("state") == "VERIFIER_PASS" and r.get("pmid"):
                AXES[_key(r.get("slug"), r["pmid"])] = {k: (x or {}).get("verdict") for k, x in (v.get("axes") or {}).items()}
                # the quote each verified axis rests on (verify_screening located it VERBATIM in the held record)
                QUOTES[_key(r.get("slug"), r["pmid"])] = {k: ((r.get("claim") or {}).get("axes") or {}).get(k, {}).get("quote")
                                          for k, x in (v.get("axes") or {}).items()
                                          if ((x or {}).get("located") or {}).get("match") == "VERBATIM"}


AXES2 = {}           # the second reader's verified verdicts (gpt-5.5), same instrument


def load_axes2():
    p = READER2_PROP
    if os.path.exists(p):
        for r in xa._j(p).get("rows", []):
            v = r.get("verification") or {}
            if v.get("state") == "VERIFIER_PASS" and r.get("pmid"):
                AXES2[_key(r.get("slug"), r["pmid"])] = {k: (x or {}).get("verdict") for k, x in (v.get("axes") or {}).items()}


def consensus(key):
    """({axis: verdict} both readers verified identically, {axis: [v1, v2]} where they differ). Where the second reader
    has no verified reading of this record, the first reader's verdicts stand (recorded as single-reader)."""
    a1, a2 = AXES.get(key) or {}, AXES2.get(key)
    if a2 is None:
        return a1, {}
    agree = {k: v for k, v in a1.items() if a2.get(k) == v}
    split = {k: [v, a2.get(k)] for k, v in a1.items() if a2.get(k) != v}
    return agree, split


def _stated_none_term(rec, cfg):
    """A population term the protocol EXCLUDES, stated in the record's title or abstract (word-bounded, folded)."""
    from harness import lexicon
    t = lexicon.fold((rec.get("title") or "") + " " + (rec.get("abstract") or ""))
    for term in (cfg.get("include") or {}).get("population_none") or []:
        f = lexicon.fold(term).rstrip("*").strip()
        if f and re.search(r"\b" + re.escape(f), t):
            return term
    return None


def _full_text(pmid):
    import html
    p = os.path.join(FT_DIR, f"{pmid}.json")
    if not os.path.exists(p):
        return None
    a = xa._j(p)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", a["fulltext"]))) if a.get("fulltext") else None


def refine(it, cls, sc, base, require_reader=True):
    """Classes the shared classifier cannot reach, each by a STATED fact (never by the comparator's decision):
      R1  a repair flipped the record to include, but the record STATES a population the protocol excludes AND the
          recorded reader reads its population NOT_MET -> TRUE_SCOPE_DIFFERENCE (WOMAN-2: 'prevent postpartum
          haemorrhage' under a treatment-of-PPH protocol whose population_none lists 'prevent')
      R2  INSUFFICIENT: the recorded, quote-verified reader's verdict on the AXIS the rule tests (X1/X-DESIGN design,
          X3 comparator/intervention, X2 population): NOT_MET -> TRUE_SCOPE_DIFFERENCE, MET -> SCREENER_ERROR
      R3  INSUFFICIENT and still undecided: the trial's OPEN full text (g1/data/audit_ft) states the design fact"""
    cfg = xa._cfg(it["slug"])
    rec, rule = it["rec"] or {}, base.get("rule_id") or it["recorded_rule"]
    # TWO READERS (gpt-6-astra, gpt-5.5; same instrument, each verified on its own): an axis counts only when both
    # verified readings give the same verdict; an axis they disagree on is NOT decided (and is reported)
    key = _key(it["slug"], it["pmid"])
    ax, split = consensus(key)
    if split:
        it["readers_disagree"] = split
    if cls == "SCREENER_ERROR" and sc.startswith(("CONDITION_AS_OUTCOME", "POPULATION_ONLY_IN_ABSTRACT")):
        term = _stated_none_term(rec, cfg)
        if term and (ax.get("population") == "NOT_MET" or not require_reader):
            base["span"] = xa.span_of(rec, xa._terms_rx([term]), ("title", "conditions", "abstract"))
            return ("TRUE_SCOPE_DIFFERENCE", f"PROTOCOL_EXCLUDES_POPULATION_STATED:'{term}' (repair overruled: the "
                    f"record states it; recorded reader population NOT_MET, quoted)", "R1")
    # R0  a repair that flips the record to include proves only that THIS rule misfired. A SCREENER_ERROR claim also
    #     needs the record to meet the protocol on every other axis: the recorded reader finding another axis NOT_MET
    #     makes it a scope difference on that axis; NOT_STATED leaves the record insufficient (SOLOIST-WHF: the X3 rule
    #     misfired -- sotagliflozin is an SGLT2 inhibitor under the registered criteria -- but its abstract never states
    #     the HFrEF population, and it enrolled across ejection fractions)
    if cls == "SCREENER_ERROR" and ax:
        bad = sorted(k for k, v in ax.items() if v == "NOT_MET")
        unk = sorted(k for k, v in ax.items() if v == "NOT_STATED")
        if bad:
            base["span"] = quote_span(rec, key, bad[0])
            return ("TRUE_SCOPE_DIFFERENCE", f"{bad[0].upper()}_OUTSIDE_PROTOCOL (rule {rule} misfired: {sc}; recorded "
                    f"reader NOT_MET on {bad}, quoted)", "R0")
        if unk:
            return ("INSUFFICIENT_RECORD", f"RULE_{rule}_MISFIRED_BUT_{'_'.join(unk).upper()}_NOT_STATED ({sc}; recorded "
                    f"reader NOT_STATED on {unk})", "R0")
    if cls != "INSUFFICIENT_RECORD":
        return cls, sc, None
    # the reader's DESIGN axis answers X-DESIGN only when the rule is about blinding/placebo; 'required design/context
    # absent: ovulation induction' (metformin, Lord 2006) is a context rule the design axis does not test
    blind_rule = rule == "X-DESIGN" and (base.get("reason") or "").startswith("not double-blind")
    axis = {"X1": "design", "X2": "population"}.get(rule) or ("design" if blind_rule else None) or (
        ("comparator" if "comparator" in (base.get("reason") or "") else "intervention") if rule == "X3" else None)
    v = ax.get(axis) if axis else None
    ft = _full_text(it["pmid"])
    ft = _current_study(ft) if ft else ft            # never a sentence about earlier / other trials (#8)
    double_blind = bool((cfg.get("include") or {}).get("design_double_blind"))
    # a fact STATED in the open full text outranks a reader's MET from the abstract: Wu 2020 (probiotics) reads as a
    # randomised trial in its abstract, and its full text says 'open-label' under a double-blind protocol
    if v == "MET" and ft and double_blind:
        m = NO_PLACEBO_FT.search(ft)
        if m:
            return ("TRUE_SCOPE_DIFFERENCE", f"NO_PLACEBO_OR_OPEN_LABEL_STATED_IN_FULL_TEXT (recorded rule {rule} misfired; "
                    "the record meets it, the protocol's double-blind requirement excludes it): '"
                    + ft[max(0, m.start() - 60):m.end() + 20] + "'", "R3")
    if v is None and axis and axis in (it.get("readers_disagree") or {}):
        return cls, sc + f" | readers disagree on {axis}: {it['readers_disagree'][axis]}", None
    if v == "NOT_MET":
        base["span"] = quote_span(rec, key, axis)
        return "TRUE_SCOPE_DIFFERENCE", f"{axis.upper()}_OUTSIDE_PROTOCOL (recorded reader NOT_MET, quoted)", "R2"
    if v == "MET":
        # the rule's axis being MET proves only that THIS rule misfired: like R0, another verified axis NOT_MET is a
        # scope difference on that axis, and NOT_STATED leaves the record insufficient (codex review #6)
        bad = sorted(k for k, x in ax.items() if x == "NOT_MET" and k != axis)
        unk = sorted(k for k, x in ax.items() if x == "NOT_STATED" and k != axis)
        if bad:
            base["span"] = quote_span(rec, key, bad[0])
            return ("TRUE_SCOPE_DIFFERENCE", f"{bad[0].upper()}_OUTSIDE_PROTOCOL (rule {rule} misfired: recorded reader "
                    f"MET on {axis}, NOT_MET on {bad}, quoted)", "R2")
        if unk:
            return (cls, f"RULE_{rule}_MISFIRED_BUT_{'_'.join(unk).upper()}_NOT_STATED (recorded reader MET on {axis}, "
                    f"NOT_STATED on {unk})", "R2")
        sub = f"{rule}_BUT_RECORD_MEETS_{axis.upper()} (recorded reader MET, quoted)"
        if rule == "X1" and re.search(r"\bsub-?study\b", rec.get("title") or "", re.I):
            sub = "RANDOMISED_SUBSTUDY_VETOED_BY_TITLE (pubtype RCT + abstract 'randomized'; recorded reader MET)"
        return "SCREENER_ERROR", sub, "R2"
    ftspan = lambda m: {"field": "fulltext", "text": ft[max(0, m.start() - 60):m.end() + 20], "match": m.group(0),  # noqa: E731
                        "source": f"open full text g1/data/audit_ft/{it['pmid']}.json (licence stated in the bytes)"}
    # X1 is 'not a randomised trial': the full text answers it with ALLOCATION, never masking -- an open-label RCT
    # meets X1, an alternately-allocated double-blind study does not (codex review #7). Blinding decides only where the
    # protocol itself requires it.
    if ft and rule == "X1":
        m = NONRANDOM_FT.search(ft)
        if m:
            base["span"] = ftspan(m)
            return "TRUE_SCOPE_DIFFERENCE", "NOT_RANDOMISED_STATED_IN_FULL_TEXT: '" + base["span"]["text"] + "'", "R3"
        m = RANDOM_FT.search(ft)
        if m:
            n = NO_PLACEBO_FT.search(ft) if double_blind else None
            if n:
                base["span"] = ftspan(n)
                return ("TRUE_SCOPE_DIFFERENCE", "RANDOMISED_BUT_OPEN_LABEL_STATED_IN_FULL_TEXT (protocol requires "
                        "double-blind): '" + base["span"]["text"] + "'", "R3")
            bad = sorted(k for k, x in ax.items() if x == "NOT_MET")
            if bad:
                base["span"] = quote_span(rec, key, bad[0])
                return ("TRUE_SCOPE_DIFFERENCE", f"{bad[0].upper()}_OUTSIDE_PROTOCOL (X1 misfired: randomised in the "
                        f"full text; recorded reader NOT_MET on {bad}, quoted)", "R3")
            return ("SCREENER_ERROR", "RANDOMISED_STATED_IN_FULL_TEXT: '" + ftspan(m)["text"] + "'", "R3")
    if ft and blind_rule:
        m = NO_PLACEBO_FT.search(ft)
        if m:
            base["span"] = {"field": "fulltext", "text": ft[max(0, m.start() - 60):m.end() + 20], "match": m.group(0),
                            "source": f"open full text g1/data/audit_ft/{it['pmid']}.json (licence stated in the bytes)"}
            return ("TRUE_SCOPE_DIFFERENCE", "NO_PLACEBO_OR_OPEN_LABEL_STATED_IN_FULL_TEXT: '"
                    + ft[max(0, m.start() - 60):m.end() + 20] + "'", "R3")
        if BLIND_PLACEBO_FT.search(ft):
            return "SCREENER_ERROR", "DOUBLE_BLIND_PLACEBO_ONLY_IN_FULL_TEXT", "R3"
    return cls, sc + (" | open full text read, fact not stated" if ft else " | no open full text (cascade R1/R2 logged)"), None


# the screen BEFORE this lane's harness fix (RANDOMISED_SUBSTUDY_VETOED_BY_TITLE, BODY_RCT 'randomized controlled
# study'): an exclusion the current screen no longer reproduces, but the pre-fix screen does, was made by a fixed rule
PRE_FIX = "79dc4435"
_PRE = {}


def _pre_fix_screen():
    if "m" not in _PRE:
        import importlib.util
        import subprocess
        import tempfile
        src = subprocess.run(["git", "show", f"{PRE_FIX}:harness/screen.py"], cwd=ROOT, capture_output=True,
                             check=True).stdout
        d = tempfile.mkdtemp(prefix="g1_prefix_")
        fp = os.path.join(d, "screen_prefix.py")
        open(fp, "wb").write(src)
        spec = importlib.util.spec_from_file_location("harness._screen_prefix", fp)
        m = importlib.util.module_from_spec(spec)
        m.__package__ = "harness"
        spec.loader.exec_module(m)
        _PRE["m"] = m
    return _PRE["m"]


def fixed_since(it):
    """The fix named when the PRE-FIX screen reproduces the recorded rule and the current one does not; else None."""
    if not it["recorded_rule"]:
        return None
    pre = _pre_fix_screen().screen_record(it["rec"], (xa._cfg(it["slug"]).get("include") or {}), set())
    if pre.rule_id != it["recorded_rule"]:
        return None
    t_ = it["rec"].get("title") or ""
    return ("RANDOMISED_SUBSTUDY_VETOED_BY_TITLE" if re.search(r"\bsub-?study\b", t_, re.I)
            else "BODY_RCT_MISSED_RANDOMIZED_CONTROLLED_STUDY" if re.search(r"randomi[sz]ed,? controlled study",
                                                                          it["rec"].get("abstract") or "", re.I)
            else f"PRE_FIX_{pre.rule_id}_NOW_DIFFERS")


def resolve_inconsistent(it, now):
    """A recorded exclusion the single-record screen cannot reproduce, because the rule that made it is NOT a
    single-record rule, or the ruleset has since changed. Each case resolved by what it is:
      X-DEDUP     a companion report of a trial already pooled through another report: NOT_AN_EXCLUSION -- the trial is
                  in our pool; the tracker needs the identity binding (esketamine Trial D -> TRANSFORM-3)
      X-CONTRAST  the record STATES a contrast that is not the protocol's (metformin vs laparoscopic ovarian diathermy):
                  TRUE_SCOPE_DIFFERENCE, span = the record's comparison words
      other       the CURRENT ruleset's class for the record, the recorded/current rule drift stated"""
    rule, rec = it["recorded_rule"], it["rec"]
    cls0, sc0, base0 = now
    if rule == "X-DEDUP":
        return "NOT_AN_EXCLUSION", ("COMPANION_REPORT_OF_A_POOLED_TRIAL (recorded X-DEDUP: the trial is pooled through "
                                    "another report -- an identity binding for the tracker, not a scope difference)"), \
            dict(base0, rule_id=rule)
    if rule == "X-CONTRAST":
        sp = xa.span_of(rec, xa.COMPARISON_STATED, ("title", "abstract")) or xa.span_of(rec, xa.OTHER_COMP, ("title", "abstract"))
        if sp:
            return ("TRUE_SCOPE_DIFFERENCE", "CONTRAST_NOT_THE_PROTOCOLS (recorded X-CONTRAST; the record states its contrast)",
                    dict(base0, rule_id=rule, span=sp))
        return "INSUFFICIENT_RECORD", "CONTRAST_NOT_STATED_NO_SPAN (recorded X-CONTRAST)", dict(base0, rule_id=rule)
    if cls0 != "INCONSISTENT":
        return cls0, f"RECORDED_{rule}_NOW_{base0.get('rule_id')}: {sc0}", base0
    return "INCONSISTENT", sc0, base0


def main(argv):
    xa.load_reader()
    load_axes()
    load_axes2()
    pop = population([a for a in argv if not a.startswith("--")] or None)
    rows, tally, sub = [], Counter(), Counter()
    for it in pop:
        if it["blocker"] == "SCREENED_VIA_OTHER_REPORT" and it["via_decision"] == "include":
            cls, sc, base = "NOT_AN_EXCLUSION", "SCREENED_VIA_AN_INCLUDED_REPORT", {}
        elif not it["rec"]:
            cls, sc, base = "INSUFFICIENT_RECORD", "RECORD_NOT_HELD", {}
        else:
            cls, sc, base = xa.classify(it["rec"], xa._cfg(it["slug"]))
            now = (cls, sc, base)
            if cls != "INCONSISTENT" and it["recorded_rule"] and base.get("rule_id") != it["recorded_rule"]:
                cls, sc = "INCONSISTENT", f"RULE_{base.get('rule_id')}_NE_RECORDED_{it['recorded_rule']}"
            if cls == "INCONSISTENT":
                fx = fixed_since(it)
                if fx:
                    # the recorded exclusion came from a rule THIS change fixed: a screener error, already fixed. What
                    # remains is whatever the fixed screen does with the record, classified in its own right
                    rem = "now INCLUDED" if now[2].get("decision") == "include" or now[0] == "INCONSISTENT" and \
                        now[1] == "RULESET_INCLUDES" else f"now excluded by {now[2].get('rule_id')}: {now[0]}/{now[1][:90]}"
                    cls, sc, base = "SCREENER_ERROR", f"FIXED_IN_HARNESS ({fx}); {rem}", dict(base, rule_id=it["recorded_rule"])
                else:
                    cls, sc, base = resolve_inconsistent(it, now)
        shared = (cls, sc)
        refined_by = None
        if it["rec"] and cls not in ("INCONSISTENT", "NOT_AN_EXCLUSION"):
            cls, sc, refined_by = refine(it, cls, sc, base)
        # the SHARED span contract: a TRUE_SCOPE_DIFFERENCE stands only with the record's own words establishing it
        # (span, verbatim in the held record); a full-text span (R3) is kept but named as such -- the tracker's
        # verbatim check reads the held record, so it cannot name on it (proposed to the k-gap lane)
        span = (base or {}).get("span") if cls == "TRUE_SCOPE_DIFFERENCE" else None
        if cls == "TRUE_SCOPE_DIFFERENCE" and not (span or {}).get("text") and refined_by != "R3":
            cls, sc = "INSUFFICIENT_RECORD", f"{sc.split(' (')[0]}_NO_SPAN"
        tally[cls] += 1
        sub[(cls, sc.split(":")[0].split(" (")[0])] += 1
        rows.append({"slug": it["slug"], "label": it["label"], "pmid": it["pmid"], "found_as": it["found_as"],
                     "stage": "SCREENED_OUT" if it["blocker"].startswith("SCREENED_OUT") else it["blocker"],
                     "rule_id": base.get("rule_id") or it["recorded_rule"], "reason": (base.get("reason") or "")[:160],
                     "class": cls, "subclass": sc, "title": ((it["rec"] or {}).get("title") or "")[:140],
                     "has_abstract": bool((it["rec"] or {}).get("abstract")),
                     "shared_classifier": {"class": shared[0], "subclass": shared[1]}, "refined_by": refined_by,
                     "reader_axes": AXES.get(_key(it["slug"], it["pmid"])), "reader2_axes": AXES2.get(_key(it["slug"], it["pmid"])),
                     "readers_disagree": it.get("readers_disagree"), "span": span if cls == "TRUE_SCOPE_DIFFERENCE" else None})
    out = {"n": len(rows), "population": "every tracker trial blocked SCREENED_OUT_UNAUDITED or SCREENED_VIA_OTHER_REPORT",
           "by_class": dict(tally), "by_subclass": {f"{a}/{b}": v for (a, b), v in sorted(sub.items())}, "rows": rows}
    json.dump(out, open(OUT, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    md = ["# Exclusion audit over the G1 tracker population (generated by scripts/g1_exclusion_audit_tracker.py)", "",
          f"n = {out['n']} excluded comparator trials: every tracker trial the shared exclusion audit "
          f"(outputs/k_gap/exclusion_audit.json) does not cover. By class: {out['by_class']}.", "",
          "TRUE_SCOPE_DIFFERENCE = the record states the excluding fact (protocol rule named). SCREENER_ERROR = our screen "
          "is wrong (FIXED_IN_HARNESS where this change fixed the class). INSUFFICIENT_RECORD = the record lacks the "
          "fact; open full text was sought through the cascade (g1/data/audit_ft). Reader axes: the recorded, "
          "quote-verified second reading (c=comparator, d=design, i=intervention, p=population).", "",
          "| topic | comparator trial | PMID | rule | class | subclass | by | reader axes |", "|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["slug"], r["class"], r["label"])):
        ax = r.get("reader_axes") or {}
        md.append(f"| {r['slug']} | {r['label'][:40]} | {r['pmid']} | {r['rule_id']} | {r['class']} | "
                  f"{r['subclass'][:150].replace('|', '/')} | {r.get('refined_by') or 'shared'} | "
                  f"{', '.join(f'{k[0]}={v}' for k, v in sorted(ax.items())) or '-'} |")
    open(os.path.join(ROOT, "g1", "EXCLUSION_AUDIT.md"), "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
    print(json.dumps({k: out[k] for k in ("n", "by_class", "by_subclass")}, indent=1))


# ------------------------------------------------------------------ second reader (recorded codex), same instrument
READER_PROP = os.path.join(ROOT, "registry", "model_proposals", "k_gap_screen_recheck.tracker.json")


def reader_items():
    """The k-gap second reader's items (scripts/k_gap_screen_recheck.py: same prompt, schema and verify_screening
    gate), for the TRACKER population instead of the counterfactual funnel."""
    import k_gap_screen_recheck as rc
    pilot = rc._pilot()
    out = []
    for it in population():
        if not it["rec"] or not it["recorded_rule"] or it["recorded_rule"] == "INCLUDE":
            continue
        t = pilot.held_text_screening(it["rec"])
        out.append({"slug": it["slug"], "item_id": f"{it['slug']}::tracker:{it['pmid']}", "pmid": it["pmid"],
                    "rule_decision": "exclude", "rule_id": it["recorded_rule"], "rule_reason": None,
                    "held_ref": f"cache/{it['slug']}/records.json#{it['pmid']} (or member_records.json)",
                    "held_text": t, "held_sha256": rc._sha(t.encode("utf-8"))})
    return out


READER2_PROP = READER_PROP.replace(".tracker.json", ".tracker.reader2.json")
READER2_MODEL = "gpt-5.5"


def reader_main(run, model=None, prop=None):
    import concurrent.futures as cf
    import k_gap_screen_recheck as rc
    from reproducible_ai import model_call_live, model_source as ms
    its = reader_items()
    bs = rc.batches(its)
    model = model or rc.MODEL
    prop = prop or READER_PROP
    data = xa._j(prop) if os.path.exists(prop) else {}
    runs = data.get("runs", {})

    def one(b):
        pilot = rc._pilot()
        rec = model_call_live.call(b["prompt"], schema=pilot._schema(rc.TASK), model=model, effort=rc.EFFORT,
                                   caller={"file": "scripts/g1_exclusion_audit_tracker.py", "line": "reader_main",
                                           "purpose": f"G1 exclusion audit reader {model} {b['batch']} (g1/tocilizumab lane)"},
                                   input_digests=b["digests"], timeout_s=1200)
        ms.write_record(rec, rc.REC_DIR)
        return {"batch": b["batch"], "record_id": rec["record_id"], "state": rec["state"], "prompt_sha256": rc._sha(b["prompt"])}
    if run:
        done = {r["prompt_sha256"] for r in runs.values() if r["state"] == "RAN_OK"}
        todo = [b for b in bs if rc._sha(b["prompt"]) not in done]
        print(f"items {len(its)}, batches {len(bs)}, to run {len(todo)}", flush=True)
        with cf.ThreadPoolExecutor(max_workers=int(os.environ.get("G1_CODEX_CONCURRENCY", "5"))) as ex:
            for r in ex.map(one, todo):
                runs[r["batch"]] = r
                print(r["batch"], r["state"], r["record_id"], flush=True)
    out = rc.verify(its, bs, runs)
    out["runs"] = runs
    out["task"] = "g1_exclusion_audit_tracker second reader"
    out["model"] = model
    json.dump(out, open(prop, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False, sort_keys=True)
    print(json.dumps({k: out[k] for k in ("N_items", "N_callable", "agreement")}, indent=1))


if __name__ == "__main__":
    # ONE stdout wrapper per process: a second wrapper over the same buffer is closed when the first is collected
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if "--reader2" in sys.argv:
        reader_main("--run" in sys.argv, READER2_MODEL, READER2_PROP)
    elif "--reader" in sys.argv:
        reader_main("--run" in sys.argv)
    else:
        main(sys.argv[1:])
