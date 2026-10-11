"""FORMAL RoB 2 per trial per served outcome (D11: RoB sign-off by reproducible AI in the harness).

For each (topic, trial, served outcome):
  1. sources     robgrade/rob2_typed.trial_sources: the PubMed abstract, the held full text (open for a prompt only if
                 marked CC -- D8), the AACT designs row and the registry description (ClinicalTrials.gov text)
  2. typed       robgrade/rob2_typed.typed_answers: registry fields + regex (regex may read any held text)
  3. dual read   two RECORDED model readings, blind to each other and to the typed answers: codex (OpenAI) and agy
                 (Google), each answering all 22 signalling questions with a VERBATIM quote from a named OPEN source.
                 A quote that is not found, verbatim, in the source it names is not an answer: that answer becomes NI.
  4. agreement   per question: same side (Y/PY or N/PN, or both NI) -> agreed (the less certain of the two: PY over Y);
                 otherwise -> 5.
  5. adjudicate  one more RECORDED call (codex, high effort) sees ONLY the disagreeing questions, both readings (as
                 'reader 1' / 'reader 2', never by model), and the same open sources; its answer must also quote verbatim.
  6. assemble    typed answers first (deterministic, cited); then agreed / adjudicated model answers; else NI. A domain
                 whose every answer is NI while the trial's full text is held but NOT open is INSUFFICIENT_OPEN_SOURCE
                 (the information may exist, but D8 keeps it from a prompt and no typed rule found it).
Every record: evidence/model_calls/rob2/. Output: outputs/robgrade/rob2/<slug>.json (no served file is written).

    python scripts/rob2_dual.py --run SLUG [SLUG ...]   (recorded calls; codex x8, agy x4, retry with back-off)
    python scripts/rob2_dual.py SLUG [SLUG ...]         (replay: no network, no model)
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import os
import re
import sys
import time
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from robgrade import rob2_formal as rf  # noqa: E402
from robgrade import rob2_typed as rt  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "rob2")
OUT_DIR = os.path.join(ROOT, "outputs", "robgrade", "rob2")
RUNS = os.path.join(ROOT, "registry", "model_proposals", "rob2_dual_runs.json")
LANE = "robgrade"
CODEX_MODEL, CODEX_EFFORT, ADJ_EFFORT = "gpt-6-astra", "medium", "high"
CODEX_WORKERS, AGY_WORKERS = 8, 4
QIDS = list(rf.QUESTIONS)

SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["answers", "notes"],
    "properties": {
        "notes": {"type": "string"},
        "answers": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["qid", "answer", "quote", "source_id", "rationale"],
            "properties": {"qid": {"type": "string", "enum": QIDS},
                           "answer": {"type": "string", "enum": list(rf.ANSWERS)},
                           "quote": {"type": "string"}, "source_id": {"type": "string"},
                           "rationale": {"type": "string"}}}}}}

INSTR = """You are assessing ONE randomised trial with the Cochrane RoB 2 tool (Handbook chapter 8), for ONE outcome,
effect of ASSIGNMENT to intervention (intention-to-treat). Answer EVERY signalling question below with one of
Y (yes), PY (probably yes), PN (probably no), N (no), NI (no information), NA (not applicable).

Rules -- they are checked mechanically and an answer that breaks them is discarded:
- Use ONLY the sources given below. Do not use anything you remember about this trial.
- Every Y, PY, PN or N answer must give a VERBATIM quote (copied exactly, 8 to 300 characters) from ONE source, and
  that source's id in source_id. The quote must support the answer by itself.
- If the sources do not say, answer NI with an empty quote. Never infer an answer from what trials usually do.
- NA only where the tool's own branching skips the question (e.g. 2.3 when participants and carers were both unaware;
  3.2-3.4 when 3.1 is Y/PY; 4.3-4.5 when 4.1 or 4.2 is Y/PY; 2.7 when 2.6 is Y/PY).
- rationale: one short sentence.
Reply with ONE JSON object with EXACTLY these keys, one element of "answers" per question (22):
{"answers": [{"qid": "1.1", "answer": "Y", "quote": "<verbatim text>", "source_id": "<a source id from the evidence>",
  "rationale": "<one sentence>"}, ...], "notes": ""}
"""

ADJ_INSTR = """Two independent readers assessed ONE randomised trial with the Cochrane RoB 2 tool for ONE outcome (effect
of assignment) and DISAGREED on the signalling questions below. For each, decide the answer the SOURCES support:
Y / PY / PN / N / NI / NA, with a VERBATIM quote (8-300 characters) from one source and its source_id (empty quote
only for NI or NA). Use only the sources. If the sources do not settle it, answer NI. Either reader may be wrong.
Reply with ONE JSON object with EXACTLY these keys, one element of "answers" per listed question:
{"answers": [{"qid": "1.2", "answer": "PY", "quote": "<verbatim text>", "source_id": "<a source id from the evidence>",
  "rationale": "<one sentence>"}], "notes": ""}
"""


# ------------------------------------------------------------------------------------------------ items and sources

def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _save(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = f"{p}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, p)


_REG_TEXT = None


def registry_texts(ncts):
    """{nct: 'Brief summary: ...\\n\\nDetailed description: ...'} from the pinned AACT snapshot (US Government text)."""
    global _REG_TEXT
    if _REG_TEXT is None:
        _REG_TEXT = {}
    want = {n for n in ncts if n and n not in _REG_TEXT}
    if want:
        from harness import aact
        parts = {n: {} for n in want}
        for table, label in (("brief_summaries", "Brief summary"), ("detailed_descriptions", "Detailed description")):
            p = aact._table(table)
            if not p:
                continue
            for r in aact._iter_rows(p):
                n = (r.get("nct_id") or "").upper()
                if n in parts and r.get("description"):
                    parts[n][label] = r["description"].strip()
        for n in want:
            _REG_TEXT[n] = "\n\n".join(f"{k}: {v}" for k, v in parts[n].items()) or None
    return {n: _REG_TEXT.get(n) for n in ncts}


def served_primary(slug):
    r = _j(os.path.join(ROOT, "docs", "reviews", slug, "review.json"))
    o = next((o for o in r["outcomes"] if o.get("primary")), r["outcomes"][0])
    pmids = [m.group(1) for t in o.get("trials") or [] for m in [re.search(r"PMID (\d+)", str(t.get("id")))] if m]
    return o["name"], pmids


_AACT_REF = None
_AACT_DESIGNS = {}


def aact_nct_for(pmids):
    """{pmid: nct} from AACT study_references (a RESULT reference preferred over a DERIVED one; an ambiguous pmid --
    several NCTs at the best type -- gets none)."""
    global _AACT_REF
    if _AACT_REF is None:
        from harness import aact
        _AACT_REF = {}
        p = aact._table("study_references")
        for r in aact._iter_rows(p) if p else []:
            pm = (r.get("pmid") or "").strip()
            if pm:
                _AACT_REF.setdefault(pm, []).append(((r.get("reference_type") or "").upper(), (r.get("nct_id") or "").upper()))
    out = {}
    for pm in pmids:
        refs = _AACT_REF.get(str(pm)) or []
        for t in ("RESULT", "DERIVED"):
            ns = sorted({n for ty, n in refs if ty == t})
            if ns:
                out[pm] = ns[0] if len(ns) == 1 else None
                break
    return out


def aact_designs(ncts):
    """{nct: header-keyed AACT designs row} (the same row the pinned registry_designs.json would hold)."""
    want = {n for n in ncts if n and n not in _AACT_DESIGNS}
    if want:
        from harness import aact
        p = aact._table("designs")
        for r in aact._iter_rows(p) if p else []:
            n = (r.get("nct_id") or "").upper()
            if n in want:
                _AACT_DESIGNS[n] = {k: v for k, v in r.items() if k != "id"}
    return {n: _AACT_DESIGNS.get(n) for n in ncts if n}


def items(slug, pmids=None):
    outcome, pool = served_primary(slug)
    pmids = pmids or pool
    machine = _j(os.path.join(ROOT, "cache", slug, "rob2.json")).get("trials", {})
    designs = _j(os.path.join(ROOT, "cache", slug, "registry_designs.json")) \
        if os.path.exists(os.path.join(ROOT, "cache", slug, "registry_designs.json")) else {}
    ncts = {p: (machine.get(p) or {}).get("nct") for p in pmids}
    # a trial outside the served pool (calibration): its NCT from AACT study_references, its designs row from AACT
    extra = aact_nct_for([p for p in pmids if not ncts.get(p)])
    ncts.update({p: n for p, n in extra.items() if n})
    designs = dict(designs, **{n: r for n, r in aact_designs([n for n in ncts.values() if n and n not in designs]).items() if r})
    texts = registry_texts([n for n in ncts.values() if n])
    lic = rt._ft_licences()
    out = []
    for p in pmids:
        nct = ncts.get(p)
        rows = {"designs": {k: v for k, v in designs[nct].items() if k != "id"}} if nct in designs else {}
        srcs = rt.trial_sources(slug, p, nct=nct, registry_rows=rows, registry_text=texts.get(nct), ft_licences=lic)
        m5 = ((machine.get(p) or {}).get("domains") or {}).get("D5_selective_reporting")
        out.append({"slug": slug, "pmid": p, "nct": nct, "outcome": outcome, "sources": srcs, "machine_d5": m5,
                    "key": f"{slug}::{p}::{outcome}"})
    return out


# ------------------------------------------------------------------------------------------------ prompts (D8 gate)

class D8Refused(Exception):
    pass


def open_sources(item):
    return [s for s in item["sources"] if s["open_for_prompt"]]


def evidence_block(item):
    """The sources a prompt may carry, as the licence guard reads them: a CC full text under 'text' with its pmid (the
    guard checks it is CC); an abstract under 'abstract' (the abstract policy); registry text under 'text' with its nct.
    D8: a source not open for prompts is never included -- refused here, before the recorder's own guard."""
    ev = []
    for s in item["sources"]:
        if not s["open_for_prompt"]:
            continue
        if s["kind"] == "fulltext":
            if s.get("licence") != "CC":
                raise D8Refused(f"{s['id']}: full text not marked CC")
            ev.append({"id": s["id"], "kind": "fulltext", "pmid": s["pmid"], "text": s["text"]})
        elif s["kind"] == "abstract":
            ev.append({"id": s["id"], "kind": "abstract", "abstract": s["text"]})
        else:
            ev.append({"id": s["id"], "kind": s["kind"], "nct": s.get("nct"), "text": s["text"]})
    return ev


def prompt_bytes(item, kind="reader", disagreements=None):
    qs = "\n".join(f"{q} {rf.QUESTIONS[q]}" for q in (QIDS if kind == "reader" else sorted(disagreements)))
    head = INSTR if kind == "reader" else ADJ_INSTR
    body = f"\nTRIAL: {item['pmid']} ({item['nct'] or 'no registry id'})\nOUTCOME: {item['outcome']}\n\nSIGNALLING QUESTIONS:\n{qs}\n"
    if kind == "adjudicator":
        body += "\nTHE TWO READINGS:\n" + json.dumps(disagreements, indent=1, ensure_ascii=False) + "\n"
    ev = evidence_block(item)
    return (head + body + "\n=== EVIDENCE ===\n" + json.dumps({"sources": ev}, ensure_ascii=False)).encode("utf-8")


def digests(item):
    return [{"ref": s["id"], "sha256": s["sha256"], "what": f"{s['kind']} ({s.get('licence')})"} for s in open_sources(item)]


# ------------------------------------------------------------------------------------------------ calls

def _call(item, who, prompt):
    from reproducible_ai import model_call_live as mcl
    caller = {"file": "scripts/rob2_dual.py", "line": f"call:{who}", "lane": LANE,
              "purpose": f"RoB 2 ({who}) {item['slug']} PMID {item['pmid']} outcome '{item['outcome'][:60]}'"}
    for attempt in range(4):
        if who == "agy":
            rec = mcl.agy_call(prompt, schema=SCHEMA, caller=caller, input_digests=digests(item), timeout_s=900)
        else:
            rec = mcl.call(prompt, schema=SCHEMA, model=CODEX_MODEL, effort=ADJ_EFFORT if who == "adjudicator" else CODEX_EFFORT,
                           caller=caller, input_digests=digests(item), timeout_s=1200)
        ms.write_record(rec, REC_DIR)
        if rec["state"] == "RAN_OK" or attempt == 3:
            break
        time.sleep(30 * 3 ** attempt)             # back-off: 30 s, 90 s, 270 s (a failed attempt stays on record)
    return {"record_id": rec["record_id"], "state": rec["state"], "error": rec.get("error"),
            "prompt_sha256": hashlib.sha256(prompt).hexdigest(), "model": rec["model"]["id_reported"]}


def parse(raw):
    t = raw.decode("utf-8", "replace").strip()
    m = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", t, re.S)
    t = m.group(1) if m else t
    try:
        d = json.loads(t)
    except ValueError:
        return None
    return d if isinstance(d, dict) and isinstance(d.get("answers"), list) else None


def replay(run):
    if not run or run.get("state") != "RAN_OK":
        return None
    return parse(ms.replay(ms.load_record(os.path.join(REC_DIR, run["record_id"] + ".json"))))


# ------------------------------------------------------------------------------------------------ verification

def _norm(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = s.replace("−", "-").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip()


def verify_answers(reading, item, allowed=None):
    """{qid: verified answer dict}. A Y/PY/PN/N answer stands only if its quote (>= 8 chars) is found verbatim
    (whitespace/case/dash-normalised) in the OPEN source it names; otherwise it becomes NI, with the reason kept."""
    srcs = {s["id"]: s for s in open_sources(item)}
    out = {}
    for a in (reading or {}).get("answers") or []:
        q = a.get("qid")
        if q not in rf.QUESTIONS or (allowed and q not in allowed) or q in out:
            continue
        v = a.get("answer") if a.get("answer") in rf.ANSWERS else "NI"
        if v in ("Y", "PY", "PN", "N"):
            s = srcs.get(a.get("source_id"))
            quote = a.get("quote") or ""
            if s is None or len(_norm(quote)) < 8 or _norm(quote) not in _norm(s["text"]):
                out[q] = {"answer": "NI", "dropped": {"answer": v, "quote": quote[:300], "source_id": a.get("source_id"),
                                                      "why": "QUOTE_NOT_FOUND_IN_NAMED_OPEN_SOURCE"}}
                continue
            out[q] = {"answer": v, "quote": quote, "source_id": s["id"], "source_sha256": s["sha256"],
                      "rationale": a.get("rationale")}
        else:
            out[q] = {"answer": v, "rationale": a.get("rationale")}
    return out


def agree(a, b):
    """(agreed {qid: answer}, disagreements {qid: (a, b)}) over every question."""
    agreed, dis = {}, {}
    for q in QIDS:
        x, y = a.get(q) or {"answer": "NI"}, b.get(q) or {"answer": "NI"}
        sx, sy = rf.side(x["answer"]), rf.side(y["answer"])
        if sx == sy:
            if sx in ("Y", "N"):
                pick = x if x["answer"] in ("PY", "PN") else y if y["answer"] in ("PY", "PN") else x
                agreed[q] = dict(pick, agreed_with=y if pick is x else x)
            else:
                agreed[q] = {"answer": x["answer"]}
        else:
            dis[q] = (x, y)
    return agreed, dis


# ------------------------------------------------------------------------------------------------ assembly

def assemble(item, typed, conflicts, agreed, adjudicated, runs):
    answers, provenance = {}, {}
    recs = [r["record_id"] for r in (runs.get("codex"), runs.get("agy")) if r]
    for q in QIDS:
        if q in typed:
            answers[q] = typed[q]
            provenance[q] = "typed"
            continue
        a = adjudicated.get(q) or agreed.get(q)
        how = "adjudicated" if q in adjudicated else "dual-agreed"
        if a and a["answer"] in ("Y", "PY", "PN", "N"):
            answers[q] = rf.answer(a["answer"], how=how, span=a["quote"], source_ref=a["source_id"],
                                   source_sha256=a["source_sha256"],
                                   records=recs + ([runs["adjudicator"]["record_id"]] if q in adjudicated and runs.get("adjudicator") else []))
        else:
            answers[q] = rf.answer(a["answer"] if a and a["answer"] in ("NI", "NA") else "NI", how=how if a else "no-reading",
                                   records=recs)
        provenance[q] = how if a else "no-reading"
    closed_ft = any(s["kind"] == "fulltext" and not s["open_for_prompt"] for s in item["sources"])
    insufficient = [d for d, qs in rf.DOMAINS.items()
                    if closed_ft and all(answers[q]["answer"] in ("NI", "NA") for q in qs)]
    obj = rf.assessment(f"PMID {item['pmid']}", item["outcome"], answers, insufficient_domains=insufficient)
    obj.update({"nct": item["nct"], "typed_conflicts": conflicts, "answer_provenance": provenance,
                "sources": [{k: s[k] for k in ("id", "kind", "sha256", "open_for_prompt", "licence")} for s in item["sources"]],
                "runs": runs})
    return obj


def process(item, runs, live, pools):
    typed, conflicts = rt.typed_answers(item["sources"], item.get("machine_d5"))
    r = dict(runs.get(item["key"]) or {})
    if not open_sources(item):
        return assemble(item, typed, conflicts, {}, {}, r), r
    p = prompt_bytes(item)
    ps = hashlib.sha256(p).hexdigest()
    if live:
        futs = {who: pools[who].submit(_call, item, who, p) for who in ("codex", "agy")
                if not ((r.get(who) or {}).get("state") == "RAN_OK" and r[who]["prompt_sha256"] == ps)}
        for who, f in futs.items():
            r[who] = f.result()
    a = verify_answers(replay(r.get("codex")), item)
    b = verify_answers(replay(r.get("agy")), item)
    agreed, dis = agree(a, b) if (r.get("codex") or {}).get("state") == "RAN_OK" and (r.get("agy") or {}).get("state") == "RAN_OK" else ({}, {})
    dis = {q: v for q, v in dis.items() if q not in typed}          # typed answers settle their questions
    adjudicated = {}
    if dis:
        shown = {q: {"reader 1": x, "reader 2": y} for q, (x, y) in dis.items()}
        pa = prompt_bytes(item, "adjudicator", shown)
        if live and not ((r.get("adjudicator") or {}).get("state") == "RAN_OK"
                         and r["adjudicator"]["prompt_sha256"] == hashlib.sha256(pa).hexdigest()):
            r["adjudicator"] = pools["codex"].submit(_call, item, "adjudicator", pa).result()
        adjudicated = verify_answers(replay(r.get("adjudicator")), item, allowed=set(dis))
    obj = assemble(item, typed, conflicts, agreed, adjudicated, r)
    obj["disagreements"] = sorted(dis)
    return obj, r


def calibration_pmids(slug):
    """Every trial the comparator's RoB figure rates (outputs/robgrade/reference/<slug>.json), bound to a PMID, for which
    an abstract is held -- in the served pool or not: the engine applies to any RCT, so it is calibrated on all of them."""
    ref = os.path.join(ROOT, "outputs", "robgrade", "reference", f"{slug}.json")
    if not os.path.exists(ref):
        return []
    rows = (_j(ref).get("rows") or {}).values()
    return sorted({r["pmid"] for r in rows if r.get("pmid")})


def main(argv):
    live = "--run" in argv
    calib = "--calibration" in argv
    slugs = [a for a in argv if not a.startswith("--")]
    runs = _j(RUNS) if os.path.exists(RUNS) else {}
    pools = {"codex": cf.ThreadPoolExecutor(CODEX_WORKERS), "agy": cf.ThreadPoolExecutor(AGY_WORKERS),
             "adjudicator": None}
    driver = cf.ThreadPoolExecutor(max(CODEX_WORKERS, AGY_WORKERS))
    for slug in slugs:
        its = items(slug, sorted(set(served_primary(slug)[1]) | set(calibration_pmids(slug))) if calib else None)
        its = [i for i in its if any(s["kind"] == "abstract" for s in i["sources"])] if calib else its
        results = {}
        for it, (obj, r) in zip(its, driver.map(lambda i: process(i, runs, live, pools), its)):
            runs[it["key"]] = r
            results[it["pmid"]] = obj
            print(slug, it["pmid"], obj["overall"]["judgement"], {d: o["judgement"] for d, o in obj["domains"].items()},
                  {w: (x or {}).get("state") for w, x in r.items()}, flush=True)
        _save(RUNS, runs)
        _save(os.path.join(OUT_DIR, f"{slug}.json"), {"slug": slug, "family": rf.FAMILY, "outcome": its[0]["outcome"] if its else None,
                                                      "trials": results})
    for p in pools.values():
        if p:
            p.shutdown()
    driver.shutdown()


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
