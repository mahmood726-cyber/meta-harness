"""G1 MISSING-TRIAL ACQUISITION: one RECORDED codex call per comparator trial we cannot yet match (concurrency 3),
replayed through deterministic gates. Nothing a model says is admitted until a gate finds it in the source.

Population: the trials of each topic's tracker file (default: the local tracker outputs; --ref=<git ref> reads a committed union) that are not matched and
not named out of scope, plus SECONDARY_SINGLE rows (a primary source would promote them). Never a comparator row.

Evidence per trial, in the source order of the goal, legitimate open sources only:
  1 AACT     the trial's posted results in the VERSIONED snapshot (kgap.aact_adapter.registry_for; snapshot id + digest)
  2 PMC OA   the trial's own open-access full text (k_gap_counterfactual.pmc_fulltext_cached: the harness fetcher, PMC OA
             bucket, sha256 in outputs/k_gap/fulltext_index.json). Shown whole up to FT_CAP; a longer text is shown as
             windows centred on the outcome terms -- and every gate searches the WHOLE text, never the window
  3 META     non-comparator meta rows the sweep / secondary tier already hold for the trial (state, values)
The comparator's own row is NEVER shown: the reader cannot copy it (anti-circularity).

Gates (replay; scripts/g1_tracker reads only ADMITTED rows), the 2 Oct decision restated 3 Oct (g1_tracker.
single_primary_source): a typed tuple bound to ONE PRIMARY source is PRIMARY-verified --
  TEXT   the quote is verbatim in the trial's whole open text; every count (or the effect AND both CI bounds) is printed
         verbatim in the quote; the secondary tier's typed matcher finds the tuple beside the topic's outcome terms
  AACT   the outcome passes the tracker's binding gates (named, same estimand, analysis set, composite) and the tuple is
         its posted participant counts or its posted two-sided effect (typed_match_registry); one time frame
  never  a source that IS the comparator (PMID); a META row (left to the secondary tier's SECONDARY_SINGLE admission)
A SCOPE claim is a candidate only (rule key + span verbatim in the trial's held text), never applied here.

    python scripts/g1_trial_acquire.py --run SLUG [SLUG ...]   (recorded calls, concurrency 3)
    python scripts/g1_trial_acquire.py [SLUG ...]              (replay + gates, no model calls)
-> registry/model_proposals/g1_trial_acquire.json (runs) and registry/g1_acquired/<slug>.json (gated rows)
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import html
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from reproducible_ai import model_call_live as mcl  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

PROP = os.path.join(ROOT, "registry", "model_proposals", "g1_trial_acquire.json")
ACQ_DIR = os.path.join(ROOT, "registry", "g1_acquired")
REC_DIR = os.path.join(ROOT, ms.RECORD_DIR)
MODEL, EFFORT = "gpt-6-astra", "high"
MODEL_2 = "gpt-5.5"                                  # the SECOND independent reader (READER_2)
FT_CAP = 60000
SOURCES = ["AACT", "PMC_TEXT", "REGULATORY", "META", "NONE"]
MEASURES = ["RR", "OR", "HR", "MD", "COUNTS", "NONE"]
VERDICTS = ["FOUND", "SOURCE_ABSENT", "SCOPE_DIFFERENCE", "UNSURE"]
_N = {"type": ["integer", "null"]}
_S = {"type": ["string", "null"]}
SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["verdict", "source", "source_ref", "aact_outcome_id", "outcome_as_stated", "timepoint_as_stated",
                 "population_as_stated", "measure", "events_t", "n_t", "events_c", "n_c", "effect", "lower", "upper",
                 "quote", "scope_rule_key", "scope_span", "why"],
    "properties": {"verdict": {"type": "string", "enum": VERDICTS}, "source": {"type": "string", "enum": SOURCES},
                   "source_ref": {"type": "string"}, "aact_outcome_id": _S, "outcome_as_stated": {"type": "string"},
                   "timepoint_as_stated": {"type": "string"}, "population_as_stated": {"type": "string"},
                   "measure": {"type": "string", "enum": MEASURES}, "events_t": _N, "n_t": _N, "events_c": _N, "n_c": _N,
                   "effect": _S, "lower": _S, "upper": _S, "quote": {"type": "string"}, "scope_rule_key": _S,
                   "scope_span": _S, "why": {"type": "string"}},
}
INSTR = """You read ONE randomised trial's own open sources to find its result for a meta-analysis outcome. Sources are
inline below; use nothing else (no files, no memory of the paper). Order: the AACT posted results first, then the trial's
own open full text (PMC, or an open-access copy found by Unpaywall), then a regulatory document (an FDA review or
label, an EMA assessment report, a NICE committee paper or evidence review -- shown as windows of the document around
where the trial is named), then the meta rows (a meta row is never the trial's own result: report it only if nothing
primary exists). A regulator's number counts only for the protocol's estimand, population, timepoint and the trial's
whole randomised population.
The result must be for the trial's RANDOMISED population: if the AACT posting covers only a subset (a site, a unit, a
stratum: compare its denominators with the randomised total the text states), use the full text instead.

Return the trial's result for the OUTCOME (name, keywords, estimand, timepoint, population as given) for experimental vs
control:
  - counts: events_t/n_t (experimental), events_c/n_c (control) as WHOLE numbers printed in the source -- never computed
    from a percentage, never from a figure, never a rate; or
  - an effect: measure + effect + lower + upper exactly as printed (two-sided 95% CI only).
quote = an EXACT substring of the source shown (copy it character for character; it must contain every number you give).
For AACT give source_ref = the NCT and aact_outcome_id = the outcome id shown; for the text source_ref = PMID; for a
regulatory review source_ref = its url exactly as shown, and the quote must come from ONE window and be about THIS trial
(a review discusses several studies: never take another study's row).
If the outcome, timepoint or population differ from the protocol, say so in why (do not stretch a definition). If the
trial is outside the protocol (scope), verdict SCOPE_DIFFERENCE with scope_rule_key (a key of the protocol given) and
scope_span (an exact substring of the trial's text stating it). If no open source states the result, SOURCE_ABSENT and
say what is missing. Never guess a number. Be terse."""


def _git_show(ref, path):
    p = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL)
    return p.stdout.decode("utf-8") if p.returncode == 0 else None


def tracker_file(slug, ref):
    s = _git_show(ref, f"outputs/k_gap/g1/{slug}.json") if ref else None
    if s is None:
        s = open(os.path.join(ROOT, "outputs", "k_gap", "g1", f"{slug}.json"), encoding="utf-8").read()
    return json.loads(s)


def targets(slug, ref):
    """Trials to acquire: not matched and not named, or matched only as SECONDARY_SINGLE (a primary would promote it)."""
    import g1_tracker as gt
    o = tracker_file(slug, ref)
    out = []
    for x in o["trials"]:
        if x.get("scope_difference") or x.get("in_our_pool"):
            continue
        if gt.is_matched(x) and x.get("route") != "SECONDARY_SINGLE":
            continue
        fam = str(x.get("family") or "")
        pmid = fam.replace("PMID ", "") if fam.startswith("PMID ") else (x.get("seeded_funnel") or {}).get("pmid")
        ncts = {c.get("nct") for c in ((x.get("registry_binding") or {}).get("candidates") or []) if c.get("nct")} \
            | ({fam} if fam.startswith("NCT") else set()) | registered_ncts(pmid)
        ncts = sorted(n for n in ncts if n)
        pmid_by = "TRACKER" if pmid else None
        if not pmid and len(ncts) == 1:
            # no report PMID on the row (tocilizumab's served rows carry the acronym only): the registration's OWN
            # results reference, when it lists exactly one (AACT study_references type RESULT); several -> none chosen
            rp_ = result_pmids(ncts).get(ncts[0]) or []
            if len(rp_) == 1:
                pmid, pmid_by = rp_[0], "AACT_RESULT_REFERENCE"
        out.append({"slug": slug, "label": x["label"], "pmid": pmid, "ncts": ncts, "route_now": x.get("route"),
                    "blocker_now": x.get("blocker"), "pmid_by": pmid_by})
    return o, out


_TABLE = None
RREF = os.path.join(ROOT, "outputs", "k_gap", "_reg", "aact_result_refs.json")


def result_pmids(ncts):
    """NCT -> the PMIDs its registration lists as RESULT references (AACT study_references; cached, gitignored)."""
    from harness import aact
    d = json.load(open(RREF, encoding="utf-8")) if os.path.exists(RREF) else {}
    want = {n for n in ncts if n and n not in d}
    if want:
        snap = aact.snapshot_dir(None)
        got = {n: [] for n in want}
        if snap:
            for r in aact._iter_rows(os.path.join(snap, "study_references.txt")):
                if r.get("nct_id") in got and (r.get("reference_type") or "").upper() == "RESULT" and r.get("pmid"):
                    got[r["nct_id"]].append(str(r["pmid"]).strip())
        d.update({n: sorted(set(v)) for n, v in got.items()})
        os.makedirs(os.path.dirname(RREF), exist_ok=True)
        json.dump(d, open(RREF, "w", encoding="utf-8"), indent=0, sort_keys=True)
    return {n: d.get(n) or [] for n in ncts}



def registered_ncts(pmid):
    """NCTs for a trial report: PubMed's OWN databank link (k_gap_table.pubmed_ncts, cached) and the k-gap table's rows
    that carry this PMID (the corticosteroid trials' main rows hold no registry candidate: CoDEX = NCT04327401)."""
    global _TABLE
    if not pmid:
        return set()
    import k_gap_table as kt
    out = {(kt.pubmed_ncts([pmid]).get(pmid) or "").upper()} - {""}
    if _TABLE is None:
        p = os.path.join(ROOT, "outputs", "k_gap", "k_gap_table.json")
        _TABLE = json.load(open(p, encoding="utf-8"))["trials"] if os.path.exists(p) else []
    for r in _TABLE:
        if pmid in (r.get("pmids") or []) and len(r.get("ncts") or []) == 1:
            out |= set(r["ncts"])
    return out


def outcome_row_terms(cfg):
    """Outcome terms that name the EVENT, for a table row label: the topic's keywords minus any that are also its
    population vocabulary (crystalloids' keywords carry 'ICU' / 'intensive care', which named SMART's baseline row
    'Another ICU within hospital' and the sub-row 'Before ICU discharge' as mortality rows)."""
    pop = {str(x).lower() for x in ((cfg.get("include") or {}).get("population_any") or [])}
    return [k for k in outcome_terms(cfg) if k.lower() not in pop]


def outcome_terms(cfg):
    from harness import extract
    po = cfg.get("primary_outcome") or {}
    return [k for k in (po.get("keywords") or []) if k and k.lower() not in extract.GENERIC_ANCHORS]


DETAIL = os.path.join(ROOT, "outputs", "k_gap", "_aact_detail.json")
_OUT_COLS = ("description", "population", "units", "units_analyzed", "param_type")
_AN_COLS = ("ci_n_sides", "ci_percent", "method", "estimate_description", "groups_description", "param_type",
            "param_value", "ci_lower_limit", "ci_upper_limit")


import threading
_DETAIL_LOCK = threading.Lock()


def aact_detail(ncts):
    with _DETAIL_LOCK:
        return _aact_detail(ncts)


def _aact_detail(ncts):
    """Per outcome id: the snapshot's outcome description / analysis population / units, and each analysis's CI
    sidedness + percent + method + estimate description (one streaming pass over outcomes + outcome_analyses for the
    NCTs not yet cached; gitignored cache keyed by snapshot). TECOS's reader could not tell a two-sided CI or the MACE
    components without them."""
    from harness import aact
    snap = aact.snapshot_dir(None)
    d = json.load(open(DETAIL, encoding="utf-8")) if os.path.exists(DETAIL) else {}
    if d.get("snapshot") != snap or d.get("v") != 2:
        d = {"snapshot": snap, "v": 2, "ncts": {}}
    want = {n for n in ncts if n and n not in d["ncts"]}
    if want and snap:
        got = {n: {"outcomes": {}, "analyses": {}} for n in want}
        for r in aact._iter_rows(os.path.join(snap, "outcomes.txt")):
            n = r.get("nct_id")
            if n in want:
                got[n]["outcomes"][str(r.get("id"))] = {k: (r.get(k) or "")[:600] for k in _OUT_COLS}
        for r in aact._iter_rows(os.path.join(snap, "outcome_analyses.txt")):
            n = r.get("nct_id")
            if n in want:
                got[n]["analyses"].setdefault(str(r.get("outcome_id")), []).append(
                    {k: (r.get(k) or "")[:400] for k in _AN_COLS})
        for r in aact._iter_rows(os.path.join(snap, "outcome_measurements.txt")):
            n = r.get("nct_id")
            if n in want:
                got[n].setdefault("measurements", {}).setdefault(str(r.get("outcome_id")), []).append(
                    {k: (r.get(k) or "")[:200] for k in ("result_group_id", "title", "units", "param_type", "param_value",
                                                         "classification", "category")})
        d["ncts"].update(got)
        tmp = DETAIL + f".{os.getpid()}.tmp"           # atomic: a reader never sees a half-written cache
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False)
        os.replace(tmp, DETAIL)
    return {n: d["ncts"].get(n) or {} for n in ncts}


def aact_evidence(ncts):
    from kgap import aact_adapter
    det = aact_detail(ncts)
    out = {}
    for n in ncts:
        try:
            aact_adapter.ensure([n])
            reg = aact_adapter.registry_for(n)
        except Exception as exc:  # noqa: BLE001 - a missing snapshot is recorded, never guessed around
            out[n] = {"state": "SNAPSHOT_UNAVAILABLE", "why": str(exc)[:160]}
            continue
        if not reg:
            out[n] = {"state": "NO_POSTED_RESULTS"}
            continue
        outs = []
        dn = det.get(n) or {}
        for oid, o in reg["outcomes"].items():
            outs.append({"outcome_id": oid, "type": o.get("type"), "title": o.get("title"), "time_frame": o.get("time_frame"),
                         "detail": (dn.get("outcomes") or {}).get(str(oid)),
                         "analysis_detail": (dn.get("analyses") or {}).get(str(oid)),
                         "groups": [{"group": g.get("group"), "title": reg["group_titles"].get(str(g.get("group"))),
                                     "count": g.get("count"), "n": g.get("n")} for g in reg["groups"].get(oid) or []],
                         # each analysis's groups BY TITLE: CORIMUNO (NCT04331808) posts HRs per stratum with no
                         # measurement rows, so ids alone left the reader unable to tell severe from critical
                         "analyses": [dict({k: a.get(k) for k in ("param_type", "param_value", "ci_lower", "ci_upper",
                                                                  "groups")},
                                           group_titles=[reg["group_titles"].get(str(g)) for g in a.get("groups") or []])
                                      for a in reg["analyses"] if a.get("outcome_id") == oid]})
        out[n] = {"state": "POSTED", "snapshot": reg.get("_snapshot"), "outcomes": outs[:60], "_reg": reg}
    return out


OPEN_COPY = ("CC", "PMC_AUTHOR_MANUSCRIPT")      # copies the DETERMINISTIC reader may admit a row from
PROMPT_COPY = ("CC",)                           # copies a model may be shown (the prompt is stored in a public record)


def pmc_copy(pmid):
    """Which copy of the trial's text we hold, and under what terms: {pmcid, url, licence, statement}. licence is
      CC                     a Creative Commons licence in the PMC permissions (redistributable: may enter a prompt)
      PMC_AUTHOR_MANUSCRIPT  a PMC author manuscript ('available for text mining ... fair use'): a legitimately open
                             copy for deterministic reading (text mining), never redistributed -- SMART PMC5846085
      NOT_OPEN               anything else, or terms that could not be read (never assumed open)
    Read once from the PMC XML and cached in outputs/k_gap/fulltext_index.json (terms only, never text)."""
    import time
    from harness import http, fetch
    ip = os.path.join(ROOT, "outputs", "k_gap", "fulltext_index.json")
    idx = json.load(open(ip, encoding="utf-8")) if os.path.exists(ip) else {}
    e = idx.get(pmid) or {}
    pmcid = e.get("pmcid")
    if not pmcid:
        return {"pmcid": None, "url": None, "licence": "NOT_OPEN", "statement": None}
    url = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
    if e.get("copy_licence"):
        return {"pmcid": pmcid, "url": url, "licence": e["copy_licence"], "statement": e.get("copy_statement")}
    xml = ""
    for attempt in range(3):
        try:
            time.sleep(0.4 + attempt)
            xml = http.get_text(f"{fetch.EUTILS}/efetch.fcgi", {"db": "pmc", "id": pmcid, "retmode": "xml",
                                                                "tool": "meta-harness", "email": "meta-harness@example.org"})
            break
        except Exception:  # noqa: BLE001 - unread terms are NOT_OPEN, never assumed open
            xml = ""
    perm = " ".join(re.findall(r"<permissions>.*?</permissions>", xml, re.S))
    stmt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", perm)).strip()[:300] or None
    if re.search(r"creativecommons\.org/(?:licenses|publicdomain)/", perm):
        lic = "CC"
    elif re.search(r"available for text mining", stmt or "", re.I) and re.search(r'article-type="[^"]*"', xml) and \
            re.search(r"\bmanuscript\b", xml, re.I):
        lic = "PMC_AUTHOR_MANUSCRIPT"
    else:
        lic = "NOT_OPEN"
    if xml:
        idx = json.load(open(ip, encoding="utf-8")) if os.path.exists(ip) else {}
        idx.setdefault(pmid, {}).update(copy_licence=lic, copy_statement=stmt)
        with open(ip, "w", encoding="utf-8") as fh:
            json.dump(idx, fh, indent=1, sort_keys=True)
    return {"pmcid": pmcid, "url": url, "licence": lic, "statement": stmt}


def pmc_licence(pmid):
    """'CC' / 'PMC_AUTHOR_MANUSCRIPT' / 'NOT_OPEN' (pmc_copy)."""
    return pmc_copy(pmid)["licence"]


def text_evidence(pmid, terms):
    """(whole text, shown text, sha256). Shown = whole when short; else windows centred on the outcome terms."""
    import k_gap_counterfactual as cfm
    t = cfm.pmc_fulltext_cached(pmid) if pmid else ""
    if not t:
        return "", "", None
    sha = hashlib.sha256(t.encode("utf-8")).hexdigest()
    if len(t) <= FT_CAP:
        return t, t, sha
    rx = re.compile("|".join(re.escape(k) for k in terms) or r"$^", re.I)
    spans = sorted({(max(0, m.start() - 1500), m.end() + 1500) for m in rx.finditer(t)})
    merged = []
    for a, b in spans:
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    shown, used = [], 0
    for a, b in merged:
        if used >= FT_CAP:
            break
        shown.append(f"[... characters {a}-{b} ...]\n" + t[a:b])
        used += b - a
    return t, "\n".join(shown)[:FT_CAP + 2000], sha


def meta_evidence(slug, label):
    p = os.path.join(ROOT, "outputs", "k_gap", "sweep", f"{slug}.json")
    rows = []
    if os.path.exists(p):
        for t in json.load(open(p, encoding="utf-8")).get("trials") or []:
            if t.get("label") == label:
                rows = [{k: r.get(k) for k in ("meta", "state", "measure", "effect", "lower", "upper", "events_t", "n_t",
                                              "events_c", "n_c")} for r in t.get("rows") or []]
    return rows


def unpaywall_evidence(pmid, terms):
    """(whole, shown, sha, doi, licence): the trial report's open-access copy found by Unpaywall (kgap.k_gap.unpaywall_text,
    cached), when PMC holds none. Its licence is Unpaywall's for the DOI ('cc-*' may be shown to a model)."""
    from reproducible_ai import record_licence as rl
    from kgap import k_gap
    doi = rl.pmid_doi(pmid) if pmid else None
    if not doi:
        return "", "", None, None, None
    try:
        u = k_gap.unpaywall_text(doi, os.path.join(ROOT, "outputs", "k_gap", "_upw"),
                                 os.path.join(ROOT, "outputs", "k_gap", "unpaywall_text_index.json"), offline=False)
    except Exception:  # noqa: BLE001 - no copy is a result, never a guess
        return "", "", None, doi, None
    t = u.get("text") or ""
    if len(t) < 3000:
        return "", "", None, doi, None
    lic = rl.doi_licences().get(doi)
    shown = t if len(t) <= FT_CAP else _windows(t, terms)
    return t, shown, hashlib.sha256(t.encode("utf-8")).hexdigest(), doi, lic


def _windows(t, terms):
    rx = re.compile("|".join(re.escape(k) for k in terms) or r"$^", re.I)
    spans = sorted({(max(0, m.start() - 1500), m.end() + 1500) for m in rx.finditer(t)})
    merged = []
    for a, b in spans:
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    out, used = [], 0
    for a, b in merged:
        if used >= FT_CAP:
            break
        out.append(f"[... characters {a}-{b} ...]\n" + t[a:b])
        used += b - a
    return "\n".join(out)[:FT_CAP + 2000]


def evidence(t, cfg, comp):
    terms = outcome_terms(cfg)
    aact = aact_evidence(t["ncts"])
    whole, shown, sha = text_evidence(t["pmid"], terms)
    origin, doi, ulic = ("PMC", None, None) if whole else ("UNPAYWALL", None, None)
    if not whole:
        whole, shown, sha, doi, ulic = unpaywall_evidence(t["pmid"], terms)
    po = cfg.get("primary_outcome") or {}
    ev = {"trial": t["label"], "pmid": t["pmid"], "ncts": t["ncts"],
          "outcome": {k: po.get(k) for k in ("name", "keywords", "estimand", "timepoint", "population")},
          "protocol_include": cfg.get("include"), "protocol_arm_object": cfg.get("arm_object"),
          "eligibility_summary": cfg.get("eligibility_summary"),
          "aact": {n: {k: v for k, v in a.items() if k != "_reg"} for n, a in aact.items()},
          "full_text": ({"pmid": t["pmid"], "sha256": sha, "chars": len(whole), "shown_chars": len(shown), "text": shown}
                        if whole and origin == "PMC" and pmc_licence(t["pmid"]) in PROMPT_COPY else
                        # an Unpaywall copy is shown only under a CC licence; the DOI (not the PMID) names it, so the
                        # licence guard checks the DOI's Unpaywall licence
                        {"doi": doi, "licence": ulic, "sha256": sha, "chars": len(whole), "shown_chars": len(shown),
                         "text": shown} if whole and origin == "UNPAYWALL" and str(ulic or "").startswith("cc") else
                        {"state": "HELD_NOT_OPEN_LICENSED", "note": "held for the deterministic gates; never shown"}
                        if whole else {"state": "NO_OPEN_FULL_TEXT"}),
          "meta_rows": meta_evidence(t["slug"], t["label"])}
    reg_shown, reg_held = regulatory_evidence(t, terms)
    if reg_shown:
        ev["regulatory"] = reg_shown
    return ev, {"aact": aact, "text": whole, "sha": sha, "terms": terms, "comp": comp, "pmid": t["pmid"], "reg": reg_held,
                "slug": t["slug"], "text_origin": origin if whole else None, "doi": doi, "doi_licence": ulic}


def regulatory_evidence(t, terms):
    """FDA/EMA review documents held for the topic that NAME the trial (scripts/g1_regulatory_source.py): windows of
    prompt-open documents are shown; every naming document is held whole for the gate."""
    import g1_regulatory_source as rs
    try:
        return rs.regulatory_evidence(t, terms, t["slug"])
    except Exception as exc:  # noqa: BLE001 - no snapshot / no held documents: nothing regulatory, never a guess
        return [], {"_error": str(exc)[:160]}


def _ws(s):
    return re.sub(r"\s+", " ", html.unescape(s or "")).strip()


def _num_in(v, span):
    if v is None:
        return True
    return bool(re.search(rf"(?<![\d.,]){int(v):,}(?![\d])|(?<![\d.,]){int(v)}(?![\d])", span))


def _str_in(v, span):
    return v is None or bool(re.search(rf"(?<![\d.]){re.escape(str(v))}(?![\d])", span.replace("·", ".")))


_TOTAL = re.compile(r"(?<![\d.,])(\d{1,3}(?:,\d{3})+|\d{3,6})\s+(?:\w+\s+){0,3}?(?:patients|adults|participants|subjects|"
                    r"children|women|men|infants)\b", re.I)
_RANDOMISED_CTX = re.compile(r"randomi[sz]|enrol|underwent|assigned|total of|were included", re.I)
_SCREENED = re.compile(r"screen|assessed|eligib|approached|consider", re.I)


def posted_population_short(slug, pmid, posted_total):
    """The trial's randomised total as its OWN held record states it (a count of patients in a randomisation /
    enrolment sentence); when the posted denominators fall more than 10% short of the largest such total, the posted
    result is a subpopulation (SMART: 5381 posted vs '15,802 adults' randomised). None when the record states no total
    -- unknown is never treated as a mismatch."""
    import g1_tracker as gt
    rec = gt.held_record(slug, pmid) if pmid else None
    ab = (rec or {}).get("abstract") or ""
    best, span = None, None
    for s in re.split(r"(?<=\.)\s+", ab):
        if not _RANDOMISED_CTX.search(s):
            continue
        for m in _TOTAL.finditer(s):
            # the count's OWN clause must randomise / enrol it, never screen it: AFFIRM-AHF '1525 patients were screened,
            # of whom 1132 patients were randomly assigned' -- 1525 is not the randomised total
            clause = s[m.start(): m.end() + (re.search(r"[,;.]|$", s[m.end():]).start())]
            before = s[max(0, m.start() - 40): m.start()]
            if _SCREENED.search(clause) or not (_RANDOMISED_CTX.search(clause) or _RANDOMISED_CTX.search(before)):
                continue
            v = int(m.group(1).replace(",", ""))
            if best is None or v > best:
                best, span = v, s
    if best and posted_total < 0.9 * best:
        return {"posted_total": posted_total, "randomised_total": best, "record_span": span[:300], "pmid": pmid}
    return None


_COL_N = re.compile(r"\(\s*[Nn]\s*=\s*([\d,]+)\s*\)")
_CELL = re.compile(r"\|\s*([\d,]+)\s*\(\s*(\d+(?:\.\d+)?)\s*%?\s*\)")


def typed_match_table(quote, resp, terms):
    """A STRUCTURED TABLE in the trial's own text (the held text renders a JATS table as '|' rows): the column header
    states each arm's N ('(N = 7942)'), the outcome's row states each arm's count with its percentage ('818 (10.3)'),
    in the same column order. Admitted only when the row label names an outcome term, the counts and Ns are the
    proposal's in order, and EACH count is corroborated by its printed percentage (count / N rounds to it). SMART
    (PMC5846085, Table 2): 'In-hospital death before 30 days -- no. (%) | 818 (10.3) | 875 (11.1)' under
    'Balanced Crystalloids (N = 7942) | Saline (N = 7860)'."""
    ns = [int(x.replace(",", "")) for x in _COL_N.findall(quote or "")]
    if len(ns) < 2 or (ns[0], ns[1]) != (resp["n_t"], resp["n_c"]):
        return None
    rx = re.compile("|".join(re.escape(t) for t in terms if t) or r"$^", re.I)
    for line in (quote or "").splitlines():
        label = line.split("|")[0]
        cells = _CELL.findall(line)
        if not rx.search(label) or len(cells) < 2:
            continue
        (a, pa), (b, pb) = cells[0], cells[1]
        a, b = int(a.replace(",", "")), int(b.replace(",", ""))
        if (a, b) != (resp["events_t"], resp["events_c"]):
            continue
        if all(abs(round(100 * e / n, 1) - float(p)) <= 0.1 for e, n, p in ((a, ns[0], pa), (b, ns[1], pb))):
            return {"result": "TYPED_MATCH", "span": line.strip()[:300], "route": "TABLE_ROW_WITH_COLUMN_N"}
    return None


_TABLE_HEAD = re.compile(r"^[^\n]*\(\s*[Nn]\s*=\s*[\d,]+\s*\)[^\n]*\(\s*[Nn]\s*=\s*[\d,]+\s*\)[^\n]*$", re.M)


def table_tuple(text, terms, timepoint=None):
    """DETERMINISTIC: the outcome's row in a table of the trial's own held text (no model; for a text that may not be
    shown to one). A table = a header line with two arm Ns + the following '|' rows; a candidate row names an outcome
    term and passes typed_match_table (percent-corroborated). One candidate -> its tuple; several -> the one whose label
    names the protocol's timepoint number, else None (ambiguous is never a pick)."""
    cands = []
    for h in _TABLE_HEAD.finditer(text or ""):
        ns = [int(x.replace(",", "")) for x in _COL_N.findall(h.group(0))][:2]
        block = [h.group(0)]
        gap = 0
        for line in text[h.end():].splitlines()[1:60]:
            if "|" in line:
                gap = 0
                block.append(line)
            elif len(line.strip()) < 80 and gap < 1:
                gap += 1                  # a section label inside the table ('Components of primary outcome')
            else:
                break
        for line in block[1:]:
            cells = _CELL.findall(line)
            if len(cells) < 2:
                continue
            r = {"events_t": int(cells[0][0].replace(",", "")), "n_t": ns[0],
                 "events_c": int(cells[1][0].replace(",", "")), "n_c": ns[1]}
            m = typed_match_table(block[0] + "\n" + line, r, terms)
            if m:
                cands.append((line.split("|")[0].strip(), r, block[0] + "\n" + line))
    if len(cands) > 1 and timepoint:
        num = re.search(r"\d+", str(timepoint))
        if num:
            cands = [c for c in cands if re.search(r"\b" + num.group(0) + r"\b", c[0])] or cands
    uniq = {(c[1]["events_t"], c[1]["events_c"]) for c in cands}
    return cands[0] if len(uniq) == 1 else None


def gate(resp, held, cfg, slug):
    """ADMITTED (with basis) or REFUSED:<gate> for one model answer, against the held sources."""
    import g1_tracker as gt
    from harness import secondary_meta as sm
    po = cfg.get("primary_outcome") or {}
    est = (po.get("estimand") or "").upper()
    if resp["verdict"] == "SCOPE_DIFFERENCE":
        span = resp.get("scope_span") or ""
        key = str(resp.get("scope_rule_key") or "").replace("include.", "")
        rule = (cfg.get("include") or {}).get(key, cfg.get(key))
        if not rule:
            # the rule must APPLY: iv-iron's design_double_blind is false, so 'open-label' names nothing (EFFECT-HF)
            return "REFUSED:SCOPE_RULE_NOT_SET_IN_PROTOCOL", None
        ok = bool(span) and _ws(span) in _ws(held["text"])
        return ("SCOPE_CANDIDATE" if ok else "REFUSED:SCOPE_SPAN_NOT_VERBATIM"), None
    if resp["verdict"] != "FOUND":
        return resp["verdict"], None
    src = resp["source"]
    if src == "META":
        return "META_CANDIDATE", None
    if str(resp.get("source_ref") or "").strip() in {str(held["comp"]), f"PMID {held['comp']}"}:
        return "REFUSED:SOURCE_IS_COMPARATOR", None
    counts = None not in (resp["events_t"], resp["n_t"], resp["events_c"], resp["n_c"])
    effect = None not in (resp["effect"], resp["lower"], resp["upper"])
    if not (counts or effect):
        return "REFUSED:TUPLE_NOT_TYPED", None
    measure = est if resp["measure"] in ("COUNTS", "NONE") else resp["measure"]
    row = sm.SecondaryRow(meta_pmid="ACQUIRED", meta_doi="", location={}, source_digest="", provenance="MODEL_READ",
                          trial_label="", measure=measure, outcome_definition="",
                          effect=resp["effect"] if effect else None, lower=resp["lower"] if effect else None,
                          upper=resp["upper"] if effect else None, events_t=resp["events_t"] if counts else None,
                          n_t=resp["n_t"] if counts else None, events_c=resp["events_c"] if counts else None,
                          n_c=resp["n_c"] if counts else None)
    if src == "PMC_TEXT":
        q = _ws(resp["quote"])
        if not held["text"] or not q or q not in _ws(held["text"]):
            return "REFUSED:QUOTE_NOT_VERBATIM_IN_WHOLE_TEXT", None
        nums_ok = (all(_num_in(resp[k], q) for k in ("events_t", "n_t", "events_c", "n_c")) if counts else True) and \
                  (all(_str_in(resp[k], q) for k in ("effect", "lower", "upper")) if effect else True)
        if not nums_ok:
            return "REFUSED:NUMBERS_NOT_IN_QUOTE", None
        m = sm.typed_match_text(row, held["text"], held["terms"], f"PMID {resp['source_ref']}")
        if not m and counts:
            m = typed_match_table(resp["quote"], resp, held["terms"])
        if not m:
            return "REFUSED:TYPED_MATCH_NOT_FOUND_BESIDE_OUTCOME_TERMS", None
        return "ADMITTED", {"kind": "TEXT", "source": f"PMID {resp['source_ref']} PMC OA full text sha256 {held['sha']}",
                            "span": m.get("span"), "quote": resp["quote"], "row": row}
    if src == "REGULATORY":
        return regulatory_gate(resp, held, row, counts, effect)
    if src == "AACT":
        n = str(resp.get("source_ref") or "").strip()
        a = (held["aact"].get(n) or {})
        reg = a.get("_reg")
        if not reg:
            return "REFUSED:NO_POSTED_RESULTS_FOR_NCT", None
        oid = str(resp.get("aact_outcome_id") or "")
        o = reg["outcomes"].get(oid)
        if not o:
            return "REFUSED:AACT_OUTCOME_ID_UNKNOWN", None
        an = next((x for x in reg["analyses"] if x.get("outcome_id") == oid), None)
        groups = reg["groups"].get(oid) or []
        bv = gt.binding_verdict(po.get("name") or "", list(po.get("keywords") or []), o.get("title"),
                                len({g["group"] for g in groups}), is_primary=(o.get("type") or "").upper() == "PRIMARY",
                                analysis=an, estimand=po.get("estimand"), population=po.get("population"))
        if bv["verdict"] != "BINDABLE":
            return f"REFUSED:AACT_{bv['gate']}", None
        tf = str(o.get("time_frame") or "")
        if "," in tf or " and " in tf:
            return "REFUSED:AACT_MULTIPLE_TIME_FRAMES", None
        if counts:
            short = posted_population_short(slug, held.get("pmid"), resp["n_t"] + resp["n_c"])
            if short:
                # SMART (NCT02444988) posts its MEDICAL-ICU subset, 2735 + 2646 = 5381, while its report randomised 15,802
                return "REFUSED:POSTED_N_IS_A_SUBPOPULATION", {"note": short}
        one = {"outcomes": {oid: o}, "analyses": [x for x in reg["analyses"] if x.get("outcome_id") == oid],
               "groups": {oid: groups}}
        # identity is the binding gate's (named / estimand / analysis set / composite): the matcher checks the NUMBERS,
        # so it is given the outcome's own title (HEART-FID's 'Number of Hospitalizations for Heart Failure' is named
        # by the topic's outcome NAME, not by a literal keyword substring)
        m = sm.typed_match_registry(row, one, [o.get("title") or ""], f"{n} outcome {oid}")
        if not m:
            return "REFUSED:TUPLE_NOT_THE_POSTED_RESULT", None
        return "ADMITTED", {"kind": "AACT", "source": f"AACT {(a.get('snapshot') or {}).get('id')} {n} outcome {oid}",
                            "span": m.get("span"), "quote": resp["quote"], "row": row, "time_frame": tf}
    return "REFUSED:UNKNOWN_SOURCE", None


def regulatory_gate(resp, held, row, counts, effect):
    """A regulatory review's tuple: the url must be a HELD typed source record whose text digest still matches; the quote
    verbatim in the WHOLE document (not the window shown); every number in the quote; the trial NAMED near the quote; the
    typed tuple beside the outcome terms. Admitted kind REGULATORY with url, digests and the host-derived licence."""
    from harness import secondary_meta as sm
    import g1_regulatory_source as rs
    url = str(resp.get("source_ref") or "").strip()
    h = (held.get("reg") or {}).get(url)
    if not h or not rs.agency_of(url):
        return "REFUSED:REGULATORY_DOC_NOT_HELD", None
    doc = h["text"]
    if rs.text_sha256(doc) != h["record"].get("text_sha256"):
        return "REFUSED:REGULATORY_DIGEST_MISMATCH", None
    q = _ws(resp.get("quote"))
    if not q or q not in _ws(doc):
        return "REFUSED:QUOTE_NOT_VERBATIM_IN_WHOLE_DOCUMENT", None
    nums_ok = (all(_num_in(resp[k], q) for k in ("events_t", "n_t", "events_c", "n_c")) if counts else True) and \
              (all(_str_in(resp[k], q) for k in ("effect", "lower", "upper")) if effect else True)
    if not nums_ok:
        return "REFUSED:NUMBERS_NOT_IN_QUOTE", None
    if rs.quote_named_and_located(doc, resp["quote"], h["names"]) is None:
        return "REFUSED:TRIAL_NOT_NAMED_NEAR_QUOTE", None
    if counts and held.get("slug"):
        short = posted_population_short(held["slug"], held.get("pmid"), resp["n_t"] + resp["n_c"])
        if short:
            return "REFUSED:REGULATORY_N_IS_A_SUBPOPULATION", {"note": short}
    m = sm.typed_match_text(row, doc, held["terms"], url)
    if not m and counts:
        m = typed_match_table(resp["quote"], resp, held["terms"])
    if not m:
        return "REFUSED:TYPED_MATCH_NOT_FOUND_BESIDE_OUTCOME_TERMS", None
    rec = h["record"]
    return "ADMITTED", {"kind": "REGULATORY",
                        "source": f"{rec['agency']} review {url} doc sha256 {rec.get('doc_sha256')} text sha256 "
                                  f"{rec.get('text_sha256')} ({rec.get('licence')})",
                        "url": url, "agency": rec["agency"], "licence": rec.get("licence"),
                        "doc_sha256": rec.get("doc_sha256"), "text_sha256": rec.get("text_sha256"),
                        "span": m.get("span"), "quote": resp["quote"], "row": row}


_PEOPLE = re.compile(r"^\s*(?:number of |count of )?(?:participants?|subjects?|patients?|people|persons?)", re.I)


def _comparator_row(o, label):
    return next((x.get("comparator_row") for x in o.get("trials") or [] if x.get("label") == label), None)


def comparator_counts_are_events(cr, ncts):
    """When the comparator's own per-arm counts for this trial are the posted measurements of an outcome whose units are
    NOT participants (AFFIRM-AHF: 217 vs 294 = 'HF Hospitalisations', units Events), name it: the comparator pooled
    event counts over participant denominators. Deterministic, at replay; the reader never saw the comparator row."""
    if not cr or cr.get("events_t") is None or cr.get("events_c") is None:
        return None
    want = {str(cr["events_t"]), str(cr["events_c"])}
    for n, d in aact_detail(ncts).items():
        for oid, ms_ in ((d or {}).get("measurements") or {}).items():
            vals = {str(m.get("param_value") or "").split(".")[0] for m in ms_}
            units = {m.get("units") or "" for m in ms_}
            if want <= vals and units and not any(_PEOPLE.search(u) for u in units):
                return {"finding": "COMPARATOR_COUNTS_ARE_POSTED_EVENTS", "nct": n, "outcome_id": oid,
                        "title": ms_[0].get("title"), "units": sorted(units), "comparator_counts": sorted(want)}
    return None


def comparator_pmid(slug, o):
    return str(o.get("comparator_pmid") or "")


def typed_first(t, cfg, held):
    """DETERMINISTIC sources before any model: (verdict, admitted) or (None, None). (1) the trial's own held text's
    outcome table row (table_tuple) from a legitimately open copy (PMC CC / author manuscript, or a CC Unpaywall copy);
    (2) a regulator's counts (g1_regulatory_source.regulatory_typed: one trial-named line, two corroborated e/N (p%)
    cells, arms ordered by a header naming both), under the randomised-N check."""
    import g1_regulatory_source as rs
    from harness import secondary_meta as sm_
    po = cfg.get("primary_outcome") or {}
    est = (po.get("estimand") or "").upper()
    terms = outcome_row_terms(cfg)

    def row(rr, label_):
        return sm_.SecondaryRow(meta_pmid="ACQUIRED", meta_doi="", location={}, source_digest="", provenance="TABLE_ROW",
                                trial_label="", measure=est, outcome_definition=label_, **rr, effect=None, lower=None,
                                upper=None)
    if held.get("text"):
        if held.get("text_origin") == "PMC":
            ok, copy = pmc_copy(t["pmid"])["licence"] in OPEN_COPY, pmc_copy(t["pmid"])
        else:
            ok, copy = str(held.get("doi_licence") or "").startswith("cc"), {"doi": held.get("doi"),
                                                                            "licence": held.get("doi_licence")}
        tt = table_tuple(held["text"], terms, po.get("timepoint")) if ok else None
        if tt and not posted_population_short(t["slug"], t["pmid"], tt[1]["n_t"] + tt[1]["n_c"]):
            return "ADMITTED", {"kind": "TEXT_TABLE", "source": f"{held.get('text_origin')} held full text sha256 "
                                                                f"{held['sha']} (read deterministically: table_tuple)",
                                "source_copy": copy, "span": tt[2][:600], "quote": None, "row": row(tt[1], tt[0])}
    reg = {k: v for k, v in (held.get("reg") or {}).items() if not k.startswith("_")}
    if reg and est in ("RR", "OR", "RD"):
        g = rs.regulatory_typed(reg, terms, cfg.get("intervention_terms") or [], cfg.get("comparator_terms") or [])
        if g:
            url, rec, rr, line = g
            if not posted_population_short(t["slug"], t["pmid"], rr["n_t"] + rr["n_c"]):
                return "ADMITTED", {"kind": "REGULATORY_TABLE", "source": f"{rec['agency']} {url} doc sha256 "
                                    f"{rec.get('doc_sha256')} text sha256 {rec.get('text_sha256')} ({rec.get('licence')}; "
                                    f"read deterministically: regulatory_typed)", "url": url, "agency": rec["agency"],
                                    "licence": rec.get("licence"), "doc_sha256": rec.get("doc_sha256"),
                                    "text_sha256": rec.get("text_sha256"), "span": line[:600], "quote": None,
                                    "row": row(rr, line[:120])}
    return None, None


MIN_FREE_GB = 5.0
_QUOTA = re.compile(r"usage limit|quota|insufficient[_ ]credits|out of credits|rate limit|You've hit your", re.I)


def disk_ok(drives=("C:\\", "F:\\")):
    """Every drive present has at least MIN_FREE_GB free (Mahmood 6 Oct: run while C: and F: each have >= 5 GB)."""
    import shutil
    for d in drives:
        if os.path.exists(d) and shutil.disk_usage(d).free < MIN_FREE_GB * 1e9:
            return False
    return True


class RunnerPool:
    """Codex slots: `local` on this machine (model_call_live.codex_runner) and `remote` on the Tailscale worker
    (reproducible_ai/model_call_remote.RemoteCodexRunner). A call takes whichever slot is free; the record names the
    client that ran it."""

    def __init__(self, local=5, remote=0, remote_runner=None):
        import queue
        self.q = queue.Queue()
        for _ in range(local):
            self.q.put(mcl.codex_runner)
        if remote:
            if remote_runner is None:
                from reproducible_ai import model_call_remote as mr
                remote_runner = mr.RemoteCodexRunner()
            for _ in range(remote):
                self.q.put(remote_runner)
        self.size = max(1, local + remote)

    def call(self, *a, **kw):
        runner = self.q.get()
        try:
            return mcl.call(*a, runner=runner, **kw)
        finally:
            self.q.put(runner)


def run(slugs, ref, redo=(), workers=5, remote_workers=0):
    """A trial already answered is asked again only when its evidence CHANGED (a new prompt digest: a new source in the
    cascade) or its label matches a --redo=<substring>. Deterministic sources first (typed_first: no model call). Calls
    stop on a disk below MIN_FREE_GB or a quota error (budget stop), recorded per trial, never silently."""
    data = json.load(open(PROP, encoding="utf-8")) if os.path.exists(PROP) else {"runs": {}}
    jobs = []
    for slug in slugs:
        cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
        o, ts = targets(slug, ref)
        for t in ts:
            jobs.append((slug, cfg, comparator_pmid(slug, o), t))

    # ONE detail pass for every job's NCTs before the pool (three threads each streaming 3 GB, and racing on one cache
    # file, corrupted it: 'Extra data: line 1 column 90017')
    aact_detail(sorted({n for _s, _c, _p, t in jobs for n in t["ncts"]}))

    import threading
    stop = threading.Event()
    pool = RunnerPool(workers, remote_workers)

    def one(job):
        slug, cfg, comp, t = job
        key = f"{slug}|{t['label']}"
        prev = data["runs"].get(key) or {}
        base = {"slug": slug, "label": t["label"], "pmid": t["pmid"], "ncts": t["ncts"]}
        try:
            ev, _held = evidence(t, cfg, comp)
        except Exception as exc:  # noqa: BLE001 - one trial's failure is recorded, never fatal
            return key, dict(base, record_id=None, state="EVIDENCE_ERROR", why=f"{type(exc).__name__}: {str(exc)[:200]}")
        v, _adm = typed_first(t, cfg, _held)
        if v == "ADMITTED":
            return key, dict(base, record_id=None, state="TYPED_ADMITTED")
        if not any(a.get("state") == "POSTED" for a in ev["aact"].values()) and not _held["text"] \
                and not ev.get("regulatory"):
            # nothing open to read: no model call (a reader with no source can only guess). A META row is never
            # admitted (gate: META_CANDIDATE), so meta rows alone are no source to read
            return f"{slug}|{t['label']}", {"record_id": None, "state": "NO_OPEN_SOURCE", "slug": slug,
                                            "label": t["label"], "pmid": t["pmid"], "ncts": t["ncts"],
                                            "why": {"aact": {n: a.get("state") for n, a in ev["aact"].items()},
                                                    "full_text": (json.load(open(os.path.join(
                                                        ROOT, "outputs", "k_gap", "fulltext_index.json"),
                                                        encoding="utf-8")).get(t["pmid"] or "") or {}).get("state")}}
        p = (INSTR + "\n\n=== EVIDENCE ===\n" + json.dumps(ev, ensure_ascii=False, indent=0, default=str)).encode("utf-8")
        psha = hashlib.sha256(p).hexdigest()

        def ask(model, line):
            """One recorded call through the pool (a local or a worker slot); None when the run must not call."""
            if stop.is_set() or not disk_ok():
                return None
            rec = pool.call(p, schema=SCHEMA, model=model, effort=EFFORT,
                            caller={"file": "scripts/g1_trial_acquire.py", "line": line,
                                    "purpose": f"G1 missing-trial acquisition {slug} / {t['label'][:50]} "
                                               f"({'reader 2' if model == MODEL_2 else 'reader 1'}; acq/k-gap lane)"},
                            input_digests=[{"ref": "evidence", "sha256": psha,
                                            "what": "inline evidence: AACT snapshot rows, PMC OA / CC Unpaywall text, "
                                                    "FDA / EMA / NICE windows, meta rows"}],
                            timeout_s=1800)
            if rec["state"] != "RAN_OK" and _QUOTA.search(json.dumps(rec.get("error") or rec.get("response") or "")):
                stop.set()                                    # the budget floor: no further calls this run
            ms.write_record(rec, REC_DIR)
            return rec

        if prev.get("state") == "RAN_OK" and prev.get("prompt_sha256") == psha and not any(r in t["label"] for r in redo):
            out = dict(prev)                                  # same evidence, already answered: no second reader-1 call
        else:
            if stop.is_set():
                return key, dict(base, record_id=None, state="SKIPPED_BUDGET", prompt_sha256=psha)
            if not disk_ok():
                return key, dict(base, record_id=None, state="SKIPPED_DISK", prompt_sha256=psha)
            try:
                rec = ask(MODEL, "run")
            except mcl.LicenceRefused as exc:
                return key, dict(base, record_id=None, state="REFUSED_LICENCE", why=str(exc)[:300], prompt_sha256=psha)
            if rec is None:
                return key, dict(base, record_id=None, state="SKIPPED_BUDGET", prompt_sha256=psha)
            out = dict(base, record_id=rec["record_id"], state=rec["state"], prompt_sha256=psha, runner=rec["client"]
                       .get("argv", ["?"])[0])
        # SECOND INDEPENDENT READER on every row reader 1's answer would BIND (Mahmood 6 Oct): the same evidence, another
        # model; replay binds only when both readers pass the gate with the same tuple
        if out.get("state") == "RAN_OK" and not (out.get("reader2") or {}).get("prompt_sha256") == psha:
            resp1 = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, out["record_id"] + ".json"))).decode("utf-8"))
            if gate(resp1, _held, cfg, slug)[0] == "ADMITTED":
                rec2 = ask(MODEL_2, "run:reader2")
                if rec2 is not None:
                    out["reader2"] = {"record_id": rec2["record_id"], "state": rec2["state"], "model": MODEL_2,
                                      "prompt_sha256": psha, "runner": rec2["client"].get("argv", ["?"])[0]}
        return key, out
    with cf.ThreadPoolExecutor(max_workers=pool.size) as ex:
        for k, r in ex.map(one, jobs):
            data["runs"][k] = r
            print(r["state"], r["record_id"], k, flush=True)
            json.dump(data, open(PROP, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    return data


_TUPLE = ("events_t", "n_t", "events_c", "n_c", "effect", "lower", "upper")


def _tuple(row):
    def norm(v):
        if v is None:
            return None
        try:
            return round(float(str(v).replace(",", "")), 6)
        except ValueError:
            return str(v).strip()
    return tuple(norm(getattr(row, k)) for k in _TUPLE)


def second_reader_check(r, held, cfg, adm):
    """A row reader 1 would bind binds only when the SECOND independent reader (MODEL_2, same evidence, its own record)
    also passes the gate with the SAME tuple (Mahmood 6 Oct). Returns (verdict, admitted, second-reader summary)."""
    r2 = r.get("reader2") or {}
    if r2.get("prompt_sha256") != r.get("prompt_sha256") or not r2.get("record_id"):
        return "PENDING_SECOND_READER", None, {"state": "NOT_RUN"}
    summ = {"record_id": r2["record_id"], "model": r2.get("model"), "runner": r2.get("runner")}
    if r2.get("state") != "RAN_OK":
        return "PENDING_SECOND_READER", None, dict(summ, state=f"CALL_{r2.get('state')}")
    resp2 = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, r2["record_id"] + ".json"))).decode("utf-8"))
    v2, adm2 = gate(resp2, held, cfg, r["slug"])
    if v2 != "ADMITTED":
        return "REFUSED:SECOND_READER_NOT_ADMITTED", None, dict(summ, state=v2)
    if _tuple(adm["row"]) != _tuple(adm2["row"]):
        return "REFUSED:READERS_DISAGREE", None, dict(summ, state="DISAGREE", reader1=_tuple(adm["row"]),
                                                      reader2=_tuple(adm2["row"]))
    return "ADMITTED", dict(adm, second_reader=dict(summ, state="AGREE")), dict(summ, state="AGREE")


def merged_rows(path, rows):
    """The replay's rows MERGED into the topic's existing acquired file: a trial re-derived now replaces its old row; a row
    this replay does not re-derive is KEPT (6 Oct: replay rewrote dpp4-mace-t2d from this lane's proposals alone and
    dropped TECOS's admitted row -- ported from g1/finish-line, and no longer a target once it was matched)."""
    old = json.load(open(path, encoding="utf-8")).get("rows") if os.path.exists(path) else []
    new = {r["label"]: r for r in rows}
    return [r for r in old or [] if r.get("label") not in new] + rows


def replay(slugs, ref):
    data = json.load(open(PROP, encoding="utf-8")) if os.path.exists(PROP) else {"runs": {}}
    by_slug = {}
    for k, r in data["runs"].items():
        if slugs and r["slug"] not in slugs:
            continue
        cfg = json.load(open(os.path.join(ROOT, "topics", f"{r['slug']}.json"), encoding="utf-8"))
        o = tracker_file(r["slug"], ref)
        t = {"slug": r["slug"], "label": r["label"], "pmid": r["pmid"], "ncts": r["ncts"]}
        if r["state"] == "TYPED_ADMITTED":
            # deterministic: re-derived from the held sources on every replay (no record exists, none is needed)
            _ev, held = evidence(t, cfg, comparator_pmid(r["slug"], o))
            verdict, adm = typed_first(t, cfg, held)
            row = {"label": r["label"], "pmid": r["pmid"], "ncts": r["ncts"], "record_id": None,
                   "verdict": verdict or "TYPED_NOT_REPRODUCED", "model": None}
            if adm:
                rw = adm.pop("row")
                row["admitted"] = dict(adm, value={k_: getattr(rw, k_) for k_ in ("measure", "effect", "lower", "upper",
                                                                                   "events_t", "n_t", "events_c", "n_c")})
            by_slug.setdefault(r["slug"], []).append(row)
            continue
        if r["state"] not in ("RAN_OK", "WITHHELD_NOT_OPEN_TEXT"):
            by_slug.setdefault(r["slug"], []).append({"label": r["label"], "verdict": r["state"] if r["state"] ==
                                                       "NO_OPEN_SOURCE" else f"CALL_{r['state']}",
                                                       "record_id": r["record_id"], "why": r.get("why")})
            continue
        _ev, held = evidence(t, cfg, comparator_pmid(r["slug"], o))
        second = None
        if r["state"] == "RAN_OK":
            resp = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, r["record_id"] + ".json"))).decode("utf-8"))
            verdict, adm = gate(resp, held, cfg, r["slug"])
            if verdict == "ADMITTED":
                verdict, adm, second = second_reader_check(r, held, cfg, adm)
        else:
            resp, verdict, adm = {}, "WITHHELD_NOT_OPEN_TEXT", None
        row_extra = {"second_reader": second} if second else {}
        if verdict != "ADMITTED" and held["text"]:
            # the trial's OWN held text, read DETERMINISTICALLY (no model): its outcome table row under the arm Ns. The
            # route for a text that may not be shown to a model (SMART: an NIH author manuscript, not CC-licensed)
            tt = table_tuple(held["text"], outcome_row_terms(cfg), (cfg.get("primary_outcome") or {}).get("timepoint"))
            copy = pmc_copy(r["pmid"]) if tt else None
            if tt and copy["licence"] not in OPEN_COPY:
                # the row is read from a copy that is not legitimately open: refused, never kept
                verdict, tt = "REFUSED:HELD_COPY_NOT_OPEN", None
                row_extra = {"source_copy": copy}
            if tt:
                label_, rr, span = tt
                verdict = "ADMITTED"
                est = ((cfg.get("primary_outcome") or {}).get("estimand") or "").upper()
                from harness import secondary_meta as sm_
                adm = {"kind": "TEXT_TABLE", "source": f"PMID {r['pmid']} {copy['pmcid']} ({copy['licence']}) held "
                                                       f"full text sha256 {held['sha']} (read deterministically: "
                                                       f"g1_trial_acquire.table_tuple)",
                       "source_copy": copy, "span": span[:600], "quote": None,
                       "row": sm_.SecondaryRow(meta_pmid="ACQUIRED", meta_doi="", location={}, source_digest="",
                                               provenance="TABLE_ROW", trial_label="", measure=est,
                                               outcome_definition=label_, **rr, effect=None, lower=None, upper=None)}
        row = {"label": r["label"], "pmid": r["pmid"], "ncts": r["ncts"], "record_id": r["record_id"],
               "verdict": verdict, "model": {k_: resp.get(k_) for k_ in ("verdict", "source", "source_ref", "measure",
                                                                         "events_t", "n_t", "events_c", "n_c", "effect",
                                                                         "lower", "upper", "outcome_as_stated",
                                                                         "timepoint_as_stated", "population_as_stated",
                                                                         "scope_rule_key", "scope_span", "why")}}
        row.update(row_extra)
        if adm and verdict != "ADMITTED":
            row["refusal_detail"] = adm                  # e.g. the randomised total a posted subpopulation falls short of
            adm = None
        if adm and adm.get("kind") == "AACT":
            adm["comparator_counts_check"] = comparator_counts_are_events(
                _comparator_row(o, r["label"]), r.get("ncts") or [])
        if adm:
            rw = adm.pop("row")
            row["admitted"] = dict(adm, value={k_: getattr(rw, k_) for k_ in ("measure", "effect", "lower", "upper",
                                                                               "events_t", "n_t", "events_c", "n_c")})
        by_slug.setdefault(r["slug"], []).append(row)
    os.makedirs(ACQ_DIR, exist_ok=True)
    for slug, rows in by_slug.items():
        rows = merged_rows(os.path.join(ACQ_DIR, f"{slug}.json"), rows)
        json.dump({"slug": slug, "ref": ref, "rule": "2 Oct decision: one PRIMARY source, typed (g1_tracker."
                   "single_primary_source); model-read, gate-verified (scripts/g1_trial_acquire.py)", "rows": rows},
                  open(os.path.join(ACQ_DIR, f"{slug}.json"), "w", encoding="utf-8", newline="\n"), indent=1,
                  ensure_ascii=False)
        for x in rows:
            m = x.get("model") or {}
            print(f"{slug} | {x['label'][:40]} | {x['verdict']} | {m.get('source')} {m.get('measure')} "
                  f"{m.get('events_t')}/{m.get('n_t')} vs {m.get('events_c')}/{m.get('n_c')} "
                  f"{m.get('effect')} ({m.get('lower')}-{m.get('upper')}) | {str(m.get('why'))[:150]}")
    return by_slug


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    argv = sys.argv[1:]
    # default: the LOCAL tracker outputs (this lane does not commit them; the captain regenerates the served union)
    ref = next((a.split("=", 1)[1] for a in argv if a.startswith("--ref=")), "")
    slugs = [a for a in argv if not a.startswith("--")]
    if "--run" in argv:
        run(slugs, ref, [a.split("=", 1)[1] for a in argv if a.startswith("--redo=")],
            workers=next((int(a.split("=", 1)[1]) for a in argv if a.startswith("--workers=")), 5),
            remote_workers=next((int(a.split("=", 1)[1]) for a in argv if a.startswith("--remote-workers=")), 0))
    replay(slugs, ref)
