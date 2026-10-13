"""K-GAP FILL FROM THE REGISTRY (Mahmood 13 Oct: "fill the k gap ... first from CT.gov/AACT"). For every comparator trial
we do not pool, the trial's OWN posted registry results are the source -- no paper, no meta row, no full text.

Stages (the funnel is reported as n of N at each stage):
  0 MISSING    g1_trial_acquire.targets(): comparator trials not matched and not named, plus SECONDARY_SINGLE rows (a
               registry primary would promote them)
  1 NCT        resolved by the typed chain of g1_trial_acquire.targets (registry binding, family, PubMed databank, the
               k-gap table, the registration's own RESULT reference) -- never by a model
  2 POSTED     the NCT has posted results in the versioned AACT snapshot (kgap.aact_adapter.registry_for), and CT.gov API
               v2 is asked hasResults (freshness: a result posted after the snapshot is NAMED, not used)
  3 OUTCOME    at least one posted outcome passes the tracker's own binding gates for the topic's protocol outcome
               (g1_tracker.binding_verdict: named, estimand, composite, two arms) -- typed, before any model
  4 ADMITTED   two INDEPENDENT readers (codex gpt-6-astra; agy routed to Gemini) each read ONLY the trial's AACT posted
               results and return a typed tuple; each answer passes g1_trial_acquire.gate (AACT branch: binding verdict,
               one time frame, posted-N-not-a-subpopulation, the tuple IS the posted counts / two-sided effect). Both
               admitted with the SAME tuple -> ADMITTED. Otherwise an ADJUDICATOR (codex gpt-5.5) sees both readings and
               the same evidence; its answer counts only if it passes the gate AND equals one reader's gated tuple.
Admitted rows go to registry/g1_acquired/<slug>.json in the existing ADMITTED format (source "AACT <snapshot> <NCT>
outcome <id>", the verbatim posted-results quote, the time frame, the registry's analysis population), which the
tracker's acquired_merge already reads -- so a fresh clone replays it with no AACT. Served pools are NOT touched: a served
number change is a signing-packet item.

    python scripts/g1_registry_fill.py funnel [SLUG ...]          stages 0-3, no model calls
    python scripts/g1_registry_fill.py run SLUG [SLUG ...] [--workers=N]   stage 4 (recorded calls) + write admitted rows
"""
from __future__ import annotations

import concurrent.futures as cf
import datetime
import hashlib
import io
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]

OUT = os.path.join(ROOT, "outputs", "k_gap", "registry_fill")
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "registry_fill")
READER_A = ("A", "gpt-6-astra", "high")
READER_B = ("B", "agy", None)
ADJUDICATOR = ("ADJ", "gpt-5.5", "high")


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def active_slugs():
    ab = {t["slug"] for t in json.load(open(os.path.join(ROOT, "registry", "g1_abandoned.json"), encoding="utf-8"))
          .get("topics", [])}
    return sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, "outputs", "k_gap", "g1"))
                  if f.endswith(".json") and f[:-5] not in ab)


def config(slug):
    from harness import served_comparator as sc
    return sc.served_config(slug, json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8")))


_NCT = re.compile(r"NCT\d{8}")
_OTHER_REG = re.compile(r"\b(?:ISRCTN\d{8}|IRCT\d{6,}N?\d*|CTRI/\d{4}/\d{2,3}/\d{5,6}|ChiCTR[-A-Z0-9]{6,}|"
                        r"ACTRN\d{14}|DRKS\d{8}|EudraCT\s*(?:No\.?\s*)?\d{4}-\d{6}-\d{2}|JPRN-\w+|UMIN\d{9}|NTR\d{3,5}|"
                        r"PACTR\d{12,})", re.I)


def _abstracts(pmids):
    """{pmid: (fetch_state, abstract_text)} from the current PubMed record (read-only efetch;
    g1_abstract_census.fetch_abstracts). A PMID the fetch did not return is FETCH_FAILED, never an empty abstract
    (PR #100 r1: a failed fetch read as 'no registration stated')."""
    pmids = sorted({p for p in pmids if p})
    if not pmids:
        return {}
    import g1_abstract_census as cen
    got = cen.fetch_abstracts(pmids)
    return {p: (("FETCHED" if (got[p][0] or "").strip() else "NO_ABSTRACT"), got[p][0] or "") if p in got
            else ("FETCH_FAILED", "") for p in pmids}


def identity_why(fetch_state, abstract, pmid):
    """Why a trial with no NCT stays MISSING: only an abstract that was actually READ can show 'no registration stated'."""
    if not pmid:
        return "NO_PMID_NO_REGISTRATION"
    if fetch_state == "FETCH_FAILED":
        return "FETCH_FAILED:PUBMED_ABSTRACT"
    if fetch_state == "NO_ABSTRACT" or not (abstract or "").strip():
        return "NO_ABSTRACT_TO_READ"
    other = sorted(set(m.group(0) for m in _OTHER_REG.finditer(abstract)))
    return ("REGISTERED_OUTSIDE_CTGOV:" + ",".join(other)) if other else "NO_REGISTRATION_STATED"


_REG_CUE = re.compile(r"regist|clinicaltrials\.gov|identifier|trial number|NCT number", re.I)
_PRIOR_CUE = re.compile(r"\b(?:previous|prior|earlier|preceding|parent|original|antecedent|another|other)\b", re.I)


def registration_ncts(abstract):
    """(the report's OWN registration NCTs, other NCTs merely mentioned). An NCT counts as the report's own only in a
    sentence that states a registration and does not name it as a prior/other trial (PR #100 r1: every NCT in an
    abstract was promoted, a named PRIOR trial included)."""
    own, other = set(), set()
    for sent in re.split(r"(?<=[.;])\s+", abstract or ""):
        found = _NCT.findall(sent)
        if not found:
            continue
        if _REG_CUE.search(sent) and not _PRIOR_CUE.search(sent):
            own.update(found)
        else:
            other.update(found)
    return sorted(own), sorted(other - own)


def results_why(aact_states, ctgov):
    """Why an NCT-resolved trial has no POSTED AACT results. 'NO_POSTED_RESULTS' needs CT.gov v2 to have ANSWERED for
    every NCT; a failed fetch is RESULTS_STATE_UNESTABLISHED (PR #100 r1: 1 of 38 rows had a failed CT.gov fetch)."""
    fresh = [n for n, c in ctgov.items() if (c or {}).get("state") == "OK" and c.get("has_results")]
    if fresh:
        return "RESULTS_POSTED_AFTER_SNAPSHOT:" + ",".join(sorted(fresh))
    gone = sorted(n for n, c in ctgov.items() if (c or {}).get("state") == "NCT_NOT_IN_REGISTRY")
    if gone and len(gone) == len(ctgov):
        return "NCT_NOT_IN_REGISTRY:" + ",".join(gone)
    bad =[f"{n}:{(c or {}).get('state')}" for n, c in sorted(ctgov.items()) if (c or {}).get("state") != "OK"]
    if bad or not ctgov:
        return "RESULTS_STATE_UNESTABLISHED:" + ",".join(bad or sorted(aact_states))
    return "NO_POSTED_RESULTS"


_ENR = {}


def _enrollment(nct):
    """{'count', 'type', 'sha256'} from CT.gov API v2 (typed; a failure is None, never a guess)."""
    if nct in _ENR:
        return _ENR[nct]
    from harness import http
    try:
        st, b = http.get_raw(f"https://clinicaltrials.gov/api/v2/studies/{nct}", {"fields": "NCTId,EnrollmentInfo"},
                             tries=3, timeout=60)
        e = ((json.loads(b).get("protocolSection") or {}).get("designModule") or {}).get("enrollmentInfo") if st == 200 else None
        r = {"count": e.get("count"), "type": e.get("type"), "sha256": hashlib.sha256(b).hexdigest()} if e else None
    except Exception:  # noqa: BLE001 - typed
        r = None
    _ENR[nct] = r
    return r


_CTG = {}


def ctgov_has_results(nct):
    """CT.gov API v2 hasResults (+ last update), cached per run; a failure is typed, never 'no results'."""
    if nct in _CTG:
        return _CTG[nct]
    from harness import http
    try:
        st, b = http.get_raw(f"https://clinicaltrials.gov/api/v2/studies/{nct}",
                             {"fields": "NCTId,HasResults,LastUpdatePostDate,ResultsFirstPostDate"}, tries=3, timeout=60)
        d = json.loads(b) if st == 200 else {}
        sm_ = (d.get("protocolSection") or {}).get("statusModule") or {}
        r = {"state": "OK" if st == 200 else f"HTTP_{st}", "has_results": bool(d.get("hasResults")),
             "results_first_posted": (sm_.get("resultsFirstPostDateStruct") or {}).get("date"),
             "last_update": (sm_.get("lastUpdatePostDateStruct") or {}).get("date"),
             "sha256": hashlib.sha256(b or b"").hexdigest()}
    except Exception as exc:  # noqa: BLE001 - typed
        # a 404 is the registry ANSWERING that it holds no such NCT (a wrong identity), never a failed fetch
        code = getattr(exc.__cause__, "code", None)
        r = {"state": "NCT_NOT_IN_REGISTRY"} if code == 404 else {"state": "FETCH_FAILED", "error": str(exc)[:120]}
    time.sleep(0.3)
    _CTG[nct] = r
    return r


def funnel_topic(slug):
    import g1_trial_acquire as ta
    import g1_tracker as gt
    cfg = config(slug)
    po = cfg.get("primary_outcome") or {}
    _o, ts = ta.targets(slug, None)
    abstracts = _abstracts([t["pmid"] for t in ts if t["pmid"] and not t["ncts"]])
    rows = []
    for t in ts:
        row = {"label": t["label"], "pmid": t["pmid"], "ncts": t["ncts"], "route_now": t["route_now"],
               "blocker_now": t["blocker_now"], "stage": "MISSING"}
        if not t["ncts"]:
            # further TYPED identity routes (13 Oct audit: 'ODYSSEY JAPAN NCT02017898' carried its NCT in its own label;
            # the PubMed databank field is empty for many reports whose ABSTRACT states the registration)
            lab = sorted(set(_NCT.findall(t["label"] or "")))
            fs, ab = abstracts.get(t["pmid"] or "", (None, ""))
            row["abstract_fetch"] = fs
            abn, mentioned = registration_ncts(ab)
            if mentioned:
                row["ncts_mentioned_not_registration"] = mentioned
            if lab or abn:
                t["ncts"] = lab or abn
                row.update(ncts=t["ncts"], nct_by="LABEL" if lab else "ABSTRACT_STATED")
            else:
                rows.append(dict(row, why=identity_why(fs, ab, t["pmid"])))
                continue
        row["stage"] = "NCT"
        ev = ta.aact_evidence(t["ncts"])
        row["aact"] = {n: e.get("state") for n, e in ev.items()}
        row["ctgov"] = {n: ctgov_has_results(n) for n in t["ncts"]}
        posted = [n for n, e in ev.items() if e.get("state") == "POSTED"]
        if not posted:
            why = results_why(row["aact"], row["ctgov"])
            # an NCT the registry does not hold is no resolved identity: the trial stays MISSING
            rows.append(dict(row, why=why, stage="MISSING" if why.startswith("NCT_NOT_IN_REGISTRY") else "NCT"))
            continue
        row["stage"] = "POSTED"
        bindable = []
        for n in posted:
            reg = ev[n]["_reg"]
            for oid, o in reg["outcomes"].items():
                an = next((x for x in reg["analyses"] if x.get("outcome_id") == oid), None)
                groups = reg["groups"].get(oid) or []
                bv = gt.binding_verdict(po.get("name") or "", list(po.get("keywords") or []), o.get("title"),
                                        len({g["group"] for g in groups}),
                                        is_primary=(o.get("type") or "").upper() == "PRIMARY", analysis=an,
                                        estimand=po.get("estimand"), population=po.get("population"))
                if bv["verdict"] == "BINDABLE":
                    bindable.append({"nct": n, "outcome_id": oid, "title": o.get("title"), "time_frame": o.get("time_frame")})
        row["bindable_outcomes"] = bindable
        if not bindable:
            rows.append(dict(row, why="NO_POSTED_OUTCOME_BINDS_TO_THE_PROTOCOL_OUTCOME"))
            continue
        row["stage"] = "OUTCOME"
        rows.append(row)
    return {"slug": slug, "protocol_outcome": po.get("name"), "estimand": po.get("estimand"), "rows": rows}


def prime(slugs):
    """ONE pass over the AACT snapshot for every NCT of every topic: aact_adapter.ensure / aact_detail stream the
    multi-GB tables once per CALL, so calling them per trial re-read the snapshot per trial (10+ min per topic)."""
    import g1_trial_acquire as ta
    from kgap import aact_adapter
    ncts = set()
    for s in slugs:
        _o, ts = ta.targets(s, None)
        ncts |= {n for t in ts for n in t["ncts"]}
    ncts = sorted(ncts)
    print(f"priming AACT for {len(ncts)} NCTs across {len(slugs)} topics", flush=True)
    aact_adapter.ensure(ncts)
    ta.aact_detail(ncts)
    return ncts


def funnel(slugs):
    os.makedirs(OUT, exist_ok=True)
    prime(slugs)
    res, md = {}, ["| topic | missing | NCT resolved | results posted | outcome matched | admitted |", "|---|---|---|---|---|---|"]
    order = ["MISSING", "NCT", "POSTED", "OUTCOME", "ADMITTED"]
    for s in slugs:
        f = funnel_topic(s)
        res[s] = f
        st = [r["stage"] for r in f["rows"]]
        c = [sum(order.index(x) >= i for x in st) for i in range(4)]
        md.append(f"| {s} | {c[0]} | {c[1]} | {c[2]} | {c[3]} | (stage 4) |")
        print(md[-1], flush=True)
        json.dump(f, open(os.path.join(OUT, f"{s}.funnel.json"), "w", encoding="utf-8", newline="\n"), indent=1,
                  ensure_ascii=False)
    tot = [sum(int(l.split("|")[i]) for l in md[2:]) for i in range(2, 6)]
    md.append(f"| **total** | {tot[0]} | {tot[1]} | {tot[2]} | {tot[3]} | |")
    print(md[-1])
    return res, md


REG_INSTR = """You read ONE randomised trial's POSTED REGISTRY RESULTS (ClinicalTrials.gov, as held in the AACT snapshot shown)
to find its result for a meta-analysis outcome. The registry record below is your ONLY source: no paper, no memory of
the trial, no files. source must be "AACT", source_ref the NCT, aact_outcome_id the outcome id shown.
Pick the posted outcome that IS the protocol outcome (name, keywords, estimand, timepoint, population as given). Do not
stretch a definition: a different composite, a different event, or a subset population is NOT the outcome -- then say so
in why and answer SOURCE_ABSENT.
ARMS: experimental = the arm that receives the protocol's INTERVENTION; control = its own comparator (its placebo, or
the protocol comparator). In a factorial or multi-arm posting (several drugs, each with its own placebo) use ONLY the
protocol intervention's arm and ITS control -- never another agent's comparison posted under the same outcome.
Return for experimental vs control either:
  - counts: events_t/n_t (experimental), events_c/n_c (control): the posted PARTICIPANT counts and the posted number
    analysed, as whole numbers shown in the record (never computed from a percentage; never event counts when the units
    are events, not participants); or
  - the posted effect: measure + effect + lower + upper exactly as shown (two-sided 95% CI only).
population_as_stated = the registry's own analysis-population description for that outcome (copy it); timepoint_as_stated
= the outcome's time frame as shown. quote = an EXACT substring of the evidence JSON shown, containing every number you
give. Never guess a number. Be terse."""

ADJ_INSTR = """Two independent readers answered the task below for the same registry record and DISAGREE (or only one
answer passed the deterministic checks). Re-read the registry record yourself and give the correct answer under the same
rules. You may agree with either reader or with neither; a quote must be an exact substring of the evidence JSON."""


def _tuple(resp):
    def n(v):
        return None if v is None else str(v).strip()
    return (str(resp.get("source_ref") or "").strip(), str(resp.get("aact_outcome_id") or "").strip(),
            *(n(resp.get(k)) for k in ("events_t", "n_t", "events_c", "n_c", "effect", "lower", "upper")))


def _call(prompt, reader, purpose, digest):
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    import g1_trial_acquire as ta
    tag, model, eff = reader
    # REUSE: the same prompt to the same model already answered (RAN_OK) is never paid for twice -- a re-run after a
    # reader was unavailable re-calls only that reader
    idx_p = os.path.join(OUT, "_calls.json")
    idx = json.load(open(idx_p, encoding="utf-8")) if os.path.exists(idx_p) else {}
    key = f"{model}|{hashlib.sha256(prompt).hexdigest()}"
    if key in idx and os.path.exists(os.path.join(REC_DIR, idx[key] + ".json")):
        return ms.load_record(os.path.join(REC_DIR, idx[key] + ".json"))
    caller = {"file": "scripts/g1_registry_fill.py", "line": f"reader {tag}", "purpose": purpose}
    dig = [{"ref": "evidence (AACT posted results only)", "sha256": digest, "what": "inline registry record"}]
    if model == "agy":
        p = prompt + ("\n\n=== ANSWER FORMAT ===\nAnswer with ONLY one JSON object (no prose, no code fence) matching "
                      "this JSON schema exactly:\n" + json.dumps(ta.SCHEMA, sort_keys=True)).encode("utf-8")
        if len(p.decode("utf-8")) > 30000:
            # agy takes its prompt only as the --print argument; Windows caps a command line at ~32k chars. Typed,
            # never a crash: the reader is UNAVAILABLE for this trial and the trial waits (no single-family admission)
            return {"state": "PROMPT_TOO_LONG_FOR_AGY_CLI", "record_id": None, "chars": len(p)}
        rec = mcl.agy_call(p, schema=ta.SCHEMA, caller=caller, input_digests=dig, timeout_s=900)
    else:
        rec = mcl.call(prompt, schema=ta.SCHEMA, model=model, effort=eff, caller=caller, input_digests=dig,
                       timeout_s=1800)
    ms.write_record(rec, REC_DIR)
    if rec.get("state") == "RAN_OK":
        with _IDX_LOCK:
            idx = json.load(open(idx_p, encoding="utf-8")) if os.path.exists(idx_p) else {}
            idx[key] = rec["record_id"]
            os.makedirs(OUT, exist_ok=True)
            json.dump(idx, open(idx_p, "w", encoding="utf-8", newline="\n"), indent=0, sort_keys=True)
    return rec


import threading  # noqa: E402
_IDX_LOCK = threading.Lock()


def _answer(rec):
    from reproducible_ai import model_source as ms
    if rec.get("state") != "RAN_OK":
        return None
    t = ms.replay(rec).decode("utf-8", "replace").strip()
    # the LAST complete top-level JSON object in the answer: agy (Gemini Flash) prefixes prose ('I have launched the
    # test command ...' -- with zero tool calls recorded) or wraps a fence; the gate still verifies every number
    dec, last = json.JSONDecoder(), None
    i = t.find("{")
    while i != -1:
        try:
            o, end = dec.raw_decode(t, i)
            if isinstance(o, dict):
                last = o
            i = t.find("{", end)
        except ValueError:
            i = t.find("{", i + 1)
    return last


_GENERIC = {"solution", "solutions", "fatty", "acid", "acids", "therapy", "standard", "control", "placebo", "dose",
            "oral", "daily", "tablet", "treatment", "group", "arm", "plus", "and", "the", "with", "for"}
# comparator terms ARE often generic words ('usual care', 'control', 'standard of care'): only filler is dropped there
_FILLER = {"group", "arm", "plus", "dose", "daily", "oral", "tablet", "and", "the", "with", "for", "of", "or"}
_WORD = re.compile(r"[a-z0-9][a-z0-9'-]*")


def _term_tokens(terms, stop):
    """Each term's DISTINCTIVE tokens (a term with none left cannot name an arm)."""
    out = []
    for t in terms or []:
        k = frozenset(w for w in _WORD.findall(str(t).lower()) if len(w) >= 3 and w not in stop)
        if k:
            out.append(k)
    return out


def _names(title, term_toks):
    """True when the title carries EVERY distinctive token of at least ONE term. One shared token is not identity
    (PR #100 r1: two compounds sharing 'sodium' passed); order and filler words are free, so 'Physiologically
    Balanced Fluid' still names 'balanced solution'."""
    words = set(_WORD.findall((title or "").lower()))
    return any(k <= words for k in term_toks)


def arm_identity(resp, held, cfg):
    """None when the admitted tuple's posted GROUPS are the protocol's intervention v its control, else a refusal code.
    g1_trial_acquire.gate checks that the OUTCOME binds, never which ARMS the numbers belong to: ASCEND (NCT00135226, a
    2x2 factorial) posts Aspirin / Placebo Aspirin / Omega-3 / Placebo Omega-3 under ONE outcome, and two readers took
    the ASPIRIN pair (658/7740 v 743/7740) for the omega-3 topic (13 Oct). The CONTROL must be the protocol's
    comparator (comparator_any) or this intervention's own placebo: omega-3 v the ACTIVE aspirin arm is refused (r1)."""
    n, oid = str(resp.get("source_ref") or "").strip(), str(resp.get("aact_outcome_id") or "")
    reg = (held["aact"].get(n) or {}).get("_reg") or {}
    groups = reg.get("groups", {}).get(oid) or []
    titles = reg.get("group_titles") or {}
    inc = cfg.get("include") or {}
    itoks = _term_tokens(inc.get("intervention_any"), _GENERIC)
    ctoks = [k for k in _term_tokens(inc.get("comparator_any"), _FILLER) if k != {"placebo"}]
    placebo_ok = any("placebo" in str(t).lower() for t in inc.get("comparator_any") or [])
    if resp.get("events_t") is None or resp.get("n_t") is None:
        return "REFUSED:ARM_IDENTITY_NOT_CHECKABLE_EFFECT_ONLY"
    exp = [g for g in groups if (g.get("count"), g.get("n")) == (resp["events_t"], resp["n_t"])]
    ctl = [g for g in groups if (g.get("count"), g.get("n")) == (resp["events_c"], resp["n_c"])]
    if len(exp) != 1 or len(ctl) != 1 or exp[0] is ctl[0]:
        return "REFUSED:ARM_AMBIGUOUS"
    et, ct = titles.get(str(exp[0]["group"])) or "", titles.get(str(ctl[0]["group"])) or ""
    if not _names(et, itoks) or "placebo" in et.lower():
        return f"REFUSED:EXPERIMENTAL_ARM_NOT_THE_INTERVENTION:{et[:60]}"
    if "placebo" in ct.lower():
        if _names(ct, itoks):
            return None  # this intervention's own placebo
        if len(groups) > 2:
            # a multi-arm / factorial posting: the control must be the placebo FOR THIS intervention, not another agent's
            return f"REFUSED:CONTROL_IS_ANOTHER_AGENTS_PLACEBO:{ct[:60]}"
        return None if placebo_ok else f"REFUSED:CONTROL_ARM_NOT_THE_COMPARATOR:{ct[:60]}"
    if _names(ct, itoks):
        return f"REFUSED:CONTROL_ARM_RECEIVES_THE_INTERVENTION:{ct[:60]}"
    if not _names(ct, ctoks):
        return f"REFUSED:CONTROL_ARM_NOT_THE_COMPARATOR:{ct[:60]}"
    return None


def _gated(resp, held, cfg, slug):
    import g1_trial_acquire as ta
    if not resp:
        return "UNPARSEABLE", None
    if resp.get("verdict") == "FOUND" and resp.get("source") != "AACT":
        return "REFUSED:SOURCE_NOT_THE_REGISTRY", None
    try:
        v, adm = ta.gate(resp, held, cfg, slug)
    except Exception as exc:  # noqa: BLE001 - a malformed answer is refused, never fatal
        return f"REFUSED:GATE_ERROR:{type(exc).__name__}", None
    if v == "ADMITTED":
        bad = arm_identity(resp, held, cfg)
        if bad:
            return bad, None
    return v, adm


def arm_pairs(bound, held, passes):
    """Every (experimental, control) tuple of POSTED group counts under the bound outcomes that `passes` (the full gate +
    arm identity). Deterministic, no model: a registry posting IS a table. Used first; only a UNIQUE survivor is admitted
    (ASCEND, 13 Oct: neither reader returned the omega-3 pair 689/7740 v 712/7740 posted under the bound outcome)."""
    out, seen = [], set()
    for n, oid in bound:
        reg = (held["aact"].get(n) or {}).get("_reg") or {}
        o = (reg.get("outcomes") or {}).get(oid) or {}
        groups = [g for g in reg.get("groups", {}).get(oid) or [] if g.get("count") is not None and g.get("n")]
        for gt_ in groups:
            for gc in groups:
                if gt_ is gc:
                    continue
                resp = {"verdict": "FOUND", "source": "AACT", "source_ref": n, "aact_outcome_id": oid, "measure": "COUNTS",
                        "events_t": gt_["count"], "n_t": gt_["n"], "events_c": gc["count"], "n_c": gc["n"],
                        "effect": None, "lower": None, "upper": None, "outcome_as_stated": o.get("title"),
                        "timepoint_as_stated": o.get("time_frame"), "population_as_stated": "",
                        # the quote is the two posted groups as HELD (id, title, count, n): record bytes, not a model's
                        "quote": json.dumps([{"group": g["group"], "title": (reg.get("group_titles") or {}).get(
                            str(g["group"])), "count": g["count"], "n": g["n"]} for g in (gt_, gc)], ensure_ascii=False),
                        "why": "deterministic arm pick: the unique posted pair every gate passes"}
                key = (n, oid, gt_["count"], gt_["n"], gc["count"], gc["n"])
                if key not in seen and passes(resp):
                    seen.add(key)
                    out.append(resp)
    return out


def run_trial(slug, cfg, comp, frow):
    """Stage 4 for one trial that reached OUTCOME: DETERMINISTIC first (arm_pairs: a unique posted pair every gate
    passes, no model); else two independent readers, gate each, adjudicate on disagreement."""
    import g1_trial_acquire as ta
    po = cfg.get("primary_outcome") or {}
    aact = ta.aact_evidence(frow["ncts"])
    # Evidence = the registry record, typed-narrowed: FULL detail for the outcomes that pass the binding gates (stage 3),
    # and id / title / type / time frame for every other posted outcome. Both readers get the SAME evidence; the gate
    # still checks against the WHOLE held record. (ASCEND's full record exceeded the Windows command line that agy's
    # --print argument travels on: WinError 206, 13 Oct.)
    keep = {(b["nct"], str(b["outcome_id"])) for b in frow.get("bindable_outcomes") or []}
    shown = {}
    for n, a in aact.items():
        if a.get("state") != "POSTED":
            continue
        outs = a.get("outcomes") or []
        shown[n] = {"state": "POSTED", "snapshot": a.get("snapshot"),
                    "bindable_outcomes": [o for o in outs if (n, str(o.get("outcome_id"))) in keep],
                    "other_outcomes": [{k: o.get(k) for k in ("outcome_id", "type", "title", "time_frame")}
                                       for o in outs if (n, str(o.get("outcome_id"))) not in keep]}
    ev = {"trial": frow["label"], "ncts": frow["ncts"],
          "outcome": {k: po.get(k) for k in ("name", "keywords", "estimand", "timepoint", "population")},
          "aact": shown}
    held = {"aact": aact, "text": "", "sha": None, "terms": ta.outcome_terms(cfg), "comp": comp, "pmid": frow["pmid"],
            "reg": None, "slug": slug, "text_origin": None, "doi": None, "doi_licence": None}
    body = json.dumps(ev, ensure_ascii=False, indent=0, default=str)
    prompt = (REG_INSTR + "\n\n=== EVIDENCE ===\n" + body).encode("utf-8")
    dg = hashlib.sha256(prompt).hexdigest()
    purpose = f"k-gap registry fill {slug} / {frow['label'][:50]}"
    out = {"label": frow["label"], "pmid": frow["pmid"], "ncts": frow["ncts"], "evidence_sha256": dg, "readers": {}}
    gated = {}
    picks = arm_pairs(sorted(keep), held, lambda rr: _gated(rr, held, cfg, slug)[0] == "ADMITTED")
    out["deterministic_pairs"] = len(picks)
    chosen = None
    if len(picks) == 1:
        v, adm = _gated(picks[0], held, cfg, slug)
        chosen, out["decision"] = (picks[0], adm), "ADMITTED_DETERMINISTIC_ARM_PICK"
    for r in (() if chosen else (READER_A, READER_B)):
        rec = _call(prompt, r, purpose + f" (reader {r[0]})", dg)
        resp = _answer(rec)
        v, adm = _gated(resp, held, cfg, slug)
        out["readers"][r[0]] = {"record_id": rec.get("record_id"), "state": rec.get("state"),
                                "model": (rec.get("model") or {}).get("id_reported"), "gate": v,
                                "answer": {k: (resp or {}).get(k) for k in ("verdict", "source_ref", "aact_outcome_id",
                                                                            "measure", "events_t", "n_t", "events_c",
                                                                            "n_c", "effect", "lower", "upper",
                                                                            "outcome_as_stated", "timepoint_as_stated",
                                                                            "population_as_stated", "why")}}
        if v == "ADMITTED":
            gated[r[0]] = (resp, adm)
    agree = len(gated) == 2 and _tuple(gated["A"][0]) == _tuple(gated["B"][0])
    unavailable = [k for k, v in out["readers"].items() if v["state"] != "RAN_OK"]
    if chosen:
        pass                                              # the deterministic pick: no reader was asked
    elif unavailable:
        # a reader that did not RUN (quota, client error) is not a reader that disagreed: never admit on one family's
        # reading plus a same-family adjudicator. The trial waits for the second reader (re-run is idempotent per record)
        out["decision"] = "WAITING_READER_UNAVAILABLE:" + ",".join(unavailable)
    elif agree:
        chosen, out["decision"] = gated["A"], "ADMITTED_BOTH_READERS"
    elif gated:
        adj_prompt = (ADJ_INSTR + "\n\n=== TASK ===\n" + REG_INSTR + "\n\n=== READER ANSWERS ===\n" + json.dumps(
            {k: v["answer"] for k, v in out["readers"].items()}, ensure_ascii=False) + "\n\n=== EVIDENCE ===\n" + body
                      ).encode("utf-8")
        rec = _call(adj_prompt, ADJUDICATOR, purpose + " (adjudicator)", hashlib.sha256(adj_prompt).hexdigest())
        resp = _answer(rec)
        v, adm = _gated(resp, held, cfg, slug)
        match = next((k for k, (rr, _a) in gated.items() if resp and _tuple(rr) == _tuple(resp)), None)
        out["adjudication"] = {"record_id": rec.get("record_id"), "state": rec.get("state"), "gate": v,
                               "agrees_with_reader": match}
        if v == "ADMITTED" and match:
            chosen, out["decision"] = (resp, adm), f"ADMITTED_ADJUDICATED_WITH_{match}"
        else:
            out["decision"] = "NOT_ADMITTED_READERS_DISAGREE"
    else:
        out["decision"] = "NOT_ADMITTED_NO_GATED_READING"
    if chosen:
        resp, adm = chosen
        rw = adm.pop("row")
        n = str(resp.get("source_ref") or "")
        oid = str(resp.get("aact_outcome_id") or "")
        detail = ((ta.aact_detail([n]).get(n) or {}).get("outcomes") or {}).get(oid) or {}
        adm.update(analysis_population_registry=detail.get("population") or None,
                   comparator_counts_check=ta.comparator_counts_are_events(
                       ta._comparator_row(ta.tracker_file(slug, None), frow["label"]), frow["ncts"]),
                   ctgov_freshness=frow.get("ctgov", {}).get(n),
                   value={k: getattr(rw, k) for k in ("measure", "effect", "lower", "upper", "events_t", "n_t",
                                                      "events_c", "n_c")})
        if not adm["analysis_population_registry"]:
            # the registry's analysis population must be NAMED (Mahmood 13 Oct). The registry's own description is blank
            # for ~1 in 4 posted outcomes; the ONLY typed way to name it then is an exact equality: the posted analysed
            # numbers sum to the registration's ACTUAL enrollment -> every randomised participant was analysed. Anything
            # else (estimated enrollment, a gap of even one participant, effect-only tuples) stays refused.
            v = adm["value"]
            enr = _enrollment(n)
            tot = (v.get("n_t") or 0) + (v.get("n_c") or 0) if v.get("n_t") is not None and v.get("n_c") is not None else None
            if enr and enr.get("type") == "ACTUAL" and tot is not None and tot == enr.get("count"):
                adm["analysis_population_registry"] = (f"ALL_RANDOMISED (typed): posted analysed {v['n_t']} + {v['n_c']} = "
                                                       f"{tot} = actual enrollment {enr['count']} (CT.gov API v2 "
                                                       f"{n}, response sha256 {enr['sha256'][:12]})")
                adm["analysis_population_basis"] = "ENROLLMENT_EQUALITY"
                out["admitted"] = adm
            else:
                out["decision"], chosen = "NOT_ADMITTED_ANALYSIS_POPULATION_NOT_NAMED", None
                out["population_check"] = {"enrollment": enr, "posted_analysed_total": tot}
        else:
            out["admitted"] = adm
    out["verdict"] = "ADMITTED" if chosen else "NOT_ADMITTED"
    # Mahmood's source ladder (13 Oct): 1 CT.gov/AACT -> 2 regulators -> 3 open sources -> 4 published metas (SECONDARY).
    # Every row records the phase that produced it, so the cumulative funnel shows what each source contributes.
    out["phase"] = "1_REGISTRY:AACT"
    out["record_id"] = (out["readers"].get("A") or {}).get("record_id")
    out["model"] = (out["readers"].get("A") or {}).get("answer")
    return out


def run(slugs, workers):
    import g1_trial_acquire as ta
    os.makedirs(os.path.join(ROOT, "registry", "g1_acquired_registry"), exist_ok=True)
    for slug in slugs:
        fp = os.path.join(OUT, f"{slug}.funnel.json")
        f = json.load(open(fp, encoding="utf-8")) if os.path.exists(fp) else funnel_topic(slug)
        cfg = config(slug)
        comp = ta.comparator_pmid(slug, ta.tracker_file(slug, None))
        todo = [r for r in f["rows"] if r["stage"] == "OUTCOME"]
        rows = []
        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            for r in ex.map(lambda fr: run_trial(slug, cfg, comp, fr), todo):
                rows.append(r)
                print(slug, "|", r["label"][:40], "|", r["decision"], "|",
                      {k: v["gate"] for k, v in r["readers"].items()}, flush=True)
        out = {"slug": slug, "written": now(), "writer": "scripts/g1_registry_fill.py",
               "rule": "registry-only PRIMARY source (AACT posted results), two independent readers (codex + agy) each "
                       "gate-verified by g1_trial_acquire.gate, adjudicated on disagreement; analysis population named",
               "aact_snapshot": "2026-08-30", "rows": rows}
        json.dump(out, open(os.path.join(ROOT, "registry", "g1_acquired_registry", f"{slug}.json"), "w",
                            encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
        st = [r["stage"] for r in f["rows"]]
        print(f"FUNNEL {slug}: missing {len(st)} -> NCT {sum(s != 'MISSING' for s in st)} -> posted "
              f"{sum(s in ('POSTED', 'OUTCOME') for s in st)} -> outcome {len(todo)} -> admitted "
              f"{sum(r['verdict'] == 'ADMITTED' for r in rows)}", flush=True)


def main(argv):
    cmd, rest = argv[0], [a for a in argv[1:] if not a.startswith("--")]
    if cmd == "funnel":
        allslugs = sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, "outputs", "k_gap", "g1")) if f.endswith(".json"))
        _res, md = funnel(rest or (allslugs if "--all" in argv else active_slugs()))
        open(os.path.join(OUT, "_funnel.md"), "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
        return 0
    if cmd == "run":
        run(rest, next((int(a.split("=", 1)[1]) for a in argv if a.startswith("--workers=")), 3))
        return 0
    raise SystemExit("usage: funnel|run SLUG ...")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
