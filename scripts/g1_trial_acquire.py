"""G1 MISSING-TRIAL ACQUISITION: one RECORDED codex call per comparator trial we cannot yet match (concurrency 3),
replayed through deterministic gates. Nothing a model says is admitted until a gate finds it in the source.

Population: the trials of each topic's tracker file (default ref origin/main, the served union) that are not matched and
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
FT_CAP = 60000
SOURCES = ["AACT", "PMC_TEXT", "META", "NONE"]
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
own full text, then the meta rows (a meta row is never the trial's own result: report it only if nothing primary exists).

Return the trial's result for the OUTCOME (name, keywords, estimand, timepoint, population as given) for experimental vs
control:
  - counts: events_t/n_t (experimental), events_c/n_c (control) as WHOLE numbers printed in the source -- never computed
    from a percentage, never from a figure, never a rate; or
  - an effect: measure + effect + lower + upper exactly as printed (two-sided 95% CI only).
quote = an EXACT substring of the source shown (copy it character for character; it must contain every number you give).
For AACT give source_ref = the NCT and aact_outcome_id = the outcome id shown; for the text source_ref = PMID.
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
        out.append({"slug": slug, "label": x["label"], "pmid": pmid, "ncts": ncts, "route_now": x.get("route"),
                    "blocker_now": x.get("blocker")})
    return o, out


_TABLE = None


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
                         "analyses": [{k: a.get(k) for k in ("param_type", "param_value", "ci_lower", "ci_upper", "groups")}
                                      for a in reg["analyses"] if a.get("outcome_id") == oid]})
        out[n] = {"state": "POSTED", "snapshot": reg.get("_snapshot"), "outcomes": outs[:60], "_reg": reg}
    return out


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


def evidence(t, cfg, comp):
    terms = outcome_terms(cfg)
    aact = aact_evidence(t["ncts"])
    whole, shown, sha = text_evidence(t["pmid"], terms)
    po = cfg.get("primary_outcome") or {}
    ev = {"trial": t["label"], "pmid": t["pmid"], "ncts": t["ncts"],
          "outcome": {k: po.get(k) for k in ("name", "keywords", "estimand", "timepoint", "population")},
          "protocol_include": cfg.get("include"), "protocol_arm_object": cfg.get("arm_object"),
          "eligibility_summary": cfg.get("eligibility_summary"),
          "aact": {n: {k: v for k, v in a.items() if k != "_reg"} for n, a in aact.items()},
          "full_text": ({"pmid": t["pmid"], "sha256": sha, "chars": len(whole), "shown_chars": len(shown), "text": shown}
                        if whole else {"state": "NO_OPEN_FULL_TEXT"}),
          "meta_rows": meta_evidence(t["slug"], t["label"])}
    return ev, {"aact": aact, "text": whole, "sha": sha, "terms": terms, "comp": comp, "pmid": t["pmid"]}


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
        if not m:
            return "REFUSED:TYPED_MATCH_NOT_FOUND_BESIDE_OUTCOME_TERMS", None
        return "ADMITTED", {"kind": "TEXT", "source": f"PMID {resp['source_ref']} PMC OA full text sha256 {held['sha']}",
                            "span": m.get("span"), "quote": resp["quote"], "row": row}
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


def run(slugs, ref, redo=()):
    """A trial already answered (RAN_OK) is not asked again unless its label matches a --redo=<substring>."""
    data = json.load(open(PROP, encoding="utf-8")) if os.path.exists(PROP) else {"runs": {}}
    jobs = []
    for slug in slugs:
        cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
        o, ts = targets(slug, ref)
        for t in ts:
            prev = data["runs"].get(f"{slug}|{t['label']}") or {}
            if prev.get("state") in ("RAN_OK", "NO_OPEN_SOURCE") and not any(r in t["label"] for r in redo):
                continue
            jobs.append((slug, cfg, comparator_pmid(slug, o), t))

    # ONE detail pass for every job's NCTs before the pool (three threads each streaming 3 GB, and racing on one cache
    # file, corrupted it: 'Extra data: line 1 column 90017')
    aact_detail(sorted({n for _s, _c, _p, t in jobs for n in t["ncts"]}))

    def one(job):
        slug, cfg, comp, t = job
        ev, _held = evidence(t, cfg, comp)
        if not any(a.get("state") == "POSTED" for a in ev["aact"].values()) and not _held["text"] and not ev["meta_rows"]:
            # nothing open to read: no model call (a reader with no source can only guess)
            return f"{slug}|{t['label']}", {"record_id": None, "state": "NO_OPEN_SOURCE", "slug": slug,
                                            "label": t["label"], "pmid": t["pmid"], "ncts": t["ncts"],
                                            "why": {"aact": {n: a.get("state") for n, a in ev["aact"].items()},
                                                    "full_text": (json.load(open(os.path.join(
                                                        ROOT, "outputs", "k_gap", "fulltext_index.json"),
                                                        encoding="utf-8")).get(t["pmid"] or "") or {}).get("state")}}
        p = (INSTR + "\n\n=== EVIDENCE ===\n" + json.dumps(ev, ensure_ascii=False, indent=0, default=str)).encode("utf-8")
        rec = mcl.call(p, schema=SCHEMA, model=MODEL, effort=EFFORT,
                       caller={"file": "scripts/g1_trial_acquire.py", "line": "run",
                               "purpose": f"G1 missing-trial acquisition {slug} / {t['label'][:50]} (g1/finish-line lane)"},
                       input_digests=[{"ref": "evidence", "sha256": hashlib.sha256(p).hexdigest(),
                                       "what": "inline evidence: AACT snapshot rows, PMC OA text, meta rows"}],
                       timeout_s=1800)
        ms.write_record(rec, REC_DIR)
        return f"{slug}|{t['label']}", {"record_id": rec["record_id"], "state": rec["state"], "slug": slug,
                                        "label": t["label"], "pmid": t["pmid"], "ncts": t["ncts"],
                                        "prompt_sha256": hashlib.sha256(p).hexdigest()}
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for k, r in ex.map(one, jobs):
            data["runs"][k] = r
            print(r["state"], r["record_id"], k, flush=True)
            json.dump(data, open(PROP, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    return data


def replay(slugs, ref):
    data = json.load(open(PROP, encoding="utf-8")) if os.path.exists(PROP) else {"runs": {}}
    by_slug = {}
    for k, r in data["runs"].items():
        if slugs and r["slug"] not in slugs:
            continue
        cfg = json.load(open(os.path.join(ROOT, "topics", f"{r['slug']}.json"), encoding="utf-8"))
        o = tracker_file(r["slug"], ref)
        if r["state"] != "RAN_OK":
            by_slug.setdefault(r["slug"], []).append({"label": r["label"], "verdict": r["state"] if r["state"] ==
                                                       "NO_OPEN_SOURCE" else f"CALL_{r['state']}",
                                                       "record_id": r["record_id"], "why": r.get("why")})
            continue
        resp = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, r["record_id"] + ".json"))).decode("utf-8"))
        t = {"slug": r["slug"], "label": r["label"], "pmid": r["pmid"], "ncts": r["ncts"]}
        _ev, held = evidence(t, cfg, comparator_pmid(r["slug"], o))
        verdict, adm = gate(resp, held, cfg, r["slug"])
        row = {"label": r["label"], "pmid": r["pmid"], "ncts": r["ncts"], "record_id": r["record_id"],
               "verdict": verdict, "model": {k_: resp.get(k_) for k_ in ("verdict", "source", "source_ref", "measure",
                                                                         "events_t", "n_t", "events_c", "n_c", "effect",
                                                                         "lower", "upper", "outcome_as_stated",
                                                                         "timepoint_as_stated", "population_as_stated",
                                                                         "scope_rule_key", "scope_span", "why")}}
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
    ref = next((a.split("=", 1)[1] for a in argv if a.startswith("--ref=")), "origin/main")
    slugs = [a for a in argv if not a.startswith("--")]
    if "--run" in argv:
        run(slugs, ref, [a.split("=", 1)[1] for a in argv if a.startswith("--redo=")])
    replay(slugs, ref)
