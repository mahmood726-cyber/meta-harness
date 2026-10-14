"""K-gap fill PHASE 3 (open sources): the identity-less missing trials with a PMID, through open full text.

Per trial (scope and open-copy class from PHASE3_OPEN_CENSUS.json, scripts/g1_open_census.py):
  CENSUS      NOT_OPEN stops here (phase 4: published metas, SECONDARY)
  ELIGIBLE    a trial blocked on SCREENING (screener error / unaudited screen-out / record insufficient) is queued to the
              screening lane with its open-copy pointer, never acquired here
  TEXT        PMC structured text (k_gap_counterfactual.pmc_fulltext_cached) else the Unpaywall copy (kgap.k_gap.
              unpaywall_text, PDF / HTML text); held by sha256 + source + retrieval date (text cached, gitignored)
  TYPED       DETERMINISTIC first: g1_trial_acquire.table_tuple on PMC tables; on prose text the conservative line reader
              g1_regulatory_source.typed_counts (one outcome line, two percent-corroborated e/N cells, arms ordered by a
              header naming both), in windows around the outcome terms; a posted total short of the randomised total
              (posted_population_short) is refused
  COPY GATE   a find is ADMISSIBLE only from a copy the existing gate admits (g1_trial_acquire.OPEN_COPY: PMC CC / PMC author
              manuscript; an Unpaywall copy only under a 'cc' licence). A find from a copy with NO licence (bronze / green)
              is TYPED_FOUND_PENDING_RULING: Mahmood's ladder reads 'other OA text is regex-only', the gate refuses it,
              and changing the gate is the Captain's (never loosened here)
  MODEL       only CC BY / CC0 text may be shown to a model (D8); counted here when the typed step found nothing
Nothing is admitted into the tracker by this script: an ADMISSIBLE find is written as a candidate row for the real
admission path (phase '3_OPEN:<origin>').

    python scripts/g1_open_fill.py run SLUG [SLUG ...]   -> outputs/k_gap/registry_fill/phase3/<slug>.json
"""
from __future__ import annotations

import datetime
import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
# --registered: the registered trials (an NCT) phases 1-2 did not fill (g1_open_census.py --registered)
_REG = "--registered" in sys.argv
# --companions: the registered trials' companion / primary-outcome publications (g1_identify.py companions)
_COMP = "--companions" in sys.argv
COMP_MODEL = "--companion-model" in sys.argv
MODEL = "--model" in sys.argv and not _COMP
CENSUS = os.path.join(ROOT, "outputs", "k_gap", "registry_fill",
                      "PHASE3_OPEN_CENSUS_COMPANIONS.json" if _COMP else
                      "PHASE3_OPEN_CENSUS_REGISTERED.json" if _REG else "PHASE3_OPEN_CENSUS.json")
OUT = os.path.join(ROOT, "outputs", "k_gap", "registry_fill",
                   "phase3_companions" if _COMP else "phase3_registered" if _REG else "phase3")
WINDOW = 1800
_SCREENING = re.compile(r"^(?:SCREENER_ERROR|SCREENED_OUT_UNAUDITED|INSUFFICIENT_RECORD)")
MODEL_LICENCES = ("CC_BY_OR_CC0",)


def screening_blocked(row):
    return bool(_SCREENING.match(row.get("blocker_now") or ""))


def licence_class(lic):
    """Unpaywall / Europe PMC licence string -> CC_BY_OR_CC0 | CC_OTHER | NONE."""
    l_ = (lic or "").lower().replace("_", "-").replace(" ", "-")
    if not l_:
        return "NONE"
    if l_ in ("cc-by", "cc0", "pd", "public-domain") or re.fullmatch(r"cc-by(-\d(\.\d)?)?", l_):
        return "CC_BY_OR_CC0"
    if l_.startswith("cc"):
        return "CC_OTHER"
    return "NONE"


def prose_windows(text, terms, width=WINDOW):
    rx = re.compile("|".join(re.escape(t) for t in terms if t) or r"$^", re.I)
    spans = []
    for m in rx.finditer(text or ""):
        a, b = max(0, m.start() - width), m.end() + width
        if spans and a <= spans[-1][1]:
            spans[-1] = (spans[-1][0], b)
        else:
            spans.append((a, b))
    return [text[a:b] for a, b in spans]


def typed_read(text, origin, cfg):
    """(tuple dict, span, reader) or (None, None, None). Deterministic only."""
    import g1_trial_acquire as ta
    import g1_regulatory_source as rs
    po = cfg.get("primary_outcome") or {}
    terms = ta.outcome_row_terms(cfg)
    # a table is read wherever the text KEEPS one: PMC structured text, and (since kgap.k_gap HTML layout 2) an HTML copy
    # whose rows are '|' lines. A PDF's text has no delimiters and stays prose-only
    if origin == "PMC" or "|" in (text or ""):
        tt = ta.table_tuple(text, terms, po.get("timepoint"))
        if tt:
            return tt[1], tt[2], "table_tuple"
    found = {}
    for w in prose_windows(text, terms):
        g = rs.typed_counts(w, terms, cfg.get("intervention_terms") or [], cfg.get("comparator_terms") or [])
        if g:
            found[tuple(sorted(g[0].items()))] = g
    if len(found) == 1:
        rr, line = next(iter(found.values()))
        return rr, line, "typed_counts"
    return None, None, None


EVIDENCE_BUDGET = 20000        # chars of open text shown to BOTH readers (agy's prompt travels on the ~32k Windows command line)
COMPANION_NOTE = ("\n\nThis source is a COMPANION publication of the trial (a secondary report, sub-study or follow-up), "
                  "not its main report. Report a result ONLY if it is for the trial's WHOLE randomised population on "
                  "the protocol outcome and timepoint; a subgroup, a sub-study population or a different outcome is "
                  "SOURCE_ABSENT (say why). For this text source use source = PMC_TEXT and source_ref = the companion PMID.")
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "open_fill")
CALLS = os.path.join(OUT, "_calls.json")


def _call(prompt, reader, purpose, digest):
    """One recorded reader call (reused by model + prompt digest). The evidence is the trial's OWN CC BY / CC0 open text
    (D8): the licence guard in model_call_live still checks every shown source."""
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    import g1_trial_acquire as ta
    tag, model, eff = reader
    idx = json.load(open(CALLS, encoding="utf-8")) if os.path.exists(CALLS) else {}
    key = f"{model}|{hashlib.sha256(prompt).hexdigest()}"
    if key in idx and os.path.exists(os.path.join(REC_DIR, idx[key] + ".json")):
        return ms.load_record(os.path.join(REC_DIR, idx[key] + ".json"))
    caller = {"file": "scripts/g1_open_fill.py", "line": f"reader {tag}", "purpose": purpose}
    dig = [{"ref": "evidence", "sha256": digest, "what": "inline evidence: the trial's own CC BY / CC0 open full text "
                                                        "(windows), AACT rows, meta rows"}]
    try:
        if model == "agy":
            p = prompt + ("\n\n=== ANSWER FORMAT ===\nAnswer with ONLY one JSON object (no prose, no code fence) matching "
                          "this JSON schema exactly:\n" + json.dumps(ta.SCHEMA, sort_keys=True)).encode("utf-8")
            if len(p.decode("utf-8")) > 30000:
                return {"state": "PROMPT_TOO_LONG_FOR_AGY_CLI", "record_id": None, "chars": len(p)}
            rec = mcl.agy_call(p, schema=ta.SCHEMA, caller=caller, input_digests=dig, timeout_s=900)
        else:
            rec = mcl.call(prompt, schema=ta.SCHEMA, model=model, effort=eff, caller=caller, input_digests=dig,
                           timeout_s=1800)
    except mcl.LicenceRefused as exc:
        # the D8 guard refused the prompt: a typed state for THIS trial, never a crash of the whole run (14 Oct)
        return {"state": "REFUSED_LICENCE", "record_id": None, "why": str(exc)[:300]}
    ms.write_record(rec, REC_DIR)
    if rec.get("state") == "RAN_OK":
        idx = json.load(open(CALLS, encoding="utf-8")) if os.path.exists(CALLS) else {}
        idx[key] = rec["record_id"]
        os.makedirs(OUT, exist_ok=True)
        json.dump(idx, open(CALLS, "w", encoding="utf-8", newline="\n"), indent=0, sort_keys=True)
    return rec


def _tuple(resp):
    return tuple(None if resp.get(k) is None else str(resp.get(k)).strip()
                 for k in ("events_t", "n_t", "events_c", "n_c", "effect", "lower", "upper"))


def model_read(slug, cfg, label):
    """Codex + agy over the trial's own CC BY / CC0 text (the SAME evidence), each answer through g1_trial_acquire.gate
    (the whole held text); an adjudicator on disagreement whose answer must equal one gated reader's tuple."""
    import g1_trial_acquire as ta
    o, ts = ta.targets(slug, None)
    t = dict(next(x for x in ts if x["label"] == label), slug=slug)
    ev, held = ta.evidence(t, cfg, ta.comparator_pmid(slug, o))
    ft = ev.get("full_text") or {}
    if not ft.get("text"):
        return {"decision": "MODEL_NOT_SHOWN:" + str(ft.get("state"))}
    if len(ft["text"]) > EVIDENCE_BUDGET:
        ft["text"] = ta._windows(held["text"], held["terms"])[:EVIDENCE_BUDGET]
        ft["shown_chars"] = len(ft["text"])
    body = json.dumps(ev, ensure_ascii=False, indent=0, default=str)
    prompt = (ta.INSTR + "\n\n=== EVIDENCE ===\n" + body).encode("utf-8")
    purpose = f"k-gap phase 3 open text {slug} / {label[:50]}"
    return _read_and_adjudicate(prompt, body, held, cfg, slug, purpose)


def companion_model_read(slug, cfg, r, text, src):
    """Read the held companion, then require a whole-trial, appropriate-unit candidate."""
    import g1_trial_acquire as ta
    held = {"aact": {}, "text": text, "sha": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "terms": ta.outcome_terms(cfg), "comp": ta.comparator_pmid(slug, ta.tracker_file(slug, None)),
            "pmid": r["pmid"], "reg": {}, "slug": slug, "text_origin": src.get("origin"),
            "doi": src.get("doi"), "doi_licence": src.get("licence")}
    shown = text if len(text) <= EVIDENCE_BUDGET else ta._windows(text, held["terms"])[:EVIDENCE_BUDGET]
    licence = src.get("licence") or (r.get("europepmc") or {}).get("license")
    evidence = {"trial": r["label"], "companion_publication_pmid": r["pmid"],
                "trial_report_pmid": r.get("population_pmid"),
                "outcome": {k: cfg["primary_outcome"].get(k)
                            for k in ("name", "keywords", "estimand", "timepoint", "population")},
                "protocol_include": cfg.get("include"),
                # the text block is named by the copy it IS: a PMC copy by its PMID (the D8 guard checks the PMC copy's
                # licence), an Unpaywall copy by its DOI (the guard checks that DOI's Unpaywall licence). Naming an
                # Unpaywall copy by PMID made the guard check the wrong copy and refuse (14 Oct, REMAP-CAP 32876697)
                "full_text": dict({"pmid": r["pmid"]} if src.get("origin") == "PMC" else {"doi": src.get("doi")},
                                  licence=licence, sha256=held["sha"], chars=len(text), shown_chars=len(shown),
                                  text=shown)}
    body = json.dumps(evidence, ensure_ascii=False, indent=0, default=str)
    prompt = (ta.INSTR + COMPANION_NOTE + "\n\n=== EVIDENCE ===\n" + body).encode("utf-8")
    purpose = f"k-gap phase 3 companion text {slug} / {r['label'][:50]}"
    out = _read_and_adjudicate(prompt, body, held, cfg, slug, purpose)
    candidate = out.get("admitted_candidate")
    if candidate:
        value = candidate["value"]
        if value.get("events_t") is not None and ta.posted_population_short(
                slug, r.get("population_pmid") or r["pmid"], value["n_t"] + value["n_c"]):
            out["decision"] = "MODEL_FOUND_REFUSED_SUBPOPULATION"
            out.pop("admitted_candidate")
        elif unit_of_analysis_refused(r, value):
            out["decision"] = "MODEL_FOUND_REFUSED_UNIT_OF_ANALYSIS"
            out.pop("admitted_candidate")
        else:
            candidate.update(source_pmid=r["pmid"], population_pmid=r.get("population_pmid"))
    return out


def _read_and_adjudicate(prompt, body, held, cfg, slug, purpose):
    """Keep the same agreement and replay rules for either held evidence source."""
    import g1_trial_acquire as ta
    import g1_registry_fill as rf
    dg = hashlib.sha256(prompt).hexdigest()
    out, gated = {"evidence_sha256": dg, "readers": {}}, {}
    for r in (rf.READER_A, rf.READER_B):
        rec = _call(prompt, r, purpose + f" (reader {r[0]})", dg)
        resp = rf._answer(rec) if rec.get("state") == "RAN_OK" else None
        try:
            v, adm = ta.gate(resp, held, cfg, slug) if resp else ("UNPARSEABLE", None)
        except Exception as exc:  # noqa: BLE001 - a malformed answer is refused, never fatal
            v, adm = f"REFUSED:GATE_ERROR:{type(exc).__name__}", None
        out["readers"][r[0]] = {"record_id": rec.get("record_id"), "state": rec.get("state"), "gate": v,
                                "answer": {k: (resp or {}).get(k) for k in ("verdict", "source", "measure", "events_t",
                                                                            "n_t", "events_c", "n_c", "effect", "lower",
                                                                            "upper", "outcome_as_stated",
                                                                            "timepoint_as_stated", "why")}}
        if v == "ADMITTED":
            gated[r[0]] = (resp, adm)
    if any(v["state"] == "REFUSED_LICENCE" for v in out["readers"].values()):
        out["decision"] = "MODEL_REFUSED_LICENCE"
    elif any(v["state"] != "RAN_OK" for v in out["readers"].values()):
        out["decision"] = "WAITING_READER_UNAVAILABLE"
    elif len(gated) == 2 and _tuple(gated["A"][0]) == _tuple(gated["B"][0]):
        out["decision"], out["admitted_candidate"] = "MODEL_ADMITTED_BOTH_READERS", gated["A"][1]
    elif gated:
        adj = (rf.ADJ_INSTR + "\n\n=== TASK ===\n" + ta.INSTR + "\n\n=== READER ANSWERS ===\n" + json.dumps(
            {k: v["answer"] for k, v in out["readers"].items()}, ensure_ascii=False) + "\n\n=== EVIDENCE ===\n" + body
               ).encode("utf-8")
        rec = _call(adj, rf.ADJUDICATOR, purpose + " (adjudicator)", hashlib.sha256(adj).hexdigest())
        resp = rf._answer(rec) if rec.get("state") == "RAN_OK" else None
        match = next((k for k, (rr, _a) in gated.items() if resp and _tuple(rr) == _tuple(resp)), None)
        out["adjudication"] = {"record_id": rec.get("record_id"), "state": rec.get("state"), "agrees_with": match}
        if match:
            out["decision"], out["admitted_candidate"] = f"MODEL_ADMITTED_ADJUDICATED_WITH_{match}", gated[match][1]
        else:
            out["decision"] = "MODEL_NOT_ADMITTED_READERS_DISAGREE"
    else:
        out["decision"] = "MODEL_NOT_ADMITTED_NO_GATED_READING"
    if out.get("admitted_candidate"):
        rw = out["admitted_candidate"].pop("row", None)
        if rw is not None:
            out["admitted_candidate"]["value"] = {k: getattr(rw, k) for k in ("measure", "effect", "lower", "upper",
                                                                               "events_t", "n_t", "events_c", "n_c")}
    return out


def unit_of_analysis_refused(r, value):
    """The tracker refuses an acquired tuple of UNADJUSTED COUNTS from a cluster design (g1_tracker.acquired_merge:
    UNIT_OF_ANALYSIS_ADJUSTMENT_UNAVAILABLE); such a find is never called admissible here (SALT and SMART, 13 Oct)."""
    return str(r.get("blocker_now") or "").startswith("UNIT_OF_ANALYSIS") and (value or {}).get("events_t") is not None


def run_trial(slug, cfg, r):
    import g1_trial_acquire as ta
    out = {"label": r["label"], "pmid": r["pmid"], "phase": None, "census_class": r["class"],
           "blocker_now": r.get("blocker_now"), "stage": "CENSUS"}
    if r["class"] == "NOT_OPEN":
        return dict(out, decision="NOT_OPEN")
    if screening_blocked(r):
        return dict(out, stage="ELIGIBLE", decision="ELIGIBILITY_BLOCKED_QUEUED_TO_SCREENING",
                    open_copy={"pmcid": (r.get("europepmc") or {}).get("pmcid"), "unpaywall": r.get("unpaywall")})
    out["stage"] = "ELIGIBLE"
    text, origin, src = "", None, {}
    pmcid = (r.get("europepmc") or {}).get("pmcid") or r.get("held_pmcid")
    if pmcid:
        import k_gap_counterfactual as cfm
        try:
            text = cfm.pmc_fulltext_cached(r["pmid"]) or ""
        except Exception as exc:  # noqa: BLE001 - typed
            src["pmc_error"] = str(exc)[:120]
        if text:
            copy = ta.pmc_copy(r["pmid"])
            origin, src = "PMC", dict(src, pmcid=pmcid, copy_licence=copy["licence"],
                                      admissible=copy["licence"] in ta.OPEN_COPY,
                                      model_ok=copy["licence"] in ta.PROMPT_COPY and
                                      licence_class((r.get("europepmc") or {}).get("license")) in MODEL_LICENCES)
    doi = ((r.get("europepmc") or {}).get("doi") or "").lower()
    if not text and doi:
        from kgap import k_gap
        try:
            u = k_gap.unpaywall_text(doi, os.path.join(ROOT, "outputs", "k_gap", "_upw"),
                                     os.path.join(ROOT, "outputs", "k_gap", "unpaywall_text_index.json"), offline=False)
        except Exception as exc:  # noqa: BLE001 - typed
            u = {"state": "FETCH_ERROR", "error": str(exc)[:120]}
        text = u.get("text") or ""
        lic = (r.get("unpaywall") or {}).get("license")
        src = dict(src, doi=doi, unpaywall_state=u.get("state"), unpaywall_tried=u.get("tried"), licence=lic,
                   admissible=str(lic or "").startswith("cc"), model_ok=licence_class(lic) in MODEL_LICENCES)
        origin = "UNPAYWALL" if text else None
    if not text:
        return dict(out, decision="NO_TEXT_LAYER_OR_NOT_FETCHED", source=src)
    out.update(stage="TEXT", source=dict(src, origin=origin, chars=len(text),
                                         text_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                                         retrieved=datetime.date.today().isoformat()))
    rr, span, reader = typed_read(text, origin, cfg)
    if rr:
        # the randomised total is the TRIAL's (its report PMID), also when the find comes from a companion paper
        short = ta.posted_population_short(slug, r.get("population_pmid") or r["pmid"], rr["n_t"] + rr["n_c"])
        if short:
            return dict(out, stage="TYPED", decision="TYPED_REFUSED_SUBPOPULATION", note=short)
        out.update(stage="TYPED", typed={"reader": reader, "value": rr, "span": (span or "")[:600]},
                   phase=f"3_OPEN:{origin}")
        if unit_of_analysis_refused(r, rr):
            return dict(out, decision="TYPED_FOUND_REFUSED_UNIT_OF_ANALYSIS")
        return dict(out, decision="TYPED_FOUND_ADMISSIBLE" if src.get("admissible") else "TYPED_FOUND_PENDING_RULING")
    if src.get("model_ok"):
        if _COMP and COMP_MODEL:
            m = companion_model_read(slug, cfg, r, text, out["source"])
            return dict(out, stage="MODEL", model=m, decision=m["decision"],
                        phase=f"3_OPEN:{origin}:COMPANION" if m.get("admitted_candidate") else None)
        if not MODEL:
            return dict(out, decision="TYPED_NONE_MODEL_ELIGIBLE")
        m = model_read(slug, cfg, r["label"])
        val = (m.get("admitted_candidate") or {}).get("value")
        if val and unit_of_analysis_refused(r, val):
            m["decision"] = "MODEL_FOUND_REFUSED_UNIT_OF_ANALYSIS"
        return dict(out, stage="MODEL", model=m, decision=m["decision"],
                    phase=f"3_OPEN:{origin}" if m.get("admitted_candidate") else None)
    return dict(out, decision="TYPED_NONE_NOT_MODEL_LICENSED")


def run(slugs):
    import g1_registry_fill as rf
    census = json.load(open(CENSUS, encoding="utf-8"))["rows"]
    os.makedirs(OUT, exist_ok=True)
    tot = {}
    for slug in slugs:
        cfg = rf.config(slug)
        rows = [run_trial(slug, cfg, r) for r in census if r["slug"] == slug]
        for x in rows:
            print(slug, "|", x["label"][:34], "|", x["census_class"], "|", x["decision"], "|",
                  (x.get("typed") or {}).get("value"), flush=True)
        json.dump({"slug": slug, "writer": "scripts/g1_open_fill.py", "census": os.path.basename(CENSUS), "rows": rows},
                  open(os.path.join(OUT, f"{slug}.json"), "w", encoding="utf-8", newline="\n"), indent=1,
                  ensure_ascii=False)
        st = lambda k: sum(1 for x in rows if x["decision"].startswith(k))  # noqa: E731
        f = {"n": len(rows), "open": sum(x["census_class"] != "NOT_OPEN" for x in rows),
             "eligible": sum(x["stage"] not in ("CENSUS",) and x["decision"] != "ELIGIBILITY_BLOCKED_QUEUED_TO_SCREENING"
                             for x in rows),
             "text": sum(x["stage"] in ("TEXT", "TYPED") for x in rows),
             "typed": st("TYPED_FOUND"), "admissible": st("TYPED_FOUND_ADMISSIBLE"),
             "pending": st("TYPED_FOUND_PENDING_RULING"), "model_eligible": st("TYPED_NONE_MODEL_ELIGIBLE")}
        tot[slug] = f
        print(f"FUNNEL OPEN {slug}: {f['n']} -> open {f['open']} -> eligible {f['eligible']} -> text {f['text']} -> typed "
              f"{f['typed']} (admissible {f['admissible']}, pending ruling {f['pending']}) | model-eligible "
              f"{f['model_eligible']}", flush=True)
    return tot


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    a = sys.argv[1:]
    if not a or a[0] != "run":
        raise SystemExit("usage: run SLUG ...")
    run([x for x in a[1:] if not x.startswith("--")])
