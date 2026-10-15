"""K-GAP FILL PHASE 2: REGULATORS (Mahmood 13 Oct source ladder; starts when phase 1, CT.gov/AACT, is maxed).
Agencies in order: FDA (Drugs@FDA review packages) -> EMA (EPARs) -> IQWiG / G-BA -> PMDA -> Health Canada -> NICE.

Per comparator trial still missing after the earlier phases (cumulative: a trial admitted in phase 1 is not re-read):
  0 MISSING     g1_trial_acquire.targets minus phase-1 admissions
  1 NAMED       the trial is NAMED (acronym / NCT / registry secondary id / sponsor study code) in >= 1 HELD text document of
                the agency (g1_regulatory_source.regulatory_evidence; documents held with url, sha256, retrieval, licence
                typed from the HOST; a scanned PDF with no text layer is NO_TEXT_LAYER -- never OCR)
  2 TYPED       DETERMINISTIC first: g1_regulatory_source.regulatory_typed (one trial-named line, two corroborated e/N (p%)
                cells, arms ordered by a header naming both), under the randomised-N check -> ADMITTED with no model call
  3 READ        only where nothing parses: codex A + agy B read the prompt-open WINDOWS (licence checked before any text
                goes to a model: FDA US Government work; EMA reproduction with acknowledgement, each window carrying it;
                NICE only if its own text states OGL / CC); each answer through g1_trial_acquire.gate's REGULATORY branch
                (document held + digest, quote verbatim in the WHOLE document, numbers in the quote, trial named near the
                quote, randomised N, typed match beside the outcome terms); an adjudicator must equal a gated reader
Rows: registry/g1_acquired_regulator/<slug>.json, phase '2_REGULATOR:<AGENCY>', read by g1_tracker.acquired_rows.

    python scripts/g1_regulator_fill.py run AGENCY SLUG [SLUG ...] [--workers=N]
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_registry_fill as rf  # noqa: E402  (readers, adjudicator, call reuse, answer parser)

OUT_DIR = os.path.join(ROOT, "registry", "g1_acquired_regulator")
EVIDENCE_BUDGET = 22000      # chars of windows shown to BOTH readers (agy's prompt must fit the ~32k Windows command line)
REG_INSTR = """You read windows of ONE regulatory review document set (a drug regulator's own analysis of the sponsor's
trial report), shown below, to find ONE randomised trial's result for a meta-analysis outcome. Use only the windows; no
memory of the trial, no files. source must be "REGULATORY", source_ref the window's url EXACTLY as shown.
The windows discuss several studies: use ONLY the named trial's own result -- never another study's row.
Pick the result that IS the protocol outcome (name, keywords, estimand, timepoint, population as given); the trial's
whole randomised population (ITT / full analysis set). Do not stretch a definition: otherwise SOURCE_ABSENT and say why.
ARMS: experimental = the arm receiving the protocol's INTERVENTION; control = its own comparator. In a multi-arm or
factorial table use ONLY the intervention's arm and its control.
Return counts (events_t/n_t, events_c/n_c as whole numbers printed, never computed from a percentage) or the effect
(measure + effect + lower + upper exactly as printed, two-sided 95% CI only). quote = an EXACT substring of ONE window,
containing every number you give. Never guess a number. Be terse."""


def admitted_earlier(slug):
    p = os.path.join(ROOT, "registry", "g1_acquired_registry", f"{slug}.json")
    rows = json.load(open(p, encoding="utf-8")).get("rows") or [] if os.path.exists(p) else []
    return {r["label"] for r in rows if r.get("verdict") == "ADMITTED"}


def run_trial(slug, agency, cfg, comp, t):
    import g1_trial_acquire as ta
    import g1_regulatory_source as rs
    po = cfg.get("primary_outcome") or {}
    terms = ta.outcome_terms(cfg)
    shown, held_reg = rs.regulatory_evidence(t, terms, slug)
    shown = [s for s in shown if s.get("agency") == agency]
    held_reg = {u: h for u, h in held_reg.items() if not u.startswith("_") and (h.get("record") or {}).get("agency") == agency}
    out = {"label": t["label"], "pmid": t["pmid"], "ncts": t["ncts"], "phase": f"2_REGULATOR:{agency}",
           "documents_naming": sorted(held_reg), "readers": {}}
    if not held_reg:
        return dict(out, stage="MISSING", decision="NOT_NAMED_IN_A_HELD_TEXT_DOCUMENT", verdict="NOT_ADMITTED")
    out["stage"] = "NAMED"
    held = {"aact": {}, "text": "", "sha": None, "terms": terms, "comp": comp, "pmid": t["pmid"], "reg": held_reg,
            "slug": slug, "text_origin": None, "doi": None, "doi_licence": None}
    # (2) DETERMINISTIC first
    v, adm = ta.typed_first(dict(t, slug=slug), cfg, dict(held, text=""))
    if v == "ADMITTED" and adm and adm.get("kind") == "REGULATORY_TABLE":
        rw = adm.pop("row")
        adm["value"] = {k: getattr(rw, k) for k in ("measure", "effect", "lower", "upper", "events_t", "n_t", "events_c", "n_c")}
        return dict(out, stage="TYPED", decision="ADMITTED_DETERMINISTIC", verdict="ADMITTED", admitted=adm,
                    record_id=None, model=None)
    if v == "HELD_FOR_BINDING" and adm:
        ruling = rs.binding_for(slug, t["label"], adm["url"], adm["text_sha256"])
        if ruling and ruling["decision"] == "BOUND":
            return dict(out, stage="TYPED", decision="ADMITTED_DETERMINISTIC_BOUND", verdict="ADMITTED",
                        admitted=dict(adm, binding=ruling), record_id=None, model=None)
        decision = ("TYPED_NOT_BOUND:" + ruling["reason"] if ruling and ruling["decision"] == "NOT_BOUND"
                    else "TYPED_HELD_PENDING_BINDING_RULING")
        return dict(out, stage="TYPED", decision=decision, verdict="NOT_ADMITTED", candidate=adm)
    if not shown:
        windows = sum(len(rs.evidence_windows(h["text"], h["names"], terms)) for h in held_reg.values())
        if windows:
            return dict(out, decision="NAMED_TYPED_ONLY_NO_ROW_PARSED", verdict="NOT_ADMITTED", typed_only_windows=windows)
        return dict(out, decision="NAMED_NO_WINDOW_WITH_OUTCOME_TERMS", verdict="NOT_ADMITTED")
    out["stage"] = "READ"
    # ONE evidence set for BOTH readers, capped so agy's --print argument fits the Windows command line (the regulatory
    # route allows 40,000 chars; every pcsk9 read hit PROMPT_TOO_LONG_FOR_AGY_CLI, 13 Oct). Windows richest in outcome
    # terms are kept first; the gate still searches every WHOLE held document.
    from harness import lexicon
    dens = lambda w: sum(lexicon.fold(w["text"]).count(lexicon.fold(x)) for x in terms if x)   # noqa: E731
    wins = sorted(((dens(w), i, j) for i, s in enumerate(shown) for j, w in enumerate(s["windows"])), reverse=True)
    budget, keep = EVIDENCE_BUDGET, set()
    for _d, i, j in wins:
        n = len(shown[i]["windows"][j]["text"])
        if n <= budget:
            keep.add((i, j))
            budget -= n
    shown = [dict(s, windows=[w for j, w in enumerate(s["windows"]) if (i, j) in keep]) for i, s in enumerate(shown)]
    shown = [s for s in shown if s["windows"]]
    out["windows_shown"] = len(keep)
    ev = {"trial": t["label"], "ncts": t["ncts"],
          "outcome": {k: po.get(k) for k in ("name", "keywords", "estimand", "timepoint", "population")},
          "regulatory": shown}
    body = json.dumps(ev, ensure_ascii=False, indent=0, default=str)
    prompt = (REG_INSTR + "\n\n=== EVIDENCE ===\n" + body).encode("utf-8")
    dg = hashlib.sha256(prompt).hexdigest()
    purpose = f"k-gap regulator fill {agency} {slug} / {t['label'][:50]}"
    gated = {}
    for r in (rf.READER_A, rf.READER_B):
        rec = rf._call(prompt, r, purpose + f" (reader {r[0]})", dg)
        resp = rf._answer(rec)
        if not resp:
            g, a = "UNPARSEABLE", None
        elif resp.get("verdict") == "FOUND" and resp.get("source") != "REGULATORY":
            g, a = "REFUSED:SOURCE_NOT_THE_REGULATOR", None
        else:
            try:
                g, a = ta.gate(resp, held, cfg, slug)
            except Exception as exc:  # noqa: BLE001 - refused, never fatal
                g, a = f"REFUSED:GATE_ERROR:{type(exc).__name__}", None
        out["readers"][r[0]] = {"record_id": rec.get("record_id"), "state": rec.get("state"),
                                "model": (rec.get("model") or {}).get("id_reported"), "gate": g,
                                "answer": {k: (resp or {}).get(k) for k in ("verdict", "source_ref", "measure", "events_t",
                                                                            "n_t", "events_c", "n_c", "effect", "lower",
                                                                            "upper", "outcome_as_stated",
                                                                            "population_as_stated", "why")}}
        if g == "ADMITTED":
            gated[r[0]] = (resp, a)
    key = lambda x: (str(x.get("source_ref")), *(str(x.get(k)) for k in ("events_t", "n_t", "events_c", "n_c", "effect",  # noqa: E731
                                                                          "lower", "upper")))
    unavailable = [k for k, v_ in out["readers"].items() if v_["state"] != "RAN_OK"]
    chosen = None
    if unavailable:
        out["decision"] = "WAITING_READER_UNAVAILABLE:" + ",".join(unavailable)
    elif len(gated) == 2 and key(gated["A"][0]) == key(gated["B"][0]):
        chosen, out["decision"] = gated["A"], "ADMITTED_BOTH_READERS"
    elif gated:
        adj = (rf.ADJ_INSTR + "\n\n=== TASK ===\n" + REG_INSTR + "\n\n=== READER ANSWERS ===\n" +
               json.dumps({k: v_["answer"] for k, v_ in out["readers"].items()}, ensure_ascii=False) +
               "\n\n=== EVIDENCE ===\n" + body).encode("utf-8")
        rec = rf._call(adj, rf.ADJUDICATOR, purpose + " (adjudicator)", hashlib.sha256(adj).hexdigest())
        resp = rf._answer(rec)
        g, a = ta.gate(resp, held, cfg, slug) if resp else ("UNPARSEABLE", None)
        match = next((k for k, (rr, _a) in gated.items() if resp and key(rr) == key(resp)), None)
        out["adjudication"] = {"record_id": rec.get("record_id"), "state": rec.get("state"), "gate": g,
                               "agrees_with_reader": match}
        if g == "ADMITTED" and match:
            chosen, out["decision"] = (resp, a), f"ADMITTED_ADJUDICATED_WITH_{match}"
        else:
            out["decision"] = "NOT_ADMITTED_READERS_DISAGREE"
    else:
        out["decision"] = "NOT_ADMITTED_NO_GATED_READING"
    if chosen:
        _resp, a = chosen
        rw = a.pop("row")
        a["value"] = {k: getattr(rw, k) for k in ("measure", "effect", "lower", "upper", "events_t", "n_t", "events_c", "n_c")}
        out["admitted"] = a
    out["verdict"] = "ADMITTED" if chosen else "NOT_ADMITTED"
    out["record_id"] = (out["readers"].get("A") or {}).get("record_id")
    out["model"] = (out["readers"].get("A") or {}).get("answer")
    return out


def run(agency, slugs, workers):
    import g1_trial_acquire as ta
    os.makedirs(OUT_DIR, exist_ok=True)
    for slug in slugs:
        cfg = rf.config(slug)
        comp = ta.comparator_pmid(slug, ta.tracker_file(slug, None))
        _o, ts = ta.targets(slug, None)
        done = admitted_earlier(slug)
        todo = [t for t in ts if t["label"] not in done]
        # prime the study-code cache ONCE, single-threaded: two workers rewriting outputs/k_gap/_reg/id_information.json
        # at once hit a Windows replace lock (PermissionError WinError 5, 13 Oct). The workers then only read it.
        import g1_regulatory_source as rs
        rs.study_codes(sorted({n for t in todo for n in t["ncts"]}))
        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            rows = list(ex.map(lambda t: run_trial(slug, agency, cfg, comp, t), todo))
        for r in rows:
            print(slug, "|", r["label"][:40], "|", r["stage"], "|", r["decision"], "|",
                  {k: v["gate"] for k, v in (r.get("readers") or {}).items()}, flush=True)
        p = os.path.join(OUT_DIR, f"{slug}.json")
        prev = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"rows": []}
        keep = [x for x in prev.get("rows") or [] if x.get("phase") != f"2_REGULATOR:{agency}"]
        json.dump({"slug": slug, "writer": "scripts/g1_regulator_fill.py", "rule": "phase 2 (regulators): deterministic "
                   "regulator table first; else codex + agy over licence-checked windows, each through "
                   "g1_trial_acquire.gate REGULATORY, adjudicated", "rows": keep + rows},
                  open(p, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
        st = [r["stage"] for r in rows]
        print(f"FUNNEL {agency} {slug}: missing {len(ts)} (after earlier phases {len(todo)}) -> named "
              f"{sum(s != 'MISSING' for s in st)} -> typed {sum(r['decision'] == 'ADMITTED_DETERMINISTIC' for r in rows)} -> "
              f"read {sum(s == 'READ' for s in st)} -> admitted {sum(r['verdict'] == 'ADMITTED' for r in rows)}", flush=True)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    a = sys.argv[1:]
    if not a or a[0] != "run":
        raise SystemExit("usage: run AGENCY SLUG ...")
    run(a[1].upper(), [x for x in a[2:] if not x.startswith("--")],
        next((int(x.split("=", 1)[1]) for x in a if x.startswith("--workers=")), 2))
